"""Incident PSF support and compression; no Apple target or image fitting."""
import unittest
import cv2
import numpy as np
from geometric_render import incident_source_filter


class IncidentFilterTest(unittest.TestCase):
    def test_zero_identity_and_unknown_rejection(self):
        source = np.full((33, 41, 3), .4)
        known = np.ones(source.shape[:2], bool)
        known[12, 13] = False
        filtered, support, radius = incident_source_filter(source, known, 0)
        np.testing.assert_array_equal(filtered[known], source[known])
        np.testing.assert_array_equal(support, known)
        self.assertTrue(np.isnan(filtered[~known]).all())
        self.assertEqual(radius, 0)

    def test_full_kernel_support_and_uniform_field(self):
        source = np.full((51, 61, 3), .4)
        known = np.ones(source.shape[:2], bool)
        known[25, 30] = False
        source[25, 30] = np.nan
        filtered, support, radius = incident_source_filter(source, known, 1.7)
        self.assertEqual(radius, 6)
        self.assertFalse(support[19:32, 24:37].any())
        self.assertFalse(support[:6].any())
        self.assertTrue(support[18, 30])
        np.testing.assert_allclose(filtered[support], .4, atol=2e-15)
        self.assertTrue(np.isnan(filtered[~support]).all())

    def test_compression_changes_image_space_width(self):
        source = np.zeros((81, 401, 3))
        source[:, 200:] = 1
        filtered, _, _ = incident_source_filter(source, np.ones((81, 401)), 3)
        def width(v):
            x = np.arange(len(v))
            return np.interp(.9, v, x) - np.interp(.1, v, x)
        ordinary = filtered[40, 120:281, 0]
        compressed = filtered[40, 40:361:2, 0]
        self.assertLess(width(compressed), .55 * width(ordinary))
        self.assertGreater(width(compressed), .45 * width(ordinary))
        # This fixture uses a declared affine map, not a new rendering warp.


if __name__ == '__main__':
    unittest.main()
