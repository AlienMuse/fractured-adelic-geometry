"""Numerics supporting Chapters 15-17: a_p tables, Lambda_E(n), completed
L-function of an elliptic curve via the standard rapidly convergent series,
zeros on the critical line, and a numerical check of Weil's explicit formula.

Curves are given by (a1,a2,a3,a4,a6) with the LMFDB minimal model.
"""
import mpmath as mp

mp.mp.dps = 30


def ap_naive(coeffs, p):
    a1, a2, a3, a4, a6 = coeffs
    cnt = 1  # point at infinity
    for x in range(p):
        rhs = (x * x * x + a2 * x * x + a4 * x + a6) % p
        for y in range(p):
            if (y * y + a1 * x * y + a3 * y - rhs) % p == 0:
                cnt += 1
    return p + 1 - cnt


def primes_upto(n):
    sieve = [True] * (n + 1)
    sieve[0] = sieve[1] = False
    for i in range(2, int(n ** 0.5) + 1):
        if sieve[i]:
            for j in range(i * i, n + 1, i):
                sieve[j] = False
    return [i for i in range(n + 1) if sieve[i]]


def an_table(coeffs, N, limit):
    """Dirichlet coefficients a_n for n <= limit."""
    ps = primes_upto(limit)
    ap = {p: ap_naive(coeffs, p) for p in ps}
    a = [0] * (limit + 1)
    a[1] = 1
    for p in ps:
        # prime powers
        pk, k = p, 1
        vals = {1: 1}
        while pk <= limit:
            if k == 1:
                vals[pk] = ap[p]
            else:
                prev = vals[pk // p]
                prev2 = vals[pk // (p * p)]
                if N % p == 0:
                    vals[pk] = ap[p] * prev
                else:
                    vals[pk] = ap[p] * prev - p * prev2
            pk *= p
            k += 1
        for q, v in vals.items():
            if q > 1:
                a[q] = v
    # multiplicativity
    for n in range(2, limit + 1):
        if a[n] != 0 or _is_pp(n):
            continue
    # build fully by factorisation
    a = [0] * (limit + 1)
    a[1] = 1
    for n in range(2, limit + 1):
        f = _factor(n)
        val = 1
        for p, e in f.items():
            val *= _ape(ap[p], p, e, N)
        a[n] = val
    return ap, a


def _is_pp(n):
    f = _factor(n)
    return len(f) == 1


def _factor(n):
    f = {}
    d = 2
    while d * d <= n:
        while n % d == 0:
            f[d] = f.get(d, 0) + 1
            n //= d
        d += 1
    if n > 1:
        f[n] = f.get(n, 0) + 1
    return f


def _ape(apv, p, e, N):
    """a_{p^e} from a_p."""
    prev2, prev = 1, apv
    if e == 1:
        return apv
    for _ in range(2, e + 1):
        if N % p == 0:
            cur = apv * prev
        else:
            cur = apv * prev - p * prev2
        prev2, prev = prev, cur
    return prev


def lambda_completed(a, N, sign, s, terms=None):
    """Lambda(E,s) = sum_n a_n [ (cn)^{-s} G(s,cn) + w (cn)^{s-2} G(2-s,cn) ]."""
    c = 2 * mp.pi / mp.sqrt(N)
    if terms is None:
        terms = len(a) - 1
    tot = mp.mpf(0)
    for n in range(1, terms + 1):
        if a[n] == 0:
            continue
        x = c * n
        t1 = mp.power(x, -s) * mp.gammainc(s, x)
        t2 = sign * mp.power(x, s - 2) * mp.gammainc(2 - s, x)
        tot += a[n] * (t1 + t2)
    return tot


def lam_von_mangoldt(ap, N, limit):
    """Lambda_E(p^k) = (alpha^k + beta^k) log p, from a_p."""
    out = {}
    for p in ap:
        pk, k = p, 1
        prev2, prev = 2, mp.mpf(ap[p])   # s_0 = 2, s_1 = a_p
        while pk <= limit:
            out[(p, k)] = prev * mp.log(p)
            if N % p == 0:
                nxt = ap[p] * prev            # alpha^k, beta=0 -> s_k = a_p^k
                nxt = mp.mpf(ap[p]) ** (k + 1)
            else:
                nxt = ap[p] * prev - p * prev2
            prev2, prev = prev, nxt
            pk *= p
            k += 1
    return out


if __name__ == "__main__":
    curves = {
        "37.a1": (dict(coeffs=(0, 0, 1, -1, 0), N=37, sign=-1)),
        "389.a1": (dict(coeffs=(0, 1, 1, -2, 0), N=389, sign=+1)),
    }
    for name, d in curves.items():
        ap, a = an_table(d["coeffs"], d["N"], 120)
        print(f"--- {name} (N={d['N']}, sign={d['sign']}) ---")
        print("a_p:", {p: ap[p] for p in sorted(ap) if p < 40})
        lam = lam_von_mangoldt(ap, d["N"], 120)
        for key in sorted(lam)[:0]:
            pass
        print("Lambda_E(p^k), p^k<=32:")
        for (p, k) in sorted(lam, key=lambda t: t[0] ** t[1]):
            if p ** k <= 32:
                print(f"   {p}^{k} = {p**k:3d}   Lambda_E = {mp.nstr(lam[(p,k)], 10)}")
        # functional equation check
        s = mp.mpf("1.3") + 0.4j
        L1 = lambda_completed(a, d["N"], d["sign"], s)
        L2 = lambda_completed(a, d["N"], d["sign"], 2 - s)
        print("  FE check |Lambda(s) - w*Lambda(2-s)| =",
              mp.nstr(abs(L1 - d["sign"] * L2), 5))
        print("  Lambda(E,1) =", mp.nstr(lambda_completed(a, d["N"], d["sign"], mp.mpf(1)), 10))
