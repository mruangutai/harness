# FEAT-53 metrics dashboard — plan signature review, pass 3

**All three of your pass-2 rulings are applied and verified at source. One high panel finding stands
between you and signature, and it is your own Q3 ruling applied to a third file I wrongly scoped
out.** Everything else this pass is a one-clause tidy-up you can strike or accept in a single word.

DEC-5 is closed and is not mentioned again below. The cycle-time question is settled and `B-6` is
struck.

**How this briefing was assembled.** I spawned no reporting round. I read three run digests off disk
— `runs/2026-09-02-1-product/digest.md` (the fix pass), `runs/2026-09-02-02-validator/digest.md`
(the cycle-3 panel) and `runs/2026-09-02-03-product/digest.md` (the panel transcription) — plus
`notes/research-FEAT-53-goalcheck-plan-c3.md` and the plan itself. Earlier phases stand as written in
the first two briefings and are not re-narrated here. Everything I state as measured, I measured
against disk myself.

---

## What your rulings changed

**Q1, the ordering gap — done, and verified as a graph rather than as a field.** `T-16.depends_on` is
now `[T-12, T-15, T-21]` (`plan.yaml:976-979`), and `T-16`'s intent says why, including why `T-22` is
deliberately *not* a dependency: it adapts the render gate to the suite and to CI and changes no
client source, so it cannot change the bundle's bytes (`:997-1000`). The whole 22-task graph was
walked: every `depends_on` id resolves, it is acyclic, and the topological order runs
`… T-19 → T-20 → T-21 → T-16 → T-17 → T-22`. Both cycle-3 readers independently confirmed the
closure, one of them by a mechanical graph check that also found no orphan task and no task tracing a
REQ that does not exist. `PF-45518258` is recorded `resolved`.

**Q2, cycle-time origin — Option A, done, and it needed no new ceremony after all.** The pass-2
briefing told you nothing records a BRIEF approval date machine-readably. **That was wrong, and I owe
you the correction:** `BRIEF.md`'s `## Approval` block has carried a `date:` field in the template
all along (`templates/BRIEF.md:55-59`), and it is populated in **43 of 47** BRIEFs in the main
checkout — 2 approved with an empty date, 2 still pending. The carrier being replaced,
`plan.yaml approval.date`, is populated in 31 of the same 58 feature directories. So the origin you
asked for is not merely defensible, it is **better recorded** than the one it replaces, and your
signature act does not change: you fill `status`, `approved-by` and `date` together, as you confirmed.

`D-14`, `D-19`, `D-21`, `T-06`, `T-10`, `T-11` and `T-19` all moved. Three references to the old
origin deliberately survive in live YAML and each was justified individually: `D-14`'s `because`
records the *rejected* origin, and `T-06`'s and `T-11`'s intents carry the *prohibition* ("read the
approval date out of BRIEF.md, never out of plan.yaml"). No live site measures cycle time or a
feature's start instant from the plan's approval date. **REQ-03 is delivered as written for the first
time.**

Two consequences stated rather than hidden: cycle time is **day-granular**, because the BRIEF date
carries no time of day; and the missing-date branch is **live, not theoretical** — 2 real BRIEFs
carry the empty-date form today, so those features report `null` plus a `D-19` sentence naming
`BRIEF.md`, never a zero.

**Q3, the git disposition — done for the two files you named.** New `D-22` (`plan.yaml:129-154`)
records that `.harness/metrics/instrumented_at` and each feature's `touchpoints.jsonl` are
**committed records**, never gitignored, and that the step whose execution first creates them commits
them in the same act. `T-02` states the disposition and — this is the part that matters — **gates**
it: its `verify` asserts those paths are *not* ignored, and it was shown to go red under a mutant
`.gitignore` carrying `.harness/metrics/`, so it binds the rule rather than asserting today's
accidental state. `T-20` is the single named owner of the commit step (`:1135-1141`), with `T-11`'s
fixture trees explicitly carved out.

One mechanism correction pm applied rather than spending a round trip on: `merge-gitignore.sh` strips
comment lines when it merges, so a snippet comment never reaches this repository's `.gitignore`. Both
halves you asked for — *stated* and *enforced* — are satisfied, by the sentence living in the snippet
every onboarded project receives and this repository's side being gated by `check-ignore`. I judge
that the right call.

---

## What needs your decision now

### 1. `V-1`, high — `trend.jsonl` has the hole you just ordered closed

**This is my error, not the panel's discovery of a new problem.** Your Q3 ruling was about metrics
runtime records being committed rather than left dirtying the tree. I scoped pm to the two files you
named by name and told it not to widen to `.harness/metrics/trend.jsonl`. The panel found that the
third file has **exactly the same shape**: no task, decision or lane names a committer for it, and
`D-22` now explicitly closes "no other task owns it" around the other two.

I verified the premise at source rather than adopting it on the reader's word. `T-19`'s `record_ship`
appends the ship record to `trend.jsonl` from inside `gh-sync.py`'s `cmd_ship`, and the only commit
that function makes is `_commit_terminal_station`, whose own docstring says **"ONLY THIS ONE FILE.
`git commit <path>` implies `--only`"** (`gh-sync.py:659-661`) — it commits `plan.yaml` and nothing
else. So the first real ship leaves your main checkout dirty at a path no ignore rule covers, which
is the condition `D-22`'s own reasoning says halts the next team run; and until someone commits it by
hand, every ship record REQ-10 promises to make durable lives in one working tree, where a `git
clean` destroys the lot silently.

The remedy is one sentence — name the committer in `D-22`'s `choice`, or state it in `T-19`. I did
not apply it: a panel finding never opens its own pre-signature fix cycle (DEC-207), and only you
resolve or overrule one. **Recommendation: fix.**

### 2. Four advisory findings — all one-clause, all in the same pm dispatch if you want them

Same convention: **strike a row by ID and it dies; anything not struck becomes a backlog issue
labelled `Dashboard`.** `B-1`..`B-5` and `B-7`..`B-14` stand as already accepted; `B-6` is struck as
redundant, since Q2 resolved it.

| ID | Sev | Finding | If you fix it now |
|---|---|---|---|
| B-15 | med | The BRIEF `## Approval` date parse has **two independent authors** — `T-06`'s `kpi.py` and `T-11`'s `touchpoints.py` — and neither cited precedent actually reads a date (`has_approval_block` only asserts the heading; `approved()` only greps status; `parse_brief` sections SC lines). A later edge fix lands in one file, and one payload then dates a feature for throughput while KPI 4 says that same feature cannot be dated — every gate green. This departs from the plan's own one-authority discipline (`D-19`'s siting, `resolve_window`'s "one authority, four callers") | Name one authority and have the other call it — one clause in `T-06` and one in `T-11` |
| B-16 | med | `T-06` names four gap-state branches and fixtures **only** the empty-date one (`plan.yaml:451-454`). `compute()` iterates every feature directory, so an uncaught exception on the absent-`## Approval` branch crashes the whole project's numbers for every window — not one degraded row. Fix `B-15` first: settling one parse authority makes the branches fixturable once instead of twice | Add the three missing fixture cases to `T-06` |
| B-17 | med | `T-11`'s mutating fixture cases (a `record()` append, epoch creation) state **no copy-to-temp discipline** while writing under the committed `dashboard/fixtures/` tree. Anyone running `run-unit-tests.sh` leaves untracked files under a tracked directory and the next team run halts on a dirty tree with nothing pointing at the suite. `T-10` explicitly stages its merges in separate worktrees; `T-11` says nothing, and an ignore rule cannot rescue it because `T-02`'s verify asserts `touchpoints.jsonl` is *not* ignored. Fires on every local run, deterministically | One sentence in `T-11`: mutating cases copy the fixture to a temp dir first |
| B-18 | low | `D-21`'s at-or-after predicate compares a `00:00:00Z` date-only start against an intra-day epoch, so a feature approved on the **same calendar day** the epoch was written reads as pre-instrumentation. On launch day the first instrumented feature — including the one whose own `approval_request` created the epoch — reports "touchpoints were never tracked for it" permanently while its `touchpoints.jsonl` sits on disk with lines in it. The loss is in the safe direction (`null`, never a fabricated zero) but the sentence is false | One clause in `D-21`: compare at day granularity, or take the epoch's date |

**My recommendation: fix all five in one pm dispatch, including `V-1`.** Every one is a sentence or a
clause in an already-drafted task or decision, none needs new design, and the plan is unsigned so
nothing has to be re-approved afterwards. That costs one cycle and one panel re-read. Strike anything
you would rather carry.

---

## What the panel confirmed rather than found

Recorded because a gate that only ever reports problems tells you nothing when it is quiet.

- **`T-16`/`PF-45518258` is closed.** Both readers independently; the graph check shows `T-16`
  transitively covers every client-source task via `T-04 → T-13 → T-14 → T-15 → T-21 → T-16`, and
  both confirm `T-17`, `T-19`, `T-20` and `T-22` touch no client source.
- **Ruling 2 holds end to end.** Both readers independently found exactly the three sanctioned
  survivors and **no rule stated twice-and-differently** across the seven changed sites — which is
  the specific failure `D-19` exists because of.
- **`T-02`'s `D-22` gate is discriminating, not decorative** — it reddens under a mutant
  `.gitignore`. That retires the "asserts today's accidental state" worry for the two paths it
  covers. `V-1` is the third path it does not cover.
- **The out-of-scope list held with zero violations.** Neither reader re-raised DEC-5, the stale
  comment block, `B-13`, `B-14`, `B-6` or the pending approval status.
- **`plan.yaml`, `BRIEF.md`, `feature.json` and `STATE.md` were byte-identical before and after the
  panel** — I checked with `git diff`, since the lead holds no Bash and correctly said it could not.

---

## Harness defects found this pass

Not about this feature; each cost real time.

1. **BUG-1080 reproduced again on the yield path.** `validate-digest.py` rejects every `code_grade`
   value for a plan-phase feature with no `review_sha` — any enum value gives "cannot be bound to
   review_sha", absence gives "missing code_grade" — so `harness-code-reviewer` could not
   terminal-yield and returned its digest in-band. Third occurrence across two cycles.
2. **A recorded digest cannot be replaced (DEC-208), so a run that needs to rewrite its own digest
   consumes a second run directory.** The cycle-3 panel occupies `2026-09-02-01-validator` (a
   superseded first draft) and `2026-09-02-02-validator` (canonical). One run, two directories, and
   nothing on disk says which is which without reading both.
3. The worktree-vendored `.claude/skills` problem recurred as expected — `set-panel` is unreachable
   in-tree, so the main checkout's binary was run against the worktree's `plan.yaml` by absolute
   path. Same tool, same lock, same single write route.

---

## Budgets, honestly

**15 runs against an informational budget of 20; 7 rework cycles against a hard 10.** One cycle was
added this pass: the fix pass itself, which is rework by definition since it descends from a panel
FAIL you routed back.

**One cycle I did not count, and you should know why.** The first `harness-pm` dispatch died at
11m43s on a host `overloaded_error` after 10 retries, and the lead reported it as a cycle. It applied
nothing — `plan.yaml` was verified byte-unchanged before re-dispatch — and no send-back was issued on
the work itself. DEC-157 defines rework as a FAIL routed back, an unmet-SC re-dispatch, or a
send-back; a host failure is none of those. Counting it would move the meter that can block this
feature for an infrastructure retry. I recorded 7, not 8.

If you accept the recommendation above, the fix pass and its panel re-read put this at 8 of 10 before
signature. That is enough, but it is not roomy, and a second round of findings after that one would
be the point at which I would come back to you rather than spend the last cycle.

---

## What I need from you

1. **`V-1` — fix, or overrule.** It gates the signature (DEC-207); nothing else does.
2. **`B-15`..`B-18` — strike any, or accept.** My recommendation is to fix all four alongside `V-1`
   in the single consolidated dispatch.

Then the main session signs `BRIEF.md` — `status`, `approved-by` **and** `date`, since `date` is now
load-bearing — and `plan.yaml`, and the build phase starts.
