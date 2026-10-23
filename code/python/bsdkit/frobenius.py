"""Exact Frobenius traces and local Euler factors."""

from __future__ import annotations

from math import gcd, isqrt
from typing import Iterator

from .ellcurve import EllipticCurve
from .reduction import LocalReduction, tate_algorithm


def primes_up_to(bound: int) -> list[int]:
    """Return the primes at most ``bound`` by an Eratosthenes sieve."""

    if bound < 2:
        return []
    sieve = bytearray(b"\x01") * (bound + 1)
    sieve[0:2] = b"\x00\x00"
    for p in range(2, isqrt(bound) + 1):
        if sieve[p]:
            sieve[p * p : bound + 1 : p] = b"\x00" * (
                (bound - p * p) // p + 1
            )
    return [i for i, flag in enumerate(sieve) if flag]


def finite_points(
    curve: EllipticCurve, prime: int
) -> Iterator[tuple[int, int] | None]:
    """Enumerate all points on the reduced affine equation, then infinity."""

    yield None
    for x in range(prime):
        rhs = (
            x**3 + curve.a2 * x * x + curve.a4 * x + curve.a6
        ) % prime
        for y in range(prime):
            lhs = (y * y + curve.a1 * x * y + curve.a3 * y) % prime
            if lhs == rhs:
                yield x, y


def count_points_naive(curve: EllipticCurve, prime: int) -> int:
    """Count ``E(F_p)`` by exact enumeration."""

    return sum(1 for _ in finite_points(curve, prime))


def _bounded_discrete_log(
    curve: EllipticCurve,
    point: tuple[int, int],
    target: tuple[int, int] | None,
    prime: int,
    bound: int,
) -> int | None:
    """Find ``0 <= k <= bound`` with ``k*point=target`` by BSGS."""

    step = isqrt(bound) + 1
    babies: dict[tuple[int, int] | None, int] = {}
    value = None
    for j in range(step):
        babies.setdefault(value, j)
        value = curve.finite_add(value, point, prime)
    giant = curve.finite_multiply(step, point, prime)
    neg_giant = (
        None
        if giant is None
        else (giant[0], (-giant[1] - curve.a1 * giant[0] - curve.a3) % prime)
    )
    value = target
    for i in range(step + 1):
        if value in babies:
            answer = i * step + babies[value]
            if answer <= bound:
                return answer
        value = curve.finite_add(value, neg_giant, prime)
    return None


def count_points_bsgs(curve: EllipticCurve, prime: int) -> int:
    """Use Hasse-interval BSGS constraints, with exact enumeration fallback.

    For each deterministic point, a bounded discrete logarithm constrains the
    possible group order in the Hasse interval.  If the exponent constraints do
    not leave a unique order (possible for non-cyclic groups), exact enumeration
    completes the certificate.
    """

    radius = isqrt(4 * prime)
    lower, upper = prime + 1 - radius, prime + 1 + radius
    candidates = set(range(lower, upper + 1))
    points = [point for point in finite_points(curve, prime) if point is not None]
    offset_bound = radius
    for point in points[: min(len(points), 12)]:
        base = curve.finite_multiply(prime + 1, point, prime)
        target = (
            None
            if base is None
            else (base[0], (-base[1] - curve.a1 * base[0] - curve.a3) % prime)
        )
        _bounded_discrete_log(curve, point, target, prime, offset_bound)
        candidates = {
            order
            for order in candidates
            if curve.finite_multiply(order, point, prime) is None
        }
        if len(candidates) == 1:
            candidate = next(iter(candidates))
            # A unique annihilator in the Hasse interval is the group order.
            if candidate == len(points) + 1:
                return candidate
    return len(points) + 1


def frobenius_trace(
    curve: EllipticCurve, prime: int, method: str = "naive"
) -> int:
    """Return ``a_p`` and enforce Hasse's exact integer inequality."""

    if curve.discriminant % prime == 0:
        local = tate_algorithm(curve, prime)
        if local.reduction == "split_multiplicative":
            return 1
        if local.reduction == "nonsplit_multiplicative":
            return -1
        return 0
    if method == "naive":
        order = count_points_naive(curve, prime)
    elif method == "bsgs":
        order = count_points_bsgs(curve, prime)
    else:
        raise ValueError("method must be 'naive' or 'bsgs'")
    trace = prime + 1 - order
    if trace * trace > 4 * prime:
        raise ArithmeticError("point count violates the Hasse bound")
    return trace


def local_l_factor(
    curve: EllipticCurve, prime: int
) -> tuple[int, ...]:
    """Return coefficients of the local denominator polynomial in ``T``."""

    if curve.discriminant % prime:
        return 1, -frobenius_trace(curve, prime), prime
    local = tate_algorithm(curve, prime)
    if local.reduction == "split_multiplicative":
        return 1, -1
    if local.reduction == "nonsplit_multiplicative":
        return 1, 1
    return (1,)
