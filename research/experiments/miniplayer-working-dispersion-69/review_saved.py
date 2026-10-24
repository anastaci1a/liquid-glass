"""Fixed saved-color cohorts; never spectral rays or RGB channel fitting."""
from pathlib import Path
import json,datetime,hashlib
import numpy as np
from PIL import Image
ROOT=Path(__file__).resolve().parents[3];OUT=Path(__file__).resolve().parent
P=json.loads((OUT/'protocol.json').read_text());END=datetime.datetime.fromisoformat(P['deadline'].replace('Z','+00:00'))
assert not (OUT/'result.json').exists(),'No repeated assessment'
observations=0;decoded=0;rows=[];bindings={}
def note_array(a):
 global decoded
 decoded+=a.nbytes;assert decoded<=P['caps']['decoded_array_bytes']
 return a
for member in ['expanded','compact']:
 work=ROOT/('.evidence-working/expanded-geometry-02' if member=='expanded' else '.evidence-working/compact-geometry-01')
 base=ROOT/('research/experiments/expanded-contrast-guard-02' if member=='expanded' else 'research/experiments/miniplayer-shared-transfer-06')
 for k in ['a','b']:
  assert datetime.datetime.now(datetime.timezone.utc)<END
  case=json.loads((work/k/'case.json').read_text());x0,y0,x1,y1=case['crop'];H,W=y1-y0,x1-x0
  T=note_array(np.asarray(Image.open(work/k/'target.png').convert('RGB').crop((x0,y0,x1,y1)),np.float32)/255)
  f=ROOT/f'research/experiments/miniplayer-incident-material-20/{member}-{k}-factor0.5.npz';z=np.load(f);C=note_array(z['complete']);coverage=note_array(z['coverage'])
  rawpath=ROOT/f'research/experiments/miniplayer-inverse-forward-18/{member}-{k}-light4.npz'
  raw=note_array(np.load(rawpath)['raw_source'])
  maskpath=work/f'{k}-masks.npz' if member=='expanded' else ROOT/f'research/experiments/compact-geometry-01/{k}-masks.npz'
  mask=note_array(np.load(maskpath)['glass'])&(coverage==1)
  crops=json.loads((ROOT/'research/experiments/miniplayer-outline-light-07/protocol.json').read_text())['fixed_crops'][member]
  for name,(a,b,c,d) in crops.items():
   cohort=np.zeros((H,W),bool);cohort[b-y0:d-y0,a-x0:c-x0]=True;cohort&=mask
   yy,xx=np.nonzero(cohort);n=len(yy);observations+=6*n;assert observations<=P['caps']['saved_pixel_observations']
   if n==0:continue
   target=T[yy,xx].astype(float);complete=C[yy,xx].astype(float);source=raw.reshape(H,2,W,2,3)[yy,:,xx,:,:].reshape(n,4,3)
   assert np.isfinite(source).all()
   residual=(complete-target)*255
   chroma=lambda v:float(np.sqrt(np.mean((v-v.mean(axis=-1,keepdims=True))**2))*255)
   rows.append(dict(member=member,reference=k,crop=name,pixels=n,target_chroma_RMSE=chroma(target),retained_source_chroma_RMSE=chroma(source),signed_residual_RGB=residual.mean(0).tolist(),residual_RGB_RMSE=float(np.sqrt(np.mean(residual**2))),residual_chroma_RMSE=chroma(complete-target),channel_displacement_identified=False))
  for file in [work/k/'case.json',work/k/'target.png',f,rawpath,maskpath]:bindings[str(file.relative_to(ROOT))]=hashlib.sha256(file.read_bytes()).hexdigest()
result=dict(status='DISPERSION_UNIDENTIFIED_NOT_ABSENT',finished=datetime.datetime.now(datetime.timezone.utc).isoformat(),records=rows,ledger=dict(saved_pixel_observations=observations,decoded_array_bytes=decoded,rays=0,heights=0,source_queries=0,filters=0,composites=0,fits=0),reason='Residual chroma is not a measured inter-channel feature displacement; colored source, conditional correspondence, ordinary PSF, scalar geometry, response and missing illumination remain confounds.',model_selected=False,source_confidence='Conditional original temporal mosaics, not independent hidden truth.',bindings=bindings)
(OUT/'result.json').write_text(json.dumps(result,indent=2,allow_nan=False)+'\n')
print(json.dumps(dict(status=result['status'],ledger=result['ledger'])),flush=True)
