# FEAT-54 — handoff "Done when" — build halted, one decision needed

**The build stopped after one of twelve tasks, and it is not a build problem.** The approved plan
pins five of its files at paths this repository forbids, and justifies two of its decisions by
machinery that no longer exists in `run-unit-tests.sh`. FEAT-47-tests-layout merged **at the plan's
own declared base commit** and moved every test under `tests/` and every probe under
`tests/manual/`; the plan was drafted against the layout that merge replaced. Nothing a squad can do
closes this. It needs your ruling on one question, then a pm amendment and a re-signature.

**What did land is real and green.** T-05 froze the historical-note baseline — 141 sorted, unique
paths from `b7956fc4`, none of them a note of this build. Its verify prints `ok 141`; the unit suite
is green in the worktree (exit 0, zero `FAIL` lines, 66 files). Committed as `669b7152`.

## The decision I need from you

**Q4 — the plan is written against the old test layout. How do you want it repaired?**

| Option | What it costs | My recommendation |
|---|---|---|
| **A. Repoint the plan to `tests/`** — tests to `tests/integration/`, the probe to `tests/manual/` beside the precedent probe; restate D-04's and D-06's falsified rationales | pm amendment to 2 decisions, 5 tasks' `files:`, 6 `verify:` blocks. Resets approval to pending, re-runs the plan panel, needs your signature again | **This one.** It moves the plan to where the repository already is |
| **B. Amend `suite_layout.py` to exempt registered probes under `bin/`** | Weakens an invariant FEAT-47 landed with its own test, to accommodate a stale plan. Adds a third file to the change | No. The gate's value is that it admits no exceptions |

Option A is also the eng-lead's recommendation, independently reached.

## The evidence, all measured at HEAD `63af2eda`, all re-derived by me rather than relayed

- `suite_layout.violations()` reports any `test-*.py`, `*.test.*` or `probe-*` left under
  `.claude/skills/harness/bin/` (`suite_layout.py:29-33`), and `run-unit-tests.sh:31` runs it on
  every invocation. **T-01, T-03, T-06, T-09 and T-12 all pin their files there.**
- `run-unit-tests.sh` has **no** `UNIT_SCRIPTS`, **no** `INTEGRATION_SCRIPTS`, **no** `KINDCHECK`
  heredoc and **no** probe-drift check. It globs `tests/unit/test-*.py` and
  `tests/integration/test-*.py` (`:25-27`). D-04's and D-06's `because` clauses both cite that
  absent machinery, and T-12's three cases have no subject at all.
- `test-check-domain.py` and `test-check-state.py` live at `tests/integration/`. T-03 and T-06 say
  "extend" a file at a path where nothing exists. `test-run-unit-tests-kinds.py` — T-12's entire
  subject — exists nowhere; the nearest file is `tests/integration/test-run-unit-tests-layout.py`.
- T-02's module `handoff_done_when.py` is **not** affected: the invariant bans only test- and
  probe-shaped names under `bin/`.

## How this briefing was assembled

**No report round was spawned.** I read the run digests off disk, per DEC-69. The paths:
`runs/2026-09-02-{01,2,3,5,1,c2,c2c,c2d,c3,c3b,goalcheck,c2goalcheck}-product/digest.md`,
`runs/2026-09-02-{4,c2,c3}-validator/digest.md`, and `runs/2026-09-02-t05t09-eng/digest.md` —
seventeen recorded runs, sixteen with a digest on disk (`2026-09-02-goalcheck-c1-product` has a run
record but no digest directory).

- **Engineering** (`runs/2026-09-02-t05t09-eng/digest.md`) — T-05 PASS with `task_verify: pass` and
  zero send-backs; T-09 BLOCKED, unimplementable as approved. The lead re-derived the member's three
  claims itself and added a fourth the dispatch had wrong: D-04's rationale describes a gate that
  does not exist.
- **Product**, twelve runs, all plan phase — the plan reached signature through four goal-check
  cycles. The last (`runs/2026-09-02-c3-product/digest.md`) found 0 uncarried settled lines and 0
  out-of-scope re-admissions; `runs/2026-09-02-c3b-product/digest.md` closed the panel-record defect.
- **Validation**, three plan-panel runs. The last (`runs/2026-09-02-c3-validator/digest.md`) ran all
  three readers, `severity_max: med`, nothing high, critical or unrated. Its own `adequacy_notes`
  state plainly: *"NO GATE SCRIPT WAS EXECUTED and NO PLAN TASK WAS BUILT… This panel cannot
  distinguish a plan that will BUILD correctly from one that READS correctly."* **That is exactly
  the blind spot the build then walked into** — see B-5 below.
- **Goal-check against the success criteria: not yet run.** It is a build-completion step and the
  build did not complete. **UAT: not reached.** No SC is graded, met or waived.

I verified on disk, not from the digests, that both approval gates read `approved` (Mike Ruangutai,
2026-09-02), that `plan.yaml`'s `panel:` records cycle 3 with all three readers `ran`, nine findings
and no stale disposition, and that no FEAT-54 note entered the frozen baseline.

## Budgets

- **Cycles: 9 of 30.** You raised the cap from 10 in this dispatch; it is recorded in `feature.json`.
  **No cycle was charged for this run** — the lead reported zero send-backs and nothing was routed
  back. A falsified plan premise is not rework (DEC-157).
- **Runs: 17 of 20.** Under budget. Sixteen of the seventeen are plan-phase; that is a heavy plan
  for a change whose core is a few hundred lines, and it did not catch the defect that stopped the
  build.

## Open questions

- **Q4 — blocking, yours.** The layout repair above.
- **Q1, Q2, Q3 — non-blocking, harness owner.** Carried unchanged from the plan phase: the
  plan-panel's non-harness reader deviated from the team spec's envelope for a second consecutive
  cycle with only the hosting lead validating it; two product-lead contexts collided on one run
  directory; a stray literal `yield` token opens the scope reviewer's c3 note.
- **Q5 — non-blocking, new, harness owner.** Four goal-checks and three panel cycles read this plan
  without noticing that five of its declared `files:` paths are forbidden by a gate that runs on
  every suite invocation.

**Resolved escalations: none this run.** The eng-lead's E1 is routed to pm and is pending your Q4
ruling. The plan phase's E1 (no `approval.rulings` key) was closed by the ruling that none was
needed — no high, critical or unrated finding remained open.

## Proposed backlog — strike any row by ID; anything not listed dies silently

| ID | Nature | Row |
|---|---|---|
| B-1 | chore | Add a plan-phase check resolving every task's declared `files:` path against `suite_layout.violations()`, so a plan cannot be signed pinning a file at a forbidden path (Q5) |
| B-2 | bug | Enforce the plan-panel team spec's single-key `findings` envelope mechanically, or restate it as the non-harness persona's actual return shape (Q1) |
| B-3 | bug | Make run-directory slugs collision-proof, or have the run-dir writer refuse an occupied directory rather than overwrite its `state.yaml` (Q2) |
| B-4 | chore | Strip the stray literal `yield` token from `notes/review-harness-code-reviewer-planpanel-c3.md:1` (Q3) |
| B-5 | enhancement | The plan panel is text-only and says so in its own `adequacy_notes`; give it one mechanical pass that resolves the plan's cited paths and greps its cited machinery against the real tree |
| B-6 | chore | Pin an artifact path for SC-04's review-time evidence, and for SC-07, SC-08 and SC-11, which carry the same looseness (panel F-2, low) |
| B-7 | chore | Drop T-06 case (g)'s misleading `fully resolving` qualifier — the state-check pass runs `resolve=False` and never opens a target (panel F-3, info) |

## What happens next, if you take option A

1. You authorize the amendment; the main session sends pm through `harness-product-lead` to repoint
   D-04, D-06 and T-01/T-03/T-06/T-09/T-12, and to re-derive whether those tasks' `intent:` bodies
   need rewriting too — several describe registration in script arrays that no longer exist.
2. The amendment resets approval to pending and the plan panel re-runs over the unfinished tasks.
3. You sign, and the build resumes at T-01. **T-05 does not need redoing**; it is committed and green.

One thing needs doing whatever you decide, and it is not mine to do: the GitHub mirror opened this
run (parent **#1262**, sub-issues **#1263-#1274**, milestone 43) because the session check found it
had never run at all. The twelve cards were created at `backlog` while the plan says `ready`. The
signature-time promotion — `gh-sync.py status <feature-dir> ready` — is the main session's row under
DEC-138's one-owner table, so I left it rather than write another owner's column.
