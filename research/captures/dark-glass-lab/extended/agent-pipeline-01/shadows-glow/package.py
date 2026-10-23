from pathlib import Path
import sys,json,time,numpy as np,cv2,csv
from PIL import Image,ImageDraw
P=Path('/evidence/extended/agent-pipeline-01');O=P/'shadows-glow';sys.path.insert(0,str(P/'code'))
from extended_fit import Study
proto=json.loads((O/'protocol.json').read_text());deadline=__import__('datetime').datetime.fromisoformat(proto['deadline'].replace('Z','+00:00')).timestamp();assert time.time()<deadline
out={}
def pic(im):
 valid=np.isfinite(im).all(2);return Image.fromarray(np.dstack([np.uint8(np.rint(np.clip(np.nan_to_num(im),0,1)*255)),valid.astype(np.uint8)*255]),'RGBA')
for key in ['a','b']:
 s=Study(P/f'inputs/{key}');x0,y0,_,_=s.crop;A=np.load(P/'color-grading'/f'{key}-step0.5-complete.npy');B=np.load(O/f'{key}-trial0-complete.npy');alpha=np.load(P/'blurriness'/f'{key}-coverage.npy');masks=np.load(P/f'historical-{key}-masks.npz');partial=masks['glass']&(alpha<1);rows=[]
 for y,x in np.argwhere(partial):
  t=s.target_crop[y,x];a=A[y,x];b=B[y,x];rows.append([int(x+x0),int(y+y0),float(alpha[y,x]),*t.tolist(),*a.tolist(),*b.tolist(),float(np.sqrt(np.mean(((a-t)*255)**2))),float(np.sqrt(np.mean(((b-t)*255)**2)))])
 with (O/f'{key}-16partial-glass.csv').open('w') as f:
  w=csv.writer(f);w.writerow(['x','y','coverage','targetR','targetG','targetB','beforeR','beforeG','beforeB','afterR','afterG','afterB','RMSE_before','RMSE_after']);w.writerows(rows)
 H,W=s.valid.shape;Y,X=np.mgrid[y0:y0+H,x0:x0+W];m=(alpha==0)&np.isfinite(A).all(2);co={'all_known_outside':m,'above':m&(Y<s.case['center'][1]-s.L),'below':m&(Y>s.case['center'][1]+s.L),'left':m&(X<s.case['center'][0]-s.case['half'][0]),'right':m&(X>s.case['center'][0]+s.case['half'][0])};out[key]={}
 for name,mask in co.items():
  ea=(A-s.target_crop)[mask]*255;eb=(B-s.target_crop)[mask]*255;out[key][name]={'pixels':int(mask.sum()),'before_rmse':float(np.sqrt(np.mean(ea*ea))),'after_rmse':float(np.sqrt(np.mean(eb*eb)))}
 panels=[s.target_crop,A,B];labels=['Apple','Incumbent physical pipeline, shadow0','REJECTED prior shadow: B original glass guards fail']
 sheet=Image.new('RGBA',(W,(H+42)*3),'white');draw=ImageDraw.Draw(sheet)
 for i,(im,label) in enumerate(zip(panels,labels)):sheet.paste(pic(im),(0,i*(H+42)+42));draw.text((7,i*(H+42)+10),label,fill='black')
 sheet.save(O/f'{key}-comparison.png');a,b,c,d=[310,320,376,508];tile=Image.new('RGBA',(220*3,(d-b)*2+50),'white');draw=ImageDraw.Draw(tile)
 for i,(im,label) in enumerate(zip(panels,['Apple','Incumbent shadow0','REJECTED shadow'])):
  crop=pic(im[b-y0:d-y0,a-x0:c-x0]).resize(((c-a)*2,(d-b)*2),Image.Resampling.NEAREST);tile.paste(crop,(i*220,50));draw.text((i*220+4,10),label,fill='black')
 tile.save(O/f'{key}-left-cap-crop.png')
(O/'advisory-exterior-before-after.json').write_text(json.dumps(out,indent=2));print(json.dumps(out))
