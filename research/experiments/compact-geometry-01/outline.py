"""Bounded actual-surface energy audit; no tracing, source sampling or image."""
import datetime,json
from pathlib import Path
import numpy as np
from native import setup
from geometric_optics import fresnel_unpolarized
out=Path(__file__).parent
protocol=json.loads((out/'protocol.json').read_text());stage=next(x for x in protocol['stages'] if x['name']=='outline')
assert datetime.datetime.now(datetime.timezone.utc)<datetime.datetime.fromisoformat(stage['deadline'])
assert not (out/'outline-result.json').exists()
_,_,surface,_,_,_=setup('a')
rows=[];heights=0;fresnel=0
front=float(fresnel_unpolarized(1.,1.,1.5));fresnel+=1
for axis in ['x','y']:
 v=np.linspace(-.999999,.999999,601);x=v*surface.half[0] if axis=='x' else np.zeros_like(v);y=v*surface.half[1] if axis=='y' else np.zeros_like(v)
 h,hx,hy,inside=surface.height_gradient(x,y);heights+=len(v)
 slope=np.hypot(hx,hy);cosine=1/np.sqrt(1+slope*slope)
 back=fresnel_unpolarized(cosine,1.5,1.);fresnel+=len(v)
 assert inside.all() and (h>0).all() and np.isfinite(back).all()
 rows.append(dict(axis=axis,maximum_slope=float(slope.max()),maximum_back_reflectance=float(back.max()),edge_back_reflectance=[float(back[0]),float(back[-1])],center_back_reflectance=float(back[300])))
limit=float(fresnel_unpolarized(1/np.sqrt(1+surface.slope_bound**2),1.5,1));fresnel+=1
assert heights<=3000 and fresnel<=3000
result=dict(status='USEFUL_MECHANISM_LIMIT_NOT_OUTLINE_FIDELITY',finished_at=datetime.datetime.now(datetime.timezone.utc).isoformat(),height_evaluations=heights,Fresnel_evaluations=fresnel,new_rays=0,RGB_queries=0,images=0,front_reflectance=front,slope_bound=surface.slope_bound,conservative_first_back_reflectance=limit,maximum_nonprimary_power_under_unit_incident_radiance=front+(1-front)*limit,sections=rows,limits=['Front environment radiance is not observed.','Encoded gain/bias is not a radiance measurement.','Power fractions are not predicted image brightness.','No reflected-path completeness or image acceptance is established.'])
(out/'outline-result.json').write_text(json.dumps(result,indent=2)+'\n')
print(json.dumps(result))
