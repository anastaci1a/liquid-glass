from pathlib import Path
from PIL import Image
import numpy as np,json,hashlib,sys
sys.path.insert(0,'/workspace/docs/liquid-glass/experiments/reconstruction');from publish import pair
R=Path('/workspace/docs/liquid-glass');O=Path('/evidence/extended/toolbar-format-round');assert not(O/'verification.json').exists();meta=json.loads((R/'comparison-panels.json').read_text());target=Image.open('/evidence/apple-matches/public-settled-replay/regular-target.png').convert('RGB')
boxes={'match-regular.png':[475,285,1445,845],'match-regular-rim.png':[650,369,1270,468],'toolbar-underside-current.png':[650,650,1270,726]};records={}
for name,box in boxes.items():
 im=Image.open(R/'assets'/name).convert('RGB');decl=meta['assets/'+name];w=(im.width-2)//2;bodyh=im.height-decl['top'];oldright=im.crop((w+2,decl['top'],im.width,im.height));h=round(1080*bodyh/w)
 left=target.crop(box).resize((1080,h),Image.Resampling.LANCZOS);right=oldright.resize((1080,h),Image.Resampling.LANCZOS);out=pair(np.asarray(left),np.asarray(right),('Apple source','Reconstruction'),font_size=32);out.save(O/name)
 records[name]={'old_size':list(im.size),'size':list(out.size),'top':64,'bottom':0,'gutter':2,'native_crop':box,'left':'Original native target cropped then resized once','right':'Accepted lossless4x RGB body resized; no material or optical render','old_sha256':hashlib.sha256((R/'assets'/name).read_bytes()).hexdigest(),'sha256':hashlib.sha256((O/name).read_bytes()).hexdigest(),'right_pixel_exact_to_declared_resize':bool(np.array_equal(np.asarray(out)[64:,1082:],np.asarray(right)))}
 assert records[name]['right_pixel_exact_to_declared_resize']
(O/'verification.json').write_text(json.dumps(dict(format_only=True,scientific_passes=0,native_scoring_unchanged=True,figures=records),indent=2)+'\n');print(json.dumps(records))
