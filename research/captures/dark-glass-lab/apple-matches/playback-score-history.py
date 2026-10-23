"""Re-score frozen playback images on one native mask, not fit-time losses."""
import sys,json
from pathlib import Path
sys.path.insert(0,'/workspace/docs/liquid-glass/experiments/reconstruction')
import cv2,numpy as np
from PIL import Image
from reproduce import CASES,scores

root=Path('/evidence/apple-matches');out=root/'playback-history'
case=CASES['media'];x0,y0,x1,y1=case['crop'];W=x1-x0;H=y1-y0
read=lambda p:np.array(Image.open(p).convert('RGB'))
fulltarget=read(root/'curvature-contour/media-target.png');target=fulltarget[y0:y1,x0:x1].astype(np.float32)/255
alpha=np.array(Image.open(root/'review-pass-02/06-white-icon-mask.png'))/255
inside=cv2.erode(np.uint8(alpha>.99),np.ones((7,7),np.uint8))>0
iconref=fulltarget[420:675,870:1095].astype(np.float32)/255

def pair(p):
    photo=read(p);assert photo.shape[1]==2*W+2
    # Native left reference crop establishes the header offset independently
    # of old publishing-font choices; verify the reference pixels exactly.
    candidates=[]
    for y in range(photo.shape[0]-H+1):
        delta=photo[y:y+H:8,:W:8].astype(float)/255-target[::8,::8]
        candidates.append(float(np.mean(delta**2)))
    y=int(np.argmin(candidates));reference_error=float(np.max(abs(photo[y:y+H,:W].astype(np.float32)/255-target))*255)
    assert reference_error==0,(p,reference_error)
    return photo[y:y+H,W+2:W*2+2],dict(path=str(p),header_px=y,reference_max_difference_255=reference_error)

def icon_score(photocrop):
    photo=photocrop.astype(np.float32)/255
    return float(np.sqrt(np.mean((photo[inside]-iconref[inside])**2))*255)

rows=[]
def add(label,image,evidence,independent_icon=True,iconcrop=None,notes=''):
    s=scores(image.astype(np.float32)/255,target,case)
    icon=icon_score(iconcrop if iconcrop is not None else image[420-y0:675-y0,870-x0:1095-x0])if independent_icon else None
    rows.append(dict(stage=label,glass_rmse=s['all_glass']['rmse'],rim_rmse=s['rim']['rmse'],interior_rmse=s['interior']['rmse'],SSIM=s['ssim'],icon_rmse=icon,evidence=evidence,notes=notes))

for commit,label,notes in [('7a8061b','First published HD fit','Early source/filtering/material setup; old nominal score10.17. Its archived exported image is re-scored here.'),('b1636bb','Corrected published HD fit','The displayed cap reconstruction, not the lower-error unshown spline candidate. Old nominal score8.60.')]:
    image,ev=pair(out/f'{commit}-match.png');ev['commit']=commit;add(label,image,ev,False,notes=notes)
image,ev=pair(out/'pass01-match.png');add('Pass 01',image,ev,False,notes='Smooth-front/flat-exit body. Apple icon interior copied on both sides; no independent icon score.')
trial=read(out/'pass02-icon.png')[78:588,1356:1806][::2,::2]
add('Pass 02',image,dict(path=str(out/'pass02-icon.png'),lens='unchanged from pass01'),True,trial,'Focused crops and first white-mask icon response; glass unchanged.')
add('Pass 03',image,dict(lens='unchanged from pass02'),True,trial,'Toolbar/slider geometry exploration; no new full playback fit.')
image,ev=pair(out/'pass04-match.png');add('Pass 04',image,ev,True,notes='Single-turn radial map and independent-channel icon response.')
for name,folder,file,notes in [('Pass 05','review-pass05-playback','combined-full.png','Displayed combined/lowest-map-loss option:1.5x tail, glass sigma2, shared monotone icon.'),('Pass 06','review-pass06-playback','selected-full.png','Displayed example:4.5x tail, glass sigma1.6, taper0.5, saturation0.2, final icon sigma2.')]:
    p=root/folder/'renders'/file;full=read(p);add(name,full[y0:y1,x0:x1],dict(path=str(p)),notes=notes)
p=root/'playback-settled/playback-reference.png';full=read(p);add('Settled final',full[y0:y1,x0:x1],dict(path=str(p)),notes='Owner choice:4.5x/gain1; glass sigma1.5, taper0.5, dark saturation0.2, final icon sigma3. Blur lengths proportional to size.')
report=dict(method='All rows re-score frozen 8-bit PNG output against exactly the same native Apple crop, current glass mask and eroded icon mask. No re-fitting. Glass excludes icon/exterior; icon score only where independently rendered. Lower RMSE is better; higher SSIM is better. Not percentage similarity.',mask=dict(glass_pixels=134483,icon_interior_pixels=int(inside.sum())),rows=rows,unscored_commits=[dict(commit='8d8015c',work='Context/evidence audit'),dict(commit='754c7c8',work='Lab presets and independent controls'),dict(commit='611e166',work='Pressure/depth motion model'),dict(commit='2257181',work='Portable equations / outer-rim correction')],other_commits=[dict(commit='b6c56fe',work='Curvature/dispersion hypotheses; public comparison image not updated. Private pass01 scored separately.'),dict(commit='99d182b',work='Slider input correction; no new playback image.'),dict(commit='2c955cb',work='Geometry/path verification; no separate accepted playback image.'),dict(commit='610a589',work='Radial-tail/icon equations; private pass05 scored separately.'),dict(commit='e42fc48',work='Proportional units / highlight taper; private pass06 scored separately.')],limits=['Common output scoring removes score-method/mask differences but does not remove differences in how earlier inputs were reconstructed.','Early icons copied from reference are deliberately not counted as zero-error icon success.','Pass02/03 glass unchanged; source-image identification and title offsets recorded.','Unscored lab/physics work has no measured Apple-reference reconstruction score; none is invented.','Same-frame pixel calibration, not independent-scene or temporal validation. SSIM is not a literal matching percentage.'])
(out/'progression.json').write_text(json.dumps(report,indent=2)+'\n')
for row in rows:print(row['stage'],round(row['glass_rmse'],3),round(row['rim_rmse'],3),round(row['SSIM'],4),None if row['icon_rmse']is None else round(row['icon_rmse'],3))
