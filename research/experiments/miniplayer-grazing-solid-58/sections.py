"""Presentation only from retained same-surface section/path arrays."""
from pathlib import Path
import numpy as np
D=Path(__file__).parent;z=np.load(D/'paths-sections.npz');front=z['expanded_y_front_section'];back=z['expanded_y_back_section'];entry=z['expanded_n1.5_entry'][:6];exit=z['expanded_n1.5_exit'][:6];ref=z['expanded_front_reflection'][:6]
front=np.concatenate([front,entry]);front=front[np.argsort(front[:,1])]
scale=400.;X=lambda p:500+scale*p[1];Y=lambda p:105-scale*p[2]
def path(points):return ' '.join(f'{X(p):.5f},{Y(p):.5f}' for p in points)
s=['<svg xmlns="http://www.w3.org/2000/svg" width="1000" height="300" viewBox="0 0 1000 300">','<rect width="1000" height="300" fill="white"/>','<text x="24" y="25" font-size="19">Same implicit solid: transverse section and retained rays</text>','<text x="24" y="49" font-size="14">Physical axes at 1:1. Blue: actual front/back. Orange: direct reflection. Green: internal primary segment.</text>','<defs><clipPath id="plot"><rect x="70" y="60" width="860" height="145"/></clipPath></defs>','<g clip-path="url(#plot)">',f'<polyline points="{path(front)}" fill="none" stroke="#175cb4" stroke-width="2"/>',f'<polyline points="{path(back)}" fill="none" stroke="#175cb4" stroke-width="2"/>']
for j in [0,2,3,5]:
 p,q=entry[j],exit[j];a=p+.2*ref[j];s+=[f'<line x1="{X(p):.5f}" y1="{Y(p):.5f}" x2="{X(q):.5f}" y2="{Y(q):.5f}" stroke="#16814d" stroke-width="1.3"/>',f'<line x1="{X(p):.5f}" y1="{Y(p):.5f}" x2="{X(a):.5f}" y2="{Y(a):.5f}" stroke="#d47b11" stroke-width="1.3"/>']
s+=['</g>','<text x="24" y="228" font-size="14">Rays are actual retained entry/exit/direction values; drawn segments are clipped to this view.</text>','<text x="24" y="250" font-size="14">The backdrop at z = -2.1 L lies outside this frame. No scene color or resolved later TIR path is drawn.</text>','<text x="24" y="272" font-size="14">Surface polylines use cached sections and entry points. This is a geometry diagram, not a reconstruction.</text>','</svg>'];(D/'section-rays.svg').write_text('\n'.join(s))
