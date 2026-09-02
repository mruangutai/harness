# EFFICIENCY angle — FEAT-53 plan review (segment B)

**BLUF: projected per-request total ≈ 4.3s–5.3s against T-12's 5.0s ceiling — straddles it, and the
efficient-implementation low end already leaves under 15% margin.** The high end (naive but
plan-consistent implementation) already breaches. This is a blocking finding: at this repo's *current*
scale, not 10x, the ceiling is already at risk, and D-06's own cited 1.1s baseline looks stale against
what T-06 through T-09 actually specify.

## 1. Per-request cost, item by item (measured, this repo, 2026-09-01)

| item | task | mechanism | measured/extrapolated cost |
|---|---|---|---|
| tracked .py file count | — | `git ls-files '*.py' \| wc -l` | **106** files |
| code-grade.py --json over all 106 | T-07 | `time python3 code-grade.py --json $(git ls-files '*.py')` | **1.00s** (measured, stable across 2 runs: 1.004s, 1.003s) |
| BUG-NN feature dirs | T-08 | `find .harness -type d -name 'BUG-*'` | **8** dirs |
| `git log --diff-filter=A` ×8 dirs | T-08 | timed loop | **0.22s** |
| full-history `git log` (Revert scan) | T-08 | `time git log --format=...` | **0.03s** — total T-08 **≈0.26s** |
| features with a real (non-`none`) branch | T-06 | `feature.json` scan, 51 files | **47** of 51 |
| `git diff --numstat` over merge range ×47 branches | T-06 | timed loop, two implementations tried | **1.6s** (single-call `main...branch`, 33.5ms/branch measured on 36 live branches, extrapolated to 47) to **2.6s** (merge-base + diff, two calls/branch, 56ms/branch measured) |
| `plan.yaml` parse ×51 (T-06's own per-feature scan for `approval.date`) | T-06 | `yaml.safe_load` timed, 12.4ms/parse average over 63 parses | **≈0.63s** |
| t-NN-prefixed commits needing a plan.yaml + agent-.md lookup | T-09 | counted via `git log --format=%s` + regex on `[harness:...]` tokens | **63** of 978 commits |
| 63 further plan.yaml re-parses (T-09, if uncached) | T-09 | same 12.4ms/parse rate | **≈0.78s** |
| 63 agent-.md reads | T-09 | `pathlib.read_text` timed | **0.004s** (negligible) |
| trend.jsonl / touchpoints.jsonl reads (T-10/T-11) | T-10/T-11 | small per-feature files, ≤51 opens | unmeasured, bounded — well under 0.1s by file-size analogy to the agent-md reads above |

**T-06 core (branch diffs + its own plan.yaml scan): 2.2s (efficient) to 3.2s (naive).**

**Honest total: 2.2+1.0+0.26+0.78+~0.05 ≈ 4.3s (efficient impl) to 3.2+1.0+0.26+0.78+~0.05 ≈ 5.3s
(naive impl, but still exactly what the intents as written specify).** Against the 5.0s ceiling
T-12's own verify asserts, this is a **likely breach** at the naive end and a **>85%-utilized, near-zero
margin** at the efficient end — before JSON serialization or HTTP response overhead is even counted.
**This makes T-12's own verify a flaky gate**, as the dispatch anticipated: pass or fail will hinge on
which of two equally-plan-consistent implementations T-06 picks, and on machine load at test time.

**Discrepancy worth flagging on its own:** D-06 cites "about 1.1 seconds... measured on 2026-09-01,"
the same date as this review, at "50 feature.json files" — essentially today's scale. But T-06's own
intent already specifies the git-diff-per-branch work costed above (2.2–3.2s), which alone is 2–3x the
cited baseline. Either the 1.1s baseline was taken before change-size computation was written into
T-06's intent, or it used a materially cheaper mechanism than "git diff --numstat over the feature
branch's merge range" as literally specified. Either way, the number D-06 leans on does not match what
D-06's own task requires.

## 2. Growth (10x: 540 features, ~10k commits, 1000 .py files)

Projected, scaling each measured term by its own driver:

- **T-06 (branch diffs) dominates**: 540/47 × 1.6–2.6s ≈ **18–30s**. This is also likely an
  underestimate at 10x, since older/larger feature branches tend to carry bigger diffs.
- T-07 (code-grade.py): 1000/106 × 1.00s ≈ **9.4s** — second-largest term, and it alone already
  breaches 5.0s at 10x.
- T-09 (uncached plan.yaml re-parse): commits scale ~10x → ~644 lookups × 12.4ms ≈ **8s**.
- T-08: BUG-dir loop scales to ~80 dirs ≈ 2.6s; full-log scan stays cheap (~0.3s).

Sum at 10x ≈ **45–50s**. Growth is **worse than any single linear term** because features, tracked
files, and commits all grow together as the project matures, and three independent terms (T-06, T-07,
T-09) each scale with a different one of those three counts simultaneously.

**Concrete scale where D-09's deferral stops being right:** it already has, or is about to, at
**current** scale. The honest total (4.3–5.3s) is already 86–106% of the 5.0s ceiling at 47 real
branches / 106 tracked .py files / 978 commits. Do not re-litigate D-09 — but the next 10–20 features
shipped (roughly 55–60 features, ~115–125 tracked .py files, ~1,050–1,100 commits — about 10–20% more
than today) would push the sum solidly past 5.0s under *any* implementation choice, not just the naive
one. That is a near-term, not a 10x-out, threshold.

## 3. Repeated I/O across tasks

Six tasks (T-06/07/08/09/10/11) each independently reach for the feature tree or git log, but most of
that is cheap (filesystem globs, single small reads) and not worth flagging. Two things are worth
naming, one blocking, one not:

- **[blocking, folded into §1's total] T-06 already parses every feature's plan.yaml (51 opens,
  ~0.63s) to get `approval.date`. T-09's `by_tier()` then independently re-opens plan.yaml for up to
  63 more commit lookups (~0.78s) — the same files, keyed by the same `feature_id`, with no caching
  named in either intent.** Concrete cost: ~0.78s, or roughly 15–18% of the total request budget, is
  pure redundant I/O for data T-06 already holds in memory when the payload is assembled by one
  `kpi.compute()` call. Alternative: T-09's intent should require either (a) reusing the per-feature
  `approval`/plan data T-06 already parsed, keyed by `feature_id`, or at minimum (b) a local
  memoization inside `by_tier()` itself so the same feature's plan.yaml is parsed once even if many
  commits resolve to it (63 commits are very unlikely to touch 63 distinct features, out of 51 total).
  `changes_task_set: no`. `remedy_cost: amend` — this is a text change to T-09's intent describing the
  same function signature and files; it does not touch `depends_on:` or `files:`.
- **[cleared] T-08 and T-09 both perform an independent full-history `git log` walk** (T-08 for the
  Revert scan, T-09 for commit-prefix resolution over the window). Measured duplicate-walk cost:
  **0.03s** — negligible against the ~5s budget. Not flagged; this is exactly the "fraction of a
  second" case the skill says not to flag.

## 4. Gate frequency

All 17 tasks' `verify:` clauses are one-shot build-time checks, run once at task completion — none
execute at session entry, per-write, or per-commit. The only genuinely repeated hot path in this whole
feature is the dashboard's own per-HTTP-request `kpi.compute()`, already costed in full in §1.

**T-13/T-14/T-15/T-16's four separate `npm run build` calls: cleared, not flagged.** Unmeasured
directly per the dispatch's constraint (no npm install/build has been run anywhere in this checkout —
no `dist/`, no `node_modules/` exist yet, so there is no prior build to time). Each of the four builds
gates a different task's own newly-added source (T-13: shell/routing; T-14: tiles/panels/gapstates/
tables; T-15: charts; T-16: the final commit-the-bundle step), each runs once at that task's own
completion, and none of them run at session entry, per-write, or per-commit. This is exactly the
skill's "deliberate full runs at boundary steps are not waste" carve-out, not duplicated work.

## Findings summary

- **EFF-1** — location: D-06 (choice text) / T-12 `verify:` (the 5.0s assertion) / T-06 intent (the
  git-diff-per-branch mechanism). Summary: honest projected per-request total is 4.3–5.3s against a
  5.0s ceiling, at current repo scale, not 10x. Concrete cost: T-12's verify becomes a flaky gate whose
  pass/fail depends on which equally-valid implementation T-06 picks and on machine load; D-06's own
  1.1s baseline does not match what D-06's task actually specifies. Alternative: either T-06's intent
  names the single-subprocess-per-branch form explicitly (`git diff --numstat main...branch`, ~1.6s
  measured, not the two-call merge-base+diff form), which buys back ~1s of margin, or D-09's cache
  deferral is revisited now rather than at 10x. `changes_task_set: no` for the first remedy (text-only
  guidance on which git invocation to use); a revisit of D-09 would be a decision change, not mine to
  propose the shape of. `remedy_cost: amend` for the git-invocation guidance in T-06's intent.
- **EFF-2** — location: T-09 intent (`by_tier()`). Summary: redundant plan.yaml re-parsing described in
  §3. Concrete cost: ~0.78s, ~15–18% of the total budget, avoidable. Alternative: memoize plan.yaml
  parses by `feature_id` inside `by_tier()`, or reuse T-06's already-parsed per-feature data.
  `changes_task_set: no`. `remedy_cost: amend`.

## Cleared (measured, not flagged)

- T-08/T-09's duplicate full-history `git log` walk: 0.03s, negligible.
- T-13/T-14/T-15/T-16's four separate `npm run build` calls: deliberate boundary-step full builds, one
  per task at completion, never per-session/write/commit — unmeasured directly (no build artifacts
  exist yet in this checkout) but structurally exempt under the skill's own carve-out.
- All 17 tasks' `verify:` clauses: one-shot, task-build-time only. No per-session/write/commit gates
  exist anywhere in this plan outside the dashboard's own per-request recompute (covered by EFF-1).

## Commands run (for re-derivation)

```
git -C <root> ls-files '*.py' | wc -l                                   # 106
git -C <root> ls-files | grep -oE '\.harness/[^/]+/features/BUG-[0-9]+' | sort -u | wc -l  # undercounts; use find
find <root>/.harness -maxdepth 3 -type d -name 'BUG-*' | wc -l          # 8
git -C <root> log --oneline | wc -l                                     # 978
cd <root> && time python3 .claude/skills/harness/bin/code-grade.py --json $(git ls-files '*.py') > /tmp/cg_out.json
cd <root> && time (for d in .harness/harness/features/BUG-*; do git log --diff-filter=A --format=%aI -1 -- "$d" >/dev/null; done)
cd <root> && time git log --format=%H%x09%aI%x09%s > /tmp/full_log.txt; grep -c '\tRevert ' /tmp/full_log.txt
python3 -c "... count feature.json branch fields via glob('.harness/*/features/*/feature.json') ..."   # 47 of 51 real
cd <root> && time (for b in $(git branch -a | grep 'feat/FEAT'); do git diff --numstat "main...$b" >/dev/null 2>&1; done)   # 36 live branches, 1.205s
cd <root> && time (for b in $(git branch -a | grep 'feat/FEAT'); do mb=$(git merge-base main "$b"); git diff --numstat "$mb" "$b" >/dev/null 2>&1; done)  # 2.0s
python3 -c "... yaml.safe_load timing over glob('.harness/harness/features/*/plan.yaml'), 63 iterations ..."   # 0.781s
python3 -c "... git log --format=%s, regex ^\[harness:(...)\], count t-NN tokens ..."  # 63 of 978
```

## Non-goals honored

No correctness findings raised (T-06/T-08/T-12 verify gaps, T-15 dead-fallback, T-12 depends_on
omission, T-15 dispatch mismatch, trend/touchpoints write-path orphans) — all already in the batch,
none re-raised here.
