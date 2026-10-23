"""Two fixed raw-transmission diagnostics. Preflight BOTH before any RGB sample."""
from pathlib import Path
import sys,json,time,hashlib
P=Path(__file__).resolve().parent;sys.path.insert(0,str(P/'code'))
import numpy as np,cv2
from PIL import Image,ImageDraw
from crowned_bevel import CrownedBevel
from geometric_optics import trace_flat_front_orthographic
from vector_foreground import _coverage
cv2.setNumThreads(1)
budget=json.loads((P/'experiment.json').read_text());deadline=budget['deadline_unix']
frozen=json.loads((P/'frozen-inputs.json').read_text());recipe=frozen['old_filtered_recipe']
inputs=Path('/tmp/agent-toolbar-evidence-package/inputs')
def sha(p):return hashlib.sha256(p.read_bytes()).hexdigest()
for name,rec in frozen['artifacts'].items():
    path=Path('/tmp/agent-toolbar-run/frozen-masks.npz') if name=='frozen-masks.npz' else inputs/name
    assert sha(path)==rec['sha256'],name
masks=np.load('/tmp/agent-toolbar-run/frozen-masks.npz')
registration=json.loads(Path('/tmp/agent-toolbar-run/input-audit.json').read_text())['registration']
A=np.array(registration['matrix'])
domain=cv2.warpAffine(np.ones((1080,1920),np.float32),A,(1920,1080),flags=cv2.INTER_LINEAR,borderMode=cv2.BORDER_CONSTANT)
contam=np.zeros((1080,1920),np.uint8);contam[350:790,490:1420]=1
estimated=cv2.warpAffine(contam,A,(1920,1080),flags=cv2.INTER_NEAREST)>0
observed=(domain==1)&~estimated
x0,y0,x1,y1=recipe['case']['crop'];H,W=y1-y0,x1-x0;L=170.;cx,cy=recipe['case']['center']
scored=np.logical_or.reduce([masks[k] for k in masks.files])
for layer in recipe['foreground_layers']:
    a,b,c,d=layer['box'];scored[b-y0:d-y0,a-x0:c-x0]=True
def guard():
    if time.time()>deadline:raise TimeoutError('Original 15-minute budget exhausted')
def save(name,obj):(P/name).write_text(json.dumps(obj,indent=2,allow_nan=False))
def metrics(C,T,mask):
    d=(C-T)[mask]*255.;l=d@np.array([.2126,.7152,.0722]);ch=d-d.mean(axis=-1,keepdims=True)
    return dict(pixels=int(mask.sum()),RGB_RMSE=float(np.sqrt(np.mean(d*d))),luma_RMSE=float(np.sqrt(np.mean(l*l))),chroma_RMSE=float(np.sqrt(np.mean(ch*ch))),signed_RGB=d.mean(axis=0).tolist())
if '--render' not in sys.argv:
    reports=[]
    for depth in [.02,.04]:
        guard();s=CrownedBevel(depth=depth);tag=f'{depth:.2f}'
        X=np.lib.format.open_memmap(P/f'X-{tag}.npy',mode='w+',dtype='float64',shape=(H*4,W*4))
        Y=np.lib.format.open_memmap(P/f'Y-{tag}.npy',mode='w+',dtype='float64',shape=(H*4,W*4))
        inside=np.lib.format.open_memmap(P/f'inside-{tag}.npy',mode='w+',dtype='bool',shape=(H*4,W*4))
        r={'depth':depth,'rays':0,'whole_inside_rays':0,'scored_rays':0,'scored_outside_outline_rays':0,'incomplete':0,'boundary_unresolved':0,'unsupported_texels':0,'unobserved_footprints':0,'bounds_min':[1e30,1e30],'bounds_max':[-1e30,-1e30],'minimum_domain_confidence':1.,'source_sampling_started':False}
        for top in range(0,H,12):
            guard();bot=min(H,top+12);yy,xx=np.mgrid[top*4:bot*4,:W*4]
            x=(x0+(xx+.5)/4-.5-cx)/L;y=(y0+(yy+.5)/4-.5-cy)/L
            out=trace_flat_front_orthographic(s,x,y,1.5,2.)
            u=out['X']*L+cx;v=out['Y']*L+cy
            r['rays']+=u.size;r['incomplete']+=int((~out['complete']).sum());r['boundary_unresolved']+=int(out['boundary_unresolved'].sum())
            if not np.isfinite(u).all() or not np.isfinite(v).all():
                r['status']='STOP_UNRESOLVED_PATH';save('preflight-failure.json',r);raise RuntimeError('Undefined actual path; stop before sampling')
            ix=np.floor(u).astype(int);iy=np.floor(v).astype(int)
            inbounds=(ix>=0)&(iy>=0)&(ix+1<1920)&(iy+1<1080)
            if not inbounds.all():
                r['status']='STOP_SOURCE_BOUNDS';r['unsupported_texels']=int((~inbounds).sum());save('preflight-failure.json',r);raise RuntimeError('Source texel out of domain; no clamp')
            confidence=np.minimum.reduce([domain[iy,ix],domain[iy,ix+1],domain[iy+1,ix],domain[iy+1,ix+1]])
            direct=observed[iy,ix]&observed[iy,ix+1]&observed[iy+1,ix]&observed[iy+1,ix+1]
            sm=np.repeat(np.repeat(scored[top:bot],4,axis=0),4,axis=1)
            r['whole_inside_rays']+=int(out['inside'].sum());r['scored_rays']+=int(sm.sum());r['scored_outside_outline_rays']+=int((sm&~out['inside']).sum())
            r['unobserved_footprints']+=int((~direct).sum());r['minimum_domain_confidence']=min(r['minimum_domain_confidence'],float(confidence.min()))
            r['unsupported_texels']+=int((confidence!=1).sum())
            r['bounds_min']=np.minimum(r['bounds_min'],[u.min(),v.min()]).tolist();r['bounds_max']=np.maximum(r['bounds_max'],[u.max(),v.max()]).tolist()
            if not np.all(confidence==1):
                r['status']='STOP_UNDEFINED_REGISTERED_DOMAIN';save('preflight-failure.json',r);raise RuntimeError('Original registered domain undefined; no extension')
            X[top*4:bot*4]=u;Y[top*4:bot*4]=v;inside[top*4:bot*4]=out['inside']
        X.flush();Y.flush();inside.flush();r['status']='ALL_ACTUAL_PATHS_AND_FOUR_TEXELS_DEFINED';reports.append(r);save(f'preflight-{tag}.json',r)
        print(json.dumps(r),flush=True)
    save('preflight-BOTH-FIRST.json',{'status':'BOTH_PASS_BEFORE_RGB_SAMPLING','observations':reports,'source_sigma':0,'post_sigma':0,'finite_kernel':'Exact four floor/floor+1 bilinear texels; no additional filter','domain':'Full-confidence warped original donor domain; modeled paper retained; observed false is disclosed, not filled','registration':registration,'source_sha256':sha(inputs/'source.png'),'mask_sha256':sha(Path('/tmp/agent-toolbar-run/frozen-masks.npz'))})
    sys.exit(0)
proof=json.loads((P/'preflight-BOTH-FIRST.json').read_text());assert proof['status']=='BOTH_PASS_BEFORE_RGB_SAMPLING'
assert not (P/'render-started.json').exists(),'Inspect partials; never duplicate an already-started image'
save('render-started.json',{'at':time.time(),'depths':[.02,.04]})
source=np.asarray(Image.open(inputs/'source.png'),float)/255.;target=np.asarray(Image.open(inputs/'target.png'),float)[y0:y1,x0:x1]/255.
historical=np.load('/evidence/extended/toolbar-response-primary-review/complete.npy')
historicalM=np.load('/evidence/extended/toolbar-response-primary-review/material.npy')
def rgb(a):return np.uint8(np.rint(np.clip(a,0,1)*255))
def gallery(arrays,names,name):
    canvas=Image.new('RGB',(arrays[0].shape[1]*len(arrays),arrays[0].shape[0]+32),'white');draw=ImageDraw.Draw(canvas)
    for i,(a,n) in enumerate(zip(arrays,names)):
        canvas.paste(Image.fromarray(rgb(a)),(i*a.shape[1],32));draw.text((i*a.shape[1]+8,8),n,fill='black')
    canvas.save(P/name)
report={'classification':'FIXED_GEOMETRIC_DIAGNOSTICS_NOT_ACCEPTED_FIDELITY','source_uncertainty':'Estimated blank paper/unknown hidden text remains; direct-observation footprint fractions in preflight, not source truth','shadow':'ZERO generated shadow/highlights in new diagnostics; historical control retains its original shading/shadow/filter','source_sigma':0,'post_sigma':0,'metrics':{},'crop_rectangles':{'upper':[650,369,1270,468],'d-stroke':[960,468,1120,550],'underside':[650,650,1270,726]}}
for depth in [.02,.04]:
    guard();tag=f'{depth:.2f}';X=np.load(P/f'X-{tag}.npy',mmap_mode='r');Y=np.load(P/f'Y-{tag}.npy',mmap_mode='r');inside=np.load(P/f'inside-{tag}.npy',mmap_mode='r')
    M=np.zeros((H,W,3),float);alpha=np.zeros((H,W),float)
    for top in range(0,H,12):
        guard();bot=min(top+12,H);u=X[top*4:bot*4];v=Y[top*4:bot*4];ix=np.floor(u).astype(int);iy=np.floor(v).astype(int);fx=(u-ix)[...,None];fy=(v-iy)[...,None]
        C=(source[iy,ix]*(1-fx)+source[iy,ix+1]*fx)*(1-fy)+(source[iy+1,ix]*(1-fx)+source[iy+1,ix+1]*fx)*fy
        M[top:bot]=C.reshape(bot-top,4,W,4,3).mean((1,3));alpha[top:bot]=inside[top*4:bot*4].reshape(bot-top,4,W,4).mean((1,3))
    C=M.copy()
    for layer in recipe['foreground_layers']:
        raw=(inputs/layer['asset']).read_bytes();assert hashlib.sha256(raw).hexdigest()==layer['sha256']
        A=_coverage(raw,tuple(recipe['case']['crop']),tuple(layer['placement']),1)
        C=C*(1-A[...,None])+np.array(layer['color'])*A[...,None]
    np.save(P/f'material-{tag}.npy',M);np.save(P/f'complete-{tag}.npy',C);np.save(P/f'alpha-{tag}.npy',alpha)
    Image.fromarray(rgb(C)).save(P/f'native-{tag}.png')
    gallery([target,historical,C],['Reference','Historical FILTERED baseline',f'Geometry depth {tag}: RAW/no shadow'],f'full-gallery-{tag}.png')
    item={'glass':metrics(M,target,masks['glass']),'rim':metrics(M,target,masks['rim']),'held':metrics(M,target,masks['held']),'exterior':metrics(C,target,masks['exterior']),'full':metrics(C,target,np.ones((H,W),bool)),'crops':{}}
    for name,box in report['crop_rectangles'].items():
        a,b,c,d=box;sl=np.s_[b-y0:d-y0,a-x0:c-x0];mask=np.zeros((H,W),bool);mask[sl]=True
        item['crops'][name]={'historical':metrics(historical,target,mask),'new':metrics(C,target,mask)}
        gallery([target[sl],historical[sl],C[sl]],['Reference','Historical filtered',f'Unblurred depth {tag}'],f'crop-{name}-{tag}.png')
    report['metrics'][tag]=item
    # Actual same-function sections and corresponding interior ray segments.
    s=CrownedBevel(depth=depth);sx=np.linspace(-s.half[0],s.half[0],401);sy=np.linspace(-.999,.999,401)
    sections={axis:s.section(v,axis) for axis,v in [('x',sx),('y',sy)]}
    rx=np.linspace(-s.half[0]*.98,s.half[0]*.98,31);ry=np.zeros_like(rx);rays=trace_flat_front_orthographic(s,rx,ry,1.5,2.)
    np.savez(P/f'actual-sections-rays-{tag}.npz',x_front=sections['x']['front'],x_back=sections['x']['back'],y_front=sections['y']['front'],y_back=sections['y']['back'],ray_back=rays['back'],ray_exit=rays['exit_direction'],source_xy=np.stack([rays['X'],rays['Y']],-1),complete=rays['complete'])
    save('measurements.json',report);print(json.dumps({'depth':depth,'glass':item['glass'],'rim':item['rim']}),flush=True)
report['finished_unix']=time.time();report['native_images']=2;save('measurements.json',report)
