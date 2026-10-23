"""Bounded native spot controls and independent cached shadow reproduction."""
import json,datetime,time
import numpy as np
from native import OUT,P,setup,save
from geometric_render import render_rows,incident_source_filter
from vector_foreground import coverage
deadline=datetime.datetime.fromisoformat(json.loads((OUT/'protocol.json').read_text())['stages'][7]['deadline']).timestamp()
records=[];rays=0
for k in ['a','b']:
 if time.time()>deadline:raise RuntimeError('Review deadline reached')
 s,c,surf,known,ext,required=setup(k);raw=np.load(OUT/f'{k}-raw.npz');blur=np.load(OUT/f'{k}-source-blur.npz');chosen=np.load(OUT/f'{k}-shadow-1.npz')['complete']
 x0,y0,_,_=s.crop
 # One 32-pixel body strip, native sample phase unchanged.
 col,row=400,145;small=dict(c);small['crop']=[x0+col,y0+row,x0+col+32,y0+row+1]
 errors=[]
 for filtering,expected in [(False,raw),(True,blur)]:
  kwargs={}
  if filtering:
   src,support,radius=incident_source_filter(s.source,known,6.75);kwargs={'incident_source':src,'incident_known':support}
  image,_,layers=render_rows(s.source,small,{},surf,1.5,2.,0,1,raw_transmission=True,exact_bilinear=True,samples_per_axis=2,source_known=known,return_layers=True,**kwargs)
  rays+=128;assert rays<=512
  actual=layers['lens_color'].astype(np.float32);target=expected['material'][row:row+1,col:col+32]
  np.testing.assert_array_equal(actual,target);errors.append(float(abs(actual-target).max()))
 # Derive the frozen rounded-rectangle shadow independently of shadow().
 x=s.x-P['shape_dx']-P['shadow']['offset'][0];y=s.y-P['shape_dy']-P['shadow']['offset'][1]
 hx,hy=surf.half;r=surf.radius;qx=abs(x)-hx+r;qy=abs(y)-hy+r
 sd=np.hypot(np.maximum(qx,0),np.maximum(qy,0))+np.minimum(np.maximum(qx,qy),0)-r
 opacity=P['shadow']['opacity']*np.exp(-np.maximum(sd,0)**2/(2*P['shadow']['sigma']**2))
 attenuation=np.ones(raw['coverage'].shape)
 for layer in s.case['foreground_layers']:
  a,b,c0,d=layer['box'];style=s.case.get('foreground_styles',{}).get(layer.get('style_key',layer['vector_asset']),{});sl=np.s_[b-y0:d-y0,a-x0:c0-x0]
  if 'response' in style:assert np.max(abs(raw['clear'][sl]))==0
  attenuation[sl]*=1-coverage(s.folder,layer)*style.get('opacity',layer.get('opacity',1.))
 replay=(raw['complete'].astype(float)-raw['clear'].astype(float)*opacity[...,None]*attenuation[...,None]).astype(np.float32)
 np.testing.assert_array_equal(replay,chosen)
 np.testing.assert_array_equal(chosen[s.valid],raw['complete'][s.valid])
 before=(raw['complete'].astype(float)-s.target_crop)*255;after=(chosen.astype(float)-s.target_crop)*255
 delta=np.mean(after**2-before**2,2)
 records.append({'reference':k,'native_material_controls_max_difference':errors,'shadow_composite_exact':True,'original_glass_pixels_exact':True,'exterior_pointwise_worse':int((delta[ext]>0).sum()),'exterior_pointwise_total':int(ext.sum()),'maximum_exterior_MSE_increase':float(delta[ext].max())})
save('verification.json',{'status':'PASS_WITH_DECLARED_LIMITS','records':records,'native_control_rays':rays,'new_full_images':0,'scope':'Small exact native material controls plus complete cached shadow replay. Not full independent optical retracing or physical environment validation.'})
print(json.dumps(records),flush=True)
