"""Independent separable-filter/bilinear replay and saved-path audit.
No new optical rays, parameter selection or source registration.
"""
import datetime,json,time
from pathlib import Path
import cv2,numpy as np
from PIL import Image
from scipy.ndimage import convolve1d,map_coordinates
from reproduce import CASES,points,masks,scores
from settled import icon_color
ROOT=Path(__file__).resolve().parents[3];OUT=Path(__file__).parent
E=ROOT/'.evidence-working/clear-play-02/dark-glass-lab';CAP=ROOT/'research/captures/dark-glass-lab'
p=json.loads((OUT/'protocol.json').read_text());deadline=datetime.datetime.fromisoformat(p['stages'][3]['deadline']).timestamp()
if time.time()>deadline:raise RuntimeError('Verification deadline')
if (OUT/'verification.json').exists():raise RuntimeError('Do not repeat completed verification')
cv2.setNumThreads(1);case=CASES['media'];x0,y0,x1,y1=case['crop'];H,W=y1-y0,x1-x0
source=np.asarray(Image.open(E/'apple-matches/public-settled-replay/media-source.png'),float)/255
sigma=json.loads((OUT/'result.json').read_text())['selected_source_sigma_pixels'];radius=int(np.ceil(3*sigma));x=np.arange(-radius,radius+1);kernel=np.exp(-.5*(x/sigma)**2);kernel/=kernel.sum()
filtered=convolve1d(convolve1d(source,kernel,axis=0,mode='constant'),kernel,axis=1,mode='constant')
B=E/'extended/playback-pipeline-01/blurriness';alpha=np.load(B/'coverage.npy');clear=np.load(B/'clear-premultiplied.npy');M=np.zeros((H,W,3))
for path in sorted((E/'extended/geometric-playback-inferred/queries').glob('*.npz')):
    if time.time()>deadline:raise RuntimeError('Verification deadline')
    q=np.load(path);X,Y=q['X'],q['Y'];row=int(path.stem);stop=row+X.shape[0]//4
    yy,xx=np.mgrid[y0+row:y0+stop:.25,x0:x1:.25];inside=(xx-.375-960)**2+(yy-.375-542)**2<=245**2
    coords=np.stack([Y[inside],X[inside]])
    values=np.zeros(X.shape+(3,))
    for c in range(3):values[...,c][inside]=map_coordinates(filtered[...,c],coords,order=1,mode='constant',prefilter=False)
    numerator=values.reshape(stop-row,4,W,4,3).mean((1,3))
    M[row:stop]=np.divide(numerator,alpha[row:stop,:,None],out=np.zeros_like(numerator),where=alpha[row:stop,:,None]>0)
C=(M*alpha[...,None]+clear).astype(np.float32)
recipe=json.loads((CAP/'extended/playback-short-round/pass-03/replay-record.json').read_text())['recipe'];old=np.load(E/'extended/playback-short-round/pass-03/candidate-material.npy');color=icon_color(old,recipe['icon'],245)
a,b,c,d=[int(round(v*245+case['center'][i%2])) for i,v in enumerate(recipe['icon']['box_over_L'])];mask=np.asarray(Image.open(ROOT/'reconstruction'/recipe['icon']['coverage']),float)/255;sl=np.s_[b-y0:d-y0,a-x0:c-x0];C[sl]=C[sl]*(1-mask[...,None])+color[sl]*mask[...,None]
trial=np.load(OUT/'candidate.npz');md=float(abs(M-trial['material']).max());cd=float(abs(C-trial['complete']).max())
assert md<2e-14 and cd<=np.finfo(np.float32).eps
np.testing.assert_array_equal(alpha,trial['coverage'])
# Verify all stored boundary locations against their actual surface, independently
# of the intersection loop. These are level evaluations, not new rays.
from geometric_optics import RadialCurvatureBack
spec=json.loads((ROOT/'reconstruction/studies/geometric-playback/g05-surface.json').read_text());back=RadialCurvatureBack(**spec['surface']);paths=np.load(OUT/'outline-paths.npz');max_error=0;count=0
for key in paths.files:
    if key.endswith('_point') and key!='final_point':
        q=paths[key];h=back.height_gradient(q[:,0],q[:,1])[0];F=np.maximum.reduce([q[:,2],-q[:,2]-h,q[:,0]**2+q[:,1]**2-1]);max_error=max(max_error,float(abs(F).max()));count+=len(q)
assert max_error<1e-10
energy=paths['background']+paths['environment']+paths['residual']+paths['unresolved'];assert abs(energy-1).max()<3e-14
result={'status':'PASS_NUMERICAL_REPLAY_AND_SAVED_PATH_AUDIT','filter':'Independent normalized exponential kernel and scipy separable convolution','sampler':'Independent scipy first-order coordinate interpolation','material_max_difference':md,'complete_max_difference':cd,'coverage_exact':True,'path_levels_checked':count,'maximum_surface_residual':max_error,'conservation_error':float(abs(energy-1).max()),'new_refraction_rays':0,'independent_full_native_replays':1,'acceptance':'No guard waiver. Replay tolerance validates independent numerical implementations; candidate remains rejected by original scores.'}
(OUT/'verification.json').write_text(json.dumps(result,indent=2)+'\n');print(json.dumps(result))
