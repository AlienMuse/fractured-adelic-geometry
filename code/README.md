# Companion code — Fractured Adelic Geometry

This is the code that accompanies *Fractured Adelic Geometry* (Research Architecture Edition 1, version 1.0.0), by Vincent Liu, licensed under the Apache
License 2.0 (`LICENSE`); the monograph itself is licensed under CC BY-NC-ND 4.0. The Birch and Swinnerton-Dyer
conjecture remains open; nothing here proves it.

| folder | what it is | book |
|---|---|---|
| `python/` | BSDKit, the certificate-first reference implementation of the computational architecture: exact curve arithmetic, Frobenius traces by two methods, certified L-value intervals, descent bounds, certificates and a ledger; `tests/` holds its unit tests | Part VII, App. G |
| `verify/` | the independent certificate checker (`check.py`): it does not import BSDKit | Ch. 47 |
| `lean/` | the Lean 4 sources of the formal statements: the axioms as a typeclass, the conjectures, the obstruction atlas, the ledger and the conditional rank theorem. **They have not been compiled**: `lean/README.md` states what is missing (`sorry`, local `axiom`s) | Part VIII, App. H |

## Reproduce

Python 3.11 or later with `mpmath` (tested: Python 3.11.9, mpmath 1.4.1). From this folder:

```sh
cd python
python -m unittest discover -s tests      # BSDKit tests
python cli.py ap 11.a1 2 3 5 7 13         # point counts and Frobenius traces (Table G.5 of the book)
```

The Lean tree is checked lexically by `python lean/tools/check_tree.py`; it is not a compiled formalisation.
`REPRODUCIBILITY.md` is the C-3 report of the final edition: the tests, the independent recomputation of the
numerical tables of Appendix G, and the lexical check of the Lean sources.

## Changes from the working tree

The files are the author's working tree, with the documentation edits listed in `CODE-EDITS.md` (the title and
series of the published book; references to unpublished drafting notes replaced by the places of the book that state
the same thing; two script names) — no line of program code is changed except one `import` that follows a rename.
