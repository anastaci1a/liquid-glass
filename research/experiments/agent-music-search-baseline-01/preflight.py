from common import *
assert json.loads((P/'geometry-checkpoint.json').read_text())['status']=='PASS_GEOMETRY_AND_CANONICAL_INPUTS'
assert all(r['semantic_equal'] and not r['type_differences'] for r in json.loads((P/'case-audit.json').read_text())['rows'])
assert not (P/'native-reservation.json').exists(),'No duplicate native grid'
gate();s=study('a');other=study('b');assert s.crop==other.crop and s.L==other.L and s.case['center']==other.case['center'] and s.case['half']==other.case['half'];f=RadiusBack();center=np.asarray(par['center']);x0,y0,x1,y1=s.crop;H,W=y1-y0,x1-x0;N=4*H*W
reserve=12*N;assert ledger['graph']+reserve+14*(3000-ledger['fixture_rays'])<6000000
save('native-reservation.json',dict(utc=utc(),native_rays_reserved=N,total_native_cap=451200,nested_graph_reserved=reserve,prior_graph=ledger['graph'],graph_cap=6000000,geometry_reuse='Identical original L, accepted pose/R, source plane, index, crop, AA phase and physical height for A/B',count_rule='Conservative 8 nested height charges plus4 boundary charges per trace point; all delegates covered.'))
yy,xx=np.mgrid[y0:y1:.5,x0:x1:.5];xx-=.25;yy-=.25;x=(xx-center[0])/89;y=(yy-center[1])/89;q=trace(f,x,y,native=True)
entry=np.where(q['inside'][...,None],np.stack([x,y,np.zeros_like(x)],-1),np.nan);X=q['X']*89+center[0];Y=q['Y']*89+center[1]
np.savez_compressed(P/'native-paths.npz',source_X=X,source_Y=Y,x=x,y=y,entry=entry,entry_outward_normal=np.array([0.,0.,1.]),internal_direction=np.array([0.,0.,-1.]),**q)
if not q['complete'].all():
 save('source-preflight.json',dict(status='STOP_INCOMPLETE_PRIMARY_PATH',incomplete=int((~q['complete']).sum()),ledger=ledger));raise RuntimeError('Incomplete path; no RGB')
alpha=q['inside'].reshape(H,2,W,2).mean((1,3));rows=[]
for k in ['a','b']:
 gate();m=np.load(P/f'{k}-masks.npz');known=cv2.imread(str(WORK/k/'known.png'),0)>0;ledger['known_mask_erosions']+=1
 safe=cv2.erode(known.astype(np.uint8),np.ones((43,43),np.uint8),borderType=cv2.BORDER_CONSTANT,borderValue=0)>0
 required=q['inside']|np.repeat(np.repeat(m['required'],2,0),2,1);finite=np.isfinite(X)&np.isfinite(Y);a=np.floor(np.where(finite,X,-2)).astype(int);b=np.floor(np.where(finite,Y,-2)).astype(int);bounds=finite&(a>=0)&(b>=0)&(a+1<known.shape[1])&(b+1<known.shape[0]);i,j=np.nonzero(bounds);base=np.zeros_like(bounds);blur=np.zeros_like(bounds)
 ledger['source_audit_subrays']+=N;ledger['bilinear_mask_lookups']+=8*len(i);save('ledger.json',ledger)
 for out,mask in [(base,known),(blur,safe)]:out[i,j]=mask[b[i,j],a[i,j]]&mask[b[i,j]+1,a[i,j]]&mask[b[i,j],a[i,j]+1]&mask[b[i,j]+1,a[i,j]+1]
 support=np.where(q['inside'],blur,base);bad=required&~support
 np.savez_compressed(P/f'{k}-support.npz',support=support,required_pixels=m['required'],required_subrays=required,coverage=alpha,known=known,incident_known=safe)
 scored=np.repeat(np.repeat(m['glass'],2,0),2,1)
 row=dict(case=k,whole_body_subrays=int(q['inside'].sum()),required_subrays=int(required.sum()),scored_subrays=int(scored.sum()),scored_outside_predicted_outline=int((scored&~q['inside']).sum()),partial_original_glass_pixels=int((m['glass']&(alpha<1)).sum()),unsupported_required=int(bad.sum()),unsupported_whole=int((q['inside']&~support).sum()),unsupported_original_scored=int((scored&~support).sum()),unavailable_unscored=int((~support&~required).sum()),source_mask_cells=int(known.size),eroded_mask_cells=int(safe.size),finite_kernel=[43,43],kernel_radius=21,bilinear_corner_lookups=8*len(i),source_bounds=[float(X.min()),float(Y.min()),float(X.max()),float(Y.max())],first_unsupported_subray_indices=np.argwhere(bad)[:12].tolist())
 rows.append(row);save('source-preflight-partial.json',dict(records=rows,ledger=ledger.copy()))
 if bad.any():
  save('source-preflight.json',dict(status='STOP_UNSUPPORTED_REQUIRED_SOURCE',records=rows,ledger=ledger.copy(),utc=utc(),RGB_queries=0,images=0));raise RuntimeError('Unsupported whole/required source; no RGB, no repair')
 gate()
save('source-preflight.json',dict(status='PASS_BOTH_BEFORE_RGB',utc=utc(),records=rows,ledger=ledger.copy(),confidence='Conditional temporal mosaic; no new observed mask or hidden photography claim',RGB_queries=0,images=0))
print('SOURCE_FIRST_PASS',rows,ledger,flush=True)
