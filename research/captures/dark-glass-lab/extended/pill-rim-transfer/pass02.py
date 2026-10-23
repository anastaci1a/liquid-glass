from pathlib import Path
import json,cv2,numpy as np
from extended_fit import Study
from render import shade
from vector_revision import composite
from publish import pair
cv2.setNumThreads(1)
R=Path('/evidence/extended/safari-tab-pill-round');D=Path('/evidence/extended/pill-rim-transfer/pass02');assert not D.exists();D.mkdir();s=Study(R/'a-canonical');r=json.loads((R/'pass-03/recipe.json').read_text());p=r['parameters'];co=np.array(r['material']);old=np.load(R/'pass-03/native-arrays.npz');base=json.loads((D.parent/'result.json').read_text())['rows'][0];assert np.array_equal(composite(s,p,old['material']),old['complete']);assert not any(k in p for k in ['ambient_rim_response','material_chroma_sensitivity','grazing_reflection']);assert p['post_sigma']==0

def response(sd,nx,ny,w):return np.exp(-(np.maximum(-sd,0)/w)**2)*(.5*(nx+ny)**2)
def render(a,w):
 H,W=old['material'].shape[:2];M=np.empty((H,W,3),np.float32);P=np.empty((H,W),np.float32);audit=dict(minimum=1.,maximum=0.,clipped_channels=0)
 for row,bottom,W,x,y in s.raster_tiles():
  C,J=s.field(x,y,p);C=shade(C,J,co);sd,nx,ny=s.shape(x,y,p)[-1];h=response(sd,nx,ny,w);assert np.isfinite(h).all() and h.min()>=0 and h.max()<=1+1e-8
  raw=C+a*h[...,None];audit['minimum']=min(audit['minimum'],float(raw.min()));audit['maximum']=max(audit['maximum'],float(raw.max()));audit['clipped_channels']+=int(np.count_nonzero((raw<0)|(raw>1)));C=np.clip(raw,0,1);M[row:bottom]=C.reshape(bottom-row,2,W,2,3).mean((1,3));P[row:bottom]=h.reshape(bottom-row,2,W,2).mean((1,3))
 # This accepted pill has no ordinary source/output filtering or post material.
 expected=old['material']+a*P[...,None];err=float(np.max(abs(expected-M)));assert err<1e-6
 return M,audit,err
rows=[]
for n,a in enumerate([.15,.1,.075]):
 O=D/f'trial{n}';O.mkdir();M,audit,err=render(a,.028);C=composite(s,p,M);np.savez_compressed(O/'arrays.npz',material=M,complete=C,alpha=old['alpha']);q=s.scores(M);q['E']=float(np.sqrt(q['loss']));g={};x0,y0,x1,y1=s.crop;yy,xx=np.mgrid[y0:y1,x0:x1];fg=np.zeros(s.valid.shape,bool)
 for name,layer in zip(['count','plus'],s.case['foreground_layers']):
  x,y,z,w=layer['box'];m=(xx>=x)&(xx<z)&(yy>=y)&(yy<w);fg|=m;g['glyph_'+name]=float(np.sqrt(np.mean(((C-s.target_crop)[m]*255)**2)))
 for name,m in [('combined_glyph',fg),('near_exterior',(s.sd>0)&(s.sd<=.35)),('full_exterior',s.sd>0)]:g[name]=float(np.sqrt(np.mean(((C-s.target_crop)[m]*255)**2)))
 checks={k:q[k]['rmse']<=base['scores'][k]['rmse']for k in ['glass','rim','held','interior']};checks.update(E=q['E']<base['scores']['E'],SSIM=q['ssim']>=base['scores']['ssim'],no_clipping=audit['clipped_channels']==0);checks.update({k:g[k]<=base['guards'][k] for k in g});row=dict(amplitude=a,width=.028,scores=q,guards=g,checks=checks,numerical_qualifier=all(checks.values()),unclipped_audit=audit,independent_cached_addition_max_error=err,source_ray_and_filter_proof_transfers=True);rows.append(row);(D/'result.json').write_text(json.dumps(dict(rows=rows,accepted_primary=False,accepted_passes=0),indent=2)+'\n');images=[cv2.resize(np.uint8(np.rint(np.clip(z,0,1)*255)),(630,420),interpolation=cv2.INTER_LANCZOS4)for z in [s.target_crop,C]];pair(*images,('Apple source','Reconstruction'),font_size=32).save(O/'comparison.png');print(json.dumps(row),flush=True)
 if row['numerical_qualifier']:break
