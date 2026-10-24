from common import *
import hashlib
from vector_foreground import coverage
assert not (P/'geometry-checkpoint.json').exists(),'No checkpoint repeat';gate(True)
f=RadiusBack();r=f.R
# Finite differences, rotational/radial fixture, mirrors and pose. No image or source sampling.
a=np.linspace(.03,.95,48);theta=np.arange(48)*.413;x=r*a*np.cos(theta);y=r*a*np.sin(theta)
h,hx,hy,inside=f.height_gradient(x,y);eps=1e-6
fdx=(f.height_gradient(x+eps,y)[0]-f.height_gradient(x-eps,y)[0])/(2*eps)
fdy=(f.height_gradient(x,y+eps)[0]-f.height_gradient(x,y-eps)[0])/(2*eps)
err=float(max(abs(fdx-hx).max(),abs(fdy-hy).max()));assert err<1e-8 and inside.all() and np.all(h>0)
charge('adapter_height_nested',8*len(x));bh,bx,by,bi=f.base.height_gradient(x/r,y/r)
np.testing.assert_array_equal(h,bh);np.testing.assert_array_equal(hx,bx/r);np.testing.assert_array_equal(hy,by/r)
assert f.maximum_height<2 and (1.5**2-1)*f.slope_bound**2<1
q=trace(f,x,y);m=trace(f,-x,-y);np.testing.assert_allclose(m['X'],-q['X'],atol=2e-14,rtol=0);np.testing.assert_allclose(m['Y'],-q['Y'],atol=2e-14,rtol=0)
class ScaleFixture:
 maximum_height=f.maximum_height*3;slope_bound=f.slope_bound
 def height_gradient(self,x,y):
  charge('adapter_height_nested',np.broadcast_arrays(x,y)[0].size);a,b,c,d=f.height_gradient(x/3,y/3);return a*3,b,c,d
 def boundary_mask(self,x,y):
  charge('adapter_boundary_nested',np.broadcast_arrays(x,y)[0].size);return f.boundary_mask(x/3,y/3)
scaled=trace(ScaleFixture(),x*3,y*3,D=6);np.testing.assert_allclose(scaled['X'],q['X']*3,atol=3e-14,rtol=0);np.testing.assert_allclose(scaled['Y'],q['Y']*3,atol=3e-14,rtol=0)
c=np.asarray(par['center']);pose=trace(f,((x*89+c[0])-c[0])/89,((y*89+c[1])-c[1])/89);np.testing.assert_allclose(pose['X'],q['X'],atol=3e-14,rtol=0);np.testing.assert_allclose(pose['Y'],q['Y'],atol=3e-14,rtol=0)
unit=trace(f,x,y,n=1);np.testing.assert_allclose(unit['X'],x,atol=1e-15,rtol=0)
edge=trace(f,np.array([r,-r,0,0]),np.array([0,0,r,-r]));assert edge['boundary_unresolved'].all() and np.isnan(edge['X']).all()
miss=trace(f,np.array([r+.1]),np.array([0.]));assert miss['complete'].all() and not miss['inside'].any()
# All original reference masks use case geometry, never this predicted footprint.
rows=[]
for k in ['a','b']:
 gate(True);s=study(k,True);recipe=json.loads((ROOT/'reconstruction/studies/music-search-vector/review-round/pass-03.json').read_text());assert s.L==89
 for name,digest in s.case['source_sha256'].items():assert hashlib.sha256((WORK/k/name).read_bytes()).hexdigest()==digest
 assert s.case['foreground_styles']==json.loads((ROOT/'reconstruction/studies/music-search-vector/paired/accepted.json').read_text())['foreground_styles']
 charge('mask_geometry',s.valid.size);*_,(sd,_,_)=s.shape(s.x,s.y,recipe['parameters']);known=cv2.imread(str(WORK/k/'known.png'),0)>0;x0,y0,x1,y1=s.crop;ext=(sd>1.5/s.L)&(sd<.20)&known[y0:y1,x0:x1]
 foreground=np.zeros_like(s.valid);deps=foreground.copy();X=s.x*s.L+s.case['center'][0];Y=s.y*s.L+s.case['center'][1]
 for a,b,c,d in s.case.get('exterior_exclusions',[]):ext&=~((X>=a)&(X<=c)&(Y>=b)&(Y<=d))
 assert len(s.foreground_layers)==1 and not s.transmission_layers
 layer=s.case['foreground_layers'][0];a,b,c,d=layer['box'];foreground[b-y0:d-y0,a-x0:c-x0]=True;deps|=foreground
 alpha=coverage(s.folder,layer);style=s.case['foreground_styles']['search.svg'];alpha=alpha*style['opacity'];color=np.asarray(style['color'],np.float32)
 controls=[]
 for value in [.2,.8]:
  backing=np.full((y1-y0,x1-x0,3),value,np.float32);expected=(backing[b-y0:d-y0,a-x0:c-x0]*(1-alpha[...,None])+color*alpha[...,None]).astype(np.float32);out=s.apply_foreground(backing.copy());ledger['foreground_controls']+=1;exact=np.array_equal(expected,out[b-y0:d-y0,a-x0:c-x0]);assert exact and np.array_equal(out[~foreground],backing[~foreground]);controls.append(exact)
 counts={name:int(mask.sum()) for name,mask in [('glass',s.valid),('rim',s.rim),('held',s.held),('interior',s.valid&~s.rim),('exterior',ext),('foreground',foreground)]};assert [counts[x] for x in ['glass','rim','held','interior','foreground']]==[14904,8364,4763,6540,9216]
 required=s.valid|s.rim|s.held|ext|deps
 np.savez_compressed(P/f'{k}-masks.npz',glass=s.valid,rim=s.rim,held=s.held,interior=s.valid&~s.rim,exterior=ext,foreground=foreground,dependencies=deps,required=required)
 actual=hashlib.sha256(json.dumps(s.case,sort_keys=True).encode()).hexdigest();rows.append(dict(case=k,counts=counts,case_fingerprint=actual,historical_recipe_fingerprint=recipe['case_sha256'][k],case_fingerprint_exact=actual==recipe['case_sha256'][k],foreground_small_backing_controls=controls))
np.savez_compressed(P/'fixture-paths.npz',x=x,y=y,**q)
gate(True);save('geometry-checkpoint.json',dict(status='PASS_GEOMETRY_AND_CANONICAL_INPUTS',utc=utc(),finite_difference_max=err,maximum_height=f.maximum_height,slope_bound=f.slope_bound,clearance_lower=float(np.sqrt(1-1.25*f.slope_bound**2)),crease_unresolved=True,mirrors=True,uniform_scale=True,pose=True,base_circle_chain_rule_exact=True,rows=rows,ledger=ledger.copy(),historical_cached_M_C='No compatible material/complete cache restored; no historical optical baseline rerender. Historical verification scores remain comparator metadata.'))
print('CHECKPOINT_PASS',rows,ledger,flush=True)
