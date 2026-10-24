"""AA2 known-signal envelopes; no unknown source value is reconstructed."""
from pathlib import Path
import sys,json,datetime,hashlib
import numpy as np,cv2
from PIL import Image,ImageDraw,ImageFont
ROOT=Path(__file__).resolve().parents[3];OUT=Path(__file__).parent;CACHE=ROOT/'research/experiments/miniplayer-native-front-26'
sys.path.insert(0,str(ROOT/'reconstruction'))
from closed_crowned_surface import ClosedRoundedSurface
from geometric_optics import refract,next_convex_boundary
from environment_radiance import two_interface_power,annular_environment,decode_srgb,encode_srgb
from geometric_render import incident_source_filter,neutral_color_response
from extended_fit import Study
P=json.loads((OUT/'protocol.json').read_text());END=datetime.datetime.fromisoformat(P['deadline'].replace('Z','+00:00'));F=json.loads((ROOT/'reconstruction/families/music-mini-player.json').read_text());shape=json.loads((ROOT/'research/experiments/miniplayer-closed-perimeter-25/protocol.json').read_text())['parameters'];ledger={k:0 for k in P['caps']};cp=json.loads((OUT/'checkpoint.json').read_text());assert cp['status']=='PASS_TWO_INTERFACE_TENSOR_AND_COVARIANCE';ledger['synthetic_vectors']=cp['synthetic_vectors'];cv2.setNumThreads(1)
def save(n,v):(OUT/n).write_text(json.dumps(v,indent=2,allow_nan=False)+'\n')
def charge(k,n):
 assert datetime.datetime.now(datetime.timezone.utc)<END and ledger[k]+n<=P['caps'][k],k;ledger[k]+=int(n);save('ledger.json',ledger)
def sha(p):return hashlib.sha256(p.read_bytes()).hexdigest()
class Counted:
 def __init__(self,s):self.s=s
 def __getattr__(self,k):return getattr(self.s,k)
 def level_gradient(self,p):
  charge('closed_level_points',len(p));charge('conservative_delegate_units',6*len(p));return self.s.level_gradient(p)
assert not (OUT/'native-started.json').exists();save('native-started.json',{'at':datetime.datetime.now(datetime.timezone.utc).isoformat()});bindings={};data={};preserved=json.loads((ROOT/'research/experiments/miniplayer-shared-transfer-06/preservation.json').read_text())['rows']
for member in ['expanded','compact']:
 work=ROOT/('.evidence-working/expanded-geometry-02' if member=='expanded' else '.evidence-working/compact-geometry-01');items=[]
 for ref in ['a','b']:
  frozen=next(r for r in preserved if r['member']==member and r['reference']==ref)
  for name,digest in frozen['hashes'].items():assert sha(work/ref/name)==digest
  charge('Study_constructor_pixels',1360*250 if member=='expanded' else 920*240);s=Study(work/ref);assert not s.transmission_layers,'No foreground fit is allowed';assert all('response' not in style for style in s.case.get('foreground_styles',{}).values());assert all(np.min(alpha)>=0 and np.max(alpha)<=1 for _,alpha,_ in s.foreground_layers);assert all(0<=style.get('opacity',1)<=1 for style in s.case.get('foreground_styles',{}).values());case=dict(s.case);center=np.array(case['center'],float)
  if member=='expanded':center=np.array(json.loads((ROOT/'reconstruction/studies/geometric-expanded-pipeline/summary.json').read_text())['geometry']['center'])
  else:
   prior=json.loads((ROOT/'reconstruction/studies/music-mini-compact-vector/review-round/pass-03.json').read_text())['parameters'];center+=88.5*np.array([prior['shape_dx'],prior['shape_dy']])
  maskpath=work/f'{ref}-masks.npz' if member=='expanded' else ROOT/f'research/experiments/compact-geometry-01/{ref}-masks.npz';m=np.load(maskpath);assert np.array_equal(s.valid,m['glass']);knownfile=work/ref/'known.png';known=cv2.imread(str(knownfile),0)>0;bindings[str(knownfile.relative_to(ROOT))]=sha(knownfile);charge('known_erosions',1);safe=cv2.erode(known.astype(np.uint8),np.ones((43,43),np.uint8),borderType=cv2.BORDER_CONSTANT,borderValue=0)>0;items.append(dict(s=s,m=m,center=center,known=known,safe=safe,ref=ref))
 assert np.array_equal(items[0]['center'],items[1]['center']);data[member]=items
for file in ['reconstruction/closed_crowned_surface.py','reconstruction/geometric_optics.py','reconstruction/environment_radiance.py','reconstruction/families/music-mini-player.json']:
 bindings[file]=sha(ROOT/file)
save('input-FIRST.json',{'at':datetime.datetime.now(datetime.timezone.utc).isoformat(),'original_assets_exact':True,'foreground_affine_monotone':True,'bindings':bindings})
records=[]
for member,items in data.items():
 file=CACHE/f'{member}-first-front.npz';bindings[str(file.relative_to(ROOT))]=sha(file);z=np.load(file);ids=z['flat_ids'];inside=z['inside'];boundary=z['boundary'];entry=z['entry'];nf=z['outward_normal'];initial=z['reflected_direction'];camera=np.zeros_like(entry);camera[:,2]=-1;n=len(ids);charge('native_internal_launches',n);charge('Snell_points',n);charge('conservative_delegate_units',4*n);v,blocked,_=refract(camera,nf,1.,1.5);assert not blocked.any();surface=ClosedRoundedSurface((F['members'][member]['major_half'],F['geometry']['minor_half']),F['geometry']['corner_radius'],shape['eta'],shape['z_offset'],0.);event=next_convex_boundary(Counted(surface),entry,v);assert event['complete'].all();nq=event['outward_normal'];charge('Snell_points',n);out,tir,disc=refract(v,-nq,1.5,1.);charge('power_interface_points',2*n);weights=two_interface_power(camera,nf,v,nq,1.5);assert np.array_equal(weights['front'],z['reflectance']);assert np.all(weights['primary'][tir]==0)
 np.savez_compressed(OUT/f'{member}-internal-events.npz',flat_ids=ids,internal_direction=v,exit=event['point'],exit_normal=nq,exit_direction=out,blocked=tir,discriminant=disc,bracket=event['bracket'],residual=event['residual'],**weights)
 frontdown=initial[:,2]<0;frontup=~frontdown;primarydown=(~tir)&(out[:,2]<0);primaryup=(~tir)&~primarydown;frontXY=np.full((n,2),np.nan);primaryXY=np.full((n,2),np.nan)
 for mask,direction,origin,coords in [(frontdown,initial,entry,frontXY),(primarydown,out,event['point'],primaryXY)]:
  t=(-2.1-origin[mask,2])/direction[mask,2];assert (t>0).all();coords[mask]=origin[mask,:2]+t[:,None]*direction[mask,:2]
 charge('environment_queries',int(frontup.sum()));frontEnv=np.zeros(n);frontEnv[frontup]=4*annular_environment(initial[frontup]);proof=[]
 H,W=items[0]['s'].valid.shape;yy,xx=np.mgrid[:H:.5,:W:.5];x0,y0,_,_=items[0]['s'].crop;clearXY=np.stack([xx.ravel()+x0-.25,yy.ravel()+y0-.25],-1);clear=~inside.ravel()&~boundary.ravel()
 for e in items:
  def support(coords,mask):
   charge('source_endpoint_checks',len(coords));valid=np.isfinite(coords).all(-1);a=np.floor(np.where(valid,coords[:,0],0)).astype(int);b=np.floor(np.where(valid,coords[:,1],0)).astype(int);bounds=valid&(a>=0)&(b>=0)&(a+1<mask.shape[1])&(b+1<mask.shape[0]);q=np.flatnonzero(bounds);charge('bilinear_mask_lookups',4*len(q));ok=np.zeros(len(coords),bool);ok[q]=mask[b[q],a[q]]&mask[b[q]+1,a[q]]&mask[b[q],a[q]+1]&mask[b[q]+1,a[q]+1];return ok
  world=lambda coords:coords*88.5+e['center'];frontCoords=world(frontXY[frontdown]);primaryCoords=world(primaryXY[primarydown]);clearCoords=clearXY[clear];fok=support(frontCoords,e['known']);pok=support(primaryCoords,e['safe']);cok=support(clearCoords,e['known']);e.update(fok=fok,pok=pok,cok=cok,frontCoords=frontCoords,primaryCoords=primaryCoords,clearCoords=clearCoords);proof.append({'reference':e['ref'],'front_down':len(fok),'front_unsupported':int((~fok).sum()),'primary_down':len(pok),'primary_unsupported':int((~pok).sum()),'clear_unsupported':int((~cok).sum()),'TIR':int(tir.sum()),'primary_up_unresolved_material':int(primaryup.sum()),'RGB_queries':0})
 save(f'{member}-support-BEFORE-RGB.json',{'status':'KNOWN_QUERIES_CERTIFIED_WHOLE_SCENE_INCOMPLETE','records':proof})
 for e in items:
  charge('incident_fields',1);charge('known_erosions',1);field,safe,r=incident_source_filter(e['s'].source,e['known'],6.75);assert r==21 and np.array_equal(safe,e['safe'])
  def sample(source,coords,ok):
   coords=coords[ok];charge('source_RGB_queries',len(coords));a=np.floor(coords[:,0]).astype(int);b=np.floor(coords[:,1]).astype(int);u=(coords[:,0]-a)[:,None];w=(coords[:,1]-b)[:,None];return (source[b,a]*(1-u)+source[b,a+1]*u)*(1-w)+(source[b+1,a]*(1-u)+source[b+1,a+1]*u)*w
  lo=np.zeros((inside.size,3));hi=np.ones_like(lo);clearIndices=np.flatnonzero(clear);C=sample(e['s'].source,e['clearCoords'],e['cok']);lo[clearIndices[e['cok']]]=C;hi[clearIndices[e['cok']]]=C
  # Radiance bounds for computed primary paths, not source completion.
  frontLo=np.repeat(frontEnv[:,None],3,1);frontHi=frontLo.copy();fd=np.flatnonzero(frontdown);frontLo[fd]=0;frontHi[fd]=1;C=decode_srgb(sample(e['s'].source,e['frontCoords'],e['fok']));frontLo[fd[e['fok']]]=C;frontHi[fd[e['fok']]]=C
  eps=256*np.finfo(np.float32).eps/(1-256*np.finfo(np.float32).eps);g,b=F['material']['gain'],F['material']['bias'];lowerMaterial=float(decode_srgb(np.array(b)));upperMaterial=float(decode_srgb(np.array(min(1,g*(1+eps)+b))));primaryLo=np.zeros((n,3));primaryHi=np.full((n,3),4.);pd=np.flatnonzero(primarydown);primaryLo[pd]=lowerMaterial;primaryHi[pd]=upperMaterial;C=decode_srgb(neutral_color_response(sample(field,e['primaryCoords'],e['pok']),gain=g,bias=b));primaryLo[pd[e['pok']]]=C;primaryHi[pd[e['pok']]]=C
  L=weights['front'][:,None]*frontLo+weights['primary'][:,None]*primaryLo;U=weights['front'][:,None]*frontHi+weights['primary'][:,None]*primaryHi+4*weights['tail'][:,None];assert np.all(L<=U);lo[ids]=np.clip(encode_srgb(L),0,1);hi[ids]=np.clip(encode_srgb(U),0,1);lo[boundary.ravel()]=0;hi[boundary.ravel()]=1;preLo=lo.reshape(H,2,W,2,3).mean((1,3)).astype(np.float32);preHi=hi.reshape(H,2,W,2,3).mean((1,3)).astype(np.float32);charge('diagnostic_bounds',2);Clo=e['s'].apply_foreground(preLo.copy());Chi=e['s'].apply_foreground(preHi.copy());assert np.all(Clo<=Chi+1e-7)
  target=e['s'].target_crop;distance=np.maximum(Clo-target,0)+np.maximum(target-Chi,0);m=e['m']['glass'];row={'member':member,'reference':e['ref'],'original_body_pixels':int(m.sum()),'relaxed_AA2_body_RMSE_lower_bound':float(np.sqrt(np.mean((255*distance[m])**2))),'body_pixels_with_target_outside_envelope':int(np.any(distance[m]>0,axis=-1).sum()),'mean_display_interval_width':float(np.mean(Chi[m]-Clo[m])),'untraced_internal_tail_max':float(weights['tail'].max()),'source_counts':next(v for v in proof if v['reference']==e['ref']),'AA2_rim_unconverged':True,'full_guard_acceptance':False};records.append(row);prefix=f'{member}-{e["ref"]}';np.savez_compressed(OUT/f'{prefix}-bounds.npz',pre_lower=preLo,pre_upper=preHi,complete_lower=Clo,complete_upper=Chi);save(prefix+'-diagnostic.json',row)
  width=min(W,1080);height=round(H*width/W);canvas=Image.new('RGB',(3*width+4,height+64),'white');draw=ImageDraw.Draw(canvas);font=ImageFont.load_default(size=15)
  for i,(pixels,title) in enumerate([(target,'Reference'),(Clo,'AA2 conditional signal lower bound; NOT reconstruction'),(Chi,'AA2 conditional signal upper bound; NOT reconstruction')]):
   image=Image.fromarray(np.uint8(np.rint(np.clip(pixels,0,1)*255))).resize((width,height),Image.Resampling.LANCZOS);canvas.paste(image,(i*(width+2),64));draw.text((i*(width+2)+6,18),title,font=font,fill='black')
  canvas.save(OUT/f'{prefix}-envelopes.png');print(json.dumps(row),flush=True)
assert all(sha(ROOT/file)==value for file,value in bindings.items());save('result.json',{'status':'CONDITIONAL_KNOWN_SIGNAL_ENVELOPES_INCOMPLETE_SOURCE_SCENE_AND_QUADRATURE','finished':datetime.datetime.now(datetime.timezone.utc).isoformat(),'records':records,'ledger':ledger,'formal_continuous_image_certificate':False,'accepted_model':False})
