"""Fixed image-plane rim sections; no optical calculation or fitted geometry."""
from pathlib import Path
import sys,json,datetime,hashlib,csv
import numpy as np
from PIL import Image,ImageDraw,ImageFont
ROOT=Path(__file__).resolve().parents[3];OUT=Path(__file__).parent;sys.path.insert(0,str(ROOT/'reconstruction'))
from music_miniplayer_family import load_working_family
P=json.loads((OUT/'protocol.json').read_text());END=datetime.datetime.fromisoformat(P['deadline'].replace('Z','+00:00'));ledger={k:0 for k in P['caps']};F=load_working_family();L=F['length_unit_native_pixels'];g=F['geometry'];font=ImageFont.load_default(size=12)
def save(n,v):(OUT/n).write_text(json.dumps(v,indent=2,allow_nan=False)+'\n')
def charge(k,n):
 assert datetime.datetime.now(datetime.timezone.utc)<END,'Original deadline';assert ledger[k]+n<=P['caps'][k],k;ledger[k]+=int(n);save('ledger.json',ledger)
def sha(p):return hashlib.sha256(p.read_bytes()).hexdigest()
def sample(a,x,y,key):
 i,j=np.floor(x).astype(int),np.floor(y).astype(int);assert ((i>=0)&(j>=0)&(i+1<a.shape[1])&(j+1<a.shape[0])).all();charge(key,4*len(i));wx=x-i;wy=y-j
 if a.ndim==3:wx=wx[:,None];wy=wy[:,None]
 v=(a[j,i]*(1-wx)+a[j,i+1]*wx)*(1-wy)+(a[j+1,i]*(1-wx)+a[j+1,i+1]*wx)*wy;assert np.isfinite(v).all();return v
assert not (OUT/'started.json').exists();save('started.json',{'at':datetime.datetime.now(datetime.timezone.utc).isoformat()});first={};records=[];summaries=[];D=np.linspace(-6,6,49);lum=np.array([.2126,.7152,.0722]);side=(abs(D)>=3);rim=abs(D)<=1.5
for member in ['expanded','compact']:
 a=F['members'][member]['major_half'];b=g['minor_half'];R=g['corner_radius'];cx=a-R;cy=b-R;points=[]
 for sign,label in [(-1,'top'),(1,'bottom')]:
  for f in [-.5,0,.5]:points.append((f'{label}_{f:g}',np.array([f*cx,sign*b]),np.array([0.,sign])))
 for sign,label in [(-1,'left_tip'),(1,'right_tip')]:points.append((label,np.array([sign*a,0.]),np.array([sign,0.])))
 for deg in [45,135,225,315]:
  n=np.array([np.cos(np.deg2rad(deg)),np.sin(np.deg2rad(deg))]);point=np.sign(n)*np.array([cx,cy])+R*n;points.append((f'corner_{deg}',point,n))
 work=ROOT/('.evidence-working/expanded-geometry-02' if member=='expanded' else '.evidence-working/compact-geometry-01');case=json.loads((work/'a/case.json').read_text());center=np.array(json.loads((ROOT/'reconstruction/studies/geometric-expanded-pipeline/summary.json').read_text())['geometry']['center'])
 if member=='compact':
  prior=json.loads((ROOT/'reconstruction/studies/music-mini-compact-vector/review-round/pass-03.json').read_text())['parameters'];center=np.array(case['center'])+L*np.array([prior['shape_dx'],prior['shape_dy']])
 for k in ['a','b']:
  cp=work/k/'case.json';tp=work/k/'target.png';zp=ROOT/f'research/experiments/miniplayer-incident-material-20/{member}-{k}-factor0.5.npz';case=json.loads(cp.read_text());assert sha(tp)==case['source_sha256']['target.png'];
  for fp in [cp,tp,zp]:first[str(fp.relative_to(ROOT))]=sha(fp)
  im=Image.open(tp).convert('RGB');charge('decoded_target_pixels',im.width*im.height);target=np.array(im).astype(np.float64)/255;z=np.load(zp);C=z['complete'];alpha=z['coverage'];charge('decoded_array_bytes',C.nbytes+alpha.nbytes);assert C.shape[:2]==alpha.shape;x0,y0,x1,y1=case['crop'];assert C.shape==(y1-y0,x1-x0,3);sheet=Image.new('RGB',(4*280,3*155),'white');draw=ImageDraw.Draw(sheet)
  for pidx,(name,point,normal) in enumerate(points):
   xy=center+L*point+D[:,None]*normal;charge('profile_positions',len(D));tv=sample(target,xy[:,0],xy[:,1],'image_RGB_corner_lookups');cv=sample(C,xy[:,0]-x0,xy[:,1]-y0,'image_RGB_corner_lookups');av=sample(alpha,xy[:,0]-x0,xy[:,1]-y0,'coverage_corner_lookups');tl=255*(tv@lum);cl=255*(cv@lum);diff=tl-cl
   # Foreground-box diagnostics stay separate from original guards.
   gx,gy=np.floor(xy[:,0]).astype(int),np.floor(xy[:,1]).astype(int);fg=np.zeros(len(D),bool)
   for layer in case['foreground_layers']:
    xA,yA,xB,yB=layer['box'];fg|=(gx+1>=xA)&(gx<xB)&(gy+1>=yA)&(gy<yB)
   inner=D<=-3;outer=D>=3;peak=int(np.argmax(np.where(rim,tl,-np.inf)));where=int(np.argmax(np.where(rim,diff,-np.inf)));summary=dict(member=member,reference=k,section=name,outline_XY=(center+L*point).tolist(),projected_outward_normal=normal.tolist(),foreground_intersecting_positions=int(fg.sum()),target_rim_peak_luma=float(tl[peak]),target_rim_peak_offset=float(D[peak]),target_prominence_above_side_means=float(tl[peak]-max(tl[inner].mean(),tl[outer].mean())),maximum_rim_target_minus_current=float(diff[where]),maximum_excess_offset=float(D[where]),rim_luma_RMSE=float(np.sqrt(np.mean(diff[rim]**2))));summaries.append(summary)
   for j,d in enumerate(D):records.append(dict(member=member,reference=k,section=name,d_native=float(d),X=float(xy[j,0]),Y=float(xy[j,1]),target_RGB_levels=(255*tv[j]).tolist(),working_RGB_levels=(255*cv[j]).tolist(),target_luma=float(tl[j]),working_luma=float(cl[j]),saved_AA2_coverage=float(av[j]),foreground_box_intersection=bool(fg[j])))
   charge('illustrative_plot_panels',1);px,py=(pidx%4)*280,(pidx//4)*155;draw.text((px+6,py+3),name,font=font,fill='black');left,top,width,height=px+30,py+25,235,100;draw.rectangle((left,top,left+width,top+height),outline='#bbb');zero=left+width/2;draw.line((zero,top,zero,top+height),fill='#ddd')
   for values,color in [(tl,'black'),(cl,'#d65b14')]:draw.line([(left+(d+6)/12*width,top+(1-v/255)*height) for d,v in zip(D,values)],fill=color,width=2)
   draw.text((left,top+height+3),'-6px    0: frozen outline    +6px',font=font,fill='black')
  sheet.save(OUT/f'{member}-{k}-profiles.png')
  if not (OUT/'checkpoint.json').exists():
   now=datetime.datetime.now(datetime.timezone.utc);assert now<datetime.datetime.fromisoformat(P['checkpoint_deadline'].replace('Z','+00:00'));save('checkpoint.json',dict(at=now.isoformat(),first_reference_sections=12,ledger=dict(ledger)));print('CHECKPOINT '+now.isoformat(),flush=True)
save('first-hashes.json',first);last={f:sha(ROOT/f) for f in first};assert last==first;save('last-hashes.json',last);save('profiles.json',dict(records=records));save('result.json',dict(status='FIXED_IMAGE_PLANE_RIM_SECTIONS_COMPLETE',finished=datetime.datetime.now(datetime.timezone.utc).isoformat(),records=summaries,ledger=ledger,interpretation='Image brightness features only, not alpha or source-feature identity. Peaks are restricted-window samples, not fitted ridge positions.',new_rays=0,new_heights=0,optical_source_queries=0,filters=0,model_composites=0,fits=0,selected_model_changed=False));print(json.dumps({'ledger':ledger,'largest_excess':sorted(summaries,key=lambda r:r['maximum_rim_target_minus_current'],reverse=True)[:6]}),flush=True)
