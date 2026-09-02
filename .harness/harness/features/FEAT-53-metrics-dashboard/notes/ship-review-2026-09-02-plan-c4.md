# FEAT-53 metrics dashboard — plan signature review, pass 4

**All three of your pass-3 rulings are applied and verified at source, and for the first time the
panel gates nothing. `severity_max: med`, `must_fix: []` — the plan is signature-ready as it
stands.** V-1 and B-15..B-18 are closed in the amended fields, not merely summarised; the seventh
KPI is complete end to end from requirement to CI gate; the accuracy KPI appears nowhere.

**Two things need you before you sign, and only one of them is about this plan.**

1. **The cycle budget is the real problem, not the findings.** 9 of a hard 10 cycles are spent, all
   of them in the PLAN phase, with 22 tasks of build, a validation phase and a ship phase still
   ahead. Signing at 9/10 gives the entire build ONE rework cycle. It will exhaust on the first
   send-back and this feature will go `BLOCKED` with nothing wrong.
2. **Seven new advisory findings**, none gating. Six are one-clause edits; one is larger. Under your
   own pass-3 ruling I did not spend cycle 10 on them — they come to you instead.

DEC-5 is closed and is not re-litigated below. The accuracy / handoff-eval KPI is out of scope and
was verified absent by regex over all three artifacts.

**How this briefing was assembled.** I spawned no reporting round. I read three run digests off disk
— `runs/2026-09-02-04-product/digest.md` (the fix pass), `runs/2026-09-02-05-validator/digest.md`
(the cycle-4 panel) and `runs/2026-09-02-06-product/digest.md` (the panel transcription) — plus
`notes/research-FEAT-53-goalcheck-plan-c4.md`, `notes/review-harness-code-reviewer-planpanel-c4.md`
and the plan itself. Passes 1–3 stand as written in the three earlier briefings and are not
re-narrated. Everything I state as measured, I measured against disk myself.

---

## What your rulings changed

**Q1, `V-1` — closed, and closed wider than the finding.** `D-22`'s `choice` went from two runtime
files to **three**: `instrumented_at`, each feature's `touchpoints.jsonl`, and now
`.harness/metrics/trend.jsonl`, each with a named committer. For the trend log that committer is the
`record_ship` call `T-19` adds to `gh-sync.py`'s `cmd_ship` — the append and its commit are one act,
wrapped non-fatally exactly as the append is, so a metrics write still cannot be what stops a feature
from landing. `plan.yaml`'s `lanes:` block gained a `.harness/metrics/trend.jsonl` row. Both readers
graded it closed at source.

**Q2, `B-15`..`B-18` — all four closed.**

- **B-15**: one authority. `T-06` now creates `.claude/skills/harness/bin/brief_approval.py` exposing
  `approval_date(feature_dir) -> (value, reason)`; `kpi.py` and `touchpoints.py`'s `feature_start`
  both **call** it and are forbidden to restate the parse; `D-14` records the rule as "one authority,
  two callers". I constrained the placement rather than leaving it open, because only one option
  survives: `touchpoints.py` may not reach into `bin/dashboard/` (its own rule), and `kpi.py` already
  imports `touchpoints.py`, so either file as the authority produces an import cycle or a task-graph
  cycle. A third module under `bin/`, created by the one task with no dependencies, is the only shape
  that works. The panel confirmed no cycle in either direction.
- **B-16**: `T-06` now fixtures all **four** gap states — no BRIEF, no Approval section, status not
  approved, approved with an empty date — as four separate assertions with four sentences asserted to
  differ. An aggregate comparison is explicitly forbidden.
- **B-17**: `T-11`'s writing cases `copytree` to a `TemporaryDirectory`; read-only cases must *not*
  copy; and a recursive digest of `dashboard/fixtures/` before and after is asserted equal as its own
  case.
- **B-18**: `D-21` and `T-11` branch 3 now both reduce **both sides to their UTC calendar date**, so
  a feature approved the same day the epoch was written is post-instrumentation. `T-06`'s general
  "date-only reads as `00:00:00Z`" rule survives with this named as its sole scoped exception, and
  the same-calendar-day case is fixtured.

**Q3, the seventh KPI — complete end to end.** REQ-15 → SC-19 (`automated`/`integration`) and SC-20
(`inspection`) → weekly buckets in `T-10` → tile and panel 7 in `T-14` on a 3×3 grid → the third
gated mount in `T-21` → suite and CI reachability in `T-22`, with the render-gate label byte-identical
on both sides. Three properties I asked the panel to check specifically, all confirmed: an empty week
is `null` with the verbatim reason `no ship record in the week of <YYYY-MM-DD>`, asserted to be
neither `0` nor `"0"`; the bucket rule **reuses** `kpi.resolve_window` rather than restating a window
boundary; and **no third chart shape was introduced** — Shape B is reused, so `T-18`'s capability
probe and `D-08`'s alpha risk are untouched by this addition.

The count is honest about what it counts: a shipped feature whose record carries no `pr` still counts
as one merged PR, and the tile says so as persistent inline text, the same discipline REQ-05 already
requires of escaped defects.

---

## What needs your decision

### 1. The cycle budget — this is the one that matters

| | Used | Budget | Teeth |
|---|---|---|---|
| Rework cycles | **9** | 10 | **HARD** — exhausting it stops the feature |
| Runs | 18 | 20 | informational only |

Two of this pass's cycles were send-backs inside the fix run, and both were **my** under-specification
rather than member error: the first dispatch's field allowlist omitted `T-22.intent` and every
`traces` list, and the grid-literal consequence surfaced one step late. I record them as rework
anyway, because DEC-157 counts send-backs regardless of fault and softening that is exactly the
record-falsification the constitution forbids.

The arithmetic: four plan cycles have consumed 9 of 10, and **the build has not started**. Twenty-two
tasks, a QA matrix gate, a simplify pass, a review panel and a ship phase are all still ahead, and
they get one cycle between them.

**Recommendation: raise `max_total_cycles` before signing.** Raising a budget is your decision and
gets recorded in `feature.json` (DEC-157). I would put it at **20**, which prices the build phase the
way the plan phase actually priced out rather than optimistically. Say a number and I will record it;
say no and I will run the build against 1 remaining cycle and report `BLOCKED` the moment it goes.

The 18 runs against 20 is informational and I am not asking you to move it — but for the record, the
runs still earn their place: each of the four plan cycles closed findings that the next cycle
confirmed closed, and the panel has found genuinely new defects every time rather than re-finding old
ones.

### 2. Seven advisory findings — none gates

Same convention: **strike a row by ID and it dies; anything not struck becomes a backlog issue
labelled `Dashboard`.** `B-1`..`B-5`, `B-7`..`B-10` and `B-12`..`B-14` stand as already accepted.
`B-6` is struck. `B-15`..`B-18` are fixed and gone.

| ID | Sev | Finding | Fix now? |
|---|---|---|---|
| B-19 | med | **`V-1`'s commit path can never be observed succeeding.** `T-19`'s simulated-ship test runs in a `copytree` temp dir that is not a git repository, so `record_ship`'s new commit only ever exercises its non-fatal *failure* branch. The plan defect V-1 named is closed; what remains is that no gate ever sees the commit work. The build-phase QA gate can still catch it, which is why the panel settled this at med after considering high | one `T-19` case that `git init`s the temp copy and asserts the copy's tree is clean with `trend.jsonl` tracked |
| B-20 | med | **Nothing defines what a week is.** `T-10` says walk the weeks from the start `resolve_window` returns, but `resolve_window` is `generated_at`-relative for `30d`/`90d` and `all` is *unfiltered*, returning no start at all. A builder must invent the answer, and the plan's own discipline is that an invented rule is a rule nobody approved. This is the one I would fix regardless of the others | one clause in `T-10`: UTC ISO weeks, `all` anchored at the earliest record's week |
| B-21 | med | **The record presents two of your own rulings as still open.** `D-08.choice` still says the alpha fallback is "an operator decision outstanding at signature" and `D-20.because` plus BRIEF `## Constraints` still say the client build "needs an explicit yes or no at signature" — both of which you ruled on 2026-09-01 (keep the build; accept the alpha with a documented rollback). `DESIGN.md:250` also still names the dead `react-charts` as the second fallback, contradicting BRIEF. The build is unaffected; the *record* is wrong, and the rollback you accepted is named nowhere | **larger than one clause** — four fields across `D-08`, `D-20`, two BRIEF bullets and DESIGN C-2 |
| B-22 | med | **Four accepted backlog rows have no carrier.** `B-7`..`B-10` were accepted in pass 1 and exist only in that pass's immutable briefing; `B-1`..`B-5` and `B-12`..`B-14` survive as panel dispositions with a filing instruction. `B-7` is substantive off this repository — pruned branches null half of KPI 1 | one clause naming `B-7`..`B-10` wherever the others are filed at ship |
| B-23 | low | `SC-13` asserts both the escaped-defect count *and* "that rule is stated in the UI beside the number" under `verify: automated` / `evidence: unit`. The UI half has no gate, and BRIEF's own verification-gaps section claims no SC does this | move the UI clause into `SC-15`'s inspection scope, or narrow `SC-13` to the count |
| B-24 | low | BRIEF `## Verification gaps` and `T-07.intent` justify not grepping the bare token `12` by saying it occurs inside `1024`, `3x3` and `ES2022`. It occurs in none of them; the real carriers are `127.0.0.1` and `122`. The conclusion survives — `12` genuinely cannot be greped bare — but two artifacts cite false evidence for it. Pre-existing, not caused by this cycle | one clause in each artifact naming the true carriers |
| B-25 | low | `T-05`'s contract was updated to the 3×3 seven-tile grid, but the committed prototype it points at is a six-tile 3×2 build that no one has ever rendered, and `T-05`'s verify cannot detect the divergence — while `T-05`'s own intent says a diverging artifact "is a finding for the plan". DEC-5 is closed and stays closed; this is about the task's contract, not about reopening the gate | one clause in `T-05` recording the six-tile artifact as accepted under DEC-5's closure |

**My recommendation, and I am deliberately not choosing for you.** If you raise the cycle budget,
spend one cycle on **B-19, B-20, B-21, B-22, B-24** together — five edits, one dispatch, one panel
re-read — and carry B-23 and B-25 as backlog. B-20 is underspecification a builder must guess at;
B-21 is your own record reading wrong. If you keep the budget at 10, **fix nothing** and sign: none
of these gates, and spending the last cycle here would leave the build with zero.

---

## What the panel confirmed rather than found

Recorded because a gate that only reports problems tells you nothing when it is quiet.

- **All five prior findings closed at source**, each cited to the field read, by both readers
  independently. Both readers ran; neither was skipped.
- **The REQ/SC tracing, the `depends_on` order and a files-vs-intent sweep across all 22 tasks came
  back clean.** I re-derived the graph mechanically myself rather than accepting it: 22 tasks, every
  `depends_on` id resolves, acyclic, and all 15 REQs are traced by at least one task.
- **No third chart shape, no new capability row** — the seventh KPI cost the alpha-charting risk
  nothing.
- **Zero out-of-scope violations.** Neither reader re-raised DEC-5, `B-13`, `B-14` or the pending
  approval status, and the accuracy KPI was confirmed absent by regex over `BRIEF.md`, `DESIGN.md`
  and `plan.yaml`.
- **`approval:` and `## Approval` are byte-unchanged and still `pending`** across all three runs — I
  verified both directly. Only you sign.

**What the panel could not tell you, in its own words:** nothing here could be falsified, because
nothing is built. Every grading is a document-consistency judgement, and a plan that reads correctly
and builds wrong is outside what this gate detects. Both readers grading the five closures CLOSED is
also weaker evidence than it looks — they read the same amended fields, written to close exactly
those findings. The independent signal is the seven new findings, where the two readers overlapped on
only two.

---

## Harness defects found this pass

Not about this feature; each cost real time.

1. **A subagent returned a well-formed `VERDICT: PASS` digest with its artifact verified on disk,
   while the host reported the job as `failed (exit 1)`.** A lead routing on the exit code rather
   than on the digest would have recorded a spurious FAIL and burned a cycle re-running clean work.
2. **The worktree-vendored `.claude/skills` copy of `plan-merge.py` is stale again** — it predates
   `set-panel` and `--yaml-value`, so every list-field amend and the panel write had to run the main
   checkout's binary against the worktree's `plan.yaml` by absolute path. Same tool, same lock, same
   single write route, but it is the third feature in a row to hit it.
3. **`git diff --stat` cannot be used as an acceptance criterion inside a live feature dir.** I set
   one ("plan.yaml is the only changed file") and it was correctly reported unmeetable: it grades the
   tree, not the change, and the tree carries every earlier uncommitted cycle-4 edit. My error, noted
   so the next dispatch does not repeat it.

---

## What I need from you

1. **The cycle budget — raise it, or confirm 10.** This is the one that decides whether the build
   phase can run at all.
2. **`B-19`..`B-25` — strike any, fix any, or accept all as backlog.** Nothing here gates; my
   recommendation is above and depends on your answer to (1).

Then the main session signs `BRIEF.md` — `status`, `approved-by` **and** `date`, since `date` is
load-bearing for cycle time — and `plan.yaml`, and the build phase starts.
