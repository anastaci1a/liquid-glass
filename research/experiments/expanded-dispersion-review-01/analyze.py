"""Saved-array chromatic identifiability review, not a dispersion renderer."""
from pathlib import Path
import datetime,json
import numpy as np
from extended_fit import Study
ROOT=Path(__file__).resolve().parents[3];OUT=Path(__file__).parent;WORK=ROOT/'.evidence-working/expanded-geometry-02';p=json.loads((OUT/'protocol.json').read_text());deadline=datetime.datetime.fromisoformat(p['deadline']);assert not (OUT/'result.json').exists();rows=[]
for k in ['a','b']:
 assert datetime.datetime.now(datetime.timezone.utc)<deadline
 s=Study(WORK/k);C=np.load(ROOT/f'research/experiments/expanded-geometry-02/h1-{k}.npz')['complete'];T=s.target_crop;m=np.load(WORK/f'{k}-masks.npz')['glass'];x0,y0,_,_=s.crop;text=np.zeros_like(m);text[326-y0:505-y0,875-x0:1258-x0]=True;text&=m;stats={}
 for name,mask in [('original_glass',m),('fixed_text',text)]:
  err=(C[mask].astype(float)-T[mask].astype(float))*255;neutral=err.mean(1,keepdims=True);chroma=err-neutral;t=T[mask];stats[name]=dict(pixels=int(mask.sum()),RGB_RMSE=float(np.sqrt(np.mean(err**2))),neutral_RMSE=float(np.sqrt(np.mean(neutral**2))),chroma_RMS=float(np.sqrt(np.mean(chroma**2))),chroma_fraction_of_squared_RGB_error=float(np.mean(chroma**2)/np.mean(err**2)),target_exact_achromatic_fraction=float(np.mean(np.ptp(t,axis=1)==0)),signed_RGB=err.mean(0).tolist());assert abs(np.mean(err**2)-np.mean(neutral**2)-np.mean(chroma**2))<1e-9
 rows.append(dict(reference=k,cohorts=stats))
(OUT/'result.json').write_text(json.dumps(dict(status='SPECTRAL_TRANSPORT_NOT_IDENTIFIED',observations=rows,new_rays=0,RGB_queries=0,images=0,filters=0,fits=0,finished_at=datetime.datetime.now(datetime.timezone.utc).isoformat(),limits=['Chromatic residual is not a measured wavelength response.','Strong A source colour, missing return geometry and illumination remain confounds.','Neutral B controls do not establish absence of physical dispersion.','No per-channel coefficients or spectral ray paths introduced.']),indent=2)+'\n');print(json.dumps(rows),flush=True)
