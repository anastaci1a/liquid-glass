"""Read saved coordinates only. No geometry/render imports or field calls."""
from pathlib import Path
import json,hashlib,datetime
import numpy as np
P=Path(__file__).resolve().parent;Q=P.parent/'agent-navigation-spline-03';R=P.parents[3]/'liquid-glass'/'research'/'experiments'/'navigation-geometry-01'
proto=json.loads((P/'protocol.json').read_text());assert datetime.datetime.now(datetime.timezone.utc)<datetime.datetime.fromisoformat(proto['deadline'].replace('Z','+00:00'))
z=np.load(Q/'native-paths.npz');b=json.loads((Q/'native-reservation.json').read_text())['bounds'];a,r,L=b['half'][0],b['radius'],b['L'];s=a-r
x,y,X,Y,inside,complete=[z[k] for k in ['x','y','X','Y','inside','complete']];dx=float(x[0,1]-x[0,0]);dy=float(y[1,0]-y[0,0]);valid=inside&complete

def stats(v,m):
 w=np.asarray(v)[m];w=w[np.isfinite(w)]
 return {'n':int(w.size),'min':float(w.min()),'median':float(np.median(w)),'max':float(w.max()),'rms':float(np.sqrt(np.mean(w*w)))} if w.size else {'n':0}
# Centered native subray stencils, excluded from caps/joins when assigned straight.
core=(slice(1,-1),slice(1,-1));xc,yc=x[core],y[core]
stencil=valid[core]&valid[1:-1,:-2]&valid[1:-1,2:]&valid[:-2,1:-1]&valid[2:,1:-1]
straight=stencil&(abs(xc)<s-2*dx)
cap=stencil&(abs(xc)>s+2*dx)
Jxx=(X[1:-1,2:]-X[1:-1,:-2])/(2*dx);Jxy=(X[2:,1:-1]-X[:-2,1:-1])/(2*dy)
Jyx=(Y[1:-1,2:]-Y[1:-1,:-2])/(2*dx);Jyy=(Y[2:,1:-1]-Y[:-2,1:-1])/(2*dy)
h=-z['back'][...,2];hxx=(h[1:-1,2:]-2*h[core]+h[1:-1,:-2])/dx**2
rows={}
for name,m in [('straight',straight),('caps',cap)]:
 rows[name]={k:stats(v,m) for k,v in [('Jxx',Jxx),('Jxy',Jxy),('Jyx',Jyx),('Jyy',Jyy),('cached_height_dxx',hxx)]}
 rows[name]['dx_native']=stats((X-x)[core]*L,m);rows[name]['dy_native']=stats((Y-y)[core]*L,m)
# Fixed original-frame crop memberships are analytical selection, not RGB queries.
framex=x*L+b['center'][0];framey=y*L+b['center'][1]
crops={}
for name,box in [('left_cap',[320,535,650,765]),('upper_body',[650,530,1270,595]),('lower_body',[650,690,1270,765])]:
 u,v,w,t=box;mask=(framex>=u)&(framex<w)&(framey>=v)&(framey<t)
 crops[name]={'box':box,'subrays':int(mask.sum()),'lens':int((mask&inside).sum()),'straight_miss':int((mask&~inside).sum()),'dx_lens_px':stats((X-x)*L,mask&valid),'dy_lens_px':stats((Y-y)*L,mask&valid),'dx_miss_px':stats((X-x)*L,mask&~inside)}
sections=[]
for target_y in [0,-.75,.75]:
 iy=int(np.argmin(abs(y[:,0]-target_y)));m=valid[iy]& (abs(x[iy])<s-2*dx)
 sections.append({'target_y_L':target_y,'saved_y_L':float(y[iy,0]),'row':iy,'straight_dx_px':stats((X-x)[iy]*L,m),'straight_dy_px':stats((Y-y)[iy]*L,m)})
coverage=np.load(Q/'a-support.npz')['coverage'];old=np.load(R/'a-raw.npz')['coverage']
H=.1381819202620016;M=.6732687148645161;n=1.5
emax=(1/np.sqrt(n*n-1)-M)/(M+2*H/a)
inputs=[Q/'native-paths.npz',Q/'a-support.npz',Q/'native-reservation.json',Q/'sections.npz',R/'a-raw.npz',R/'surface-sections.json']
result={'status':'SAVED_ANALYSIS_COMPLETE_NO_IMPLEMENTATION','finished':datetime.datetime.now(datetime.timezone.utc).isoformat(),'half':b['half'],'radius':r,'L':L,'straight_half_length_L':s,'native_grid_shape':list(x.shape),'step_L':[dx,dy],'stencils':rows,'crops':crops,'sections':sections,'coverage':{'old_H1_exact':bool(np.array_equal(old,coverage)),'zero':int((coverage==0).sum()),'partial':int(((coverage>0)&(coverage<1)).sum()),'full':int((coverage==1).sum())},'source_coordinate_conversion_max_error_px':{'X':float(np.max(abs(z['source_X']-(X*L+b['center'][0])))),'Y':float(np.max(abs(z['source_Y']-(Y*L+b['center'][1]))))},'symbolic_bound_constants':{'H':H,'M':M,'a':a,'strict_epsilon_absolute_upper_from_slope':float(emax),'not_a_selected_parameter':True},'new_rays':0,'new_height_evaluations':0,'RGB_queries':0,'filters':0,'images':0,'fits':0,'inputs_sha256':{p.parent.name+'/'+p.name:hashlib.sha256(p.read_bytes()).hexdigest() for p in inputs}}
(P/'result.json').write_text(json.dumps(result,indent=2,allow_nan=False)+'\n');print(json.dumps(result,indent=2))
