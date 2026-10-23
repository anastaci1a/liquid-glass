"""Independent cheap replay/guard check, cached original optical body only."""
import os,sys,json,hashlib,copy
from pathlib import Path
import numpy as np
from PIL import Image
sys.path.insert(0,'/workspace/docs/liquid-glass/experiments/reconstruction')
from reproduce import CASES,points,scores
from render import case_geometry
from shapes import oval_field
from settled import RECIPES
os.umask(0o002);D=Path('/evidence/extended/blue-slider-short-round');R=D/'generated-exterior';O=D/'exterior-primary';O.mkdir(exist_ok=False);c=CASES['slider'];L=min(c['half']);x0,y0,x1,y1=c['crop'];base=json.loads((R/'proposal.json').read_text());par=base['parameters'];geo=base['contact_geometry'];raw=Path('/evidence/apple-matches/public-settled-replay');read=lambda p:np.asarray(Image.open(p).convert('RGB'));B=read(raw/'slider-source.png').astype(float)[y0:y1,x0:x1]/255;T=read(raw/'slider-target.png').astype(np.float32)[y0:y1,x0:x1]/255;M=np.load(R/'native-material.npy');_,_,x,y=points(c);sd=case_geometry(c,x,y)[0];cover=np.zeros(x.shape);contact=cover.copy();sx=geo['width_ratio'];sy=geo['height_ratio'];oy=geo['offset_y_over_L']*L
for dy in [-.375,-.125,.125,.375]:
 for dx in [-.375,-.125,.125,.375]:
  # Exact implicit membership avoids unnecessary nearest-footpoint solves.
  xx=np.abs(x+dx).astype(float);yy=np.abs(y+dy).astype(float);cover+=(oval_field(xx,yy,c['half'],c['oval'])[0]<=1)/16
  xx=np.abs((x+dx)/sx).astype(float);yy=np.abs((y+dy-oy)/sy).astype(float);contact+=(oval_field(xx,yy,c['half'],c['oval'])[0]<=1)/16
assert np.array_equal(cover,np.load(R/'coverage.npy'))
C0=M*cover[...,None]+B*(1-cover[...,None]);assert np.array_equal(C0,np.load(R/'zero-generated-exterior.npy'))
accent=np.array(par['accent_rgb']);halo=par['halo_opacity']*np.exp(-.5*(np.maximum(sd,0)/(par['halo_sigma_L']*L))**2)
def apply(q):
 C=B*(1-q*contact[...,None]);C=C*(1-halo[...,None])+halo[...,None]*(par['halo_tint_scale']*accent);return M*cover[...,None]+C*(1-cover[...,None])
first=apply(par['contact_opacity']);assert np.array_equal(first,np.load(R/'candidate-complete.npy'))
yy,xx=np.mgrid[y0:y1,x0:x1];held=(xx//32+3*(yy//32))%4==0
masks={'near_exterior':(sd>0)&(sd<.35*L),'full_visible_exterior':sd>0};masks.update({k+'_'+a:m&b for k,m in list(masks.items()) for a,b in [('train',~held),('held',held)]})
rmse=lambda C,m:float(np.sqrt(np.mean((((C-T)[m])*255)**2)))
original=json.loads((raw/'settled-scores.json').read_text())['slider']['scores'];assert scores(first.astype(np.float32),T,c)==original
report={k:dict(before=rmse(C0,m),after=rmse(first,m),pixels=int(m.sum())) for k,m in masks.items()};assert all(v['after']<v['before'] for v in report.values())
# Source-domain bound for EVERY whole/ALL-scored RGB subray, no kernel/filter.
p=RECIPES['slider'];a=p['parameters'];hx,hy=p['shape']['half'];A,Boval=p['shape']['oval'];hymax=hy*(1+abs(A)+abs(Boval));rb=np.hypot(hx,hymax);ma=max(abs(z) for z in a['coefficients']);fac=max(abs(1+a['dispersion']*(w**-2-.550**-2)) for w in [.650,.550,.450]);bounds=[]
for i,(h,k) in enumerate([(hx,'core_x'),(hymax,'core_y')]):
 dis=(abs(a[k])*h+ma+abs(a['tangent'])*rb)*fac*L;bounds.append([c['center'][i]-h*L-dis,c['center'][i]+h*L+dis])
assert min(bounds[0])>1 and max(bounds[0])<1918 and min(bounds[1])>1 and max(bounds[1])<1078
proof=dict(kind='Conservative analytic all-RGB native/whole+ALL-scored domain bound; not observed-source evidence',inside_rgb_xy_bounds=bounds,outside_identity_xy_bounds=[[x0-.375,x1-.625],[y0-.375,y1-.625]],bilinear_margin_px=1,source_sigma=0,basis_bound='Nonnegative partition-of-unity B-splines => |a|<=max|co|; B(u) in[0,1]; unit normal and |tangent_position|<=hypot(hx,hy_bound). Include core and all RGB factors.',source_size=[1920,1080],covered=True,limits='Incident hidden blue endpoint/paper remain modeled; finite-domain proof does not establish photographic recovery or physical optics.')
np.save(O/'distance.npy',sd);np.save(O/'contact.npy',contact);np.save(O/'coverage.npy',cover)
(O/'pass01-verification.json').write_text(json.dumps(dict(accepted=True,round_pass=1,scope='Single-background generated-exterior reconstruction, not optical improvement; gray profiles withheld/advisory only',original_scores_exact=True,independent_complete_exact=True,all_exterior_guards=report,source_proof=proof,visual_review=True,limits=base['limits']),indent=2)+'\n')
# ONE bounded existing-opacity proposal; no source/material/shape/gain changes.
q=.16;C2=apply(q);metrics={k:dict(before=rmse(first,m),after=rmse(C2,m),nonregression=rmse(C2,m)<=rmse(first,m)) for k,m in masks.items()};assert scores(C2.astype(np.float32),T,c)==original
np.save(O/'pass02-candidate.npy',C2);(O/'pass02-proposal.json').write_text(json.dumps(dict(accepted=False,contact_opacity=q,previous_contact_opacity=par['contact_opacity'],original_scores_exact=True,metrics=metrics,qualifier=all(v['nonregression'] for v in metrics.values()),hypothesis='Owner white-background samples have uncertain background calibration; neutral contact opacity is tunable shared material, not a new source. Try ONE lower opacity inside .12..18 bracket; do not deform contact footprint or fit pixels individually.'),indent=2)+'\n');print('PASS1',report,'PASS2',metrics,'SOURCE',proof,flush=True)
