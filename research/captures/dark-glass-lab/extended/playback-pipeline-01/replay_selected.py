"""Verify the accepted cached pipeline; never fit, trace rays or overwrite evidence."""
import os,json,hashlib
from pathlib import Path
import numpy as np
from PIL import Image
from geometric_render import coverage_blur
from settled import icon_color
from reproduce import CASES,points,masks,scores
os.umask(2)
P=Path('/evidence/extended/playback-pipeline-01');R=Path('/evidence/extended/playback-short-round/pass-03');D=P/'final-review';D.mkdir(exist_ok=True);out=D/'cached-replay.json';assert not out.exists()
sha=lambda f:hashlib.sha256(Path(f).read_bytes()).hexdigest()
inputs=Path('/evidence/apple-matches/public-settled-replay');expected={'media-source.png':'ae20f4366287078794c6e84d70aff6e786400456264d88ffd832fd478d7b23f6','media-target.png':'f47fba56384d84de3c106812e8b153fe7a826cfbd0dc082a75f62bc4e2df6bb9'}
for f,h in expected.items():assert sha(inputs/f)==h
p=json.loads((R/'replay-record.json').read_text())['recipe'];case=CASES['media'];x0,y0,x1,y1=case['crop'];M=np.load(P/'blurriness/raw-lens-material.npy');A=np.load(P/'blurriness/coverage.npy');clear=np.load(P/'blurriness/clear-premultiplied.npy');B=coverage_blur(M,A,1.7);assert np.array_equal(B,np.load(P/'blurriness/candidate-material.npy'))
C=(B*A[...,None]+clear).astype(np.float32);L=245.;a,b,c,d=[int(round(v*L+case['center'][i%2])) for i,v in enumerate(p['icon']['box_over_L'])];sl=np.s_[b-y0:d-y0,a-x0:c-x0];alpha=np.asarray(Image.open(P/'code'/p['icon']['coverage']),float)/255;color=icon_color(np.load(R/'candidate-material.npy'),p['icon'],L);C[sl]=C[sl]*(1-alpha[...,None])+color[sl]*alpha[...,None];saved=np.load(P/'blurriness/candidate-complete.npy');assert np.array_equal(C,saved)
xs,ys,dx,dy=points(case);sd,_,_,_=masks(case,xs,ys,dx,dy);fg=np.zeros(sd.shape,bool)
for a,b,c,d in case['foreground']:fg|=(xs>=a)&(xs<=c)&(ys>=b)&(ys<=d)
ref=np.asarray(Image.open(inputs/'media-target.png'),np.float32)[y0:y1,x0:x1]/255;raw=np.load('/evidence/extended/geometric-playback-inferred/complete.npy');s=scores(C,ref,case);bs=scores(raw,ref,case);g={k:s[k]['rmse']<=bs[k]['rmse'] for k in ['train','held_blocks','all_glass','rim','outer_rim','interior']};g['ssim']=s['ssim']>=bs['ssim'];supp={}
for name,mask in [('foreground',fg),('exterior',sd>0)]:
 v=float(np.mean(((C-ref)[mask]*255)**2));old=float(np.mean(((raw-ref)[mask]*255)**2));g[name]=v<=old;supp[name]={'pixels':int(mask.sum()),'MSE':v,'unfiltered_MSE':old}
assert all(g.values());report={'accepted_complete_pixel_exact':True,'material_pixel_exact':True,'scores':s,'correct_supplemental':supp,'guards':g,'source_target_sha256':expected,'new_geometric_rays':0,'new_texture_queries':0,'new_candidates':0,'legacy_icon_material_dependency':True,'filter_is_not_a_geometry_change':True,'complete_sha256':sha(P/'blurriness/candidate-complete.npy'),'code_sha256':{f:sha(P/'code'/f) for f in ['geometric_optics.py','geometric_render.py','settled.py','reproduce.py']}}
out.write_text(json.dumps(report,indent=2)+'\n');print(json.dumps(report))
