"""One source-PSF comparison using retained G05 geometric queries.
Run from the repository root with reconstruction and dependencies on PYTHONPATH.
"""
import argparse, datetime, hashlib, json, time
from pathlib import Path
import cv2
import numpy as np
from PIL import Image, ImageDraw
from geometric_render import incident_source_filter
from reproduce import CASES, points, masks, scores
from settled import icon_color

ROOT = Path(__file__).resolve().parents[3]
OUT = Path(__file__).parent
WORK = ROOT / '.evidence-working/clear-play-02'
E = WORK / 'dark-glass-lab'
CAP = ROOT / 'research/captures/dark-glass-lab'
G = E / 'extended/geometric-playback-inferred'
B = E / 'extended/playback-pipeline-01/blurriness'
SOURCE = E / 'apple-matches/public-settled-replay'
case = CASES['media']
x0, y0, x1, y1 = case['crop']
H, W = y1-y0, x1-x0
L = min(case['half'])
SIGMAS = [1.25, 1.5, 1.7, 2., 2.5]
BOXES = {'bottom-left': [690,570,910,810], 'top-left': [690,290,910,530],
         'upper-right': [1025,320,1245,560], 'center-texture': [900,690,1040,755]}
cv2.setNumThreads(1)

def gate():
    p = json.loads((OUT/'protocol.json').read_text())
    deadline = datetime.datetime.fromisoformat(p['stages'][1]['deadline']).timestamp()
    if time.time() > deadline:
        raise RuntimeError('Declared source-blur deadline reached')

def write(name, data):
    (OUT/name).write_text(json.dumps(data, indent=2)+'\n')

def tile(path):
    q = np.load(path)
    X,Y = q['X'],q['Y']
    row = int(path.stem)
    stop = row + X.shape[0]//4
    yy,xx = np.mgrid[y0+row:y0+stop:.25,x0:x1:.25]
    inside = (xx-.375-case['center'][0])**2+(yy-.375-case['center'][1])**2 <= L*L
    return row,stop,X,Y,inside

def preflight():
    gate()
    if (OUT/'source-proof.json').exists():
        raise RuntimeError('Preserve completed preflight')
    reg = json.loads((CAP/'apple-matches/public-settled-replay/settled-scores.json').read_text())['media']['registration']
    inverse = np.linalg.inv(np.vstack([reg['matrix'],[0,0,1]]))
    yy,xx = np.mgrid[:1080,:1920]
    u = inverse[0,0]*xx + inverse[0,1]*yy + inverse[0,2]
    v = inverse[1,0]*xx + inverse[1,1]*yy + inverse[1,2]
    known = (u>=0)&(v>=0)&(u<1919)&(v<1079)
    support = cv2.erode(known.astype(np.uint8),np.ones((17,17),np.uint8),borderType=cv2.BORDER_CONSTANT,borderValue=0)>0
    xs,ys,dx,dy = points(case)
    sd,train,held,valid = masks(case,xs,ys,dx,dy)
    counts = dict(cached_crop_subrays=0,whole_body=0,original_scored=0,unsupported=0,nonfinite=0)
    coverage = np.zeros((H,W))
    for path in sorted((G/'queries').glob('*.npz')):
        gate();row,stop,X,Y,inside = tile(path)
        if not (np.isfinite(X).all() and np.isfinite(Y).all()):
            raise ValueError('Nonfinite retained query')
        a,b = np.floor(X).astype(int),np.floor(Y).astype(int)
        if not ((a>=0)&(b>=0)&(a+1<1920)&(b+1<1080)).all():
            raise ValueError('Undefined retained bilinear query')
        ok = np.ones(X.shape,bool)
        for ix,iy in [(0,0),(1,0),(0,1),(1,1)]:
            ok &= np.where(inside,support[b+iy,a+ix],known[b+iy,a+ix])
        counts['cached_crop_subrays'] += X.size
        counts['whole_body'] += int(inside.sum())
        counts['original_scored'] += int(valid[row:stop].sum())*16
        counts['unsupported'] += int((~ok).sum())
        coverage[row:stop] = inside.reshape(stop-row,4,W,4).mean((1,3))
    assert counts['unsupported']==0
    np.testing.assert_array_equal(coverage,np.load(B/'coverage.npy'))
    hashes = {n:hashlib.sha256((SOURCE/n).read_bytes()).hexdigest() for n in ['media-source.png','media-target.png']}
    expected = json.loads((ROOT/'reconstruction/studies/geometric-playback/g05.json').read_text())['source_hashes']
    assert hashes == expected
    np.save(WORK/'registered-known.npy',known)
    write('source-proof.json',dict(status='PASS_BEFORE_NEW_RGB_SAMPLING',**counts,
        source_hashes=hashes,maximum_source_sigma_pixels=2.5,finite_kernel_radius=8,
        texels='Every four bilinear corners with the complete 17x17 registered-source footprint for lens rays; original source for clear rays.',
        registered_domain='Every participating registered texel maps into the original donor frame with its bilinear margin.',
        coverage_exact=True,new_refraction_rays=0,observational_limits='Finite-domain support; no claim of exact hidden RGB, source PSF, registration or physical roughness.'))
    print(json.dumps(counts),flush=True)

def sample(src,X,Y):
    a,b = np.floor(X).astype(int),np.floor(Y).astype(int)
    fx,fy = (X-a)[...,None],(Y-b)[...,None]
    return (src[b,a]*(1-fx)+src[b,a+1]*fx)*(1-fy)+(src[b+1,a]*(1-fx)+src[b+1,a+1]*fx)*fy

def detail(im):
    lum=im@np.array([.2126,.7152,.0722],np.float32)
    band=(cv2.GaussianBlur(lum,(0,0),.5)-cv2.GaussianBlur(lum,(0,0),3))[8:-8,8:-8]*255
    return float(np.sqrt(np.mean(band**2)))

def compare():
    gate()
    if (OUT/'result.json').exists(): raise RuntimeError('Completed study cannot repeat')
    proof=json.loads((OUT/'source-proof.json').read_text())
    assert proof['unsupported']==0
    source=np.asarray(Image.open(SOURCE/'media-source.png'),float)/255
    target=np.asarray(Image.open(SOURCE/'media-target.png'),np.float32)/255
    ref=target[y0:y1,x0:x1]
    known=np.load(WORK/'registered-known.npy')
    baseline=np.load(B/'candidate-complete.npy')
    coverage=np.load(B/'coverage.npy');clear=np.load(B/'clear-premultiplied.npy')
    raw_lens=np.load(B/'raw-lens-material.npy')
    old_complete=np.load(G/'complete.npy')
    p=json.loads((CAP/'extended/playback-short-round/pass-03/replay-record.json').read_text())['recipe']
    oldM=np.load(E/'extended/playback-short-round/pass-03/candidate-material.npy')
    icon=icon_color(oldM,p['icon'],L)
    ia,ib,ic,id=[int(round(v*L+case['center'][k%2])) for k,v in enumerate(p['icon']['box_over_L'])]
    alpha=np.asarray(Image.open(ROOT/'reconstruction'/p['icon']['coverage']),float)/255
    def compose(M):
        C=(M*coverage[...,None]+clear).astype(np.float32)
        sl=np.s_[ib-y0:id-y0,ia-x0:ic-x0]
        C[sl]=C[sl]*(1-alpha[...,None])+icon[sl]*alpha[...,None]
        return C
    np.testing.assert_array_equal(compose(raw_lens),old_complete)
    xs,ys,dx,dy=points(case);sd,_,_,valid=masks(case,xs,ys,dx,dy)
    fg=np.zeros((H,W),bool)
    for a,b,c,d in case['foreground']:fg|=(xs>=a)&(xs<=c)&(ys>=b)&(ys<=d)
    assert fg.sum()==52998
    def metrics(C):
        sc=scores(C,ref,case);delta=(C-ref)*255
        sc['foreground_fullbox_MSE']=float(np.mean(delta[fg]**2))
        sc['exterior_MSE']=float(np.mean(delta[sd>0]**2))
        local={}
        for name,(a,b,c,d) in BOXES.items():
            q=C[b-y0:d-y0,a-x0:c-x0];t=target[b:d,a:c]
            local[name]={'RGB_RMSE':float(np.sqrt(np.mean(((q-t)*255)**2))),
                         'MAE':float(np.mean(abs(q-t))*255),'detail_band_RMS':detail(q),
                         'reference_detail_RMS':detail(t)}
        return sc,local
    base_scores,base_local=metrics(baseline)
    expected=json.loads((ROOT/'reconstruction/studies/geometric-playback/pipeline-01.json').read_text())['original_body_scores']
    assert base_scores==expected, 'Saved incumbent scoring must match the corrected original protocol'
    tiles=[tile(path) for path in sorted((G/'queries').glob('*.npz'))]
    # Independent zero check: 32 pixels at each of three fixed tiles.
    zero=[]
    for row,stop,X,Y,inside in [tiles[0],tiles[13],tiles[-1]]:
        q=sample(source,X[:4,:128],Y[:4,:128]);ii=inside[:4,:128]
        numerator=np.where(ii[...,None],q,0).reshape(1,4,32,4,3).mean((1,3))
        cov=coverage[row:row+1,:32,None]
        lens=np.divide(numerator,cov,out=np.zeros_like(numerator),where=cov>0)
        np.testing.assert_array_equal(lens,raw_lens[row:row+1,:32]);zero.append({'row':row,'pixels':32,'max_difference':0})
    write('native-zero-controls.json',{'cached_composition_exact':True,'original_scores_exact':True,'sampling_controls':zero,'new_refraction_rays':0})
    a,b,c,d=BOXES['center-texture'];goal=base_local['center-texture']['detail_band_RMS']
    rows=[]
    for sigma in SIGMAS:
        gate();filtered,support,radius=incident_source_filter(source,known,sigma)
        patch=np.zeros((d-b,c-a,3),np.float32)
        for row,stop,X,Y,inside in tiles:
            top=max(row,b-y0);end=min(stop,d-y0)
            if top>=end:continue
            sl=np.s_[4*(top-row):4*(end-row),4*(a-x0):4*(c-x0)]
            xx,yy=X[sl],Y[sl]
            assert inside[sl].all()
            value=sample(filtered,xx,yy)
            assert np.isfinite(value).all()
            patch[top-(b-y0):end-(b-y0)]=value.reshape(end-top,4,c-a,4,3).mean((1,3))
        rows.append({'source_sigma':sigma,'finite_radius':radius,'center_detail':detail(patch),'difference_from_incumbent':abs(detail(patch)-goal)})
        np.save(WORK/f'center-source-{sigma}.npy',patch)
    selected=min(rows,key=lambda x:x['difference_from_incumbent'])
    write('center-selection.json',{'criterion':'Nearest fixed-center bandpass RMS to accepted output sigma1.7; no edge or aggregate-score selection.', 'incumbent_detail':goal,'source_candidates':rows,'selected':selected})
    sigma=selected['source_sigma'];filtered,support,radius=incident_source_filter(source,known,sigma)
    M=np.zeros_like(raw_lens)
    for row,stop,X,Y,inside in tiles:
        gate();i,j=np.nonzero(inside)
        value=np.zeros(X.shape+(3,))
        value[i,j]=sample(filtered,X[i,j],Y[i,j])
        assert np.isfinite(value).all()
        numerator=value.reshape(stop-row,4,W,4,3).mean((1,3))
        cov=coverage[row:stop,:,None]
        M[row:stop]=np.divide(numerator,cov,out=np.zeros_like(numerator),where=cov>0)
    C=compose(M);sc,local=metrics(C)
    guards={n:sc[n]['rmse']<=base_scores[n]['rmse'] for n in ['train','held_blocks','all_glass','rim','outer_rim','interior']}
    guards.update(ssim=sc['ssim']>=base_scores['ssim'],foreground=sc['foreground_fullbox_MSE']<=base_scores['foreground_fullbox_MSE'],exterior=sc['exterior_MSE']<=base_scores['exterior_MSE'])
    np.savez_compressed(OUT/'candidate.npz',material=M,complete=C,coverage=coverage)
    def pic(im):return Image.fromarray(np.uint8(np.rint(np.clip(im,0,1)*255)))
    for name,(a,b,c,d) in BOXES.items():
        width=min(2*(c-a),max(c-a,720));height=round((d-b)*width/(c-a))
        canvas=Image.new('RGB',(3*width+4,height+64),'white');draw=ImageDraw.Draw(canvas)
        for j,(im,label) in enumerate([(target[b:d,a:c],'Reference'),(baseline[b-y0:d-y0,a-x0:c-x0],'Output blur 1.7 px'),(C[b-y0:d-y0,a-x0:c-x0],f'Source blur {sigma:g} px')]):
            canvas.paste(pic(im).resize((width,height),Image.Resampling.NEAREST),(j*(width+2),64));draw.text((j*(width+2)+6,18),label,fill='black')
        canvas.save(OUT/f'{name}.png')
    result={'status':'NUMERICAL_CANDIDATE_PENDING_VISUAL' if all(guards.values()) else 'NO_STRICT_QUALIFIER',
            'selected_source_sigma_pixels':sigma,'output_sigma_pixels':0,'baseline_output_sigma_pixels':1.7,
            'scores':sc,'baseline_scores':base_scores,'guards':guards,'local':local,'baseline_local':base_local,
            'new_full_native_candidates':1,'new_refraction_rays':0,'crop_candidates':len(rows),
            'clear_exterior_exact':bool(np.array_equal(C[coverage==0],baseline[coverage==0])),
            'foreground_color_alpha_frozen':True,'clipping':'No optical or body clipping introduced.',
            'precision':{'full_glass_MSE_delta_f64':float(np.mean(((C.astype(float)-ref)[valid]*255)**2)-np.mean(((baseline.astype(float)-ref)[valid]*255)**2))},
            'limits':'Registered-source empirical neutral PSF. Geometry/foreground fixed; source RGB, PSF and illumination uncertainty remain.'}
    write('result.json',result);print(json.dumps({'status':result['status'],'selected':selected,'glass':sc['all_glass'],'guards':guards,'local':local}),flush=True)

if __name__=='__main__':
    stage=argparse.ArgumentParser();stage.add_argument('stage',choices=['preflight','compare']);a=stage.parse_args()
    {'preflight':preflight,'compare':compare}[a.stage]()
