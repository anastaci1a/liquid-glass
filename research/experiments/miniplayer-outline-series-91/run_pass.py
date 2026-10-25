"""Bounded shared-family outline pass; all trials and original guards retained."""
from pathlib import Path
import ast, datetime, hashlib, json, sys, time
import numpy as np
from PIL import Image, ImageDraw, ImageFont

ROOT = Path(__file__).resolve().parents[3]
SERIES = Path(__file__).parent
OUT = SERIES / sys.argv[1]
sys.path.insert(0, str(ROOT/'reconstruction'))
from extended_fit import Study
from outline_response import cap_strength, point_alpha, integrate, response_delta, composite

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
    for i, (arr, label) in enumerate([(study.target_crop, 'Reference'), (baseline, 'Frozen working body'), (candidate, 'Shared outline candidate')]):
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
        for i, (arr,label) in enumerate([(study.target_crop,'Reference'),(baseline,'Frozen body'),(candidate,'Candidate')]):
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
    bind=[Path(__file__),ROOT/'reconstruction/outline_response.py',ROOT/'reconstruction/pixel_quadrature.py',metric_file,ROOT/'reconstruction/extended_fit.py',ROOT/'reconstruction/families/music-mini-player-working.json']
    for f in bind:first[str(f.relative_to(ROOT))]=sha(f)
    first[str((OUT/'protocol.json').relative_to(ROOT))]=sha(OUT/'protocol.json')
    configs=P['configs'];c=configs[0]
    # Algebraic/profile fixtures, not optical calls.
    t=np.deg2rad(np.array([-90.,c['start'],c['minimum'],c['hold'],c['recover'],90.]))
    x=2+np.cos(t);y=-np.sin(t);charge('profile_controls',36)
    w=cap_strength(x,y,(3.,1.),1.,(0.,0.),c)
    assert np.allclose(w,[1,1,0,0,1,1],atol=1e-14)
    assert np.allclose(w,cap_strength(-x,-y,(3.,1.),1.,(0.,0.),c),atol=1e-14)
    samples=np.array([[[0.,0.,0.],[.2,.4,.6],[1.,1.,1.],[.1,.1,.1]]])
    for kind in ['white','encoded_lift','linear_lift']:
        delta=response_delta(samples,kind);assert np.isfinite(delta).all()
        assert np.array_equal(composite(samples,np.ones((1,4)),delta,0),samples)
        assert np.all((samples+delta>=0)&(samples+delta<=1))
    save('profile-controls.json',dict(angle_strength=w.tolist(),rotation180=True,zero_responses_exact=True,black_and_white_finite=True))
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
        for k in ['a','b']:
            case=json.loads((work/k/'case.json').read_text())
            for fn,h in case['source_sha256'].items():
                f=work/k/fn;assert sha(f)==h;first[str(f.relative_to(ROOT))]=h
            first[str((work/k/'case.json').relative_to(ROOT))]=sha(work/k/'case.json')
            charge('Study_constructor_pixels',1360*250 if member=='expanded' else 920*240)
            charge('target_source_bitmap_pixels',2*1920*1080)
            s=Study(work/k)
            zp=ROOT/f'research/experiments/miniplayer-incident-material-20/{member}-{k}-factor0.5.npz'
            first[str(zp.relative_to(ROOT))]=sha(zp);z=read_npz(zp,['complete','coverage'])
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
            baseline=z['complete'];charge('identity_composites',1)
            ident=composite(baseline,np.ones(baseline.shape[:2]),response_delta(baseline,'white'),0.)
            assert np.array_equal(ident,baseline,equal_nan=True)
            train=m['glass']&~m['held']
            assert not np.any(train&m['held'])
            x0,y0,x1,y1=s.crop
            for layer in s.case['foreground_layers']:
                a,b,c,e=layer['box'];assert not train[b-y0:e-y0,a-x0:c-x0].any()
            incumbent=before
            previous=SERIES/'selection.json'
            if previous.exists():
                selection=json.loads(previous.read_text())
                if selection.get('accepted'):
                    ip=SERIES/selection['accepted']['folder']/f"{member}-{k}-c{selection['accepted']['candidate']}-metrics.json"
                    first[str(ip.relative_to(ROOT))]=sha(ip);incumbent=json.loads(ip.read_text())['scores']
            data[(member,k)]=dict(s=s,baseline=baseline,m=m,partial=partial,before=before,incumbent=incumbent,crops=crops,center=center,half=half,radius=radius,train=train)
    reused={}
    if P.get('reuse_alpha'):
        reuse=P['reuse_alpha']
        for config in configs:
            assert {k:v for k,v in config.items() if k not in ['response','white_mix']}==reuse['geometry_config']
        for member in ['expanded','compact']:
            f=SERIES/reuse['folder']/f'{member}-alpha.npz'
            assert sha(f)==reuse['hashes'][member]
            first[str(f.relative_to(ROOT))]=sha(f)
            reused[member]=read_npz(f,['order8','order16'])
    save('first-hashes.json',first)
    now=datetime.datetime.now(datetime.timezone.utc)
    assert now<datetime.datetime.fromisoformat(P['checkpoint_deadline'])
    save('checkpoint.json',{'at':now.isoformat(),'four_zero_identities_exact':True,'masks_and_inputs_bound':True,'analytic_profile_controls_pass':True,'ledger':dict(ledger)})
    print('CHECKPOINT',now.isoformat(),flush=True)
    fields={};integrals=[]
    for member in ['expanded','compact']:
        d=data[(member,'a')];pair=[];infos=[]
        for order in P['orders']:
            if member in reused:
                selected=reused[member][f'order{order}'][P['reuse_alpha']['candidate']]
                charge('reused_alpha_values',selected.size*len(configs))
                a=np.stack([selected]*len(configs));info=dict(order=order,reused_from=P['reuse_alpha']['folder'])
            else:
                a,info=integrate(d['s'].crop,d['half'],d['radius'],d['center'],configs,order,charge,reserve,tail=P['tail_bound'])
            pair.append(a);infos.append(info)
        diffs=np.max(abs(pair[1]-pair[0]),axis=(1,2))
        assert np.all(diffs<=P['maximum_order_difference']), 'Unresolved opacity quadrature'
        fields[member]=pair[1]
        np.savez_compressed(OUT/f'{member}-alpha.npz',order8=pair[0],order16=pair[1])
        integrals.append(dict(member=member,maximum_alpha_differences=diffs.tolist(),orders=infos))
    results=[];fits=[]
    for j,config in enumerate(configs):
        numerator=0.;denominator=0.;loss0=0.;deltas={}
        for (member,k),d in data.items():
            a=fields[member][j]
            if config['response']=='mixed_lift':
                mix=config['white_mix'];assert 0<=mix<=1
                delta=mix*response_delta(d['baseline'],'white')+(1-mix)*response_delta(d['baseline'],'linear_lift')
            else:delta=response_delta(d['baseline'],config['response'])
            deltas[(member,k)]=delta
            train=d['train'];v=a[train,None]*delta[train];r=d['s'].target_crop[train].astype(float)-d['baseline'][train]
            charge('fit_pixel_channels',v.size)
            numerator+=float(np.mean(v*r))/4;denominator+=float(np.mean(v*v))/4;loss0+=float(np.mean(r*r))/4
        charge('scalar_fits',1);strength=float(np.clip(numerator/denominator,0,1)) if denominator>0 else 0.
        loss=loss0-2*strength*numerator+strength*strength*denominator
        fits.append(dict(candidate=j,config=config,strength=strength,numerator=numerator,denominator=denominator,train_loss=loss,unoutlined_train_loss=loss0,held_excluded=True,foreground_excluded=True))
        for (member,k),d in data.items():
            a=fields[member][j];charge('candidate_composites',1)
            C=composite(d['baseline'],a,deltas[(member,k)],strength)
            assert np.array_equal(np.isnan(C),np.isnan(d['baseline']))
            assert np.array_equal(C[a==0],d['baseline'][a==0],equal_nan=True)
            now=score(d['s'],C,d['m'],d['partial'],d['crops'])
            def guards(before):
                g={n:now[n]['rmse']<=before[n]['rmse'] for n in ['glass','rim','held','interior']}
                g.update(E=now['E']<=before['E'],SSIM=now['ssim']>=before['ssim'],partial=now['partial']['RMSE']<=before['partial']['RMSE'],exterior=now['exterior']<=before['exterior'])
                g.update({n:v<=before['foreground'][n] for n,v in now['foreground'].items()});return g
            original=guards(d['before']);incumbent=guards(d['incumbent'])
            row=dict(candidate=j,member=member,reference=k,config=config,strength=strength,scores=now,baseline=d['before'],original_guards=original,incumbent_guards=incumbent,all_guards_pass=all(original.values()) and all(incumbent.values()))
            prefix=f'{member}-{k}-c{j}';save(prefix+'-metrics.json',row);np.savez_compressed(OUT/f'{prefix}.npz',complete=C)
            presentation(prefix,d['s'],d['baseline'],C,d['crops']);results.append(row)
            print('RESULT',prefix,'strength',strength,'E',now['E'],'partial',now['partial']['RMSE'],'fail',[n for n,v in original.items() if not v],flush=True)
    qualifiers=[j for j,f in enumerate(fits) if f['strength']>0 and all(r['all_guards_pass'] for r in results if r['candidate']==j)]
    seed=min(range(len(fits)),key=lambda j:fits[j]['train_loss'])
    accepted=min(qualifiers,key=lambda j:fits[j]['train_loss']) if qualifiers else None
    save('fits.json',fits)
    last={f:sha(ROOT/f) for f in first};assert last==first
    save('last-hashes.json',last);save('ledger.json',ledger)
    save('result.json',dict(status='ONE_SEPARATE_OUTLINE_OBSERVATION_COMPLETE',finished=datetime.datetime.now(datetime.timezone.utc).isoformat(),records=results,integration=integrals,ledger=ledger,selected_model_changed=False,numerical_qualifier=accepted,development_seed=seed,development_seed_is_acceptance=False,all_family_guards_pass=bool(qualifiers)))


try:
    run()
except Exception as exc:
    save('failure.json',dict(at=datetime.datetime.now(datetime.timezone.utc).isoformat(),type=type(exc).__name__,message=str(exc),ledger=ledger))
    raise
