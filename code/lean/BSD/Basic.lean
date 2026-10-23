/-
  BSD/Basic.lean

  Universe and namespace setup, and the epistemic tagging convention.

  STATUS OF THIS FILE AND OF THE WHOLE TREE.  Nothing here has been compiled.
  Lean 4 and Mathlib are not installed in the environment in which this tree
  was written, so every declaration below is *unchecked source*.  No claim of
  correctness, and in particular no claim of type-correctness, is made.

  Reference: Chapter 48, "Formalisation in Lean"; Chapter 51, "The Proof
  Obligation Ledger"; the book's Statement of Epistemic Status (the honesty rule).
-/

namespace BSD

universe u v w

/--
The four epistemic tags of the book, mirroring the LaTeX macros
`\KNOWN`, `\COND`, `\NEW`, `\OPEN` of the book (Statement of Epistemic Status).

* `known`       -- a theorem of the existing literature, with a real citation.
* `conditional` -- true conditionally on hypotheses that are stated explicitly.
* `new`         -- proposed or constructed in the book, with a complete proof
                   given there.
* `open_`       -- a conjecture or open problem; no proof is claimed.
                   (The trailing underscore is forced: `open` is a Lean
                   keyword.)

READ THIS BEFORE READING ANY `theorem` IN THIS TREE.  A `theorem` whose proof
is `sorry` is **not a result**.  It is an *obligation*: a statement that the
book asserts must eventually be discharged, recorded here in a form a machine
can track.  Lean will accept such a file and emit a warning; it will also mark
every downstream declaration as depending on `sorryAx`.  In this tree every
`sorry` carries an `-- OBLIGATION: <id>` comment on the line above it and is
listed in `BSD/Ledger.lean`.  Nothing in this tree proves the
Birch--Swinnerton-Dyer conjecture, and nothing in it is evidence for or
against it.

Note also the distinction the book draws (Chapter 48, section on the eight
sketches): `sorry` marks a genuine gap; `axiom` marks a deliberate enlargement
of the trusted base.  Both appear below, and they mean different things.
-/
inductive RigourTag where
  | known
  | conditional
  | new
  | open_
  deriving DecidableEq, Repr

namespace RigourTag

/--
Combination of tags along a chain of reasoning: a conclusion is no stronger
than the weakest link.  The order of weakness is
`known` < `new` < `conditional` < `open_`, so `open_` absorbs everything.

This is the epistemic analogue of the three-element rigour lattice of
Chapter 42 (exact / certified interval / heuristic) reproduced in Chapter 48;
the shape of the definition is deliberately the same.
-/
def meet : RigourTag → RigourTag → RigourTag
  | open_,       _           => open_
  | _,           open_       => open_
  | conditional, _           => conditional
  | _,           conditional => conditional
  | new,         _           => new
  | _,           new         => new
  | known,       known       => known

theorem meet_comm (a b : RigourTag) : meet a b = meet b a := by
  cases a <;> cases b <;> rfl

theorem meet_assoc (a b c : RigourTag) :
    meet (meet a b) c = meet a (meet b c) := by
  cases a <;> cases b <;> cases c <;> rfl

theorem meet_idem (a : RigourTag) : meet a a = a := by
  cases a <;> rfl

theorem meet_open_left (a : RigourTag) : meet open_ a = open_ := by
  cases a <;> rfl

theorem meet_known_left (a : RigourTag) : meet known a = a := by
  cases a <;> rfl

/-- A tag is *load-bearing* if it does not by itself license an unconditional
assertion.  `known` and `new` do; `conditional` and `open_` do not. -/
def isUnconditional : RigourTag → Bool
  | known       => true
  | new         => true
  | conditional => false
  | open_       => false

theorem isUnconditional_open : isUnconditional open_ = false := rfl

theorem isUnconditional_meet_open (a : RigourTag) :
    isUnconditional (meet a open_) = false := by
  cases a <;> rfl

end RigourTag

/--
A one-line human-readable citation into the book.  Used by `BSD.Ledger` and by
the doc-comments throughout.  It is a `String`, not a checked reference:
nothing verifies that the chapter cited says what the comment claims.
-/
abbrev BookRef := String

end BSD
