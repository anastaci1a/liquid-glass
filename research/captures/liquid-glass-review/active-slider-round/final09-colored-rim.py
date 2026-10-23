"""Final09 advisory crops from saved native06/09 arrays; NO optical renderer."""
import json,os,hashlib,sys,math
from pathlib import Path
import numpy as np
from PIL import Image,ImageDraw,ImageFont
R=Path('/evidence/extended/helper-toolbar-work/active-slider-round');O=R/'final09-colored-rim';sys.path.insert(0,str(R/'code'))
from preview_size import dimensions
FONT='/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf'
def sha(p):return hashlib.sha256(p.read_bytes()).hexdigest()
def rgb(a):return Image.fromarray(np.rint(np.clip(a,0,1)*255).astype(np.uint8))
def metrics(T,C,normalized,box):
 a,b,c,d=box;e=(C[b:d,a:c].astype(float)-T[b:d,a:c].astype(float));l=np.array([.2126,.7152,.0722]);L=e@l;ch=e-L[...,None]
 return dict(bounds_normalized=normalized,bounds_pixels=box,rgb_rmse_255=float(np.sqrt(np.mean(e**2))*255),channel_rmse_255=(np.sqrt(np.mean(e**2,axis=(0,1)))*255).tolist(),luma_rmse_255=float(np.sqrt(np.mean(L**2))*255),chroma_rmse_255=float(np.sqrt(np.mean(ch**2))*255),mean_signed_rgb_255=(e.mean((0,1))*255).tolist(),pixel_error_p95_255=float(np.quantile(np.sqrt(np.mean(e**2,axis=2)),.95)*255))
def pair(left,right,labels):
 w,h=left.size;bar=46;out=Image.new('RGB',(2*w+4,h+bar),'#171a20');d=ImageDraw.Draw(out);f=ImageFont.truetype(FONT,20)
 for i,(im,label) in enumerate(zip([left,right],labels)):out.paste(im,(i*(w+4),bar));d.text((i*(w+4)+10,10),label,font=f,fill='white')
 return out

def main():
 os.umask(0o002)
 if (O/'verification.json').exists():print('Advisory exports complete,no repeat');return
 if O.exists():raise RuntimeError('Inspect partial exports; never overwrite evidence')
 O.mkdir();definition=R/'final09-crop-reference.json';reference=json.loads(definition.read_text());inputs={str(definition):sha(definition)};observations=[];sheetrows=[];files={};regressions=[]
 for i,label in enumerate(['A','B']):
  before=R/f'ref{i}-baseline-complete.npy';after=R/f'pass08-ambient-neutral/shared-nullspace/ref{i}-complete.npy';case=json.loads((R/label.lower()/'case.json').read_text());targetpath=R/label.lower()/'target.png'
  with Image.open(targetpath) as im:target=np.asarray(im.convert('RGB')).astype(np.float32)/255
  x0,y0,x1,y1=case['crop'];T=target[y0:y1,x0:x1];B=np.load(before);C=np.load(after);assert T.shape==B.shape==C.shape
  for p in [before,after,targetpath]:inputs[str(p)]=sha(p)
  H,W=T.shape[:2];assert dimensions(W,H,large=False)==(W,H),'Nativewiderthan720cap remainsnative'
  old={};new={};changes={}
  definition_rows=reference['observations'][i]['states'][-1];assert reference['observations'][i]['observation']==label
  for name,v in definition_rows.items():
   normalized=v['bounds_normalized'];box=v['bounds_pixels'];assert [round(normalized[k]*[W,H,W,H][k]) for k in range(4)]==box,'Frozen normalized/native rectangle mismatch'
   # Check both historical states used these same native rectangles.
   assert all(state[name]['bounds_pixels']==box and state[name]['bounds_normalized']==normalized for state in reference['observations'][i]['states'])
   old[name]=metrics(T,B,normalized,box);new[name]=metrics(T,C,normalized,box)
   changes[name]={k:new[name][k]-old[name][k] for k in ['rgb_rmse_255','luma_rmse_255','chroma_rmse_255']}
   if any(x>0 for x in changes[name].values()):regressions.append(dict(observation=label,crop=name,changes=changes[name]))
   a,b,c,d=box;size=dimensions(c-a,d-b,large=False);panels=[]
   for tag,array in [('apple',T),('rev06',B),('rev09',C)]:
    im=rgb(array[b:d,a:c]).resize(size,Image.Resampling.BILINEAR);filename=f'{label.lower()}-{name}-{tag}.png';im.save(O/filename);files[filename]=dict(native=[c-a,d-b],presentation=list(size),sha256=sha(O/filename));panels.append(im)
   sheetrows.append(dict(label=f'{label} / {name}',panels=panels,metrics=changes[name]))
  observations.append(dict(observation=label,states=[old,new],changes=changes))
  pair(rgb(T),rgb(C),['Apple native source', 'Final accepted review09']).save(O/f'{label.lower()}-final09-comparison.png')
  pair(rgb(B),rgb(C),['Accepted review06 native', 'Final accepted review09 native']).save(O/f'{label.lower()}-06-09-comparison.png')
  rgb(C).save(O/f'{label.lower()}-final09-native.png')
 # Each sheet cell uses its OWN approved presentationwidth; whitespace only
 # aligns columns. No new nativecrop, diagnosticmask, recenter or color fit.
 cellw=max(p.width for row in sheetrows for p in row['panels']);margin=14;gap=16;header=72;rowheights=[max(p.height for p in r['panels'])+68 for r in sheetrows]
 sheet=Image.new('RGB',(3*cellw+4*margin,sum(rowheights)+header),'#171a20');draw=ImageDraw.Draw(sheet);font=ImageFont.truetype(FONT,20);small=ImageFont.truetype(FONT,16)
 for j,label in enumerate(['Apple / same native rectangle','Accepted06 / saved native','Final09 / saved native']):draw.text((margin+j*(cellw+margin),14),label,font=font,fill='white')
 y=header
 for row,height in zip(sheetrows,rowheights):
  delta=row['metrics'];draw.text((margin,y),row['label']+f"  deltaRMSE RGB {delta['rgb_rmse_255']:+.8f} / luma {delta['luma_rmse_255']:+.8f} / chroma {delta['chroma_rmse_255']:+.8f}",font=small,fill='#e6e7eb')
  for j,im in enumerate(row['panels']):sheet.paste(im,(margin+j*(cellw+margin),y+32))
  y+=height
 sheet.save(O/'switch-round09-crops.png')
 report=dict(advisory_only=True,state_order=['accepted review06','final accepted review09'],scope='EXACT historical normalized/native rectangles; SAVEDnative completearrays only, NO opticalrerender/HQ4x/newmask/recrop/recenter/recolor. Presentationresize only; metrics beforePNGquantization.',observations=observations,local_regressions=regressions,limits='Smallglobalimprovements do not establish solvedcoloredfringes/rainbows. Originaldefined1/observed0modeledhiddenRGB/sourceuncertainty and physicaloperator ambiguity retained. Native scoregate/masks/epoch unchanged.')
 (O/'pass-09-crops.json').write_text(json.dumps(report,indent=2)+'\n')
 for filename in ['switch-round09-crops.png','a-final09-comparison.png','b-final09-comparison.png','a-06-09-comparison.png','b-06-09-comparison.png','a-final09-native.png','b-final09-native.png','pass-09-crops.json']:
  files[filename]=dict(bytes=(O/filename).stat().st_size,sha256=sha(O/filename))
 assert all(sha(Path(p))==digest for p,digest in inputs.items())
 (O/'verification.json').write_text(json.dumps(dict(inputs_sha256=inputs,files=files,original_crop_rectangles_exact=True,new_optical_renders=0,fitmask_changes=0,source_or_score_epoch_changes=0,review09_commit='46b888dd',sheet_pixels=list(sheet.size),per_image_width_rule='min(2W,max(W,720)), aspect retained; fullnativecontroloriginalwidth>720 staysoriginal; no4x',local_regressions=regressions),indent=2)+'\n');print(json.dumps(dict(sheet=list(sheet.size),regressions=regressions,changes=[dict(observation=o['observation'],changes=o['changes']) for o in observations]),indent=2))
if __name__=='__main__':main()
