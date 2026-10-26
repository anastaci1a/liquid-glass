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
    path=f'assets/hsv102-{name}.png';im.save(G/path);metadata[path]=dict(width=im.width,height=im.height,top=38,bottom=0,gutter=2,leftLabel=label,rightLabel=right);receipts.append(dict(asset=path,sha256=hashlib.sha256((G/path).read_bytes()).hexdigest(),native_pixels_exact=True))
    return f'![{name}]({path})\n\n'
page='''# Miniplayer HSV outline options

Five options share the finalized pill geometry, incident blur, optical paths, shadow and artwork. Only outline saturation differs: 60%, 70%, 80%, 90% or 100% of the blurred preimage saturation. No option has been selected.

Jump to [60%](#60-preimage-saturation), [70%](#70-preimage-saturation), [80%](#80-preimage-saturation), [90%](#90-preimage-saturation) or [100%](#100-preimage-saturation).

At maximum filter strength, hue is preserved and HSV value is 253 out of 255. White becomes #FDFDFD. The maximum-strength plateau is one native pixel, 1.5 times its previous thickness. The two-pixel inward fade and opposing diagonal gaps remain unchanged.

The body grade also maps white to #FDFDFD before optical transmission and reflected light. Final body pixels need not equal that value. The saved white-patch measurements distinguish these stages. Display clipping, if present, is reported explicitly.

Drag each divider for Apple/result or current/result comparisons. Fullscreen exposes native pixels; detail crops preserve identical coordinates without realignment. All saturation options use the same shape even where the reference contour differs.

[Research and white patches](../research/experiments/miniplayer-hsv-options-102/README.md) · [Previous three passes](miniplayer-three-pass.md) · [Selected reconstruction](reconstruction.md)

'''
cases={}
page+='## Compact white checks\n\n'
band=json.loads((B/'white-band.json').read_text())['records']
page+='The strict exact-white cohort is empty. Fixed samples through the visible compact white stripe show the remaining issue: Apple is about 252–253, while this test body is about 240–243 after optical attenuation. The grade endpoint passes, but final body white is still too dark.\n\n'
page+='| Reference / crop-local pixel | Blurred preimage | Apple | Current output | New body |\n| --- | --- | --- | --- | --- |\n'
for x in band:
    def rgb(v):return '#'+''.join(f'{min(255,max(0,round(c))):02X}' for c in v)
    page+=f"| {x['case']} ({x['local_x']}, {x['local_y']}) | {rgb(x['blurred_preimage'])} | {rgb(x['target'])} | {rgb(x['previous'])} | {rgb(x['new_body'])} |\n"
page+='\n'
for m in ['expanded','compact']:
    for r in ['a','b']:
        k=f'{m}-{r}';cases[k]=(open_image(B/f'{k}-reference.png'),open_image(B/f'{k}-previous.png'))
for fraction in [.6,.7,.8,.9,1.]:
    percent=round(100*fraction);page+=f'## {percent}% preimage saturation\n\n'
    page+='| Reference | E | SSIM | Original partial RMSE | Clipped body channels before display |\n| --- | ---: | ---: | ---: | ---: |\n'
    for row in rows:
        if row['saturation_fraction']==fraction:
            s=row['scores'];page+=f"| {row['member']} {row['reference'].upper()} | {s['E']:.4f} | {s['ssim']:.5f} | {s['partial']['RMSE']:.4f} | {row['preclip_channels']} |\n"
    page+='\nScores are diagnostic. The finalized geometry is not retuned to improve outline scores.\n\n'
    for case,(reference,previous) in cases.items():
        result=open_image(B/f'{case}-s{percent}.png');w,h=result.size;label=f'S{percent} · HSV value 253'
        page+=f'### {case.replace("-"," ").title()} — {percent}%\n\n'+pair(reference,result,f'{case}-s{percent}',right=label)
        page+=f'<details data-hsv="{case}-s{percent}-previous"><summary>Current model versus this option</summary>\n\n'+pair(previous,result,f'{case}-s{percent}-previous',label='Current selected',right=label)+'</details>\n\n'
        page+=f'<details data-hsv="{case}-s{percent}-details"><summary>Native zooms: caps, upper/lower rim and disappearing diagonals</summary>\n\n'
        crops={'left-cap':(0,0,260,h),'right-cap':(w-260,0,w,h),'upper-rim':(w//2,12,w-180,75),'lower-rim':(w//2,h-85,w-180,h-20),'upper-right-gap':(w-180,0,w,125),'lower-left-gap':(0,h-125,180,h)}
        if case.startswith('compact'):crops['white-content']=(w//2-40,10,w-100,h-20)
        for name,box in crops.items():page+=pair(reference,result,f'{case}-s{percent}-{name}',right=label,box=box)
        page+='</details>\n\n'
page+='''## Reading the comparisons

Equal HSV value is not equal luminance. A saturated yellow and white can share the same largest RGB channel while having different measured lightness. Saturation percentages are relative to each blurred preimage color, not absolute saturation settings.

Pixel coverage and angular fading blend the endpoint with the completed body. A boundary pixel therefore need not reach value 253. The right upper-right and left lower-left gaps retain zero overlay contribution; existing refracted brightness remains visible.

The source mosaics and reflected scene remain conditional. These are display options for visual review, not physical identification or full-fidelity acceptance.
'''
(G/'miniplayer-hsv-options.md').write_text(page);(G/'hsv-comparison-panels.json').write_text(json.dumps(metadata,indent=2)+'\n');(B/'publication.json').write_text(json.dumps(dict(decoded_pixels=decoded,cap=cap,panels=receipts),indent=2)+'\n');print('PUBLISHED',len(metadata),'pairs;',decoded,'decoded pixels')
