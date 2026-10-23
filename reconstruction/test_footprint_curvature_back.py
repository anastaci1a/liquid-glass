"""Check actual profile derivatives, circle normalization and crease status."""
import argparse,json,unittest,sys
from pathlib import Path
import numpy as np
from footprint_curvature_back import FootprintCurvatureBack
from geometric_optics import RadialCurvatureBack,trace_flat_front_orthographic
LAUNCHES=0
class FootprintCurvatureTests(unittest.TestCase):
    knots=[0,.3,.7,1.];curvature=[0,.4,1.,2.]
    def test_same_height_supplies_gradient(self):
        s=FootprintCurvatureBack((4.,1.2),1.2,self.knots,self.curvature);x=np.array([0.,3.2,3.5]);y=np.array([.5,.2,.1]);h,gx,gy,inside=s.height_gradient(x,y);eps=1e-5
        for axis,g in [(0,gx),(1,gy)]:
            dx=eps if axis==0 else 0;dy=eps if axis==1 else 0;fd=(s.height_gradient(x+dx,y+dy)[0]-s.height_gradient(x-dx,y-dy)[0])/(2*eps);np.testing.assert_allclose(fd,g,atol=1e-7,rtol=0)
        self.assertTrue(inside.all());self.assertTrue((h>=0).all())
    def test_circle_scale_matches_existing_profile(self):
        global LAUNCHES
        r=1.2;s=FootprintCurvatureBack((r,r),r,self.knots,self.curvature);reference=RadialCurvatureBack(self.knots,np.asarray(self.curvature)/r);x,y=np.meshgrid(np.linspace(-.8*r,.8*r,3),np.linspace(-.8*r,.8*r,3));a=trace_flat_front_orthographic(s,x,y,1.5,2.1);b=trace_flat_front_orthographic(reference,x/r,y/r,1.5,2.1/r);LAUNCHES+=2*x.size
        np.testing.assert_array_equal(a['complete'],b['complete']);np.testing.assert_allclose(a['X'],r*b['X'],atol=1e-12,rtol=0);np.testing.assert_allclose(a['Y'],r*b['Y'],atol=1e-12,rtol=0)
    def test_zero_thickness_remains_unresolved(self):
        global LAUNCHES
        s=FootprintCurvatureBack((4.,1.2),1.2,self.knots,[0,0,0,0]);x=np.linspace(-.5,.5,5);q=trace_flat_front_orthographic(s,x,np.zeros_like(x),1.5,2.1);LAUNCHES+=len(x)
        self.assertFalse(q['complete'].any());self.assertTrue(np.isnan(q['X']).all())
if __name__=='__main__':
    parser=argparse.ArgumentParser();parser.add_argument('--receipt',type=Path);args=parser.parse_args();r=unittest.TextTestRunner(verbosity=2).run(unittest.defaultTestLoader.loadTestsFromTestCase(FootprintCurvatureTests));out=dict(status='PASS' if r.wasSuccessful() else 'FAIL',tests=r.testsRun,fixture_rays=LAUNCHES,RGB_queries=0)
    if args.receipt:args.receipt.write_text(json.dumps(out,indent=2)+'\n')
    print(json.dumps(out));sys.exit(not r.wasSuccessful())
