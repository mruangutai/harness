# SIMPLIFY — angle EFFICIENCY — FEAT-55

BLUF: **0 apply-worthy EFFICIENCY findings.** Largest measured/bounded cost: the per-issue
type-apply path (`apply_issue_type`) costs 2 `gh` subprocess invocations per issue typed this
run — bounded floor ≥ 21.7ms/invocation (measured locally, no-network `gh --version` spawn,
n=20) — but it is a one-shot cost per issue's entire lifetime (never re-applied once promoted
to `True`), which the dispatch's own criteria explicitly exclude from "waste."

## Per-run / per-issue `gh` invocation counts (derived by reading call sites, not estimated)

- **Capability query** (`detect_issue_types` / `factory_gh.detect_issue_types`): exactly **1**
  `gh api graphql` call per `gh-sync.py` invocation (call site `gh-sync.py:1116`, inside
  `cmd_open`; also 1 per `cmd_backlog` at `gh-sync.py:1727`) and exactly **1** per
  `factory_decompose.py` invocation (`factory_decompose.py:507`, inside `_main`). Confirmed by
  grepping every call site of `detect_issue_types(` in both files — one call site per command
  function, none inside a per-task loop. **Does not scale per issue.** No change vs. what a
  correctly-written probe should cost; this did not regress.
- **Node-id lookup + type-apply mutation** (`apply_issue_type`, `gh-sync.py:980-986` /
  `factory_gh.py:226-231`): **2** `gh` invocations (1 REST `gh api repos/.../issues/N --jq
  .node_id`, 1 GraphQL `gh api graphql` mutation) **per issue whose provenance is exactly
  `"created"` this run** — scales linearly, O(N) in issues typed. This is entirely **new**
  work: 0 such calls existed before FEAT-55. Verified at both call sites:
  `gh-sync.py:989-1007` (`_backfill_issue_types`, one call per parent/task with
  `typed.get(x) == "created"`) and `factory_decompose.py:431-446` (same shape, called twice per
  `_main` run at `factory_decompose.py:514` and `:579`, over disjoint task sets — see below).

## Findings

None met the bar (a concrete, measured or bounded cost that is actually avoidable waste).
Detail on the two candidates named in the dispatch:

1. **Node-id lookup, per issue** — cost: N issues typed this run × 2 `gh` invocations × ≥21.7ms
   floor (measured; real network round-trip is materially higher but unmeasured here — no
   live `gh auth` in this sandbox). For a small feature (5 tasks + 1 parent = 6 issues), floor
   ≈ 261ms, real-world likely 1–3s. **Not flagged**: each `apply_issue_type` call fires exactly
   once per issue's entire lifetime (promoted `"created"` → `True`, gh-sync.py:999/1006,
   factory_decompose.py:427, never re-selected by `_task_needs_type`/`_parent_needs_type` or
   the `typed.get(x) == "created"` guards afterward) — this is the "single one-shot query on a
   one-shot build path" the dispatch names as NOT waste, not a gate that runs at every session
   entry or write.
   severity: info · apply: no (not waste by the stated criteria)

2. **Batching node-id lookups / mutations across N issues into one aliased GraphQL query** —
   technically possible (GraphQL supports aliased sub-queries/mutations) and would collapse 2N
   `gh` invocations to O(1) per run. **Not flagged as a finding**: both call sites document
   immediate per-issue persistence as deliberate crash-safety (`factory_decompose.py:422-424`,
   "the receipt ordering that survives a crash between the two remote calls (T-07 case E)";
   `gh-sync.py:989-994`, "every number comes from the local receipt only"). Batching would
   trade away that per-issue crash-recoverability for round-trip count — the tradeoff is
   already implicitly decided in favor of crash safety elsewhere in this feature's T-07 cases.
   Raising it as an apply-now finding would contradict that existing design shape, so it is
   routed to `decision_questions` below instead.

3. **`factory_decompose.py`'s two `_backfill_issue_types` calls per run** (`:514` and `:579`)
   — checked whether this double-calls the same work: no. Call 1 (before step 5) only matches
   remnants from a prior crashed run; call 2 (only when `need_parent_create`) only matches
   issues created earlier in *this* run's step 6, whose provenance was just set to `"created"`.
   Once a key is promoted to `True` inside call 1 it can never re-match in call 2 (`typed.get(x)
   == "created"` fails for `True`). Two Python-level list iterations over `tasks` (no I/O) is
   the only duplicated cost, and that is O(task count) in-memory work, not measurable I/O.
   severity: info · apply: no (no I/O duplication; confirmed by reading the guard predicates)

4. **`_issue_type_overrides` re-reading remote config** (`factory_decompose.py:359-366` calls
   `factory_config.product_config(fleet, repo)`) — checked for a redundant remote fetch of
   `.harness/harness.json` already read earlier in the same run via `board_for`
   (`factory_decompose.py:491`, also calling `product_config` for the same `(repo, ref)` key).
   Confirmed **not wasteful**: `product_config` process-memoizes by `(repo_name, ref)`
   (`factory_config.py:278-288,311`), so the second call is a dict hit, zero network calls.
   No finding.

5. **Import-time / module-load work in `gh_issue_types.py`** (imported by three callers now) —
   module body is only dict/string/tuple literals (`gh_issue_types.py:13-42`), no computation,
   no I/O at import. No finding.

6. **Repeated file reads** (feature.json / factory.yaml / harness.json / backlog-issues.json) —
   `load_recorded`/`save_recorded` and `load_factory`/`write_factory` are called once per
   create/apply, matching the pre-existing DEC-131 "record after every remote call" convention
   already used pre-FEAT-55 for milestone/parent/task creates; FEAT-55's new `typed`-promotion
   writes (`gh-sync.py:1000,1007`; `factory_decompose.py:428`) follow the identical convention,
   not a new pattern. No finding.

## correctness: (D-20 key-presence sweep)

none. Grepped every `typed`-touching line across `gh-sync.py`, `factory_decompose.py`, and all
four new test files for `"typed" in rec`/`"typed" in factory`/bare membership tests: zero
matches. Every read is an exact-value comparison (`.get("typed") == "created"`, `is True`,
`is False`), consistent with the documented four-state provenance model.

## decision_questions:

1. Should the N per-issue node-id lookups (and/or the N type-apply mutations) ever be
   batched into a single aliased GraphQL query to cut O(N) `gh` invocations to O(1)? Not
   raised as a finding because it trades away the documented per-issue crash-safety guarantee
   (T-07 case E) — flagging purely for the record since nobody has explicitly weighed the
   tradeoff in the plan's decisions.

## git status --porcelain (verbatim, at end of run)

```
 M .claude/skills/harness/references/github-mirror.md
 M .harness/harness/features/FEAT-55-issue-types-created-work/feature.json
?? .harness/harness/features/FEAT-55-issue-types-created-work/notes/qa-2026-09-05-01-validator.md
?? .harness/harness/features/FEAT-55-issue-types-created-work/notes/receipt-harness-backend-dev-simplify-reuse-c1.md
?? .harness/harness/features/FEAT-55-issue-types-created-work/notes/receipt-harness-dev-ops-simplify-simplification-c1.md
?? .harness/harness/features/FEAT-55-issue-types-created-work/observations/harness-data-engineer.md
?? .harness/harness/features/FEAT-55-issue-types-created-work/observations/harness-qa.md
```

None of these are mine — `github-mirror.md` is the main session's named non-goal edit; the
rest are sibling SIMPLIFY-pass receipts/observations and a concurrent QA note. My own artifact
(this file) is not yet reflected in this snapshot since it was taken immediately before write.
