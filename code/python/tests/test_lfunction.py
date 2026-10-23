"""Certified central values and the rank-zero BSD consistency check."""

from __future__ import annotations

import unittest

from bsdkit.data import get_curve
from bsdkit.heights import real_period
from bsdkit.lfunction import certified_l_derivative
from bsdkit.reduction import bad_reduction_data


class LFunctionTests(unittest.TestCase):
    def test_central_nonvanishing_and_sign_forced_zero(self) -> None:
        nonzero = certified_l_derivative(get_curve("11.a1").curve, 0, 44)
        self.assertEqual(nonzero.rigour, "proved")
        self.assertTrue(nonzero.interval.excludes_zero())
        zero = certified_l_derivative(get_curve("37.a1").curve, 0, 44)
        self.assertEqual(zero.rigour, "proved")
        self.assertTrue(zero.interval.contains(0))
        self.assertEqual(zero.interval.width, 0)

    def test_rank_two_central_interval_does_not_claim_vanishing(self) -> None:
        result = certified_l_derivative(get_curve("389.a1").curve, 0, 36)
        self.assertEqual(result.rigour, "proved")
        self.assertTrue(result.interval.contains(0))
        self.assertGreater(result.interval.width, 0)

    def test_rank_zero_bsd_leading_term_for_11a1(self) -> None:
        record = get_curve("11.a1")
        lvalue = certified_l_derivative(record.curve, 0, 52).interval
        period = real_period(record.curve, 50)
        torsion = record.curve.torsion_subgroup().order_lower
        tamagawa = 1
        for local in bad_reduction_data(record.curve):
            tamagawa *= local.tamagawa
        quotient = (
            float(lvalue.midpoint)
            * torsion
            * torsion
            / (float(period.midpoint) * tamagawa)
        )
        # The nearest integer is isolated numerically; this test checks the
        # classical rank-zero leading-term identity, not a general BSD proof.
        self.assertEqual(round(quotient), 1)
        self.assertAlmostEqual(quotient, 1.0, places=11)
        self.assertFalse(period.certified)


if __name__ == "__main__":
    unittest.main()
