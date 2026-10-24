"""Two predeclared incident widths, cached geometric coordinates only."""
from pathlib import Path
import json,datetime,hashlib,sys,atexit,os
import numpy as np,cv2
from PIL import Image,ImageDraw,ImageFont
P=Path(__file__).resolve().parent;ROOT=P.parents[2];B=P.parent/'agent-music-search-baseline-01';W=ROOT/'.evidence-working/music-search-baseline-01'
sys.path.insert(0,str(ROOT/'reconstruction'))
from extended_fit import Study
from geometric_render import incident_source_filter
os.umask(0o002);cv2.setNumThreads(1)
p=json.loads((P/'protocol.json').read_text());end=datetime.datetime.fromisoformat(p['deadline'].replace('Z','+00:00'))
def now():return datetime.datetime.now(datetime.timezone.utc).isoformat()
def save(n,x):(P/n).write_text(json.dumps(x,indent=2,allow_nan=False)+'\n')
def gate():assert datetime.datetime.now(datetime.timezone.utc)<end,'Original stage deadline'
assert not (P/'started.json').exists(),'No repeated scientific phase';gate();save('started.json',dict(utc=now()))
ledger=dict(rays=0,heights=0,lens_RGB_queries=0,clear_RGB_queries=0,incident_fields=0,full_known_mask_erosions=0,candidate_composites=0,cached_identity_composites=0,original_reference_mask_points=0,source_audit_subrays=0,bilinear_mask_lookups=0,known_mask_cells_processed=0,score_calls=0,SSIM_metric_Gaussian_calls=0,SSIM_metric_mask_erosions=0,fits=0)
atexit.register(lambda:save('ledger.json',ledger))
def count(k,n=1):
 if k in p['caps']:assert ledger[k]+n<=p['caps'][k],'Budget '+k
 ledger[k]+=int(n);save('ledger.json',ledger)
def sha(f):return hashlib.sha256(f.read_bytes()).hexdigest()
for x in json.loads((B/'code-pin.json').read_text())['files']:assert sha(ROOT/x['file'])==x['sha256']
for x in json.loads((B/'manifest.json').read_text())['files']:assert sha(B/x['file'])==x['sha256']
qz=np.load(B/'native-paths.npz');q={n:qz[n] for n in ['source_X','source_Y','inside','complete']};X,Y,inside=q['source_X'],q['source_Y'],q['inside'];assert q['complete'].all();H,Wc=inside.shape[0]//2,inside.shape[1]//2
finite=np.isfinite(X)&np.isfinite(Y);fx0=np.floor(np.where(finite,X,-2)).astype(int);fy0=np.floor(np.where(finite,Y,-2)).astype(int)
data={};ids=[]
for k in ['a','b']:
 gate();count('original_reference_mask_points',H*Wc);s=Study(W/k);case=json.loads((B/'cases'/f'{k}.json').read_text());assert s.case==case
 m={n:z for n,z in np.load(B/f'{k}-masks.npz').items()};assert np.array_equal(s.valid,m['glass']) and np.array_equal(s.rim,m['rim']) and np.array_equal(s.held,m['held']);z={n:v for n,v in np.load(B/f'{k}-candidate.npz').items()};support={n:v for n,v in np.load(B/f'{k}-support.npz').items()}
 assert np.array_equal(z['inside'],inside) and np.array_equal(z['coverage'],inside.reshape(H,2,Wc,2).mean((1,3)))
 pre=z['sample_before_response'].reshape(H,2,Wc,2,3).mean((1,3)).astype(np.float32);assert np.array_equal(pre,z['pre_foreground'],equal_nan=True)
 count('cached_identity_composites');C=s.apply_foreground(pre.copy());assert np.array_equal(C,z['complete'],equal_nan=True)
 known=cv2.imread(str(W/k/'known.png'),0)>0;assert np.array_equal(known,support['known']);required=inside|np.repeat(np.repeat(m['required'],2,0),2,1);assert np.array_equal(required,support['required_subrays'])
 data[k]=dict(s=s,m=m,z=z,support=support,known=known,required=required)
 ids.append(dict(reference=k,pre_foreground_exact=True,complete_exact=True,inside_coverage_masks_exact=True,source_and_vector_hash_checks='Original Study constructor assertions and unchanged baseline manifest',case_fingerprint=hashlib.sha256(json.dumps(case,sort_keys=True).encode()).hexdigest()))
save('identity.json',dict(utc=now(),records=ids,scope='Two unchanged cached composites; no source lookup or baseline optical render',ledger=ledger.copy()))
# Every requested setting is preflighted before any changed field or RGB query.
preflights=[];safe_masks={};accepted={}
for hyp in p['hypotheses']:
 name,r=hyp['name'],hyp['radius'];passed=True
 assert int(np.ceil(3*hyp['sigma']))==r
 for k,d in data.items():
  gate();known=d['known'];count('full_known_mask_erosions');count('known_mask_cells_processed',known.size)
  safe=cv2.erode(known.astype(np.uint8),np.ones((2*r+1,2*r+1),np.uint8),borderType=cv2.BORDER_CONSTANT,borderValue=0)>0;safe_masks[name,k]=safe
  bounds=finite&(fx0>=0)&(fy0>=0)&(fx0+1<known.shape[1])&(fy0+1<known.shape[0]);ii,jj=np.nonzero(bounds);base=np.zeros_like(inside);blur=np.zeros_like(inside)
  count('source_audit_subrays',inside.size);count('bilinear_mask_lookups',8*len(ii))
  for out,mask in [(base,known),(blur,safe)]:out[ii,jj]=mask[fy0[ii,jj],fx0[ii,jj]]&mask[fy0[ii,jj]+1,fx0[ii,jj]]&mask[fy0[ii,jj],fx0[ii,jj]+1]&mask[fy0[ii,jj]+1,fx0[ii,jj]+1]
  supported=np.where(inside,blur,base);bad=d['required']&~supported;scored=np.repeat(np.repeat(d['m']['glass'],2,0),2,1);passed &= not bool(bad.any())
  row=dict(width=name,reference=k,sigma=hyp['sigma'],radius=r,sigma_over_original_L=hyp['sigma']/89,whole_body_subrays=int(inside.sum()),required_union=int(d['required'].sum()),scored=int(scored.sum()),outside_outline_scored=int((scored&~inside).sum()),unsupported_required=int(bad.sum()),unsupported_whole=int((inside&~supported).sum()),unsupported_scored=int((scored&~supported).sum()),unavailable_unscored=int((~supported&~d['required']).sum()),first_bad=np.argwhere(bad)[:8].tolist(),clear_support_exact=bool(np.array_equal(supported[~inside],d['z']['support'][~inside])))
  assert row['clear_support_exact'];preflights.append(row);np.savez_compressed(P/f'{name}-{k}-support.npz',support=supported,incident_known=safe)
 accepted[name]=passed
save('source-proof-FIRST.json',dict(utc=now(),settings=accepted,records=preflights,ledger=ledger.copy(),RGB_queries_before_gate=0,changed_fields_before_gate=0,confidence='Conditional mosaic only; no source extension or new observation'))
crops=json.loads((B/'RGB-started.json').read_text())['fixed_original_frame_crops'];luma=np.array([.2126,.7152,.0722]);rows=[]
def scores(s,pre,C,m):
 result={}
 for label,im in [('original',pre),('complete',C)]:
  count('score_calls');count('SSIM_metric_Gaussian_calls',5);count('SSIM_metric_mask_erosions');z=s.scores(im);z['E']=float(np.sqrt(z['loss']));e=(C-s.target_crop)*255
  z['exterior_RMSE']=float(np.sqrt(np.mean(e[m['exterior']]**2)));z['foreground_RMSE']=float(np.sqrt(np.mean(e[m['foreground']]**2)));result[label]=z
 return result

def diagnostics(im,d):
 out={};s=d['s'];x0,y0,_,_=s.crop
 for name,(a,b,c,e) in crops.items():
  tile=im[b-y0:e-y0,a-x0:c-x0].astype(float);target=s.target_crop[b-y0:e-y0,a-x0:c-x0].astype(float);finite=np.isfinite(tile).all(2);err=(tile-target)[finite]*255;dy=err@luma;dc=err-dy[:,None]
  valid=d['m']['glass'][b-y0:e-y0,a-x0:c-x0]&(d['z']['coverage'][b-y0:e-y0,a-x0:c-x0]==1)&finite
  lum=tile@luma*255;tar=target@luma*255;delta=[];tdelta=[]
  for ax in [0,1]:
   v=(valid[1:,:]&valid[:-1,:]) if ax==0 else (valid[:,1:]&valid[:,:-1]);delta.extend(np.diff(lum,axis=ax)[v].tolist());tdelta.extend(np.diff(tar,axis=ax)[v].tolist())
  delta=np.asarray(delta);tdelta=np.asarray(tdelta)
  out[name]=dict(original_bounds=[a,b,c,e],finite_pixels=int(finite.sum()),pixels=int(finite.size),RGB_RMSE=float(np.sqrt(np.mean(err**2))),luma_RMSE=float(np.sqrt(np.mean(dy**2))),chroma_RMSE=float(np.sqrt(np.mean(dc**2))),signed_RGB=err.mean(0).tolist(),detail_pairs=len(delta),luma_adjacent_RMS=float(np.sqrt(np.mean(delta**2))) if len(delta) else None,target_luma_adjacent_RMS=float(np.sqrt(np.mean(tdelta**2))) if len(delta) else None,luma_difference_error_RMS=float(np.sqrt(np.mean((delta-tdelta)**2))) if len(delta) else None)
 return out
baseline_diagnostics={k:diagnostics(d['z']['complete'],d) for k,d in data.items()};save('baseline-fixed-diagnostics.json',baseline_diagnostics)
for hyp in p['hypotheses']:
 name=hyp['name']
 if not accepted[name]:continue
 for k,d in data.items():
  gate();s=d['s'];z=d['z'];m=d['m'];safe=safe_masks[name,k];assert inside.sum()+ledger['lens_RGB_queries']<=p['caps']['lens_RGB_queries']
  count('incident_fields');count('full_known_mask_erosions');count('known_mask_cells_processed',d['known'].size)
  field,shared_safe,r=incident_source_filter(s.source,d['known'],hyp['sigma']);assert r==hyp['radius'] and np.array_equal(shared_safe,safe)
  count('lens_RGB_queries',int(inside.sum()));raw=z['sample_before_response'].copy();ii,jj=np.nonzero(inside)
  for first in range(0,len(ii),65536):
   ri,ci=ii[first:first+65536],jj[first:first+65536];a=fx0[ri,ci];b=fy0[ri,ci];fx=(X[ri,ci]-a)[:,None];fy=(Y[ri,ci]-b)[:,None]
   raw[ri,ci]=(field[b,a]*(1-fx)+field[b,a+1]*fx)*(1-fy)+(field[b+1,a]*(1-fx)+field[b+1,a+1]*fx)*fy
  assert np.isfinite(raw[inside]).all();assert np.array_equal(raw[~inside],z['sample_before_response'][~inside],equal_nan=True)
  pre=raw.reshape(H,2,Wc,2,3).mean((1,3)).astype(np.float32);count('candidate_composites');C=s.apply_foreground(pre.copy());assert np.isfinite(C[m['required']]).all();assert np.array_equal(C[~m['foreground']],pre[~m['foreground']],equal_nan=True)
  now_scores=scores(s,pre,C,m);old=json.loads((B/f'{k}-result.json').read_text());guards={}
  for label,basekey in [('original','original_mask_scores_on_physical_pre_foreground'),('complete','completed_image_scores')]:
   a=now_scores[label];b=old[basekey];g={n:a[n]['rmse']<=b[n]['rmse'] for n in ['glass','rim','held','interior']};g.update({n:a[n]<=b[n] for n in ['E','exterior_RMSE','foreground_RMSE']});g['SSIM']=a['ssim']>=b['ssim'];guards[label]=g
  partial=m['glass']&(z['coverage']<1);assert int(partial.sum())==38;part=float(np.sqrt(np.mean(((C-s.target_crop)[partial]*255)**2)));guards['partial_boundary']=part<=old['partial_boundary']['complete_RMSE']
  lens=np.where(inside[...,None],raw,0).reshape(H,2,Wc,2,3).mean((1,3));clear=np.where((~inside)[...,None],raw,0).reshape(H,2,Wc,2,3).mean((1,3));assert np.array_equal(clear,z['clear_premultiplied'],equal_nan=True)
  clip=[int((raw[inside]<0).sum()),int((raw[inside]>1).sum())];row=dict(width=name,reference=k,sigma=hyp['sigma'],radius=r,sigma_over_original_L=hyp['sigma']/89,scores=now_scores,guards=guards,strict_all=bool(all(guards['original'].values()) and all(guards['complete'].values()) and guards['partial_boundary']),partial_pixels=38,partial_RMSE=part,raw_preclip_counts=clip,post_unit_response_clip_counts=clip,raw_lens_range=[float(raw[inside].min()),float(raw[inside].max())],clear_exact=True,coverage_exact=True,fixed_crops=diagnostics(C,d))
  np.savez_compressed(P/f'{name}-{k}-candidate.npz',sample_before_response=raw,raw_lens_samples=np.where(inside[...,None],raw,np.nan),raw_clear_samples=z['raw_clear_samples'],inside=inside,coverage=z['coverage'],lens_premultiplied=lens,clear_premultiplied=clear,pre_foreground=pre,complete=C)
  rows.append(row);save(f'{name}-{k}-result.json',row);gate();print(name,k,row['strict_all'],now_scores['complete']['E'],flush=True)
save('result.json',dict(utc=now(),status='FIXED_BRACKET_COMPLETE_PENDING_VISUAL_REVIEW',settings_source_pass=accepted,records=rows,ledger=ledger.copy(),selected_sigma=6.75,selected_radius=21,adopted=False,new_pass_count=0,limitations=['Conditional mosaic; historical recipe receipt mismatch unresolved.','Detail reductions confound correspondence, color and illumination; no identified physical PSF.','No geometry, normal, clear-source, mask, vector, style or response change.']))
