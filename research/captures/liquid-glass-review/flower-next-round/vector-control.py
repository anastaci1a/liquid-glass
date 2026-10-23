"""ONE pinned path vs cached originalfont; silhouette diagnostics ONLY/no matte renderer."""
import os,json,re,hashlib,sys,copy,datetime
from pathlib import Path
import cv2,numpy as np
from PIL import Image,ImageDraw
from fontTools.svgLib.path import parse_path
from fontTools.pens.boundsPen import BoundsPen
R=Path('/evidence/extended/helper-toolbar-work/flower-next-round');D=R/'vector-control';os.umask(0o002);cv2.setNumThreads(1);sys.path.insert(0,'/evidence/extended/helper-toolbar-work/safari-magnifier-round/code')
from vector_foreground import coverage
assert not (D/'review.json').exists();st=json.loads((D/'started.json').read_text())
raw=(D/'sfForwardEndFill.js').read_bytes();blob=hashlib.sha1(b'blob '+str(len(raw)).encode()+b'\0'+raw).hexdigest();assert blob=='22247334b9d1ed3b285152be9a786306769a2831';paths=re.findall(r'\{d:"([^"]+)"',raw.decode());assert len(paths)==1 and re.fullmatch(r'[MmLlHhVvCcSsQqTtAaZz0-9., +\-Ee]+',paths[0]);bp=BoundsPen(None);parse_path(paths[0],bp);l,b,r,t=bp.bounds;w,h=r-l,t-b
svg=f'<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 {w:.12g} {h:.12g}"><path fill="#fff" transform="translate({-l:.12g} {-b:.12g})" d="{paths[0]}"/></svg>\n';(D/'forward.end.fill-pinned.svg').write_text(svg)
case=json.loads((R/'sky-only-correction/a-proposed/case.json').read_text());old=case['foreground_layers'][0];bounds=case['foreground_provenance']['exposed_white_bbox'];a0,b0,c0,d0=bounds;sc=min((c0-a0)/w,(d0-b0)/h);mx=(a0+c0-1)/2;my=(b0+d0-1)/2;placement=[mx-w*sc/2,my-h*sc/2,mx+w*sc/2,my+h*sc/2];new={**old,'vector_asset':'forward.end.fill-pinned.svg','vector_sha256':hashlib.sha256(svg.encode()).hexdigest(),'vector_box':placement}
Aold=coverage(R/'sky-only-correction/a-proposed',old);Anew=coverage(D,new);a,b,c,d=old['box'];T=np.asarray(Image.open(R/'sky-only-correction/a-proposed/target.png').convert('RGB'))[b:d,a:c];rows=[]
def contours(mask):return mask&~(cv2.erode(mask.astype(np.uint8),np.ones((3,3),np.uint8))>0)
def diagnostic(A,target):
 mask=A>=.5;un=(mask|target).sum();tc=contours(target);mc=contours(mask);dt=cv2.distanceTransform((~tc).astype(np.uint8),cv2.DIST_L2,5);dm=cv2.distanceTransform((~mc).astype(np.uint8),cv2.DIST_L2,5);dist=np.r_[dt[mc],dm[tc]];return dict(iou=float((mask&target).sum()/un),different_pixels=int((mask^target).sum()),symmetric_contour_mean_px=float(dist.mean()),symmetric_contour_p95_px=float(np.percentile(dist,95)))
for threshold in [225,240]:
 target=(T.min(2)>threshold)&((T.max(2).astype(int)-T.min(2).astype(int))<20);rows.append(dict(native_white_threshold=threshold,old_original_font=diagnostic(Aold,target),pinned_path=diagnostic(Anew,target)));np.savez_compressed(D/f'DIAGNOSTIC_ONLY-white-threshold-{threshold}.npz',target_silhouette=target)
better=all(q['pinned_path']['iou']>q['old_original_font']['iou'] and q['pinned_path']['symmetric_contour_mean_px']<=q['old_original_font']['symmetric_contour_mean_px'] for q in rows);selected=new if better else old
result=dict(status='PINNED_PATH_SELECTED_COUNT0' if better else 'RETAIN_ORIGINAL_FONT_COUNT0',diagnostics=rows,js_executed=False,one_candidate=True,blob_sha1=blob,pinned_commit='2a0100e93e11a22ea0ff5e0530efd10e2cf0d243',file_sha256=hashlib.sha256(raw).hexdigest(),new_svg_sha256=new['vector_sha256'],new_ink_bounds=list(bp.bounds),new_uniform_placement=placement,fixed_native_glyph_box=old['box'],native_bbox=bounds,no_aspect_distortion=True,no_weight_or_pose_fit=True,opacity_policy='White1fixed; libraryfillOpacity.85notadopted',no_target_matte_in_render=True,provenance='AuthenticatedpinnedSFdata path, not independentproofAppleofficialSVG or exacttargetweight; no screenshottrace',source_pose_protocol_unchanged=True,old_glyph_history='sky-only-correction/a-proposed originalfontbytes unchanged',material_fits=0,optical_renders=0,count=0,wall_budget_exceeded=True,overrun_reason='Interleavedreadingqueuedbaselineimplementationbeforecomparison; preservedstartedtime, onecandidateonly/nosearchcontinuation',elapsed_seconds=(datetime.datetime.now(datetime.timezone.utc)-datetime.datetime.fromisoformat(st['at'].replace('Z','+00:00'))).total_seconds())
(D/'review.json').write_text(json.dumps(result,indent=2)+'\n');(D/'selected-layer.json').write_text(json.dumps(selected,indent=2)+'\n');print(json.dumps(result),flush=True)
# Glyphcoverage diagnostic only, fixedbbox, no lens/source render.
can=Image.new('RGB',(600,236),'#222');dr=ImageDraw.Draw(can)
for i,(im,title) in enumerate([(T,'Native reference'),(np.repeat((Aold*255)[...,None],3,axis=2).astype(np.uint8),'Originalfont coverage'),(np.repeat((Anew*255)[...,None],3,axis=2).astype(np.uint8),'Pinnedpath coverage')]):can.paste(Image.fromarray(im).resize((200,172),Image.Resampling.NEAREST),(i*200,64));dr.text((i*200+4,20),title,fill='white')
can.save(D/'glyph-control.png')
