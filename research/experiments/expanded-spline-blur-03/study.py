"""One incident width on the accepted spline/tone, with source-first gates."""
from pathlib import Path
import datetime
import hashlib
import json
import cv2
import numpy as np
from PIL import Image, ImageDraw, ImageFont
from scipy.ndimage import map_coordinates
from extended_fit import Study
from geometric_render import incident_source_filter, neutral_color_response

OUT = Path(__file__).resolve().parent; ROOT = OUT.parents[2]
P = ROOT / 'research/experiments/expanded-spline-observation-01'
BASE = ROOT / 'research/experiments/expanded-contrast-guard-02'
WORK = ROOT / '.evidence-working/expanded-geometry-02'
p = json.loads((OUT / 'protocol.json').read_text())
deadline = datetime.datetime.fromisoformat(p['deadline_utc'].replace('Z', '+00:00'))
assert not (OUT / 'started.json').exists(), 'One observation attempt only'
(OUT / 'started.json').write_text(json.dumps(dict(utc=datetime.datetime.now(datetime.timezone.utc).isoformat())) + '\n')
cv2.setNumThreads(1)
q = np.load(P / 'native-paths.npz'); X, Y, inside = q['X'], q['Y'], q['inside']
decision = json.loads((BASE / 'native-result.json').read_text())
g, b = decision['gain'], decision['bias']
radius = p['setting']['finite_radius']; contexts = []; support_rows = []
queries = 0; candidates = 0; mask_erosions = 0

def gate():
    assert datetime.datetime.now(datetime.timezone.utc) < deadline, 'Original stage deadline'

def save(name, value):
    (OUT / name).write_text(json.dumps(value, indent=2, allow_nan=False) + '\n')

def sha(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()

def score(s, C, masks):
    z = s.scores(C); z['E'] = float(np.sqrt(z['loss']))
    err = (C - s.target_crop) * 255
    z['exterior_RMSE'] = float(np.sqrt(np.mean(err[masks['exterior']] ** 2)))
    z['foreground_artwork_MSE'] = {}; x0, y0, _, _ = s.crop
    for layer in s.case['foreground_layers']:
        a, bb, c, d = layer['box']; e = err[bb-y0:d-y0, a-x0:c-x0]
        name = layer.get('style_key', layer.get('vector_asset', layer.get('artwork_asset')))
        z['foreground_artwork_MSE'][name] = float(np.mean(e * e))
    return z

def sample(field, x, y):
    a = np.floor(x).astype(int); bb = np.floor(y).astype(int)
    fx = (x-a)[:, None]; fy = (y-bb)[:, None]
    return ((field[bb, a]*(1-fx) + field[bb, a+1]*fx)*(1-fy)
            + (field[bb+1, a]*(1-fx) + field[bb+1, a+1]*fx)*fy)

for key in ['a', 'b']:
    gate(); s = Study(WORK / key); masks = np.load(WORK / f'{key}-masks.npz')
    before = np.load(BASE / f'{key}-candidate.npz'); raw0 = np.load(P / f'{key}-candidate.npz')
    np.testing.assert_array_equal(before['coverage'], raw0['coverage'])
    known = cv2.imread(str(WORK / key / 'known.png'), 0) > 0
    safe = cv2.erode(known.astype(np.uint8), np.ones((2*radius+1, 2*radius+1), np.uint8),
                    borderType=cv2.BORDER_CONSTANT, borderValue=0) > 0
    mask_erosions += 1
    H, W = s.valid.shape; req = masks['glass'] | masks['exterior'] | (before['coverage'] > 0)
    x0, y0, _, _ = s.crop
    for layer in s.case['foreground_layers']:
        a, bb, c, d = layer['box']; req[bb-y0:d-y0, a-x0:c-x0] = True
    required = np.repeat(np.repeat(req, 2, 0), 2, 1)
    defined = np.isfinite(X) & np.isfinite(Y) & (X >= 0) & (Y >= 0) & (X < known.shape[1]-1) & (Y < known.shape[0]-1)
    ii, jj = np.nonzero(defined); a = np.floor(X[ii, jj]).astype(int); bb = np.floor(Y[ii, jj]).astype(int)
    base_ok = np.zeros(inside.shape, bool); lens_ok = np.zeros_like(base_ok)
    for field, output in [(known, base_ok), (safe, lens_ok)]:
        output[ii, jj] = field[bb, a] & field[bb+1, a] & field[bb, a+1] & field[bb+1, a+1]
    support = np.where(inside, lens_ok, base_ok)
    row = dict(reference=key,required_subrays=int(required.sum()),whole_lens_subrays=int(inside.sum()),
        incomplete_required=int((required & ~q['complete']).sum()),
        unsupported_required=int((required & ~support).sum()),
        source_radius=radius,source_RGB_queries=0,
        inputs={f:sha(WORK/key/f) for f in ['case.json','source.png','target.png','known.png']})
    support_rows.append(row); save('source-first.json', dict(status='PENDING',records=support_rows))
    assert row['incomplete_required'] == row['unsupported_required'] == 0
    np.savez_compressed(OUT / f'{key}-support.npz', support=support, required=required)
    contexts.append((key,s,masks,before,raw0,known))

save('source-first.json', dict(status='PASS_BOTH_BEFORE_RGB',records=support_rows,
    mask_erosions_before_RGB=mask_erosions,original_paths_sha256=sha(P/'native-paths.npz')))
rows = []; luma = np.array([.2126,.7152,.0722])
for key,s,masks,before,raw0,known in contexts:
    gate(); field,field_known,actual_radius = incident_source_filter(s.source,known,p['setting']['sigma_native'])
    mask_erosions += 1; assert actual_radius == radius
    ii,jj = np.nonzero(inside); raw = raw0['sample_before_response'].copy()
    assert queries + len(ii) + 32 <= p['budgets']['source_RGB_queries']
    raw[ii,jj] = sample(field,X[ii,jj],Y[ii,jj]); queries += len(ii)
    selected = np.linspace(0,len(ii)-1,32,dtype=int); xx=X[ii[selected],jj[selected]]; yy=Y[ii[selected],jj[selected]]
    control = np.stack([map_coordinates(field[...,c].astype(float),np.stack([yy,xx]),order=1,prefilter=False) for c in range(3)],-1)
    queries += len(selected); error=float(np.max(abs(control-raw[ii[selected],jj[selected]])))
    assert error < 1e-12
    response,preclip = neutral_color_response(raw,gain=g,bias=b,return_preclip=True)
    clips=[int((preclip[inside]<0).sum()),int((preclip[inside]>1).sum())]; assert clips==[0,0]
    values=np.where(inside[...,None],response,raw); H,W=s.valid.shape
    pre=values.reshape(H,2,W,2,3).mean((1,3)).astype(np.float32)
    C=s.apply_foreground(pre.copy()); candidates+=1; baseline=before['complete']
    assert np.array_equal(raw[~inside],raw0['sample_before_response'][~inside],equal_nan=True)
    now,old=score(s,C,masks),score(s,baseline,masks)
    expected=next(r['scores'] for r in decision['records'] if r['reference']==key); assert old==expected
    guards={name:now[name]['rmse']<=old[name]['rmse'] for name in ['glass','rim','held','interior']}
    guards.update(E=now['E']<=old['E'],ssim=now['ssim']>=old['ssim'],exterior=now['exterior_RMSE']<=old['exterior_RMSE'])
    guards.update({name:value<=old['foreground_artwork_MSE'][name] for name,value in now['foreground_artwork_MSE'].items()})
    error64=(C.astype(float)-s.target_crop.astype(float))*255; old64=(baseline.astype(float)-s.target_crop.astype(float))*255
    cohorts={name:masks[name] for name in ['glass','rim','held','exterior']};cohorts['interior']=masks['glass']&~masks['rim']
    x0,y0,_,_=s.crop
    for layer in s.case['foreground_layers']:
        a,bb,c,d=layer['box'];m=np.zeros((H,W),bool);m[bb-y0:d-y0,a-x0:c-x0]=True
        cohorts[layer.get('style_key',layer.get('vector_asset',layer.get('artwork_asset')))]=m
    double={name:bool(np.mean(error64[m]**2)<=np.mean(old64[m]**2)) for name,m in cohorts.items()}
    a,bb,c,d=p['fixed_detail_crop_relative'];m=masks['glass'][bb:d,a:c]
    detail={}
    for name,image in [('reference',s.target_crop),('baseline',baseline),('candidate',C)]:
        tile=image[bb:d,a:c].astype(float); y=tile@luma; good=m[:,:-1]&m[:,1:]
        detail[name]=dict(luma_std=float(y[m].std()*255),horizontal_difference_RMS=float(np.sqrt(np.mean(np.diff(y,axis=1)[good]**2))*255))
    partial=masks['glass']&(before['coverage']<1)
    partial_review=dict(pixels=int(partial.sum()),baseline_RMSE=float(np.sqrt(np.mean(old64[partial]**2))),candidate_RMSE=float(np.sqrt(np.mean(error64[partial]**2))))
    np.savez_compressed(OUT/f'{key}-candidate.npz',sample_before_response=raw,pre_foreground=pre,complete=C,coverage=before['coverage'])
    valid=np.isfinite(C).all(2); yy,xx=np.indices(valid.shape);view=np.where(valid[...,None],C,np.where(((xx//6+yy//6)%2)[...,None],.72,.9))
    width=1080;height=round(H*width/W);canvas=Image.new('RGB',(2*width+2,height+64),'white');draw=ImageDraw.Draw(canvas);font=ImageFont.load_default(size=18)
    canvas.paste(Image.fromarray(np.uint8(np.rint(s.target_crop*255))).resize((width,height),Image.Resampling.LANCZOS),(0,64))
    canvas.paste(Image.fromarray(np.uint8(np.rint(np.clip(view,0,1)*255))).resize((width,height),Image.Resampling.LANCZOS),(width+2,64))
    draw.text((12,20),'Apple reference',fill='black',font=font);draw.text((width+14,20),'One incident sigma 5.0625; geometry/tone fixed',fill='black',font=font);canvas.save(OUT/f'{key}-comparison.png')
    row=dict(reference=key,scores=now,baseline_scores=old,guards=guards,float64_guards=double,all_pass=all(guards.values())and all(double.values()),
        clear_samples_exact=True,clips=clips,independent_bilinear_error=error,detail=detail,partial_boundary_advisory=partial_review)
    rows.append(row);save(f'{key}-measurement.json',row);print(json.dumps(row),flush=True);gate()

result=dict(status='STRICT_PAIRED_NUMERIC_CANDIDATE'if all(r['all_pass']for r in rows)else'REJECTED_FIXED_WIDTH',
    finished_utc=datetime.datetime.now(datetime.timezone.utc).isoformat(),records=rows,source_RGB_queries=queries,
    candidate_composites=candidates,incident_fields=2,known_mask_erosions=mask_erosions,new_rays=0,new_height_evaluations=0,fits=0)
save('result.json',result);print(result['status'],flush=True)
