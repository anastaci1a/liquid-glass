import time,json,datetime
from pathlib import Path
import numpy as np
from PIL import Image,ImageDraw
from scipy.optimize import minimize
from vector_foreground import _coverage
from settled import icon_color
from reproduce import CASES,scores,points,masks
P=Path('/evidence/extended/playback-pipeline-01');D=P/'icon';assert not (D/'trace-result.json').exists();deadline=min(time.time()+420,datetime.datetime(2026,10,22,9,12,57,tzinfo=datetime.timezone.utc).timestamp())
c=CASES['media'];x0,y0,x1,y1=c['crop'];p=json.loads(Path('/evidence/extended/playback-short-round/pass-03/replay-record.json').read_text())['recipe'];a,b,cc,d=[int(round(v*245+c['center'][i%2])) for i,v in enumerate(p['icon']['box_over_L'])];box=(a,b,cc,d);sl=np.s_[b-y0:d-y0,a-x0:cc-x0];oldalpha=np.asarray(Image.open(P/'code'/p['icon']['coverage']),float)/255;count=0;best=None
def svg(v):
 left,right,cy,H,rl,rt=v;vertices=np.array([[left,cy-H],[right,cy],[left,cy+H]]);arcs=[]
 for i,r in enumerate([rl,rt,rl]):
  q=vertices[i];u=vertices[(i-1)%3]-q;u/=np.linalg.norm(u);w=vertices[(i+1)%3]-q;w/=np.linalg.norm(w);theta=np.arccos(np.clip(u@w,-1,1));dist=r/np.tan(theta/2);assert dist<min(np.linalg.norm(vertices[(i-1)%3]-q),np.linalg.norm(vertices[(i+1)%3]-q))/2
  arcs.append((q+u*dist,q+w*dist,r))
 text=f'M{arcs[-1][1][0]},{arcs[-1][1][1]}'
 for entry,exit,r in arcs:text+=f'L{entry[0]},{entry[1]} A{r},{r} 0 0 1 {exit[0]},{exit[1]}'
 return f'<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 225 255"><path fill="black" d="{text}Z"/></svg>'.encode()
def f(v):
 global best,count
 if count>=72 or time.time()>deadline:raise RuntimeError('CAP')
 raw=svg(v);alpha=_coverage(raw,box,(a-.5,b-.5,cc-.5,d-.5),1).astype(float);loss=float(np.mean((alpha-oldalpha)**2));count+=1
 if best is None or loss<best[0]:best=(loss,list(map(float,v)),raw,alpha)
 return loss
try:minimize(f,[14,219,125,120,14,14],method='Powell',bounds=[(10,19),(211,225),(122,128),(114,125),(8,20),(8,20)],options={'maxfev':72,'xtol':.01,'ftol':1e-9})
except RuntimeError as e:assert str(e)=='CAP'
loss,v,raw,alpha=best;A=np.load(P/'blurriness/coverage.npy');B=np.load(P/'blurriness/candidate-material.npy');clear=np.load(P/'blurriness/clear-premultiplied.npy');C=(A[...,None]*B+clear).astype(np.float32);col=icon_color(np.load('/evidence/extended/playback-short-round/pass-03/candidate-material.npy'),p['icon'],245);C[sl]=C[sl]*(1-alpha[...,None])+col[sl]*alpha[...,None];ref=np.asarray(Image.open('/evidence/apple-matches/public-settled-replay/media-target.png'),np.float32)[y0:y1,x0:x1]/255;old=np.load(P/'blurriness/candidate-complete.npy');xs,ys,dx,dy=points(c);fg=np.zeros(xs.shape,bool)
for aa,bb,ccc,dd in c['foreground']:fg|=(xs>=aa)&(xs<=ccc)&(ys>=bb)&(ys<=dd)
err=float(np.mean(((C-ref)[fg]*255)**2));base=float(np.mean(((old-ref)[fg]*255)**2));np.save(D/'clean-trace-complete.npy',C);np.save(D/'clean-trace-alpha.npy',alpha);(D/'clean-rounded-play.svg').write_bytes(raw)
result={'parameters':dict(zip(['left','right','center_y','half_height','left_corner_radius','tip_radius'],v)),'shape_alpha_MSE':loss,'raster_evaluations':count,'foreground_MSE':err,'baseline_foreground_MSE':base,'numerical_foreground_pass':err<base,'exact_top_bottom_symmetry':True,'solid_geometry':'Three straight sides joined by true circular arcs; shared left corner radius; no raster, filters, opacity or screenshot matte','adoption':'PENDING_PRIMARY_VISUAL' if err<base else 'REJECTED_INPUT_PROPOSAL','optical_gain':False};(D/'trace-result.json').write_text(json.dumps(result,indent=2)+'\n');print(json.dumps(result))
canvas=Image.new('RGB',(1414,594),'white');dr=ImageDraw.Draw(canvas)
for j,(arr,label) in enumerate([(ref,'Apple'),(old,'Incumbent'),(C,'Clean trace proposal')]):
 im=Image.fromarray(np.uint8(np.rint(np.clip(arr[415-y0:680-y0,865-x0:1100-x0],0,1)*255))).resize((470,530),Image.Resampling.NEAREST);canvas.paste(im,(j*472,64));dr.text((j*472+4,20),label,fill='black')
canvas.save(D/'clean-trace-comparison.png')
