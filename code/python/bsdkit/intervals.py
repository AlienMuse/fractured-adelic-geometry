"""Exact rational interval arithmetic for the certified L0 kernel.

Finite arithmetic is performed on :class:`fractions.Fraction` endpoints, so
there is no machine-rounding error.  ``sqrt``, ``exp`` and ``log`` use rational
series with explicit remainder bounds and return outward dyadic/rational
enclosures.  The ``certified`` bit is the pessimistic join of the input tags;
it is never upgraded merely because a computation is reproducible.
"""

from __future__ import annotations

from dataclasses import dataclass
from fractions import Fraction
from functools import lru_cache
from math import isqrt
from typing import SupportsInt

Rational = int | Fraction


def _fraction(value: Rational | str | float) -> Fraction:
    """Convert a supported value to an exact rational.

    Floats are converted to their exact binary value.  They are therefore
    suitable only when the caller deliberately wants to enclose that binary
    number, not an intended decimal constant.
    """

    if isinstance(value, Fraction):
        return value
    if isinstance(value, str):
        return Fraction(value)
    return Fraction(value)


def _pow2(bits: int) -> int:
    return 1 << max(0, bits)


def _outward_dyadic(
    lower: Fraction, upper: Fraction, bits: int
) -> tuple[Fraction, Fraction]:
    scale = _pow2(bits)
    low_integer = (lower.numerator * scale) // lower.denominator
    high_numerator = upper.numerator * scale
    high_integer = -(-high_numerator // upper.denominator)
    return Fraction(low_integer, scale), Fraction(high_integer, scale)


def _sqrt_bounds(value: Fraction, bits: int) -> tuple[Fraction, Fraction]:
    if value < 0:
        raise ValueError("square root requires a non-negative interval")
    if value == 0:
        return Fraction(0), Fraction(0)
    scale = _pow2(bits)
    floor_scaled_square = (value.numerator * scale * scale) // value.denominator
    lower_int = isqrt(floor_scaled_square)
    lower = Fraction(lower_int, scale)
    if lower * lower == value:
        return lower, lower
    return lower, Fraction(lower_int + 1, scale)


def _exp_positive_bounds(value: Fraction, bits: int) -> tuple[Fraction, Fraction]:
    """Enclose exp(value) for non-negative rational ``value``."""

    if value == 0:
        return Fraction(1), Fraction(1)
    halvings = 0
    reduced = value
    while reduced > Fraction(1, 8):
        reduced /= 2
        halvings += 1

    target = Fraction(1, _pow2(bits + halvings + 8))
    term = Fraction(1)
    partial = Fraction(1)
    n = 0
    while True:
        n += 1
        term *= reduced / n
        partial += term
        ratio = reduced / (n + 1)
        remainder = term * reduced / (n + 1) / (1 - ratio)
        if remainder <= target:
            break
    lower, upper = _outward_dyadic(partial, partial + remainder, bits + 10)
    for _ in range(halvings):
        lower, upper = _outward_dyadic(
            lower * lower, upper * upper, bits + 10
        )
    return lower, upper


def _exp_bounds(value: Fraction, bits: int) -> tuple[Fraction, Fraction]:
    if value >= 0:
        return _exp_positive_bounds(value, bits)
    lower, upper = _exp_positive_bounds(-value, bits)
    return Fraction(1, 1) / upper, Fraction(1, 1) / lower


def _normalise_power_two(value: Fraction) -> tuple[int, Fraction]:
    """Return ``k,y`` with value = 2**k*y and 1 <= y < 2."""

    if value <= 0:
        raise ValueError("logarithm requires a positive value")
    k = value.numerator.bit_length() - value.denominator.bit_length()
    if k >= 0:
        y = value / (1 << k)
    else:
        y = value * (1 << (-k))
    while y < 1:
        y *= 2
        k -= 1
    while y >= 2:
        y /= 2
        k += 1
    return k, y


def _atanh_log_bounds(value: Fraction, bits: int) -> tuple[Fraction, Fraction]:
    """Enclose log(value) for 1 <= value <= 2 by the atanh series."""

    z = (value - 1) / (value + 1)
    if z == 0:
        return Fraction(0), Fraction(0)
    z2 = z * z
    target = Fraction(1, _pow2(bits + 6))
    power = z
    partial = Fraction(0)
    n = 0
    while True:
        partial += power / (2 * n + 1)
        next_power = power * z2
        tail = 2 * next_power / ((2 * n + 3) * (1 - z2))
        if tail <= target:
            return 2 * partial, 2 * partial + tail
        power = next_power
        n += 1


@lru_cache(maxsize=32)
def _log_two_bounds(bits: int) -> tuple[Fraction, Fraction]:
    return _atanh_log_bounds(Fraction(2), bits + 4)


def _log_bounds(value: Fraction, bits: int) -> tuple[Fraction, Fraction]:
    k, reduced = _normalise_power_two(value)
    low_y, high_y = _atanh_log_bounds(reduced, bits + 8)
    low_two, high_two = _log_two_bounds(bits + 8)
    if k >= 0:
        return low_y + k * low_two, high_y + k * high_two
    return low_y + k * high_two, high_y + k * low_two


@lru_cache(maxsize=32)
def pi_interval(bits: int = 128) -> "Interval":
    """Return a rigorous Machin-formula enclosure of pi."""

    def atan_reciprocal(q: int) -> tuple[Fraction, Fraction]:
        x = Fraction(1, q)
        x2 = x * x
        power = x
        partial = Fraction(0)
        sign = 1
        n = 0
        target = Fraction(1, _pow2(bits + 12))
        while True:
            term = power / (2 * n + 1)
            new_partial = partial + sign * term
            next_term = power * x2 / (2 * n + 3)
            if next_term <= target:
                if sign > 0:
                    return new_partial - next_term, new_partial
                return new_partial, new_partial + next_term
            partial = new_partial
            power *= x2
            sign = -sign
            n += 1

    a_low, a_high = atan_reciprocal(5)
    b_low, b_high = atan_reciprocal(239)
    return Interval(16 * a_low - 4 * b_high, 16 * a_high - 4 * b_low)


@dataclass(frozen=True, slots=True)
class Interval:
    """A closed rational interval with a certification tag."""

    lower: Fraction
    upper: Fraction
    certified: bool = True

    def __init__(
        self,
        lower: Rational | str | float,
        upper: Rational | str | float | None = None,
        certified: bool = True,
    ) -> None:
        low = _fraction(lower)
        high = low if upper is None else _fraction(upper)
        if low > high:
            raise ValueError("interval lower endpoint exceeds upper endpoint")
        object.__setattr__(self, "lower", low)
        object.__setattr__(self, "upper", high)
        object.__setattr__(self, "certified", certified)

    @classmethod
    def exact(cls, value: Rational | str) -> "Interval":
        """Construct a certified singleton interval."""

        return cls(value)

    @classmethod
    def from_midpoint_radius(
        cls, midpoint: Rational, radius: Rational, *, certified: bool = True
    ) -> "Interval":
        """Construct ``[midpoint-radius, midpoint+radius]``."""

        mid, rad = _fraction(midpoint), _fraction(radius)
        if rad < 0:
            raise ValueError("radius must be non-negative")
        return cls(mid - rad, mid + rad, certified)

    @property
    def width(self) -> Fraction:
        """Return the exact interval width."""

        return self.upper - self.lower

    @property
    def midpoint(self) -> Fraction:
        """Return the exact midpoint."""

        return (self.lower + self.upper) / 2

    def contains(self, value: Rational | float | "Interval") -> bool:
        """Test containment of a scalar or another interval."""

        if isinstance(value, Interval):
            return self.lower <= value.lower and value.upper <= self.upper
        q = _fraction(value)
        return self.lower <= q <= self.upper

    def excludes_zero(self) -> bool:
        """Return whether zero is provably outside the interval."""

        return self.upper < 0 or self.lower > 0

    def _coerce(self, other: Rational | "Interval") -> "Interval":
        return other if isinstance(other, Interval) else Interval.exact(other)

    def __add__(self, other: Rational | "Interval") -> "Interval":
        rhs = self._coerce(other)
        return Interval(
            self.lower + rhs.lower,
            self.upper + rhs.upper,
            self.certified and rhs.certified,
        )

    __radd__ = __add__

    def __neg__(self) -> "Interval":
        return Interval(-self.upper, -self.lower, self.certified)

    def __sub__(self, other: Rational | "Interval") -> "Interval":
        return self + (-self._coerce(other))

    def __rsub__(self, other: Rational | "Interval") -> "Interval":
        return self._coerce(other) - self

    def __mul__(self, other: Rational | "Interval") -> "Interval":
        rhs = self._coerce(other)
        products = (
            self.lower * rhs.lower,
            self.lower * rhs.upper,
            self.upper * rhs.lower,
            self.upper * rhs.upper,
        )
        return Interval(min(products), max(products), self.certified and rhs.certified)

    __rmul__ = __mul__

    def reciprocal(self) -> "Interval":
        """Return the reciprocal enclosure, rejecting an interval through zero."""

        if self.contains(0):
            raise ZeroDivisionError("interval denominator contains zero")
        return Interval(1 / self.upper, 1 / self.lower, self.certified)

    def __truediv__(self, other: Rational | "Interval") -> "Interval":
        return self * self._coerce(other).reciprocal()

    def __rtruediv__(self, other: Rational | "Interval") -> "Interval":
        return self._coerce(other) / self

    def __pow__(self, exponent: SupportsInt) -> "Interval":
        n = int(exponent)
        if n < 0:
            return (self.reciprocal()) ** (-n)
        result = Interval.exact(1)
        base = self
        while n:
            if n & 1:
                result *= base
            base *= base
            n >>= 1
        return result

    def sqrt(self, bits: int = 128) -> "Interval":
        """Return an outward dyadic enclosure of the non-negative square root."""

        if self.lower < 0:
            raise ValueError("square root interval crosses the negative axis")
        low, _ = _sqrt_bounds(self.lower, bits)
        _, high = _sqrt_bounds(self.upper, bits)
        return Interval(low, high, self.certified)

    def exp(self, bits: int = 128) -> "Interval":
        """Return an outward rational enclosure of the exponential."""

        low, _ = _exp_bounds(self.lower, bits)
        _, high = _exp_bounds(self.upper, bits)
        return Interval(low, high, self.certified)

    def log(self, bits: int = 128) -> "Interval":
        """Return an outward rational enclosure of the natural logarithm."""

        if self.lower <= 0:
            raise ValueError("logarithm interval is not strictly positive")
        low, _ = _log_bounds(self.lower, bits)
        _, high = _log_bounds(self.upper, bits)
        return Interval(low, high, self.certified)

    def enlarge(self, radius: Rational) -> "Interval":
        """Enlarge both endpoints by a non-negative exact radius."""

        r = _fraction(radius)
        if r < 0:
            raise ValueError("radius must be non-negative")
        return Interval(self.lower - r, self.upper + r, self.certified)

    def quantize(self, bits: int) -> "Interval":
        """Outward-round both endpoints to a fixed dyadic denominator."""

        lower, upper = _outward_dyadic(self.lower, self.upper, bits)
        return Interval(
            lower,
            upper,
            self.certified,
        )

    def intersect(self, other: "Interval") -> "Interval":
        """Return the certified intersection of two enclosures."""

        lower, upper = max(self.lower, other.lower), min(self.upper, other.upper)
        if lower > upper:
            raise ValueError("certified intervals have empty intersection")
        return Interval(lower, upper, self.certified and other.certified)

    def to_dict(self) -> dict[str, object]:
        """Return canonical JSON-compatible endpoint strings."""

        def encode(value: Fraction) -> str:
            return f"{value.numerator}/{value.denominator}"

        return {
            "lower": encode(self.lower),
            "upper": encode(self.upper),
            "certified": self.certified,
        }

    @classmethod
    def from_dict(cls, value: dict[str, object]) -> "Interval":
        """Decode :meth:`to_dict` output."""

        return cls(
            str(value["lower"]),
            str(value["upper"]),
            bool(value.get("certified", True)),
        )

    def __str__(self) -> str:
        suffix = "certified" if self.certified else "not-certified"
        return f"[{float(self.lower):.15g}, {float(self.upper):.15g}] ({suffix})"
