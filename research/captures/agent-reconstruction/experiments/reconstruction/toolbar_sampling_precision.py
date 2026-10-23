"""Explicit full-fraction bilinear comparator; not an accepted scoring change."""
import numpy as np
import cv2
import toolbar_candidate as baseline
from render import shade

def bilinear(image,x,y,*,gradient=False):
    x,y=np.broadcast_arrays(np.asarray(x,float),np.asarray(y,float));ix=np.floor(x).astype(np.int64);iy=np.floor(y).astype(np.int64);fx=x-ix;fy=y-iy;channels=image.shape[2:] or ();v=[]
    for dy,dx in [(0,0),(0,1),(1,0),(1,1)]:
        xx=ix+dx;yy=iy+dy;valid=(xx>=0)&(xx<image.shape[1])&(yy>=0)&(yy<image.shape[0]);sample=image[np.clip(yy,0,image.shape[0]-1),np.clip(xx,0,image.shape[1]-1)];sample=sample*valid.reshape((*valid.shape,*([1]*len(channels))));v.append(sample)
    fx=fx.reshape((*fx.shape,*([1]*len(channels))));fy=fy.reshape((*fy.shape,*([1]*len(channels))));a,b,c,d=v;out=a*(1-fx)*(1-fy)+b*fx*(1-fy)+c*(1-fx)*fy+d*fx*fy
    if gradient:return out,(b-a)*(1-fy)+(d-c)*fy,(c-a)*(1-fx)+(d-b)*fx
    return out

def quantized_coordinates(x,y):
    xy,f=cv2.convertMaps(np.asarray(x,np.float32),np.asarray(y,np.float32),cv2.CV_16SC2,nninterpolation=False);return xy[...,0].astype(float)+(f%cv2.INTER_TAB_SIZE)/cv2.INTER_TAB_SIZE,xy[...,1].astype(float)+(f//cv2.INTER_TAB_SIZE)/cv2.INTER_TAB_SIZE

def render(source,case,p,*,atlas):
    L=min(case['half']);sigma=p['source_sigma']*L;blur=cv2.GaussianBlur(source,(0,0),sigma) if sigma else source;x0,y0,x1,y1=case['crop'];H=y1-y0;W=x1-x0;C=np.zeros((H,W,3),np.float32);alpha=np.zeros((H,W),np.float32)
    for top in range(0,H,8):
        bot=min(top+8,H);yy,xx=np.mgrid[top*4:bot*4,0:W*4];x=(x0+(xx+.5)/4-.5-case['center'][0])/L;y=(y0+(yy+.5)/4-.5-case['center'][1])/L;sd,*_=baseline.boundary(x,y,p);sx=atlas['sx'][top*4:bot*4].astype(np.float32);sy=atlas['sy'][top*4:bot*4].astype(np.float32);sample=bilinear(blur,sx,sy)
        if p.get('blur_transition'):
            u=np.clip(-sd/p['blur_transition'],0,1);w=u**3*(u*(6*u-15)+10);clear=bilinear(source,sx,sy);sample=clear+(sample-clear)*w[...,None]
        shaded=shade(sample,baseline.lighting(x,y,p),np.asarray(p['material']));inside=sd<=0;sh=(bot-top,4,W,4);weight=inside.reshape(sh).sum((1,3));C[top:bot]=(shaded*inside[...,None]).reshape((*sh,3)).sum((1,3))/np.maximum(weight,1)[...,None];alpha[top:bot]=weight/16
    if p.get('post_sigma'):
        sigma=p['post_sigma']*L;C=cv2.GaussianBlur(C*alpha[...,None],(0,0),sigma)/np.maximum(cv2.GaussianBlur(alpha,(0,0),sigma),1e-12)[...,None]
    return C,alpha
