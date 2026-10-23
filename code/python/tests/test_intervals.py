"""Soundness regressions for the exact rational interval kernel."""

from __future__ import annotations

import random
import unittest
from fractions import Fraction

from bsdkit.intervals import Interval, pi_interval


class IntervalTests(unittest.TestCase):
    def test_exact_arithmetic_contains_samples(self) -> None:
        rng = random.Random(1729)
        for _ in range(100):
            a, b, c, d = (Fraction(rng.randint(-20, 20), rng.randint(1, 10)) for _ in range(4))
            x = Interval(min(a, b), max(a, b))
            y = Interval(min(c, d), max(c, d))
            sx = Fraction(rng.randint(0, 100), 100)
            sy = Fraction(rng.randint(0, 100), 100)
            xv = x.lower + sx * x.width
            yv = y.lower + sy * y.width
            self.assertTrue((x + y).contains(xv + yv))
            self.assertTrue((x - y).contains(xv - yv))
            self.assertTrue((x * y).contains(xv * yv))
            if y.excludes_zero():
                self.assertTrue((x / y).contains(xv / yv))

    def test_elementary_composition(self) -> None:
        x = Interval(Fraction(1, 7), Fraction(13, 8))
        exponential = x.exp(100)
        self.assertTrue(
            exponential.contains(
                Fraction(
                    "1.1535649948951077534613396244718624419956877327396609515388"
                )
            )
        )
        self.assertTrue(
            exponential.contains(
                Fraction(
                    "5.0784190371800811144887489580334242873899337026252117910513"
                )
            )
        )
        self.assertTrue(exponential.log(90).contains(x))
        positive = Interval(Fraction(2, 9), Fraction(17, 3))
        root = positive.sqrt(100)
        self.assertTrue((root * root).contains(positive))

    def test_pi_and_quantisation_are_outward(self) -> None:
        enclosure = pi_interval(100)
        self.assertTrue(
            enclosure.contains(
                Fraction(
                    "3.1415926535897932384626433832795028841971693993751058209749"
                )
            )
        )
        coarse = enclosure.quantize(20)
        self.assertTrue(coarse.contains(enclosure))
        self.assertTrue(coarse.certified)

    def test_domain_failures_are_typed(self) -> None:
        with self.assertRaises(ZeroDivisionError):
            _ = Interval(-1, 1).reciprocal()
        with self.assertRaises(ValueError):
            _ = Interval(-1, 2).sqrt()
        with self.assertRaises(ValueError):
            _ = Interval(0, 2).log()


if __name__ == "__main__":
    unittest.main()
