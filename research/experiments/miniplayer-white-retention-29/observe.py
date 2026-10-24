"""One fixed lossless primary/direct-front partition from retained actual paths."""
from pathlib import Path
import sys,json,datetime,ast,hashlib
import numpy as np,cv2
from PIL import Image,ImageDraw,ImageFont
ROOT=Path(__file__).resolve().parents[3];OUT=Path(__file__).parent;D=ROOT/'research/experiments/miniplayer-inverse-forward-18';M=ROOT/'research/experiments/miniplayer-incident-material-20'
P=json.loads((OUT/'protocol.json').read_text());END=datetime.datetime.fromisoformat(P['deadline'].replace('Z','+00:00'));ledger={k:0 for k in P['caps']}
def save(n,v):(OUT/n).write_text(json.dumps(v,indent=2,allow_nan=False)+'\n')
def gate():assert datetime.datetime.now(datetime.timezone.utc)<END,'Original deadline'
def charge(k,n):
 gate();assert ledger[k]+n<=P['caps'][k],k;ledger[k]+=int(n);save('ledger.json',ledger)
def load(p):
 z=np.load(p,allow_pickle=False);v={k:z[k] for k in z.files};return v
assert not (OUT/'started.json').exists();save('started.json',{'at':datetime.datetime.now(datetime.timezone.utc).isoformat()})
sys.path.insert(0,str(ROOT/'reconstruction'))
from extended_fit import Study
from geometric_render import neutral_color_response
from environment_radiance import annular_environment,decode_srgb,encode_srgb
cv2.setNumThreads(1);F=json.loads((ROOT/'reconstruction/families/music-mini-player.json').read_text());WF=json.loads((ROOT/'reconstruction/families/music-mini-player-working.json').read_text());from geometric_optics import fresnel_components
charge('normal_calibration_points',1);Rnormal=float(fresnel_components(np.array([1.]),1.,1.5).mean());Tnormal=(1-Rnormal)**2;oldwhite=F['material']['gain']+F['material']['bias'];newwhite=float(encode_srgb(decode_srgb(np.array(oldwhite))/Tnormal));NEWG=WF['material']['gain'];NEWB=newwhite-NEWG;assert np.float32(encode_srgb(Tnormal*decode_srgb(np.array(NEWG+NEWB))))==np.float32(oldwhite);assert 0<NEWB and NEWG+NEWB<1
save('white-calibration.json',dict(old_encoded_white=oldwhite,new_incident_white=newwhite,normal_transmission=Tnormal,gain=NEWG,bias=NEWB,float32_normal_white_exact=True,target_fit=False))
oldproto=json.loads((D/'protocol.json').read_text())
tree=ast.parse((ROOT/'research/experiments/miniplayer-outline-light-07/render.py').read_text());defs=[n for n in tree.body if isinstance(n,ast.FunctionDef) and n.name in ['score','display','to_image']];exec(compile(ast.Module(body=defs,type_ignores=[]),'frozen-score-display','exec'))
bindings={};data=[];identity=[]
for member in ['expanded','compact']:
 q=load(D/f'{member}-paths.npz');inside=q['inside'];charge('scene_queries',int(inside.sum()));unit=q['front_reflection_power'][inside]*annular_environment(q['front_reflection_direction'][inside]);T=q['primary_power'][inside]
 closure=q['front_reflection_power'][inside]+T+q['retained_back_power'][inside];assert np.max(abs(closure-1))<2e-14
 work=ROOT/('.evidence-working/expanded-geometry-02' if member=='expanded' else '.evidence-working/compact-geometry-01')
 for ref in ['a','b']:
  charge('Study_constructors',1);s=Study(work/ref);H,W=s.valid.shape;charge('mask_points',H*W)
  m=load(work/f'{ref}-masks.npz' if member=='expanded' else ROOT/f'research/experiments/compact-geometry-01/{ref}-masks.npz');assert np.array_equal(s.valid,m['glass']) and np.array_equal(s.rim,m['rim']) and np.array_equal(s.held,m['held'])
  path=M/f'{member}-{ref}-factor0.5.npz';bindings[str(path.relative_to(ROOT))]=hashlib.sha256(path.read_bytes()).hexdigest();saved=load(path);source=load(D/f'{member}-{ref}-light4.npz');raw=source['raw_source'];values=raw.copy();values[inside]=neutral_color_response(raw[inside],gain=WF['material']['gain'],bias=WF['material']['bias']);lin=decode_srgb(values[inside])
  replay=values.copy();replay[inside]=np.clip(encode_srgb(T[:,None]*lin+4*unit[:,None]),0,1);pre=replay.reshape(H,2,W,2,3).mean((1,3)).astype(np.float32);charge('identity_composites',1);C=s.apply_foreground(pre.copy());assert np.array_equal(pre,saved['pre_foreground'],equal_nan=True) and np.array_equal(C,saved['complete'],equal_nan=True)
  frozen=load(ROOT/f'research/experiments/compact-geometry-01/{ref}-raw.npz')['coverage'] if member=='compact' else source['coverage'];partial=m['glass']&(frozen<1);charge('metric_gaussians',5);charge('metric_erosions',1);scores=score(s,C,m,partial,oldproto['fixed_crops'][member]);old=json.loads((M/f'{member}-{ref}-factor0.5-metrics.json').read_text());old['baseline']=json.loads((D/f'{member}-{ref}-light4-metrics.json').read_text())['baseline'];assert scores==old['scores']
  identity.append({'member':member,'reference':ref,'pre_foreground_exact':True,'complete_exact':True,'scores_exact':True,'closure_max_error':float(np.max(abs(closure-1)))})
  data.append((member,ref,s,m,inside,T,unit,values,lin,saved,partial,old,raw))
save('checkpoint.json',{'at':datetime.datetime.now(datetime.timezone.utc).isoformat(),'all_four_identities_exact':True,'records':identity,'changed_candidates':0,'ledger':ledger});save('bindings.json',bindings)
records=[]
for member,ref,s,m,inside,T,unit,values,lin,saved,partial,old,raw in data:
 gate();H,W=s.valid.shape;changed=values.copy();primary=neutral_color_response(raw[inside],gain=NEWG,bias=NEWB);linear=T[:,None]*decode_srgb(primary)+4*unit[:,None];encoded=encode_srgb(linear);clipped=int((encoded>1).sum());changed[inside]=np.clip(encoded,0,1);pre=changed.reshape(H,2,W,2,3).mean((1,3)).astype(np.float32);charge('candidate_composites',1);C=s.apply_foreground(pre.copy());charge('metric_gaussians',5);charge('metric_erosions',1);now=score(s,C,m,partial,oldproto['fixed_crops'][member])
 def guards(before):
  g={k:now[k]['rmse']<=before[k]['rmse'] for k in ['glass','rim','held','interior']};g.update(E=now['E']<=before['E'],SSIM=now['ssim']>=before['ssim'],exterior=now['exterior']<=before['exterior'],partial=now['partial']['RMSE']<=before['partial']['RMSE']);g.update({k:v<=before['foreground'][k] for k,v in now['foreground'].items()});return g
 a=guards(old['baseline']);b=guards(old['scores']);row={'member':member,'reference':ref,'scores':now,'canonical_guards':a,'hybrid_guards':b,'clipped_channels':clipped,'all_canonical_pass':all(a.values()),'all_hybrid_pass':all(b.values()),'primary_power_min':float(T.min()),'primary_power_max':float(T.max()),'tail_unassigned':True};records.append(row);prefix=f'{member}-{ref}';np.savez_compressed(OUT/f'{prefix}.npz',pre_foreground=pre,complete=C);save(f'{prefix}-metrics.json',row)
 width=min(W,1080);height=round(H*width/W);im=Image.new('RGB',(2*width+2,height+64),'white');draw=ImageDraw.Draw(im);font=ImageFont.load_default(size=16)
 for i,(v,label) in enumerate([(s.target_crop,'Apple reference'),(C,'One shared normal-white retention; material test')]):im.paste(to_image(v).resize((width,height),Image.Resampling.LANCZOS),(i*(width+2),64));draw.text((i*(width+2)+8,20),label,fill='black',font=font)
 im.save(OUT/f'{prefix}-comparison.png');print('CANDIDATE',member,ref,now['E'],[k for k,v in a.items() if not v],flush=True)
save('result.json',{'status':'FIXED_NORMAL_WHITE_RETENTION_COMPLETE','finished':datetime.datetime.now(datetime.timezone.utc).isoformat(),'records':records,'ledger':ledger,'adopted':False})
