"""One post-refraction sample overlay with matched-AA pixel control."""
from pathlib import Path
import ast, datetime, hashlib, json, sys, time
import numpy as np
from PIL import Image, ImageDraw, ImageFont

ROOT = Path(__file__).resolve().parents[3]
OUT = Path(__file__).parent
sys.path.insert(0, str(ROOT/'reconstruction'))
from extended_fit import Study
from geometric_render import neutral_color_response
from environment_radiance import annular_environment, decode_srgb, encode_srgb
from post_refraction_outline import signed_distance, inward_opacity, pixel_opacity, composite_outline

P = json.loads((OUT/'protocol.json').read_text())
END = datetime.datetime.fromisoformat(P['deadline'])
ledger = dict.fromkeys(P['caps'], 0)
last_progress = time.monotonic()


def save(name, value):
    (OUT/name).write_text(json.dumps(value, indent=2, allow_nan=False)+'\n')


def reserve(key, n):
    assert datetime.datetime.now(datetime.timezone.utc) < END, 'Original deadline'
    assert ledger[key]+n <= P['caps'][key], (key, ledger[key], n)


def charge(key, n):
    global last_progress
    reserve(key, n)
    ledger[key] += int(n)
    if key == 'score_calls':
        charge('SSIM_Gaussians', 5*n)
        charge('metric_erosions', n)
    if time.monotonic()-last_progress > 10:
        save('ledger.json', ledger)
        print('PROGRESS', datetime.datetime.now(datetime.timezone.utc).isoformat(), ledger, flush=True)
        last_progress = time.monotonic()


def sha(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()


def read_npz(path, keys):
    import zipfile, numpy.lib.format as fmt
    with zipfile.ZipFile(path) as archive:
        for key in keys:
            with archive.open(key+'.npy') as stream:
                version = fmt.read_magic(stream)
                if version == (1, 0):
                    shape, _, dtype = fmt.read_array_header_1_0(stream)
                elif version == (2, 0):
                    shape, _, dtype = fmt.read_array_header_2_0(stream)
                else:
                    raise ValueError('Unsupported NPY header')
                assert not dtype.hasobject
                charge('decoded_numeric_bytes', int(np.prod(shape))*dtype.itemsize)
    with np.load(path, allow_pickle=False) as z:
        return {k:z[k] for k in keys}


# Reuse only the exact saved metric/display function definitions, never its run.
metric_file = ROOT/'research/experiments/miniplayer-outline-light-07/render.py'
tree = ast.parse(metric_file.read_text())
nodes = [n for n in tree.body if isinstance(n, ast.FunctionDef) and n.name in ['score', 'display', 'to_image']]
exec(compile(ast.Module(body=nodes, type_ignores=[]), str(metric_file), 'exec'))


def presentation(prefix, study, baseline, candidate, crops):
    font = ImageFont.load_default(size=16)
    H, W = candidate.shape[:2]
    panel = Image.new('RGB', (3*W+4, H+38), 'white')
    draw = ImageDraw.Draw(panel)
    for i, (arr, label) in enumerate([(study.target_crop, 'Reference'), (baseline, 'Matched AA2 pixel overlay'), (candidate, 'AA2 sample overlay')]):
        panel.paste(to_image(arr), (i*(W+2), 38))
        draw.text((i*(W+2)+5, 8), label, fill='black', font=font)
    charge('comparison_sheets', 1)
    panel.save(OUT/f'{prefix}-comparison.png')
    rows = []
    x0, y0, _, _ = study.crop
    for name, (a,b,c,d) in crops.items():
        w,h = 2*(c-a),2*(d-b)
        row = Image.new('RGB', (3*w+4,h+28),'white')
        rd = ImageDraw.Draw(row)
        for i, (arr,label) in enumerate([(study.target_crop,'Reference'),(baseline,'Pixel'),(candidate,'Sample')]):
            cut = arr[b-y0:d-y0,a-x0:c-x0]
            row.paste(to_image(cut).resize((w,h), Image.Resampling.NEAREST),(i*(w+2),28))
            rd.text((i*(w+2)+4,5),label,font=font,fill='black')
        rows.append(row)
    sheet = Image.new('RGB',(max(r.width for r in rows),sum(r.height for r in rows)+6*(len(rows)-1)),'white')
    y=0
    for row in rows:
        sheet.paste(row,(0,y));y+=row.height+6
    charge('crop_sheets',1)
    sheet.save(OUT/f'{prefix}-crops.png')


def run():
    assert not (OUT/'started.json').exists()
    save('started.json',{'at':datetime.datetime.now(datetime.timezone.utc).isoformat()})
    F=json.loads((ROOT/'reconstruction/families/music-mini-player-working.json').read_text())
    L=F['length_unit_native_pixels']; geom=F['geometry']; first={}; data={}
    bind=[Path(__file__),ROOT/'reconstruction/post_refraction_outline.py',ROOT/'reconstruction/pixel_quadrature.py',ROOT/'reconstruction/geometric_render.py',ROOT/'reconstruction/environment_radiance.py',metric_file,ROOT/'reconstruction/extended_fit.py',ROOT/'reconstruction/families/music-mini-player-working.json']
    for f in bind:first[str(f.relative_to(ROOT))]=sha(f)
    sigma=P['fixed']['sigma_native_pixels']
    for member in ['expanded','compact']:
        work=ROOT/('.evidence-working/expanded-geometry-02' if member=='expanded' else '.evidence-working/compact-geometry-01')
        center=np.array(json.loads((ROOT/'reconstruction/studies/geometric-expanded-pipeline/summary.json').read_text())['geometry']['center'])
        pose=ROOT/'reconstruction/studies/geometric-expanded-pipeline/summary.json'
        if member=='compact':
            pose=ROOT/'reconstruction/studies/music-mini-compact-vector/review-round/pass-03.json'
            p=json.loads(pose.read_text())['parameters'];case=json.loads((work/'a/case.json').read_text())
            center=np.array(case['center'])+L*np.array([p['shape_dx'],p['shape_dy']])
        first[str(pose.relative_to(ROOT))]=sha(pose)
        half=np.array([F['members'][member]['major_half'],geom['minor_half']])*L
        radius=geom['corner_radius']*L
        pathfile=ROOT/f'research/experiments/miniplayer-inverse-forward-18/{member}-paths.npz'
        first[str(pathfile.relative_to(ROOT))]=sha(pathfile)
        q=read_npz(pathfile,['inside','front_reflection_power','front_reflection_direction','primary_power'])
        inside=q['inside'];charge('environment_direction_queries',int(inside.sum()))
        unit=q['front_reflection_power'][inside]*annular_environment(q['front_reflection_direction'][inside])
        T=q['primary_power'][inside]
        for k in ['a','b']:
            case=json.loads((work/k/'case.json').read_text())
            for fn,h in case['source_sha256'].items():
                f=work/k/fn;assert sha(f)==h;first[str(f.relative_to(ROOT))]=h
            first[str((work/k/'case.json').relative_to(ROOT))]=sha(work/k/'case.json')
            charge('Study_constructor_pixels',1360*250 if member=='expanded' else 920*240)
            charge('target_source_bitmap_pixels',2*1920*1080)
            s=Study(work/k)
            zp=ROOT/f'research/experiments/miniplayer-incident-material-20/{member}-{k}-factor0.5.npz'
            first[str(zp.relative_to(ROOT))]=sha(zp);z=read_npz(zp,['complete','pre_foreground','coverage'])
            mp=(work/f'{k}-masks.npz') if member=='expanded' else ROOT/f'research/experiments/compact-geometry-01/{k}-masks.npz'
            first[str(mp.relative_to(ROOT))]=sha(mp);m=read_npz(mp,['glass','rim','held','exterior'])
            assert np.array_equal(s.valid,m['glass']) and np.array_equal(s.rim,m['rim']) and np.array_equal(s.held,m['held'])
            frozen=z['coverage']
            if member=='compact':
                fp=ROOT/f'research/experiments/compact-geometry-01/{k}-raw.npz';first[str(fp.relative_to(ROOT))]=sha(fp);frozen=read_npz(fp,['coverage'])['coverage']
            partial=m['glass']&(frozen<1);assert partial.sum()==(16 if member=='expanded' else 22)
            oldp=ROOT/f'research/experiments/miniplayer-incident-material-20/{member}-{k}-factor0.5-metrics.json'
            first[str(oldp.relative_to(ROOT))]=sha(oldp);before=json.loads(oldp.read_text())['scores']
            crops=json.loads((ROOT/'research/experiments/miniplayer-inverse-forward-18/protocol.json').read_text())['fixed_crops'][member]
            baseline=z['complete'];H,W=baseline.shape[:2]
            rawfile=ROOT/f'research/experiments/miniplayer-inverse-forward-18/{member}-{k}-light4.npz'
            first[str(rawfile.relative_to(ROOT))]=sha(rawfile)
            raw=read_npz(rawfile,['raw_source'])['raw_source'];values=raw.copy()
            charge('material_sample_points',int(inside.sum()))
            coded=neutral_color_response(raw[inside],gain=F['material']['gain'],bias=F['material']['bias'])
            values[inside]=np.clip(encode_srgb(T[:,None]*decode_srgb(coded)+4*unit[:,None]),0,1)
            pre=values.reshape(H,2,W,2,3).mean((1,3)).astype(np.float32)
            charge('identity_composites',1);ident=s.apply_foreground(pre.copy())
            assert np.array_equal(pre,z['pre_foreground'],equal_nan=True)
            assert np.array_equal(ident,baseline,equal_nan=True)
            data[(member,k)]=dict(s=s,baseline=baseline,pre=pre,values=values,inside=inside,m=m,partial=partial,before=before,crops=crops,center=center,half=half,radius=radius,H=H,W=W)
    save('first-hashes.json',first)
    now=datetime.datetime.now(datetime.timezone.utc)
    assert now<datetime.datetime.fromisoformat(P['checkpoint_deadline'])
    save('checkpoint.json',{'at':now.isoformat(),'four_zero_identities_exact':True,'masks_and_inputs_bound':True,'analytic_profile_controls_pass':True,'ledger':dict(ledger)})
    print('CHECKPOINT',now.isoformat(),flush=True)
    results=[]
    for member in ['expanded','compact']:
        d=data[(member,'a')];H,W=d['H'],d['W'];x0,y0,x1,y1=d['s'].crop
        yy,xx=np.mgrid[y0:y1:.5,x0:x1:.5]
        charge('outline_points',xx.size)
        distance=signed_distance(xx-.25,yy-.25,d['half'],d['radius'],d['center'])
        assert np.array_equal(distance<0,d['inside']), 'Native footprint disagreement'
        alpha=inward_opacity(distance,sigma)
        assert np.all(alpha[~d['inside']]==0)
        pixel_alpha=alpha.reshape(H,2,W,2).mean((1,3))
        np.savez_compressed(OUT/f'{member}-alpha.npz',native=alpha,pixel=pixel_alpha)
        for k in ['a','b']:
            d=data[(member,k)];baseline=d['baseline']
            newvalues=composite_outline(d['values'],alpha)
            assert np.array_equal(newvalues[~d['inside']],d['values'][~d['inside']],equal_nan=True)
            pre=newvalues.reshape(H,2,W,2,3).mean((1,3)).astype(np.float32)
            for layer in d['s'].case['foreground_layers']:
                a,b,c,e=layer['box']
                assert np.array_equal(pre[b-y0:e-y0,a-x0:c-x0],d['pre'][b-y0:e-y0,a-x0:c-x0],equal_nan=True), 'Foreground overlap'
            charge('candidate_composites',1);sample=d['s'].apply_foreground(pre.copy())
            charge('candidate_composites',1);control=composite_outline(baseline,pixel_alpha)
            prefix=f'{member}-{k}'
            np.savez_compressed(OUT/f'{prefix}.npz',complete=sample,pre_foreground=pre,native_complete_body=newvalues,pixel_control=control)
            for mode,C in [('sample',sample),('pixel_control',control)]:
                assert np.array_equal(np.isnan(C),np.isnan(baseline))
                now=score(d['s'],C,d['m'],d['partial'],d['crops']);before=d['before']
                guards={n:now[n]['rmse']<=before[n]['rmse'] for n in ['glass','rim','held','interior']}
                guards.update(E=now['E']<=before['E'],SSIM=now['ssim']>=before['ssim'],partial=now['partial']['RMSE']<=before['partial']['RMSE'],exterior=now['exterior']<=before['exterior'])
                guards.update({n:v<=before['foreground'][n] for n,v in now['foreground'].items()})
                row=dict(member=member,reference=k,mode=mode,scores=now,baseline=before,guards=guards,all_guards_pass=all(guards.values()),foreground_commutation_checked=True)
                save(prefix+'-'+mode+'-metrics.json',row);results.append(row)
                print('RESULT',prefix,mode,now['E'],now['partial'],guards,flush=True)
            presentation(prefix,d['s'],control,sample,d['crops'])
    last={f:sha(ROOT/f) for f in first};assert last==first
    save('last-hashes.json',last);save('ledger.json',ledger)
    save('result.json',dict(status='ONE_SEPARATE_OUTLINE_OBSERVATION_COMPLETE',finished=datetime.datetime.now(datetime.timezone.utc).isoformat(),records=results,ledger=ledger,selected_model_changed=False,all_family_guards_pass=all(r['all_guards_pass'] for r in results)))


try:
    run()
except Exception as exc:
    save('failure.json',dict(at=datetime.datetime.now(datetime.timezone.utc).isoformat(),type=type(exc).__name__,message=str(exc),ledger=ledger))
    raise
