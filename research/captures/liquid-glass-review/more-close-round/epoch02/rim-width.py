import os,sys,json,copy,hashlib,datetime
from pathlib import Path
import numpy as np,cv2
from PIL import Image,ImageDraw
os.umask(0o002);cv2.setNumThreads(1)
R=Path('/evidence/extended/helper-toolbar-work/more-close-round');B=R/'epoch02';P=B/'gray-pass01';D=B/'rim-width-pass02';D.mkdir();sys.path.insert(0,str(R/'latest-circle-baseline/code'));from extended_fit import Study;from vector_revision import composite;import neutral_rim
s=Study(B/'inputs/a');rec=json.loads((P/'candidate-native.json').read_text());z=np.load(P/'candidate-native.npz');masks=np.load(B/'baseline-arrays.npz');M=z['material'];C=z['complete'];base=rec['scores'];p=rec['preset'];a0=rec['neutral_rim']['amplitude'];w=rec['neutral_rim']['width'];assert a0==.125 and w==.028;sourcecase=s.case
# Source-independent geometric derivative from same pose/normal/kernel/grid;
# foreground/source correction does not enter derivative; evaluate NEW masks.
def complete(m):
 try:s.case={**sourcecase,'foreground_styles':rec['foreground_styles']};return composite(s,p,m)
 finally:s.case=sourcecase
def scores(m,c):
 q=s.scores(m);q['E']=float(np.sqrt(q['loss']))
 for n,key in [('glyph','glyph_mask'),('exterior','exterior_mask'),('full_visible_exterior','full_visible_exterior_mask')]:mask=masks[key];q[n]=dict(pixels=int(mask.sum()),rmse=float(np.sqrt(np.mean(((c-s.target_crop)[mask]*255)**2))))
 return q
def checks(q):
 v={n:q[n]['rmse']<=base[n]['rmse'] for n in ['glass','rim','held','interior','glyph','exterior','full_visible_exterior']};v.update(E=q['E']<=base['E'],SSIM=q['ssim']>=base['ssim'],meaningful_E_improvement=q['E']<base['E']);return v
assert scores(M,C)==base
rows=[];chosen=None
for width in [.027,.029]:
 delta=np.zeros_like(M)
 for row,bottom,W,x,y in s.raster_tiles():
  F=a0*(neutral_rim.field(x,y,p,width)-neutral_rim.field(x,y,p,w));delta[row:bottom]=F.reshape(bottom-row,2,W,2).mean((1,3))[:,:,None]
 if p['post_sigma']:delta=cv2.GaussianBlur(delta,(0,0),p['post_sigma']*s.L)
 pm=M+delta;pc=complete(pm);q=scores(pm,pc);ck=checks(q);row=dict(width=width,prediction_ONLY=q,checks=ck,supported=all(ck.values()));rows.append(row);np.savez_compressed(D/f'prediction-{str(width).replace(".","p")}.npz',material=pm,complete=pc)
 if row['supported']:chosen=width;break
report=dict(stage='NEW_EPOCH02_CACHED_EXISTING_WIDTH_REVIEW',assignment='d2e65b87-acbf-4d7f-bc01-fe9f3eba7abc',proposal_model='Source-independent delta of exact neutral_rim fields at fixed amplitude .125, each2x2averaged/postfiltered; no repeated amplitude derivative. Proposal only, actualnativefloat32operationorder decides.',base=base,predictions=rows,selected_first_supported_width=chosen,old_epoch_predictions_not_reclassified=True,new_native_renders=0,source_adopted=True,epoch02_accepted_count=1)
(D/'cached-review.json').write_text(json.dumps(report,indent=2)+'\n');print('PRED '+json.dumps(report),flush=True)
if chosen is None:print('STOP_NEGATIVE_NO_NATIVE',flush=True);sys.exit(0)
audit={};nativeM=neutral_rim.render(s.source,s.case,p,a0,chosen,samples=2,audit=audit);nativeC=complete(nativeM);q=scores(nativeM,nativeC);ck=checks(q);ck['actual_global_rim_clip0']=audit['clipped_channels']==0
f64={}
for n,key in [('glass','glass_mask'),('rim','rim_mask')]:mask=masks[key];f64[n]={name:float(np.sqrt(np.mean(((x[mask].astype(float)-s.target_crop[mask].astype(float))*255)**2))) for name,x in [('before',M),('after',nativeM)]}
f64['E']={n:float(np.sqrt(.7*f64['glass'][n]**2+.3*f64['rim'][n]**2)) for n in ['before','after']}
record=copy.deepcopy(rec);record.update(stage='EPOCH02_NATIVE_RIM_CANDIDATE_STOP_FOR_PRIMARY',neutral_rim=dict(amplitude=a0,width=chosen),scores=q,checks=ck,qualifies_numerically=all(ck.values()),advisory_f64=f64,native_raw_clip_audit=audit,body_renders=1,actual_composites=1,gray_LS_solves=0,accepted_count=1,source_support_proof_transfer='Only neutral_rim width changed; original source geometry/map/kernels/footprint/material/source/foreground unchanged. WHOLE7731/ALLscored5380/post8752 defined1/observed0 proof transfers. Actual helper global preclip0 verifies all cohorts, previous baseclip0 transfers.',limitations='Same empirical neutral normal-lighting operator; no claim refraction/blur identification from estimated smoothheader. Sourcehidden0/upper3.785/posep95.463/originalUIweightuncertainty retained. Historical oldmask negativeSSIM not reclassified; currentepoch adopted by primary before new evaluation.')
np.savez_compressed(D/'candidate-native.npz',material=nativeM,complete=nativeC,alpha=z['alpha']);(D/'candidate-native.json').write_text(json.dumps(record,indent=2)+'\n');(D/'native-verification.json').write_text(json.dumps(dict(checks=ck,scores=q,raw_clip_audit=audit,advisory_f64=f64,native_body_renders=1,accepted_count=1,first_supported_width=chosen),indent=2)+'\n');im=Image.new('RGB',(234,180),'#222');draw=ImageDraw.Draw(im);draw.text((3,18),'Apple CLOSE',fill='white');draw.text((121,18),'Rim candidate',fill='white')
for i,img in enumerate([s.target_crop,nativeC]):im.paste(Image.fromarray(np.uint8(np.rint(np.clip(img,0,1)*255))).resize((116,116),Image.Resampling.LANCZOS),(118*i,64))
im.save(D/'candidate-comparison.png');report.update(new_native_renders=1,native_qualifier=all(ck.values()),native_checks=ck);(D/'cached-review.json').write_text(json.dumps(report,indent=2)+'\n');print('NATIVE '+json.dumps(dict(qualifier=all(ck.values()),width=chosen,scores=q,checks=ck,audit=audit,f64=f64)),flush=True)
