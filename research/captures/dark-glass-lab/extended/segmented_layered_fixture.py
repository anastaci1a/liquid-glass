"""Separate clear control content from background scattering/material.

Original source/reference files stay frozen. Known vector content is subtracted
from the generated incident RGB, then projected separately through the same
optical field. This tests compositing order, not a claim about Apple internals.
"""
from pathlib import Path
import sys,json,copy,time
sys.path.insert(0,'/workspace/docs/liquid-glass/experiments/reconstruction')
import cv2,numpy as np
from scipy.optimize import minimize,lsq_linear
from scipy.interpolate import BSpline
from extended_fit import Study,KNOTS
from vector_foreground import coverage
from render import fit_material,shade
from source_support import coverage_report,supported
root=Path('/evidence/extended');folder=root/'active-segmented-selector';out=folder/'layered-content-probe';out.mkdir(exist_ok=True)
INK=np.array([1.,.35,.4],np.float32)
class Layered(Study):
 def __init__(self,path,content_scale,phase=False):
  super().__init__(path);self.phase=phase;self.original=self.source.copy();track=self.case['background_estimate']['track_pose'];camera=track[2]/823.5;bg=self.source[500,400].copy();poses=self.case['background_estimate']['font_calibration'];nearest=min(poses,key=lambda r:abs((r['selected']['pose'][0]-957.5)*camera+track[0]-self.case['center'][0]))['text'];self.alpha_source=np.zeros((4320,7680),np.float32)
  for record in poses:
   layer=copy.deepcopy(record['selected']['layer']);box=np.array(layer['vector_box'],float);box[[0,2]]=(box[[0,2]]-957.5)*camera+track[0];box[[1,3]]=(box[[1,3]]-547.5)*camera+track[1];center=np.array([(box[0]+box[2])/2,(box[1]+box[3])/2]*2);large=center+(box-center)*1.25
   layer['box']=[int(large[0]-3),int(large[1]-3),int(large[2]+4),int(large[3]+4)];layer['vector_box']=box.tolist();A=coverage(folder,layer);a,b,c,d=layer['box'];self.source[b:d,a:c]-=A[...,None]*(INK-bg)
   layer['vector_box']=(center+(box-center)*(content_scale if record['text']==nearest else 1.)).tolist();self.alpha_source[b*4:d*4,a*4:c*4]=coverage(folder,layer,4)
   if record['text']==nearest:self.anchor=(center[:2]-self.case['center'])/self.L
  self.source=np.clip(self.source,0,1);self.cache.clear()
 def geometry_field(self,x,y,p):
  if not self.phase:return super().geometry_field(x,y,p)
  q={**p,'core_x':0.,'core_y':0.,'tangent':0.,'coupling':0.,'cap_normal_gain':0.,'cap_join_width':0.};X,Y,d,J=super().geometry_field(x,y,q);*_,(sd,nx,ny)=self.shape(x,y,q);rx=x-self.anchor[0];ry=y-self.anchor[1];u=np.clip(d/p['anchor_band'],0,1);W=u**3*(u*(6*u-15)+10);Wd=30*u*u*(u-1)**2/p['anchor_band'];P=.5*(p['anchor_x']*rx*rx+p['anchor_y']*ry*ry)
  return X-p['anchor_x']*W*rx+Wd*P*nx,Y-p['anchor_y']*W*ry+Wd*P*ny,d,J
 def alpha(self,x,y,p):
  X,Y,*_=self.geometry_field(x,y,p);px=((X*self.L+self.case['center'][0]+self.backdrop_shift[0]+.5)*4-.5).astype(np.float32);py=((Y*self.L+self.case['center'][1]+self.backdrop_shift[1]+.5)*4-.5).astype(np.float32)
  return cv2.remap(self.alpha_source,px,py,cv2.INTER_LINEAR).reshape(x.shape)
 def fit(self,p):
  x=self.x.ravel()[self.indices];y=self.y.ravel()[self.indices];C,J=self.field(x,y,p);A=self.alpha(x,y,p);w=1-A;target=(self.expected-A[...,None]*INK)/np.maximum(w[...,None],1e-5);co,_=fit_material(C,J,target,self.weights*w);B=shade(C,J,co);pred=B*w[...,None]+A[...,None]*INK;return float(np.mean(((pred-self.expected)*self.weights[:,None])**2)),co
 def render(self,p,co,scale=1):
  B=super().render(p,co,scale);H,W=B.shape[:2];A=np.empty((H,W),np.float32)
  for row,bottom,width,x,y in self.raster_tiles(scale):A[row:bottom]=self.alpha(x,y,p).reshape(bottom-row,2,width,2).mean((1,3))
  return B*(1-A[...,None])+A[...,None]*INK
