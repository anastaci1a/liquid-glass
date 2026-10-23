"""One fixed paired observation, only cached coordinates and original compositor."""
from geometry import *
import hashlib
from PIL import Image,ImageDraw
from geometric_render import render_rows,incident_source_filter
assert (P/'sampler-authority.json').exists() and json.loads((P/'source-preflight.json').read_text())['status']=='PASS'
assert not (P/'observation-started.json').exists(),'Do not repeat pair'
save('observation-started.json',{'utc':utc(),'fixed_index':1.5,'fixed_D':2.1})
q=np.load(P/'native-paths.npz');X=q['source_X'];Y=q['source_Y'];inside=q['inside'];rows=[];parity=[];proof=json.loads((P/'source-preflight.json').read_text());luma=np.array([.2126,.7152,.0722]);crop_bounds={'left-cap':[320,535,650,765],'upper-body':[650,530,1270,595],'lower-body':[650,690,1270,765]}
def sample(source,X,Y):
 a=np.floor(X).astype(int);b=np.floor(Y).astype(int);fx=(X-a)[:,None];fy=(Y-b)[:,None]
 return (source[b,a]*(1-fx)+source[b,a+1]*fx)*(1-fy)+(source[b+1,a]*(1-fx)+source[b+1,a+1]*fx)*fy
def reserve_RGB(n):
 assert ledger['RGB_queries']+n<=3000000;ledger['RGB_queries']+=int(n);save('ledger.json',ledger)
def metric(s,M,C,ext):
 z=s.scores(M);z['E']=float(np.sqrt(z['loss']));z['foreground_mse']={};x0,y0,_,_=s.crop
 for layer in s.case['foreground_layers']:
  if layer.get('fit_style',True) and layer['mode']!='transmission':
   a,b,c,d=layer['box'];z['foreground_mse'][layer.get('style_key',layer['vector_asset'])]=float(np.mean((C[b-y0:d-y0,a-x0:c-x0]-s.target[b:d,a:c])**2))*255**2
 z['exterior']={'pixels':int(ext.sum()),'rmse':float(np.sqrt(np.mean((C[ext]-s.target_crop[ext])**2))*255)};return z
def guards(z,b):
 g={n:z[n]['rmse']<=b[n]['rmse'] for n in ['glass','rim','held','interior','exterior']};g.update(E=z['E']<=b['E'],ssim=z['ssim']>=b['ssim']);g.update({n:z['foreground_mse'][n]<=v for n,v in b['foreground_mse'].items()});return g
for key in ['a','b']:
 gate();s,f,center=setup(key);old=np.load(CACHE/f'{key}-source-blur.npz');raw=np.load(CACHE/f'{key}-raw.npz');m=np.load(CACHE/f'{key}-masks.npz');sp=np.load(P/f'{key}-support.npz');support=sp['support'];required=sp['required_pixels'];H,W=s.valid.shape;x0,y0,_,_=s.crop
 rec=next(r for r in proof['rows'] if r['case']==key)
 for name,digest in rec['input_hashes'].items():assert hashlib.sha256((WORK/key/name).read_bytes()).hexdigest()==digest
 known=cv2.imread(str(WORK/key/'known.png'),0)>0;filtered,filtered_known,radius=incident_source_filter(s.source,known,6.75);assert radius==21
 before=np.full(inside.shape+(3,),np.nan,float)
 for mask,source in [(inside,filtered),(~inside,s.source)]:
  ii,jj=np.nonzero(mask&support)
  for start in range(0,len(ii),100000):
   gate();i=ii[start:start+100000];j=jj[start:start+100000];reserve_RGB(len(i));before[i,j]=sample(source,X[i,j],Y[i,j])
 # All sampling uses retained certified coordinates. Shared-renderer parity is
 # separately charged, including its preliminary unfiltered lens samples.
 cov=sp['coverage'];conditions={'lens':(cov==1)&m['glass'],'straight-miss':(cov==0)&m['exterior'],'partial-coverage':(cov>0)&(cov<1)&required}
 for name,mask in conditions.items():
  locations=np.argwhere(mask);assert len(locations);rr,cc=locations[len(locations)//2];top=int(np.clip(rr-1,0,H-2));left=int(np.clip(cc-1,0,W-2));h=w=2;sub=(slice(top*2,(top+h)*2),slice(left*2,(left+w)*2));pc=dict(s.case);pc['center']=center.tolist();pc['crop']=[x0+left,y0+top,x0+left+w,y0+top+h];n=4*h*w;assert ledger['fixture_rays']+n<=5000 and ledger['graph']+6*n<=12000000;ledger['fixture_rays']+=n;reserve_RGB(int(support[sub].sum())+int((support[sub]&inside[sub]).sum()))
  image,bounds,sup,layers=render_rows(s.source,pc,{},f,1.5,2.1,0,h,raw_transmission=True,exact_bilinear=True,samples_per_axis=2,source_known=known,required_pixels=required[top:top+h,left:left+w],return_support=True,return_layers=True,return_samples=True,incident_source=filtered,incident_known=filtered_known)
  expected=before[sub].reshape(h,2,w,2,3).mean((1,3)).astype(np.float32);same=np.array_equal(image,expected,equal_nan=True);samples_same=np.array_equal(layers['sample_rgb'],before[sub],equal_nan=True);coords_same=np.array_equal(layers['source_X'],X[sub]) and np.array_equal(layers['source_Y'],Y[sub]);status={'case':key,'cohort':name,'patch_native':[left,top,left+w,top+h],'complete_exact':same,'samples_exact':samples_same,'coords_exact':coords_same,'inside_exact':bool(np.array_equal(layers['sample_inside'],inside[sub])),'support_exact':bool(np.array_equal(sup,support[sub].reshape(h,2,w,2).all((1,3))))};parity.append(status);save('parity.json',{'records':parity,'ledger':ledger.copy()});assert all(status[n] for n in ['complete_exact','samples_exact','coords_exact','inside_exact','support_exact']),'Parity failure: stop without repair'
 pre=before.reshape(H,2,W,2,3).mean((1,3)).astype(np.float32);lens=np.where(inside[...,None],before,0).reshape(H,2,W,2,3).mean((1,3));clear=np.where((~inside)[...,None],before,0).reshape(H,2,W,2,3).mean((1,3));M=np.divide(lens,cov[...,None],out=np.zeros_like(lens),where=cov[...,None]>0).astype(np.float32)
 gate();assert ledger['candidate_composites']<2;ledger['candidate_composites']+=1;save('ledger.json',ledger);C=s.apply_foreground(pre.copy());assert np.isfinite(C[required]).all();baseline=metric(s,old['material'],old['complete'],m['exterior']);record=next(r['scores'] for r in json.loads((CACHE/'blur-result.json').read_text())['references'] if r['reference']==key);assert baseline==record,'Original baseline score mismatch, no repair';score=metric(s,M,C,m['exterior']);g=guards(score,baseline)
 completed=metric(s,C,C,m['exterior']);old_completed=metric(s,old['complete'],old['complete'],m['exterior']);cg=guards(completed,old_completed);partial=m['glass']&(cov<1);partial_errors={name:float(np.sqrt(np.mean(((array-s.target_crop)[partial]*255)**2))) for name,array in [('baseline',old['complete']),('candidate',C)]};crop_metrics={}
 for name,(a,b,c,d) in crop_bounds.items():
  a-=x0;c-=x0;b-=y0;d-=y0;target=s.target_crop[b:d,a:c].astype(float);values={}
  for label,array in [('baseline',old['complete']),('candidate',C)]:
   error=(array[b:d,a:c].astype(float)-target)*255;dy=error@luma;dc=error-dy[...,None];values[label]={'RGB_RMSE':float(np.sqrt(np.mean(error*error))),'luma_RMSE':float(np.sqrt(np.mean(dy*dy))),'chroma_RMSE':float(np.sqrt(np.mean(dc*dc))),'signed_RGB':error.mean((0,1)).tolist()}
  crop_metrics[name]={'original_frame_bounds':crop_bounds[name],'native_crop_bounds':[a,b,c,d],'values':values}
 np.savez_compressed(P/f'{key}-candidate.npz',sample_RGB=before,inside=inside,support=support,lens_premultiplied=lens,clear_premultiplied=clear,coverage=cov,material=M,pre_foreground=pre,complete=C)
 panel=Image.new('RGB',(3*W+4,H+64),'white');draw=ImageDraw.Draw(panel)
 for col,(label,array) in enumerate([('Apple',s.target_crop),('Current incident baseline',old['complete']),('Fixed spline D2.1; unit body',C)]):
  defined=np.isfinite(array).all(2);yy,xx=np.indices(defined.shape);view=np.where(defined[...,None],array,np.where(((xx//6+yy//6)%2)[...,None],.72,.9));panel.paste(Image.fromarray(np.uint8(np.rint(np.clip(view,0,1)*255))),(col*(W+2),64));draw.text((col*(W+2)+8,20),label,fill='black')
 panel.save(P/f'{key}-comparison.png');row={'case':key,'scores':score,'baseline_scores':baseline,'original_guards':g,'completed_image_scores':completed,'completed_baseline_scores':old_completed,'completed_guards':cg,'partial_boundary_pixels':int(partial.sum()),'partial_boundary_errors':partial_errors,'fixed_crops':crop_metrics,'raw_clips_below':int((before[support]<0).sum()),'raw_clips_above':int((before[support]>1).sum()),'source_queries_cumulative':ledger['RGB_queries'],'actual_full_candidate_composites':ledger['candidate_composites']};rows.append(row);save(f'{key}-result.json',row);print(key,score['E'],g,cg,flush=True)
 gate()
save('result.json',{'status':'STRICT_NUMERICAL_CANDIDATE_PENDING_VISUAL' if all(all(x['original_guards'].values()) and all(x['completed_guards'].values()) for x in rows) else 'NO_PAIRED_QUALIFIER','records':rows,'ledger':ledger.copy(),'finished_utc':utc(),'source_limit':'Conditional temporal mosaic; no new hidden source truth','geometry':'One fixed actual spline, index1.5 D2.1, unit neutral body and original incident sigma6.75. No fitting or fallback.'});print('Pair complete',utc(),ledger,flush=True)
