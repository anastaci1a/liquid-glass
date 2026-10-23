"""Raw geometric observation with exact subray/pre-foreground retention."""
import argparse,datetime,hashlib,json,time
from pathlib import Path
import cv2,numpy as np
from PIL import Image,ImageDraw,ImageFont
from extended_fit import Study
from geometric_optics import trace_flat_front_orthographic
from geometric_render import render_rows
from rounded_rectangle_back import RoundedRectangleHarmonicBack
ROOT=Path(__file__).resolve().parents[3];OUT=Path(__file__).parent
WORK=ROOT/'.evidence-working/compact-geometry-01'
P=json.loads((ROOT/'reconstruction/studies/music-mini-compact-vector/review-round/pass-03.json').read_text())['parameters']
protocol=json.loads((OUT/'protocol.json').read_text());deadline=datetime.datetime.fromisoformat(protocol['stages'][0]['deadline']).timestamp()
cv2.setNumThreads(1)
def gate():
 if time.time()>deadline:raise RuntimeError('Refraction deadline reached')
def save(name,value):(OUT/name).write_text(json.dumps(value,indent=2)+'\n')
def setup(k):
 s=Study(WORK/k);c=dict(s.case)
 c['center']=(np.asarray(c['center'])+s.L*np.array([P['shape_dx'],P['shape_dy']])).tolist()
 half=tuple(s.half+[P['half_x_delta'],P['half_y_delta']]);radius=min(s.radius+P['radius_delta'],*half)
 surface=RoundedRectangleHarmonicBack(half,radius,cap_join_width=P['cap_join_width'])
 known=cv2.imread(str(WORK/k/'known.png'),0)>0;x0,y0,x1,y1=s.crop
 reference=s.case['exterior_reference_shape'];sd=s.shape(s.x,s.y,reference)[-1][0]
 ext=(sd>1.5/s.L)&(sd<.2)&known[y0:y1,x0:x1]
 X=s.x*s.L+s.case['center'][0];Y=s.y*s.L+s.case['center'][1]
 for a,b,c0,d in s.case.get('exterior_exclusions',[]):ext&=~((X>=a)&(X<=c0)&(Y>=b)&(Y<=d))
 required=s.valid|ext
 for layer in s.case['foreground_layers']:
  a,b,c0,d=layer['box'];required[b-y0:d-y0,a-x0:c0-x0]=True
 return s,c,surface,known,ext,required
def metrics(s,M,C,ext):
 legacy=s.scores(M);legacy['E']=float(np.sqrt(legacy['loss']))
 completed=s.scores(C);completed['E']=float(np.sqrt(completed['loss']))
 x0,y0,_,_=s.crop;fg={}
 for layer in s.case['foreground_layers']:
  a,b,c,d=layer['box'];name=layer.get('style_key',layer.get('vector_asset',layer.get('artwork_asset')))
  fg[name]=float(np.mean(((C[b-y0:d-y0,a-x0:c-x0].astype(float)-s.target[b:d,a:c])*255)**2))
 return {'legacy_material':legacy,'completed_image':completed,'foreground_artwork_MSE':fg,'exterior':{'pixels':int(ext.sum()),'rmse':float(np.sqrt(np.mean((C[ext]-s.target_crop[ext])**2))*255)}}
def preview(s,C,name,label):
 H,W=C.shape[:2];canvas=Image.new('RGB',(2*W+2,H+64),'white');draw=ImageDraw.Draw(canvas);font=ImageFont.load_default(size=18)
 for i,(im,title) in enumerate([(s.target_crop,'Apple reference'),(C,label)]):
  valid=np.isfinite(im).all(2);yy,xx=np.indices(valid.shape);checker=np.where(((yy//6+xx//6)%2)[...,None],.72,.9)
  image=np.where(valid[...,None],im,checker)
  canvas.paste(Image.fromarray(np.uint8(np.rint(np.clip(image,0,1)*255))),(i*(W+2),64));draw.text((i*(W+2)+12,20),title,font=font,fill='black')
 canvas.save(OUT/name)
def preflight():
 if (OUT/'source-preflight.json').exists():raise RuntimeError('Completed preflight cannot repeat')
 assert json.loads((OUT/'geometry-check.json').read_text())['status']=='PASS'
 rows=[];total=0
 for k in ['a','b']:
  gate();s,c,surface,known,ext,required=setup(k);x0,y0,x1,y1=s.crop;H,W=required.shape
  rec={'reference':k,'rays':0,'whole':0,'required':0,'scored_outside_physical_outline_subrays':0,'unsupported_required':0,'unknown_unscored':0,'incomplete':0,'rgb_samples':0}
  for top in range(0,H,12):
   gate();bot=min(top+12,H);yy,xx=np.mgrid[y0+top:y0+bot:.5,x0:x1:.5]
   q=trace_flat_front_orthographic(surface,(xx-.25-c['center'][0])/s.L,(yy-.25-c['center'][1])/s.L,1.5,2.)
   total+=q['X'].size;rec['rays']+=q['X'].size;assert total<=1766400
   rec['incomplete']+=int((~q['complete']).sum())
   if rec['incomplete']:save('preflight-failure.json',rec);raise RuntimeError('Incomplete primary path')
   u=q['X']*s.L+c['center'][0];v=q['Y']*s.L+c['center'][1]
   a=np.floor(u).astype(int);b=np.floor(v).astype(int);safe=(a>=0)&(b>=0)&(a+1<known.shape[1])&(b+1<known.shape[0])
   i,j=np.nonzero(safe);safe[i,j]&=known[b[i,j],a[i,j]]&known[b[i,j]+1,a[i,j]]&known[b[i,j],a[i,j]+1]&known[b[i,j]+1,a[i,j]+1]
   needed=q['inside']|np.repeat(np.repeat(required[top:bot],2,0),2,1)
   scored=np.repeat(np.repeat(s.valid[top:bot],2,0),2,1)
   rec['whole']+=int(q['inside'].sum());rec['required']+=int(needed.sum());rec['scored_outside_physical_outline_subrays']+=int((scored&~q['inside']).sum())
   rec['unsupported_required']+=int((needed&~safe).sum());rec['unknown_unscored']+=int((~safe&~needed).sum())
   if rec['unsupported_required']:save('preflight-failure.json',rec);raise RuntimeError('Unsupported original required source footprint')
  rec['input_hashes']={n:hashlib.sha256((WORK/k/n).read_bytes()).hexdigest() for n in ['case.json',*s.case['source_sha256']]}
  np.savez_compressed(OUT/f'{k}-masks.npz',glass=s.valid,rim=s.rim,held=s.held,exterior=ext,required=required)
  rows.append(rec);print(json.dumps(rec),flush=True)
 save('source-preflight.json',{'status':'PASS','references':rows,'rays':total,'bilinear_texels':4,'finite_source_kernel_radius':0,'masks':'Original target masks and separate exterior_reference_shape; no dropped outside-outline samples.','confidence':'Recorded temporal-mosaic known mask, not hidden-scene truth.'})
def render():
 proof=json.loads((OUT/'source-preflight.json').read_text());assert proof['status']=='PASS'
 if (OUT/'raw-result.json').exists():raise RuntimeError('Completed native proposal cannot repeat')
 rows=[];total=0
 for k,rec in zip(['a','b'],proof['references']):
  gate();s,c,surface,known,ext,required=setup(k)
  for n,digest in rec['input_hashes'].items():assert hashlib.sha256((WORK/k/n).read_bytes()).hexdigest()==digest
  H,W=required.shape;M=np.zeros((H,W,3));C=np.zeros((H,W,3),np.float32);alpha=np.zeros((H,W));clear=np.zeros_like(M)
  samples={n:[] for n in ['sample_rgb','sample_inside','source_X','source_Y']}
  for top in range(0,H,12):
   gate();bot=min(top+12,H)
   image,_,layers=render_rows(s.source,c,{},surface,1.5,2.,top,bot,raw_transmission=True,exact_bilinear=True,samples_per_axis=2,source_known=known,required_pixels=required,return_layers=True,return_samples=True)
   total+=(bot-top)*W*4;assert total<=1766400
   M[top:bot]=layers['lens_color'];C[top:bot]=image;alpha[top:bot]=layers['coverage'];clear[top:bot]=layers['clear_premultiplied']
   for n in samples:samples[n].append(layers[n])
  cache={n:np.concatenate(v,axis=0) for n,v in samples.items()}
  complete=s.apply_foreground(C.copy())
  np.savez_compressed(OUT/f'{k}-raw-prevalidation.npz',material=M,pre_foreground=C,complete=complete,coverage=alpha,clear=clear,**cache)
  np.testing.assert_array_equal(alpha,s.shape_coverage(P))
  replay=cache['sample_rgb'].reshape(H,2,W,2,3).mean((1,3)).astype(np.float32)
  np.testing.assert_array_equal(replay,C);np.testing.assert_array_equal(s.apply_foreground(replay.copy()),complete)
  (OUT/f'{k}-raw-prevalidation.npz').rename(OUT/f'{k}-raw.npz')
  z=metrics(s,M.astype(np.float32),complete,ext);rows.append({'reference':k,'scores':z,'coverage_exact_historical':True,'sample_replay_exact':True,'foreground_replay_exact':True})
  preview(s,complete,f'{k}-raw-comparison.png','Primary geometric baseline');print(json.dumps(rows[-1]),flush=True)
 save('raw-result.json',{'status':'PRIMARY_GEOMETRIC_BASELINE_WITH_OPEN_DEFECTS','references':rows,'new_native_images':2,'renderer_rays':total,'acceptance':'Primary selection is separate from visual-improvement acceptance; historical empirical fits remain archived.'})
if __name__=='__main__':
 p=argparse.ArgumentParser();p.add_argument('stage',choices=['preflight','render']);a=p.parse_args();{'preflight':preflight,'render':render}[a.stage]()
