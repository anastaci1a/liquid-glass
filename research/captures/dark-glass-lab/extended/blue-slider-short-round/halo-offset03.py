"""One common geometric halo offset, no source/body/contact changes."""
import os,json,sys
from pathlib import Path
import numpy as np
from PIL import Image
sys.path.insert(0,'/workspace/docs/liquid-glass/experiments/reconstruction');from reproduce import CASES,points;from render import case_geometry
os.umask(0o002);D=Path('/evidence/extended/blue-slider-short-round');P=D/'exterior-primary';O=D/'halo-offset03';O.mkdir(exist_ok=False);c=CASES['slider'];L=min(c['half']);_,_,x,y=points(c);sd=np.load(P/'distance.npy');a=np.load(P/'coverage.npy');contact=np.load(P/'contact.npy');M=np.load(D/'generated-exterior/native-material.npy');v=np.array(json.loads((D/'exterior-joint02/result.json').read_text())['candidate']['parameters']);base=np.load(D/'exterior-joint02/candidate-complete.npy');original=json.loads((D/'generated-exterior/proposal.json').read_text());accent=np.array(original['parameters']['accent_rgb']);read=lambda n:np.asarray(Image.open('/evidence/apple-matches/public-settled-replay/slider-'+n+'.png').convert('RGB'));B=read('source').astype(float)[440:690,540:985]/255;T=read('target').astype(np.float32)[440:690,540:985]/255;yy,xx=np.mgrid[440:690,540:985];held=(xx//32+3*(yy//32))%4==0;masks={'near_exterior':(sd>0)&(sd<.35*L),'full_visible_exterior':sd>0};masks.update({k+'_'+n:m&b for k,m in list(masks.items()) for n,b in [('train',~held),('held',held)]});rmse=lambda C,m:float(np.sqrt(np.mean(((C-T)[m]*255)**2)))
bp=json.loads((D/'halo-profiles.json').read_text())['observations'][1]['profiles'];bd=np.array([r['outward_distance_over_L'] for r in bp]);bP=np.array([r['uncovered_donor_rgb'] for r in bp])/255;bT=np.array([r['target_rgb'] for r in bp])/255
q,ha,s,beta=v
bscore=lambda offset:float(np.sqrt(np.mean(((1-(ha*np.exp(-.5*(np.maximum(bd-offset,0)/s)**2))[:,None])*bP+(ha*np.exp(-.5*(np.maximum(bd-offset,0)/s)**2))[:,None]*beta*accent-bT)**2))*255)
record=dict(scope='One generated-halo geometric offset; original optics/contact/source frozen',previous_parameters=v.tolist(),baseline_gray_profile_rmse=bscore(0),trials=[])
for dy in [.1,.05]:
 dh=case_geometry(c,x,y-dy*L)[0];h=ha*np.exp(-.5*(np.maximum(dh,0)/(s*L))**2);C0=B*(1-q*contact[...,None]);C=M*a[...,None]+((1-h[...,None])*C0+h[...,None]*beta*accent)*(1-a[...,None]);metrics={k:dict(before=rmse(base,m),after=rmse(C,m),nonregression=rmse(C,m)<=rmse(base,m)) for k,m in masks.items()};profile=bscore(dy);ok=all(v['nonregression'] for v in metrics.values()) and profile<=bscore(0);row=dict(halo_offset_y_L=dy,metrics=metrics,gray_profile_rmse=profile,qualifier=bool(ok));record['trials'].append(row)
 if ok:record['candidate']=row;np.save(O/'candidate-complete.npy',C);break
(O/'result.json').write_text(json.dumps(record,indent=2)+'\n');print(json.dumps(record),flush=True)
