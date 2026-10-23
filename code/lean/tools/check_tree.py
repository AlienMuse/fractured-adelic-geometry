#!/usr/bin/env python3
"""
tools/check_tree.py -- mechanical checks on the BSD Lean skeleton.

Lean and Mathlib are NOT installed in the authoring environment, so this script
is the only automated check the tree gets.  It is a lexical checker, not a type
checker.  It CANNOT tell you that the tree compiles, and passing it is very
weak evidence of anything.  What it does check:

  1. bracket balance -- (), [], {}, <> anonymous-constructor brackets -- and
     `namespace` / `end` pairing, per file, after stripping comments;
  2. every `sorry` sits on a line immediately below a comment
     `-- OBLIGATION: <id>`, and every such id appears in BSD/Ledger.lean;
     and every id in the ledger is used by exactly one `sorry`;
  3. no declaration name is declared twice anywhere in the tree
     (namespace-qualified);
  4. every `import` names either a module file that exists in this tree or a
     path beginning `Mathlib.`.

Usage:  python tools/check_tree.py            (run from code/lean)
Exit code 0 on success, 1 on any failure.
"""

from __future__ import annotations

import os
import re
import sys

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))

OPEN_TO_CLOSE = {"(": ")", "[": "]", "{": "}", "\u27e8": "\u27e9"}
CLOSE_TO_OPEN = {v: k for k, v in OPEN_TO_CLOSE.items()}

DECL_RE = re.compile(
    r"^\s*(?:@\[[^\]]*\]\s*)?"
    r"(?:private\s+|protected\s+|noncomputable\s+|partial\s+|unsafe\s+)*"
    r"(theorem|lemma|def|abbrev|structure|class|inductive|axiom|opaque|instance)\s+"
    r"([^\s:{(\[]+)"
)
NAMESPACE_RE = re.compile(r"^\s*namespace\s+(\S+)")
END_RE = re.compile(r"^\s*end\b\s*(\S*)")
SECTION_RE = re.compile(r"^\s*section\b\s*(\S*)")
IMPORT_RE = re.compile(r"^\s*import\s+(\S+)")
OBLIGATION_RE = re.compile(r"--\s*OBLIGATION:\s*(\S+)")


def lean_files():
    out = []
    for base, _dirs, files in os.walk(ROOT):
        if os.sep + "tools" in base or os.sep + ".lake" in base:
            continue
        for f in sorted(files):
            if f.endswith(".lean"):
                out.append(os.path.join(base, f))
    return sorted(out)


def strip_comments(text: str) -> str:
    """Blank out /- ... -/ blocks (nesting-aware) and -- line comments,
    preserving line structure so line numbers stay valid."""
    out = list(text)
    i, n, depth = 0, len(text), 0
    while i < n:
        if depth == 0 and text.startswith("/-", i):
            depth = 1
            out[i] = out[i + 1] = " "
            i += 2
            continue
        if depth > 0:
            if text.startswith("/-", i):
                depth += 1
                out[i] = out[i + 1] = " "
                i += 2
                continue
            if text.startswith("-/", i):
                depth -= 1
                out[i] = out[i + 1] = " "
                i += 2
                continue
            if text[i] != "\n":
                out[i] = " "
            i += 1
            continue
        if text.startswith("--", i):
            j = text.find("\n", i)
            j = n if j < 0 else j
            for k in range(i, j):
                out[k] = " "
            i = j
            continue
        if text[i] == '"':
            out[i] = " "
            i += 1
            while i < n and text[i] != '"':
                if text[i] == "\\":
                    out[i] = " "
                    i += 1
                    if i < n:
                        out[i] = " "
                        i += 1
                    continue
                if text[i] != "\n":
                    out[i] = " "
                i += 1
            if i < n:
                out[i] = " "
                i += 1
            continue
        i += 1
    return "".join(out)


def check_brackets(path, code, errors):
    stack = []
    for lineno, line in enumerate(code.splitlines(), 1):
        for ch in line:
            if ch in OPEN_TO_CLOSE:
                stack.append((ch, lineno))
            elif ch in CLOSE_TO_OPEN:
                if not stack:
                    errors.append(
                        "%s:%d: closing %r with nothing open" % (path, lineno, ch)
                    )
                    return
                op, oln = stack.pop()
                if OPEN_TO_CLOSE[op] != ch:
                    errors.append(
                        "%s:%d: closing %r does not match %r opened at line %d"
                        % (path, lineno, ch, op, oln)
                    )
                    return
    if stack:
        op, oln = stack[-1]
        errors.append("%s: %r opened at line %d never closed" % (path, op, oln))


def check_namespaces(path, code, errors):
    stack = []
    for lineno, line in enumerate(code.splitlines(), 1):
        m = NAMESPACE_RE.match(line)
        if m:
            stack.append(("namespace", m.group(1), lineno))
            continue
        m = SECTION_RE.match(line)
        if m:
            stack.append(("section", m.group(1), lineno))
            continue
        m = END_RE.match(line)
        if m:
            name = m.group(1)
            if not stack:
                errors.append("%s:%d: `end %s` with nothing open" % (path, lineno, name))
                return
            kind, opened, oln = stack.pop()
            if kind == "namespace" and name != opened:
                errors.append(
                    "%s:%d: `end %s` closes `namespace %s` opened at line %d"
                    % (path, lineno, name, opened, oln)
                )
                return
            if kind == "section" and name not in ("", opened):
                errors.append(
                    "%s:%d: `end %s` closes `section %s` opened at line %d"
                    % (path, lineno, name, opened, oln)
                )
                return
    for kind, name, oln in stack:
        errors.append("%s: `%s %s` opened at line %d never closed" % (path, kind, name, oln))


def collect_decls(path, code, seen, errors):
    ns = []
    for lineno, line in enumerate(code.splitlines(), 1):
        m = NAMESPACE_RE.match(line)
        if m:
            ns.append(m.group(1))
            continue
        if END_RE.match(line):
            mm = END_RE.match(line)
            if ns and mm.group(1) == ns[-1]:
                ns.pop()
            continue
        m = DECL_RE.match(line)
        if not m:
            continue
        kind, name = m.group(1), m.group(2)
        if kind == "instance" and not name:
            continue
        if name.startswith("_"):
            continue
        full = ".".join(ns + [name]) if ns else name
        if full in seen:
            errors.append(
                "duplicate declaration %s: %s:%d and %s"
                % (full, path, lineno, seen[full])
            )
        else:
            seen[full] = "%s:%d" % (path, lineno)


def main():
    files = lean_files()
    errors = []
    warnings = []

    rel = lambda p: os.path.relpath(p, ROOT).replace("\\", "/")
    module_names = set()
    for p in files:
        r = rel(p)
        module_names.add(r[:-5].replace("/", "."))

    seen_decls = {}
    sorry_sites = []          # (module, lineno, obligation-id or None)

    for p in files:
        raw = open(p, encoding="utf-8").read()
        code = strip_comments(raw)
        check_brackets(rel(p), code, errors)
        check_namespaces(rel(p), code, errors)
        collect_decls(rel(p), code, seen_decls, errors)

        raw_lines = raw.splitlines()
        code_lines = code.splitlines()
        for i, cline in enumerate(code_lines):
            if re.search(r"\bsorry\b", cline):
                prev = raw_lines[i - 1] if i > 0 else ""
                m = OBLIGATION_RE.search(prev)
                sorry_sites.append((rel(p), i + 1, m.group(1) if m else None))

        for lineno, line in enumerate(raw.splitlines(), 1):
            m = IMPORT_RE.match(line)
            if not m:
                continue
            mod = m.group(1)
            if mod.startswith("Mathlib.") or mod == "Mathlib":
                continue
            if mod in module_names:
                continue
            errors.append(
                "%s:%d: import %s resolves to no module in this tree and is "
                "not a Mathlib path" % (rel(p), lineno, mod)
            )

    ledger_path = os.path.join(ROOT, "BSD", "Ledger.lean")
    ledger_ids = []
    if os.path.exists(ledger_path):
        ltext = open(ledger_path, encoding="utf-8").read()
        ledger_ids = re.findall(r'id\s*:=\s*"([^"]+)"', ltext)
    else:
        errors.append("BSD/Ledger.lean not found")

    dups = {x for x in ledger_ids if ledger_ids.count(x) > 1}
    for d in sorted(dups):
        errors.append("ledger: duplicate obligation id %s" % d)

    for mod, lineno, oid in sorry_sites:
        if oid is None:
            errors.append(
                "%s:%d: `sorry` with no `-- OBLIGATION: <id>` comment above it"
                % (mod, lineno)
            )
        elif oid not in ledger_ids:
            errors.append(
                "%s:%d: obligation id %s is not registered in BSD/Ledger.lean"
                % (mod, lineno, oid)
            )

    used = [oid for _m, _l, oid in sorry_sites if oid]
    for oid in ledger_ids:
        c = used.count(oid)
        if c == 0:
            errors.append("ledger: obligation %s has no corresponding `sorry`" % oid)
        elif c > 1:
            errors.append("ledger: obligation %s is claimed by %d sorries" % (oid, c))

    print("BSD Lean skeleton -- lexical self-check")
    print("root: %s" % ROOT)
    print("")
    print("files scanned: %d" % len(files))
    for p in files:
        n = sum(1 for _ in open(p, encoding="utf-8"))
        print("  %-32s %4d lines" % (rel(p), n))
    print("")
    print("declarations found (namespace-qualified): %d" % len(seen_decls))
    print("sorry occurrences: %d" % len(sorry_sites))
    for mod, lineno, oid in sorry_sites:
        print("  %-28s line %-5d %s" % (mod, lineno, oid or "<UNLABELLED>"))
    print("")
    print("ledger entries: %d" % len(ledger_ids))
    print("")

    if warnings:
        print("WARNINGS")
        for w in warnings:
            print("  " + w)
        print("")

    if errors:
        print("FAILED -- %d problem(s)" % len(errors))
        for e in errors:
            print("  " + e)
        return 1

    print("OK -- all lexical checks passed.")
    print("")
    print("This says NOTHING about whether the tree type-checks.  Lean and")
    print("Mathlib are not installed here and the tree has never been built.")
    return 0


if __name__ == "__main__":
    sys.exit(main())
