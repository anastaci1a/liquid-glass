import sys,json,copy,time,itertools
from pathlib import Path
sys.path.insert(0,'/workspace/docs/liquid-glass/experiments/reconstruction');sys.path.insert(0,'/evidence/extended')
import cv2,numpy as np
cv2.setNumThreads(1)
from extended_fit import Study
from switch_native_cache import NativeCachedStudy
from switch_snell_dispersion import SnellStudy,InvalidSnell,ray_scale
from revision_replay import clean_composite
root=Path('/evidence/extended/active-switch');out=root/'rev3-snell-review';out.mkdir(exist_ok=True)
base=json.loads((root/'joint-native-review/candidate.json').read_text());v=json.loads((root/'joint-native-review/hq/verification.json').read_text());old=[v['candidate']['observations'][n] for n in ['A','B']]
class CachedSnell(NativeCachedStudy):
 def geometry_field(self,x,y,p):return super().geometry_field(x,y,{k:v for k,v in p.items() if k!='snell_dispersion'})
 field=SnellStudy.field
S=[CachedSnell(root/'paired'/n,base['parameters']) for n in ['a','b']];co=np.array(base['material']);p=base['parameters']
maxr=0.
for s in S:
 for _,_,_,x,y in s.raster_tiles():
  X,Y,_,_=s.geometry_field(x,y,p);*_,(sd,_,_)=s.shape(x,y,p)
  if (sd<=0).any():maxr=max(maxr,float(np.hypot(X-x,Y-y)[sd<=0].max()))
# Numerical local Snell identities, zero dispersion and small-angle limit.
a=np.linspace(0,.60,100);n0=1.5;delta=np.arcsin(n0*np.sin(a))-a;recovered=np.arctan2(np.sin(delta),n0-np.cos(delta));assert np.max(abs(a-recovered))<1e-12
r=np.linspace(0,.9,100);k=ray_scale(r,2.,n0,n0,np.ones(100,bool));assert np.max(abs(k-1))<1e-12
trials=[(.90,0.,True)]+[(m,d,True) for m,d in itertools.product([.8,.95,.985],[.003,.01,.025])]+[(.95,.01,False),(.985,.01,False)]
rows=[]
for margin,dn,keep in trials:
 gap=maxr*1.001/np.tan(np.arcsin(margin)-np.arcsin(margin/n0));p=copy.deepcopy(base['parameters']);p['snell_dispersion']=dict(gap=float(gap),n0=n0,delta_n=dn,retain_directional=keep);t=time.time()
 row=dict(margin=margin,parameters=p['snell_dispersion'])
 try:
  scores=[]
  for i,s in enumerate(S):
   im=s.render(p,co);m=s.scores(im,include_ssim=False);C=clean_composite(s,p,im);ext=(s.sd>0)&(s.sd<.35);m['shadow']={'rmse':float(np.sqrt(np.mean(((C-s.target_crop)[ext]*255)**2)))};scores.append(m)
   if dn==0:assert abs(m['loss']-old[i]['loss'])<1e-7,(m['loss'],old[i]['loss'])
  ratios=[float(np.sqrt(a['loss']/b['loss'])) for a,b in zip(scores,old)];guards=[a['glass']['rmse']<=b['glass']['rmse']+1e-8 and a['shadow']['rmse']<=b['shadow']['rmse']+1e-8 for a,b in zip(scores,old)]
  row.update(scores=scores,ratios=ratios,guards=guards,numeric_pass=all(g and r<=.995 for g,r in zip(guards,ratios)))
 except InvalidSnell as e:row.update(invalid=str(e),numeric_pass=False)
 row['seconds']=time.time()-t;rows.append(row);print('SNELL',margin,dn,keep,row.get('ratios',row.get('invalid')),row['numeric_pass'],flush=True)
 (out/'screen.json').write_text(json.dumps(dict(baseline=base,baseline_scores=old,max_displacement_over_L=maxr,tests=dict(inverse_snell=True,zero_dispersion=True),trials=rows,accepted=False,limits='Local-normal approximation only. No integrability/physical thickness proof. RGB samples not spectrum. New source rays require full proof before adoption.'),indent=2)+'\n')
