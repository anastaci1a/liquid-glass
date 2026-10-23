"""Only failed fixture corrected. Earlier completed geometry checks not repeated."""
import json,copy,hashlib,sys
from pathlib import Path
sys.path.insert(0,'/tmp/agent-toolbar-code')
import numpy as np
import toolbar_back_surface as m
out=Path('/tmp/agent-toolbar-back-surface');p=json.loads(Path('/tmp/agent-toolbar-evidence-package/recipe.json').read_text());p['back_surface']={'thickness':.5,'background':2.5,'ior':1.5,'b_major':-.012,'b_minor':.018,'quartic':-.12}
p['material']=[1.,1.,1.]+[0.]*(len(p['material'])-6)+[1.,1.,1.]
C,a=m.render(np.full((1080,1920,3),.5,float),p['case'],p);err=float(np.max(np.abs(C[a>0]-.5)));assert err<1e-6
report={'stage1_before_fixture_failure':{'analytic_gradient_error_asserted_less_than':1e-8,'Snell_mirror_rotation_scale_circle_errors_asserted_less_than':1e-12,'flat_surface_identity_exact_assertion_passed':True,'parameter_box_all8corners_height_slope_clearance_and_Snell_assertions_passed':True,'invalid_TIR_rejection_assertion_passed':True,'evidence':'test-before-uniform-fixture-fix.py reached uniform assertion line23; preceding assertions passed. Numeric maxima were not flushed before failure, so bounds are reported instead, not invented values.'},'failed_fixture':{'fixture':'allzero material','expected_in_test':.5,'actual_semantics':'zero gain plus zero offsets produces black; test setup invalid','model_changed':False,'retained':True},'corrected_fixture':{'neutral_unit_gain':True,'uniform_source_max_error':err,'asserted_below':1e-6,'new_target_pixels_used':0},'model_sha256':hashlib.sha256(Path('/tmp/agent-toolbar-code/toolbar_back_surface.py').read_bytes()).hexdigest(),'completed_geometry_checks_repeated':False,'counted_passes':0}
(out/'invariants.json').write_text(json.dumps(report,indent=2)+'\n');print('INVARIANTS_COMPLETE',json.dumps(report),flush=True)
