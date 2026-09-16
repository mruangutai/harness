# Code review — BUG-1129 — df871448

## BLUF

FAIL: T-01's implementation is spec-conformant on inspection, but its focused ship regression does not bind two explicit SC-01 outcomes. A regression can remove the required `validation incomplete` wording or mutate the plan station to any non-`done` value and the test remains green. Because Stage 1 does not pass, Stage 2 substantive review is intentionally not performed.

## Stage 1 — spec compliance

- **SC-01 — incomplete.** The guard is before the first ship write and calls `die()` with both required strings (`.claude/skills/harness/bin/gh-sync.py:2209-2218`); the fail-first receipt records the pre-fix card, milestone, and station mutations. The focused test checks exit 1 and `handoff-validate.md`, but not `validation incomplete` (`tests/integration/test-gh-sync-ship.py:469-473`). Its station assertion is `read_plan_station(featH) != "done"`, not equality with the pre-call value (`tests/integration/test-gh-sync-ship.py:481-482`). Thus the required regression protection is incomplete.
- **SC-02 — satisfied.** The focused test rejects `gh-sync: SKIP` (`tests/integration/test-gh-sync-ship.py:478-480`); the real sweep case checks the worktree remains, the refusal reaches output, and no milestone write occurs (`tests/integration/test-post-merge-sweep.py:591-602`).
- **SC-03 — satisfied on pinned behavior.** `check-state.py` and `gh-sync.py` both call the one `handoff_policy.exempt_reason` authority (`.claude/skills/harness/bin/check-state.py:1197`; `.claude/skills/harness/bin/gh-sync.py:2211`). The extracted predicate retains existence/mapping, non-empty list, mapping-task, and exact-mode fail-closed conditions (`.claude/skills/harness/bin/handoff_policy.py:39-68`); the all-direct ship case reaches `done` without a note (`tests/integration/test-gh-sync-ship.py:484-500`).
- **SC-04 — satisfied on diff shape.** `stage()` and `stage_ship()` now write the note by default, while the refusal alone passes `validated=False` (`tests/integration/gh_sync_support.py:61-69,119,789-812`; `tests/integration/test-gh-sync-ship.py:463-465`). Abandon and terminal sweep/hooks fixtures were migrated (`tests/integration/test-gh-sync-abandon.py:260,353`; `tests/integration/test-post-merge-sweep.py:182-192`; `tests/integration/test-hooks-install.py:197-207`). The ledgered hooks-install addition is aligned with SC-04, not scope creep.
- No pinned production/test change lacks an SC trace; the other changed paths are feature records required to carry this approved patch. No `[harness:human]` commit is in the reviewed range.

### Stage 1 finding (rank 1, T-01)

**Substance / medium / omission / SC-01.** If a future edit changes the refusal text from `validation incomplete` to a generic error, the focused test still passes because it only searches for `handoff-validate.md`. If an error path writes an arbitrary station such as `failed` instead of preserving the original `review`, the test also passes because it asserts only `!= done`. T-01 therefore does not provide the regression demonstration SC-01 requires. Fix the focused case to assert the mandated phrase and exact before/after station equality.

## Stage 2 — code quality

Not entered: the required Stage 1 compliance gate failed. The mandatory mechanical Python audit was still recorded for digest integrity: `code-grade.py --base 142026456c64c80c3dd3aa776636dadbc0e21881 --head df871448f55bcb7cf5804e5ffc9cca187a364131` reported 8 passing functions, no `SEVERITY` and no `REASON REQUIRED`; `code_grade: pass`. No tests, builds, linters, or formatters were run.

## Assessed and dismissed

- **Fail-open exemption drift:** dismissed; the helper is a direct extraction, and malformed/non-mapping/empty/mixed modes return no reason (`handoff_policy.py:39-68`).
- **Write ordering:** dismissed; the refusal precedes body posting, record loading effects, board mutation, milestone closure, and station recording (`gh-sync.py:2209-2224`).
- **`SKIP` accidentally permitting sweep removal:** dismissed; refusal uses `die`, and the sweep case binds worktree survival and surfaced refusal (`test-post-merge-sweep.py:591-599`).
- **Fixture gap:** dismissed beyond the SC-01 assertion defects above; shared validated fixtures default to writing the note, and the explicit negative fixture opts out.
- **Scope creep:** dismissed; the only task-file amendment is ledgered in `feature.json` and serves SC-04.

```yaml
VERDICT: FAIL
DIGEST:
  headline: "T-01 behavior is correctly ordered and fail-closed, but SC-01's focused regression does not assert the required wording or exact station preservation."
  severity_max: med
  findings:
    - kind: substance
      scope: task
      severity: med
      reader: code-reviewer
      summary: "T-01's focused ship test lets required SC-01 wording removal and arbitrary non-done station mutation pass."
      why: "With output changed to a generic error, or the review station corrupted to failed, assertions at test-gh-sync-ship.py:469-482 remain green although SC-01 is violated."
  must_fix:
    - "T-01: make the focused refusal case assert `validation incomplete` and exact pre-call/post-call plan station equality."
  spec_violations:
    - kind: omission
      path: tests/integration/test-gh-sync-ship.py
      ref: SC-01
  code_grade: pass
  reviewed: "142026456c64c80c3dd3aa776636dadbc0e21881..df871448f55bcb7cf5804e5ffc9cca187a364131"
  human_commits_in_scope: []
  open_questions: []
  files_touched:
    - .harness/harness/features/BUG-1129-validate-handoff-sweep/notes/review-harness-code-reviewer-c0.md
  expertise_update: []
artifact: /Users/molchairuangutai/GitHub/harness/.claude/worktrees/harness/BUG-1129-validate-handoff-sweep/.harness/harness/features/BUG-1129-validate-handoff-sweep/notes/review-harness-code-reviewer-c0.md
```
