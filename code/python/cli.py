"""Command-line façade for the certificate-first BSD reference package."""

from __future__ import annotations

import argparse
import json
import subprocess
import sys
from pathlib import Path
from typing import Any, Sequence

from bsdkit.certificates import (
    make_analytic_certificate,
    make_ap_certificate,
    make_local_certificate,
    make_rank_lower_certificate,
)
from bsdkit.data import get_curve
from bsdkit.descent import determine_rank
from bsdkit.frobenius import count_points_bsgs, count_points_naive, frobenius_trace
from bsdkit.lfunction import certified_l_derivative
from bsdkit.reduction import bad_reduction_data, conductor, global_root_number


def _print(value: object) -> None:
    print(json.dumps(value, sort_keys=True, indent=2))


def _local_dict(local: object) -> dict[str, object]:
    return {
        "prime": local.prime,
        "reduction": local.reduction,
        "kodaira": local.kodaira,
        "conductor_exponent": local.conductor_exponent,
        "discriminant_exponent": local.discriminant_exponent,
        "tamagawa": local.tamagawa,
        "local_root_number": local.local_root_number,
        "rigour": local.rigour,
    }


def command_curve(args: argparse.Namespace) -> int:
    """Print exact curve invariants and local data."""

    record = get_curve(args.label)
    curve = record.curve
    n_value, conductor_rigour = conductor(curve)
    sign, sign_rigour = global_root_number(curve)
    torsion = curve.torsion_subgroup()
    value = curve.to_dict()
    value.update(
        {
            "label": record.label,
            "minimal_model": list(curve.minimal_model().curve.coefficients),
            "minimality_rigour": curve.minimal_model().rigour,
            "conductor": n_value,
            "conductor_rigour": conductor_rigour,
            "sign": sign,
            "sign_rigour": sign_rigour,
            "torsion": {
                "lower_order": torsion.order_lower,
                "upper_order": torsion.order_upper,
                "structure": torsion.structure,
                "rigour": torsion.rigour,
            },
            "bad_reduction": [_local_dict(item) for item in bad_reduction_data(curve)],
        }
    )
    _print(value)
    return 0


def command_ap(args: argparse.Namespace) -> int:
    """Print exact point counts and traces at requested primes."""

    curve = get_curve(args.label).curve
    rows = []
    for prime in args.primes:
        naive = count_points_naive(curve, prime)
        bsgs = count_points_bsgs(curve, prime)
        trace = frobenius_trace(curve, prime, args.method)
        rows.append(
            {
                "prime": prime,
                "point_count_naive": naive,
                "point_count_bsgs": bsgs,
                "ap": trace,
                "hasse": trace * trace <= 4 * prime,
                "rigour": "proved",
            }
        )
    _print({"label": args.label, "traces": rows})
    return 0


def command_lvalue(args: argparse.Namespace) -> int:
    """Print an L-derivative interval and its truncation metadata."""

    result = certified_l_derivative(
        get_curve(args.label).curve, args.derivative, args.bits
    )
    _print(
        {
            "label": args.label,
            "derivative": result.derivative,
            "interval": result.interval.to_dict(),
            "decimal_interval": [
                float(result.interval.lower),
                float(result.interval.upper),
            ],
            "cutoff": result.cutoff,
            "tail_bound": (
                f"{result.tail_bound.numerator}/{result.tail_bound.denominator}"
            ),
            "conductor": result.conductor,
            "sign": result.sign,
            "rigour": result.rigour,
            "method": result.method,
        }
    )
    return 0


def command_rank(args: argparse.Namespace) -> int:
    """Print certified rank bounds and the exact Chapter 44 verdict."""

    result = determine_rank(
        get_curve(args.label).curve, args.height, args.denominator_bound
    )
    _print(
        {
            "label": args.label,
            "lower_bound": result.lower_bound,
            "upper_bound": result.upper_bound,
            "verdict": result.verdict,
            "rank": result.rank,
            "lower_rigour": result.lower_rigour,
            "upper_rigour": result.upper_rigour,
            "points": [point.to_json() for point in result.points],
            "obstruction": result.obstruction,
        }
    )
    return 0


def command_certificate(args: argparse.Namespace) -> int:
    """Produce a versioned C1, C4, or C6 certificate."""

    curve = get_curve(args.label).curve
    if args.kind == "ap":
        certificate = make_ap_certificate(curve, args.prime)
    elif args.kind == "local":
        certificate = make_local_certificate(curve)
    elif args.kind == "rank":
        rank = determine_rank(curve, args.height, args.denominator_bound)
        certificate = make_rank_lower_certificate(curve, rank.points)
    else:
        result = certified_l_derivative(curve, args.derivative, args.bits)
        certificate = make_analytic_certificate(curve, result)
    text = certificate.to_json() + "\n"
    if args.output:
        Path(args.output).write_text(text, encoding="utf-8")
        _print(
            {
                "output": str(Path(args.output)),
                "content_hash": certificate.content_hash,
                "rigour": certificate.rigour,
            }
        )
    else:
        print(text, end="")
    return 0


def command_verify(args: argparse.Namespace) -> int:
    """Run the separate dependency-free checker process."""

    checker = Path(__file__).resolve().parent.parent / "verify" / "check.py"
    completed = subprocess.run(
        [sys.executable, str(checker), args.path],
        check=False,
        text=True,
        capture_output=True,
    )
    print(completed.stdout, end="")
    if completed.stderr:
        print(completed.stderr, file=sys.stderr, end="")
    return completed.returncode


def build_parser() -> argparse.ArgumentParser:
    """Construct the complete CLI grammar."""

    parser = argparse.ArgumentParser(description=__doc__)
    commands = parser.add_subparsers(dest="command", required=True)

    curve = commands.add_parser("curve", help="invariants and reduction data")
    curve.add_argument("label")
    curve.set_defaults(function=command_curve)

    ap = commands.add_parser("ap", help="Frobenius traces")
    ap.add_argument("label")
    ap.add_argument("primes", nargs="+", type=int)
    ap.add_argument("--method", choices=("naive", "bsgs"), default="naive")
    ap.set_defaults(function=command_ap)

    lvalue = commands.add_parser("lvalue", help="central L-derivative interval")
    lvalue.add_argument("label")
    lvalue.add_argument("--derivative", "-r", type=int, default=0)
    lvalue.add_argument("--bits", type=int, default=40)
    lvalue.set_defaults(function=command_lvalue)

    rank = commands.add_parser("rank", help="certified lower/upper rank bounds")
    rank.add_argument("label")
    rank.add_argument("--height", type=int, default=10)
    rank.add_argument("--denominator-bound", type=int, default=1)
    rank.set_defaults(function=command_rank)

    certificate = commands.add_parser("certificate", help="emit certificate JSON")
    certificate.add_argument("label")
    certificate.add_argument(
        "--kind", choices=("ap", "local", "rank", "lvalue"), default="ap"
    )
    certificate.add_argument("--prime", type=int, default=5)
    certificate.add_argument("--derivative", "-r", type=int, default=0)
    certificate.add_argument("--bits", type=int, default=40)
    certificate.add_argument("--height", type=int, default=10)
    certificate.add_argument("--denominator-bound", type=int, default=1)
    certificate.add_argument("--output", "-o")
    certificate.set_defaults(function=command_certificate)

    verify = commands.add_parser("verify", help="run the independent checker")
    verify.add_argument("path")
    verify.set_defaults(function=command_verify)
    return parser


def main(argv: Sequence[str] | None = None) -> int:
    """Parse arguments and run one command."""

    args = build_parser().parse_args(argv)
    return int(args.function(args))


if __name__ == "__main__":
    raise SystemExit(main())
