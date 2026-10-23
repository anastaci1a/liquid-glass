"""Compare saved pure-geometric paths with matched incident softness."""
import ast,datetime,json
from pathlib import Path
import cv2,numpy as np
from PIL import Image,ImageDraw,ImageFont
from extended_fit import Study
from geometric_render import incident_source_filter,neutral_color_response
ROOT=Path(__file__).resolve().parents[3];OUT=Path(__file__).parent;WORK=ROOT/'.evidence-working/expanded-geometry-02'
p=json.loads((OUT/'protocol.json').read_text());deadline=datetime.datetime.fromisoformat(p['refraction_deadline'])
assert not (OUT/'result.json').exists()
assert json.loads((OUT/'source-preflight.json').read_text())['status']=='PASS'
cv2.setNumThreads(1)
def function(path,name):
 t=ast.parse(path.read_text());return next(ast.dump(x,include_attributes=False) for x in ast.walk(t) if isinstance(x,ast.FunctionDef) and x.name==name)
assert function(ROOT/'reconstruction/extended_fit.py','apply_foreground')==function(ROOT/'research/captures/dark-glass-lab/extended/agent-pipeline-01/code/extended_fit.py','apply_foreground')
def sample(source,X,Y):
 a=np.floor(X).astype(int);b=np.floor(Y).astype(int);fx=(X-a)[...,None];fy=(Y-b)[...,None]
 return (source[b,a]*(1-fx)+source[b,a+1]*fx)*(1-fy)+(source[b+1,a]*(1-fx)+source[b+1,a+1]*fx)*fy
rows=[];zeros=[];queries=0
for k in ['a','b']:
 assert datetime.datetime.now(datetime.timezone.utc)<deadline
 s=Study(WORK/k);m=np.load(WORK/f'{k}-masks.npz');known=cv2.imread(str(WORK/k/'known.png'),0)>0
 q1=np.load(WORK/f'h1-{k}-paths.npz');H,W=m['glass'].shape
 cov=q1['inside'].reshape(H,2,W,2).mean((1,3));ids=np.flatnonzero(cov==1);ids=ids[np.linspace(0,len(ids)-1,96,dtype=int)];rr,cc=np.unravel_index(ids,cov.shape)
 r=(2*rr[:,None,None]+np.arange(2)[None,:,None])+np.zeros((1,1,2),int);c=2*cc[:,None,None]+np.arange(2)[None,None,:]+np.zeros((1,2,1),int)
 zero=sample(s.source,q1['X'][r,c],q1['Y'][r,c]).mean((1,2)).astype(np.float32);queries+=r.size
 old=np.load(WORK/f'{k}-raw-material.npy');np.testing.assert_array_equal(zero,old[rr,cc]);zeros.append(dict(reference=k,native_pixels=96,RGB_queries=r.size,raw_float32_exact=True,foreground_AST_exact=True))
 filtered,_,radius=incident_source_filter(s.source,known,6.75);assert radius==21
 for h in ['h1','h2']:
  assert datetime.datetime.now(datetime.timezone.utc)<deadline
  q=np.load(WORK/f'{h}-{k}-paths.npz');support=np.load(OUT/f'{h}-{k}-support.npz')['support'];inside=q['inside'];np.testing.assert_array_equal(inside,q1['inside'])
  before=np.full(inside.shape+(3,),np.nan)
  for flag,source in [(inside,filtered),(~inside,s.source)]:
   ii,jj=np.nonzero(flag&support);before[ii,jj]=sample(source,q['X'][ii,jj],q['Y'][ii,jj]);queries+=len(ii)
  assert queries<=p['cached_RGB_phase']['maximum_RGB_queries_including_sparse_controls']
  graded,unclipped=neutral_color_response(before,gain=p['nuisance']['gain'],bias=p['nuisance']['bias'],return_preclip=True)
  fixed=np.where(inside[...,None],graded,before);pre=fixed.reshape(H,2,W,2,3).mean((1,3)).astype(np.float32);C=s.apply_foreground(pre.copy())
  assert np.isfinite(C[m['glass']|m['exterior']]).all()
  scores=s.scores(C);scores['E']=float(np.sqrt(scores['loss']));error=(C-s.target_crop)*255
  scores['exterior_RMSE']=float(np.sqrt(np.mean(error[m['exterior']]**2)));scores['foreground_artwork_MSE']={}
  x0,y0,_,_=s.crop
  for layer in s.case['foreground_layers']:
   a,b,c,d=layer['box'];e=error[b-y0:d-y0,a-x0:c-x0];assert np.isfinite(e).all();name=layer.get('style_key',layer.get('vector_asset',layer.get('artwork_asset')));scores['foreground_artwork_MSE'][name]=float(np.mean(e*e))
  np.savez_compressed(OUT/f'{h}-{k}.npz',sample_before_response=before,pre_foreground=pre,complete=C,coverage=cov)
  valid=np.isfinite(C).all(2);yy,xx=np.indices(valid.shape);display=np.where(valid[...,None],C,np.where(((xx//6+yy//6)%2)[...,None],.72,.9));target=Image.fromarray(np.uint8(np.rint(s.target_crop*255)))
  image=Image.fromarray(np.uint8(np.rint(np.clip(display,0,1)*255)));w=1080;hh=round(H*w/W);canvas=Image.new('RGB',(2*w+2,hh+64),'white');draw=ImageDraw.Draw(canvas);font=ImageFont.load_default(size=18)
  canvas.paste(target.resize((w,hh),Image.Resampling.LANCZOS),(0,64));canvas.paste(image.resize((w,hh),Image.Resampling.LANCZOS),(w+2,64));draw.text((12,20),'Apple reference',font=font,fill='black');draw.text((w+14,20),f'{h}: incident blur 6.75 px; fixed response',font=font,fill='black');canvas.save(OUT/f'{h}-{k}-comparison.png')
  row=dict(hypothesis=h,reference=k,scores=scores,unavailable_unscored_pixels=int((~valid).sum()),clipped_lens_channels=int(((unclipped[inside]<0)|(unclipped[inside]>1)).sum()));rows.append(row);print(json.dumps(row),flush=True)
result=dict(status='FIXED_MATCHED_NUISANCE_COMPARISON',records=rows,RGB_queries=queries,new_geometry_rays=0,fits=0,full_composites=4,zero_controls=zeros,finished_at=datetime.datetime.now(datetime.timezone.utc).isoformat())
(OUT/'result.json').write_text(json.dumps(result,indent=2)+'\n')
