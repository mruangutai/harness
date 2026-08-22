#!/usr/bin/env python3
"""SC-14 / REQ-08 — every .harness YAML must load under a real parser.

WHY THIS EXISTS: on 2026-08-03 all four gates were green while FOUR files in this
repo's own `.harness/` tree could not be parsed at all —

HISTORICAL RECORD, NOT CURRENT PATHS: the three paths below name each file as it
was named on 2026-08-03. FEAT-14 later closed the key set and converted that
format to JSON. The citations are deliberately left unrenamed - renaming them
would assert those files existed under a name they never had, and this docstring
is the evidence for why the gate exists.

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
import re
import os
import sys
import tempfile

# THE GATE MUST USE THE HARNESS'S OWN LOADER, not a more forgiving one.
#
# It used `yaml.safe_load`, which ACCEPTS a duplicated top-level key (last one wins)
# while `harness_yaml.load_str` REJECTS it. So a .harness file could pass this gate
# green and then break check-state.sh and both write hooks — a gate more permissive
# than the thing it protects is not a gate. Found by the goal-check.
try:
    import yaml
    import harness_yaml
except ModuleNotFoundError:
    print("test-harness-yaml-corpus: PyYAML is not importable from this interpreter "
          f"({sys.executable}).\n"
          "  install:  python3 -m pip install --user --break-system-packages pyyaml\n"
          "  This is REQUIRED, not optional (DEC-171 am.1) — there is no line-scan "
          "fallback by design.", file=sys.stderr)
    sys.exit(1)

REPO = os.environ.get("CLAUDE_PROJECT_DIR") or os.getcwd()


def _rel(p, root):
    """Report from the REPO root where possible, so a failure names which tree it
    came from — `.claude/skills/harness/teams/build.yaml`, not a bare `build.yaml`.
    Falls back to `root` for the throwaway fixture roots, which live outside REPO."""
    ap = os.path.abspath(p)
    try:
        if os.path.commonpath([ap, REPO]) == REPO:
            return os.path.relpath(ap, REPO)
    except ValueError:      # different drive / no common path
        pass
    return os.path.relpath(p, root)


NOTES_DIR_RE = re.compile(r"(?:^|/)features/[^/]+/notes(?:/|$)")


def _is_feature_notes(dirpath):
    """True for a feature's `notes/` directory, or anything under it.

    WHY THIS EXEMPTION EXISTS, measured 2026-08-21. FEAT-31's planning was hit by issue
    #628 — two `harness-pm` spawns wrote `plan.yaml` 63 seconds apart and a 14-task plan
    became a 1-task plan. The lost draft was recovered from transcripts and committed as
    EVIDENCE, named `notes/recovered-draft-14task-does-not-parse.yaml` because the recovery
    was imperfect and the file genuinely does not parse: line 85 carries prose with a
    colon-space inside a task's `intent`, which YAML reads as a mapping key — the exact
    failure mode this test exists to catch.

    So a file committed BECAUSE it is unparseable was read by the test asserting everything
    parses. The unit suite went red, and four of that feature's own tasks required it green
    — their `verify:` blocks were unsatisfiable from the moment the plan was signed.

    THE RULE, and it is about what a directory is FOR. `notes/` holds evidence, research and
    recovered artifacts: the place you put the broken thing you are documenting. Every other
    YAML in the tree is a live document that something reads — `plan.yaml`, `feature.json`'s
    siblings, `team-config.yaml`, the shipped team definitions — and those stay covered.
    Exempting `notes/` closes the CLASS: no future recovery of a malformed artifact can
    break the suite for the feature that recovered it.

    WHAT THIS GIVES UP, stated rather than discovered: a genuinely malformed YAML that
    matters, parked in a feature's `notes/`, is no longer caught here. Accepted, because
    nothing reads a file in `notes/` as a document — if something ever does, that consumer
    brings its own parse and its own error.

    Matched on the PATH SHAPE `features/<id>/notes/`, not on the bare name `notes`, so an
    unrelated `notes/` elsewhere in the tree stays covered.
    """
    norm = dirpath.replace(os.sep, "/")
    return NOTES_DIR_RE.search(norm) is not None


def scan(root):
    """-> (files_checked, [(relpath, message)]) for every *.yaml under <root>, recursively.

    SIGNATURE AND RETURN SHAPE ARE FIXED — six call sites below unpack `_, nb = scan(d)`.
    `root` is the tree to scan. It used to have `.harness` hard-coded onto it; that moved
    to the caller so a SECOND tree (the shipped team definitions) can be scanned by the
    same code path rather than by a parallel copy of it. A fixture root still works
    unchanged: the glob is recursive, so `<d>/.harness/probe.yaml` is still found.
    For per-root counts use `scan_roots`, which calls this once per root.

    WALK, NOT GLOB. `glob('<root>/**/*.yaml', recursive=True)` skips DOTTED directories,
    so it returns ZERO files for `.harness` and `.claude` alike — measured, not assumed:
    the recursive glob from this repo root matches 0 files while the tree holds 54.
    A gate that scans nothing passes vacuously, which is the exact failure the
    corpus-is-not-empty assertion below exists to catch."""
    paths = []
    for dirpath, _dirnames, filenames in os.walk(root):
        if _is_feature_notes(dirpath):
            continue
        for fn in filenames:
            if fn.endswith((".yaml", ".yml")):
                paths.append(os.path.join(dirpath, fn))
    paths.sort()
    bad = []
    for p in paths:
        try:
            harness_yaml.load_file(p)
        except harness_yaml.DuplicateKeyError as e:
            bad.append((_rel(p, root), str(e)))
        except harness_yaml.YamlParseError as e:
            e = e.original if getattr(e, "original", None) is not None else e
            # Name file, line and column — the diagnostics are the whole point. The
            # 2026-08-03 hunt was tractable ONLY because PyYAML reports a mark; a
            # bare "invalid YAML" would have cost hours across 10 files.
            mark = getattr(e, "problem_mark", None) or getattr(e, "context_mark", None)
            where = f":{mark.line + 1}:{mark.column + 1}" if mark else ""
            problem = getattr(e, "problem", None) or str(e).splitlines()[0]
            context = getattr(e, "context", None)
            detail = f"{context}, {problem}" if context else problem
            bad.append((_rel(p, root) + where, detail))
        except OSError as e:
            bad.append((_rel(p, root), f"unreadable: {e}"))
    return len(paths), bad


TEAMS_ROOT = os.path.join(".claude", "skills", "harness", "teams")
ROOTS = [".harness", TEAMS_ROOT]

# SC-05's second conjunct. The criterion reads "the directory's contents at completion
# are exactly TWO files — review.yaml (receiving the quoting fix) and build.yaml (born
# valid); gate-probe.yaml is deleted, so the count is two, not three" — and declares
# `verify: automated  evidence: unit`. Without this line only the PARSE half had an
# assertion: the `2` appeared in an f-string LABEL, which reports a number without
# asserting it. A criterion whose cited test does not cover what it claims is this
# repo's own charter defect, so the count is asserted rather than displayed.
# If a third team is legitimately added, this failing is the intended prompt to revisit
# SC-05 rather than to silently widen the number.
TEAMS_EXPECTED = 2


def scan_roots(roots):
    """-> ([(relpath, message)], {root: files_checked}) — `scan` once per root.

    Separate from `scan` so the per-root counts survive: a SECOND root that matches
    zero files must fail the not-empty assertion rather than hide behind the first
    root's total. `scan`'s own signature and two-value shape are unchanged."""
    bad, counts = [], {}
    for r in roots:
        n, b = scan(os.path.join(REPO, r))
        counts[r] = n
        bad.extend(b)
    return bad, counts


def _fixture(body):
    """A throwaway repo root containing .harness/probe.yaml with `body`."""
    d = tempfile.mkdtemp()
    os.makedirs(os.path.join(d, ".harness"))
    with open(os.path.join(d, ".harness", "probe.yaml"), "w", encoding="utf-8") as fh:
        fh.write(body)
    return d


def _fixture_teams(body):
    """A throwaway repo root containing a shipped-team-definition tree (SC-06).

    Deliberately NOT written into the real `.claude/skills/harness/teams/` — a gate
    proved by mutating the tree it guards is a gate that has been switched off for
    the duration of its own test."""
    d = tempfile.mkdtemp()
    sub = os.path.join(d, ".claude", "skills", "harness", "teams")
    os.makedirs(sub)
    with open(os.path.join(sub, "broken.yaml"), "w", encoding="utf-8") as fh:
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


# --- 1. the real corpus, across BOTH shipped trees ---------------------------
# `.claude/skills/harness/teams` is here because it was outside this gate's reach
# while both files in it failed to parse — the gate's own blind spot, not a new tree.
bad, counts = scan_roots(ROOTS)
total = sum(counts.values())
check(f"every shipped YAML parses ({total} files across {len(ROOTS)} roots: "
      + ", ".join(f"{r}={n}" for r, n in counts.items()) + ")", not bad,
      "\n".join(f"{p} — {m}" for p, m in bad))
# PER ROOT, not on the total: a second root matching zero files would otherwise pass
# vacuously behind the first root's count, which is the whole reason this exists.
for r, n in counts.items():
    check(f"the corpus under {r} is not empty (a scan that matches nothing passes vacuously)",
          n > 0, f"scanned {n} files under {os.path.join(REPO, r)}")
# SC-05's count conjunct — ASSERTED, not merely reported in a label above.
check(f"{TEAMS_ROOT} holds exactly {TEAMS_EXPECTED} team definitions (SC-05)",
      counts.get(TEAMS_ROOT) == TEAMS_EXPECTED,
      f"found {counts.get(TEAMS_ROOT)}: "
      f"{sorted(os.listdir(os.path.join(REPO, TEAMS_ROOT))) if os.path.isdir(os.path.join(REPO, TEAMS_ROOT)) else 'directory missing'}")

# --- 2..5. the detector must actually detect -------------------------------
# Each fixture is a real defect class observed in this repo on 2026-08-03.
NEGATIVE = [
    ("detects ` #` opening a comment inside a flow sequence (the team-config.yaml bug)",
     "writes: [a/BRIEF.md ## Approval, b/PLAN.md ## Approval]\nnext_key: 1\n"),
    ("detects `: ` inside a multi-line plain scalar (the FEAT-04/05 bug)",
     "pending:\n  - a note that says by me: presence 2\n    and continues here\n"),
    ("detects a sequence item opening with a backtick (the FEAT-03 bug)",
     "pending:\n  - `members: []` is rejected\n"),
    # Was labelled "duplicated top-level key" while feeding an UNCLOSED FLOW SEQUENCE —
    # so it tested a different defect entirely and the duplicate case was never covered.
    # That is why the loader mismatch above survived: the fixture agreed with the label,
    # not with the code.
    ("detects an unclosed flow sequence",
     "cost: 1\nfoo: [unclosed\n"),
    ("detects a DUPLICATED top-level key (safe_load accepts these; the harness does not)",
     "cost: 1\ncost: 2\n"),
    ("detects a duplicated key NESTED in a block (column-0 scans cannot see these)",
     "steps:\n  - id: s1\n    cost: 1\n    cost: 2\n"),
]
for name, body in NEGATIVE:
    d = _fixture(body)
    _, nb = scan(d)
    check(name, len(nb) == 1, f"expected exactly 1 finding, got {len(nb)}: {nb}")

# --- 5b. a feature's notes/ is exempt, and the SAME file outside it is not ---
# THE PAIR IS THE POINT. A case asserting only that notes/ is skipped would also pass if
# scan() stopped finding anything at all -- a gate switched off looks identical to a gate
# with a correct exemption. So the identical malformed body is written to TWO places and the
# assertions run in opposite directions.
_BAD = "steps:\n  - id: s1\n    intent: what it does NOT catch, stated: (a) presence\n"

_d = tempfile.mkdtemp()
_notes = os.path.join(_d, ".harness", "harness", "features", "FEAT-XX", "notes")
os.makedirs(_notes)
with open(os.path.join(_notes, "recovered-draft.yaml"), "w", encoding="utf-8") as _fh:
    _fh.write(_BAD)
_, _nb = scan(_d)
check("a malformed YAML in a feature's notes/ is EXEMPT (issue #628's recovered draft)",
      not _nb, _nb)

_d2 = tempfile.mkdtemp()
_live = os.path.join(_d2, ".harness", "harness", "features", "FEAT-XX")
os.makedirs(_live)
with open(os.path.join(_live, "plan.yaml"), "w", encoding="utf-8") as _fh:
    _fh.write(_BAD)
_, _nb2 = scan(_d2)
check("the IDENTICAL body one directory up, as plan.yaml, is still flagged -- so the "
      "exemption is scoped and the scan is not simply dead",
      len(_nb2) == 1, f"expected exactly 1 finding, got {len(_nb2)}: {_nb2}")

# And the exemption must be keyed on the PATH SHAPE, not the bare directory name: an
# unrelated notes/ that is not under features/<id>/ stays covered.
_d3 = tempfile.mkdtemp()
_other = os.path.join(_d3, ".harness", "notes")
os.makedirs(_other)
with open(os.path.join(_other, "thing.yaml"), "w", encoding="utf-8") as _fh:
    _fh.write(_BAD)
_, _nb3 = scan(_d3)
check("a notes/ NOT under features/<id>/ is still covered", len(_nb3) == 1,
      f"expected exactly 1 finding, got {len(_nb3)}: {_nb3}")

# --- 6. and must NOT cry wolf ------------------------------------------------
d = _fixture('writes: [".harness/features/*/BRIEF.md ## Approval", "x/**"]\n'
             'pending:\n  - >-\n    prose with a colon: and a `backtick`, safely folded\n')
_, nb = scan(d)
check("a correctly quoted/folded file is NOT flagged", not nb, nb)

# --- 6b. SC-06: the WIDENED root is really scanned, not just declared --------
# The defect this whole widening exists for: an unquoted `{{template}}` opening a flow
# sequence. Both shipped team files failed exactly this way at 635ef14 while this gate
# reported green, because it could not see the directory at all.
d = _fixture_teams("outputs: [a/{{x}}/b]\nnext_key: 1\n")
_, nb = scan(d)
check("detects a broken team definition under .claude/skills/harness/teams (SC-06)",
      len(nb) == 1, f"expected exactly 1 finding, got {len(nb)}: {nb}")

# --- 7. the message has to be actionable ------------------------------------
d = _fixture("writes: [a ## b, c]\nnext: 1\n")
_, nb = scan(d)
has_mark = bool(nb) and ":" in nb[0][0].split("probe.yaml")[-1]
check("a finding names file:line:column, not just 'invalid'", has_mark,
      nb[0] if nb else "no finding produced")

print(f"\n{ran - fails}/{ran} checks passed." if fails == 0 else f"\n{fails} of {ran} FAILING.")
sys.exit(1 if fails else 0)
