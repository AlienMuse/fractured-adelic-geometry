"""Exact L1 arithmetic for integral Weierstrass models over the rationals.

The group law and invariants are exact.  Minimality is certified whenever the
standard discriminant criterion ``v_p(Delta) < 12`` applies at every prime;
the implementation also performs admissible integral ``u=p`` reductions by a
finite residue search.  If neither route settles a general input, the returned
model is explicitly tagged ``heuristic`` rather than being called minimal.
"""

from __future__ import annotations

from dataclasses import dataclass
from fractions import Fraction
from math import gcd, isqrt
from typing import Iterable, Iterator, Literal, Sequence

Rigour = Literal["proved", "conditional", "heuristic", "numerical"]


def factor_integer(value: int) -> dict[int, int]:
    """Factor a non-zero integer by deterministic trial division."""

    n = abs(value)
    if n in (0, 1):
        return {}
    factors: dict[int, int] = {}
    divisor = 2
    while divisor * divisor <= n:
        while n % divisor == 0:
            factors[divisor] = factors.get(divisor, 0) + 1
            n //= divisor
        divisor = 3 if divisor == 2 else divisor + 2
    if n > 1:
        factors[n] = factors.get(n, 0) + 1
    return factors


def valuation(value: int, prime: int) -> int:
    """Return the ``prime``-adic valuation of a non-zero integer."""

    if value == 0:
        return 10**9
    answer = 0
    n = abs(value)
    while n % prime == 0:
        answer += 1
        n //= prime
    return answer


@dataclass(frozen=True, slots=True)
class Point:
    """An affine rational point, or the point at infinity."""

    x: Fraction = Fraction(0)
    y: Fraction = Fraction(0)
    infinity: bool = False

    def __init__(
        self,
        x: int | Fraction = 0,
        y: int | Fraction = 0,
        infinity: bool = False,
    ) -> None:
        object.__setattr__(self, "x", Fraction(x))
        object.__setattr__(self, "y", Fraction(y))
        object.__setattr__(self, "infinity", infinity)

    @classmethod
    def origin(cls) -> "Point":
        """Return the group identity."""

        return cls(infinity=True)

    def to_json(self) -> dict[str, str] | None:
        """Return exact JSON coordinates, or ``None`` for infinity."""

        if self.infinity:
            return None
        return {
            "x": f"{self.x.numerator}/{self.x.denominator}",
            "y": f"{self.y.numerator}/{self.y.denominator}",
        }


@dataclass(frozen=True, slots=True)
class MinimalModelResult:
    """A model, accumulated changes, and the epistemic status of minimality."""

    curve: "EllipticCurve"
    transformations: tuple[dict[str, int], ...]
    rigour: Rigour
    reason: str


@dataclass(frozen=True, slots=True)
class TorsionResult:
    """Bounds and witnesses for the rational torsion subgroup."""

    order_lower: int
    order_upper: int
    structure: str
    generators: tuple[Point, ...]
    reduction_primes: tuple[int, ...]
    rigour: Rigour


@dataclass(frozen=True, slots=True)
class EllipticCurve:
    """An elliptic curve in general Weierstrass form over ``Q``."""

    a1: int
    a2: int
    a3: int
    a4: int
    a6: int

    def __init__(self, coefficients: Sequence[int]) -> None:
        if len(coefficients) != 5:
            raise ValueError("five Weierstrass coefficients are required")
        values = tuple(int(value) for value in coefficients)
        object.__setattr__(self, "a1", values[0])
        object.__setattr__(self, "a2", values[1])
        object.__setattr__(self, "a3", values[2])
        object.__setattr__(self, "a4", values[3])
        object.__setattr__(self, "a6", values[4])
        if self.discriminant == 0:
            raise ValueError("the Weierstrass cubic is singular")

    @property
    def coefficients(self) -> tuple[int, int, int, int, int]:
        """Return ``[a1,a2,a3,a4,a6]`` as an immutable tuple."""

        return self.a1, self.a2, self.a3, self.a4, self.a6

    @property
    def b2(self) -> int:
        return self.a1 * self.a1 + 4 * self.a2

    @property
    def b4(self) -> int:
        return self.a1 * self.a3 + 2 * self.a4

    @property
    def b6(self) -> int:
        return self.a3 * self.a3 + 4 * self.a6

    @property
    def b8(self) -> int:
        return (
            self.a1 * self.a1 * self.a6
            + 4 * self.a2 * self.a6
            - self.a1 * self.a3 * self.a4
            + self.a2 * self.a3 * self.a3
            - self.a4 * self.a4
        )

    @property
    def c4(self) -> int:
        return self.b2 * self.b2 - 24 * self.b4

    @property
    def c6(self) -> int:
        return -self.b2**3 + 36 * self.b2 * self.b4 - 216 * self.b6

    @property
    def discriminant(self) -> int:
        return (
            -(self.b2**2) * self.b8
            - 8 * self.b4**3
            - 27 * self.b6**2
            + 9 * self.b2 * self.b4 * self.b6
        )

    @property
    def j_invariant(self) -> Fraction:
        return Fraction(self.c4**3, self.discriminant)

    def rhs(self, x: int | Fraction) -> Fraction:
        """Return the right side of the Weierstrass equation."""

        q = Fraction(x)
        return q**3 + self.a2 * q**2 + self.a4 * q + self.a6

    def is_on_curve(self, point: Point) -> bool:
        """Check the projective identity or exact affine equation."""

        if point.infinity:
            return True
        x, y = point.x, point.y
        return y * y + self.a1 * x * y + self.a3 * y == self.rhs(x)

    def negate(self, point: Point) -> Point:
        """Return the exact group inverse."""

        if point.infinity:
            return point
        return Point(point.x, -point.y - self.a1 * point.x - self.a3)

    def add(self, left: Point, right: Point) -> Point:
        """Add two rational points by the general Weierstrass formulas."""

        if not self.is_on_curve(left) or not self.is_on_curve(right):
            raise ValueError("point is not on the curve")
        if left.infinity:
            return right
        if right.infinity:
            return left
        if right == self.negate(left):
            return Point.origin()

        x1, y1, x2, y2 = left.x, left.y, right.x, right.y
        if x1 != x2:
            denominator = x2 - x1
            slope = (y2 - y1) / denominator
            intercept = (y1 * x2 - y2 * x1) / denominator
        else:
            denominator = 2 * y1 + self.a1 * x1 + self.a3
            if denominator == 0:
                return Point.origin()
            slope = (
                3 * x1 * x1
                + 2 * self.a2 * x1
                + self.a4
                - self.a1 * y1
            ) / denominator
            intercept = (
                -x1**3 + self.a4 * x1 + 2 * self.a6 - self.a3 * y1
            ) / denominator
        x3 = slope * slope + self.a1 * slope - self.a2 - x1 - x2
        y3 = -(slope + self.a1) * x3 - intercept - self.a3
        answer = Point(x3, y3)
        if not self.is_on_curve(answer):
            raise ArithmeticError("group-law invariant failed")
        return answer

    def multiply(self, scalar: int, point: Point) -> Point:
        """Multiply a rational point by an integer."""

        if scalar < 0:
            return self.multiply(-scalar, self.negate(point))
        answer = Point.origin()
        addend = point
        n = scalar
        while n:
            if n & 1:
                answer = self.add(answer, addend)
            addend = self.add(addend, addend)
            n >>= 1
        return answer

    def point_order(self, point: Point, limit: int = 16) -> int | None:
        """Return a proved order at most ``limit``, or ``None``."""

        if point.infinity:
            return 1
        current = Point.origin()
        for order in range(1, limit + 1):
            current = self.add(current, point)
            if current.infinity:
                return order
        return None

    def integral_points(self, bound: int) -> Iterator[Point]:
        """Enumerate integral points with ``|x| <= bound`` exactly."""

        for x in range(-bound, bound + 1):
            linear = self.a1 * x + self.a3
            discriminant_y = linear * linear + 4 * int(self.rhs(x))
            if discriminant_y < 0:
                continue
            root = isqrt(discriminant_y)
            if root * root != discriminant_y:
                continue
            for numerator in {-linear + root, -linear - root}:
                if numerator % 2 == 0:
                    point = Point(x, numerator // 2)
                    if self.is_on_curve(point):
                        yield point

    def admissible_change(self, p: int, r: int, s: int, t: int) -> "EllipticCurve" | None:
        """Try the integral change with scale ``u=p`` and translation ``r,s,t``."""

        numerators = (
            self.a1 + 2 * s,
            self.a2 - s * self.a1 + 3 * r - s * s,
            self.a3 + r * self.a1 + 2 * t,
            self.a4
            - s * self.a3
            + 2 * r * self.a2
            - (t + r * s) * self.a1
            + 3 * r * r
            - 2 * s * t,
            self.a6
            + r * self.a4
            + r * r * self.a2
            + r**3
            - t * self.a3
            - t * t
            - r * t * self.a1,
        )
        divisors = (p, p**2, p**3, p**4, p**6)
        if any(value % divisor for value, divisor in zip(numerators, divisors)):
            return None
        return EllipticCurve([value // divisor for value, divisor in zip(numerators, divisors)])

    def minimal_model(self, search_prime_limit: int = 13) -> MinimalModelResult:
        """Apply the Laska--Kraus--Connell integral scaling step when feasible.

        The finite residue search is complete for a single ``u=p`` step at each
        searched prime.  Minimality is proved directly whenever every remaining
        discriminant valuation is below 12.  Larger unsupported branches are
        returned with a ``heuristic`` tag rather than a false proof claim.
        """

        curve = self
        transformations: list[dict[str, int]] = []
        changed = True
        while changed:
            changed = False
            for p, exponent in factor_integer(curve.discriminant).items():
                if exponent < 12 or p > search_prime_limit:
                    continue
                found: tuple[EllipticCurve, int, int, int] | None = None
                for s in range(p):
                    for r in range(p * p):
                        for t in range(p**3):
                            candidate = curve.admissible_change(p, r, s, t)
                            if candidate is not None:
                                found = candidate, r, s, t
                                break
                        if found:
                            break
                    if found:
                        break
                if found:
                    curve, r, s, t = found
                    transformations.append({"u": p, "r": r, "s": s, "t": t})
                    changed = True
                    break
        unresolved = [
            (p, e) for p, e in factor_integer(curve.discriminant).items() if e >= 12
        ]
        if not unresolved:
            return MinimalModelResult(
                curve,
                tuple(transformations),
                "proved",
                "v_p(discriminant) < 12 at every prime",
            )
        return MinimalModelResult(
            curve,
            tuple(transformations),
            "heuristic",
            f"unimplemented deep LKC branches at {unresolved}",
        )

    def finite_add(
        self,
        left: tuple[int, int] | None,
        right: tuple[int, int] | None,
        prime: int,
    ) -> tuple[int, int] | None:
        """Add points on the reduced curve over ``F_prime``."""

        if left is None:
            return right
        if right is None:
            return left
        x1, y1 = left
        x2, y2 = right
        neg_left = (x1, (-y1 - self.a1 * x1 - self.a3) % prime)
        if right == neg_left:
            return None
        if x1 != x2:
            inv = pow((x2 - x1) % prime, -1, prime)
            slope = (y2 - y1) * inv % prime
            intercept = (y1 * x2 - y2 * x1) * inv % prime
        else:
            denominator = (2 * y1 + self.a1 * x1 + self.a3) % prime
            if denominator == 0:
                return None
            inv = pow(denominator, -1, prime)
            slope = (
                3 * x1 * x1
                + 2 * self.a2 * x1
                + self.a4
                - self.a1 * y1
            ) * inv % prime
            intercept = (
                -x1**3 + self.a4 * x1 + 2 * self.a6 - self.a3 * y1
            ) * inv % prime
        x3 = (slope * slope + self.a1 * slope - self.a2 - x1 - x2) % prime
        y3 = (-(slope + self.a1) * x3 - intercept - self.a3) % prime
        return x3, y3

    def finite_multiply(
        self, scalar: int, point: tuple[int, int] | None, prime: int
    ) -> tuple[int, int] | None:
        """Multiply a point over a prime field."""

        answer = None
        addend = point
        n = scalar
        while n:
            if n & 1:
                answer = self.finite_add(answer, addend, prime)
            addend = self.finite_add(addend, addend, prime)
            n >>= 1
        return answer

    def torsion_subgroup(self, search_bound: int = 100) -> TorsionResult:
        """Determine torsion using integral-point search, Mazur, and reductions.

        Integral torsion candidates are enumerated in the Nagell--Lutz spirit.
        Completeness is certified only when the exhibited subgroup order reaches
        the gcd bound from injective reduction at odd good primes.
        """

        from .frobenius import count_points_naive, primes_up_to

        allowed_orders = {1, 2, 3, 4, 5, 6, 7, 8, 9, 10, 12}
        best_order = 1
        best_point: Point | None = None
        for point in self.integral_points(search_bound):
            order = self.point_order(point, 12)
            if order in allowed_orders and order > best_order:
                best_order, best_point = order, point

        upper = 0
        used_primes: list[int] = []
        for prime in primes_up_to(50):
            if prime == 2 or self.discriminant % prime == 0:
                continue
            group_order = count_points_naive(self, prime)
            upper = group_order if upper == 0 else gcd(upper, group_order)
            used_primes.append(prime)
            if upper == best_order and len(used_primes) >= 2:
                break
        if upper == 0:
            upper = best_order
        proved = upper == best_order
        generators = () if best_point is None else (best_point,)
        structure = "0" if best_order == 1 else f"Z/{best_order}Z"
        return TorsionResult(
            best_order,
            upper,
            structure,
            generators,
            tuple(used_primes),
            "proved" if proved else "heuristic",
        )

    def to_dict(self) -> dict[str, object]:
        """Return exact invariant data suitable for JSON output."""

        return {
            "model": list(self.coefficients),
            "b2": self.b2,
            "b4": self.b4,
            "b6": self.b6,
            "b8": self.b8,
            "c4": self.c4,
            "c6": self.c6,
            "discriminant": self.discriminant,
            "j": f"{self.j_invariant.numerator}/{self.j_invariant.denominator}",
        }
