"""Independent public-renderer replay and material-only ablation; no fitting."""
import sys,json,hashlib,copy
from pathlib import Path
sys.path.insert(0,'/workspace/docs/liquid-glass/experiments/reconstruction')
import numpy as np,cv2
from PIL import Image
import crowned_tensor
from tensor_replay import composite
cv2.setNumThreads(1)
root=Path('/evidence/extended');out=root/'toolbar-response-primary-review';original=Path('/tmp/agent-toolbar-evidence-package/inputs')
proposal=root/'helper-toolbar-work/agent-toolbar-response-trials/first-proposal'
base=json.loads(Path('/workspace/docs/liquid-glass/experiments/reconstruction/studies/archive-plus/review-round/pass-02.json').read_text());p=json.loads((proposal/'recipe.json').read_text());case=p['case']
for name,h in base['source_sha256'].items():assert hashlib.sha256((original/name).read_bytes()).hexdigest()==h
expected=copy.deepcopy(base);expected['model']=p['model'];expected['intensity_response']=p['intensity_response'];co=np.asarray(expected['material']);co[:3]+=.006;co[3:6]+=.003;co[-3:]+=.006;expected['material']=co.tolist();assert expected==p
source=np.asarray(Image.open(original/'source.png'),float)/255;target=np.asarray(Image.open(original/'target.png'),np.float32)/255;a,b,c,d=case['crop'];T=target[b:d,a:c];masks=np.load('/tmp/agent-toolbar-run/frozen-masks.npz')
def metrics(full,material):
 sc={n:float(np.sqrt(np.mean(((material-T)[masks[n]]*255)**2))) for n in ['glass','rim']};sc['E']=float(np.sqrt(.7*sc['glass']**2+.3*sc['rim']**2));sc['exterior']=float(np.sqrt(np.mean(((full-T)[masks['exterior']]*255)**2)))
 for l in p['foreground_layers']:
  x0,y0,x1,y1=l['box'];sc[l['name']]=float(np.sqrt(np.mean((full[y0-b:y1-b,x0-a:x1-a]-T[y0-b:y1-b,x0-a:x1-a])**2))*255)
 return sc
shade=crowned_tensor.shade;gamma=p['intensity_response']['gamma']
try:
 crowned_tensor.shade=lambda C,J,co:shade(np.maximum(C,0.)**gamma,J,co)
 full,material,alpha=composite(source,case,p,original)
finally:crowned_tensor.shade=shade
np.save(out/'complete.npy',full);np.save(out/'material.npy',material);np.save(out/'alpha.npy',alpha)
diff=float(np.max(abs(material-np.load(proposal/'material.npy'))));full_diff=float(np.max(abs(full-np.load(proposal/'complete.npy'))));assert diff<2e-7 and full_diff<2e-7,(diff,full_diff)
assert np.array_equal(alpha,np.load(proposal/'alpha.npy'))
sc=metrics(full,material);print('REPLAY',sc,'differences',diff,full_diff,flush=True)
Image.fromarray(np.uint8(np.rint(np.clip(full,0,1)*255))).save(out/'public-replay.png')
# Existing renderer ignores the proposed response key: this is deliberately
# the exact same common-material offsets without the new power operation.
no_power,mat,_=composite(source,case,p,original);abl=metrics(no_power,mat)
Image.fromarray(np.uint8(np.rint(np.clip(no_power,0,1)*255))).save(out/'material-only.png')
record=dict(method=__doc__,candidate_sha256=hashlib.sha256((proposal/'recipe.json').read_bytes()).hexdigest(),changes_verified_exact=True,public_material_max_difference=diff,public_complete_max_difference=full_diff,coverage_exact=True,scores=sc,material_only_ablation=abl,accepted=False,limits='One empirical shared power/common-material proposal; source and illumination response remain confounded. Native replay does not imply visual acceptance or identified Apple physics. No additional fit or optical pass.')
with (out/'verification.json').open('x') as f:json.dump(record,f,indent=2)
print('FINAL',json.dumps(record),flush=True)
