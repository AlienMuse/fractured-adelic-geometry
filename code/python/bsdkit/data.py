"""The five running curves of the book (Appendix G, Table G.1), as local regression data.

The expected conductor, rank, torsion, sign, and listed generators are
regression metadata only.  Computational claims and certificates are produced
from the equations and witnesses; an expected field never discharges a proof
obligation.
"""

from __future__ import annotations

from dataclasses import dataclass

from .ellcurve import EllipticCurve, Point


@dataclass(frozen=True, slots=True)
class CurveRecord:
    """A permitted running-curve record and its regression expectations."""

    label: str
    curve: EllipticCurve
    expected_conductor: int
    expected_rank: int
    expected_torsion: int
    expected_sign: int
    generators: tuple[Point, ...]


RUNNING_CURVES: dict[str, CurveRecord] = {
    "11.a1": CurveRecord(
        "11.a1", EllipticCurve([0, -1, 1, -10, -20]), 11, 0, 5, 1, ()
    ),
    "37.a1": CurveRecord(
        "37.a1", EllipticCurve([0, 0, 1, -1, 0]), 37, 1, 1, -1, (Point(0, 0),)
    ),
    "37.b1": CurveRecord(
        "37.b1", EllipticCurve([0, 1, 1, -23, -50]), 37, 0, 3, 1, ()
    ),
    "389.a1": CurveRecord(
        "389.a1",
        EllipticCurve([0, 1, 1, -2, 0]),
        389,
        2,
        1,
        1,
        (Point(0, 0), Point(-1, 1)),
    ),
    "5077.a1": CurveRecord(
        "5077.a1",
        EllipticCurve([0, 0, 1, -7, 6]),
        5077,
        3,
        1,
        -1,
        (Point(-2, 3), Point(-1, 3), Point(0, 2)),
    ),
}


def get_curve(label: str) -> CurveRecord:
    """Resolve one of the five authorised labels."""

    try:
        return RUNNING_CURVES[label]
    except KeyError as error:
        raise ValueError(
            f"unknown local curve {label!r}; available: {', '.join(RUNNING_CURVES)}"
        ) from error
