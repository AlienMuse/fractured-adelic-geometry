/-
  BSD/Obstructions.lean

  The obstruction atlas: fourteen obstructions, roman numerals I--XIV.
  Canonical source: book Chapter 53.

  UNCHECKED.  Not compiled; see BSD/Basic.lean and README.md.

  I--VIII obstruct the Construction Problem (Problem 7.6.1: does a FAP space
  satisfying F1--F12 exist?).  IX--XIV obstruct the arithmetic and analytic
  routes, and are *not* obstructions to the Construction Problem.  The
  numbering is fixed by the writing contract and must not be changed.

  Lean identifiers cannot begin with a numeral-like roman literal without
  ambiguity, so the constructors are named `obs_I` ... `obs_XIV`.
-/

import BSD.Basic

namespace BSD

/-- The fourteen obstructions of the atlas. -/
inductive Obstruction where
  /-- I. The adelic structured infinity-topos. -/
  | obs_I
  /-- II. Coherence of prismatic gauges across all primes. -/
  | obs_II
  /-- III. The archimedean place and the Arakelov boundary. -/
  | obs_III
  /-- IV. Construction of the arithmetic flow. -/
  | obs_IV
  /-- V. Nuclearity and meromorphic continuation. -/
  | obs_V
  /-- VI. Independence of realisation. -/
  | obs_VI
  /-- VII. The Selmer fixed-point principle. -/
  | obs_VII
  /-- VIII. Equality of the two trivialisations. -/
  | obs_VIII
  /-- IX. Existence and representability of the stack of r-legged shtukas. -/
  | obs_IX
  /-- X. Integral multi-leg norm relations. -/
  | obs_X
  /-- XI. The higher relative trace identity over the rationals. -/
  | obs_XI
  /-- XII. Primitivity, transversality, derived rank-r descent. -/
  | obs_XII
  /-- XIII. Wild integral control at 2 and 3, additive reduction. -/
  | obs_XIII
  /-- XIV. The mechanism for rank at least two. -/
  | obs_XIV
  deriving DecidableEq, Repr

namespace Obstruction

/-- The roman numeral, as the book prints it. -/
def numeral : Obstruction → String
  | obs_I    => "I"
  | obs_II   => "II"
  | obs_III  => "III"
  | obs_IV   => "IV"
  | obs_V    => "V"
  | obs_VI   => "VI"
  | obs_VII  => "VII"
  | obs_VIII => "VIII"
  | obs_IX   => "IX"
  | obs_X    => "X"
  | obs_XI   => "XI"
  | obs_XII  => "XII"
  | obs_XIII => "XIII"
  | obs_XIV  => "XIV"

/-- The book's one-line name for each obstruction. -/
def name : Obstruction → String
  | obs_I    => "The adelic structured infinity-topos"
  | obs_II   => "Coherence of prismatic gauges across all p"
  | obs_III  => "The archimedean place and the Arakelov boundary"
  | obs_IV   => "Construction of the arithmetic flow"
  | obs_V    => "Nuclearity and meromorphic continuation"
  | obs_VI   => "Independence of realisation"
  | obs_VII  => "The Selmer fixed-point principle"
  | obs_VIII => "Equality of the two trivialisations"
  | obs_IX   => "Existence and representability of Sht^(r) over Z"
  | obs_X    => "Integral multi-leg norm relations"
  | obs_XI   => "The higher relative trace identity over Q"
  | obs_XII  => "Primitivity, transversality, derived rank-r descent"
  | obs_XIII => "Wild integral control at p = 2, 3 and additive reduction"
  | obs_XIV  => "The mechanism for r at least 2"

/--
What each obstruction blocks: axioms, conjectures and chapters, as strings.
Transcribed from the "Blocks" column of the atlas, Chapter 53.  Strings,
not typed references, because several of the targets (chapters, the routes)
have no Lean counterpart.
-/
def blocks : Obstruction → List String
  | obs_I    => ["F1", "F2", "everything downstream"]
  | obs_II   => ["F5", "Ch. 6", "Ch. 10"]
  | obs_III  => ["F3", "F11", "Ch. 5", "Ch. 17", "Ch. 22"]
  | obs_IV   => ["Route 1 entirely", "Conjecture L"]
  | obs_V    => ["Ch. 13", "Ch. 16", "Ch. 17", "Conjecture M"]
  | obs_VI   => ["F1", "F10", "Ch. 10", "Ch. 22"]
  | obs_VII  => ["F12", "Ch. 20", "Ch. 21", "Conjecture A", "Conjecture G",
                 "Conjecture K"]
  | obs_VIII => ["Conjecture A", "Ch. 37", "Ch. 39"]
  | obs_IX   => ["Route 2 entirely", "Conjecture B", "Conjecture D",
                 "Conjecture F"]
  | obs_X    => ["Ch. 29", "Ch. 30", "Conjecture B", "Conjecture F"]
  | obs_XI   => ["Conjecture C", "Ch. 34", "Ch. 35"]
  | obs_XII  => ["rank upper bound", "Thm 30.4.1 second half"]
  | obs_XIII => ["Conjecture F", "Conjecture J", "Ch. 22", "Ch. 30", "Ch. 39"]
  | obs_XIV  => ["Conjecture G", "the explanatory claim of Route 1"]

/--
Which known open problem, if any, an obstruction subsumes.  These are the facts
the book insists must never be softened:

* **IV subsumes Deninger's programme in full.**
* **VII subsumes finiteness of Sha, and the ETNC.**
* **VIII subsumes the ETNC for `h^1(E)(1)`.**
* **XI subsumes a number-field Yun--Zhang.**
* **XIV *is* the rank at least two barrier itself.**

III, V, VI and XII subsume something only partly, and the partial answers are
recorded as such rather than promoted.
-/
def subsumes : Obstruction → Option String
  | obs_I    => none
  | obs_II   => none
  | obs_III  => some "partly: Deninger's archimedean programme"
  | obs_IV   => some "YES: Deninger's programme in full"
  | obs_V    => some "partly: the intrinsic proof of continuation of Lambda(E,s)"
  | obs_VI   => some "partly: l-independence of local terms"
  | obs_VII  => some "YES: finiteness of Sha; and the ETNC"
  | obs_VIII => some "YES: the ETNC for h^1(E)(1)"
  | obs_IX   => some "depends on IV: the same missing Frobenius"
  | obs_X    => none
  | obs_XI   => some "YES: a number-field Yun-Zhang"
  | obs_XII  => some "partly: the converse half of Kolyvagin"
  | obs_XIII => none
  | obs_XIV  => some "YES: this is the rank at least 2 barrier itself"

/-- Difficulty on the book's one-to-five star scale. -/
def difficulty : Obstruction → Nat
  | obs_I    => 3
  | obs_II   => 3
  | obs_III  => 4
  | obs_IV   => 5
  | obs_V    => 4
  | obs_VI   => 3
  | obs_VII  => 5
  | obs_VIII => 5
  | obs_IX   => 5
  | obs_X    => 4
  | obs_XI   => 5
  | obs_XII  => 4
  | obs_XIII => 4
  | obs_XIV  => 5

/-- I--VIII obstruct the Construction Problem; IX--XIV obstruct the arithmetic
and analytic routes and are not obstructions to it. -/
def obstructsConstructionProblem : Obstruction → Bool
  | obs_I | obs_II | obs_III | obs_IV | obs_V | obs_VI | obs_VII | obs_VIII =>
      true
  | _ => false

/-- The book's LaTeX label. -/
def latexLabel (o : Obstruction) : String := "obs:" ++ o.numeral

/-- Every obstruction is OPEN.  There is no other value. -/
def tag : Obstruction → RigourTag := fun _ => RigourTag.open_

end Obstruction

/-- The atlas, in order. -/
def obstructionAtlas : List Obstruction :=
  [Obstruction.obs_I, Obstruction.obs_II, Obstruction.obs_III,
   Obstruction.obs_IV, Obstruction.obs_V, Obstruction.obs_VI,
   Obstruction.obs_VII, Obstruction.obs_VIII, Obstruction.obs_IX,
   Obstruction.obs_X, Obstruction.obs_XI, Obstruction.obs_XII,
   Obstruction.obs_XIII, Obstruction.obs_XIV]

theorem obstructionAtlas_length : obstructionAtlas.length = 14 := rfl

/-- The eight obstructions to the Construction Problem. -/
def constructionObstructions : List Obstruction :=
  obstructionAtlas.filter Obstruction.obstructsConstructionProblem

theorem constructionObstructions_length : constructionObstructions.length = 8 := rfl

/-- The five obstructions that outright subsume a known major open problem:
IV, VII, VIII, XI, XIV.  This list is the honest measure of how far the
programme is from a proof. -/
def subsumingObstructions : List Obstruction :=
  [Obstruction.obs_IV, Obstruction.obs_VII, Obstruction.obs_VIII,
   Obstruction.obs_XI, Obstruction.obs_XIV]

theorem subsumingObstructions_length : subsumingObstructions.length = 5 := rfl

/-- Practical (engineering, not mathematical) obstructions P1--P6, catalogued
separately in Chapter 55 and deliberately kept out of the atlas numbering.
P6 is the formalisation gap that this very tree documents. -/
def practicalObstructions : List (String × String) :=
  [ ("P1", "Mordell-Weil and Sha completeness at scale"),
    ("P2", "certified analytic derivatives of high order"),
    ("P3", "Heegner points of enormous height"),
    ("P4", "general p-descent"),
    ("P5", "no algorithmic substrate for prismatic/FAP objects"),
    ("P6", "the formalisation gap: Neron models, Tate's algorithm, "
           ++ "Mordell-Weil, canonical heights, Selmer, Sha, modularity "
           ++ "are all absent from mathlib") ]

theorem practicalObstructions_length : practicalObstructions.length = 6 := rfl

end BSD
