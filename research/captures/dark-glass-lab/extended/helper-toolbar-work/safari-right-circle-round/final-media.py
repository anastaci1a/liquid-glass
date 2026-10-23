"""Private export only: exact settled map/lighting/shade, frozen source grid.
Internal sufficient integer raster8 (1560 wide), final1080, no optical scoring here.
"""
import os,sys,json,hashlib,subprocess,time
from pathlib import Path
import numpy as np,cv2
from PIL import Image,ImageDraw,ImageSequence
os.umask(0o002);cv2.setNumThreads(1)
R=Path('/evidence/extended/helper-toolbar-work/safari-right-circle-round');B=R/'neutral-baseline';C=R/'neutral-additive-round3';D=R/'final-media';D.mkdir(exist_ok=True);(D/'frames').mkdir(exist_ok=True);sys.path.insert(0,str(B/'code'))
import settled
from extended_fit import Study
from vector_revision import composite
s=Study(B/'inputs/a');rec=json.loads((C/'candidate-native.json').read_text());p=rec['preset'];old=np.load(C/'candidate-native.npz');L=min(s.case['half']);x0,y0,x1,y1=s.crop
sigma=p['source_sigma']*L;blur=cv2.GaussianBlur(s.source,(0,0),sigma) if sigma else s.source

def save(n,v):(D/n).write_text(json.dumps(v,indent=2)+'\n')
def digest(p):return hashlib.sha256(Path(p).read_bytes()).hexdigest()
def kernel_radius(sigma):
 z=np.zeros((501,501),np.float32);z[250,250]=1;o=cv2.GaussianBlur(z,(0,0),sigma);a,b=np.where(o!=0);return int(max(abs(a-250).max(),abs(b-250).max()))

def tiles(scale):
 samples=2;step=1/(samples*scale)
 for top in range(y0*scale,y1*scale,24*scale):
  bottom=min(top+24*scale,y1*scale);yy,xx=np.mgrid[top/scale:bottom/scale:step,x0:x1:step]
  x=(xx-.5+.5/(samples*scale)-s.case['center'][0])/L;y=(yy-.5+.5/(samples*scale)-s.case['center'][1])/L
  X,Y=settled.mapping(x,y,p)
  yield top-y0*scale,bottom-y0*scale,(X*L+s.case['center'][0]),(Y*L+s.case['center'][1]),settled.lighting(x,y,p)

def render(scale,shift=(0,0),cached=None):
 H,W=(y1-y0)*scale,(x1-x0)*scale;out=np.zeros((H,W,3),np.float32)
 for top,bottom,X,Y,light in (cached if cached is not None else tiles(scale)):
  sampled=cv2.remap(blur,(X+shift[0]).astype(np.float32),(Y+shift[1]).astype(np.float32),cv2.INTER_LINEAR)
  q=settled.shade(sampled,light,np.asarray(p['material']));out[top:bottom]=q.reshape(bottom-top,2,W,2,3).mean((1,3))
 return cv2.GaussianBlur(out,(0,0),p['post_sigma']*L*scale) if p.get('post_sigma') else out

def combine(M,scale,shift=(0,0),alpha=None):
 H,W=M.shape[:2];yy,xx=np.mgrid[:H,:W].astype(np.float32);X=x0-.5+(xx+.5)/scale;Y=y0-.5+(yy+.5)/scale
 bg=cv2.remap(s.source,X+shift[0],Y+shift[1],cv2.INTER_LINEAR);A=s.shape_coverage(p,scale) if alpha is None else alpha
 assert 'shadow' not in p and not s.transmission_layers
 return s.apply_foreground(M*A[...,None]+bg*(1-A[...,None]),scale)

# This is an authorized export-equation control against saved candidate arrays,
# not a repeated fit/baseline/score. Native settled operation order is preserved.
if (D/'native-zero-control.json').exists():
 checks=json.loads((D/'native-zero-control.json').read_text())['checks'];assert all(checks.values());print('Reusing saved exact native zero control, no repeated render',flush=True)
else:
 M=render(1);Q=combine(M,1);checks=dict(material_exact=bool(np.array_equal(M,old['material'])),complete_exact=bool(np.array_equal(Q,old['complete'])),clean_public_compositor_exact=bool(np.array_equal(Q,composite(s,p,M))))
 save('native-zero-control.json',dict(checks=checks,material_max_difference=float(np.max(abs(M-old['material']))),complete_max_difference=float(np.max(abs(Q-old['complete']))),native_scores_not_rerun=True));assert all(checks.values());print('native-zero EXACT',flush=True)
scale=8;W=(x1-x0)*scale;H=(y1-y0)*scale;postradius=kernel_radius(p['post_sigma']*L*scale);sourceradius=kernel_radius(sigma);alpha=s.shape_coverage(p,scale);scope=cv2.dilate((alpha>0).astype(np.uint8),np.ones((2*postradius+1,2*postradius+1),np.uint8))>0
# Retain only reusable geometry/light, NOT shaded material. Every pose samples
# the original fixed source and executes actual shade/post blur anew.
cache=[];bounds=np.array([np.inf,np.inf,-np.inf,-np.inf]);subrays=0
for top,bottom,X,Y,J in tiles(scale):
 m=np.repeat(np.repeat(scope[top:bottom],2,0),2,1);xx=X[m].astype(np.float32);yy=Y[m].astype(np.float32);bounds=np.array([min(bounds[0],float(xx.min()) if xx.size else np.inf),min(bounds[1],float(yy.min()) if yy.size else np.inf),max(bounds[2],float(xx.max()) if xx.size else -np.inf),max(bounds[3],float(yy.max()) if yy.size else -np.inf)]);subrays+=len(xx);cache.append((top,bottom,X,Y,J))
travel=4.;frames=90;fps=15;poses=[(0.,float(travel*np.sin(2*np.pi*i/frames))) for i in range(frames)]
known=cv2.imread(str(B/'inputs/a/known.png'),cv2.IMREAD_GRAYSCALE)>254
# Enclose every actual query after float32 rounding, bilinear footprint and
# ALL finite nonzero source-Gaussian neighbors. Rectangle conservative.
def check_rect(b,margin=0):
 l,t,r,z=b;l=int(np.floor(l))-margin;t=int(np.floor(t))-margin;r=int(np.ceil(r))+margin;z=int(np.ceil(z))+margin
 assert 0<=l<=r<known.shape[1] and 0<=t<=z<known.shape[0]
 assert known[t:z+1,l:r+1].all(),(l,t,r,z)
 return [l,t,r,z]
union=[bounds[0],bounds[1]-travel,bounds[2],bounds[3]+travel];rayrect=check_rect(union,sourceradius+1)
backgroundrect=check_rect([x0+.5,y0+.5-travel,x1-1.5,y1-1.5+travel],1)
# Independent conservative radial enclosure, not an extremum search.
# For active output/post neighbor subrays r<=1+sqrt(2)*(postradius+.5)/scale/L.
# Tail <= A*.5**power because both exponent coefficients are nonpositive.
rmax=1+np.sqrt(2)*(postradius+.5)/scale/L;par=p['parameters'];assert par['inner_power']-par['power']*par['width']<=0 and par['inner_power']-par['power']*par['width']**2<=0
amax=par['amplitude']*(1+max(rmax-1,0)/par['band'])**par['power'];Rbound=max(rmax,par['amplitude'],max(amax-1,0))*L
independent=check_rect([s.case['center'][0]-Rbound,s.case['center'][1]-Rbound-travel,s.case['center'][0]+Rbound,s.case['center'][1]+Rbound+travel],sourceradius+1)
save('source-support.json',dict(passed=True,internal_scale=scale,post_radius_output_pixels=postradius,source_radius_native_pixels=sourceradius,contributing_subrays=subrays,actual_zero_query_bounds=bounds.tolist(),all_90_pose_source_enclosure_including_bilinear_and_source_kernel=rayrect,all_90_pose_exterior_enclosure=backgroundrect,independent_radial_rmax=rmax,independent_radial_amax=amax,independent_bound_formula='max(rmax,A,max(amax-1,0))*L; inside r<=1 a<=A; outside1<=r<=rmax, 1-amax<=r-a<=rmax',independent_all_pose_enclosure=independent,minimum_modeled_confidence=1,observed_hidden_fraction=0,declared_panel_domain_respected=True,travel_native_pixels=travel,axis='y',poses=poses,limits='Finite discrete kernels + all visible-alpha/post-neighbor source subrays with bilinear footprint; conservative independent bound includes every pose. Modeled panel definition, not observed recovery or physical optical validation. Full native scored proof inherited separately; export does not rescore.'))
print('all-pose/source support PASS',rayrect,independent,flush=True)
finalW=1080;finalH=round((y1-y0-2)*finalW/(x1-x0-2));zero=None;framehashes=[];t0=time.time()
for i,pose in enumerate(poses):
 M=render(scale,pose,cache);rgb=combine(M,scale,pose,alpha);rgb8=np.uint8(np.rint(np.clip(rgb,0,1)*255));out=cv2.resize(rgb8[scale:-scale,scale:-scale],(finalW,finalH),interpolation=cv2.INTER_AREA)
 file=D/'frames'/f'{i:03}.png';Image.fromarray(out).save(file);framehashes.append(dict(frame=i,shift=pose,sha256=digest(file)))
 if i==0:
  zero=out;Image.fromarray(out).save(D/'reconstruction.png');target=cv2.resize(np.uint8(np.rint(s.target_crop[1:-1,1:-1]*255)),(finalW,finalH),interpolation=cv2.INTER_LANCZOS4);Image.fromarray(target).save(D/'original.png');pair=Image.new('RGB',(2*finalW+2,finalH+64),'#222');draw=ImageDraw.Draw(pair);draw.text((12,20),'Apple Safari bag / 1px presentation trim',fill='white');draw.text((finalW+14,20),'Reconstruction / neutral grading b=.075',fill='white');pair.paste(Image.fromarray(target),(0,64));pair.paste(Image.fromarray(out),(finalW+2,64));pair.save(D/'comparison.png')
 print(f'frame {i+1}/{frames}',flush=True)
cmd=['ffmpeg','-v','error','-threads','2','-filter_threads','1','-y','-framerate',str(fps),'-i',str(D/'frames/%03d.png')]
subprocess.run(cmd+['-vf','pad=ceil(iw/2)*2:ceil(ih/2)*2,scale=in_range=pc:out_range=tv:out_color_matrix=bt601','-colorspace','smpte170m','-color_range','tv','-c:v','libx264','-threads','2','-crf','18','-pix_fmt','yuv420p','-movflags','+faststart',str(D/'motion.mp4')],check=True)
for colors in [128,96,64]:
 subprocess.run(cmd+['-vf',f'palettegen=max_colors={colors}:stats_mode=full','-frames:v','1',str(D/'palette.png')],check=True)
 subprocess.run(cmd+['-i',str(D/'palette.png'),'-filter_complex_threads','1','-lavfi','[0:v][1:v]paletteuse=dither=bayer:bayer_scale=3:diff_mode=rectangle','-loop','0',str(D/'motion.gif')],check=True)
 if (D/'motion.gif').stat().st_size<10_000_000:break
assert (D/'motion.gif').stat().st_size<10_000_000
import runpy
runpy.run_path(str(R/'finish-media.py'),run_name='__main__')
