"""The certified central L-function engine of Chapter 45.

At derivative order zero the incomplete-gamma expansion simplifies to

``L(E,1) = (1+epsilon) sum(a_n/n * exp(-n/Q))``.

This module evaluates that identity entirely with rational outward intervals.
The omitted tail uses ``|a_n| <= d(n)*sqrt(n) <= 2n`` and therefore

``R_0(X) <= 4 exp(-(X+1)/Q)/(1-exp(-1/Q))``.

Higher derivatives require certified incomplete-gamma jets.  The lightweight
Python reference exposes a numerical fallback carrying ``certified=False``;
it never mislabels that fallback as a proof-producing C6 result.
"""

from __future__ import annotations

from dataclasses import dataclass
from fractions import Fraction
from math import ceil, log
from typing import Literal

from .ellcurve import EllipticCurve, Rigour
from .frobenius import frobenius_trace, primes_up_to
from .intervals import Interval, pi_interval
from .reduction import conductor, global_root_number


@dataclass(frozen=True, slots=True)
class LValueResult:
    """An L-derivative enclosure and its complete truncation metadata."""

    derivative: int
    interval: Interval
    cutoff: int
    tail_bound: Fraction
    conductor: int
    sign: int
    rigour: Rigour
    method: str


def dirichlet_coefficients(curve: EllipticCurve, bound: int) -> list[int]:
    """Generate exact ``a_n`` from prime traces and Euler recurrences."""

    if bound < 1:
        return [0]
    smallest = list(range(bound + 1))
    for p in range(2, int(bound**0.5) + 1):
        if smallest[p] == p:
            for multiple in range(p * p, bound + 1, p):
                if smallest[multiple] == multiple:
                    smallest[multiple] = p
    prime_traces = {
        p: frobenius_trace(curve, p)
        for p in primes_up_to(bound)
    }
    prime_power_values: dict[tuple[int, int], int] = {}
    for p, trace in prime_traces.items():
        value_previous_previous = 1
        value_previous = trace
        prime_power_values[p, 1] = trace
        exponent = 2
        power = p * p
        while power <= bound:
            if curve.discriminant % p:
                value = trace * value_previous - p * value_previous_previous
            else:
                value = trace**exponent
            prime_power_values[p, exponent] = value
            value_previous_previous, value_previous = value_previous, value
            exponent += 1
            power *= p

    coefficients = [0] * (bound + 1)
    coefficients[1] = 1
    for n in range(2, bound + 1):
        remaining = n
        value = 1
        while remaining > 1:
            p = smallest[remaining]
            exponent = 0
            while remaining % p == 0:
                exponent += 1
                remaining //= p
            value *= prime_power_values[p, exponent]
        coefficients[n] = value
    return coefficients


def _central_tail(q: Interval, cutoff: int, bits: int) -> Interval:
    exponent_first = Interval.exact(-(cutoff + 1)) / q
    exponent_step = Interval.exact(-1) / q
    numerator = 4 * exponent_first.exp(bits + 24)
    denominator = 1 - exponent_step.exp(bits + 24)
    return (numerator / denominator).quantize(bits + 12)


def _choose_cutoff(q: Interval, target: Fraction, bits: int) -> tuple[int, Interval]:
    estimate_q = float(q.upper)
    estimate_target = max(float(target), 1e-300)
    cutoff = max(1, ceil(estimate_q * log(8 / estimate_target)))
    while True:
        tail = _central_tail(q, cutoff, bits)
        if tail.upper <= target:
            return cutoff, tail
        cutoff += 1


def certified_l_derivative(
    curve: EllipticCurve, derivative: int = 0, bits: int = 40
) -> LValueResult:
    """Enclose ``L^(derivative)(E,1)`` with an honest rigour tag."""

    if derivative < 0:
        raise ValueError("derivative order must be non-negative")
    n_value, conductor_rigour = conductor(curve)
    sign, sign_rigour = global_root_number(curve)
    if conductor_rigour != "proved" or sign_rigour != "proved":
        raise ValueError("certified L-values require proved local data")
    if derivative == 0 and sign == -1:
        return LValueResult(
            0,
            Interval.exact(0),
            0,
            Fraction(0),
            n_value,
            sign,
            "proved",
            "functional-equation parity",
        )
    if derivative != 0:
        return _numerical_derivative(curve, derivative, bits, n_value, sign)

    work_bits = bits + 36
    q = (
        Interval.exact(n_value).sqrt(work_bits) / (2 * pi_interval(work_bits))
    ).quantize(work_bits)
    target = Fraction(1, 1 << (bits + 3))
    cutoff, tail = _choose_cutoff(q, target, work_bits)
    coefficients = dirichlet_coefficients(curve, cutoff)
    total = Interval.exact(0)
    for n in range(1, cutoff + 1):
        if coefficients[n] == 0:
            continue
        weight = (Interval.exact(-n) / q).exp(work_bits).quantize(bits + 24)
        total = (total + Fraction(2 * coefficients[n], n) * weight).quantize(
            bits + 24
        )
    answer = total.enlarge(tail.upper).quantize(bits)
    return LValueResult(
        0,
        answer,
        cutoff,
        tail.upper,
        n_value,
        sign,
        "proved",
        "incomplete-gamma central sum with explicit exponential tail",
    )


def _numerical_derivative(
    curve: EllipticCurve,
    derivative: int,
    bits: int,
    n_value: int,
    sign: int,
) -> LValueResult:
    """Numerical higher-jet fallback, deliberately not certification."""

    try:
        import mpmath as mp
    except ImportError as error:  # pragma: no cover
        raise RuntimeError("higher numerical derivatives require mpmath") from error

    mp.mp.dps = max(50, int(bits / 3.2) + 30)
    q = mp.sqrt(n_value) / (2 * mp.pi)
    cutoff = max(50, ceil(float(q) * (bits + 25)))
    coefficients = dirichlet_coefficients(curve, cutoff)

    def completed(s: object) -> object:
        first = mp.mpf("0")
        second = mp.mpf("0")
        for n in range(1, cutoff + 1):
            a_n = coefficients[n]
            if a_n:
                x = mp.mpf(n) / q
                first += a_n * q**s * n ** (-s) * mp.gammainc(s, x, mp.inf)
                second += (
                    sign
                    * a_n
                    * q ** (2 - s)
                    * n ** (s - 2)
                    * mp.gammainc(2 - s, x, mp.inf)
                )
        return (first + second) / (q**s * mp.gamma(s))

    midpoint_mp = mp.diff(completed, 1, derivative)
    midpoint = Fraction(mp.nstr(midpoint_mp, max(30, int(bits / 3.2) + 8)))
    radius = Fraction(1, 1 << max(8, bits - 8))
    return LValueResult(
        derivative,
        Interval.from_midpoint_radius(midpoint, radius, certified=False),
        cutoff,
        radius,
        n_value,
        sign,
        "numerical",
        "mpmath incomplete-gamma jet without a directed-rounding transcript",
    )


def completed_lambda(
    curve: EllipticCurve, s: Fraction, bits: int = 40
) -> Interval:
    """Return ``Lambda(E,s)`` at ``s=1`` from a certified central value.

    General ``s`` needs the higher special-function kernel and is intentionally
    unsupported by this compact checker path.
    """

    if s != 1:
        raise NotImplementedError("certified completed Lambda is implemented at s=1")
    result = certified_l_derivative(curve, 0, bits)
    q = Interval.exact(result.conductor).sqrt(bits + 32) / (
        2 * pi_interval(bits + 32)
    )
    return q * result.interval
