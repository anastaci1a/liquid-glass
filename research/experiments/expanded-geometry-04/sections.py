"""Actual geometry and saved primary rays; no optical or RGB evaluation."""
from pathlib import Path
import json,datetime
import numpy as np
from rounded_rectangle_back import RoundedRectangleHarmonicBack
from parabolic_front_solid import ParabolicFrontHeightSolid
ROOT=Path(__file__).resolve().parents[3];OUT=Path(__file__).parent;p=json.loads((OUT/'protocol.json').read_text());assert datetime.datetime.now(datetime.timezone.utc)<datetime.datetime.fromisoformat(p['deadline'])
scene=json.loads((ROOT/'reconstruction/studies/geometric-expanded-pipeline/summary.json').read_text())['geometry'];solid=ParabolicFrontHeightSolid(RoundedRectangleHarmonicBack(tuple(scene['surface_half']),scene['surface_radius']),.4);q=np.load(OUT/'checkpoint-paths.npz');paths=[]
svg=['<svg xmlns="http://www.w3.org/2000/svg" width="1120" height="650" viewBox="0 0 1120 650">','<rect width="1120" height="650" fill="white"/>','<text x="25" y="25" font-size="18">Actual curved-front solid and retained primary rays; common physical scale</text>','<text x="25" y="48" font-size="14">Index 1.5; front depth 0.4 L; background 2 L behind the original reference plane</text>']
for axis,offset,origin,half in [('x',130,7.4,solid.back.half[0]),('y',425,1.7,solid.back.half[1])]:
 v=np.linspace(-half,half,401);s=solid.section(v,axis);front=s['front'];back=s['back'];idx=0 if axis=='x' else 1
 def xy(point):return (30+(point[idx]+origin)*70,offset-point[2]*70)
 def poly(points):return ' '.join(f'{xy(t)[0]:.5f},{xy(t)[1]:.5f}' for t in points)
 for a in [front,back]:F,_=solid.level_gradient(a);assert np.max(abs(F))<1e-10
 contour=np.r_[front,back[::-1],front[:1]];svg.append(f'<polyline points="{poly(contour)}" stroke="black" stroke-width="1.5" fill="#eef2ff"/>');svg.append(f'<text x="25" y="{offset-48}" font-size="16">{axis.upper()} section; sides are part of the solid</text>')
 line=np.array([[-half,0,-2],[half,0,-2]]) if axis=='x' else np.array([[0,-1.5,-2],[0,1.5,-2]])
 svg.append(f'<polyline points="{poly(line)}" stroke="#64748b" stroke-dasharray="4 3" fill="none"/>')
 picks=[(8,3),(8,15),(8,27)] if axis=='x' else [(4,15),(8,15),(12,15)]
 for (r,c),color in zip(picks,['#be123c','#2563eb','#15803d']):
  entry=q['entry'][r,c];exit=q['exit'][r,c];assert q['complete'][r,c]
  incoming=entry.copy();incoming[2]=.6;source=np.array([q['X'][r,c],q['Y'][r,c],-2]);points=np.array([incoming,entry,exit,source]);paths.append(dict(section=axis,points=points.tolist()))
  svg.append(f'<polyline points="{poly(points)}" stroke="{color}" stroke-width="1.2" fill="none"/>')
svg+=['<text x="25" y="630" font-size="14">No reflected radiance, fitted halo, independent normal or decorative lens geometry.</text>','</svg>'];(OUT/'sections-rays.svg').write_text('\n'.join(svg)+'\n')
level=solid.level_point_evaluations;prior=json.loads((OUT/'source-preflight.json').read_text())['total_level_points'];assert level+prior<=p['budgets']['total_new_level_points']
(OUT/'sections.json').write_text(json.dumps(dict(level_points=level,cumulative_level_points=prior+level,height_points=solid.height_point_evaluations,new_rays=0,RGB_queries=0,native_images=0,source='Same adapter and parameters as native paths; selected rays reused from checkpoint.',paths=paths),indent=2)+'\n')
