"""Complete sequential display stages on a source-certified geometry."""
from pathlib import Path
import sys,json,datetime,traceback,importlib.util,zipfile,hashlib
import numpy as np,cv2,shutil
from PIL import Image
ROOT=Path(__file__).resolve().parents[3];BASE=Path(__file__).parent;OUT=BASE/sys.argv[1];P=json.loads((OUT/'protocol.json').read_text());END=datetime.datetime.fromisoformat(P['deadline']);stage_end=END
spec=importlib.util.spec_from_file_location('middle_common',ROOT/'research/experiments/miniplayer-middle-ground-99/material_common.py');common=importlib.util.module_from_spec(spec);spec.loader.exec_module(common);common.NATIVE=BASE/P['native']
from shoulder_core_coordinate import ShoulderCoreCoordinate
from miniplayer_refinement_effects import integrate_rims,soft_channel_rim_dark as saturated_rim,low_luminance_body,shadow_field,artwork_study
from geometric_render import incident_source_filter,neutral_color_response
from environment_radiance import decode_srgb,encode_srgb,annular_environment
cv2.setNumThreads(1);ledger=dict.fromkeys(P['caps'],0);first={};rows=[];choices={};stage='setup'
def now():return datetime.datetime.now(datetime.timezone.utc)
def save(n,v):(OUT/n).write_text(json.dumps(v,indent=2,allow_nan=False)+'\n')
def flush():save('ledger.json',ledger)
def charge(k,n):
 assert now()<min(END,stage_end),('Deadline',stage)
 assert ledger[k]+n<=P['caps'][k],(k,ledger[k],n,P['caps'][k]);ledger[k]+=int(n)
 if k=='score_calls':charge('metric_Gaussians',5*n);charge('metric_erosions',n)
def read(p,keys):
 first[str(p.relative_to(ROOT))]=common.sha(p)
 with zipfile.ZipFile(p) as z:
  for k in keys:
   with z.open(k+'.npy') as f:
    version=np.lib.format.read_magic(f);shape,_,dt=(np.lib.format.read_array_header_1_0(f) if version==(1,0) else np.lib.format.read_array_header_2_0(f));assert not dt.hasobject;charge('numeric_bytes',int(np.prod(shape))*dt.itemsize)
 with np.load(p,allow_pickle=False) as z:return {k:z[k] for k in keys}
def begin(name):
 global stage,stage_end
 stage=name;start=now();stage_end=min(END,start+datetime.timedelta(minutes=P['stage_limits_minutes'][name]));save(name+'-clock.json',{'start':start.isoformat(),'deadline':stage_end.isoformat()});print('STAGE',name,start.isoformat(),flush=True)
fx=common.metric_functions(charge);score=fx['score'];data={};paths={};raws={};fields={};alphas={};shadow={};all_metrics={}
def evaluate(label,rawmap,gain,bias,alpha_index=None,shadow_index=None,art=None,retain=False,low_lift=0.):
 metrics=[];outputs={}
 for key,d in data.items():
  m,r=key;s,z=d['s'],d['z'];I=z['inside'];raw=rawmap[key];q=paths[m];H,W=s.valid.shape
  values=raw.copy();graded=low_luminance_body(raw[I],gain,bias,low_lift)
  encoded=encode_srgb(q['primary_power'][I,None]*decode_srgb(graded)+4*q['unit'][:,None]);assert encoded.min()>=0 and encoded.max()<=1,'Candidate requires clipping';values[I]=encoded
  clear=(~I)&z['supported']
  if shadow_index is not None:
   values[clear]*=1-P['shadow'][shadow_index]['opacity']*shadow[m][shadow_index][clear,None]
   assert np.array_equal(values[I],encoded)
  pre=values.reshape(H,2,W,2,3).mean((1,3)).astype(np.float32)
  compositor=s if art is None else artwork_study(s,**art)
  charge('candidate_composites',1);C=compositor.apply_foreground(pre.copy())
  guide=None
  if alpha_index is not None:
   charge('guide_composites',1);guide=compositor.apply_foreground(raw.reshape(H,2,W,2,3).mean((1,3)).astype(np.float32))
   C=saturated_rim(C,guide,alphas[m][alpha_index],curve_power=P['curve_power'][alpha_index],dark_neutral=P['dark_neutral'][alpha_index])
  sc=score(s,C,d['m'],d['partial'],d['crops']);baseline=d['comparison'];cats=[sc['glass']['rmse']/baseline['glass']['rmse'],sc['rim']['rmse']/baseline['rim']['rmse'],sc['exterior']/baseline['exterior'],np.sqrt(sc['foreground']['jupiter.jpg']/baseline['foreground']['jupiter.jpg'])]
  row=dict(member=m,reference=r,setting=label,scores=sc,previous99_guards=common.guards(sc,baseline),original_guards=common.guards(sc,d['original']),normalized_categories=dict(zip(['glass','rim','shadow','artwork'],[float(x) for x in cats])),combined=float(np.mean(cats)))
  training={}
  for category,mask in d['training_masks'].items():
   charge('training_channel_reductions',int(mask.sum())*3)
   training[category]=float(np.sqrt(np.mean(((C[mask]-s.target_crop[mask])*255)**2)))/d['training_denominators'][category]
  row['normalized_training_errors']=training
  metrics.append(row);outputs[key]=(C,pre,guide)
  if retain:
   np.savez_compressed(OUT/f'{m}-{r}-{label}.npz',complete=C,pre_foreground=pre)
   save(f'{m}-{r}-{label}-metrics.json',row)
  print(label,m,r,round(sc['E'],5),flush=True)
 rows.extend(metrics);save('all-metrics.json',rows);flush();all_metrics[label]=metrics
 return metrics,outputs

def select(labels,category):
 def loss(label):return float(np.mean([x['normalized_training_errors'][category] for x in all_metrics[label]]))
 ranked={k:loss(k) for k in labels};chosen=min(ranked,key=ranked.get);choices[stage]=dict(chosen=chosen,category=category,mean_normalized_training_errors=ranked,held_excluded=True,finished=now().isoformat());save('choices.json',choices);return labels.index(chosen)

def run():
 global data,stage_end
 assert not (OUT/'started.json').exists();save('started.json',{'at':now().isoformat()});save('durable-reservations.json',P)
 for p in [Path(__file__),ROOT/'reconstruction/miniplayer_refinement_effects.py',ROOT/'reconstruction/shoulder_core_coordinate.py',ROOT/'reconstruction/extended_fit.py',ROOT/'reconstruction/geometric_render.py',ROOT/'reconstruction/environment_radiance.py']:first[str(p.relative_to(ROOT))]=common.sha(p)
 data=common.load_data(charge,first)
 F=common.F;L=common.L
 for (m,r),d in data.items():
  d['half'][0]+=1.5;d['center'][0]-=.5;d['radius']-=1.25
  d['coord']=ShoulderCoreCoordinate(tuple(d['half']),d['radius'],P['shoulder_native'])
  old=ROOT/f'research/experiments/miniplayer-middle-ground-99/peak-brightness/{m}-{r}-floor0.24-metrics.json';first[str(old.relative_to(ROOT))]=common.sha(old);d['comparison']=json.loads(old.read_text())['scores']
  masks={cat:d['m'][name]&~d['m']['held'] for cat,name in [('glass','glass'),('rim','rim'),('shadow','exterior')]};artmask=np.zeros(d['s'].valid.shape,bool);x0,y0,_,_=d['s'].crop
  for layer in d['s'].case['foreground_layers']:
   if layer['mode']=='artwork':a,b,c,e=layer['box'];artmask[b-y0:e-y0,a-x0:c-x0]=True
  masks['artwork']=artmask&~d['m']['held'];d['training_masks']=masks
  baseline=read(ROOT/f'research/experiments/miniplayer-middle-ground-99/peak-brightness/{m}-{r}-floor0.24.npz',['complete'])['complete'];den={}
  for cat,mask in masks.items():
   charge('training_channel_reductions',int(mask.sum())*3);den[cat]=float(np.sqrt(np.mean(((baseline[mask]-d['s'].target_crop[mask])*255)**2)));assert den[cat]>0
  d['training_denominators']=den
  charge('identity_composites',1);assert np.array_equal(d['s'].apply_foreground(d['z']['pre_foreground'].copy()),d['z']['complete'],equal_nan=True)
  assert score(d['s'],d['z']['complete'],d['m'],d['partial'],d['crops'])==d['before']
 for m in ['expanded','compact']:
  q=read(common.NATIVE/f'{m}-paths.npz',['X','Y','inside','primary_power','front_reflection_power','front_reflection_direction']);I=q['inside'];charge('environment_points',int(I.sum()));q['unit']=q['front_reflection_power'][I]*annular_environment(q['front_reflection_direction'][I]);paths[m]=q
 raws[6.075]={key:d['z']['raw_source'] for key,d in data.items()}
 basegain,basebias=F['material']['gain'],F['material']['bias']
 save('checkpoint.json',{'at':now().isoformat(),'four_foreground_and_metric_identities_exact':True})
 begin('blur')
 # Both references for each width/member are certified before changed fields.
 proofs=[]
 for sigma in P['blur']:
  if sigma==6.075:continue
  raws[sigma]={};radius=int(np.ceil(3*sigma))
  for m in ['expanded','compact']:
   q=paths[m];I=q['inside'];d=data[(m,'a')];X=q['X']*L+d['center'][0];Y=q['Y']*L+d['center'][1];a=np.floor(X).astype(int);b=np.floor(Y).astype(int);i,j=np.nonzero(I);masks={}
   for r in ['a','b']:
    s=data[(m,r)]['s'];path=s.folder/'known.png';first[str(path.relative_to(ROOT))]=common.sha(path);charge('bitmap_pixels',1920*1080);known=cv2.imread(str(path),0)>0
    charge('known_erosions',1);safe=cv2.erode(known.astype(np.uint8),np.ones((2*radius+1,2*radius+1),np.uint8),borderType=cv2.BORDER_CONSTANT,borderValue=0)>0
    charge('source_audit_subrays',len(i));assert ((a[i,j]>=0)&(b[i,j]>=0)&(a[i,j]+1<1920)&(b[i,j]+1<1080)).all();charge('source_corner_lookups',4*len(i));ok=safe[b[i,j],a[i,j]]&safe[b[i,j]+1,a[i,j]]&safe[b[i,j],a[i,j]+1]&safe[b[i,j]+1,a[i,j]+1];assert ok.all(),'Changed kernel unsupported'
    proofs.append(dict(member=m,reference=r,sigma=sigma,radius=radius,lens_subrays=len(i),unsupported=0));masks[r]=(known,safe)
   save('blur-source-FIRST.json',{'records':proofs,'gate':'Both current member references pass before any changed field or RGB; clear rays unchanged.'})
   for r in ['a','b']:
    s=data[(m,r)]['s'];known,safe=masks[r];charge('incident_fields',1);charge('known_erosions',1);field,safe2,rad=incident_source_filter(s.source,known,sigma);assert rad==radius and np.array_equal(safe,safe2)
    wx=(X[i,j]-a[i,j])[:,None];wy=(Y[i,j]-b[i,j])[:,None];charge('RGB_queries',len(i));values=(field[b[i,j],a[i,j]]*(1-wx)+field[b[i,j],a[i,j]+1]*wx)*(1-wy)+(field[b[i,j]+1,a[i,j]]*(1-wx)+field[b[i,j]+1,a[i,j]+1]*wx)*wy
    raw=raws[6.075][(m,r)].copy();raw[I]=values;assert np.array_equal(raw[~I],raws[6.075][(m,r)][~I],equal_nan=True);raws[sigma][(m,r)]=raw
    np.savez_compressed(OUT/f'{m}-{r}-blur{sigma}-samples.npz',raw_source=raw)
 labels=[]
 for sigma in P['blur']:
  label=f'blur{sigma}';labels.append(label);evaluate(label,raws[sigma],basegain,basebias,retain=True)
 ix=select(labels,'glass');sigma=P['blur'][ix];rawmap=raws[sigma]
 begin('color');labels=[]
 for i,p in enumerate(P['color']):
  label=f'color{i}';labels.append(label);evaluate(label,rawmap,p['gain'],p['bias'],retain=True,low_lift=p['low_lift'])
 ci=select(labels,'glass');gain,bias=P['color'][ci]['gain'],P['color'][ci]['bias']
 low_lift=P['color'][ci]['low_lift']
 begin('outline');angular=json.loads((ROOT/'research/experiments/miniplayer-complete-refinement-94/highlight/protocol.json').read_text())['config'];integration=[]
 for m in ['expanded','compact']:
  d=data[(m,'a')];old=None
  for order in P['orders']:
   alpha=integrate_rims(d['s'].crop,d['coord'],d['center'],angular,P['profiles'][:1],order,charge);alpha=np.repeat(alpha,3,axis=0)
   np.savez_compressed(OUT/f'{m}-alpha{order}.npz',alpha=alpha)
   diff=None if old is None else float(np.max(abs(alpha-old)));integration.append(dict(member=m,order=order,maximum_difference=diff));save('integration.json',integration);flush();print('ALPHA',m,order,diff,flush=True)
   if diff is not None and diff<=P['maximum_order_difference']:break
   old=alpha
  assert diff is not None and diff<=P['maximum_order_difference'],'Unconverged rim integration';alphas[m]=alpha
 labels=[]
 for i in range(3):
  label=f'outline{i}';labels.append(label);evaluate(label,rawmap,gain,bias,alpha_index=i,retain=True,low_lift=low_lift)
 oi=select(labels,'rim')
 begin('shadow')
 for m in ['expanded','compact']:
  d=data[(m,'a')];shadow[m]={}
  for i,p in enumerate(P['shadow']):
   shadow[m][i]=shadow_field(d['s'].crop,d['coord'],d['center'],p['sigma_x'],p['sigma_y'],p['offset'],charge)
   np.savez_compressed(OUT/f'{m}-shadow{i}.npz',field=shadow[m][i])
 labels=[]
 for i in range(3):
  label=f'shadow{i}';labels.append(label);evaluate(label,rawmap,gain,bias,alpha_index=oi,shadow_index=i,retain=True,low_lift=low_lift)
 si=select(labels,'shadow')
 begin('artwork');labels=[]
 for i,p in enumerate(P['artwork']):
  label=f'artwork{i}';labels.append(label);evaluate(label,rawmap,gain,bias,alpha_index=oi,shadow_index=si,art=p,retain=True,low_lift=low_lift)
 ai=select(labels,'artwork');stage_end=END
 final=all_metrics[f'artwork{ai}'];outputs={}
 for key in data:
  m,r=key;z=read(OUT/f'{m}-{r}-artwork{ai}.npz',['complete','pre_foreground']);outputs[key]=(z['complete'],z['pre_foreground'],None);shutil.copyfile(OUT/f'{m}-{r}-artwork{ai}.npz',OUT/f'{m}-{r}-final.npz');row=next(x for x in final if x['member']==m and x['reference']==r);save(f'{m}-{r}-final-metrics.json',row)
 for (m,r),d in data.items():
  C,pre,guide=outputs[(m,r)];charge('presentation_panels',1);common.panels(OUT,f'{m}-{r}-final',d,C,fx['to_image'],'Pass 4 complete candidate; local regressions disclosed')
 save('final-recipe.json',dict(native=P['native'],sigma=sigma,gain=gain,bias=bias,outline=P['profiles'][oi],curve_power=P['curve_power'][oi],dark_neutral=P['dark_neutral'][oi],low_lift=low_lift,outline_index=oi,shadow=P['shadow'][si],shadow_index=si,artwork=P['artwork'][ai],artwork_index=ai,response='soft-channel-dark-neutral'))
 save('result.json',{'finished':now().isoformat(),'records':final,'combined_normalized_score':float(np.mean([r['combined'] for r in final])),'selected_state_changed':False,'own_independent_final_replay':'Pending separate verifier','dispersion':'Excluded by scope'})
 assert first=={p:common.sha(ROOT/p) for p in first};save('hashes.json',first);flush()
try:run()
except Exception as e:save('failure.json',{'at':now().isoformat(),'stage':stage,'error':repr(e),'traceback':traceback.format_exc()});flush();raise
