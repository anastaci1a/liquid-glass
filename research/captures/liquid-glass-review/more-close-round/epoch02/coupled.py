import os,sys,json,copy,hashlib,datetime
from pathlib import Path
import numpy as np,cv2
from PIL import Image,ImageDraw
os.umask(0o002);cv2.setNumThreads(1)
R=Path('/evidence/extended/helper-toolbar-work/more-close-round');B=R/'epoch02';P=B/'gray-pass01';D=B/'coupled-pass02';D.mkdir();sys.path.insert(0,str(R/'latest-circle-baseline/code'));from extended_fit import Study;from vector_revision import composite;import neutral_rim
s=Study(B/'inputs/a');rec=json.loads((P/'candidate-native.json').read_text());z=np.load(P/'candidate-native.npz');masks=np.load(B/'baseline-arrays.npz');M=z['material'];C=z['complete'];base=rec['scores'];p=rec['preset'];a0=rec['neutral_rim']['amplitude'];w=rec['neutral_rim']['width'];assert a0==.125 and w==.028;directionpath=R/'rim-amplitude-round1/cached-direction.npz';direction=np.load(directionpath)['d_material_da'];assert direction.shape==M.shape;sourcecase=s.case
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
for t in [1.,.5]:
 da=t*.00625;db=-t*.0005;pm=M+da*direction+db;pc=complete(pm);q=scores(pm,pc);ck=checks(q);row=dict(t=t,amplitude=a0+da,bias=.07500000000000001+db,prediction_ONLY=q,checks=ck,supported=all(ck.values()));rows.append(row);np.savez_compressed(D/f'prediction-t{str(t).replace(".","p")}.npz',material=pm,complete=pc)
 if row['supported']:chosen=t;break
report=dict(stage='NEW_EPOCH02_CACHED_PREDECLARED_COUPLED_REVIEW',assignment='c4ef8301-e646-4c51-899e-ab582074e201',reused_derivative=str(directionpath),derivative_sha256=hashlib.sha256(directionpath.read_bytes()).hexdigest(),derivative_compatibility='Samepose/circle geometry/normal response/width/2x2grid/postkernel; derivative source-independent, no AA/source/filter/mask assumption reused. New epoch masks/styles evaluated afresh.',base=base,predictions=rows,selected_first_supported=chosen,old_epoch_predictions_not_reclassified=True,new_native_renders=0,source_adopted=True,epoch02_accepted_count=1)
(D/'cached-review.json').write_text(json.dumps(report,indent=2)+'\n');print('PRED '+json.dumps(report),flush=True)
if chosen is None:print('STOP_NEGATIVE_NO_NATIVE',flush=True);sys.exit(0)
newp=copy.deepcopy(p);newp['material'][3:6]=[.07500000000000001-chosen*.0005]*3;newa=a0+chosen*.00625
oldclip=json.loads((R/'latest-circle-baseline/native-raw-clip-proof.json').read_text())['cohorts']['base_unclipped']['global'];assert oldclip['minimum']-chosen*.0005>0 and oldclip['maximum']-chosen*.0005<1
audit={};nativeM=neutral_rim.render(s.source,s.case,newp,newa,w,samples=2,audit=audit);nativeC=complete(nativeM);q=scores(nativeM,nativeC);ck=checks(q);ck['actual_global_rim_clip0']=audit['clipped_channels']==0
f64={}
for n,key in [('glass','glass_mask'),('rim','rim_mask')]:mask=masks[key];f64[n]={name:float(np.sqrt(np.mean(((x[mask].astype(float)-s.target_crop[mask].astype(float))*255)**2))) for name,x in [('before',M),('after',nativeM)]}
f64['E']={n:float(np.sqrt(.7*f64['glass'][n]**2+.3*f64['rim'][n]**2)) for n in ['before','after']}
record=copy.deepcopy(rec);record.update(stage='EPOCH02_NATIVE_RIM_CANDIDATE_STOP_FOR_PRIMARY',preset=newp,neutral_rim=dict(amplitude=newa,width=w),scores=q,checks=ck,qualifies_numerically=all(ck.values()),advisory_f64=f64,native_raw_clip_audit=audit,body_renders=1,actual_composites=1,gray_LS_solves=0,accepted_count=1,source_support_proof_transfer='Only predeclared neutral_rim amplitude and COMMONmaterialbias changed; source geometry/map/kernels/footprint/gains/lights/source/foreground unchanged. WHOLE7731/ALLscored5380/post8752 defined1/observed0 proof transfers. Actual helper global preclip0 verifies all cohorts, Previousactualrawbaseglobal interval shifted by commonnegativebias remains strictlyinside[0,1], so no hiddenbaseclip; actualrimhelperclip0.',limitations='Same existing empirical neutral normal-lighting plus commonmaterialbias operator; no claim refraction/blur identification from estimated smoothheader. Sourcehidden0/upper3.785/posep95.463/originalUIweightuncertainty retained. Historical oldmask negativeSSIM not reclassified; currentepoch adopted by primary before new evaluation.')
np.savez_compressed(D/'candidate-native.npz',material=nativeM,complete=nativeC,alpha=z['alpha']);(D/'candidate-native.json').write_text(json.dumps(record,indent=2)+'\n');(D/'native-verification.json').write_text(json.dumps(dict(checks=ck,scores=q,raw_clip_audit=audit,advisory_f64=f64,native_body_renders=1,accepted_count=1,first_supported_t=chosen),indent=2)+'\n');im=Image.new('RGB',(234,180),'#222');draw=ImageDraw.Draw(im);draw.text((3,18),'Apple CLOSE',fill='white');draw.text((121,18),'Rim candidate',fill='white')
for i,img in enumerate([s.target_crop,nativeC]):im.paste(Image.fromarray(np.uint8(np.rint(np.clip(img,0,1)*255))).resize((116,116),Image.Resampling.LANCZOS),(118*i,64))
im.save(D/'candidate-comparison.png');report.update(new_native_renders=1,native_qualifier=all(ck.values()),native_checks=ck);(D/'cached-review.json').write_text(json.dumps(report,indent=2)+'\n');print('NATIVE '+json.dumps(dict(qualifier=all(ck.values()),t=chosen,amplitude=newa,bias=newp['material'][3],scores=q,checks=ck,audit=audit,f64=f64)),flush=True)
