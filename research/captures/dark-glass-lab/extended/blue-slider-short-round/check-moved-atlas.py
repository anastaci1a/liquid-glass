import copy,os,json,time
from pathlib import Path
import cv2,numpy as np
from PIL import Image
from clear_field import ClearField
from settled import render
os.umask(0o002);cv2.setNumThreads(1);D=Path('/evidence/extended/blue-slider-short-round');r=json.loads((D/'pass03-public-record.json').read_text());S=np.asarray(Image.open('/evidence/apple-matches/public-settled-replay/slider-source.png').convert('RGB')).astype(float)/255;f=ClearField(r['case'],r['body_recipe']);c=copy.deepcopy(r['case']);c['center'][0]+=17;c['crop'][0]+=17;c['crop'][2]+=17;t=time.monotonic();A=f.render(S,c['center']);fast=time.monotonic()-t;t=time.monotonic();B=render(S,c,r['body_recipe'],samples=4);slow=time.monotonic()-t;old=np.load(D/'generated-exterior/native-material.npy');v=dict(moved_native_exact=bool(np.array_equal(A,B)),max_difference=float(np.max(abs(A-B))),changed_from_static_pixels=int(np.count_nonzero(A!=old)),cached_seconds=fast,legacy_seconds=slow,offset_native_px=17,scope='Offline fixed-geometry cache equivalence at a distinct source position; not Android performance');(D/'atlas-moved-check.json').write_text(json.dumps(v,indent=2)+'\n');print(v,flush=True);assert v['moved_native_exact'] and v['changed_from_static_pixels']>0
