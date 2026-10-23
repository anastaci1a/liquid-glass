from pathlib import Path
import sys,numpy as np
from PIL import Image,ImageDraw,ImageFont
sys.path.insert(0,'/workspace/docs/liquid-glass/experiments/reconstruction')
from solid import trace,body_height
from curvature import footprint
font='/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf';F=ImageFont.truetype(font,17);S=ImageFont.truetype(font,13)
out=Path('/tmp/review');out.mkdir(exist_ok=True)
case=dict(half=[196,85],radius=85)
base=dict(height=1.2,beta=.5,crown_y=0,shoulder=2,ior=1.33,rear=1.,gap=1.)
profiles=[('Constant crown',dict(crown_x=0,cross_curvature=0)),('Independent X crown',dict(crown_x=.4,cross_curvature=0)),('Cross-coupled curvature',dict(crown_x=.4,cross_curvature=1))]
canvas=Image.new('RGB',(1320,355),'#10151e');draw=ImageDraw.Draw(canvas)
levels=[0,.25,.5,.75,.9];colors=['#9dacbf','#78b4ff','#69d4be','#edbd75','#e58bb0']
a=np.linspace(0,2*np.pi,500);cx=np.cos(a);cy=np.sin(a)
for col,(name,extra) in enumerate(profiles):
 p={**base,**extra};H=min(case['half'])*p['height'];draw.text((col*440+18,14),name,font=F,fill='#e9edf4')
 for level,color in zip(levels,colors):
  low=np.zeros_like(a);high=np.minimum(np.divide(196,np.abs(cx),out=np.full_like(cx,np.inf),where=np.abs(cx)>1e-9),np.divide(85,np.abs(cy),out=np.full_like(cy,np.inf),where=np.abs(cy)>1e-9))
  for _ in range(35):
   r=(low+high)/2;x=r*cx;y=r*cy;h,t=body_height(x,y,case,p);ok=(t<=1)&(h>=level*H);low=np.where(ok,r,low);high=np.where(ok,high,r)
  r=(low+high)/2;points=list(zip((col*440+220+r*cx).tolist(),(155+r*cy).tolist()));draw.line(points,fill=color,width=2)
 draw.text((col*440+18,265),'XY sections; +Z points toward the viewer.',font=S,fill='#adb9c9')
for k,(level,color) in enumerate(zip(levels,colors)):draw.text((20+k*210,318),f'Z/H = {level:g}',font=S,fill=color)
canvas.save(out/'05-depth-sections.png')
# Genuine multiple-interface ray evaluation against an analytic background.
def background(x,y):
 palette=np.array([[.37,.57,.76],[.74,.66,.48],[.66,.46,.62],[.39,.68,.60],[.28,.35,.49]])
 u=(x+260)/18;idx=np.floor(u).astype(int);t=u-np.floor(u);t=t*t*(3-2*t)
 color=palette[idx%5]*(1-t[...,None])+palette[(idx+1)%5]*t[...,None]
 line=np.exp(-(np.sin((y+130)*np.pi/38)/.045)**2)
 return color*(1-.65*line[...,None])
y,x=np.mgrid[-125:126,-245:246].astype(float);plain=background(x,y);images=[]
for name,extra in [profiles[0],profiles[2]]:
 p={**base,**extra};r=trace(x,y,case,p,bounces=16,intersection_steps=28);color=np.zeros_like(plain)
 for path in r['paths']:color+=background(path['position'][...,0],path['position'][...,1])*path['weight'][...,None]
 for path in r['environment']:
  light=.12+.60*np.maximum(0,path['direction'][...,1]);color+=light[...,None]*path['weight'][...,None]
 _,t=body_height(x,y,case,p);color=np.where((t<=1)[...,None],color,plain)
 im=Image.new('RGB',(491,307),'#10151e');d=ImageDraw.Draw(im);d.text((12,9),name,font=F,fill='#e9edf4');im.paste(Image.fromarray(np.uint8(np.clip(color,0,1)*255)),(0,36));d.text((12,288),'Two curved interfaces; Snell + Fresnel.',font=S,fill='#adb9c9');images.append(im)
pair=Image.new('RGB',(984,307),'#10151e');pair.paste(images[0],(0,0));pair.paste(images[1],(493,0));pair.save(out/'06-geometry-ray-refraction.png')
