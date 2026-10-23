"""Exact arithmetic, local reduction, trace, and rank regressions."""

from __future__ import annotations

import unittest

from bsdkit.data import RUNNING_CURVES
from bsdkit.frobenius import count_points_bsgs, count_points_naive, frobenius_trace
from bsdkit.heights import points_are_independent, regulator
from bsdkit.reduction import bad_reduction_data, conductor, global_root_number


class RunningCurveTests(unittest.TestCase):
    def test_invariants_rank_torsion_and_sign(self) -> None:
        for record in RUNNING_CURVES.values():
            with self.subTest(curve=record.label):
                minimal = record.curve.minimal_model()
                self.assertEqual(minimal.rigour, "proved")
                self.assertEqual(minimal.curve, record.curve)
                self.assertEqual(conductor(record.curve), (record.expected_conductor, "proved"))
                self.assertEqual(global_root_number(record.curve), (record.expected_sign, "proved"))
                torsion = record.curve.torsion_subgroup()
                self.assertEqual(torsion.rigour, "proved")
                self.assertEqual(torsion.order_lower, record.expected_torsion)
                self.assertEqual(torsion.order_upper, record.expected_torsion)
                self.assertEqual(len(record.generators), record.expected_rank)
                self.assertTrue(all(record.curve.is_on_curve(p) for p in record.generators))
                if record.generators:
                    self.assertTrue(points_are_independent(record.curve, record.generators))
                    self.assertGreater(regulator(record.curve, record.generators).lower, 0)

    def test_tate_data_at_every_bad_prime(self) -> None:
        for record in RUNNING_CURVES.values():
            for local in bad_reduction_data(record.curve):
                with self.subTest(curve=record.label, prime=local.prime):
                    self.assertEqual(local.rigour, "proved")
                    self.assertEqual(local.conductor_exponent, 1)
                    self.assertEqual(local.kodaira, f"I{local.discriminant_exponent}")
                    expected_tamagawa = (
                        local.discriminant_exponent
                        if local.split
                        else (1 if local.discriminant_exponent % 2 else 2)
                    )
                    self.assertEqual(local.tamagawa, expected_tamagawa)

    def test_frobenius_two_exact_methods(self) -> None:
        for record in RUNNING_CURVES.values():
            for prime in (3, 5, 7, 13):
                if record.curve.discriminant % prime == 0:
                    continue
                with self.subTest(curve=record.label, prime=prime):
                    naive = count_points_naive(record.curve, prime)
                    bsgs = count_points_bsgs(record.curve, prime)
                    trace = frobenius_trace(record.curve, prime)
                    self.assertEqual(naive, bsgs)
                    self.assertEqual(trace, prime + 1 - naive)
                    self.assertLessEqual(trace * trace, 4 * prime)


if __name__ == "__main__":
    unittest.main()
