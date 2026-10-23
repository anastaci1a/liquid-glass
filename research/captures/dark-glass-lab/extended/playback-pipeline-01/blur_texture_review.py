from pathlib import Path
import json,numpy as np,cv2
from PIL import Image,ImageDraw
D=Path('/evidence/extended/playback-pipeline-01/blurriness');A=Path('/evidence/apple-matches/public-settled-replay');T=np.asarray(Image.open(A/'media-target.png'),np.float32)/255;old=np.load('/evidence/extended/geometric-playback-inferred/complete.npy');rows=json.loads((D/'ledger.json').read_text());box=[900,690,1040,755];a,b,c,d=box
# Fixed crop, constant mean removed by bandpass; no fitted tone response.
def detail(im):
 lum=im@np.array([.2126,.7152,.0722],np.float32);band=cv2.GaussianBlur(lum,(0,0),.5)-cv2.GaussianBlur(lum,(0,0),3.);band=band[8:-8,8:-8]*255;return {'bandpass_RMS':float(np.sqrt(np.mean(band**2))),'bandpass_p95':float(np.percentile(abs(band),95))}
ref=detail(T[b:d,a:c]);out={'texture_box':box,'analysis_filter_not_optical_render':True,'reference':ref,'zero':detail(old[b-220:d-220,a-620:c-620]),'trials':[]}
# This gallery is just reformatting saved native arrays, no sampling/filter re-evaluation.
items=[(T[b:d,a:c],'Apple'),(old[b-220:d-220,a-620:c-620],'G05 no optical blur')]
for row in rows:
 C=np.load(D/f'trial-{row["trial"]:02d}-complete.npy');v=C[b-220:d-220,a-620:c-620];dd=detail(v);dd.update(source=row['source_sigma_native_px'],output=row['output_sigma_native_px'],trial=row['trial']);out['trials'].append(dd)
 if row['source_sigma_native_px']==0 and row['output_sigma_native_px'] in [1.,1.5,1.6,1.75,2.,2.5]:items.append((v,f'Output sigma {row["output_sigma_native_px"]}px'))
canvas=Image.new('RGB',(892,4*264),'white');draw=ImageDraw.Draw(canvas)
for k,(v,label) in enumerate(items):
 left=(k%2)*446;top=(k//2)*264;im=Image.fromarray(np.uint8(np.rint(np.clip(v,0,1)*255))).resize((440,204),Image.Resampling.NEAREST);canvas.paste(im,(left,top+50));draw.text((left+5,top+12),label,fill='black')
canvas.save(D/'center-texture-options.png');(D/'texture-analysis.json').write_text(json.dumps(out,indent=2)+'\n');print(json.dumps(out))
