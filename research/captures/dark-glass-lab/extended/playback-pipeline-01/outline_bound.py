from pathlib import Path
import time,json
import numpy as np
from PIL import Image
from geometric_optics import fresnel_components
P=Path('/evidence/extended/playback-pipeline-01');D=P/'outline';start=time.time();M=np.load(P/'blurriness/candidate-material.npy');A=np.load(P/'blurriness/coverage.npy');T=np.asarray(Image.open('/evidence/apple-matches/public-settled-replay/media-target.png'),float)[220:875,620:1300]/255;geom=json.loads(Path('/evidence/extended/geometric-playback-inferred/geometry-checkpoint-FIRST.json').read_text());slope=geom['global_slope_bound'];theta=np.arctan(slope);assert theta<np.arctan(1/1.5);rs,rp=fresnel_components(np.cos(theta),1.5,1);R0=.04;Rbound=.5*(float(rs)+R0);Tmin=.96*(1-Rbound);Tmax=.96;remaining=1-Tmin
# Explicit standard sRGB assumption only; no conversion/adoption of frozen source.
linear=np.where(T<=.04045,T/12.92,((T+.055)/1.055)**2.4);Breq=np.max((linear-Tmax*M-1e-6)/remaining,axis=-1);yy,xx=np.mgrid[220:875,620:1300];r=np.hypot(xx-960,yy-542);mask=(r<245-.75)&(r>245-4)&(A==1)
for aa,bb,cc,dd in [[870,425,1088,666]]:mask&=~((xx>=aa)&(xx<=cc)&(yy>=bb)&(yy<=dd))
regions={'whole_original_rim':mask,'bottom_left_feedback':mask&(xx>=690)&(xx<910)&(yy>=570)&(yy<810),'top_left_feedback':mask&(xx>=690)&(xx<910)&(yy>=290)&(yy<530),'upper_right_feedback':mask&(xx>=1025)&(xx<1245)&(yy>=320)&(yy<560)};rows={}
for name,m in regions.items():
 b=Breq[m];rows[name]={'pixels':int(m.sum()),'required_B_p50_p95_max':np.percentile(b,[50,95,100]).tolist(),'count_required_above_unit':int((b>1).sum()),'fraction_required_above_unit':float((b>1).mean())}
np.savez(D/'radiance-bound.npz',required_B=Breq,original_rim_mask=mask);result={'status':'ASSUMPTION_BOUNDED_DIAGNOSTIC_NOT_AN_IMAGE','actual_global_slope':slope,'back_Rs_at_max_slope':float(rs),'back_Rp_at_max_slope':float(rp),'conservative_back_R_bound':Rbound,'primary_power_upper_bound':Tmax,'nonprimary_power_upper_bound':remaining,'encoding_assumption':'sRGB inverse transfer ONLY for diagnostic; originalvideo/PSF/tone are not independentlyidentified','regions':rows,'unresolved_paths_not_filled':True,'new_rays':0,'ray_to_texture_queries':0,'fits':0,'wall_seconds':time.time()-start,'sources':['https://pbr-book.org/4ed/Reflection_Models/Specular_Reflection_and_Transmission','https://www.w3.org/TR/css-color-4/#color-conversion-code']};(D/'radiance-bound.json').write_text(json.dumps(result,indent=2)+'\n');print(json.dumps(result))
