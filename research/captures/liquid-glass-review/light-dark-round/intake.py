"""Read-only SOURCE/PROTOCOL intake, legacy settled native4x4; no fitting."""
import json,os,sys,math
from pathlib import Path
import cv2,numpy as np
from PIL import Image
R=Path('/evidence/extended/helper-toolbar-work/light-dark-round');sys.path.insert(0,str(R/'code'))
import settled
from reproduce import CASES,points,masks,scores
from render import case_geometry
cv2.setNumThreads(1)
def save(n,v):(R/n).write_text(json.dumps(v,indent=2)+'\n')
def source_domain(name,case,p,source,valid):
 L=min(case['half']);x0,y0,x1,y1=case['crop'];H,W=source.shape[:2];rows={k:dict(rays=0,undefined=0,outside_footprint=0,min_x=1e9,max_x=-1e9,min_y=1e9,max_y=-1e9,source_rgb_min=[1.,1.,1.],source_rgb_max=[0.,0.,0.],light_black_splice_rays=0,dark_copied_top_rays=0) for k in ['whole','ALL_scored']}
 for top in range(y0,y1,24):
  bottom=min(top+24,y1);yy,xx=np.mgrid[top:bottom:.25,x0:x1:.25];x=(xx-.375-case['center'][0])/L;y=(yy-.375-case['center'][1])/L;inside=case_geometry(p['shape'],x,y)[0]<=0
  X,Y=settled.mapping(x,y,p);X=X*L+case['center'][0];Y=Y*L+case['center'][1];defined=(X>=0)&(X<W-1)&(Y>=0)&(Y<H-1);scored=np.repeat(np.repeat(valid[top-y0:bottom-y0],4,axis=0),4,axis=1);sample=cv2.remap(source,X.astype(np.float32),Y.astype(np.float32),cv2.INTER_LINEAR)
  for key,mask in [('whole',inside),('ALL_scored',scored)]:
   row=rows[key];row['rays']+=int(mask.sum());row['undefined']+=int((mask&~defined).sum());row['outside_footprint']+=int((mask&~inside).sum())
   if mask.any():
    row['min_x']=min(row['min_x'],float(X[mask].min()));row['max_x']=max(row['max_x'],float(X[mask].max()));row['min_y']=min(row['min_y'],float(Y[mask].min()));row['max_y']=max(row['max_y'],float(Y[mask].max()));row['source_rgb_min']=np.minimum(row['source_rgb_min'],sample[mask].min(0)).tolist();row['source_rgb_max']=np.maximum(row['source_rgb_max'],sample[mask].max(0)).tolist()
   if name=='regular-light':row['light_black_splice_rays']+=int((mask&(Y>=739)).sum())
   else:row['dark_copied_top_rays']+=int((mask&(Y<349)).sum())
 return dict(native_subsamples_per_axis=4,cohorts=rows,source_gaussian_sigma_native=0,defined_finite_RGB_domain_pass=all(v['undefined']==0 for v in rows.values()),observed_confidence='NOT AVAILABLE: archivedsource has no separateconfidence/observedmask; reconstruction/inference explicitly retained, no maskadoption',limits='Originallegacy4x4 whole+ALLscored ray domain only; in-image finiteRGB is not directobservation/sourcecertainty. No source/shadow adoption, no output/HQepoch.')
def main():
 os.umask(0o002)
 if (R/'intake-result.json').exists():print('Protocolintake complete,no repeat');return
 if (R/'started.json').exists():raise RuntimeError('Inspect partialrun before recovery')
 save('started.json',dict(pid=os.getpid(),scope='SOURCE/PROTOCOL ONLY',renders='ONE unchangedlegacy4x4 nativebaseline pertheme from frozenarchivedPNGs; no sourceprepare/registration/paperfit/opticalfit/compositorshadow'))
 expected=json.loads((R/'authoritative-settled-scores.json').read_text());rows=[]
 for name in ['regular-light','regular-dark']:
  case=CASES[name];p=settled.RECIPES[name];assert p['source_sigma']==0 and not p.get('post_sigma') and not case['foreground']
  # Dtypes match archived settled.main explicit8bit source then float64;
  # target retained original decoded float32 after uint8 checkpoint.
  source=np.asarray(Image.open(R/f'{name}-source.png').convert('RGB')).astype(float)/255;target=np.asarray(Image.open(R/f'{name}-target.png').convert('RGB')).astype(np.float32)/255
  pred=settled.render(source,case,p,samples=4);x0,y0,x1,y1=case['crop'];sc=scores(pred,target[y0:y1,x0:x1],case);old=expected[name]['scores'];same={k:sc[k]['rmse']==old[k]['rmse'] for k in ['all_glass','rim','held_blocks','interior','outer_rim']}
  xs,ys,x,y=points(case);sd,train,held,valid=masks(case,xs,ys,x,y);rim=valid&(-sd<L*.2) if (L:=min(case['half'])) else valid
  np.save(R/f'{name}-native-material.npy',pred);np.savez_compressed(R/f'{name}-native-masks.npz',train=train,held=held,all_glass=valid,rim=rim,outer_rim=valid&(-sd<4),interior=valid&~rim)
  support=source_domain(name,case,p,source,valid);row=dict(theme=name,case=case,recipe=p,native_scores=sc,archived_score_exact=same,derived_E_for_protocol_review=math.sqrt(.7*sc['all_glass']['rmse']**2+.3*sc['rim']['rmse']**2),source_domain=support,original_frame_and_source_provenance=expected[name]['frame'],source_construction=expected[name]['registration'],exterior_guard='NONE in original settled scores; publish.contact_context is targetderived unscored residual/distanttarget, not generatedshadow or cleanindependentexteriorbaseline')
  rows.append(row);save('intake-partial.json',rows);print(name,'glass',sc['all_glass']['rmse'],'exact',same,'domain',support['defined_finite_RGB_domain_pass'],flush=True)
 save('intake-result.json',dict(scope='SOURCE/PROTOCOL ONLY',observations=rows,unchanged_native_replay_verified=all(all(r['archived_score_exact'].values()) for r in rows),optical_fit_authorized=False,source_or_shadow_adopted=False,two_independent_theme_recipes=True,new_pass_count=0,limits='Do not silentlyreplacelegacy4x4 covered-sample AA or independenttheme materials with Study2x2/sharedmaterial/source/shadow. Uniform/estimatedsources do not identifyrefraction. Primary mustreviewguard/protocol before anyfit.'))
if __name__=='__main__':main()
