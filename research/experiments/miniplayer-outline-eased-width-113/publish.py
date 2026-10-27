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
    path=f'assets/eased113-{name}.png';im.save(G/path);metadata[path]=dict(width=im.width,height=im.height,top=38,bottom=0,gutter=2,leftLabel=label,rightLabel=right);receipts.append(dict(asset=path,sha256=hashlib.sha256((G/path).read_bytes()).hexdigest(),native_pixels_exact=True))
    return f'![{name}]({path})\n\n'
page="""# Eased outline thickness

Color B at 120% is the chosen review baseline. This candidate replaces its short middle taper with a long smooth thickness transition. The color response, completed body, shape, artwork, blur, shadow and diagonal gaps stay fixed.

From left to right, the existing thin width holds through 7.614% of the full pill width. A cubic smoothstep reaches 120% at 91.966%. A short linear transition reaches 145% at 94.365%, then holds through the right tip. Both plateau and inward fade scale together.

The slight left brightness reduction eases separately: its existing maximum holds through 7.614%, then smoothly reaches zero at the exact center. It reduces only positive HSV value lift by at most one percent; hue and saturation retain Color B.

The entire right endcap is not constant width: the exact supplied horizontal coordinates govern its transition. At the right tip the plateau is 1.74 native pixels and fade scale is 2.32. The existing thin-left values remain approximately 0.686 and 0.914 pixels.

Each slider compares Apple with the candidate. Expand the previous-choice comparison to compare Color B at 120% directly. Zoomed crops preserve native pixels. No new aggregate score or fidelity acceptance is claimed.

[Verification](../research/experiments/miniplayer-outline-eased-width-113/README.md) · [Previous options](miniplayer-outline-range.md)

"""
for row in rows:
    case=row['case'];reference=open_image(B.parent/'miniplayer-outline-value-110'/f'{case}-reference.png');previous=open_image(B.parent/'miniplayer-outline-range-112'/f'{case}-c1-w1.png');result=open_image(B/f'{case}-candidate.png');w,h=result.size
    page+=f'### {case.replace("-"," ").title()}\n\n'+pair(reference,result,case,right='Eased outline')
    page+=f'<details data-hsv="{case}-previous"><summary>Chosen Color B 120% versus revision</summary>\n\n'+pair(previous,result,case+'-previous',label='Chosen Color B 120%',right='Eased outline')+'</details>\n\n'
    page+=f'<details data-hsv="{case}-details"><summary>Native crops: colored rims, caps and disappearing diagonals</summary>\n\n'
    crops={'left-cap':(0,0,260,h),'right-cap':(w-260,0,w,h),'upper-rim':(w//2,12,w-180,75),'lower-rim':(w//2,h-85,w-180,h-20),'upper-right-gap':(w-180,0,w,125),'lower-left-gap':(0,h-125,180,h)}
    crops['upper-transition']=(int(w*.78),12,w,105)
    crops['lower-transition']=(int(w*.78),h-105,w,h-10)
    if case.startswith('compact'):crops['white-content']=(w//2-40,10,w-100,h-20)
    else:crops['brown-content']=(260,12,620,90)
    record=json.loads((B.parent/'miniplayer-outline-taper-107'/f'{case}-metrics.json').read_text());rec=record['artwork_records'][0];x0,y0,_,_=record['crop'];a,b0,c,d=rec['new_box'];crops['artwork']=(max(0,a-x0-12),max(0,b0-y0-12),min(w,c-x0+12),min(h,d-y0+12))
    for name,box in crops.items():page+=pair(reference,result,case+'-'+name,right='Eased outline',box=box)
    page+='</details>\n\n'
page+='## Verification\n\nFour chosen-baseline identities and four independent composition replays pass. The new area integration uses orders 16/32 and restricted 64/96 refinement. Source guides are finite everywhere the outline contributes. Unchanged body pixels remain exact. No optical rays, source filtering or fitting ran.\n';
(G/'miniplayer-outline-eased-width.md').write_text(page);(G/'outline-eased-width-comparison-panels.json').write_text(json.dumps(metadata,indent=2)+'\n');(B/'publication.json').write_text(json.dumps(dict(decoded_pixels=decoded,panels=receipts),indent=2)+'\n');print('PUBLISHED',len(metadata))
