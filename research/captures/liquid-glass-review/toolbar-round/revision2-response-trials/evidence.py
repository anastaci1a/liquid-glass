"""Fresh candidate diagnostics/crops; no fitting, no pass count."""
import sys,json,copy,hashlib
from pathlib import Path
sys.path.insert(0,'/tmp/agent-toolbar-code')
import numpy as np
import cv2
from PIL import Image,ImageDraw
import toolbar_response as model
from vector_foreground import _coverage
from progress_gate import error
import importlib.util
spec=importlib.util.spec_from_file_location('trial_control',str(Path(__file__).parent/'control-and-first.py'));driver=importlib.util.module_from_spec(spec);spec.loader.exec_module(driver)
cv2.setNumThreads(1)
root=driver.root;pkg=driver.pkg;p=driver.p;case=driver.case;q=json.loads((root/'first-proposal/recipe.json').read_text());trial=json.loads((root/'first-proposal/measurement.json').read_text());assert trial['numerical_qualifier'];assert trial['model_sha256']==hashlib.sha256(Path(model.__file__).read_bytes()).hexdigest();source=driver.source;target=np.asarray(Image.open(pkg/'inputs/target.png'),float)/255;out=root/'fresh-evidence';out.mkdir(exist_ok=True)
def write(path,x):path.write_text(json.dumps(x,indent=2,allow_nan=False)+'\n')
# Inherited source proof applies to ALL full-native/HQ rays because the inverse
# map, source arrays, source width/transition and sample coordinates are identical.
for key in ['shape','parameters','footprint_softness','source_sigma','blur_transition','post_sigma','case','foreground_layers','shadow','source_sha256']:assert q[key]==p[key]
proof={'unchanged_geometry_and_sampling_verified':True,'unchanged_source_target_hashes':q['source_sha256'],'map_code_sha256':hashlib.sha256(Path('/tmp/agent-toolbar-code/toolbar_candidate.py').read_bytes()).hexdigest(),'inherited_full_HQ_domain_proof':json.loads((pkg/'primary-verification.json').read_text())['source_support'],'finite_source_Gaussian_radius_native_px':44,'bilinear_margin_native_px':1,'source_confidence':'DEFINED input, NOT all observed truth; partly estimated hidden background. Source23 NOT adopted. No new optical query/dispersion/kernel introduced.','fresh_crop_emitted_ray_proofs':{}}
for layer in p['foreground_layers']:
    assert hashlib.sha256((pkg/'inputs'/layer['asset']).read_bytes()).hexdigest()==layer['sha256']
# Fresh native8 diagnostic is separate from frozen4x4 gate.
diag=out/'native8';diag.mkdir(exist_ok=True)
if not (diag/'measurement.json').exists():
    C,a=model.render(source,case,q,samples=8,checkpoint=diag);sc,fg,full,crops=driver.measure(C,a);np.save(diag/'complete.npy',full);old_diag=json.loads((pkg/'primary-verification.json').read_text())['diagnostic_scores'];write(diag/'measurement.json',{'candidate_E_diagnostic':error(sc),'candidate_scores':sc,'candidate_foreground':fg,'candidate_crops':crops,'baseline_saved8_glass':old_diag['all_glass'],'baseline_saved8_rim':old_diag['rim'],'gate_uses_original4x4_only':True});print('NATIVE8_DIAGNOSTIC29',error(sc),flush=True)
for name,box in {'upper':[650,369,1270,435],'d':[960,450,1120,550],'underside':[650,650,1270,726]}.items():
    folder=out/name;folder.mkdir(exist_ok=True);a0,b0,c0,d0=box;local=copy.deepcopy(case);local['crop']=[a0-12,b0-12,c0+12,d0+12];hq,alpha=model.render(source,local,q,scale=4,checkpoint=folder/'candidate-render');sl=(slice(48,48+(d0-b0)*4),slice(48,48+(c0-a0)*4));C=hq[sl];a=alpha[sl];np.save(folder/'candidate-hq-material.npy',C);np.save(folder/'hq-alpha.npy',a)
    # Upper/underside baseline HQ float arrays already exist from queue9's
    # exact padded recovery; use them, never repeat those completed tests.
    if name in ['upper','underside']:
        basepath=root/'reused-baseline-HQ'/f'{name}-hq4x-material.npy';base=np.load(basepath);ba=np.load(basepath.with_name(f'{name}-hq4x-alpha.npy'));assert np.array_equal(a,ba);baseline_origin='Immutable queue9 accepted-rev2 HQ arrays; checksums in reused-baseline-manifest.json'
    else:
        bp=folder/'baseline-material.npy'
        if bp.exists():base=np.load(bp)
        else:bc,ba=model.baseline.render(source,local,p,scale=4);base=bc[sl];np.save(bp,base);assert np.array_equal(a,ba[sl])
        baseline_origin='One fresh accepted d-crop HQ render; no identical saved baseline crop found'
    yy,xx=np.mgrid[:a.shape[0],:a.shape[1]];X=a0+(xx+.5)/4-.5;Y=b0+(yy+.5)/4-.5;B=cv2.remap(source,X.astype(np.float32),Y.astype(np.float32),cv2.INTER_LINEAR);displaycase=copy.deepcopy(case);displaycase['crop']=box;shadow=model.baseline.gaussian_coverage_shadow(displaycase,p,scale=4)
    def composite(material):
        full=material*a[...,None]+B*(1-shadow[...,None])*(1-a[...,None])
        for layer in p['foreground_layers']:
            left,top,right,bottom=layer['box'];x0=max(left,a0);y0=max(top,b0);x1=min(right,c0);y1=min(bottom,d0)
            if x0>=x1 or y0>=y1:continue
            aa=_coverage((pkg/'inputs'/layer['asset']).read_bytes(),tuple(layer['box']),tuple(layer['placement']),4);aa=aa[(y0-top)*4:(y1-top)*4,(x0-left)*4:(x1-left)*4,None];sl2=(slice((y0-b0)*4,(y1-b0)*4),slice((x0-a0)*4,(x1-a0)*4));full[sl2]=full[sl2]*(1-aa)+np.asarray(layer['color'])*aa
        return full
    candidate=composite(C);baseline=composite(base);ref=cv2.resize(target[b0:d0,a0:c0],(a.shape[1],a.shape[0]),interpolation=cv2.INTER_NEAREST);sheet=Image.new('RGB',(a.shape[1]*3,a.shape[0]+32),'#202020');draw=ImageDraw.Draw(sheet)
    for i,(label,I) in enumerate([('Native reference enlarged4x',ref),('Accepted rev2 HQ',baseline),('Unaccepted gamma/common-material candidate',candidate)]):sheet.paste(Image.fromarray(np.uint8(np.rint(np.clip(I,0,1)*255))),(i*a.shape[1],32));draw.text((i*a.shape[1]+5,8),label,fill='white')
    sheet.save(folder/'comparison.png');Image.fromarray(np.uint8(np.rint(np.clip(candidate,0,1)*255))).save(folder/'candidate-complete.png')
    # Check every actual emitted HQ source coordinate for this padded crop,
    # including unscored exterior rays; ordinary finite filter+bilinear margin.
    l,t,r,b=local['crop'];Lo=min(case['half']);lo=np.full(2,np.inf);hi=np.full(2,-np.inf);count=0
    for row in range(0,(b-t)*16,32):
        end=min(row+32,(b-t)*16);ys,xs=np.mgrid[row:end,0:(r-l)*16];x=(l+(xs+.5)/16-.5-case['center'][0])/Lo;y=(t+(ys+.5)/16-.5-case['center'][1])/Lo;fx,fy=model.baseline.mapping(x,y,p);fx=(fx*Lo+case['center'][0]).astype(np.float32);fy=(fy*Lo+case['center'][1]).astype(np.float32);lo=np.minimum(lo,[fx.min(),fy.min()]);hi=np.maximum(hi,[fx.max(),fy.max()]);count+=fx.size
    margin=float(min(lo[0],lo[1],1919-hi[0],1079-hi[1])-45);assert margin>0;proof['fresh_crop_emitted_ray_proofs'][name]={'padded_crop':local['crop'],'scale':4,'samples':4,'emitted_coordinate_pairs':count,'bounds_min':lo.tolist(),'bounds_max':hi.tolist(),'finite_source_kernel44_plus_bilinear1_margin_native_px':margin,'all_defined':True,'baseline_HQ_origin':baseline_origin};write(out/'source-verification.json',proof);print('HQ29',name,margin,flush=True)
print('EVIDENCE29_COMPLETE',flush=True)
