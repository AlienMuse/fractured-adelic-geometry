"""Runnable, certificate-first reference implementation for Part VII.

Author:       Vincent Liu
Organisation: WiseMotif.ai

Companion code to *Fractured Adelic Geometry: A Foundational Framework for the Birch and Swinnerton-Dyer Conjecture* (WiseMotif Monograph of Mathematical Intelligence, Series 04).  Nothing in this package proves the BSD conjecture, which
remains open; see the monograph's Statement of Epistemic Status.
"""

__author__ = "Vincent Liu"
__organisation__ = "WiseMotif.ai"

from .data import RUNNING_CURVES, CurveRecord, get_curve
from .ellcurve import EllipticCurve, Point
from .intervals import Interval

__all__ = [
    "CurveRecord",
    "EllipticCurve",
    "Interval",
    "Point",
    "RUNNING_CURVES",
    "get_curve",
]
