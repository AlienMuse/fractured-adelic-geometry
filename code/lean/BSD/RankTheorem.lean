/-
  BSD/RankTheorem.lean

  The payload: the conditional rank formula of Chapter 38
  (Theorem 38.3.1, `thm:ch38-rank-formula`).

  UNCHECKED.  Not compiled; see BSD/Basic.lean and README.md.

  READ THE DOC-COMMENT ON `rank_formula_of_axioms` BEFORE READING THE THEOREM.
  In plain English: it says that the axioms, plus Conjecture G, plus the
  categorified trace formula (plus the further inputs the book lists), imply
  the rank formula.  It says **nothing whatever** about whether the axioms
  hold, whether the conjectures hold, or whether the Birch--Swinnerton-Dyer
  conjecture is true.  A conditional theorem is exactly as strong as its
  hypotheses, and these hypotheses are all open.
-/

import BSD.Conjectures

namespace BSD

/--
**The rank formula, Route 1** (Chapter 38, Theorem 38.3.1, tagged CONDITIONAL
in the book).

    order of vanishing of the FAP zeta function at s = 1  =  the rank.

Every hypothesis is an explicit argument:

* `[FAPAxioms X]`  -- the twelve axioms F1--F12 of Chapter 8, assumed, not
  established; there is no instance anywhere in this tree.
* `hG`   -- Conjecture G, Graded Vanishing (Chapter 20).  This is what supplies
  the identification of the order of vanishing with a dimension.  Five stars.
* `hCTF` -- the categorified trace formula of Chapter 16, which is what turns
  the analytic side into a sum over closed orbits.
* `hA`   -- Conjecture A, the Master Identity (Chapter 37).  Five stars.
* `hL`   -- Conjecture L, existence of the arithmetic flow (Chapter 15).  Five
  stars; Obstruction IV, which subsumes Deninger's programme.
* `hM`   -- Conjecture M, the heat-kernel expansion (Chapter 17), without which
  `det_infty` and hence the left-hand side is not defined.
* `hSha` -- finiteness of Sha, without which the right-hand side is not the
  quantity the book means.  Needed on **both** of the book's routes.

DEVIATION FROM THE SPECIFICATION, DELIBERATE AND FLAGGED.  The specification of this tree gave
the signature with only `[FAPAxioms X]`, `hG` and `hCTF`.  Chapter 38's
statement of Theorem 38.3.1 is conditional in addition on Conjectures A, L, M
and on finiteness of Sha, and its specification says in terms "every hypothesis
listed".  Omitting the four would make this Lean statement *stronger* than the
theorem the book proves, which the honesty rule forbids.  They are therefore
present as extra explicit arguments.  See README.md.

WHAT THIS THEOREM WOULD CERTIFY IF PROVED.  That the implication holds.  Not
that the antecedent holds.  Not that BSD is true.  Chapter 48: "a `Prop` is not
evidence, and a formalised conditional theorem is exactly as strong as its
hypotheses".
-/
theorem rank_formula_of_axioms (X : FAPSpace) [FAPAxioms X]
    (hG : ConjectureG X) (hCTF : CohomologicalTraceFormula X)
    (hA : ConjectureA X) (hL : ConjectureL X) (hM : ConjectureM X)
    (hSha : ShaFiniteFAP X) :
    ordVanishing (zetaFAP X) 1 = mordellWeilRank X := by
  -- OBLIGATION: obl-rank-formula
  sorry

/--
The shape of the argument, recorded as data so that it can be read without
reading the proof that does not exist.

Chapter 38 proceeds in two halves.  On the analytic side, the categorified
trace formula and the regularised determinant give
`ord_{s=1} Z_E(s) = dim` of a `Theta = 1` eigenspace.  On the algebraic side,
Axiom F12 identifies that eigenspace with `H^1_f`, whose dimension is the
algebraic rank *given* finiteness of Sha.  Conjecture G is what licenses the
first identification in rank at least two; Conjecture A is what makes the two
sides comparable at all.

The book adds a warning that this file cannot enforce: the higher rank in Route
1 comes from the flow eigenspace, **not** from a derived Hecke action.
`delta(GL_2 / Q) = 0`, so Venkatesh's mechanism supplies nothing, and
Conjecture G must not be read as an explanation of higher rank.  Obstruction
XIV is precisely that gap.
-/
def rankFormulaInputs : List String :=
  [ "Problem 7.6.1 (the Construction Problem)",
    "Axioms F1-F12",
    "Conjecture A (Master Identity)",
    "Conjecture G (Graded Vanishing)",
    "Conjecture L (existence of the flow)",
    "Conjecture M (heat-kernel expansion)",
    "the categorified trace formula (CTF)",
    "finiteness of Sha" ]

theorem rankFormulaInputs_length : rankFormulaInputs.length = 8 := rfl

/--
The corresponding statement on the classical side, for reference: what the
formula would say about a curve.  A `Prop`, not a theorem, and not proved
anywhere in this tree.
-/
def ClassicalRankFormula (W : WeierQ) (D : ContinuationDatum (dirichletCoeff W)) :
    Prop :=
  mwRank W = analyticRank W D

/--
The one unconditional thing the literature gives, imported as an axiom in
`BSD/Classical.lean`: the classical rank formula in analytic rank at most one.
Recorded here so that the contrast is visible in the same file.  It is *not*
derived from the framework, and the framework does not reprove it.
-/
theorem classicalRankFormula_of_analyticRank_le_one
    (W : WeierQ) (D : ContinuationDatum (dirichletCoeff W))
    (h : analyticRank W D ≤ 1) : ClassicalRankFormula W D :=
  (grossZagierKolyvagin W D h).1

end BSD
