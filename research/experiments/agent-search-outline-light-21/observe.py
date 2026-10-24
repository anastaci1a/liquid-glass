"""One pinned cached Search first-return lighting experiment; no backdrop lookup."""
from pathlib import Path
import sys,json,datetime,hashlib
import numpy as np,cv2
from PIL import Image,ImageDraw,ImageFont
OUT=Path(__file__).resolve().parent;ROOT=OUT.parents[2];B=OUT.parent/'agent-music-search-baseline-01';T=OUT.parent/'agent-music-search-neutral-05';WORK=ROOT/'.evidence-working/music-search-baseline-01'
P=json.loads((OUT/'protocol.json').read_text());ledger={k:0 for k in P['caps']}
def now():return datetime.datetime.now(datetime.timezone.utc).isoformat()
def clock(checkpoint=False):
 end=P['checkpoint_deadline' if checkpoint else 'deadline'];assert datetime.datetime.now(datetime.timezone.utc)<datetime.datetime.fromisoformat(end.replace('Z','+00:00')),'Original deadline'
def save(n,v):clock();(OUT/n).write_text(json.dumps(v,indent=2,allow_nan=False)+'\n')
def charge(k,n):
 clock();assert ledger[k]+n<=P['caps'][k],k;ledger[k]+=int(n)
def sha(f):return hashlib.sha256(f.read_bytes()).hexdigest()
assert not (OUT/'started.json').exists(),'No retry'
result={'status':'STARTING','records':[],'ledger':ledger}
try:
 save('started.json',{'at':now()})
 files=[ROOT/'reconstruction/environment_radiance.py',ROOT/'reconstruction/geometric_optics.py',ROOT/'reconstruction/geometric_render.py',ROOT/'reconstruction/extended_fit.py',ROOT/'reconstruction/vector_foreground.py',ROOT/'reconstruction/foreground_response.py',B/'native-paths.npz',B/'source-preflight.json',T/'result.json']
 for k in ('a','b'):files.extend([T/f'full-{k}-candidate.npz',T/f'full-{k}-result.json',B/f'{k}-masks.npz',B/f'{k}-support.npz'])
 restored=json.loads((B/'restored-inputs.json').read_text())['records']
 for r in restored:
  f=WORK/r['case']/r['name'];assert sha(f)==r['sha256'];files.append(f)
 for k in ('a','b'):files.append(WORK/k/'case.json')
 first={str(f.relative_to(ROOT)):sha(f) for f in files};save('first-hashes.json',first)
 sys.path.insert(0,str(ROOT/'reconstruction'))
 import environment_radiance as env
 from geometric_render import neutral_color_response
 from extended_fit import Study
 cv2.setNumThreads(1)
 # Narrow wrappers count existing utility delegates without changing any equation.
 captured={}
 def counted(name,key,fn):
  def call(*args,**kwargs):
   n=np.asarray(args[0]).shape[0] if name in ('reflect','refract') else np.asarray(args[0]).size
   charge(key,n);v=fn(*args,**kwargs)
   if name=='fresnel':captured.setdefault('fresnel',[]).append(np.array(v,copy=True))
   return v
  return call
 env.reflect_direction=counted('reflect','reflect_points',env.reflect_direction)
 env.refract=counted('refract','snell_points',env.refract)
 env.fresnel_components=counted('fresnel','fresnel_points',env.fresnel_components)
 original_annulus=env.annular_environment
 def annulus(*args,**kwargs):charge('environment_direction_queries',np.asarray(args[0]).size//3);return original_annulus(*args,**kwargs)
 env.annular_environment=annulus
 q=np.load(B/'native-paths.npz',allow_pickle=False);inside=q['inside'];N=int(inside.sum());assert N==98989 and q['complete'][inside].all() and not q['boundary_unresolved'][inside].any()
 normal=q['outward_normal'][inside];back=q['back'][inside];assert np.isfinite(normal).all() and (normal[:,2]<0).all() and np.max(abs(np.linalg.norm(normal,axis=1)-1))<1e-10
 proof=json.loads((B/'source-preflight.json').read_text());assert proof['status']=='PASS_BOTH_BEFORE_RGB'
 for row in proof['records']:assert row['unsupported_required']==0 and row['kernel_radius']==21
 par=json.loads((B/'protocol.json').read_text())['parameters'];assert par['R']==.9972124917582454 and par['L']==89 and par['D']==2
 bounds=json.loads((B/'geometry-checkpoint.json').read_text());Hmax=bounds['maximum_height'];M=bounds['slope_bound'];R=par['R'];delta=2*Hmax*M/(1-M*M)
 assert M<1 and delta<R and np.all(back[:,2]<0)
 # Radially nonincreasing concave actual harmonic height gives global first-front order.
 charge('helper_points',N);branch=env.certified_first_return(normal,1.5)
 direction=branch['reflected_direction'];times=-back[:,2]/direction[:,2];front=back+times[:,None]*direction
 assert np.isfinite(front).all() and np.all(times>0) and np.max(abs(front[:,2]))<1e-12
 radial=np.hypot(front[:,0]/R,front[:,1]/R);assert np.all(radial<1),'Actual projected front membership failed'
 assert np.all(np.sum(direction*normal,axis=1)<0),'Reflection not inward'
 assert np.isfinite(branch['unit_emitter_radiance']).all() and branch['closure_max_error']<2e-14
 # Keep actual s/p products, not products of unpolarized averages.
 R0,Rb,Rf=captured['fresnel'];T0=1-R0;primary_sp=.5*T0*(1-Rb);return_sp=.5*T0*Rb*(1-Rf);later_sp=.5*T0*Rb*Rf
 assert np.array_equal(return_sp.sum(1),branch['first_return_power']) and np.array_equal(later_sp.sum(1),branch['retained_tail'])
 np.savez_compressed(OUT/'first-return.npz',back=back,normal=normal,front=front,first_front_time=times,primary_sp=primary_sp,first_return_sp=return_sp,later_sp=later_sp,**{k:v for k,v in branch.items() if isinstance(v,np.ndarray)})
 save('geometry-certificate.json',{'H':Hmax,'M':M,'R':R,'global_inward_displacement_bound':delta,'actual_projected_radius_max':float(radial.max()),'actual_front_z_error_max':float(abs(front[:,2]).max()),'first_return_blocked':int(branch['blocked'].sum()),'closure_max':branch['closure_max_error'],'new_rays':0,'new_heights':0,'scope':'Radial decreasing back, convex solid, strict positive-thickness interior; actual projected next-front membership verified.'})
 crops=json.loads((B/'RGB-started.json').read_text())['fixed_original_frame_crops'];luma=np.array([.2126,.7152,.0722]);data={}
 def score(s,pre,C,m):
  charge('score_calls',1);charge('metric_gaussians',5);charge('metric_erosions',1);z=s.scores(C);z['E']=float(np.sqrt(z['loss']));error=(C-s.target_crop)*255
  # Original pre-foreground and completed cohorts agree: paint is entirely in excluded FG boxes.
  assert not (m['glass']&m['foreground']).any() and np.array_equal(pre[~m['foreground']],C[~m['foreground']],equal_nan=True)
  for name,mask in [('glass',m['glass']),('rim',m['rim']),('held',m['held']),('interior',m['glass']&~m['rim'])]:
   value=float(np.sqrt(np.mean(((pre-s.target_crop)[mask]*255)**2)));assert value==z[name]['rmse']
  z['exterior_RMSE']=float(np.sqrt(np.mean(error[m['exterior']]**2)));z['foreground_RMSE']=float(np.sqrt(np.mean(error[m['foreground']]**2)))
  return z
 def diagnostic(s,C):
  x0,y0,_,_=s.crop;out={}
  for name,(a,b,c,d) in crops.items():
   err=(C[b-y0:d-y0,a-x0:c-x0].astype(float)-s.target_crop[b-y0:d-y0,a-x0:c-x0].astype(float))*255;valid=np.isfinite(err).all(2);e=err[valid];Y=e@luma;ch=e-Y[:,None]
   out[name]={'bounds':[a,b,c,d],'RGB_RMSE':float(np.sqrt(np.mean(e*e))),'luma_RMSE':float(np.sqrt(np.mean(Y*Y))),'chroma_RMSE':float(np.sqrt(np.mean(ch*ch))),'signed_RGB':e.mean(0).tolist()}
  return out
 for k in ('a','b'):
  charge('Study_constructors',1);charge('mask_pixels',56400);s=Study(WORK/k);m=dict(np.load(B/f'{k}-masks.npz',allow_pickle=False));z=np.load(T/f'full-{k}-candidate.npz',allow_pickle=False)
  assert np.array_equal(s.valid,m['glass']) and np.array_equal(s.rim,m['rim']) and np.array_equal(s.held,m['held'])
  base=np.load(B/f'{k}-candidate.npz',allow_pickle=False);raw=base['sample_before_response'];values=raw.copy();values[inside]=neutral_color_response(raw[inside],gain=.5193880051291454,bias=.4473611800152188)
  assert np.array_equal(values,z['sample_after_response'],equal_nan=True)
  coverage=z['coverage'];H,W=coverage.shape;pre=values.reshape(H,2,W,2,3).mean((1,3)).astype(np.float32);charge('zero_composites',1);C=s.apply_foreground(pre.copy())
  assert np.array_equal(pre,z['pre_foreground'],equal_nan=True) and np.array_equal(C,z['complete'],equal_nan=True),'Zero identity failure'
  baseline=score(s,pre,C,m);saved=json.loads((T/f'full-{k}-result.json').read_text())['scores']['complete'];assert baseline==saved,'Baseline score mismatch'
  partial=m['glass']&(coverage<1);assert int(partial.sum())==38
  data[k]={'s':s,'m':m,'values':values,'pre':pre,'C':C,'coverage':coverage,'before':baseline,'partial':partial,'before_partial':float(np.sqrt(np.mean(((C-s.target_crop)[partial]*255)**2))),'before_crops':diagnostic(s,C)}
 clock(True);save('checkpoint.json',{'at':now(),'zero_identities':2,'geometry_and_source_proof_valid':True,'per_point_front_membership':True,'fixed_crops':crops,'ledger':ledger});print('CHECKPOINT_JSON:'+json.dumps({'at':now(),'status':'PASS_CERTIFICATE_AND_BOTH_ZERO_CONTROLS','inside':N,'ledger':ledger}),flush=True)
 def display(a):
  valid=np.isfinite(a).all(2);yy,xx=np.indices(valid.shape);return np.where(valid[...,None],a,np.where(((yy//6+xx//6)%2)[...,None],.72,.9))
 def im(a):return Image.fromarray(np.uint8(np.rint(np.clip(display(a),0,1)*255)))
 for amplitude in (1.,4.):
  for k,d in data.items():
   clock();s=d['s'];values=d['values'];H,W=d['coverage'].shape
   linear=env.decode_srgb(values[inside])+amplitude*branch['unit_emitter_radiance'][:,None]
   encoded=env.encode_srgb(linear);upper=env.encode_srgb(linear+amplitude*branch['retained_tail'][:,None])
   changed=values.copy();changed[inside]=np.clip(encoded,0,1);assert np.array_equal(changed[~inside],values[~inside],equal_nan=True)
   pre=changed.reshape(H,2,W,2,3).mean((1,3)).astype(np.float32);charge('candidate_composites',1);C=s.apply_foreground(pre.copy());now_score=score(s,pre,C,d['m']);part=float(np.sqrt(np.mean(((C-s.target_crop)[d['partial']]*255)**2)))
   guards={name:now_score[name]['rmse']<=d['before'][name]['rmse'] for name in ('glass','rim','held','interior')}
   guards.update(E=now_score['E']<=d['before']['E'],SSIM=now_score['ssim']>=d['before']['ssim'],exterior=now_score['exterior_RMSE']<=d['before']['exterior_RMSE'],foreground=now_score['foreground_RMSE']<=d['before']['foreground_RMSE'],partial38=part<=d['before_partial'])
   name=f'{k}-light{int(amplitude)}';np.savez_compressed(OUT/(name+'.npz'),pre_foreground=pre,complete=C,coverage=d['coverage'],linear_inside=linear,encoded_preclip_inside=encoded,later_sp=later_sp)
   width=2*W;height=2*H;canvas=Image.new('RGB',(3*width+4,height+64),'white');draw=ImageDraw.Draw(canvas);font=ImageFont.load_default(size=17)
   for i,(v,label) in enumerate([(s.target_crop,'Apple reference'),(d['C'],'Accepted Search tone'),(C,f'Conditional annulus, radiance {int(amplitude)}')]):canvas.paste(im(v).resize((width,height),Image.Resampling.NEAREST),(i*(width+2),64));draw.text((i*(width+2)+8,20),label,font=font,fill='black')
   canvas.save(OUT/(name+'-comparison.png'))
   row={'reference':k,'amplitude':amplitude,'scores':now_score,'baseline':d['before'],'guards':guards,'all_guards_pass':all(guards.values()),'partial38_RMSE':part,'partial38_baseline':d['before_partial'],'clipped_channels':int((encoded>1).sum()),'clear_exact':True,'crops':diagnostic(s,C),'baseline_crops':d['before_crops'],'later_interval_encoded_max_levels':float(np.max(np.clip(upper,0,1)-np.clip(encoded,0,1))*255),'later_interval_scope':'Omitted contribution of hypothetical bounded emitter after first return, not total physical scene radiance. No tail RGB assigned.'}
   result['records'].append(row);save(name+'-metrics.json',row);print('CANDIDATE_JSON:'+json.dumps({'reference':k,'amplitude':amplitude,'E':now_score['E'],'guards':guards,'clips':row['clipped_channels']}),flush=True)
 result['status']='CONDITIONAL_OBSERVATIONS_COMPLETE_PENDING_PRIMARY';result['hypothesis']='Unobserved annular infinite white emitter; calibrated-primary/sRGB hybrid, not recovered environment or physical radiometry.'
 result['hashes_last']={str(f.relative_to(ROOT)):sha(f) for f in files};assert result['hashes_last']==first,'Input changed'
except Exception as exc:
 result['status']='STOPPED_FIRST_INVARIANT';result['failure']=repr(exc)
finally:
 result['finished']=now();(OUT/'result.json').write_text(json.dumps(result,indent=2,allow_nan=False)+'\n');print('FINAL_JSON:'+json.dumps({'status':result['status'],'failure':result.get('failure'),'records':len(result['records']),'ledger':ledger}),flush=True)
