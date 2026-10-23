"""Primary independent replay helper. Agent did NOTrun a repeated baseline.
--code may point to a separatelyfrozen committedpubliccode directory.
"""
import argparse,json,sys,hashlib
from pathlib import Path
import numpy as np
ap=argparse.ArgumentParser();ap.add_argument('--baseline',type=Path,required=True);ap.add_argument('--output',type=Path,required=True);ap.add_argument('--code',type=Path);args=ap.parse_args();R=args.baseline;assert not args.output.exists();args.output.mkdir(parents=True);sys.path.insert(0,str(args.code or R/'code'))
import cv2
cv2.setNumThreads(1)
from extended_fit import Study
from settled import render
from vector_revision import composite
s=Study(R/'inputs/a');rec=json.loads((R/'baseline-recipe.json').read_text());assert hashlib.sha256(json.dumps(s.case,sort_keys=True).encode()).hexdigest()==rec['case_sha256']['a'];p=rec['preset'];M=render(s.source,s.case,p,samples=2);C=composite(s,p,M);alpha=s.shape_coverage(p);old=np.load(R/'baseline-native-arrays.npz');check={k:bool(np.array_equal(v,old[k])) for k,v in [('material',M),('complete',C),('alpha',alpha)]};q=s.scores(M);q['E']=float(np.sqrt(q['loss']))
for n,k in [('glyph','glyph_mask'),('exterior','exterior_mask'),('full_visible_exterior','full_visible_exterior_mask')]:m=old[k];q[n]=dict(pixels=int(m.sum()),rmse=float(np.sqrt(np.mean(((C-s.target_crop)[m]*255)**2))))
expected=json.loads((R/'baseline-native.json').read_text())['scores'];v=dict(pixel_exact=check,score_exact=q==expected,scores=q,g=rec['g'],b=rec['b'],material_fits=0,pass_count=0,source_truth='Estimatedmodeledpanel/observed0; nativebaselineonly, no refraction/blur/dispersionvalidation');(args.output/'verification.json').write_text(json.dumps(v,indent=2)+'\n');np.savez_compressed(args.output/'native-replay.npz',material=M,complete=C,alpha=alpha);assert all(check.values()) and q==expected;print(json.dumps(v))
