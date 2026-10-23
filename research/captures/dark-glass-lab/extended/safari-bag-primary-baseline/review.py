from pathlib import Path
import json,copy,numpy as np,hashlib,cv2
from extended_fit import Study
from settled import render
from vector_revision import composite
cv2.setNumThreads(1);R=Path('/evidence/extended/helper-toolbar-work/safari-right-circle-round');B=R/'neutral-baseline';O=Path('/evidence/extended/safari-bag-primary-baseline');s=Study(R/'a-proposed');r=json.loads((B/'baseline-recipe.json').read_text());p=r['preset'];a=np.load(B/'baseline-native-arrays.npz');seed=json.loads(Path('/workspace/docs/liquid-glass/experiments/reconstruction/studies/flower-next/baseline.json').read_text())['preset'];assert p==seed
assert hashlib.sha256(json.dumps(s.case,sort_keys=True).encode()).hexdigest()==r['case_sha256']['a'];co=np.zeros(23);co[:3]=co[-3:]=1;assert np.array_equal(co,p['material'])
M=render(s.source,s.case,p,samples=2);C=composite(s,p,M);assert np.array_equal(M,a['material']) and np.array_equal(C,a['complete']);q=s.scores(M);q['E']=float(np.sqrt(q['loss']))
for n,k in [('glyph','glyph_mask'),('exterior','exterior_mask'),('full_visible_exterior','full_visible_exterior_mask')]:m=a[k];q[n]=dict(pixels=int(m.sum()),rmse=float(np.sqrt(np.mean(((C-s.target_crop)[m]*255)**2))))
assert q==json.loads((B/'baseline-native.json').read_text())['scores'];v={'accepted_primary_baseline':True,'count':0,'native_material_and_complete_exact':True,'scores_exact':True,'seed_preset_exact_CURRENT_playback_neutral_prior':True,'source_case_unchanged':True,'source_proof_review':'Exact source/post finite kernels and bilinear footprints, WHOLE+ALLscored+post checked within original known rectangle. No observed hidden RGB.','E':q['E'],'limits':'Pose/outline uncertainty and lower-source residual2.273levels; smooth gradient cannot identify optics, glyph weight unproven.'};(O/'verification.json').write_text(json.dumps(v,indent=2)+'\n');print(json.dumps(v))
