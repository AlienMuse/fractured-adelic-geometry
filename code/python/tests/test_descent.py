"""Scope and honesty tests for descent and rank decisions."""

from __future__ import annotations

import unittest

from bsdkit.data import get_curve
from bsdkit.descent import determine_rank, point_search, two_isogeny_descent
from bsdkit.ellcurve import EllipticCurve


class DescentTests(unittest.TestCase):
    def test_point_search_certifies_running_lower_bounds(self) -> None:
        for label in ("11.a1", "37.a1", "37.b1", "389.a1", "5077.a1"):
            record = get_curve(label)
            with self.subTest(curve=label):
                result = point_search(record.curve)
                self.assertEqual(result.rigour, "proved")
                self.assertEqual(result.lower_bound, record.expected_rank)

    def test_general_case_stays_undetermined_without_upper_bound(self) -> None:
        result = determine_rank(get_curve("389.a1").curve)
        self.assertEqual(result.lower_bound, 2)
        self.assertIsNone(result.upper_bound)
        self.assertEqual(result.verdict, "undetermined")
        self.assertIsNone(result.rank)

    def test_rational_two_torsion_selects_isogeny_path(self) -> None:
        curve = EllipticCurve([0, 0, 0, -1, 0])
        result = two_isogeny_descent(curve)
        self.assertFalse(result.rational_two_torsion.infinity)
        self.assertEqual(result.a_coefficient, 0)
        self.assertEqual(result.b_coefficient, -1)
        self.assertTrue(result.phi_classes)
        self.assertTrue(result.dual_classes)
        self.assertEqual(result.rigour, "proved")
        self.assertEqual(result.rank_upper_bound, 0)


if __name__ == "__main__":
    unittest.main()
