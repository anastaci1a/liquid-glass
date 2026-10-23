"""Recover export-only GIF cap failure using completed video; no optical rerender."""
import sys,os,json,hashlib,subprocess,importlib.util
from pathlib import Path
import numpy as np
from PIL import Image
R=Path('/evidence/extended/helper-toolbar-work/playback-format-round');O=R/'normalized';spec=importlib.util.spec_from_file_location('normalizer',R/'normalize.py');n=importlib.util.module_from_spec(spec);spec.loader.exec_module(n)
os.umask(0o002)
if (O/'verification.json').exists():raise RuntimeError('Already complete; do not duplicate')
rejected=O/'playback-settled-96-sierra-rejected.gif'
if not rejected.exists():(O/'playback-settled.gif').rename(rejected);(O/'palette.png').rename(O/'palette-96-sierra-rejected.png')
video=O/'playback-settled.mp4';gif=O/'playback-settled.gif';palette=O/'palette.png';trials=[]
for colors in [128,96,64,48]:
 subprocess.run(['ffmpeg','-v','error','-y','-threads','2','-filter_threads','1','-i',str(video),'-vf',f'palettegen=max_colors={colors}:stats_mode=diff','-frames:v','1',str(palette)],check=True)
 subprocess.run(['ffmpeg','-v','error','-y','-threads','2','-filter_complex_threads','1','-i',str(video),'-i',str(palette),'-lavfi','[0:v][1:v]paletteuse=dither=bayer:bayer_scale=4:diff_mode=rectangle','-loop','0','-gifflags','+transdiff',str(gif)],check=True);n.exact_gif_delays(gif);trials.append(dict(colors=colors,dither='bayer_scale4',bytes=gif.stat().st_size));print(trials[-1],flush=True)
 if gif.stat().st_size<10_000_000:break
assert gif.stat().st_size<10_000_000
n.save(O/'gif-cap-recovery.json',dict(reason='Sierra2_4a attempts256/192/128/96all exceeded10MB; final96retained, earlier sizes not recorded and not fabricated.',preserved_rejected_file=rejected.name,preserved_rejected_bytes=rejected.stat().st_size,bayer_trials=trials,new_scene_renders=0,video_reused_sha256=n.sha(video)))
files=[]
for f in [video,gif]:
 decoded=O/(f.suffix[1:]+'-decoded.framemd5');subprocess.run(['ffmpeg','-v','error','-threads','2','-i',str(f),'-f','framemd5','-y',str(decoded)],check=True);count=len([s for s in decoded.read_text().splitlines() if s and not s.startswith('#')]);assert count==90;pr=json.loads(subprocess.check_output(['ffprobe','-v','error','-count_frames','-show_streams','-show_format','-of','json',str(f)]));st=next(s for s in pr['streams'] if s['codec_type']=='video');assert int(st['nb_read_frames'])==90 and st['width']==1080 and st['height']==608 and float(pr['format']['duration'])==6
 files.append(dict(file=f.name,bytes=f.stat().st_size,sha256=n.sha(f),decoded_frames=count,width=1080,height=608,duration_seconds=6,probe=pr))
record=json.loads((R/'pass-03.json').read_text());frames=json.loads((O/'frames.json').read_text());p=record['recipe'];L=p['reference_length'];N=540;axis=(np.arange(N*2)+.5)/2-N/2;Y,X=np.meshgrid(axis,axis,indexing='ij');A,B=n.mapping(X/L,Y/L,p);lo=np.array([np.inf,np.inf]);hi=-lo
for f in frames:
 cx,cy=f['center'];sx=(A*L+cx).astype(np.float32);sy=(B*L+cy).astype(np.float32);lo=np.minimum(lo,[sx.min(),sy.min()]);hi=np.maximum(hi,[sx.max(),sy.max()])
margin=float(min(lo[0],lo[1],1919-hi[0],1079-hi[1])-3);assert margin>0
original=json.loads((R/'pass-03-verification.json').read_text());still=json.loads((O/'still-verification.json').read_text());source_unchanged=all(n.sha(n.I/name)==sha for name,sha in record['input_sha256'].items());assert source_unchanged
motion=dict(files=files,frames=90,fps=15,palette_colors=colors,dither='bayer_scale4',sampling='UNCHANGED existingmotion2x2; original4x4native scoring and savedmaterial unchanged; motionzero NOTasserted bitexact to4x4native',trajectory='Original round(960+340sin(2pi*t)),round(542+120sin(4pi*t)); t=i/90 matchesoriginalframe2i/180',source_bounds_min=lo.tolist(),source_bounds_max=hi.tolist(),whole_and_ALL_scored_domain='ALL1080x1080subpixel sourcecoordinates/moving540x540patch for ALL90poses, including unscored exterior; scoredrays subset. Finite sourceGaussian radius2+bilinear1 included.',source_margin_after_kernel_bilinear_native_px=margin,native_source_proof_inherited=original['domain'],source_limits='Finite image support is NOT independently observed reconstructed photograph/registration truth or Applegeneralization. No new scientificpass.',source_hashes_unchanged=source_unchanged,old_target_context_used=False,new_scene_renders_in_recovery=0)
n.save(O/'motion-verification.json',motion);n.save(O/'verification.json',dict(scope='Playback formatting/export ONLY; completed3passmodel unchanged; no new acceptedpass',recipe_sha256=n.sha(R/'pass-03.json'),input_hashes=record['input_sha256'],native_scoring_unchanged=True,new_fits=0,new_optical_still_renders=0,new_motion_frames=90,still=still,motion=motion));print('NORMALIZATION READY',flush=True)
