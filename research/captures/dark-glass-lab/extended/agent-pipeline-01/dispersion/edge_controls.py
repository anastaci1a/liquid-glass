"""Fixed ORIGINAL upper/lower cohorts, including edges: not interior-only inference."""
from pathlib import Path
import json,time,numpy as np,cv2
P=Path('/evidence/extended/agent-pipeline-01');O=P/'dispersion';proto=json.loads((O/'protocol.json').read_text());deadline=__import__('datetime').datetime.fromisoformat(proto['deadline'].replace('Z','+00:00')).timestamp();assert time.time()<deadline
out={'new_rays':0,'new_images':0,'new_source_queries':0,'parameter_fits':0,'cohort_rule':'Predeclared upper/lower native crop rectangles; report alloriginalglass plus source-neutral subset maxchannelrange<=1/255. This is an advisory source-only cohort, not an active scoring mask or target-selected threshold.','cases':{}}
for key in ['a','b']:
 case=json.loads((P/f'inputs/{key}/case.json').read_text());x0,y0,x1,y1=case['crop'];target=cv2.imread(str(P/f'inputs/{key}/target.png'))[:,:,::-1].astype(float)/255;target=target[y0:y1,x0:x1];src=np.load(P/'blurriness'/f'{key}-lens-color.npy');alpha=np.load(P/'blurriness'/f'{key}-coverage.npy');mask=np.load(P/f'historical-{key}-masks.npz')['glass'];records={}
 for name,(a,b,c,d) in [('upper',[500,321,1245,355]),('lower',[500,477,1258,509])]:
  box=np.zeros(mask.shape,bool);box[b-y0:d-y0,a-x0:c-x0]=True
  for suffix,m in [('all_scored',box&mask&(alpha==1)),('source_neutral',box&mask&(alpha==1)&(np.ptp(src,axis=2)<=1/255))]:
   if not m.any():continue
   T=target[m];S=src[m];opp=np.stack([(T[:,0]-T[:,1])/np.sqrt(2),(T[:,0]+T[:,1]-2*T[:,2])/np.sqrt(6)],1);records[name+'_'+suffix]={'pixels':int(m.sum()),'target_exact_neutral_fraction':float(((T[:,0]==T[:,1])&(T[:,1]==T[:,2])).mean()),'target_spatial_opponent_RMS_levels':float(np.sqrt(np.mean((opp-opp.mean(0))**2))*255),'target_opponent_mean_levels':(opp.mean(0)*255).tolist(),'source_mean_channel_range_levels':float(np.mean(np.ptp(S,axis=1))*255)}
 out['cases'][key]=records
assert time.time()<deadline;out['finished_unix']=time.time();(O/'edge-controls.json').write_text(json.dumps(out,indent=2));print(json.dumps(out))
