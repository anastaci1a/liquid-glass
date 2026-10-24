"""One unfitted shared-family transfer; source-first, no model-specific fit."""
from pathlib import Path
import datetime,json,hashlib,sys
import numpy as np,cv2
from PIL import Image,ImageDraw,ImageFont
ROOT=Path(__file__).resolve().parents[3];P=Path(__file__).resolve().parent
sys.path.insert(0,str(ROOT/'reconstruction'))
from extended_fit import Study
from geometric_optics import trace_flat_front_orthographic
from geometric_render import incident_source_filter,neutral_color_response,render_rows
from music_miniplayer_family import load_family,surface_for_member
cv2.setNumThreads(1)
p=json.loads((P/'protocol.json').read_text());end=datetime.datetime.fromisoformat(p['deadline'].replace('Z','+00:00'))
assert not (P/'started.json').exists(),'No second transfer attempt'
ledger={k:0 for k in p['caps']}
def save(name,v):(P/name).write_text(json.dumps(v,indent=2,allow_nan=False)+'\n')
def gate():assert datetime.datetime.now(datetime.timezone.utc)<end

def charge(k,n):
 assert ledger[k]+n<=p['caps'][k],k
 ledger[k]+=int(n);save('ledger.json',ledger)
def nrows(x,y):return np.broadcast_arrays(np.asarray(x),np.asarray(y))[0].size
class Query:
 def __init__(self,fn,name):self.fn,self.name=fn,name
 def __call__(self,*args):
  n=nrows(*args[:2]) if self.name=='footprint' else np.asarray(args[0]).size
  charge('geometry_query_units',n);return self.fn(*args)
def counted(surface):
 original_height=surface.height_gradient;original_boundary=surface.boundary_mask
 def height(x,y):charge('geometry_query_units',nrows(x,y));return original_height(x,y)
 def boundary(x,y):charge('geometry_query_units',nrows(x,y));return original_boundary(x,y)
 surface.height_gradient=height;surface.boundary_mask=boundary
 class Coordinate:
  def __init__(self,inner):self.inner=inner
  def footprint(self,x,y):charge('geometry_query_units',nrows(x,y));return self.inner.footprint(x,y)
 surface.coordinate=Coordinate(surface.coordinate);surface.profile=Query(surface.profile,'profile');surface.radial_derivative=Query(surface.radial_derivative,'derivative')
 return surface
family=load_family();g=family['material']['gain'];b=family['material']['bias'];L=family['length_unit_native_pixels'];sigma=family['material']['incident_sigma_native_pixels'];radius=family['material']['incident_kernel_radius'];aaf=family['sampling']['samples_per_axis'];assert aaf==2
save('started.json',dict(utc=datetime.datetime.now(datetime.timezone.utc).isoformat(),family_sha256=hashlib.sha256((ROOT/'reconstruction/families/music-mini-player.json').read_bytes()).hexdigest()))
# Bind geometry and material to the selected expanded record, without a new ray.
fit=json.loads((ROOT/family['provenance']['expanded_height_record']).read_text());assert family['geometry']['height_controls']==fit['best']['heights'] and family['geometry']['breaks']==fit['breaks']
scene=json.loads((ROOT/'reconstruction/studies/geometric-expanded-pipeline/summary.json').read_text())['geometry']
surface_exp=surface_for_member('expanded');assert surface_exp.half==tuple(scene['surface_half']) and surface_exp.radius==scene['surface_radius']
expanded=[]
for k in ['a','b']:
 gate();work=ROOT/'.evidence-working/expanded-geometry-02'/k;charge('reference_mask_constructor_pixels',1360*250);s=Study(work);assert s.L==L and not s.transmission_layers
 cache=np.load(ROOT/f'research/experiments/expanded-spline-observation-01/{k}-candidate.npz');inside=cache['sample_inside'] if 'sample_inside' in cache else np.load(ROOT/'research/experiments/expanded-spline-observation-01/native-paths.npz')['inside']
 raw=cache['sample_before_response'];values=raw.copy();values[inside]=neutral_color_response(raw[inside],gain=g,bias=b)
 H,W=s.valid.shape;pre=values.reshape(H,2,W,2,3).mean((1,3)).astype(np.float32);charge('expanded_identity_composites',1);C=s.apply_foreground(pre.copy());accepted=np.load(ROOT/f'research/experiments/expanded-contrast-guard-02/{k}-candidate.npz')
 assert np.array_equal(pre,accepted['pre_foreground'],equal_nan=True) and np.array_equal(C,accepted['complete'],equal_nan=True)
 expanded.append(dict(reference=k,pre_foreground_exact=True,complete_exact=True))
save('expanded-zero-controls.json',dict(status='EXACT',records=expanded,rays=0,source_queries=0))
# Frozen compact reference masks and measured translation/major length.
B=ROOT/'research/experiments/compact-geometry-01';WORK=ROOT/'.evidence-working/compact-geometry-01'
prior=json.loads((ROOT/'reconstruction/studies/music-mini-compact-vector/review-round/pass-03.json').read_text())['parameters'];data={};input_hashes={}
for k in ['a','b']:
 gate();charge('reference_mask_constructor_pixels',920*240);s=Study(WORK/k);assert s.L==L and not s.transmission_layers
 masks={name:v for name,v in np.load(B/f'{k}-masks.npz').items()};assert np.array_equal(s.valid,masks['glass']) and np.array_equal(s.rim,masks['rim']) and np.array_equal(s.held,masks['held'])
 known=cv2.imread(str(WORK/k/'known.png'),0)>0
 c=dict(s.case);c['center']=(np.asarray(c['center'])+L*np.array([prior['shape_dx'],prior['shape_dy']])).tolist()
 data[k]=dict(s=s,m=masks,known=known,case=c)
 input_hashes[k]={name:hashlib.sha256((WORK/k/name).read_bytes()).hexdigest() for name in ['case.json',*s.case['source_sha256']]}
assert data['a']['case']['center']==data['b']['case']['center'] and data['a']['s'].crop==data['b']['s'].crop
surface=counted(surface_for_member('compact'));c=data['a']['case'];x0,y0,x1,y1=c['crop'];H,W=y1-y0,x1-x0
assert family['geometry']['minor_half']==surface_exp.half[1] and surface.radius==surface_exp.radius
assert np.array_equal(surface.height_controls,surface_exp.height_controls) and np.array_equal(surface.breaks,surface_exp.breaks)
yy,xx=np.mgrid[y0:y1:.5,x0:x1:.5];x=(xx-.25-c['center'][0])/L;y=(yy-.25-c['center'][1])/L
charge('compact_native_grid_rays',x.size);gate();q=trace_flat_front_orthographic(surface,x,y,family['optics']['index'],family['optics']['background_distance'])
np.savez_compressed(P/'compact-paths.npz',**q)
assert q['complete'].all(),'Incomplete path: stop before RGB'
X=q['X']*L+c['center'][0];Y=q['Y']*L+c['center'][1];a=np.floor(X).astype(int);bb=np.floor(Y).astype(int);coverage=q['inside'].reshape(H,2,W,2).mean((1,3))
proof=[]
for k,d in data.items():
 gate();known=d['known'];charge('source_audit_subrays',x.size);charge('known_mask_erosions',1)
 safe=cv2.erode(known.astype(np.uint8),np.ones((43,43),np.uint8),borderType=cv2.BORDER_CONSTANT,borderValue=0)>0
 bounds=np.isfinite(X)&np.isfinite(Y)&(a>=0)&(bb>=0)&(a+1<known.shape[1])&(bb+1<known.shape[0]);ii,jj=np.nonzero(bounds)
 rawok=np.zeros_like(bounds);blur_ok=np.zeros_like(bounds)
 for out,mask in [(rawok,known),(blur_ok,safe)]:
  charge('bilinear_mask_lookups',4*len(ii));out[ii,jj]=mask[bb[ii,jj],a[ii,jj]]&mask[bb[ii,jj]+1,a[ii,jj]]&mask[bb[ii,jj],a[ii,jj]+1]&mask[bb[ii,jj]+1,a[ii,jj]+1]
 supported=np.where(q['inside'],blur_ok,rawok);required=q['inside']|np.repeat(np.repeat(d['m']['required'],2,0),2,1)
 bad=required&~supported;row=dict(reference=k,whole_subrays=int(q['inside'].sum()),required_subrays=int(required.sum()),scored_outside_outline=int((np.repeat(np.repeat(d['m']['glass'],2,0),2,1)&~q['inside']).sum()),unsupported_required=int(bad.sum()),unknown_unscored=int((~supported&~required).sum()),kernel_radius=radius,RGB_queries=0)
 proof.append(row);save('source-proof-FIRST.json',dict(status='IN_PROGRESS',references=proof,geometry_shared=True))
 assert not bad.any(),'Unsupported required finite footprint; no source repair or RGB'
 d.update(supported=supported,incident_known=safe)
save('source-proof-FIRST.json',dict(status='PASS_BOTH_BEFORE_RGB',references=proof,geometry_shared=True,confidence='Conditional original mosaics; no photographic recovery'))

def sample(field,mask):
 ii,jj=np.nonzero(mask);charge('source_RGB_queries',len(ii));aa=a[ii,jj];by=bb[ii,jj];fx=(X[ii,jj]-aa)[:,None];fy=(Y[ii,jj]-by)[:,None]
 return (field[by,aa]*(1-fx)+field[by,aa+1]*fx)*(1-fy)+(field[by+1,aa]*(1-fx)+field[by+1,aa+1]*fx)*fy

def scores(s,M,C,m):
 out={}
 for name,value in [('legacy_material',M),('completed_image',C)]:charge('score_calls',1);charge('SSIM_metric_Gaussian_calls',5);charge('SSIM_metric_mask_erosions',1);z=s.scores(value);z['E']=float(np.sqrt(z['loss']));out[name]=z
 err=(C-s.target_crop)*255;out['exterior']=dict(pixels=int(m['exterior'].sum()),rmse=float(np.sqrt(np.mean((C[m['exterior']]-s.target_crop[m['exterior']])**2)))*255)
 fg={}
 for layer in s.case['foreground_layers']:
  A,Bb,Cc,D=layer['box'];key=layer.get('style_key',layer.get('vector_asset',layer.get('artwork_asset')));tile=((C[Bb-y0:D-y0,A-x0:Cc-x0].astype(float)-s.target[Bb:D,A:Cc])*255);assert np.isfinite(tile).all();fg[key]=float(np.mean(tile**2))
 out['foreground_artwork_MSE']=fg;return out
rows=[];parity=[]
for k,d in data.items():
 gate();s=d['s'];charge('material_fields',1);charge('known_mask_erosions',1);field,inc_known,r=incident_source_filter(s.source,d['known'],sigma);assert r==radius and np.array_equal(inc_known,d['incident_known'])
 raw=np.full(X.shape+(3,),np.nan);inside=q['inside'];clear=(~inside)&d['supported'];raw[clear]=sample(s.source,clear);raw[inside]=sample(field,inside)
 graded,preclip=neutral_color_response(raw[inside],gain=g,bias=b,return_preclip=True);clips=[int((preclip<0).sum()),int((preclip>1).sum())];assert clips==[0,0]
 values=raw.copy();values[inside]=graded;pre=values.reshape(H,2,W,2,3).mean((1,3)).astype(np.float32);charge('compact_candidate_composites',1);C=s.apply_foreground(pre.copy())
 lens=np.where(inside[...,None],values,0).reshape(H,2,W,2,3).mean((1,3));material=np.divide(lens,coverage[...,None],out=np.zeros_like(lens),where=coverage[...,None]>0).astype(np.float32)
 now=scores(s,material,C,d['m']);old=next(r for r in json.loads((B/'selected.json').read_text())['material']['references'] if r['reference']==k)['scores']
 guards={}
 for scope in ['legacy_material','completed_image']:
  for name in ['glass','rim','held','interior']:guards[scope+':'+name]=now[scope][name]['rmse']<=old[scope][name]['rmse']
  guards[scope+':E']=now[scope]['E']<=old[scope]['E'];guards[scope+':SSIM']=now[scope]['ssim']>=old[scope]['ssim']
 guards['exterior']=now['exterior']['rmse']<=old['exterior']['rmse']
 guards.update({name:value<=old['foreground_artwork_MSE'][name] for name,value in now['foreground_artwork_MSE'].items()})
 partial=d['m']['glass']&(coverage<1);err=(C-s.target_crop)*255;partial_row=dict(pixels=int(partial.sum()),RMSE=float(np.sqrt(np.mean(err[partial]**2))) if partial.any() else None)
 # Two 4x4 patches per reference: central body and left cap, same shared renderer.
 for top,left in [(H//2-2,W//2-2),(H//2-2,26)]:
  patch=dict(d['case']);patch['crop']=[x0+left,y0+top,x0+left+4,y0+top+4]
  charge('parity_rays',64);inside_patch=int(inside[2*top:2*(top+4),2*left:2*(left+4)].sum());charge('source_RGB_queries',64+inside_patch);charge('source_audit_subrays',64);charge('bilinear_mask_lookups',4*(64+inside_patch))
  params={'material':[g]*3+[b]*3+[0.]*17}
  expected=render_rows(s.source,patch,params,surface,family['optics']['index'],family['optics']['background_distance'],0,4,exact_bilinear=True,samples_per_axis=2,source_known=d['known'],required_pixels=np.ones((4,4),bool),incident_source=field,incident_known=inc_known)[0]
  assert np.array_equal(expected,pre[top:top+4,left:left+4]),'Shared renderer parity failed'
  parity.append(dict(reference=k,top=top,left=left,pre_foreground_exact=True))
 np.savez_compressed(P/f'compact-{k}-candidate.npz',sample_before_response=raw,pre_foreground=pre,complete=C,coverage=coverage,material=material)
 valid=np.isfinite(C).all(2);iy,ix=np.indices(valid.shape);view=np.where(valid[...,None],C,np.where(((iy//6+ix//6)%2)[...,None],.72,.9))
 canvas=Image.new('RGB',(2*W+2,H+64),'white');draw=ImageDraw.Draw(canvas);font=ImageFont.load_default(size=18)
 for i,(v,label) in enumerate([(s.target_crop,'Apple reference'),(view,'Same expanded model; shorter length')]):canvas.paste(Image.fromarray(np.uint8(np.rint(np.clip(v,0,1)*255))),(i*(W+2),64));draw.text((i*(W+2)+10,20),label,font=font,fill='black')
 canvas.save(P/f'compact-{k}-comparison.png')
 row=dict(reference=k,scores=now,prior_separate_model_scores=old,guards=guards,all_guards_pass=all(guards.values()),partial_original_glass=partial_row,clipping=clips,shared_family_sha256=hashlib.sha256((ROOT/'reconstruction/families/music-mini-player.json').read_bytes()).hexdigest());rows.append(row);save(f'compact-{k}-metrics.json',row);gate()
assert ledger['source_RGB_queries']<=p['caps']['source_RGB_queries']
save('parity.json',dict(records=parity,all_exact=True));save('result.json',dict(status='UNFITTED_EXACT_FAMILY_TRANSFER_COMPLETE',finished=datetime.datetime.now(datetime.timezone.utc).isoformat(),expanded_zeros=expanded,compact_records=rows,ledger=ledger,source_proof='source-proof-FIRST.json',input_hashes=input_hashes,only_shape_difference='major_half',family_glass_identical=True,individual_compact_fit=False,claim='Required shared model transfer; numerical failures remain failures, not acceptance waivers.'))
print(json.dumps(dict(status='COMPLETE',E=[r['scores']['completed_image']['E'] for r in rows],guards=[r['all_guards_pass'] for r in rows],ledger=ledger)),flush=True)
