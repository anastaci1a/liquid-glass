"""ONE authorized analytic uniform opaque-gray candidate, cached body only."""
import os,json,copy,hashlib,sys
from pathlib import Path
import numpy as np,cv2
from PIL import Image,ImageDraw
os.umask(0o002);cv2.setNumThreads(1)
R=Path('/evidence/extended/helper-toolbar-work/more-close-round');B=R/'latest-circle-baseline';D=R/'foreground-gray-round1';D.mkdir();sys.path.insert(0,str(B/'code'))
from extended_fit import Study
from vector_foreground import coverage
from vector_revision import composite
s=Study(B/'inputs/a');base=json.loads((B/'baseline-native.json').read_text())['scores'];rec=json.loads((B/'baseline-recipe.json').read_text());z=np.load(B/'baseline-native-arrays.npz');M=z['material'];originalC=z['complete'];p=rec['preset'];layer=s.case['foreground_layers'][0];A=coverage(s.folder,layer);l,t,r,b=layer['box'];x0,y0,x1,y1=s.crop;sl=np.s_[t-y0:b-y0,l-x0:r-x0];assert np.all(z['alpha'][sl]==1);assert np.array_equal(originalC[sl],np.asarray(M[sl]*(1-A[...,None]),dtype=originalC.dtype))
# Analytic one-scalar LS on the ORIGINAL full glyph box, alpha fixed by SVG.
# The earlier deepcore55.333 estimate was diagnostic, not a native trial.
residual=s.target_crop[sl].astype(float)-originalC[sl].astype(float);den=3*float(np.sum(A.astype(float)**2));unbounded=float(np.sum(A[...,None].astype(float)*residual)/den);q=float(np.clip(unbounded,0,.4));assert q>0
style={layer.get('style_key',layer['vector_asset']):dict(color=[q,q,q],opacity=1.)};oldcase=s.case;fp=hashlib.sha256(json.dumps(oldcase,sort_keys=True).encode()).hexdigest();assert fp==rec['case_sha256']['a'];assert 'foreground_styles' not in oldcase
try:
 s.case={**oldcase,'foreground_styles':style};C=composite(s,p,M)
finally:s.case=oldcase
fg=z['glyph_mask'];outside=~fg;assert np.array_equal(C[outside],originalC[outside]);assert np.array_equal(M,z['material'])
scores=copy.deepcopy(base)
for name,key in [('glyph','glyph_mask'),('exterior','exterior_mask'),('full_visible_exterior','full_visible_exterior_mask')]:m=z[key];scores[name]=dict(pixels=int(m.sum()),rmse=float(np.sqrt(np.mean(((C-s.target_crop)[m]*255)**2))))
checks={n:scores[n]['rmse']<=base[n]['rmse'] for n in ['glass','rim','held','interior','glyph','exterior','full_visible_exterior']};checks.update(E=scores['E']<=base['E'],SSIM=scores['ssim']>=base['ssim'],foreground_progress=scores['glyph']['rmse']<base['glyph']['rmse'],body_bit_exact=True,outside_glyph_bit_exact=True,opacity_fixed_1=True,input_case_unchanged=fp==rec['case_sha256']['a']);qualifier=all(checks.values())
original_fg_error=(originalC[fg].astype(float)-s.target_crop[fg].astype(float))*255;new_fg_error=(C[fg].astype(float)-s.target_crop[fg].astype(float))*255;f64=dict(before=float(np.sqrt(np.mean(original_fg_error**2))),after=float(np.sqrt(np.mean(new_fg_error**2))));assert f64['after']<f64['before']
cohorts={}
for n,m in [('canonical_deep',A>=.995),('canonical_partial_edge',(A>.005)&(A<.995))]:
 e0=(originalC[sl].astype(float)-s.target_crop[sl].astype(float))*255;e1=(C[sl].astype(float)-s.target_crop[sl].astype(float))*255;cohorts[n]=dict(pixels=int(m.sum()),old_RGB_RMSE=float(np.sqrt(np.mean(e0[m]**2))),new_RGB_RMSE=float(np.sqrt(np.mean(e1[m]**2))),old_signed_RGB=e0[m].mean(0).tolist(),new_signed_RGB=e1[m].mean(0).tolist(),advisory_only=True)
sha=lambda path:hashlib.sha256(Path(path).read_bytes()).hexdigest()
record=copy.deepcopy(rec);record.update(foreground_styles=style,foreground_model='ONEopaqueuniformneutralgray, RGBtied and opacity1. Parameter override in EXISTING public Study.apply_foreground, not input/case/SVG/source modification.',stage='FOREGROUND_ONLY_CANDIDATE_AWAIT_PRIMARY_NO_COUNT',approval='6a9a563d-4f4b-4795-8230-adaacdbab0f2',foreground_gray=q,analytic_unbounded_gray=unbounded,gray_bounds=[0,.4],scores=scores,checks=checks,qualifies_numerically=qualifier,foreground_f64=f64,advisory_cohorts=cohorts,body_source_proof_transfer='Material/source/rays/map/kernels/rim/pose/alpha/SVG/masks/shadow unchanged. WHOLE7731/ALLscored5624/post8752 originalmodelconfidence1/hiddenobserved0 and priorrawclip0 transfer; newcolorin[0,.4] withfixedalpha isconvex, no body/ray rerender.',original_source_proof_sha256=sha(B/'source-proof-FIRST.json'),original_native_clip_proof_sha256=sha(B/'native-raw-clip-proof.json'),actual_body_renders_added=0,actual_native_composites=1,uniform_gray_LS_solves=1,accepted_count=0,limits='Foreground-only empirical color, not optics/materialradiance/Appleopacity identification. SVG remains thinner than target; partialedge regression retained. BodyE/SSIM exactties. Sourceupper3.785/pose.463/sourcehidden0 unchanged.')
(D/'candidate-native.json').write_text(json.dumps(record,indent=2)+'\n');np.savez_compressed(D/'candidate-native.npz',material=M,complete=C,alpha=z['alpha']);(D/'verification.json').write_text(json.dumps(dict(status='FIRST_ACTUAL_COMPOSITE_QUALIFIER_STOP_FOR_PRIMARY' if qualifier else 'ONE_ACTUAL_COMPOSITE_REJECTED_STOP',scores=scores,checks=checks,gray=q,uniform_gray_LS_solves=1,native_composites=1,body_renders=0,optical_fits=0,accepted_count=0,advisory_cohorts=cohorts),indent=2)+'\n')
w,h=2*(x1-x0),2*(y1-y0);im=Image.new('RGB',(2*w+2,h+64),'#222');draw=ImageDraw.Draw(im);draw.text((4,20),'Apple CLOSE',fill='white');draw.text((w+6,20),'Opaque gray',fill='white')
for i,rgb in enumerate([s.target_crop,C]):im.paste(Image.fromarray(np.uint8(np.rint(np.clip(rgb,0,1)*255))).resize((w,h),Image.Resampling.LANCZOS),(i*(w+2),64))
im.save(D/'candidate-comparison.png');print(json.dumps(dict(status='QUALIFIER' if qualifier else 'NEGATIVE',gray=q,gray255=q*255,baseline_foreground=base['glyph'],candidate_scores=scores,checks=checks,advisory_cohorts=cohorts,body_renders=0,native_composites=1,count=0)),flush=True)
