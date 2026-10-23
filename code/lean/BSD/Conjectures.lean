/-
  BSD/Conjectures.lean

  The twelve conjectures A--M of the book (there is no Conjecture I; the letter
  is skipped to avoid collision with Obstruction I).  Canonical register:
  Chapter 3 and Table 41.3 of the book.

  UNCHECKED.  Not compiled; see BSD/Basic.lean and README.md.

  EVERY DECLARATION IN THIS FILE IS A `def ... : Prop`.  None is a theorem and
  none is proved.  Ten of the twelve are rated four or five stars in the book's
  register -- five stars meaning "subsumes or exceeds a known major open
  problem" -- and only Conjecture H is described there as genuinely tractable.
  That ratio is, in the book's own words, the single most important number in
  the register.
-/

import BSD.Axioms
import BSD.Classical

namespace BSD

/-! ### Framework invariants used by the statements

All opaque.  They stand for objects defined in Chapters 15--23 and 37 of the
book, none of which exists in Lean.
-/

/-- The FAP fundamental line `Delta(X_E)`, Chapter 37: an invertible object of
the relevant symmetric monoidal category.  Its very existence is conditional --
Chapter 41 (the circularity audit) records that it may not exist without finiteness
of Sha. -/
axiom FundamentalLine : FAPSpace → Type

/-- The analytic trivialisation `lambda_an`, Chapter 37, built from
`det_infty` and the categorified trace formula. -/
axiom lambdaAn : (X : FAPSpace) → FundamentalLine X

/-- The algebraic trivialisation `lambda_alg`, Chapter 37, built from the
critical complex, the height pairing and the local terms of Chapter 22.
(The book renames SOL-A's "arithmetic trivialisation" to *algebraic* to avoid
collision with the arithmetic route; we follow.) -/
axiom lambdaAlg : (X : FAPSpace) → FundamentalLine X

/-- The FAP zeta function `Z_E(s)`, Chapter 17, normalised so as to equal the
completed `Lambda(E, s)` (Seam S-2). -/
axiom zetaFAP : FAPSpace → (Complex → Complex)

/-- The algebraic rank attached to the arithmetic spectrum: the rank of the
Mordell--Weil group of the curve the spectrum is built from.  Distinct from
`mwRank` of `BSD/Classical.lean`, which takes a Weierstrass model. -/
axiom mordellWeilRank : FAPSpace → Nat

/-- The dimension of the hidden flow space `h_E = H^1_f(Q, V_p E)`,
Chapter 20. -/
axiom hiddenFlowDim : FAPSpace → Nat

/-- The categorified trace formula (CTF) of Chapter 16: the categorical trace
of the flow is the sum over closed orbits.  A *hypothesis*, notwithstanding
that the book calls it a theorem in the function-field model. -/
axiom CohomologicalTraceFormula : FAPSpace → Prop

/-- Finiteness of Sha for the curve underlying a FAP space, transported to the
framework side.  A standing imported conjecture, never renumbered. -/
axiom ShaFiniteFAP : FAPSpace → Prop

/-- The flow Euler characteristic `chi^Theta_FAP(E)` of Chapter 37, whose value
is the third clause of Conjecture A. -/
axiom flowEulerChar : FAPSpace → Type

/-- Auxiliary opaque predicates for the statements below.  Each names a clause
the book states in prose and that has no Lean-expressible content yet. -/
axiom IntegralTrivialisationsAgree : FAPSpace → Prop
axiom HigherReciprocityHolds : FAPSpace → Nat → Prop
axiom HigherAGZHolds : FAPSpace → Nat → Prop
axiom LegFiltrationEqualsBockstein : FAPSpace → Prop
axiom OrbitPeriodNormalisation : FAPSpace → Prop
axiom PlecticMainConjectureHolds : FAPSpace → Nat → Prop
axiom FreeExteriorAction : FAPSpace → Prop
axiom TopGradedPieceIsRegulator : FAPSpace → Prop
axiom LocalTrivialisationsAgree : FAPSpace → Nat → Prop
axiom IntegralOrientationExists : FAPSpace → Prop
axiom CriticalComplexNuclear : FAPSpace → Prop
axiom FlowExistsUniquelyWithFrobenius : FAPSpace → Prop
axiom HeatKernelPolyhomogeneous : FAPSpace → Prop
axiom ZetaContinuesWithFunctionalEquation : FAPSpace → Prop

/-! ### The twelve conjectures -/

/--
**Conjecture A -- the Master Identity.**
Chapter 37, `conj:master-identity`.  Difficulty: five stars.

Statement (register): `z^{-r} lambda_an |_{z=0} = lambda_alg` as *integral*
trivialisations of `Delta(X_E)`.  Equivalently: the fundamental line has two
trivialisations, one analytic and one algebraic, and they agree.

Implies: the rank formula (Chapter 38) and the leading coefficient
(Chapter 39).  Depends on: Problem 7.6.1, F1--F12, and Conjectures L, M, K.
Obstruction VIII, which **subsumes the ETNC for `h^1(E)(1)`**.

STATUS: OPEN.  Nothing in this tree proves it, and Chapter 37 is explicit that
Conjecture A is not equivalent to BSD: it implies BSD given the Construction
Problem and finiteness of Sha.
-/
def ConjectureA (X : FAPSpace) : Prop :=
  lambdaAn X = lambdaAlg X ∧ IntegralTrivialisationsAgree X

/--
**Conjecture B -- the Higher Reciprocity Law.**
Chapter 30, `conj:higher-reciprocity`.  Difficulty: five stars.

The `r`-legged determinant class `kappa^{(r)}` and the plectic `p`-adic
`L`-function are related by an `r`-variable reciprocity law with archimedean
period `L^{(r)}(E,1) / (r! Omega_E)`.

Implies the rank lower bound of Theorem 30.4.1, and with Conjecture F the
`p`-part.  Depends on the existence of the stack of `r`-legged arithmetic
shtukas (Chapter 29; Obstruction IX) and, for the archimedean half, on
Conjecture C.

STATUS: OPEN.
-/
def ConjectureB (X : FAPSpace) (r : Nat) : Prop := HigherReciprocityHolds X r

/--
**Conjecture C -- Higher Arithmetic Gross--Zagier.**
Chapter 35, `conj:higher-agz`.  Difficulty: five stars.

An `r`-legged cycle `Z^{(r)}_E` over `Q` has derived self-intersection equal to
`L^{(r)}(E,1) / (r! Omega_E)`.

Depends on modularity and on a number-field analogue of Yun--Zhang 2017.
Obstruction XI **subsumes a number-field Yun--Zhang**: over `Q` there is no
curve, no Hitchin base and no properness.

STATUS: OPEN.
-/
def ConjectureC (X : FAPSpace) (r : Nat) : Prop := HigherAGZHolds X r

/--
**Conjecture D -- Spectral--Shtuka Compatibility.**
Chapter 37, section 37.6, `conj:spectral-shtuka`.  Difficulty: five stars.

The leg filtration on `RGamma_FAP(X_E, M_E)` equals the `Theta`-Bockstein
filtration on the critical complex `C_E`; hence `kappa^{(r)}` is the `r`-th
divided power of `beta_Theta`.

This is the conjecture that glues the book's two routes: it is what makes
"Conjecture A implies the `p`-parts of Conjecture B" and conversely.  It is
also what would decide between the two candidate mechanisms for rank at least
two listed under Obstruction XIV.

STATUS: OPEN.
-/
def ConjectureD (X : FAPSpace) : Prop := LegFiltrationEqualsBockstein X

/--
**Conjecture E -- Orbit--Period Normalisation.**
Chapter 35 section 35.6 and Chapter 17 section 17.5, `conj:orbit-period`.
Difficulty: four stars.

The archimedean regularisation constant of the regularised-determinant axioms
equals the period normalisation of Conjecture C.  It pins the factors of
`2 pi` and the Gamma-factor conventions, and it is what lets Conjecture C feed
the archimedean half of Conjecture B.

STATUS: OPEN.
-/
def ConjectureE (X : FAPSpace) : Prop := OrbitPeriodNormalisation X

/--
**Conjecture F -- the Plectic Main Conjecture.**
Chapter 30, section 30.6, `conj:plectic-mc`.  Difficulty: five stars.

The characteristic ideal over the multivariable plectic algebra of `H^2` of the
plectic Selmer complex is generated by the plectic `p`-adic `L`-function.

With Conjecture B this gives the `p`-part of the leading coefficient.  Depends
on the Chapter 29 axioms, on Kato 2004 and on Skinner--Urban 2014 (both KNOWN,
both imported, neither reproved here).

STATUS: OPEN.
-/
def ConjectureF (X : FAPSpace) (r : Nat) : Prop := PlecticMainConjectureHolds X r

/--
**Conjecture G -- Graded Vanishing.**
Chapter 20, section 20.6, `conj:graded-vanishing`.  Difficulty: five stars.

The critical complex `C_E` carries a free graded action of the exterior algebra
on the hidden flow space `h_E`, with `ord_{s=1} L = dim h_E` and top graded
piece the regulator.

This is the only candidate *mechanism* inside Route 1 for rank at least two,
and the book forbids presenting it as an explanation: Obstruction XIV records
that `delta(GL_2 / Q) = 0`, so the derived Hecke algebra is trivial and cannot
supply the `r` independent directions.  Lemma K2 of Chapter 20 is stated to be
**false** without the flowed enhancement, and that caveat must not be papered
over.

STATUS: OPEN.
-/
def ConjectureG (X : FAPSpace) : Prop :=
  FreeExteriorAction X ∧
  ordVanishing (zetaFAP X) 1 = hiddenFlowDim X ∧
  TopGradedPieceIsRegulator X

/--
**Conjecture H -- the Integral Hasse Principle.**
Chapter 39, section 39.4, `conj:integral-hasse`.  Difficulty: three stars.

If `lambda_an` and `lambda_alg` agree locally at every prime and at infinity,
then they agree globally and integrally.

The register describes H as the only one of the twelve that is genuinely
tractable.  It depends on finiteness of Sha and on Conjecture K.

STATUS: OPEN.
-/
def ConjectureH (X : FAPSpace) : Prop :=
  (∀ p : Nat, LocalTrivialisationsAgree X p) → IntegralTrivialisationsAgree X

/--
**Conjecture J -- Integral Orientation.**
Chapter 39, section 39.5, `conj:integral-orientation`.  Difficulty: four stars.
(The letter I is skipped throughout the book.)

A single integral lattice orientation of `Delta(X_E)` realises correctly at
every prime, including at `p = 2, 3` and at additive primes.

With Conjecture H this upgrades prime-by-prime results to BSD.  Obstruction
XIII (wild integral control at 2 and 3, additive reduction, supersingular
signs) is what blocks it.

STATUS: OPEN.
-/
def ConjectureJ (X : FAPSpace) : Prop := IntegralOrientationExists X

/--
**Conjecture K -- Nuclearity if and only if finiteness of Sha.**
Chapter 23, section 23.5, `conj:nuclear-sha`.  Difficulty: five stars.

The critical complex is nuclear (trace-class) in the flowed coefficient
category **if and only if** Sha is finite.

This reformulates a known major open problem as a functional-analytic
finiteness statement.  Reformulating is not solving, and the book says so.

STATUS: OPEN.
-/
def ConjectureK (X : FAPSpace) : Prop :=
  CriticalComplexNuclear X ↔ ShaFiniteFAP X

/--
**Conjecture L -- existence of the arithmetic flow.**
Chapter 15, section 15.6, `conj:lambda-flow`.  Difficulty: five stars.

`Phi^t` exists, is unique, restricts to Frobenius at `t` in `log p` times the
non-negative integers, and has Deninger's `Theta` at the archimedean place.

Obstruction IV, which **subsumes Deninger's programme in full**: no action of
the non-negative reals on any arithmetic cohomology over `Spec Z` with closed
orbits of length `log p` has ever been constructed.  Note the monoid, not the
group.

STATUS: OPEN.
-/
def ConjectureL (X : FAPSpace) : Prop := FlowExistsUniquelyWithFrobenius X

/--
**Conjecture M -- the heat-kernel expansion.**
Chapter 17, section 17.4, `conj:heat-kernel`.  Difficulty: four stars.

The trace of `Phi^t` on FAP cohomology is polyhomogeneous as `t` tends to zero
from above, so that `det_infty` is defined and `Z_E(s)` continues
meromorphically with the expected functional equation.

This is the analytic-continuation half of Conjecture A, and Obstruction V.
The book preserves the earlier formulation's own concession that the underlying nuclearity axiom
may be false as stated.

STATUS: OPEN.
-/
def ConjectureM (X : FAPSpace) : Prop :=
  HeatKernelPolyhomogeneous X ∧ ZetaContinuesWithFunctionalEquation X

/-! ### The register, as data -/

/-- The labels of the twelve conjectures.  **There is no `I`.** -/
inductive ConjectureLabel where
  | A | B | C | D | E | F | G | H | J | K | L | M
  deriving DecidableEq, Repr

namespace ConjectureLabel

/-- The book's name for each conjecture (Chapter 3, Table 41.3). -/
def name : ConjectureLabel → String
  | A => "Master Identity"
  | B => "Higher Reciprocity Law"
  | C => "Higher Arithmetic Gross-Zagier"
  | D => "Spectral-Shtuka Compatibility"
  | E => "Orbit-Period Normalisation"
  | F => "Plectic Main Conjecture"
  | G => "Graded Vanishing"
  | H => "Integral Hasse Principle"
  | J => "Integral Orientation"
  | K => "Nuclearity iff finiteness of Sha"
  | L => "Existence of the arithmetic flow"
  | M => "Heat-kernel expansion"

/-- The book's primary LaTeX label for each conjecture. -/
def latexLabel : ConjectureLabel → String
  | A => "conj:master-identity"
  | B => "conj:higher-reciprocity"
  | C => "conj:higher-agz"
  | D => "conj:spectral-shtuka"
  | E => "conj:orbit-period"
  | F => "conj:plectic-mc"
  | G => "conj:graded-vanishing"
  | H => "conj:integral-hasse"
  | J => "conj:integral-orientation"
  | K => "conj:nuclear-sha"
  | L => "conj:lambda-flow"
  | M => "conj:heat-kernel"

/-- The chapter in which each conjecture is stated. -/
def chapter : ConjectureLabel → Nat
  | A => 37
  | B => 30
  | C => 35
  | D => 37
  | E => 35
  | F => 30
  | G => 20
  | H => 39
  | J => 39
  | K => 23
  | L => 15
  | M => 17

/-- Difficulty on the book's one-to-five star scale.  Five means "subsumes or
exceeds a known major open problem". -/
def difficulty : ConjectureLabel → Nat
  | A => 5
  | B => 5
  | C => 5
  | D => 5
  | E => 4
  | F => 5
  | G => 5
  | H => 3
  | J => 4
  | K => 5
  | L => 5
  | M => 4

/-- Every conjecture is OPEN.  There is no other value in this tree. -/
def tag : ConjectureLabel → RigourTag := fun _ => RigourTag.open_

end ConjectureLabel

/-- The register, in the book's order. -/
def conjectureRegister : List ConjectureLabel :=
  [ConjectureLabel.A, ConjectureLabel.B, ConjectureLabel.C, ConjectureLabel.D,
   ConjectureLabel.E, ConjectureLabel.F, ConjectureLabel.G, ConjectureLabel.H,
   ConjectureLabel.J, ConjectureLabel.K, ConjectureLabel.L, ConjectureLabel.M]

theorem conjectureRegister_length : conjectureRegister.length = 12 := rfl

/--
How many of the twelve are rated four or five stars.  Stated as a computation
so that it can be checked by evaluation rather than believed.

DISCREPANCY, recorded rather than smoothed over.  The prose of an earlier draft of the register said "Ten of twelve conjectures are four or five
stars.  Only H is genuinely tractable", and Chapter 48's companions repeat the
figure.  The register's own table, transcribed verbatim in `difficulty` above,
gives H three stars and every other conjecture four or five -- that is
**eleven**, not ten.  We follow the table, because the table is the data and
the sentence is a summary of it, and we flag the mismatch in README.md.
-/
def hardCount : Nat :=
  (conjectureRegister.filter (fun c => decide (4 ≤ ConjectureLabel.difficulty c))).length

theorem hardCount_eq : hardCount = 11 := rfl

end BSD
