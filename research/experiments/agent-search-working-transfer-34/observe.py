from pathlib import Path
import sys,json,datetime,hashlib
import numpy as np,cv2
from PIL import Image,ImageDraw
O=Path(__file__).parent;ROOT=O.parents[2];OLD=O.parent/'agent-search-family-forward-29';B=O.parent/'agent-music-search-baseline-01';T=O.parent/'agent-music-search-neutral-05';WORK=ROOT/'.evidence-working/music-search-baseline-01'
P=json.loads((O/'protocol.json').read_text());F=json.loads((O/'working-recipe.json').read_text());ledger={k:0 for k in P['caps']}
def gate(checkpoint=False):assert datetime.datetime.now(datetime.timezone.utc)<datetime.datetime.fromisoformat(P['checkpoint_deadline' if checkpoint else 'deadline'].replace('Z','+00:00'))
def charge(k,n):gate();assert ledger[k]+n<=P['caps'][k],k;ledger[k]+=int(n)
def save(f,v):(O/f).write_text(json.dumps(v,indent=2,allow_nan=False)+'\n')
sys.path.insert(0,str(ROOT/'reconstruction'))
from extended_fit import Study
from geometric_render import neutral_color_response
from environment_radiance import annular_environment,decode_srgb,encode_srgb
cv2.setNumThreads(1);data={};result={'status':'STARTING','records':[]}
try:
 for f,h in json.loads((O/'first-hashes.json').read_text()).items():assert hashlib.sha256((ROOT/f).read_bytes()).hexdigest()==h,f
 q=np.load(OLD/'native-paths.npz',allow_pickle=False);inside=q['inside'];charge('cached_annular_evaluations',int(inside.sum()));unit=q['front_reflection_power'][inside]*annular_environment(q['front_reflection_direction'][inside]);power=q['primary_power'][inside];assert np.isfinite(power).all() and ((power>=0)&(power<=1)).all()
 for k in ['a','b']:
  charge('Study_constructors',1);s=Study(WORK/k);H,W=s.valid.shape;charge('mask_points',H*W);m=dict(np.load(B/f'{k}-masks.npz',allow_pickle=False));assert np.array_equal(s.valid,m['glass']) and np.array_equal(s.rim,m['rim']) and np.array_equal(s.held,m['held'])
  old=np.load(OLD/f'{k}-candidate.npz',allow_pickle=False);raw=old['sample_before_response'];assert np.array_equal(inside,old['inside'])
  v=raw.copy();v[inside]=np.clip(encode_srgb(decode_srgb(neutral_color_response(raw[inside],gain=.596189238519786,bias=.3290237590837732))+4*unit[:,None]),0,1);pre=v.reshape(H,2,W,2,3).mean((1,3)).astype(np.float32);charge('identity_composites',1);C=s.apply_foreground(pre.copy());assert np.array_equal(pre,old['pre_foreground'],equal_nan=True) and np.array_equal(C,old['complete'],equal_nan=True),'Search29 identity'
  data[k]=(s,m,old,raw,H,W)
 gate(True);save('checkpoint.json',{'status':'PASS_TWO_EXACT_29_IDENTITIES_AND_FROZEN_BYTES','at':datetime.datetime.now(datetime.timezone.utc).isoformat(),'ledger':ledger.copy(),'original_foreground_extension':'Use completed foreground scalar for both original and complete historical conventions; retain29 as-run correction separately'})
 crops=json.loads((B/'RGB-started.json').read_text())['fixed_original_frame_crops']
 def metric(s,a,m):
  charge('score_calls',1);charge('metric_Gaussians',5);charge('metric_erosions',1);z=s.scores(a);z['E']=float(np.sqrt(z['loss']));e=(a-s.target_crop)*255;z['exterior_RMSE']=float(np.sqrt(np.mean(e[m['exterior']]**2)));z['foreground_RMSE']=float(np.sqrt(np.mean(e[m['foreground']]**2)));return z
 def local(s,C):
  out={};x0,y0,_,_=s.crop;luma=np.array([.2126,.7152,.0722])
  for name,(a,b,c,d) in crops.items():
   e=(C[b-y0:d-y0,a-x0:c-x0].astype(float)-s.target_crop[b-y0:d-y0,a-x0:c-x0].astype(float))*255;e=e[np.isfinite(e).all(2)];Y=e@luma;ch=e-Y[:,None];out[name]={'bounds':[a,b,c,d],'RGB_RMSE':float(np.sqrt(np.mean(e*e))),'luma_RMSE':float(np.sqrt(np.mean(Y*Y))),'chroma_RMSE':float(np.sqrt(np.mean(ch*ch))),'signed_RGB':e.mean(0).tolist()}
 for k,(s,m,old,raw,H,W) in data.items():
  gate();grade,preclip=neutral_color_response(raw[inside],gain=F['material']['gain'],bias=F['material']['bias'],return_preclip=True);linear=power[:,None]*decode_srgb(grade)+4*unit[:,None];encoded=encode_srgb(linear);v=raw.copy();v[inside]=np.clip(encoded,0,1);pre=v.reshape(H,2,W,2,3).mean((1,3)).astype(np.float32);charge('candidate_composites',1);C=s.apply_foreground(pre.copy());scores={'original':metric(s,pre,m),'complete':metric(s,C,m)};scores['original']['foreground_RMSE']=scores['complete']['foreground_RMSE'];partial=m['glass']&(old['coverage']<1);assert int(partial.sum())==38;part=float(np.sqrt(np.mean(((C-s.target_crop)[partial]*255)**2)))
  selected=json.loads((T/f'full-{k}-result.json').read_text())['scores'];prior=json.loads((OLD/f'{k}-metrics.json').read_text());prior_scores=json.loads(json.dumps(prior['scores']));prior_scores['original']['foreground_RMSE']=prior_scores['complete']['foreground_RMSE'];guards={}
  for name,base in [('selected',selected),('Search29',prior_scores)]:
   g={}
   for role in ['original','complete']:
    z=scores[role];before=base[role];g[role]={n:z[n]['rmse']<=before[n]['rmse'] for n in ['glass','rim','held','interior']};g[role].update(E=z['E']<=before['E'],SSIM=z['ssim']>=before['ssim'],exterior=z['exterior_RMSE']<=before['exterior_RMSE'],foreground=z['foreground_RMSE']<=before['foreground_RMSE'])
   baselinepart=prior['partial38_baseline'] if name=='selected' else prior['partial38_RMSE'];g['partial38']=part<=baselinepart;guards[name]=g
  assert np.array_equal(v[~inside],raw[~inside],equal_nan=True),'Clear changed'
  np.savez_compressed(O/f'{k}-candidate.npz',sample_after_response=v,linear_inside=linear,encoded_preclip_inside=encoded,neutral_preclip_inside=preclip,pre_foreground=pre,complete=C,coverage=old['coverage'])
  row={'reference':k,'gain':F['material']['gain'],'bias':F['material']['bias'],'scores':scores,'guards':guards,'partial38_RMSE':part,'partial_selected':prior['partial38_baseline'],'partial29':prior['partial38_RMSE'],'clipping':{'neutral_below':int((preclip<0).sum()),'neutral_above':int((preclip>1).sum()),'encoded_below':int((encoded<0).sum()),'encoded_above':int((encoded>1).sum())},'clear_exact':True,'fixed_crops':local(s,C),'selected_crops':prior['baseline_crops'],'Search29_crops':prior['fixed_crops'],'tail_unassigned':True};result['records'].append(row);save(f'{k}-metrics.json',row)
  canvas=Image.new('RGB',(1926,540),'white');draw=ImageDraw.Draw(canvas)
  for j,(arr,label) in enumerate([(s.target_crop,'Apple'),(np.load(T/f'full-{k}-candidate.npz')['complete'],'Selected Search'),(old['complete'],'Search29'),(C,'Working family transfer34')]):
   finite=np.isfinite(arr).all(2);yy,xx=np.indices(finite.shape);display=np.where(finite[...,None],arr,np.where(((xx//6+yy//6)%2)[...,None],.72,.9));im=Image.fromarray(np.uint8(np.rint(np.clip(display,0,1)*255)));canvas.paste(im.resize((480,470),Image.Resampling.NEAREST),(j*482,64));draw.text((j*482+8,20),label,fill='black')
  canvas.save(O/f'{k}-comparison.png');print('CANDIDATE',k,scores['complete']['E'],guards,flush=True)
 result['status']='ONE_UNFITTED_WORKING_TRANSFER_PAIR_READY';result['selected_state_changed']=False
except Exception as e:result['status']='STOPPED_FIRST_FAILURE';result['failure']=repr(e)
finally:
 result.update(ledger=ledger,finished=datetime.datetime.now(datetime.timezone.utc).isoformat(),new_rays_source_queries_filters_Fresnel_fits=0);save('result.json',result);print(result['status'],result.get('failure'),flush=True)
