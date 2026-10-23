"""Generated slider exterior, frozen original optical body. No copied shadows.
A-only exterior calibration; gray B profiles are withheld transfer evidence only.
"""
import os,sys,json,hashlib
from pathlib import Path
import cv2,numpy as np
from PIL import Image,ImageDraw
from scipy.optimize import least_squares
sys.path.insert(0,'/workspace/docs/liquid-glass/experiments/reconstruction')
from reproduce import CASES,points,scores
from render import case_geometry
from settled import RECIPES,render
os.umask(0o002);cv2.setNumThreads(1)
D=Path('/evidence/extended/blue-slider-short-round');O=D/'generated-exterior';O.mkdir(exist_ok=False)
R=Path('/evidence/apple-matches/public-settled-replay');c=CASES['slider'];L=min(c['half']);p=RECIPES['slider'];x0,y0,x1,y1=c['crop'];source=np.asarray(Image.open(R/'slider-source.png').convert('RGB')).astype(float)/255;target=np.asarray(Image.open(R/'slider-target.png').convert('RGB')).astype(np.float32)/255;T=target[y0:y1,x0:x1];B=source[y0:y1,x0:x1]
M=render(source,c,p,samples=4);np.save(O/'native-material.npy',M);original=scores(M,T,c);old=json.loads((R/'settled-scores.json').read_text())['slider']['scores'];assert original==old,(original,old)
_,_,x,y=points(c);sd=case_geometry(c,x,y)[0];coverage=np.zeros(x.shape);contact=np.zeros(x.shape);sx=1963/1896;sy=929/906;offset_y=-(sy-1)*c['half'][1]
for dy in [-.375,-.125,.125,.375]:
 for dx in [-.375,-.125,.125,.375]:
  coverage+=(case_geometry(c,x+dx,y+dy)[0]<=0)/16
  contact+=(case_geometry(c,(x+dx)/sx,(y+dy-offset_y)/sy)[0]<=0)/16
clean=M*coverage[...,None]+B*(1-coverage[...,None]);np.save(O/'zero-generated-exterior.npy',clean);np.save(O/'coverage.npy',coverage)
accent=np.median(target[544:556,580:625],axis=(0,1)).astype(float);profiles=json.loads((D/'halo-profiles.json').read_text())['observations'];A=profiles[0]['profiles'];ds=np.array([r['outward_distance_over_L'] for r in A]);P=np.array([r['uncovered_donor_rgb'] for r in A])/255;obs=np.array([r['target_rgb'] for r in A])/255
# Calibrate ONE shared halo law on predeclared A profile patches only, not full image.
# C=(1-alpha)B+alpha*beta*accent, alpha=a exp(-.5(d/sigma)^2).
fun=lambda v:((1-(v[0]*np.exp(-.5*(ds/v[1])**2))[:,None])*P+(v[0]*np.exp(-.5*(ds/v[1])**2))[:,None]*v[2]*accent-obs).ravel()
opt=least_squares(fun,[.14,.8,.85],bounds=([0,.1,0],[.4,2,1]),max_nfev=80)
# Neutral contact opacity from owner white-background samples, unsaturated as requested.
contact_samples=np.array([[201,209,214],[205,209,218],[202,210,213],[205,210,217]],float)
contact_opacity=1-float(contact_samples.mean()/255)
v=[contact_opacity,*opt.x.tolist()]
def complete(v):
 q,a,s,beta=v;C0=B*(1-q*contact[...,None]);alpha=a*np.exp(-.5*(np.maximum(sd,0)/(s*L))**2);background=C0*(1-alpha[...,None])+alpha[...,None]*(beta*accent);return M*coverage[...,None]+background*(1-coverage[...,None])
C=complete(v);np.save(O/'candidate-complete.npy',C);assert scores(C.astype(np.float32),T,c)==original
masks={'near_exterior':(sd>0)&(sd<.35*L),'full_visible_exterior':sd>0}
rmse=lambda a,t,m:float(np.sqrt(np.mean((((a-t)[m])*255)**2)))
report={k:dict(before=rmse(clean,T,m),after=rmse(C,T,m),pixels=int(m.sum())) for k,m in masks.items()};print('EXTERIOR',report,flush=True)
# Independent gray-profile prediction, no B fit or source/optics adoption.
bp=profiles[1]['profiles'];bds=np.array([r['outward_distance_over_L'] for r in bp]);bP=np.array([r['uncovered_donor_rgb'] for r in bp])/255;bT=np.array([r['target_rgb'] for r in bp])/255;ba=v[1]*np.exp(-.5*(bds/v[2])**2);bC=(1-ba[:,None])*bP+ba[:,None]*v[3]*accent
record=dict(scope='UNACCEPTED A-only generated-exterior proposal; B profile transfer only, no paired optical epoch',parameters=dict(contact_opacity=v[0],halo_opacity=v[1],halo_sigma_L=v[2],halo_tint_scale=v[3],accent_rgb=accent.tolist()),contact_geometry=dict(width_ratio=sx,height_ratio=sy,offset_y_over_L=offset_y/L,rule='Measured wider/taller original-shape affine footprint, horizontally centered and bottom aligned; native4x4 coverage, neutral shadow'),halo_law='C0=B*(1-contact_opacity*contact_coverage); halo=a*exp(-.5*(max(sd,0)/(sigma*L))^2); Bout=(1-halo)*C0+halo*beta*accent; complete=body*coverage+Bout*(1-coverage)',original_scores_exact=True,original_scores=original,A_guards=report,gray_profile_transfer=dict(baseline_rmse=float(np.sqrt(np.mean((bP-bT)**2))*255),candidate_rmse=float(np.sqrt(np.mean((bC-bT)**2))*255),predicted_rgb=(bC*255).tolist(),reference_rgb=(bT*255).tolist()),profile_fit=dict(evaluations=int(opt.nfev),success=bool(opt.success),message=str(opt.message),trained='Only eight predeclared A exterior profile patches; B withheld',ordinary_blur=False,dispersion=False),inputs={n:hashlib.sha256((R/n).read_bytes()).hexdigest() for n in ['slider-source.png','slider-target.png']},limits='Native source/optical body unchanged, original conditional source ambiguity retained. Contact opacity uses owner samples on assumed white (not verified acquisition/color calibration). UI-accent halo is empirical, not identified lighting/Apple algorithm; no B source or matched interaction state established. Copied old exterior context is absent but removal earns no credit. Do not count until independent source/native/visual acceptance.')
(O/'proposal.json').write_text(json.dumps(record,indent=2)+'\n');pair=Image.new('RGB',(1440,round(250*720/445)+64),'white');dr=ImageDraw.Draw(pair)
for i,(a,label) in enumerate([(T,'Apple reference'),(C,'Generated shadow and halo / frozen body')]):dr.text((i*720+10,22),label,fill='black');pair.paste(Image.fromarray(np.rint(np.clip(a,0,1)*255).astype(np.uint8)).resize((720,round(250*720/445)),Image.Resampling.LANCZOS),(i*720,64))
pair.save(O/'comparison.png');print(json.dumps(record['gray_profile_transfer']),flush=True)
