"""One two-variable train direction; actual four-reference backtracks decide."""
from pathlib import Path
import sys,json,datetime,ast,itertools
import numpy as np,cv2
from PIL import Image,ImageDraw,ImageFont
ROOT=Path(__file__).resolve().parents[3];OUT=Path(__file__).resolve().parent
sys.path.insert(0,str(ROOT/'reconstruction'))
from extended_fit import Study
from geometric_render import neutral_color_response
from environment_radiance import decode_srgb,encode_srgb,annular_environment
from music_miniplayer_family import load_working_family as load_family
P=json.loads((OUT/'protocol.json').read_text());END=datetime.datetime.fromisoformat(P['deadline'].replace('Z','+00:00'));F=load_family();cv2.setNumThreads(1)
ledger={k:0 for k in P['caps']}
def save(n,v):(OUT/n).write_text(json.dumps(v,indent=2,allow_nan=False)+'\n')
def gate():assert datetime.datetime.now(datetime.timezone.utc)<END,'Original color deadline'
def charge(k,n):
 gate();d={k:int(n)}
 if k=='score_calls':d.update({'SSIM_Gaussians':5*n,'metric_erosions':n})
 assert all(ledger[key]+v<=P['caps'][key] for key,v in d.items()),d
 for key,v in d.items():ledger[key]+=int(v)
 save('ledger.json',ledger)
helper=ROOT/'research/experiments/miniplayer-outline-light-07/render.py'
tree=ast.parse(helper.read_text());exec(compile(ast.Module(body=[n for n in tree.body if isinstance(n,ast.FunctionDef) and n.name in ['score','display','to_image']],type_ignores=[]),str(helper),'exec'))
assert not (OUT/'started.json').exists(),'One fit only'
save('started.json',{'at':datetime.datetime.now(datetime.timezone.utc).isoformat()})
BASE=ROOT/'research/experiments/miniplayer-incident-material-20';PATHS=ROOT/'research/experiments/miniplayer-inverse-forward-18';data={};p0=np.array([P['parameters']['original_gain'],P['parameters']['original_bias']]);Hess=np.zeros((2,2));gradient=np.zeros(2);loss0=0
oldrows=json.loads((BASE/'result.json').read_text())['records']
def blocks(a,H,W):return a.reshape(H,2,W,2,*a.shape[2:]).transpose(0,2,1,3,*range(4,a.ndim+2)).reshape(H*W,4,*a.shape[2:])
for member in ['expanded','compact']:
 q=np.load(PATHS/f'{member}-paths.npz');inside=q['inside'];power=np.where(inside,q['primary_power'],1.);T=q['primary_power'][inside];charge('environment_direction_queries',int(inside.sum()));unit=q['front_reflection_power'][inside]*annular_environment(q['front_reflection_direction'][inside]);light=np.zeros(inside.shape);light[inside]=4*unit
 work=ROOT/('.evidence-working/expanded-geometry-02' if member=='expanded' else '.evidence-working/compact-geometry-01')
 for k in ['a','b']:
  charge('Study_constructor_pixels',1360*250 if member=='expanded' else 920*240);s=Study(work/k);H,W=s.valid.shape
  masks=np.load(work/f'{k}-masks.npz') if member=='expanded' else np.load(ROOT/f'research/experiments/compact-geometry-01/{k}-masks.npz');assert np.array_equal(s.valid,masks['glass'])
  z=np.load(BASE/f'{member}-{k}-factor0.5.npz');source=np.load(PATHS/f'{member}-{k}-light4.npz');raw=source['raw_source'];values=raw.copy();primary=neutral_color_response(raw[inside],gain=p0[0],bias=p0[1]);values[inside]=np.clip(encode_srgb(T[:,None]*decode_srgb(primary)+4*unit[:,None]),0,1)
  pre=values.reshape(H,2,W,2,3).mean((1,3)).astype(np.float32);charge('identity_composites',1);C=s.apply_foreground(pre.copy());assert np.array_equal(pre,z['pre_foreground'],equal_nan=True) and np.array_equal(C,z['complete'],equal_nan=True)
  ids=s.indices;charge('train_pixels',len(ids));assert s.valid.ravel()[ids].all() and not s.held.ravel()[ids].any()
  S=blocks(raw,H,W)[ids];I=blocks(inside,H,W)[ids];L=blocks(light,H,W)[ids][...,None];TP=blocks(power,H,W)[ids][...,None]
  c=p0[0]*S+p0[1];linear=TP*decode_srgb(c)+L;encoded=encode_srgb(linear)
  prediction=np.where(I[...,None],encoded,S).mean(axis=1)
  Dprime=np.where(c<=.04045,1/12.92,2.4/1.055*((c+.055)/1.055)**1.4)
  Eprime=np.where(linear<=.0031308,12.92,1.055/2.4*np.maximum(linear,1e-30)**(1/2.4-1))
  derivative=TP*Dprime*Eprime*I[...,None];J=np.stack([(derivative*S).mean(1),derivative.mean(1)],-1)
  residual=prediction-s.expected;weight=s.weights**2;weight=weight/(4*3*weight.sum())
  Hess+=np.einsum('ncj,nck,n->jk',J,J,weight);gradient+=np.einsum('ncj,nc,n->j',J,residual,weight);loss0+=float(np.einsum('nc,nc,n->',residual,residual,weight))
  old=dict(next(r for r in oldrows if r['member']==member and r['reference']==k and r['factor']==.5));frozen=np.load(ROOT/f'research/experiments/compact-geometry-01/{k}-raw.npz')['coverage'] if member=='compact' else source['coverage'];partial=masks['glass']&(frozen<1)
  crops=json.loads((PATHS/'protocol.json').read_text())['fixed_crops'][member]
  old['baseline']=next(r['baseline'] for r in json.loads((PATHS/'result.json').read_text())['records'] if r['member']==member and r['reference']==k)
  data[(member,k)]=dict(s=s,H=H,W=W,inside=inside,unit=unit,T=T,raw=raw,coverage=source['coverage'],baseline=C,old=old,partial=partial,masks=masks,crops=crops)
save('checkpoint.json',{'at':datetime.datetime.now(datetime.timezone.utc).isoformat(),'four_identities_exact':True,'train_only':True,'train_pixels':ledger['train_pixels'],'condition':float(np.linalg.cond(Hess))})
charge('fits',1)
A=np.array([[-1,0],[1,0],[0,-1],[0,1],[1,1]],float);B=np.array([-.4,.8,-.15,.5,.98])
white=float(p0.sum());direction=np.array([-1.,1.]);line_H=float(direction@Hess@direction);line_gradient=float(direction@gradient);assert line_H>0
best_bias=float(np.clip(p0[1]-line_gradient/line_H,.15,.5));point=np.array([white-best_bias,best_bias]);delta=point-p0;charge('proposal_checks',1);assert np.all(A@point<=B)
save('proposal.json',dict(gain=float(point[0]),bias=float(point[1]),white_fixed=white,delta=delta.tolist(),line_Hessian=line_H,line_gradient=line_gradient,Hessian=Hess.tolist(),gradient=gradient.tolist(),baseline_train_loss=loss0,predicted_train_change=float(delta@Hess@delta+2*gradient@delta),scope='ONE scalar Gauss-Newton contrast proposal at fixed encoded white; empirical, not radiance/geometry identification.'))
records=[];qualifier=None
for factor in P['factors']:
 if np.array_equal(delta,np.zeros(2)):break
 bb=p0[1]+factor*delta[1];point=np.array([white-bb,bb]);charge('proposal_checks',1);assert np.all(A@point<=B)
 factor_rows=[]
 for (member,k),d in data.items():
  raw=d['raw'];inside=d['inside'];primary,preclip=neutral_color_response(raw[inside],gain=point[0],bias=point[1],return_preclip=True);encoded=encode_srgb(d['T'][:,None]*decode_srgb(primary)+4*d['unit'][:,None]);clipping=[int((preclip<0).sum()),int((preclip>1).sum()),int((encoded>1).sum())]
  values=raw.copy();values[inside]=np.clip(encoded,0,1);pre=values.reshape(d['H'],2,d['W'],2,3).mean((1,3)).astype(np.float32);charge('candidate_composites',1);C=d['s'].apply_foreground(pre.copy());now=score(d['s'],C,d['masks'],d['partial'],d['crops'])
  def guards(before):
   g={n:now[n]['rmse']<=before[n]['rmse'] for n in ['glass','rim','held','interior']};g.update(E=now['E']<=before['E'],SSIM=now['ssim']>=before['ssim'],exterior=now['exterior']<=before['exterior'],partial=now['partial']['RMSE']<=before['partial']['RMSE']);g.update({n:v<=before['foreground'][n] for n,v in now['foreground'].items()});return g
  held=guards(d['old']['scores']);selected=guards(d['old']['baseline']);prefix=f'{member}-{k}-factor{factor}'
  np.savez_compressed(OUT/f'{prefix}.npz',pre_foreground=pre,complete=C,coverage=d['coverage'])
  w=min(1080,d['W']);h=round(d['H']*w/d['W']);canvas=Image.new('RGB',(2*w+2,h+64),'white');draw=ImageDraw.Draw(canvas);font=ImageFont.load_default(size=16)
  for i,(v,title) in enumerate([(d['s'].target_crop,'Apple reference'),(C,f'Explicit interface power; shared white-fixed contrast step {factor}')]):canvas.paste(to_image(v).resize((w,h),Image.Resampling.LANCZOS),(i*(w+2),64));draw.text((i*(w+2)+8,20),title,font=font,fill='black')
  canvas.save(OUT/f'{prefix}-comparison.png');row=dict(member=member,reference=k,factor=factor,gain=float(point[0]),bias=float(point[1]),scores=now,held_guards=held,selected_guards=selected,clipping=clipping,all_pass=all(held.values()) and not any(clipping),original_numerical_all_pass=all(selected.values()));factor_rows.append(row);records.append(row);save(prefix+'-metrics.json',row);print(json.dumps(dict(member=member,reference=k,factor=factor,E=now['E'],all_pass=row['all_pass'])),flush=True);gate()
 if all(r['all_pass'] for r in factor_rows):qualifier=factor;break
save('result.json',dict(status='SHARED_NEUTRAL_DIRECTION_COMPLETE',finished=datetime.datetime.now(datetime.timezone.utc).isoformat(),records=records,qualifier=qualifier,ledger=ledger,adopted=False,full_radiance=False,selected_model_changed=False))
