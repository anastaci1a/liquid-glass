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
    path=f'assets/taper107-{name}.png';im.save(G/path);metadata[path]=dict(width=im.width,height=im.height,top=38,bottom=0,gutter=2,leftLabel=label,rightLabel=right);receipts.append(dict(asset=path,sha256=hashlib.sha256((G/path).read_bytes()).hexdigest(),native_pixels_exact=True))
    return f'![{name}]({path})\n\n'
page="""# Thinner hue-preserving outline

The yellow hue correction is removed. Saturation and value retain revision 106's calibrated response, while every outline endpoint preserves its input hue. The enlarged artwork and completed lens body remain unchanged. At full strength, tentative input #EBCE48 now gives approximately #F6E286, preserving its hue while retaining the calibrated saturation and value. White remains #FCFCFC.

The outline plateau and inward fade are both multiplied by 0.8. A second thickness multiplier rises linearly from 4/7 at 43.359684% of the pill width to one at 44.584980%. It stays thinner to the left and thicker to the right. Expanded and compact use the same proportional rule.

[Research and verification](../research/experiments/miniplayer-outline-taper-107/README.md) · [Previous revision](miniplayer-yellow-match.md) · [Selected reconstruction](reconstruction.md)

## Thickness and brightness

| Region | Plateau | Fade scale | Positive value increase |
| --- | ---: | ---: | ---: |
| Left of 43.359684% | 0.685714 px | 0.914286 px | 99% |
| Transition | Linear | Linear | Linear |
| Right of 44.584980% | 1.2 px | 1.6 px | 100% |

The one-percent reduction applies only to the positive HSV value increase, not to the entire color or saturation. Its size is a provisional interpretation of the requested slight brightness change. Endpoint hue and saturation are preserved during this reduction. The original opposing angular gaps remain zero.

Thickness and brightness moments use actual pixel area. Orders 16 and 32 identify pixels needing refinement; those pixels use orders 64 and 96. All pixels remain scored. The original tolerance is unchanged. Original geometry, shadow, optical transport and incident blur remain frozen.

## Image comparisons

| Case | Previous E | Revised E | SSIM | Partial RMSE |
| --- | ---: | ---: | ---: | ---: |
"""
for row in rows:
 s=row['scores'];page+=f"| {row['member']} {row['reference'].upper()} | {row['previous106_scores']['E']:.4f} | {s['E']:.4f} | {s['ssim']:.5f} | {s['partial']['RMSE']:.4f} |\n"
page+='\nAll local and aggregate changes are retained below. All original scoring cohorts remain unchanged. These comparisons are held for review, without a full-family fidelity claim.\n\n'
for row in rows:
    case=f"{row['member']}-{row['reference']}";reference=open_image(B/f'{case}-reference.png');previous=open_image(B/f'{case}-previous.png');result=open_image(B/f'{case}-candidate.png');w,h=result.size
    page+=f'### {case.replace("-"," ").title()}\n\n'+pair(reference,result,case,right='Thinner hue-preserving outline')
    page+=f'<details data-hsv="{case}-previous"><summary>Previous revision versus revision</summary>\n\n'+pair(previous,result,case+'-previous',label='Previous revision',right='Thinner hue-preserving outline')+'</details>\n\n'
    page+=f'<details data-hsv="{case}-details"><summary>Native crops: colored rims, caps and disappearing diagonals</summary>\n\n'
    crops={'left-cap':(0,0,260,h),'right-cap':(w-260,0,w,h),'upper-rim':(w//2,12,w-180,75),'lower-rim':(w//2,h-85,w-180,h-20),'upper-right-gap':(w-180,0,w,125),'lower-left-gap':(0,h-125,180,h)}
    crops['upper-transition']=(int(w*.38),12,int(w*.50),75)
    crops['lower-transition']=(int(w*.38),h-85,int(w*.50),h-20)
    if case.startswith('compact'):crops['white-content']=(w//2-40,10,w-100,h-20)
    else:crops['brown-content']=(260,12,620,90)
    rec=row['artwork_records'][0];x0,y0,_,_=row['crop'];a,b0,c,d=rec['new_box'];crops['artwork']=(max(0,a-x0-12),max(0,b0-y0-12),min(w,c-x0+12),min(h,d-y0+12))
    for name,box in crops.items():page+=pair(reference,result,case+'-'+name,right='Thinner hue-preserving outline',box=box)
    page+='</details>\n\n'
page+='## Verification\n\nThe completed body and artwork are pixel-exact to revision 106. Four original baseline identities and four independent color/composition replays pass. All original masks and local guards remain. No clipping, optical rays, source sampling or incident filtering was introduced.\n';
(G/'miniplayer-outline-taper.md').write_text(page);(G/'outline-taper-comparison-panels.json').write_text(json.dumps(metadata,indent=2)+'\n');(B/'publication.json').write_text(json.dumps(dict(decoded_pixels=decoded,panels=receipts),indent=2)+'\n');print('PUBLISHED',len(metadata))
