# BRIEF — BUG-1129-validate-handoff-sweep Prevent pre-validation shipping

## Problem

An operator can trigger the post-merge sweep while validation is still in progress and `notes/handoff-validate.md` does not exist. `gh-sync.py ship` then performs irreversible GitHub card and milestone writes before repository state proves that validation completed, leaving the board, milestone, plan station, and surviving worktree in an invalid lifecycle order.

## Done when — by perspective

**operator** — I can rely on ship and the post-merge sweep refusing an unvalidated, non-exempt feature before any terminal GitHub or repository-station write, while leaving its worktree available for recovery. A fully direct feature that crosses no squad seam still ships normally.

**code maintainer** — I can rely on ship and INV-17 using one fail-closed exemption rule, with the focused refusal and all existing lifecycle cases protected by regression coverage.

## Success criteria

- SC-01 (operator): For a non-exempt feature with no `notes/handoff-validate.md`, `gh-sync.py ship` exits 1 with output that names validation as incomplete and names the missing note, moves no card, closes no milestone, and leaves the `plan.yaml` station unchanged. The focused regression is demonstrated failing before the fix and passing after it.
  verify: automated        evidence: integration
- SC-02 (operator): That refusal never prints `gh-sync: SKIP`; when reached through the post-merge sweep, the feature's worktree remains standing and no GitHub write occurs. The focused sweep regression is demonstrated failing before the fix and passing after it.
  verify: automated        evidence: integration
- SC-03 (code maintainer): A feature whose `plan.yaml` has a non-empty task list and every task declares `execution_mode: main-session-direct` ships without `notes/handoff-validate.md`; ship and check-state INV-17 use the single `handoff_policy.exempt_reason` predicate, an unreadable or malformed plan grants no exemption, and the existing INV-17 cases remain green. Focused shared-predicate cases are demonstrated failing before the fix and passing after it.
  verify: automated        evidence: integration, unit
- SC-04 (code maintainer): Every existing ship, record, open, abandon, and post-merge sweep case remains green after validated-feature fixtures write `notes/handoff-validate.md` by default, while the refusal fixture explicitly omits it. The note-writing fixture assertion is demonstrated failing before migration and passing after it.
  verify: automated        evidence: integration

## Verification gaps

- none; unit and integration both have active runners for the Python and fixture surfaces this patch touches.

## Constraints

- DEC-174 BLOCKS team execution of this enforcement-layer change and its gate-facing tests; implementation and focused verification are main-session-direct.
- DEC-225 SUPPLIES the patch lane: this BRIEF is at most 120 lines, the plan has exactly one bugfix task, and there is no plan panel or goal-check.
- DEC-232 SUPPLIES the seven exact `{path, quote}` task anchors and the plan-exit resolver; future anchors name the text the implementation must create.
- The guard belongs in `cmd_ship` before its first irreversible GitHub write, uses `die()` exit 1 rather than `skip()`, and leaves the plan station untouched on refusal.
- `handoff_policy.exempt_reason` preserves check-state INV-17's current three-condition all-direct predicate and fails closed when `plan.yaml` cannot be read or parsed.
- Issue 1129 is open and reopened because its earlier branch-only shell fix never landed; it is neither fixed nor superseded.

## Out of scope

- Whether the sweep should run on `git pull` at all (its trigger); INV-17's own wording.

## Approval

status: approved
approved-by: mruangutai
date: 2026-09-16
