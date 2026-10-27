from pathlib import Path
import json,hashlib
from PIL import Image,ImageDraw
B=Path(__file__).resolve().parent;R=B.parents[2];G=R/'guide';REFERENCES=B.parent/'miniplayer-outline-value-110';GEOM=B.parent/'miniplayer-outline-taper-107';assert (B/'finished.json').exists()
metadata={};options={};receipts=[];decoded=0

def image(p):
 global decoded
 im=Image.open(p);decoded+=im.width*im.height;assert decoded<100_000_000;return im.convert('RGB')
def pairs(left,variants,name,box=None,leftlabel='Apple reference'):
 if box:left=left.crop(box);variants=[[v.crop(box) for v in colors] for colors in variants]
 w,h=left.size;paths=[]
 for color,colors in enumerate(variants):
  choices=[]
  for width,right in enumerate(colors):
   label=f'Color {chr(65+color)} · {100+20*width}%';out=Image.new('RGB',(w*2+2,h+38),'white');out.paste(left,(0,38));out.paste(right,(w+2,38));draw=ImageDraw.Draw(out);draw.text((4,10),leftlabel,fill='black');draw.text((w+6,10),label,fill='black');path=f'assets/range112-{name}-c{color}-w{width}.png';out.save(G/path);receipts.append(dict(asset=path,sha256=hashlib.sha256((G/path).read_bytes()).hexdigest()));choices.append(dict(src=path,label=label))
   assert out.crop((0,38,w,h+38)).tobytes()==left.tobytes() and out.crop((w+2,38,2*w+2,h+38)).tobytes()==right.tobytes()
  paths.append(choices)
 path=paths[0][0]['src'];metadata[path]=dict(width=w*2+2,height=h+38,top=38,bottom=0,gutter=2,leftLabel=leftlabel,rightLabel='Color A · 100%');options[path]=paths
 return f'![{name}]({path})\n\n'
page='''# Choose outline color and right-side thickness

Use two dropdowns to choose color and non-left outline thickness. Every full comparison and zoomed crop switches together while its divider keeps position. Apple stays on the left. Additional comparisons keep Color A at 100% thickness on the left.

<div class="outline-range-controls" style="position:sticky;top:0;z-index:20;background:var(--bg,#fff);padding:12px;border:1px solid #ccc;border-radius:8px">
<label for="outline-color">Color</label>
<select id="outline-color" data-outline-range="outline-range-sources.json" aria-describedby="outline-range-status">'''
for i in range(11):page+=f'<option value="{i}">Color {chr(65+i)}'+(' — previous Step 5' if i==0 else '')+'</option>'
page+='''</select>
<label for="outline-thickness">Non-left thickness</label>
<select id="outline-thickness" aria-describedby="outline-range-status"><option value="0">100%</option><option value="1">120%</option><option value="2">140%</option><option value="3">160%</option><option value="4">180%</option></select>
<p id="outline-range-status" aria-live="polite">Color A · 100%</p>
</div>

Color A is the previous series' Step 5. Each following color multiplies saturation by 0.9509900499 and hue-shift strength by 0.88689046875, adding 0.010 to HSV value. The hue reduction is half of the originally proposed larger increment. HSV value is bounded at one, so brighter options can reach the ceiling.

Thickness increases affect the region to the right of the 43.36%–44.58% transition, including top, bottom and right endcap. The thin left region remains fixed. The transition blends into the chosen width, scaling plateau and fade together. Existing diagonal gaps remain unchanged.

Geometry, body, artwork, incident blur and shadow remain fixed. No choice is adopted automatically.

| Thickness | Non-left plateau | Non-left fade scale |
| --- | ---: | ---: |
| 100% | 1.20 px | 1.60 px |
| 120% | 1.44 px | 1.92 px |
| 140% | 1.68 px | 2.24 px |
| 160% | 1.92 px | 2.56 px |
| 180% | 2.16 px | 2.88 px |

| Color | Saturation versus A | Hue shift versus A | Extra HSV value |
| --- | ---: | ---: | ---: |
'''
for i in range(11):page+=f'| {chr(65+i)} | {100*(.99**5)**i:.3f}% | {100*(1-(1-.95**5)/2)**i:.3f}% | {i*.010:.3f} |\n'
page+='\n[Verification](../research/experiments/miniplayer-outline-range-112/README.md) · [Previous series](miniplayer-outline-options.md)\n\n'
for m in ['expanded','compact']:
 for r in ['a','b']:
  case=f'{m}-{r}';reference=image(REFERENCES/f'{case}-reference.png');variants=[[image(B/f'{case}-c{color}-w{width}.png') for width in range(5)] for color in range(11)];base=variants[0][0];w,h=base.size
  page+=f'## {case.replace("-"," ").title()}\n\n'+pairs(reference,variants,case)
  page+=f'<details data-hsv="{case}-previous"><summary>Compare with Color A at 100%</summary>\n\n'+pairs(base,variants,case+'-previous',leftlabel='Color A · 100%')+'</details>\n\n'
  page+=f'<details data-hsv="{case}-details"><summary>Zoomed outline, caps and transition crops</summary>\n\n'
  crops={'left-cap':(0,0,260,h),'right-cap':(w-260,0,w,h),'upper-rim':(w//2,12,w-180,75),'lower-rim':(w//2,h-85,w-180,h-20),'upper-right-gap':(w-180,0,w,125),'lower-left-gap':(0,h-125,180,h),'upper-transition':(int(w*.38),12,int(w*.50),75),'lower-transition':(int(w*.38),h-85,int(w*.50),h-20)}
  crops['white-content' if m=='compact' else 'brown-content']=(w//2-40,10,w-100,h-20) if m=='compact' else (260,12,620,90)
  rec=json.loads((GEOM/f'{case}-metrics.json').read_text());x0,y0,_,_=rec['crop'];a,b,c,d=rec['artwork_records'][0]['new_box'];crops['artwork']=(max(0,a-x0-12),max(0,b-y0-12),min(w,c-x0+12),min(h,d-y0+12))
  for name,box in crops.items():page+=pairs(reference,variants,case+'-'+name,box)
  page+='</details>\n\n'
page+='## Verification\n\nThe 55 combinations retain the completed body and artwork. Four base identities are exact, and 220 independent scalar HSV/composition replays pass within 1e-7. New widths use positive full-pixel area weights with successive-order refinement. No new optical transport, source filtering, fitting or aggregate score claims occur.\n'
(G/'miniplayer-outline-range.md').write_text(page);(G/'outline-range-comparison-panels.json').write_text(json.dumps(metadata,indent=2)+'\n');(G/'outline-range-sources.json').write_text(json.dumps(options,indent=2)+'\n');(B/'publication.json').write_text(json.dumps(dict(decoded_pixels=decoded,panels=receipts,comparison_count=len(metadata),color_options=11,width_options=5),indent=2)+'\n');print('PUBLISHED',len(metadata),len(receipts),decoded)
