"""Independent default-compatibility and same-surface derivative checks."""
import argparse,json,sys,unittest
from pathlib import Path
import numpy as np
from geometric_optics import trace_closed_orthographic,trace_flat_front_orthographic
from rounded_rectangle_back import RoundedRectangleHarmonicBack
from parabolic_front_solid import ParabolicFrontHeightSolid

SOLIDS=[];LAUNCHES=0
class ParabolicFrontTests(unittest.TestCase):
    def setUp(self):self.back=RoundedRectangleHarmonicBack((7.225022904390323,1.012503164339156),1.0043663048754772)
    def solid(self,depth=.4):
        s=ParabolicFrontHeightSolid(self.back,depth);SOLIDS.append(s);return s
    def test_validated_bounds(self):
        for depth in [-1,np.nan]:
            with self.assertRaises(ValueError):ParabolicFrontHeightSolid(self.back,depth)
        s=self.solid();self.assertAlmostEqual(s.center[2]+s.half_extents[2],.4);self.assertAlmostEqual(s.center[2]-s.half_extents[2],-self.back.maximum_height)
    def test_sections_are_actual_boundaries(self):
        s=self.solid()
        for axis,half in zip(['x','y'],self.back.half):
            cut=s.section(np.linspace(-half,half,9),axis)
            for name in ['front','back']:np.testing.assert_allclose(s.level_gradient(cut[name])[0],0,atol=1e-12,rtol=0)
    def test_level_gradient_matches_finite_difference(self):
        s=self.solid();x,y=3.2,.3;points=np.array([[x,y,s._front(x,y)[0]],[x,y,-self.back.height_gradient(x,y)[0]]]);_,g=s.level_gradient(points);eps=1e-5
        for axis in range(3):
            d=np.eye(3)[axis]*eps;fd=(s.level_gradient(points+d)[0]-s.level_gradient(points-d)[0])/(2*eps);np.testing.assert_allclose(fd,g[:,axis],atol=1e-7,rtol=0)
    def test_default_zero_front_preserves_analytic_paths(self):
        global LAUNCHES
        x,y=np.meshgrid(np.linspace(-.85*self.back.half[0],.85*self.back.half[0],7),np.linspace(-.8,.8,6));LAUNCHES+=2*x.size
        a=trace_closed_orthographic(self.solid(0),x,y,1.5,2);b=trace_flat_front_orthographic(self.back,x,y,1.5,2)
        np.testing.assert_array_equal(a['complete'],b['complete']);np.testing.assert_allclose(a['X'],b['X'],atol=1e-9,rtol=0);np.testing.assert_allclose(a['Y'],b['Y'],atol=1e-9,rtol=0)
    def test_side_crease_is_not_a_smoothed_normal(self):
        s=self.solid();y=self.back.half[1];points=np.array([[0,y,.4],[0,y,.2]])
        self.assertTrue(s.boundary_mask(0.,y));np.testing.assert_array_equal(s.nonsmooth_mask(points,np.array([1e-11,1e-11])),[True,False])

if __name__=='__main__':
    parser=argparse.ArgumentParser();parser.add_argument('--receipt',type=Path);args=parser.parse_args();result=unittest.TextTestRunner(verbosity=2).run(unittest.defaultTestLoader.loadTestsFromTestCase(ParabolicFrontTests))
    receipt=dict(status='PASS' if result.wasSuccessful() else 'FAIL',tests=result.testsRun,launches=LAUNCHES,level_points=sum(s.level_point_evaluations for s in SOLIDS),height_points=sum(s.height_point_evaluations for s in SOLIDS),new_RGB_queries=0)
    if args.receipt:args.receipt.write_text(json.dumps(receipt,indent=2)+'\n')
    print(json.dumps(receipt));sys.exit(not result.wasSuccessful())
