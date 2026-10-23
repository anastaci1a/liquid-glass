"""Actual surface sections, equal physical scale on both axes of each panel."""
import json
import numpy as np
from pathlib import Path
from rounded_rectangle_back import RoundedRectangleHarmonicBack
OUT=Path(__file__).parent
c=json.loads((OUT/'geometry-check.json').read_text());s=RoundedRectangleHarmonicBack(tuple(c['half']),c['radius'])
svg=['<svg xmlns="http://www.w3.org/2000/svg" width="1080" height="340" viewBox="0 0 1080 340"><rect width="1080" height="340" fill="white"/>'];data={}
for axis,extent,top in [('x',s.half[0],65),('y',s.half[1],235)]:
 v=np.linspace(-extent,extent,401);zero=np.zeros_like(v)
 h=s.height_gradient(v,zero)[0] if axis=='x' else s.height_gradient(zero,v)[0]
 scale=960/(2*extent);points=' '.join(f'{60+(t+extent)*scale:.4f},{top+z*scale:.4f}' for t,z in zip(v,h))
 svg.append(f'<text x="60" y="{top-30}" font-family="sans-serif" font-size="18">{axis} section: front z=0, back z=-h; equal axis scale</text>')
 svg.append(f'<path d="M60 {top} H1020" stroke="#777"/><polyline points="{points}" fill="none" stroke="#2769a5" stroke-width="2"/>')
 svg.append(f'<text x="60" y="{top+75}" font-family="sans-serif" font-size="14">Horizontal extent ±{extent:.6f} L; maximum depth {h.max():.6f} L</text>')
 data[axis]={'coordinate':v.tolist(),'height':h.tolist(),'physical_units':'L','pixels_per_L_both_axes':scale}
svg.append('</svg>');(OUT/'surface-sections.svg').write_text(''.join(svg));(OUT/'surface-sections.json').write_text(json.dumps({'surface_height_evaluations':802,'new_rays':0,'sections':data},indent=2)+'\n')
