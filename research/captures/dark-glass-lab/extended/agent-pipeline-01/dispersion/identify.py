"""Saved-array spectral identifiability; no channel warp, fit or tracing."""
from pathlib import Path
import json,time,numpy as np,cv2
P=Path('/evidence/extended/agent-pipeline-01');O=P/'dispersion';proto=json.loads((O/'protocol.json').read_text());deadline=__import__('datetime').datetime.fromisoformat(proto['deadline'].replace('Z','+00:00')).timestamp();assert time.time()<deadline
out={'status':'IDENTIFICATION_ONLY','new_rays':0,'new_source_queries':0,'new_native_images':0,'fits':0,'analysis':'Fixed Btext and middle rectangles; eroded originalglass51x51 and actualfullcoverage. Masks advisory only, original scoring unchanged. Fixed1px derivative analysis on everyRGB channel equally, no opticalfilter/registration change.','cases':{}}
for key in ['a','b']:
 case=json.loads((P/f'inputs/{key}/case.json').read_text());x0,y0,x1,y1=case['crop'];T=cv2.imread(str(P/f'inputs/{key}/target.png'))[:,:,::-1].astype(float)/255;T=T[y0:y1,x0:x1];source=np.load(P/'blurriness'/f'{key}-lens-color.npy');model=np.load(P/'color-grading'/f'{key}-step0.5-complete.npy');alpha=np.load(P/'blurriness'/f'{key}-coverage.npy');valid=np.load(P/f'historical-{key}-masks.npz')['glass'];safe=(cv2.erode(valid.astype(np.uint8),np.ones((51,51),np.uint8))>0)&(alpha==1);records={}
 for name,box in [('text',[875,326,1258,505]),('middle',[865,326,1050,505])]:
  a,b,c,d=box;m=np.zeros(valid.shape,bool);m[b-y0:d-y0,a-x0:c-x0]=True;m&=safe;stats={}
  for label,C in [('target',T),('raw_source_samples',source),('current_model',model)]:
   V=C[m];opp=np.stack([(V[:,0]-V[:,1])/np.sqrt(2),(V[:,0]+V[:,1]-2*V[:,2])/np.sqrt(6)],1);filtered=cv2.GaussianBlur(np.nan_to_num(C),(7,7),1.);gy,gx=np.gradient(filtered,axis=(0,1));grad=np.stack([gx[m],gy[m]],axis=1);cor={}
   for i,j in [(0,1),(0,2),(1,2)]:
    gi=grad[:,:,i];gj=grad[:,:,j];den=np.sqrt((gi*gi).sum()*(gj*gj).sum());cor[f'{i}{j}']=float((gi*gj).sum()/den) if den>0 else None
   stats[label]={'pixels':int(m.sum()),'exact_neutral_fraction':float(((V[:,0]==V[:,1])&(V[:,1]==V[:,2])).mean()),'mean_RGB':V.mean(0).tolist(),'opponent_mean_levels':(opp.mean(0)*255).tolist(),'opponent_spatial_RMS_levels':float(np.sqrt(np.mean((opp-opp.mean(0))**2))*255),'RG_max_difference_levels':float(abs(V[:,0]-V[:,1]).max()*255),'channel_gradient_correlations':cor}
  e=(model-T)[m]*255;Y=e@np.array([.2126,.7152,.0722]);ce=np.stack([(e[:,0]-e[:,1])/np.sqrt(2),(e[:,0]+e[:,1]-2*e[:,2])/np.sqrt(6)],1);stats['residual']={'luma_RMSE':float(np.sqrt(np.mean(Y*Y))),'opponent_RMSE':float(np.sqrt(np.mean(ce*ce))),'signed_RGB':e.mean(0).tolist()};records[name]=stats
 out['cases'][key]=records
out['ordinary_blur_evidence']='Existing detail-review.json selected neutral6.75px filter: same scalar kernel forRGB, modifies luminance width, no wavelengthdependentIOR/offset. Never call it dispersion.';out['limits']='Neutral target can constrain visible channel separation at this source/PSF/codec precision but cannot prove wavelength-independentAppleIOR. ColoredA edges already differ spectrally in input and have large tone/geometry/illumination error. UnknowncameraRGB/PSF/environment prevent unique physicalspectral identification.';out['finished_unix']=time.time();assert time.time()<deadline;(O/'identification.json').write_text(json.dumps(out,indent=2));print(json.dumps(out))
