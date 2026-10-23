"""One fixed source PSF, independently certified before paired RGB evaluation."""
import argparse,datetime,json,time
from pathlib import Path
import cv2,numpy as np
from native import OUT,setup,save,metrics,preview
from geometric_optics import trace_flat_front_orthographic
from geometric_render import incident_source_filter,render_rows
deadline=datetime.datetime.fromisoformat(json.loads((OUT/'protocol.json').read_text())['stages'][1]['deadline']).timestamp()
def gate():
 if time.time()>deadline:raise RuntimeError('Blur stage deadline reached')
def preflight():
 if (OUT/'blur-source-proof.json').exists():raise RuntimeError('Completed support test cannot repeat')
 records=[];total=0
 for k in ['a','b']:
  s,c,surf,known,ext,required=setup(k);radius=21
  safe=cv2.erode(known.astype(np.uint8),np.ones((43,43),np.uint8),borderType=cv2.BORDER_CONSTANT,borderValue=0)>0
  x0,y0,x1,y1=s.crop;count=0;unsupported=0
  for top in range(0,y1-y0,12):
   gate();bot=min(top+12,y1-y0);yy,xx=np.mgrid[y0+top:y0+bot:.5,x0:x1:.5]
   q=trace_flat_front_orthographic(surf,(xx-.25-c['center'][0])/s.L,(yy-.25-c['center'][1])/s.L,1.5,2.)
   total+=q['X'].size;assert total<=2894400 and q['complete'].all()
   i,j=np.nonzero(q['inside']);u=q['X'][i,j]*s.L+c['center'][0];v=q['Y'][i,j]*s.L+c['center'][1]
   a=np.floor(u).astype(int);b=np.floor(v).astype(int);count+=len(a)
   assert ((a>=0)&(b>=0)&(a+1<safe.shape[1])&(b+1<safe.shape[0])).all()
   ok=safe[b,a]&safe[b+1,a]&safe[b,a+1]&safe[b+1,a+1];unsupported+=int((~ok).sum())
   if unsupported:
    save('blur-source-failure.json',{'reference':k,'unsupported':unsupported,'rays_attempted':total,'rgb_samples':0,'radius':radius});raise RuntimeError('Unsupported incident PSF; no RGB proposal')
  records.append({'reference':k,'whole_lens_rays':count,'unsupported':unsupported,'radius':radius,'rgb_samples':0})
 save('blur-source-proof.json',{'status':'PASS','references':records,'rays':total,'original_exterior_guard_support':'Reused unchanged raw proof; clear rays retain original source.'})
def render():
 assert json.loads((OUT/'blur-source-proof.json').read_text())['status']=='PASS'
 if (OUT/'blur-result.json').exists():raise RuntimeError('Completed proposal cannot repeat')
 baseline=json.loads((OUT/'raw-result.json').read_text());rows=[];rays=51840
 for k,old in zip(['a','b'],baseline['references']):
  s,c,surf,known,ext,required=setup(k);filtered,support,radius=incident_source_filter(s.source,known,6.75)
  raw=np.load(OUT/f'{k}-raw.npz');H,W=required.shape;M=np.zeros_like(raw['material']);C=np.zeros_like(M)
  start=0
  if k=='a':
   # The failed first tile was entirely clear exterior, with no foreground.
   # Reuse its exact saved float32 pixels; charge its attempted rays above.
   assert not raw['coverage'][:12].any()
   assert all(layer['box'][1]>=s.crop[1]+12 for layer in s.case['foreground_layers'])
   C[:12]=raw['clear'][:12];M[:12]=raw['material'][:12];start=12
  for top in range(start,H,12):
   gate();bot=min(top+12,H)
   image,_,ok,layers=render_rows(s.source,c,{},surf,1.5,2.,top,bot,raw_transmission=True,exact_bilinear=True,samples_per_axis=2,source_known=known,required_pixels=required,return_support=True,return_layers=True,incident_source=filtered,incident_known=support)
   rays+=(bot-top)*W*4;assert rays<=2894400
   np.testing.assert_array_equal(layers['coverage'],raw['coverage'][top:bot]);np.testing.assert_array_equal(layers['clear_premultiplied'].astype(raw['clear'].dtype),raw['clear'][top:bot])
   M[top:bot]=layers['lens_color'];C[top:bot]=image
  complete=s.apply_foreground(C.copy());z=metrics(s,M,complete,ext);prior=old['scores']
  guards={n:z[n]['rmse']<=prior[n]['rmse'] for n in ['glass','rim','held','interior','exterior']};guards.update(E=z['E']<=prior['E'],ssim=z['ssim']>=prior['ssim']);guards.update({n:z['foreground_mse'][n]<=v for n,v in prior['foreground_mse'].items()})
  np.savez_compressed(OUT/f'{k}-source-blur.npz',material=M,complete=complete)
  preview(s,complete,k+'-source-blur','Incident blur 6.75 px');rows.append({'reference':k,'scores':z,'guards':guards,'clear_and_coverage_exact':True});print(json.dumps(rows[-1]),flush=True)
 save('blur-result.json',{'status':'PAIRED_QUALIFIER_PENDING_VISUAL' if all(all(r['guards'].values()) for r in rows) else 'NO_PAIRED_QUALIFIER','sigma_native':6.75,'radius':21,'references':rows,'native_images':2,'renderer_rays_including_failed_tile':rays,'reused_clear_pixels':12960,'meaning':'Empirical incident PSF, not derived optical roughness.'})
if __name__=='__main__':
 p=argparse.ArgumentParser();p.add_argument('stage',choices=['preflight','render']);a=p.parse_args();{'preflight':preflight,'render':render}[a.stage]()
