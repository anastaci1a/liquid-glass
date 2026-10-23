"""Summarize retained paths only; no new intersections or radiance sampling."""
from pathlib import Path
import datetime,json
import numpy as np
root=Path(__file__).resolve().parents[3];out=Path(__file__).parent
p=json.loads((out/'protocol.json').read_text());assert datetime.datetime.now(datetime.timezone.utc)<datetime.datetime.fromisoformat(p['deadline'])
assert not (out/'path-audit.json').exists()
a=np.load(root/'research/experiments/clear-play-02/outline-paths.npz');r=a['r'];assert len(r)<=p['budgets']['saved_path_evaluations']
env=a['environment'];residual=a['residual'];background=a['background']
assert np.max(abs(background+env+residual+a['unresolved']-1))<3e-14
j={'status':'BLOCKED_REFLECTED_IMAGE_NOT_ABSENT_OUTLINE','selected_launches':len(r),'new_rays':0,'RGB_queries':0,'radius_range_over_L':[float(r.min()),float(r.max())],'environment_weight_range':[float(env.min()),float(env.max())],'unresolved_remaining_power_max':float(residual.max()),'launches_above_1e_minus_6':int((residual>1e-6).sum()),'hypothetical_unit_environment_contribution_max':float(env.max()),'assumptions':['Unit environment is only a conditional energy scale, not an adopted RGB or HDR environment.','Selected largest-residual launches are not a uniform or complete rim sample.','Original secondary-source failures and unobserved front environment remain blockers.'],'next_requirement':'A scene-supported reflection illumination model and complete supported paths, using the same surface. Do not paint a halo or modify normals.'}
(out/'path-audit.json').write_text(json.dumps(j,indent=2)+'\n');print(json.dumps(j))
