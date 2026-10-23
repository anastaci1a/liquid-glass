import sys,json
sys.path.insert(0,'/workspace/docs/liquid-glass/experiments/reconstruction')
from reproduce import *
from publish import compose,pair
from PIL import Image
p=Path('/evidence/apple-matches');case=CASES['regular'];source,target,_,_=prepare(p,'regular',case)
x0,y0,x1,y1=case['crop'];crop=target[y0:y1,x0:x1];xs,ys,x,y=points(case);sd,train,held,valid=masks(case,xs,ys,x,y)
rng=np.random.default_rng(222);ids=np.flatnonzero(train);rng.shuffle(ids);ids=ids[:6500]
light=illumination(x,y,case['half'],case['radius'],12)
weights=np.where(-sd.flat[ids]<min(case['half'])*.2,1.3,1.)
old=json.loads((p/'fits-final/regular-cap.json').read_text())
for i,(h,g,b,sigma,trans) in enumerate([(.678,.807,.472,8,30),(.678,.807,.472,4,30),(.678,.807,.472,12,30),(.678,.807,.472,8,12),(.678,.807,.472,8,60),(.678,.807,.472,0,30),(.678,.807,.472,8,0),(.4,.8,.35,8,30),(.8,.8,.5,8,30),(.6,1.2,.5,8,30)]):
 case['blur_transition']=trans
 f=dict(model='cap',parameters=dict(height=h,gap=g,band=b,ior=1.33),sigma=sigma,rim_width=12,material=[1,1,1]+[0]*20)
 sample=render(source,case,f)
 co,invalid=fit_material(sample.reshape(-1,3)[ids],light.reshape(-1,15)[ids],crop.reshape(-1,3)[ids],weights)
 f['material']=co.tolist();out=render(source,case,f).astype(np.float32);sc=scores(out,crop,case)
 print(i,h,g,b,sigma,trans,round(sc['all_glass']['rmse'],3),round(sc['rim']['rmse'],3),flush=True)
 result=compose('regular',case,np.uint8(target*255),np.uint8(out*255))
 pair(np.uint8(crop*255),result[y0:y1,x0:x1],('Apple',f'cap {i}')).save(p/f'probe-{i}.png')
