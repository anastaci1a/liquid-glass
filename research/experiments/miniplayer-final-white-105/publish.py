"""Exact native crops and interactive comparisons; no scientific rerender."""
from pathlib import Path
import json,hashlib
from PIL import Image,ImageDraw
B=Path(__file__).resolve().parent;R=B.parents[2];G=R/'guide';assert (B/'finished.json').exists()
rows=json.loads((B/'artwork/results.json').read_text());metadata={};receipts=[];decoded=0;cap=100_000_000
def open_image(p):
    global decoded
    im=Image.open(p);decoded+=im.width*im.height;assert decoded<=cap;return im.convert('RGB')
def pair(a,b,name,label='Apple reference',right='Candidate',box=None):
    if box:a=a.crop(box);b=b.crop(box)
    assert a.size==b.size
    w,h=a.size;im=Image.new('RGB',(2*w+2,h+38),'white');im.paste(a,(0,38));im.paste(b,(w+2,38));draw=ImageDraw.Draw(im);draw.text((4,10),label,fill='black');draw.text((w+6,10),right,fill='black')
    assert im.crop((0,38,w,h+38)).tobytes()==a.tobytes() and im.crop((w+2,38,2*w+2,h+38)).tobytes()==b.tobytes()
    path=f'assets/white105-{name}.png';im.save(G/path);metadata[path]=dict(width=im.width,height=im.height,top=38,bottom=0,gutter=2,leftLabel=label,rightLabel=right);receipts.append(dict(asset=path,sha256=hashlib.sha256((G/path).read_bytes()).hexdigest(),native_pixels_exact=True))
    return f'![{name}]({path})\n\n'
controls=json.loads((B/'body-controls.json').read_text());actual=json.loads((B/'actual-white-cohort.json').read_text())
page="""# Final white, revised yellow and centered artwork

One candidate adjusts existing body gain to target #E6E6E6 after optical lighting. Bias, dark-tone lift and the original optical brightness pipeline remain unchanged. The finalized geometry, incident blur, shadow and angular outline gaps are fixed.

The strongest outline band is 1.5 native pixels, with its two-pixel inward fade unchanged. The yellow saturation/value target is now #FCF8AD. Input hue remains preserved, yielding approximately #FCEFAD; the nine-level green difference is explicit rather than an exact RGB-match claim.

Artwork width and height are each multiplied by 0.986 relative to the current artwork, then rounded to native pixels. Its horizontal center is unchanged, vertical placement is centered on the pill to the nearest native pixel, and corner radius remains 18 pixels.

Drag each divider or open the native crops and fullscreen. This candidate is for review; the selected reconstruction remains unchanged.

[Research and verification](../research/experiments/miniplayer-final-white-105/README.md) · [Previous revision](miniplayer-restored-grade.md) · [Selected reconstruction](reconstruction.md)

## Final-output white calibration

The frozen calibration cohort uses central expanded-B body pixels with full coverage and near-white retained input, excluding foreground, rim and held pixels. One gain solve sends pure white through those actual cached optical paths, targeting the mean final encoded value 230. No optical path, source sample or illumination parameter is fitted.

"""
page+=f"The cohort contains {controls['cohort_pixels']:,} pixels. Gain is {controls['gain']:.15f}. Final pure-white output spans {controls['final_white_min']:.6f}–{controls['final_white_max']:.6f}, with mean {controls['final_white_mean']:.6f}. Grading-stage white is about {controls['grading_white'][0][0]*255:.4f}; it is deliberately higher than the final target.\n\n"
page+=f"Actual retained near-white samples produce mean final RGB {', '.join(f'{v:.3f}' for v in actual['mean_complete'])}. Their input is not exactly pure white. The synthetic white control and actual image observations remain separate.\n\n"
page+='## Outline anchors\n\n| Input | Requested endpoint | Hue-preserved endpoint |\n| --- | --- | --- |\n'
for a in json.loads((B/'calibration-checkpoint.json').read_text())['anchors']:page+=f"| #{a['input']} | #{a['target']} | #{a['hue_preserved_output']} |\n"
page+='\n## Comparisons\n\n| Case | Previous revision E | New E | SSIM | Partial RMSE |\n| --- | ---: | ---: | ---: | ---: |\n'
for row in rows:
    q=row['scores'];page+=f"| {row['member']} {row['reference'].upper()} | {row['previous104_scores']['E']:.4f} | {q['E']:.4f} | {q['ssim']:.5f} | {q['partial']['RMSE']:.4f} |\n"
page+='\nScores retain every original cohort. The finalized shape is not adjusted to improve them. Compact color regressions remain diagnostic under the shared expanded-first color requirement.\n\n'
page+='## Fixed compact white samples\n\nThese same native positions show preimage and final body values separately. They are observations of the restored pipeline, not extra calibration targets.\n\n| Case / crop-local position | Blurred preimage | Apple | New body |\n| --- | --- | --- | --- |\n'
for x in json.loads((B/'fixed-color-patches.json').read_text()):
    if x['member']!='compact':continue
    def rgb(v):return '#'+''.join(f'{min(255,max(0,round(c))):02X}' for c in v)
    page+=f"| Compact {x['reference'].upper()} ({x['local_x']}, {x['local_y']}) | {rgb(x['preimage'])} | {rgb(x['target'])} | {rgb(x['new_body'])} |\n"
page+='\n'
for row in rows:
    case=f"{row['member']}-{row['reference']}";reference=open_image(B/f'{case}-reference.png');previous=open_image(B/f'{case}-previous.png');result=open_image(B/'artwork'/f'{case}-candidate.png');w,h=result.size
    page+=f'### {case.replace("-"," ").title()}\n\n'+pair(reference,result,case,right='Final white + 1.5px rim')
    page+=f'<details data-hsv="{case}-previous"><summary>Previous revision versus revision</summary>\n\n'+pair(previous,result,case+'-previous',label='Previous revision',right='Final white + 1.5px rim')+'</details>\n\n'
    page+=f'<details data-hsv="{case}-details"><summary>Native crops: colored rims, caps and disappearing diagonals</summary>\n\n'
    crops={'left-cap':(0,0,260,h),'right-cap':(w-260,0,w,h),'upper-rim':(w//2,12,w-180,75),'lower-rim':(w//2,h-85,w-180,h-20),'upper-right-gap':(w-180,0,w,125),'lower-left-gap':(0,h-125,180,h)}
    if case.startswith('compact'):crops['white-content']=(w//2-40,10,w-100,h-20)
    else:crops['brown-content']=(260,12,620,90)
    rec=row['artwork_records'][0];x0,y0,_,_=row['crop'];a,b0,c,d=rec['new_box'];crops['artwork']=(max(0,a-x0-12),max(0,b0-y0-12),min(w,c-x0+12),min(h,d-y0+12))
    for name,box in crops.items():page+=pair(reference,result,case+'-'+name,right='Final white + 1.5px rim',box=box)
    page+='</details>\n\n'
page+='## Limits\n\nThe white calibration applies to the declared body cohort; edge lighting and mixed coverage can produce different values. The outline remains an empirical hue-preserving response. Optical scene, source-return and foreground fidelity limitations remain. The album-art change is isolated to its original and revised rectangles; other pixels remain exact.\n'
(G/'miniplayer-final-white.md').write_text(page);(G/'final-white-comparison-panels.json').write_text(json.dumps(metadata,indent=2)+'\n');(B/'publication.json').write_text(json.dumps(dict(decoded_pixels=decoded,panels=receipts),indent=2)+'\n');print('PUBLISHED',len(metadata))
