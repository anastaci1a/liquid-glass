"""Engineering SVG sections from exact saved geometry; no new optical rays."""
from pathlib import Path
import sys,json,numpy as np,html
P=Path('/evidence/extended/agent-pipeline-01');O=P/'refraction/h1';sys.path.insert(0,str(P/'code'))
from expanded_surface import ExpandedHarmonicBack
g=json.loads((O/'geometry-checkpoint.json').read_text())['scene'];s=ExpandedHarmonicBack(tuple(g['surface_half']),g['surface_radius']);q=np.load(O/'checkpoint-paths.npz');parts=['<svg xmlns="http://www.w3.org/2000/svg" width="1200" height="720" viewBox="0 0 1200 720"><rect width="1200" height="720" fill="white"/><g font-family="sans-serif" font-size="13" fill="black">'];parts.append('<text x="25" y="25">Expanded H1: actual surface, actual shared-Snell paths. L=88.5 native px; n=1/1.5/1; D=2L.</text>')
for row,(axis,ext) in enumerate([('x',s.half[0]),('y',s.half[1])]):
 v=np.linspace(-ext,ext,801);sec=s.section(v,axis);h=sec['back'][:,2]
 for col in range(2):
  x0=70+col*590;y0=75+row*325;w=500;H=240;zmin=-.16 if col==0 else -2.05;zmax=.04 if col==0 else .15
  X=lambda u:x0+(u+ext)/(2*ext)*w
  Y=lambda z:y0+(zmax-z)/(zmax-zmin)*H
  label=f'{axis} section: '+('surface detail; different horizontal/vertical scales' if col==0 else 'actual saved paths to z=-2L')
  parts.append(f'<text x="{x0}" y="{y0-15}">{label}</text>')
  for z in ([0,-.05,-.1,-.15] if col==0 else [0,-1,-2]):parts.append(f'<path d="M{x0},{Y(z)}h{w}" stroke="#ddd"/><text x="{x0-45}" y="{Y(z)+4}">{z:g}</text>')
  parts.append(f'<text x="{x0-48}" y="{y0-5}">z/L</text><text x="{x0+w/2}" y="{y0+H+30}">{axis}/L</text>')
  for u in [-ext,0,ext]:parts.append(f'<text x="{X(u)-15}" y="{y0+H+16}">{u:.3f}</text>')
  def path(us,zs,color,width=1):
   d=' '.join(('M' if i==0 else 'L')+f'{X(u):.4f},{Y(z):.4f}' for i,(u,z) in enumerate(zip(us,zs)) if np.isfinite([u,z]).all());parts.append(f'<path d="{d}" fill="none" stroke="{color}" stroke-width="{width}"/>')
  path(v,h,'#174b8c',2);path([-ext,ext],[0,0],'black')
  if col:
   if axis=='x':ix=np.linspace(2,q['x'].shape[1]-3,9,dtype=int);iy=np.full(9,q['x'].shape[0]//2)
   else:iy=np.linspace(2,q['x'].shape[0]-3,9,dtype=int);ix=np.full(9,q['x'].shape[1]//2)
   coord=0 if axis=='x' else 1
   for j,i in zip(iy,ix):
    if q['complete'][j,i] and q['inside'][j,i]:
     p0=q[axis][j,i];b=q['back'][j,i];end=q['X' if axis=='x' else 'Y'][j,i];path([p0,p0,b[coord],end],[.1,0,b[2],-2],'#c35b20',.8)
parts.append('</g></svg>');(O/'same-surface-sections.svg').write_text(''.join(parts));print('Saved exact engineering sections; zero new rays/RGB')
