"""Two cached-coordinate observations; unchanged source/AA/foreground chain."""
import datetime,json
from pathlib import Path
import cv2,numpy as np
from PIL import Image,ImageDraw,ImageFont
from extended_fit import Study
from geometric_render import incident_source_filter,neutral_color_response
ROOT=Path(__file__).resolve().parents[3];OUT=Path(__file__).parent;BASE=ROOT/'research/experiments/expanded-geometry-02';WORK=ROOT/'.evidence-working/expanded-geometry-02'
p=json.loads((OUT/'protocol.json').read_text());deadline=datetime.datetime.fromisoformat(p['deadline'])
assert not (OUT/'result.json').exists() and json.loads((OUT/'source-preflight.json').read_text())['status']=='PASS'
q=np.load(OUT/'native-paths.npz');rows=[];queries=0;cv2.setNumThreads(1)
def sample(source,X,Y):
 a=np.floor(X).astype(int);b=np.floor(Y).astype(int);fx=(X-a)[:,None];fy=(Y-b)[:,None]
 return (source[b,a]*(1-fx)+source[b,a+1]*fx)*(1-fy)+(source[b+1,a]*(1-fx)+source[b+1,a+1]*fx)*fy
for k in ['a','b']:
 assert datetime.datetime.now(datetime.timezone.utc)<deadline
 s=Study(WORK/k);m=np.load(WORK/f'{k}-masks.npz');support=np.load(OUT/f'{k}-support.npz')['support'];known=cv2.imread(str(WORK/k/'known.png'),0)>0
 filtered,_,radius=incident_source_filter(s.source,known,6.75);assert radius==21
 inside=q['inside'];before=np.full(inside.shape+(3,),np.nan)
 for flag,source in [(inside,filtered),(~inside,s.source)]:
  ii,jj=np.nonzero(flag&support);before[ii,jj]=sample(source,q['X'][ii,jj],q['Y'][ii,jj]);queries+=len(ii)
 assert queries<=p['budgets']['source_RGB_queries']
 fixed,unclipped=neutral_color_response(before,gain=.701980827595718,bias=.22423217000784113,return_preclip=True);fixed=np.where(inside[...,None],fixed,before)
 H,W=s.valid.shape;pre=fixed.reshape(H,2,W,2,3).mean((1,3)).astype(np.float32);C=s.apply_foreground(pre.copy());assert np.isfinite(C[m['glass']|m['exterior']]).all()
 score=s.scores(C);score['E']=float(np.sqrt(score['loss']));err=(C-s.target_crop)*255;score['exterior_RMSE']=float(np.sqrt(np.mean(err[m['exterior']]**2)));score['foreground_artwork_MSE']={}
 x0,y0,_,_=s.crop
 for l in s.case['foreground_layers']:
  a,b,c,d=l['box'];e=err[b-y0:d-y0,a-x0:c-x0];assert np.isfinite(e).all();name=l.get('style_key',l.get('vector_asset',l.get('artwork_asset')));score['foreground_artwork_MSE'][name]=float(np.mean(e*e))
 old=next(r['scores'] for r in json.loads((BASE/'result.json').read_text())['records'] if r['reference']==k and r['hypothesis']=='h1')
 guards={name:score[name]['rmse']<=old[name]['rmse'] for name in ['glass','rim','held','interior']};guards.update({name:score[name]<=old[name] for name in ['E','exterior_RMSE']});guards['ssim']=score['ssim']>=old['ssim'];guards.update({name:score['foreground_artwork_MSE'][name]<=v for name,v in old['foreground_artwork_MSE'].items()})
 coverage=inside.reshape(H,2,W,2).mean((1,3));np.testing.assert_array_equal(coverage,np.load(BASE/f'h1-{k}.npz')['coverage'])
 np.savez_compressed(OUT/f'{k}-candidate.npz',sample_before_response=before,pre_foreground=pre,complete=C,coverage=coverage)
 valid=np.isfinite(C).all(2);yy,xx=np.indices(valid.shape);view=np.where(valid[...,None],C,np.where(((xx//6+yy//6)%2)[...,None],.72,.9));target=Image.fromarray(np.uint8(np.rint(s.target_crop*255)));image=Image.fromarray(np.uint8(np.rint(np.clip(view,0,1)*255)));w=1080;hh=round(H*w/W)
 canvas=Image.new('RGB',(2*w+2,hh+64),'white');draw=ImageDraw.Draw(canvas);font=ImageFont.load_default(size=18);canvas.paste(target.resize((w,hh),Image.Resampling.LANCZOS),(0,64));canvas.paste(image.resize((w,hh),Image.Resampling.LANCZOS),(w+2,64));draw.text((12,20),'Apple reference',font=font,fill='black');draw.text((w+14,20),'One positive spline back; source blur6.75',font=font,fill='black');canvas.save(OUT/f'{k}-comparison.png')
 row=dict(reference=k,scores=score,guards=guards,status='PASS' if all(guards.values()) else 'REJECTED',coverage_exact=True,clipped_lens_channels=int(((unclipped[inside]<0)|(unclipped[inside]>1)).sum()));rows.append(row);print(json.dumps(row),flush=True)
result=dict(status='STRICT_PAIRED_QUALIFIER' if all(r['status']=='PASS' for r in rows) else 'NO_STRICT_PAIRED_QUALIFIER',records=rows,source_RGB_queries=queries,new_rays_in_RGB_phase=0,full_native_observations=2,fits=0,finished_at=datetime.datetime.now(datetime.timezone.utc).isoformat())
(OUT/'result.json').write_text(json.dumps(result,indent=2)+'\n')
