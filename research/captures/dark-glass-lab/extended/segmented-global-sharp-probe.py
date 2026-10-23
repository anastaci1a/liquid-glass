"""Coarse sharp registration before local refinement; never render blurred text."""
exec(open('/evidence/extended/segmented-chroma-geometry-probe.py').read().split('for seed,file in ')[0].replace("out=folder/'chroma-geometry-probe'","out=folder/'global-sharp-probe'"))
from scipy.optimize import minimize
allrows=[]
for seed in ['current','flat-core']:
 p=copy.deepcopy(json.loads((folder/'clear-local-probe/measured-outline-1.json').read_text())['parameters']);p.update(sigma=0.,post_sigma=0.,blur_transition=0.,gamma=1.,prism_x=0.,prism_y=0.)
 if seed=='flat-core':p.update(c5=.02,c6=0.,core_y=.11)
 expected=target[b:d,a:c].ravel()[idx];grid=[]
 for power in np.linspace(-.1,.18,15):
  for shift in np.linspace(-.5,.15,66):
   q={**p,'core_x':float(power),'prism_x':float(shift)};X,Y,*_=A.geometry_field(x,y,q);alpha=cv2.remap(source,(X*A.L+A.case['center'][0]).astype(np.float32),(Y*A.L+A.case['center'][1]).astype(np.float32),cv2.INTER_LINEAR).ravel();grid.append((float(np.mean((alpha-expected)**2)),q))
 grid.sort(key=lambda r:r[0]);(out/f'{seed}-grid.json').write_text(json.dumps([dict(loss=l,parameters=q) for l,q in grid],indent=2)+'\n');print('Best grid',seed,[(v[0],v[1]['core_x'],v[1]['prism_x']) for v in grid[:5]],flush=True)
 for rank,(_,p) in enumerate(grid[:3]):
  selectedkeys=[*[f'c{i}' for i in range(7)],'core_x','core_y','prism_x','prism_y','cap_normal_gain','tangent','tangent_band','coupling'];lohi=[(-.65,.4) if k.startswith('prism') else A.parameter_bounds(k) for k in selectedkeys];lo,hi=np.array(lohi).T
  def residual(v):
   q={**p,**dict(zip(selectedkeys,map(float,v)))};X,Y,*_=A.geometry_field(x,y,q);alpha=cv2.remap(source,(X*A.L+A.case['center'][0]).astype(np.float32),(Y*A.L+A.case['center'][1]).astype(np.float32),cv2.INTER_LINEAR).ravel();return (alpha-expected).astype(float)
  def jac(v):
   h=.0007;J=np.empty((len(idx),len(v)))
   for i in range(len(v)):
    up=v.copy();dn=v.copy();up[i]=min(hi[i],v[i]+h);dn[i]=max(lo[i],v[i]-h);J[:,i]=(residual(up)-residual(dn))/(up[i]-dn[i])
   return J
  t=time.time();fit=least_squares(residual,np.clip([p[k] for k in selectedkeys],lo+1e-8,hi-1e-8),jac=jac,bounds=(lo,hi),x_scale='jac',max_nfev=180,ftol=1e-9,xtol=1e-8,gtol=1e-8);p.update(zip(selectedkeys,map(float,fit.x)));_,co=A.fit(p);scores=[q.scores(q.render(p,co)) for q in [A,B]];support=[supported(q,coverage_report(q,p)) for q in [A,B]];row=dict(seed=seed,rank=rank,parameters=p,material=co.tolist(),scores=scores,supported=support,beats_published_A=scores[0]['loss']<=old['scores']['loss'] and scores[0]['glass']['rmse']<=old['scores']['glass']['rmse'],registration_loss=float(np.mean(fit.fun**2)),seconds=time.time()-t);allrows.append(row);(out/f'{seed}-{rank}.json').write_text(json.dumps(row,indent=2)+'\n');A.comparison(A.render(p,co),out/f'{seed}-{rank}.png',p,context_completed=True);print(json.dumps(dict(seed=seed,rank=rank,loss=[q['loss'] for q in scores],glass=[q['glass']['rmse'] for q in scores],beats_published=row['beats_published_A'],prism=[p['prism_x'],p['prism_y']],core=[p['core_x'],p['core_y']])),flush=True)
(out/'report.json').write_text(json.dumps(dict(rows=allrows,baseline=old,limits='Sharp-only global prism/power registration followed by vector-boundary refinement. Original inputs and public accepted state unchanged. Both A gates still required; no Apple-model identification.'),indent=2)+'\n')
