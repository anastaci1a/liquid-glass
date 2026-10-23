"""Test whether transmission preblur suppresses the observed chromatic rim."""
from pathlib import Path
exec(Path('/evidence/extended/switch-spectral-reflection-probe.py').read_text().split('root=Path(')[0])
from scipy.optimize import minimize
from paired_fit import permitted
root=Path('/evidence/extended/active-switch/paired');old=json.loads((root/'pass-23.json').read_text())['current'];out=root.parent/'spectral-scattering-probe';out.mkdir(exist_ok=True);co=np.array(old['material']);studies=[Study(root/n) for n in ['a','b']];caches=[SpectralCache(s,old['parameters'],co) for s in studies];start=time.time();scale=np.mean([m['loss'] for m in old['scores']]);prior=root.parent/'spectral-reflection-probe/running.json';seed=np.array(json.loads(prior.read_text())['best']['parameters']);trials=[];best=None;calls=0
for sigma in [0.,1.,2.,3.,4.339320119358678]:
 p={**old['parameters'],'sigma':sigma}
 for c in caches:c.p=p;c.texture=c.s.blur(c.s.kernel_sigma(p))
 memo={}
 def evaluate(v):
  global calls,best
  key=np.asarray(v).tobytes()
  if key not in memo:
   memo.clear();m=[s.scores(c.render(v),include_ssim=False) for s,c in zip(studies,caches)];memo[key]=m;calls+=1
   if permitted(m,old['scores']) and (best is None or sum(a['loss'] for a in m)<sum(a['loss'] for a in best['scores'])):best=dict(sigma=sigma,parameters=np.asarray(v).tolist(),scores=m)
  return memo[key]
 def f(v):return np.mean([m['loss'] for m in evaluate(v)])/scale
 def g(v):return np.array([x for a,b in zip(evaluate(v),old['scores']) for x in [(b['loss']-a['loss'])/scale,(b['glass']['rmse']**2-a['glass']['rmse']**2)/scale]])
 raw=evaluate(seed);fit=minimize(f,seed,method='SLSQP',bounds=[(-.5,.5)]*7+[(-.1,.1)]*2,constraints=[dict(type='ineq',fun=g)],options=dict(maxiter=15,ftol=1e-9,eps=.001));m=evaluate(fit.x);trials.append(dict(sigma=sigma,initial=raw,final=m,fit=fit.x.tolist(),success=bool(fit.success)));(out/'running.json').write_text(json.dumps(dict(trials=trials,best=best,calls=calls,seconds=time.time()-start),indent=2)+'\n');print(json.dumps(dict(sigma=sigma,losses=[a['loss'] for a in m],best=best,calls=calls)),flush=True)
verified=None
if best:
 p={**old['parameters'],'sigma':best['sigma'],'spectral_profile':best['parameters']};metrics=[];supports=[]
 for s,c,n in zip(studies,caches,['a','b']):
  c.p=p;c.texture=s.blur(s.kernel_sigma(p));fresh=SpectralStudy(s.folder);pred=fresh.render(p,co);assert np.max(abs(pred-c.render(np.array(best['parameters']))))<2e-6;metrics.append(fresh.scores(pred));supports.append(c.support(np.array(best['parameters'])));fresh.comparison(pred,out/f'{n}.png',p)
 if permitted(metrics,old['scores']) and min(supports)>=.999:verified=dict(parameters=p,scores=metrics,support=supports)
(out/'report.json').write_text(json.dumps(dict(baseline_pass=23,trials=trials,best=best,verified=verified,evaluations=calls,seconds=time.time()-start,status='Private unadopted source-scattering/dispersion hypothesis; reflection fixed, frozen A/B gates.'),indent=2)+'\n')
