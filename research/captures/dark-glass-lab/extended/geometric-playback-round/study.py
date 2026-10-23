"""G01: three bounded geometric proposals, no image optimization or blur."""
import os,json,time,hashlib
from pathlib import Path
import cv2,numpy as np
from PIL import Image,ImageDraw
from geometric_optics import CircularBevel,trace_flat_front_orthographic
from playback_replay import composite
from settled import icon_color,mapping
from reproduce import CASES,scores
os.umask(2);cv2.setNumThreads(1)
D=Path('/evidence/extended/geometric-playback-round');R=Path('/evidence/extended/playback-short-round/pass-03');INPUT=Path('/evidence/apple-matches/public-settled-replay');REC=json.loads((R/'replay-record.json').read_text());p=REC['recipe'];case=CASES['media'];L=min(case['half']);x0,y0,x1,y1=case['crop'];deadline=Path('/evidence/../liquid-glass-review/geometric-playback-round/experiment-01.md')
# The declaration lives outside this container mount. Record its original start,
# not the current script start, and never extend the wall budget.
START=1792638898.6595252 # 2026-10-22T03:14:58.659525Z
DEADLINE=START+1200
if time.time()>DEADLINE:raise RuntimeError('G01 wall budget expired before execution')
for n,digest in REC['input_sha256'].items():assert hashlib.sha256((INPUT/n).read_bytes()).hexdigest()==digest
source=np.asarray(Image.open(INPUT/'media-source.png'),float)/255;target=np.asarray(Image.open(INPUT/'media-target.png'),np.float32)/255;Mold=np.load(R/'candidate-material.npy');Cold=composite(source,case,p,Mold,1)
# Nuisance: keep exactly the historical calculated foreground color and alpha;
# do not use its material/blur for new transmission or calculate a new icon fit.
icon=icon_color(Mold,p['icon'],L);ia,ib,ic,id=[int(round(v*L+case['center'][i%2])) for i,v in enumerate(p['icon']['box_over_L'])];alpha=np.asarray(Image.open('/workspace/docs/liquid-glass/experiments/reconstruction/playback-mask.png'),float)/255
rects=[('bottom-left',[690,570,910,810]),('top-left',[690,290,910,530]),('upper-right-crossings',[1025,320,1245,560])]
rr=np.linspace(0,1,16385);prior=mapping(rr,np.zeros_like(rr),p)[0];prior_j=np.gradient(prior,rr);fold=rr[prior_j<0];geometry=[]
for name,s in [('narrow-bevel',CircularBevel(.6,.02)),('broad-bevel',CircularBevel(.3,.04))]:
 q=trace_flat_front_orthographic(s,rr,np.zeros_like(rr),1.5,2);jac=np.gradient(q['X'],rr);geometry.append(dict(name=name,surface=s.__dict__,radial_min_jacobian=float(jac.min()),edge_displacement=float(1-q['X'][-1]),maximum_height=s.maximum_height,slope_bound=s.slope_bound))
# Third surface: maximum nonfold depth within the same core=.6,p3 family,
# chosen ONLY by target-independent geometric Jacobian safety margin .05.
lo,hi=.0001,.4/(3*np.sqrt(1.5**2-1))*.99
for k in range(12):
 dep=(lo+hi)/2;s=CircularBevel(.6,dep);q=trace_flat_front_orthographic(s,rr,np.zeros_like(rr),1.5,2);j=np.gradient(q['X'],rr)
 if j.min()>=.05:lo=dep
 else:hi=dep
s=CircularBevel(.6,lo);q=trace_flat_front_orthographic(s,rr,np.zeros_like(rr),1.5,2);geometry.append(dict(name='nonfold-depth-limit',surface=s.__dict__,radial_min_jacobian=float(np.gradient(q['X'],rr).min()),edge_displacement=float(1-q['X'][-1]),maximum_height=s.maximum_height,slope_bound=s.slope_bound,selection='12-step geometry-only bisection; no target pixels or image score'))
checkpoint=dict(stage='GEOMETRY_CHECKPOINT_BEFORE_IMAGES',started_unix=START,deadline_unix=DEADLINE,proposal_count=3,small_geometry_evaluations=16,allowed=24,historical_map=dict(folds=True,fold_start=float(fold.min()),fold_end=float(fold.max()),minimum_radial_jacobian=float(prior_j.min()),comment='Diagnostic empirical map only. It is NEVER called in the new ray tracer.'),surfaces=geometry,optical_source_blur=0,optical_post_blur=0,AA=4,source_hashes=REC['input_sha256'],frozen_nuisance='Constant historical RGB gain/bias only; no old spatial lights. Historical calculated foreground color/alpha frozen separately, including its old icon-only filtering; not an unfiltered icon experiment.',historical_official_filtered_E=9.06474721701574)
(D/'geometry-checkpoint-FIRST.json').write_text(json.dumps(checkpoint,indent=2)+'\n')
rows=[]
def pic(a):return Image.fromarray(np.uint8(np.rint(np.clip(a,0,1)*255)))
def pair(a,b,path,labels):
 W=min(2*a.shape[1],max(a.shape[1],720));H=round(W*a.shape[0]/a.shape[1]);out=Image.new('RGB',(2*W+2,H+48),'#1c2026');d=ImageDraw.Draw(out)
 for i,(v,label) in enumerate(zip([a,b],labels)):out.paste(pic(v).resize((W,H),Image.Resampling.LANCZOS),((W+2)*i,48));d.text(((W+2)*i+8,18),label,fill='white')
 out.save(path)
for g in geometry:
 if time.time()>DEADLINE:break
 s=CircularBevel(**g['surface']);C=np.empty_like(Mold);bounds=[np.inf,np.inf,-np.inf,-np.inf];aamin=1.
 for row in range(0,y1-y0,24):
  if time.time()>DEADLINE:raise RuntimeError('Budget reached; partial output preserved, no extension')
  bottom=min(row+24,y1-y0);yy,xx=np.mgrid[y0+row:y0+bottom:1/4,x0:x1:1/4];x=(xx-.375-case['center'][0])/L;y=(yy-.375-case['center'][1])/L;q=trace_flat_front_orthographic(s,x,y,1.5,2);X=q['X']*L+case['center'][0];Y=q['Y']*L+case['center'][1]
  assert q['complete'].all();bounds=[min(bounds[0],float(X.min())),min(bounds[1],float(Y.min())),max(bounds[2],float(X.max())),max(bounds[3],float(Y.max()))];assert X.min()>=0 and Y.min()>=0 and X.max()<source.shape[1]-1 and Y.max()<source.shape[0]-1
  raw=cv2.remap(source,X.astype(np.float32),Y.astype(np.float32),cv2.INTER_LINEAR);graded=raw*np.asarray(p['material'][:3])+np.asarray(p['material'][3:6]);raw=np.where(q['inside'][...,None],graded,raw);C[row:bottom]=raw.reshape(bottom-row,4,x1-x0,4,3).mean((1,3))
 C[ib-y0:id-y0,ia-x0:ic-x0]=C[ib-y0:id-y0,ia-x0:ic-x0]*(1-alpha[...,None])+icon[ib-y0:id-y0,ia-x0:ic-x0]*alpha[...,None]
 folder=D/g['name'];folder.mkdir();np.save(folder/'complete.npy',C);pair(target[y0:y1,x0:x1],C,folder/'comparison.png',['Apple reference','Geometric '+g['name']]);ss=scores(C,target[y0:y1,x0:x1],case);local={}
 sheet=Image.new('RGB',(1324,3*528),'#1c2026');draw=ImageDraw.Draw(sheet)
 for k,(name,(a,b,c,d)) in enumerate(rects):
  region=np.s_[b-y0:d-y0,a-x0:c-x0];local[name]=dict(box=[a,b,c,d],composite_RGB_RMSE=float(np.sqrt(np.mean(((C[region]-target[b:d,a:c])*255)**2))),historical_composite_RGB_RMSE=float(np.sqrt(np.mean(((Cold[region]-target[b:d,a:c])*255)**2))))
  for j,(im,label) in enumerate([(target[b:d,a:c],'Apple'),(Cold[region],'Historical filtered'),(C[region],g['name'])]):sheet.paste(pic(im).resize((440,480),Image.Resampling.NEAREST),(442*j,528*k+48));draw.text((442*j+8,528*k+18),name+' / '+label,fill='white')
 sheet.save(folder/'rim-crops.png')
 # Actual same-height section and exit rays: full ray panel has equal x/z scale.
 view=Image.new('RGB',(1000,800),'#1c2026');dr=ImageDraw.Draw(view);scale=260.;ox=500;oy=85;proj=lambda x,z:(ox+x*scale,oy-z*scale);xs=np.linspace(-1,1,1001);zs=s.section(xs)[0];dr.line([proj(-1,0),proj(1,0)],fill='#ddd',width=2);dr.line([proj(x,z) for x,z in zip(xs,zs)],fill='#7edddd',width=2);dr.line([proj(-1.6,-2),proj(1.6,-2)],fill='#888',width=2)
 for x in [-.95,-.8,-.6,.6,.8,.95]:
  ray=trace_flat_front_orthographic(s,np.array([x]),np.array([0.]),1.5,2);back=ray['back'][0];dr.line([proj(x,.2),proj(x,0),proj(back[0],back[2]),proj(ray['X'][0],-2)],fill='#e2b483',width=1)
 dr.text((20,690),'Actual section and traced rays; x/z equal scale. Front z=0; background z=-2L.',fill='white');dr.text((20,714),str(g['surface'])+'; index 1.5; no optical blur.',fill='white');view.save(folder/'section-rays.png')
 row=dict(**g,visible_composite_scores=ss,local=local,source_query_bounds=bounds,all_paths_complete=True,finite_bilinear_source_domain_pass=True,source_is_frozen_registered_photo=True,new_image_render=1,accepted_visible_improvement=False);rows.append(row);(D/'partial-results.json').write_text(json.dumps(rows,indent=2)+'\n');print(json.dumps(dict(name=g['name'],scores=ss['all_glass'],local=local,edge_displacement=g['edge_displacement'])),flush=True)
(D/'result.json').write_text(json.dumps(dict(checkpoint=checkpoint,rows=rows,wall_seconds=time.time()-START,completed_image_renders=len(rows),fits=0,classification='DIAGNOSTIC_PENDING_VISUAL_REVIEW_NOT_ACCEPTED',limitations='Only orthographic flat-front primary transmission tested. No finite camera, Fresnel multipath, lighting fit, optical blur, spectral dispersion or device performance claim. Historical filtered baseline is not silently replaced; foreground color remains frozen historical nuisance.'),indent=2)+'\n')
