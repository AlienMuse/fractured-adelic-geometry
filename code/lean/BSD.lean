/-
Author:       Vincent Liu
Organisation: WiseMotif.ai

Formalisation skeleton accompanying *Fractured Adelic Geometry: A Foundational Framework for the Birch and Swinnerton-Dyer Conjecture* (WiseMotif Monograph of Mathematical Intelligence, Series 04), Chapter 48.

HONESTY NOTE. This tree has never been compiled; Lean and Mathlib are not
installed here. Nothing in it is verified, and it does not prove BSD.
-/

/-
  BSD.lean -- root module of the BSD formalisation skeleton.

  This tree accompanies Part VIII of the monograph and is described in
  Chapter 48, "Formalisation in Lean".

  IT HAS NEVER BEEN COMPILED.  Lean 4, elan, lake and Mathlib are not installed
  in the environment in which it was written.  Every declaration in it is
  unchecked source.  See README.md for the `sorry` census, the list of declared
  axioms, and an honest statement of what the tree is and is not.

  What the tree targets, on Chapter 48's five-level ladder:

    F0  statability of the classical conjecture  -- partial, and only relative
        to a continuation datum (BSD/Classical.lean)
    F1  statability of the framework             -- attempted here
    F2  elementary consequences                  -- barely begun
    F3  conditional theorems                     -- one, and it is a `sorry`
    F4  the conjectures themselves               -- not a formalisation target;
        it is the mathematics

  Nothing here bears on the truth of the Birch--Swinnerton-Dyer conjecture,
  which remains open.
-/

import BSD.Basic
import BSD.FractureDiagram
import BSD.FAPSpace
import BSD.Axioms
import BSD.Classical
import BSD.Conjectures
import BSD.Obstructions
import BSD.RankTheorem
import BSD.Certificates
import BSD.Ledger
