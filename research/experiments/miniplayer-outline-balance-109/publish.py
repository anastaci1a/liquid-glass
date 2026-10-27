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
    path=f'assets/balance109-{name}.png';im.save(G/path);metadata[path]=dict(width=im.width,height=im.height,top=38,bottom=0,gutter=2,leftLabel=label,rightLabel=right);receipts.append(dict(asset=path,sha256=hashlib.sha256((G/path).read_bytes()).hexdigest(),native_pixels_exact=True))
    return f'![{name}]({path})\n\n'
page="""# Softer outline color with the thinner outline

Outline saturation is reduced by two percent relative to revision 108. Hue-shift strength is reduced by ten percent. These are relative reductions, not percentage-point changes. HSV value and the existing slight brightness taper remain unchanged.

Revision 107's thinner-left outline, 80% base width, slight brightness taper, angular gaps, body grading and artwork are unchanged. Saved outline integration is reused exactly. No geometry, optical sampling, filtering, quadrature or fitting was repeated.

[Verification](../research/experiments/miniplayer-outline-balance-109/README.md) · [Previous revision](miniplayer-restored-yellow.md) · [Selected reconstruction](reconstruction.md)

Four prior-image identities pass. Independent scalar HSV replay agrees within 1e-7. New aggregate scores were not computed for this small color adjustment; older scores are not presented as new measurements.

"""
for row in rows:
    case=f"{row['member']}-{row['reference']}";reference=open_image(B/f'{case}-reference.png');previous=open_image(B/f'{case}-previous.png');result=open_image(B/f'{case}-candidate.png');w,h=result.size
    page+=f'### {case.replace("-"," ").title()}\n\n'+pair(reference,result,case,right='Softer outline color')
    page+=f'<details data-hsv="{case}-previous"><summary>Previous revision versus revision</summary>\n\n'+pair(previous,result,case+'-previous',label='Previous revision',right='Softer outline color')+'</details>\n\n'
    page+=f'<details data-hsv="{case}-details"><summary>Native crops: colored rims, caps and disappearing diagonals</summary>\n\n'
    crops={'left-cap':(0,0,260,h),'right-cap':(w-260,0,w,h),'upper-rim':(w//2,12,w-180,75),'lower-rim':(w//2,h-85,w-180,h-20),'upper-right-gap':(w-180,0,w,125),'lower-left-gap':(0,h-125,180,h)}
    crops['upper-transition']=(int(w*.38),12,int(w*.50),75)
    crops['lower-transition']=(int(w*.38),h-85,int(w*.50),h-20)
    if case.startswith('compact'):crops['white-content']=(w//2-40,10,w-100,h-20)
    else:crops['brown-content']=(260,12,620,90)
    rec=row['artwork_records'][0];x0,y0,_,_=row['crop'];a,b0,c,d=rec['new_box'];crops['artwork']=(max(0,a-x0-12),max(0,b0-y0-12),min(w,c-x0+12),min(h,d-y0+12))
    for name,box in crops.items():page+=pair(reference,result,case+'-'+name,right='Softer outline color',box=box)
    page+='</details>\n\n'
page+='## Verification\n\nThe completed body and artwork are pixel-exact to revision 106. Four original baseline identities and four independent color/composition replays pass. All original masks and local guards remain. No clipping, optical rays, source sampling or incident filtering was introduced.\n';
(G/'miniplayer-outline-balance.md').write_text(page);(G/'outline-balance-comparison-panels.json').write_text(json.dumps(metadata,indent=2)+'\n');(B/'publication.json').write_text(json.dumps(dict(decoded_pixels=decoded,panels=receipts),indent=2)+'\n');print('PUBLISHED',len(metadata))
