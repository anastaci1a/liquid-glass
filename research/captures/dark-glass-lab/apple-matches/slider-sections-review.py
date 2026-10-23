"""Shape-only variants; rejected optical trials are not presented as choices."""
import sys,json
from pathlib import Path
import numpy as np
from PIL import Image,ImageDraw,ImageFont
sys.path.insert(0,'/workspace/docs/liquid-glass/experiments/reconstruction')
from solid import body_height

out=Path('/evidence/apple-matches/review-pass-03')
g=json.loads(Path('/workspace/docs/liquid-glass/experiments/reconstruction/contour.json').read_text())['geometry']
case=dict(half=g['half'],radius=g['radius'],oval=g['oval'])
font='/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf';F=ImageFont.truetype(font,17);S=ImageFont.truetype(font,13)
canvas=Image.new('RGB',(1478,600),'#10151e');d=ImageDraw.Draw(canvas)
levels=[0,.25,.5,.75,.9];colors=['#9dacbf','#78b4ff','#69d4be','#edbd75','#e58bb0']
for col,crown in enumerate([.2,.4,.6]):
 p=dict(height=1.2,beta=.5,crown_x=crown,crown_y=0,cross_curvature=1,shoulder=1,ior=1.33,rear=1,gap=1)
 xbase=col*493;scale=196/case['half'][0];H=min(case['half'])*p['height']
 d.text((xbase+14,12),f'Slider: crown {crown:g}',font=F,fill='#e9edf4')
 d.text((xbase+14,38),'Longitudinal section, Y = 0',font=S,fill='#adb9c9')
 x=np.linspace(-case['half'][0],case['half'][0],1000);h,_=body_height(x,np.zeros_like(x),case,p)
 d.line([(xbase+25,187),(xbase+465,187)],fill='#334153')
 for sign in [-1,1]:d.line(list(zip(xbase+245+x*scale,187-sign*h*scale)),fill='#78b4ff',width=2)
 d.text((xbase+14,340),'XY sections at increasing Z/H',font=S,fill='#adb9c9')
 theta=np.linspace(0,2*np.pi,1000);ct=np.cos(theta);st=np.sin(theta)
 for level,color in zip(levels,colors):
  low=np.zeros_like(theta);high=np.minimum(np.divide(case['half'][0],np.abs(ct),out=np.full_like(ct,np.inf),where=np.abs(ct)>1e-9),np.divide(case['half'][1],np.abs(st),out=np.full_like(st,np.inf),where=np.abs(st)>1e-9))
  for _ in range(40):
   R=(low+high)*.5;height,t=body_height(R*ct,R*st,case,p);ok=(t<=1)&(height>=level*H);low=np.where(ok,R,low);high=np.where(ok,high,R)
  R=(low+high)*.5;d.line(list(zip(xbase+245+scale*R*ct,465+scale*R*st)),fill=color,width=2)
for k,(level,color)in enumerate(zip(levels,colors)):d.text((15+210*k,565),f'Z/H = {level:g}',font=S,fill=color)
canvas.save(out/'03-slider-shape-options.png')
