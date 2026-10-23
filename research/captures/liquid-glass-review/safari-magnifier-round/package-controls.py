"""Complete provenance and saved-array controls; NO new optical render or fit."""
import os,json,hashlib,sys
from pathlib import Path
import cv2,numpy as np
from PIL import Image
R=Path('/evidence/extended/helper-toolbar-work/safari-magnifier-round');os.umask(0o002);cv2.setNumThreads(1)
def sha(p):return hashlib.sha256(p.read_bytes()).hexdigest()
def save(n,v):(R/n).write_text(json.dumps(v,indent=2)+'\n')
assert not (R/'package-controls.json').exists(),'Do not repeat completed provenance control'
# One decode of A only verifies cached native frame belongs to the named official source. Reuse prior verified video hash record, do not decode donors.
cap=cv2.VideoCapture('/evidence/apple-matches/219-hd.mp4');cap.set(cv2.CAP_PROP_POS_MSEC,300000);ok,im=cap.read();assert ok;pts=cap.get(cv2.CAP_PROP_POS_MSEC);frame=int(cap.get(cv2.CAP_PROP_POS_FRAMES))-1;cap.release();cached=np.asarray(Image.open(R/'a/target.png').convert('RGB'));same=np.array_equal(im[:,:,::-1],cached);assert same
sys.path.insert(0,str(R/'code'));from extended_fit import Study
from source_support import masks,kernel_safe,confidence_at
s=Study(R/'a');rec=json.loads((R/'baseline-recipe.json').read_text());p=rec['parameters'];A=np.load(R/'baseline-native-arrays.npz');material=A['material'];complete=A['complete'];raw=s.scores(material);prior=json.loads((R/'baseline-native.json').read_text());assert raw=={k:prior['scores'][k] for k in raw};assert np.isfinite(material).all() and np.isfinite(complete).all()
# Output blur also consumes material outside the alpha/scoring outline. Audit this additional finite footprint, including source scattering. No RGB evaluation/duplicate native render.
post_radius=int(np.ceil(3*s.kernel_sigma(p,'post_sigma')));kernel=np.ones((2*post_radius+1,2*post_radius+1),np.uint8);post_scope=cv2.dilate(((A['alpha']>0)|s.valid).astype(np.uint8),kernel)>0
safe,radius=kernel_safe(masks(s)[0],s,p);count=0;bad=0;minimum=1.;bounds=[1e9,1e9,-1e9,-1e9]
for row,bottom,W,x,y in s.raster_tiles():
 X,Y,*_=s.geometry_field(x,y,p);X=(X*s.L+s.case['center'][0]).astype(np.float32);Y=(Y*s.L+s.case['center'][1]).astype(np.float32);mask=np.repeat(np.repeat(post_scope[row:bottom],2,axis=0),2,axis=1);c=confidence_at(safe,X,Y);count+=int(mask.sum());bad+=int((c[mask]<.999999).sum());minimum=min(minimum,float(c[mask].min()) if mask.any() else 1.)
 if mask.any():bounds=[min(bounds[0],float(X[mask].min())),min(bounds[1],float(Y[mask].min())),max(bounds[2],float(X[mask].max())),max(bounds[3],float(Y[mask].max()))]
result=dict(native_A_decode=dict(seconds=300,presentation_seconds=pts/1000,frame_index=frame,cached_target_pixel_exact=same,video_sha256_reused_from='photos-actions-source-round/started.json + prior completed decoder audit;3d58f9e843f0b8c22e99d76de6b5201ef5b17de5bb4bf5732862ba7dbf9be60e',native_size=[1920,1080]),saved_array_scores_exact=True,no_optical_render=True,no_fit=True,additional_output_scattering_finite_support=dict(output_gaussian_radius_native_px=post_radius,source_gaussian_radius_native_px=radius,native2x2_rays=count,bad=bad,minimum_defined_confidence=minimum,ray_bounds=bounds,passed=bad==0,limits='Finite3sigma postblur dilation plus source3sigma. All underlyingfield rays included even outside alpha/scored shape. No infinite Gaussian/continuous proof; source remains modeled observed0.'))
save('package-controls.json',result);print(json.dumps(result),flush=True)
# Manifest immutable scientific inputs/arrays; review and queue files deliberately excluded.
files=[p for p in R.rglob('*') if p.is_file() and p.suffix in ['.py','.png','.npz','.json','.svg'] and p.name!='manifest.json'];save('manifest.json',{str(p.relative_to(R)):dict(sha256=sha(p),bytes=p.stat().st_size) for p in sorted(files)})
