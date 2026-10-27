from pathlib import Path
import json,hashlib
from PIL import Image,ImageDraw
B=Path(__file__).resolve().parent;R=B.parents[2];G=R/'guide';OLD=B.parent/'miniplayer-outline-value-110';GEOM=B.parent/'miniplayer-outline-taper-107';assert (B/'finished.json').exists()
metadata={};options={};receipts=[];decoded=0

def image(p):
 global decoded
 im=Image.open(p);decoded+=im.width*im.height;assert decoded<20_000_000;return im.convert('RGB')
def pairs(left,variants,name,box=None,leftlabel='Apple reference'):
 if box:left=left.crop(box);variants=[v.crop(box) for v in variants]
 w,h=left.size;paths=[]
 for step,right in enumerate(variants):
  assert left.size==right.size;label='Current' if step==0 else f'Step {step}'
  out=Image.new('RGB',(w*2+2,h+38),'white');out.paste(left,(0,38));out.paste(right,(w+2,38));draw=ImageDraw.Draw(out);draw.text((4,10),leftlabel,fill='black');draw.text((w+6,10),label,fill='black');path=f'assets/options111-{name}-step{step}.png';out.save(G/path);receipts.append(dict(asset=path,sha256=hashlib.sha256((G/path).read_bytes()).hexdigest()));paths.append(dict(src=path,label=label))
  assert out.crop((0,38,w,h+38)).tobytes()==left.tobytes() and out.crop((w+2,38,2*w+2,h+38)).tobytes()==right.tobytes()
 path=paths[0]['src'];metadata[path]=dict(width=w*2+2,height=h+38,top=38,bottom=0,gutter=2,leftLabel=leftlabel,rightLabel='Current');options[path]=paths
 return f'![{name}]({path})\n\n'
page='''# Choose an outline color step

Choose Current or Steps 1–5 in the dropdown. Every comparison and zoomed crop switches together while the divider keeps its position. Apple stays on the left; the chosen rendering appears on the right. Additional comparisons keep the current rendering on the left.

<label for="outline-step">Outline option</label>
<select id="outline-step" data-outline-options="outline-options-sources.json" aria-describedby="outline-step-status"><option value="0">Current — revision 110</option><option value="1">Step 1</option><option value="2">Step 2</option><option value="3">Step 3</option><option value="4">Step 4</option><option value="5">Step 5</option></select>
<p id="outline-step-status" aria-live="polite">Current — revision 110</p>

Each further step multiplies saturation by 0.99 and hue-shift strength by 0.95, then adds 0.002 to HSV value. Value is bounded at one. Thickness, spatial taper, artwork and lens rendering stay fixed. No option is selected for adoption.

| Option | Saturation versus current | Hue shift versus current | Extra HSV value |
| --- | ---: | ---: | ---: |
| Current | 100% | 100% | 0 |
'''
for i in range(1,6):page+=f'| Step {i} | {100*.99**i:.3f}% | {100*.95**i:.3f}% | {i*.002:.3f} |\n'
page+='\n[Verification](../research/experiments/miniplayer-outline-options-111/README.md) · [Current version](miniplayer-outline-value.md)\n\n'
for m in ['expanded','compact']:
 for r in ['a','b']:
  case=f'{m}-{r}';reference=image(OLD/f'{case}-reference.png');current=image(OLD/f'{case}-candidate.png');variants=[current]+[image(B/f'{case}-step{i}.png') for i in range(1,6)];w,h=current.size
  page+=f'## {case.replace("-"," ").title()}\n\n'+pairs(reference,variants,case)
  page+=f'<details data-hsv="{case}-previous"><summary>Compare with the current version</summary>\n\n'+pairs(current,variants,case+'-previous',leftlabel='Current version')+'</details>\n\n'
  page+=f'<details data-hsv="{case}-details"><summary>Zoomed outline, caps and transition crops</summary>\n\n'
  crops={'left-cap':(0,0,260,h),'right-cap':(w-260,0,w,h),'upper-rim':(w//2,12,w-180,75),'lower-rim':(w//2,h-85,w-180,h-20),'upper-right-gap':(w-180,0,w,125),'lower-left-gap':(0,h-125,180,h),'upper-transition':(int(w*.38),12,int(w*.50),75),'lower-transition':(int(w*.38),h-85,int(w*.50),h-20)}
  crops['white-content' if m=='compact' else 'brown-content']=(w//2-40,10,w-100,h-20) if m=='compact' else (260,12,620,90)
  rec=json.loads((GEOM/f'{case}-metrics.json').read_text());x0,y0,_,_=rec['crop'];a,b,c,d=rec['artwork_records'][0]['new_box'];crops['artwork']=(max(0,a-x0-12),max(0,b-y0-12),min(w,c-x0+12),min(h,d-y0+12))
  for name,box in crops.items():page+=pairs(reference,variants,case+'-'+name,box)
  page+='</details>\n\n'
page+='## Verification\n\nAll twenty candidates retain the current body and original outside-outline pixels. Four baseline identities are exact; twenty independent scalar HSV replays pass within 1e-7. Values reaching the declared ceiling are recorded. No new optical work, quadrature, filtering, fitting or scores were produced.\n'
(G/'miniplayer-outline-options.md').write_text(page);(G/'outline-options-comparison-panels.json').write_text(json.dumps(metadata,indent=2)+'\n');(G/'outline-options-sources.json').write_text(json.dumps(options,indent=2)+'\n');(B/'publication.json').write_text(json.dumps(dict(decoded_pixels=decoded,panels=receipts,comparison_count=len(metadata),options=6),indent=2)+'\n');print('PUBLISHED',len(metadata),len(receipts),decoded)
