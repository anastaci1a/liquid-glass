from pathlib import Path
import copy,hashlib,json,cv2,numpy as np
from extended_fit import Study
from neutral_rim import render
from settled import mapping
from vector_revision import composite
from publish import pair
cv2.setNumThreads(1)
D=Path('/evidence/extended/safari-search-common-material');assert not (D/'result.json').exists();R=Path('/evidence/extended/helper-toolbar-work/safari-magnifier-round');A=R/'foreground-control/proposed-a';s=Study(A);H=Path('/evidence/extended/safari-plus-shadow-round/pass-03');oldrec=json.loads((H/'search_advisory-recipe.json').read_text());old=np.load(H/'search_advisory-native.npz');assert np.array_equal(composite(s,oldrec['parameters'],old['material']),old['complete'])
base_masks=np.load(R/'foreground-control/proposed-baseline-native-arrays.npz');assert np.array_equal(base_masks['glass_mask'],s.valid) and np.array_equal(base_masks['rim_mask'],s.rim)
p=copy.deepcopy(json.loads(Path('/evidence/extended/helper-toolbar-work/safari-right-circle-round/neutral-additive-round3/candidate-native.json').read_text())['preset']);p['shadow']=copy.deepcopy(oldrec['parameters']['shadow']);L=min(s.case['half']);x0,y0,x1,y1=s.crop;known=cv2.imread(str(A/'known.png'),0)>0
for name,digest in s.case['source_sha256'].items():assert hashlib.sha256((A/name).read_bytes()).hexdigest()==digest
alpha=s.shape_coverage(p);assert np.array_equal(alpha,old['alpha']);sigma=p['source_sigma']*L;post=p['post_sigma']*L
def radius(sigma):
 a=np.zeros((501,501),np.float32);a[250,250]=1;b=cv2.GaussianBlur(a,(0,0),sigma);y,x=np.where(b!=0);return int(max(abs(y-250).max(),abs(x-250).max()))
sr,pr=radius(sigma),radius(post);safe=cv2.erode(known.astype(np.uint8),np.ones((2*sr+1,2*sr+1),np.uint8),borderType=cv2.BORDER_CONSTANT)>0;scope=cv2.dilate((alpha>0).astype(np.uint8),np.ones((2*pr+1,2*pr+1),np.uint8))>0;counts={};bounds=[np.inf,np.inf,-np.inf,-np.inf]
for name,mask in [('whole',alpha>0),('scored',s.valid),('post',scope)]:
 yy,xx=np.mgrid[y0:y1:.5,x0:x1:.5];X,Y=mapping((xx-.25-s.case['center'][0])/L,(yy-.25-s.case['center'][1])/L,p);m=np.repeat(np.repeat(mask,2,0),2,1);X=(X[m]*L+s.case['center'][0]).astype(np.float32);Y=(Y[m]*L+s.case['center'][1]).astype(np.float32);ix=np.floor(X).astype(int);iy=np.floor(Y).astype(int);good=safe[iy,ix]&safe[iy,ix+1]&safe[iy+1,ix]&safe[iy+1,ix+1];counts[name]=dict(rays=len(X),bad=int((~good).sum()));assert good.all();bounds=[min(bounds[0],float(X.min())),min(bounds[1],float(Y.min())),max(bounds[2],float(X.max())),max(bounds[3],float(Y.max()))]
proof=dict(passed=True,counts=counts,bounds=bounds,source_radius=sr,post_radius=pr,same_input=True,hidden_observed_fraction=0);(D/'source-proof-FIRST.json').write_text(json.dumps(proof,indent=2)+'\n');audit={};M=render(s.source,s.case,p,.125,.028,audit=audit);C=composite(s,p,M);np.savez_compressed(D/'candidate.npz',material=M,complete=C,alpha=alpha)
def score(M,C):
 q=s.scores(M);q['E']=float(np.sqrt(q['loss']))
 for n,m in [('glyph',base_masks['glyph_mask']),('exterior',(s.sd>0)&(s.sd<=.35)),('full_visible_exterior',s.sd>0)]:q[n]=dict(pixels=int(m.sum()),rmse=float(np.sqrt(np.mean(((C-s.target_crop)[m]*255)**2))))
 return q
before=score(old['material'],old['complete']);after=score(M,C);checks={n:after[n]['rmse']<=before[n]['rmse'] for n in ['glass','rim','held','interior','glyph','exterior','full_visible_exterior']};checks.update(E=after['E']<before['E'],ssim=after['ssim']>=before['ssim'],no_clipping=audit['clipped_channels']==0);result=dict(accepted_primary=False,qualifier=all(checks.values()),before=before,after=after,checks=checks,raw_audit=audit,preset=p,amplitude=.125,width=.028,source_proof=proof,actual_native_candidates=1,no_baseline_rerender=True,limits='Single prior transfer; smooth estimated source and parent geometry uncertainty. No new source/glyph/pose/mask, no fitting. No ray identification.');(D/'result.json').write_text(json.dumps(result,indent=2)+'\n');imgs=[cv2.resize(np.uint8(np.rint(np.clip(a,0,1)*255)),(430,440),interpolation=cv2.INTER_LANCZOS4)for a in [s.target_crop,C]];pair(*imgs,('Apple source','Shared circle prior'),font_size=28).save(D/'comparison.png');print(json.dumps({k:v for k,v in result.items()if k not in ['preset','source_proof']}))
