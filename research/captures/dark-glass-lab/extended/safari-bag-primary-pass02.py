from pathlib import Path
import json,hashlib,copy,cv2,numpy as np
from extended_fit import Study
from settled import render
from vector_revision import composite
cv2.setNumThreads(1)
R=Path('/evidence/extended/helper-toolbar-work/safari-right-circle-round');B=R/'neutral-baseline';D=R/'neutral-additive-round2';O=Path('/evidence/extended/safari-bag-primary-pass02');assert not O.exists();O.mkdir()
s=Study(B/'inputs/a');base=json.loads((B/'baseline-recipe.json').read_text());r=json.loads((D/'candidate-native.json').read_text());assert hashlib.sha256(json.dumps(s.case,sort_keys=True).encode()).hexdigest()==base['case_sha256']['a']==r['case_sha256']['a']
for name,digest in s.case['source_sha256'].items():assert hashlib.sha256((B/'inputs/a'/name).read_bytes()).hexdigest()==digest
p=copy.deepcopy(base['preset']);co=np.zeros(23);co[:3]=co[-3:]=1;co[3:6]=.05;p['material']=co.tolist();assert p==r['preset'] and r['g']==1 and r['b']==.05
for name in ['settled.py','vector_revision.py','extended_fit.py']:
 assert (B/'code'/name).read_bytes()==(Path('/workspace/docs/liquid-glass/experiments/reconstruction')/name).read_bytes(),name
M=render(s.source,s.case,p,samples=2);C=composite(s,p,M);a=np.load(D/'candidate-native.npz');assert np.array_equal(M,a['material']) and np.array_equal(C,a['complete']);old=np.load(B/'baseline-native-arrays.npz');q=s.scores(M);q['E']=float(np.sqrt(q['loss']));e=(M.astype(float)-s.target_crop.astype(float))*255;q['advisory_f64_E']=float(np.sqrt(.7*np.mean(e[s.valid]**2)+.3*np.mean(e[s.rim]**2)))
for n,k in [('glyph','glyph_mask'),('exterior','exterior_mask'),('full_visible_exterior','full_visible_exterior_mask')]:m=old[k];q[n]=dict(pixels=int(m.sum()),rmse=float(np.sqrt(np.mean(((C-s.target_crop)[m]*255)**2))))
assert q==r['scores'];checks=json.loads((D/'trial-01.json').read_text())['checks'];assert all(checks.values());assert all(t['upper_clipped_channels']==t['lower_clipped_channels']==0 for t in r['clipping_counts'].values());v={'native_material_complete_pixel_exact':True,'scores_and_all_guards_exact':True,'frozen_case_source_and_code_exact':True,'sole_change_tied_RGB_additive_b':.05,'new_verified_pass':2,'E':q['E'],'accepted_primary':True,'source_observed_fraction':0,'limits':'Empirical neutral grading on estimated quadratic panel; no refraction/blur identification or Apple radiance model. Glyph/highlight residuals remain.'};(O/'verification.json').write_text(json.dumps(v,indent=2)+'\n');np.savez_compressed(O/'native-replay.npz',material=M,complete=C);print(json.dumps(v))
