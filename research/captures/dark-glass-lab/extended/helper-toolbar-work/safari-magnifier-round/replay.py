"""Independent frozen single-A baseline replay. Never fits or overwrites evidence.
python replay.py --root /evidence/extended/helper-toolbar-work/safari-magnifier-round --output /evidence/extended/safari-primary-baseline-review
The primary may instead prepend a separately committed public reconstruction folder with --code.
"""
import argparse,json,sys,hashlib
from pathlib import Path
import numpy as np
ap=argparse.ArgumentParser();ap.add_argument('--root',type=Path,required=True);ap.add_argument('--output',type=Path,required=True);ap.add_argument('--code',type=Path);args=ap.parse_args();R=args.root;assert not args.output.exists(),'Preserve prior independent review';args.output.mkdir(parents=True)
sys.path.insert(0,str(args.code or R/'code'))
import cv2
cv2.setNumThreads(1)
from extended_fit import Study
from vector_revision import composite
rec=json.loads((R/'baseline-recipe.json').read_text());s=Study(R/'a');assert hashlib.sha256(json.dumps(s.case,sort_keys=True).encode()).hexdigest()==rec['case_sha256']['a'];M=s.render(rec['parameters'],np.asarray(rec['material']));C=composite(s,rec['parameters'],M);A=s.shape_coverage(rec['parameters']);old=np.load(R/'baseline-native-arrays.npz');checks={k:bool(np.array_equal(v,old[k])) for k,v in [('material',M),('complete',C),('alpha',A)]};assert all(checks.values()),checks
prior=json.loads((R/'baseline-native.json').read_text())['scores'];scores=s.scores(M);scores['E']=float(np.sqrt(scores['loss']))
for name,key in [('glyph','glyph_mask'),('exterior','exterior_mask')]:
 m=old[key];scores[name]=dict(pixels=int(m.sum()),rmse=float(np.sqrt(np.mean(((C-s.target_crop)[m]*255)**2))))
assert all(scores[k]==prior[k] for k in scores)
np.savez_compressed(args.output/'replayed-native.npz',material=M,complete=C,alpha=A)
out=dict(pixel_exact=checks,scores=scores,source_truth='MODELED affine gray field; hiddenobserved0, Bpending; no paired/optical-identification claim',guard_epoch='Frozen SINGLE A baseline proposal, not an accepted pass',optical_fits=0)
(args.output/'verification.json').write_text(json.dumps(out,indent=2)+'\n');print(json.dumps(out))
