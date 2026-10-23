/-
  BSD/Axioms.lean

  The twelve axioms F1--F12 of Chapter 8, "The Twelve Axioms"
  (labels `ax:F1` ... `ax:F12`).  This file is the centrepiece of the tree:
  the whole of the book is a conditional whose antecedent is this class.

  UNCHECKED.  Not compiled; see BSD/Basic.lean and README.md.

  HOW TO READ THIS FILE.  Each axiom is a *demand*, not a theorem.  Chapter 8
  does not claim that F1--F12 are consistent; Problem 8.8.3 asks whether they
  are, and it is OPEN.  Nothing below asserts that any FAP space satisfies any
  of them.  In particular `FAPAxioms` is a class with no declared instance, and
  producing one is the Construction Problem (Problem 7.6.1), not an exercise.

  ON THE ENCODING.  The specification asked for "twelve fields F1 ... F12, each a
  `Prop`".  That phrase has two readings: a field whose *type* is `Prop` (the
  class carries twelve statements), or a field whose type *is a* `Prop` (the
  class carries twelve proofs).  We take the second, idiomatic reading, because
  only it makes `[FAPAxioms X]` usable as a hypothesis downstream -- which is
  the entire point of Chapter 48's argument that a typeclass is the right idiom
  for machine-visible conditionality.  The twelve statements themselves are the
  named predicates declared immediately below.  The discrepancy is recorded in
  README.md.
-/

import BSD.FAPSpace

namespace BSD

/-! ### The twelve statements

Each predicate is declared as an `axiom`, i.e. as an opaque `Prop`-valued
function of a FAP space.  This is not evasion: the content of each axiom is a
statement about objects (`D_FAP`, the six operations, `det_infty`, the Selmer
complex) that do not exist in Lean and are years from existing.  Declaring the
predicate opaque records *where* the content sits without pretending to have
it.  Chapter 48 calls this specification-first formalisation and argues it is
the highest-value use of a proof assistant in a speculative programme.

TODO: each of these must eventually be replaced by an actual definition.  Until
then, no theorem proved from `FAPAxioms` has any content beyond its shape.
-/

/--
**F1** (Chapter 8, section "Realisation and descent"; `ax:F1`).
The family of realisation functors out of `D_FAP(X)` -- p-adic etale, de Rham,
crystalline/prismatic, Betti at the archimedean vertex -- is jointly
conservative on constructible objects.

This is *not* the trivial vertexwise statement of Chapter 7: it uses a strictly
smaller family of vertices, and its failure is Obstruction VI (independence of
realisation, l-independence of local terms at bad primes).
-/
axiom RealisationConservative : FAPSpace → Prop

/--
**F2** (Chapter 8, section "Realisation and descent"; `ax:F2`).
`D_FAP` satisfies hyperdescent for the FVA topology `tau_FVA`, and adelic
excision holds: the restricted-product boundedness clause of the topology is
compatible with the descent condition.

Obstruction I: no known site simultaneously supports prismatic, analytic and
archimedean covers with that boundedness clause.  The *Restricted Descent
Lemma* named in Chapter 9 is the target here; it is named, not proved.
-/
axiom FVAHyperdescent : FAPSpace → Prop

/--
**F3** (Chapter 8, section "Local structures"; `ax:F3`).
Analytic spectral structure: the vertexwise coefficient categories are stable,
presentable and symmetric monoidal, with the condensed analytic-ring
enhancement of Chapter 5, and the limit defining `D_FAP` is taken in that
2-category.

This absorbs axiom C1 of the earlier working formulation (see the book, Chapter 8, Table 8.1); C1--C12 are
never printed as a second axiom list.
-/
axiom AnalyticSpectralStructure : FAPSpace → Prop

/--
**F4** (Chapter 8, section "Local structures"; `ax:F4`).
Absolute cyclotomic descent: the operations `psi^n` form a coherent action of
the multiplicative monoid of positive integers, with `psi^m psi^n = psi^{mn}`,
restricting to the prismatic Frobenius `phi_p` p-typically, and endowing the
coefficient theory with a Lambda-structure.

Chapter 7 is emphatic that the `psi^n` are *not* morphisms of `I_ar`: making
them so would force every diagram to be psi-equivariant, a strictly stronger
and different demand.  They are a separate clause of the definition of a FAP
space, and F4 is the demand that the clause can be met coherently.  Whether the
two impositions (Nygaard filtration and Lambda-structure) are coherent on the
whole diagram is not known.
-/
axiom CyclotomicDescent : FAPSpace → Prop

/--
**F5** (Chapter 8, section "Local structures"; `ax:F5`).
Prismatic gauge completeness: the p-typical part of `D_FAP` recovers the theory
of F-gauges on the prismatisation, for every `p` simultaneously.

Obstruction II: F-gauges are defined one prime at a time, and gluing them over
`Spec Z` requires a big-Witt or absolute prism envelope that has not been
constructed.  Chapter 6 states F5's requirement precisely and does not prove it.
-/
axiom PrismaticGaugeCompleteness : FAPSpace → Prop

/--
**F6** (Chapter 8, section "Formal calculus"; `ax:F6`).
The six operations exist on `D_FAP` with the standard adjunctions, base change
and the projection formula, compatibly with the fracture diagram.

Absorbs the earlier formulation's C2 and C3.  Chapter 9 derives the formal consequences; every
one of them is conditional on F6 and must be read as such.
-/
axiom SixOperations : FAPSpace → Prop

/--
**F7** (Chapter 8, section "Formal calculus"; `ax:F7`).
Constructibility, duality, and integral lattices: a well-behaved constructible
subcategory relative to `I_ar`, Verdier duality with a dualising object
(including at the archimedean vertex), and a determinant functor valued in
integral lattices.

Absorbs the earlier formulation's C8.  The integral-lattice clause is what makes the leading
coefficient, not merely the order of vanishing, expressible; it is also what
Conjecture J is about.
-/
axiom ConstructibilityDuality : FAPSpace → Prop

/--
**F8** (Chapter 8, section "Dynamics"; `ax:F8`).
The arithmetic flow: a continuous action `Phi^t` of the non-negative reals on
rationalised periodic coefficients, whose primitive closed orbits are the
primes with lengths `log p`, whose value at `t = log p` is geometric Frobenius
at `p`, with infinitesimal generator `Theta` satisfying the weight adjunction
`Theta^vee = w + 1 - Theta` (so for `h^1(E)`, where `w = 1`, `Theta^vee =
2 - Theta`).

Absorbs the earlier formulation's C4 and C5.  Its existence is Conjecture L; the obstruction is
Obstruction IV, which **subsumes Deninger's programme in full**.  No
`R_{>=0}`-action on any arithmetic cohomology over `Spec Z` with closed orbits
of length `log p` has ever been constructed.  Note: a monoid action of the
non-negative reals, not a group action.
-/
axiom ArithmeticFlow : FAPSpace → Prop

/--
**F9** (Chapter 8, section "Traces and localisation"; `ax:F9`).
Nuclearity and the regularised trace: the relevant objects are nuclear and
flow-dualisable, the trace of `Phi^t` is a distribution with a polyhomogeneous
short-time expansion, and the regularised determinant `det_infty` is therefore
defined.

Absorbs the earlier formulation's C6 and C11.  Chapter 13 states F9 in distributional form and
marks it OPEN; the earlier formulation itself flags C6 as possibly false as stated, and the book
keeps that concession rather than hiding it.  Obstruction V; Conjecture M.
-/
axiom NuclearTrace : FAPSpace → Prop

/--
**F10** (Chapter 8, section "Traces and localisation"; `ax:F10`).
Lefschetz--Verdier localisation: the categorical trace localises to a sum of
local terms supported on the fixed loci, in all FAP settings simultaneously.

Chapter 13: F10 asks for this package simultaneously in all FAP settings, which
is more than is known in any one of them.  Obstruction VI touches this via
l-independence of the local terms at bad primes.
-/
axiom LefschetzVerdierLocalisation : FAPSpace → Prop

/--
**F11** (Chapter 8, section "Orientation and arithmetic"; `ax:F11`).
Riemann--Roch orientation: characteristic classes `ch_FAP` and `Td_FAP` exist,
with an orientation of the archimedean vertex fixing the Gamma-factor and the
arithmetic degree normalisation.

Absorbs the earlier formulation's C7.  Obstruction III: there is no prism at infinity, and the
"F-gauge at infinity" is a real Hodge structure with an unexplained
Gamma-factor.  Chapter 21 records that F11 is what decides whether the
archimedean bookkeeping is more than bookkeeping.
-/
axiom RiemannRochOrientation : FAPSpace → Prop

/--
**F12** (Chapter 8, section "Orientation and arithmetic"; `ax:F12`;
stated in full as `axiom:ch20-F12`).
The Selmer fixed-point principle: the fibre of `Theta - 1` on
`RGamma_FAP(X_E, M_E)` is, after p-completion, the Nekovar Selmer complex
`\widetilde{RGamma}_f(Q, T_p E)`, and the induced `Theta`-Bockstein
`beta_Theta` is the Neron--Tate height pairing.

**This is where the arithmetic content of BSD is hidden, and the book says so
rather than presenting F12 as innocuous.**  Obstruction VII subsumes two known
major open problems: **finiteness of Sha, and the ETNC**.  F12 is also the axiom
with no counterpart in the function-field model: Chapter 8 records that in the
`F_q` case F1--F11 hold by Grothendieck's theory and F12 does not apply.
-/
axiom SelmerFixedPoint : FAPSpace → Prop

/-! ### The class -/

/--
The twelve axioms, as a typeclass on a FAP space.

Chapter 48 argues that a typeclass is the correct idiom precisely because it
makes conditionality *machine-visible*: a linter can list every theorem whose
transitive dependencies include this class, and that mechanism is what keeps
the proof-obligation ledger of Chapter 51 honest.

There is deliberately **no instance**.  Constructing one is Problem 7.6.1, and
Chapter 7 warns explicitly that nothing beyond two degenerate examples is known
to satisfy the definition together with these axioms.  `FAPAxioms X` should be
read as "X has been *assumed* to satisfy F1--F12", never as "X satisfies
F1--F12".
-/
class FAPAxioms (X : FAPSpace) : Prop where
  /-- F1: joint conservativity of the realisation family.  Obstruction VI. -/
  F1 : RealisationConservative X
  /-- F2: `tau_FVA`-hyperdescent and adelic excision.  Obstruction I. -/
  F2 : FVAHyperdescent X
  /-- F3: analytic spectral structure on the coefficient categories. -/
  F3 : AnalyticSpectralStructure X
  /-- F4: absolute cyclotomic descent; the `psi^n` and the Lambda-structure. -/
  F4 : CyclotomicDescent X
  /-- F5: prismatic gauge completeness at every `p` at once.  Obstruction II. -/
  F5 : PrismaticGaugeCompleteness X
  /-- F6: the six operations with base change and projection formula. -/
  F6 : SixOperations X
  /-- F7: constructibility, Verdier duality, integral lattices. -/
  F7 : ConstructibilityDuality X
  /-- F8: the arithmetic flow, closed orbits of length `log p`, weight
  adjunction `Theta^vee = w + 1 - Theta`.  Obstruction IV; Conjecture L. -/
  F8 : ArithmeticFlow X
  /-- F9: nuclearity, the regularised trace, `det_infty`.  Obstruction V. -/
  F9 : NuclearTrace X
  /-- F10: Lefschetz--Verdier localisation of the categorical trace. -/
  F10 : LefschetzVerdierLocalisation X
  /-- F11: Riemann--Roch orientation, including at the archimedean vertex.
  Obstruction III. -/
  F11 : RiemannRochOrientation X
  /-- F12: the Selmer fixed-point principle.  Obstruction VII; subsumes
  finiteness of Sha and the ETNC. -/
  F12 : SelmerFixedPoint X

/--
Problem 8.8.3, OPEN: are F1--F12 consistent over `Z`?  Equivalently, is there a
FAP space satisfying all twelve?

This is stated as a `def ... : Prop`, deliberately **not** as a
`theorem ... := sorry`.  A `sorry` would assert that the book expects it to be
provable, and the book expects no such thing: consistency is not claimed, and
Chapter 2 lists an inconsistency proof for F1--F12 as one of the outcomes the
programme would count as a result.
-/
def FAPAxiomsConsistency : Prop := ∃ X : FAPSpace, FAPAxioms X

/--
The book's own worked check: in the function-field case, F1--F11 hold by
Grothendieck's theory (Proposition 8.8.2, KNOWN) and F12 does not apply.  We
record the *shape* of that statement, not the statement: there is no
function-field model in this tree to apply it to.  It is a `Prop`, not a
theorem, for the same reason as above.
-/
def FunctionFieldModelSatisfiesF1toF11 (X : FAPSpace) : Prop :=
  RealisationConservative X ∧ FVAHyperdescent X ∧ AnalyticSpectralStructure X ∧
  CyclotomicDescent X ∧ PrismaticGaugeCompleteness X ∧ SixOperations X ∧
  ConstructibilityDuality X ∧ ArithmeticFlow X ∧ NuclearTrace X ∧
  LefschetzVerdierLocalisation X ∧ RiemannRochOrientation X

/-- The names of the twelve axioms, in order, for cross-checking against the
book's Chapter 8 and against `BSD/Ledger.lean`. -/
def axiomNames : List String :=
  ["F1", "F2", "F3", "F4", "F5", "F6", "F7", "F8", "F9", "F10", "F11", "F12"]

theorem axiomNames_length : axiomNames.length = 12 := rfl

end BSD
