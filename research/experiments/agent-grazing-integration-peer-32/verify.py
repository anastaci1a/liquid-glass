from pathlib import Path
import json,datetime,hashlib
import numpy as np
r=Path('/research/liquid-glass');o=Path(__file__).parent
p=json.loads((o/'protocol.json').read_text());end=datetime.datetime.fromisoformat(p['deadline'].replace('Z','+00:00'))
def check():assert datetime.datetime.now(datetime.timezone.utc)<end
check()
f=json.loads((r/'reconstruction/families/music-mini-player.json').read_text());old=json.loads((r/'research/experiments/miniplayer-closed-perimeter-25/protocol.json').read_text())['parameters'];rows=json.loads((r/'research/experiments/miniplayer-grazing-quadrature-27/result.json').read_text())['records'];L=88.5;R=f['geometry']['corner_radius'];b=f['geometry']['minor_half'];eta=old['eta'];assert old['kappa']==0 and old['index']==1.5
centers={}
for m in ['expanded','compact']:
 if m=='expanded':cy=json.loads((r/'reconstruction/studies/geometric-expanded-pipeline/summary.json').read_text())['geometry']['center'][1]
 else:
  c=json.loads((r/'.evidence-working/compact-geometry-01/a/case.json').read_text());q=json.loads((r/'reconstruction/studies/music-mini-compact-vector/review-round/pass-03.json').read_text())['parameters'];cy=c['center'][1]+L*q['shape_dy']
 centers[m]=cy
for d in rows:assert abs(d['edge']-(centers[d['member']]+(-1 if d['side']=='upper' else 1)*b*L))<1e-12
(o/'checkpoint.json').write_text(json.dumps({'verified_before_quadrature':True,'R':R,'minor_half':b,'eta':eta,'L':L,'centers':centers,'inner_offset':b-R,'at':datetime.datetime.now(datetime.timezone.utc).isoformat()},indent=2)+'\n')
out=[];points=0;quadratures=0;status='PASS_WITH_LIMITS'
for d in rows:
 values=[];cy=centers[d['member']];sgn=-1 if d['side']=='upper' else 1
 # On each rim, y=cy+sgn*L*((b-R)+R*sin(beta)).
 lo=max(d['row']-.5,cy-b*L);hi=min(d['row']+.5,cy+b*L)
 for n in [64,128]:
  check();quadratures+=1
  if hi<=lo:value=0.
  else:
   yy=np.sort(sgn*(np.array([lo,hi])-cy)/L);rho=(yy-(b-R))/R;assert np.min(rho)>0 and np.max(rho)<=1+1e-14
   # Exact projected edge is the integration limit, not an evaluated tangent ray.
   rho[np.abs(rho-1)<1e-14]=1
   beta=np.arcsin(rho);x,w=np.polynomial.legendre.leggauss(n);t=(beta[1]-beta[0])*x/2+beta.mean();cb=np.cos(t);sb=np.sin(t);c=cb/np.sqrt(cb*cb+(eta/R)**2*sb*sb);ct=np.sqrt(1-(1-c*c)/2.25);rs=((c-1.5*ct)/(c+1.5*ct))**2;rp=((1.5*c-ct)/(1.5*c+ct))**2;value=float((beta[1]-beta[0])/2*np.sum(w*(rs+rp)/2*L*R*cb));points+=n
  values.append(value)
 rec={**d,'GL64':values[0],'GL128':values[1],'difference_64_128':abs(values[1]-values[0]),'difference_root':abs(values[1]-d['adaptive'])};out.append(rec)
 if rec['difference_64_128']>1e-7 or rec['difference_root']>1e-7:status='STOP_DISCREPANCY';break
assert points<=3000 and quadratures<=24
(o/'result.json').write_text(json.dumps({'status':status,'records':out,'quadratures':quadratures,'scalar_points':points,'root_adaptive_reruns':0,'optical_rays_RGB_source_reads':0,'finished':datetime.datetime.now(datetime.timezone.utc).isoformat()},indent=2)+'\n')
print(status,points,quadratures,max(x['difference_root'] for x in out),max(x['difference_64_128'] for x in out))
