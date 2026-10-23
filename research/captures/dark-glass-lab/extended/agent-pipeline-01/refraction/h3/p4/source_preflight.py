"""H1 native 2x2 path/texel proof. ZERO RGB access. No renderer replacement."""
from pathlib import Path
import sys,json,time,hashlib
import numpy as np,cv2
P=Path('/evidence/extended/agent-pipeline-01');O=P/'refraction/h3/p4';sys.path.insert(0,str(P/'code'))
from expanded_surface import ExpandedHarmonicBack
from geometric_optics import trace_flat_front_orthographic
G=json.loads((O/'geometry-checkpoint.json').read_text())['scene'];s=ExpandedHarmonicBack(tuple(G['surface_half']),G['surface_radius'],power=G['power']);L=G['original_reference_L'];cx,cy=G['center']
result={'status':'RUNNING','RGB_samples':0,'native_images':0,'AA':2,'source_kernel':'zero added scattering; exact four bilinear texels, conservative including zero weights','deadline':1792657200.,'cases':{}}
for key in ['a','b']:
 case=json.loads((P/f'inputs/{key}/case.json').read_text());known=cv2.imread(str(P/f'inputs/{key}/known.png'),0)>0
 masks=np.load(P/f'historical-{key}-masks.npz');x0,y0,x1,y1=case['crop'];H=y1-y0;W=x1-x0
 fg=np.zeros((H,W),bool)
 for layer in case['foreground_layers']:
  a,b,c,d=layer['box'];fg[max(0,b-y0):min(H,d-y0),max(0,a-x0):min(W,c-x0)]=True
 required_guard=masks['glass']|masks['exterior']|fg
 Xmap=np.empty((H*2,W*2),np.float64);Ymap=np.empty_like(Xmap);inside=np.zeros_like(Xmap,dtype=bool);support=np.zeros_like(inside);complete=np.zeros_like(inside)
 counts={'emitted_subrays':0,'whole':0,'all_original_guard_subrays':0,'required_union':0,'unsupported_required':0,'unsupported_whole':0,'unsupported_glass':0,'unsupported_exterior':0,'unsupported_foreground':0,'incomplete_required':0};examples=[]
 for row in range(0,H,12):
  if time.time()>result['deadline']:raise TimeoutError('H1 deadline')
  bottom=min(row+12,H)
  yy,xx=np.mgrid[y0+row:y0+bottom:.5,x0:x1:.5]
  q=trace_flat_front_orthographic(s,(xx-.25-cx)/L,(yy-.25-cy)/L,1.5,2.)
  X=q['X']*L+cx;Y=q['Y']*L+cy;finite=np.isfinite(X)&np.isfinite(Y)
  ix=np.floor(np.where(finite,X,0)).astype(int);iy=np.floor(np.where(finite,Y,0)).astype(int)
  inbounds=finite&(ix>=0)&(iy>=0)&(ix+1<known.shape[1])&(iy+1<known.shape[0]);ok=np.zeros_like(inbounds)
  j=inbounds;ok[j]=known[iy[j],ix[j]]&known[iy[j]+1,ix[j]]&known[iy[j],ix[j]+1]&known[iy[j]+1,ix[j]+1]
  expand=lambda m:np.repeat(np.repeat(m[row:bottom],2,axis=0),2,axis=1)
  whole=q['inside'];guard=expand(required_guard);req=whole|guard;bad=req&~ok
  counts['emitted_subrays']+=X.size;counts['whole']+=int(whole.sum());counts['all_original_guard_subrays']+=int(guard.sum());counts['required_union']+=int(req.sum());counts['unsupported_required']+=int(bad.sum());counts['unsupported_whole']+=int((whole&~ok).sum());counts['incomplete_required']+=int((req&~q['complete']).sum())
  for label,m in [('glass',masks['glass']),('exterior',masks['exterior']),('foreground',fg)]:counts['unsupported_'+label]+=int((expand(m)&~ok).sum())
  if bad.any() and len(examples)<12:
   for v,u in np.argwhere(bad)[:12-len(examples)]:examples.append({'output':[float(xx[v,u]-.25),float(yy[v,u]-.25)],'query':[float(X[v,u]),float(Y[v,u])],'inside':bool(whole[v,u]),'complete':bool(q['complete'][v,u])})
  sl=slice(row*2,bottom*2);Xmap[sl]=X;Ymap[sl]=Y;inside[sl]=whole;support[sl]=ok;complete[sl]=q['complete']
 np.savez(O/f'{key}-native-paths.npz',X=Xmap,Y=Ymap,inside=inside,support=support,complete=complete)
 result['cases'][key]={'counts':counts,'unsupported_examples':examples,'source_known_sha256':hashlib.sha256((P/f'inputs/{key}/known.png').read_bytes()).hexdigest(),'query_bounds':[float(np.nanmin(Xmap)),float(np.nanmin(Ymap)),float(np.nanmax(Xmap)),float(np.nanmax(Ymap))],'unscored_presentation_unknown_subrays':int((~support&~np.repeat(np.repeat(required_guard,2,0),2,1)&~inside).sum())}
 (O/'source-preflight.json').write_text(json.dumps(result,indent=2,allow_nan=False))
result['status']='PASS_REQUIRED_SOURCE' if all(not(v['counts']['unsupported_required'] or v['counts']['incomplete_required']) for v in result['cases'].values()) else 'STOP_UNSUPPORTED_REQUIRED_SOURCE'
result['finished_unix']=time.time();(O/'source-preflight.json').write_text(json.dumps(result,indent=2,allow_nan=False));print(json.dumps(result))
