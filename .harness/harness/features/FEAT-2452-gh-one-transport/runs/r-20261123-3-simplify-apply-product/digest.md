# FEAT-2452 — simplify application

PASS: F1–F9 all have dispositions (F1–F8 folded, F9 left), OQ-F2 is decided as option (a), and all seven cycle-1 panel findings are now `resolved` with `resolved_by`, including the high PF-3bfe1e6f. The final `plan-merge.py check --root <worktree>` exited 0: 5 tasks, 31 anchors, 0 failures, no OVERLAP. `approval.status: pending`, `status: plan`, all five tasks `main-session-direct`, `panel.readers` = 4. Zero send-backs (cycles_used: 0). Evidence and full writer stdout: [PM research note](../../notes/research-FEAT-2452-gh-one-transport-simplify-apply-plan.md).

## Per-F disposition
- F1 fold: T-02.files gains `tests/offline_gh_support.py` (create). T-02.intent states `offline_gh_env` / `assert_sentinel_unused` once, with the full contract. T-03.intent and T-04.intent only import it.
- F2 fold, **OQ-F2 = (a)**: T-02.intent pins one literal condition: nonzero int `result.status` AND lowercased stdout+stderr contains `label with name` and `already exists`. T-03.intent cites it verbatim. Why (a): two callers do not justify a new interface. PM checked gh's create.go source: the message carries no `422`, which confirms the reuse reader's inference.
- F3 fold: T-02.intent covers every gh-sync issue-create URL parse. Backlog maps GhError to SKIP; replacement keeps its uncertain-create refusal. One backlog malformed-URL regression added.
- F4 fold: T-01.intent makes result fields authoritative. T-04.intent writes `result.status`.
- F5 fold: T-02.intent brackets by `gh_cost_log._COUNTER_ARGV`, which the regression imports.
- F6 fold (reword): T-02.intent now calls gh_bin the binary resolver T-04 removes; the argv builders stay.
- F7 fold: T-05.verify derives the union of non-`.harness/` task files (29), asserts that count, and asserts `GH_SYNC_GH` and `\bD-11\b` are absent. A literal list exceeded the 50-line DEC-182 budget, so the list is derived from the plan instead.
- F8 fold: T-01.verify adds the INV-26 unit and integration files (run only) with `--workers 4`.
- F9 leave, as the reader recommended. S#3, S#4+E#1 and S#6 stay skipped, as routed.

No BRIEF.md edit and no SC text change were made.

## Panel dispositions (cycle 1, set-panel)
PF-3bfe1e6f (high) → T-02 · PF-500b6ede → T-04 · PF-1d616c71 → T-02 · PF-264d65c0 → T-02 · PF-f10c24fc → T-05 · PF-e4b1875d → T-02 · PF-3cf5ab12 → T-05. None is open, so `sign-approval` needs no overrule.

## Lead assessment
- The member's work met the dispatch, so nothing was sent back.
- Note that PF-264d65c0 (DEC accounting) is resolved by `decisions_affected` rows plus T-02. Its underlying DEC-138 conflict remains OQ-1 for the operator at signature, unchanged.
- One PM choice goes beyond the routed fold. The F1 helper strips every inherited `GH_*` variable rather than naming `GH_SYNC_GH`. That is stronger offline confinement, it keeps SC-02's absence clause literally true, and SC text is unchanged. It is cheap and reversible; the operator can see it at signature.
- Writer stderr carried the expected guard block: unsigned BRIEF and the INV-37 Build-entry receipt. This is not presented as green, and no gh-sync was called. The `APPROVAL-RESET:` grep count is 0 across the three writers. One intermediate check failed on the T-05 line budget; a third apply fixed it.
- No readers, record-panel, goal-check rerun, approval write, signing, code, tests or builds.

## Open questions
- OQ-1 (non-blocking, carried from cycle 1): should DEC-138 get an amend row? It is for the operator at signature.

```yaml
VERDICT: PASS
DIGEST:
  headline: "F1\u2013F8 folded and F9 left. OQ-F2 decided as (a). All seven cycle-1\
    \ panel findings, including the high one, are resolved with resolved_by. plan-merge\
    \ check exits 0 with 0 failures, and the plan stays pending and signable."
  open_questions:
  - id: OQ-1
    question: 'Carried from cycle 1, for the operator at signature: should DEC-138''s
      shared-code clause get an amend row and an owning task for DECISIONS.md? After
      T-02/T-04 its claims that gh_bin lives in gh_issues.py and that each caller
      has its own runner are stale. It is kept as a keep row per the settled no-amendments
      scope.'
    blocking: false
  files_touched:
  - /Users/molchairuangutai/GitHub/harness/.claude/worktrees/harness/FEAT-2452-gh-one-transport/.harness/harness/features/FEAT-2452-gh-one-transport/plan.yaml
  - /Users/molchairuangutai/GitHub/harness/.claude/worktrees/harness/FEAT-2452-gh-one-transport/.harness/harness/features/FEAT-2452-gh-one-transport/observations/harness-pm.md
  expertise_update: []
  team: simplify-apply-product
  steps_run: 1
  cycles_used: 0
  members:
  - step: simplify-apply
    persona: harness-pm
    verdict: PASS
    headline: "F1\u2013F8 folded into task fields, F9 left, OQ-F2 decided as (a).\
      \ Seven PF findings resolved, check exits 0, approval still pending."
    files_touched:
    - /Users/molchairuangutai/GitHub/harness/.claude/worktrees/harness/FEAT-2452-gh-one-transport/.harness/harness/features/FEAT-2452-gh-one-transport/plan.yaml
    - /Users/molchairuangutai/GitHub/harness/.claude/worktrees/harness/FEAT-2452-gh-one-transport/.harness/harness/features/FEAT-2452-gh-one-transport/observations/harness-pm.md
  must_fix: []
  branch: feat/FEAT-2452-gh-one-transport
  escalations: []
  adequacy_notes:
  - 'F1 fold: T-02.files creates tests/offline_gh_support.py. T-02.intent states offline_gh_env/assert_sentinel_unused
    once, with the full contract. T-03.intent and T-04.intent only import it.'
  - 'F2 fold with OQ-F2 = (a): T-02.intent pins one condition, a nonzero int result.status
    AND lowercased output containing ''label with name'' and ''already exists''. T-03.intent
    cites it verbatim. Why: two callers do not justify a new interface, and gh''s
    own create.go message has no 422.'
  - 'F3 fold: T-02.intent covers every gh-sync issue-create URL parse. Backlog maps
    to SKIP and replacement keeps its uncertain-create refusal. A backlog malformed-URL
    regression is added.'
  - 'F4 fold: T-01.intent and T-04.intent make result fields authoritative. F5 fold:
    T-02 references gh_cost_log._COUNTER_ARGV. F6 fold: T-02 rewords gh_bin as the
    binary resolver.'
  - 'F7 fold: T-05.verify takes the plan-derived union of task files (29), asserts
    that count, and asserts GH_SYNC_GH and D-11 are absent. The list is derived to
    stay within the DEC-182 50-line budget.'
  - 'F8 fold: T-01.verify adds the INV-26 unit and integration files (run only). F9
    left. S#3, S#4+E#1 and S#6 stay skipped as routed. No BRIEF.md or SC text change.'
  - "Panel: PF-3bfe1e6f(high)\u2192T-02, PF-500b6ede\u2192T-04, PF-1d616c71\u2192\
    T-02, PF-264d65c0\u2192T-02, PF-f10c24fc\u2192T-05, PF-e4b1875d\u2192T-02, PF-3cf5ab12\u2192\
    T-05. None open; panel.readers still 4. The DEC-138 conflict behind PF-264d65c0\
    \ stays OQ-1 for the operator."
  - 'PM choice beyond the routed fold: the helper strips every inherited GH_* variable
    rather than naming GH_SYNC_GH. It is stronger confinement, keeps SC-02 literally
    true and is reversible, and it is visible at signature.'
  - 'Final plan-merge check output (quoted in the PM note): ''5 task(s), 31 anchor(s)
    resolved, 0 failure(s)'', exit 0. One intermediate check failed on the T-05 line
    budget (70 lines against 50) and was fixed by a third apply.'
  - 'APPROVAL-RESET: grep count is 0 across the three writer invocations, so no gh-sync
    call was made. Writer stderr carried the expected unsigned-BRIEF and INV-37 guard
    block, which is not a green signal.'
  - No readers, record-panel, goal-check rerun, approval write, signing, code, tests
    or builds.
  sc_status: []
  needs_approval: true
  severity_max: none
  matrix_ok: none
  coverage_gaps: []
  findings: []
  readers: []
artifact: /Users/molchairuangutai/GitHub/harness/.claude/worktrees/harness/FEAT-2452-gh-one-transport/.harness/harness/features/FEAT-2452-gh-one-transport/runs/r-20261123-3-simplify-apply-product/digest.md
```
