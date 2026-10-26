"""Exact saved-pixel review pairs; no scientific rerender or resizing."""
from pathlib import Path
import json,hashlib
from PIL import Image,ImageDraw,ImageFont
ROOT=Path(__file__).resolve().parents[3];BASE=Path(__file__).parent;GUIDE=ROOT/'guide';font=ImageFont.load_default(size=16);cache={};metadata={};bindings=[];decode=0
high=json.loads((BASE/'highlight/result.json').read_text());shadow=json.loads((BASE/'shadow/result.json').read_text());geo=json.loads((BASE/'geometry-run-02/geometry-result.json').read_text())
def pair(folder,prefix,mode):
 global decode
 p=BASE/folder/f'{prefix}-comparison.png'
 if p not in cache:
  im=Image.open(p);decode+=im.width*im.height;assert decode<40000000;cache[p]=im.convert('RGB')
 im=cache[p];W=(im.width-4)//3;H=im.height-38;leftx=0 if mode=='reference' else W+2;left=im.crop((leftx,38,leftx+W,H+38));right=im.crop((2*W+4,38,3*W+4,H+38));out=Image.new('RGB',(2*W+2,H+38),'white');out.paste(left,(0,38));out.paste(right,(W+2,38));label='Apple reference' if mode=='reference' else 'Starting model';draw=ImageDraw.Draw(out);draw.text((5,8),label,font=font,fill='black');draw.text((W+7,8),'Experimental result — not adopted',font=font,fill='black');name=f'assets/refinement94-{prefix}-{mode}.png';dest=GUIDE/name;out.save(dest)
 assert out.crop((0,38,W,H+38)).tobytes()==left.tobytes();assert out.crop((W+2,38,2*W+2,H+38)).tobytes()==right.tobytes()
 metadata[name]=dict(width=out.width,height=out.height,top=38,bottom=0,gutter=2,leftLabel=label,rightLabel='Experimental result');bindings.append(dict(asset=name,sha256=hashlib.sha256(dest.read_bytes()).hexdigest(),source=str(p.relative_to(ROOT)),source_sha256=hashlib.sha256(p.read_bytes()).hexdigest(),native_panel_bytes_exact=True));return name
lines=['# Miniplayer: smooth shape, shadow and color-aware rim','','The complete refinement sequence is finished and independently replayed by the primary researcher. The combined proposal makes the compact rim clearer and keeps edge color, but expanded A becomes too bright. **No proposal passes every original family guard.** The selected model remains unchanged.','','Drag the divider to compare identical native coordinates. Touch, keyboard arrows, side-by-side mode and fullscreen are available. The first comparisons show the final experimental combination; every separate stage and tested setting follows.','','[Full report and verification](../research/experiments/miniplayer-complete-refinement-94/README.md) · [Previous five outline passes](outline-review.md) · [Selected reconstructions](reconstruction.md)','','## Combined development result','','The shared contour has smooth curvature and slightly convex long sides. The exterior-only shadow uses strength 0.1. The color-aware inner fade uses width 2.6 pixels and a bounded lift with gentle desaturation. Compact and expanded differ only in major length.','','| Reference | Starting E | Combined E | Frozen boundary RMSE: start → combined |','| --- | ---: | ---: | ---: |']
for row in high['combined']:
 old=next(r['baseline'] for r in geo['records'] if (r['member'],r['reference'])==(row['member'],row['reference']));lines.append(f"| {row['member'].title()} {row['reference'].upper()} | {old['E']:.4f} | {row['scores']['E']:.4f} | {old['partial']['RMSE']:.4f} → {row['scores']['partial']['RMSE']:.4f} |")
lines+=['','Lower errors are better. Improvements in one reference do not waive another reference’s failure.','']
for mode in ['reference','starting']:
 if mode=='starting':lines+=['<details id="starting-comparison">','<summary>Starting model versus combined result</summary>','']
 for m in ['expanded','compact']:
  for k in ['a','b']:
   asset=pair('highlight',f'{m}-{k}-combined',mode);lines += [f'### {m.title()} {k.upper()}' if mode=='reference' else f'**{m.title()} {k.upper()}.**','',f'![{m} {k.upper()}: {mode} versus combined result]({asset})','']
 if mode=='starting':lines+=['</details>','']
lines+=['## Separate stages and every setting','','Each group includes the Apple reference and the starting-model comparison. Shadow and highlight proposals use the new smooth geometry, so they are not isolated changes to the old body. Their separate component-relative guards are retained in the linked reports.','']
stages=[('geometry','Smooth geometry only','geometry-run-02',[('geometry',geo['records'])]),('shadow','Exterior-only shadow','shadow',[(f's{v}',[r for r in shadow['records'] if r['strength']==v]) for v in [.025,.05,.1]]),('highlight','Color-aware highlight','highlight',[(f'h{j}',[r for r in high['records'] if r['candidate']==j]) for j in range(3)])]
for ident,title,folder,settings in stages:
 lines += [f'<details data-stage="{ident}" id="stage-{ident}">',f'<summary>{title}</summary>','',f'[Method, limits and original guards](../research/experiments/miniplayer-complete-refinement-94/{folder}/README.md)','']
 for setting,rows in settings:
  lines += [f'<details id="setting-{setting}">',f'<summary>Setting {setting}: all four references</summary>','']
  for row in rows:
   m,k=row['member'],row['reference'];failed=', '.join(n for n,v in row.get('original_guards',row.get('guards',{})).items() if not v);lines += [f'**{m.title()} {k.upper()}.** E: {row["scores"]["E"]:.4f}. Failed original guards: {failed or "none"}.','']
   for mode in ['reference','starting']:
    asset=pair(folder,f'{m}-{k}-{setting}',mode);lines += [f'![{m} {k.upper()} {setting}: {mode} comparison]({asset})','']
  lines += ['</details>','']
 lines += ['</details>','']
lines += ['## What remains wrong','','Expanded A’s left and lower edge becomes too bright. Compact returns, especially the left cap and upper lettering, remain misplaced. The new outline does not repair those source-feature errors. Its nominal width and angular fade remain hypotheses, not measured shader parameters.','','The shadow improves separation from bright exterior backgrounds, but neither the shadow alone nor the full combination passes every original guard. The contour keeps the measured extrema; it is not an accepted pose or size correction.','','All four baseline images reproduce exactly. Twenty-eight material candidates replay within one float32 rounding step, and every stored score and guard reproduces exactly. Positive-area checks and two-order outline integration pass. These checks establish implementation consistency, not Apple fidelity or a uniquely identified material.','']
(GUIDE/'miniplayer-refinement.md').write_text('\n'.join(lines));(GUIDE/'refinement-comparison-panels.json').write_text(json.dumps(metadata,indent=2)+'\n');(BASE/'presentation-bindings.json').write_text(json.dumps(dict(decoded_source_panel_pixels=decode,unique_source_panels=len(cache),unique_pair_assets=len(metadata),assets=bindings,no_resampling=True),indent=2)+'\n');print('PRESENTATION',len(metadata),decode)
