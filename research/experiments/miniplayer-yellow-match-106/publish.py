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
    path=f'assets/yellow106-{name}.png';im.save(G/path);metadata[path]=dict(width=im.width,height=im.height,top=38,bottom=0,gutter=2,leftLabel=label,rightLabel=right);receipts.append(dict(asset=path,sha256=hashlib.sha256((G/path).read_bytes()).hexdigest(),native_pixels_exact=True))
    return f'![{name}]({path})\n\n'
comparison=json.loads((B/'color-comparison.json').read_text());anchors=json.loads((B/'calibration-checkpoint.json').read_text())['anchors']
page="""# More saturated yellow and larger artwork

One candidate maps the proposed preimage #EBCE48 exactly to #F6F586 at full outline strength. It retains the previous body grade, final-white calibration, optical lighting, geometry, incident blur, shadow, 1.5-pixel plateau, two-pixel fade and opposing diagonal gaps.

Artwork width and height are multiplied by 1.0183 relative to revision 105, then rounded to native pixels. Both artwork centers and radius 18 remain unchanged. The selected reconstruction is unchanged pending review.

[Research and verification](../research/experiments/miniplayer-yellow-match-106/README.md) · [Previous revision](miniplayer-final-white.md) · [Selected reconstruction](reconstruction.md)

## Supplied color comparison

| Color | HSV hue | HSV saturation | HSV value | Linear-light luminance |
| --- | ---: | ---: | ---: | ---: |
"""
labels=['Input #EBCE48','Reported current #F7EDB4','Requested #F6F586']
for label,row in zip(labels,comparison['colors']):page+=f"| {label} | {row['hue_degrees']:.3f}° | {100*row['saturation']:.3f}% | {100*row['value']:.3f}% | {row['linear_luminance']:.6f} |\n"
page+='\nThe requested color is about 68% more saturated than the reported current output. Its maximum channel decreases by one, while linear-light luminance increases about 3.6%. The channel change is −1 red, +8 green and −46 blue. Increasing brightness alone would not reproduce it.\n\n'
page+='Exact mapping from the proposed input requires a 10.139° hue shift toward yellow. This revision adds an explicit smooth warm-hue correction. It preserves neutral colors and leaves hue unchanged outside its fixed 30° half-width. The earlier brown anchors retain zero hue correction. This is a color-dependent response, not a painted spatial correction.\n\n'
svg=['<svg xmlns="http://www.w3.org/2000/svg" width="1000" height="130" viewBox="0 0 1000 130"><rect width="1000" height="130" fill="white"/>']
for i,(label,color) in enumerate([('Input','EBCE48'),('Reported current','F7EDB4'),('Requested','F6F586'),('Full-strength result','F6F586')]):
 x=i*250;svg.append(f'<rect x="{x+5}" y="5" width="240" height="75" fill="#{color}"/><text x="{x+10}" y="102" font-family="sans-serif" font-size="16">{label}</text><text x="{x+10}" y="123" font-family="sans-serif" font-size="16">#{color}</text>')
svg.append('</svg>');(G/'assets/yellow106-swatches.svg').write_text(''.join(svg));page+='![Supplied colors and exact full-strength endpoint](assets/yellow106-swatches.svg)\n\n'
page+='The preimage correspondence is tentative user-supplied evidence. Exact anchor matching does not prove that every reference rim pixel has that incident color. Coverage, angular strength and inward fade still blend the endpoint with the completed body.\n\n## Image comparisons\n\n| Case | Previous E | Revised E | SSIM | Partial RMSE |\n| --- | ---: | ---: | ---: | ---: |\n'
for row in rows:
 s=row['scores'];page+=f"| {row['member']} {row['reference'].upper()} | {row['previous105_scores']['E']:.4f} | {s['E']:.4f} | {s['ssim']:.5f} | {s['partial']['RMSE']:.4f} |\n"
page+='\nExpanded aggregate errors improve slightly; compact errors increase. All original scoring cohorts remain unchanged. These comparisons are held for review, without a full-family fidelity claim.\n\n'
for row in rows:
    case=f"{row['member']}-{row['reference']}";reference=open_image(B/f'{case}-reference.png');previous=open_image(B/f'{case}-previous.png');result=open_image(B/f'{case}-candidate.png');w,h=result.size
    page+=f'### {case.replace("-"," ").title()}\n\n'+pair(reference,result,case,right='Yellow matched + larger art')
    page+=f'<details data-hsv="{case}-previous"><summary>Previous revision versus revision</summary>\n\n'+pair(previous,result,case+'-previous',label='Previous revision',right='Yellow matched + larger art')+'</details>\n\n'
    page+=f'<details data-hsv="{case}-details"><summary>Native crops: colored rims, caps and disappearing diagonals</summary>\n\n'
    crops={'left-cap':(0,0,260,h),'right-cap':(w-260,0,w,h),'upper-rim':(w//2,12,w-180,75),'lower-rim':(w//2,h-85,w-180,h-20),'upper-right-gap':(w-180,0,w,125),'lower-left-gap':(0,h-125,180,h)}
    if case.startswith('compact'):crops['white-content']=(w//2-40,10,w-100,h-20)
    else:crops['brown-content']=(260,12,620,90)
    rec=row['artwork_records'][0];x0,y0,_,_=row['crop'];a,b0,c,d=rec['new_box'];crops['artwork']=(max(0,a-x0-12),max(0,b0-y0-12),min(w,c-x0+12),min(h,d-y0+12))
    for name,box in crops.items():page+=pair(reference,result,case+'-'+name,right='Yellow matched + larger art',box=box)
    page+='</details>\n\n'
page+='## Artwork placement\n\n| Member | Previous size | Requested size | Raster size | Horizontal center | Vertical center |\n| --- | --- | --- | --- | --- | --- |\n'
for row in rows[::2]:
 r=row['artwork_records'][0];o=r['old_box'];page+=f"| {row['member']} | {o[2]-o[0]} × {o[3]-o[1]} | {r['requested_size'][0]:.4f} × {r['requested_size'][1]:.4f} | {r['realized_size'][0]} × {r['realized_size'][1]} | Unchanged | Unchanged |\n"
page+='\nBody pixels outside the artwork rectangles are exact. The optical samples, body grading and outline geometry were reused without rerendering optics or incident blur. Four baseline identities and four independent candidate replays are pixel-exact. No clipping occurred.\n'
(G/'miniplayer-yellow-match.md').write_text(page);(G/'yellow-match-comparison-panels.json').write_text(json.dumps(metadata,indent=2)+'\n');(B/'publication.json').write_text(json.dumps(dict(decoded_pixels=decoded,panels=receipts,swatch=dict(asset='assets/yellow106-swatches.svg',sha256=hashlib.sha256((G/'assets/yellow106-swatches.svg').read_bytes()).hexdigest())),indent=2)+'\n');print('PUBLISHED',len(metadata))
