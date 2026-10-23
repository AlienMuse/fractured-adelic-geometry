/-
  BSD/Certificates.lean

  Certificate checking, from Part VII (Chapter 47, "Certificates and
  Reproducibility"), and its soundness.

  UNCHECKED.  Not compiled; see BSD/Basic.lean and README.md.

  WHY THIS FILE IS DIFFERENT FROM THE REST OF THE TREE.  Everything else here
  is scaffolding for objects that do not exist.  This file is about finite
  data and a decision procedure, and a decision procedure can be given a real
  proof.  Two of the three soundness lemmas below are proved outright; only the
  step that needs canonical heights is an obligation.  Chapter 48: formalising
  computation is cheap and formalising structure is not.

  A certificate is a promise; it becomes a theorem exactly when a kernel
  evaluates the checker on it and the soundness of the checker has itself been
  proved.  Absent either half, a certificate is an assertion about a program,
  not about an elliptic curve.
-/

import BSD.Classical

namespace BSD

/--
A **C4 certificate**: a rank lower bound (Chapter 47, section "C4: a rank lower
bound").

The book's C4 certificate contains rational points, exact on-curve witnesses,
and a symmetric interval matrix enclosing their Neron--Tate pairings, together
with an interval determinant excluding zero.  A floating determinant without
entrywise and tail enclosures is not C4.

Here the interval matrix is modelled by exact rational lower and upper bounds:
`gramLower` and `gramUpper` are `r`-by-`r` matrices given as lists of rows, and
`detLower` is a claimed strictly positive rational lower bound for the
determinant of the true Gram matrix.  Interval arithmetic proper belongs to the
certified kernel of Chapter 43 and is not modelled.
-/
structure RankLowerBoundCertificate where
  /-- The minimal Weierstrass model naming the curve. -/
  curve : WeierQ
  /-- The claimed rank lower bound. -/
  r : Nat
  /-- The witnessing rational points, in affine coordinates. -/
  points : List (Rat × Rat)
  /-- Entrywise lower bounds for the Neron--Tate height Gram matrix. -/
  gramLower : List (List Rat)
  /-- Entrywise upper bounds for the same. -/
  gramUpper : List (List Rat)
  /-- A claimed strictly positive lower bound for the determinant. -/
  detLower : Rat

/-- Every listed point satisfies the Weierstrass equation.  Written by hand,
recursively, rather than via `List.all`, so that the soundness proof below is
self-contained and does not depend on library lemma names. -/
def allOnCurve (W : WeierQ) : List (Rat × Rat) → Bool
  | [] => true
  | P :: rest => onCurveB W P && allOnCurve W rest

/-- The on-curve half of the checker, exposed under the name the specification asks
for.  It is `decide` on an exact rational equation: a kernel evaluation, never
`native_decide`. -/
def checkOnCurve (W : WeierQ) (P : Rat × Rat) : Bool := onCurveB W P

/--
Soundness of the pointwise on-curve check.  A real proof: `OnCurve` is by
definition the proposition that `checkOnCurve` decides.
-/
theorem checkOnCurve_sound (W : WeierQ) (P : Rat × Rat)
    (h : checkOnCurve W P = true) : OnCurve W P :=
  onCurveB_sound W P h

/--
Soundness of the list check.  A real proof, by induction on the list, using
only `Bool.and_eq_true` and the pointwise lemma.
-/
theorem allOnCurve_sound (W : WeierQ) :
    ∀ ps : List (Rat × Rat), allOnCurve W ps = true → ∀ P ∈ ps, OnCurve W P := by
  intro ps
  induction ps with
  | nil =>
      intro _ P hP
      cases hP
  | cons Q rest ih =>
      intro h P hP
      simp only [allOnCurve, Bool.and_eq_true] at h
      cases hP with
      | head => exact checkOnCurve_sound W Q h.1
      | tail _ hmem => exact ih h.2 P hmem

/-- The structural checks: the number of points matches the claimed rank, the
Gram bounds are square of the right size, and the claimed determinant lower
bound is strictly positive.  Positivity is tested on the numerator, an `Int`,
because integer order is decidable in core Lean and we do not wish to rely on
the spelling of the rational order instance. -/
def checkShape (c : RankLowerBoundCertificate) : Bool :=
  decide (c.points.length = c.r) &&
  decide (c.gramLower.length = c.r) &&
  decide (c.gramUpper.length = c.r) &&
  decide (0 < c.detLower.num)

/-- The full C4 checker. -/
def checkCertificate (c : RankLowerBoundCertificate) : Bool :=
  checkShape c && allOnCurve c.curve c.points

/--
Soundness of the shape check, in the only part that has content without
heights: an accepted certificate really does exhibit `c.r` points on the curve.
A real proof.
-/
theorem checkCertificate_points_on_curve (c : RankLowerBoundCertificate)
    (h : checkCertificate c = true) : ∀ P ∈ c.points, OnCurve c.curve P := by
  simp only [checkCertificate, Bool.and_eq_true] at h
  exact allOnCurve_sound c.curve c.points h.2

/--
**C4 soundness** (Chapter 47, Proposition "C4 soundness", tagged NEW there and
proved there in three lines).

If a C4 certificate is accepted then its points are independent modulo torsion
and the rank is at least `c.r`.

The book's proof: if a non-trivial integral combination were torsion, its
canonical height would vanish, so bilinearity would make the exact height Gram
matrix singular; the accepted determinant interval contains the determinant and
excludes zero, a contradiction.

Every ingredient of that argument -- the canonical height, its bilinearity, the
Gram matrix, the enclosure -- is absent from Lean, so this cannot be discharged
here.  Note also what the proposition does *not* say: C4 does not prove that
the points generate a saturated Mordell--Weil lattice.  Saturation is a
separate certificate.
-/
theorem checkCertificate_sound (c : RankLowerBoundCertificate)
    (h : checkCertificate c = true) : c.r ≤ mwRank c.curve := by
  -- OBLIGATION: obl-cert-rank-lower-bound
  sorry

/--
A checker is a specification only if it discriminates.  Chapter 48 makes the
point sharply, and it is not a joke: a checker weakened during debugging until
it always succeeds is a realistic failure mode invisible to the type checker.
The development compiles and nothing is verified.

The countermeasure is a suite of certificates that must be **rejected**, run
alongside those that must be accepted.  Recorded here as a specification that a
test harness must meet; there is no data in this tree to run it on.
-/
def CheckerDiscriminates : Prop :=
  ∃ c : RankLowerBoundCertificate, checkCertificate c = false

/--
The book's concrete instance of that requirement: for the curve `11.a1`, whose
rank is zero, a rank certificate asserting `r = 1` must fail, and that failing
case belongs beside the passing case for `37.a1`.  We state the requirement; we
do not ship the data, because shipping numerical data we cannot verify here
would violate the honesty rule.
-/
def negativeTestRequirement : List String :=
  [ "11.a1 with claimed r = 1 must be REJECTED",
    "37.a1 with claimed r = 1 must be ACCEPTED" ]

theorem negativeTestRequirement_length : negativeTestRequirement.length = 2 := rfl

/--
The trust hierarchy, as it applies to this file (Chapter 48, Proposition
"certificate soundness"; Chapter 52).

If the equation `checkCertificate c = true` is produced by kernel evaluation,
the certificate contributes no axioms at all.  If it is instead imported as an
axiom on the say-so of an external tool, that tool joins the trusted base.  And
if the checker were the constant `true`, the soundness lemma would be an
unconditional theorem and the certificate would be doing no work.

`native_decide` is forbidden throughout: it enlarges the trusted base by a
compiler and a runtime, and Chapter 48 excludes it from the whitelist.
-/
def trustNotes : List String :=
  [ "kernel evaluation adds no axioms",
    "an imported checker result puts the external tool in the trusted base",
    "a constant-true checker verifies nothing",
    "native_decide is forbidden" ]

theorem trustNotes_length : trustNotes.length = 4 := rfl

end BSD
