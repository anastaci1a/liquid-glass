"""Finish already-rendered export: GIF delay metadata only, no rerender/reencode."""
import os,json,hashlib,subprocess,shutil
from pathlib import Path
from PIL import Image,ImageSequence
os.umask(0o002)
R=Path('/evidence/extended/helper-toolbar-work/flower-next-round');D=R/'final-media'
def digest(p):return hashlib.sha256(Path(p).read_bytes()).hexdigest()
def save(n,x):(D/n).write_text(json.dumps(x,indent=2)+'\n')
gif=D/'motion.gif';raw=bytearray(gif.read_bytes());pos=13
if raw[10]&128:pos+=3*(2**((raw[10]&7)+1))
def blocks(p):
 while raw[p]:p+=1+raw[p]
 return p+1
entries=[]
while raw[pos]!=0x3b:
 tag=raw[pos];pos+=1
 if tag==0x21:
  label=raw[pos];pos+=1
  if label==0xf9:
   assert raw[pos]==4;entries.append((pos+2,int.from_bytes(raw[pos+2:pos+4],'little')))
  pos=blocks(pos)
 elif tag==0x2c:
  packed=raw[pos+8];pos+=9
  if packed&128:pos+=3*(2**((packed&7)+1))
  pos+=1;pos=blocks(pos)
 else:raise AssertionError((pos,tag))
assert len(entries)==90
before=sum(x[1] for x in entries);delta=600-before;assert delta in [0,1]
if delta:
 backup=D/'motion-initial-5990ms.gif';assert not backup.exists();shutil.copyfile(gif,backup);offset,delay=entries[-1];raw[offset:offset+2]=(delay+delta).to_bytes(2,'little');gif.write_bytes(raw)
else:backup=D/'motion-initial-5990ms.gif'
save('gif-timing-correction.json',dict(kind='GraphicControlExtension finalframe delay metadata only; compressed image and palette bytes unchanged',frames=90,original_duration_ms=before*10,new_duration_ms=6000,lastframe_added_ms=delta*10,prior_file=str(backup),no_render_or_encode=True))
# Re-decode only the metadata-modified GIF. Unchanged MP4 fully decoded in
# initial run before its final5990ms GIF assertion; do not repeat its rendering.
subprocess.run(['ffmpeg','-v','error','-threads','2','-i',str(gif),'-f','null','-'],check=True)
with Image.open(gif) as im:
 durations=[f.info.get('duration',0) for f in ImageSequence.Iterator(im)];assert len(durations)==90 and sum(durations)==6000 and im.size==(1080,1073)
files={}
for n in ['motion.mp4','motion.gif','comparison.png','original.png','reconstruction.png']:
 p=D/n;x=dict(bytes=p.stat().st_size,sha256=digest(p))
 if p.suffix in ['.mp4','.gif']:
  probe=json.loads(subprocess.check_output(['ffprobe','-v','error','-show_streams','-show_format','-of','json',str(p)]));x['probe']=probe;assert abs(float(probe['format']['duration'])-6)<.0001
  if n=='motion.mp4':assert probe['streams'][0]['nb_frames']=='90';assert probe['streams'][0]['width']==1080 and probe['streams'][0]['height']==1074
 else:x['size']=Image.open(p).size
 files[n]=x
assert files['motion.gif']['bytes']<10_000_000
support=json.loads((D/'source-support.json').read_text());zero=json.loads((D/'native-zero-control.json').read_text());assert support['passed'] and all(zero['checks'].values())
frames=[]
for i,p in enumerate(sorted((D/'frames').glob('*.png'))):frames.append(dict(frame=i,shift=support['poses'][i],sha256=digest(p)))
assert len(frames)==90
save('verification.json',dict(status='FINAL_ACCEPTED_PASS03_EXPORT_READY_PRIMARY_REVIEW',candidate_recipe_sha256=digest(R/'neutral-additive-round3/candidate-native.json'),native_zero_exact=zero,source_support='source-support.json',internal_raster=[1268,1260],final_content=[1080,1073],mp4_canvas=[1080,1074],mp4_bottom_padding=1,comparison=[2162,1137],caption_height=64,frames=90,fps=15,seconds=6,gif_duration_ms=6000,gif_palette=128,gif_dither='Bayer3',all_files_decode=True,decode_evidence='Initial export fully decoded both files and counted90frames before final timing assertion. Modified GIF fully decoded again here; MP4 unchanged.',frame_hashes=frames,files=files,method='Fresh original settled map/lighting/shade samples2 perOUTPUTpixel; fixed native source Gaussian, output post sigma scaled with raster. Geometry/light cached only; every moving source query reshaded/refiltered, NOT cached shading translation. Internal1268 downsampled1080; actual higher-resolution field/vector, no enlarged nativebitmap or4k export.',limitations=['Estimated affine sky, hidden observed0, model-domain confidence1 only.','Illustrative source translation ±20nativepx, no actual observational movie/paired/refraction/blur/dispersion validation.','Missing highlights/dark edge/glyph residuals remain; neutral encoded grading only.','No generated/copied target shadow, context, residual or input repair. Native scoring/epoch unchanged.','GIF encoder initially produced5990ms, preserved prior file. Final frame delay metadata +10ms produces exact6s; no pixels reencoded.']))
print(json.dumps(dict(status='READY',files={n:{k:v for k,v in x.items() if k!='probe'} for n,x in files.items()},native_zero=zero['checks'],source_support=support['passed'])),flush=True)
