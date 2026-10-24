"""Synthetic graph-clearance guards, not another optical ray study."""
import numpy as np
import unittest
from raised_front_optics import escape_clearance


def check_normal_escape_and_lateral_reentry_ambiguity():
    directions = np.array([[0., 0., -1.], [.8, 0., -.6], [.99, 0., -.1]])
    margins = escape_clearance(directions, .5)
    np.testing.assert_allclose(margins, [1., .2, -.395], rtol=0, atol=1e-15)
    assert margins[-1] < 0  # Failure is unresolved geometry, not a replacement path.


def check_front_sign_and_equal_slope_critical_case():
    directions = np.array([[0., 0., 1.], [.8, 0., .4]])
    np.testing.assert_array_equal(escape_clearance(directions, .5, upward=True), [1., 0.])


class ClearanceTests(unittest.TestCase):
    def test_directions(self):
        check_normal_escape_and_lateral_reentry_ambiguity()
    def test_front_and_critical(self):
        check_front_sign_and_equal_slope_critical_case()
    def test_nonfinite(self):
        with self.assertRaises(ValueError):
            escape_clearance(np.array([np.nan, 0., -1.]), .5)

if __name__ == "__main__":
    unittest.main()
