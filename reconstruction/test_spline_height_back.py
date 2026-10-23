"""Positive basis and global derivative certificates; no image/ray fixture."""
import unittest
import numpy as np
from spline_height_back import SplineFootprintBack
class SplineHeightTests(unittest.TestCase):
    def setUp(self):
        self.breaks=[0,.2,.4,.6,.8,.9,.97,.99,1]
        self.controls=[.14,.14,.13,.135,.12,.1,.06,.03,.01,.002,0.]
    def test_basis_bounds_and_regular_center(self):
        s=SplineFootprintBack((2.,1.),1.,self.breaks,self.controls)
        r=np.linspace(0,1,129);h=s.profile(r);derivative=s.radial_derivative(r)
        self.assertTrue(np.all(h>=0));self.assertTrue(np.all(h<=s.maximum_height))
        self.assertTrue(np.all(abs(derivative)<=s.slope_bound))
        self.assertEqual(derivative[0],0.);self.assertEqual(h[-1],0.)
        self.assertTrue(np.all(h[:-1]>0))
    def test_reject_unphysical_control_or_join(self):
        for index,value in [(0,-.1),(1,.15),(-1,.01)]:
            c=self.controls.copy();c[index]=value
            with self.assertRaises(ValueError):SplineFootprintBack((2.,1.),1.,self.breaks,c)
if __name__=='__main__':unittest.main()
