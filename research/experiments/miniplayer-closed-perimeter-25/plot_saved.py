"""Geometry presentation from saved sections and actual internal segments only."""
from pathlib import Path
import json,datetime
import numpy as np
O=Path(__file__).parent;p=json.loads((O/'protocol.json').read_text());payload=0;records=0
for member in ['expanded','compact']:
 sections=json.loads((O/f'{member}-sections.json').read_text())['sections'];q=np.load(O/f'{member}-paths.npz');entry=q['entry'];exit=q['exit'];regular=q['regular_entry'];payload+=entry.nbytes+exit.nbytes+regular.nbytes
 extent=max(abs(v) for v in sections[0]['coordinate']);sx=780/(2*extent);parts=['<svg xmlns="http://www.w3.org/2000/svg" width="840" height="310" viewBox="0 0 840 310">','<rect width="840" height="310" fill="white"/>','<g font-family="sans-serif" font-size="13" fill="black">',f'<text x="12" y="20">{member}: actual closed surface; z magnified 8 times</text>']
 for j,s in enumerate(sections):
  axis=0 if s['axis']=='x' else 1;other=1-axis;y0=90+140*j;scalez=8*sx
  def point(x,z):return f'{420+sx*x:.5f},{y0-scalez*z:.5f}'
  for k in ['front','back']:parts.append('<polyline fill="none" stroke="black" stroke-width="1.3" points="'+' '.join(point(x,z) for x,z in zip(s['coordinate'],s[k]))+'"/>')
  ids=np.flatnonzero(regular&(entry[:,other]==0));chosen=ids[np.linspace(0,len(ids)-1,min(8,len(ids))).astype(int)]
  for i in chosen:
   parts.append(f'<line x1="{420+sx*entry[i,axis]:.5f}" y1="{y0-scalez*entry[i,2]:.5f}" x2="{420+sx*exit[i,axis]:.5f}" y2="{y0-scalez*exit[i,2]:.5f}" stroke="#176ac0"/>');records+=1
  parts.append(f'<text x="12" y="{y0-45}">{s["axis"]} section; black same-F roots, blue actual entry-to-exit rays</text>')
 parts+=['</g></svg>'];(O/f'{member}-actual-sections.svg').write_text('\n'.join(parts))
(O/'presentation.json').write_text(json.dumps({'at':datetime.datetime.now(datetime.timezone.utc).isoformat(),'decoded_payload_bytes':payload,'saved_ray_segments':records,'new_rays_heights_RGB':0,'vertical_scale':8,'source':'Saved same-F sections and actual cached entry/exit positions only.'},indent=2)+'\n')
