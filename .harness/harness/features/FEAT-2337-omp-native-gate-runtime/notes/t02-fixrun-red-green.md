# T-02 follow-up RED/GREEN — fix-run QA receipts (DEC-255 deviation)

Builder: BuildFixRunReceipt (main-session-direct, DEC-174), in worktree W on top of 197e080b. The
binding ruling is `notes/answers-2026-11-22-fix-run-receipts.md`; BRIEF SC-06 carries the amendment
line. This is candidate source only: it says nothing about the installed control-plane hook. No git
writes and no formatters were run.

## Files changed

- `.claude/skills/harness/bin/validate-digest.py`
  - `_FIX_RUN = (?:^|-)fix-c[0-9]+-validator$`. This is feature-record.py's token-bounded `fix-`
    rule (`FIX_RUN`, which prune-run-evidence.py also uses) narrowed to the ruling's
    `fix-c<N>-validator`. No importable helper exists: feature-record.py has a hyphenated name and
    a heavy import, and it only matches the bare `fix-` token.
  - `_fix_run(run_id, payload)` classifies the run. `run_id` is the registered run from
    `digest_destination.registered_destination`. The mission is the dispatch-forwarded
    `harness_mission`, stripped the same way `_hook_options` strips it. If exactly one of them says
    "fix", it raises `_Untrusted` naming both values. The result is exit 2, `no trusted receipt
    location: the registered run … is / is not a fix run (fix-c<N>-validator) but the dispatch's
    harness_mission is …`, plus the repair commands. The digest, the receipts and anything the lead
    writes are never read for this.
  - `_receipt_context` sets `ctx["lineage"]` to `_fix_lineage` for a fix run and to the unchanged
    `_lineage` for every other run. `_kind_problems` calls `ctx["lineage"]` under the same
    per-(review, tested, feature_rel) cache.
  - `_fix_lineage(root, review, tested, feature_rel)` applies three checks:
    - `tested_commit` must equal `git -C <root> rev-parse --verify HEAD^{commit}`, using the same
      runtime-derived `authorization_root`.
    - `merge-base --is-ancestor review tested` must hold.
    - The working tree must be clean outside `<feature_rel>/`. `_dirty_paths` reads
      `status --porcelain=v1 -z --no-renames --untracked-files=all` and covers tracked changes
      plus untracked, unignored files.

    Intervening code commits are allowed.
  - `_receipt_refusal` prose now says "validate or fix run" and adds "in a fix run, at its clean
    HEAD descending from review_sha" to the Repair line. The layout and the `--kind <kind>
    --shard 1/1 --manifest …` repair command format are unchanged.
  - Main later asked for one more change after the T-03 builder found it. Since 06b60905, the
    default `tests/unit/test-code-grade.py` failed `validate-digest.py:check_qa_matrix_claim
    grade >= 4`: the function graded 3 (cc 8 / cog 8 / abc 20.1), and the production bar is 4.
    The fix splits it, with no allowlist entry. `_checked_receipts` now holds the
    `_Untrusted`/`_evidence_failures()` refusal mapping, and `check_qa_matrix_claim` keeps the
    trigger and the refusal. Behavior is unchanged: the `if family == "qa": return
    check_qa_matrix_claim(agent, obj, d)` anchor that `_bug919_red_mutant` keys on is untouched.
  - Unchanged: the validate-run rule (`_lineage`), coverage (`discover_expected`/`evidence_defects`
    at the tested commit), schema-1, exit-0, all-pass and empty-claim refusals.
- `tests/integration/test-validate-digest.py`
  - `_rx_record` gains `run_id=RX_RUN`.
  - New: `RX_FIX_RUN`, `RX_MISSION`, `_rx_code`, `_rx_dirt`, the `RX_FIX` table (13 rows),
    `_rx_fix_case` and `_rx_recorder`.
  - `run_feat2337_qa_receipt_cases` runs the `RX_FIX` rows after `RX_LINEAGE`. It is already
    registered in `--only` and in the default suite.
  - Every row uses real-runner receipts recorded under the registered fix or validate run's
    `qa/` in the committed git fixture.

**Interpretation, flagged for Main:** "clean working tree" exempts the feature's own directory. The
run's registration rewrites the tracked `feature.json`, and the receipts and notes live in that
directory. In the fixture, and in a real fix run, `feature.json` is tracked-dirty, so a literal
whole-tree check would refuse every fix run. The exemption is the same feature-directory exemption
the validate rule already grants. A row asserts it: "uncommitted note in its own feature directory
is accepted".

## RED: tests first, before any production edit

`python3 tests/integration/test-validate-digest.py --only run_feat2337_qa_receipt_cases`
exited 1 with `68/78 feat2337 cases passed. 10 FAILING.` (23.1 s). Failing rows:

    FAIL  a fix run whose code-changing descendant is HEAD is accepted         (refused: src/app.py outside the feature dir)
    FAIL  a fix run's uncommitted note in its own feature directory is accepted
    FAIL  a fix run whose tested_commit is not HEAD is refused                (missing "is not the checkout's HEAD")
    FAIL  a fix run on history divergent from the pin is refused              (missing "is not an ancestor")
    FAIL  a fix run with a modified tracked file is refused                   (missing "not clean", docs/readme.md)
    FAIL  a fix run with an untracked file is refused                         (missing "not clean", src/scratch.py)
    FAIL  a fix slug whose dispatch carries no mission is refused             (missing harness_mission)
    FAIL  a fix slug dispatched as validate is refused
    FAIL  a validate slug dispatched as fix is refused
    FAIL  a fix mission on a run id without the fix- token is refused

These new rows were already ok, because the old behavior satisfied them:
- "a fix run recorded at the exact pin is accepted" (control)
- "a validate-slug run with code changes is still refused"
- "a validate-slug run dispatched as validate with code changes is still refused"

All 65 pre-existing rows were ok.

## GREEN

    python3 tests/integration/test-validate-digest.py --only run_feat2337_qa_receipt_cases
      -> exit 0; "78/78 feat2337 cases passed." "ALL PASSED." (22.7 s; rerun after the
         check_qa_matrix_claim split: same, exit 0, 78/78)
    python3 tests/integration/test-validate-digest.py
      -> exit 0; "ALL PASSED." (32.2 s) — 133/133 CLI, 10/10 bug919, 78/78 feat2337, 2/2 #1185,
         2/2 #1883, 27/27 hook, 26/26 SC-07, 23/23 T-09, 37/37 T-04, bug2253 3 ok, sentinel ok
         (rerun after the split: exit 0, "ALL PASSED.", 71.3 s)
    python3 tests/unit/test-code-grade.py   (after the split)
      -> exit 0; "PASS test-code-grade", no FAIL line

## Grades (`code_grade.grade_source` over the working-tree files)

| file | function | grade (cc / cog / abc) |
|---|---|---|
| validate-digest.py | `_receipt_refusal` | 5 (3 / 2 / 7.5) |
| validate-digest.py | `_receipt_context` | 4 (2 / 2 / 16.9) |
| validate-digest.py | `_lineage` (unchanged) | 4 (6 / 2 / 8.4) |
| validate-digest.py | `_fix_run` | 4 (3 / 4 / 8.4) |
| validate-digest.py | `_dirty_paths` | 5 (3 / 0 / 3.7) |
| validate-digest.py | `_fix_lineage` | 4 (4 / 2 / 9.0) |
| validate-digest.py | `_kind_problems` | 4 (8 / 6 / 15.5) |
| validate-digest.py | `_checked_receipts` (split out) | 5 (4 / 3 / 7.8) |
| validate-digest.py | `check_qa_matrix_claim` (was 3) | 4 (4 / 2 / 9.4) |
| test-validate-digest.py | `_rx_record` | 5 (2 / 1 / 7.1) |
| test-validate-digest.py | `_rx_code` | 5 |
| test-validate-digest.py | `_rx_dirt` | 5 |
| test-validate-digest.py | `_rx_fix_case` | 4 (3 / 5 / 15.5) |
| test-validate-digest.py | `_rx_recorder` | 5 |
| test-validate-digest.py | `run_feat2337_qa_receipt_cases` | 4 (3 / 3 / 14.7) |

Every new or changed function grades 3 or above.

## Out of scope (per the ruling)

This change does not touch `_head_is_pin_error`. It still refuses a fix-run code-reviewer
re-verifying the fixed tip (DEC-255 open question, backlog #2356). A fix run therefore still cannot
pass end to end.
