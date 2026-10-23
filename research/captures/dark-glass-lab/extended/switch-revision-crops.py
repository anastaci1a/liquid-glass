"""Registered visible-composite diagnostics and fresh-render crop comparisons."""
import sys,json,argparse
from pathlib import Path
ap=argparse.ArgumentParser(description=__doc__)
for name in ['inputs','previous','candidate','hq','out']:ap.add_argument(name,type=Path)
ap.add_argument('--code',type=Path,default=Path('/workspace/docs/liquid-glass/experiments/reconstruction'))
ap.add_argument('--previous-label',default='previous');ap.add_argument('--current-label',default='candidate')
args=ap.parse_args();sys.path.insert(0,str(args.code))
import cv2,numpy as np
from PIL import Image
from extended_fit import Study
from revision_replay import clean_composite
from crop_diagnostics import diagnostics
from publish import pair
cv2.setNumThreads(1)
out=args.out;out.mkdir(parents=True,exist_ok=True);models=[json.loads(p.read_text()) for p in [args.previous,args.candidate]]
crops={'upper-left':[.12,.06,.40,.31],'lower-left':[.12,.64,.42,.87],'right-rim':[.72,.28,.91,.70],'center':[.35,.35,.65,.65]}
keep=['bounds_normalized','bounds_pixels','rgb_rmse_255','channel_rmse_255','luma_rmse_255','chroma_rmse_255','mean_signed_rgb_255','pixel_error_p95_255'];summary=[];details=[];panels=[];tail=[]
for label in ['a','b']:
 s=Study(args.inputs/label);row=dict(observation=label.upper(),states=[]);fullrow=dict(observation=label.upper(),states=[]);tails=[]
 for model in models:
  p=model['parameters'];im=s.render(p,np.array(model['material']));C=clean_composite(s,p,im);detail=diagnostics(s.target_crop,C,crops);fullrow['states'].append(detail);row['states'].append({name:{k:v for k,v in value.items() if k in keep} for name,value in detail.items()});band=[]
  for lo,hi in [(0,.10),(.10,.20),(.20,.35),(.35,.55),(.55,.8)]:
   mask=(s.sd>lo)&(s.sd<=hi);band.append(dict(bounds_over_L=[lo,hi],pixels=int(mask.sum()),rmse=float(np.sqrt(np.mean(((C-s.target_crop)[mask]*255)**2))) if mask.any() else None))
  tails.append(band)
 summary.append(row);details.append(fullrow);tail.append(dict(observation=label.upper(),states=tails))
 fresh=np.array(Image.open(args.hq/f'{label}-render.png').convert('RGB'));reference=cv2.resize(np.uint8(np.rint(s.target_crop*255)),(fresh.shape[1],fresh.shape[0]),interpolation=cv2.INTER_LANCZOS4)
 H,W=s.target_crop.shape[:2]
 for name,box in crops.items():
  if name=='center':continue
  a,b,c,d=[round(v*size)*4 for v,size in zip(box,[W,H,W,H])]
  pane=pair(reference[b:d,a:c],fresh[b:d,a:c],[f'{label.upper()} Apple {name}',args.current_label],font_size=28)
  pane=pane.resize((1282,round(pane.height*1282/pane.width)),Image.Resampling.LANCZOS);panels.append(pane)
canvas=Image.new('RGB',(1282,sum(p.height for p in panels)),(20,23,29));y=0
for panel in panels:canvas.paste(panel,(0,y));y+=panel.height
canvas.save(out/'current-crops.png');(out/'visible-crops.json').write_text(json.dumps(dict(advisory_only=True,state_order=[args.previous_label,args.current_label],scope='Fixed native crops of visible clean composite; fresh4x images, no recenter/recolor; no crop acceptance gate',observations=summary),indent=2)+'\n');(out/'full-crop-profiles.json').write_text(json.dumps(details,indent=2)+'\n');(out/'shadow-tails.json').write_text(json.dumps(tail,indent=2)+'\n');print(json.dumps({r['observation']:{k:[v[k]['rgb_rmse_255'] for v in r['states']] for k in crops} for r in summary}),flush=True)
