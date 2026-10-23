"""Necessary finite-gap clearance field; no arbitrary gap fitting, no images."""
import sys,json
from pathlib import Path
sys.path.insert(0,'/tmp')
import importlib.util
spec=importlib.util.spec_from_file_location('diag','/tmp/agent-toolbar-surface-diagnostic.py');d=importlib.util.module_from_spec(spec);spec.loader.exec_module(d)
import numpy as np
import cv2
out=d.out
def derivatives(fun,x,y,h):
    v=fun(x,y);dx=(fun(x+h,y)-fun(x-h,y))/(2*h);dy=(fun(x,y+h)-fun(x,y-h))/(2*h)
    c=dx[...,1]-dy[...,0];M=np.sum(v*v,axis=-1);K=v[...,1]*np.sum(v*dx,axis=-1)-v[...,0]*np.sum(v*dy,axis=-1)
    return v,c,M,K
def required_clearance(rho,M,n):
    A=rho-M;return np.sqrt((2*n*n*A+M+np.sqrt(M*M+4*n*n*A*rho))/(2*(n*n-1)))
def validate_known():
    x,y=np.meshgrid(np.linspace(-1.7,1.7,31),np.linspace(-.7,.7,23));n=1.5;G=2.5;h=.5+.01*x*x+.02*y*y
    def fun(x,y):return d.forward(.5+.01*x*x+.02*y*y,np.stack([.02*x,.04*y],axis=-1),G,n)[0]
    v,c,M,K=derivatives(fun,x,y,5e-5);good=np.abs(c)>1e-7;rho=K[good]/c[good];s=required_clearance(rho,M[good],n);err=float(np.max(np.abs(s-(G-h)[good])));assert np.all(rho>M[good]) and err<1e-5
    q,valid,*_=d.inverse(v,G-h,n);assert np.all(valid)
    report={'known_surface_points':int(good.sum()),'known_surface_clearance_max_error_L':err,'transmitted_branch_recovered':True,'nearzero_c_not_inverted':int((~good).sum()),'new_test_only':'Closed-form clearance inversion; earlier Snell/path equation checks reused, not repeated'}
    (out/'clearance-inversion-check.json').write_text(json.dumps(report,indent=2)+'\n');print('NEW_INVERSION_CHECK',report,flush=True)
def run(spacing):
    xs=np.arange(-int(np.floor(d.half[0]/spacing)),int(np.floor(d.half[0]/spacing))+1)*spacing;ys=np.arange(-int(np.floor(d.half[1]/spacing)),int(np.floor(d.half[1]/spacing))+1)*spacing;y,x=np.meshgrid(ys,xs,indexing='ij');inside=d.empirical.boundary(x,y,d.p)[0]<=0
    v,c1,M,K1=derivatives(d.accepted_v,x,y,1e-4);_,c,M,K=derivatives(d.accepted_v,x,y,5e-5);cerr=np.abs(c-c1);kerr=np.abs(K-K1);minimum=1e-5;robust=inside&(np.abs(c)>np.maximum(10*cerr,minimum));rho=np.divide(K,c,out=np.full_like(K,np.nan),where=np.abs(c)>1e-14)
    sign_margin=c*(K-M*c);noise=20*(np.abs(c)*kerr+np.abs(K-M*c)*cerr+M*np.abs(c)*cerr);viol=robust&(sign_margin < -noise);possible=robust&(sign_margin>noise)
    rows=[];fields={}
    for n in [1.33,1.5,1.8]:
        s=np.full_like(c,np.nan);s[possible]=required_clearance(rho[possible],M[possible],n);q,valid,*_=d.inverse(v,s,n);valid&=possible;sy,sx=np.gradient(s,spacing,spacing,edge_order=2);stencil=cv2.erode(valid.astype(np.uint8),np.ones((3,3),np.uint8))>0;err=np.linalg.norm(np.stack([-sx,-sy],axis=-1)-q,axis=-1)
        rows.append({'n':n,'necessary_valid_clearance_points':int(valid.sum()),'required_clearance_L':d.stats(s[valid]),'required_clearance_PDE_stencil_points':int(stencil.sum()),'required_clearance_PDE_gradient_error':d.stats(err[stencil]),'limits':'Necessary clearance only, no gap/surface promotion. Nearzero curl and violation boundary omitted from derivative stencil, retained in full fields.'});fields[f's_required_{n}']=s
    sensitivity=[]
    for floor in [1e-5,1e-4,1e-3]:
        r=inside&(np.abs(c)>np.maximum(10*cerr,floor));bad=r&(sign_margin < -noise)
        sensitivity.append({'curl_floor':floor,'robust_points':int(r.sum()),'wrong_branch_compatibility_points':int(bad.sum()),'fraction_of_robust':float(bad.sum()/r.sum()) if r.sum() else None,'fraction_of_all_inside':float(bad.sum()/inside.sum())})
    report={'spacing_L':spacing,'inside_points':int(inside.sum()),'robust_nonzero_curl_points':int(robust.sum()),'robust_wrong_branch_compatibility_points':int(viol.sum()),'robust_possible_branch_points':int(possible.sum()),'nearzero_or_derivative_ambiguous_points':int((inside&~(viol|possible)).sum()),'direct_map_curl_fd_difference':d.stats((c-c1)[inside]),'direct_K_fd_difference':d.stats((K-K1)[inside]),'threshold_sensitivity':sensitivity,'IOR_dependence':rows,'optical_passes':0,'claim':'Necessary local condition for EXACT specified flat-front orthographic single-back surface. Does not bound all approximate surfaces or infer Apple geometry.'}
    label='compatibility-'+str(spacing);(out/(label+'.json')).write_text(json.dumps(report,indent=2)+'\n');np.savez_compressed(out/(label+'-fields.npz'),x=x,y=y,inside=inside,curl=c,K=K,M=M,rho=rho,robust=robust,violation=viol,possible=possible,**fields);print('COMPATIBILITY',json.dumps(report),flush=True)
if __name__=='__main__':
    validate_known();run(.04);run(.02)
