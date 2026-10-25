"""Publish exact saved comparison panels, never rerender scientific candidates."""
from pathlib import Path
import json,hashlib
from PIL import Image,ImageDraw,ImageFont
ROOT=Path(__file__).resolve().parents[3];SERIES=Path(__file__).parent
GUIDE=ROOT/'guide';ASSETS=GUIDE/'assets';font=ImageFont.load_default(size=16)
metadata={};bindings=[];passes=[]
for number in range(1,6):
    p=SERIES/f'pass-{number:02d}'
    passes.append((p,json.loads((p/'protocol.json').read_text()),json.loads((p/'result.json').read_text()),json.loads((p/'fits.json').read_text())))

def pair(p,member,k,j,mode='reference'):
    cached=f'assets/outline91-{p.name}-{member}-{k}-c{j}-{mode}.png'
    if cached in metadata:return cached
    source=p/f'{member}-{k}-c{j}-comparison.png';im=Image.open(source).convert('RGB')
    W=(im.width-4)//3;H=im.height-38;assert im.width==3*W+4
    leftx=0 if mode=='reference' else W+2
    left=im.crop((leftx,38,leftx+W,38+H));right=im.crop((2*W+4,38,3*W+4,38+H))
    name=f'outline91-{p.name}-{member}-{k}-c{j}-{mode}.png';dest=ASSETS/name
    out=Image.new('RGB',(2*W+2,H+38),'white');out.paste(left,(0,38));out.paste(right,(W+2,38))
    label='Apple reference' if mode=='reference' else 'Starting model'
    draw=ImageDraw.Draw(out);draw.text((5,8),label,font=font,fill='black');draw.text((W+7,8),'Proposed outline — not adopted',font=font,fill='black');out.save(dest)
    # Exact byte comparison of the two saved panel crops, no resampling.
    assert out.crop((0,38,W,H+38)).tobytes()==left.tobytes()
    assert out.crop((W+2,38,2*W+2,H+38)).tobytes()==right.tobytes()
    rel='assets/'+name;metadata[rel]=dict(width=out.width,height=out.height,top=38,bottom=0,gutter=2,leftLabel=label,rightLabel='Outline proposal')
    bindings.append(dict(asset=rel,sha256=hashlib.sha256(dest.read_bytes()).hexdigest(),source=str(source.relative_to(ROOT)),source_sha256=hashlib.sha256(source.read_bytes()).hexdigest(),left_panel='reference' if mode=='reference' else 'frozen working20',right_panel='candidate',native_panel_pixels_exact=True))
    return rel

selection=json.loads((SERIES/'selection.json').read_text());dev=selection['development'];dp=SERIES/dev['folder'];dj=dev['candidate']
lines=['# Miniplayer outline: five-pass comparison','',
'Five outline passes are complete. **No candidate passed every original family guard**, so the starting model remains the incumbent. The proposals below show useful local changes and their regressions, rather than an accepted replacement.','',
'**Drag the divider** to compare aligned pixels. Use **Side by side** or **Fullscreen** for a larger view. The handle also supports touch, arrow keys, Home and End. Reference and result have identical native crop coordinates; no image alignment was changed for presentation.','',
'Compact and expanded use one outline law. Refraction, source blur, foreground and original masks stayed fixed. The sizing audit found no coherent correction supported across the references; local edge placement remains uncertain by roughly one to two pixels.','',
'[Registration audit](../research/experiments/agent-miniplayer-registration-54/README.md) · [Full study and method](../research/experiments/miniplayer-outline-series-91/README.md)','',
'## Final development proposal','',
f"This is {dev['folder']} setting {dj}, the lowest shared training-loss proposal carried forward. It is **not accepted**. These first sliders compare the Apple reference with that proposal; the next group isolates the change from the starting model.",'']
dev_rows=[x for x in json.loads((dp/'result.json').read_text())['records'] if x['candidate']==dj]
lines+=['| Reference | Starting body E | Proposal E | Original boundary RMSE: start → proposal |','| --- | ---: | ---: | ---: |']
for x in dev_rows:
 lines.append(f"| {x['member'].title()} {x['reference'].upper()} | {x['baseline']['E']:.4f} | {x['scores']['E']:.4f} | {x['baseline']['partial']['RMSE']:.4f} → {x['scores']['partial']['RMSE']:.4f} |")
lines+=['','For a more color-preserving tradeoff, open [pass 5, setting 0](#pass-5-setting-0). It improves both compact partial-edge scores but still fails expanded A and compact exterior checks.','']
for m in ['expanded','compact']:
 for k in ['a','b']:
    asset=pair(dp,m,k,dj);lines += [f'### {m.title()} {k.upper()}', '',f'![Apple reference versus final {m} {k.upper()} outline proposal]({asset})','']
lines+=['<details>','<summary>Starting model versus final proposal</summary>','']
for m in ['expanded','compact']:
 for k in ['a','b']:
    asset=pair(dp,m,k,dj,'starting');lines += [f'![Starting model versus final {m} {k.upper()} outline proposal]({asset})','']
lines+=['</details>','','## All five passes','','Each pass includes every tested setting and all four references. The incumbent is retained whenever any original guard fails. The training-selected proposal can change independently, so its images are labeled proposals throughout.','']
for p,proto,r,fits in passes:
 n=proto['number'];lines += [f'<details data-pass="{n}" id="pass-{n}">',f'<summary>Pass {n}: {proto["question"]} — incumbent retained</summary>','',f'[Full record, fixed crops and all original guards](../research/experiments/miniplayer-outline-series-91/{p.name}/README.md)','', '| Setting | Response | Width (px) | Strength | Expanded A / B E | Compact A / B E |','| --- | --- | ---: | ---: | --- | --- |']
 for f in fits:
    j=f['candidate'];rows=[x for x in r['records'] if x['candidate']==j];E=[x['scores']['E'] for x in rows]
    lines.append(f"| {j} | {(f['config']['response']+(' / '+str(round(100*f['config']['white_mix']))+'% white' if 'white_mix' in f['config'] else ''))} | {f['config']['sigma']:.3f} | {f['strength']:.4f} | {E[0]:.4f} / {E[1]:.4f} | {E[2]:.4f} / {E[3]:.4f} |")
 lines+=['']
 for f in fits:
    j=f['candidate'];lines += [f'<details id="pass-{n}-setting-{j}">',f'<summary>Setting {j}: four reference/result sliders</summary>','']
    for m in ['expanded','compact']:
     for k in ['a','b']:
      asset=pair(p,m,k,j);row=next(x for x in r['records'] if x['candidate']==j and x['member']==m and x['reference']==k)
      fail=', '.join(key for key,v in row['original_guards'].items() if not v) or 'none'
      lines += [f'**{m.title()} {k.upper()}.** Failed original guards: {fail}.','',f'![Pass {n} setting {j}: {m} {k.upper()} reference and outline proposal]({asset})','']
    lines+=['</details>','']
 lines+=['</details>','']
lines+=['## What to inspect','','Compare the width of the inward fade, the right upper-cap weakening and the rotated left lower-cap weakening. Check whether the color-preserving alternatives retain useful color or appear too saturated. Please identify the member, reference and setting when giving feedback.','',
'The strongest unresolved conflict is expanded A: brighter wide outlines worsen its original body and partial-edge errors. Compact and expanded B can improve while that reference regresses. Original boundary and exterior failures are retained, even when the aggregate score is lower.','',
'These are display-effect hypotheses, not a reconstruction of an undocumented radiance slider or proof of Apple’s shader. Existing body/source-return defects and registration uncertainty remain visible.','']
(GUIDE/'outline-review.md').write_text('\n'.join(lines))
(GUIDE/'outline-comparison-panels.json').write_text(json.dumps(metadata,indent=2)+'\n')
(SERIES/'presentation-bindings.json').write_text(json.dumps(dict(assets=bindings,no_resampling=True,no_scientific_rerender=True,unique_assets=len(metadata)),indent=2)+'\n')
print('Published',len(metadata),'unique exact-panel pairs')
