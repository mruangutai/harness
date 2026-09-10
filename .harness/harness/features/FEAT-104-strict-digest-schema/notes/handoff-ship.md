# Handoff — FEAT-104, ship → close-out — written at 6d28b350, seq-8

## Next

Nothing is dispatchable until the operator's ship instruction returns. On **accept**, the main
session owns the sequence — `gh-sync.py ship <feature-dir>` **from the main checkout, with
`--body-file notes/ship-review-ship-c11.md`** (it refuses at exit 1 when the dir resolves inside
`.claude/worktrees/`), stage the unstruck `B-N` rows as backlog issues, merge, then dispatch the
next orchestrator with the **distill** mission (DEC-145 — feature-close distillation runs at MERGE,
never before). That distill dispatch must name the surviving artifacts explicitly: `runs/` is
gitignored, so every run digest dies with the worktree the `post-merge` hook removes, leaving only
`notes/` and `observations/`. On **strike-and-fix instead**, note that `cycles_used` is 10/10: any
in-feature fix needs an operator-recorded budget raise first (DEC-157).

## Trust

- The goal is met in full: 9/9 REQ and 15/15 live SC at `984bd26b`, SC-14 struck, **SC-13 closed by
  the operator's own `passed`** — `notes/uat.md`, `runs/2026-09-10-18-goalcheck-product/digest.md` —
  verified-at 984bd26b
- The pin still reviews the shipping code: `git diff --stat 984bd26b..HEAD -- . ':!.harness'` is
  EMPTY and the tree is clean, so `4907a81b`/`6d28b350` are records only — measured this cycle —
  verified-at 6d28b350
- Panel PASS, `must_fix: []`, `severity_max: med` advisory, `code_grade: pass` (42 fn), zero
  send-backs; `PF-C10-01` withdrawn by the reviewer that raised it at `high` after measuring its
  closure — `runs/2026-09-10-17-panel-validator/digest.md` — verified-at 984bd26b
- Blocking `qa_gate` PASS at the pin, unit 36 / integration 70 both exit 0, focused 13/13 —
  `runs/2026-09-10-15-qa-gate-validator/digest.md`, `notes/qa-2026-09-10-15.md` — verified-at 984bd26b
- 28 of 29 digest files validate; `runs/2026-09-09-08-simplify-eng/digest.md` does not and cannot be
  repaired in place, `-09` supersedes it — `validate-digest.py lead` run over every file this cycle —
  verified-at 6d28b350
- Every residual is an operator or backlog item, none routable to a squad: all four surfaces are the
  DEC-174 carve-out — `notes/ship-review-ship-c11.md` rows B-1..B-29 — verified-at 984bd26b

## Dead ends

- Do not re-run the panel, qa, simplify or the goal-check: all four ran at this exact pin with zero
  send-backs — `feature.json` `runs:` — verified-at 984bd26b
- Do not route any `B-N` row to a lead: every remedy edits `validate-digest.py`, `check-domain.sh`,
  `check-state.sh`, `run-state-schema.json` or their tests — DEC-174 — verified-at 984bd26b
- Do not spend a cycle re-adjudicating CF-3: the recommendation is ACCEPT and record, and excising it
  would rewrite history beneath a signed pin — `runs/2026-09-09-10-panel-validator/digest.md` CF-3 —
  verified-at 168f875f
- Do not attempt to repair `-08`'s digest: the append-only channel structurally cannot and has
  refused twice — STATE Q6, re-measured this cycle — verified-at 6d28b350
- Do not re-pin `review_sha` or increment `cycles_used` for the ship phase: no lead ran, so
  `feature.json` was not written — `feature.json` — verified-at 6d28b350

## Working set

- `.harness/harness/features/FEAT-104-strict-digest-schema/notes/ship-review-ship-c11.md`
- `.harness/harness/features/FEAT-104-strict-digest-schema/notes/uat.md`
- `.harness/harness/features/FEAT-104-strict-digest-schema/STATE.md`
- `.harness/harness/features/FEAT-104-strict-digest-schema/feature.json`
- `.harness/harness/features/FEAT-104-strict-digest-schema/runs/2026-09-10-17-panel-validator/digest.md`

## Done when

Scope: the operator's ship decision on the c11 briefing is relayed back down
Authority: brief-sc:SC-13
Authority: approval:.harness/harness/features/FEAT-104-strict-digest-schema/BRIEF.md#Approval
