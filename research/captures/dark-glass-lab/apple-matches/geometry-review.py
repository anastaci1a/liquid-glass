"""Private controlled geometry variants; no Apple fit or hand-drawn warp."""
import sys,json
from pathlib import Path
sys.path.insert(0,'/workspace/docs/liquid-glass/experiments/reconstruction')
import numpy as np
from PIL import Image,ImageDraw,ImageFont
from curvature import surface,footprint,capsule_offset
from solid import body_height,trace,primary_map

out=Path('/evidence/apple-matches/review-pass-03');out.mkdir(exist_ok=True)
font='/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf';F=ImageFont.truetype(font,17);S=ImageFont.truetype(font,13)
base=dict(height=1.2,beta=.5,crown_y=0,shoulder=2,ior=1.33,rear=1.,gap=1.,cross_curvature=1)
toolbar=dict(half=[196,85],radius=85)
outline=json.loads(Path('/workspace/docs/liquid-glass/experiments/reconstruction/contour.json').read_text())['geometry']
slider=dict(half=outline['half'],radius=outline['radius'],oval=outline['oval'])
diagnostics={}

def background(x,y):
 palette=np.array([[.37,.57,.76],[.74,.66,.48],[.66,.46,.62],[.39,.68,.60],[.28,.35,.49]])
 u=(x+260)/18;idx=np.floor(u).astype(int);t=u-np.floor(u);t=t*t*(3-2*t)
 color=palette[idx%5]*(1-t[...,None])+palette[(idx+1)%5]*t[...,None]
 line=np.exp(-(np.sin((y+130)*np.pi/38)/.045)**2)
 return color*(1-.65*line[...,None])

def render(name,case,p):
 # Identical display scaling, backdrop, Fresnel environment and AA across cells.
 scale=196/case['half'][0];Y,X=np.mgrid[-125:126,-245:246].astype(float)
 image=np.zeros((*X.shape,3));residual=[]
 for ox,oy in [(-.25,-.25),(.25,-.25),(-.25,.25),(.25,.25)]:
  x=(X+ox)/scale;y=(Y+oy)/scale;plain=background(X+ox,Y+oy)
  _,t=body_height(x,y,case,p);mask=t<1
  r=trace(x[mask],y[mask],case,p,bounces=32,cutoff=1e-6,intersection_steps=30)
  color=np.zeros((mask.sum(),3))
  for path in r['paths']:color+=background(path['position'][...,0]*scale,path['position'][...,1]*scale)*path['weight'][...,None]
  for path in r['environment']:
   light=.12+.60*np.maximum(0,path['direction'][...,1]);color+=light[...,None]*path['weight'][...,None]
  plain[mask]=color;image+=plain*.25;residual.append(r['residual'])
 diagnostics[name]={'untraced_energy_mean':float(np.concatenate(residual).mean()),'untraced_energy_max':float(np.concatenate(residual).max()),'parameters':p,'case':case}
 result=Image.fromarray(np.uint8(np.clip(image,0,1)*255))
 print('Rendered',name,diagnostics[name]['untraced_energy_mean'],flush=True)
 return result

def sheet(items,dest):
 image=Image.new('RGB',(491*len(items)+2*(len(items)-1),323),'#10151e');d=ImageDraw.Draw(image)
 for i,(title,subtitle,picture)in enumerate(items):
  x=i*493;d.text((x+12,8),title,font=F,fill='#e9edf4');d.text((x+12,31),subtitle,font=S,fill='#adb9c9');image.paste(picture,(x,59))
 image.save(out/dest)

old={**base,'crown_x':.4,'cap_join':0};smooth={**old,'cap_join':.30}
sheet([('Original cap join','Same slopes; abrupt curvature change',render('join-original',toolbar,old)),('Smoothed cap join','C2 transition; join width = 0.30 radius',render('join-smoothed',toolbar,smooth))],'01-cap-join-comparison.png')
items=[]
for c in [0,.15,.30]:
 p={**base,'crown_x':c,'cap_join':.30}
 items.append((f'Toolbar: crown {c:g}','Same height and optics; smooth cap join',render(f'toolbar-{c:g}',toolbar,p)))
sheet(items,'02-toolbar-curvature-options.png')
items=[]
for c in [0,.20,.40]:
 p={**base,'crown_x':c,'shoulder':1,'height':1.2,'cap_join':0}
 items.append((f'Slider: crown {c:g}','Measured oval; continuously rounded front',render(f'slider-{c:g}',slider,p)))
sheet(items,'03-slider-curvature-options.png')

# A continuous normal field does not imply continuous curvature or magnification.
a=toolbar['half'][0]-toolbar['radius'];y=np.array([40.,60.]);eps=.001
for name,p in [('original',old),('smoothed',smooth)]:
 def normal(x):return np.stack(surface(x,y,toolbar['half'],toolbar['radius'],p)[1:],axis=-1)
 x=np.full_like(y,a)
 left=(normal(x)-normal(x-eps))/eps;right=(normal(x+eps)-normal(x))/eps
 diagnostics['join-'+name]['normal_derivative_jump']=np.linalg.norm(left-right,axis=1).tolist()
 diagnostics['join-'+name]['normal_continuity_difference']=np.linalg.norm(normal(x+eps)-normal(x-eps),axis=1).tolist()
 # Relative horizontal source derivative at the upper straight region.
 try:
  px=np.array([30.,60.]);py=np.array([-65.,-65.]);h=.01
  J=(primary_map(px+h,py,toolbar,p)[0]-primary_map(px-h,py,toolbar,p)[0])/(2*h)
  diagnostics['join-'+name]['displayed_horizontal_scale']=(1/J).tolist()
 except ValueError as e:diagnostics['join-'+name]['scale_probe_unavailable']=str(e)

for c in [0,.15,.30]:
 p=diagnostics[f'toolbar-{c:g}']['parameters'];px=np.array([30.,60.]);py=np.array([-65.,-65.]);h=.01
 try:
  J=(primary_map(px+h,py,toolbar,p)[0]-primary_map(px-h,py,toolbar,p)[0])/(2*h)
  diagnostics[f'toolbar-{c:g}']['displayed_horizontal_scale']=(1/J).tolist()
 except ValueError as e:diagnostics[f'toolbar-{c:g}']['scale_probe_unavailable']=str(e)

# Bound the silhouette difference numerically, not by claiming identical shape.
x=np.linspace(-196,196,20001);r=85.;s=np.abs(x)-(196-r)
q0,_=capsule_offset(s,0);q1,_=capsule_offset(s,.3*r)
y0=np.sqrt(np.maximum(r*r-q0*q0,0));y1=np.sqrt(np.maximum(r*r-q1*q1,0))
diagnostics['silhouette_max_vertical_shift_px']=float(np.max(np.abs(y1-y0)))
diagnostics['limits']='Synthetic geometry comparisons, not Apple fits. Encoded RGB; fixed environment; finite internal-path series; no blur, tone curve, painted rim or fitted lighting. Convexity of arbitrary parameters is not certified.'
(out/'geometry-diagnostics.json').write_text(json.dumps(diagnostics,indent=2)+'\n')
print(json.dumps(diagnostics,indent=2),flush=True)
