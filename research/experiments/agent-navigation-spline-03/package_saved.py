"""Presentation and section extraction from saved arrays only; no evaluator."""
from pathlib import Path
import json,datetime
import numpy as np,cv2
from PIL import Image,ImageDraw
P=Path(__file__).resolve().parent;ROOT=P.parents[2];PRIMARY=ROOT.parent/'liquid-glass';CACHE=PRIMARY/'research/experiments/navigation-geometry-01';WORK=PRIMARY/'.evidence-working/navigation-geometry-01';protocol=json.loads((P/'protocol.json').read_text());assert datetime.datetime.now(datetime.timezone.utc)<datetime.datetime.fromisoformat(protocol['deadline_utc'].replace('Z','+00:00'))
result=json.loads((P/'result.json').read_text());ledger_before=(P/'ledger.json').read_bytes();present=[]
for key in ['a','b']:
 case=json.loads((WORK/key/'case.json').read_text());x0,y0,x1,y1=case['crop'];target=cv2.cvtColor(cv2.imread(str(WORK/key/'target.png')),cv2.COLOR_BGR2RGB).astype(np.float32)/255;target=target[y0:y1,x0:x1];old=np.load(CACHE/f'{key}-source-blur.npz')['complete'];candidate=np.load(P/f'{key}-candidate.npz')['complete'];row=next(x for x in result['records'] if x['case']==key);tiles=[]
 for name,rec in row['fixed_crops'].items():
  a,b,c,d=rec['native_crop_bounds'];w=c-a;width=min(2*w,max(w,1080));height=round((d-b)*width/w);panel=Image.new('RGB',(3*width+4,height+48),'white');draw=ImageDraw.Draw(panel)
  for col,(label,array) in enumerate([('Apple',target),('Current source-filtered baseline',old),('Fixed spline observation',candidate)]):
   tile=array[b:d,a:c];assert np.isfinite(tile).all();im=Image.fromarray(np.uint8(np.rint(np.clip(tile,0,1)*255))).resize((width,height),Image.Resampling.LANCZOS);panel.paste(im,(col*(width+2),48));draw.text((col*(width+2)+6,16),label+' / '+name,fill='black')
  panel.save(P/f'{key}-{name}.png');tiles.append({'case':key,'crop':name,'bounds':rec['native_crop_bounds'],'width_per_side':width})
 present+=tiles
sections=np.load(P/'sections.npz');svg=['<svg xmlns="http://www.w3.org/2000/svg" width="1000" height="530" viewBox="0 0 1000 530"><rect width="1000" height="530" fill="white"/>','<text x="35" y="25" font-family="sans-serif" font-size="18">Actual saved surface sections; coordinates in L (height axis enlarged)</text>']
for row,axis in enumerate(['x','y']):
 front=sections[axis+'_front'];back=sections[axis+'_back'];u=front[:,0 if axis=='x' else 1];low,high=float(u.min()),float(u.max());y0=70+row*240;X=lambda q:60+(q-low)/(high-low)*880;Z=lambda q:y0-q/.18*155
 svg.append(f'<text x="60" y="{y0-15}" font-family="sans-serif">{axis.upper()}–Z section: front 0; back from the same spline height</text>');svg.append(f'<path d="M60,{y0} L940,{y0}" stroke="#777" fill="none"/>');pts=' '.join(f'{X(v):.4f},{Z(z):.4f}' for v,z in zip(u,back[:,2]) if np.isfinite(z));svg.append(f'<polyline points="{pts}" stroke="#126b9a" stroke-width="2" fill="none"/>');svg.append(f'<text x="60" y="{y0+185}" font-family="sans-serif">{low:.4f} to {high:.4f} L; back range {np.nanmin(back[:,2]):.6f} to {np.nanmax(back[:,2]):.6f} L</text>')
svg.append('</svg>');(P/'surface-sections.svg').write_text('\n'.join(svg))
q=np.load(P/'native-paths.npz');x=q['x'];y=q['y'];inside=q['inside'];entries=q['entry'];back=q['back'];select=[];sv=['<svg xmlns="http://www.w3.org/2000/svg" width="1000" height="660"><rect width="1000" height="660" fill="white"/><text x="25" y="25" font-family="sans-serif" font-size="17">Saved 3D paths, X–Z projection; Y can vary after exit. No new trace.</text>']
for row,yn in enumerate([0.,-.75]):
 rr=int(np.argmin(abs(y[:,0]-yn)));idx=np.flatnonzero(inside[rr]);cols=idx[np.linspace(0,len(idx)-1,17).astype(int)];lo=-5.;hi=5.;top=65+row*290;XX=lambda a:50+(a-lo)/(hi-lo)*900;ZZ=lambda z:top-z/2.1*225
 sv.append(f'<text x="30" y="{top-12}" font-family="sans-serif">View row y = {y[rr,0]:.6f} L</text>');sv.append(f'<path d="M50,{ZZ(0)} L950,{ZZ(0)} M50,{ZZ(-2.1)} L950,{ZZ(-2.1)}" stroke="#999" fill="none"/>')
 for col in cols:
  points=[entries[rr,col],back[rr,col],np.array([q['X'][rr,col],q['Y'][rr,col],-2.1])];pts=' '.join(f'{XX(v[0]):.4f},{ZZ(v[2]):.4f}' for v in points);sv.append(f'<polyline points="{pts}" fill="none" stroke="#167b87" stroke-width="1"/>');select.append({'native_subray':[int(rr),int(col)],'entry':points[0].tolist(),'back':points[1].tolist(),'background':points[2].tolist(),'normal':q['outward_normal'][rr,col].tolist(),'exit_direction':q['exit_direction'][rr,col].tolist()})
sv.append('</svg>');(P/'saved-ray-projections.svg').write_text('\n'.join(sv));(P/'saved-selected-paths.json').write_text(json.dumps(select,indent=2)+'\n');assert ledger_before==(P/'ledger.json').read_bytes()
(P/'presentation.json').write_text(json.dumps({'finished_utc':datetime.datetime.now(datetime.timezone.utc).isoformat(),'crops':present,'sections':'Exact saved fixture sections, no geometry calls','ray_projections':'34 selected already-traced paths, only projected for plotting; no refitting or retracing','new_rays':0,'new_RGB_sampling_queries':0,'new_filters':0,'new_full_native_composites':0,'ledger_exact_unchanged':True},indent=2)+'\n');print('Saved-array packaging complete')
