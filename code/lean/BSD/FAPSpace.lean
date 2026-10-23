/-
  BSD/FAPSpace.lean

  FAP spaces and FAP coefficients (Chapter 7, `defn:ch07-fap-space`,
  `defn:ch07-fap-category`, `defn:ch07-coefficients`).

  UNCHECKED.  Not compiled; see BSD/Basic.lean and README.md.

  METHODOLOGICAL NOTE.  The geometries that sit at the vertices of `I_ar` --
  hypercomplete structured infinity-topoi, prismatic stacks, small v-stacks,
  derived real analytic stacks -- do not exist in Mathlib and will not for many
  years (Chapter 48, Table "Objects required by the BSD formula").  They are
  therefore declared here as `axiom`s: opaque type families with no content.
  This is the specification-first methodology of Chapter 48, sketch (5): fix
  the interface, derive the consequences, leave the construction as an
  obligation.  An `axiom` here is a deliberate enlargement of the trusted base
  and every one of them is declared in the open.
-/

import BSD.FractureDiagram

namespace BSD

/--
The type of geometric objects appropriate to a vertex of `I_ar`: a condensed
analytic stack over `Q` at `eta`, a derived real analytic stack with involution
at `infty`, a bounded quasisyntomic prismatic stack at `prism p`, and so on
(Chapter 7, the vertex dictionary).

TODO: replace by an actual construction once the objects exist.  There is no
Mathlib declaration to reach for here; this is not a naming problem but a
mathematical one.
-/
axiom GeomAt : ArVertex → Type

/--
The type of comparison data between the value of a diagram at one vertex and
its value at another.  Clause (7) of the definition of a FAP space asks for a
transition functor for each relation of `I_ar` and a coherence equivalence for
each composable pair.

TODO: replace by a genuine functor category once `GeomAt` is constructed.
-/
axiom Comparison : {i j : ArVertex} → GeomAt i → GeomAt j → Type

/--
The coherence (cocycle) condition on a composable pair of comparisons.  Clause
(7) of the definition of a FAP space, and all higher coherences with it,
compressed into a single `Prop`.  Compressing an infinite tower of coherences
into one proposition is a genuine loss of information and is flagged as such in
the README; it is honest only because nothing downstream uses more than the
statement.
-/
axiom Coherent : {i j k : ArVertex} → {x : GeomAt i} → {y : GeomAt j} →
    {z : GeomAt k} → Comparison x y → Comparison y z → Comparison x z → Prop

/--
The coherent action of the multiplicative monoid of positive integers by
correspondences (clause (5) of the definition of a FAP space): the absolute
cyclotomic operations `psi^n`, restricting to `phi_p` on the p-typical
prismatic component.  Axiom F4 is the demand that this exist and be coherent.
-/
axiom CyclotomicAction : ((i : ArVertex) → GeomAt i) → Type

/--
The continuous action of the reals on the rationalised periodic coefficient
category, with infinitesimal generator `Theta` (clause (6) of the definition of
a FAP space), together with the specified 2-isomorphism relating `sigma^{log p}`
to geometric Frobenius at `p`.  Its existence is Conjecture L and Obstruction
IV; declaring the *type* asserts nothing.
-/
axiom FlowAction : ((i : ArVertex) → GeomAt i) → Type

/--
A **FAP space** (Frobenius--Arakelov--Prismatic space), Chapter 7,
`defn:ch07-fap-space`, written `\mathfrak{X}` in the book.

The book's tuple has eight clauses.  Here clauses (1)--(4) and (8) are packaged
as the diagram `obj`, clause (7) as `alpha` together with `cocycle`, clause (5)
as `psi` and clause (6) as `sigma`.  The packaging is a presentation choice;
nothing is added and nothing is removed.

WARNING, transcribed from Chapter 7: this definition says what it would mean
for something to be a FAP space.  It does not exhibit one.  Beyond two
degenerate examples nothing is known to satisfy it together with the axioms
F1--F12.  `FAPSpace` being a Lean type does not make it inhabited by anything
of arithmetic interest, and nothing in this tree may be read as asserting that
it is.
-/
structure FAPSpace where
  /-- Clauses (1)--(4), (8): the underlying `I_ar`-diagram of geometric objects. -/
  obj : (i : ArVertex) → GeomAt i
  /-- Clause (7), first half: a transition datum for each relation of `I_ar`. -/
  alpha : {i j : ArVertex} → ArLe i j → Comparison (obj i) (obj j)
  /-- Clause (7), second half: cocycle coherence on composable pairs. -/
  cocycle : ∀ {i j k : ArVertex} (h₁ : ArLe i j) (h₂ : ArLe j k),
    Coherent (alpha h₁) (alpha h₂) (alpha (ArLe.trans h₁ h₂))
  /-- Clause (5): the absolute cyclotomic operations. -/
  psi : CyclotomicAction obj
  /-- Clause (6): the arithmetic flow on rationalised periodic coefficients. -/
  sigma : FlowAction obj

namespace FAPSpace

/-- The forgetful map to the vertex `i`; the book writes `ev_i`. -/
def ev (X : FAPSpace) (i : ArVertex) : GeomAt i := X.obj i

theorem ev_def (X : FAPSpace) (i : ArVertex) : X.ev i = X.obj i := rfl

/-- The generic vertex. -/
def generic (X : FAPSpace) : GeomAt ArVertex.eta := X.ev ArVertex.eta

/-- The archimedean vertex.  The only vertex with no Frobenius; a leaf. -/
def archimedean (X : FAPSpace) : GeomAt ArVertex.infty := X.ev ArVertex.infty

/-- The prismatic vertex at `p`. -/
def prismatic (X : FAPSpace) (p : Nat) : GeomAt (ArVertex.prism p) :=
  X.ev (ArVertex.prism p)

/-- The Hodge--Tate vertex at `p`. -/
def hodgeTate (X : FAPSpace) (p : Nat) : GeomAt (ArVertex.hodgeTate p) :=
  X.ev (ArVertex.hodgeTate p)

/-- The analytic (diamond) vertex at `p`. -/
def analytic (X : FAPSpace) (p : Nat) : GeomAt (ArVertex.analytic p) :=
  X.ev (ArVertex.analytic p)

/-- The Fargues--Fontaine vertex at `p`: where generic and p-adic data are
required to agree. -/
def fargFont (X : FAPSpace) (p : Nat) : GeomAt (ArVertex.fargFont p) :=
  X.ev (ArVertex.fargFont p)

/-- The comparison imposed at the Fargues--Fontaine vertex by the relation
`eta <= fargFont p`.  This single datum is the entire contact between the
rational motive and the p-adic geometry. -/
def etaFFComparison (X : FAPSpace) (p : Nat) :
    Comparison (X.obj ArVertex.eta) (X.obj (ArVertex.fargFont p)) :=
  X.alpha (ArLe.eta_fargFont p)

end FAPSpace

/--
The type of coefficient objects appropriate to a vertex: solid modules at
analytic vertices, derived quasicoherent F-gauges at prismatic vertices,
constructible l-adic sheaves at diamond vertices, equivariant real Deligne
complexes at `infty` (Chapter 7, section on coefficients).

TODO: replace by the actual categories once they exist.
-/
axiom CoeffAt : (i : ArVertex) → GeomAt i → Type

/-- The gluing condition on a pair of coefficient objects along a comparison. -/
axiom Glued : {i j : ArVertex} → {x : GeomAt i} → {y : GeomAt j} →
    Comparison x y → CoeffAt i x → CoeffAt j y → Prop

/--
**FAP coefficients** on a FAP space (Chapter 7, `defn:ch07-coefficients`):
the limit over `I_ar` of the vertexwise coefficient categories.  By the
sections description quoted in Chapter 7 from Lurie, an object of the limit is
a vertexwise family together with compatible comparison equivalences, and that
is exactly what this structure records.

We record objects only.  The morphisms, the symmetric monoidal structure, the
dualisable constructible part `D_{FAP,c}` and the integral perfect part
`Perf_{FAP}` are not modelled; they are what Axioms F6 and F7 are about.
-/
structure FAPCoefficients (X : FAPSpace) where
  /-- The value at each vertex. -/
  comp : (i : ArVertex) → CoeffAt i (X.obj i)
  /-- Compatibility along each relation of `I_ar`. -/
  glue : ∀ {i j : ArVertex} (h : ArLe i j), Glued (X.alpha h) (comp i) (comp j)

namespace FAPCoefficients

/-- The forgetful map on coefficients. -/
def ev {X : FAPSpace} (M : FAPCoefficients X) (i : ArVertex) : CoeffAt i (X.obj i) :=
  M.comp i

theorem ev_def {X : FAPSpace} (M : FAPCoefficients X) (i : ArVertex) :
    M.ev i = M.comp i := rfl

/--
Coefficients are determined by their vertex values.

This is the *empty* half of the conservativity story, in the sense of
Chapter 7: an equivalence of `I_ar`-diagrams is a vertexwise equivalence, and
that says nothing.  The substantive statement, which uses a strictly smaller
family of vertices, is Axiom F1 (see `BSD/Axioms.lean`) and is not this.

Even the empty half is not free in Lean: the `glue` field is a dependent family
of `Prop`s, so the extensionality argument needs proof irrelevance plus a
dependent congruence.  Rather than guess at the tactic, we record it.
-/
theorem ext_of_vertexwise {X : FAPSpace} (M N : FAPCoefficients X)
    (h : ∀ i, M.comp i = N.comp i) : M = N := by
  -- OBLIGATION: obl-fap-coeff-ext
  sorry

end FAPCoefficients

end BSD
