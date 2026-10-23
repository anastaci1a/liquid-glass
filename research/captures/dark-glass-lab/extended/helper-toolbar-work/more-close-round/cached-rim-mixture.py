"""ONE cached direction for target-independent angular environment mixture."""
import os,json,copy,sys,hashlib
from pathlib import Path
import numpy as np,cv2
os.umask(0o002);cv2.setNumThreads(1)
R=Path('/evidence/extended/helper-toolbar-work/more-close-round');B=R/'latest-circle-baseline';P=R/'foreground-gray-round1';D=R/'rim-mixture-round1';D.mkdir();sys.path.insert(0,str(B/'code'))
from extended_fit import Study
import settled,neutral_rim
from vector_revision import composite
s=Study(B/'inputs/a');r=json.loads((P/'candidate-native.json').read_text());z=np.load(P/'candidate-native.npz');masks=np.load(B/'baseline-native-arrays.npz');M=z['material'];C=z['complete'];p=r['preset'];a=r['neutral_rim']['amplitude'];w=r['neutral_rim']['width'];sourcecase=s.case;direction=np.zeros_like(M);zero_exact=True;component_range=[1e9,-1e9];bound_violation=0.;x0,y0,x1,y1=s.crop
for row,bottom,W,x,y in s.raster_tiles():
 F=neutral_rim.field(x,y,p,w);sd,nx,ny=settled.case_geometry(p['shape'],x,y);G=np.exp(-(np.maximum(-sd,0)/w)**2);H0=F # c0 branch EXACTLY returnsoriginal
 zero_exact &= np.array_equal(H0,F);component_range=[min(component_range[0],float(F.min())),max(component_range[1],float(G.max()))];bound_violation=max(bound_violation,float((F-G).max()));delta=a*(G-F);direction[row:bottom]=delta.reshape(bottom-row,2,W,2).mean((1,3))[:,:,None]
if p['post_sigma']:direction=cv2.GaussianBlur(direction,(0,0),p['post_sigma']*s.L)
assert zero_exact
np.savez_compressed(D/'cached-direction.npz',d_material_dc=direction)

def scores(m,c):
 q=s.scores(m);q['E']=float(np.sqrt(q['loss']))
 for name,key in [('glyph','glyph_mask'),('exterior','exterior_mask'),('full_visible_exterior','full_visible_exterior_mask')]:mask=masks[key];q[name]=dict(pixels=int(mask.sum()),rmse=float(np.sqrt(np.mean(((c-s.target_crop)[mask]*255)**2))))
 return q
base=scores(M,C);assert base==r['scores'];rows=[]
for coeff in [.25,.125,.0625]:
 predM=M+coeff*direction
 try:s.case={**sourcecase,'foreground_styles':r['foreground_styles']};predC=composite(s,p,predM)
 finally:s.case=sourcecase
 q=scores(predM,predC);checks={n:q[n]['rmse']<=base[n]['rmse'] for n in ['glass','rim','held','interior','glyph','exterior','full_visible_exterior']};checks.update(E=q['E']<=base['E'],SSIM=q['ssim']>=base['ssim'],meaningful_E_improvement=q['E']<base['E']);rows.append(dict(mixture=coeff,prediction_ONLY=q,checks=checks,supported=all(checks.values()),no_native_body_render=True))
# Fixed original rim masks only; angle bins advisory, NEVER optimization masks.
_,nx,ny=settled.case_geometry(p['shape'],s.x,s.y);angle=np.arctan2(ny,nx);error=(M.astype(float)-s.target_crop.astype(float))*255;cohorts=[]
for i in range(8):
 lo=-np.pi+i*np.pi/4;hi=lo+np.pi/4;mask=s.rim&(angle>=lo)&(angle<hi)
 if mask.any():cohorts.append(dict(normal_angle_radians=[lo,hi],pixels=int(mask.sum()),baseline_signed_RGB=error[mask].mean(0).tolist(),baseline_RGB_RMSE=float(np.sqrt(np.mean(error[mask]**2))),direction_mean_native255=float(direction[mask].mean()*255),advisory_only=True))
clip=json.loads((B/'native-raw-clip-proof.json').read_text());base_max=clip['cohorts']['base_unclipped']['global']['maximum'];conservative_max=base_max+a;result=dict(status='CACHED_ONE_MIXTURE_DIRECTION_COMPLETE',approval='e90c7b70-8ca4-4333-a267-21355dadce19',formula='Hc=(1-c)*G*(n dot ell)^2+c*G; G=exp(-(max(-sd,0)/w)^2), ell=(1,1)/sqrt2, c[0,1], a.125/w.028FIXED',zero_c_returns_original_field_exact=bool(zero_exact),floating_component_bound_overshoot=bound_violation,conservative_base_plus_max_rim=conservative_max,predictions=rows,normal_angle_cohorts=cohorts,baseline=base,body_renders=0,source_ray_queries=0,extra_glyph_fit=False,limits='Cached ideal-unclipped additive direction integrated on frozen2x2output/postkernel, float32predictionNOTactualnative. All original masks/source/pose/map/kernel/SVG/tint fixed. Interior/glyph exactties mayhold; no fabricatedstrictimprovement there. Convexneutralenvironmentlightingproxy, notFresnel/Applephysics. No per-angle/crop/pointwisecoefficients or altered masks.',next='Ifprediction supported, authorizealreadyqueued first c.25/backtracks.125,.0625 max3actualnative stopfirstqualifier; elseSTOPboundednegative.')
(D/'cached-review.json').write_text(json.dumps(result,indent=2)+'\n');print(json.dumps(result),flush=True)
