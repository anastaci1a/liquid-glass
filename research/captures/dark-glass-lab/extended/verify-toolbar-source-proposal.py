"""Independent input construction and public-renderer replay; no fitting."""
import sys,json,hashlib,copy
from pathlib import Path
sys.path[:0]=['/workspace/docs/liquid-glass/experiments/reconstruction']
import numpy as np,cv2
from PIL import Image
from tensor_replay import composite
cv2.setNumThreads(1)
root=Path('/evidence/extended');out=root/'toolbar-source-primary-review'
proposal=root/'helper-toolbar-work/agent-toolbar-A-typography/input-proposal'
original=Path('/tmp/agent-toolbar-evidence-package/inputs')
public=Path('/workspace/docs/liquid-glass/experiments/reconstruction/studies/archive-plus/review-round/pass-02.json')
p=json.loads(public.read_text());manifest=json.loads((out/'input-proposal-manifest.json').read_text())
def digest(path):return hashlib.sha256(path.read_bytes()).hexdigest()
for name,h in p['source_sha256'].items():assert digest(original/name)==h
newpath=proposal/'source-typography-proposed.png';assert digest(newpath)==manifest['proposed_source_sha256']
source=np.asarray(Image.open(newpath),float)/255;old=np.asarray(Image.open(original/'source.png'),float)/255
target=np.asarray(Image.open(original/'target.png'),np.float32)/255
fields=np.load(proposal/'source-confidence.npz');mask=fields['typography_model_weight'];alpha=fields['known_font_ink_alpha']
assert mask.shape==alpha.shape==old.shape[:2] and mask.min()>=0 and mask.max()<=1
yy,xx=np.mgrid[:1080,:1920];X=(xx-960)/960;Y=(yy-540)/540
paper=np.clip(np.stack([X**i*Y**j for i in range(5) for j in range(5-i)],-1)@np.array(manifest['paper_field_reused_exact_coefficients']),0,1)
expected=np.rint(np.clip(old*(1-mask[...,None])+paper*(1-alpha[...,None])*mask[...,None],0,1)*255).astype(np.uint8)
assert np.array_equal(expected,np.asarray(Image.open(newpath)))
assert np.array_equal(source[mask==0],old[mask==0])
changed=int(np.any(source!=old,axis=-1).sum());assert changed==manifest['changed_pixels']
# Fix the proposal's hash serialization using the ORIGINAL public schema.
# The helper draft stored a string in this field; the replay CLI expects a map.
q=copy.deepcopy(p);q['source_sha256']['source.png']=digest(newpath)
with (out/'incumbent-with-proposed-input.json').open('x') as f:json.dump(q,f,indent=2)
full,material,coverage=composite(source,p['case'],q,original)
saved=np.load(proposal/'material.npy');savedfull=np.load(proposal/'complete.npy')
diff=float(np.max(abs(material-saved)));assert diff<2e-7,diff
full_diff=float(np.max(abs(full-savedfull)));assert full_diff<2e-7,full_diff
a,b,c,d=p['case']['crop'];T=target[b:d,a:c];masks=np.load('/tmp/agent-toolbar-run/frozen-masks.npz')
scores={name:float(np.sqrt(np.mean(((material-T)[masks[name]]*255)**2))) for name in ['glass','rim']}
E=float(np.sqrt(.7*scores['glass']**2+.3*scores['rim']**2))
control=np.s_[425:555,60:480]
def rmse(image):return float(np.sqrt(np.mean(((image-target)[control]*255)**2)))
record=dict(public_recipe_sha256=digest(public),source_sha256=digest(newpath),source_construction_byte_exact=True,changed_pixels=changed,unchanged_outside_model=True,public_material_max_difference=diff,public_complete_max_difference=full_diff,scores=scores,E=E,heldout_outside_control=dict(old=rmse(old),proposed=rmse(source)),schema_fix='Keep source_sha256 as a filename-to-digest mapping, not one string.',adopted=False,optical_passes=0,limits='Independent replay and heldout control support a source proposal, not exact hidden-source recovery. All replaced pixels remain estimated. Accepted scoring epoch/count/history remain unchanged pending source decision.')
with (out/'verification.json').open('x') as f:json.dump(record,f,indent=2)
Image.fromarray(np.uint8(np.rint(np.clip(full,0,1)*255))).save(out/'public-replay.png')
print(json.dumps(record),flush=True)
