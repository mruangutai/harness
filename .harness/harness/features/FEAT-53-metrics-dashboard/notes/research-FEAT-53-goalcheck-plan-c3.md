# Goal-check — FEAT-53 plan after the pass-2 rulings — 2026-09-02

**Does this plan deliver the operator's stated intent? Yes, on all three rulings, and REQ-03 is now
delivered as stated.** Scope of this check: what the pass-2 fix touched, plus what it reaches. No
finding is manufactured below; two disclosures are named because they are consequences, not gaps.

## REQ-03 — delivered as stated, for the first time

BRIEF REQ-03 (`BRIEF.md:29`) says "elapsed time from BRIEF approval to ship". The grilling says the
same (`.harness/notes/grilling-metrics-dashboard-2026-09-01.md:26`). Before this pass, D-14, T-06,
D-21, T-10 and T-19 all measured from `plan.yaml approval.date` — a different quantity. They now
measure from the feature's `BRIEF.md` `## Approval` `date:`, the field the main session already fills
at the existing signature act. No new field, no new ceremony, no REQ reworded.

The grilling left this as open fog — "exactly how the orchestrator sources when this feature's BRIEF
was approved ... since no structured approval timestamp exists anywhere today" (`:103-104`). That
premise was wrong, and the fix is what disproves it: measured 2026-09-02 in the main checkout at
`e74e0880`, 43 of 47 `BRIEF.md` files already carry `status: approved` with a `YYYY-MM-DD` date. The
carrier existed; nobody had looked. It is better populated than the one it replaces (31 of the same
58 feature directories carry a dated plan-side approval). The fog item is closed, not deferred.

**Two disclosures, both handled honestly, neither a gap:**
- **Day granularity.** The BRIEF date carries no time of day, so cycle time is days, and D-14 says
  so. REQ-03 asks for elapsed time from an act the operator performs once a day at most; a day is a
  fidelity limit on the right quantity, not a proxy for a different one.
- **The missing-date branch is live, not theoretical.** 2 of 47 BRIEFs are approved with an empty
  date. Those features report `null` plus a D-19 specific sentence — never 0. T-06 now names that
  case and builds a fixture for it, so REQ-11's honesty contract covers the new carrier too.

## Ruling 1 — the bundle can no longer ship chartless

`T-16 depends_on: [T-12, T-15, T-21]`. The graph is acyclic, every dependency id resolves, and in the
topological order `T-21 -> T-16 -> T-17` — the last by a real edge (`T-17 depends_on: [T-16]`), not
by luck of ordering. T-16's intent now says why, and says why T-22 is deliberately *not* the
dependency: T-22 adapts the render gate to the suite and CI and changes no client source, so it
cannot change the bundle's bytes. The DEC-4 defect the operator refused to ship twice is closed at
the only place that closes it — the scheduler's own field.

## Ruling 3 — the disposition is stated, gated, and has exactly one owner

D-22 records it: `.harness/metrics/instrumented_at` and each feature's `touchpoints.jsonl` are
committed records, and the step whose execution first creates them commits them in the same act.
That step is T-20, named as the sole owner in its own intent. This is the operator's own grilling
argument (`:64-68`: a durable record must survive worktree reclamation, so it must be git-committed)
applied to the two files that argument had missed.

The commit rides the instruction T-20 writes rather than a task that seeds the epoch, because D-21
gives `record()` sole authorship of the epoch — a task-authored seed would add a second writer to
the one marker separating a tracked project from an untracked one. That is the weakest form that
satisfies both constraints (tree not dirty; a second clone keeps the epoch), which is why it was
chosen over the seeding shape.

**One correction to the ruling's stated mechanism, applied rather than raised:** a comment in
`templates/gitignore.snippet` does *not* reach this repo's `.gitignore`. `merge-gitignore.sh` merges
only rule lines and greps comments out. So the sentence lives in the snippet (the distributed copy
every project receives) and T-02's verify gates the repo side by asserting `git check-ignore` matches
neither path — a stated disposition *and* a gate, which is what the ruling asked for. Both halves
discriminate: the snippet greps exit 1 today, and the check-ignore assertion reddens under a mutant
`.gitignore` carrying `.harness/metrics/`.

`.harness/metrics/trend.jsonl` is deliberately not widened into D-22: its only write is the
user-gated ship step, which is already a commit boundary, and the ruling named two paths.

## The one contradiction that remains, and is meant to

The ~250 spliced `#` comment lines still quote the *old* predicate — `plan.yaml approval.date` at
`plan.yaml:1373`, re-derived at final state — and now contradict the live YAML on the cycle-time
origin as well as the two ways already
recorded. That is backlog row B-12, accepted by the operator, unfixable until the `plan-merge.py`
tool defect is fixed. No new comment line was added by this pass (191 before, 191 after). A reader
must take the YAML, never the comments.

`B-6` needed no plan edit: no live-YAML row for it exists. It lives in the cycle-1 review record
(`ship-review-2026-09-01-plan.md:125`, an immutable shipped artifact) and in `STATE.md:28-30`, which
is the orchestrator's file. Ruling 2 resolves its substance, so it is struck by being answered.
