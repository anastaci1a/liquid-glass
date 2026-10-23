"""Material operators reuse exact sampled geometry and original compositor."""
import datetime,json,time
import cv2,numpy as np
from native import OUT,setup,save,metrics,preview
from geometric_render import incident_source_filter,coverage_blur
SIGMA=6.75;RADIUS=21
def cache(k):
 with np.load(OUT/f'{k}-raw.npz') as z:return {n:z[n] for n in z.files}
def good(new,old):
 gates={}
 for kind in ['legacy_material','completed_image']:
  for name in ['glass','rim','held','interior']:gates[kind+':'+name]=new[kind][name]['rmse']<=old[kind][name]['rmse']
  gates[kind+':E']=new[kind]['E']<=old[kind]['E'];gates[kind+':ssim']=new[kind]['ssim']>=old[kind]['ssim']
 gates['exterior']=new['exterior']['rmse']<=old['exterior']['rmse']
 gates.update({n:new['foreground_artwork_MSE'][n]<=v for n,v in old['foreground_artwork_MSE'].items()})
 return gates
def body_material(samples,inside,H,W):
 alpha=inside.reshape(H,2,W,2).mean((1,3));lens=np.where(inside[...,None],samples,0).reshape(H,2,W,2,3).mean((1,3))
 return np.divide(lens,alpha[...,None],out=np.zeros_like(lens),where=alpha[...,None]>0)
def sample_incident(source,raw):
 result=raw['sample_rgb'].copy();i,j=np.nonzero(raw['sample_inside']);X=raw['source_X'][i,j];Y=raw['source_Y'][i,j]
 a=np.floor(X).astype(int);b=np.floor(Y).astype(int);fx=(X-a)[:,None];fy=(Y-b)[:,None]
 result[i,j]=(source[b,a]*(1-fx)+source[b,a+1]*fx)*(1-fy)+(source[b+1,a]*(1-fx)+source[b+1,a+1]*fx)*fy
 return result,len(i)
def run_blur():
 if (OUT/'blur-result.json').exists():raise RuntimeError('Completed material question cannot repeat')
 protocol=json.loads((OUT/'protocol.json').read_text());deadline=datetime.datetime.fromisoformat(protocol['stages'][1]['deadline']).timestamp()
 def gate():
  if time.time()>deadline:raise RuntimeError('Blur deadline reached')
 # Support reads only: certify both proposals before filtering or sampling RGB.
 proof=[]
 for k in ['a','b']:
  gate();s,c,surface,known,ext,required=setup(k);raw=cache(k);inside=raw['sample_inside'];i,j=np.nonzero(inside)
  safe=cv2.erode(known.astype(np.uint8),np.ones((43,43),np.uint8),borderType=cv2.BORDER_CONSTANT,borderValue=0)>0
  a=np.floor(raw['source_X'][i,j]).astype(int);b=np.floor(raw['source_Y'][i,j]).astype(int)
  ok=safe[b,a]&safe[b+1,a]&safe[b,a+1]&safe[b+1,a+1]
  rr,cc=np.nonzero(raw['coverage']>0);H,W=raw['coverage'].shape;margin=int(min(rr.min(),cc.min(),H-1-rr.max(),W-1-cc.max()))
  assert margin>=RADIUS
  proof.append({'reference':k,'whole_lens_queries':len(i),'unsupported_source_PSF_queries':int((~ok).sum()),'source_radius':RADIUS,'output_kernel_padding_pixels':margin,'output_PSF_supported':True,'source_RGB_samples':0})
 save('blur-support-FIRST.json',{'references':proof,'new_rays':0,'source_kernel':'Full finite43x43 texels plus four bilinear corners; no RGB before this proof.','output_kernel':'All covered input pixels/source samples already certified; exact finite padding checked.'})
 source_supported=all(p['unsupported_source_PSF_queries']==0 for p in proof)
 baseline=json.loads((OUT/'raw-result.json').read_text())['references'];results=[];queries=0;zero=[]
 for operator in ['source','output']:
  if operator=='source' and not source_supported:
   results.append({'operator':'source','status':'STOP_UNSUPPORTED_SOURCE_BEFORE_RGB'});continue
  rows=[]
  for k,old in zip(['a','b'],baseline):
   gate();s,c,surface,known,ext,required=setup(k);raw=cache(k);H,W=raw['coverage'].shape
   if operator=='source':
    original,n=sample_incident(s.source,raw);queries+=n
    np.testing.assert_array_equal(original,raw['sample_rgb'])
    np.testing.assert_array_equal(s.apply_foreground(original.reshape(H,2,W,2,3).mean((1,3)).astype(np.float32)),raw['complete'])
    filtered,support,radius=incident_source_filter(s.source,known,SIGMA);assert radius==RADIUS
    samples,n=sample_incident(filtered,raw);queries+=n;assert queries<=2351584
    assert np.isfinite(samples).all()
    M=body_material(samples,raw['sample_inside'],H,W);pre=samples.reshape(H,2,W,2,3).mean((1,3)).astype(np.float32)
   else:
    np.testing.assert_array_equal(coverage_blur(raw['material'],raw['coverage'],0),raw['material'])
    np.testing.assert_array_equal(s.apply_foreground(raw['pre_foreground'].copy()),raw['complete'])
    M=coverage_blur(raw['material'],raw['coverage'],SIGMA)
    pre=(M*raw['coverage'][...,None]+raw['clear']).astype(np.float32)
   C=s.apply_foreground(pre.copy());z=metrics(s,M.astype(np.float32),C,ext);gates=good(z,old['scores'])
   np.savez_compressed(OUT/f'{k}-blur-{operator}.npz',material=M,pre_foreground=pre,complete=C)
   preview(s,C,f'{k}-blur-{operator}.png',f'{operator.capitalize()} softness 6.75 px')
   rows.append({'reference':k,'scores':z,'guards':gates});zero.append({'operator':operator,'reference':k,'zero_exact':True})
   print(json.dumps({'operator':operator,'reference':k,'E':z['completed_image']['E'],'guards':gates}),flush=True)
  results.append({'operator':operator,'status':'STRICT_PAIRED_COMPONENT_QUALIFIER' if all(all(r['guards'].values()) for r in rows) else 'NO_STRICT_PAIRED_QUALIFIER','references':rows})
 save('blur-zero-controls.json',{'records':zero,'new_rays':0})
 save('blur-result.json',{'operators':results,'sigma_native_pixels':SIGMA,'source_RGB_queries_including_zero':queries,'new_rays':0,'fits':0,'selection':'Pending local texture and guard review. Operator placement differs; neither is identified physical roughness.'})
if __name__=='__main__':run_blur()
