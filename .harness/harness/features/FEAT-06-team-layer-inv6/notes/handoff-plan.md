# Handoff — FEAT-06, plan → build — written at 635ef14, seq-2 (supersedes seq-1)

## Next

**Stop and wait for the user's signature.** BRIEF.md and PLAN.md are both `status: pending` and are
signed TOGETHER, in one act; only the main session writes `## Approval`. Nothing else in this phase
is outstanding — there is no open `must_fix` and no open question.

**After signature**, the build phase opens with `gh-sync.py open <feature-dir>` and then PLAN's
topological order at `PLAN.md:23`. Note the shape before dispatching: **9 of 10 tasks are
main-session-direct or carve-out**, and **T-08 is the only squad-dispatched task** (product squad,
`harness-documentor`, `docs/**`). A build-team dispatch is not the default here.

## Trust

- All six AMF findings fixed AND independently re-verified at source by the eng delta review —
  `runs/delta-review-eng/digest.md` — verified-at 635ef14
- DMF-1 closed; T-02's clause is a predicated general SWEEP and its protect-list carve is
  categorical, so the two cannot contradict at execution — `PLAN.md:301-315`, `:320-323`, read
  directly by the orchestrator — verified-at 635ef14
- `review.yaml` is byte-unchanged; the routing wall held through three squad runs. All four
  count-bearing comments (`:8`, `:9`, `:19`, `:62`) are still present for T-02 to correct —
  `git status --porcelain` + grep — verified-at 635ef14
- SC-14's predicate is an 8-consecutive-line sliding window, RED exit 1 at `635ef14` and GREEN
  exit 0 with T-11's passage — measured twice, by pm and independently by the reviewer — verified
- `PLACEHOLDER_UNSET` is an ORDERED TUPLE at `PLAN.md:234`, byte-identical to
  `validate-digest.py:472`. A `set` would make the `json.dumps` join order arbitrary and match 0 —
  verified-at 635ef14
- Cost 170.17 MEASURED against a 160 budget — **over by 10.17**; 182-215 band-inclusive. The
  segment-1 band will never be measured (transcript window aged) — `feature.yaml` cost_note — verified
- **PLAN.md line anchors older than DMF-1 are STALE**: +8 through T-02's middle, +9 below the carve.
  Cite T-02 fields by NAME — `feature.yaml` anchor_note — verified-at 635ef14

## Dead ends

- Do NOT re-review the plan in any form. A full architecture pass (28.19) plus a scoped delta
  (22.19) both ran; the user has spent three gates on this phase — `runs/arch-review-eng/digest.md`,
  `runs/delta-review-eng/digest.md` — verified-at 635ef14
- Do NOT re-open the re-scope, D-01..D-08, the 15 SCs' intent, the 10-task shape or retired T-03.
  All cleared by the full pass — same digests — verified-at 635ef14
- Do NOT action the ten advisories, AQ-2 or MF-1 as build work — they are backlog for the user's
  ship acceptance — `feature.yaml` pending — verified-at 635ef14
- Do NOT re-derive issues #10, #19, #20 or the routing wall — filed, out of scope — verified
- Do NOT read `runs/plan-eng/` or `runs/replan-product/` — archive, superseded by the arch review

## Working set

- `.harness/features/FEAT-06-team-layer-inv6/PLAN.md`
- `.harness/features/FEAT-06-team-layer-inv6/BRIEF.md`
- `.harness/features/FEAT-06-team-layer-inv6/feature.yaml`
- `.harness/features/FEAT-06-team-layer-inv6/runs/delta-review-eng/digest.md`
- `.harness/features/FEAT-06-team-layer-inv6/notes/answers-arch-review-eng.md`
