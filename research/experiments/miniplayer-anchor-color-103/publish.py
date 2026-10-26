"""Exact native crops and interactive comparisons; no scientific rerender."""
from pathlib import Path
import json,hashlib
from PIL import Image,ImageDraw
B=Path(__file__).resolve().parent;R=B.parents[2];G=R/'guide';assert (B/'finished.json').exists()
rows=json.loads((B/'results.json').read_text());metadata={};receipts=[];decoded=0;cap=100_000_000
def open_image(p):
    global decoded
    im=Image.open(p);decoded+=im.width*im.height;assert decoded<=cap;return im.convert('RGB')
def pair(a,b,name,label='Apple reference',right='Candidate',box=None):
    if box:a=a.crop(box);b=b.crop(box)
    assert a.size==b.size
    w,h=a.size;im=Image.new('RGB',(2*w+2,h+38),'white');im.paste(a,(0,38));im.paste(b,(w+2,38));draw=ImageDraw.Draw(im);draw.text((4,10),label,fill='black');draw.text((w+6,10),right,fill='black')
    assert im.crop((0,38,w,h+38)).tobytes()==a.tobytes() and im.crop((w+2,38,2*w+2,h+38)).tobytes()==b.tobytes()
    path=f'assets/anchor103-{name}.png';im.save(G/path);metadata[path]=dict(width=im.width,height=im.height,top=38,bottom=0,gutter=2,leftLabel=label,rightLabel=right);receipts.append(dict(asset=path,sha256=hashlib.sha256((G/path).read_bytes()).hexdigest(),native_pixels_exact=True))
    return f'![{name}]({path})\n\n'
page="""# Calibrated miniplayer colors

One candidate uses your new body and outline color anchors. Geometry, blur, shadow, artwork and the opposing diagonal outline gaps are fixed. This is held for review; the selected reconstruction is unchanged.

The body and outline map the blurred, refracted preimage directly into final display colors. Old body grading, transmission darkening and hypothetical reflected-light brightness are replaced in this candidate. Geometric displacement is unchanged. No new optical calculation or source filtering ran.

Expanded defines the shared color target. Compact uses precisely the same mapping; its color regressions are diagnostic, not a veto. The outline retains a one-pixel maximum-strength plateau and two-pixel inward fade.

Drag each divider, open the native detail crops, or use fullscreen. Coordinates are unchanged; there is no alignment correction.

[Research and verification](../research/experiments/miniplayer-anchor-color-103/README.md) · [Selected reconstruction](reconstruction.md)

## Color anchors

Saturation and HSV value match every requested anchor to numerical precision. Input hue is preserved. Consequently the yellow outline becomes #FEEB85 rather than #FEF985: its green channel differs by about 14 levels. The swatches expose this deliberate hue-preservation tradeoff.

| Role | Preimage | Requested | Hue-preserved result |
| --- | --- | --- | --- |
"""
anchors=json.loads((B/'calibration-checkpoint.json').read_text())['anchors']
svg=['<svg xmlns="http://www.w3.org/2000/svg" width="900" height="410" viewBox="0 0 900 410"><rect width="900" height="410" fill="white"/>']
for i,a in enumerate(anchors):
    page+=f"| {a['role']} | #{a['input']} | #{a['target']} | #{a['hue_preserved_output']} |\n"
    y=10+i*50
    svg.append(f'<text x="5" y="{y+25}" font-family="sans-serif" font-size="16">{a["role"]}</text>')
    for j,(label,key) in enumerate([('Input','input'),('Target','target'),('Result','hue_preserved_output')]):
        x=90+j*265;v=a[key];svg.append(f'<rect x="{x}" y="{y}" width="110" height="40" fill="#{v}" stroke="#777"/><text x="{x+115}" y="{y+25}" font-family="sans-serif" font-size="14">{label} #{v}</text>')
svg.append('</svg>');(G/'assets/anchor103-swatches.svg').write_text(''.join(svg))
page+='\n![Input, requested and hue-preserved color swatches](assets/anchor103-swatches.svg)\n\nWhite maps to #E5E5E5 in the body and #FCFCFC at full outline strength. Coverage, fade and angular gaps blend the outline endpoint with the body. This intentionally darkens compact white content relative to its reference.\n\n## Image comparisons\n\n| Case | Selected E | Candidate E | SSIM | Partial RMSE |\n| --- | ---: | ---: | ---: | ---: |\n'
for row,base in zip(rows,[10.2238849,5.0735640,14.8296018,14.4726862]):
    s=row['scores'];page+=f"| {row['member']} {row['reference'].upper()} | {base:.4f} | {s['E']:.4f} | {s['ssim']:.5f} | {s['partial']['RMSE']:.4f} |\n"
page+='\nAggregate error increases on all four references. Anchor calibration is successful, but it does not establish image fidelity. There is no clipping. All original guards and local failures remain in the research record.\n\n'
for row in rows:
    case=f"{row['member']}-{row['reference']}";reference=open_image(B/f'{case}-reference.png');previous=open_image(B/f'{case}-previous.png');result=open_image(B/f'{case}-candidate.png');w,h=result.size
    page+=f'### {case.replace("-"," ").title()}\n\n'+pair(reference,result,case,right='Calibrated candidate')
    page+=f'<details data-hsv="{case}-previous"><summary>Selected model versus candidate</summary>\n\n'+pair(previous,result,case+'-previous',label='Current selected',right='Calibrated candidate')+'</details>\n\n'
    page+=f'<details data-hsv="{case}-details"><summary>Native crops: colored rims, caps and disappearing diagonals</summary>\n\n'
    crops={'left-cap':(0,0,260,h),'right-cap':(w-260,0,w,h),'upper-rim':(w//2,12,w-180,75),'lower-rim':(w//2,h-85,w-180,h-20),'upper-right-gap':(w-180,0,w,125),'lower-left-gap':(0,h-125,180,h)}
    if case.startswith('compact'):crops['white-content']=(w//2-40,10,w-100,h-20)
    else:crops['brown-content']=(260,12,620,90)
    for name,box in crops.items():page+=pair(reference,result,case+'-'+name,right='Calibrated candidate',box=box)
    page+='</details>\n\n'
page+='## Limits\n\nFour warm-color anchors do not identify a unique global filter. The response uses smooth bounded interpolation, retains the prior neutral black behavior, and extrapolates the colored coefficients constantly beyond their sampled value range. Blue and other unsampled colors remain predictions. These are empirical display mappings, not measured physical radiance.\n'
(G/'miniplayer-anchor-colors.md').write_text(page);(G/'anchor-color-comparison-panels.json').write_text(json.dumps(metadata,indent=2)+'\n');(B/'publication.json').write_text(json.dumps(dict(decoded_pixels=decoded,panels=receipts),indent=2)+'\n');print('PUBLISHED',len(metadata))
