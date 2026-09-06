# FEAT-55 — scoped re-check at 76ba5f41 (validator run 2026-09-05-30-validator's must_fix)

## BLUF
**Finding closed, measured, PASS.** The one gating finding — `write_factory.transform` GRADE 3
(cyclomatic 5, cognitive 4, ABC 20.5) at `cd6a3c0d` — is gone at `76ba5f41`. The extraction is a
literal, behavior-preserving move (no key/sort/default change). The corrected comment in
`probe-issue-types.py` now matches `gh-sync.py`'s actual call. All four suites plus the unit driver
are green. Nothing new found in the two-file delta.

## 1. Is the finding closed? — measured, not assumed
`env -u HARNESS_AGENT_TYPE python3 .claude/skills/harness/bin/code-grade.py --base eb9d044e --head 76ba5f41`:
- `PASSING: 95`; **0** lines match `SEVERITY: high`.
- The diffed report (base=eb9d044e, whole-feature range) lists `_factory_block` as new (GRADE 4,
  ABC 14.1, PASS) but omits `write_factory.transform` — the tool only lists new-or-worsened
  functions, so absence means non-worsening, not proof of the fixed value. I did not stop there.
- Direct un-diffed grade of the current file (`code-grade.py .claude/skills/harness/bin/factory_decompose.py`,
  HEAD = `76ba5f41`) gives both functions explicitly:
  - `write_factory.transform` — CYCLOMATIC 4, COGNITIVE 4, **ABC 9.0**, GRADE **4**, BAR 4, PASS
    (was cyclomatic 5, cognitive 4, ABC 20.5, GRADE 3 at `cd6a3c0d`).
  - `_factory_block` — CYCLOMATIC 2, COGNITIVE 0, **ABC 14.1**, GRADE **4**, BAR 4, PASS.
  - Confirms the remedy did not merely relocate the mass into an equally-failing helper: the
    helper itself clears bar 4, and the caller's ABC dropped from 20.5 to 9.0.
- `--base cd6a3c0d --head 76ba5f41` (remedy commit alone) lists exactly one function
  (`_factory_block`, new, GRADE 4, PASS) and nothing else — consistent with `transform` improving,
  not regressing.
- Remaining `SEVERITY: med` GRADE-2 findings (`classify_capability`, `case_a_b`…`case_k` in three
  test files) are pre-existing, already assessed at stage 1 and explicitly out of scope per this
  dispatch's non-goals. Not re-opened.

## 2. Is the extraction behaviour-preserving?
`git diff cd6a3c0d 76ba5f41 -- .claude/skills/harness/bin/factory_decompose.py` (full diff read,
not elided): the removed 12-line dict literal inside `transform` and the added `_factory_block`
body are **textually identical** — same six keys (`repo`, `parent`, `issues` sorted, `items`
sorted, `edges.parent` as `list(...)`, `edges.blocked_by` sorted, `typed` sorted), same
`factory.get("typed", {})` default, no added validation, no renamed key. The only change at the
call site is `doc["factory"] = {...}` → `doc["factory"] = _factory_block(factory)`. Confirmed pure
extraction.

## 3. Does the corrected comment now state what the code does?
`probe-issue-types.py:70-73` (at `76ba5f41`) now reads: "gh-sync.py's detect_issue_types no longer
appends `--repo` either (operator ruling F-02 / D-22): gh api has no `--repo` flag at all, so
gh-sync.py now calls `capability_query_args(repo)` bare, same as here."
Compared against the actual call site, `gh-sync.py:918`:
`r = subprocess.run([GH] + gh_issue_types.capability_query_args(repo), capture_output=True, text=True)`
— no `--repo` appended anywhere in that call. **Comment is accurate.**

## Suites (each run separately, own exit code, own `^FAIL ` count)
| Suite | exit | `^FAIL ` count |
|---|---|---|
| `tests/integration/test-factory-issue-types.py` | 0 | 0 |
| `tests/integration/test-factory-decompose.py` | 0 | 0 |
| `tests/integration/test-factory-integration.py` | 0 | 0 |
| `tests/unit/test-factory-gh.py` | 0 | 0 |
| `bash .claude/skills/harness/bin/run-unit-tests.sh` (captured `$?` right after) | 0 | 0 |

## Working tree
`git status --porcelain`:
```
 M .harness/harness/features/FEAT-55-issue-types-created-work/feature.json
```
Only feature-tracking metadata is dirty; no source file was touched by this segment (verified
read-only throughout — this reviewer's own read-only guard blocked two of my attempted `>`/`tee`
commands, confirming no accidental write occurred).

## Anything new in the two-file delta?
**Nothing new.** I looked at: the full `factory_decompose.py` diff (extraction body, call site),
the full `probe-issue-types.py` diff (comment only), the grader's numeric output for both
functions, and the corrected comment against the live `gh-sync.py` call site. No behavior change,
no new fail-open, no scope creep beyond the remedy the finding asked for.
