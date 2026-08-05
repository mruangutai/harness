# STATE

## Current

- feature: FEAT-08-remove-cost-tracking
- run: dispatching the four-wide review panel to validator-lead — runs/panel-validator
- squad: validator
- status: in_progress

**Phase is `validate`. Branch tip `942505e`, and `review_sha` is PINNED to it (INV-6).**

**All twelve tasks are DONE and every task issue is closed.** T-10's remainder — signed amendment
A-3's rows 10 and 11 — landed at `942505e`; issue #95 is closed. **All five of T-10's `verify:`
clauses were re-run by me at that SHA rather than relayed:** the compound-token sweep leaves one hit
and it carries the `DEC-178` marker; the unchanged-count clause is 8 before and 8 after, matching the
member's own captured baseline; the new plain-word sweep printed exactly the two defect lines
mid-flight and prints nothing now; unit 0; docs 0. The diff is two hunks and nothing else.

**A-1, A-3 and A-4 are SIGNED** — both artifacts read `status: approved`,
`amendments-signed: A-1, A-3, A-4` — and A-4's five-edit main-session-direct batch across the two
DEC-174 carve-out files is committed at `00f3e03`.

**SC-01 and SC-04 both verified directly by me, not relayed.** SC-01's amended sweep returns exactly
the four survivors it enumerates — `BUILD.md`, `SPEC.md`, `DECISIONS.md`, `DECISIONS-INDEX.md`. It
returned 18 at `ae2443d` and 6 before the batch, so it stays discriminating in both directions.
SC-04's surviving half returns `digest ok`, exit 0. Gates at `942505e`: unit 0, docs 0, state 0 with
zero violations.

Next: **the four-wide panel, all four steps, no pre-emptive skips (standing user ruling)** → pm's
goal-check → distillation → the CEO briefing, which is this phase's terminus.

## Open Questions

IDs are not reused. Q2, Q4 and Q8 are answered; Q18 is ruled.

- Q1 (carried, partially answered): the briefing loses its only size signal. perf-review row 10 is
  filed as **issue #79**. Still unscheduled, so the gap is real and tracked rather than only noted.
  Blocked on: the user, at the briefing.

- Q3 (carried, harness defect): a send-back gives the returning member a FRESH context, so
  `open_questions` it raised in its own previous DIGEST are unrecoverable to it.
  Blocked on: nobody — routed to the harness owner.

- Q5: SC-06's glob over-captures; restricted to FEAT-01..07 its numbers are exactly pm's 89 and
  67-of-67. The goal-check must record BOTH the restricted and unrestricted results.
  Blocked on: nobody.

- Q6: SC-03 is repo-wide and a concurrent flow can fail it. FEAT-09 has moved to its own worktree,
  so the hazard is dormant, not gone. Re-rooting `check-state.sh` via `CLAUDE_PROJECT_DIR` to make it
  pass is **forbidden by user ruling** — that is the re-baselining the user refused.
  Blocked on: nobody.

- Q7 (for the panel, not the user): **three** comments reworded around the S1 plan defect justify
  themselves with "this task's `verify:`", which will not exist after ship. The A-4 batch created the
  third, at `test-check-state.py:326`.
  Blocked on: nobody — the code-reviewer rules.

- Q9 (from eng-lead, non-blocking): nothing detects live/template config divergence — the unit suite
  exited 0 on a half-stripped pair. Backlog candidate.
  Blocked on: the user, at the briefing.

- Q18 (**RULED by the user: add nothing**): deleting the pin removed the only deliberate assertion of
  unknown-key tolerance. The user's mandate is a **strict** schema — unknown keys should be rejected,
  not tolerated — so a fixture asserting tolerance would cement the opposite direction. Filed as
  **issue #104** with the measurement: 51 of 71 real digests on disk carry keys outside their schema.
  Blocked on: nobody — closed.

- Q19 (harness defect): INV-4's task regex cannot tell a task DEFINITION from a REFERENCE, so a PLAN
  amending a task by heading trips `check-state.sh`. The regex is the defect, not the amendment.
  Blocked on: nobody — routed to the harness owner.
