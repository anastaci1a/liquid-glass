"""Complete rectangular query support, including partial-pixel exterior samples."""
from pathlib import Path
import json,numpy as np,cv2,copy
from extended_fit import Study
from source_support import masks,confidence_at
cv2.setNumThreads(1);R=Path('/evidence/extended/mail-toolbar-round');O=R/'final-media';s=Study(R/'a-canonical');r=json.loads((R/'pass-03/recipe.json').read_text());p=r['parameters'];D,_=masks(s);base=copy.deepcopy(s.case);crop=list(s.crop);reports=[]
for scale,dx,dy in [(2,0,0)]+[(1,*map(int,f.stem.split('_')))for f in sorted((O/'cache').glob('*.json'))]:
 s.case=copy.deepcopy(base);s.case['center']=[base['center'][0]+dx,base['center'][1]+dy];s.crop=[v+(dx if i%2==0 else dy)for i,v in enumerate(crop)];bad=n=0;bounds=[1e9,1e9,-1e9,-1e9]
 for row,bottom,W,x,y in s.raster_tiles(scale):
  X,Y,d,J=s.geometry_field(x,y,p);rx=(X*s.L+s.case['center'][0]).astype('float32');ry=(Y*s.L+s.case['center'][1]).astype('float32');q=confidence_at(D,rx,ry);bad+=int((q<.999999).sum());n+=q.size;bounds=[min(bounds[0],float(rx.min())),min(bounds[1],float(ry.min())),max(bounds[2],float(rx.max())),max(bounds[3],float(ry.max()))]
 assert bad==0,(scale,dx,dy,bad)
 reports.append({'scale':scale,'translation':[dx,dy],'all_rectangular_queries':n,'bad':bad,'bounds':bounds})
(O/'full-support.json').write_text(json.dumps({'method':'Every2x2 emitted ray in ENTIRE evaluated crop, including all partial-pixel/scored/outside samples; original defined mask bilinear confidence. Both HQ and every unique moving pose. Filters0. This is definedness of estimated RGB, not independent observation.','hidden_observed_fraction':0,'reports':reports},indent=2)+'\n');print('PASS FULL SUPPORT',len(reports))
