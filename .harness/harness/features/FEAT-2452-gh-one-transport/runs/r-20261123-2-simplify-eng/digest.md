# FEAT-2452 — four-angle plan pass (simplify-eng)

PASS (advisory, flag-only). Four separate readers returned. After deduplication there are nine findings for PM: three med, five low, and one leave. No plan edits were made, and no tests, builds, linters, gh or git were run. cycles_used: 0. plan.yaml and BRIEF.md are byte-unchanged by this run, because every reader was read-only and only harness-pm holds those paths. Paths below are relative to this feature directory.

## Readers and receipts (chosen by adjacency)
- **Reuse → harness-backend-dev.** Adjacency: the Python bin/ transport (factory_gh, gh-sync, gh_cost_log) and the tests that migrate onto it. R = notes/receipt-harness-backend-dev-r-20261123-2-simplify-eng-reuse.md
- **Simplification → harness-frontend-dev.** It was the nearest remaining eng specialist; the deletion test needs no domain ownership. S = notes/receipt-harness-frontend-dev-r-20261123-2-simplify-eng-simplification.md
- **Efficiency → harness-dev-ops.** Adjacency: test-harness/CI fixtures, verify-pool cost, recorded CI duration medians. E = notes/receipt-harness-dev-ops-r-20261123-2-simplify-eng-efficiency.md
- **Altitude → harness-data-engineer.** Adjacency: structured decision dispositions, policy-table and doctrine placement. A = notes/receipt-harness-data-engineer-r-20261123-2-simplify-eng-altitude.md

## Numbered findings: PM applies by F-id
- **F1 · reuse + simplification + altitude · med · R#1, S#1, A#1 · T-02/T-03/T-04 · SC-02 · plan.yaml:242, :264, :285 → fold-in.**
  - The offline-sentinel confinement contract is restated in three intents, and the restatements have already drifted. T-04 at :285 drops the separate directory and the exit-97 detail.
  - As planned, it is hand-built at roughly 8–14 runner env sites.
  - Cost: one drifted copy, for example one missing the GH_SYNC_GH strip or the empty-log assertion, re-opens the real-gh path that SC-02/#893 closes, and its suite still passes (fail-open).
  - Alternative: T-02 creates one helper and adds it to T-02 `files` with `create: true`. The helper is `offline_gh_env(fake_path, tmp) -> (env, sentinel_log)` plus `assert_sentinel_unused(log)`, and it carries the full contract stated once: only FACTORY_GH set; GH_SYNC_GH popped; sentinel in its own directory prepended to PATH; the fake kept outside that directory; exit 97; log asserted empty. Every T-02 runner calls it. T-03 :264 and T-04 :285 replace their restatements with "use T-02's offline_gh_env / assert_sentinel_unused; do not re-implement confinement".
  - Behaviour, the land-first ordering and the red-run evidence from cycle-1 PF-3bfe1e6f are unchanged. This changes only where the confinement lives, so it is not a re-raise.
  - **Lead resolution of the home:** R proposed `tests/integration/gh_sync_support.py`; S and A proposed a new tests-root file. The pick is a **new tests-root file**, e.g. `tests/offline_gh_support.py`. Reasons: it follows the `tests/harness_config_support.py` "one fixture builder" precedent; tests root is already on sys.path for both unit (T-03/T-04 board/wayfind) and integration runners; it avoids unit tests importing an integration support module.
- **F2 · reuse + altitude · med · R#2, A#2 · T-02/T-03 · SC-04 · plan.yaml:238, :262 → fold-in.**
  - Two callers parse the same `gh label create` response: gh-sync `ensure_labels` (gh-sync.py:987) and `board_lifecycle._ensure_abandoned_label` (:1137). Both must accept "a diagnosed already-existing label", but neither task spells the matcher.
  - Cost: two independently invented matchers. If one is broader, a real failure is treated as idempotent on one path, which re-creates divergences (c)/(d) inside the feature that removes them, and reviewers have no stated rule to check against. [INFERENCE per R] gh's label-exists text may not contain `422`, so copying the milestone conjunction unexamined could reject the true idempotent case.
  - Alternative (PM picks; non-blocking OQ-F2):
    - (a) T-02 :238 pins one literal condition: nonzero typed result AND lowercased stdout+stderr contains gh's actual label-exists text, confirmed against the fake. T-03 :262 says "the same condition as T-02's mirror label check, spelled identically". Both regressions use the same fake stderr.
    - (b) T-01 adds one factory_gh predicate with one unit case, and T-02/T-03 call it. There are two callers, so it is a real seam.
  - Lead lean: (a), because it adds no interface. Either option leaves the settled milestone (e) no-helper trim untouched.
- **F3 · reuse · med · R#3 · T-01/T-02 · SC-05 · plan.yaml:208, :240 → fold-in or explicit leave.**
  - T-02 applies T-01's `issue_number_from_url` only to ordinary parent/task create. Two other parses stay as they are:
    - backlog create `gh-sync.py:2439` (`int(url.rstrip("/").rsplit("/",1)[-1])`), the same shape as the #1542 crash;
    - the replacement-create regex at `:1134`.
  - Cost: three issue-URL grammars remain in one module, and a raw ValueError traceback stays on a path T-02 already migrates. That leaves the folded #1542 only partly closed.
  - Alternative: change T-02 :240 to "every gh-sync issue-create URL parse".
    - Backlog maps GhError to its ordinary SKIP.
    - Replacement adds GhError to its existing except (:1138), keeping its uncertain-create refuse.
    - Add one backlog malformed-URL regression.
  - Or PM records "backlog/replacement deliberately left" with a one-line reason.
  - This extends the settled #1542 fold; it does not contest it.
- **F4 · simplification · low · S#2 · T-01/T-04 · SC-01, SC-03 · plan.yaml:204, :282 → fold-in.**
  - GhResult carries status/stdout/stderr, and GhError carries them too. `_rate_limit_budget_error` sets `error.status=None` after a completed nonzero process (factory_gh.py:70-85), so the two copies disagree.
  - Cost: consumers must guess which copy is authoritative, and T-04's "None = launch failure" rule only holds if it reads `result.status`. The outcome still fails closed.
  - Alternative: add to T-01 :204 "GhResult.status/stdout/stderr are authoritative (status None only on launch failure); callers classify on result fields, never error.status". Write `result.status` explicitly in T-04 :282. No new field and no new test.
- **F5 · reuse · low · R#4 · T-02 · SC-02 · plan.yaml:242 → fold-in.**
  - The counter argv `api rate_limit --jq .resources.graphql.used` is restated in the intent and would be restated in the test.
  - Cost: two spellings of `gh_cost_log._COUNTER_ARGV` (gh_cost_log.py:44). A drift fails loudly.
  - Alternative: phrase it as "bracketed by `gh_cost_log._COUNTER_ARGV`", and have the regression import it, as test-gh-cost-log.py does.
- **F6 · simplification · low · S#5 · T-02/T-04 · SC-02 · plan.yaml:242 → fold-in.**
  - The ownership sentence calls `gh_issues.gh_bin` "the pure argv resolver". It is a binary resolver, and T-04 :284 explicitly keeps the argv builders.
  - Cost: it points the implementer at the opposite shape. The exclusivity claim also duplicates the `files` lists that plan-merge OVERLAP already enforces.
  - Alternative: delete the sentence, or reword it to "T-04 owns removal of the gh_issues.gh_bin binary resolver; argv builders stay."
- **F7 · altitude · low · A#3 · T-05 · SC-02 · BRIEF.md:17; plan.yaml:305-324 (verify), :331 (intent) → fold-in.**
  - SC-02's "GH_SYNC_GH / D-11 dual-pin prose absent from scoped files" clause is a grep fact, but it is checked only by a sentence in T-05's intent.
  - Cost: one leftover header or comment passes every verify; today there are 13 such sites, e.g. test-board-station.py:10-13 and probe-issue-types.py:10,44.
  - Alternative: add one assertion to the T-05 verify heredoc. It iterates the union of T-01..T-05 `files` plus tests/manual/probe-issue-types.py and asserts that `GH_SYNC_GH` and `D-11` are absent from each.
- **F8 · altitude · low · A#4 · T-01 · SC-01 (and the DEC-174 enforcement-executor safety) · plan.yaml:200-201, :331 → fold-in.**
  - T-01 changes factory_gh's launch entry and import graph, yet check-state's INV-26 coverage runs only at T-05's final boundary.
  - Cost: an import or alias break in an enforcement executor's dependency chain only surfaces after four tasks have landed on top of it, which makes bisecting costly.
  - Alternative: add `tests/integration/test-check-state-inv26.py` (optionally also `tests/unit/test-check-state-inv26-routing.py`) to T-01's verify pool. T-01 does not edit them, so ownership stays disjoint. Keep the T-05 sentence as the cumulative re-proof.
- **F9 · altitude · low · A#5 · T-02/T-03/T-05 · SC-02 · plan.yaml:242, :263, :327 → leave.**
  - The FACTORY_GH-only rationale is about to be rewritten into module docstrings and test headers, the same spread that made D-11 a 13-file removal.
  - Alternative, only if PM is already rewriting those lines: replace each removed D-11 block with a one-line pointer to references/github-mirror.md.
  - The reader recommends leave: the cost lands only on a future override change.

## Skipped, with reasons
- **S#3 (drop divergence letters (c)/(d)/(e) from SC-04 and T-02 :239): skip.** The letters are the operator's ruling handles from the grilling ("divergences (a)–(e) each with a regression test, (e) first to cut"). Rewording SC-04 to remove them would cut traceability to a settled ruling, and SC-04 already spells out their meaning. The reader cost is negligible.
- **S#4 + E#1 (five intent preambles repeat the consult list / "never delegate" / absent-docs sentence; ~265 KB of re-reads): skip, merged as one mechanism.** Intents must stay self-contained cold-start specs (harness-spec-driven), and the FEAT-2397 precedent skipped the same boilerplate. Per the efficiency reader the cost is tokens only, never correctness, and that reader offered leave.
- **S#6 (three spellings of "no DEC amendments"; T-05 lacks BRIEF L49's conditional): skip.** The conditional is the escape hatch at the centre of the DEC-138 / OQ-1 question already with the operator (apply note line 21). Harmonising the wording before the operator answers would pre-empt that ruling. PM reconciles it when OQ-1 resolves.
- Every reader explicitly passed on these "checked, not flagged" items, and they are not re-raised:
  - verify pools, red runs and the T-05 boundary gate (all proportionate);
  - the wayfind local 404 helper (one caller);
  - `issue_number_from_url` living in factory_gh;
  - the test-gh-cost-log cross-reference (cycle-1);
  - telemetry under the opt-in flag only.

## Assessment
- **No reader contradiction left unresolved.** The one disagreement was the F1 helper's home, and the lead picked one above with reasons. **No settled ruling re-opened.** F1 and F2 build on the applied cycle-1 confinement and (e) trim without contesting them. F3 tightens the settled #1542 fold.
- F1–F3 are the ones worth applying before signature. Each closes a fail-open or crash path that the plan's own SCs claim to close. F4–F8 are cheap wording or verify-pool folds. F9 is leave.
- Product root docs/spec.md, docs/decisions.md and docs/architecture.md are absent. The plan already routes guidance to SPEC §3.3/§9 and DECISIONS.md, so this did not block the pass.

## Open questions
- **OQ-F2 (non-blocking):** PM picks F2 option (a) inline matcher spelled once, or (b) a factory_gh predicate in T-01. Lead leans (a).

```yaml
VERDICT: PASS
DIGEST:
  headline: 'Four plan-angle receipts complete. Nine deduplicated findings for PM,
    flag-only: three med, five low, one leave. The med ones are F1 (sentinel confinement
    restated in three places, with one helper home picked), F2 (label-exists matcher
    never spelled out) and F3 (two gh-sync URL parses left behind)'
  open_questions:
  - id: OQ-F2
    question: 'PM: for F2, choose (a) one literal label-exists condition pinned in
      T-02 and cited verbatim from T-03, or (b) one factory_gh predicate added in
      T-01 that T-02 and T-03 call. Lead leans (a). See the artifact, F2.'
    blocking: false
  files_touched: []
  expertise_update: []
  team: simplify-eng
  steps_run: 4
  cycles_used: 0
  members:
  - step: reuse
    persona: harness-backend-dev
    verdict: PASS
    headline: '4 reuse findings (3 med, 1 low): sentinel helper, label matcher, URL
      parser coverage, counter argv'
    files_touched: []
  - step: simplification
    persona: harness-frontend-dev
    verdict: PASS
    headline: Plan shapes pass the deletion test; 6 restatement findings (1 med, 5
      low)
    files_touched: []
  - step: efficiency
    persona: harness-dev-ops
    verdict: PASS
    headline: One low finding (repeated consult list); verify pools, boundary gate
      and hot path proportionate
    files_touched: []
  - step: altitude
    persona: harness-data-engineer
    verdict: PASS
    headline: '5 altitude findings (2 med, 3 low): 4 fold-in, 1 leave'
    files_touched: []
  must_fix: []
  branch: none
  escalations: []
  adequacy_notes:
  - There were four separate parallel read-only dispatches. Reuse went to backend-dev
    (Python bin/ transport and tests), efficiency to dev-ops (test-harness/CI cost),
    altitude to data-engineer (decision dispositions and doctrine), and simplification
    to frontend-dev (nearest remaining specialist). All four receipts exist under
    notes/.
  - The pass is flag-only, so plan.yaml and BRIEF.md are byte-unchanged by this run.
    No tests, builds, linters, gh or git were run.
  - 'Dedup: three readers flagged sentinel confinement, merged as F1. The lead picked
    the helper home, a new tests-root file on the harness_config_support.py precedent
    over gh_sync_support.py, because unit and integration runners both reach it. R#2
    and A#2 merged as F2. S#4 and E#1 merged and skipped.'
  - 'Skipped with reasons in the artifact: S#3, because the divergence letters are
    the operator''s ruling handles. S#4 and E#1, because intents stay self-contained
    cold-start specs, as in the FEAT-2397 precedent. S#6, because that wording is
    the DEC-138/OQ-1 escape hatch already with the operator.'
  - PM should apply F1 to F3 before signature; each closes a fail-open or crash path
    the SCs claim. F4 to F8 are cheap folds, and F9 is leave.
  sc_status: []
  needs_approval: none
  severity_max: med
  matrix_ok: none
  coverage_gaps: []
  findings:
  - kind: substance
    scope: none
    severity: med
    reader: reuse, simplification, altitude
    summary: 'F1: offline-sentinel confinement is restated in T-02/T-03/T-04 (plan.yaml:242/264/285),
      already drifted, and hand-built at about 8 to 14 runner env sites'
    why: 'One drifted copy re-opens real-gh dispatch while its suite still passes
      (SC-02). Fix: one tests-root offline_gh_env/assert_sentinel_unused helper created
      in T-02, which T-03 and T-04 import.'
  - kind: substance
    scope: none
    severity: med
    reader: reuse, altitude
    summary: 'F2: the label already-exists diagnosis is required in T-02 and T-03
      (plan.yaml:238/262) but never spelled out'
    why: 'Two independent matchers can disagree and re-create divergences (c)/(d)
      (SC-04). Fix: one literal condition stated once, or a factory_gh predicate.'
  - kind: substance
    scope: none
    severity: med
    reader: reuse
    summary: 'F3: issue_number_from_url is applied only to ordinary create; backlog
      (gh-sync.py:2439, the #1542 shape) and replacement (:1134) parses remain'
    why: 'Three URL grammars in one module, and a raw ValueError left on a migrated
      path (SC-05). Fix: extend T-02 :240 to every issue-create parse, or record leave.'
  - kind: form
    scope: none
    severity: low
    reader: simplification
    summary: 'F4: GhResult and GhError both carry status, and they disagree on the
      rate-limit path'
    why: Name result fields as authoritative in T-01 :204 and T-04 :282.
  - kind: form
    scope: none
    severity: low
    reader: reuse
    summary: 'F5: the counter argv literal is restated in T-02 :242'
    why: Reference gh_cost_log._COUNTER_ARGV instead.
  - kind: form
    scope: none
    severity: low
    reader: simplification
    summary: 'F6: T-02 :242 misnames gh_bin as an argv resolver and duplicates the
      files ownership lists'
    why: Delete the sentence, or reword it as the binary resolver.
  - kind: substance
    scope: none
    severity: low
    reader: altitude
    summary: 'F7: SC-02''s absence clause has no mechanical check in T-05 verify'
    why: Add a GH_SYNC_GH/D-11 absence assertion over the task-owned files to the
      T-05 heredoc.
  - kind: proportionality
    scope: task
    severity: low
    reader: altitude
    summary: 'F8: INV-26 check-state coverage runs only at T-05, although T-01 reshapes
      factory_gh'
    why: Add test-check-state-inv26.py to T-01's verify pool for early fault localization.
  - kind: form
    scope: none
    severity: low
    reader: altitude
    summary: 'F9: the FACTORY_GH rationale is about to be restated in docstrings and
      headers'
    why: Leave; at most a one-line pointer to github-mirror.md.
  readers:
  - reader: reuse
    status: ran
    persona: harness-backend-dev
    reason: none
  - reader: simplification
    status: ran
    persona: harness-frontend-dev
    reason: none
  - reader: efficiency
    status: ran
    persona: harness-dev-ops
    reason: none
  - reader: altitude
    status: ran
    persona: harness-data-engineer
    reason: none
  amendments: []
artifact: /Users/molchairuangutai/GitHub/harness/.claude/worktrees/harness/FEAT-2452-gh-one-transport/.harness/harness/features/FEAT-2452-gh-one-transport/runs/r-20261123-2-simplify-eng/digest.md
```
