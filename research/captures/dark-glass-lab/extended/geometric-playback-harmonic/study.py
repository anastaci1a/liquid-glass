"""G04 one declared explicit surface; no fitting or optical filtering."""
import os,time,json,hashlib,datetime
from pathlib import Path
import numpy as np,cv2
from PIL import Image,ImageDraw
from geometric_optics import HarmonicCircularBack,trace_flat_front_orthographic
from reproduce import CASES,scores,points,masks
from settled import icon_color
from playback_replay import composite
os.umask(2);cv2.setNumThreads(1)
D=Path('/evidence/extended/geometric-playback-harmonic');deadline=datetime.datetime(2026,10,22,4,27,tzinfo=datetime.timezone.utc).timestamp();start=time.time()
def gate():
 if time.time()>deadline:raise RuntimeError('G04 original wall limit; stop with partials, no extension')
 if (D/'result.json').exists():raise RuntimeError('Completed experiment cannot restart')
gate();s=HarmonicCircularBack(.15,.4);case=CASES['media'];L=min(case['half']);x0,y0,x1,y1=case['crop'];W=x1-x0;H=y1-y0
rr=np.linspace(0,1-1e-9,2001);rad=trace_flat_front_orthographic(s,rr,np.zeros_like(rr),1.5,2);jac=np.gradient(rad['X'],rr);xx=np.linspace(-.95,.95,201);yy=np.full_like(xx,.07);h,hx,hy,_=s.height_gradient(xx,yy);e=1e-6;fd=(s.height_gradient(xx+e,yy)[0]-s.height_gradient(xx-e,yy)[0])/(2*e);assert abs(fd-hx).max()<1e-9
assert rad['complete'].all() and jac.min()>0
geom=dict(surface=dict(family='HarmonicCircularBack',depth=.15,crown_depth=.4,index=1.5,background_distance=2),minimum_radial_map_derivative=float(jac.min()),edge_inward_displacement=float(1-rad['X'][-1]),actual_max_height=s.maximum_height,global_slope_bound=s.slope_bound,gradient_error=float(abs(fd-hx).max()),geometry_checkpoint_rays=2001,complete=True,fold=False)
(D/'geometry-checkpoint-FIRST.json').write_text(json.dumps(geom,indent=2)+'\n');np.savez(D/'radial-geometry.npz',r=rr,**rad)
INPUT=Path('/evidence/apple-matches/public-settled-replay');R=Path('/evidence/extended/playback-short-round/pass-03');record=json.loads((R/'replay-record.json').read_text());p=record['recipe']
for name,digest in record['input_sha256'].items():assert hashlib.sha256((INPUT/name).read_bytes()).hexdigest()==digest
registration=json.loads((INPUT/'settled-scores.json').read_text())['media']['registration'];mat=np.vstack([registration['matrix'],[0,0,1]]);inverse=np.linalg.inv(mat)
xs,ys,dx,dy=points(case);sd,train,held,valid=masks(case,xs,ys,dx,dy)
cache=D/'queries';cache.mkdir(exist_ok=False);proof=dict(all_crop_rays=0,whole_lens_rays=0,all_original_scored_subrays=0,incomplete=0,unsupported_bilinear=0,unsupported_registered_frame_texels=0,source_query_bounds=[1e10,1e10,-1e10,-1e10]);tiles=[]
for row in range(0,H,24):
 gate();bottom=min(row+24,H);yy,xx=np.mgrid[y0+row:y0+bottom:1/4,x0:x1:1/4];q=trace_flat_front_orthographic(s,(xx-.375-case['center'][0])/L,(yy-.375-case['center'][1])/L,1.5,2)
 X=q['X']*L+case['center'][0];Y=q['Y']*L+case['center'][1];a=np.floor(X).astype(np.int32);b=np.floor(Y).astype(np.int32)
 proof['all_crop_rays']+=X.size;proof['whole_lens_rays']+=int(q['inside'].sum());proof['all_original_scored_subrays']+=int(valid[row:bottom].sum())*16;proof['incomplete']+=int((~q['complete']).sum());proof['unsupported_bilinear']+=int(((a<0)|(b<0)|(a+1>=1920)|(b+1>=1080)).sum())
 for ix,iy in [(0,0),(1,0),(0,1),(1,1)]:
  ux=inverse[0,0]*(a+ix)+inverse[0,1]*(b+iy)+inverse[0,2];uy=inverse[1,0]*(a+ix)+inverse[1,1]*(b+iy)+inverse[1,2]
  proof['unsupported_registered_frame_texels']+=int(((ux<0)|(uy<0)|(ux>=1919)|(uy>=1079)).sum())
 bounds=proof['source_query_bounds'];proof['source_query_bounds']=[min(bounds[0],float(X.min())),min(bounds[1],float(Y.min())),max(bounds[2],float(X.max())),max(bounds[3],float(Y.max()))]
 path=cache/f'{row:04d}.npz';np.savez(path,X=X,Y=Y);tiles.append((row,bottom,path))
assert proof['all_crop_rays']==7126400 and proof['incomplete']==proof['unsupported_bilinear']==proof['unsupported_registered_frame_texels']==0
proof.update(source_hashes=record['input_sha256'],actual_registered_frame_domain='Every four sampled registered texels maps into original frame180 with one-texel bilinear margin',source_is_not='A certificate of exact hidden scene RGB, PSF or registration; temporal registered photograph uncertainty remains',source_registration=registration,source_blur=0,post_blur=0,sampling='4x4 pixel integration; exact continuous bilinear interpolation, distinct from old OpenCV table interpolation',saved_before_source_RGB_sampling=True)
(D/'source-proof-FIRST.json').write_text(json.dumps(proof,indent=2)+'\n')
source=np.asarray(Image.open(INPUT/'media-source.png'),float)/255;target=np.asarray(Image.open(INPUT/'media-target.png'),np.float32)/255;C=np.empty((H,W,3),np.float32)
for row,bottom,path in tiles:
 gate();q=np.load(path);X=q['X'];Y=q['Y'];a=np.floor(X).astype(int);b=np.floor(Y).astype(int);fx=(X-a)[...,None];fy=(Y-b)[...,None]
 raw=(source[b,a]*(1-fx)+source[b,a+1]*fx)*(1-fy)+(source[b+1,a]*(1-fx)+source[b+1,a+1]*fx)*fy
 C[row:bottom]=raw.reshape(bottom-row,4,W,4,3).mean((1,3))
oldM=np.load(R/'candidate-material.npy');Cold=composite(source,case,p,oldM,1);oldicon=icon_color(oldM,p['icon'],L);ia,ib,ic,id=[int(round(v*L+case['center'][i%2])) for i,v in enumerate(p['icon']['box_over_L'])];alpha=np.asarray(Image.open(D/'code'/p['icon']['coverage']),float)/255;sl=np.s_[ib-y0:id-y0,ia-x0:ic-x0];C[sl]=C[sl]*(1-alpha[...,None])+oldicon[sl]*alpha[...,None]
np.save(D/'complete.npy',C);np.save(D/'historical-complete.npy',Cold)
def pic(a):return Image.fromarray(np.uint8(np.rint(np.clip(a,0,1)*255)))
reference=target[y0:y1,x0:x1];preview=Image.new('RGB',(W*3+4,H+64),'white');draw=ImageDraw.Draw(preview)
for i,(im,label) in enumerate([(reference,'Apple'),(Cold,'Historical filtered'),(C,'G04 unblurred raw transmission')]):preview.paste(pic(im),(i*(W+2),64));draw.text((i*(W+2)+8,20),label,fill='black')
preview.save(D/'comparison.png');rects=[('bottom-left',[690,570,910,810]),('top-left',[690,290,910,530]),('upper-right-crossings',[1025,320,1245,560])];local={};sheet=Image.new('RGB',(1324,3*544),'white');draw=ImageDraw.Draw(sheet)
for k,(name,(a,b,c,d)) in enumerate(rects):
 region=np.s_[b-y0:d-y0,a-x0:c-x0];ref=target[b:d,a:c];data={}
 for label,im in [('historical',Cold[region]),('candidate',C[region])]:
  diff=(im-ref)*255;luma=diff@np.array([.2126,.7152,.0722]);chroma=diff-diff.mean(-1)[...,None]
  data[label]=dict(RGB_RMSE=float(np.sqrt(np.mean(diff**2))),luma_RMSE=float(np.sqrt(np.mean(luma**2))),chroma_RMSE=float(np.sqrt(np.mean(chroma**2))),signed_RGB=diff.mean((0,1)).tolist())
 local[name]=dict(box=[a,b,c,d],**data)
 for j,(im,label) in enumerate([(ref,'Apple'),(Cold[region],'Historical filtered'),(C[region],'G04 harmonic back')]):sheet.paste(pic(im).resize((440,480),Image.Resampling.NEAREST),(442*j,544*k+64));draw.text((442*j+6,544*k+20),name+' / '+label,fill='black')
sheet.save(D/'rim-crops.png')
result=dict(classification='FIXED_GEOMETRIC_DIAGNOSTIC_PENDING_VISIBLE_REVIEW_NOT_ACCEPTED',geometry=geom,proof=proof,visible_composite_scores=scores(C,reference,case),historical_scores=scores(Cold,reference,case),local=local,completed_image_renders=1,fits=0,wall_seconds=time.time()-start,scope='Unit raw transmission, no body grading/lighting/reflection/shadow/scattering; historical filtered icon color/alpha frozen nuisance. Sampling differs from old quantized remap. Original source/masks/registration unchanged. Not a full dielectric radiance or device validation.')
(D/'result.json').write_text(json.dumps(result,indent=2)+'\n');print(json.dumps(dict(geometry=geom,scores=result['visible_composite_scores']['all_glass'],local=local,wall_seconds=result['wall_seconds'])),flush=True)
