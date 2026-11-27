# Team digest — FEAT-2458 plan, run 2026-11-23-01-plan-product (cycle 1)

**FAIL (roll-up of the scope reader's FAIL): the plan is drafted, applied and pending with `panel:` recorded and `plan-merge.py check` exit 0, but the scope reader's high substance finding (prefix match could delete an absent feature's stamp) was applied without being re-read, so it stays open.** No mission downgrade is recommended: neither reader raised a `scope: mission` finding, and should-not-exist judged the plan lane proportionate.

## Steps

| Step | Persona | Verdict | Artifact |
|---|---|---|---|
| draft | harness-pm | PASS | `BRIEF.md`, `plan.yaml` (2 tasks, both `main-session-direct`) |
| scope | harness-code-reviewer | FAIL | `notes/review-harness-code-reviewer-plan-c1.md` |
| should-not-exist | fable-advisor | PASS | transcribed into `runs/2026-11-23-01-plan-product/panel-c1.md` |
| design | harness-ui-reviewer | PASS (self-scoped out) | `notes/review-harness-ui-reviewer-plan-c1.md` |
| apply | harness-pm | PASS | `notes/research-apply-plan-c1.md`. `record-panel` and `check` exit 0; no `APPROVAL-RESET` |
| goalcheck | harness-pm | PASS | `notes/research-FEAT-2458-shape-stamp-sweep-goalcheck-plan.md` |

Send-backs: 0. The scope FAIL was routed to apply as findings, not returned to the reader.

## Assessment

- **High finding confirmed at the source** by the lead. `worktree_terminal.py::_match_landed_id` prefix-matches (`n.startswith(wt_id)`). Apply rewrote T-01: `classify_feature` now resolves exact ids and walks `_fleet_segments` + `_landed_dir_names`. It calls none of `_match_landed_id`, `_planning_segment` or `_resolve_landed` (new D-03), and still routes through `_landed_classification` (D-02 held). An AST verify pins this. PF-9ad7c484 and five lower findings are applied but `open` until a reader re-reads T-01/T-02.
- **Operator-wording departure (for signature).** The operator constraint said fleet features "must resolve through the existing planning-segment lookup". D-03 forbids `_planning_segment` because it uses the same prefix matcher. Goal-check grades this "intent met, wording departed": FEAT-01-kaya-platform still resolves under kaya.
- **Side-effect on the gate path (for signature).** T-01 adds an `except UnicodeDecodeError` around `_landed_blob_text`. This also changes `classify`/`classify_all` on the INV-29 path, so it reaches beyond the stamp sweep.
- **Converging findings.** Both readers flagged `FEATURE_CLASSES`; it is dropped, and the literals stay.
- **Prototype gate:** none required. The work has no end-user interaction (ui-reviewer, `in_scope: false`). The operator may override this in either direction.
- **Goal-check:** operator pass, code maintainer pass. The fleet-lookup point is partial on wording only.

## Open for the operator

pm's draft questions Q-01 (`not_terminal` spelling) and Q-02 (removal lines for deleted stamps), plus the two signature points above.

```yaml
VERDICT: FAIL
artifact: /Users/molchairuangutai/GitHub/harness/.claude/worktrees/harness/FEAT-2458-shape-stamp-sweep/.harness/harness/features/FEAT-2458-shape-stamp-sweep/runs/2026-11-23-01-plan-product/digest.md
DIGEST:
  headline: FEAT-2458 BRIEF and plan.yaml are pending with panel recorded and plan-merge
    check exit 0, but the scope reader's high finding (prefix match deletes an absent
    feature's stamp) was applied without being re-read, so it is still open; no mission
    downgrade
  team: plan
  steps_run: 6
  cycles_used: 0
  members:
  - step: draft
    persona: harness-pm
    verdict: PASS
    headline: BRIEF (11 SCs) and 2-task main-session-direct plan.yaml drafted at pending;
      check exit 0, 7/7 anchors
    files_touched:
    - /Users/molchairuangutai/GitHub/harness/.claude/worktrees/harness/FEAT-2458-shape-stamp-sweep/.harness/harness/features/FEAT-2458-shape-stamp-sweep/BRIEF.md
    - /Users/molchairuangutai/GitHub/harness/.claude/worktrees/harness/FEAT-2458-shape-stamp-sweep/.harness/harness/features/FEAT-2458-shape-stamp-sweep/plan.yaml
  - step: scope
    persona: harness-code-reviewer
    verdict: FAIL
    headline: Prefix lookup can delete a never-landed feature's stamp; undecodable
      landed blob aborts sweep; plan otherwise fits
    files_touched: []
  - step: should-not-exist
    persona: fable-advisor
    verdict: PASS
    headline: Plan lane proportionate; three low findings (optional _resolve_landed
      refactor, redundant SC-06 clauses, public FEATURE_CLASSES)
    files_touched: []
  - step: design
    persona: harness-ui-reviewer
    verdict: PASS
    headline: 'Mode A out of scope: no visual or interactive UI surface'
    files_touched: []
  - step: apply
    persona: harness-pm
    verdict: PASS
    headline: All 8 findings applied (exact-id classify_feature, decode catch, SC-11
      removed, keep rows, FEATURE_CLASSES dropped); record-panel and check exit 0;
      no APPROVAL-RESET
    files_touched:
    - /Users/molchairuangutai/GitHub/harness/.claude/worktrees/harness/FEAT-2458-shape-stamp-sweep/.harness/harness/features/FEAT-2458-shape-stamp-sweep/BRIEF.md
    - /Users/molchairuangutai/GitHub/harness/.claude/worktrees/harness/FEAT-2458-shape-stamp-sweep/.harness/harness/features/FEAT-2458-shape-stamp-sweep/plan.yaml
  - step: goalcheck
    persona: harness-pm
    verdict: PASS
    headline: Operator and code-maintainer perspectives pass; D-03 departs from the
      operator's wording on the fleet lookup, not from intent
    files_touched: []
  must_fix:
  - 'Re-gate T-01/T-02 against PF-9ad7c484 (high, substance, scope reader): exact-id
    classify_feature (D-03) was applied but no reader has re-read it, so the finding
    stays open and gates signature until it is closed or the operator overrules it
    (DEC-176).'
  branch: feat/FEAT-2458-shape-stamp-sweep
  escalations: []
  adequacy_notes:
  - 'Lead checked the high finding''s premise at the worktree: worktree_terminal.py::_match_landed_id
    prefix-matches (n.startswith(wt_id)).'
  - Scope FAIL went to apply as findings, not as a reader send-back. Cycle 1 had 0
    send-backs.
  - 'Prototype gate: none required, because the work has no end-user interaction (ui-reviewer
    in_scope false). The operator may override either way.'
  - fable-advisor's own readers entry named persona harness-validator-lead. The fan-in
    records the dispatched persona, fable-advisor.
  - Five lower applied findings (PF-dd345693, PF-74d8eda7, PF-bb8bb7d3, PF-7dd2962d,
    PF-007b122a) stay open until the same re-read. The two form findings are resolved.
  sc_status:
  - id: operator
    verdict: pass
    method: goal-check inspection
    evidence: 'notes/research-FEAT-2458-shape-stamp-sweep-goalcheck-plan.md: T-02
      carries SC-03, SC-04, SC-05'
  - id: code maintainer
    verdict: pass
    method: goal-check inspection
    evidence: 'same note: T-01 carries SC-01, SC-02, SC-08, SC-09, SC-10; T-02 carries
      SC-06, SC-07, SC-08, SC-09, SC-10'
  - id: fleet-lookup wording
    verdict: partial
    method: goal-check inspection
    evidence: D-03 forbids _planning_segment (prefix matcher) and walks _fleet_segments
      with exact ids; FEAT-01-kaya-platform still resolves under kaya
  needs_approval: true
  severity_max: high
  matrix_ok: none
  coverage_gaps: []
  findings:
  - kind: substance
    scope: none
    severity: high
    reader: scope
    summary: T-01/T-02 can delete an absent feature's stamp by matching a different
      landed ID.
    why: _match_landed_id prefix-matches; an absent id that prefixes a landed done
      id resolves terminal. Applied as exact-id D-03; open pending re-read.
  - kind: substance
    scope: none
    severity: med
    reader: scope
    summary: T-01/T-02 let undecodable landed records abort the stamp sweep.
    why: UnicodeDecodeError from worktree_terminal.py _landed_blob_text escapes the
      OSError catch. Applied as a decode catch; open pending re-read.
  - kind: form
    scope: none
    severity: med
    reader: scope
    summary: SC-11 requires a post-merge observation as a pre-ship UAT gate.
    why: 'Conflicts with DEC-74. Fixed in place: SC-11 deleted and moved to Verification
      gaps as a post-merge check that gates nothing.'
  - kind: form
    scope: none
    severity: low
    reader: scope
    summary: The decision dispositions omit three governing keep rows.
    why: DEC-221, DEC-191, DEC-252 govern touched surfaces. Fixed in place with keep
      rows.
  - kind: proportionality
    scope: task
    severity: low
    reader: scope
    summary: T-01 publishes a result vocabulary with no production caller.
    why: 'FEATURE_CLASSES only serves a test assertion. Applied: dropped.'
  - kind: proportionality
    scope: task
    severity: low
    reader: should-not-exist
    summary: T-01's mandated extraction of a shared _landed_names helper out of _resolve_landed
      is an optional refactor of a gate-critical path; classify_feature can carry
      the ~6-line segment lookup privately instead
    why: 'Regression surface on the INV-29 chain in a DEC-174 human-read diff. Applied:
      T-01 now forbids modifying _resolve_landed.'
  - kind: proportionality
    scope: task
    severity: low
    reader: should-not-exist
    summary: SC-06's inspection clauses that re-check what T-02's verify line already
      greps should be dropped, keeping only the reads-no-records clause
    why: The clauses restate automation and spend human review attention. Applied.
  - kind: substance
    scope: none
    severity: low
    reader: should-not-exist
    summary: The new public FEATURE_CLASSES constant (T-01 step 1, named in SC-08's
      docstring surface) was not asked for by grilling R3 and should not be public
      surface; its only planned consumer is a test membership assertion a literal
      tuple serves
    why: The tuple sits beside CLASSES with the opposite treatment of absence and
      invites misuse. Applied together with the scope finding.
  readers:
  - reader: scope
    status: ran
    persona: harness-code-reviewer
    reason: none
  - reader: should-not-exist
    status: ran
    persona: fable-advisor
    reason: none
  - reader: design
    status: ran
    persona: harness-ui-reviewer
    reason: none
  - reader: goalcheck
    status: ran
    persona: harness-pm
    reason: none
  open_questions:
  - id: Q-01
    question: Is not_terminal (underscore, matching exempt_absent) the right spelling
      for classify_feature's live-work result? The grilling wrote not-terminal.
    blocking: false
  - id: Q-02
    question: 'Keep or drop the per-removed-stamp output lines (''stamps: removed''
      / ''stamps: would remove'' under --dry-run)? The grilling settled only kept-unresolved
      lines and silence for live stamps.'
    blocking: false
  - id: Q-03
    question: 'Accept D-03 at signature? You said fleet features must resolve through
      the existing planning-segment lookup. The plan now forbids _planning_segment,
      which prefix-matches, and walks _fleet_segments with exact ids instead. FEAT-01-kaya-platform
      still resolves under kaya. Recommendation: accept.'
    blocking: false
  - id: Q-04
    question: Accept the UnicodeDecodeError catch in worktree_terminal._landed_blob_text
      at signature? It also changes classify/classify_all on the INV-29 gate path,
      not just the stamp sweep.
    blocking: false
  - id: Q-05
    question: Route a scope-reader re-read of T-01/T-02 to close PF-9ad7c484 (high)
      and the other applied-but-open findings, or have the operator rule on them at
      the batched signature (DEC-176)?
    blocking: true
  files_touched:
  - /Users/molchairuangutai/GitHub/harness/.claude/worktrees/harness/FEAT-2458-shape-stamp-sweep/.harness/harness/features/FEAT-2458-shape-stamp-sweep/BRIEF.md
  - /Users/molchairuangutai/GitHub/harness/.claude/worktrees/harness/FEAT-2458-shape-stamp-sweep/.harness/harness/features/FEAT-2458-shape-stamp-sweep/plan.yaml
  - /Users/molchairuangutai/GitHub/harness/.claude/worktrees/harness/FEAT-2458-shape-stamp-sweep/.harness/harness/features/FEAT-2458-shape-stamp-sweep/runs/2026-11-23-01-plan-product/state.yaml
  - /Users/molchairuangutai/GitHub/harness/.claude/worktrees/harness/FEAT-2458-shape-stamp-sweep/.harness/harness/features/FEAT-2458-shape-stamp-sweep/runs/2026-11-23-01-plan-product/panel-c1.md
  - /Users/molchairuangutai/GitHub/harness/.claude/worktrees/harness/FEAT-2458-shape-stamp-sweep/.harness/harness/features/FEAT-2458-shape-stamp-sweep/runs/2026-11-23-01-plan-product/acceptance.md
  expertise_update: []
```
