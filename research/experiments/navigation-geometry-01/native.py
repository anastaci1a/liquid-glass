"""Source-first paired transfer diagnostic; original foreground and guards."""
import argparse,datetime,json,hashlib,time
from pathlib import Path
import cv2,numpy as np
from PIL import Image,ImageDraw
from extended_fit import Study
from geometric_optics import trace_flat_front_orthographic
from geometric_render import render_rows
from rounded_rectangle_back import RoundedRectangleHarmonicBack
ROOT=Path(__file__).resolve().parents[3];OUT=Path(__file__).parent
WORK=ROOT/'.evidence-working/navigation-geometry-01'
P=json.loads((ROOT/'reconstruction/studies/music-navigation/review-round/pass-03.json').read_text())['parameters']
protocol=json.loads((OUT/'protocol.json').read_text())
deadline=datetime.datetime.fromisoformat(protocol['stages'][0]['deadline']).timestamp()
cv2.setNumThreads(1)
def gate():
 if time.time()>deadline:raise RuntimeError('Declared refraction deadline reached')
def save(name,value):(OUT/name).write_text(json.dumps(value,indent=2)+'\n')
def setup(k):
 s=Study(WORK/k);c=dict(s.case);L=s.L
 c['center']=(np.asarray(c['center'])+L*np.array([P['shape_dx'],P['shape_dy']])).tolist()
 half=tuple(s.half+[P['half_x_delta'],P['half_y_delta']]);radius=min(s.radius+P['radius_delta'],*half)
 surf=RoundedRectangleHarmonicBack(half,radius)
 known=cv2.imread(str(WORK/k/'known.png'),0)>0;x0,y0,x1,y1=s.crop
 sd=s.shape(s.x,s.y,P)[-1][0];exterior=(sd>1.5/L)&(sd<.2)&known[y0:y1,x0:x1]
 X=s.x*L+s.case['center'][0];Y=s.y*L+s.case['center'][1]
 for a,b,c0,d in s.case.get('exterior_exclusions',[]):exterior&=~((X>=a)&(X<=c0)&(Y>=b)&(Y<=d))
 required=s.valid|exterior
 for layer in s.case['foreground_layers']:
  a,b,c0,d=layer['box'];required[b-y0:d-y0,a-x0:c0-x0]=True
 return s,c,surf,known,exterior,required
def preflight():
 if (OUT/'source-preflight.json').exists():raise RuntimeError('Completed preflight cannot repeat')
 rows=[];count=0
 for k in ['a','b']:
  gate();s,c,surf,known,ext,required=setup(k);x0,y0,x1,y1=s.crop;H,W=required.shape
  rec={'reference':k,'rays':0,'whole':0,'required':0,'unknown_unscored':0,'incomplete':0,'unsupported_required':0,'rgb_samples':0}
  for top in range(0,H,12):
   gate();bottom=min(top+12,H);yy,xx=np.mgrid[y0+top:y0+bottom:.5,x0:x1:.5]
   q=trace_flat_front_orthographic(surf,(xx-.25-c['center'][0])/s.L,(yy-.25-c['center'][1])/s.L,1.5,2.)
   count+=q['X'].size;rec['rays']+=q['X'].size;assert count<=2894400
   rec['incomplete']+=int((~q['complete']).sum())
   if not q['complete'].all():save('source-preflight-failure.json',rec);raise RuntimeError('Incomplete path')
   u=q['X']*s.L+c['center'][0];v=q['Y']*s.L+c['center'][1]
   ax=np.floor(u).astype(int);ay=np.floor(v).astype(int)
   supported=(ax>=0)&(ay>=0)&(ax+1<known.shape[1])&(ay+1<known.shape[0]);i,j=np.nonzero(supported)
   supported[i,j]&=known[ay[i,j],ax[i,j]]&known[ay[i,j]+1,ax[i,j]]&known[ay[i,j],ax[i,j]+1]&known[ay[i,j]+1,ax[i,j]+1]
   need=q['inside']|np.repeat(np.repeat(required[top:bottom],2,0),2,1)
   rec['whole']+=int(q['inside'].sum());rec['required']+=int(need.sum());rec['unknown_unscored']+=int((~supported&~need).sum())
   rec['unsupported_required']+=int((need&~supported).sum())
   if rec['unsupported_required']:save('source-preflight-failure.json',rec);raise RuntimeError('Unsupported original guard or lens source')
  np.savez_compressed(OUT/f'{k}-masks.npz',glass=s.valid,rim=s.rim,held=s.held,exterior=ext,required=required)
  rec['input_hashes']={n:hashlib.sha256((WORK/k/n).read_bytes()).hexdigest() for n in ['case.json','source.png','target.png','known.png']}
  rows.append(rec);print(json.dumps(rec),flush=True)
 save('source-preflight.json',{'status':'PASS','references':rows,'total_rays':count,'bilinear_texels':4,'source_kernel_radius':0,'confidence':'Recorded mosaic known mask; no hidden-scene truth claim.'})
def metrics(s,M,C,ext):
 z=s.scores(M);z['E']=float(np.sqrt(z['loss']));z['foreground_mse']={}
 x0,y0,_,_=s.crop
 for layer in s.case['foreground_layers']:
  if layer.get('fit_style',True) and layer['mode']!='transmission':
   a,b,c,d=layer['box'];z['foreground_mse'][layer.get('style_key',layer['vector_asset'])]=float(np.mean((C[b-y0:d-y0,a-x0:c-x0]-s.target[b:d,a:c])**2))*255**2
 z['exterior']={'pixels':int(ext.sum()),'rmse':float(np.sqrt(np.mean((C[ext]-s.target_crop[ext])**2))*255)}
 return z
def preview(s,C,k,label='Raw physical transfer'):
 H,W=C.shape[:2];canvas=Image.new('RGB',(2*W+2,H+64),'white');draw=ImageDraw.Draw(canvas)
 for i,(im,label) in enumerate([(s.target_crop,'Reference'),(C,label)]):
  valid=np.isfinite(im).all(2);im=np.where(valid[...,None],im,np.array([1,0,1]))
  canvas.paste(Image.fromarray(np.uint8(np.rint(np.clip(im,0,1)*255))),(i*(W+2),64));draw.text((i*(W+2)+8,20),label,fill='black')
 canvas.save(OUT/f'{k}-comparison.png')
def render():
 proof=json.loads((OUT/'source-preflight.json').read_text());assert proof['status']=='PASS'
 if (OUT/'raw-result.json').exists():raise RuntimeError('Completed native proposal cannot repeat')
 results=[];rays=0
 for k,rec in zip(['a','b'],proof['references']):
  gate();s,c,surf,known,ext,required=setup(k)
  for n,digest in rec['input_hashes'].items():assert hashlib.sha256((WORK/k/n).read_bytes()).hexdigest()==digest
  H,W=required.shape;M=np.zeros((H,W,3),np.float32);C=np.zeros_like(M);alpha=np.zeros((H,W));clear=np.zeros_like(M)
  for top in range(0,H,12):
   gate();bottom=min(top+12,H)
   image,_,support,layers=render_rows(s.source,c,{},surf,1.5,2.,top,bottom,raw_transmission=True,exact_bilinear=True,samples_per_axis=2,source_known=known,required_pixels=required,return_support=True,return_layers=True)
   rays+=(bottom-top)*W*4;assert rays<=2894400
   C[top:bottom]=image;M[top:bottom]=layers['lens_color'];alpha[top:bottom]=layers['coverage'];clear[top:bottom]=layers['clear_premultiplied']
  np.testing.assert_array_equal(alpha,s.shape_coverage(P))
  complete=s.apply_foreground(C.copy());z=metrics(s,M,complete,ext)
  np.savez_compressed(OUT/f'{k}-raw.npz',material=M,complete=complete,coverage=alpha,clear=clear)
  preview(s,complete,k);results.append({'reference':k,'scores':z,'coverage_exact_historical':True});print(json.dumps(results[-1]),flush=True)
 save('raw-result.json',{'status':'RAW_DIAGNOSTIC_NOT_ACCEPTANCE','references':results,'new_native_images':2,'renderer_rays':rays,'nuisances':'Unit body, no added optical blur, light, grading or shadow; frozen foreground.'})
if __name__=='__main__':
 p=argparse.ArgumentParser();p.add_argument('stage',choices=['preflight','render']);a=p.parse_args();{'preflight':preflight,'render':render}[a.stage]()
