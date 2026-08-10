# FEAT-10 software factory — ship review

**2026-08-09 · build phase complete · base `f9488a2` · nothing committed**

---

## The short version

**The factory is built and it is not shippable yet — for two reasons, neither of which is a defect
in the code you paid for.**

Eleven of twelve tasks landed across four runs with **zero rework**. Fifteen new files — **1,585
lines of implementation against 4,008 lines of test** (measured, not estimated) — and all suites are
green. The first real code review of those modules found nothing that gates.

What stops it:

1. **Your only blocking gate cannot return a verdict**, because `harness.json` describes a test kind
   that does not exist in this repository. This is a config decision, not a code fix, and its blast
   radius is every future feature.
2. **One task was withheld from the robots on purpose** and only you can land it. Until you do, one
   success criterion out of twenty has no evidence at all.

**Budget is healthy.** Eight of ten rework cycles used — **all eight from the planning phase, none
from the build.** Two remain.

| | |
|---|---|
| Tasks | 11 of 12 done, **0 send-backs** across three build waves |
| Success criteria | **16 met, 3 one-assertion-short, 1 with no evidence** (see the tally dispute below) |
| Blocking gate (qa) | **BLOCKED** — on `harness.json`, not on the code |
| Review panel | **PASS**, worst severity `med` — nothing gates |
| Security | **PASS**, worst severity `info` |
| Cycles | 8 of 10, two remaining |

---

## What I need you to decide

### D-1 · The `functional` test kind — this is the blocker

`harness.json` says three change types must have "functional" tests. The factory's modules classify
into two of those types, because they shell out to `gh` and `git`. So functional tests are required.

**They cannot run, for two independent reasons, and I verified both myself:**

- `test_kinds.functional.cmd` is `null` — there is no command to run.
- `test_kinds.functional.detect` is `tests/functional/**`, and **no such directory exists** in this
  repository. It matches zero files.

The gate's rule is that a test kind it cannot run is `BLOCKED`, never a pass and never a failure —
because a hard gate that waves through a broken command is worse than one that halts.

**Why both triggers matter:** there is a known disagreement across four harness skill files about
whether a `null` command means "blocked" or "harmlessly not applicable." You might reasonably reach
for settling that in favour of "not applicable." **It would not unblock you** — the second trigger,
the glob matching nothing, stands on its own.

Your options, with the real cost of each:

| Option | What it costs | What it buys |
|---|---|---|
| Stand up a functional test runner | New work nobody planned; this feature has no functional tests to run under it | The gate passes honestly |
| Change the matrix so CLI work does not require `functional` | A plan change, so it comes back for your approval; changes the gate for **every future feature** | The gate passes, and the four-file contradiction must be settled in the same pass or the next gate re-derives the opposite answer |
| Accept the feature with its only blocking gate unresolved | You are overriding the gate knowingly | Ships now |

There is no free option here. The code is not the problem in any of them.

### D-2 · T-08 — the task only you can land

`T-08` adds an invariant to `check-state.sh`. It was withheld from every squad because a gate cannot
vouch for a change to itself — that is the standing carve-out, and I honoured it.

It is the **only** thing that can satisfy **SC-06** ("the state check fails when a feature records a
claimed issue in a repository the fleet file does not declare"). I confirmed by grep that `INV-24`
appears nowhere in the codebase.

**One timing detail you would not otherwise see.** The integration test runner uses a hardcoded file
list, not the config — and that list **already contains** `check-state.sh`'s test. T-12's evidence
therefore depends on that file. If T-08 lands *after* the fact, T-12's green becomes stale evidence
for two criteria. T-08 depends only on T-01, which is done, so it can be landed at any time and
sooner is strictly better.

### D-3 · Which bar counts as "done"

The goal-check and the qa gate graded the same tree differently, and the difference is honest:

- **19 of 20**, if the question is *does each criterion have evidence pointing at it* (qa's bar).
- **16 of 20**, if the question is *does every clause of each criterion have an assertion behind it*
  (the goal-check's stricter bar).

The three criteria in dispute — **SC-13, SC-18, SC-19** — are each **one added assertion** from met.
Each has a clause nothing tests: that no two skip reasons read alike; that the fleet loader is the
only reader of the fleet file; and three clauses of the end-to-end journey. The goal-check flagged
that this stricter bar is **its own construction, not something the brief states**, and that you may
overturn it.

My recommendation: **add the three assertions.** It is one small run, it costs one of my two
remaining cycles at most, and amending the criteria instead would be a plan change needing your
signature anyway.

### D-4 · Two smaller calls

- **The GitHub mirror was not run, deliberately.** Publishing this feature's tasks as issues would
  put them in `mruangutai/harness` — the same repository the factory itself publishes into. The plan
  records this as a double-write hazard producing two issues per task, and defers it to you.
  Creating a milestone, a parent issue and twelve sub-issues is not cheaply reversible, so I left it.
- **Nothing is committed, and I recommend you commit by explicit pathspec if you do.** Two reasons.
  First, `run-unit-tests.sh` is a file this feature changed *and* one that already carried unrelated
  uncommitted work, so its change cannot be isolated. Second — and I did not expect this — **two
  staged deletions appeared in the index during this session**
  (`.claude/commands/harness-grill.md`, `.claude/commands/harness-wayfind.md`). They are not this
  feature's; no agent I dispatched has written anywhere near `.claude/commands/`. A plain
  `git commit` right now would sweep them in.

---

## Two limits the plan deliberately preserved. Neither is a surprise; both must be said out loud.

### No success criterion exercises the live GitHub API. At all. Before shipping.

This feature's only hand-operated criterion, SC-07, was **deleted on your 2026-08-08 ruling** as
anticipation under the one-in-flight cap. The consequence you accepted then, restated now because
this is the moment it bites:

**The entire test suite is green against scripted stand-ins for `gh` and `git`. The first real
dispatch of this factory IS its live verification.**

Concretely: that two agents racing for the same work item genuinely serialise is *inferred* from the
GitHub endpoint being create-only — it is measured by nothing. The board, the target repository and
the merge are exercised by no criterion. The whole automated set could be green on a factory that
cannot perform one real claim. That is disclosed in the brief and it remains true.

### The plain-English rewrite of the requirements got only a partial review

When the requirements and criteria were rewritten into plain English, a reviewer could only compare
**7 of the 20 criteria** against their earlier wording — the other 13 had no earlier version on
record to diff against, because the feature's files were untracked at the time.

Those 7 got a full meaning-level comparison and produced the one real change (SC-01 gained a
precondition). The other 13, plus all 8 requirements, got a mechanical check only — identifiers,
paths, command names, exit codes — which found nothing wrong. **So for 13 criteria, "the rewrite
changed no meaning" is unverified and unverifiable by construction.** The files are tracked now, so
this cannot recur; it does not retroactively create the missing baseline.

---

## What each squad found

**Assembled from run digests read off disk. I spawned no reporting round** — every run wrote a
digest and re-narrating them would have cost three lead spawns to tell me what I can open. Every
claim below is cited to its file. All paths are under
`.harness/features/FEAT-10-software-factory/`.

**Engineering — three build waves, `runs/w1-eng/`, `runs/w2-eng/`, `runs/w3-eng/`, all PASS, zero
send-backs.** Wave 1 shipped the CLI contract, the GitHub seam and the test-kind widening. Wave 2
shipped the fleet loader, workspace, publish and claim tools. Wave 3 shipped the pull-request tool
and the fork-level suite. Two things worth your attention: the lead caught a contradiction in the
plan's own wording that would have cost three tasks an import error, and it was ruled before
dispatch rather than after — zero spawns spent. And a coverage hole the builders admitted
themselves (git commands validated against the manual, never executed) was closed in wave 3 against
real git, which also corrected a misattribution about which safety hook had been blocking them.

**Product — `runs/t09-product/`, PASS.** DEC-186 recorded: GitHub issues and one board are the
factory's interface, the signed plan remains the source of truth, and the factory may read GitHub
state back for exactly three purposes.

**QA gate — `runs/qa-validator/`, BLOCKED.** Covered as D-1. Unit and integration are both genuinely
green — 10 and 14 files, exit 0. qa also built the criterion-to-test evidence map the goal-check
then audited.

**Review panel — `runs/panel-validator/`, PASS, worst severity `med`.** First code review these
fifteen modules have ever had. Security audited twelve mechanisms — argv construction, path
resolution, YAML loading, environment seams, credential flow — and topped out at `info`: no shell
injection surface, safe YAML loading confirmed, no credential reaches output or a ledger.

**The panel's most valuable act was to argue its own findings down.** Two `high` findings it was
handed came back `med` on evidence, and the lead disclosed that it had *caused* one of them by
carrying the word "high" into all three reviewer briefs — three reviewers echoed a severity instead
of deriving one. It then ran the check nobody had run and refuted the reasoning behind it. I would
rather have that disclosure than a clean-looking panel.

**Goal-check — `runs/goalcheck-product/`, ESCALATE.** Covered as D-3. It found three cases of a
mapped test that passes while a clause of its criterion has nothing asserting it — including that
the very test guarding against the top-ranked defect omits both discriminators, so it passes without
binding what it exists to bind. It also corrected three rows of qa's evidence map.

---

## Proposed backlog

Nothing here gates. **Anything you do not strike becomes an issue; anything not listed dies here.**

| ID | Nature | Item |
|---|---|---|
| B-1 | bug | `factory_land.py:77` adopts any error containing "already exists" plus any URL as the pull request — no 422 check, no URL-shape check. Can exit 0 with a wrong URL. **Fix via a `create_pull_request` helper behind the seam, not in place** — the in-place patch gets thrown away. Closes B-2 too |
| B-2 | chore | Three different predicates for the same GitHub error, in three files, at three strictnesses |
| B-3 | bug | An absent or unparseable fleet file prints a Python exception class name to the operator — the exact shape a plan-phase ruling forbade. Two fix points, not one |
| B-4 | enhancement | The three missing assertions behind SC-13, SC-18, SC-19 — see D-3 |
| B-5 | bug | Repeat publish under a different `--repo` can confuse issue numbers across repositories |
| B-6 | chore | `factory_claim.py:43` resolves a path at module import, against the stated no-side-effects rule |
| B-7 | bug | `factory_config` with no `--show` prints empty output and exits 0, which breaks a JSON parse |
| B-8 | chore | A test round-trip that passes without exercising the ordering it exists to check |
| B-9 | enhancement | Record the trigger: if Projects v2 auto-add is ever enabled on the fleet board, the claim tool needs a provenance check first. Safe today only because of a board setting |
| B-10 | chore | Settle the four-file disagreement on whether a null test command blocks or is skipped — regardless of how D-1 is resolved |
| B-11 | chore | The harness prescribes a receipt path that five agent roles are not permitted to write. Hit repeatedly across this feature; already filed as #199 |
| B-12 | chore | Two `<!-- ok-stale -->` markers sit one line off from the text they exempt, so they are inert |
| B-13 | chore | Plan-phase advisories never resolved: the "edge (i)" label names two different scenarios; SC-10 declares unit evidence while the plan's own reasoning argues integration |

---

## Housekeeping

- **Run count: 23 against a budget of 20** (counted from the run directories on disk, not estimated).
  That budget is informational and never stops work. My read: eleven tasks landed with zero rework,
  every run resolved something and advanced the criteria. The count is earning its place. It is also
  a floor — the two tasks you handle directly never appear in it.
- **`check-state.sh` exits 1** with four violations. All four are old FEAT-04 and FEAT-07 digests,
  untouched since early August, unrelated to this feature. I did not repair them: the validator
  behind them is enforcement-layer code under the same carve-out as T-08. Scoped to this feature's
  paths, the check is clean.
- **Close-out was deliberately skipped.** Distillation happens once, when a feature closes. This one
  is returning for your decisions, so distilling now would mean distilling twice and overwriting.
- Documentation gate green: `check-docs.sh` exit 0 across 300 files. Suites re-measured green after
  every review run.
