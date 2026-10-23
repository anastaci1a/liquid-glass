"""Actual profile sections and retained Snell rays; no new optical traces."""
from pathlib import Path
import datetime,json
import numpy as np
from footprint_curvature_back import FootprintCurvatureBack
ROOT=Path(__file__).resolve().parents[3];OUT=Path(__file__).parent;p=json.loads((OUT/'protocol.json').read_text());assert datetime.datetime.now(datetime.timezone.utc)<datetime.datetime.fromisoformat(p['deadline'])
spec=json.loads((ROOT/'reconstruction/studies/geometric-expanded-pipeline/summary.json').read_text())['geometry'];fit=json.loads((OUT/'inference.json').read_text());surface=FootprintCurvatureBack(tuple(spec['surface_half']),spec['surface_radius'],fit['knots'],fit['best']['curvature']);q=np.load(OUT/'checkpoint-paths.npz')
svg=['<svg xmlns="http://www.w3.org/2000/svg" width="1120" height="650" viewBox="0 0 1120 650">','<rect width="1120" height="650" fill="white"/>','<text x="25" y="25" font-size="18">Same integrated-curvature height, intersections and primary rays</text>','<text x="25" y="48" font-size="14">Index 1.5; background distance 2.1 L; common physical axis scale</text>'];paths=[]
for axis,offset,origin,half in [('x',130,7.4,surface.half[0]),('y',425,1.7,surface.half[1])]:
 section=surface.section(np.linspace(-half,half,301),axis);idx=0 if axis=='x' else 1
 def xy(point):return (30+(point[idx]+origin)*70,offset-point[2]*70)
 def poly(points):return ' '.join(f'{xy(t)[0]:.5f},{xy(t)[1]:.5f}' for t in points)
 contour=np.r_[section['front'],section['back'][::-1],section['front'][:1]];svg.append(f'<polyline points="{poly(contour)}" stroke="black" stroke-width="1.5" fill="#eef2ff"/>');svg.append(f'<text x="25" y="{offset-48}" font-size="16">{axis.upper()} section; projected crease remains unresolved</text>')
 line=np.array([[-half,0,-2.1],[half,0,-2.1]]) if axis=='x' else np.array([[0,-1.5,-2.1],[0,1.5,-2.1]]);svg.append(f'<polyline points="{poly(line)}" stroke="#64748b" stroke-dasharray="4 3" fill="none"/>')
 picks=[(8,1),(8,8),(8,15)] if axis=='x' else [(3,8),(8,8),(13,8)]
 for (r,c),color in zip(picks,['#be123c','#2563eb','#15803d']):
  assert q['complete'][r,c];entry=np.array([q['x'][r,c],q['y'][r,c],0]);incoming=entry.copy();incoming[2]=.35;source=np.array([q['X'][r,c],q['Y'][r,c],-2.1]);points=np.array([incoming,entry,q['back'][r,c],source]);paths.append(dict(section=axis,points=points.tolist()));svg.append(f'<polyline points="{poly(points)}" stroke="{color}" stroke-width="1.2" fill="none"/>')
svg+=['<text x="25" y="630" font-size="14">Height and normals share one polynomial. No diagnostic warp or decorative surface.</text>','</svg>'];(OUT/'sections-rays.svg').write_text('\n'.join(svg)+'\n');(OUT/'sections.json').write_text(json.dumps(dict(new_rays=0,RGB_queries=0,section_height_evaluations=602,paths=paths),indent=2)+'\n')
