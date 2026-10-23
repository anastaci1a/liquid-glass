"""ONE new-input baseline from committed best shared circle/rim prior, no fit."""
import os,json,copy,hashlib,sys
from pathlib import Path
import numpy as np,cv2
from PIL import Image,ImageDraw
os.umask(0o002);cv2.setNumThreads(1)
R=Path('/evidence/extended/helper-toolbar-work/more-close-round');D=R/'latest-circle-baseline';sys.path.insert(0,str(D/'code'))
from extended_fit import Study
import settled,neutral_rim
from vector_revision import composite
assert not (D/'baseline-native.json').exists(),'Never repeat a completed baseline'
s=Study(D/'inputs/a');seed=json.loads((D/'selected-public-next-pass03.json').read_text());rim=json.loads((D/'selected-public-neutral-rim-pass03.json').read_text());p=copy.deepcopy(seed['preset']);a=rim['amplitude'];w=rim['width'];assert a==.125 and w==.028;assert p['material'][3:6]==[.05+.025]*3 and p['material'][:3]==[1.]*3 and p['material'][-3:]==[1.]*3 and p['material'][6:-3]==[0.]*14
sha=lambda p:hashlib.sha256(Path(p).read_bytes()).hexdigest()
def save(n,v):(D/n).write_text(json.dumps(v,indent=2)+'\n')
# Exact old-to-new prior proof transfer: added lighting has no sampling calls.
prior=json.loads((R/'baseline-PROPOSED.json').read_text())['preset'];c=copy.deepcopy(p);c['material']=prior['material'];assert c==prior
oldcode=Path('/evidence/extended/helper-toolbar-work/safari-right-circle-round/neutral-baseline/code')
for n in ['settled.py','render.py','extended_fit.py','source_support.py','vector_revision.py','vector_foreground.py']:assert sha(D/'code'/n)==sha(oldcode/n),n
proto=np.load(R/'proposed-native-masks.npz');assert np.array_equal(s.valid,proto['glass']) and np.array_equal(s.rim,proto['rim']) and np.array_equal(s.held,proto['held'])
x0,y0,x1,y1=s.crop;yy,xx=np.mgrid[y0:y1,x0:x1];l,t,r,b=s.case['foreground'][0];fg=(xx>=l)&(xx<r)&(yy>=t)&(yy<b);ext=(s.sd>0)&(s.sd<=.35);full=s.sd>0;safe_ssim=cv2.erode(s.valid.astype(np.uint8),np.ones((11,11),np.uint8))>0;assert int(safe_ssim.sum())==140
alpha=s.shape_coverage(p);masks=dict(glass=s.valid,rim=s.rim,held=s.held,interior=s.valid&~s.rim,SSIM_safe=safe_ssim,glyph=fg,exterior=ext,full_visible_exterior=full);np.savez_compressed(D/'canonical-masks-FIRST.npz',**masks);save('mask-protocol-FIRST.json',dict(case_sha256=hashlib.sha256(json.dumps(s.case,sort_keys=True).encode()).hexdigest(),counts={k:int(v.sum()) for k,v in masks.items()},glass_foreground_exclusion='Original inclusive box, fixed BEFORE baseline',foreground_guard='Full half-open declared box',AA='Frozen native2x2; no maskdrop/epochchange'))
proof=json.loads((R/'proposed-domain-FIRST.json').read_text());assert proof['passed'];proof.update(stage='FIRST_BEFORE_NEW_BASELINE_COMPATIBLE_PROOF_REUSED',transfer='Exact case/PNG/source masks, canonical native masks, settled/render/Study/source-support function hashes, map and source/post kernels identical to source-only preflight. New helper adds normal-lighting only, no source queries. No repeated ray sweep.',neutral_rim_sha256=sha(D/'code/neutral_rim.py'));save('source-proof-FIRST.json',proof)
rec=dict(preset=p,neutral_rim=dict(amplitude=a,width=w),material_contract='Best current shared prior, g1/b.07500000000000001/14lights0 plus neutral normal-white rim a.125/w.028. Prior transfer count0, not deliberately poor b0 or new calibration.',samples=2,case_sha256={'a':hashlib.sha256(json.dumps(s.case,sort_keys=True).encode()).hexdigest()},vector_sha256={'a':{q['vector_asset']:q['vector_sha256'] for q in s.case['foreground_layers']}},prior_commit=json.loads((D/'code-snapshot.json').read_text())['head'],selected_recipe_hashes={n:sha(D/n) for n in ['selected-public-next-pass03.json','selected-public-neutral-rim-pass03.json']},helper_sha256=sha(D/'code/neutral_rim.py'),input_approval='f03593c7-65a7-4dfc-9b45-728f0d33596d',stage='FROZEN_ONE_BASELINE_BEFORE_ANY_NEW_INPUT_FIT',accepted_count=0,source_kind='Estimated local header affineRGB/hiddenobserved0/upper3.785 uncertainty',generated_shadow='ZERO/no targetcontext',B_paired=False);save('baseline-recipe.json',rec)
# Observe actual native sample streams; wrappers return original outputs.
postr=proof['post_kernel_radius'];post=cv2.dilate(((alpha>0)|s.valid).astype(np.uint8),np.ones((2*postr+1,2*postr+1),np.uint8))>0
origmap,origshade,origfield=settled.mapping,settled.shade,neutral_rim.field;state={'row':0};audit={stage:{scope:dict(subrays=0,clipped_subrays=0,clipped_channels=0,endpoints=0,minimum=1e9,maximum=-1e9) for scope in ['whole','scored','postfootprint','global']} for stage in ['base_unclipped','rim_unclipped']}
def observe_map(x,y,p,boundary=None):
 X,Y=origmap(x,y,p,boundary);state.update(x=x,y=y,top=state['row'],bottom=state['row']+x.shape[0]//2);return X,Y
def observe_field(x,y,p,width):
 F=origfield(x,y,p,width);state['field']=F;return F
def observe_shade(sample,light,co):
 core=light[...,-1];gain=(1-core[...,None])*co[:3]+core[...,None]*co[-3:];L=light[...,:-1]@co[6:-3];raw=sample*gain+co[3:6]+L[...,None];base=origshade(sample,light,co);assert np.array_equal(base,np.clip(raw,0,1));rimraw=base+a*state['field'][...,None];top,bottom=state['top'],state['bottom'];whole=s.shape(state['x'],state['y'],p)[-1][0]<=0;score=np.repeat(np.repeat(s.valid[top:bottom],2,0),2,1);ps=np.repeat(np.repeat(post[top:bottom],2,0),2,1)
 for stage,F in [('base_unclipped',raw),('rim_unclipped',rimraw)]:
  for scope,m in [('whole',whole),('scored',score),('postfootprint',ps),('global',np.ones(whole.shape,bool))]:
   z=F[m];q=audit[stage][scope];q['subrays']+=int(m.sum());q['clipped_subrays']+=int(((z<0)|(z>1)).any(1).sum());q['clipped_channels']+=int(((z<0)|(z>1)).sum());q['endpoints']+=int(((z==0)|(z==1)).any(1).sum())
   if z.size:q['minimum']=min(q['minimum'],float(z.min()));q['maximum']=max(q['maximum'],float(z.max()))
 state['row']=bottom;return base
settled.mapping,settled.shade,neutral_rim.field=observe_map,observe_shade,observe_field;actual_helper_audit={}
try:M=neutral_rim.render(s.source,s.case,p,a,w,samples=2,audit=actual_helper_audit)
finally:settled.mapping,settled.shade,neutral_rim.field=origmap,origshade,origfield
assert state['row']==y1-y0
for stage in audit:
 for scope,key in [('whole','whole'),('scored','scored'),('postfootprint','postfootprint')]:assert audit[stage][scope]['subrays']==proof['counts'][key]
global_rim=audit['rim_unclipped']['global'];assert actual_helper_audit==dict(minimum=global_rim['minimum'],maximum=global_rim['maximum'],clipped_channels=global_rim['clipped_channels'])
clipproof=dict(stage='ACTUAL_NATIVE_STREAM_BOTH_BASE_AND_ADDED_RIM',cohorts=audit,committed_helper_global_actual_audit=actual_helper_audit,helper_audit_matches_scoped_reconstruction=True,observational_only=True);save('native-raw-clip-proof.json',clipproof);np.savez_compressed(D/'baseline-material-raw.npz',material=M)
if any(q['clipped_channels'] for stage in audit.values() for q in stage.values()):save('BLOCKER.json',dict(reason='Transferred prior clips actual native raw stream; no baselineacceptance/fit/extension',audit=clipproof));raise RuntimeError('Stop: actual baseline raw clips')
C=composite(s,p,M);scores=s.scores(M);scores['E']=float(np.sqrt(scores['loss']))
for name,m in [('glyph',fg),('exterior',ext),('full_visible_exterior',full)]:scores[name]=dict(pixels=int(m.sum()),rmse=float(np.sqrt(np.mean(((C-s.target_crop)[m]*255)**2))))
np.savez_compressed(D/'baseline-native-arrays.npz',material=M,complete=C,alpha=alpha,glass_mask=s.valid,rim_mask=s.rim,held_mask=s.held,interior_mask=s.valid&~s.rim,SSIM_safe_mask=safe_ssim,glyph_mask=fg,exterior_mask=ext,full_visible_exterior_mask=full)
result=dict(status='BEST_CURRENT_SHARED_PRIOR_BASELINE_READY_PRIMARY_REVIEW_COUNT0',scores=scores,source_proof=proof,native_raw_clip_proof=clipproof,native_body_renders=1,optical_fits=0,accepted_count=0,case_sha256=rec['case_sha256'],prior=dict(g=1,b=.05+.025,neutral_rim_a=a,neutral_rim_w=w,commit=rec['prior_commit']),limitations='Conditionalaffinepaper/sourcehidden0/upper3.785levels; posep95.463/nativeXweight/AA uncertainty. Circlemap/blurpriornotidentifiedbylowfrequencyinput. No baselinegain/pass, no materialfituntilprimaryindependentbaseline review. No shadow/context/copiedpixels.');save('baseline-native.json',result)
wout=2*(x1-x0);hout=2*(y1-y0);im=Image.new('RGB',(2*wout+2,hout+64),'#222');dr=ImageDraw.Draw(im);dr.text((4,20),'Apple CLOSE',fill='white');dr.text((wout+6,20),'Transferred prior',fill='white')
for i,z in enumerate([s.target_crop,C]):im.paste(Image.fromarray(np.uint8(np.rint(np.clip(z,0,1)*255))).resize((wout,hout),Image.Resampling.LANCZOS),(i*(wout+2),64))
im.save(D/'baseline-comparison.png');print(json.dumps(dict(status=result['status'],scores=scores,clip_global=actual_helper_audit,counts=proof['counts'],baseline_renders=1,fit_count=0,pass_count=0)),flush=True)
