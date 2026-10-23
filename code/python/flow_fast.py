"""Double-precision evaluation of Lambda(E,s) on the critical line, zeros, the
Weyl count, and a numerical check of Weil's explicit formula.

Incomplete gamma is computed from the lower series / upper continued fraction
(Numerical Recipes scheme) in complex double precision.
"""
import cmath
import math
from flow_numerics import an_table, primes_upto

EPS = 1e-15
ITMAX = 4000


def cgamma(z):
    """Lanczos gamma for complex z."""
    g = 7
    p = [0.99999999999980993, 676.5203681218851, -1259.1392167224028,
         771.32342877765313, -176.61502916214059, 12.507343278686905,
         -0.13857109526572012, 9.9843695780195716e-6, 1.5056327351493116e-7]
    if z.real < 0.5:
        return math.pi / (cmath.sin(math.pi * z) * cgamma(1 - z))
    z -= 1
    x = p[0]
    for i in range(1, g + 2):
        x += p[i] / (z + i)
    t = z + g + 0.5
    return math.sqrt(2 * math.pi) * t ** (z + 0.5) * cmath.exp(-t) * x


def gammainc_upper(s, x):
    """Gamma(s,x) for complex s, real x>0."""
    if x < abs(s) + 1.0:
        # lower series: gamma(s,x) = x^s e^{-x} sum_{n>=0} x^n / (s(s+1)...(s+n))
        ap = s
        term = 1.0 / s
        total = term
        for _ in range(ITMAX):
            ap += 1
            term *= x / ap
            total += term
            if abs(term) < abs(total) * EPS:
                break
        low = total * cmath.exp(-x + s * cmath.log(x))
        return cgamma(s) - low
    # continued fraction (Lentz)
    tiny = 1e-300
    b = x + 1.0 - s
    c = 1.0 / tiny
    d = 1.0 / b
    h = d
    for i in range(1, ITMAX):
        an = -i * (i - s)
        b += 2.0
        d = an * d + b
        if abs(d) < tiny:
            d = tiny
        c = b + an / c
        if abs(c) < tiny:
            c = tiny
        d = 1.0 / d
        de = d * c
        h *= de
        if abs(de - 1.0) < EPS:
            break
    return cmath.exp(-x + s * cmath.log(x)) * h


CURVES = {
    "37.a1": dict(coeffs=(0, 0, 1, -1, 0), N=37, sign=-1, rank=1),
    "389.a1": dict(coeffs=(0, 1, 1, -2, 0), N=389, sign=+1, rank=2),
}


class Curve:
    def __init__(self, name, nmax):
        d = CURVES[name]
        self.name = name
        self.N = d["N"]
        self.w = d["sign"]
        self.rank_hint = d["rank"]
        self.ap, self.a = an_table(d["coeffs"], self.N, nmax)
        self.nmax = nmax
        self.c = 2 * math.pi / math.sqrt(self.N)

    def Lam(self, s):
        tot = 0j
        for n in range(1, self.nmax + 1):
            an = self.a[n]
            if an == 0:
                continue
            x = self.c * n
            tot += an * (x ** (-s) * gammainc_upper(s, x)
                         + self.w * x ** (s - 2) * gammainc_upper(2 - s, x))
        return tot

    def Z(self, t):
        v = self.Lam(1 + 1j * t)
        return v.real if self.w == 1 else v.imag

    def L(self, s):
        """Uncompleted L(E,s) = Lambda / (N^{s/2}(2pi)^{-s}Gamma(s))."""
        return self.Lam(s) / (self.N ** (s / 2) * (2 * math.pi) ** (-s) * cgamma(s))


def bisect(f, a, b, tol=1e-13):
    fa, fb = f(a), f(b)
    for _ in range(200):
        m = 0.5 * (a + b)
        fm = f(m)
        if fa * fm <= 0:
            b, fb = m, fm
        else:
            a, fa = m, fm
        if b - a < tol:
            break
    return 0.5 * (a + b)


def find_zeros(cv, tmax, step=0.02):
    out = []
    t = 1e-8
    prev = cv.Z(t)
    while t < tmax:
        t2 = t + step
        cur = cv.Z(t2)
        if prev * cur < 0:
            out.append(bisect(cv.Z, t, t2))
        prev, t = cur, t2
    return out


def weyl(N, T):
    return T / math.pi * math.log(T * math.sqrt(N) / (2 * math.pi * math.e))


def lambdaE(cv, pmax):
    """(n, Lambda_E(n)) for prime powers n <= pmax."""
    out = []
    for p in primes_upto(pmax):
        pk, k = p, 1
        prev2, prev = 2.0, float(cv.ap[p]) if p in cv.ap else None
        if prev is None:
            continue
        while pk <= pmax:
            out.append((pk, prev * math.log(p)))
            if cv.N % p == 0:
                nxt = float(cv.ap[p]) ** (k + 1)
            else:
                nxt = cv.ap[p] * prev - p * prev2
            prev2, prev = prev, nxt
            pk *= p
            k += 1
    return sorted(out)


def explicit_formula(cv, sigma, zeros_list, pmax):
    def g(u):
        return math.exp(-u * u / (2 * sigma * sigma)) / (sigma * math.sqrt(2 * math.pi))

    def h(r):
        return math.exp(-sigma * sigma * r * r / 2)

    lhs = 2.0 * sum(h(t) for t in zeros_list) + cv.rank_hint * h(0.0)
    const = g(0.0) * math.log(cv.N / (4 * math.pi ** 2))

    # archimedean: (1/2pi) int h(r)[psi(1+ir)+psi(1-ir)] dr  (Simpson)
    def integ(r):
        z = 1 + 1j * r
        return 2.0 * h(r) * digamma(z).real

    R, M = 30.0, 6000
    hstep = R / M
    tot = integ(0.0) + integ(R)
    for i in range(1, M):
        tot += (4 if i % 2 else 2) * integ(i * hstep)
    arch = 2 * (tot * hstep / 3) / (2 * math.pi)   # times 2 for r<0 by symmetry
    prime = sum(lam / n * (g(math.log(n)) + g(-math.log(n)))
                for n, lam in lambdaE(cv, pmax))
    rhs = const + arch - prime
    return lhs, const, arch, -prime, rhs


def digamma(z):
    r = 0j
    while z.real < 12:
        r -= 1 / z
        z += 1
    f = 1 / (z * z)
    return (r + cmath.log(z) - 0.5 / z
            + f * (-1 / 12.0 + f * (1 / 120.0 + f * (-1 / 252.0 + f * (1 / 240.0
                   + f * (-1 / 132.0))))))


if __name__ == "__main__":
    for nm in CURVES:
        cv = Curve(nm, 300)
        print(f"=== {nm}  N={cv.N}  sign={cv.w} ===")
        s = 2.5 + 0j
        direct = sum(cv.a[n] * n ** (-s) for n in range(1, cv.nmax + 1))
        print("  L(2.5) via fast series =", cv.L(2.5 + 0j))
        print("  L(2.5) via Dirichlet   =", direct)
        zs = find_zeros(cv, 25.0)
        print("  zeros t>0 of Lambda(E,1+it):")
        for z in zs:
            print(f"     {z:.10f}")
        for T in (10, 15, 20, 25):
            print(f"     N({T}) actual={len([z for z in zs if z<=T])} "
                  f"Weyl={weyl(cv.N, T):.4f}")
        for sg in (1.0, 1.5, 2.0):
            lhs, c0, ar, pr, rhs = explicit_formula(cv, sg, zs, 200000)
            print(f"  explicit formula sigma={sg}: LHS={lhs:.8f} const={c0:.8f} "
                  f"arch={ar:.8f} prime={pr:.8f} RHS={rhs:.8f} diff={lhs-rhs:.2e}")


