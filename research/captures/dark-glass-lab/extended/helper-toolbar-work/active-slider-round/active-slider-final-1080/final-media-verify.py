"""Verify completed approved-helper videos; encode15fpsGIFonly if needed."""
from pathlib import Path
from PIL import Image,ImageSequence
import subprocess,json,hashlib,os
R=Path('/evidence/extended/helper-toolbar-work/active-slider-round/active-slider-final-1080')
sha=lambda p:hashlib.sha256(p.read_bytes()).hexdigest()
def frames(path):
 with Image.open(path) as im:
  data=[dict(duration_ms=f.info.get('duration',0),sha256=hashlib.sha256(f.convert('RGBA').tobytes()).hexdigest()) for f in ImageSequence.Iterator(im)];return list(im.size),data

def main():
 os.umask(0o002)
 if (R/'export-summary.json').exists():print('Finalmedia verification complete; no repeat');return
 recipe=json.loads((R/'recipe.json').read_text());results=[]
 for n in ['a','b']:
  F=R/n/'final';helper=json.loads((F/'verification.json').read_text());destination=F/'motion-6s.gif'
  if (F/'final-media-verification.json').exists():results.append(json.loads((F/'final-media-verification.json').read_text()));continue
  assert not destination.exists(),'Inspect partially verified preferred GIF; never overwrite'
  assert helper['frames']==90 and helper['fps']==15 and helper['output_size'][0]==1080
  video=F/'motion.mp4';source=F/'motion.gif';commands=[];colors=helper['gif']['palette_colors'];dither=helper['gif']['dither'];size,original=frames(source)
  if len(original)!=90 or helper['gif']['fps']!=15:
   for colors in [256,128,96,64]:
    palette=F/f'palette-15fps-{colors}.png';source=F/f'motion-15fps-{colors}.gif';dither='none'
    assert not palette.exists() and not source.exists(),'Inspect partial reencoding before retry'
    cmds=[['ffmpeg','-v','error','-threads','2','-filter_threads','1','-y','-i',str(video),'-vf',f'fps=15,palettegen=max_colors={colors}:stats_mode=full','-frames:v','1',str(palette)],['ffmpeg','-v','error','-threads','2','-filter_complex_threads','1','-y','-i',str(video),'-i',str(palette),'-lavfi','fps=15[x];[x][1:v]paletteuse=dither=none:diff_mode=rectangle','-loop','0','-gifflags','+transdiff',str(source)]]
    for cmd in cmds:subprocess.run(cmd,check=True);commands.append(cmd)
    if source.stat().st_size<10_000_000:break
   assert source.stat().st_size<10_000_000
  size,original=frames(source);assert len(original)==90
  cmd=['ffmpeg','-v','error','-threads','2','-y','-i',str(source),'-c:v','copy','-loop','0','-final_delay','7',str(destination)];subprocess.run(cmd,check=True);commands.append(cmd)
  finalsize,corrected=frames(destination);assert size==finalsize==helper['output_size'];assert len(corrected)==90;assert sum(v['duration_ms'] for v in corrected)==6000;assert [v['sha256'] for v in original]==[v['sha256'] for v in corrected];assert destination.stat().st_size<10_000_000
  probe=json.loads(subprocess.check_output(['ffprobe','-v','error','-select_streams','v:0','-show_entries','stream=width,height,nb_frames,r_frame_rate:format=duration','-of','json',str(video)]));v=probe['streams'][0];assert [v['width'],v['height']]==helper['output_size'] and v['nb_frames']=='90' and v['r_frame_rate']=='15/1' and float(probe['format']['duration'])==6
  assert sha(video)==helper['files']['motion.mp4']['sha256'];assert all(sha(Path(row['path']))==row['sha256'] for row in recipe['input_sha256'][n].values())
  result=dict(reference=n,mp4=dict(file='motion.mp4',bytes=video.stat().st_size,sha256=sha(video),probe=probe,decode='Approved helper full decode+hash passed; preserved'),gif=dict(file='motion-6s.gif',bytes=destination.stat().st_size,sha256=sha(destination),output_size=size,frames=90,duration_ms=6000,average_fps=15,palette_colors=colors,dither=dither,timing_source=str(source),all90decoded_RGBAframes_identical_to_timing_source=True,frame_hashes=corrected),commands=commands,source_estimate_limits=recipe['source_limits'],helper_verification=helper,frozen_inputs_unchanged=True,limits='Definedsource-margin-capped illustrative animation on frozenMODELEDhiddenRGB/observed0. Native sourceproof notcontinuous/fullmovinghighresconfidence proof. Existingfixedglobalmaterial/source-mean law reevaluated eachframe, no new coefficients/source repair or scoreepoch.')
  (F/'final-media-verification.json').write_text(json.dumps(result,indent=2)+'\n');results.append(result);print('FINAL',n,result['mp4']['bytes'],result['gif']['bytes'],size,flush=True)
 assert all(sha(R/'code'/name)==digest for name,digest in recipe['code_sha256'].items())
 (R/'export-summary.json').write_text(json.dumps(dict(exports=results,accepted_round_count=3,frozen_code_and_inputs_unchanged=True,preferred='a/b final/motion.mp4 + motion-6s.gif',source_epoch_unchanged=True),indent=2)+'\n')
if __name__=='__main__':main()
