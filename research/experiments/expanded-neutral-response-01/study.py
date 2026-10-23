"""One common neutral response; source samples and geometry remain frozen."""
from pathlib import Path
import datetime,json
import cv2,numpy as np
from PIL import Image,ImageDraw,ImageFont
from extended_fit import Study
from geometric_render import neutral_color_response
ROOT=Path(__file__).resolve().parents[3];OUT=Path(__file__).parent;BASE=ROOT/'research/experiments/expanded-geometry-02';WORK=ROOT/'.evidence-working/expanded-geometry-02';p=json.loads((OUT/'protocol.json').read_text());deadline=datetime.datetime.fromisoformat(p['deadline']);assert not (OUT/'result.json').exists();assert all(z['pixel_exact'] for z in json.loads((ROOT/'research/experiments/expanded-incident-blur-01/result.json').read_text())['zero_controls'])
g0=p['parameters']['original_gain'];b0=p['parameters']['original_bias'];numerator=0.;denominator=0.;contexts={};training=[]
for k in ['a','b']:
 s=Study(WORK/k);q=np.load(WORK/f'h1-{k}-paths.npz');z=np.load(BASE/f'h1-{k}.npz');m=np.load(WORK/f'{k}-masks.npz');samples=z['sample_before_response'];inside=q['inside'];H,W=s.valid.shape;alpha=inside.reshape(H,2,W,2).mean((1,3));lens=np.where(inside[...,None],samples,0).reshape(H,2,W,2,3).mean((1,3));direction=alpha[...,None]-lens;train=s.valid&~s.held;rim=train&s.rim
 # Glass excludes every foreground box; no assumption of linear foreground blending.
 x0,y0,_,_=s.crop
 for layer in s.case['foreground_layers']:
  a,b,c,d=layer['box'];assert not train[b-y0:d-y0,a-x0:c-x0].any()
 weight=np.where(train,.7/train.sum(),0)+np.where(rim,.3/rim.sum(),0);e=z['pre_foreground'].astype(float)-s.target_crop;D=direction[train];E=e[train];weights=weight[train,None];numerator+=float(np.sum(weights*D*E));denominator+=float(np.sum(weights*D*D));contexts[k]=(s,inside,samples,m,z['complete'].copy());training.append(dict(reference=k,train_pixels=int(train.sum()),rim_train_pixels=int(rim.sum())))
raw=-numerator/denominator;delta=float(np.clip(raw,*p['parameters']['delta_bounds']));proposal=dict(raw_delta=raw,bounded_delta=delta,training=training,gain_at_full=g0-delta,bias_at_full=b0+delta,white_point=g0+b0,fits=1);(OUT/'proposal.json').write_text(json.dumps(proposal,indent=2)+'\n')
def score(s,C,m):
 a=s.scores(C);a['E']=float(np.sqrt(a['loss']));e=(C-s.target_crop)*255;a['exterior_RMSE']=float(np.sqrt(np.mean(e[m['exterior']]**2)));a['foreground_artwork_MSE']={};x0,y0,_,_=s.crop
 for layer in s.case['foreground_layers']:
  x,y,x1,y1=layer['box'];key=layer.get('style_key',layer.get('vector_asset',layer.get('artwork_asset')));a['foreground_artwork_MSE'][key]=float(np.mean(e[y-y0:y1-y0,x-x0:x1-x0]**2))
 return a
def good(new,old):
 g={name:new[name]['rmse']<=old[name]['rmse'] for name in ['glass','rim','held','interior']};g.update({name:new[name]<=old[name] for name in ['E','exterior_RMSE']});g['ssim']=new['ssim']>=old['ssim'];g.update({name:new['foreground_artwork_MSE'][name]<=v for name,v in old['foreground_artwork_MSE'].items()});return g
old={k:score(s,C,m) for k,(s,inside,samples,m,C) in contexts.items()};ledger=[];selected=None
for trial,factor in enumerate([1.,.5,.25,.125] if delta>0 else []):
 assert datetime.datetime.now(datetime.timezone.utc)<deadline
 change=delta*factor;gain=g0-change;bias=b0+change;np.testing.assert_array_equal(neutral_color_response(np.array([0.,.5,1.]),g0,b0)[-1].astype(np.float32),neutral_color_response(np.array([0.,.5,1.]),gain,bias)[-1].astype(np.float32));rows=[]
 for k,(s,inside,samples,m,C0) in contexts.items():
  H,W=s.valid.shape;value,unclipped=neutral_color_response(samples,gain,bias,return_preclip=True);value=np.where(inside[...,None],value,samples);pre=value.reshape(H,2,W,2,3).mean((1,3)).astype(np.float32);C=s.apply_foreground(pre.copy());a=score(s,C,m);g=good(a,old[k]);np.savez_compressed(OUT/f'trial{trial}-{k}.npz',pre_foreground=pre,complete=C)
  row=dict(reference=k,scores=a,guards=g,clipped_lens_channels=int(((unclipped[inside]<0)|(unclipped[inside]>1)).sum()),preclip_range=[float(np.min(unclipped[inside])),float(np.max(unclipped[inside]))]);rows.append(row);print(json.dumps(dict(trial=trial,factor=factor,**row)),flush=True)
 rec=dict(trial=trial,factor=factor,delta=change,gain=gain,bias=bias,status='PASS' if all(all(r['guards'].values()) for r in rows) else 'REJECTED',records=rows);ledger.append(rec)
 if rec['status']=='PASS':selected=rec;break
(OUT/'result.json').write_text(json.dumps(dict(status='STRICT_PAIRED_COMPONENT_QUALIFIER' if selected else 'NO_STRICT_QUALIFIER',selected=selected,ledger=ledger,new_rays=0,new_source_RGB_queries=0,uniform_white_fixture_float32_exact=True,finished_at=datetime.datetime.now(datetime.timezone.utc).isoformat()),indent=2)+'\n')
if selected:
 for k,(s,inside,samples,m,C0) in contexts.items():
  C=np.load(OUT/f"trial{selected['trial']}-{k}.npz")['complete'];H,W=s.valid.shape;valid=np.isfinite(C).all(2);yy,xx=np.indices(valid.shape);view=np.where(valid[...,None],C,np.where(((xx//6+yy//6)%2)[...,None],.72,.9));a=Image.fromarray(np.uint8(np.rint(s.target_crop*255)));b=Image.fromarray(np.uint8(np.rint(np.clip(view,0,1)*255)));w=1080;h=round(H*w/W);canvas=Image.new('RGB',(2162,h+64),'white');draw=ImageDraw.Draw(canvas);font=ImageFont.load_default(size=18);canvas.paste(a.resize((w,h),Image.Resampling.LANCZOS),(0,64));canvas.paste(b.resize((w,h),Image.Resampling.LANCZOS),(1082,64));draw.text((12,20),'Apple reference',font=font,fill='black');draw.text((1094,20),'Same geometry/blur; common neutral response',font=font,fill='black');canvas.save(OUT/f'{k}-candidate-comparison.png')
