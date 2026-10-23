import os,sys,json,copy,hashlib,datetime,time,shutil
from pathlib import Path
import numpy as np,cv2
from fontTools.ttLib import TTFont
from fontTools.varLib.instancer import instantiateVariableFont
from fontTools.pens.basePen import BasePen
from fontTools.pens.boundsPen import BoundsPen
from fontTools.pens.svgPathPen import SVGPathPen
os.umask(0o002);cv2.setNumThreads(1)
R=Path('/evidence/extended/helper-toolbar-work/more-close-round');D=R/'original-weight-correction';D.mkdir(exist_ok=True);B=R/'latest-circle-baseline';X=R/'xmark-source-review';P=R/'foreground-gray-round1'
start=time.time();stamp=lambda:datetime.datetime.now(datetime.timezone.utc).isoformat();(D/'started.json').write_text(json.dumps(dict(started_at=stamp(),deadline_seconds=600,assignment='42c60db8-d944-45b0-b260-3506e9501271')))
sys.path.insert(0,str(B/'code'));from extended_fit import Study;from vector_foreground import coverage;from vector_revision import composite
geom=json.loads((X/'review.json').read_text())['geometry_measurement'];center=np.array(geom['center']);span=19.1377995;targetwidth=geom['stroke_width_native'];C0=np.array([746.,187.5]);box=[737,178,757,198];edge=[736.5,177.5,756.5,197.5];fontpath=json.loads((X/'original-one-control.json').read_text())['font'];font=TTFont(fontpath);name='xmark.tag.color.large'
class Lines(BasePen):
 def __init__(self,gs):super().__init__(gs);self.lines=[];self.p=None;self.first=None
 def _moveTo(self,p):self.p=np.array(p);self.first=self.p.copy()
 def _lineTo(self,p):p=np.array(p);self.lines.append([self.p.copy(),p]);self.p=p
 def _curveToOne(self,p1,p2,p3):
  p0=self.p.copy();p1,p2,p3=map(np.array,[p1,p2,p3]);ts=np.linspace(0,1,129)[1:]
  for t in ts:self._lineTo((1-t)**3*p0+3*(1-t)**2*t*p1+3*(1-t)*t*t*p2+t**3*p3)
 def _qCurveToOne(self,p1,p2):
  p0=self.p.copy();p1,p2=map(np.array,[p1,p2]);ts=np.linspace(0,1,129)[1:]
  for t in ts:self._lineTo((1-t)**2*p0+2*(1-t)*t*p1+t*t*p2)
 def _closePath(self):self._lineTo(self.first)
 def _endPath(self):pass
v1=np.array([1.,1.])/np.sqrt(2);v2=np.array([1.,-1.])/np.sqrt(2)
def line_interval(lines,origin,n):
 v=np.array([-n[1],n[0]]);a=lines[:,0]-origin;z=lines[:,1]-origin;ya=a@v;yz=z@v;keep=(ya<=0)&(yz>0)|(yz<=0)&(ya>0);f=ya[keep]/(ya[keep]-yz[keep]);x=(a[keep]+f[:,None]*(z[keep]-a[keep]))@n;x=np.sort(x)
 intervals=[(x[i],x[i+1]) for i in range(0,len(x)-1,2)];return min(intervals,key=lambda q:abs((q[0]+q[1])/2))
evals=[];cache={}
def evaluate(w):
 assert time.time()-start<600
 f=font;gs=f.getGlyphSet(location={'wght':float(w)});g=gs[name];bp=BoundsPen(gs);g.draw(bp);bounds=np.array(bp.bounds);bc=(bounds[:2]+bounds[2:])/2;scale=span/max(bounds[2:]-bounds[:2]);lp=Lines(gs);g.draw(lp);lines=(np.array(lp.lines)-bc)*[scale,-scale]+center
 widths=[];held=[]
 for pr in geom['profiles']:
  v,sgn=({'SE':(v1,1),'NW':(v1,-1),'NE':(v2,1),'SW':(v2,-1)})[pr['arm']];left,right=line_interval(lines,C0+sgn*pr['along']*v,np.array(pr['normal']))
  if pr['train']:widths.append(right-left)
  else:held.append(dict(along=pr['along'],left_error=float(left-pr['left']),right_error=float(right-pr['right'])))
 width=float(np.median(widths));info=dict(weight=w,training_median_width=width,target_training_width=targetwidth,width_error=width-targetwidth,held_outline_edges=held,bounds=bounds.tolist(),scale=float(scale));evals.append(info);cache[w]=(f,gs,g,bc,scale,lines,info);print(json.dumps(info),flush=True);return width
w400=evaluate(400);w600=evaluate(600);lo,hi=(400.,600.)
# At most five extra GEOMETRIC evaluations; no color/raster objective.
extra=0
if not min(w400,w600)<=targetwidth<=max(w400,w600):
 if targetwidth>max(w400,w600):lo,hi=600.,1000.;evaluate(hi)
 else:lo,hi=1.,400.;evaluate(lo)
 extra+=1
for k in range(5-extra):
 wl=cache[lo][-1]['training_median_width'];wh=cache[hi][-1]['training_median_width']
 if not min(wl,wh)<=targetwidth<=max(wl,wh):break
 w=(lo+hi)/2;val=evaluate(w)
 if val<targetwidth:lo=w
 else:hi=w
best=min(cache,key=lambda w:abs(cache[w][-1]['width_error']));f,gs,g,bc,scale,lines,info=cache[best];pen=SVGPathPen(gs);g.draw(pen);transform=f'matrix({scale} 0 0 {-scale} {center[0]-edge[0]-scale*bc[0]} {center[1]-edge[1]+scale*bc[1]})';svg=f'<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 20 20"><path fill="#000" transform="{transform}" d="{pen.getCommands()}"/></svg>\n';asset='xmark-original-matched.svg';(D/asset).write_text(svg)
# ONE cached composite of resulting original-font candidate. No body render.
old=Study(B/'inputs/a');rec=json.loads((P/'candidate-native.json').read_text());arr=np.load(P/'candidate-native.npz');M=arr['material'];folder=D/'a-original-matched';folder.mkdir();case=copy.deepcopy(old.case);oldlayer=case['foreground_layers'][0];case['foreground_layers']=[{**oldlayer,'box':box,'vector_asset':asset,'vector_sha256':hashlib.sha256(svg.encode()).hexdigest(),'vector_box':edge,'style_key':oldlayer['vector_asset']}];case['glyph_provenance_history']=[case.pop('glyph_provenance')];case['glyph_provenance']=dict(identity=name,font=fontpath,font_sha256=hashlib.sha256(Path(fontpath).read_bytes()).hexdigest(),weight_geometry_selected=best,measured_major_span=span,center=center.tolist(),exact_Apple_UI_weight=False,no_tint_or_body_optimization=True);case['foreground_provenance_proposal']=dict(stage='SOURCE_ONLY_UNADOPTED',original_placement_control_corrected=True)
for n in case['source_sha256']:shutil.copyfile(B/'inputs/a'/n,folder/n)
shutil.copyfile(D/asset,folder/asset);(folder/'case.json').write_text(json.dumps(case,indent=2)+'\n');s=Study(folder);s.case['foreground_styles']=rec['foreground_styles'];C=composite(s,rec['preset'],M);s.case.pop('foreground_styles');A=coverage(folder,case['foreground_layers'][0]);offset=np.arange(-4,4.0001,.0625)
def crossings(x,y,level):
 inside=y>=level;idx=np.flatnonzero(inside);k=idx[np.argmin(abs(x[idx]))];a=b=k
 while a>0 and inside[a-1]:a-=1
 while b<len(x)-1 and inside[b+1]:b+=1
 interp=lambda i,j:float(x[i]+(level-y[i])*(x[j]-x[i])/(y[j]-y[i]));return interp(a-1,a),interp(b,b+1)
def sample(pts):return cv2.remap(A,pts[:,0].astype(np.float32)[None,:],pts[:,1].astype(np.float32)[None,:],cv2.INTER_LINEAR)[0]
held=[]
for pr in geom['profiles']:
 if pr['train']:continue
 pts=C0-pr['along']*v2+offset[:,None]*np.array(pr['normal'])-np.array(box[:2]);left,right=crossings(offset,sample(pts),.5);held.append(dict(along=pr['along'],left_error=left-pr['left'],right_error=right-pr['right']))
u=np.arange(5,15.0001,.0625);values=sample(center-u[:,None]*v2-np.array(box[:2]));j=np.flatnonzero(values>=.5)[-1];tip=float(u[j]+(.5-values[j])*(u[j+1]-u[j])/(values[j+1]-values[j]));obstip=next(q['tip_distance'] for q in geom['endpoint_evidence'] if not q['train']);bm=np.load(B/'baseline-native-arrays.npz');fg=bm['glyph_mask'];fgerr=float(np.sqrt(np.mean(((C-s.target_crop)[fg]*255)**2)));np.savez_compressed(folder/'cached-native-NOT-ADOPTED.npz',material=M,complete=C,alpha=arr['alpha']);report=dict(stage='SOURCE_ONLY_NOT_ADOPTED_COUNT0',evaluations=evals,selected_weight=best,selected=info,flattening='Each cubic/quadratic128pieces, numerical geometry evidence not exact contour truth',actual_svg_held_edges=held,actual_svg_held_tip_error=tip-obstip,old_frozen_FG_RMSE=fgerr,old_incumbent_FG_RMSE=rec['scores']['glyph']['rmse'],clean_trace_FG_RMSE=17.05976676940918,clean_trace_tip_error=-.20147,body_renders=0,cached_font_composites=1,color_opacity_body_source_fixed=True,count_added=0)
(D/'geometry-review.json').write_text(json.dumps(report,indent=2)+'\n');print('RESULT '+json.dumps(report),flush=True)
# Separately proposed NEW scoring epochs: exclusion matches20x20 canvas under inclusive public box convention.
maskreport=[]
for label,sourcefolder,npz in [('clean',X/'a-clean-full','CACHEDM-reevaluation-NOT-ADOPTED.npz'),('original',folder,'cached-native-NOT-ADOPTED.npz')]:
 newfolder=D/f'new-epoch-{label}';newfolder.mkdir();newcase=json.loads((sourcefolder/'case.json').read_text());newcase['foreground']=[box];newcase['protocol']={**newcase.get('protocol',{}),'stage':'PROPOSED_NEW_SOURCE_AND_SCORING_EPOCH_NOT_ACTIVE','old_case_immutable':True,'not_optical_gain':True}
 for n in newcase['source_sha256']:shutil.copyfile(sourcefolder/n,newfolder/n)
 va=newcase['foreground_layers'][0]['vector_asset'];shutil.copyfile(sourcefolder/va,newfolder/va);(newfolder/'case.json').write_text(json.dumps(newcase,indent=2)+'\n');ns=Study(newfolder);ca=np.load(sourcefolder/npz)['complete'];before=old.scores(M);after=ns.scores(M);details={}
 masks={}
 for name,om,nm in [('glass',old.valid,ns.valid),('rim',old.rim,ns.rim),('held',old.held,ns.held),('interior',old.valid&~old.rim,ns.valid&~ns.rim),('SSIM_safe',cv2.erode(old.valid.astype(np.uint8),np.ones((11,11),np.uint8))>0,cv2.erode(ns.valid.astype(np.uint8),np.ones((11,11),np.uint8))>0)]:
  assert np.all(~nm|om);details[name]=dict(old=int(om.sum()),new=int(nm.sum()),removed=int((om&~nm).sum()),new_subset_of_old=True);masks[name]=nm
 yy,xx=np.mgrid[160:218,720:778];guard=(xx>=box[0])&(xx<=box[2])&(yy>=box[1])&(yy<=box[3]);paint=(xx>=box[0])&(xx<box[2])&(yy>=box[1])&(yy<box[3]);assert not np.any(ns.valid&paint)
 np.savez_compressed(newfolder/'cached-baseline-and-masks-NOT-ACTIVE.npz',material=M,complete=ca,alpha=arr['alpha'],foreground_guard_inclusive=guard,paint_box=paint,**masks)
 entry=dict(variant=label,case_fingerprint=hashlib.sha256(json.dumps(newcase,sort_keys=True).encode()).hexdigest(),mask_counts=details,scoring_inclusive_foreground_pixels=int(guard.sum()),paint_pixels=int(paint.sum()),old_scores=before,proposed_NEW_epoch_baseline_scores=after,NEW_epoch_FG_guard_RMSE=float(np.sqrt(np.mean(((ca-ns.target_crop)[guard]*255)**2))),source_whole_post_superset_proof_transfers=True,new_scored_subrays_must_report_exact_subset_counts=True,optical_gain_claim=False,count_added=0)
 maskreport.append(entry)
(D/'new-epoch-proposal.json').write_text(json.dumps(dict(stage='NOT_ACTIVE_PRIMARY_DECISION_REQUIRED',variants=maskreport,body_renders=0,elapsed_seconds=time.time()-start),indent=2)+'\n');print('MASKS '+json.dumps(maskreport),flush=True)
