"""Saved input/vector QC only, no new source fitting or body rendering."""
import os,json,hashlib,sys
from pathlib import Path
import numpy as np,cv2
from PIL import Image,ImageDraw
os.umask(0o002);cv2.setNumThreads(1)
R=Path('/evidence/extended/helper-toolbar-work/more-close-round');A=R/'a-proposed';case=json.loads((A/'case.json').read_text());s=np.load(R/'source-controls.npz');T=np.asarray(Image.open(A/'target.png'));H,W=T.shape[:2];yy,xx=np.mgrid[:H,:W];u=(xx-747)/60;v=(yy-188)/60;co=np.asarray(case['background_estimate']['coefficient_rgb']);field=np.stack([np.ones_like(u),u,v],-1)@co;domain=s['modeled_domain'];rgb=np.zeros_like(T);rgb[domain]=np.uint8(np.rint(np.clip(field[domain],0,1)*255));assert np.array_equal(rgb,np.asarray(Image.open(A/'source.png')))
checks={n:not bool(np.any(s[n]&(s['train']|s['held']))) for n in ['left','upper','lower']};assert all(checks.values()) and not np.any(s['train']&s['held'])
for n,sha in case['source_sha256'].items():assert hashlib.sha256((A/n).read_bytes()).hexdigest()==sha
assert np.array_equal(T,np.asarray(Image.open('/evidence/apple-matches/219-320.png')))
sys.path.insert(0,'/evidence/extended/helper-toolbar-work/safari-right-circle-round/neutral-baseline/code');from vector_foreground import coverage
layer=case['foreground_layers'][0];mask=coverage(A,layer);a,b,c,d=layer['box'];target=T[b:d,a:c];diags=[]
for th in [60,80]:
 ref=target.mean(2)<th;pred=mask>=.5;diags.append(dict(black_threshold=th,IoU=float((ref&pred).sum()/(ref|pred).sum()),different_pixels=int((ref^pred).sum()),diagnostic_only=True))
# Aspect preserved in both pure-vector and actual-pixel diagnostic panels.
w,h=2*(c-a),2*(d-b);im=Image.new('RGB',(2*w,h+64),'white');dr=ImageDraw.Draw(im);dr.text((2,12),'Ref',fill='black');dr.text((w+2,12),'SVG',fill='black');im.paste(Image.fromarray(target).resize((w,h),Image.Resampling.NEAREST),(0,64));ink=np.uint8(np.rint((1-mask[...,None])*np.ones((*mask.shape,3))*255));im.paste(Image.fromarray(ink).resize((w,h),Image.Resampling.NEAREST),(w,64));im.save(R/'glyph-DIAGNOSTIC_ONLY.png')
x0,y0,x1,y1=case['crop'];w=2*(x1-x0);h=2*(y1-y0);im=Image.new('RGB',(2*w+2,h+64),'#222');dr=ImageDraw.Draw(im);dr.text((4,20),'Original',fill='white');dr.text((w+6,20),'Input only',fill='white');im.paste(Image.fromarray(T[y0:y1,x0:x1]).resize((w,h),Image.Resampling.NEAREST),(0,64));im.paste(Image.fromarray(rgb[y0:y1,x0:x1]).resize((w,h),Image.Resampling.NEAREST),(w+2,64));im.save(R/'source-input-comparison.png')
img=T.astype(float).copy()
for n,col in [('train',[0,255,0]),('held',[255,180,0]),('left',[0,255,255]),('upper',[0,255,255]),('lower',[0,255,255])]:m=s[n];img[m]=.4*img[m]+.6*np.asarray(col)
Image.fromarray(np.uint8(np.rint(img))).crop((700,140,861,248)).resize((322,216),Image.Resampling.NEAREST).save(R/'control-overlay.png')
q=dict(status='SAVED_INPUT_QC_PASS_NOT_INPUT_ADOPTION',source_png_exact_frozen_coefficients_quantization=True,target_pixels_exact_cached_native=True,all_png_hashes_exact=True,train_held_disjoint=True,validation_disjoint_from_train_held=checks,validation_pairwise_overlaps={f'{x}/{y}':int((s[x]&s[y]).sum()) for x,y in [('left','upper'),('left','lower'),('upper','lower')]},glyph_diagnostics=diags,glyph_style='Pinned originalxmark unmodified, black1/uniformaspect; exactUIweight remains unscoredpendingreview, no glyphfit or screenshotmatte.',source_ambiguity='Upper3.785px-level error near parenttop remains; source not physical incidentlight/observedhiddenRGB. Nestedquad rejected for left/lower regressions, no parentglowfitted.',new_source_fit=False,new_body_render=False,new_glyph_fit=False)
(R/'saved-input-integrity.json').write_text(json.dumps(q,indent=2)+'\n');print(json.dumps(q))
