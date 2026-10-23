"""Two bounded existing fade-position proposals; preserve the accepted paired epoch."""
from pathlib import Path
import copy, hashlib, json, math
import cv2, numpy as np
from extended_fit import Study
from revision_replay import clean_composite
from source_support import masks, confidence_at
from chromatic_transmission import rays, weight

cv2.setNumThreads(1)
R=Path('/evidence/extended/switch-dispersion-round/fade-study');R.mkdir(exist_ok=True)
B=Path('/evidence/extended/helper-toolbar-work/active-slider-round')
P=Path('/workspace/docs/liquid-glass/experiments/reconstruction')
assert not (R/'started.json').exists(), 'Inspect existing work instead of repeating it'
rec=json.loads((P/'studies/active-switch/review-round/pass-09.json').read_text())
previous=json.loads((B/'pass08-ambient-neutral/shared-nullspace/candidate-public-native.json').read_text())
assert rec['parameters']==previous['parameters'] and rec['material']==previous['material']
for name in ['extended_fit.py','render.py','crowned_footprint.py','material_context.py','grazing_reflection.py','chromatic_transmission.py','revision_replay.py']:
    assert (P/name).read_bytes()==(B/'code'/name).read_bytes(), name
studies=[Study(B/n) for n in ['a','b']]
co=np.array(rec['material']); p=rec['parameters']
old=[np.load(B/f'pass08-ambient-neutral/shared-nullspace/trial0-ref{i}-material.npy') for i in range(2)]
freeze=json.loads((B/'freeze.json').read_text())
for n,s in zip(['a','b'],studies):
    assert s.case==freeze['cases'][n]
    for name,d in s.case['source_sha256'].items():
        assert hashlib.sha256((s.folder/name).read_bytes()).hexdigest()==d

def save(name,data):
    (R/name).write_text(json.dumps(data,indent=2)+'\n')

def score(s,q,M):
    v=s.scores(M);v['E']=math.sqrt(v['loss']);C=clean_composite(s,q,M)
    ext=(s.sd>0)&(s.sd<.35)
    v['shadow']={'rmse':float(np.sqrt(np.mean(((C-s.target_crop)[ext]*255)**2))),'pixels':int(ext.sum())}
    return v,C

# Reuse accepted images; only remeasure their scores, never rerender baseline.
base=[]
for s,M,expected in zip(studies,old,rec['scores']):
    v,C=score(s,p,M);assert v==expected
    base.append(v)
save('started.json',{'family':'Existing directional_transmission.fade_center only','budget':'Two leftward fade-center proposals (-.02,-.04), both original backgrounds, stop first qualifier','accepted_recipe_sha256':hashlib.sha256((P/'studies/active-switch/review-round/pass-09.json').read_bytes()).hexdigest(),'source_epoch_unchanged':True,'no_baseline_rerender':True,'frozen_fields':'All source, masks, geometry, material, lighting, ordinary blur, dispersion length/strength/fade, shadow','accepted_count':0})

def support(s,q):
    defined,_=masks(s)
    radius=math.ceil(4*(round(s.kernel_sigma(q)*4)/4))+1
    safe=cv2.erode(defined.astype('uint8'),np.ones((2*radius+1,2*radius+1),np.uint8),borderType=cv2.BORDER_CONSTANT,borderValue=0)
    post=math.ceil(4*s.kernel_sigma(q,'post_sigma'))+1
    scope=cv2.dilate(((s.shape_coverage(q)>0)|s.valid).astype('uint8'),np.ones((2*post+1,2*post+1),np.uint8))>0
    count=bad=0
    for row,bottom,W,x,y in s.raster_tiles():
        active=np.repeat(np.repeat(scope[row:bottom],2,0),2,1)
        X,Y,_,_=s.geometry_field(x,y,q)
        maps=[('base',X,Y,active)]
        maps.extend((str(c),X,Y,active&(weight(s,q,x)!=0)) for c,X,Y,_ in rays(s,q,x,y))
        for _,X,Y,m in maps:
            z=confidence_at(safe,(X*s.L+s.case['center'][0]).astype('float32'),(Y*s.L+s.case['center'][1]).astype('float32'))
            count+=int(m.sum());bad+=int((z[m]<1).sum())
    return {'transmission_queries':count,'bad':bad,'source_radius_native':radius,'post_scope_radius_native':post,'passed':bad==0,'limits':'Conservative finite source kernel and output footprint; reflection/context queries unchanged from accepted proof. Hidden track is modeled, not observed.'}

cropref=json.loads((B/'final09-crop-reference.json').read_text())['observations']
trials=[]
for index,degrees in enumerate([-.02,-.04]):
    q=copy.deepcopy(p);q['directional_transmission']['fade_center']+=degrees
    reports=[support(s,q) for s in studies]
    save(f'proposal-{index}-source.json',reports)
    if not all(r['passed'] for r in reports):
        trials.append({'degrees':degrees,'source_pass':False,'native_renders':0,'accepted':False})
        save('trials.json',trials);continue
    native=[];advisory=[];good=True
    for i,s in enumerate(studies):
        M=s.render(q,co);v,C=score(s,q,M)
        np.savez_compressed(R/f'proposal-{index}-ref{i}.npz',material=M,complete=C)
        checks={k:v[k]['rmse']<=base[i][k]['rmse'] for k in ['glass','rim','held','interior','shadow']}
        checks.update(E=v['E']<=base[i]['E'],SSIM=v['ssim']>=base[i]['ssim'])
        good &= checks['glass'] and checks['shadow'] and checks['E']
        native.append({'reference':i,'scores':v,'checks':checks})
        crops={}
        for name,desc in cropref[i]['states'][0].items():
            x,y,z,w=desc['bounds_pixels'];e=(C[y:w,x:z].astype(float)-s.target_crop[y:w,x:z].astype(float))*255
            L=e@np.array([.2126,.7152,.0722]);ch=e-L[...,None]
            crops[name]={'RGB_RMSE':float(np.sqrt(np.mean(e*e))),'luma_RMSE':float(np.sqrt(np.mean(L*L))),'chroma_RMSE':float(np.sqrt(np.mean(ch*ch)))}
        advisory.append(crops)
    progress=any(n['scores']['E']<b['E'] for n,b in zip(native,base))
    row={'degrees':degrees,'parameters':q,'native':native,'advisory_crops':advisory,'source_pass':True,'native_renders':2,'qualifies':bool(good and progress),'accepted_primary':False,'gate':'Original paired E/glass/shadow; other scores and fixed local crops advisory, unchanged historical protocol'}
    trials.append(row);save('trials.json',trials)
    print('FADE_CENTER',degrees,[n['scores']['E']for n in native],row['qualifies'],flush=True)
    if row['qualifies']:break
save('result.json',{'trials':trials,'new_count':0,'accepted_recipe_unchanged':True,'limits':'Bounded existing fade-center study, not global exhaustion. Ordinary blur and RGB dispersion remain separate. Any qualifier still requires independent native/source/visual review.'})
