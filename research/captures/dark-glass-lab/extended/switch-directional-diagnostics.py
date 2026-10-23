from pathlib import Path
exec(Path('/evidence/extended/switch-directional-dispersion-probe.py').read_text().split('calls=0;')[0])
best=json.loads((out/'best.json').read_text());v=best['parameters'];measured=json.loads(Path('/workspace/docs/liquid-glass/experiments/reconstruction/switch-rim-analysis.json').read_text());records=[]
for s,c,n,ref in zip(studies,caches,['a','b'],measured['samples']):
 base=s.render(old['parameters'],co);pred=c.render(v);strength,length,angle,center,width=v;u=np.clip((c.axis-center)/width+.5,0,1);S=u**3*(u*(6*u-15)+10);w=strength*(1-S);direction=np.array([np.cos(angle),np.sin(angle)])*length*s.L
 # Matched achromatic three-tap blur control uses all channels on each ray.
 D=sum(cv2.remap(c.H,c.X+np.float32(k*direction[0]),c.Y+np.float32(k*direction[1]),cv2.INTER_LINEAR) for k in [-1,0,1])/3
 T=c.T*(1-w[...,None])+D*w[...,None];control=(T*(1-c.F[...,None])+c.E*c.F[...,None]).astype(np.float32);regions=[];x0,y0,_,_=s.crop
 for patch in ref['samples']:
  x,y=patch['position'];region=np.zeros_like(s.valid);region[max(y-y0-24,0):y-y0+25,max(x-x0-24,0):x-x0+25]=True;region&=s.valid
  def metric(a):
   e=(a-s.target_crop)[region]*255;chroma=e-e.mean(-1,keepdims=True);return dict(rgb_rmse=float(np.sqrt(np.mean(e**2))),chroma_rmse=float(np.sqrt(np.mean(chroma**2))))
  regions.append(dict(region=patch['region'],center=patch['position'],pixels=int(region.sum()),baseline=metric(base),directional_dispersion=metric(pred),same_geometry_achromatic_blur=metric(control)))
 records.append(dict(sample=n,native_baseline=s.scores(base,include_ssim=False),native_dispersion=s.scores(pred,include_ssim=False),native_blur_control=s.scores(control,include_ssim=False),regions=regions))
report=dict(parameters=v,samples=records,limits='Fixed historical49x49 region windows, clipped by frozen valid mask. ChromaRMSE is encodedRGB residual orthogonal to grayscale, not perceptual DeltaE or proof of dispersion. Blur control matches dispersion kernel length/orientation/blend; not independently optimized. Separate native loss/glass gates unchanged.')
(out/'regional-diagnostics.json').write_text(json.dumps(report,indent=2)+'\n');print(json.dumps(report),flush=True)
