# `code/lean` — the BSD formalisation skeleton

**Author:** Vincent Liu · **Organisation:** WiseMotif.ai

This tree accompanies **Part VIII** of the monograph *Fractured Adelic Geometry: A Foundational Framework for the Birch and Swinnerton-Dyer Conjecture* (WiseMotif Monograph of Mathematical Intelligence, Series 04) and is the object
described in **Chapter 48, "Formalisation in Lean"**.

---

## 1. Read this first

**THE TREE HAS NOT BEEN COMPILED.**

Lean 4, `elan`, `lake` and Mathlib are **not installed** in the environment in
which this tree was written, and installing them was explicitly out of scope (a
Mathlib build is many gigabytes and many hours). Consequently:

* every `.lean` file here is **unchecked source**;
* no claim is made that any declaration type-checks;
* the toolchain pin in `lean-toolchain` and the Mathlib revision in
  `lakefile.toml` are **nominal and unverified** — they are plausible, not
  confirmed;
* the only automated check the tree has received is the *lexical* one in
  `tools/check_tree.py`, whose output is reproduced in §6 below and which
  cannot tell you anything about type-correctness.

**Every framework-level result in this tree is a `sorry`.** There are ten of
them; they are enumerated in §4 and, as structured Lean data, in
`BSD/Ledger.lean`.

Nothing in this tree proves the Birch–Swinnerton-Dyer conjecture. Nothing in it
is evidence for or against it. BSD is open.

---

## 2. What the tree is

A skeleton at levels **F0–F3** of Chapter 48's ladder:

| Level | Meaning | Status here |
|---|---|---|
| `F0` | statability of the *classical* conjecture | partial, and only *relative to a continuation datum* (`BSD/Classical.lean`) |
| `F1` | statability of the *framework*: FAP spaces, F1–F12, `X_E`, `Δ(X_E)`, `λ_an`, `λ_alg` | attempted; the objects are opaque `axiom`s |
| `F2` | elementary consequences | barely begun — a handful of genuinely proved lemmas |
| `F3` | conditional theorems ("Conjecture A implies the rank formula") | exactly one, and it is a `sorry` |
| `F4` | the conjectures themselves | not a formalisation target; it is the mathematics |

The design follows Chapter 48's **specification-first** methodology (its
sketch (5)): axiomatise the interface as a class, state the consequences, leave
the construction as an obligation. Chapter 48 argues that this is the
highest-value use of a proof assistant in a speculative programme, because if
the intended consequences cannot be derived from the stated axioms one learns
that the axioms are wrong — cheaply, and years before a construction is
attempted.

### Layout

```
code/lean/
  lakefile.toml            nominal, unverified
  lean-toolchain           nominal, unverified
  BSD.lean                 root module; imports the ten below
  BSD/
    Basic.lean             RigourTag (known/conditional/new/open_); the
                           epistemic tagging convention; what a `sorry` means
    FractureDiagram.lean   ArVertex, ArLe, and I_ar as a SmallCategory
    FAPSpace.lean          FAPSpace, FAPCoefficients, the forgetful maps
    Axioms.lean            class FAPAxioms with the twelve fields F1..F12
    Conjectures.lean       ConjectureA .. ConjectureM (no I), as `def ... : Prop`
    Obstructions.lean      Obstruction I..XIV, with `name`, `blocks`, `subsumes`
    Classical.lean         the classical inputs, and an honest Mathlib audit
    RankTheorem.lean       the payload: `rank_formula_of_axioms`
    Certificates.lean      C4 rank-lower-bound certificates and soundness
    Ledger.lean            every `sorry` in the tree, as structured data
  tools/
    check_tree.py          the lexical self-check
```

Line counts (from `tools/check_tree.py`):

| File | Lines |
|---|---:|
| `BSD.lean` | 35 |
| `BSD/Axioms.lean` | 278 |
| `BSD/Basic.lean` | 111 |
| `BSD/Certificates.lean` | 188 |
| `BSD/Classical.lean` | 396 |
| `BSD/Conjectures.lean` | 388 |
| `BSD/FAPSpace.lean` | 201 |
| `BSD/FractureDiagram.lean` | 179 |
| `BSD/Ledger.lean` | 243 |
| `BSD/Obstructions.lean` | 215 |
| `BSD/RankTheorem.lean` | 115 |
| **total `.lean`** | **2 349** |
| `tools/check_tree.py` | 313 |

---

## 3. What the tree is **not**

* It is **not a verification of anything**. Nothing has been verified. The word
  does not apply.
* It is **not a formalisation of BSD**, nor of the framework. It is a
  formalisation of the *shapes* of the framework's statements.
* It is **not evidence** for the conjectures. A conjecture rendered as a Lean
  `Prop` is the same conjecture, and a verified conditional theorem is exactly
  as strong as its hypotheses (Chapter 48, "What formalisation cannot do").
* It **does not decide whether the definitions are right**. Type-checking
  catches a large but proper subclass of definitional errors — the ill-formed
  ones. It does not catch the definition that is well-formed and wrong. And it
  has not even done that much here, since nothing has been type-checked.
* It **does not contain the twelve conjectures as claims**. They are
  `def ... : Prop` and are never asserted.

---

## 4. The `sorry` census

**Total: 10.** Every one carries an `-- OBLIGATION: <id>` comment on the line
immediately above it, and every one is registered in `BSD/Ledger.lean`. The
correspondence is checked mechanically by `tools/check_tree.py`.

| # | Module | Line | Obligation id | Tag | Ch. | Meaning |
|---|---|---:|---|---|---:|---|
| 1 | `FractureDiagram.lean` | 119 | `obl-ar-antisymm` | new | 7 | `I_ar` is a partial order, not merely a preorder: the five generating relations produce no cycles. |
| 2 | `FractureDiagram.lean` | 131 | `obl-ar-eta-not-prism` | new | 7 | `η ≰ p^prism`: the generic fibre carries no integral *p*-adic structure, so the comparison is imposed at the Fargues–Fontaine vertex instead. |
| 3 | `FAPSpace.lean` | 197 | `obl-fap-coeff-ext` | new | 7 | FAP coefficients agreeing at every vertex are equal. The *empty* half of conservativity; the substantive half is Axiom F1. |
| 4 | `Classical.lean` | 156 | `obl-mw-rank-zero-iff-torsion` | known | 48 | Mordell–Weil rank zero ⟺ torsion. Elementary given a definition of the rank; the definition is absent from Mathlib. |
| 5 | `Classical.lean` | 259 | `obl-cont-datum-unique` | new | 48 | Any two continuation data agree (identity theorem). Chapter 48's proposition, part (i). |
| 6 | `Classical.lean` | 270 | `obl-cont-datum-ne-zero` | new | 48 | A continuation datum for an elliptic curve is not identically zero (Hasse bound; let `Re s → ∞`). Part (ii). |
| 7 | `Classical.lean` | 288 | `obl-analytic-rank-welldef` | new | 48 | Hence `ord_{s=1}` depends only on the curve. Part (iii). |
| 8 | `Classical.lean` | 361 | `obl-selmer-bound-of-hes` | conditional | 30 | A higher Euler system plus finiteness of Ш bounds the rank above by `r`. Obstruction XII: Kolyvagin's derivative machinery has no `r`-dimensional analogue. |
| 9 | `RankTheorem.lean` | 63 | `obl-rank-formula` | conditional | 38 | **The payload.** F1–F12 + G + CTF + A + L + M + finiteness of Ш ⟹ `ord_{s=1} 𝒵_E = rank`. |
| 10 | `Certificates.lean` | 139 | `obl-cert-rank-lower-bound` | conditional | 47 | C4 soundness: an accepted certificate gives `r ≤ rank E(ℚ)`. Needs canonical heights, which are absent. |

Distribution: `Classical.lean` 4, `FractureDiagram.lean` 2, and one each in
`FAPSpace.lean`, `RankTheorem.lean`, `Certificates.lean` — and **zero** in
`Basic.lean`, `Axioms.lean`, `Conjectures.lean`, `Obstructions.lean`,
`Ledger.lean`. That distribution is deliberate: the axioms and the conjectures
are *hypotheses and statements*, not obligations, and writing them as
`theorem ... := sorry` would misrepresent them as things the book expects to
prove.

### The larger danger: the declared axioms

Ten `sorry`s are the *loud* part of the trusted base. The quiet part is larger.
This tree declares **66** `axiom`s, grouped as:

* `BSD/FAPSpace.lean` — `GeomAt`, `Comparison`, `Coherent`, `CyclotomicAction`,
  `FlowAction`, `CoeffAt`, `Glued`: the geometries and their gluing.
* `BSD/Axioms.lean` — the twelve statement-predicates behind F1–F12.
* `BSD/Conjectures.lean` — the framework invariants (`FundamentalLine`,
  `lambdaAn`, `lambdaAlg`, `zetaFAP`, `mordellWeilRank`, `hiddenFlowDim`, …)
  and the clause-predicates of the twelve conjectures.
* `BSD/Classical.lean` — Mordell–Weil, Selmer, Ш, heights, periods, Tamagawa
  numbers, `L`-series, and the two imported theorems `modularity` and
  `grossZagierKolyvagin`.

Chapter 48's axiom-accounting proposition is exactly about this: *a build whose
headline theorem depends on an undeclared axiom is worse than no build — it is
a false advertisement of rigour.* A real continuous-integration rule would
compute the transitive axiom set of every headline declaration and compare it
against a published whitelist. We cannot run it. The list above is what such a
rule would have to whitelist, and it is reproduced in Lean as
`BSD.declaredAxiomGroups`.

Note the distinction the book draws and this tree observes: **`sorry` marks a
genuine gap; `axiom` marks a deliberate enlargement of the trusted base.**
Recording Kolyvagin's theorem as an `axiom` is not a claim to have proved it; it
is a claim to have made every downstream use of it visible to `#print axioms`.

### What *is* proved

A small amount, all of it elementary, none of it checked:

* `RigourTag.meet_comm`, `meet_assoc`, `meet_idem`, `meet_open_left`,
  `meet_known_left`, `isUnconditional_meet_open` — the epistemic tag lattice, by
  exhaustive case analysis.
* `Weier.c4_c6_disc` — `1728·Δ = c₄³ − c₆²`, by `ring`. Transcribed verbatim
  from Chapter 48, sketch (1).
* `onCurveB_sound`, `checkOnCurve_sound`, `allOnCurve_sound`,
  `checkCertificate_points_on_curve` — soundness of the on-curve half of the C4
  checker, by `of_decide_eq_true` and one induction.
* `classicalRankFormula_of_analyticRank_le_one` — from the imported
  Gross–Zagier–Kolyvagin axiom.
* A dozen `rfl` facts pinning down the registers: twelve axioms, twelve
  conjectures, fourteen obstructions, eight construction obstructions, six
  practical obstructions, ten ledger entries.

---

## 5. Building it, if you have Lean

The tree has never been built. These are the commands you would use; they are
not commands anybody has run on this tree.

```bash
# 1. install the toolchain manager
curl https://raw.githubusercontent.com/leanprover/elan/master/elan-init.sh -sSf | sh

# 2. from code/lean
lake update            # resolve Mathlib; will rewrite lake-manifest.json
lake exe cache get     # fetch prebuilt Mathlib oleans -- do NOT skip this
lake build
```

**Caveats you should expect to hit.**

* The pin is nominal. `lean-toolchain` says `leanprover/lean4:v4.12.0` and
  `lakefile.toml` requires Mathlib at `master`. These will not in general be
  compatible. Pick a Mathlib commit, read *its* `lean-toolchain`, and copy that
  string into ours.
* `lake exe cache get` must be run *after* `lake update` and *before*
  `lake build`, or you will compile Mathlib from source.
* `lake build` will emit **ten `declaration uses 'sorry'` warnings**. That is
  the intended output, not a failure. If it emits fewer than ten, something has
  been silently removed; if more, `tools/check_tree.py` should have caught it.
* Expect real errors on first contact. The most likely failure points, in
  descending order of risk, are: the hand-written
  `CategoryTheory.SmallCategory` instance in `FractureDiagram.lean`; the
  `simp only [...]; ring` proof of `Weier.c4_c6_disc`; the `Bool.and_eq_true`
  rewrites in `Certificates.lean`; and the `Preorder` instance field names.
* `native_decide` is forbidden throughout, per Chapter 48 and Chapter 52: it
  enlarges the trusted base by a compiler and a runtime.

Then run the lexical check, which needs only Python:

```bash
python tools/check_tree.py
```

---

## 6. Self-check output

Verbatim, from this machine, at the time of writing:

```
BSD Lean skeleton -- lexical self-check
root: code/lean

files scanned: 11
  BSD.lean                           35 lines
  BSD/Axioms.lean                   278 lines
  BSD/Basic.lean                    111 lines
  BSD/Certificates.lean             188 lines
  BSD/Classical.lean                396 lines
  BSD/Conjectures.lean              388 lines
  BSD/FAPSpace.lean                 201 lines
  BSD/FractureDiagram.lean          179 lines
  BSD/Ledger.lean                   243 lines
  BSD/Obstructions.lean             215 lines
  BSD/RankTheorem.lean              115 lines

declarations found (namespace-qualified): 203
sorry occurrences: 10
  BSD/Certificates.lean        line 139   obl-cert-rank-lower-bound
  BSD/Classical.lean           line 156   obl-mw-rank-zero-iff-torsion
  BSD/Classical.lean           line 259   obl-cont-datum-unique
  BSD/Classical.lean           line 270   obl-cont-datum-ne-zero
  BSD/Classical.lean           line 288   obl-analytic-rank-welldef
  BSD/Classical.lean           line 361   obl-selmer-bound-of-hes
  BSD/FAPSpace.lean            line 197   obl-fap-coeff-ext
  BSD/FractureDiagram.lean     line 119   obl-ar-antisymm
  BSD/FractureDiagram.lean     line 131   obl-ar-eta-not-prism
  BSD/RankTheorem.lean         line 63    obl-rank-formula

ledger entries: 10

OK -- all lexical checks passed.

This says NOTHING about whether the tree type-checks.  Lean and
Mathlib are not installed here and the tree has never been built.
```

The checker was itself tested against a deliberately broken file — an unbalanced
paren, an `end Foo` closing `namespace BSD`, a duplicate declaration name, a
bad import and an unlabelled `sorry` — and reported all five. This matters:
Chapter 48 records that *a checker weakened until it always succeeds is a
realistic failure mode invisible to the type checker*, and that a checker is a
specification only if it discriminates.

---

## 7. What formalisation would and would not certify

This is the distinction the book insists on, and it is the reason the tree
exists at all.

**It would certify implications.** If `rank_formula_of_axioms` were completed,
the kernel would have checked that F1–F12, plus Conjecture G, plus the
categorified trace formula, plus Conjectures A, L, M, plus finiteness of Ш,
*jointly entail* the rank formula. That is a real and useful fact: the book is
one long conditional, and in a corpus of that shape the likeliest error is not a
false lemma but a **silent loss of conditionality** — a lemma proved under a
hypothesis and invoked, twenty chapters later, without it. A proof assistant
makes that error impossible to commit and trivial to detect, and it requires the
*least* formalisation: one need not prove Kolyvagin's theorem in Lean in order to
record it as an axiom and have the machine track who uses it.

**It would never certify the axioms.** F1–F12 are demands, not theorems.
Chapter 8 does not claim they are consistent; Problem 8.8.3 asks whether they
are, and it is open. Chapter 2 lists an inconsistency proof for F1–F12 as one of
the outcomes the programme would count as a *result*. Accordingly
`FAPAxiomsConsistency` in `BSD/Axioms.lean` is a `def ... : Prop`, deliberately
not a `theorem ... := sorry`: a `sorry` would assert that the book expects it to
be provable, and the book expects no such thing.

**It would never certify the conjectures**, and it would not raise their
credibility by a particle. If the hypothesis is Conjecture A, the theorem asserts
nothing unconditional about any elliptic curve.

**It would not supply mathematical ideas.** Every unconditional advance on the
conjecture — Coates–Wiles, Gross–Zagier, Kolyvagin, Kato, Skinner–Urban — rested
on a construction that did not previously exist: elliptic units, Heegner points,
Euler systems, `p`-adic families. Nothing in a proof assistant generates objects
of that kind.

**It would not tell you whether a definition is right.** Both the correct
definition of Ш and a subtly wrong one type-check, and both support theorems.
Noticing which one makes the descent sequence exact is mathematics.

The honest one-line description of the deliverable, transcribed from
Chapter 48: *a machine-checked account of what this book would prove if its
conjectures were true.* This tree is not even that yet. It is the scaffolding
for it, unbuilt.

---

## 8. Discrepancies and deliberate deviations

Recorded here rather than smoothed over, per the book's Statement of Epistemic Status.

> **Note (publication, 2026-10-23).** This section records the state of the book when this tree was written. Chapters 8, 49 and 50 have since been written: Chapter 8 states F1–F12 (and Table 8.1 the absorption of the earlier axioms C1–C12), and where it differs from `BSD/Axioms.lean`, Chapter 8 governs. The published book counts eleven conjectures rated four or five stars, as `BSD.hardCount_eq` does. The drafting notes cited below (the chapter specifications, the synthesis of the working formulations) are not published; the book states their content in the chapters named.

1. **`ch49` and `ch50` do not exist.** `book/chapters/` contains no
   `ch49-*.tex` and no `ch50-the-multi-agent-mathematician.tex` at the time of
   writing. `ch48` forward-references
   `\Cref{ch:ch49-autoformalisation-and-proof-search}`. Nothing in this tree
   depends on them.

2. **`ch08-the-twelve-axioms.tex` does not exist either.** The twelve axioms are
   reconstructed in `BSD/Axioms.lean` from the chapter specification for Chapter 8 (which
   fixes the grouping F1–F2 / F3–F5 / F6–F7 / F8 / F9–F10 / F11–F12), from
   the synthesis of the working formulations (the C→F absorption table, now Table 8.1 of the book), and from the
   places where written chapters state individual axioms (ch06 for F5, ch07 for
   F1/F4/F7/F11, ch13 for F9/F10, ch20 for F12, ch21 for F11). Where the
   eventual Chapter 8 disagrees, Chapter 8 wins and this file must be corrected.

3. **"twelve fields F1…F12, each a `Prop`".** The specification's phrase is ambiguous
   between *a field whose type is `Prop`* (the class carries twelve statements)
   and *a field whose type is a `Prop`* (the class carries twelve proofs). We
   took the second, idiomatic reading: only it makes `[FAPAxioms X]` usable as a
   hypothesis downstream, which is the whole of Chapter 48's argument that a
   typeclass is the right idiom for machine-visible conditionality. The twelve
   *statements* are the named predicates `RealisationConservative`, …,
   `SelmerFixedPoint`, declared as `axiom`s immediately above the class.

4. **`rank_formula_of_axioms` has four hypotheses more than the specification asked
   for.** the specification gave the signature with `[FAPAxioms X]`, `hG` and `hCTF`.
   Chapter 38's Theorem 38.3.1 is conditional *in addition* on Conjectures A, L
   and M and on finiteness of Ш — its specification says in terms "every hypothesis
   listed" — and the synthesis of the register (Chapter 3 of the book) confirms that Conjecture A depends on L,
   M and K. Omitting them would make the Lean statement **stronger than the
   theorem the book proves**, which the honesty rule forbids. They are present
   as explicit named arguments `hA`, `hL`, `hM`, `hSha`. The obligation id and
   the conclusion are unchanged.

5. **The category instance was written out by hand.** the specification allowed either a
   `CategoryTheory.Category` instance or a `Quiver` with axiomatised coherence.
   We chose the first, because for a *poset* the coherence is free: hom-types
   are `PLift` of a `Prop`, parallel morphisms are equal by proof irrelevance,
   and the three category laws are `rfl`. What we did *not* do is route through
   Mathlib's preorder-to-category instance, whose exact name we cannot check
   from here.

6. **Primes are `Nat`, not primes.** `ArVertex.prism (p : Nat)` follows the specification's constructor signature; primality is not enforced by the type. Chapter
   7 indexes by an actual prime. This is a genuine weakening and a real
   formalisation would either carry a `Nat.Prime` proof in the constructor or
   quotient the diagram by a primality predicate.

7. **`ArVertex.fargFont` and `ArVertex.analytic` are ordered as the specification lists
   them, not as Chapter 7 lists them.** Chapter 7's order is
   η, ∞, p^prism, p^HT, p^an, p^FF; the specification's constructor order puts
   `fargFont` before `analytic`. We follow the specification for the constructor order
   (it is immaterial) and Chapter 7 for the *relations*, which are what carry
   content: `p^an ≤ p^FF`, not the reverse.

8. **The infinite tower of coherences is compressed to one `Prop`.** Clause (7)
   of Chapter 7's definition asks for a transition functor per relation, a
   coherence equivalence per composable pair, "together with all higher
   coherences". `FAPSpace.cocycle` records only the first level. This is a real
   loss of information; it is honest only because nothing downstream in this
   tree uses more than the statement.

9. **The register says "ten of twelve"; its own table says eleven.**
   the synthesis of the register (Chapter 3 of the book) asserts "Ten of twelve conjectures are ★★★★ or
   ★★★★★. Only H is genuinely tractable", but the table immediately above rates
   H at three stars and *every* other conjecture at four or five — that is
   eleven, not ten. `BSD.hardCount_eq` follows the table and evaluates to `11`,
   with the discrepancy noted in the file. The book's prose should be corrected
   to "eleven of twelve", or one further conjecture demoted.

10. **Chapter 51's `provenance` and `discharge condition` fields are not
    modelled** in `BSD.Obligation`. Provenance would have to name a person and a
    date; a discharge condition would have to be machine-checkable. Neither is
    available here, and inventing them would be worse than omitting them. The
    `Obligation` structure is therefore a proper *reduct* of Chapter 51's
    definition, not an implementation of it.

11. **No Mathlib declaration is named except `CommRing`, `Rat`, `Complex`,
    `Preorder`, `CategoryTheory.SmallCategory`, `PLift` and the `ring`,
    `simp only`, `induction` and `cases` tactics**, and only five Mathlib
    modules are imported: `Mathlib.Order.Basic`,
    `Mathlib.CategoryTheory.Category.Basic`, `Mathlib.Data.Rat.Defs`,
    `Mathlib.Data.Complex.Basic`, `Mathlib.Tactic.Ring`. Chapter 48's Warning
    "audit" forbids asserting the existence of particular declaration names,
    because names change far faster than a monograph is revised. Everything else
    that would have come from Mathlib — entire functions, `L`-series, orders of
    vanishing, Selmer groups, heights — is a local `axiom` with a
    `TODO: replace with Mathlib's ‹…› once the exact name is confirmed`. Even
    the seven names and five paths above are a risk, and they are the first
    thing to check on a machine with a compiler. (`of_decide_eq_true` and
    `Bool.and_eq_true` are core Lean, not Mathlib.)

12. **The Mathlib audit table in `BSD/Classical.lean` is transcribed from
    Chapter 48 and has not been re-verified.** It is deliberately understated.
    Chapter 48's own warning applies: any printed statement about library
    contents is stale on the day it is printed.
