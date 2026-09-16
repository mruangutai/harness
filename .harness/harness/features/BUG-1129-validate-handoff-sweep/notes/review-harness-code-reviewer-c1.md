# Code review — BUG-1129 — c1 — 499eaf0b

## BLUF

PASS. Stage 1 spec compliance passed before Stage 2 began. The full pinned T-01 diff is traceable to SC-01–SC-04, both ledgered file amendments are relevant, every c0 code/consolidated finding is closed, and the implementation remains fail-closed before irreversible writes.

## Stage 1 — spec compliance (completed first)

- **SC-01 — satisfied.** `cmd_ship` refuses with exit 1 before body posting or any later write and names both `validation incomplete` and the exact missing note (`.claude/skills/harness/bin/gh-sync.py:2209-2218`). The focused case now binds the phrase, an empty whole-GitHub write boundary (including the supplied body/comment path), and byte-identical `plan.yaml` plus exact station preservation (`tests/integration/test-gh-sync-ship.py:457-495`). This closes the c0 code finding and consolidated GC-01/GC-02.
- **SC-02 — satisfied.** The focused ship case rejects `gh-sync: SKIP` and proves no GitHub write (`tests/integration/test-gh-sync-ship.py:480-490`); the real sweep case proves the refusal is surfaced and the worktree remains standing (`tests/integration/test-post-merge-sweep.py:577-612`). The pre-fix incident red remains recorded in `notes/receipt-main-session-T-01-fail-first.md`.
- **SC-03 — satisfied.** Ship and INV-17 call the single `handoff_policy.exempt_reason` predicate (`.claude/skills/harness/bin/gh-sync.py:2211-2213`; `.claude/skills/harness/bin/check-state.py:1196-1199`). Its plan-read and task-shape misses deny exemption (`.claude/skills/harness/bin/handoff_policy.py:36-68`). The new unit cases cover the one exempt shape and absent, malformed, non-mapping, empty/non-list tasks, malformed/missing-mode, team, mixed, and unreadable shapes (`tests/unit/test-handoff-policy.py:43-81`); the verb-level malformed-plan case also proves refusal, diagnostic, and no write (`tests/integration/test-gh-sync-ship.py:497-513`). The recorded fail-open mutant reddens these assertions (`notes/receipt-main-session-T-01-fail-first.md`, Arm 5). This closes consolidated GC-03.
- **SC-04 — satisfied.** `stage_ship` writes a structurally valid note by default and the refusal opts out explicitly (`tests/integration/gh_sync_support.py:61-69,789-814`; `tests/integration/test-gh-sync-ship.py:457-462`). The fixture-contract assertion binds all required sections (`tests/integration/test-gh-sync-ship.py:515-528`) and its pre-migration red is recorded in the fail-first receipt Arm 4. This closes consolidated GC-04.
- **Amendments and scope.** `tests/integration/test-hooks-install.py` is the ledgered validated-terminal-fixture migration serving SC-04; `tests/unit/test-handoff-policy.py` is the ledgered fail-closed shared-predicate coverage serving SC-03. Both are signed T-01 scope and independently relevant, not scope creep. All other production/test changes serve SC-01–SC-04; feature records carry the approved patch. There are no `decisions:` entries and no `[harness:human]` commits in the reviewed range.

Stage 1 therefore passed; Stage 2 follows.

## Stage 2 — code quality

The full pinned diff was assessed for correctness, silent failure, fail-open behavior, ordering, and codebase conventions. Missing/unreadable/malformed plans deny exemption rather than fabricate one; malformed task entries and partial/mixed direct modes also deny it. The refusal is before `post_body_path`, record loading, comment posting, board mutation, milestone closure, and station recording. The shared predicate is a real two-consumer seam and removes the former duplicated policy. No substantive defect survives.

`code-grade.py --base 142026456c64c80c3dd3aa776636dadbc0e21881 --head 499eaf0b9c1eb04e0f51dcfec47fab9ea50abd54` reported 11 passing changed functions, with no `SEVERITY` and no `REASON REQUIRED`; `code_grade: pass`. Per dispatch, no formatter, linter, build, or test suite was run by this reader; QA owns exactly the two matrix commands.

## Prior-finding disposition

- c0 code finding (SC-01 wording and exact station preservation): **closed** by the focused assertions above.
- Consolidated GC-01 (diagnostic): **closed**; GC-02 (whole GitHub write boundary): **closed**; GC-03 (fail-closed predicate/verb evidence): **closed**; GC-04 (fixture fail-first evidence): **closed**.
- c0 security and UI reviews had no findings; the c1 changes add tests/evidence only and introduce no new production boundary or rendered surface.

```yaml
VERDICT: PASS
DIGEST:
  headline: "Stage 1 passes before Stage 2: both amended T-01 test files are relevant, all c0 code/consolidated findings are closed, and the pinned diff is fail-closed and clean."
  severity_max: none
  findings: []
  must_fix: []
  spec_violations: []
  code_grade: pass
  reviewed: "142026456c64c80c3dd3aa776636dadbc0e21881..499eaf0b9c1eb04e0f51dcfec47fab9ea50abd54"
  human_commits_in_scope: []
  open_questions: []
  files_touched:
    - .harness/harness/features/BUG-1129-validate-handoff-sweep/notes/review-harness-code-reviewer-c1.md
  expertise_update: []
artifact: /Users/molchairuangutai/GitHub/harness/.claude/worktrees/harness/BUG-1129-validate-handoff-sweep/.harness/harness/features/BUG-1129-validate-handoff-sweep/notes/review-harness-code-reviewer-c1.md
```
