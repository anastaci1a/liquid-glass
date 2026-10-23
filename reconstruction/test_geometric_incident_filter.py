"""Incident PSF support and compression; no Apple target or image fitting."""
import unittest
import cv2
import numpy as np
from geometric_render import incident_source_filter,render_rows
from geometric_optics import CircularBevel


class IncidentFilterTest(unittest.TestCase):
    def test_exact_sample_cache_preserves_integration_order(self):
        source=np.random.default_rng(23).uniform(0,1,(81,81,3)).astype(np.float32)
        case={'crop':[20,20,60,60],'center':[40,40],'half':[10,10]}
        image,_,layers=render_rows(source,case,{},CircularBevel(depth=.02),1.5,2.,0,40,raw_transmission=True,exact_bilinear=True,samples_per_axis=2,return_layers=True,return_samples=True)
        replay=layers['sample_rgb'].reshape(40,2,40,2,3).mean((1,3)).astype(np.float32)
        np.testing.assert_array_equal(replay,image)
        np.testing.assert_array_equal(layers['sample_inside'].reshape(40,2,40,2).mean((1,3)),layers['coverage'])
        self.assertEqual(layers['source_X'].shape,(80,80))

    def test_incident_layer_preserves_clear_exterior_and_zero(self):
        source=np.full((81,81,3),.4)
        known=np.ones((81,81),bool)
        case={'crop':[20,20,60,60],'center':[40,40],'half':[10,10]}
        args=(source,case,{},CircularBevel(depth=.02),1.5,2.,0,40)
        opts=dict(raw_transmission=True,exact_bilinear=True,samples_per_axis=2,source_known=known,return_layers=True)
        original,_,layers=render_rows(*args,**opts)
        zero,_,_=render_rows(*args,**opts,incident_source=source,incident_known=known)
        np.testing.assert_array_equal(original,zero)
        changed,_,_=render_rows(*args,**opts,incident_source=np.full_like(source,.2),incident_known=known)
        alpha=layers['coverage']
        np.testing.assert_array_equal(original[alpha==0],changed[alpha==0])
        np.testing.assert_allclose(changed[...,0],.4-.2*alpha,atol=2e-8)
        bad=known.copy();bad[40,40]=False
        with self.assertRaisesRegex(ValueError,'Unsupported finite incident'):
            render_rows(*args,**opts,incident_source=source,incident_known=bad)

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
