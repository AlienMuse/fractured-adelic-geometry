/-
  BSD/Classical.lean

  The classical inputs the book uses, stated as Lean declarations, with an
  honest note against each about whether Mathlib has it.

  UNCHECKED.  Not compiled; see BSD/Basic.lean and README.md.

  CONVENTION, from Chapter 48: `sorry` marks a genuine gap that this tree
  claims should be closed; `axiom` marks a deliberate enlargement of the
  trusted base, used for theorems of the existing literature that are simply
  not available in Lean.  Recording Kolyvagin's theorem as an `axiom` is not a
  claim to have proved it; it is a claim to have made every downstream use of
  it visible to `#print axioms`.

  ON THE MATHLIB SURVEY.  Chapter 48 warns (its Warning "audit") against
  asserting the existence of particular declaration names, because names change
  far faster than a monograph is revised.  We obey: no Mathlib declaration is
  named below except `CommRing`, `Rat`, `Complex` and the `ring` tactic.
  Everything else is a local `axiom` with a TODO.  UNDERSTATING Mathlib's
  coverage is the intended failure mode.
-/

import Mathlib.Data.Rat.Defs
import Mathlib.Data.Complex.Basic
import Mathlib.Tactic.Ring
import BSD.Basic

namespace BSD

/-! ## 1. What Mathlib really has: Weierstrass models

This is the one part of the story that is genuinely available.  Chapter 48:
the library contains Weierstrass models over a commutative ring with the
derived quantities `b_i`, `c_4`, `c_6` and the discriminant; affine, projective
and Jacobian models; and the group law with associativity, proved by embedding
the points into a divisor class group (work of D. K. Angdinata with
contributions from J. Xu, developed inside the library).

We nevertheless re-declare the model here rather than import it, for a reason
that is methodological and not stylistic: we cannot check the library's
spelling from this environment, and a wrong import name would make the whole
file fail where a local definition merely duplicates.  A real development would
delete this section and import.
-/

universe u

/-- A Weierstrass model over a commutative ring.  Duplicated from Mathlib on
purpose; see the section header. -/
structure Weier (R : Type u) [CommRing R] where
  a1 : R
  a2 : R
  a3 : R
  a4 : R
  a6 : R

namespace Weier

variable {R : Type u} [CommRing R] (W : Weier R)

def b2 : R := W.a1 ^ 2 + 4 * W.a2

def b4 : R := 2 * W.a4 + W.a1 * W.a3

def b6 : R := W.a3 ^ 2 + 4 * W.a6

def b8 : R := W.a1 ^ 2 * W.a6 - W.a1 * W.a3 * W.a4
              + 4 * W.a2 * W.a6 + W.a2 * W.a3 ^ 2 - W.a4 ^ 2

def c4 : R := W.b2 ^ 2 - 24 * W.b4

def c6 : R := -W.b2 ^ 3 + 36 * W.b2 * W.b4 - 216 * W.b6

def disc : R := -W.b2 ^ 2 * W.b8 - 8 * W.b4 ^ 3 - 27 * W.b6 ^ 2
                + 9 * W.b2 * W.b4 * W.b6

/--
The identity relating `c_4`, `c_6` and the discriminant.  A polynomial
identity, hence provable by normalisation -- an instance of the general
phenomenon that formalising computation is cheap and formalising structure is
not (Chapter 48, sketch (1)).

The proof is transcribed verbatim from Chapter 48.  It has not been run.
-/
theorem c4_c6_disc : 1728 * W.disc = W.c4 ^ 3 - W.c6 ^ 2 := by
  simp only [disc, c4, c6, b2, b4, b6, b8]; ring

end Weier

/-- Weierstrass models over the rationals, the only case the certificates of
Part VII ever use. -/
abbrev WeierQ := Weier Rat

/-- The affine Weierstrass equation, as a proposition about a rational point. -/
def OnCurve (W : WeierQ) (P : Rat × Rat) : Prop :=
  P.2 ^ 2 + W.a1 * P.1 * P.2 + W.a3 * P.2
    = P.1 ^ 3 + W.a2 * P.1 ^ 2 + W.a4 * P.1 + W.a6

/-- The decision procedure for `OnCurve`: exact rational arithmetic, evaluated
by the kernel.  `native_decide` is forbidden throughout this tree (Chapter 48,
sketch (7), and Chapter 52 on the trust hierarchy). -/
def onCurveB (W : WeierQ) (P : Rat × Rat) : Bool :=
  decide (P.2 ^ 2 + W.a1 * P.1 * P.2 + W.a3 * P.2
    = P.1 ^ 3 + W.a2 * P.1 ^ 2 + W.a4 * P.1 + W.a6)

/-- Soundness of the on-curve check.  A real proof: `of_decide_eq_true` is the
whole content, because `OnCurve` is by definition the proposition decided. -/
theorem onCurveB_sound (W : WeierQ) (P : Rat × Rat) (h : onCurveB W P = true) :
    OnCurve W P :=
  of_decide_eq_true h

/-! ## 2. What Mathlib does not have

Chapter 48's table lists, as absent at the time of writing: the Mordell--Weil
theorem, rank and regulator; Neron models over a Dedekind base (the deepest
single gap); `c_p`, Kodaira types, the conductor and `Omega_E`; continuous
`H^1(Q, -)`, Poitou--Tate, Selmer groups, Sha and Cassels--Tate; the analytic
continuation of `L(E, s)` and hence `ord_{s=1} L(E, s)`.  Partial: `E[n]` as a
group scheme, the Weil pairing and the Tate module; Weil and canonical heights;
`a_p`, the Euler product and `L(E, s)` on the half-plane of convergence.

Everything in this section is therefore a local `axiom` or a labelled `sorry`.
-/

/-- The Mordell--Weil group of a curve over `Q`.  Absent.
TODO: replace with the point group of an `EllipticCurve` over a number field
once the group-law API is confirmed to cover what is needed. -/
axiom MWGroup : WeierQ → Type

/-- The rank of the Mordell--Weil group, defined as in Chapter 48, sketch (2),
by tensoring with `Q`: basis-free and torsion-insensitive.  Absent. -/
axiom mwRank : WeierQ → Nat

/-- `E(Q)` is a torsion group.  Absent. -/
axiom MWIsTorsion : WeierQ → Prop

/-- `E(Q)` is finitely generated. -/
axiom MWFinitelyGenerated : WeierQ → Prop

/--
The Mordell--Weil theorem.  KNOWN in the literature (Mordell 1922; Weil 1929);
**absent from Mathlib**, and recorded here as an `axiom` so that every
downstream use is visible to `#print axioms`.  Chapter 48, sketch (2), does
exactly this.
-/
axiom mordellWeil_fg (W : WeierQ) : MWFinitelyGenerated W

/--
Rank zero is equivalent to being torsion.  Elementary given the definition of
the rank as a `Q`-dimension, but the definition is not available, so this is an
obligation rather than a proof.  Chapter 48, sketch (2), leaves the same gap.
-/
theorem mwRank_eq_zero_iff (W : WeierQ) : mwRank W = 0 ↔ MWIsTorsion W := by
  -- OBLIGATION: obl-mw-rank-zero-iff-torsion
  sorry

/-- Continuous cohomology of a profinite group with coefficients in a
topological module.  Chapter 48, sketch (3): "a milestone, not a definition
available at the time of writing".  Absent. -/
axiom H1cont : Type → Type → Type

/-- The `n`-Selmer group.  Absent: it is a kernel of a map of abelian groups,
trivial *given* continuous Galois cohomology and the localisation maps,
impossible without them. -/
axiom SelmerGroup : WeierQ → Nat → Type

/-- The Tate--Shafarevich group.  Absent. -/
axiom Sha : WeierQ → Type

/-- Finiteness of Sha, as a proposition.  **Not a theorem.**  It is one of the
standing imported conjectures of the book (the register, Chapter 3 and Table 41.3), and it
is subsumed by Obstruction VII. -/
axiom ShaIsFinite : WeierQ → Prop

/-- Finiteness of Sha as a hypothesis *class*, so that conditionality is
machine-visible (Chapter 48, sketch (3)). -/
class ShaFinite (W : WeierQ) : Prop where
  out : ShaIsFinite W

/-- The Neron local subgroup `E_0(Q_v)`.  Requires the Neron model over the
local ring at `v`.  Absent; Chapter 48 calls the Neron model the deepest single
gap. -/
axiom NeronLocalIndex : WeierQ → Nat → Nat

/-- The Tamagawa number `c_v = [E(Q_v) : E_0(Q_v)]`.  A one-liner whose content
is entirely in the Neron model. -/
def tamagawa (W : WeierQ) (v : Nat) : Nat := NeronLocalIndex W v

/-- Positivity of the Tamagawa numbers.  KNOWN; absent; axiomatised. -/
axiom tamagawa_pos (W : WeierQ) (v : Nat) : 0 < tamagawa W v

/-- The real period `Omega_E`.  Absent. -/
axiom realPeriod : WeierQ → Real

/-- The Neron--Tate regulator.  Absent: heights on projective space exist, but
the height machine and the Neron--Tate limit are not assembled. -/
axiom regulator : WeierQ → Real

/-! ## 3. The analytic side, and the relativisation device

The Euler product defining `L(E, s)` converges only for `Re(s) > 3/2`, so to
speak of the order of vanishing at `s = 1` one must first have the analytic
continuation, and the only known route to it is modularity.  Chapter 48's
escape is to relativise: define the analytic rank as a function of the curve
*together with a continuation datum*.  Modularity then becomes the assertion
that such a datum exists, quarantined as an explicit hypothesis.

Chapter 48 is explicit that this is no substitute for modularity: a development
founded on it proves theorems of the form "for every continuation datum D,
...", vacuous if no datum exists.  What it buys is that the point at which the
analytic input is needed becomes a binder rather than a footnote.
-/

/-- An entire function.
TODO: replace with Mathlib's notion (differentiability of a complex function on
all of the complex plane) once the exact spelling is confirmed. -/
axiom IsEntire : (Complex → Complex) → Prop

/-- The sum of a Dirichlet series, where it converges.
TODO: replace with Mathlib's `L`-series infrastructure (largely due to
D. Loeffler and collaborators) once the exact name and argument order are
confirmed. -/
axiom dirichletSum : (Nat → Complex) → Complex → Complex

/-- The Dirichlet coefficients `a_n` of `L(E, s)`.  Mathlib has point counting
and, in part, the Hasse bound, so this is the closest thing in the file to
being available; we do not rely on that. -/
axiom dirichletCoeff : WeierQ → Nat → Complex

/-- The order of vanishing of a function at a point, as a natural number.
Meaningful only for a function holomorphic and not identically zero near the
point; the hypotheses are carried by the obligations below, not by the type.
TODO: replace with Mathlib's order of vanishing / `analyticOrderAt` once the
exact name is confirmed. -/
axiom ordVanishing : (Complex → Complex) → Complex → Nat

/--
A **continuation datum** for a sequence of Dirichlet coefficients: an entire
function agreeing with the Dirichlet series on the half-plane of convergence
(Chapter 48, Proposition "relative well-definedness of the analytic rank").
-/
structure ContinuationDatum (a : Nat → Complex) where
  f : Complex → Complex
  entire : IsEntire f
  agrees : ∀ s : Complex, (3 : Real) / 2 < s.re → f s = dirichletSum a s

namespace ContinuationDatum

/--
Part (i) of Chapter 48's proposition: any two continuation data are equal as
functions.  The informal proof is one line -- the difference is entire and
vanishes on a non-empty open subset of a connected set, so it vanishes by the
identity theorem -- but the identity theorem, the notion of entire, and the
Dirichlet sum are all placeholders here, so nothing can be discharged.
-/
theorem uniq {a : Nat → Complex} (D D' : ContinuationDatum a) : D.f = D'.f := by
  -- OBLIGATION: obl-cont-datum-unique
  sorry

/--
Part (ii): a continuation datum for the coefficients of an elliptic curve is
not identically zero, so its order of vanishing at `1` is a well-defined
natural number.  The informal proof uses the Hasse bound and multiplicativity
to let `Re(s)` tend to infinity term by term, obtaining the limit `1`.
-/
theorem ne_zero (W : WeierQ) (D : ContinuationDatum (dirichletCoeff W)) :
    D.f ≠ (fun _ => 0) := by
  -- OBLIGATION: obl-cont-datum-ne-zero
  sorry

end ContinuationDatum

/-- The analytic rank, relative to a continuation datum. -/
noncomputable def analyticRank (W : WeierQ) (D : ContinuationDatum (dirichletCoeff W)) :
    Nat :=
  ordVanishing D.f 1

/--
Part (iii): the analytic rank depends only on the curve.  Immediate from the
two obligations above, but "immediate" is a claim about a proof that does not
exist yet, so this too is recorded.
-/
theorem analyticRank_indep (W : WeierQ)
    (D D' : ContinuationDatum (dirichletCoeff W)) :
    analyticRank W D = analyticRank W D' := by
  -- OBLIGATION: obl-analytic-rank-welldef
  sorry

/--
Modularity of elliptic curves over `Q`, in the only form this tree needs: a
continuation datum exists.  KNOWN (Wiles; Taylor--Wiles; Breuil--Conrad--
Diamond--Taylor).  **Absent from Mathlib**, and blocked behind Hecke operators,
newforms, Eichler--Shimura and modularity lifting -- which is the bulk of what
a community formalisation of Fermat's Last Theorem must construct anyway.
Chapter 48 recommends designing a BSD formalisation as a dependent of that
effort rather than a competitor to it.

Recorded as an `axiom`, not a `sorry`: it is a theorem of the literature, and
the point of the declaration is to make its use visible, not to promise a
proof.
-/
axiom modularity (W : WeierQ) : Nonempty (ContinuationDatum (dirichletCoeff W))

/--
Gross--Zagier and Kolyvagin, in the combined form the book uses: in analytic
rank at most one, the rank formula holds and Sha is finite.  KNOWN
(Gross--Zagier 1986; Kolyvagin 1988/1990).  Absent from Mathlib; axiomatised.

Chapter 25 is the book's account of why this is a *barrier* and not a
stepping-stone: the method does not extend to analytic rank two or more, and
Obstruction XIV is exactly that barrier.
-/
axiom grossZagierKolyvagin (W : WeierQ) (D : ContinuationDatum (dirichletCoeff W))
    (h : analyticRank W D ≤ 1) :
    mwRank W = analyticRank W D ∧ ShaIsFinite W

/-! ## 4. Euler systems as an interface

Chapter 48, sketch (5): the structures of Part IV cannot be constructed in Lean
for many years, and the correct methodology is specification-first --
axiomatise the interface as a class, prove the consequences, leave the
construction as an obligation.  If the intended consequences cannot be derived
from the stated axioms, one learns that the axioms are wrong, cheaply, and
years before a construction is attempted.
-/

/-- The type of `r`-legged Euler system data at the prime `l`.  Absent. -/
axiom HESystem : WeierQ → Nat → Nat → Type

/-- The `r`-leg norm relations: one Euler factor per leg, not its `r`-th power,
and integrally.  Obstruction X, which the book calls the most testable of the
hard obstructions. -/
axiom HESNormCompatible : {W : WeierQ} → {l r : Nat} → HESystem W l r → Prop

/-- Non-vanishing of the bottom class. -/
axiom HESNonvanishing : {W : WeierQ} → {l r : Nat} → HESystem W l r → Prop

/--
A higher Euler system, as a class.  Three fields, matching Chapter 48's sketch:
the classes, the norm relation, the non-vanishing.  There is no instance, and
producing one is Obstruction IX together with Obstruction X.
-/
class HigherEulerSystem (W : WeierQ) (l r : Nat) where
  system : HESystem W l r
  normRel : HESNormCompatible system
  nonzero : HESNonvanishing system

/--
The consequence the interface is designed to yield: a rank upper bound.
CONDITIONAL on the existence of an instance and on finiteness of Sha.

The book is careful here (Obstruction XII): a non-zero class gives a rank
*lower* bound easily; the upper bound needs a descent argument bounding Selmer,
and Kolyvagin's derivative machinery has no `r`-dimensional analogue.  This
obligation is therefore harder than its one-line statement suggests.
-/
theorem selmerBound_of_hes (W : WeierQ) (l r : Nat)
    [HigherEulerSystem W l r] [ShaFinite W] : mwRank W ≤ r := by
  -- OBLIGATION: obl-selmer-bound-of-hes
  sorry

/-! ## 5. The audit table, as data

Chapter 48's Warning "audit" asks a programme depending on library contents to
ship a script that re-checks each assumed declaration against a pinned commit
and reports PRESENT, ABSENT or RENAMED.  We cannot run such a script here (no
Lean, no Mathlib), so we ship the *claims* in a form a script could consume,
and nothing more.
-/

/-- Qualitative status of an object needed by the BSD formula, as of the
book's audit and *not* re-verified here.  Deliberately understated. -/
inductive MathlibStatus where
  | formalised
  | partial
  | absent
  deriving DecidableEq, Repr

/-- The audit table of Chapter 48, transcribed.  Unverified. -/
def mathlibAudit : List (String × MathlibStatus) :=
  [ ("Weierstrass model, discriminant, j", MathlibStatus.formalised),
    ("group law and associativity", MathlibStatus.formalised),
    ("E[n] as a group scheme; Weil pairing; Tate module", MathlibStatus.partial),
    ("Weil and canonical heights", MathlibStatus.partial),
    ("Mordell-Weil theorem, rank, regulator", MathlibStatus.absent),
    ("Neron model over a Dedekind base", MathlibStatus.absent),
    ("c_p, Kodaira types, conductor, Omega_E", MathlibStatus.absent),
    ("continuous H^1(Q,-); Poitou-Tate; Selmer; Sha; Cassels-Tate",
      MathlibStatus.absent),
    ("a_p, Euler product, L(E,s) for Re s > 3/2", MathlibStatus.partial),
    ("continuation of L(E,s); ord_{s=1} L(E,s)", MathlibStatus.absent) ]

theorem mathlibAudit_length : mathlibAudit.length = 10 := rfl

end BSD
