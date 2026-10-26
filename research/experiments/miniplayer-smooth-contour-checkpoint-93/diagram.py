"""One proposed 2D contour only; no actual-height or optical adapter."""
from pathlib import Path
import datetime,hashlib,json
import numpy as np
from PIL import Image,ImageDraw,ImageFont
ROOT=Path(__file__).resolve().parents[3];OUT=Path(__file__).parent
P=json.loads((OUT/'protocol.json').read_text());END=datetime.datetime.fromisoformat(P['deadline']);ledger={k:0 for k in P['caps']}
def save(n,x):(OUT/n).write_text(json.dumps(x,indent=2,allow_nan=False)+'\n')
def sha(p):return hashlib.sha256(p.read_bytes()).hexdigest()
def charge(k,n):
 assert datetime.datetime.now(datetime.timezone.utc)<END;assert ledger[k]+n<=P['caps'][k],(k,ledger[k],n);ledger[k]+=int(n);save('ledger.json',ledger)
def boundary(theta,A,B,R):
 a,b=A-R,B-R;n=np.stack([np.cos(theta),np.sin(theta)],-1);h=np.hypot(a*n[...,0],b*n[...,1]);e=np.stack([a*a*n[...,0]/h,b*b*n[...,1]/h],-1);return e+R*n,n,h+R,e,R+(a*b)**2/h**3
F=json.loads((ROOT/'reconstruction/families/music-mini-player-working.json').read_text());L=F['length_unit_native_pixels'];B=L*F['geometry']['minor_half'];R=L*F['geometry']['corner_radius'];first={};cases=[]
for member in ['expanded','compact']:
 work=ROOT/f'.evidence-working/{member}-geometry-0{2 if member=="expanded" else 1}';center=json.loads((ROOT/'reconstruction/studies/geometric-expanded-pipeline/summary.json').read_text())['geometry']['center']
 if member=='compact':
  ca=json.loads((work/'a/case.json').read_text());pr=json.loads((ROOT/'reconstruction/studies/music-mini-compact-vector/review-round/pass-03.json').read_text())['parameters'];center=[ca['center'][0]+L*pr['shape_dx'],ca['center'][1]+L*pr['shape_dy']]
 for ref in ['a','b']:
  cp=work/ref/'case.json';tp=work/ref/'target.png';case=json.loads(cp.read_text());assert sha(tp)==case['source_sha256']['target.png']
  with Image.open(tp) as im:assert im.size==(1920,1080)
  for f in [cp,tp]:first[str(f.relative_to(ROOT))]=sha(f)
  cases.append((member,ref,tp,center))
for f in [Path(__file__),ROOT/'reconstruction/families/music-mini-player-working.json',ROOT/'research/experiments/agent-miniplayer-contour-theory-58/README.md']:
 first[str(f.relative_to(ROOT))]=sha(f)
save('first-hashes.json',first);charge('contour_proposals',1);curves={};controls=[];sections=[]
for member in ['expanded','compact']:
 A=L*F['members'][member]['major_half'];a,b=A-R,B-R
 t=np.linspace(0,2*np.pi,32768,endpoint=False);theta=np.unique(np.concatenate([t,np.mod(np.arctan2(a*np.sin(t),b*np.cos(t)),2*np.pi)]));charge('boundary_points',65536);xy,n,h,e,curv=boundary(theta,A,B,R)
 chord=np.linalg.norm(np.roll(xy,-1,axis=0)-xy,axis=1);ellipse_error=float(np.max(abs((e[:,0]/a)**2+(e[:,1]/b)**2-1)));support_error=float(np.max(abs(np.sum(xy*n,axis=1)-h)));normal_error=float(np.max(abs(np.sum(n*n,axis=1)-1)));extent_error=float(np.max(abs(np.max(abs(xy),axis=0)-[A,B])));old_sd=np.hypot(np.maximum(abs(xy[:,0])-a,0),np.maximum(abs(xy[:,1])-b,0))-R
 assert ellipse_error<1e-12 and support_error<1e-9 and normal_error<1e-12 and extent_error<1e-9
 assert np.max(chord)<.6 and np.min(curv)>0 and np.max(old_sd)<1e-9
 # Fixed controls are distinct geometry queries, included before evaluation.
 tt=np.linspace(0,2*np.pi,256,endpoint=False);charge('control_points',4*256);p0,*_=boundary(tt,A,B,R);pm,*_=boundary(-tt,A,B,R);ps,*_=boundary(tt,2*A,2*B,2*R);pc,*_=boundary(tt,B,B,R)
 mirror=float(np.max(abs(pm-p0*np.array([1,-1]))));scale=float(np.max(abs(ps-2*p0)));circle=float(np.max(abs(np.linalg.norm(pc,axis=1)-B)));assert max(mirror,scale,circle)<1e-9
 controls.append({'member':member,'A':A,'B':B,'R':R,'inner_a':a,'inner_b':b,'raw_reserved_points':65536,'unique_points':len(theta),'maximum_chord_px':float(chord.max()),'ellipse_residual':ellipse_error,'support_residual_px':support_error,'unit_normal_residual':normal_error,'extent_residual_px':extent_error,'minimum_curvature_radius_px':float(curv.min()),'maximum_curvature_radius_px':float(curv.max()),'largest_old_signed_distance_px':float(old_sd.max()),'mirror_residual_px':mirror,'scale_residual_px':scale,'circle_residual_px':circle})
 curves[member]=xy;np.savez_compressed(OUT/f'{member}-contour.npz',normal_angle=theta,xy=xy,normal=n,curvature_radius=curv,old_signed_distance=old_sd)
 for x in [0,a*.5,a-32,a-16,a,a+16,a+32,a+64]:
  lo,hi=0.,np.pi/2
  for _ in range(64):
   charge('section_bisection_points',1);mid=(lo+hi)/2;pt=boundary(np.array(mid),A,B,R)[0]
   if pt[0]>x:lo=mid
   else:hi=mid
  charge('section_bisection_points',1);pt=boundary(np.array((lo+hi)/2),A,B,R)[0];old_y=b+np.sqrt(R*R-max(x-a,0)**2);sections.append({'member':member,'x_local_px':float(x),'offset_from_old_join_px':float(x-a),'new_y_local_px':float(pt[1]),'old_y_local_px':float(old_y),'inward_vertical_change_px':float(old_y-pt[1]),'x_residual_px':float(pt[0]-x)})
save('controls.json',controls);save('sections.json',sections);now=datetime.datetime.now(datetime.timezone.utc);assert now<datetime.datetime.fromisoformat(P['checkpoint_deadline']);save('checkpoint.json',{'at':now.isoformat(),'geometry_controls_pass':True,'reference_payload_unread':True,'ledger':dict(ledger)});print('CHECKPOINT',now.isoformat(),flush=True)
font=ImageFont.load_default(size=16);boxes=[]
for member,ref,tp,center in cases:
 charge('target_bitmap_pixels',1920*1080);target=Image.open(tp).convert('RGB');cx,cy=center;A=L*F['members'][member]['major_half'];core=A-R;new=curves[member]+np.array(center);sheet=Image.new('RGB',(1728,4*178),'#eee');d=ImageDraw.Draw(sheet)
 row=0
 for sign,label in [(-1,'top'),(1,'bottom')]:
  for side in [-1,1]:
   jx=int(np.floor(cx+side*core+.5));jy=int(np.floor(cy+sign*B+.5));box=(jx-96,jy-24,jx+96,jy+24);crop=target.crop(box).resize((576,144),Image.Resampling.NEAREST);old=crop.copy();proposed=crop.copy();x=np.linspace(box[0],box[2],769);charge('old_contour_points',len(x));qx=np.maximum(abs(x-cx)-core,0);valid=qx<=R;y=cy+sign*(B-R+np.sqrt(np.maximum(R*R-qx*qx,0)))
   ImageDraw.Draw(old).line([(float((xx-box[0])*3),float((yy-box[1])*3)) for xx,yy in zip(x[valid],y[valid])],fill='#ff00ff',width=1)
   sel=(new[:,0]>=box[0]-1)&(new[:,0]<=box[2]+1)&(new[:,1]>=box[1]-1)&(new[:,1]<=box[3]+1);pts=new[sel];ImageDraw.Draw(proposed).line([(float((xx-box[0])*3),float((yy-box[1])*3)) for xx,yy in pts],fill='#00ffff',width=1)
   top=row*178;d.text((5,top+5),f'{member} {ref} {label} {"left" if side<0 else "right"}: reference | current (magenta) | proposed (cyan)',font=font,fill='black')
   for col,im in enumerate([crop,old,proposed]):sheet.paste(im,(576*col,top+30))
   boxes.append({'member':member,'reference':ref,'side':label,'end':'left' if side<0 else 'right','native_box':box,'display_scale':3,'line_width_display_pixels':1});row+=1
 charge('diagnostic_pngs',1);sheet.save(OUT/f'{member}-{ref}-contour-comparison.png')
last={f:sha(ROOT/f) for f in first};assert last==first;save('last-hashes.json',last);save('presentation.json',boxes);save('result.json',{'finished':datetime.datetime.now(datetime.timezone.utc).isoformat(),'status':'ONE_UNFITTED_2D_CONTOUR_CONTROLLED_AND_ANNOTATED','ledger':ledger,'selected_state_changed':False,'optical_geometry_implemented':False});print(json.dumps(controls),flush=True)
