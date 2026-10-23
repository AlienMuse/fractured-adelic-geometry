#!/usr/bin/env python
"""Independent BSD certificate checker.

This file intentionally has no dependency on ``bsdkit`` and is kept below
roughly 300 source lines so that its exact arithmetic can be audited by eye.
It checks hashes/schema plus C1 point counts and C4 Tate-limit height witnesses.
Unsupported evidence is rejected, never accepted by default.
"""

from __future__ import annotations

import hashlib
import itertools
import json
import sys
from fractions import Fraction as F
from functools import lru_cache
from math import isqrt, lcm


def canonical(value: object) -> bytes:
    return json.dumps(value, sort_keys=True, separators=(",", ":"), ensure_ascii=True).encode("ascii")


def digest(value: object) -> str:
    return "sha256:" + hashlib.sha256(canonical(value)).hexdigest()


def invs(a: tuple[int, ...]) -> tuple[int, int, int, int, int, int, int]:
    a1, a2, a3, a4, a6 = a
    b2 = a1 * a1 + 4 * a2
    b4 = a1 * a3 + 2 * a4
    b6 = a3 * a3 + 4 * a6
    b8 = a1 * a1 * a6 + 4 * a2 * a6 - a1 * a3 * a4 + a2 * a3 * a3 - a4 * a4
    c4 = b2 * b2 - 24 * b4
    c6 = -b2**3 + 36 * b2 * b4 - 216 * b6
    delta = -b2 * b2 * b8 - 8 * b4**3 - 27 * b6**2 + 9 * b2 * b4 * b6
    return b2, b4, b6, b8, c4, c6, delta


def on_curve(a: tuple[int, ...], p: tuple[F, F] | None) -> bool:
    if p is None:
        return True
    x, y = p
    a1, a2, a3, a4, a6 = a
    return y * y + a1 * x * y + a3 * y == x**3 + a2 * x * x + a4 * x + a6


def add(a: tuple[int, ...], p: tuple[F, F] | None, q: tuple[F, F] | None) -> tuple[F, F] | None:
    if p is None:
        return q
    if q is None:
        return p
    a1, a2, a3, a4, a6 = a
    x1, y1 = p
    x2, y2 = q
    if x1 == x2 and y2 == -y1 - a1 * x1 - a3:
        return None
    if x1 != x2:
        m = (y2 - y1) / (x2 - x1)
        n = (y1 * x2 - y2 * x1) / (x2 - x1)
    else:
        d = 2 * y1 + a1 * x1 + a3
        if d == 0:
            return None
        m = (3 * x1 * x1 + 2 * a2 * x1 + a4 - a1 * y1) / d
        n = (-x1**3 + a4 * x1 + 2 * a6 - a3 * y1) / d
    x3 = m * m + a1 * m - a2 - x1 - x2
    return x3, -(m + a1) * x3 - n - a3


def iadd(x: tuple[F, F], y: tuple[F, F]) -> tuple[F, F]:
    return x[0] + y[0], x[1] + y[1]


def ineg(x: tuple[F, F]) -> tuple[F, F]:
    return -x[1], -x[0]


def imul(x: tuple[F, F], y: tuple[F, F]) -> tuple[F, F]:
    values = (x[0] * y[0], x[0] * y[1], x[1] * y[0], x[1] * y[1])
    return min(values), max(values)


def idiv(x: tuple[F, F], n: int) -> tuple[F, F]:
    return x[0] / n, x[1] / n


def exp_pos(x: F, bits: int = 150) -> tuple[F, F]:
    halves, t = 0, x
    while t > F(1, 8):
        t /= 2
        halves += 1
    term = total = F(1)
    n, target = 0, F(1, 1 << (bits + halves + 8))
    while True:
        n += 1
        term *= t / n
        total += term
        rem = term * t / (n + 1) / (1 - t / (n + 2))
        if rem <= target:
            break
    lo, hi = total, total + rem
    for _ in range(halves):
        lo, hi = lo * lo, hi * hi
    return lo, hi


def log_unit(y: F, bits: int) -> tuple[F, F]:
    z = (y - 1) / (y + 1)
    if not z:
        return F(0), F(0)
    z2, power, total, n = z * z, z, F(0), 0
    while True:
        total += power / (2 * n + 1)
        nxt = power * z2
        tail = 2 * nxt / ((2 * n + 3) * (1 - z2))
        if tail <= F(1, 1 << (bits + 6)):
            return 2 * total, 2 * total + tail
        power, n = nxt, n + 1


@lru_cache(maxsize=8)
def log_two(bits: int) -> tuple[F, F]:
    return log_unit(F(2), bits + 4)


def log_bounds(x: F, bits: int = 140) -> tuple[F, F]:
    if x <= 0:
        raise ValueError("non-positive logarithm")
    k = x.numerator.bit_length() - x.denominator.bit_length()
    y = x / (1 << k) if k >= 0 else x * (1 << -k)
    while y < 1:
        y, k = y * 2, k - 1
    while y >= 2:
        y, k = y / 2, k + 1
    lo, hi = log_unit(y, bits + 8)
    l2, h2 = log_two(bits + 8)
    return (lo + k * l2, hi + k * h2) if k >= 0 else (lo + k * h2, hi + k * l2)


def trim(p: list[F]) -> list[F]:
    while len(p) > 1 and p[-1] == 0:
        p.pop()
    return p


def padd(a: list[F], b: list[F]) -> list[F]:
    return trim([(a[i] if i < len(a) else 0) + (b[i] if i < len(b) else 0) for i in range(max(len(a), len(b)))])


def pmul(a: list[F], b: list[F]) -> list[F]:
    out = [F(0)] * (len(a) + len(b) - 1)
    for i, x in enumerate(a):
        for j, y in enumerate(b):
            out[i + j] += x * y
    return trim(out)


def pscale(a: list[F], c: F) -> list[F]:
    return trim([c * x for x in a])


def pdiv(a: list[F], b: list[F]) -> tuple[list[F], list[F]]:
    a, b = trim(a[:]), trim(b[:])
    q = [F(0)] * max(1, len(a) - len(b) + 1)
    while a != [0] and len(a) >= len(b):
        d, c = len(a) - len(b), a[-1] / b[-1]
        q[d] += c
        a = padd(a, [F(0)] * d + pscale(b, -c))
    return trim(q), trim(a)


def bezout(a: list[F], b: list[F]) -> tuple[list[F], list[F]]:
    r0, r1, s0, s1, t0, t1 = trim(a[:]), trim(b[:]), [F(1)], [F(0)], [F(0)], [F(1)]
    while r1 != [0]:
        q, r = pdiv(r0, r1)
        r0, r1 = r1, r
        s0, s1 = s1, padd(s0, pscale(pmul(q, s1), -1))
        t0, t1 = t1, padd(t0, pscale(pmul(q, t1), -1))
    return pscale(s0, 1 / r0[0]), pscale(t0, 1 / r0[0])


@lru_cache(maxsize=32)
def height_constant(a: tuple[int, ...]) -> F:
    b2, b4, b6, b8, _, _, _ = invs(a)
    f = [F(-b8), F(-2 * b6), F(-b4), F(0), F(1)]
    g = [F(b6), F(2 * b4), F(b2), F(4), F(0)]
    aa, bb = bezout(f, g)
    ar, br = bezout(list(reversed(f)), list(reversed(g)))
    den_left = den_right = 1
    for poly in (aa, bb):
        for c in poly:
            den_left = lcm(den_left, c.denominator)
    for poly in (ar, br):
        for c in poly:
            den_right = lcm(den_right, c.denominator)
    k = max(sum(map(abs, aa)) + sum(map(abs, bb)), sum(map(abs, ar)) + sum(map(abs, br)))
    upper = max(1 + abs(b4) + 2 * abs(b6) + abs(b8), 4 + abs(b2) + 2 * abs(b4) + abs(b6))
    return log_bounds(max(F(upper), k * den_left * den_right, F(1)))[1]


def height(a: tuple[int, ...], p: tuple[F, F] | None, n: int) -> tuple[F, F]:
    if p is None:
        return F(0), F(0)
    q = p
    for _ in range(n):
        q = add(a, q, q)
        if q is None:
            return F(0), F(0)
    size = max(abs(q[0].numerator), q[0].denominator)
    h = idiv(log_bounds(F(size)), 2 * 4**n)
    error = height_constant(a) / (6 * 4**n)
    return h[0] - error, h[1] + error


def determinant(matrix: list[list[tuple[F, F]]]) -> tuple[F, F]:
    answer = (F(0), F(0))
    for perm in itertools.permutations(range(len(matrix))):
        inv = sum(perm[i] > perm[j] for i in range(len(perm)) for j in range(i + 1, len(perm)))
        term = (F(-1), F(-1)) if inv % 2 else (F(1), F(1))
        for i, j in enumerate(perm):
            term = imul(term, matrix[i][j])
        answer = iadd(answer, term)
    return answer


def check_rank(a: tuple[int, ...], data: dict[str, object]) -> None:
    points = []
    for raw in data["points"]:
        p = (F(raw["x"]), F(raw["y"]))
        if not on_curve(a, p):
            raise ValueError("claimed point is off curve")
        points.append(p)
    n = int(data["doublings"])
    hs = [height(a, p, n) for p in points]
    matrix = [[(F(0), F(0)) for _ in points] for _ in points]
    for i in range(len(points)):
        matrix[i][i] = hs[i]
        for j in range(i):
            value = idiv(iadd(height(a, add(a, points[i], points[j]), n), iadd(ineg(hs[i]), ineg(hs[j]))), 2)
            matrix[i][j] = matrix[j][i] = value
    det = determinant(matrix) if matrix else (F(1), F(1))
    if det[0] <= 0 <= det[1]:
        raise ValueError("height determinant does not certify independence")


def check_ap(a: tuple[int, ...], data: dict[str, object]) -> None:
    p, order = int(data["prime"]), int(data["order"])
    if p < 2 or any(p % d == 0 for d in range(2, isqrt(p) + 1)):
        raise ValueError("non-prime field")
    count = 1
    a1, a2, a3, a4, a6 = a
    for x in range(p):
        for y in range(p):
            count += (y * y + a1 * x * y + a3 * y - x**3 - a2 * x*x - a4*x - a6) % p == 0
    if count != order or int(data["ap"]) != p + 1 - count:
        raise ValueError("point-count witness fails")


def check(path: str) -> str:
    cert = json.loads(open(path, encoding="utf-8").read())
    required = {"version", "identification", "claim", "evidence", "dependencies", "assumptions", "rigour", "checker", "content_hash"}
    if set(cert) != required or cert["version"] != "1.0.0":
        raise ValueError("strict certificate schema fails")
    unsigned = dict(cert)
    claimed_hash = unsigned.pop("content_hash")
    if digest(unsigned) != claimed_hash:
        raise ValueError("certificate hash mismatch")
    model = tuple(map(int, cert["identification"]["model"]))
    if len(model) != 5 or invs(model)[-1] == 0:
        raise ValueError("invalid model")
    if digest({"base_field": "Q", "model": [str(x) for x in model]}) != cert["identification"]["curve_hash"]:
        raise ValueError("curve hash mismatch")
    for item in cert["evidence"]:
        if digest(item["data"]) != item["hash"]:
            raise ValueError("evidence hash mismatch")
        if item["kind"] == "frobenius_trace":
            check_ap(model, item["data"])
        elif item["kind"] == "rank_lower_height":
            check_rank(model, item["data"])
        else:
            raise ValueError("unsupported evidence kind")
    return claimed_hash


if __name__ == "__main__":
    try:
        print(json.dumps({"accepted": True, "content_hash": check(sys.argv[1])}, sort_keys=True))
    except Exception as error:
        print(json.dumps({"accepted": False, "error": str(error)}, sort_keys=True))
        raise SystemExit(1)
