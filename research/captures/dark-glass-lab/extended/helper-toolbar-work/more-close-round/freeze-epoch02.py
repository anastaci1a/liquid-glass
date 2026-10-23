import os,json,shutil,hashlib,datetime,sys
from pathlib import Path
import numpy as np,cv2
os.umask(0o002);cv2.setNumThreads(1)
R=Path('/evidence/extended/helper-toolbar-work/more-close-round');D=R/'epoch02';D.mkdir();B=R/'latest-circle-baseline';PRIMARY=Path('/evidence/extended/more-close-primary-epoch02');src=R/'default400-source/a-proposed';shutil.copytree(src,D/'inputs/a');
for n in ['baseline-arrays.npz','baseline-scores.json','verification.json']:shutil.copyfile(PRIMARY/n,D/n)
for n in ['source-proof-FIRST.json','native-raw-clip-proof.json','code-snapshot.json']:shutil.copyfile(B/n,D/n)
sys.path.insert(0,str(B/'code'));from extended_fit import Study
s=Study(D/'inputs/a');z=np.load(D/'baseline-arrays.npz');print('ARRAY_KEYS '+str(z.files),flush=True);primary=json.loads((D/'verification.json').read_text());assert primary['primary_adopts_source_and_scoring_epoch'] and primary['new_verified_count']==0
# Freeze every cohort from the original protocol: foreground guard half-open; glass exclusion inclusive.
yy,xx=np.mgrid[160:218,720:778];fg=(xx>=737)&(xx<757)&(yy>=178)&(yy<198);oldm=np.load(B/'baseline-native-arrays.npz');masks=dict(glass=s.valid,rim=s.rim,held=s.held,interior=s.valid&~s.rim,SSIM_safe=cv2.erode(s.valid.astype(np.uint8),np.ones((11,11),np.uint8))>0,glyph=fg,exterior=oldm['exterior_mask'],full_visible_exterior=oldm['full_visible_exterior_mask']);assert int(fg.sum())==400
np.savez_compressed(D/'canonical-masks-FIRST.npz',**masks)
rec=json.loads((src/'baseline-recipe-NOT-ADOPTED.json').read_text());rec.update(stage='PRIMARY_ADOPTED_EPOCH02_BASELINE_COUNT0',epoch='02-original-SF-default400-full-canvas',scores=json.loads((D/'baseline-scores.json').read_text()),accepted_count=0,old_epoch_count=1,adoption_authority='b5950fa8-6bb9-46c9-ada3-891a9b153b88',foreground_guard='Half-open20x20paint400; inclusiveexclusion441NOTglyphguard');(D/'baseline-recipe.json').write_text(json.dumps(rec,indent=2)+'\n')
proof=json.loads((R/'default400-source/review.json').read_text())['source_support'];(D/'source-support-transfer-FIRST.json').write_text(json.dumps(proof,indent=2)+'\n');report=dict(stage='EPOCH02_FROZEN_BEFORE_GRAY_RECALIBRATION',frozen_at=datetime.datetime.now(datetime.timezone.utc).isoformat(),case_fingerprint=hashlib.sha256(json.dumps(s.case,sort_keys=True).encode()).hexdigest(),mask_counts={n:int(m.sum()) for n,m in masks.items()},primary_arrays_sha256=hashlib.sha256((D/'baseline-arrays.npz').read_bytes()).hexdigest(),body_renders=0,new_epoch_count=0,old_epoch_count=1,no_cross_epoch_gain=True,old_source_case_immutable=True);(D/'freeze-FIRST.json').write_text(json.dumps(report,indent=2)+'\n');print(json.dumps(report),flush=True)
