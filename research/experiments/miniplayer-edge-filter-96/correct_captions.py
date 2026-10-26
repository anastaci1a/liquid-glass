"""Correct one presentation label; all native comparison pixels stay exact."""
from pathlib import Path
from PIL import Image,ImageDraw,ImageFont
import hashlib,json
b=Path(__file__).parent;out=b/'as-run-headers';out.mkdir(exist_ok=True);rows=[];font=ImageFont.load_default(size=16)
for p in sorted(b.glob('*-comparison.png')):
 before=hashlib.sha256(p.read_bytes()).hexdigest();im=Image.open(p).convert('RGB');W=(im.width-4)//3;native=hashlib.sha256(im.crop((0,38,im.width,im.height)).tobytes()).hexdigest();im.crop((0,0,im.width,38)).save(out/p.name);draw=ImageDraw.Draw(im);draw.rectangle((W+2,0,2*W+3,37),fill='white');draw.text((W+6,8),'Previous combined94',font=font,fill='black');assert hashlib.sha256(im.crop((0,38,im.width,im.height)).tobytes()).hexdigest()==native;im.save(p);rows.append({'file':p.name,'original_sha256':before,'corrected_sha256':hashlib.sha256(p.read_bytes()).hexdigest(),'unchanged_native_pixels_sha256':native,'decoded_pixels':im.width*im.height})
(b/'caption-correction.json').write_text(json.dumps({'reason':'Shared presentation helper labeled the previous94 panel as original20. Only that header is corrected; original headers and all native image bytes are retained.','records':rows},indent=2)+'\n')
