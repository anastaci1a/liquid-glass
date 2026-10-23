"""Queue10 evidence: saved native directions only; no renderer/fit call."""
import json,hashlib
from pathlib import Path
import numpy as np
from PIL import Image
out=Path('/tmp/agent-toolbar-revision2-sensitivity');out.mkdir(exist_ok=True)
root=Path('/tmp/agent-toolbar-evidence-package');p=json.loads((root/'recipe.json').read_text());C=np.load('/tmp/agent-toolbar-inner-settlement/material.npy');T=np.asarray(Image.open(root/'inputs/target.png'),np.float32)[285:845,475:1445]/255
files={'outer_derivatives':'/tmp/agent-toolbar-revision2-outer-fit/baseline-outer-derivatives.npz','rev1_material':'/tmp/agent-toolbar-run/candidate-with-shadow-material.npy','tangent_material':'/tmp/agent-toolbar-revision2-tangent/seed-1/material.npy','blur_material':'/tmp/agent-toolbar-revision2-blur/best-raw/material.npy'}
outer=np.load(files['outer_derivatives'])['derivative'].astype(float)
inner=(C-np.load(files['rev1_material'])).astype(float)
tangent=(np.load(files['tangent_material'])-C).astype(float)
blur=(np.load(files['blur_material'])-C).astype(float)
directions=np.concatenate([outer,inner[None],tangent[None],blur[None]],axis=0)*255
names=['outer_c0','outer_c1','outer_c2','outer_c3','inner_accepted_secant','tangent_rejected_secant','blur_rejected_secant']
masks=np.load('/tmp/agent-toolbar-run/frozen-masks.npz');cohorts=np.load('/tmp/agent-toolbar-revision2-identifiability/support-cohorts.npz');R=(C.astype(float)-T)*255
yy,xx=np.mgrid[:C.shape[0],:C.shape[1]];xs=xx+475;ys=yy+285

def evidence(mask,weighted=False):
    count=int(mask.sum())
    if not count:return {'pixels':0}
    if weighted:
        A=np.concatenate([directions[:,masks['glass']].reshape(7,-1)*np.sqrt(.7/(3*masks['glass'].sum())),directions[:,masks['rim']].reshape(7,-1)*np.sqrt(.3/(3*masks['rim'].sum()))],axis=1).T
        desired=np.concatenate([-R[masks['glass']].ravel()*np.sqrt(.7/(3*masks['glass'].sum())),-R[masks['rim']].ravel()*np.sqrt(.3/(3*masks['rim'].sum()))])
    else:A=directions[:,mask].reshape(7,-1).T/np.sqrt(3*count);desired=-R[mask].ravel()/np.sqrt(3*count)
    G=A.T@A;norms=np.sqrt(np.maximum(np.diag(G),0));den=norms[:,None]*norms[None,:];correlation=np.divide(G,den,out=np.zeros_like(G),where=den>1e-20)
    active=norms>1e-8;unit_gram=correlation[np.ix_(active,active)];values=np.linalg.eigvalsh(unit_gram);singular=np.sqrt(np.maximum(values,0))[::-1]
    projections=np.divide(A.T@desired,norms*np.linalg.norm(desired),out=np.zeros(7),where=norms>1e-20)
    explain={}
    for k,name in enumerate(names):
        idx=[i for i in range(7) if i!=k and active[i]]
        if norms[k]<=1e-8:explain[name]=None;continue
        coeff=np.linalg.pinv(G[np.ix_(idx,idx)],rcond=1e-10)@G[idx,k];fraction=float(coeff@G[idx,k]/G[k,k]);explain[name]={'squared_direction_energy_explained_by_other_saved_directions':float(np.clip(fraction,0,1)),'coefficients_in_saved_basis':dict(zip([names[i] for i in idx],coeff.tolist()))}
    return {'pixels':count,'direction_names':names,'active_directions':dict(zip(names,map(bool,active))),'direction_weighted_RMS':norms.tolist(),'Gram':G.tolist(),'cosine_matrix':correlation.tolist(),'zero_energy_direction_note':'Zero cosine placeholders for inactive columns are not orthogonality evidence','cosine_to_desired_correction':projections.tolist(),'unit_direction_singular_values':singular.tolist(),'numerical_unit_direction_rank':int((singular>max(singular[0]*1e-6,1e-8)).sum()) if len(singular) else 0,'leave_one_direction_out':explain,'weighted_gate_geometry':weighted}

regions={'whole_gate_weighted':evidence(masks['glass'],True)}
for name,box in {'full-glass':None,'upper-rim':[650,369,1270,435],'d-stroke':[960,450,1120,550],'underside':[650,650,1270,726]}.items():
    region=np.ones(C.shape[:2],bool) if box is None else (xs>=box[0])&(xs<box[2])&(ys>=box[1])&(ys<box[3])
    regions[name]={cohort:evidence(region&cohorts[cohort]) for cohort in ['all','observed_kernel_proxy','estimated_kernel_proxy','mixed_or_uncertain']}
report={'accepted_commit':'bb1ee80131d39e7661c3d55174767c4d15182e05','source_files':{k:{'path':v,'sha256':hashlib.sha256(Path(v).read_bytes()).hexdigest()} for k,v in files.items()},'directions':names,'regions':regions,'limits':['No optical render/fit, pixel/source/mask/registration/epoch change or new pass','Outer0–3 are native central finite derivatives at h=.002; sampled raster derivative not analytic physical optics','Inner is accepted rev1→rev2 material secant with only inner4–6 changed; sign/span is historical, not a current gradient','Tangent and blur are aggregate same-baseline rejected fitted secants, not independent parameter Jacobians or blind validation','Unit direction Gram/singular values measure degeneracy of these saved image directions only, not full model identifiability','Unsupported cohorts/crops remain in original gate; this review never promotes a subset to a new score mask','Float64 diagnostic linear algebra does not replace frozen float32 native E']}
(out/'evidence.json').write_text(json.dumps(report,indent=2,allow_nan=False)+'\n')
G=regions['whole_gate_weighted'];print(json.dumps({'names':names,'global_cosines':G['cosine_matrix'],'singular_values':G['unit_direction_singular_values'],'explainability':{n:v['squared_direction_energy_explained_by_other_saved_directions'] if v else None for n,v in G['leave_one_direction_out'].items()}},indent=2),flush=True)
