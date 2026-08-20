# Layer-0 batch B — FEAT-29 — the build phase is closed, two tasks remain and both are yours

**BLUF.** All nine tasks are written, the blocking gate is green, the panel passed, and SIMPLIFY
applied nothing — so **the code you are about to measure is final**. Two tasks remain: **T-07 first,
then T-09.** The mirror stays frozen until T-07 lands.

Branch `feat/FEAT-29-graphql-budget`, HEAD **`e7104ca`**, `review_sha` pinned there and verified equal
to the tip.

## Why T-07 must go first, and why now is the right moment

Seven of the positive control's lines quote cards reading `Backlog`. Every `start-task` or
`close-task` moves a card and deletes a line — that is exactly how the eighth was lost when #586
closed. So no mirror subcommand runs, for any task, until `measurement-after.md` exists.

And SIMPLIFY finishing with **zero applies** is what makes now correct rather than merely convenient:
had it changed `gh_board.py` or `factory_gh.py` afterwards, T-07 would have measured code that never
shipped. `git diff` on `.claude/skills/harness/bin/` against the reviewed commit is empty.

## The order

| # | Task | Issue | Notes |
|---|---|---|---|
| 1 | **T-07** | #585 | Cut-over proof + `measurement-after.md`. Nothing may move a card before it |
| 2 | **T-09** | #587 | Board-6 proof for SC-03. Independent of T-07, but its card move would break the control |

Extract each `intent:` and `verify:` from `plan.yaml` as batch A did — they are the specification and
I have not copied them.

## What T-07's verify now enforces, which is the part worth knowing

Amendment 4 rewrote it and I read it: it loads `measurement-before-positive.md`, filters the `T-08`
line, asserts **exactly 7** control lines survive (I counted 7 in the file myself), requires a
`POSITIVE-CONTROL` section in the after-file, requires all seven present verbatim, and emits
`CONTROL FAILED - n/7 INV-26 lines absent; the cheap read is not reading the board. REJECT, do not
explain`. **That gate can fail** — you mutation-proved it against a hand-written after-file.

The `delta` ceiling is 100 points. Expect about 5.

## Board state, measured directly rather than assumed

| Card | Station |
|---|---|
| parent #571 | `Building` |
| T-01 #579, T-02 #580, T-03 #581, T-04 #582 | `Backlog` |
| T-07 #585, T-09 #587 | `Backlog` |
| T-05 #583, T-06 #584, T-08 #586 | `Done` |

After T-07's after-measurement is captured, run the catch-up `start-task`/`close-task` pairs — about
4 points each. You said you would take those yourself.

## Corroboration for what T-07 is about to prove

One live call to `factory_gh.project_item_stations('mruangutai', 3, 'Status')` read **486 items for 5
GraphQL points**. The `check-state.sh` run the old path sits inside measured **506** in your own
baseline. That is corroboration only — SC-01 is a differenced `check-state.sh` run and that is T-07's
job, not something already discharged.

## State of the build, verified at my tier rather than relayed

- **`matrix_ok: true`.** `--kind unit` exit 0, `grep -c '^PASS '` = **175** (the runner-level count is
  18 scripts), 0 FAIL; `--kind integration` exit 0, 12 of 12, 0 FAIL.
- **Panel PASS**, `must_fix` empty, `severity_max: low`. A security reviewer ran because the validator
  lead reversed its own scope-out after reading the briefing's disclosure that none ever had.
- **SIMPLIFY: four angles, zero applies.** Two findings, both downgraded to backlog by the lead after
  it checked their premises — one had its stated cost falsified, the other a clause corrected.
- **SC-02, SC-05, SC-06, SC-07, SC-10 met.** SC-01, SC-03, SC-04 **pending on T-07 and T-09**. SC-08
  and SC-09 are `not-assessed`: both sit on `NOBODY` paths, so no agent domain covers them and they
  are pre-ship steps for you, not gaps.
- 7 cycles of 10; 11 runs of 20; **46 GraphQL points** spent by me across the whole feature.

## Still yours, and not touched by me

`CLAUDE.md` · the two paused flow directories · `.harness/logs/gh-cost-2026-08-19.jsonl`, still
untracked and un-ignored, so the tree is dirty at ship. The security reviewer's narrow remedy is a
`.harness/logs/gh-cost-*.jsonl` ignore rule — **not** blanket `.harness/logs/`, whose sibling session
logs are tracked.

## After batch B

pm's goal-check through product-lead over all ten SCs, then close-out — ship-refresh and distillation
dispatched in one turn — then the final CEO briefing for your ship decision.
