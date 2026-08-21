# FINDING — two success criteria have no implementing task, and the plan says so on purpose

**BLUF.** **SC-07 and SC-13 have no task, no file and no mention of their substance anywhere in the
signed plan's 14 tasks.** This is not an execution defect and nobody dropped anything: `D-02` states
the plan is *"HALF-WRITTEN BY DESIGN"* and names SC-07 and SC-13 among the criteria a **second
planning run** was to append. That run appended T-11..T-14 and covered SC-14 — it never reached SC-07
or SC-13. So the feature can finish every task in its plan and still fail a full goal-check.

**This decides what "ship" means for FEAT-31 and it is the operator's call, not mine.** The build now
running is legitimate and unaffected; I am not pausing it.

## The measurement

Loaded `plan.yaml` at HEAD e5f88c4 with `harness_yaml.load_file` — 14 tasks, 22 decisions. The plan
touches **14 distinct files**, enumerated in full:

```
check-state.sh              T-10 T-14      test-context-watch.py        T-02 T-06
context-watch.py            T-01 T-06 T-08 test-run-unit-tests-kinds.py T-12
run-unit-tests.sh           T-02 T-07 T-12 test-upgrade-config.py       T-05
test-check-state.py         T-10 T-14      upgrade-config.py            T-05
test-context-watch-cli.py   T-07           verify-context-watch-live.py T-13
templates/harness.json      T-04           .harness/harness.json        T-03 T-11
DECISIONS.md                T-09           DECISIONS-INDEX.md           T-09
```

`check-domain.sh` — **absent from every task.** `feature-schema.json` — **absent.** Any hook,
`settings.json`, or injection surface — **absent.**

Substance probes across all 14 task bodies, case-insensitive: *"agent identifier"*, *"runs entry"*,
*"refuses a run"*, *"write route"*, *"DEC-191"*, *"own context"*, *"SubagentStart"*, *"while it is
running"* — **no task mentions any of them.**

## What the two criteria actually require

- **SC-07** (`verify: automated`, `evidence: unit`, REQ-04): *"`feature.json`'s `runs` items carry an
  agent identifier, and the write path refuses a run entry that omits it — enforced where DEC-191's
  closed key set is already enforced, on `check-domain.sh`'s `feature.json` write route."* That is a
  change to `check-domain.sh` plus the `runs` item schema in `feature-schema.json`. Both are
  **enforcement layer under DEC-174**, so the task would additionally have to be
  `main-session-direct` — it does not exist in either lane.
- **SC-13** (`verify: automated`, `evidence: integration`, REQ-08): *"An orchestrator whose context
  crosses the threshold receives the warning **in its own context**, and the warning names its
  current size, the threshold, and the nearest seam."* T-06 adds a threshold warning to
  `context-watch.py`'s **stdout**, which the operator reads. REQ-08 requires the orchestrator to be
  told *"while it is running, without the operator asking"* — a delivery mechanism into a live
  agent's context. No task builds one.

## Coverage as it actually stands

The BRIEF declares **14 criteria, numbered SC-01..SC-15 with no SC-12** (verified — the list skips
it; that is a numbering gap, not a missing criterion).

| | criteria |
|---|---|
| Task-covered | SC-01, SC-02, SC-03, SC-04, SC-05, SC-06, SC-08, SC-09, SC-10, SC-11, SC-14 |
| Automatable half only, behaviour half hand-graded (`D-21`) | SC-15 |
| Operator-run UAT by design | SC-10 |
| **No implementing task** | **SC-07, SC-13** |

`D-02` verbatim: *"This plan is HALF-WRITTEN BY DESIGN. Its tasks cover SC-01 to SC-06, SC-08, SC-10,
SC-11 only, that is REQ-01, REQ-02, REQ-03, REQ-05, REQ-06, REQ-07. A second planning run APPENDS
tasks for SC-07, SC-09, SC-13, SC-14, SC-15, that is REQ-04, REQ-08, REQ-09, REQ-10."*

Against that stated intent the second run delivered SC-09 (T-09), SC-14 (T-14) and SC-15's gate half
(T-10), and left **SC-07 and SC-13** — REQ-04 and REQ-08 — unwritten. So the shortfall is exactly two
of the five criteria D-02 promised, and the promise is in the signed artifact.

## Why this is the operator's decision and not a re-plan I can order

The measurement half of this feature — read the sidecars, correct the arithmetic, warn at a threshold,
report blind spots, resolve worktree slugs — is fully planned and is what is being built now. The
**relay half's enforcement pieces** are what is missing: run attribution that a write path enforces
(SC-07) and warning delivery into a live orchestrator's context (SC-13).

Three courses, and the cost of each is real:

1. **Ship the measurement half now**, recording SC-07 and SC-13 as explicitly deferred to a follow-up
   feature. Cheapest, and it delivers the thing DEC-159 assumed exists. Cost: REQ-08's "told without
   the operator asking" — the property that makes the watch *automatic* rather than something the
   operator must remember to run — does not ship, and a deferred criterion on a shipped feature is
   how a half-built mechanism becomes permanent.
2. **Send pm back to append tasks for SC-07 and SC-13** before the ship decision, under a fresh
   signature. Completes the feature as approved. Cost: SC-13 needs a delivery mechanism this
   repository does not yet have, and SC-07 edits `check-domain.sh`, so both land in the
   `main-session-direct` lane — the operator's own hands, on top of the four such tasks already
   queued.
3. **Amend the BRIEF** to drop SC-07 and SC-13. Cost: BRIEF is approval-gated and this narrows an
   approved goal; `D-21` already set the precedent that a signed criterion is *"not the planner's to
   re-methodise"*, and it deliberately left SC-15's text byte-identical rather than quietly
   reclassifying it. The same reasoning applies here.

I am recording the finding and continuing the build. Per the playbook an SC that cannot be met as
written is a plan-level problem — pm re-plans under the operator's approval — and I never mark an SC
met, waived or edited. `D-21` set exactly the right precedent for this situation and its own words are
the warning: *"a goal-check reading BRIEF.md alone would report SC-15 as fully automated, which is
FALSE."* The same trap is open for SC-07 and SC-13, and nothing on disk would surface it at goal-check
time except this note.

## Method

`harness_yaml.load_file` on `plan.yaml` at HEAD e5f88c4 in worktree `.claude/worktrees/FEAT-31`; file
list built from each task's `files:` key; substance probes are case-insensitive substring tests over
each task's full serialised body, so a paraphrase would still have matched. SC list from
`BRIEF.md:105-200`. Re-derivable with the same two commands at the same sha.
