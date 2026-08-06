# Performance roadmap — the remaining tickets, by batch — 2026-08-05

User-scoped and user-sequenced on 2026-08-05. This is the plan of record; `/harness-plan` takes
one batch at a time and does NOT re-derive the grouping.

## State

`performance` label: **13 issues** — 3 shipped in FEAT-07 (#18, #19, #22), **#81 closed 2026-08-05 as
not reproducible**, 9 open. **#20 is in flight as FEAT-09.** **Eight remain**, in three batches.

Not labelled, deliberately, and previously ruled out of scope: #36, #74, #78 (marginal — they cost
time but their purpose is not speed), #58 and #78 (simplification, not workflow performance), and
**#103** (a worktree enforcement bug; it was labelled in error and the label was removed).

## The batches, in order

### A — preload trimming · #83, #84, #43
Everything agents load at **every spawn**. Already queued behind FEAT-08 by construction: all three
touch files FEAT-08 is editing.

- **#83** drop `harness-team` from the orchestrator's preload — 19,088 bytes of a 53,445-byte
  preload (~36%), paid 3–4× per feature under DEC-159. Flat mode is dead (`SPEC.md:1309`).
- **#84** split `harness-expertise`'s distillation half out of the 16-agent universal preload —
  lines 51–113 of 125 govern a once-per-agent-per-feature event; ~29k tokens/feature.
- ~~**#43** the line budget on `harness-team/SKILL.md`~~ — **STRUCK 2026-08-05, MISCHARACTERISED HERE.**
  #43 is *"Two FEAT-06 residuals: T-09's line-cap estimate and a stale 3x quote in PLAN.md"* — a
  low-severity bookkeeping pair, and it states the shipped file was **within budget**: "this is a
  discrepancy between the advisory's estimate and the cap, not a violation." It was never a trimming
  task. The row was read as one and ranked #1 on that basis before anyone opened the issue.
  **The trim itself was still worth doing and was done** (18,533 -> 15,584 B, ~47,200 B/feature) as
  unticketed work at `712b070`. #43 remains open as the two residuals it actually is.

**Waiting makes #83 cheaper, not just safer:** its first required rider — *"move the
ORCHESTRATOR-ONLY `cost-report.py` paragraph or INV-11's metering instruction is lost"* — evaporates
once FEAT-08 deletes both. The rider becomes a deletion instead of a relocation.

**Trigger: FEAT-08 merges.**

### B — observability · #79, and #82 rides along
- **#79** count and budget RUNS, not just cycles. FEAT-03 ran **19 runs against a 6-cycle budget**
  and tripped nothing, because DEC-157 counts rework only. Urgent because FEAT-08 removes cost —
  the other long-feature signal — leaving nothing that notices a feature running long.
- **#82** give a held orchestrator read-only work. Tiny, no evidence section in the review, no
  batch of its own; it rides with B because both touch the orchestrator playbook.

**#79 touches `check-state.sh` — DEC-174 carve-out.** Direct execution, tests run explicitly, a
human reads the diff.

### C — the validation and close-out tier · #7, #21, #80
All three change when and how the panel and the close-out run.

- **#7** panel members re-derive gate results they were told to audit — price the independence.
- **#21** qa phase 1 concurrent with the build. **Collides with open #40, #41, #42**, which contest
  qa's write permissions and the panel's membership. Those must be scoped before #21 is plannable.
- **#80** collapse the close-out rounds. The one row on the review's stack rank with a genuine
  quality cost; do NOT collapse all three rounds (DEC-69 — distillation feeds the briefing's
  curation block).

**Land the four-wide panel ruling here.** It is currently an instruction the main session pastes
into every spawn prompt by hand. If C ships without codifying it in the playbook, the ruling is
prose-only enforcement depending on someone remembering — the exact pattern this whole effort has
been correcting. Carry it into C's BRIEF as a requirement, not a nicety.

### D — the hook-fire multiplier · #81. ~~LAST, ALONE, MEASURE FIRST.~~ **WITHDRAWN 2026-08-05.**

**The probe ran and the premise does not reproduce: 1 Write tool call = 1 hook fire**, allow path
and deny path alike, one `PreToolUse` entry registered. The 11 and 21 were incidental observations
inside probes of other questions, flagged "not chased" when recorded. The `~0.9s per governed call`
figure was `21 × 43.5ms`; the real cost is 43.5ms — already 46% faster than pre-FEAT-05 while doing
more work. **Issue #81 closed, batch D dropped.** Nothing to deduplicate.

The measure-before-planning ruling is what made this cheap: one probe closed the highest-risk item
on the roadmap instead of a feature being planned against a mechanism nobody had observed.

Original text below, kept because how it got ranked second is the more useful finding.


The write-permission hook fires **11–21 times per single write**; at ~43.5ms each that is ~0.9s on
every governed tool call. Highest risk on the review's own ranking, and the only item where a
mistake makes the harness **less safe** rather than slower — the fix must be deduplication only,
never "fire less".

**USER RULING: measure before planning.** Nobody has established *why* it fires 11–21 times; the
review says outright "multiplier is not constant, not chased". Run the bounded probe first — the
additive-line, byte-identical-revert technique both existing measurements used, and the one
FEAT-07's probe-don't-infer rule now mandates. **Until that lands, any plan is a guess about a
mechanism nobody has observed.** Only after the probe does D become plannable.

`check-domain.sh` is DEC-174 carve-out.

## Sequencing summary

| Batch | Starts when | Blocked by |
|---|---|---|
| A | FEAT-08 merges | file collisions with FEAT-08 |
| B | after A, or in parallel if nothing shares files — check first | — |
| C | #40/#41/#42 scoped | qa permissions and panel membership are contested |
| ~~D~~ | **withdrawn** — probed 2026-08-05, not reproducible | — |

## What this roadmap does not cover

Perf-review rows 6, 8, 9, 10 and 12 are all filed and in the batches above; **row 7 was withdrawn on
measurement** (see D). Row 11 was closed by
FEAT-06. Rows 1, 2 and 5 shipped as FEAT-07. **The review is fully triaged** — there is no
unaccounted row.
