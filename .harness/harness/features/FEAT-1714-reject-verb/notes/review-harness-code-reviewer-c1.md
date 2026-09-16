# Pinned code review — FEAT-1714 c1

## BLUF

PASS with one non-gating medium specification note over `origin/main..8090ce0b0fd8eb9d12c63df83ef9cb45a7b38125` (53 paths). Both lifecycle branches fail closed. VAL-01..VAL-05 and ADV-01 are closed at the immutable pin. The scoped Python audit reports 40 PASSING and 0 FAIL.

All source citations below refer to pinned SHA `8090ce0b0fd8eb9d12c63df83ef9cb45a7b38125`.

## Stage 1 — spec compliance: PASS with advisory note

- **First sync:** with no recorded parent, `_source_reject_steps` uses `plan.yaml.source_issues`, comments and reseats each source ticket, and never closes or labels it (`gh-sync.py:1886-1900`). With neither parent nor source issue, reject refuses before station mutation (`gh-sync.py:1903-1920`). The orchestrator creates the station-only plan and writes the `none` station only after exit 0 (`harness/SKILL.md:48-74`). VAL-01 is closed.
- **Recorded parent:** close, comment, optional label and backlog are ordered in `_parent_reject_steps`; milestone follows, and numeric station recording occurs only after all steps return (`gh-sync.py:1873-1884,1903-1920,1932-1966`). SC-03's parent lifecycle is unchanged.
- **Failure ordering:** every required executed write completes or raises `_RejectHalt`; the first halt exits 1, reports landed/unrun work and cannot reach station recording. A failed station write also exits 1 (`gh-sync.py:1833-1871,1922-1966`). VAL-02 is closed.
- **SC-05 inspection:** the set is declared once as `("abandoned", "rejected")` (`factory_config.py:51`) and consumed by the domain, route, state, board, handoff, plan-write, GitHub and cleanup paths (`check-domain.py:1320`; `check-plan-routes.py:525,545`; `check-state.py:105-106`; `board_lifecycle.py:528`; `gh_board.py:174,240,274`; `handoff_done_when.py:277`; `plan-merge.py:239`; `gh-sync.py:138`; `worktree_terminal.py:413-417`).

**F-07 — med · substance · T-02.** A stale reason file can be confirmed without its text being displayed. `_reject_reason_file` builds the actual body, but the report renders only `disposition`, not the reason-bearing comment (`gh-sync.py:1813-1826,1873-1900`). This is a non-gating mismatch with T-02's exact-comment report detail.

## Stage 2 — code quality: PASS

Report and execution share one ordered `(description, action)` list (`gh-sync.py:1873-1920`). A miss blocks rather than fabricating success: the runner stops on the first required-write failure, while station recording sits after the completed list (`gh-sync.py:1932-1966`). The no-parent lookup either yields authoritative source-ticket steps or refuses (`gh-sync.py:1886-1920`). No blocking silent-failure, dangling-alias or duplicated terminal-vocabulary defect survives.

The regression covers label failure after irreversible work and asserts exit 1, landed/not-run reporting, no later writes and no station. It also covers the first-sync source-ticket disposition and preservation of source issues and drafted BRIEF (`test-gh-sync-abandon.py:685-780`).

## Code grade and prior dispositions

Command: `python3 .claude/skills/harness/bin/code-grade.py --base origin/main --head 8090ce0b0fd8eb9d12c63df83ef9cb45a7b38125`

Outcome: **40 PASSING, 0 FAIL**, matching the stated expectation. `_reject_judgement_errors` is grade 4 (VAL-03 closed); landed classifier helpers are grade 4 (VAL-04 closed); the split INV-44 wrapper is grade 5 and subcases meet the test bar (VAL-05 closed); `cmd_reject` is grade 4; `_landed_station_records` is grade 4 (ADV-01 closed). VAL-01 and VAL-02 are closed by the pinned behavior above.

The commit walk contains no `[harness:human]` commit. Before this note, `feature.json` was already modified in the worktree; code claims use the pin.

```yaml
VERDICT: PASS
DIGEST:
  headline: "Both reject branches fail closed and prior code-grade findings are resolved; exact-comment preview remains advisory."
  severity_max: med
  findings:
    - { id: F-07, kind: substance, scope: task, severity: med, reader: code-reviewer, task: T-02, summary: "Reject dry-run omits the exact reason-bearing comment required by T-02.", why: "A stale reason file can be confirmed without the operator seeing what will be published." }
  must_fix: []
  spec_violations:
    - { kind: mismatch, path: .claude/skills/harness/bin/gh-sync.py, ref: T-02 }
  code_grade: pass
  reviewed: "origin/main..8090ce0b0fd8eb9d12c63df83ef9cb45a7b38125"
  human_commits_in_scope: []
  open_questions: []
  files_touched:
    - /Users/molchairuangutai/GitHub/harness/.claude/worktrees/harness/FEAT-1714-reject-verb/.harness/harness/features/FEAT-1714-reject-verb/notes/review-harness-code-reviewer-c1.md
  expertise_update: []
artifact: /Users/molchairuangutai/GitHub/harness/.claude/worktrees/harness/FEAT-1714-reject-verb/.harness/harness/features/FEAT-1714-reject-verb/notes/review-harness-code-reviewer-c1.md
```
