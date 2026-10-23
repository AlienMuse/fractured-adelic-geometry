# BSDKit Python reference

**Author:** Vincent Liu · **Organisation:** WiseMotif.ai

Companion code to *Fractured Adelic Geometry: A Foundational Framework for the Birch and Swinnerton-Dyer Conjecture* (WiseMotif Monograph of Mathematical Intelligence, Series 04).

BSDKit is the runnable, certificate-first Python companion to Part VII.  Exact
curve arithmetic uses only the standard library.  `mpmath` is optional and is
used only by routines whose output is explicitly tagged `numerical`.

## Install and test

```powershell
cd code/python
python -m pip install mpmath
python -m unittest discover -s tests -v
```

No network or database is used at runtime.  The only labelled curve catalogue is
the five running curves of the book (Appendix G, Table G.1).

## Commands

Run commands from `code\python`:

| Command | Purpose |
|---|---|
| `python cli.py curve 11.a1` | Exact invariants, minimality status, torsion, conductor and Tate data |
| `python cli.py ap 11.a1 3 5 7` | Point counts and Frobenius traces by two exact methods |
| `python cli.py lvalue 11.a1 --bits 40` | Certified central-value interval and explicit tail |
| `python cli.py lvalue 37.a1 -r 1` | Higher derivative; currently tagged `numerical` |
| `python cli.py rank 389.a1` | Point-search lower bound, descent upper bound, and verdict |
| `python cli.py certificate 11.a1 --kind ap --prime 7 -o cert.json` | Emit canonical C1 JSON |
| `python cli.py certificate 37.a1 --kind rank -o rank.json` | Emit a C4 rank-lower certificate |
| `python cli.py verify cert.json` | Invoke the separate dependency-free checker |

The versioned schema is `bsdkit\certificate-schema.json`.  The checker is
`code\verify\check.py`; it does not import producer code and rejects evidence
kinds it does not understand.

## Rigour boundaries

`proved`, `conditional`, `heuristic`, and `numerical` are distinct output tags.
The rational interval kernel uses exact endpoints and proved remainder bounds.
The order-zero incomplete-gamma expansion is certified.  Higher derivatives
currently use an `mpmath` fallback and are therefore `numerical`.  Tate's
good/odd-multiplicative branches are complete; unsupported wild additive
branches are rejected.  Classical 2-isogeny descent is implemented for rational
2-torsion.  The general cubic-algebra descent is not: those rank upper bounds are
reported as unavailable.

## What this does **not** do

- Nothing in this package proves the Birch and Swinnerton-Dyer conjecture.
- A rank verdict is `undetermined` unless certified lower and upper bounds
  coincide.  The authorised catalogue rank is regression metadata, never a
  proof input.
- A ball containing zero does not prove vanishing.
- Numerical agreement of a BSD quotient with an integer proves only
  consistency unless a theorem supplies the missing equality.
- No rank `>= 2` curve has a complete C7 BSD certificate: current theorems do
  not prove finiteness of its full Tate--Shafarevich group.  In particular,
  `389.a1` stops at the rank-two barrier described in Chapter 47.
