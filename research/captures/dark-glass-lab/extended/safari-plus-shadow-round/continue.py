"""One source-limited exterior proposal; cached native material stays frozen."""
from pathlib import Path
import sys,os,json,copy,hashlib
import cv2,numpy as np
from PIL import Image
sys.path.insert(0,'/workspace/docs/liquid-glass/experiments/reconstruction')
from extended_fit import Study
from vector_revision import composite
from publish import pair
os.umask(0o002);cv2.setNumThreads(1)
import argparse
ap=argparse.ArgumentParser();ap.add_argument('--number',type=int,required=True);args=ap.parse_args();assert args.number in [2,3]
ROOT=Path('/evidence/extended/safari-plus-shadow-round');PRE=ROOT/f'pass-{args.number-1:02d}';assert(PRE/'accepted.json').exists();O=ROOT/f'pass-{args.number:02d}';assert not O.exists();O.mkdir()
cases=[('plus',Path('/evidence/extended/safari-plus-source-round'),'b-proposed','unfitted-native-arrays.npz','transfer-recipe.json'),('search_advisory',Path('/evidence/extended/helper-toolbar-work/safari-magnifier-round'),'foreground-control/proposed-a','foreground-control/proposed-baseline-native-arrays.npz','foreground-control/proposed-baseline-recipe.json')]
report={'scope':'SINGLE plus generated-exterior progress only; magnifier unchanged optical advisory guard, not paired-optics validation','verified_passes':0,'decision':'PENDING independent peer replay/visual review','delta_opacity':-.005,'unchanged':'Source,pose,glyph,map,all material and filtering; cached native M reused','observations':{}}
for name,R,folder,arrays,recipe in cases:
 s=Study(R/folder);a=np.load(PRE/(name+'-native.npz'));base=np.load(R/arrays);rec=json.loads((PRE/(name+'-recipe.json')).read_text());p=copy.deepcopy(rec['parameters']);old=composite(s,p,a['material']);assert np.array_equal(old,a['complete']);p['shadow']['opacity']-=.005;C=composite(s,p,a['material']);near=(s.sd>0)&(s.sd<=.35);full=s.sd>0;glyph=base['glyph_mask'];deferr=lambda v,m:float(np.sqrt(np.mean(((v-s.target_crop)[m]*255)**2)))
 olderr={k:deferr(old,m) for k,m in [('near',near),('full',full),('glyph',glyph)]};err={k:deferr(C,m) for k,m in [('near',near),('full',full),('glyph',glyph)]}
 check={'baseline_complete_exact':True,'native_material_reused':True,'all_original_glass_pixels_exact':bool(np.array_equal(C[s.valid],old[s.valid])),'glyph_pixels_exact':bool(np.array_equal(C[glyph],old[glyph])),'near_nonreg':err['near']<=olderr['near'],'full_nonreg':err['full']<=olderr['full'],'measurable_exterior_improvement':err['near']<olderr['near']}
 assert all(check.values()),check
 scores=s.scores(a['material']);scores['E']=float(np.sqrt(scores['loss']));item={'before':olderr,'after':err,'native_optical_scores_unchanged':scores,'checks':check,'opacity_before':rec['parameters']['shadow']['opacity'],'opacity_after':p['shadow']['opacity']};report['observations'][name]=item
 target=np.uint8(np.rint(np.clip(s.target_crop,0,1)*255));rgb=np.uint8(np.rint(np.clip(C,0,1)*255));w=2*rgb.shape[1];h=2*rgb.shape[0];pair(cv2.resize(target,(w,h),interpolation=cv2.INTER_LANCZOS4),cv2.resize(rgb,(w,h),interpolation=cv2.INTER_LANCZOS4),('Apple source','Generated shadow proposal'),font_size=24).save(O/(name+'-comparison.png'));np.savez_compressed(O/(name+'-native.npz'),complete=C,material=a['material'],alpha=a['alpha']);rec['parameters']=p;rec['scope']=report['scope'];(O/(name+'-recipe.json')).write_text(json.dumps(rec,indent=2)+'\n')
(O/'proposal.json').write_text(json.dumps(report,indent=2)+'\n');print(json.dumps(report))
