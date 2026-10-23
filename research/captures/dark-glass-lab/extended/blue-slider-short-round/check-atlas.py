import os,json,sys,time
from pathlib import Path
import numpy as np,cv2
from PIL import Image
from clear_field import ClearField
os.umask(0o002);cv2.setNumThreads(1);D=Path('/evidence/extended/blue-slider-short-round');r=json.loads((D/'pass03-public-record.json').read_text());S=np.asarray(Image.open('/evidence/apple-matches/public-settled-replay/slider-source.png').convert('RGB')).astype(float)/255;t=time.monotonic();f=ClearField(r['case'],r['body_recipe'],samples=4);prepared=time.monotonic()-t;t=time.monotonic();M=f.render(S);elapsed=time.monotonic()-t;old=np.load(D/'generated-exterior/native-material.npy');err=float(np.max(np.abs(M-old)));record=dict(native_exact=bool(np.array_equal(M,old)),max_difference=err,prepare_seconds=prepared,frame_seconds=elapsed,contributing_subrays=len(f.active),full_pixel_subrays=int(f.inside.size),source_model_unchanged=True);(D/'atlas-native-check.json').write_text(json.dumps(record,indent=2)+'\n');np.save(D/'atlas-native-material.npy',M);print(record,flush=True);assert record['native_exact']
