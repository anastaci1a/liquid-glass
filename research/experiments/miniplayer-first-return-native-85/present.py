from pathlib import Path
from PIL import Image,ImageDraw,ImageFont
import numpy as np,json,hashlib
ROOT=Path('/repo');OUT=ROOT/'research/experiments/miniplayer-first-return-native-85';retired={};assets=[];crops=json.loads((ROOT/'research/experiments/miniplayer-inverse-forward-18/protocol.json').read_text())['fixed_crops'];font=ImageFont.load_default(size=16)
for member in ['expanded','compact']:
 for k in ['a','b']:
  name=member+'-'+k;src=OUT/(name+'-comparison.png');im=Image.open(src).convert('RGB');w=(im.width-4)//3;result=Image.new('RGB',(2*w+2,im.height),'white');left=im.crop((0,0,w,im.height));right=im.crop((2*(w+2),0,3*w+4,im.height));result.paste(left,(0,0));result.paste(right,(w+2,0));dest=ROOT/'guide/assets'/('geometric-'+member+'-first-return-'+k+'.png');result.save(dest);assert np.array_equal(np.asarray(result)[:,:w],np.asarray(left)) and np.array_equal(np.asarray(result)[:,w+2:],np.asarray(right));assets.append(dict(file=str(dest.relative_to(ROOT)),source=str(src.relative_to(ROOT)),source_panels=[1,3],pixels_exact=True,width=result.width,height=result.height,sha256=hashlib.sha256(dest.read_bytes()).hexdigest()))
  original=OUT/(name+'-crops.png');backup=OUT/(name+'-crops-as-run.png');backup.write_bytes(original.read_bytes());sheet=Image.open(original).convert('RGB');d=ImageDraw.Draw(sheet);y=0;protected=np.asarray(sheet).copy();allowed=np.zeros(protected.shape[:2],bool)
  for number,(_,box) in enumerate(crops[member].items(),1):
   a,b,c,e=box;cw=2*(c-a);ch=2*(e-b);d.rectangle((0,y,sheet.width-1,y+31),fill='white');allowed[y:y+32]=True
   for i,label in enumerate(['Ref','78','Return']):d.text((i*(cw+2)+3,y+6),str(number)+' '+label,font=font,fill='black')
   y+=ch+32+8
  assert np.array_equal(np.asarray(sheet)[~allowed],protected[~allowed]);sheet.save(original)
(OUT/'presentation.json').write_text(json.dumps(dict(assets=assets,crop_caption_only=True,noncaption_pixels_exact=True,crop_rows={m:list(v) for m,v in crops.items()},as_run_crops_retained=True,new_optical_evaluations=0),indent=2)+'\n')
# Same saved geometry and actual sparse rays: straight-body transverse projection.
with np.load(ROOT/'research/experiments/miniplayer-codesigned-native-78/actual-sections.npz') as z:section=z['expanded_y']
with np.load(ROOT/'research/experiments/miniplayer-first-return-83/expanded-returns.npz') as z:data={k:z[k] for k in ['cached_front','cached_back','return_point','return_interface_transmitted_direction','return_interface_blocked','initial_back_reflected_direction','return_interface_reflected_direction']}
def xy(p):return (500+390*float(p[1]),155-390*float(p[2]))
def poly(v):return ' '.join('%.5f,%.5f'%xy(p) for p in v)
F=np.stack([section[:,0],section[:,1],section[:,2]],-1);B=np.stack([section[:,0],section[:,1],section[:,3]],-1)
s=['<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 1000 300"><rect width="1000" height="300" fill="white"/><g font-family="sans-serif" font-size="14" fill="#222"><text x="25" y="25">Actual power-eight front and Hermite back; first reflected returns</text><text x="25" y="48">Transverse straight-body section. Equal axis scales; lengths in original L.</text></g>', '<polyline points="'+poly(F)+'" fill="none" stroke="#222" stroke-width="2"/>','<polyline points="'+poly(B)+'" fill="none" stroke="#222" stroke-width="2"/>']
for i in [4,12,20,28]:
 p0,p1,p2=[data[k][i] for k in ['cached_front','cached_back','return_point']];s.append('<polyline points="'+poly([p0,p1,p2])+'" fill="none" stroke="#c05a00" stroke-width="1.5"/>');blocked=bool(data['return_interface_blocked'][i]);direction=data['return_interface_reflected_direction' if blocked else 'return_interface_transmitted_direction'][i];end=p2+.12*direction;s.append('<polyline points="'+poly([p2,end])+'" fill="none" stroke="'+('#9845b0' if blocked else '#087e8b')+'" stroke-width="2" stroke-dasharray="4 2"/>')
s+=['<g font-family="sans-serif" font-size="14" fill="#222"><text x="25" y="235">Orange: traced front/back/return path. Teal: emitted direction. Purple: retained TIR direction.</text><text x="25" y="258">Dashed segments show directions only; no later intersection or scene endpoint is invented.</text><text x="25" y="281">Geometry: cached78 sections. Rays: exact same-surface sparse83 data.</text></g></svg>'];(OUT/'actual-return-section.svg').write_text(''.join(s))
