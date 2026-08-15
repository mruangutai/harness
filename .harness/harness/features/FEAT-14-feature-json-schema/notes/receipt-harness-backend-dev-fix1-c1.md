# Receipt — harness-backend-dev — FEAT-14 fix1 (gh-sync.py atomic write + load guard)

## BLUF

Fixed. `save_recorded` is now atomic (mkstemp+fsync+os.replace, matching
`factory_decompose.py:142-186`'s `write_factory`), `load_recorded` now converges on
`json.load` (B-5) and turns an empty/unparseable/non-mapping `feature.json`, or a
non-mapping `github:` value, into a loud `SystemExit` instead of "nothing recorded".
Row-1 (absent file, or present with no `github` key) still returns the default rec —
the first-sync path is unbroken. B-14: a discriminating test for `_is_shipped` already
exists (`test-check-plan-routes.py` case_24, grep below); nothing built there.

## Files touched

- `.claude/skills/harness/bin/gh-sync.py` — `load_recorded` and `save_recorded`
  rewritten; `import tempfile` added.
- `.claude/skills/harness/bin/test-gh-sync.py` — T-06C's two YAML-comment fixtures
  rewritten as JSON (B-5 converged the reader; JSON has no comments to tolerate — this
  is a deliberate contract change, not a dropped assertion), plus new Part A/Part B
  cases.

## Mutation proof — revert-the-fix run, VERBATIM

Ran the new `test-gh-sync.py` (post-fix test file) against the PRE-FIX `gh-sync.py`
(worktree checked out at `0b33188`, disposable, then removed):

```
$ git worktree add <scratch>/wt-fix1 0b33188
$ cp .../test-gh-sync.py <scratch>/wt-fix1/.claude/skills/harness/bin/test-gh-sync.py
$ cd <scratch>/wt-fix1 && python3 .claude/skills/harness/bin/test-gh-sync.py
...
ok    fix1 B row1a: absent feature.json returns the default rec, does not raise
ok    fix1 B row1b: dict present with no github key returns the default rec
ok    fix1 B row2: 0 bytes on disk
FAIL  fix1 B row2: a 0-byte feature.json raises SystemExit, never loads as empty
      load_recorded returned instead of raising
FAIL  fix1 B row2 (a_list): a non-mapping document raises SystemExit
      load_recorded returned instead of raising
FAIL  fix1 B row2 (a_scalar): a non-mapping document raises SystemExit
      load_recorded returned instead of raising
FAIL  fix1 B row4 (github=a_string): a non-mapping github: value raises SystemExit
      load_recorded returned instead of raising
FAIL  fix1 B row4 (github=a_list): a non-mapping github: value raises SystemExit
      load_recorded returned instead of raising
FAIL  fix1 A: a failed save_recorded leaves feature.json byte-identical, never truncated
      before=b'{"feature_id": "F-atomic", "status": "Building"}' after=b'{\n  "feature_id": "F-atomic",\n  "status": "Building",\n  "github": {\n    "milestone": 9,\n    "parent": 40,\n    "parent_origin": "created",\n    "attached": [\n      "T-01"\n    ],\n    "issues": {\n      "T-01": '
ok    fix1 A: no leftover temp file after a failed save_recorded
ok    finding 2: save_recorded round-trips a feature.json with no github block yet
ok    finding 2: save_recorded round-trips a feature.json with an existing github block
ok    finding 2: save_recorded round-trips a feature.json with other keys present

6 FAILED
```
Exit code 1. Exactly the 6 new assertions failed — nothing else. `$WT` above stands for
the literal scratch worktree path; the actual commands used the literal absolute path
per the dispatch's hard constraint #4 (the write guard denies an unexpanded shell var).

Worktree removed afterward:
```
$ git worktree remove <scratch>/wt-fix1 --force
$ git status --porcelain -- .claude/skills/harness/bin/gh-sync.py .claude/skills/harness/bin/test-gh-sync.py
 M .claude/skills/harness/bin/gh-sync.py
 M .claude/skills/harness/bin/test-gh-sync.py
```
(only the two intended files carry a diff in the main checkout — the worktree left no
trace.)

## Green run, VERBATIM (post-fix, main checkout)

```
$ python3 .claude/skills/harness/bin/test-gh-sync.py
...
ok    fix1 B row1a: absent feature.json returns the default rec, does not raise
ok    fix1 B row1b: dict present with no github key returns the default rec
ok    fix1 B row2: 0 bytes on disk
ok    fix1 B row2: a 0-byte feature.json raises SystemExit, never loads as empty
ok    fix1 B row2 (a_list): a non-mapping document raises SystemExit
ok    fix1 B row2 (a_scalar): a non-mapping document raises SystemExit
ok    fix1 B row4 (github=a_string): a non-mapping github: value raises SystemExit
ok    fix1 B row4 (github=a_list): a non-mapping github: value raises SystemExit
ok    fix1 A: a failed save_recorded leaves feature.json byte-identical, never truncated
ok    fix1 A: no leftover temp file after a failed save_recorded
ok    finding 2: save_recorded round-trips a feature.json with no github block yet
ok    finding 2: save_recorded round-trips a feature.json with an existing github block
ok    finding 2: save_recorded round-trips a feature.json with other keys present

ALL PASSED
```
Exit code 0.

## Part B — three states proven individually (plus the fourth)

| State | Fixture | Result |
|---|---|---|
| **absent** | no `feature.json` at all | `load_recorded` returns the all-None default rec, does not raise (`fix1 B row1a`) |
| **present, dict, no `github` key** | `{"feature_id": "F2"}` | returns the default rec — the first-sync regression case (`fix1 B row1b`, and `T-06C` no-github-block case) |
| **present, empty (0 bytes)** | `open(...).close()` — the exact artifact the old truncating `open(p, "w")` produced | `SystemExit`, message contains "does not parse ... cannot be known" (`fix1 B row2`) |
| **present, non-mapping JSON** | `[1, 2]` / `"just a string"` | `SystemExit` (`fix1 B row2 (a_list/a_scalar)`) |
| **present, `github` key present but not a mapping** (the 4th state, not in the operator's table) | `{"github": "not-a-mapping"}` / `{"github": ["T-01", 41]}` | `SystemExit` (`fix1 B row4`) |
| **present, valid `github` mapping** | populated block incl. quoted `"7"` milestone | loads, `_opt_int` coerces the quoted milestone to `7` (`T-06C`) |

Each row is its own named assertion above, not a count — the first-sync path
(row 1a/1b) is proven to still return cleanly, not merely "not crash".

## Gates — real exit codes

| Gate | Exit |
|---|---|
| `run-unit-tests.sh` (default `--kind all`, both kinds) | `0` — all 25 suites `PASS`, including `test-gh-sync.py` |
| `test-gh-sync.py` standalone | `0` — `ALL PASSED` |
| `validate-feature-json.py` | `0` |
| `check-state.sh` | `0` — output is entirely pre-existing `note` lines (34), none new |
| `check-plan-routes.py` | `0` — `0 violation(s) across 10 plan(s)` (verbatim tail line) |

## B-14 — grep evidence, no refactor performed

```
$ grep -n "_is_shipped" .claude/skills/harness/bin/check-plan-routes.py
395:def _is_shipped(feature_dir):
568:            if _is_shipped(entry.path):

$ grep -n "_is_shipped" .claude/skills/harness/bin/test-check-plan-routes.py
872:    # above cannot reach, and it was a live crash: the first draft put `_is_shipped`'s
919:    # (harness_yaml.load_file -> json.dumps'd feature.json -> _is_shipped)
931:    # the document was actually parsed and _is_shipped actually consulted.
```
`test-check-plan-routes.py` case_24 (`:863-950`) exercises `_is_shipped` with four
malformed-document guards (sequence, bare scalar, status-is-a-list, mapping-with-no-
status) each asserted on exit code + clean stderr + the summary line together, PLUS a
paired eleven-key Done/Building end-to-end case (`:915-950`) that is the same
discrimination shape as `test-check-state.py`'s `case_g`: only the `status` field flips
the outcome (Done -> excluded from the plan count entirely, Building -> reached and
checked), proving the document is actually parsed and `_is_shipped` actually consulted,
not merely that the checker exits without crashing. A discriminating test already
exists. Nothing built here.

## Part B row-4 note (raised as open_question, non-blocking)

`github` present-but-not-a-mapping was not in the operator's three-row table. Treated it
as row 2 (loud error) per the dispatch's own instruction, and documented the choice in
`gh-sync.py`'s `load_recorded` docstring. Filed below for visibility since the operator
did not enumerate this state themselves.
