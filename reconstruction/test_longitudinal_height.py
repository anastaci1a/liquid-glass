"""Product-rule, boundary and scale invariants; no tracing or image fixture."""
import unittest
import numpy as np
from spline_height_back import SplineFootprintBack
from longitudinal_height import LongitudinalHeight


class LongitudinalHeightTests(unittest.TestCase):
    evaluations = 0

    def base(self, scale=1.):
        owner = self
        class CountedSpline(SplineFootprintBack):
            def charge(self, x, y):
                type(owner).evaluations += np.broadcast_arrays(x, y)[0].size
                if type(owner).evaluations > 1000:
                    raise AssertionError('Height/boundary evaluation cap')
            def height_gradient(self, x, y):
                self.charge(x, y)
                return super().height_gradient(x, y)
            def boundary_mask(self, x, y):
                self.charge(x, y)
                return super().boundary_mask(x, y)
        return CountedSpline((2 * scale, scale), scale,
            [0, .2, .4, .6, .8, .9, .97, .99, 1],
            np.asarray([.14, .14, .13, .135, .12, .1, .06, .03, .01, .002, 0]) * scale)

    def test_gradient_and_bounds(self):
        x = np.array([-.7, -.3, 0, .3, .7, 1.2, 1.5])
        y = np.array([.2, .4, .6, -.4, -.2, .3, .2])
        for strength in [-.1, .1]:
            s = LongitudinalHeight(self.base(), strength)
            h, hx, hy, inside = s.height_gradient(x, y)
            step = 1e-6
            for dx, dy, expected in [(step, 0, hx), (0, step, hy)]:
                actual = (s.height_gradient(x + dx, y + dy)[0]
                          - s.height_gradient(x - dx, y - dy)[0]) / (2 * step)
                np.testing.assert_allclose(actual, expected, atol=2e-9, rtol=0)
            self.assertTrue(inside.all())
            self.assertTrue(np.all((h >= 0) & (h <= s.maximum_height)))
            self.assertTrue(np.all(np.hypot(hx, hy) <= s.slope_bound))

    def test_identity_boundary_center_and_sections(self):
        b = self.base()
        x, y = np.array([-2., -.5, 0, .5, 2., 3.]), np.zeros(6)
        for actual, expected in zip(LongitudinalHeight(b, 0).height_gradient(x, y), b.height_gradient(x, y)):
            np.testing.assert_array_equal(actual, expected)
        for strength in [-.1, .1]:
            s = LongitudinalHeight(b, strength)
            np.testing.assert_array_equal(s.boundary_mask(x, y), b.boundary_mask(x, y))
            for actual, expected in zip(s.height_gradient(0., .3), b.height_gradient(0., .3)):
                np.testing.assert_array_equal(actual, expected)
            section = s.section(x)
            np.testing.assert_array_equal(section['back'][:, 2][section['inside']],
                                          -s.height_gradient(x, y)[0][section['inside']])

    def test_scale_mirror_and_invalid_strength(self):
        x, y = np.array([-.8, .2, 1.3]), np.array([.3, -.6, .2])
        s, scaled = LongitudinalHeight(self.base(), .1), LongitudinalHeight(self.base(3), .1)
        h, hx, hy, inside = s.height_gradient(x, y)
        H, Hx, Hy, Inside = scaled.height_gradient(3 * x, 3 * y)
        np.testing.assert_allclose(H, 3 * h, atol=2e-15, rtol=0)
        np.testing.assert_allclose(Hx, hx, atol=2e-15, rtol=0)
        np.testing.assert_allclose(Hy, hy, atol=2e-15, rtol=0)
        hm, hxm, hym, _ = s.height_gradient(-x, y)
        np.testing.assert_array_equal(hm, h)
        np.testing.assert_array_equal(hxm, -hx)
        np.testing.assert_array_equal(hym, hy)
        for strength in [-1, 1, float('nan'), float('inf')]:
            with self.assertRaises(ValueError):
                LongitudinalHeight(self.base(), strength)


if __name__ == '__main__':
    unittest.main()
