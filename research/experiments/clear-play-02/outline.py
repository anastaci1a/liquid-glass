"""Bounded continuation test of the existing circle's reflected paths.
The old cache lacks unfinished path states, so selected starts replay honestly.
No source radiance is sampled or invented.
"""
import datetime,json,time
from pathlib import Path
import numpy as np
from geometric_optics import RadialCurvatureBack,CircularHeightSolid,next_convex_boundary,fresnel_components,reflect_direction,refract
ROOT=Path(__file__).resolve().parents[3];OUT=Path(__file__).parent
WORK=ROOT/'.evidence-working/clear-play-02/dark-glass-lab/extended'
P=WORK/'playback-pipeline-01/outline';G=WORK/'geometric-playback-inferred'
START=time.time();EPS=1e-6
protocol=json.loads((OUT/'protocol.json').read_text())
DEADLINE=datetime.datetime.fromisoformat(protocol['stages'][2]['deadline']).timestamp()
def gate():
    if time.time()>DEADLINE:raise RuntimeError('Outline deadline reached')
if (OUT/'outline-result.json').exists():raise RuntimeError('Completed outline study cannot restart')
spec=json.loads((ROOT/'reconstruction/studies/geometric-playback/g05-surface.json').read_text())
back=RadialCurvatureBack(**spec['surface']);solid=CircularHeightSolid(back);solid.maximum_level_points=2_000_000
old=np.load(P/'g05-weights.npz');saved=np.load(G/'radial-geometry.npz')
sel=np.argsort(-old['residual_weight'],kind='stable')[:64];r=old['r'][sel]
idx=np.searchsorted(saved['r'],r);np.testing.assert_array_equal(saved['r'][idx],r)
primary={k:saved[k][idx] for k in ['back','outward_normal','exit_direction','X','Y','complete']}
assert primary['complete'].all();N=len(r);events=N
initial_R=fresnel_components(np.ones(N),1,1.5)
weight=.5*(1-initial_R);environment=.5*initial_R.sum(-1)
d=np.zeros((N,3));d[:,2]=-1
R=fresnel_components(np.sum(d*primary['outward_normal'],axis=-1),1.5,1)
background=(weight*(1-R)).sum(-1);weight*=R
point=primary['back'].copy();direction=reflect_direction(d,primary['outward_normal'])
unresolved=np.zeros(N);bracket_max=0.;residual_max=0.;counts=[];records={};paths={j:[np.array([r[j],0.,0.]),point[j].copy()] for j in range(3)}
# Retain external secondary destinations without evaluating RGB.
secondary=[];env_directions=[]
for step in range(2,65):
    gate();active=np.flatnonzero(weight.sum(-1)>EPS)
    if not len(active):break
    if events+len(active)>4096:raise RuntimeError('Event cap reached before dispatch')
    events+=len(active);ev=next_convex_boundary(solid,point[active],direction[active])
    bracket_max=max(bracket_max,float(ev['bracket'].max()));residual_max=max(residual_max,float(abs(ev['residual']).max()))
    good=ev['complete'];bad=active[~good]
    unresolved[bad]+=weight[bad].sum(-1);weight[bad]=0
    ids=active[good];q=ev['point'][good];normal=ev['outward_normal'][good];inc=direction[ids]
    c=np.sum(inc*normal,axis=-1);RR=fresnel_components(c,1.5,1)
    transmitted,tir,discriminant=refract(inc,-normal,1.5,1)
    emitted=weight[ids]*(1-RR);down=(~tir)&(transmitted[:,2]<0);up=(~tir)&~down
    background[ids[down]]+=emitted[down].sum(-1)
    environment[ids[up]]+=emitted[up].sum(-1)
    if down.any():
        t=(-2-q[down,2])/transmitted[down,2];assert (t>0).all()
        hits=q[down]+t[:,None]*transmitted[down]
        secondary.append(np.c_[ids[down],hits[:,:2],emitted[down].sum(-1)])
    if up.any():env_directions.append(np.c_[ids[up],transmitted[up],emitted[up].sum(-1)])
    for j in paths:
        match=np.flatnonzero(ids==j)
        if len(match):paths[j].append(q[match[0]].copy())
    records[f'{step:02d}_ids']=ids;records[f'{step:02d}_point']=q;records[f'{step:02d}_normal']=normal
    records[f'{step:02d}_incident']=inc;records[f'{step:02d}_weight_sp']=weight[ids].copy()
    weight[ids]*=RR;point[ids]=q;direction[ids]=reflect_direction(inc,normal)
    counts.append({'encounter':step,'active':len(active),'tir':int(tir.sum()),'unresolved':len(bad)})
remain=weight.sum(-1);energy=background+environment+remain+unresolved
assert np.max(abs(energy-1))<3e-14
secondary=np.concatenate(secondary) if secondary else np.empty((0,4))
env_directions=np.concatenate(env_directions) if env_directions else np.empty((0,5))
np.savez_compressed(OUT/'outline-paths.npz',r=r,selection=sel,background=background,environment=environment,residual=remain,unresolved=unresolved,final_point=point,final_direction=direction,final_weight_sp=weight,secondary_background=secondary,environment_directions=env_directions,**records)
# Same registered donor bounds used by the primary source proof, now only a
# necessary domain check for these sparse unfiltered secondary destinations.
reg=json.loads((ROOT/'research/captures/dark-glass-lab/apple-matches/public-settled-replay/settled-scores.json').read_text())['media']['registration']['matrix'];inv=np.linalg.inv(np.vstack([reg,[0,0,1]]))
X=secondary[:,1]*245+960;Y=secondary[:,2]*245+542;a=np.floor(X);b=np.floor(Y);ok=np.ones(len(a),bool)
for ix,iy in [(0,0),(1,0),(0,1),(1,1)]:
    u=inv[0,0]*(a+ix)+inv[0,1]*(b+iy)+inv[0,2];v=inv[1,0]*(a+ix)+inv[1,1]*(b+iy)+inv[1,2]
    ok&=(a+ix>=0)&(a+ix<1920)&(b+iy>=0)&(b+iy<1080)&(u>=0)&(u<1919)&(v>=0)&(v<1079)
result={'status':'LIMITED_PATH_AUDIT_NO_REFLECTION_IMAGE','launches':N,'new_primary_rays':0,'internal_events':events,'level_evaluations':solid.level_point_evaluations,'maximum_encounters':64,'selected_from':'Largest residuals of the prior997-ray audit, including ties. Same physical surface. Old pending internal states were not saved, requiring this bounded replay.','prior_selected_residual_max':float(old['residual_weight'][sel].max()),'residual_max_64':float(remain.max()),'unresolved_max':float(unresolved.max()),'above_tolerance_count':int((remain+unresolved>EPS).sum()),'power_tolerance':EPS,'conservation_error':float(abs(energy-1).max()),'root_bracket_max_L':bracket_max,'level_residual_max':residual_max,'background_weight_range':[float(background.min()),float(background.max())],'environment_weight_range':[float(environment.min()),float(environment.max())],'secondary_background_events':len(secondary),'unsupported_secondary_background_events':int((~ok).sum()),'unsupported_secondary_power_sum_across_launches':float(secondary[~ok,3].sum()),'environment_observations':0,'RGB_queries':0,'image_renders':0,'counts':counts,'wall_seconds':time.time()-START,'limits':'Sparse selected paths only. Fresnel power needs scene-linear radiance and measured or independently justified reflected environment. No target-colored replacement, complete-image proof or physical-material identification.'}
(OUT/'outline-result.json').write_text(json.dumps(result,indent=2)+'\n')
# Actual height and traced points; uniform XY plot scale, no decorative lens.
xs=np.linspace(.85,1.01,512);h=back.height_gradient(xs,np.zeros_like(xs))[0]
def screen(x,z):return (70+(x-.85)*7000,300-z*7000)
def poly(points):return ' '.join(f'{screen(v[0],v[2])[0]:.5f},{screen(v[0],v[2])[1]:.5f}' for v in points)
curve=[np.array([x,0,-v]) for x,v in zip(xs,h) if x<=1]
svg=['<svg xmlns="http://www.w3.org/2000/svg" width="1260" height="520" viewBox="0 0 1260 520">','<rect width="1260" height="520" fill="white"/>','<text x="24" y="28" font-size="18">Actual G05 section and selected reflected paths; equal physical axis scale</text>',f'<polyline points="{poly(curve)}" stroke="black" stroke-width="2" fill="none"/>',f'<path d="M {screen(.85,0)[0]} 300 L {screen(1,0)[0]} 300" stroke="black" stroke-width="2"/>']
for j,color in enumerate(['#be123c','#2563eb','#059669']):svg.append(f'<polyline points="{poly(paths[j])}" stroke="{color}" stroke-width="1.2" fill="none"/>');svg.append(f'<text x="24" y="{55+22*j}" fill="{color}" font-size="15">r/L={r[j]:.8f}; residual after64={remain[j]:.6g}</text>')
svg.append('<text x="24" y="490" font-size="15">No reflected environment RGB is assigned. Paths outside this section view are clipped by the viewport.</text></svg>');(OUT/'outline-section.svg').write_text('\n'.join(svg)+'\n')
print(json.dumps({k:v for k,v in result.items() if k!='counts'}),flush=True)
