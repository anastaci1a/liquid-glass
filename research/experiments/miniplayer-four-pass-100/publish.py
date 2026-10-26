"""Exact saved comparison crops only; no scientific evaluations."""
from pathlib import Path
from PIL import Image,ImageDraw
import json,hashlib,sys
ROOT=Path('/repo');OUT=Path(__file__).parent;guide=ROOT/'guide';meta={};receipts=[];decoded=0
CAP=500000000

def read(p):
 global decoded
 im=Image.open(p);assert decoded+im.width*im.height<=CAP;decoded+=im.width*im.height;return im.convert('RGB')
def pair(tag,src,old=None,box=None,label='Apple reference'):
 im=read(src);w=(im.width-4)//3;h=im.height-38
 a=im.crop((0,38,w,h+38));b=im.crop((2*(w+2),38,2*(w+2)+w,h+38))
 if old:
  oi=read(old);assert oi.size==im.size;a=oi.crop((2*(w+2),38,2*(w+2)+w,h+38))
 if box:a=a.crop(box);b=b.crop(box)
 w,h=a.size;result=Image.new('RGB',(2*w+2,h+38),'white');result.paste(a,(0,38));result.paste(b,(w+2,38));ImageDraw.Draw(result).text((4,10),label,fill='black');ImageDraw.Draw(result).text((w+6,10),'Pass result',fill='black')
 rel=f'assets/four100-{tag}.png';result.save(guide/rel)
 assert result.crop((0,38,w,h+38)).tobytes()==a.tobytes() and result.crop((w+2,38,2*w+2,h+38)).tobytes()==b.tobytes()
 meta[rel]=dict(width=result.width,height=result.height,top=38,bottom=0,gutter=2,leftLabel=label,rightLabel='Pass result')
 receipts.append(dict(asset=rel,source=str(src.relative_to(ROOT)),sha256=hashlib.sha256((guide/rel).read_bytes()).hexdigest(),native_pixels_exact=True))
 return f'![{tag}]({rel})\n'
folders=[OUT/f'pass{i}' for i in range(1,5) if (OUT/f'pass{i}/verification.json').exists()]
assert folders,'Only verified completed passes may be published'
page='''# Miniplayer: four complete refinement passes

This review follows the shared compact and expanded model through contour, refraction, incident blur, color, outline, exterior shadow and artwork. Dispersion is excluded. Each completed pass retains its original failures and local tradeoffs.

Drag the mask to compare identical native coordinates. Fullscreen, keyboard, touch and side-by-side controls are available. Native detail crops preserve source pixels without smoothing or alignment changes.

[Research plan](../research/experiments/miniplayer-four-pass-100/README.md) · [Feedback](../research/feedback/miniplayer-four-pass.md) · [Previous proposal](miniplayer-middle-ground.md) · [Current models](reconstruction.md)

'''
page+=f'Completed and independently replayed: **{len(folders)} of four passes**. Numerical ranking and visual selection are separate; the original strict local guards remain reported.\n\n'
if (OUT/'selection.json').exists():
 selection=json.loads((OUT/'selection.json').read_text())
 page+=f"**Final working choice: pass {selection['selected_pass']}.** All four passes are retained below. The combined category score improves about 8.7% against the starting proposal, mainly through artwork, compact tone and shadow. Average glass error is nearly unchanged; average rim error is worse. Expanded and partial-boundary regressions remain. [Full decision](../research/experiments/miniplayer-four-pass-100/FINAL-REVIEW.md).\n\n"
cases=[f'{m}-{r}' for m in ['expanded','compact'] for r in ['a','b']]
for folder in folders:
 number=folder.name[4:];result=json.loads((folder/'result.json').read_text());recipe=json.loads((folder/'final-recipe.json').read_text())
 page+=f'## Pass {number}\n\n'
 review=folder/'public-summary.md'
 page+=review.read_text()+'\n' if review.exists() else 'The integrated candidate is verified; visual selection remains pending.\n\n'
 page+='| Reference | E | SSIM | Original partial RMSE | Normalized combined score |\n| --- | ---: | ---: | ---: | ---: |\n'
 for r in result['records']:
  s=r['scores'];page+=f"| {r['member']} {r['reference'].upper()} | {s['E']:.4f} | {s['ssim']:.5f} | {s['partial']['RMSE']:.4f} | {r['combined']:.4f} |\n"
 page+='\nCombined score equally weights baseline-normalized glass, rim, exterior and artwork errors across references. Lower than one improves this numerical ranking. It is not a physical-material identification or a replacement for visual review.\n\n'
 for case in cases:page+=f'### {case.replace("-"," ").title()}\n\n'+pair(f'p{number}-{case}',folder/f'{case}-final-comparison.png')+'\n'
 page+=f'<details id="pass{number}-previous" data-stage="pass{number}-previous">\n<summary>Previous result versus pass {number}</summary>\n\n'
 for case in cases:
  old=(OUT.parent/'miniplayer-middle-ground-99/peak-brightness'/f'{case}-floor0.24-comparison.png') if number=='1' else OUT/f'pass{int(number)-1}'/f'{case}-final-comparison.png'
  page+=pair(f'p{number}-{case}-previous',folder/f'{case}-final-comparison.png',old=old,label='Previous result')+'\n'
 page+='</details>\n\n'
 page+=f'<details data-stage="pass{number}-details">\n<summary>Native cap, rim and artwork details</summary>\n\n'
 for case in cases:
  w=1360 if case.startswith('expanded') else 920
  for side in ['left','right']:
   box=(0,14,260,240) if side=='left' else (w-260,14,w,240)
   page+=pair(f'p{number}-{case}-{side}',folder/f'{case}-final-comparison.png',box=box)+'\n'
 for case in ['expanded-a','expanded-b']:
  page+=pair(f'p{number}-{case}-yellow',folder/f'{case}-final-comparison.png',box=(760,16,1200,65))+'\n'
 page+='</details>\n\n'
 page+=f"Recipe: incident sigma `{recipe['sigma']}`; rim plateau `{recipe['outline']['plateau']}` pixels and fade `{recipe['outline']['fade']}` pixels; artwork scale `{recipe['artwork']['scale']}`. [Exact results and stage choices](../research/experiments/miniplayer-four-pass-100/{folder.name}/README.md).\n\n"
page+='''## Interpretation

Artwork uses the original asset with a shared centered scale, upward offset and absolute corner radius. Its score includes the exposed backing in the unchanged original guard box. It does not improve the glass score by changing that mask.

The outline uses incident-blurred refraction before the body grade. Chroma and peak strength remain distinct. Shadow darkens only uncovered contributions; it is excluded from lens transport. Shared optical parameters still differ only by member length.

All source mosaics are conditional evidence. Reflected scene assumptions and unassigned later power remain unresolved. A better appearance does not uniquely identify the original renderer.
'''
(guide/'miniplayer-four-pass.md').write_text(page);(guide/'four-pass-comparison-panels.json').write_text(json.dumps(meta,indent=2)+'\n');(OUT/'publication-panels.json').write_text(json.dumps(dict(passes=len(folders),decoded_bitmap_pixels=decoded,cap=CAP,scientific_evaluations=0,panels=receipts),indent=2)+'\n');print('EXACT PAIRS',len(meta),'decoded',decoded)
