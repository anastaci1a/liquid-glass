"""ONE existing-amplitude geometric direction, cached guards before native."""
import os,json,copy,sys
from pathlib import Path
import numpy as np,cv2
os.umask(0o002);cv2.setNumThreads(1)
R=Path('/evidence/extended/helper-toolbar-work/more-close-round');B=R/'latest-circle-baseline';P=R/'foreground-gray-round1';D=R/'rim-amplitude-round1';D.mkdir();sys.path.insert(0,str(B/'code'))
from extended_fit import Study
import neutral_rim
from vector_revision import composite
s=Study(B/'inputs/a');r=json.loads((P/'candidate-native.json').read_text());z=np.load(P/'candidate-native.npz');masks=np.load(B/'baseline-native-arrays.npz');M=z['material'];C=z['complete'];p=r['preset'];a0=r['neutral_rim']['amplitude'];w=r['neutral_rim']['width'];assert a0==.125 and w==.028;direction=np.zeros_like(M);sourcecase=s.case
for row,bottom,W,x,y in s.raster_tiles():
 F=neutral_rim.field(x,y,p,w);direction[row:bottom]=F.reshape(bottom-row,2,W,2).mean((1,3))[:,:,None]
if p['post_sigma']:direction=cv2.GaussianBlur(direction,(0,0),p['post_sigma']*s.L)
np.savez_compressed(D/'cached-direction.npz',d_material_da=direction)

def scores(m,c):
 q=s.scores(m);q['E']=float(np.sqrt(q['loss']))
 for name,key in [('glyph','glyph_mask'),('exterior','exterior_mask'),('full_visible_exterior','full_visible_exterior_mask')]:mask=masks[key];q[name]=dict(pixels=int(mask.sum()),rmse=float(np.sqrt(np.mean(((c-s.target_crop)[mask]*255)**2))))
 return q
base=scores(M,C);assert base==r['scores'];rows=[]
for a in [.15,.1375,.13125]:
 predM=M+(a-a0)*direction
 try:s.case={**sourcecase,'foreground_styles':r['foreground_styles']};predC=composite(s,p,predM)
 finally:s.case=sourcecase
 q=scores(predM,predC);checks={n:q[n]['rmse']<=base[n]['rmse'] for n in ['glass','rim','held','interior','glyph','exterior','full_visible_exterior']};checks.update(E=q['E']<=base['E'],SSIM=q['ssim']>=base['ssim'],meaningful_E_improvement=q['E']<base['E']);rows.append(dict(amplitude=a,prediction_ONLY=q,checks=checks,supported=all(checks.values())))
clip=json.loads((B/'native-raw-clip-proof.json').read_text());result=dict(status='CACHED_EXISTING_AMPLITUDE_DIRECTION',approval='96b4c3d6-a763-4971-911a-5ba1f5fc1cc7',accepted_amplitude=a0,fixed_width=w,fixed_c=0,base=base,predictions=rows,first_supported_amplitude=next((v['amplitude'] for v in rows if v['supported']),None),geometric_direction_source_independent=True,new_body_renders=0,new_optical_source_ray_queries=0,cached_foreground_composites=3,max_raw_conservative_bound=clip['cohorts']['base_unclipped']['global']['maximum']+.15,limits='Ideal-unclippedcachedprediction only; float32native/currenthelperoperationorder+actualrawclipauditstillrequired. Originalmasks/width/bias/tint/SVG/shape/rays/source frozen. No jointbias/c compensation, source or font change.')
(D/'cached-review.json').write_text(json.dumps(result,indent=2)+'\n');print(json.dumps(result),flush=True)
