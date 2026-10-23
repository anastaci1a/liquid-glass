"""Saved-array sections/crops/review only. No surface or render imports."""
from pathlib import Path
import json,datetime,hashlib
import numpy as np,cv2
from PIL import Image,ImageDraw
P=Path(__file__).resolve().parent;Q=P.parent/'agent-navigation-spline-03';ROOT=P.parents[2];PRIMARY=ROOT.parent/'liquid-glass';CACHE=PRIMARY/'research/experiments/navigation-geometry-01';WORK=PRIMARY/'.evidence-working/navigation-geometry-01';proto=json.loads((P/'protocol.json').read_text());assert datetime.datetime.now(datetime.timezone.utc)<datetime.datetime.fromisoformat(proto['deadline'].replace('Z','+00:00'));ledger=(P/'ledger.json').read_bytes();b=json.loads((Q/'native-reservation.json').read_text())['bounds'];L=b['L'];a,r=b['half'][0],b['radius'];q0=np.load(Q/'native-paths.npz');x,y=q0['x'],q0['y'];inside=q0['inside'];step=float(x[0,1]-x[0,0]);straight=inside&(abs(x)<a-r-2*step);caps=inside&(abs(x)>a-r+2*step);mode={};summary=[]
def st(v,m):
 t=v[m];t=t[np.isfinite(t)];return dict(count=int(t.size),min=float(t.min()),median=float(np.median(t)),max=float(t.max()),rms=float(np.sqrt(np.mean(t*t))))
for label in ['plus','minus']:
 q=np.load(P/label/'paths.npz');np.testing.assert_array_equal(q['inside'],inside);valid=inside&q['complete'];dx=(q['X']-q0['X'])*L;dy=(q['Y']-q0['Y'])*L;mode[label]={'strength':.1 if label=='plus' else -.1,'straight_delta_X_px':st(dx,straight),'straight_delta_Y_px':st(dy,straight),'cap_delta_X_px':st(dx,caps),'cap_delta_Y_px':st(dy,caps),'sections':[]}
 for yn in [0.,-.75,.75]:
  rr=int(np.argmin(abs(y[:,0]-yn)));m=straight[rr];mode[label]['sections'].append(dict(row=rr,y_L=float(y[rr,0]),delta_X_px=st(dx[rr],m),delta_Y_px=st(dy[rr],m)))
 result=json.loads((P/label/'result.json').read_text())
 for rec in result['records']:
  summary.append(dict(sign=label,case=rec['case'],E=rec['scores']['E'],SSIM=rec['scores']['ssim'],H1_failed=[k for k,v in rec['H1_guards'].items() if not v],zero_failed=[k for k,v in rec['zero_guards'].items() if not v],completed_H1_failed=[k for k,v in rec['completed_H1_guards'].items() if not v],completed_zero_failed=[k for k,v in rec['completed_zero_guards'].items() if not v],partial_errors=rec['partial_errors'],fixed_crops=rec['fixed_crops'],clips=[rec['raw_clips_below'],rec['raw_clips_above']]))
# Native saved height/path sections, including their actual nonzero center offsets.
svg=['<svg xmlns="http://www.w3.org/2000/svg" width="1080" height="650"><rect width="1080" height="650" fill="white"/><text x="25" y="24" font-family="sans-serif" font-size="18">Saved actual back sections and X-Z path projections (Y may vary)</text>'];selected=[]
for row,yn in enumerate([0.,-.75]):
 rr=int(np.argmin(abs(y[:,0]-yn)));ids=np.flatnonzero(inside[rr]);ix=ids[np.linspace(0,len(ids)-1,25).astype(int)];top=65+row*290;XX=lambda v:40+(v+5)*100;ZZ=lambda v:top-v/2.1*225
 svg.append(f'<text x="40" y="{top-10}" font-family="sans-serif">Saved y = {y[rr,0]:.7f} L; gray zero, red +0.1, blue -0.1</text>')
 for label,color,paths in [('zero','#888',q0),('plus','#bd4b38',np.load(P/'plus/paths.npz')),('minus','#2671b5',np.load(P/'minus/paths.npz'))]:
  for col in ix:
   pts=[paths['entry'][rr,col],paths['back'][rr,col],np.array([paths['X'][rr,col],paths['Y'][rr,col],-2.1])];sv=' '.join(f'{XX(p[0]):.4f},{ZZ(p[2]):.4f}' for p in pts);svg.append(f'<polyline points="{sv}" fill="none" stroke="{color}" stroke-width="0.8" opacity="0.65"/>');selected.append(dict(setting=label,row=rr,col=int(col),entry=pts[0].tolist(),back=pts[1].tolist(),background=pts[2].tolist(),normal=paths['outward_normal'][rr,col].tolist(),direction=paths['exit_direction'][rr,col].tolist()))
 svg.append(f'<path d="M40,{ZZ(0)} L1040,{ZZ(0)} M40,{ZZ(-2.1)} L1040,{ZZ(-2.1)}" fill="none" stroke="#aaa"/>')
svg.append('</svg>');(P/'saved-paths.svg').write_text('\n'.join(svg));(P/'saved-paths.json').write_text(json.dumps(selected,indent=2)+'\n')
# Sections use exactly the saved row/column, never a fresh idealized height grid.
sections={}
for label,paths in [('zero',q0),('plus',np.load(P/'plus/paths.npz')),('minus',np.load(P/'minus/paths.npz'))]:
 rr=int(np.argmin(abs(y[:,0])));cc=int(np.argmin(abs(x[0])))
 sections[label]={'longitudinal_y_L':float(y[rr,0]),'transverse_x_L':float(x[0,cc]),'longitudinal':{'x':x[rr].tolist(),'back_z':np.where(inside[rr],paths['back'][rr,:,2],0).tolist(),'inside':inside[rr].tolist()},'transverse':{'y':y[:,cc].tolist(),'back_z':np.where(inside[:,cc],paths['back'][:,cc,2],0).tolist(),'inside':inside[:,cc].tolist()}}
(P/'saved-sections.json').write_text(json.dumps(sections,indent=2)+'\n')
sv=['<svg xmlns="http://www.w3.org/2000/svg" width="1080" height="500"><rect width="1080" height="500" fill="white"/><text x="25" y="25" font-family="sans-serif" font-size="18">Actual cached height sections; height axis enlarged, not new evaluations</text>']
for row,axis in enumerate(['longitudinal','transverse']):
 top=75+row*220;limit=5 if row==0 else 1.1
 for label,color in [('zero','#888'),('plus','#bd4b38'),('minus','#2671b5')]:
  sec=sections[label][axis];coord=sec['x' if row==0 else 'y'];pts=' '.join(f'{40+(v+limit)/(2*limit)*1000:.4f},{top-z/.17*140:.4f}' for v,z,ok in zip(coord,sec['back_z'],sec['inside']) if ok);sv.append(f'<polyline points="{pts}" fill="none" stroke="{color}" stroke-width="1.5"/>')
 sv.append(f'<text x="40" y="{top-15}" font-family="sans-serif">{axis}: gray zero, red +0.1, blue -0.1</text>')
sv.append('</svg>');(P/'saved-sections.svg').write_text('\n'.join(sv))
for key in ['a','b']:
 case=json.loads((WORK/key/'case.json').read_text());x0,y0,x1,y1=case['crop'];target=cv2.cvtColor(cv2.imread(str(WORK/key/'target.png')),cv2.COLOR_BGR2RGB).astype(np.float32)/255;target=target[y0:y1,x0:x1];arrays=[('Apple',target),('Current incident H1',np.load(CACHE/f'{key}-source-blur.npz')['complete']),('Spline zero',np.load(Q/f'{key}-candidate.npz')['complete']),('+0.1',np.load(P/'plus'/f'{key}-candidate.npz')['complete']),('-0.1',np.load(P/'minus'/f'{key}-candidate.npz')['complete'])]
 rec=next(z for z in summary if z['sign']=='plus' and z['case']==key)
 for name,meta in rec['fixed_crops'].items():
  a0,b0,c0,d0=meta['native_crop_bounds'];w=c0-a0;outw=min(2*w,max(w,1080));outh=round((d0-b0)*outw/w);panel=Image.new('RGB',(5*outw+8,outh+48),'white');draw=ImageDraw.Draw(panel)
  for i,(title,array) in enumerate(arrays):
   tile=array[b0:d0,a0:c0];assert np.isfinite(tile).all();im=Image.fromarray(np.uint8(np.rint(np.clip(tile,0,1)*255))).resize((outw,outh),Image.Resampling.LANCZOS);panel.paste(im,(i*(outw+2),48));draw.text((i*(outw+2)+5,16),title+' / '+name,fill='black')
  panel.save(P/f'{key}-{name}.png')
# Mask/filter accounting describes actual past operations, not additional work.
maskwork=[]
for key in ['a','b']:
 ar=np.load(P/f'{key}-incident.npz');shape=list(ar['safe'].shape);maskwork.append(dict(case=key,shape=shape,mask_erosions=2,mask_output_pixels=2*int(ar['safe'].size),filter_count=1,filter_RGB_output_pixels=int(ar['safe'].size),kernel=[43,43]))
assert ledger==(P/'ledger.json').read_bytes()
record=dict(status='THREE_SETTINGS_CLOSED_NO_H1_QUALIFIER',utc=datetime.datetime.now(datetime.timezone.utc).isoformat(),summary=summary,coordinate_modes=mode,filter_mask_work=maskwork,ledger=json.loads(ledger),new_scientific_work_during_packaging=dict(rays=0,height=0,RGB_queries=0,filters=0,composites=0))
(P/'review-data.json').write_text(json.dumps(record,indent=2,allow_nan=False)+'\n');print(json.dumps({'summary':[{k:v for k,v in r.items() if k not in ['fixed_crops']} for r in summary],'modes':mode,'mask_work':maskwork},indent=2))
