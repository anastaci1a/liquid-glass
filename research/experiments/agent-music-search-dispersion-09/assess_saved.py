"""Direct saved-image reductions only; no optical, raster or compositor imports."""
from pathlib import Path
import json,datetime
import numpy as np
from PIL import Image
P=Path(__file__).resolve().parent;ROOT=P.parents[2];B=P.parent/'agent-music-search-baseline-01';T=P.parent/'agent-music-search-neutral-05';W=ROOT/'.evidence-working/music-search-baseline-01';p=json.loads((P/'protocol.json').read_text());assert not (P/'result.json').exists();assert datetime.datetime.now(datetime.timezone.utc)<datetime.datetime.fromisoformat(p['deadline'].replace('Z','+00:00'))
luma=np.array([.2126,.7152,.0722]);count=0;rows=[]
def stats(v):
 y=v@luma;c=v-y[:,None]
 return dict(mean_RGB=v.mean(0).tolist(),channel_min=v.min(0).tolist(),channel_max=v.max(0).tolist(),encoded_luma_mean=float(y.mean()),encoded_chroma_RMS=float(np.sqrt(np.mean(c*c))))
def gradients(v,valid):
 diffs=[]
 for ax in [0,1]:
  good=(valid[1:]&valid[:-1]) if ax==0 else (valid[:,1:]&valid[:,:-1]);diffs.append(np.diff(v,axis=ax)[good])
 q=np.concatenate(diffs)
 if not len(q):return dict(pairs=0)
 y=q@luma;c=q-y[:,None]
 return dict(pairs=len(q),channel_difference_RMS=np.sqrt(np.mean(q*q,axis=0)).tolist(),encoded_luma_difference_RMS=float(np.sqrt(np.mean(y*y))),encoded_chroma_difference_RMS=float(np.sqrt(np.mean(c*c))))
for k in ['a','b']:
 source=Image.open(W/k/'source.png').convert('RGB');target=Image.open(W/k/'target.png').convert('RGB');known=Image.open(W/k/'known.png').convert('L');z=np.load(T/f'full-{k}-candidate.npz');m=np.load(B/f'{k}-masks.npz');records={}
 for name,box in p['fixed_crops'].items():
  a,b,c,d=box;N=(c-a)*(d-b);count+=7*N;assert count<=p['pixel_cap'];sl=np.s_[b-560:d-560,a-1395:c-1395]
  S=np.asarray(source.crop(tuple(box)),np.float32)/255;R=np.asarray(target.crop(tuple(box)),np.float32)/255;C=z['pre_foreground'][sl];cov=z['coverage'][sl];glass=m['glass'][sl].astype(bool);fg=m['foreground'][sl].astype(bool);K=np.asarray(known.crop(tuple(box)))>0
  valid=K&~fg&np.isfinite(C).all(2);cohorts={}
  for label,mask in [('known_non_foreground',valid),('original_glass_fully_covered',valid&glass&(cov==1))]:
   n=int(mask.sum())
   if not n:cohorts[label]=dict(pixels=0,reason='Original foreground exclusion or no qualifying pixels; no replacement mask.');continue
   s=S[mask].astype(float)*255;r=R[mask].astype(float)*255;cur=C[mask].astype(float)*255;e=cur-r;ey=e@luma;ec=e-ey[:,None]
   cohorts[label]=dict(pixels=n,source_native_plane=stats(s),target=stats(r),selected_body=stats(cur),residual=dict(RGB_RMSE=float(np.sqrt(np.mean(e*e))),channel_RMSE=np.sqrt(np.mean(e*e,axis=0)).tolist(),signed_RGB=e.mean(0).tolist(),luma_RMSE=float(np.sqrt(np.mean(ey*ey))),signed_luma=float(ey.mean()),chroma_RMSE=float(np.sqrt(np.mean(ec*ec))),RG_residual_mean=float((e[:,0]-e[:,1]).mean()),BG_residual_mean=float((e[:,2]-e[:,1]).mean())),native_adjacent_differences={label2:gradients(v.astype(float)*255,mask) for label2,v in [('source_native_plane',S),('target',R),('selected_body',C)]})
  records[name]=dict(bounds=box,rectangle_pixels=N,foreground_excluded=int(fg.sum()),known_pixels=int(K.sum()),original_glass_pixels=int(glass.sum()),partial_original_glass=int((glass&(cov<1)).sum()),cohorts=cohorts)
 rows.append(dict(reference=k,crops=records))
(P/'result.json').write_text(json.dumps(dict(utc=datetime.datetime.now(datetime.timezone.utc).isoformat(),status='DISPERSION_UNIDENTIFIED_NO_SPECTRAL_SETTING',records=rows,native_saved_pixel_observations=count,cap=p['pixel_cap'],optical_operations=0,fields_filters_composites_rasterizations_images_fits=0,interpretation='Native source statistics describe existing unwarped mosaic content, not the refracted correspondence. Encoded luma/chroma are diagnostics, not spectral radiance. Adjacent differences have no smoothing or channel-registration fit.',discriminant_needed='An independently supported source feature and reference-specific channel displacement reproducible across backgrounds, distinguishable from common positional error, encoded tone, PSF/codec and missing illumination. Current evidence does not identify a coupled wavelength-index law.'),indent=2)+'\n')
print('Saved observations',count)
for x in rows:
 for name,record in x['crops'].items():
  q=record['cohorts']['original_glass_fully_covered'];print(x['reference'],name,q['pixels'],q.get('residual',{}))
