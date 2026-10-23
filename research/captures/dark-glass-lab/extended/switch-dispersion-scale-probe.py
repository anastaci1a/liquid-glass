"""Compare a wavelength-scaled displacement, rather than a free RGB spline."""
from pathlib import Path
exec(Path('/evidence/extended/switch-spectral-reflection-probe.py').read_text().split('root=Path(')[0])
from paired_fit import permitted
root=Path('/evidence/extended/active-switch/paired');old=json.loads((root/'pass-23.json').read_text())['current'];out=root.parent/'dispersion-scale-probe';out.mkdir(exist_ok=True);studies=[SpectralStudy(root/n) for n in ['a','b']];co=np.array(old['material']);start=time.time();trials=[];best=None
for sigma in [0.,1.,2.,3.,old['parameters']['sigma']]:
 for delta in [-.08,-.04,-.02,.01,.02,.04,.08,.12]:
  p={**old['parameters'],'sigma':sigma};p['spectral_profile']=[delta*p[f'c{i}'] for i in range(7)]+[delta*p['core_x'],delta*p['core_y']]
  metric=[s.scores(s.render(p,co),include_ssim=False) for s in studies];allowed=permitted(metric,old['scores']);row=dict(source_sigma=sigma,dispersion=delta,scores=metric,allowed=allowed);trials.append(row)
  if allowed and (best is None or sum(m['loss'] for m in metric)<sum(m['loss'] for m in best['scores'])):
   best=dict(**row,parameters=p)
   for name,s in zip(['a','b'],studies):s.comparison(s.render(p,co),out/f'{name}.png',p)
 (out/'running.json').write_text(json.dumps(dict(trials=trials,best=best,seconds=time.time()-start),indent=2)+'\n');print(json.dumps(dict(sigma=sigma,losses=[m['loss'] for m in metric],best=best)),flush=True)
(out/'report.json').write_text(json.dumps(dict(model='F_R=x+(1-delta)*(F_G-x),F_B=x+(1+delta)*(F_G-x), shared RGB displacement scaling of the same geometry field. No channel-specific painted color; not a recovered Cauchy IOR.',baseline=old['scores'],trials=trials,best=best,seconds=time.time()-start,status='Private unadopted comparator.'),indent=2)+'\n')
