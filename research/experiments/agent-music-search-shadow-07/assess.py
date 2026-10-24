"""Three fixed historical shadow strengths on immutable cached contributions."""
from pathlib import Path
import json,datetime,hashlib,sys,atexit,os
import numpy as np,cv2
P=Path(__file__).resolve().parent;ROOT=P.parents[2];B=P.parent/'agent-music-search-baseline-01';T=P.parent/'agent-music-search-neutral-05';W=ROOT/'.evidence-working/music-search-baseline-01'
sys.path.insert(0,str(ROOT/'reconstruction'))
from extended_fit import Study
from extended_shadow import shadow
os.umask(0o002);cv2.setNumThreads(1)
p=json.loads((P/'protocol.json').read_text());end=datetime.datetime.fromisoformat(p['deadline'].replace('Z','+00:00'))
def utc():return datetime.datetime.now(datetime.timezone.utc).isoformat()
def save(n,x):(P/n).write_text(json.dumps(x,indent=2,allow_nan=False)+'\n')
def gate():assert datetime.datetime.now(datetime.timezone.utc)<end,'Original deadline'
assert not (P/'started.json').exists(),'No restart';gate();save('started.json',dict(utc=utc()))
ledger={k:0 for k in p['caps']};atexit.register(lambda:save('ledger.json',ledger))
def charge(k,n=1):assert ledger[k]+n<=p['caps'][k],k;ledger[k]+=int(n);save('ledger.json',ledger)
def count(k,n=1):charge(k,n)
def failure(t,v,tb):
 save('failure.json',dict(utc=utc(),type=t.__name__,message=str(v),ledger=ledger));sys.__excepthook__(t,v,tb)
sys.excepthook=failure
def sha(f):return hashlib.sha256(f.read_bytes()).hexdigest()
for folder in [B,T]:
 for x in json.loads((folder/'manifest.json').read_text())['files']:assert sha(folder/x['file'])==x['sha256']
for x in p['shared_pins']:assert sha(ROOT/x['file'])==x['sha256']
assert sha(ROOT/p['recipe'])==p['recipe_sha256'];parameters=json.loads((ROOT/p['recipe']).read_text())['parameters'];assert parameters['shadow']==p['shadow']
data={};identity=[]
for key in ['a','b']:
 gate();charge('original_reference_mask_points',56400);charge('original_mask_geometry_helper_point_calls',56400);s=Study(W/key);assert s.case==json.loads((B/'cases'/f'{key}.json').read_text()) and not s.transmission_layers
 m={k:v for k,v in np.load(B/f'{key}-masks.npz').items()};z={k:v for k,v in np.load(T/f'full-{key}-candidate.npz').items()};assert np.array_equal(m['glass'],s.valid) and np.array_equal(m['rim'],s.rim) and np.array_equal(m['held'],s.held)
 L=z['lens_premultiplied'];U=z['clear_premultiplied'];alpha=z['coverage'];pre=(L+U).astype(np.float32);assert np.array_equal(pre,z['pre_foreground'],equal_nan=True),'Zero pre-foreground identity failed'
 charge('identity_composites');C=s.apply_foreground(pre.copy());assert np.array_equal(C,z['complete'],equal_nan=True),'Zero full compositor identity failed'
 old=json.loads((T/f'full-{key}-result.json').read_text());partial=m['glass']&(alpha<1);assert int(partial.sum())==38
 identity.append(dict(reference=key,pre_foreground_exact=True,complete_exact=True,lens_preserved=True,clear_preserved=True,partial_pixels=38))
 data[key]=dict(s=s,m=m,z=z,L=L,U=U,alpha=alpha,old=old)
save('identity.json',dict(utc=utc(),records=identity,ledger=ledger.copy()))
a=data['a']['s'];b=data['b']['s'];same=bool(a.L==b.L and a.radius==b.radius and a.case['radial']==b.case['radial'] and np.array_equal(a.half,b.half) and np.array_equal(a.x,b.x) and np.array_equal(a.y,b.y));assert same,'No assumed field sharing; stop if coordinates differ'
N=a.x.size;charge('shadow_field_points',N);charge('shadow_shape_helper_point_calls',2*N);unit=shadow(a,{**parameters,'shadow':{**parameters['shadow'],'opacity':1.}},a.x,a.y);assert unit.shape==a.x.shape and np.isfinite(unit).all() and unit.min()>=0 and unit.max()<=1
np.savez_compressed(P/'unit-shadow-field.npz',unit=unit);save('field.json',dict(utc=utc(),shape_same_exact=same,points=N,references_reusing=['a','b'],helper_point_calls=2*N,formula='Historical extended_shadow.shadow evaluated once with unit opacity; no kernel convolution or added cutoff.',field_min=float(unit.min()),field_max=float(unit.max()),parameters=dict(shape=p['shape'],shadow=p['shadow']),ledger=ledger.copy()))
crops=json.loads((B/'RGB-started.json').read_text())['fixed_original_frame_crops'];luma=np.array([.2126,.7152,.0722])
def scores(s,pre,C,m):
 out={}
 for label,img in [('original',pre),('complete',C)]:
  count('score_calls');count('SSIM_metric_Gaussian_calls',5);count('SSIM_metric_mask_erosions');r=s.scores(img);r['E']=float(np.sqrt(r['loss']));err=(C-s.target_crop)*255;r['exterior_RMSE']=float(np.sqrt(np.mean(err[m['exterior']]**2)));r['foreground_RMSE']=float(np.sqrt(np.mean(err[m['foreground']]**2)));out[label]=r
 return out
def diagnostics(im,d):
 out={};s=d['s'];x0,y0,_,_=s.crop
 for name,(a,b,c,e) in crops.items():
  tile=im[b-y0:e-y0,a-x0:c-x0].astype(float);target=s.target_crop[b-y0:e-y0,a-x0:c-x0].astype(float);finite=np.isfinite(tile).all(2);err=(tile-target)[finite]*255;dy=err@luma;dc=err-dy[:,None];valid=d['m']['glass'][b-y0:e-y0,a-x0:c-x0]&(d['alpha'][b-y0:e-y0,a-x0:c-x0]==1)&finite;Y=tile@luma*255;T=target@luma*255;diff=[];td=[]
  for ax in [0,1]:
   v=(valid[1:]&valid[:-1]) if ax==0 else(valid[:,1:]&valid[:,:-1]);diff.extend(np.diff(Y,axis=ax)[v].tolist());td.extend(np.diff(T,axis=ax)[v].tolist())
  diff=np.array(diff);td=np.array(td);out[name]=dict(original_bounds=[a,b,c,e],finite_pixels=int(finite.sum()),RGB_RMSE=float(np.sqrt(np.mean(err**2))),luma_RMSE=float(np.sqrt(np.mean(dy**2))),chroma_RMSE=float(np.sqrt(np.mean(dc**2))),signed_RGB=err.mean(0).tolist(),detail_pairs=len(diff),luma_adjacent_RMS=float(np.sqrt(np.mean(diff**2))) if len(diff) else None,target_luma_adjacent_RMS=float(np.sqrt(np.mean(td**2))) if len(diff) else None,luma_difference_error_RMS=float(np.sqrt(np.mean((diff-td)**2))) if len(diff) else None)
 return out
trials=[];qualifier=None
for factor in p['factors']:
 gate();opacity=float(p['shadow']['opacity']*factor);field=unit*opacity;name={1:'full',.5:'half',.25:'quarter'}[factor];records=[]
 for key,d in data.items():
  gate();s,m,z=d['s'],d['m'],d['z'];clear_after=d['U']*(1-field[...,None]);pre=(d['L']+clear_after).astype(np.float32);charge('candidate_composites');C=s.apply_foreground(pre.copy());assert np.isfinite(C[m['required']]).all();full=d['alpha']==1
  assert np.array_equal(pre[full],z['pre_foreground'][full]) and np.array_equal(C[full],z['complete'][full]),'Fully covered pixel changed'
  now=scores(s,pre,C,m);guards={}
  for label in ['original','complete']:
   v=now[label];old=d['old']['scores'][label];g={k:v[k]['rmse']<=old[k]['rmse'] for k in ['glass','rim','held','interior']};g.update({k:v[k]<=old[k] for k in ['E','exterior_RMSE','foreground_RMSE']});g['SSIM']=v['ssim']>=old['ssim'];guards[label]=g
  part=m['glass']&(d['alpha']<1);err=float(np.sqrt(np.mean(((C-s.target_crop)[part]*255)**2)));guards['partial_boundary']=err<=d['old']['partial_RMSE'];finite=np.isfinite(pre);clips=dict(below=int((pre[finite]<0).sum()),above=int((pre[finite]>1).sum()));assert clips==dict(below=0,above=0)
  row=dict(reference=key,factor=factor,opacity=opacity,scores=now,guards=guards,strict_all=bool(all(guards['original'].values()) and all(guards['complete'].values()) and guards['partial_boundary']),partial_pixels=int(part.sum()),partial_RMSE=err,fully_covered_pixels=int(full.sum()),fully_covered_exact=True,lens_contribution_unchanged=True,original_clear_cache_unchanged=True,generated_clear_contribution_changed=True,clipping=clips,fixed_crops=diagnostics(C,d))
  np.savez_compressed(P/f'{name}-{key}-candidate.npz',lens_premultiplied=d['L'],clear_before=d['U'],clear_after=clear_after,shadow_opacity=field,coverage=d['alpha'],pre_foreground=pre,complete=C)
  save(f'{name}-{key}-result.json',row);records.append(row);print(name,key,row['strict_all'],row['partial_RMSE'],now['complete']['exterior_RMSE'],flush=True)
 trial=dict(name=name,factor=factor,opacity=opacity,records=records,strict_pair=all(r['strict_all'] for r in records));trials.append(trial);save('trials.json',dict(trials=trials,ledger=ledger.copy()))
 if trial['strict_pair']:qualifier=name;break
save('result.json',dict(utc=utc(),status='NUMERICAL_QUALIFIER_PENDING_VISUAL_PRIMARY' if qualifier else 'NO_STRICT_PAIR_KEEP_SHADOW_ZERO',qualifier=qualifier,trials=trials,remaining_factors_not_run=p['factors'][len(trials):],ledger=ledger.copy(),accepted_tone_unchanged=p['accepted_tone'],source_proof_transfer='No changed sampling, source/known input, geometry or incident kernel. Cached clear contribution receives only the declared generated attenuation.',selected_shadow=0,new_pass_count=0,limits=['Empirical generated exterior operator, not measured illumination or optical refraction.','Original partial pixels remain guarded.','Historical fingerprint mismatch and original masks-after-fixtures disclosure retained.']))
