# STATE

## Current

- feature: FEAT-08-remove-cost-tracking
- run: dispatching S4 to product-lead — runs/s4-product
- squad: product
- status: in_progress

**Eight of twelve tasks are DONE and committed**, issues #86-#93 all closed. Branch tip `95c1c38`.
Gates green at that SHA: unit exit 0 (now **twelve** scripts, not thirteen), check-docs exit 0,
check-state exit 0 with zero violations.

**The meter is gone as of `1a69d9d`.** Last measurable figure, taken at `3503d1d` just before the
deletion: **$370.53** against a $120 budget. Everything after that is unmeasurable by design and no
figure for it will be invented. D-02's ordering proved itself on the first unmetered run — `s2-eng`
carries no `cost:` key and `check-state.sh` still exits 0, because T-02 removed INV-11 before T-03
removed the meter.

**SC-01 IS UNREACHABLE AS WRITTEN and blocks the goal-check.** The sweep is down from 18 files to
6, but SC-01 demands only two remain. Three approved requirements make four files unavoidable — see
`feature.yaml` `sc01_blocker`. Routed to pm to draft the amendment; the ruling and the signature
are the user's, never mine.

**The T-04 lane defect is the routing wall's fourth recurrence**, landing inside the feature running
concurrently with FEAT-09, which exists to prevent it. eng-lead returned BLOCKED rather than routing
around `check-domain.sh` when a `python3 -c` rewrite would have passed `bash-write-guard.sh` unseen.
User ruling received: T-04 splits, no domain widened.

Next: S4 (T-09..T-12, documentor) plus pm's two amendments, as ONE product-squad run. Then the
user re-signs, then the four-wide panel, then the goal-check.

## Open Questions

IDs are not reused. Q1 and Q3 carried from plan; Q5-Q9 new. Q2 and Q4 were answered in planning.

- **Q8 (BLOCKING the goal-check, the user's call): SC-01 cannot be met as written.** It requires the
  sweep to return only `DECISIONS.md` and `DECISIONS-INDEX.md`. Four files cannot leave it:
  `test-validate-digest.py` because T-01's intent mandates the `cost_usd` backward-compat fixture
  that proves SC-04's second half; `BUILD.md` and `SPEC.md` because T-10/T-11 mandate inline
  `(cost-report.py removed — DEC-178)` markers and SC-14 blesses them; `test-check-state.py` because
  two comments explain what the deleted INV-11 used to do. SC-01 contradicts SC-04, SC-14 and D-07
  at once. Options: (a) widen SC-01's expected file set with each reason named, or (b) narrow its
  pattern to exclude fixture and marker contexts. pm drafts; the user signs.
  Blocked on: the user.

- Q1 (carried, **partially answered**): the briefing loses its only size signal. perf-review row 10
  is now filed as **issue #79** (count and budget RUNS). Still unscheduled, so the gap is real and
  now tracked rather than only noted.
  Blocked on: the user, at the briefing.

- Q3 (carried, harness defect): a send-back gives the returning member a FRESH context, so
  `open_questions` it raised in its own previous DIGEST are unrecoverable to it.
  Blocked on: nobody — routed to the harness owner.

- Q5: SC-06's glob over-captures; restricted to FEAT-01..07 its numbers are exactly pm's 89 and
  67-of-67. Recommend the goal-check use the restricted glob and record both.
  Blocked on: nobody.

- Q6: SC-03 is repo-wide and a concurrent flow can fail it. FEAT-09 has moved to its own worktree,
  so the hazard is dormant, not gone.
  Blocked on: nobody.

- Q7 (for the panel, not the user): both comments reworded around the S1 plan defect justify
  themselves with "this task's `verify:`", which will not exist after ship.
  Blocked on: nobody — the code-reviewer rules.

- Q9 (from eng-lead, non-blocking): nothing detects live/template config divergence — the unit
  suite exited 0 on a half-stripped pair. In scope for FEAT-08, or a follow-up?
  Blocked on: the user, at the briefing.
