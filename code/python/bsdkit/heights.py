"""Naive and canonical heights, pairings, regulators, and real periods.

The canonical-height enclosure uses the defining Tate limit

``hhat(P) = lim h_x(2**n P)/(2*4**n)``.

A uniform error constant is derived from exact Bézout identities for the two
homogeneous duplication polynomials.  This is deliberately slower than the
local-height algorithm in production systems, but it is self-contained and
gives a genuine rational error bound.  The convenience real-period routine uses
``mpmath`` quadrature and is therefore tagged ``numerical``, never ``proved``.
"""

from __future__ import annotations

from dataclasses import dataclass
from fractions import Fraction
from functools import lru_cache
from itertools import permutations
from math import lcm
from typing import Iterable, Sequence

from .ellcurve import EllipticCurve, Point, Rigour
from .intervals import Interval

Polynomial = list[Fraction]


def naive_height(point: Point) -> Interval:
    """Return the logarithmic projective height of the x-coordinate."""

    if point.infinity:
        return Interval.exact(0)
    size = max(abs(point.x.numerator), point.x.denominator)
    return Interval.exact(size).log()


def _trim(poly: Polynomial) -> Polynomial:
    while len(poly) > 1 and poly[-1] == 0:
        poly.pop()
    return poly


def _add(left: Polynomial, right: Polynomial) -> Polynomial:
    size = max(len(left), len(right))
    answer = [Fraction(0)] * size
    for i in range(size):
        answer[i] = (left[i] if i < len(left) else 0) + (
            right[i] if i < len(right) else 0
        )
    return _trim(answer)


def _neg(poly: Polynomial) -> Polynomial:
    return [-value for value in poly]


def _mul(left: Polynomial, right: Polynomial) -> Polynomial:
    answer = [Fraction(0)] * (len(left) + len(right) - 1)
    for i, a in enumerate(left):
        for j, b in enumerate(right):
            answer[i + j] += a * b
    return _trim(answer)


def _scale(poly: Polynomial, scalar: Fraction) -> Polynomial:
    return _trim([scalar * value for value in poly])


def _divmod(numerator: Polynomial, denominator: Polynomial) -> tuple[Polynomial, Polynomial]:
    numerator = _trim(numerator[:])
    denominator = _trim(denominator[:])
    if denominator == [0]:
        raise ZeroDivisionError
    if len(numerator) < len(denominator):
        return [Fraction(0)], numerator
    quotient = [Fraction(0)] * (len(numerator) - len(denominator) + 1)
    while numerator != [0] and len(numerator) >= len(denominator):
        degree = len(numerator) - len(denominator)
        coefficient = numerator[-1] / denominator[-1]
        quotient[degree] += coefficient
        subtraction = [Fraction(0)] * degree + _scale(denominator, coefficient)
        numerator = _add(numerator, _neg(subtraction))
    return _trim(quotient), _trim(numerator)


def _bezout(left: Polynomial, right: Polynomial) -> tuple[Polynomial, Polynomial]:
    """Return A,B with A*left+B*right = 1."""

    old_r, r = _trim(left[:]), _trim(right[:])
    old_s, s = [Fraction(1)], [Fraction(0)]
    old_t, t = [Fraction(0)], [Fraction(1)]
    while r != [0]:
        quotient, remainder = _divmod(old_r, r)
        old_r, r = r, remainder
        old_s, s = s, _add(old_s, _neg(_mul(quotient, s)))
        old_t, t = t, _add(old_t, _neg(_mul(quotient, t)))
    if len(old_r) != 1 or old_r[0] == 0:
        raise ArithmeticError("singular duplication polynomials")
    factor = Fraction(1, 1) / old_r[0]
    return _scale(old_s, factor), _scale(old_t, factor)


def _denominator_lcm(polys: Iterable[Polynomial]) -> int:
    value = 1
    for poly in polys:
        for coefficient in poly:
            value = lcm(value, coefficient.denominator)
    return value


@lru_cache(maxsize=128)
def _duplication_height_constant(curve: EllipticCurve, bits: int = 160) -> Fraction:
    """Return an exact rational upper bound for ``|h(2P)-4h(P)|``."""

    f = [
        Fraction(-curve.b8),
        Fraction(-2 * curve.b6),
        Fraction(-curve.b4),
        Fraction(0),
        Fraction(1),
    ]
    g = [
        Fraction(curve.b6),
        Fraction(2 * curve.b4),
        Fraction(curve.b2),
        Fraction(4),
        Fraction(0),
    ]
    a, b = _bezout(f, g)
    reverse_f, reverse_g = list(reversed(f)), list(reversed(g))
    reverse_a, reverse_b = _bezout(reverse_f, reverse_g)
    denominator_bound = _denominator_lcm((a, b)) * _denominator_lcm(
        (reverse_a, reverse_b)
    )
    bezout_bound = max(
        sum(abs(value) for value in a) + sum(abs(value) for value in b),
        sum(abs(value) for value in reverse_a)
        + sum(abs(value) for value in reverse_b),
    )
    upper_coefficient_bound = max(
        1 + abs(curve.b4) + 2 * abs(curve.b6) + abs(curve.b8),
        4 + abs(curve.b2) + 2 * abs(curve.b4) + abs(curve.b6),
    )
    distortion = max(
        Fraction(upper_coefficient_bound),
        bezout_bound * denominator_bound,
        Fraction(1),
    )
    return Interval.exact(distortion).log(bits).upper


@lru_cache(maxsize=2048)
def canonical_height(
    curve: EllipticCurve, point: Point, doublings: int = 4, bits: int = 160
) -> Interval:
    """Enclose the Néron--Tate height via the Tate limit.

    The tail after ``doublings`` is at most ``C/(6*4**doublings)``, where
    ``C`` is an exact duplication-height distortion bound derived from Bézout
    identities.  Torsion detected before the cutoff has height exactly zero.
    """

    if not curve.is_on_curve(point):
        raise ValueError("point is not on the curve")
    if point.infinity:
        return Interval.exact(0)
    current = point
    for _ in range(doublings):
        current = curve.add(current, current)
        if current.infinity:
            return Interval.exact(0)
    central = naive_height(current) / (2 * 4**doublings)
    error = _duplication_height_constant(curve, bits) / (6 * 4**doublings)
    return central.enlarge(error).quantize(bits)


@dataclass(frozen=True, slots=True)
class LocalHeightBundle:
    """A transparent status record for the local-height decomposition."""

    finite: dict[int, Interval]
    archimedean: Interval
    total: Interval
    rigour: Rigour


def local_heights(
    curve: EllipticCurve, point: Point, doublings: int = 4
) -> LocalHeightBundle:
    """Return a conservative local-height bundle.

    This compact reference kernel certifies the global Tate-limit enclosure but
    does not implement every Néron component correction separately.  It records
    an empty finite decomposition and the certified total as an archimedean
    placeholder, with ``numerical`` rigour for the decomposition itself.
    """

    total = canonical_height(curve, point, doublings)
    return LocalHeightBundle({}, total, total, "numerical")


def height_pairing_matrix(
    curve: EllipticCurve, points: Sequence[Point], doublings: int = 4
) -> tuple[tuple[Interval, ...], ...]:
    """Return a symmetric interval enclosure of the height Gram matrix."""

    heights = [canonical_height(curve, point, doublings) for point in points]
    matrix: list[list[Interval]] = [
        [Interval.exact(0) for _ in points] for _ in points
    ]
    for i, height in enumerate(heights):
        matrix[i][i] = height
        for j in range(i):
            pair_sum = canonical_height(
                curve, curve.add(points[i], points[j]), doublings
            )
            value = (pair_sum - heights[i] - heights[j]) / 2
            matrix[i][j] = matrix[j][i] = value
    return tuple(tuple(row) for row in matrix)


def interval_determinant(matrix: Sequence[Sequence[Interval]]) -> Interval:
    """Compute a small interval determinant by the Leibniz formula."""

    size = len(matrix)
    if any(len(row) != size for row in matrix):
        raise ValueError("determinant requires a square matrix")
    if size == 0:
        return Interval.exact(1)
    answer = Interval.exact(0)
    for permutation in permutations(range(size)):
        inversions = sum(
            1
            for i in range(size)
            for j in range(i + 1, size)
            if permutation[i] > permutation[j]
        )
        term = Interval.exact(-1 if inversions % 2 else 1)
        for row, column in enumerate(permutation):
            term *= matrix[row][column]
        answer += term
    return answer


def regulator(
    curve: EllipticCurve, points: Sequence[Point], doublings: int = 4
) -> Interval:
    """Return an interval determinant for the Néron--Tate regulator."""

    return interval_determinant(height_pairing_matrix(curve, points, doublings))


def points_are_independent(
    curve: EllipticCurve, points: Sequence[Point], doublings: int = 4
) -> bool:
    """Certify independence when the regulator interval excludes zero."""

    return regulator(curve, points, doublings).excludes_zero()


def real_period(curve: EllipticCurve, digits: int = 70) -> Interval:
    """Numerically evaluate the real Néron period using ``mpmath``.

    ``mpmath`` does not expose a proof-producing directed-rounding transcript;
    the returned narrow interval is therefore explicitly non-certified.  It is
    intended for numerical BSD consistency tests, never theorem discharge.
    """

    try:
        import mpmath as mp
    except ImportError as error:  # pragma: no cover - environment diagnostic
        raise RuntimeError("real_period requires the optional mpmath package") from error

    mp.mp.dps = digits + 20
    roots = mp.polyroots(
        [mp.mpf(4), mp.mpf(curve.b2), mp.mpf(2 * curve.b4), mp.mpf(curve.b6)],
        maxsteps=500,
        error=False,
    )
    real_roots = [mp.re(root) for root in roots if abs(mp.im(root)) < mp.mpf(10) ** (-digits)]
    if not real_roots:
        raise ArithmeticError("failed to isolate a real cubic root")
    root = max(real_roots)

    def cubic(x: object) -> object:
        return 4 * x**3 + curve.b2 * x**2 + 2 * curve.b4 * x + curve.b6

    derivative = 12 * root**2 + 2 * curve.b2 * root + 2 * curve.b4

    def integrand(t: object) -> object:
        if t == 0:
            return 4 / mp.sqrt(derivative)
        x = root + t * t
        return 4 * t / mp.sqrt(cubic(x))

    value = mp.re(mp.quad(integrand, [0, 1, mp.inf]))
    if len(real_roots) == 3:
        # The BSD real period integrates over both real components.
        value *= 2
    decimal = mp.nstr(value, digits)
    midpoint = Fraction(decimal)
    radius = Fraction(1, 10 ** (digits - 4))
    return Interval.from_midpoint_radius(midpoint, radius, certified=False)
