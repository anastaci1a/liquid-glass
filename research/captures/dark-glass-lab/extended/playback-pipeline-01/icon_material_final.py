import json,time,datetime
from pathlib import Path
import cv2,numpy as np
from PIL import Image
from settled import icon_color
from reproduce import CASES,points,masks,scores
P=Path('/evidence/extended/playback-pipeline-01');D=P/'icon';assert not (D/'final-correction.json').exists();assert time.time()<datetime.datetime(2026,10,22,9,12,57,tzinfo=datetime.timezone.utc).timestamp()
case=CASES['media'];x0,y0,x1,y1=case['crop'];p=json.loads(Path('/evidence/extended/playback-short-round/pass-03/replay-record.json').read_text())['recipe'];L=245.;a,b,c,d=[int(round(v*L+case['center'][i%2])) for i,v in enumerate(p['icon']['box_over_L'])];sl=np.s_[b-y0:d-y0,a-x0:c-x0];alpha=np.asarray(Image.open(P/'code'/p['icon']['coverage']),float)/255;A=np.load(P/'blurriness/coverage.npy');B=np.load(P/'blurriness/candidate-material.npy');raw=np.load(P/'blurriness/raw-lens-material.npy');clear=np.load(P/'blurriness/clear-premultiplied.npy');body=(A[...,None]*B+clear).astype(np.float32);base=np.load(P/'blurriness/candidate-complete.npy');ref=np.asarray(Image.open('/evidence/apple-matches/public-settled-replay/media-target.png'),np.float32)[y0:y1,x0:x1]/255
xs,ys,dx,dy=points(case);sd,_,_,_=masks(case,xs,ys,dx,dy);fg=np.zeros(sd.shape,bool)
for aa,bb,cc,dd in case['foreground']:fg|=(xs>=aa)&(xs<=cc)&(ys>=bb)&(ys<=dd)
baseerr=float(np.mean(((base-ref)[fg]*255)**2));rows=[]
for i,m in enumerate([1.,1.1],6):
 ip=dict(p['icon']);ip['gamma']=(np.array(ip['gamma'])*m).tolist();col=icon_color(raw,ip,L);C=body.copy();C[sl]=C[sl]*(1-alpha[...,None])+col[sl]*alpha[...,None];err=float(np.mean(((C-ref)[fg]*255)**2));s=scores(C,ref,case);np.save(D/f'material-{i}-complete.npy',C);rows.append({'trial':i,'shape':'frozen legacy, original vector rejected','gamma_multiplier':m,'foreground_MSE':err,'baseline_foreground_MSE':baseerr,'accepted':err<baseerr,'scores':s})
# No numerical tie qualifies as visible improvement; original-vector input rejected.
accepted=[r for r in rows if r['accepted']];selected=base if not accepted else np.load(D/f'material-{accepted[0]["trial"]}-complete.npy');np.save(D/'FINAL-selected-complete.npy',selected)
out={'status':'NO_QUALIFIER' if not accepted else 'CANDIDATE_PENDING_VISUAL','original_vector_accepted':False,'original_vector_reason':'Correct foreground MSE 130.63246 exceeds 98.16660','rows':rows,'total_material_composites':8,'legacy_empirical_icon_background_dependency':not bool(accepted),'old_result_superseded':True,'new_rays':0};(D/'final-correction.json').write_text(json.dumps(out,indent=2)+'\n');print(json.dumps(out))
