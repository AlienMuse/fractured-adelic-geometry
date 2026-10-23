"""C1--C7 certificate objects and canonical JSON content addressing.

The hierarchy follows Chapter 47.  ``proved``, ``conditional``, ``heuristic``
and ``numerical`` are distinct literal tags.  Hashes establish byte identity,
not mathematical truth; an independent level-specific checker must still
validate each inline evidence object.
"""

from __future__ import annotations

import hashlib
import json
from dataclasses import dataclass, field
from pathlib import Path
from typing import Any, ClassVar, Literal, TypeVar

from .ellcurve import EllipticCurve, Point, Rigour
from .frobenius import count_points_naive
from .heights import height_pairing_matrix, interval_determinant
from .intervals import Interval
from .lfunction import LValueResult
from .reduction import bad_reduction_data, conductor

CertificateLevel = Literal["C1", "C2", "C3", "C4", "C5", "C6", "C7"]


def _canonical_bytes(value: object) -> bytes:
    return json.dumps(
        value, sort_keys=True, separators=(",", ":"), ensure_ascii=True
    ).encode("ascii")


def _digest(value: object) -> str:
    return "sha256:" + hashlib.sha256(_canonical_bytes(value)).hexdigest()


def curve_hash(model: tuple[int, int, int, int, int]) -> str:
    """Hash the canonical base field and minimal model."""

    return _digest({"base_field": "Q", "model": [str(value) for value in model]})


@dataclass(frozen=True, slots=True)
class Evidence:
    """An inline, independently hashed evidence object."""

    kind: str
    data: dict[str, Any]
    media_type: str = "application/json"

    def to_dict(self) -> dict[str, Any]:
        return {
            "kind": self.kind,
            "hash": _digest(self.data),
            "media_type": self.media_type,
            "data": self.data,
        }


T = TypeVar("T", bound="Certificate")


@dataclass(frozen=True, slots=True)
class Certificate:
    """Common immutable fields of every certificate level."""

    model: tuple[int, int, int, int, int]
    claim_id: str
    statement: str
    evidence: tuple[Evidence, ...]
    rigour: Rigour
    dependencies: tuple[str, ...] = ()
    assumptions: tuple[str, ...] = ()
    checker_name: str = "bsdkit-independent-checker"
    checker_version: str = "1.0.0"
    version: str = "1.0.0"
    LEVEL: ClassVar[CertificateLevel] = "C1"

    def unsigned_dict(self) -> dict[str, Any]:
        """Return canonical semantic data, excluding the self hash."""

        return {
            "version": self.version,
            "identification": {
                "curve_hash": curve_hash(self.model),
                "model": [str(value) for value in self.model],
            },
            "claim": {
                "id": self.claim_id,
                "statement": self.statement,
                "level": self.LEVEL,
            },
            "evidence": [item.to_dict() for item in self.evidence],
            "dependencies": list(self.dependencies),
            "assumptions": list(self.assumptions),
            "rigour": self.rigour,
            "checker": {
                "name": self.checker_name,
                "version": self.checker_version,
                "hash": "sha256:"
                + hashlib.sha256(b"code/verify/check.py:1.0.0").hexdigest(),
            },
        }

    @property
    def content_hash(self) -> str:
        """Return the SHA-256 content address of the unsigned certificate."""

        return _digest(self.unsigned_dict())

    def to_dict(self) -> dict[str, Any]:
        """Return the canonical JSON object including its content hash."""

        value = self.unsigned_dict()
        value["content_hash"] = self.content_hash
        return value

    def to_json(self, *, indent: int | None = 2) -> str:
        """Serialise with stable key ordering."""

        return json.dumps(self.to_dict(), sort_keys=True, indent=indent)

    @classmethod
    def from_dict(cls: type[T], value: dict[str, Any]) -> T:
        """Parse, dispatch by level, and verify all content hashes."""

        expected = {
            "version",
            "identification",
            "claim",
            "evidence",
            "dependencies",
            "assumptions",
            "rigour",
            "checker",
            "content_hash",
        }
        if set(value) != expected:
            raise ValueError(f"certificate fields differ: {set(value) ^ expected}")
        claim = value["claim"]
        level = claim["level"]
        target = _LEVEL_CLASSES.get(level)
        if target is None:
            raise ValueError(f"unknown certificate level {level!r}")
        evidence: list[Evidence] = []
        for item in value["evidence"]:
            if _digest(item["data"]) != item["hash"]:
                raise ValueError("evidence content hash mismatch")
            evidence.append(Evidence(item["kind"], item["data"], item["media_type"]))
        identification = value["identification"]
        model = tuple(int(item) for item in identification["model"])
        if len(model) != 5 or curve_hash(model) != identification["curve_hash"]:
            raise ValueError("curve identification mismatch")
        checker = value["checker"]
        result = target(
            model=model,
            claim_id=claim["id"],
            statement=claim["statement"],
            evidence=tuple(evidence),
            rigour=value["rigour"],
            dependencies=tuple(value["dependencies"]),
            assumptions=tuple(value["assumptions"]),
            checker_name=checker["name"],
            checker_version=checker["version"],
            version=value["version"],
        )
        if result.content_hash != value["content_hash"]:
            raise ValueError("certificate content hash mismatch")
        return result  # type: ignore[return-value]

    @classmethod
    def from_json(cls: type[T], text: str) -> T:
        """Parse :meth:`to_json` output."""

        value = json.loads(text)
        if not isinstance(value, dict):
            raise ValueError("certificate must be a JSON object")
        return cls.from_dict(value)


@dataclass(frozen=True, slots=True)
class C1LocalDataCertificate(Certificate):
    """C1: minimal model, local data, or an exact Frobenius count."""

    LEVEL: ClassVar[CertificateLevel] = "C1"


@dataclass(frozen=True, slots=True)
class C2TorsionCertificate(Certificate):
    """C2: rational torsion generators and reduction bounds."""

    LEVEL: ClassVar[CertificateLevel] = "C2"


@dataclass(frozen=True, slots=True)
class C3SelmerCertificate(Certificate):
    """C3: a Selmer presentation with explicit completeness assumptions."""

    LEVEL: ClassVar[CertificateLevel] = "C3"


@dataclass(frozen=True, slots=True)
class C4RankLowerCertificate(Certificate):
    """C4: exact points and a certified non-singular height matrix."""

    LEVEL: ClassVar[CertificateLevel] = "C4"


@dataclass(frozen=True, slots=True)
class C5RankUpperCertificate(Certificate):
    """C5: a Selmer/torsion rank upper bound."""

    LEVEL: ClassVar[CertificateLevel] = "C5"


@dataclass(frozen=True, slots=True)
class C6AnalyticCertificate(Certificate):
    """C6: an incomplete-gamma interval and its truncation witness."""

    LEVEL: ClassVar[CertificateLevel] = "C6"


@dataclass(frozen=True, slots=True)
class C7BSDCertificate(Certificate):
    """C7: a dependency graph for the strongest justified BSD claim."""

    LEVEL: ClassVar[CertificateLevel] = "C7"


_LEVEL_CLASSES: dict[str, type[Certificate]] = {
    item.LEVEL: item
    for item in (
        C1LocalDataCertificate,
        C2TorsionCertificate,
        C3SelmerCertificate,
        C4RankLowerCertificate,
        C5RankUpperCertificate,
        C6AnalyticCertificate,
        C7BSDCertificate,
    )
}


def make_ap_certificate(curve: EllipticCurve, prime: int) -> C1LocalDataCertificate:
    """Produce a C1 exact point-count certificate."""

    order = count_points_naive(curve, prime)
    trace = prime + 1 - order
    evidence = Evidence("frobenius_trace", {"prime": prime, "order": order, "ap": trace})
    return C1LocalDataCertificate(
        curve.coefficients,
        f"ap:{prime}",
        f"a_{prime} = {trace}",
        (evidence,),
        "proved",
    )


def make_local_certificate(curve: EllipticCurve) -> C1LocalDataCertificate:
    """Produce a C1 semistable local-data certificate."""

    n_value, rigour = conductor(curve)
    locals_payload = [
        {
            "prime": item.prime,
            "reduction": item.reduction,
            "kodaira": item.kodaira,
            "conductor_exponent": item.conductor_exponent,
            "discriminant_exponent": item.discriminant_exponent,
            "tamagawa": item.tamagawa,
            "transcript": list(item.transcript),
        }
        for item in bad_reduction_data(curve)
    ]
    return C1LocalDataCertificate(
        curve.coefficients,
        "local-data",
        f"the conductor is {n_value} with the displayed local data",
        (Evidence("tate_local_data", {"conductor": n_value, "places": locals_payload}),),
        rigour,
    )


def make_rank_lower_certificate(
    curve: EllipticCurve, points: tuple[Point, ...], doublings: int = 4
) -> C4RankLowerCertificate:
    """Produce a C4 point and height-determinant certificate."""

    matrix = height_pairing_matrix(curve, points, doublings)
    determinant = interval_determinant(matrix)
    data = {
        "points": [point.to_json() for point in points],
        "doublings": doublings,
        "height_matrix": [[entry.to_dict() for entry in row] for row in matrix],
        "determinant": determinant.to_dict(),
    }
    rigour: Rigour = "proved" if determinant.excludes_zero() else "numerical"
    return C4RankLowerCertificate(
        curve.coefficients,
        "rank-lower",
        f"rank E(Q) >= {len(points)}",
        (Evidence("rank_lower_height", data),),
        rigour,
    )


def make_analytic_certificate(
    curve: EllipticCurve, result: LValueResult
) -> C6AnalyticCertificate:
    """Produce a C6 interval record."""

    data = {
        "derivative": result.derivative,
        "interval": result.interval.to_dict(),
        "cutoff": result.cutoff,
        "tail_bound": f"{result.tail_bound.numerator}/{result.tail_bound.denominator}",
        "conductor": result.conductor,
        "sign": result.sign,
        "method": result.method,
    }
    return C6AnalyticCertificate(
        curve.coefficients,
        f"L-derivative:{result.derivative}",
        f"L^({result.derivative})(E,1) is in the displayed interval",
        (Evidence("incomplete_gamma", data),),
        result.rigour,
    )


CERTIFICATE_SCHEMA: dict[str, Any] = {
    "$schema": "https://json-schema.org/draft/2020-12/schema",
    "$id": "https://bsd.example/schema/certificate-1.json",
    "type": "object",
    "additionalProperties": False,
    "required": [
        "version",
        "identification",
        "claim",
        "evidence",
        "dependencies",
        "assumptions",
        "rigour",
        "checker",
        "content_hash",
    ],
    "properties": {
        "version": {"const": "1.0.0"},
        "identification": {"type": "object"},
        "claim": {"type": "object"},
        "evidence": {"type": "array"},
        "dependencies": {"type": "array", "items": {"$ref": "#/$defs/hash"}},
        "assumptions": {"type": "array", "items": {"type": "string"}},
        "rigour": {
            "enum": ["proved", "conditional", "heuristic", "numerical"]
        },
        "checker": {"type": "object"},
        "content_hash": {"$ref": "#/$defs/hash"},
    },
    "$defs": {
        "hash": {"type": "string", "pattern": "^sha256:[0-9a-f]{64}$"}
    },
}


def emit_json_schema(path: str | Path) -> None:
    """Write the versioned JSON Schema."""

    Path(path).write_text(
        json.dumps(CERTIFICATE_SCHEMA, sort_keys=True, indent=2) + "\n",
        encoding="utf-8",
    )
