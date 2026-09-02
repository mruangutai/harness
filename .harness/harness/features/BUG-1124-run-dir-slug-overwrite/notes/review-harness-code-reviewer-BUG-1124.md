# Review — harness-code-reviewer — BUG-1124-run-dir-slug-overwrite (PR #1155)

reviewed: `8ff525e246ba3af9d69d08646e52be28d7546c47..749b90777c2a849a1e3352d2eac0d4a952c3f893`
(review_sha pinned to branch tip `749b9077`; merge-base with `origin/main` is `8ff525e2`)

## Stage 1 — spec compliance (issue #1124 + PR #1155 body)

The fix is scoped to exactly the two named files, entirely inside the `RE_STATE_YAML` branch
of `shape_problems` plus its tests. Every requirement in the PR description is met:

- Identity check (`run_id`), not a content/prefix compare — correctly avoids re-denying the
  DEC-154 checkpoint upsert. ✓ (`check-domain.sh:1437-1462`)
- Same `run_id` rewritten any number of times → allowed. ✓ tested `state-run-id-upsert-allowed`.
- Prior file with no `run_id` → allowed (nothing to compare). ✓ tested `state-no-prior-run-id-allowed`.
- First write to an empty run dir → allowed. ✓ tested `state-new-file-allowed`.
- Different `run_id` in a live run dir → denied, message names the collision and the fix
  ("write this cycle's state into a run directory of its own"). ✓ tested `state-run-id-collision`.
- RED-proof mutant (`state-run-id-collision-red`) excises exactly the new block between the
  `# Issue #1124` comment and the following `# T-17 / D-08` comment and confirms the same
  write goes from denied (exit 2) to allowed (exit 0) with the guard removed — genuinely
  exercises the new code, not a returncode coincidence.
- No scope creep: nothing touches `check-state.sh` (the sibling vocabulary sweep) or any
  other guard; that is correctly out of scope since #1124 is specifically about the
  write-time collision guard #1058 already patterns.

Stage 1: no violations.

## Stage 2 — code quality

### must_fix — fail-open on an unreadable prior `state.yaml` (`check-domain.sh:1437-1451`)

The new guard's own comment frames it as mirroring the `RE_RUN_DIGEST` guard (#1058) one
block above it (`check-domain.sh:1191-1207`). The digest guard explicitly denies when the
prior file exists but cannot be read:

```
except OSError:
    pass
...
if prior is None:
    out.append(_head("run digest already exists but cannot be read safely; "
                     "refusing a Write that could destroy its recorded content."))
```

The new state.yaml guard hits the identical `OSError` branch and does the opposite —
`prior_state` stays `None`/falsy, `if prior_state:` is skipped, and the function falls
through to the rest of `shape_problems` with **no finding appended at all**, so the write is
allowed:

```
except OSError:
    pass
if prior_state:
    ...                      # <- never runs; nothing replaces it
```

Concretely: a run directory whose `state.yaml` exists but cannot be opened right now
(permission bits stripped, a transient I/O error, or the file replaced by a directory — the
sibling guard's own regression fixture, `_feat50_digest_unreadable_case` at
`test-check-domain.py:3352`, constructs exactly this condition via `os.makedirs(path)`) is
treated as "nothing to compare against" rather than "cannot verify, so refuse." A write that
would in fact collide with a different run's checkpoint sails through unflagged in precisely
the condition class this defect (#1124) exists to close, and it is untested — no
`_bug1124_*` case exercises an unreadable prior file the way `_feat50_digest_unreadable_case`
does for digest.md.

This is not a hypothetical: the exact trigger is already proven constructible in this same
test file for the sibling guard. Fix: when `absolute_path is not None` and the file
`os.path.lexists`s but cannot be opened, deny (matching the digest guard's wording/precedent)
rather than silently falling through.

### should_fix / advisory — `run_feat50_artifact_integrity` grades 2 (informational, non-gating)

`code-grade.py --base 8ff525e2..749b9077` reports one record below its test-path bar (3):

```
PATH: test-check-domain.py  LINE: 3459  QUALNAME: run_feat50_artifact_integrity
CYCLOMATIC: 1  COGNITIVE: 0  ABC: 33.4  GRADE: 2  DRIVER: abc  BAR: 3  RESULT: FAIL  SEVERITY: med
```

Reasoned acceptance: the function is a flat orchestrator — cyclomatic 1, cognitive 0, no
branching or nesting at all. Its elevated ABC score comes entirely from the growing count of
fixture-setup and list-literal calls (Branches), which is the established shape of this
function across every prior FEAT-50/#1058 addition; this diff extends that same pattern with
5 more calls rather than introducing new structure. All five new `_bug1124_*` helper
functions it calls are separately graded and pass at grade 5 — the actual test logic lives
there, not in this aggregator. Grade 2 never blocks the build per policy; flagging for
awareness that the next addition to this list is a good point to switch it to a data-driven
table.

All other 6 changed functions (the new `_bug1124_*` helpers) grade 5/PASS.

No other Stage 2 findings — comment conventions, `_head()` usage, `str()`-coercion on both
`run_id` sides (T-17/D-08 convention), and PRE/`Write`-only gating all match the surrounding
file's established patterns.

## Verification run

`python3 test-check-domain.py` (working tree, unmodified) → all 5 new cases plus the
pre-existing 10 FEAT-50 cases pass: `15/15 FEAT-50 artifact-integrity cases passed.`

## code_grade

```
code_grade: grade_2
grade_2_reasons:
  - "run_feat50_artifact_integrity (test-check-domain.py:3459) is a flat, unbranching
     (cyclomatic 1, cognitive 0) orchestrator whose ABC score is driven entirely by the
     count of fixture/list-literal calls it makes, consistent with every prior FEAT-50
     addition to this same function; the 5 new calls this diff adds continue that
     established shape rather than adding new structure, and the logic under test lives
     in the separately-graded (grade 5) _bug1124_* helpers, not here."
```
