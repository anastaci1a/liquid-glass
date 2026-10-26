"""Bind one completed verified pass to the shared public working factory."""
from pathlib import Path
import json,sys,hashlib,datetime,copy
import numpy as np
from shoulder_core_coordinate import ShoulderCoreSplineBack
from hermite_height_back import HermiteFootprintBack
B=Path(__file__).parent;R=B.parents[2];number=int(sys.argv[1]);P=B/f'pass{number}';assert json.loads((P/'verification.json').read_text())['passed']
recipe=json.loads((P/'final-recipe.json').read_text());protocol=json.loads((P/'protocol.json').read_text());legacy=json.loads((B/'legacy-numerical-family.json').read_text());F=json.loads((B/'starting-family.json').read_text());L=F['length_unit_native_pixels'];g=copy.deepcopy(legacy['geometry']);g['corner_radius']-=protocol['dilation_reduction_native']/L;g['shoulder_inset']=protocol['shoulder_native']/L;g['coordinate']='shoulder_core';g['model']='Smooth shoulder-core contour; same actual spline front and Hermite back'
F['members']=copy.deepcopy(legacy['members'])
for member in F['members']:F['members'][member]['major_half']+=1.5/L
base=ShoulderCoreSplineBack((F['members']['expanded']['major_half'],g['minor_half']),g['corner_radius'],g['shoulder_inset'],g['breaks'],g['height_controls'])
profile=json.loads((R/legacy['geometry']['back_profile']).read_text());scale=base.radius/profile['radius_nodes'][-1];profile['radius_nodes']=(np.array(profile['radius_nodes'])*scale).tolist();profile['radius_nodes'][-1]=base.radius;profile['derivatives']=(np.array(profile['derivatives'])/scale*1.02).tolist();profile['heights']=(np.array(profile['heights'])*1.02).tolist();actual=HermiteFootprintBack(base,profile);profile['maximum_height']=actual.maximum_height;profile['slope_bound']=actual.slope_bound
name='reconstruction/families/music-mini-player-three-pass-profile.json';(R/name).write_text(json.dumps(profile,indent=2)+'\n');g['back_profile']=name;g['back_profile_sha256']=hashlib.sha256((R/name).read_bytes()).hexdigest();g['front_scale']*=1.02;F['geometry']=g
F['material'].update(incident_sigma_native_pixels=recipe['sigma'],incident_kernel_radius=int(np.ceil(3*recipe['sigma'])),gain=recipe['gain'],bias=recipe['bias'],low_luminance_lift=recipe['low_lift'],chroma=recipe['chroma'],generated_shadow=recipe['shadow'],outline=dict(response='bright_colored_rim',endpoint=recipe['endpoint'],**recipe['outline'],angular=recipe['angular'],guide='Incident-blurred actual refraction before body grade and assigned reflection; ordered foreground retained'))
F['artwork']=recipe['artwork'];F['sampling']['outline']['order']=max(x['order'] for x in json.loads((P/'integration.json').read_text()));F['provenance']['starting_family']=str((B/'starting-family.json').relative_to(R));F['evidence']=str((B/'FINAL-REVIEW.md').relative_to(R));F['selection_record']='research/decisions/miniplayer-three-pass-working.json'
(R/'reconstruction/families/music-mini-player-working.json').write_text(json.dumps(F,indent=2)+'\n')
record=dict(at=datetime.datetime.now(datetime.timezone.utc).isoformat(),selected_pass=number,reason='Verified shared visual working compromise; original and transfer failures retained',full_fidelity=False,full_pipeline_pass=False,new_accepted_count=0,dispersion='Excluded',family='reconstruction/families/music-mini-player-working.json',records=json.loads((P/'result.json').read_text())['records'])
(B/'selection.json').write_text(json.dumps(record,indent=2)+'\n');(R/F['selection_record']).write_text(json.dumps(record,indent=2)+'\n')
registry=json.loads((R/'reconstruction/current-models.json').read_text());meta=json.loads((R/'guide/comparison-panels.json').read_text());newmeta=json.loads((R/'guide/three-pass-comparison-panels.json').read_text())
for member in ['expanded','compact']:
 row=registry['models'][member+'-mini-player'];row.update(record=F['selection_record'],study=F['evidence'],material=f"Incident sigma {recipe['sigma']} before refraction; shared grade, narrow colored rim with opposing zero gaps, exterior shadow and original artwork transform",images=[f'assets/three101-p{number}-{member}-{r}.png' for r in ['a','b']],limits='Working approximation, not all-guard acceptance. Original failures and compact transfer differences remain; source and scene are conditional.',own_verification=str((B/'selected-verification/result.json').relative_to(R)))
 for image in row['images']:meta[image]=newmeta[image]
(R/'reconstruction/current-models.json').write_text(json.dumps(registry,indent=2)+'\n');(R/'guide/comparison-panels.json').write_text(json.dumps(meta,indent=2)+'\n')
print('Prepared selected shared family',number)
