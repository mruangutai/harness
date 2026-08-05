# STATE

## Current

- feature: FEAT-08-remove-cost-tracking
- run: validate phase complete — briefing written, returning to the main session
- squad: none
- status: awaiting_user

**Phase `validate` is at its terminus.** Thirteen runs, `cycles_used: 4` of 10. `review_sha` pinned
to `942505e` before the panel (INV-6); `8958840` is the last source-bearing commit.

**All twelve tasks DONE, every task issue closed.** T-10's remainder — signed amendment A-3's rows
10 and 11 — landed, and I re-ran all five of its `verify:` clauses at my own tier rather than
relaying them.

**The four-wide panel ran in full**, under the standing user ruling: code, qa, security, ui, no
pre-emptive skips. **All four members returned PASS; their lead found three REQ-08 violations they
had all missed**, every one in a file no member's scope reached and all three invisible to the
compound-token sweeps this feature is built on. MF-2 (`org.html`) and MF-3 (my own Expertise, the
highest blast radius — a dead metering procedure injected into every orchestrator spawn) are FIXED.
**MF-1 is open and only layer 0 can close it:** `.claude/commands/harness.md:18` and `:83` still
instruct the main session to render a spend column and log a cost field. I confirmed no agent may
write that file by running `check-domain.sh` against four personas — all BLOCKED.

**Goal-check: 13 of 15 met.** SC-15 was genuinely not met, was fixed, and pm re-graded it to met —
I did not mark it myself. **SC-05 and SC-06 are red on their own signed wording with correct delivery
behind them**; correcting either edits text the user signed, so both go up rather than into a fix
cycle. Three criteria are met by methods that cannot detect the failure they exist to detect, and
that judgement was asked for explicitly and is recorded.

**Distillation done.** Twelve Expertise files, all `check-expertise.sh` clean, re-run by me because
no lead holds `Bash`. Product 25 ops, validator 16 plus 2 stranded lead ops re-applied, eng 4.

Briefing: `notes/ship-review-validate-close.md`. Handoff: `notes/handoff-validate.md`.

## Open Questions

IDs are not reused. Q2, Q4, Q5, Q7, Q8, Q18 are answered or ruled.

- **MF-1 (BLOCKING, the user's, and nobody else can): two prose deletions in
  `.claude/commands/harness.md`.** `:18` renders a `cost vs budget` column for in-flight features;
  `:83` logs a `cost` field on every return. Both instruct the main session to produce figures from a
  deleted meter. Found independently by the panel and by the goal-check. A third line, `:49`, names a
  dollar figure in a historical anecdote — history, not an instruction; the user's call either way.
  Blocked on: the user.

- **SC-05 and SC-06 are not met on their own wording, with correct delivery behind them.** SC-05's
  second clause forbids any diff line mentioning the cycle counter, and one matched because the cost
  entry shared a line with it. SC-06 pins two numbers measured before this feature's own directory
  existed; restricted to the features it was measured against it returns 89 and 67-of-67 exactly.
  Correcting either edits a signed criterion. A fix aimed at the code would be aimed at nothing.
  Blocked on: the user.

- Q1 (carried): the briefing loses its only size signal. Issue **#79** filed, still unscheduled.
  Blocked on: the user, at the briefing.

- Q3 (carried, harness defect): a send-back gives the returning member a FRESH context, so
  `open_questions` it raised in its own previous DIGEST are unrecoverable to it. Raised twice more.
  Blocked on: nobody — in the briefing's backlog.

- Q6: SC-03 is repo-wide and passes today only because FEAT-09 sits in its own worktree — the hazard
  is dormant, not gone. Re-rooting `check-state.sh` via `CLAUDE_PROJECT_DIR` is **forbidden by user
  ruling** and was not proposed.
  Blocked on: nobody.

- Q9 (from eng-lead, raised twice): nothing detects live/template config divergence — the unit suite
  exited 0 on a half-stripped pair.
  Blocked on: nobody — in the backlog.

- Q19 (harness defect): INV-4's task regex cannot tell a task DEFINITION from a REFERENCE.
  Blocked on: nobody — in the backlog.

- Q20 (raised independently by three agents): the **deployed global** rules still instruct every lead
  to run the deleted meter and write a `cost:` key. One earlier run of this feature complied, so the
  placeholder is on disk in a run dir. `/harness-deploy` after merge, **before** the queued
  preload-trimming batch.
  Blocked on: nobody — in the backlog, near-term.

- **My one substitution, named rather than buried:** the three leads were not re-spawned to file
  domain reports for the briefing. All three ran inside this phase and their own digests are its
  source. That is my judgement, not a rule, and it is reversible for three spawns.
  Blocked on: the user, if they want it done properly.

- The full backlog is **nineteen items** in the briefing. Anything not listed there dies silently.
