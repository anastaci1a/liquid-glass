import os,time,json,sys,subprocess
from pathlib import Path
import numpy as np
from geometric_optics import RadialCurvatureBack,trace_flat_front_orthographic
os.umask(2);D=Path('/evidence/extended/geometric-playback-distance');p=json.loads((D/'protocol-FIRST.json').read_text());rows=[];raycount=0;calls=0
for distance in [1,4]:
 remaining=p['deadline_unix']-time.time();assert remaining>0
 folder=D/f'distance-{distance}';subprocess.run([sys.executable,str(D/'code/geometric_inverse.py'),'/evidence/extended/playback-short-round/pass-03/replay-record.json',str(folder),'--distance',str(distance),'--seconds',str(min(120,remaining))],check=True,timeout=min(125,remaining))
 result=json.loads((folder/'result.json').read_text());raycount+=result['geometry_rays'];calls+=result['rhs_calls'];assert raycount<=105000 and calls<=6000
 rows.append(dict(distance=distance,new_geometry=result['rows'][-1],fresh_rays=result['geometry_rays'],RHS_calls=result['rhs_calls']))
old=json.loads(Path('/evidence/extended/geometric-playback-inverse/result.json').read_text());rows.insert(1,dict(distance=2,new_geometry=old['rows'][-1],fresh_rays=0,RHS_calls=0,evidence_reused=True))
g=np.load('/evidence/extended/geometric-playback-inverse/geometry-513.npz');s=RadialCurvatureBack(g['nodes'],g['curvature']);fixed=[];r=np.linspace(0,1-1e-9,2001)
for distance in [1,4]:
 assert time.time()<p['deadline_unix'];q=trace_flat_front_orthographic(s,r,np.zeros_like(r),1.5,distance);raycount+=len(r);assert raycount<=105000 and q['complete'].all()
 jac=np.gradient(q['X'],r);fixed.append(dict(distance=distance,edge_inward_displacement_L=float(1-q['X'][-1]),minimum_radial_jacobian=float(jac.min()),all_paths_complete=True));np.savez(D/f'fixed-surface-D{distance}.npz',r=r,**q)
result=dict(classification='USEFUL_GEOMETRIC_DISTANCE_AMBIGUITY_NOT_IMAGE_FIDELITY',protocol=p,compensating_surfaces=rows,fixed_surface=fixed,fresh_geometry_rays=raycount,RHS_calls=calls,wall_seconds=time.time()-p['started_unix'],images=0,fits=0,interpretation='At fixed geometry distance changes refraction. Different actual convex back heights can compensate distance to recover the same diagnostic map, so this single map cannot identify physical distance and geometry uniquely. This is not an Apple inverse solution or a rendering gain. Edge reversal is wanted where the reference shows it, not prohibited.',limits='Fixed orthographic camera/index1.5/primary branch. Inverse initialized from historical diagnostic map. No source queries/images, finite camera, reflection radiance or performance claim.')
(D/'result.json').write_text(json.dumps(result,indent=2)+'\n');print(json.dumps(result))
