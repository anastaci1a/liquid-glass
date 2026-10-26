"""Reproducer for the recorded projection repair controls; no optical calls."""
from pathlib import Path
import numpy as np,json
from shoulder_core_coordinate import ShoulderCoreCoordinate
B=Path(__file__).parent;R=B.parents[2];F=json.loads((B/'legacy-numerical-family.json').read_text());L=88.5;g=F['geometry'];counter={}
def count(k,n):counter[k]=counter.get(k,0)+n
c=ShoulderCoreCoordinate((F['members']['expanded']['major_half']+1.5/L,g['minor_half']),g['corner_radius']-1/L,.25/L,count)
center=np.array(json.loads((R/'reconstruction/studies/geometric-expanded-pipeline/summary.json').read_text())['geometry']['center'])+[-.5,0]
case=json.loads((R/'.evidence-working/expanded-geometry-02/a/case.json').read_text());crop=case['crop'];yy,xx=np.mgrid[0:32,0:2720]
x=(crop[0]+xx*.5-.25-center[0])/L;y=(crop[1]+yy*.5-.25-center[1])/L
d,nx,ny=c.distance_gradient(x,y);assert np.isfinite(d).all();assert np.max(abs(nx[d>0]**2+ny[d>0]**2-1))<1e-14
t=np.linspace(.01,2*np.pi-.01,128);x=(c.half[0]-.2)*np.cos(t);y=(c.half[1]-.1)*np.sin(t);eps=1e-6
d,nx,ny=c.distance_gradient(x,y);dx=(c.distance_gradient(x+eps,y)[0]-c.distance_gradient(x-eps,y)[0])/(2*eps);dy=(c.distance_gradient(x,y+eps)[0]-c.distance_gradient(x,y-eps)[0])/(2*eps)
assert max(np.max(abs(dx-nx)),np.max(abs(dy-ny)))<1e-7
mirror=c.distance_gradient(-x,-y);assert np.max(abs(mirror[0]-d))<1e-12 and np.max(abs(mirror[1]+nx))<1e-12
s=ShoulderCoreCoordinate(tuple(np.array(c.half)*L),c.original_radius*L,c.shoulder*L,count);sd,sx,sy=s.distance_gradient(x*L,y*L)
assert np.max(abs(sd/L-d))<1e-11 and np.max(abs(sx-nx))<1e-11
assert counter['coordinate_queries']<100000
print('PASS projection, gradients, inversion and physical scale',counter)
