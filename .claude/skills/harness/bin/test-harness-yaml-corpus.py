#!/usr/bin/env python3
"""SC-14 / REQ-08 — every .harness YAML must load under a real parser.

WHY THIS EXISTS: on 2026-08-03 all four gates were green while FOUR files in this
repo's own `.harness/` tree could not be parsed at all —

  .harness/team-config.yaml:18   ` ##` opens a comment even inside a `[...]` flow
                                 sequence, so the `[` never closed and the document
                                 DIED AT LINE 23. Every key from `orchestrator:`
                                 onward — the whole team roster — was unreachable.
  FEAT-03/feature.yaml:97        a sequence item opening with a backtick, a YAML
                                 reserved indicator.
  FEAT-04/feature.yaml:77        `re-verified by me: presence 2` — a `: ` inside a
  FEAT-05/feature.yaml:55        multi-line plain scalar is read as a mapping key.

One root cause: unquoted prose in plain scalars. Six hand-rolled line scanners read
these happily for months because none of them had to close a bracket or resolve a
key. The first real parser refused them.

`FEAT-05/feature.yaml` was written the SAME DAY by an agent, so this is live
production of invalid YAML, not historical debt. A repair without a gate means the
next run reintroduces it (DEC-171/DEC-173 lineage; REQ-08, SC-14).

THE NEGATIVE CASES ARE NOT DECORATION. An always-green validity gate is
indistinguishable from no gate, so `case_detects_*` below feed this checker known-bad
fixtures and REQUIRE it to complain. Delete the corpus and cases 2-5 still fail if the
detector stops detecting. That is deliberate: it is the one property a validity gate
cannot self-report.
"""
import glob
import os
import sys
import tempfile

try:
    import yaml
except ModuleNotFoundError:
    print("test-harness-yaml-corpus: PyYAML is not importable from this interpreter "
          f"({sys.executable}).\n"
          "  install:  python3 -m pip install --user --break-system-packages pyyaml\n"
          "  This is REQUIRED, not optional (DEC-171 am.1) — there is no line-scan "
          "fallback by design.", file=sys.stderr)
    sys.exit(1)

REPO = os.environ.get("CLAUDE_PROJECT_DIR") or os.getcwd()


def scan(root):
    """-> (files_checked, [(relpath, message)]) for every *.yaml under <root>/.harness."""
    base = os.path.join(root, ".harness")
    paths = sorted(glob.glob(os.path.join(base, "**", "*.yaml"), recursive=True))
    paths += sorted(glob.glob(os.path.join(base, "**", "*.yml"), recursive=True))
    bad = []
    for p in paths:
        try:
            with open(p, encoding="utf-8") as fh:
                yaml.safe_load(fh)
        except yaml.YAMLError as e:
            # Name file, line and column — the diagnostics are the whole point. The
            # 2026-08-03 hunt was tractable ONLY because PyYAML reports a mark; a
            # bare "invalid YAML" would have cost hours across 10 files.
            mark = getattr(e, "problem_mark", None) or getattr(e, "context_mark", None)
            where = f":{mark.line + 1}:{mark.column + 1}" if mark else ""
            problem = getattr(e, "problem", None) or str(e).splitlines()[0]
            context = getattr(e, "context", None)
            detail = f"{context}, {problem}" if context else problem
            bad.append((os.path.relpath(p, root) + where, detail))
        except OSError as e:
            bad.append((os.path.relpath(p, root), f"unreadable: {e}"))
    return len(paths), bad


def _fixture(body):
    """A throwaway repo root containing .harness/probe.yaml with `body`."""
    d = tempfile.mkdtemp()
    os.makedirs(os.path.join(d, ".harness"))
    with open(os.path.join(d, ".harness", "probe.yaml"), "w", encoding="utf-8") as fh:
        fh.write(body)
    return d


fails = 0
ran = 0


def check(name, ok, detail=""):
    # Counted, never a literal total in the summary: a frozen count is issue #5's
    # exact defect — it reddens (or lies) the moment a case is added.
    global fails, ran
    ran += 1
    if ok:
        print(f"ok    {name}")
    else:
        fails += 1
        print(f"FAIL  {name}")
        for line in str(detail).splitlines():
            print(f"      | {line}")


# --- 1. the real corpus ------------------------------------------------------
n, bad = scan(REPO)
check(f"every .harness YAML parses ({n} files scanned)", not bad,
      "\n".join(f"{p} — {m}" for p, m in bad))
check("the corpus is not empty (a glob that matches nothing passes vacuously)", n > 0,
      f"scanned {n} files under {os.path.join(REPO, '.harness')}")

# --- 2..5. the detector must actually detect -------------------------------
# Each fixture is a real defect class observed in this repo on 2026-08-03.
NEGATIVE = [
    ("detects ` #` opening a comment inside a flow sequence (the team-config.yaml bug)",
     "writes: [a/BRIEF.md ## Approval, b/PLAN.md ## Approval]\nnext_key: 1\n"),
    ("detects `: ` inside a multi-line plain scalar (the FEAT-04/05 bug)",
     "pending:\n  - a note that says by me: presence 2\n    and continues here\n"),
    ("detects a sequence item opening with a backtick (the FEAT-03 bug)",
     "pending:\n  - `members: []` is rejected\n"),
    ("detects a duplicated top-level key colliding under a real parser",
     "cost: 1\nfoo: [unclosed\n"),
]
for name, body in NEGATIVE:
    d = _fixture(body)
    _, nb = scan(d)
    check(name, len(nb) == 1, f"expected exactly 1 finding, got {len(nb)}: {nb}")

# --- 6. and must NOT cry wolf ------------------------------------------------
d = _fixture('writes: [".harness/features/*/BRIEF.md ## Approval", "x/**"]\n'
             'pending:\n  - >-\n    prose with a colon: and a `backtick`, safely folded\n')
_, nb = scan(d)
check("a correctly quoted/folded file is NOT flagged", not nb, nb)

# --- 7. the message has to be actionable ------------------------------------
d = _fixture("writes: [a ## b, c]\nnext: 1\n")
_, nb = scan(d)
has_mark = bool(nb) and ":" in nb[0][0].split("probe.yaml")[-1]
check("a finding names file:line:column, not just 'invalid'", has_mark,
      nb[0] if nb else "no finding produced")

print(f"\n{ran - fails}/{ran} checks passed." if fails == 0 else f"\n{fails} of {ran} FAILING.")
sys.exit(1 if fails else 0)
