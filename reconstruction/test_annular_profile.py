"""Domain and same-height derivative controls for the shared physical profile."""
import unittest
import numpy as np
from annular_profile import annular_level_profile
class AnnularProfileTests(unittest.TestCase):
    def test_physical_domain_and_endpoint(self):
        for depth,ratio in [(0.,.1),(.4,0.),(.4,1.),(float('nan'),.1)]:
            with self.assertRaises(ValueError):annular_level_profile(.2,depth,ratio)
        for t in [-.01,1.01,float('nan')]:
            with self.assertRaises(ValueError):annular_level_profile(t,.4,.1)
        h,ht,_=annular_level_profile(np.array([0.,.45,1.]),.4,.1)
        self.assertEqual(h[-1],0.);self.assertGreater(h[0],0.);self.assertGreater(ht[0],0.);self.assertLess(ht[-1],0.)
        self.assertAlmostEqual(h[1],.121)
    def test_gradient_and_global_radial_bound(self):
        t=np.linspace(.001,.999,129);e=1e-6
        h,ht,htt=annular_level_profile(t,.4,.1)
        plus=annular_level_profile(t+e,.4,.1);minus=annular_level_profile(t-e,.4,.1)
        np.testing.assert_allclose((plus[0]-minus[0])/(2*e),ht,atol=4e-11,rtol=0)
        np.testing.assert_allclose((plus[1]-minus[1])/(2*e),htt,atol=1e-10,rtol=0)
        self.assertTrue(np.all(2*np.sqrt(t)*abs(ht)<=.88))
if __name__=='__main__':unittest.main()
