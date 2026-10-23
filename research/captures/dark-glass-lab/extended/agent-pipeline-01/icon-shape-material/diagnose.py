"""Frozen vector coverage/ink diagnostic only; screenshot threshold never a matte."""
from pathlib import Path
import sys,time,json,hashlib,numpy as np
P=Path('/evidence/extended/agent-pipeline-01');O=P/'icon-shape-material';sys.path.insert(0,str(P/'code'))
from extended_fit import Study
proto=json.loads((O/'protocol.json').read_text());start=__import__('datetime').datetime.fromisoformat(proto['start'].replace('Z','+00:00')).timestamp();assert time.time()<start+480,'Original first8minute subpass cap'
result={'status':'CACHED_VECTOR_DIAGNOSTIC','new_rays':0,'new_source_queries':0,'native_candidate_composites':0,'cases':{}}
for key in ['a','b']:
 s=Study(P/f'inputs/{key}');x0,y0,_,_=s.crop;M=np.load(P/'color-grading'/f'{key}-step0.5-material.npy');C=np.load(P/'color-grading'/f'{key}-step0.5-complete.npy');records=[]
 for layer in s.case['foreground_layers']:
  name=layer.get('vector_asset',layer.get('artwork_asset'));a,b,c,d=layer['box'];alpha=next(alpha for box,alpha,color in s.foreground_layers if tuple(box)==tuple(layer['box']));T=s.target[b:d,a:c];core=alpha>=.995;edge=(alpha>.01)&(alpha<.995);data={'asset':name,'sha256':hashlib.sha256((s.folder/name).read_bytes()).hexdigest(),'mode':layer['mode'],'box':layer['box'],'vector_box':layer.get('vector_box'),'opacity':layer.get('opacity',1),'color':layer.get('color'),'core_pixels':int(core.sum()),'partial_edge_pixels':int(edge.sum()),'variant_status':layer.get('vector_provenance',{}).get('variant_status'),'font_file':layer.get('vector_provenance',{}).get('font_file')}
  if layer['mode']!='artwork':
   lum=T@np.array([.2126,.7152,.0722]);data['observed_core_luma_percentiles']=np.percentile(lum[core],[0,10,25,50,75,90,100]).tolist() if core.any() else [];data['observed_core_RGB_mean']=T[core].mean(0).tolist() if core.any() else []
   if name!='artist.svg':
    observed=lum<.1;pred=alpha>=.5;data['black_silhouette_threshold_diagnostic']={'IoU':float((observed&pred).sum()/(observed|pred).sum()),'observed_pixels':int(observed.sum()),'vector_halfcoverage_pixels':int(pred.sum()),'not_a_render_matte':True}
   else:
    Y,X=np.mgrid[b:d,a:c];held=((X//8+3*(Y//8))%4)==0;data['core_train_pixels']=int((core&~held).sum());data['core_held_pixels']=int((core&held).sum());data['core_baseline_RMSE']=float(np.sqrt(np.mean(((C[b-y0:d-y0,a-x0:c-x0]-T)[core]*255)**2)));data['partial_edge_baseline_RMSE']=float(np.sqrt(np.mean(((C[b-y0:d-y0,a-x0:c-x0]-T)[edge]*255)**2)))
  records.append(data)
 result['cases'][key]=records
result['limits']='Original font outline identity known, exact UIweight/layout not proven. Core heterogeneity can reflect placement/coverage/codec/background mismatch; no tint or contour metric establishes exact glyph truth. Photo artwork stays immutable. No screenshot threshold used for rendering/masks/source.';result['finished_unix']=time.time();(O/'diagnostic.json').write_text(json.dumps(result,indent=2));print(json.dumps({k:[r for r in rows if r['asset']=='artist.svg'] for k,rows in result['cases'].items()}))
