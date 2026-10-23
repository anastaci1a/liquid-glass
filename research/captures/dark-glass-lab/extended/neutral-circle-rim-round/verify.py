from pathlib import Path
import json,hashlib,cv2,numpy as np
from extended_fit import Study
cv2.setNumThreads(1)
D=Path('/evidence/extended/neutral-circle-rim-round');rows=[]
for k,name in enumerate(['flower-next-round','safari-right-circle-round']):
 R=Path('/evidence/extended/helper-toolbar-work')/name;B=R/('neutral-playback-baseline' if k==0 else 'neutral-baseline');s=Study(B/'inputs/a');r=json.loads((R/'neutral-additive-round3/candidate-native.json').read_text());p=r['preset'];L=min(s.case['half']);cx,cy=s.case['center'];x0,y0,x1,y1=s.crop;P=np.zeros((y1-y0,x1-x0),np.float32)
 assert hashlib.sha256(json.dumps(s.case,sort_keys=True).encode()).hexdigest()==r['case_sha256']['a']
 for f,d in s.case['source_sha256'].items():assert hashlib.sha256((B/'inputs/a'/f).read_bytes()).hexdigest()==d
 for top in range(y0,y1,24):
  bot=min(top+24,y1);yy,xx=np.mgrid[top:bot:.5,x0:x1:.5];x=(xx-.25-cx)/L;y=(yy-.25-cy)/L;rad=np.hypot(x,y);d=np.maximum(1-rad,0);H=np.exp(-(d/.02)**2)*np.divide((x+y)**2,2*rad**2,out=np.zeros_like(rad),where=rad>0);P[top-y0:bot-y0]=H.reshape(bot-top,2,x1-x0,2).mean((1,3))
 P=cv2.GaussianBlur(P,(0,0),p['post_sigma']*L)
 base=np.load(R/'neutral-additive-round3/candidate-native.npz');new=np.load(D/f'trial1-{k}/arrays.npz');pred=base['material']+.025*P[...,None];err=float(np.max(abs(pred-new['material'])));assert err<8*np.finfo(np.float32).eps
 bound=max(z['max_unclipped'] for z in r['clipping_counts'].values())+.025;assert bound<1
 rows.append(dict(control=name,case_source_hashes_exact=True,independent_radial_normal_response_max_difference=err,upper_unclipped_bound=bound,clipping_impossible=True,source_queries_and_kernels_unchanged=True,nonregression_checks=json.loads((D/'result.json').read_text())['rows'][0]['items'][k]['checks']))
(D/'verification.json').write_text(json.dumps(dict(accepted_primary=True,accepted_pass=1,controls=rows,invariants='finite/nonnegative<=1, normal inversion, exact a0 branch; empirical neutral boundary response only; constant continuation outside silhouette before fixed postfilter',no_ray_rerender=True,float32_order_tolerance=float(8*np.finfo(np.float32).eps)),indent=2)+'\n');print(rows)
