"""Certified rank bounds and the classical rational-2-torsion descent.

For a rational point of order two, the curve is transformed exactly to
``v^2 = u^3 + A*u^2 + B*u`` and both isogeny squareclass groups are enumerated.
Local quartics are tested by exhaustive residue trees.  A class for which the
implemented Hensel criterion is inconclusive makes the whole upper bound
``heuristic``/unavailable; a timeout is never interpreted as insolubility.

For curves without rational 2-torsion this lightweight package implements only
the exact point-search lower bound.  General cubic-algebra 2-descent needs
certified class groups and local Kummer images and is deliberately reported as
an obstruction, not simulated from the authorised regression ranks.
"""

from __future__ import annotations

from dataclasses import dataclass
from fractions import Fraction
from itertools import combinations
from math import gcd, isqrt
from typing import Literal, Sequence

from .ellcurve import EllipticCurve, Point, Rigour, factor_integer
from .heights import points_are_independent, regulator


@dataclass(frozen=True, slots=True)
class SelmerClass:
    """A squareclass and its local quartic decisions."""

    representative: int
    local_status: tuple[tuple[str, str], ...]
    accepted: bool | None


@dataclass(frozen=True, slots=True)
class TwoIsogenyDescent:
    """The two isogeny Selmer presentations and resulting upper bound."""

    rational_two_torsion: Point
    a_coefficient: int
    b_coefficient: int
    phi_classes: tuple[SelmerClass, ...]
    dual_classes: tuple[SelmerClass, ...]
    phi_dimension: int | None
    dual_dimension: int | None
    rank_upper_bound: int | None
    rigour: Rigour
    obstruction: str | None


@dataclass(frozen=True, slots=True)
class PointSearchResult:
    """A certified lower bound supplied by exact points and a regulator."""

    points: tuple[Point, ...]
    lower_bound: int
    regulator_lower: Fraction
    rigour: Rigour
    search_height: int
    denominator_bound: int


@dataclass(frozen=True, slots=True)
class RankResult:
    """Lower/upper rank bounds and the Chapter 44 termination verdict."""

    lower_bound: int
    upper_bound: int | None
    verdict: Literal["proved", "undetermined"]
    rank: int | None
    lower_rigour: Rigour
    upper_rigour: Rigour | None
    points: tuple[Point, ...]
    obstruction: str | None


def _divisors(value: int) -> list[int]:
    n = abs(value)
    if n == 0:
        return [0]
    values: list[int] = []
    for d in range(1, isqrt(n) + 1):
        if n % d == 0:
            values.extend([d, n // d])
    return sorted(set(values))


def _rational_two_torsion(curve: EllipticCurve) -> Point | None:
    """Find an exact root of the 2-division cubic."""

    constant = curve.b6
    numerators = [0] if constant == 0 else [
        sign * divisor for divisor in _divisors(constant) for sign in (-1, 1)
    ]
    for denominator in (1, 2, 4):
        for numerator in numerators:
            if gcd(abs(numerator), denominator) != 1:
                continue
            x = Fraction(numerator, denominator)
            polynomial = 4 * x**3 + curve.b2 * x**2 + 2 * curve.b4 * x + curve.b6
            if polynomial == 0:
                y = -(curve.a1 * x + curve.a3) / 2
                point = Point(x, y)
                if curve.is_on_curve(point):
                    return point
    return None


def _squarefree_products(value: int) -> list[int]:
    primes = list(factor_integer(value))
    products = {1, -1}
    for prime in primes:
        products |= {item * prime for item in list(products)}
    return sorted(products)


def _quartic_value(a: int, b: int, d: int, u: int, v: int) -> int:
    return d * u**4 + a * u * u * v * v + (b // d) * v**4


def _real_soluble(a: int, b: int, d: int) -> bool:
    # v=0 gives z^2=d*u^4 for d>0.  For d<0, inspect the quadratic
    # d*T^2+a*T+b/d on T=(u/v)^2 >= 0 at its endpoint/vertex.
    if d > 0:
        return True
    c = Fraction(b, d)
    values = [c]
    vertex = Fraction(-a, 2 * d)
    if vertex >= 0:
        values.append(d * vertex * vertex + a * vertex + c)
    return any(value >= 0 for value in values)


def _local_quartic_status(
    a: int, b: int, d: int, prime: int, max_power: int = 3
) -> str:
    """Return ``soluble``, ``insoluble``, or ``unknown`` over ``Q_p``."""

    for u in range(-4, 5):
        for v in range(-4, 5):
            if u == v == 0:
                continue
            value = _quartic_value(a, b, d, u, v)
            if value >= 0 and isqrt(value) ** 2 == value:
                return "soluble"
    for exponent in range(1, max_power + 1):
        modulus = prime**exponent
        squares = {z * z % modulus for z in range(modulus)}
        primitive_found = False
        nonsingular_found = False
        for u in range(modulus):
            for v in range(modulus):
                if u % prime == 0 and v % prime == 0:
                    continue
                value = _quartic_value(a, b, d, u, v) % modulus
                if value not in squares:
                    continue
                primitive_found = True
                if prime != 2:
                    for z in range(prime):
                        if z * z % prime == value % prime and (2 * z) % prime:
                            nonsingular_found = True
                            break
                if nonsingular_found:
                    return "soluble"
        if not primitive_found:
            return "insoluble"
    return "unknown"


def _isogeny_classes(a: int, b: int) -> tuple[SelmerClass, ...]:
    support = {2, *factor_integer(b), *factor_integer(a * a - 4 * b)}
    classes: list[SelmerClass] = []
    for d in _squarefree_products(b):
        if d == 0 or b % d:
            continue
        statuses: list[tuple[str, str]] = []
        real = _real_soluble(a, b, d)
        statuses.append(("infinity", "soluble" if real else "insoluble"))
        unknown = False
        accepted = real
        for prime in sorted(support):
            status = _local_quartic_status(a, b, d, prime)
            statuses.append((str(prime), status))
            if status == "insoluble":
                accepted = False
            elif status == "unknown":
                unknown = True
        result: bool | None = None if accepted and unknown else accepted
        classes.append(SelmerClass(d, tuple(statuses), result))
    return tuple(classes)


def two_isogeny_descent(curve: EllipticCurve) -> TwoIsogenyDescent:
    """Run the complete supported 2-isogeny descent workflow."""

    torsion = _rational_two_torsion(curve)
    if torsion is None:
        return TwoIsogenyDescent(
            Point.origin(),
            0,
            0,
            (),
            (),
            None,
            None,
            None,
            "heuristic",
            "general cubic-algebra 2-descent is not implemented",
        )
    root = torsion.x
    a = 3 * root + Fraction(curve.b2, 4)
    b = 3 * root * root + Fraction(curve.b2, 2) * root + Fraction(curve.b4, 2)
    if a.denominator != 1 or b.denominator != 1 or b == 0:
        return TwoIsogenyDescent(
            torsion,
            int(a),
            int(b),
            (),
            (),
            None,
            None,
            None,
            "heuristic",
            "the integral isogeny normal form needs an additional scaling",
        )
    a_int, b_int = int(a), int(b)
    phi = _isogeny_classes(a_int, b_int)
    dual_a, dual_b = -2 * a_int, a_int * a_int - 4 * b_int
    dual = _isogeny_classes(dual_a, dual_b)
    if any(item.accepted is None for item in (*phi, *dual)):
        return TwoIsogenyDescent(
            torsion,
            a_int,
            b_int,
            phi,
            dual,
            None,
            None,
            None,
            "heuristic",
            "a local residue tree ended in an unproved singular branch",
        )
    phi_order = sum(item.accepted is True for item in phi)
    dual_order = sum(item.accepted is True for item in dual)
    if (
        phi_order == 0
        or dual_order == 0
        or phi_order & (phi_order - 1)
        or dual_order & (dual_order - 1)
    ):
        return TwoIsogenyDescent(
            torsion,
            a_int,
            b_int,
            phi,
            dual,
            None,
            None,
            None,
            "heuristic",
            "accepted classes did not form powers-of-two groups",
        )
    phi_dimension = phi_order.bit_length() - 1
    dual_dimension = dual_order.bit_length() - 1
    return TwoIsogenyDescent(
        torsion,
        a_int,
        b_int,
        phi,
        dual,
        phi_dimension,
        dual_dimension,
        max(0, phi_dimension + dual_dimension - 2),
        "proved",
        None,
    )


def _rational_square(value: Fraction) -> Fraction | None:
    if value < 0:
        return None
    numerator = isqrt(value.numerator)
    denominator = isqrt(value.denominator)
    if numerator * numerator == value.numerator and denominator * denominator == value.denominator:
        return Fraction(numerator, denominator)
    return None


def point_search(
    curve: EllipticCurve,
    height: int = 10,
    denominator_bound: int = 1,
    max_points: int = 3,
) -> PointSearchResult:
    """Search ``x=a/b^2`` and greedily certify an independent subgroup."""

    candidates: list[Point] = []
    seen_x: set[Fraction] = set()
    for denominator in range(1, denominator_bound + 1):
        for numerator in range(-height * denominator * denominator, height * denominator * denominator + 1):
            if gcd(abs(numerator), denominator) != 1:
                continue
            x = Fraction(numerator, denominator * denominator)
            if x in seen_x:
                continue
            seen_x.add(x)
            linear = curve.a1 * x + curve.a3
            discriminant_y = linear * linear + 4 * curve.rhs(x)
            root = _rational_square(discriminant_y)
            if root is None:
                continue
            point = Point(x, (-linear + root) / 2)
            if curve.is_on_curve(point) and curve.point_order(point, 12) is None:
                candidates.append(point)

    independent: list[Point] = []
    for point in candidates:
        if len(independent) >= max_points:
            break
        trial = [*independent, point]
        independent_at_three = points_are_independent(curve, trial, 3)
        if independent_at_three or points_are_independent(curve, trial, 4):
            independent.append(point)
    determinant = regulator(curve, independent)
    lower = determinant.lower if independent else Fraction(1)
    return PointSearchResult(
        tuple(independent),
        len(independent),
        lower,
        "proved",
        height,
        denominator_bound,
    )


def determine_rank(
    curve: EllipticCurve, height: int = 10, denominator_bound: int = 1
) -> RankResult:
    """Combine certified point search and supported 2-isogeny descent."""

    lower = point_search(curve, height, denominator_bound)
    descent = two_isogeny_descent(curve)
    upper = descent.rank_upper_bound if descent.rigour == "proved" else None
    if (
        lower.rigour == "proved"
        and descent.rigour == "proved"
        and upper == lower.lower_bound
    ):
        return RankResult(
            lower.lower_bound,
            upper,
            "proved",
            upper,
            lower.rigour,
            descent.rigour,
            lower.points,
            None,
        )
    return RankResult(
        lower.lower_bound,
        upper,
        "undetermined",
        None,
        lower.rigour,
        descent.rigour if upper is not None else None,
        lower.points,
        descent.obstruction or "certified lower and upper bounds do not meet",
    )
