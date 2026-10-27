"""Positive-area integration for right-side outline width choices."""
import numpy as np
from miniplayer_refinement_effects import pixel_rule_batch
from miniplayer_outline_taper import transition
from outline_response import cap_strength

def integrate_widths(crop,coordinate,center,angular,config,widths,order,charge,pixel_mask=None,tail=1e-10):
 x0,y0,x1,y1=crop;yy,xx=np.mgrid[y0:y1,x0:x1];charge('distance_points',xx.size)
 sd,_,_=coordinate.boundary_distance(xx-center[0],yy-center[1])
 maximum=config['base_scale']*max(widths)*(config['plateau_native']+config['fade_native']*np.sqrt(-np.log(tail)))
 left_boundary=center[0]-coordinate.half[0]+2*coordinate.half[0]*config['left_fraction']
 mask=(sd<=np.sqrt(.5))&(sd>=-maximum-np.sqrt(.5))&(xx+.5>left_boundary)
 if pixel_mask is not None:mask&=pixel_mask
 iy,ix=np.nonzero(mask);out=np.zeros((len(widths),2)+sd.shape)
 for start in range(0,len(iy),64):
  i,j=iy[start:start+64],ix[start:start+64];xy=np.stack([xx[i,j]-center[0],yy[i,j]-center[1]],1)
  pts,w,owner=pixel_rule_batch(xy,coordinate,order,charge)
  if not len(w):continue
  charge('distance_points',len(w));d,_,_=coordinate.boundary_distance(pts[:,0],pts[:,1]);assert d.max()<2e-8
  t=transition(pts[:,0],coordinate.half[0],config['left_fraction'],config['right_fraction']);angular_strength=cap_strength(pts[:,0],pts[:,1],coordinate.half,coordinate.original_radius,(0,0),angular)
  for k,right in enumerate(widths):
   scale=config['base_scale']*(config['left_scale']+(right-config['left_scale'])*t)
   charge('profile_points',2*len(w));v=np.exp(-(np.maximum(-d-config['plateau_native']*scale,0)/(config['fade_native']*scale))**2)*angular_strength
   out[k,0,i,j]=np.bincount(owner,weights=w*v,minlength=len(xy))
   out[k,1,i,j]=np.bincount(owner,weights=w*v*config['brightness_increase_reduction']*(1-t),minlength=len(xy))
 assert np.isfinite(out).all() and out.min()>=0 and out[:,0].max()<=1+1e-12
 return out
