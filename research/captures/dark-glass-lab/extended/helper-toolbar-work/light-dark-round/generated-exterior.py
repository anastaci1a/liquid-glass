"""One shared empirical exterior family. No optical renderer or source fitting."""
import os,sys,json,hashlib
from pathlib import Path
import numpy as np
from PIL import Image,ImageDraw
from scipy.optimize import minimize
R=Path('/evidence/extended/helper-toolbar-work/light-dark-round'); O=R/'generated-exterior'; C=R/'clean-presentation'
sys.path.insert(0,str(R/'code'))
from reproduce import CASES,points
from render import case_geometry

def sha(p):return hashlib.sha256(p.read_bytes()).hexdigest()
def save(n,v):(O/n).write_text(json.dumps(v,indent=2)+'\n')
def load():
 rows=[]
 for name in ['regular-light','regular-dark']:
  c=CASES[name];x0,y0,x1,y1=c['crop'];L=min(c['half']);_,_,x,y=points(c)
  B=np.asarray(Image.open(R/f'{name}-source.png').convert('RGB')).astype(float)[y0:y1,x0:x1]/255
  T=(np.asarray(Image.open(R/f'{name}-target.png').convert('RGB')).astype(np.float32)/255)[y0:y1,x0:x1]
  M=np.load(R/f'{name}-native-material.npy');cov=np.load(C/f'{name}-coverage.npy');base=np.load(C/f'{name}-baseline-complete.npy');mask=np.load(C/f'{name}-exterior-mask.npy')
  sd=case_geometry(c,x,y)[0]/L
  dK=np.maximum(case_geometry(c,x,y-.06*L)[0]/L,0);dH=np.maximum(case_geometry(c,x,y+.4*L)[0]/L,0)
  rows.append(dict(name=name,B=B,T=T,M=M,cov=cov,base=base,mask=mask,sd=sd,x=x,y=y,dK=dK,dH=dH))
 return rows

def evaluate(row,p,deriv=False):
 oK,sK,oH,sH=p;gK=np.exp(-.5*(row['dK']/sK)**2);gH=np.exp(-.5*(row['dH']/sH)**2);aK=oK*gK;aH=oH*gH
 B1=row['B']*(1-aK[...,None]);Bout=B1+aH[...,None]*(1-B1);out=row['M']*row['cov'][...,None]+Bout*(1-row['cov'][...,None])
 if not deriv:return out,Bout,aK,aH
 # Complete analytic derivatives of composited encoded RGB, order oK,sK,oH,sH.
 k=-row['B']*(1-aH[...,None])*(1-row['cov'][...,None]);h=(1-B1)*(1-row['cov'][...,None])
 J=np.stack([k*gK[...,None],k*(aK*row['dK']**2/sK**3)[...,None],h*gH[...,None],h*(aH*row['dH']**2/sH**3)[...,None]],-1)
 return out,J

def inspect(rows):
 profiles=[];controls=[]
 for r in rows:
  result=[]
  for lo,hi in [(0,.05),(.05,.1),(.1,.2),(.2,.35),(.35,.7),(.7,1.2)]:
   for region,side in [('upper',r['y']<0),('lower',r['y']>=0)]:
    m=(r['sd']>lo)&(r['sd']<=hi)&side
    if not m.any():continue
    residual=(r['T']-r['base'])[m]*255
    result.append(dict(sd_L=[lo,hi],region=region,pixels=int(m.sum()),target_minus_baseline_rgb=residual.mean(0).tolist(),rmse=float(np.sqrt(np.mean(residual**2))),target_luma_mean=float((r['T'][m]@np.array([.2126,.7152,.0722])).mean()*255)))
  zero=evaluate(r,[0,.2,0,.3])[0];shadow=evaluate(r,[.05,.2,0,.3])[0];glow=evaluate(r,[0,.2,.05,.3])[0]
  controls.append(dict(theme=r['name'],zero_bit_exact=bool(np.array_equal(zero,r['base'])),shadow_never_increases=bool(np.all(shadow<=r['base'])),glow_never_decreases=bool(np.all(glow>=r['base'])),source_sha256=sha(R/f"{r['name']}-source.png"),material_sha256=sha(R/f"{r['name']}-native-material.npy"),exterior_mask_sha256=sha(C/f"{r['name']}-exterior-mask.npy")))
  profiles.append(dict(theme=r['name'],bins=result))
 # Classification evidence: upper dark residual positive, lower dark identically black;
 # light lower exterior needs reduction. It supports testing a shared empirical component,
 # not an assertion about the incident source or lighting apparatus.
 dark=rows[1];light=rows[0];far=(dark['sd']>.2)&(dark['sd']<.35)
 support=bool(np.mean((dark['T']-dark['base'])[far&(dark['y']<0)])>0 and np.all(dark['T'][far&(dark['y']>=0)]==0) and np.mean((light['T']-light['base'])[(light['sd']>.2)&(light['sd']<.35)&(light['y']>=0)])<0)
 save('inspection.json',dict(profiles=profiles,controls=controls,classification_support=support,interpretation='Localized upper brightening and light-theme darkening support testing the prescribed shared empirical exterior operator only. Gray is NOT established incident background; black underbody source stays frozen.',offsets_L=dict(K=[0,.06],H=[0,-.4]),parameters=['opacityK','sigmaK_L','opacityH','sigmaH_L'],bounds=[[0,.12],[.03,.7],[0,.12],[.03,.7]],original_mask='frozen 0<original_sd<.35L; far bands advisory only',target_used_only_for_residual_scoring=True))
 assert all(c['zero_bit_exact'] and c['shadow_never_increases'] and c['glow_never_decreases'] for c in controls)
 print('CLASSIFICATION',support,flush=True)
 for p in profiles:
  print(p['theme'],json.dumps(p['bins']),flush=True)
 return support

def fit(rows):
 if (O/'result.json').exists():raise RuntimeError('Existing result: no duplicate fit')
 if not json.loads((O/'inspection.json').read_text())['classification_support']:raise RuntimeError('No supported classification')
 history=[];mse0=[float(np.mean((r['base']-r['T'])[r['mask']]**2)) for r in rows]
 # Work only on the already-frozen exterior pixels; no optical render.
 small=[{k:(v[r['mask']] if isinstance(v,np.ndarray) and v.shape[:2]==r['mask'].shape else v) for k,v in r.items()} for r in rows]
 def fun(p):
  if len(history)>=120:raise RuntimeError('120 evaluation cap reached')
  errors=[];grad=np.zeros(4)
  for r,base_mse in zip(small,mse0):
   out,J=evaluate(r,p,True);err=out-r['T'];errors.append(float(np.mean(err**2)));grad+=np.mean(2*err[...,None]*J,axis=(0,1))/base_mse/2
  value=float(np.mean(np.array(errors)/mse0));history.append(dict(evaluation=len(history)+1,parameters=p.tolist(),objective=value,exterior_rmse=(np.sqrt(errors)*255).tolist()))
  return value,grad
 result=minimize(fun,np.array([.03,.2,.03,.3]),jac=True,method='L-BFGS-B',bounds=[(0,.12),(.03,.7),(0,.12),(.03,.7)],options=dict(maxfun=110,maxiter=100,ftol=1e-12,gtol=1e-8,maxls=15))
 save('trials.json',history);p=result.x;records=[]
 for r,base_mse in zip(rows,mse0):
  out,Bout,aK,aH=evaluate(r,p);err=out-r['T'];m=r['mask'];rmse=float(np.sqrt(np.mean(err[m]**2))*255);base_rmse=float(np.sqrt(base_mse)*255)
  np.save(O/f"{r['name']}-complete.npy",out);np.save(O/f"{r['name']}-background-out.npy",Bout);np.savez_compressed(O/f"{r['name']}-generated-alpha.npz",shadow=aK,glow=aH)
  masks=np.load(R/f"{r['name']}-native-masks.npz");unchanged={k:bool(np.array_equal(out[masks[k]],r['M'][masks[k]])) for k in masks.files}
  bands=[]
  for lo,hi in [(.2,.35),(.35,.7),(.7,1.2)]:
   for region,side in [('upper',r['y']<0),('lower',r['y']>=0)]:
    b=(r['sd']>lo)&(r['sd']<=hi)&side
    if b.any():bands.append(dict(sd_L=[lo,hi],region=region,pixels=int(b.sum()),baseline_rmse=float(np.sqrt(np.mean((r['base']-r['T'])[b]**2))*255),candidate_rmse=float(np.sqrt(np.mean(err[b]**2))*255)))
  images=[]
  for label,arr in [('target',r['T']),('zero-generated',r['base']),('generated',out)]:
   im=Image.fromarray(np.rint(np.clip(arr,0,1)*255).astype(np.uint8));im.save(O/f"{r['name']}-{label}-native.png");im=im.resize((720,round(im.height*720/im.width)),Image.Resampling.LANCZOS);images.append((label,im))
  sheet=Image.new('RGB',(720*3,images[0][1].height+28),'white');d=ImageDraw.Draw(sheet)
  for i,(label,im) in enumerate(images):d.text((i*720+8,7),label,fill='black');sheet.paste(im,(i*720,28))
  sheet.save(O/f"{r['name']}-comparison.png")
  records.append(dict(theme=r['name'],baseline_exterior_rmse=base_rmse,candidate_exterior_rmse=rmse,exterior_improves=rmse<base_rmse,original_scored_pixels_bit_exact=unchanged,far_bands_advisory=bands,complete_sha256=sha(O/f"{r['name']}-complete.npy"),output_range=[float(out.min()),float(out.max())]))
 accepted=all(r['exterior_improves'] and all(r['original_scored_pixels_bit_exact'].values()) for r in records)
 save('recipe.json',dict(family='empirical shared generated exterior shadow+possible glow; NOT physical identification',parameters=dict(zip(['opacityK','sigmaK_L','opacityH','sigmaH_L'],p.tolist())),offsets_L=dict(K=[0,.06],H=[0,-.4]),formula='B1=B*(1-alphaK); Bout=B1+alphaH*(1-B1); complete=M*coverage+Bout*(1-coverage)',alpha='opacity*exp(-.5*(max(sd_of_translated_original_shape/L,0)/sigma_L)^2)',geometry='original fixed rounded rectangle; L106.5; shared both themes',source_adopted=False,optical_renders=0,source_fit=False,theme_specific_coefficients=False,source_proof='unchanged material/map/kernel/source; original whole and ALL-scored native source proof transfers, estimated/unobserved input limitations retained',input_hashes=json.loads((O/'inspection.json').read_text())['controls']))
 save('result.json',dict(numerical_qualifier=accepted,classification='EXTERIOR-ONLY; Eoptical TIE',primary_acceptance=False,count=0,evaluations=len(history),evaluation_cap=120,solver_success=bool(result.success),solver_message=str(result.message),observations=records,original_scores_reused=json.loads((R/'intake-result.json').read_text())['observations'],limitations='Far bands advisory; generated glow is not proof of incident source black or Apple lighting. Removing target-derived old context earns no credit. No adoption or optical pass before independent primary review.'))
 print('RESULT',accepted,'evaluations',len(history),'parameters',p.tolist(),flush=True)
 for r in records:print(r['theme'],r['baseline_exterior_rmse'],r['candidate_exterior_rmse'],r['original_scored_pixels_bit_exact'],flush=True)

if __name__=='__main__':
 os.umask(0o002)
 if sys.argv[-1]=='inspect':
  O.mkdir(exist_ok=False);inspect(load())
 elif sys.argv[-1]=='fit':fit(load())
