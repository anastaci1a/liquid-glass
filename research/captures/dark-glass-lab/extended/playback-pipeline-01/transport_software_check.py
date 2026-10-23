from pathlib import Path
import time,json,unittest,numpy as np
import geometric_optics as g
START=time.time();D=Path('/evidence/extended/playback-pipeline-01/outline');counter={'attempted_Snell_rows':0,'attempted_ordered_segments':0};oldr=g.refract;oldb=g.next_convex_boundary

def rr(i,n,a,b):
 count=np.broadcast_arrays(np.asarray(i)[...,0],np.asarray(n)[...,0])[0].size
 if counter['attempted_Snell_rows']+count>10000:raise RuntimeError('Software Snell budget would be exceeded')
 counter['attempted_Snell_rows']+=count;return oldr(i,n,a,b)
def bb(s,p,d,*args,**kwargs):
 count=len(p)
 if counter['attempted_ordered_segments']+count>10000:raise RuntimeError('Software segment budget would be exceeded')
 counter['attempted_ordered_segments']+=count;return oldb(s,p,d,*args,**kwargs)
g.refract=rr;g.next_convex_boundary=bb
names=['test_geometric_transport','test_geometric_optics.GeometryTests.test_closed_ellipsoid_intersections_and_identity','test_geometric_optics.GeometryTests.test_closed_surface_gradient_and_branch_status','test_geometric_optics.GeometryTests.test_shared_circle_fixtures_for_crowned_adapters','test_geometric_render.CoverageFilterTest','test_geometric_render.NeutralResponseTest'];suite=unittest.defaultTestLoader.loadTestsFromNames(names);result=unittest.TextTestRunner(verbosity=1).run(suite);assert time.time()-START<300;out={'passed':result.wasSuccessful(),'tests':result.testsRun,'failed':len(result.failures),'errors':len(result.errors),**counter,'wall_seconds':time.time()-START,'source_queries':0,'RGB_sampling':0,'candidate_images':0,'O1_extended':False};(D/'software-validation.json').write_text(json.dumps(out,indent=2)+'\n');print(json.dumps(out));raise SystemExit(0 if out['passed'] else 1)
