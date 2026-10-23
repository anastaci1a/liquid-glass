import sys,json,hashlib,shutil
from pathlib import Path
sys.path.insert(0,'/workspace/docs/liquid-glass/experiments/reconstruction')
import cv2,numpy as np
from PIL import Image
from extended_fit import Study
from vector_revision import composite
from source_support import masks
from motion_support import complete
from preview_size import dimensions
from publish import pair
cv2.setNumThreads(1)
root=Path('/evidence/extended');public=Path('/workspace/docs/liquid-glass/experiments/reconstruction')
def packet(name,inputs,native,verify,large,cache):
 out=root/(name+'-primary-publish');out.mkdir(exist_ok=True)
 record={**native,'case_sha256':{},'vector_sha256':{},'large':large,'parameter_units':'sigma/post_sigma in source pixels; all shape/map coefficients normalized by study.L, the source short half-size. Scale pixel widths with L when changing source resolution.','presentation':'Unknown unscored exterior extended by nearest defined source RGB only. No reference shadow copied, no scoring/input change.'}
 for i,obs in enumerate(['a','b']):
  study=Study(inputs/obs);record['case_sha256'][obs]=hashlib.sha256(json.dumps(study.case,sort_keys=True).encode()).hexdigest();record['vector_sha256'][obs]={layer['vector_asset']:hashlib.sha256((study.folder/layer['vector_asset']).read_bytes()).hexdigest() for layer in study.case['foreground_layers']}
  M=np.load(cache(i));scale=round(M.shape[1]/(study.crop[2]-study.crop[0]));defined,_=masks(study);completed=complete(study,defined);assert study.exterior_source is None
  before=study.source.copy();im=composite(study,record['parameters'],M,scale,completed);assert np.array_equal(before,study.source)
  w,h=dimensions(study.crop[2]-study.crop[0],study.crop[3]-study.crop[1],large=large);rgb=cv2.resize(np.uint8(np.rint(np.clip(im,0,1)*255)),(w,h),interpolation=cv2.INTER_AREA);target=cv2.resize(np.uint8(np.rint(study.target_crop*255)),(w,h),interpolation=cv2.INTER_LANCZOS4)
  Image.fromarray(rgb).save(out/(obs+'-render.png'));pair(target,rgb,('Apple source','Reconstruction'),font_size=24).save(out/(obs+'-comparison.png'))
  # Completion cannot affect any scored pixel: original native glass coverage is1 on valid mask.
  original=composite(study,record['parameters'],M,scale)
  valid=cv2.resize(study.valid.astype(np.uint8),(M.shape[1],M.shape[0]),interpolation=cv2.INTER_NEAREST)>0
  assert np.array_equal(im[valid],original[valid]),'Presentation completion changed measured pixels'
 record.pop('cases',None);record.pop('scores',None)
 (out/'pass-01.json').write_text(json.dumps(record,indent=2)+'\n');shutil.copyfile(verify,out/'pass-01-verification.json')
 print(name,'packaged',flush=True)
nav=root/'helper-toolbar-work/navigation-round';packet('navigation-pass02',nav/'short-outer-profile',json.loads((nav/'rim-width-neighborhood/candidate-native.json').read_text()),root/'navigation-pass02-primary-review/accepted-verification.json',True,lambda i:nav/f'rim-width-neighborhood/trial0-ref{i}-material.npy')
