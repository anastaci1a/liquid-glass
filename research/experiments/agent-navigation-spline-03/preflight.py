"""One identical paired geometry grid; both full source proofs before RGB."""
from geometry import *
assert json.loads((P/'geometry-checkpoint.json').read_text())['status']=='PASS_GEOMETRY_ONLY'
assert not (P/'native-reservation.json').exists(),'No repeated native grid'
gate();s,f,center=setup('a');sb,fb,cb=setup('b');assert s.crop==sb.crop and s.L==sb.L and np.array_equal(center,cb) and f.half==fb.half and f.radius==fb.radius and np.array_equal(f.height_controls,fb.height_controls)
x0,y0,x1,y1=s.crop;H,W=y1-y0,x1-x0;N=4*H*W;reservation=6*N;assert ledger['graph']+reservation+6*(5000-ledger['fixture_rays'])<12000000
save('native-reservation.json',{'utc':utc(),'one_reused_grid_rays':N,'native_graph_reserved':reservation,'prior_graph':ledger['graph'],'total_limit':12000000,'pair_geometry_identical':True,'bounds':{'half':list(f.half),'radius':f.radius,'center':center.tolist(),'L':s.L},'remaining_fixture_graph_allowance':6*(5000-ledger['fixture_rays'])})
yy,xx=np.mgrid[y0:y1:.5,x0:x1:.5];xx-=.25;yy-=.25;x=(xx-center[0])/s.L;y=(yy-center[1])/s.L
q=trace(f,x,y,native=True);save('ledger.json',ledger);gate();X=q['X']*s.L+center[0];Y=q['Y']*s.L+center[1];entry=np.stack([x,y,np.zeros_like(x)],-1);entry=np.where(q['inside'][...,None],entry,np.nan)
np.savez_compressed(P/'native-paths.npz',source_X=X,source_Y=Y,x=x,y=y,entry=entry,entry_outward_normal=np.array([0.,0.,1.]),**q)
assert q['complete'].all(),'Incomplete primary path; stop'
coverage=q['inside'].reshape(H,2,W,2).mean((1,3));rows=[]
for key in ['a','b']:
 gate();case=Study(WORK/key);m=np.load(CACHE/f'{key}-masks.npz');raw=np.load(CACHE/f'{key}-raw.npz');np.testing.assert_array_equal(coverage,raw['coverage']);np.testing.assert_array_equal(m['glass'],case.valid);np.testing.assert_array_equal(m['rim'],case.rim);np.testing.assert_array_equal(m['held'],case.held)
 oldreq=m['required'];req=oldreq.copy();req|=m['glass']|m['rim']|m['held']|m['exterior'];deps=np.load(P/f'{key}-zero-control.npz')['style_dependencies'];req|=deps
 required=q['inside']|np.repeat(np.repeat(req,2,0),2,1);known=cv2.imread(str(WORK/key/'known.png'),0)>0;safe=cv2.erode(known.astype(np.uint8),np.ones((43,43),np.uint8),borderType=cv2.BORDER_CONSTANT,borderValue=0)>0
 assert np.isfinite(X).all() and np.isfinite(Y).all();a=np.floor(X).astype(int);b=np.floor(Y).astype(int);bounds=(a>=0)&(b>=0)&(a+1<known.shape[1])&(b+1<known.shape[0]);i,j=np.nonzero(bounds);base=np.zeros(bounds.shape,bool);lens=np.zeros_like(base)
 ledger['source_audit_subrays']+=int(N);ledger['bilinear_mask_lookups']+=8*len(i);save('ledger.json',ledger)
 for out,mask in [(base,known),(lens,safe)]:out[i,j]=mask[b[i,j],a[i,j]]&mask[b[i,j]+1,a[i,j]]&mask[b[i,j],a[i,j]+1]&mask[b[i,j]+1,a[i,j]+1]
 support=np.where(q['inside'],lens,base);unsupported=required&~support;np.savez_compressed(P/f'{key}-support.npz',support=support,required_pixels=req,required_subrays=required,coverage=coverage,original_glass=m['glass'],original_exterior=m['exterior']);row={'case':key,'whole_body_rays':int(q['inside'].sum()),'required_subrays':int(required.sum()),'all_audited_subrays':N,'unsupported_required':int(unsupported.sum()),'unknown_unscored':int((~support&~required).sum()),'source_radius':21,'finite_kernel_shape':[43,43],'bilinear_texels_per_field':4,'actual_mask_lookups':8*len(i),'support_certification':'43 by 43 known-mask erosion followed by all four bilinear corner lookups; clear rays use original known mask. Erosion is source-domain work, not zero effort.','coverage_exact':True,'original_masks_exact':True,'input_hashes':{name:__import__('hashlib').sha256((WORK/key/name).read_bytes()).hexdigest() for name in ['case.json','source.png','target.png','known.png']}};rows.append(row);save('source-preflight-partial.json',rows)
 if unsupported.any():
  bad=np.argwhere(unsupported);row['first_bad_subrays']=bad[:16].tolist();save('source-preflight.json',{'status':'STOP_UNSUPPORTED_REQUIRED_SOURCE','rows':rows,'ledger':ledger,'finished_utc':utc()});raise RuntimeError('Required source unsupported; no RGB')
 gate()
save('source-preflight.json',{'status':'PASS','rows':rows,'ledger':ledger,'finished_utc':utc(),'new_RGB_queries':0,'new_images':0,'confidence':'Existing conditional temporal mosaics. No new observational truth or observed mask.'});print('Source-first PASS',ledger,flush=True)
