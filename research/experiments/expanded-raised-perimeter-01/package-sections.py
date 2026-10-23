"""Presentation of immutable cached paths only; no height or ray evaluation."""
from pathlib import Path
import json,hashlib
import numpy as np
ROOT=Path(__file__).resolve().parents[3];OUT=Path(__file__).parent;q=np.load(OUT/'native-paths.npz');scene=json.loads((ROOT/'reconstruction/studies/geometric-expanded-pipeline/summary.json').read_text())['geometry'];B=q['back'];inside=q['inside'];cx,cy=scene['center'];L=88.5
H,W=inside.shape;row=int(np.nanargmin(np.nanmedian(abs(B[...,1]),axis=1)));col=int(np.nanargmin(np.nanmedian(abs(B[...,0]),axis=0)))
for axis,name in [(0,'longitudinal'),(1,'transverse')]:
 points=B[row] if axis==0 else B[:,col];mask=inside[row] if axis==0 else inside[:,col];ids=np.flatnonzero(mask&np.isfinite(points).all(1));selected=ids[np.linspace(0,len(ids)-1,7,dtype=int)];source=(q['X'][row] if axis==0 else q['Y'][:,col]);source=(source-(cx if axis==0 else cy))/L;values=points[ids,axis];lo=min(float(values.min()),float(source[selected].min()))-.15;hi=max(float(values.max()),float(source[selected].max()))+.15
 def xy(u,z):return (50+(u-lo)/(hi-lo)*860,45+(.15-z)/2.3*465)
 def poly(uv):return ' '.join(f'{xy(float(u),float(z))[0]:.3f},{xy(float(u),float(z))[1]:.3f}' for u,z in uv)
 parts=['<svg xmlns="http://www.w3.org/2000/svg" width="960" height="600" viewBox="0 0 960 600">','<rect width="960" height="600" fill="white"/>',f'<text x="30" y="24" font-family="sans-serif" font-size="17">Cached native {name} section and seven primary paths</text>',f'<polyline points="{poly([(values.min(),0),(values.max(),0)])}" fill="none" stroke="#444" stroke-width="2"/>',f'<polyline points="{poly([(p[axis],p[2]) for p in points[ids]])}" fill="none" stroke="#a22" stroke-width="2"/>']
 for j in selected:
  v=points[j,axis];z=points[j,2];parts.append(f'<polyline points="{poly([(v,.08),(v,0),(v,z),(source[j],-2)])}" fill="none" stroke="#267b8c" stroke-width="1.2"/>')
 parts.extend(['<text x="30" y="550" font-family="sans-serif" font-size="14">Red: actual cached back. Gray: flat front. Blue: cached primary ray projections.</text>','<text x="30" y="574" font-family="sans-serif" font-size="14">Coordinates in L; axes independently scaled. No reflected-path or environment claim.</text>','</svg>']);(OUT/f'{name}-cached-paths.svg').write_text('\n'.join(parts))
files=['reconstruction/annular_profile.py','reconstruction/raised_perimeter_back.py','reconstruction/geometric_optics.py','reconstruction/geometric_render.py',str((OUT/'preflight.py').relative_to(ROOT)),str((OUT/'observe.py').relative_to(ROOT))];(OUT/'code-snapshot.json').write_text(json.dumps({p:hashlib.sha256((ROOT/p).read_bytes()).hexdigest() for p in files},indent=2)+'\n')
