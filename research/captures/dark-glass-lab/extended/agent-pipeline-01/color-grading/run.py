"""One constrained common-neutral affine material proposal; saved physical layers."""
from pathlib import Path
import sys,time,json,numpy as np,cv2
P=Path('/evidence/extended/agent-pipeline-01');O=P/'color-grading';sys.path.insert(0,str(P/'code'))
from extended_fit import Study
from geometric_render import coverage_blur
proto=json.loads((O/'protocol.json').read_text());deadline=__import__('datetime').datetime.fromisoformat(proto['deadline'].replace('Z','+00:00')).timestamp()
def gate():assert time.time()<deadline,'Actual color20minute cap'
assert not (O/'result.json').exists(),'Do not restart completed material study'
def scores(s,masks,C):
 r=s.scores(C);err=(C-s.target_crop)*255;r['E']=float(np.sqrt(r['loss']));r['exterior']={'pixels':int(masks['exterior'].sum()),'rmse':float(np.sqrt(np.mean(err[masks['exterior']]**2)))};r['foreground_MSE']=[];x0,y0,_,_=s.crop
 for layer in s.case['foreground_layers']:
  a,b,c,d=layer['box'];e=err[b-y0:d-y0,a-x0:c-x0];r['foreground_MSE'].append(float(np.mean(e*e)))
 return r
H=np.zeros((2,2));v=np.zeros(2);constant=0.;cases={};baseledger=json.loads((P/'blurriness/ledger.json').read_text());base=next(t for t in baseledger if t['sigma_native_px']==6.75)
for key in ['a','b']:
 gate();s=Study(P/f'inputs/{key}');assert not s.transmission_layers;masks=np.load(P/f'historical-{key}-masks.npz');M=np.load(P/'blurriness'/f'{key}-sigma6p75-material.npy');alpha=np.load(P/'blurriness'/f'{key}-coverage.npy');clear=np.load(P/'blurriness'/f'{key}-clear-premultiplied.npy');lens=np.load(P/'blurriness'/f'{key}-lens-color.npy');train=masks['glass']&~masks['held'];rim=train&masks['rim'];weights=np.where(train,.7/train.sum(),0)+np.where(rim,.3/rim.sum(),0);weights=np.repeat((weights[train]/6),3);A=np.stack([(M-clear)[train].ravel(),np.repeat(alpha[train],3)],1);y=(s.target_crop-clear)[train].ravel();assert np.isfinite(A).all() and np.isfinite(y).all();H+=A.T@(weights[:,None]*A);v+=A.T@(weights*y);constant+=float((weights*y*y).sum());cases[key]=(s,masks,lens,clear,alpha)
p=np.linalg.solve(H,v);inside=lambda z:.25<=z[0]<=1 and 0<=z[1]<=.6 and .75<=z.sum()<=1
# Finite exact constrained convex quadratic boundary alternatives, not optimizer iterations.
polygon=np.array([[.75,0],[1,0],[.4,.6],[.25,.6],[.25,.5]]);options=[]
if inside(p):options.append(('unconstrained',p))
else:
 for k,a in enumerate(polygon):
  d=polygon[(k+1)%len(polygon)]-a;t=float(np.clip((d@(v-H@a))/(d@H@d),0,1));options.append((f'edge{k}',a+t*d))
loss=lambda z:float(z@H@z-2*z@v+constant)
label,proposal=min(options,key=lambda kv:loss(kv[1]));assert inside(proposal)
fit={'family':'common neutral encoded affine','unconstrained':p.tolist(),'constrained_proposal':proposal.tolist(),'selected_constraint':label,'normal_matrix':H.tolist(),'condition_number':float(np.linalg.cond(H)),'training_objective':loss(proposal),'held_used_in_fit':False,'foreground_used_in_fit':False,'polygon_projection_candidates':[{'label':k,'g_b':z.tolist(),'loss':loss(z)} for k,z in options],'surrogate_precision':'Proposal uses cached nativefloat32 integrated material minus known clear. Affine/filter commutation exact mathematically; native cast/order is a nearby numerical surrogate. Actual shade-before-filter compositor below alone scores.'};(O/'analytic-proposal.json').write_text(json.dumps(fit,indent=2));ledger=[];selected=None
for t in proto['fixed_backtracks']:
 gate();gb=np.array([1.,0.])+t*(proposal-np.array([1.,0.]));g,b=gb;assert inside(gb);row={'backtrack':t,'g':float(g),'b':float(b),'cases':{}}
 for key,(s,masks,lens,clear,alpha) in cases.items():
  shade=g*lens+b;B=coverage_blur(shade,alpha,6.75);M=(alpha[...,None]*B+clear).astype(np.float32);C=s.apply_foreground(M.copy());r=scores(s,masks,C);basecase=base['cases'][key]['scores'];guards={x:r[x]['rmse']<=basecase[x]['rmse'] for x in ['glass','rim','held','interior','exterior']};guards.update(E=r['E']<=basecase['E'],ssim=r['ssim']>=basecase['ssim']);guards.update({f'foreground{k}':z<=basecase['foreground_MSE'][k] for k,z in enumerate(r['foreground_MSE'])});raw=shade[alpha>0];post=B[alpha>0];native=M[np.isfinite(M).all(2)];audit={'pre_minmax':[float(raw.min()),float(raw.max())],'pre_below0':int((raw<0).sum()),'pre_above1':int((raw>1).sum()),'post_minmax':[float(post.min()),float(post.max())],'post_below0':int((post<0).sum()),'post_above1':int((post>1).sum()),'native_below0':int((native<0).sum()),'native_above1':int((native>1).sum())};assert audit['pre_below0']==audit['pre_above1']==audit['post_below0']==audit['post_above1']==audit['native_below0']==audit['native_above1']==0
  crops={};x0,y0,_,_=s.crop
  for name,(a,b0,c,d) in json.loads((P/'refraction/h1/protocol.json').read_text())['reference_crops'].items():
   m=np.zeros(s.valid.shape,bool);m[max(0,b0-y0):min(M.shape[0],d-y0),max(0,a-x0):min(M.shape[1],c-x0)]=True;m&=s.valid
   if m.any():e=(C-s.target_crop)[m]*255;crops[name]={'pixels':int(m.sum()),'RGB_RMSE':float(np.sqrt(np.mean(e*e))),'luma_RMSE':float(np.sqrt(np.mean((e@np.array([.2126,.7152,.0722]))**2))),'signed_RGB':e.mean(0).tolist()}
  np.save(O/f'{key}-step{t}-material.npy',M);np.save(O/f'{key}-step{t}-complete.npy',C);np.save(O/f'{key}-step{t}-lens.npy',B);row['cases'][key]={'scores':r,'guards':guards,'all_guards':bool(all(guards.values())),'raw_clipping':audit,'advisory_crops':crops}
 row['paired_qualifier']=all(c['all_guards'] for c in row['cases'].values());ledger.append(row);(O/'ledger.json').write_text(json.dumps(ledger,indent=2,allow_nan=False));print(json.dumps({'t':t,'g':float(g),'b':float(b),'paired_qualifier':row['paired_qualifier'],'E':{k:z['scores']['E'] for k,z in row['cases'].items()},'failed':{k:[g for g,ok in z['guards'].items() if not ok] for k,z in row['cases'].items()}}),flush=True)
 if row['paired_qualifier']:
  selected=row;break
result={'status':'FIRST_STRICT_LOCAL_QUALIFIER_PENDING_VISUAL_PRIMARY' if selected else 'NEGATIVE_ALL_PREREGISTERED_BACKTRACKS','selected':selected,'fit':fit,'trials':ledger,'new_rays':0,'new_source_queries':0,'historical_public_adoption':False,'finished_unix':time.time()};(O/'result.json').write_text(json.dumps(result,indent=2,allow_nan=False))
