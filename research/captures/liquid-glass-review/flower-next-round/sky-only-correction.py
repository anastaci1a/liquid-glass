"""ONE explicit visible-photo exclusion BEFORE input freeze; not an optical gain.
Reuse completed pose/glyph/native masks. No new decode/register/render/materialfit.
"""
import os,json,hashlib,shutil,datetime
from pathlib import Path
import numpy as np
from PIL import Image,ImageDraw
R=Path('/evidence/extended/helper-toolbar-work/flower-next-round');D=R/'sky-only-correction';D.mkdir();os.umask(0o002)
def sha(p):return hashlib.sha256(p.read_bytes()).hexdigest()
def save(n,v):(D/n).write_text(json.dumps(v,indent=2)+'\n')
start=json.loads((R/'started.json').read_text());assert datetime.datetime.now(datetime.timezone.utc)<datetime.datetime.fromisoformat(start['deadline_at'].replace('Z','+00:00'));T=np.asarray(Image.open(R/'a-proposed/target.png').convert('RGB'));y,x=np.mgrid[:1080,:1920];u=(x-1318)/200;v=(y-552)/250;X=np.stack([np.ones_like(u),u,v],-1);Q=np.stack([np.ones_like(u),u,v,u*u,u*v,v*v],-1);old=np.load(R/'source-controls.npz');clean=(y<790)|(x<=1420);train=old['train']&clean;test=old['held']&clean;checks=[('held_clean_upper_lower',test),('independent_left_upper_UNCHANGED',old['left']),('independent_right_lower_UNCHANGED',old['right'])]
def errors(field):
 out=[]
 for n,m in checks:
  e=(field-T/255)[m]*255;out.append(dict(name=n,pixels=int(m.sum()),rgb_rmse=float(np.sqrt(np.mean(e**2))),signed_rgb=e.mean(0).tolist(),p95_absolute=float(np.percentile(abs(e),95))))
 return out
co=np.linalg.lstsq(X[train],T[train]/255,rcond=None)[0];plane=X@co;pe=errors(plane);blocks=[]
for a,b in [(1140,1250),(1250,1360),(1360,1490)]:
 for lo,hi in [(260,320),(790,850)]:
  m=test&(x>=a)&(x<=b)&(y>=lo)&(y<=hi)
  if m.any():blocks.append(dict(rect=[a,lo,b,hi],pixels=int(m.sum()),mean_error_rgb=((plane-T/255)[m]*255).mean(0).tolist()))
trend=max(max(abs(np.array(q['mean_error_rgb']))) for q in blocks);quadratic=None;field=plane;selected='affine';coef=co;chosen=pe
if trend>1:
 qc=np.linalg.lstsq(Q[train],T[train]/255,rcond=None)[0];qf=Q@qc;qe=errors(qf);ok=bool(qe[0]['rgb_rmse']<pe[0]['rgb_rmse']*.9 and all(a['rgb_rmse']<=b['rgb_rmse'] for a,b in zip(qe[1:],pe[1:])));quadratic=dict(coefficients_rgb=qc.tolist(),controls=qe,selected=ok)
 if ok:field=qf;selected='quadratic';coef=qc;chosen=qe
# Visible non-sky stalk rectangle is also UNDEFINED in proposed field confidence. Original crop/material guards unaffected.
stalk=(x>=1430)&(y>=785);domain=old['defined']&~stalk;source=np.where(domain[...,None],np.clip(field,0,1),0);a=D/'a-proposed';a.mkdir()
for n in ['target.png','observed.png','target-visible.png','forward.end.fill-original.svg']:shutil.copyfile(R/'a-proposed'/n,a/n)
Image.fromarray(np.uint8(np.rint(source*255))).save(a/'source.png');Image.fromarray(np.uint8(domain)*255).save(a/'known.png');case=json.loads((R/'a-proposed/case.json').read_text());case['background_estimate'].update(kind='Separate uncovered-sky '+selected+' RGBfield afterONEvisible-stalk exclusion, NOTobservedhiddenphoto',basis=['1','(x-1318)/200','(y-552)/250']+(['u²','uv','v²'] if selected=='quadratic' else []),coefficient_rgb=coef.tolist(),controls=chosen,excluded_nonsky_rectangle=[1430,785,1491,851],source_control_correction='Original lowerband crossed VISIBLEblurredstalk atlower-right. Changedlowertrain/held x<=1420; independentleft/right controls, pose/glyph/target/native masks unchanged. Priorplane/quadresults preserved, source-onlyquality correctionCOUNT0.')
case['source_sha256']={n:sha(a/n) for n in ['source.png','target.png','known.png','observed.png','target-visible.png']};(a/'case.json').write_text(json.dumps(case,indent=2)+'\n');shutil.copyfile(R/'protocol-masks-PROPOSED.npz',D/'protocol-masks-PROPOSED.npz');np.savez_compressed(D/'source-controls.npz',train=train,held=test,left=old['left'],right=old['right'],excluded_all_glass_shadow=old['excluded_all_glass_shadow'],defined=domain,source_field=np.where(domain[...,None],field,np.nan).astype(np.float32))
original=json.loads((R/'input-proposal.json').read_text());out={**original,'status':'CORRECTED_SKY_ONLY_SINGLE_INPUT_PROPOSAL_BEFORE_ANYFIT','selected_source_model':selected,'selected_controls':chosen,'affine_coefficients_rgb':co.tolist(),'affine_controls':pe,'affine_held_block_residuals':blocks,'affine_max_abs_held_block_mean_native':trend,'quadratic':quadratic,'source_training_pixels':int(train.sum()),'source_held_pixels':int(test.sum()),'case_sha256':hashlib.sha256(json.dumps(case,sort_keys=True).encode()).hexdigest(),'source_center_rgb':field[552,1318].tolist(),'control_correction':case['background_estimate']['source_control_correction'],'prior_source_audit':'../input-proposal.json andcontrol-context-native.png preserved','source_domain_excluded_photo':[1430,785,1491,851],'pose_glyph_target_native_masks_REUSED_unchanged':True,'optical_renders':0,'material_fits':0,'accepted_count':0};save('input-proposal.json',out);print(json.dumps({k:out[k] for k in ['selected_source_model','selected_controls','affine_max_abs_held_block_mean_native','quadratic','source_training_pixels','source_held_pixels','source_center_rgb','control_correction']}),flush=True)
x0,y0,x1,y1=case['crop'];A=T[y0:y1,x0:x1];B=np.uint8(np.rint(np.clip(field[y0:y1,x0:x1],0,1)*255));w=2*(x1-x0);h=2*(y1-y0);sheet=Image.new('RGB',(2*w+2,h+64),'#222');draw=ImageDraw.Draw(sheet);draw.text((8,20),'Original NEXT — no opticalfit',fill='white');draw.text((w+12,20),'Cleancontrols estimatedsky — NOlensmodel',fill='white');sheet.paste(Image.fromarray(A).resize((w,h),Image.Resampling.LANCZOS),(0,64));sheet.paste(Image.fromarray(B).resize((w,h),Image.Resampling.LANCZOS),(w+2,64));sheet.save(D/'input-source-comparison.png')
