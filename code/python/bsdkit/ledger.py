"""Proof-obligation ledger loading and certificate-discharge reports."""

from __future__ import annotations

import json
from dataclasses import dataclass
from pathlib import Path
from typing import Literal, Sequence

from .certificates import Certificate

LedgerStatus = Literal["refuted", "open", "conditional", "proved"]
_STRENGTH = {"refuted": 0, "open": 1, "conditional": 2, "proved": 3}


@dataclass(frozen=True, slots=True)
class Obligation:
    """The six fields of the Chapter 51 obligation tuple."""

    identifier: str
    statement: str
    status: LedgerStatus
    dependencies: tuple[str, ...]
    provenance: dict[str, object]
    discharge_condition: str
    certificate_claims: tuple[str, ...] = ()


@dataclass(frozen=True, slots=True)
class Ledger:
    """A finite, dependency-checked collection of proof obligations."""

    obligations: tuple[Obligation, ...]

    @classmethod
    def load(cls, path: str | Path) -> "Ledger":
        """Load the machine-readable JSON form described in Appendix F."""

        value = json.loads(Path(path).read_text(encoding="utf-8"))
        records = value["obligations"] if isinstance(value, dict) else value
        obligations = tuple(
            Obligation(
                identifier=item["identifier"],
                statement=item["statement"],
                status=item["status"],
                dependencies=tuple(item.get("dependencies", [])),
                provenance=dict(item.get("provenance", {})),
                discharge_condition=item["discharge_condition"],
                certificate_claims=tuple(item.get("certificate_claims", [])),
            )
            for item in records
        )
        result = cls(obligations)
        result.validate()
        return result

    def validate(self) -> None:
        """Reject duplicate IDs, missing dependencies, cycles, and status inflation."""

        by_id = {item.identifier: item for item in self.obligations}
        if len(by_id) != len(self.obligations):
            raise ValueError("duplicate ledger identifier")
        visiting: set[str] = set()
        visited: set[str] = set()

        def visit(identifier: str) -> None:
            if identifier in visiting:
                raise ValueError("ledger dependency cycle")
            if identifier in visited:
                return
            visiting.add(identifier)
            item = by_id[identifier]
            for dependency in item.dependencies:
                if dependency not in by_id:
                    raise ValueError(f"missing ledger dependency {dependency}")
                visit(dependency)
                if _STRENGTH[item.status] > _STRENGTH[by_id[dependency].status]:
                    raise ValueError(f"status of {identifier} exceeds dependency")
            visiting.remove(identifier)
            visited.add(identifier)

        for identifier in by_id:
            visit(identifier)

    def discharge_report(
        self, certificates: Sequence[Certificate]
    ) -> dict[str, list[str]]:
        """Map each obligation to proved certificate hashes matching its claim IDs."""

        proved = [certificate for certificate in certificates if certificate.rigour == "proved"]
        report: dict[str, list[str]] = {}
        for obligation in self.obligations:
            report[obligation.identifier] = [
                certificate.content_hash
                for certificate in proved
                if certificate.claim_id in obligation.certificate_claims
            ]
        return report
