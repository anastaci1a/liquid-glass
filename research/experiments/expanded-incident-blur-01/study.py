"""Two fixed incident widths on frozen selected geometry; no new tracing."""
from pathlib import Path
import datetime,json
import cv2,numpy as np
from PIL import Image,ImageDraw,ImageFont
from extended_fit import Study
from geometric_render import incident_source_filter,neutral_color_response
ROOT=Path(__file__).resolve().parents[3];OUT=Path(__file__).parent;BASE=ROOT/'research/experiments/expanded-geometry-02';WORK=ROOT/'.evidence-working/expanded-geometry-02';p=json.loads((OUT/'protocol.json').read_text());deadline=datetime.datetime.fromisoformat(p['deadline']);cv2.setNumThreads(1)
assert not (OUT/'result.json').exists()
def gate():assert datetime.datetime.now(datetime.timezone.utc)<deadline
proof=[]
# No RGB filtering/sampling until both sources have their support disposition.
for k in ['a','b']:
 gate();q=np.load(WORK/f'h1-{k}-paths.npz');old=np.load(BASE/f'h1-{k}-support.npz');known=cv2.imread(str(WORK/k/'known.png'),0)>0;safe=cv2.erode(known.astype(np.uint8),np.ones((55,55),np.uint8),borderType=cv2.BORDER_CONSTANT,borderValue=0)>0
 i,j=np.nonzero(q['inside']);a=np.floor(q['X'][i,j]).astype(int);b=np.floor(q['Y'][i,j]).astype(int);good=safe[b,a]&safe[b+1,a]&safe[b,a+1]&safe[b+1,a+1];support=old['support'].copy();support[i,j]=good;required=old['required'];np.savez_compressed(OUT/f'{k}-support.npz',maximum_radius_support=support,required=required)
 proof.append(dict(reference=k,emitted_subrays=q['X'].size,whole=int(q['inside'].sum()),unsupported_radius27_required=int((required&~support).sum()),smaller_radius14_supported_by_prior_radius21=True,RGB_queries=0))
assert sum(r['emitted_subrays'] for r in proof)<=p['budgets']['source_support_subrays']
(OUT/'source-preflight.json').write_text(json.dumps(dict(records=proof,new_rays=0,RGB_queries=0,known_limit='Existing source confidence only; no hidden photographic truth.'),indent=2)+'\n')
rows=[];zeros=[];queries=0;arrays={}
def scores(s,C,m):
 z=s.scores(C);z['E']=float(np.sqrt(z['loss']));e=(C-s.target_crop)*255;z['exterior_RMSE']=float(np.sqrt(np.mean(e[m['exterior']]**2)));z['foreground_artwork_MSE']={};x0,y0,_,_=s.crop
 for l in s.case['foreground_layers']:
  a,b,c,d=l['box'];name=l.get('style_key',l.get('vector_asset',l.get('artwork_asset')));z['foreground_artwork_MSE'][name]=float(np.mean(e[b-y0:d-y0,a-x0:c-x0]**2))
 return z
def guards(new,old):
 g={n:new[n]['rmse']<=old[n]['rmse'] for n in ['glass','rim','held','interior']};g.update({n:new[n]<=old[n] for n in ['E','exterior_RMSE']});g['ssim']=new['ssim']>=old['ssim'];g.update({n:new['foreground_artwork_MSE'][n]<=v for n,v in old['foreground_artwork_MSE'].items()});return g
for k in ['a','b']:
 gate();s=Study(WORK/k);q=np.load(WORK/f'h1-{k}-paths.npz');base=np.load(BASE/f'h1-{k}.npz');m=np.load(WORK/f'{k}-masks.npz');inside=q['inside'];H,W=s.valid.shape
 response=neutral_color_response(base['sample_before_response'],gain=p['frozen']['gain'],bias=p['frozen']['bias']);response=np.where(inside[...,None],response,base['sample_before_response']);pre=response.reshape(H,2,W,2,3).mean((1,3)).astype(np.float32);np.testing.assert_array_equal(pre,base['pre_foreground']);np.testing.assert_array_equal(s.apply_foreground(pre.copy()),base['complete']);zeros.append(dict(reference=k,pixel_exact=True,RGB_queries=0,new_rays=0))
 old=scores(s,base['complete'],m);arrays[k]={'baseline':base['complete'].copy(),'Apple':s.target_crop.copy()};known=cv2.imread(str(WORK/k/'known.png'),0)>0
 for sigma in p['fixed_widths_native_pixels']:
  gate();radius=int(np.ceil(3*sigma));supported=radius<=21 or next(r for r in proof if r['reference']==k)['unsupported_radius27_required']==0
  if not supported:rows.append(dict(reference=k,sigma=sigma,status='STOP_UNSUPPORTED_REQUIRED_NO_RGB'));continue
  filtered,_,r=incident_source_filter(s.source,known,sigma);assert r==radius;sample=base['sample_before_response'].copy();ii,jj=np.nonzero(inside);X=q['X'][ii,jj];Y=q['Y'][ii,jj];a=np.floor(X).astype(int);b=np.floor(Y).astype(int);fx=(X-a)[:,None];fy=(Y-b)[:,None]
  sample[ii,jj]=(filtered[b,a]*(1-fx)+filtered[b,a+1]*fx)*(1-fy)+(filtered[b+1,a]*(1-fx)+filtered[b+1,a+1]*fx)*fy;queries+=len(ii);assert queries<=p['budgets']['source_RGB_queries']
  response=neutral_color_response(sample,gain=p['frozen']['gain'],bias=p['frozen']['bias']);response=np.where(inside[...,None],response,sample);pre=response.reshape(H,2,W,2,3).mean((1,3)).astype(np.float32);C=s.apply_foreground(pre.copy());assert np.isfinite(C[s.valid|m['exterior']]).all();z=scores(s,C,m);g=guards(z,old);key=str(sigma);arrays[k][key]=C.copy();np.savez_compressed(OUT/f'{k}-sigma{key}.npz',sample_before_response=sample,pre_foreground=pre,complete=C)
  valid=np.isfinite(C).all(2);yy,xx=np.indices(valid.shape);show=np.where(valid[...,None],C,np.where(((xx//6+yy//6)%2)[...,None],.72,.9));aimg=Image.fromarray(np.uint8(np.rint(s.target_crop*255)));bimg=Image.fromarray(np.uint8(np.rint(np.clip(show,0,1)*255)));w=1080;hh=round(H*w/W);canvas=Image.new('RGB',(2*w+2,hh+64),'white');draw=ImageDraw.Draw(canvas);font=ImageFont.load_default(size=18);canvas.paste(aimg.resize((w,hh),Image.Resampling.LANCZOS),(0,64));canvas.paste(bimg.resize((w,hh),Image.Resampling.LANCZOS),(w+2,64));draw.text((12,20),'Apple reference',font=font,fill='black');draw.text((w+14,20),f'Incident width {sigma} native pixels',font=font,fill='black');canvas.save(OUT/f'{k}-sigma{key}-comparison.png')
  row=dict(reference=k,sigma=sigma,status='PASS' if all(g.values()) else 'REJECTED',scores=z,guards=g);rows.append(row);print(json.dumps(row),flush=True)
# The fixed historical text diagnostic is separate from rendering/scoring.
s=Study(WORK/'b');m=np.load(WORK/'b-masks.npz')['glass'];safe=cv2.erode(m.astype(np.uint8),np.ones((75,75),np.uint8))>0;mask=np.zeros_like(m);mask[326-s.crop[1]:505-s.crop[1],875-s.crop[0]:1258-s.crop[0]]=True;mask&=safe;details={}
for name,C in arrays['b'].items():
 luma=np.nan_to_num(C)@np.array([.2126,.7152,.0722]);g1=cv2.GaussianBlur(luma,(7,7),1);g3=cv2.GaussianBlur(luma,(19,19),3);g12=cv2.GaussianBlur(luma,(73,73),12);high=float(np.sqrt(np.mean((g1-g3)[mask]**2)));low=float(np.sqrt(np.mean((g3-g12)[mask]**2)));details[name]=dict(high_band_RMS=high,low_band_RMS=low,ratio=high/low)
(OUT/'detail-review.json').write_text(json.dumps(dict(safe_pixels=int(mask.sum()),crop=[875,326,1258,505],values=details,limits='Advisory detail measure; source PSF, geometry, camera and illumination remain confounds. No optical output blur was added.'),indent=2)+'\n')
(OUT/'result.json').write_text(json.dumps(dict(records=rows,zero_controls=zeros,source_RGB_queries=queries,new_rays=0,fits=0,finished_at=datetime.datetime.now(datetime.timezone.utc).isoformat()),indent=2)+'\n')
