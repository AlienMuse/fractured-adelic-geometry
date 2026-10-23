"""Local reduction data from the finite branches of Tate's algorithm.

All running curves are semistable at odd primes, where the implementation is
complete: ``v_p(c4)=0`` gives type ``I_n``, splitness is checked from ``-c6``,
and the conductor and component group follow from Tate's theorem.  Additive
branches at primes at least five implement the valuation table but are tagged
``heuristic`` where a component-polynomial split test would be required.
Wild additive reduction at 2 or 3 is rejected rather than silently guessed.
"""

from __future__ import annotations

from dataclasses import dataclass
from typing import Literal

from .ellcurve import EllipticCurve, Rigour, factor_integer, valuation

ReductionType = Literal[
    "good", "split_multiplicative", "nonsplit_multiplicative", "additive"
]


@dataclass(frozen=True, slots=True)
class LocalReduction:
    """Terminal local data and the predicates selecting the Tate branch."""

    prime: int
    reduction: ReductionType
    kodaira: str
    conductor_exponent: int
    discriminant_exponent: int
    tamagawa: int
    local_root_number: int
    split: bool | None
    rigour: Rigour
    transcript: tuple[str, ...]


def _is_square_mod(value: int, prime: int) -> bool:
    value %= prime
    if value == 0:
        return True
    return pow(value, (prime - 1) // 2, prime) == 1


def tate_algorithm(curve: EllipticCurve, prime: int) -> LocalReduction:
    """Compute local data, with proved output on good/multiplicative branches."""

    if prime < 2:
        raise ValueError("prime must be at least two")
    v_delta = valuation(curve.discriminant, prime)
    transcript = [
        f"v_p(Delta)={v_delta}",
        f"v_p(c4)={valuation(curve.c4, prime)}",
        f"v_p(c6)={valuation(curve.c6, prime)}",
    ]
    if v_delta == 0:
        return LocalReduction(
            prime, "good", "I0", 0, 0, 1, 1, None, "proved", tuple(transcript)
        )
    if valuation(curve.c4, prime) == 0:
        if prime == 2:
            raise NotImplementedError("the multiplicative split test at p=2 is unsupported")
        split = _is_square_mod(-curve.c6, prime)
        reduction: ReductionType = (
            "split_multiplicative" if split else "nonsplit_multiplicative"
        )
        tamagawa = v_delta if split else (1 if v_delta % 2 else 2)
        transcript.append(f"-c6 square mod p={split}")
        return LocalReduction(
            prime,
            reduction,
            f"I{v_delta}",
            1,
            v_delta,
            tamagawa,
            -1 if split else 1,
            split,
            "proved",
            tuple(transcript),
        )

    if prime in (2, 3):
        raise NotImplementedError(
            "wild additive Tate branches at 2 and 3 require a full branch transcript"
        )

    # The Kodaira valuation table is exact at p >= 5.  Some component-group
    # orders need an additional splitting polynomial, so those are not promoted.
    if v_delta == 2:
        kodaira, tamagawa, rigour = "II", 1, "proved"
    elif v_delta == 3:
        kodaira, tamagawa, rigour = "III", 2, "proved"
    elif v_delta == 4:
        kodaira, tamagawa, rigour = "IV", 3, "heuristic"
    elif v_delta == 6:
        kodaira, tamagawa, rigour = "I0*", 4, "heuristic"
    elif v_delta == 8:
        kodaira, tamagawa, rigour = "IV*", 3, "heuristic"
    elif v_delta == 9:
        kodaira, tamagawa, rigour = "III*", 2, "proved"
    elif v_delta == 10:
        kodaira, tamagawa, rigour = "II*", 1, "proved"
    elif v_delta >= 7:
        kodaira, tamagawa, rigour = f"I{v_delta - 6}*", 4, "heuristic"
    else:
        raise NotImplementedError("unsupported additive Tate branch")
    transcript.append("p>=5 additive valuation branch")
    return LocalReduction(
        prime,
        "additive",
        kodaira,
        2,
        v_delta,
        tamagawa,
        1,
        None,
        rigour,
        tuple(transcript),
    )


def bad_reduction_data(curve: EllipticCurve) -> tuple[LocalReduction, ...]:
    """Run Tate's algorithm at every prime dividing the discriminant."""

    return tuple(tate_algorithm(curve, p) for p in factor_integer(curve.discriminant))


def conductor(curve: EllipticCurve) -> tuple[int, Rigour]:
    """Return the conductor and the weakest local rigour tag."""

    value = 1
    rigour: Rigour = "proved"
    for local in bad_reduction_data(curve):
        value *= local.prime**local.conductor_exponent
        if local.rigour != "proved":
            rigour = local.rigour
    return value, rigour


def global_root_number(curve: EllipticCurve) -> tuple[int, Rigour]:
    """Return the global sign, including the archimedean root number ``-1``."""

    sign = -1
    rigour: Rigour = "proved"
    for local in bad_reduction_data(curve):
        sign *= local.local_root_number
        if local.rigour != "proved":
            rigour = local.rigour
    return sign, rigour
