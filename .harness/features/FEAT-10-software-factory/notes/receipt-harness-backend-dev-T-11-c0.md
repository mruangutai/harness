# Receipt — harness-backend-dev — T-11 — c0

## Task
T-11: Add the shared CLI contract module and its unit test (D-08).

## TDD sequence
1. Wrote `.claude/skills/harness/bin/test-factory-cli.py` first, importing `factory_cli`
   which did not yet exist.
2. RED, watched it fail for the right reason (`ModuleNotFoundError: No module named
   'factory_cli'`, exit 1) — not a wrong-assertion failure.
3. Wrote `.claude/skills/harness/bin/factory_cli.py` to satisfy the contract.
4. GREEN: `python3 .claude/skills/harness/bin/test-factory-cli.py` — 32/32 checks pass,
   exit 0.
5. Advisor review flagged two coverage gaps against the intent text and closed them
   before returning:
   - `FACTORY_DEBUG` previously only had a hint-text assertion (the string
     `"FACTORY_DEBUG"` appears in the stderr line regardless of the env var). Added a
     pair of cases that set/unset the env var and assert the traceback itself is
     present/absent. Confirmed this pair is load-bearing: reverting `factory_cli.py`'s
     `if os.environ.get("FACTORY_DEBUG"):` guard to an unconditional
     `traceback.print_exc()` fails 2 checks (verified by temporarily mutating the file
     and re-running, then restoring it — restored file re-verified green).
   - The em dash in `body()`/`message()` was checked only against a literal written in
     the same sitting as the implementation. Added a check that reads the actual
     codepoint out of `plan.yaml`'s D-08 intent text (independent source of truth) and
     asserts `body()` emits that same U+2014, not a hyphen or en dash.

## Files touched
- `.claude/skills/harness/bin/factory_cli.py` (new)
- `.claude/skills/harness/bin/test-factory-cli.py` (new)
- `.claude/skills/harness/bin/run-unit-tests.sh` — appended `"test-factory-cli.py"` to the
  `UNIT_SCRIPTS` array (line 58 at task start). Nothing else in this file was touched;
  the pre-existing unrelated diff in it (root-resolution rewrite, extra `INTEGRATION_SCRIPTS`
  entries `test-gen-omp-agents.py`/`test-omp-reviewer-guard.py`) was already present in the
  working tree before this run and is left exactly as-is.

## verify: — run verbatim from repo root

Command (verbatim, cross-checked against `plan.yaml` T-11 lines 192-193 before running —
matches exactly):

```
.claude/skills/harness/bin/run-unit-tests.sh --kind unit > /tmp/v-t11.txt 2>&1; s=$?; grep -q "^PASS test-factory-cli.py$" /tmp/v-t11.txt && [ "$s" -eq 0 ]
```

Compound command exit status (`echo $?` immediately after): `0`

Full contents of `/tmp/v-t11.txt`:

```
ok    every shipped YAML parses (115 files across 2 roots: .harness=113, .claude/skills/harness/teams=2)
ok    the corpus under .harness is not empty (a scan that matches nothing passes vacuously)
ok    the corpus under .claude/skills/harness/teams is not empty (a scan that matches nothing passes vacuously)
ok    .claude/skills/harness/teams holds exactly 2 team definitions (SC-05)
ok    detects ` #` opening a comment inside a flow sequence (the team-config.yaml bug)
ok    detects `: ` inside a multi-line plain scalar (the FEAT-04/05 bug)
ok    detects a sequence item opening with a backtick (the FEAT-03 bug)
ok    detects an unclosed flow sequence
ok    detects a DUPLICATED top-level key (safe_load accepts these; the harness does not)
ok    detects a duplicated key NESTED in a block (column-0 scans cannot see these)
ok    a correctly quoted/folded file is NOT flagged
ok    detects a broken team definition under .claude/skills/harness/teams (SC-06)
ok    a finding names file:line:column, not just 'invalid'

13/13 checks passed.
PASS test-harness-yaml-corpus.py
ok    hard-wrapped prose is ONE paragraph
ok    a blank line still separates paragraphs
ok    bold straddling a wrap boundary still renders
ok    a table becomes a table, in its own scroll container
ok    a RAGGED row is padded, never shifted left
ok    an over-long row is truncated to the header width
ok    a pipe line with NO separator row is prose, not a table
ok    asterisks inside backticks are not emphasis
ok    a bare underscore in an identifier is not emphasis
ok    a wrapped list item stays one item
ok    a numbered list is an ol
ok    an HTML comment is authoring metadata, not body prose
ok    a fenced block is escaped, not interpreted
ok    headings keep their level and get an anchor
ok    every emitted tag is balanced

15/15 checks passed.
PASS test-render-brief.py
ok    (1) review.yaml is {code, qa, security, ui} and qa is gate-only (persona: qa, mutates_repo: false) — SC-04, MF-1
ok    (2) build.yaml parses, name: build, lead: eng-lead — SC-07
ok    (3) build.yaml is hosted by a lead whose squad is Engineering, so the team is single-squad by construction — SC-07, DEC-118
ok    (4) the Engineering squad covers the personas FEAT-03's eng build runs actually used {dev-ops, backend-dev} — SC-08
ok    (5) harness/SKILL.md has a line naming both `build` and DEC-118 — SC-09
ok    (6) the placeholder literal occurs exactly once across bin/, and both consumers reference PLACEHOLDER_UNSET — SC-02
ok    (7) SPEC §13 has a `build` row whose conducted-by cell matches build.yaml's lead — SC-10
ok    (8) harness/SKILL.md names the blocking qa gate: `test_matrix` present and qa+validator+loop_back within 8 consecutive lines — SC-14, issue #24
ok    (9) the panel set agrees across SPEC's ship-feature row, SPEC's review row and the shipped review.yaml — SC-15
ok    (10) test-check-state.py still carries T-01's INV-6 fixtures (`review_sha: none` >= 2, `review_sha: 1ce886a` >= 1) — SC-01

10/10 checks passed.
PASS test-team-catalog.py
ok    run(): fn returning normally leaves exit 0
ok    run(): success writes nothing to stdout
ok    run(): success writes nothing to stderr
ok    run(): unhandled KeyError exits 2, not 1
ok    run(): unhandled KeyError leaves stdout empty
ok    run(): unhandled KeyError stderr mentions FACTORY_DEBUG
ok    run(): fn calling sys.exit(1) still exits 1
ok    run(): fn calling sys.exit(3) still exits 3
ok    run(): expected exception produces the preformed line, no prefix duplication
ok    run(): expected exception has no 'unexpected failure' text
ok    run(): expected exception exits 2
ok    run(): FACTORY_DEBUG=1 prints a traceback after the hint line
ok    run(): without FACTORY_DEBUG set, no traceback is printed
ok    message(): renders the five parts in order with the em dash
ok    body(): builds 'what: value — next_step'
ok    plan.yaml's D-08 intent actually uses U+2014 (source of truth for 'em dash')
ok    body(): the dash emitted is U+2014, not a hyphen or en dash
ok    payload(): writes exactly one stdout line
ok    payload(): that line parses as json.loads
ok    payload(): writes nothing to stderr
ok    payload(): a plain string raises TypeError
ok    nothing_to_do(): writes nothing to stdout
ok    nothing_to_do(): writes to stderr
ok    nothing_to_do(): exits 1 (EXIT_NOTHING), not an error
ok    EXIT_OK == 0
ok    EXIT_NOTHING == 1
ok    EXIT_REFUSED == 2
ok    EXIT_RACE == 3
ok    refuse(): exits EXIT_REFUSED
ok    refuse(): stdout stays empty
ok    refuse(): stderr carries message()
ok    lost_race(): exits EXIT_RACE
ok    lost_race(): stdout stays empty

ok: 0 failing check(s).
PASS test-factory-cli.py
```

## Sanity: `--kind all`
Not part of the declared verify, run only to confirm this diff (which touches only
`UNIT_SCRIPTS`) does not disturb the integration suite: `run-unit-tests.sh --kind all`
exits `0`, all scripts including `test-omp-reviewer-guard.py` (last in the list) report
`ALL PASS` / `PASS`.

## Notes on scope
- No other factory module was created. `factory_gh.py` (T-03) and `factory_config.py`
  (T-02) are untouched, unread beyond what plan.yaml quotes.
- `.harness/factory/fleet.yaml` was not edited.
- `factory_cli.py` imports nothing from any other factory module, has no side effects on
  import, and has no `if __name__ == "__main__"` entry point, per the intent block.
