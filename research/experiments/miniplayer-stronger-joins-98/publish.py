"""Presentation-only crops of sealed PNGs; no numerical model execution."""
from pathlib import Path
from PIL import Image, ImageDraw
import json, hashlib
ROOT=Path('/repo'); OUT=Path(__file__).parent; EXP=OUT.parent
guide=ROOT/'guide'; meta={}; receipts=[]; decoded=0
def read(p):
 global decoded
 im=Image.open(p); decoded+=im.width*im.height
 assert decoded<=80000000
 return im.convert('RGB')
def pair(tag,src,left=0,old=None,box=None,label='Apple reference'):
 im=read(src); w=(im.width-4)//3; h=im.height-38
 a=im.crop((left*(w+2),38,left*(w+2)+w,38+h)); b=im.crop((2*(w+2),38,2*(w+2)+w,38+h))
 if old:
  oi=read(old); assert oi.size==im.size
  a=oi.crop((2*(w+2),38,2*(w+2)+w,38+h))
 if box:a=a.crop(box);b=b.crop(box)
 w,h=a.size; result=Image.new('RGB',(2*w+2,h+38),'white');result.paste(a,(0,38));result.paste(b,(w+2,38))
 ImageDraw.Draw(result).text((4,10),label,fill='black');ImageDraw.Draw(result).text((w+6,10),'Experimental result',fill='black')
 rel=f'assets/feedback98-{tag}.png'; result.save(guide/rel)
 assert result.crop((0,38,w,38+h)).tobytes()==a.tobytes()
 assert result.crop((w+2,38,2*w+2,38+h)).tobytes()==b.tobytes()
 meta[rel]=dict(width=result.width,height=result.height,top=38,bottom=0,gutter=2,leftLabel=label,rightLabel='Experimental result')
 receipts.append(dict(asset=rel,source=str(src.relative_to(ROOT)),sha256=hashlib.sha256((guide/rel).read_bytes()).hexdigest(),native_panels_exact=True))
 return f'![{tag}](assets/feedback98-{tag}.png)\n'
cases=[f'{m}-{r}' for m in ['expanded','compact'] for r in ['a','b']]
page='''# Miniplayer feedback: inward joins, edge color and broad shadow

The new shared shape moves top joins down and bottom joins up, while keeping the outer tips fixed. Near-tip refraction becomes stronger. The final combination remains experimental: boundary, foreground and other local failures prevent family acceptance. The selected reconstruction is unchanged.

Drag each divider across identical native coordinates. Fullscreen, keyboard, touch and side-by-side views are available. The first group shows the complete proposal; isolated tests and native edge close-ups follow.

[Full report](../research/experiments/miniplayer-stronger-joins-98/README.md) · [Previous refinement](miniplayer-refinement.md) · [Selected models](reconstruction.md)

## Complete experimental result

The common model uses stronger inward join smoothing, ten-percent less incident blur, a broad exterior-only shadow and a finite color filter. Black reaches light gray at maximum filter strength; nonwhite inputs remain below white. Compact and expanded still differ only by major length.

| Reference | Original E | Final E | Original boundary RMSE → final |
| --- | ---: | ---: | ---: |
| Expanded A | 7.8835 | 11.1280 | 40.3268 → 78.4099 |
| Expanded B | 6.1494 | 5.6279 | 26.0804 → 50.9031 |
| Compact A | 20.5319 | 16.0236 | 23.8132 → 40.2864 |
| Compact B | 19.6819 | 16.7582 | 21.0766 → 39.8497 |

All four original partial-boundary guards fail. Aggregate improvements do not override those failures. The final images retain incorrect returned-feature placement and compact tone differences.

'''
for c in cases:page+=f'### {c.replace("-"," ").title()}\n\n'+pair(c+'-final',OUT/'display'/f'{c}-final-comparison.png')+'\n'
page+='<details id="starting-comparison">\n<summary>Previous published refinement versus this result</summary>\n\n'
for c in cases:page+=pair(c+'-previous',OUT/'display'/f'{c}-final-comparison.png',old=EXP/'miniplayer-complete-refinement-94/highlight'/f'{c}-combined-comparison.png',label='Previous refinement')+'\n'
page+='</details>\n\n## Native edge close-ups\n\nThese crops preserve native pixels without smoothing. Use fullscreen to inspect the cap joins and upper colored edge. The filter preserves yellow rather than replacing it with white, but the correct strength and source-feature placement remain unresolved.\n\n'
for c in cases:
 for side in ['left','right']:
  w=1360 if c.startswith('expanded') else 920
  box=(0,14,260,150) if side=='left' else (w-260,14,w,150)
  page+=pair(c+'-'+side+'-detail',OUT/'display'/f'{c}-final-comparison.png',box=box)+'\n'
page+='''## Shadow measurements

Fixed source/reference patches show darkening extending tens of pixels beyond the pill. Top-center residuals approach the measured far-background level around 45–55 pixels, rather than the previous four-pixel shadow width. The conditional mosaic is not a pristine before-image; these measurements do not uniquely identify a physical shadow.

| Reference | Darkening at 4 px | 16 px | 32 px | 64 px |
| --- | ---: | ---: | ---: | ---: |
| Expanded A | 15.55 | 8.92 | 4.07 | 0.07 |
| Expanded B | 19.06 | 12.06 | 6.71 | -0.07 |
| Compact A | 7.65 | 5.80 | 3.57 | -0.57 |
| Compact B | 21.57 | 15.00 | 10.00 | 1.00 |

Values are encoded luminance levels on a 255-level scale. Negative values and far-field confounds remain in the [measurement record](../research/experiments/miniplayer-feedback-diagnostics-95/README.md). Bottom profiles can cross unrelated interface content; they are not evidence of a growing shadow.

## Separate tests

Less blur sharpens texture but worsens aggregate error on all four fixed-geometry references. The stronger joins are a single geometric hypothesis, not a fitted silhouette. The compact interior is approximately 12–14 luminance levels too dark in the preceding model, while expanded means are nearly correct. A global exposure increase cannot resolve that discrepancy safely.

'''
stages=[('geometry','Stronger joins and less blur, before new edge/shadow',OUT/'native','geometry'),('blur','Less blur on the previous geometry',EXP/'miniplayer-subtle-blur-97','blur-only'),('filter','Light-gray edge response with broad shadow',EXP/'miniplayer-subtle-blur-97','filter-revision'),('combination','Previous geometry with all new material stages',EXP/'miniplayer-subtle-blur-97','combined')]
for name,title,folder,suffix in stages:
 page+=f'<details data-stage="{name}">\n<summary>{title}</summary>\n\n'
 for c in cases:
  src=folder/f'{c}-{suffix}-comparison.png'
  if not src.exists():src=folder/f'{c}-comparison.png'
  page+=pair(c+'-'+name,src)+'\n'
 page+='</details>\n\n'
page+='[Finite filter and broad-shadow trials](../research/experiments/miniplayer-edge-filter-96/README.md) · [Blur and revised filter evidence](../research/experiments/miniplayer-subtle-blur-97/README.md)\n'
(guide/'miniplayer-feedback-review.md').write_text(page)
(guide/'feedback-comparison-panels.json').write_text(json.dumps(meta,indent=2)+'\n')
(OUT/'publication-panels.json').write_text(json.dumps(dict(decoded_bitmap_pixels=decoded,cap=80000000,scientific_evaluations=0,panels=receipts),indent=2)+'\n')
print('Published',len(meta),'exact pairs;',decoded,'decoded pixels')
