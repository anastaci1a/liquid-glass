"""Primary independent replay helper; agent did NOT run another body/candidate."""
import argparse,json,sys,hashlib
from pathlib import Path
import numpy as np,cv2
ap=argparse.ArgumentParser();ap.add_argument('--baseline',type=Path,required=True);ap.add_argument('--candidate',type=Path,required=True);ap.add_argument('--output',type=Path,required=True);ap.add_argument('--code',type=Path);a=ap.parse_args();assert not a.output.exists();a.output.mkdir(parents=True);sys.path.insert(0,str(a.code or a.baseline/'code'));cv2.setNumThreads(1)
from extended_fit import Study
import neutral_rim
from vector_revision import composite
s=Study(a.baseline/'inputs/a');r=json.loads((a.candidate/'candidate-native.json').read_text());assert hashlib.sha256(json.dumps(s.case,sort_keys=True).encode()).hexdigest()==r['case_sha256']['a'];expected=np.load(a.candidate/'candidate-native.npz');old=np.load(a.baseline/'baseline-native-arrays.npz');audit={};M=neutral_rim.render(s.source,s.case,r['preset'],r['neutral_rim']['amplitude'],r['neutral_rim']['width'],samples=r['samples'],audit=audit)
original=s.case
try:s.case={**original,'foreground_styles':r['foreground_styles']};C=composite(s,r['preset'],M)
finally:s.case=original
checks=dict(material_exact=np.array_equal(M,expected['material']),complete_exact=np.array_equal(C,expected['complete']),body_unchanged=np.array_equal(M,old['material']),outside_glyph_unchanged=np.array_equal(C[~old['glyph_mask']],old['complete'][~old['glyph_mask']]),raw_helper_clip_zero=audit['clipped_channels']==0)
q=s.scores(M);q['E']=float(np.sqrt(q['loss']))
for name,key in [('glyph','glyph_mask'),('exterior','exterior_mask'),('full_visible_exterior','full_visible_exterior_mask')]:m=old[key];q[name]=dict(pixels=int(m.sum()),rmse=float(np.sqrt(np.mean(((C-s.target_crop)[m]*255)**2))))
checks['native_scores_exact']=q==r['scores'];assert all(checks.values());v=dict(checks={k:bool(x) for k,x in checks.items()},scores=q,actual_helper_audit=audit,foreground_only=True,optical_gain=False,source_hidden_observed_fraction=0,primary_visual_acceptance_still_required=True,accepted_count='PRIMARY_DECIDES_NOT_AUTOMATIC',limits='Canonicalpartialedgeadvisory worsens andthinSVGstyle remains; empiricalopaquegray only, no Appleopacity/radiance or pairedclaim.');(a.output/'verification.json').write_text(json.dumps(v,indent=2)+'\n');np.savez_compressed(a.output/'native-replay.npz',material=M,complete=C);print(json.dumps(v))
