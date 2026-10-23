"""Convex decreasing normal displacement: no oscillating spline folds.

a(d)=sum w_j max(1-d/b_j,0)^3, w_j>=0. Hence a'>=not: a'<=0,
a''>=0 and the normal source-coordinate derivative1+a' crosses zero at most
once (where defined). This is a restricted optical map, not an Apple solid.
"""
exec(open('/evidence/extended/segmented-selected-state-sharp-probe.py').read().split('for scale in [')[0].replace("out=folder/'selected-state-sharp-probe'","out=folder/'convex-clear-probe'"))
class Convex(Selected):
 def geometry_field(self,x,y,p):
  q={**p,'spline':False,'amplitude':0.,'tangent':0.,'coupling':0.,'cap_join_width':0.,'cap_normal_gain':0.};X,Y,d,J=super().geometry_field(x,y,q);*_,half,R,(sd,nx,ny)=self.shape(x,y,q);a=sum(p[f'm{i}']*np.maximum(1-d/band,0)**3 for i,band in enumerate([.05,.1,.2,.4,.8,1.]));a*=1+p.get('mixture_cap_gain',0.)*nx*nx;return X-a*nx,Y-a*ny,d,J
rows=[]
for scale in [1.,1.125,1.1875]:
 A=Convex(folder,scale);B=Convex(folder/'second-observation',scale);source=np.clip((A.source[:,:,0]-A.source[:,:,1])/.65,0,1);target=np.clip((A.target[:,:,0]-A.target[:,:,1])/.65,0,1);a,b,c,d=A.crop;rng=np.random.default_rng(222);near=cv2.dilate((target>.05).astype(np.uint8),np.ones((21,21),np.uint8));general=np.flatnonzero(A.valid);special=np.flatnonzero(A.valid&(near[b:d,a:c]>0));rng.shuffle(general);rng.shuffle(special);idx=np.unique(np.r_[general[:2500],special[:3500]]);x=A.x.ravel()[idx];y=A.y.ravel()[idx]
 for seed in ['middle','broad']:
  p=copy.deepcopy(old['parameters']);p.update(sigma=0.,post_sigma=0.,blur_transition=0.,gamma=1.,shape_dx=0.,shape_dy=0.,half_x_delta=0.,half_y_delta=0.,radius_delta=0.,cap_join_width=0.,core_x=0.,core_y=0.,mixture_cap_gain=0.)
  p.update({f'm{i}':(.55 if i==(3 if seed=='middle' else 4) else .001) for i in range(6)})
  keys=[*[f'm{i}' for i in range(6)],'core_x','core_y','mixture_cap_gain'];lo,hi=np.array([(0.,2.) if k.startswith('m') and k[1:].isdigit() else (-.75,2.) if k=='mixture_cap_gain' else (-.2,.18) for k in keys]).T
  for level,sigma in enumerate([5.,2.,.5,0.],1):
   S=cv2.GaussianBlur(source,(0,0),sigma) if sigma else source;T=cv2.GaussianBlur(target,(0,0),sigma) if sigma else target;expected=T[b:d,a:c].ravel()[idx];calls=0;t=time.time()
   def residual(v):
    global calls
    calls+=1;q={**p,**dict(zip(keys,map(float,v)))};X,Y,*_=A.geometry_field(x,y,q);pred=cv2.remap(S,(X*A.L+A.case['center'][0]).astype(np.float32),(Y*A.L+A.case['center'][1]).astype(np.float32),cv2.INTER_LINEAR).ravel();return (pred-expected).astype(float)
   def jac(v):
    h=.0007;J=np.empty((len(idx),len(v)))
    for i in range(len(v)):
     up=v.copy();dn=v.copy();up[i]=min(hi[i],v[i]+h);dn[i]=max(lo[i],v[i]-h);J[:,i]=(residual(up)-residual(dn))/(up[i]-dn[i])
    return J
   fit=least_squares(residual,np.clip([p[k] for k in keys],lo+1e-8,hi-1e-8),jac=jac,bounds=(lo,hi),x_scale='jac',max_nfev=180,ftol=1e-9,xtol=1e-8,gtol=1e-8);p.update(zip(keys,map(float,fit.x)));_,co=A.fit(p);scores=[s.scores(s.render(p,co)) for s in [A,B]];row=dict(content_scale=scale,seed=seed,level=level,registration_objective_sigma=sigma,renderer_sigma=0.,renderer_post_sigma=0.,parameters=p.copy(),material=co.tolist(),scores=scores,supported=[supported(s,coverage_report(s,p)) for s in [A,B]],beats_published_A=scores[0]['loss']<=old['scores']['loss'] and scores[0]['glass']['rmse']<=old['scores']['glass']['rmse'],registration_loss=float(np.mean(fit.fun**2)),evaluations=calls,seconds=time.time()-t);rows.append(row);(out/f'{scale}-{seed}-{level}.json').write_text(json.dumps(row,indent=2)+'\n');print(json.dumps(dict(scale=scale,seed=seed,level=level,loss=[q['loss'] for q in scores],glass=[q['glass']['rmse'] for q in scores],beats_published=row['beats_published_A'],calls=calls)),flush=True)
   if level==4:A.comparison(A.render(p,co),out/f'{scale}-{seed}.png',p,context_completed=True)
(out/'report.json').write_text(json.dumps(dict(rows=rows,baseline=old,limits='One-fold convex decreasing normal profile; fixed measured silhouette, rendering blurZERO. Registration filtering affects the objective only. Selected-caption size is an optional explicit UI-content hypothesis, not refraction or an identified Apple rule. Original files/accepted state unchanged.'),indent=2)+'\n')
