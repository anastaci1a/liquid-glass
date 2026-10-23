"""Select saved incident filtering; presentation only, no optical evaluation."""
from pathlib import Path
import datetime,hashlib,json,shutil
import numpy as np
from PIL import Image,ImageDraw,ImageFont
root=Path(__file__).resolve().parents[3];out=Path(__file__).parent
p=json.loads((out/'protocol.json').read_text())
assert datetime.datetime.now(datetime.timezone.utc)<datetime.datetime.fromisoformat(p['deadline'])
assert not (out/'selection.json').exists()
old=root/'guide/assets/geometric-playback-primary.png'
shutil.copy2(old,out/'historical-output-comparison.png')
source=root/'research/experiments/clear-play-02/candidate.npz'
a=np.load(source)['complete'];reference=Image.open(root/'.evidence-working/clear-play-02/dark-glass-lab/apple-matches/public-settled-replay/media-target.png').convert('RGB').crop((620,220,1300,875))
assert a.shape==(655,680,3) and np.isfinite(a).all()
canvas=Image.new('RGB',(1362,719),'white');draw=ImageDraw.Draw(canvas);font=ImageFont.load_default(size=18)
canvas.paste(reference,(0,64));canvas.paste(Image.fromarray(np.uint8(np.rint(np.clip(a,0,1)*255))),(682,64))
draw.text((12,20),'Apple reference',font=font,fill='black');draw.text((694,20),'Incident blur 1.7 px; incomplete model',font=font,fill='black')
canvas.save(old)
r=dict(status='MODEL_CONVENTION_SELECTION_NOT_NUMERICAL_ACCEPTANCE',finished_at=datetime.datetime.now(datetime.timezone.utc).isoformat(),selected_source_sigma_native_pixels=1.7,selected_output_sigma_native_pixels=0,new_rays=0,new_RGB_queries=0,new_optical_renders=0,new_fits=0,source_artifact=str(source.relative_to(root)),source_sha256=hashlib.sha256(source.read_bytes()).hexdigest(),image_sha256=hashlib.sha256(old.read_bytes()).hexdigest(),proof='../clear-play-02/source-proof.json',independent_replay='../clear-play-02/verification.json',guard_result='../clear-play-02/result.json',limits=['Original strict guards still reject this as a numerical improvement.','Sharper compressed texture does not repair outline illumination or feature crossing.','Historical output-filter result is preserved separately.'])
(out/'selection.json').write_text(json.dumps(r,indent=2)+'\n')
print(json.dumps(r))
