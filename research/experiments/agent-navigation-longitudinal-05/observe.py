"""One predeclared sign pair, certified coordinates and original composition."""
from driver import *
from PIL import Image,ImageDraw
label=sys.argv[1];assert label in ['plus','minus'];e=.1 if label=='plus' else -.1;folder=P/label;proof=json.loads((folder/'source-proof.json').read_text());assert proof['status']=='PASS';assert not (folder/'observation-started.json').exists();gate();pin()
(folder/'observation-started.json').write_text(json.dumps(dict(utc=utc(),strength=e))+'\n')
q=np.load(folder/'paths.npz');q0=np.load(Q/'native-paths.npz');inside=q['inside'];X=q['source_X'];Y=q['source_Y'];assert np.array_equal(inside,q0['inside']);assert np.array_equal(X[~inside],q0['source_X'][~inside]) and np.array_equal(Y[~inside],q0['source_Y'][~inside]);rows=[];parity=[];luma=np.array([.2126,.7152,.0722]);crop_bounds={'left-cap':[320,535,650,765],'upper-body':[650,530,1270,595],'lower-body':[650,690,1270,765]}
def output(n,j):(folder/n).write_text(json.dumps(j,indent=2,allow_nan=False)+'\n')
def reserve_RGB(n):
 assert ledger['RGB_queries']+n<=limits['RGB_queries'];ledger['RGB_queries']+=int(n);save('ledger.json',ledger)
def sample(source,X,Y):
 a=np.floor(X).astype(int);b=np.floor(Y).astype(int);fx=(X-a)[:,None];fy=(Y-b)[:,None]
 return (source[b,a]*(1-fx)+source[b,a+1]*fx)*(1-fy)+(source[b+1,a]*(1-fx)+source[b+1,a+1]*fx)*fy
def metric(s,M,C,ext):
 z=s.scores(M);z['E']=float(np.sqrt(z['loss']));z['foreground_mse']={};x0,y0,_,_=s.crop
 for layer in s.case['foreground_layers']:
  if layer.get('fit_style',True) and layer['mode']!='transmission':
   a,b,c,d=layer['box'];z['foreground_mse'][layer.get('style_key',layer['vector_asset'])]=float(np.mean((C[b-y0:d-y0,a-x0:c-x0]-s.target[b:d,a:c])**2))*255**2
 z['exterior']={'pixels':int(ext.sum()),'rmse':float(np.sqrt(np.mean((C[ext]-s.target_crop[ext])**2))*255)};return z
def guards(z,b):
 g={n:z[n]['rmse']<=b[n]['rmse'] for n in ['glass','rim','held','interior','exterior']};g.update(E=z['E']<=b['E'],ssim=z['ssim']>=b['ssim']);g.update({n:z['foreground_mse'][n]<=v for n,v in b['foreground_mse'].items()});return g
integrity=json.loads((Q/'input-integrity.json').read_text())
for case in integrity['cases']:
 key=case['case'];assert hashlib.sha256((WORK/key/'case.json').read_bytes()).hexdigest()==case['case_sha256']
 for record in case['input_hashes']+case['vector_hashes']:assert hashlib.sha256((WORK/key/record['file']).read_bytes()).hexdigest()==record['sha256']
for record in integrity['mask_archives']:assert hashlib.sha256((CACHE/f"{record['case']}-masks.npz").read_bytes()).hexdigest()==record['sha256']
output('unchanged-inputs.json',dict(status='PASS',cached_contract_reused=True,all_case_source_target_known_vectors_masks_exact=True,shared_code_exact=True))
for key in ['a','b']:
 gate();s=Study(WORK/key);f=setup(e);old=np.load(CACHE/f'{key}-source-blur.npz');zero=np.load(Q/f'{key}-candidate.npz');m=np.load(CACHE/f'{key}-masks.npz');sp=np.load(folder/f'{key}-support.npz');support=sp['support'];required=sp['required_pixels'];H,W=s.valid.shape;x0,y0,_,_=s.crop;known=cv2.imread(str(WORK/key/'known.png'),0)>0
 field=P/f'{key}-incident.npz'
 if not field.exists():
  assert ledger['incident_filters']<2;ledger['incident_filters']+=1;ledger['known_mask_erosions']+=1;save('ledger.json',ledger);filtered,safe,radius=incident_source_filter(s.source,known,6.75);assert radius==21;np.testing.assert_array_equal(safe,np.load(P/f'{key}-audit-mask.npz')['safe']);np.savez_compressed(field,filtered=filtered,safe=safe);save(f'{key}-field-record.json',dict(utc=utc(),one_filter=True,sigma=6.75,radius=21,source_sha256=hashlib.sha256((WORK/key/'source.png').read_bytes()).hexdigest(),filtered_array_sha256=hashlib.sha256(filtered.tobytes()).hexdigest(),finite_mask_sha256=hashlib.sha256(safe.tobytes()).hexdigest(),output_file_sha256=hashlib.sha256(field.read_bytes()).hexdigest()))
 else:
  fieldcache=np.load(field);filtered,safe=fieldcache['filtered'],fieldcache['safe'];fr=json.loads((P/f'{key}-field-record.json').read_text());assert hashlib.sha256(field.read_bytes()).hexdigest()==fr['output_file_sha256'];assert hashlib.sha256(filtered.tobytes()).hexdigest()==fr['filtered_array_sha256']
 before=np.full(inside.shape+(3,),np.nan,float);before[~inside]=zero['sample_RGB'][~inside];assert np.array_equal(support[~inside],zero['support'][~inside]);ii,jj=np.nonzero(inside&support)
 for start in range(0,len(ii),100000):
  gate();i=ii[start:start+100000];j=jj[start:start+100000];reserve_RGB(len(i));before[i,j]=sample(filtered,X[i,j],Y[i,j])
 cov=sp['coverage'];conditions={'lens':(cov==1)&m['glass'],'straight-miss':(cov==0)&m['exterior'],'partial-coverage':(cov>0)&(cov<1)&required}
 for name,mask in conditions.items():
  locations=np.argwhere(mask);rr,cc=locations[len(locations)//2];top=int(np.clip(rr-1,0,H-2));left=int(np.clip(cc-1,0,W-2));h=w=2;sub=(slice(top*2,(top+h)*2),slice(left*2,(left+w)*2));pc=dict(s.case);pc['center']=bounds['center'];pc['crop']=[x0+left,y0+top,x0+left+w,y0+top+h];n=4*h*w;assert ledger['fixture_rays']+n<=limits['fixture_rays'] and ledger['graph']+8*n<=limits['graph'];ledger['fixture_rays']+=n;reserve_RGB(int(support[sub].sum())+int((support[sub]&inside[sub]).sum()))
  image,_,sup,layers=render_rows(s.source,pc,{},f,1.5,2.1,0,h,raw_transmission=True,exact_bilinear=True,samples_per_axis=2,source_known=known,required_pixels=required[top:top+h,left:left+w],return_support=True,return_layers=True,return_samples=True,incident_source=filtered,incident_known=safe)
  expected=before[sub].reshape(h,2,w,2,3).mean((1,3)).astype(np.float32);status=dict(case=key,cohort=name,patch=[left,top,left+w,top+h],native_exact=bool(np.array_equal(image,expected,equal_nan=True)),sample_exact=bool(np.array_equal(layers['sample_rgb'],before[sub],equal_nan=True)),coordinates_exact=bool(np.array_equal(layers['source_X'],X[sub]) and np.array_equal(layers['source_Y'],Y[sub])),membership_exact=bool(np.array_equal(layers['sample_inside'],inside[sub])),support_exact=bool(np.array_equal(sup,support[sub].reshape(h,2,w,2).all((1,3)))));parity.append(status);output('parity.json',dict(records=parity,ledger=ledger.copy()));assert all(status[n] for n in ['native_exact','sample_exact','coordinates_exact','membership_exact','support_exact']),'Parity failure stops family'
 pre=before.reshape(H,2,W,2,3).mean((1,3)).astype(np.float32);lens=np.where(inside[...,None],before,0).reshape(H,2,W,2,3).mean((1,3));clear=np.where((~inside)[...,None],before,0).reshape(H,2,W,2,3).mean((1,3));assert np.array_equal(clear,zero['clear_premultiplied'],equal_nan=True);M=np.divide(lens,cov[...,None],out=np.zeros_like(lens),where=cov[...,None]>0).astype(np.float32)
 gate();assert ledger['candidate_composites']<limits['candidate_composites'];ledger['candidate_composites']+=1;save('ledger.json',ledger);C=s.apply_foreground(pre.copy());assert np.isfinite(C[required]).all();base=metric(s,old['material'],old['complete'],m['exterior']);zbase=metric(s,zero['material'],zero['complete'],m['exterior']);prior=next(v for v in json.loads((Q/'result.json').read_text())['records'] if v['case']==key);assert base==prior['baseline_scores'] and zbase==prior['scores'];score=metric(s,M,C,m['exterior']);completed=metric(s,C,C,m['exterior']);cb=metric(s,old['complete'],old['complete'],m['exterior']);cz=metric(s,zero['complete'],zero['complete'],m['exterior']);partial=m['glass']&(cov<1);partial_errors={name:float(np.sqrt(np.mean(((ar-s.target_crop)[partial]*255)**2))) for name,ar in [('H1',old['complete']),('spline_zero',zero['complete']),('candidate',C)]};cropmetrics={}
 for name,(a,b,c,d) in crop_bounds.items():
  a-=x0;c-=x0;b-=y0;d-=y0;target=s.target_crop[b:d,a:c].astype(float);values={}
  for text,ar in [('H1',old['complete']),('spline_zero',zero['complete']),('candidate',C)]:
   err=(ar[b:d,a:c].astype(float)-target)*255;dy=err@luma;dc=err-dy[...,None];values[text]=dict(RGB_RMSE=float(np.sqrt(np.mean(err*err))),luma_RMSE=float(np.sqrt(np.mean(dy*dy))),chroma_RMSE=float(np.sqrt(np.mean(dc*dc))),signed_RGB=err.mean((0,1)).tolist())
  cropmetrics[name]=dict(original_frame_bounds=crop_bounds[name],native_crop_bounds=[a,b,c,d],values=values)
 np.savez_compressed(folder/f'{key}-candidate.npz',sample_RGB=before,inside=inside,support=support,lens_premultiplied=lens,clear_premultiplied=clear,coverage=cov,material=M,pre_foreground=pre,complete=C)
 panel=Image.new('RGB',(4*W+6,H+64),'white');draw=ImageDraw.Draw(panel)
 for col,(text,ar) in enumerate([('Apple',s.target_crop),('Current incident H1 D2',old['complete']),('Spline zero D2.1',zero['complete']),(f'Longitudinal {e:+.1f}',C)]):
  ok=np.isfinite(ar).all(2);yy,xx=np.indices(ok.shape);view=np.where(ok[...,None],ar,np.where(((xx//6+yy//6)%2)[...,None],.72,.9));panel.paste(Image.fromarray(np.uint8(np.rint(np.clip(view,0,1)*255))),(col*(W+2),64));draw.text((col*(W+2)+8,20),text,fill='black')
 panel.save(folder/f'{key}-comparison.png');row=dict(case=key,strength=e,scores=score,H1_scores=base,zero_scores=zbase,H1_guards=guards(score,base),zero_guards=guards(score,zbase),completed_scores=completed,completed_H1_scores=cb,completed_zero_scores=cz,completed_H1_guards=guards(completed,cb),completed_zero_guards=guards(completed,cz),partial_boundary_pixels=int(partial.sum()),partial_errors=partial_errors,fixed_crops=cropmetrics,raw_clips_below=int((before[support]<0).sum()),raw_clips_above=int((before[support]>1).sum()),clear_exact=True,ledger=ledger.copy());rows.append(row);output(f'{key}-result.json',row);print(label,key,score['E'],row['H1_guards'],flush=True);gate()
output('result.json',dict(status='PENDING_VISUAL_AND_PRIMARY_REVIEW' if all(all(r['H1_guards'].values()) and all(r['completed_H1_guards'].values()) for r in rows) else 'NO_PAIRED_QUALIFIER',records=rows,ledger=ledger.copy(),finished_utc=utc()));print(label,'PAIR COMPLETE',utc(),ledger,flush=True)
