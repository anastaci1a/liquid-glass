from pathlib import Path
import sys,json,datetime,hashlib,zipfile,struct,ast,math
import numpy as np,cv2
from PIL import Image,ImageDraw
O=Path(__file__).parent;ROOT=O.parents[2];BASE=O.parent/'agent-search-shallow-transfer-39';B=O.parent/'agent-music-search-baseline-01';SEL=O.parent/'agent-music-search-neutral-05';WORK=ROOT/'.evidence-working/music-search-baseline-01';P=json.loads((O/'protocol.json').read_text());ledger={k:0 for k in P['caps']};meta={'NPY_bytes':0,'NPY_members':0,'header_bytes_bound':0,'PNG_pixels':0,'crop_pixel_reductions':0};headers=[]
def gate(cp=False):assert datetime.datetime.now(datetime.timezone.utc)<datetime.datetime.fromisoformat(P['checkpoint_deadline' if cp else 'deadline'].replace('Z','+00:00')),'Original deadline'
def charge(k,n):gate();assert ledger[k]+n<=P['caps'][k],k;ledger[k]+=int(n)
def save(f,v):(O/f).write_text(json.dumps(v,indent=2,allow_nan=False)+'\n')
# Only inert helper definitions are reused; no old experiment body or hook runs.
helper=O.parent/'agent-search-shallow-blur-40/run.py';tree=ast.parse(helper.read_text());names={'load','metric','local'};defs=[n for n in ast.walk(tree) if isinstance(n,ast.FunctionDef) and n.name in names];assert len(defs)==3;exec(compile(ast.Module(body=defs,type_ignores=[]),str(helper),'exec'))
for f,h in json.loads((O/'first-hashes.json').read_text()).items():assert hashlib.sha256((ROOT/f).read_bytes()).hexdigest()==h,f
proposal=json.loads((O/'shared-proposal.json').read_text());assert proposal['gain']==P['gain'] and proposal['bias']==P['bias']
for k in ['a','b']:
 for name in ['source.png','target.png']:
  h=(WORK/k/name).read_bytes()[:33];assert h[:8]==b'\x89PNG\r\n\x1a\n';w,v,depth,color,*_=struct.unpack('>IIBBBBB',h[16:29]);assert (w,v)==(1920,1080) and depth==8;headers.append({'path':str((WORK/k/name).relative_to(ROOT)),'PNG_size':[w,v],'depth':depth,'color':color})
sys.path.insert(0,str(ROOT/'reconstruction'))
from extended_fit import Study
from geometric_render import neutral_color_response
from environment_radiance import decode_srgb,encode_srgb,annular_environment
cv2.setNumThreads(1);data={};result={'status':'STARTING','records':[]}
try:
 q=load(BASE/'native-paths.npz',['X','Y','inside','primary_power','front_reflection_power','front_reflection_direction']);inside=q['inside'];I=int(inside.sum());assert I==98989;charge('cached_annular_directions',I);unit=q['front_reflection_power'][inside]*annular_environment(q['front_reflection_direction'][inside]);power=q['primary_power'][inside]
 for k in ['a','b']:
  charge('Study_constructors',1);st=Study(WORK/k);H,W=st.valid.shape;charge('mask_points',H*W);meta['PNG_pixels']+=2*1920*1080;m=load(B/f'{k}-masks.npz',['glass','rim','held','exterior','foreground','required']);assert np.array_equal(st.valid,m['glass']) and np.array_equal(st.rim,m['rim']) and np.array_equal(st.held,m['held']);old=load(BASE/f'{k}-candidate.npz',['sample_before_response','pre_foreground','complete','coverage','inside','support']);assert np.array_equal(inside,old['inside']);raw=old['sample_before_response'];v=raw.copy();v[inside]=np.clip(encode_srgb(power[:,None]*decode_srgb(neutral_color_response(raw[inside],gain=P['old_gain'],bias=P['old_bias']))+4*unit[:,None]),0,1);pre=v.reshape(H,2,W,2,3).mean((1,3)).astype(np.float32);charge('identity_composites',1);C=st.apply_foreground(pre.copy());assert np.array_equal(pre,old['pre_foreground'],equal_nan=True) and np.array_equal(C,old['complete'],equal_nan=True),'Baseline39 identity';selected=load(SEL/f'full-{k}-candidate.npz',['complete'])['complete'];data[k]={'st':st,'m':m,'old':old,'selected':selected}
 gate(True);save('checkpoint.json',{'status':'PASS_FROZEN_CODE_INPUT_MASK_CACHE_HEADERS_TWO_EXACT_IDENTITIES','at':datetime.datetime.now(datetime.timezone.utc).isoformat(),'ledger':ledger.copy(),'decode':meta.copy()});print('CHECKPOINT_PASS',flush=True)
 crops=json.loads((B/'RGB-started.json').read_text())['fixed_original_frame_crops']
 for k,d in data.items():
  gate();st=d['st'];m=d['m'];raw=d['old']['sample_before_response'];grade,preclip=neutral_color_response(raw[inside],gain=P['gain'],bias=P['bias'],return_preclip=True);linear=power[:,None]*decode_srgb(grade)+4*unit[:,None];encoded=encode_srgb(linear);v=raw.copy();v[inside]=np.clip(encoded,0,1);assert np.array_equal(v[~inside],raw[~inside],equal_nan=True),'Clear changed';pre=v.reshape(H,2,W,2,3).mean((1,3)).astype(np.float32);charge('candidate_composites',1);C=st.apply_foreground(pre.copy());scores={'original':metric(st,pre,m),'complete':metric(st,C,m)};scores['original']['foreground_RMSE']=scores['complete']['foreground_RMSE'];partial=m['glass']&(d['old']['coverage']<1);assert int(partial.sum())==38;part=float(np.sqrt(np.mean(((C-st.target_crop)[partial]*255)**2)));baseline=json.loads((BASE/f'{k}-metrics.json').read_text());selected=json.loads((SEL/f'full-{k}-result.json').read_text())['scores'];guards={}
  for name,before in [('selected',selected),('shallow39',baseline['scores'])]:
   g={}
   for role in ['original','complete']:
    now=scores[role];old=before[role];g[role]={n:now[n]['rmse']<=old[n]['rmse'] for n in ['glass','rim','held','interior']};g[role].update(E=now['E']<=old['E'],SSIM=now['ssim']>=old['ssim'],exterior=now['exterior_RMSE']<=old['exterior_RMSE'],foreground=now['foreground_RMSE']<=old['foreground_RMSE'])
   g['partial38']=part<=(baseline['partial_selected'] if name=='selected' else baseline['partial38_RMSE']);guards[name]=g
  np.savez_compressed(O/f'{k}-candidate.npz',sample_after_response=v,neutral_preclip_inside=preclip,linear_inside=linear,encoded_preclip_inside=encoded,pre_foreground=pre,complete=C,coverage=d['old']['coverage']);row={'reference':k,'gain':P['gain'],'bias':P['bias'],'scores':scores,'guards':guards,'partial38_RMSE':part,'partial_baseline39':baseline['partial38_RMSE'],'partial_selected':baseline['partial_selected'],'clipping':{'neutral_low':int((preclip<0).sum()),'neutral_high':int((preclip>1).sum()),'encoded_low':int((encoded<0).sum()),'encoded_high':int((encoded>1).sum())},'clear_exact':True,'fixed_crops':local(st,C),'baseline_crops':local(st,d['old']['complete']),'selected_crops':local(st,d['selected']),'conditional_scene':True,'tail_unassigned':True};result['records'].append(row);save(k+'-metrics.json',row)
  canvas=Image.new('RGB',(1926,540),'white');draw=ImageDraw.Draw(canvas)
  for j,(arr,title) in enumerate([(st.target_crop,'Apple'),(d['selected'],'Selected Search'),(d['old']['complete'],'Shallow39 working colour'),(C,'Exact shared full-step colour')]):
   finite=np.isfinite(arr).all(2);yy,xx=np.indices(finite.shape);display=np.where(finite[...,None],arr,np.where(((xx//6+yy//6)%2)[...,None],.72,.9));im=Image.fromarray(np.uint8(np.rint(np.clip(display,0,1)*255)));canvas.paste(im.resize((480,470),Image.Resampling.NEAREST),(482*j,64));draw.text((482*j+8,20),title,fill='black')
  canvas.save(O/f'{k}-comparison.png');print('CANDIDATE',k,scores['complete']['E'],guards,flush=True)
 result['status']='ONE_UNFITTED_SHARED_COLOUR_TRANSFER_READY';result['selected_state_changed']=False
except Exception as e:result.update(status='STOPPED_FIRST_INVARIANT',failure=repr(e));print('STOP',repr(e),flush=True)
finally:
 result.update(finished=datetime.datetime.now(datetime.timezone.utc).isoformat(),ledger=ledger,new_rays_heights_queries_fields_filters_fits=0);save('result.json',result);save('decode-and-analysis.json',{'actual':meta,'headers':headers});print('FINAL',result['status'],ledger,flush=True)
