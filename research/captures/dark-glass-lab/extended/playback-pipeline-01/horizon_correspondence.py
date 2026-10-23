from pathlib import Path
import json,numpy as np
from scipy.optimize import brentq
D=Path('/evidence/extended/playback-pipeline-01/horizon-audit');a=json.loads((D/'result.json').read_text());z=np.load('/evidence/extended/geometric-playback-inferred/radial-geometry.npz');r=z['r'];sr=z['X'];m,c=a['source_line_coefficients'];rows=[]
for case in a['all_peak_candidates']:
 angle=case['angle'];theta=np.deg2rad(angle);q=(c+m*960-542)/(245*(np.sin(theta)-m*np.cos(theta)));v=sr-q;cross=np.flatnonzero(v[:-1]*v[1:]<0);pred=[]
 for k in cross:
  rr=float(r[k]-v[k]*(r[k+1]-r[k])/(v[k+1]-v[k]));sign=1 if v[k+1]>v[k] else -1
  if .70<=rr<=.994:
   pp=[x for x in case['branches']['Apple'] if x['sign']==sign and abs(x['r']-rr)*245<=10]
   pp=sorted(pp,key=lambda x:abs(x['r']-rr));pred.append(dict(r=rr,branch='normal' if sign==1 else 'reversed',target_candidates=pp,ambiguous=len(pp)!=1,nearest_delta_native_px=None if not pp else (pp[0]['r']-rr)*245))
 rows.append(dict(angle=angle,source_radial_crossing=q,predicted=pred))
result=dict(rows=rows,assumptions='Single source horizon approximate line .42px RMS/1.20px max; peak candidates retained within10nativepx, same polarity. Nearest is diagnostic, not certified correspondence.',new_rays=0,new_fits=0)
(D/'correspondence.json').write_text(json.dumps(result,indent=2)+'\n');print(json.dumps(result))
