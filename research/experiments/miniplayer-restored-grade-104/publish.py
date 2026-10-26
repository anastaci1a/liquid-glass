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
    path=f'assets/restored104-{name}.png';im.save(G/path);metadata[path]=dict(width=im.width,height=im.height,top=38,bottom=0,gutter=2,leftLabel=label,rightLabel=right);receipts.append(dict(asset=path,sha256=hashlib.sha256((G/path).read_bytes()).hexdigest(),native_pixels_exact=True))
    return f'![{name}]({path})\n\n'
page="""# Restored lens grading and thicker colored rim

One review candidate restores the previous body grading and optical brightness composition. Only its existing gain changes, so grading-stage white becomes #E5E5E5. Bias and dark-tone lift are unchanged. Refraction geometry, incident blur, shadow and foreground are fixed.

The improved outline color mapping from the last candidate is retained exactly. Its maximum-strength plateau doubles from one to two native pixels. The two-pixel inward fade and opposing diagonal gaps remain unchanged. This does not double the complete outline width.

Final body white varies with optical transmission and reflected light. With normal-incidence transmission alone, grading-stage 229 becomes about 221. This is the restored position-dependent pipeline, not the direct final-color map from the last test.

The selected reconstruction remains unchanged pending review. Drag the comparisons or open native crops and fullscreen.

[Research and verification](../research/experiments/miniplayer-restored-grade-104/README.md) · [Previous calibrated candidate](miniplayer-anchor-colors.md) · [Selected reconstruction](reconstruction.md)

## Controls changed

| Control | Previous candidate | This candidate |
| --- | --- | --- |
| Body response | New anchor map | Previous gain/bias plus dark-tone lift |
| Body gain | Not applicable | 0.507202380341388 |
| Body bias | Not applicable | 0.39083683534488656, restored |
| Dark-tone lift | Not applicable | 0.08, restored |
| Optical brightness | Replaced | Original primary power and direct reflection restored |
| Outline endpoint | Calibrated color map | Identical |
| Strongest outline thickness | 1 native pixel | 2 native pixels |
| Inward fade | 2 native pixels | Identical |

## Comparisons

| Case | Previous candidate E | New E | SSIM | Partial RMSE |
| --- | ---: | ---: | ---: | ---: |
"""
for row in rows:
    q=row['scores'];page+=f"| {row['member']} {row['reference'].upper()} | {row['anchor103_scores']['E']:.4f} | {q['E']:.4f} | {q['ssim']:.5f} | {q['partial']['RMSE']:.4f} |\n"
page+='\nScores retain every original cohort. The finalized shape is not adjusted to improve them. Compact color regressions remain diagnostic under the shared expanded-first color requirement.\n\n'
page+='## Fixed compact white samples\n\nThese same native positions show preimage and final body values separately. They are observations of the restored pipeline, not extra calibration targets.\n\n| Case / crop-local position | Blurred preimage | Apple | New body |\n| --- | --- | --- | --- |\n'
for x in json.loads((B/'fixed-color-patches.json').read_text()):
    if x['member']!='compact':continue
    def rgb(v):return '#'+''.join(f'{min(255,max(0,round(c))):02X}' for c in v)
    page+=f"| Compact {x['reference'].upper()} ({x['local_x']}, {x['local_y']}) | {rgb(x['preimage'])} | {rgb(x['target'])} | {rgb(x['new_body'])} |\n"
page+='\n'
for row in rows:
    case=f"{row['member']}-{row['reference']}";reference=open_image(B/f'{case}-reference.png');previous=open_image(B/f'{case}-previous.png');result=open_image(B/f'{case}-candidate.png');w,h=result.size
    page+=f'### {case.replace("-"," ").title()}\n\n'+pair(reference,result,case,right='Restored grade + wider rim')
    page+=f'<details data-hsv="{case}-previous"><summary>Previous calibrated candidate versus revision</summary>\n\n'+pair(previous,result,case+'-previous',label='Previous calibrated candidate',right='Restored grade + wider rim')+'</details>\n\n'
    page+=f'<details data-hsv="{case}-details"><summary>Native crops: colored rims, caps and disappearing diagonals</summary>\n\n'
    crops={'left-cap':(0,0,260,h),'right-cap':(w-260,0,w,h),'upper-rim':(w//2,12,w-180,75),'lower-rim':(w//2,h-85,w-180,h-20),'upper-right-gap':(w-180,0,w,125),'lower-left-gap':(0,h-125,180,h)}
    if case.startswith('compact'):crops['white-content']=(w//2-40,10,w-100,h-20)
    else:crops['brown-content']=(260,12,620,90)
    for name,box in crops.items():page+=pair(reference,result,case+'-'+name,right='Restored grade + wider rim',box=box)
    page+='</details>\n\n'
page+='## Limits\n\nThe outline still preserves preimage hue. Its yellow anchor is approximately #FEEB85 rather than the sampled #FEF985. Coverage and angular fading blend that endpoint with the body. The restored reflected scene remains hypothetical, and neither this display adjustment nor a better score establishes full optical fidelity.\n'
(G/'miniplayer-restored-grade.md').write_text(page);(G/'restored-grade-comparison-panels.json').write_text(json.dumps(metadata,indent=2)+'\n');(B/'publication.json').write_text(json.dumps(dict(decoded_pixels=decoded,panels=receipts),indent=2)+'\n');print('PUBLISHED',len(metadata))
