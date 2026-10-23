"""Cached-evidence package; no optical queries or candidate fitting."""
from pathlib import Path
import json
import numpy as np
from PIL import Image,ImageDraw
from geometric_optics import RadialCurvatureBack,HarmonicCircularBack
OUT=Path('/evidence/extended/geometric-playback-inferred');root=OUT/'public-package';root.mkdir(exist_ok=False)
for name,folder,cls in [('g04','geometric-playback-harmonic',HarmonicCircularBack),('g05','geometric-playback-inferred',RadialCurvatureBack)]:
 d=Path('/evidence/extended')/folder;result=json.loads((d/'result.json').read_text());spec=result['geometry']['surface'];family=spec['family'];params={k:v for k,v in spec.items() if k not in ['family','index','background_distance']};s=cls(**params)
 recipe=dict(surface_kind='harmonic' if name=='g04' else 'curvature',surface=params,index=1.5,background_distance=2,raw_transmission=True,exact_bilinear=True)
 (root/f'{name}-surface.json').write_text(json.dumps(recipe,indent=2)+'\n')
 summary=dict(classification='USEFUL_NEGATIVE_NOT_ACCEPTED_VISIBLE_IMPROVEMENT' if name=='g04' else 'GEOMETRIC_BASELINE_NOT_A_NEW_VISIBLE_IMPROVEMENT',geometry={k:v for k,v in result['geometry'].items() if k!='surface'},surface_recipe=f'{name}-surface.json',source_hashes=result['proof']['source_hashes'],source_support={k:result['proof'][k] for k in ['all_crop_rays','whole_lens_rays','all_original_scored_subrays','incomplete','unsupported_bilinear','unsupported_registered_frame_texels','source_query_bounds']},scores=result['visible_composite_scores'],local=result['local'],scope=result['scope'],optical_source_blur=0,optical_output_blur=0,sampling='4x4 finite pixel integration and exact bilinear; not optical blur',renders=1,fits=0,public_wrapper_partial_control=json.loads((d/'public-wrapper-partial-control.json').read_text()))
 (root/f'{name}.json').write_text(json.dumps(summary,indent=2)+'\n')
 # Actual profiles and saved ray segments; no extra traced rays.
 v=Image.new('RGB',(1000,800),'white');draw=ImageDraw.Draw(v);scale=260;ox=500;oy=85;xy=lambda x,z:(ox+x*scale,oy-z*scale);xx=np.linspace(-1,1,1001);back=s.section(xx)[0]
 draw.line([xy(-1,0),xy(1,0)],fill='#111',width=2);draw.line([xy(x,z) for x,z in zip(xx,back)],fill='#14749b',width=2);draw.line([xy(-1.6,-2),xy(1.6,-2)],fill='#888',width=2)
 rays=np.load(d/'radial-geometry.npz');r=rays['r']
 for rr in [.6,.8,.9,.95,.99]:
  i=int(np.argmin(abs(r-rr)))
  for sign in [-1,1]:
   p=rays['back'][i];draw.line([xy(sign*r[i],.2),xy(sign*r[i],0),xy(sign*p[0],p[2]),xy(sign*rays['X'][i],-2)],fill='#b74a27',width=1)
 draw.text((20,690),f'{name.upper()}: actual section and saved traced rays, x and z at equal scale.',fill='black');draw.text((20,716),'Front z=0; background z=-2L; exact edge crease unresolved. No separate decorative lens.',fill='black');v.save(root/f'{name}-rays.png')
print(root)
