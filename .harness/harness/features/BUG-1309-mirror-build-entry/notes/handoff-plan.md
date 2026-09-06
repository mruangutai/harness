# Handoff — BUG-1309-mirror-build-entry, plan → build — written at 272968ff, seq-2

## Next

Nothing is dispatchable until the operator signs. The main session presents the four open panel
findings (PF-1aa3b36c, PF-6030c547, PF-8bfef7ee, PF-23f51fd8) plus the two disclosed decided
ambiguities (D-08's era/retention split, D-09's unpinned-repo block) in ONE batched signature
review, then runs `plan-merge.py sign-approval` on the plan. Only then does build entry run —
and build entry for THIS feature is the act the feature defines: signed approval, then
`gh-sync.py open`. First build segment is T-01 (the schema field) to harness-eng-lead;
T-04..T-08 are main-session-direct.

## Trust

- Plan loads, 9 tasks, 9 decisions, station plan, approval pending, source_issues [1390] — .harness/harness/features/BUG-1309-mirror-build-entry/plan.yaml in this worktree — verified-at 272968ff
- check-plan-routes.py exits 0, three declared DEC-174 deviation rows (T-04, T-06, T-07) — run at orchestrator tier — verified-at 272968ff
- All ten REQ traced; REQ-07 by T-02+T-05, REQ-09 by T-03+T-07 — plan.yaml traces: — verified-at 272968ff
- panel key holds both readers ran and exactly 7 findings, 3 resolved / 4 open, severity_max med, zero high/critical/unrated — plan.yaml panel: — verified-at 272968ff
- runs/2026-09-06-02-validator is a DUPLICATE directory of the one panel run, not a second reading; both digests now validate and 01 is authoritative — runs/2026-09-06-01-validator/digest.md — verified-at 272968ff
- INV-29 calls a worktree terminal only on the LANDED plan.yaml status done — .claude/skills/harness/bin/worktree_terminal.py:389-394 — verified-at 272968ff
- /harness-init installs hooks from merge-settings.py HOOK_SPECS, not from the snippet, which is a one-way drift check — .claude/skills/harness/bin/merge-settings.py:44,232-246 — verified-at 272968ff
- Live PreToolUse Bash order is branch-create, bash-write-guard, gh-close, plan-sign; the snippet lacks gh-close — .claude/settings.json — verified-at 272968ff
- Every task verify command shape and case-name assertion is TEXTUAL only; no reader ran one — runs/2026-09-06-01-validator/digest.md adequacy notes — UNVERIFIED

## Dead ends

- Denying a merge on a failed GitHub read — DEC-138 at .harness/harness/docs/DECISIONS.md:2948-2952 — verified-at 272968ff
- Routing an already-worked feature to bare gh-sync.py open — grilling Out of scope at .harness/notes/grilling-mirror-build-entry-2026-09-06.md — verified-at 272968ff
- Sweeping a worktree that records recovery-required to pre-empt an INV-29 report — settled bullet 8, same artifact — verified-at 272968ff
- Backfilling the legacy corpus automatically — BRIEF.md forward-only clause — verified-at 272968ff

## Working set

- .harness/harness/features/BUG-1309-mirror-build-entry/plan.yaml
- .harness/harness/features/BUG-1309-mirror-build-entry/BRIEF.md
- .harness/notes/grilling-mirror-build-entry-2026-09-06.md
- .harness/harness/features/BUG-1309-mirror-build-entry/notes/research-BUG-1309-mirror-build-entry-goalcheck-plan-c3.md
- .harness/harness/features/BUG-1309-mirror-build-entry/runs/2026-09-06-01-validator/digest.md

## Done when

Scope: operator signs the pending plan after the batched findings review
Authority: approval:.claude/worktrees/harness/BUG-1309-mirror-build-entry/.harness/harness/features/BUG-1309-mirror-build-entry/BRIEF.md#Approval
