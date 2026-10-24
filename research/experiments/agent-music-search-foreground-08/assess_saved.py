"""Metadata and saved glyph-cohort assessment; no rendering imports."""
from pathlib import Path
import json,datetime,hashlib
import numpy as np
from PIL import Image
P=Path(__file__).resolve().parent;ROOT=P.parents[2];B=P.parent/'agent-music-search-baseline-01';T=P.parent/'agent-music-search-neutral-05';W=ROOT/'.evidence-working/music-search-baseline-01'
assert not (P/'result.json').exists();protocol=json.loads((P/'protocol.json').read_text());assert datetime.datetime.now(datetime.timezone.utc)<datetime.datetime.fromisoformat(protocol['deadline'].replace('Z','+00:00'))
rows=[];count=0
for k in ['a','b']:
 case=json.loads((W/k/'case.json').read_text());assert case==json.loads((B/'cases'/f'{k}.json').read_text());layer=case['foreground_layers'][0];assert len(case['foreground_layers'])==1 and layer['mode']=='mask'
 digest=hashlib.sha256((W/k/'search.svg').read_bytes()).hexdigest();assert digest==layer['vector_sha256'];style=case['foreground_styles']['search.svg'];assert 'response' not in style
 box=layer['box'];assert box==[1467,626,1563,722];x0,y0,_,_=case['crop'];a,b,c,d=box;sl=np.s_[b-y0:d-y0,a-x0:c-x0];N=(d-b)*(c-a);count+=6*N;assert count<=225600
 old=np.load(B/f'{k}-candidate.npz');new=np.load(T/f'full-{k}-candidate.npz');target=np.asarray(Image.open(W/k/'target.png').convert('RGB').crop(tuple(box)),dtype=np.float32)/255
 oldpre=old['pre_foreground'][sl];oldC=old['complete'][sl];newpre=new['pre_foreground'][sl];newC=new['complete'][sl];cov=new['coverage'][sl]
 assert target.shape==newC.shape and np.isfinite(newC).all();assert np.all(cov==1)
 oldrecord=json.loads((B/f'{k}-result.json').read_text());newrecord=json.loads((T/f'full-{k}-result.json').read_text())
 rows.append(dict(reference=k,guard_box=box,pixels=N,fully_covered=N,SVG_sha256=digest,provenance=case['foreground_provenance'],placement=layer['vector_box'],style=style,bare_layer_color=layer['color'],bare_layer_opacity=layer['opacity'],ordered_layers=1,transmission_layers=0,style_response=False,original_glyph_RMSE=oldrecord['completed_image_scores']['foreground_RMSE'],accepted_tone_glyph_RMSE=newrecord['scores']['complete']['foreground_RMSE'],retained_glyph_crop_diagnostics=newrecord['fixed_crops']['glyph'],changed_backing_pixels=int(np.any(newpre!=oldpre,axis=2).sum()),changed_completed_pixels=int(np.any(newC!=oldC,axis=2).sum()),target_finite=bool(np.isfinite(target).all()),original_complete_minus_backing_range=[float((oldC-oldpre).min()),float((oldC-oldpre).max())],accepted_complete_minus_backing_range=[float((newC-newpre).min()),float((newC-newpre).max())]))
(P/'result.json').write_text(json.dumps(dict(utc=datetime.datetime.now(datetime.timezone.utc).isoformat(),status='ASSESSED_FIDELITY_UNRESOLVED_NO_INTERVENTION_SELECTED',records=rows,native_saved_pixel_observations=count,cap=225600,work_scope='Six existing 96x96 cohorts per reference; archive decoding is not new optical sampling. No alpha inferred from pixel differences.',optical_operations=0,rasterizations=0,composites=0,fits=0,rendered_images=0,decision='Fixed rendering identity and provenance verified. Body-tone changes alone explain large guard improvement; exact symbol weight/pose/material cannot be isolated from current backing and illumination residuals. No foreground modification is justified by this assessment.'),indent=2)+'\n')
print((P/'result.json').read_text())
