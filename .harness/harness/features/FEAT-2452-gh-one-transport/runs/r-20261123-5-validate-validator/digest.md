# Validate — FEAT-2452 — cycle 1 — r-20261123-5-validate-validator

**FAIL** at review_sha `64102016cba259b96fcf7761b3f31ec685a65a8c` (base `b788e9da`). The suites are green with DEC-255 receipts (unit 67, integration 95). Two high substance defects remain. Checked label creation now SKIP-exits abandon and reject (T-02), and wayfind still treats a successful but unusable dependency payload as absence (T-04). SC-05's #13 failing-first clause is unmet. Per `gates.review: advisory_unless_high`, the high findings are what block.

## Readers
| step | persona | verdict | note |
|---|---|---|---|
| qa | harness-qa | PASS | `notes/review-harness-qa-c1.md`; receipts `qa/manifest-{unit,integration}.json`; all 5 verify blocks exit 0 |
| code | harness-code-reviewer | FAIL | `notes/review-harness-code-reviewer-c1.md`; code-grade pass |
| security | harness-security-reviewer | PASS | `notes/review-harness-security-reviewer-c1.md`; one med finding |
| ui | harness-ui-reviewer | PASS | scoped out on a measured census of the 137-path diff |
| goalcheck | harness-pm | FAIL | `notes/research-…-goalcheck-validate-c1.md`; maintainer pass, operator partial |

## Ranked must-fix (in fix order)
1. **H1 · high · substance · T-02 (SC-04/SC-05, DEC-203) — code-reviewer.** `gh-sync.py ensure_labels` calls `skip()` on any label-create failure (exit 0). In abandon, `ensure_labels(repo, {"abandoned"})` runs before the non-exiting per-item loop and the local abandoned station, so a 403 drops the close/reseat work and the local record. Reject's `label` step calls `ensure_labels` inside `_run_reject_steps`, so a 403 exits 0 and bypasses the `_RejectHalt` report and exit 1. Lead verified both call sites in the worktree source. Remedy: the check stays ahead of the dependent label attachment, and each caller keeps its own policy for what follows. **Ordering:** the new create-failure regression for abandon fails at the current pin, so it also supplies SC-05's missing #13 failing-first evidence (see G1).
2. **H2 · high · substance · T-04 (SC-03) — code-reviewer.** `blockers()` returns `gh_json_or_absent(...) or []`, so a successful JSON `null` becomes "no blockers". `parent_of` maps `{}` to no parent and accepts `{"number": false}`. SC-03's "only a … 404 … as absence" forbids both. The lead checked the main checkout: the `or []` coercion predates this feature, so this is a gap in the SC rather than a regression this diff introduced. It still falls inside SC-03's literal text, so the high rating is kept. Independent of H1.
3. **G1 · gating SC row · T-02 (SC-05) — pm, qa, code-reviewer (deduplicated).** The #13 abandon assertions passed on the old code (`t02-red-green/05-red-abandon-old-override.txt`), so no failing-first exists. QA's mutation proof was refused by check-domain. H1's regression closes this. If it does not, a dev-side mutant that aborts the abandon loop on the first `gh_try` failure would do.
4. **F1 · med · form · T-05 (SC-06 omission) — code-reviewer; pm OQ-3 folded in.** The wayfind row in `github-mirror.md` omits the partial write: comment and close have already landed when the gist fails. Write the abandon/reject label outcomes after H1. Remove the cut-history prose from the milestone row (pm, low). This depends on H1.

## Advisory (not gating)
- **A1 · med · substance · T-01 — code-reviewer.** `factory_gh` accepts `https://?/o/r/issues/42` as issue 42. This is not a realistic gh reply, but the fix is cheap, so do it in the same cycle while T-01 is open.
- **A2 · med · substance · T-01/T-04 — security.** With opt-in `HARNESS_GH_COST_LOG=1`, the full inline `--body` resolve comment is persisted to local JSONL. Redact body operands, or backlog it.

## Assessed and dismissed
- **code-reviewer med form (T-04 evidence):** the baseline reds hit the exit-97 sentinel rather than the named payloads. **Closed by QA:** in-memory mutants at the pin showed discrimination. M2 reddens exactly the 2 status-zero-with-404 cases, and M3 reddens 12 non-404 cases.
- **Disclosure 1 / SC-04 (e):** met with the cut, not as written. C5 pre-sanctions the cut. It is carried to the ship record, not to must-fix.
- **Disclosures 2–6:** accepted as disclosed. No reader raised them as new.

## Adequacy
- QA's green is real, with runner receipts and non-zero discovery. Its own mutants closed the SC-03 discrimination question. The one gap it could not close is the #13 mutation, refused by a capability, not missing from the work.
- Security's clean verdict on injection and binary selection is reasoning-only, and its threat model leaves PATH/env trust unchanged from base.

## Open questions (non-blocking, harness defects)
- QA OQ-QA-2: check-domain refuses a QA perturbation edit inside QA's own pinned checkout, although DEC-153 sanctions it.
- QA OQ-QA-3: a fresh pinned checkout lacks node_modules, so the integration typecheck is red until `bun install`.

```yaml
VERDICT: FAIL
artifact: /Users/molchairuangutai/GitHub/harness/.claude/worktrees/harness/FEAT-2452-gh-one-transport/.harness/harness/features/FEAT-2452-gh-one-transport/runs/r-20261123-5-validate-validator/digest.md
DIGEST:
  headline: 'FEAT-2452 FAIL at 64102016: suites green with receipts (unit 67, integration
    95), but two high defects block. Checked label creation SKIP-exits abandon and
    reject (T-02), and wayfind treats successful unusable payloads as absence (T-04).
    SC-05 #13 failing-first is unmet.'
  team: validate
  steps_run: 5
  cycles_used: 0
  branch: none
  members:
  - step: qa
    persona: harness-qa
    verdict: PASS
    headline: 'unit 67/67 and integration 95/95 green with DEC-255 receipts; all 5
      verify blocks exit 0; #13 abandon has no red'
    files_touched:
    - /Users/molchairuangutai/GitHub/harness/.claude/worktrees/harness/FEAT-2452-gh-one-transport/.harness/harness/features/FEAT-2452-gh-one-transport/runs/r-20261123-5-validate-validator/qa/manifest-unit.json
    - /Users/molchairuangutai/GitHub/harness/.claude/worktrees/harness/FEAT-2452-gh-one-transport/.harness/harness/features/FEAT-2452-gh-one-transport/runs/r-20261123-5-validate-validator/qa/manifest-integration.json
    - /Users/molchairuangutai/GitHub/harness/.claude/worktrees/harness/FEAT-2452-gh-one-transport/.harness/harness/features/FEAT-2452-gh-one-transport/observations/harness-qa.md
  - step: code
    persona: harness-code-reviewer
    verdict: FAIL
    headline: Checked label creation breaks the abandon and reject policies; wayfind
      fails open on unusable blocker data; code-grade pass
    files_touched: []
  - step: security
    persona: harness-security-reviewer
    verdict: PASS
    headline: Wayfind fails closed on auth errors and enforcement is unchanged; opt-in
      telemetry logs the full resolve comment (med)
    files_touched: []
  - step: ui
    persona: harness-ui-reviewer
    verdict: PASS
    headline: 'Out of scope: the 137-path diff has no built UI'
    files_touched: []
  - step: goalcheck
    persona: harness-pm
    verdict: FAIL
    headline: 'code maintainer pass; operator partial on SC-05 #13 failing-first;
      SC-04 met with the cut; SC-06, SC-07 and the DEC-138 amendment met'
    files_touched: []
  must_fix:
  - 'H1 (T-02, high, substance; SC-04/SC-05, DEC-203): gh-sync ensure_labels skip()s
    (exit 0) on any label-create failure. That drops abandon''s per-item close/reseat
    and the local abandoned station, and bypasses reject''s _RejectHalt report and
    exit 1. Keep the check before the dependent label attachment and let each caller
    apply its own policy. Add create-failure regressions for abandon and reject that
    fail first.'
  - 'H2 (T-04, high, substance; SC-03): wayfind blockers() coerces a successful JSON
    null to []; parent_of maps {} to no parent and accepts {"number": false}. Only
    a confirmed 404 may mean absence; reject unusable payloads before eligibility
    or writes; add fail-first regressions.'
  - 'G1 (T-02, SC-05 row partial): supply #13 abandon failing-first evidence. H1''s
    abandon regression, red at the current pin, satisfies it; otherwise use a dev-side
    mutant that aborts the loop on the first gh_try failure.'
  - 'F1 (T-05, med, form; SC-06 omission): add to github-mirror.md the wayfind partial
    write (comment and close land before the gist fails) and the abandon/reject label
    outcomes after H1, and remove the cut-history prose from the milestone row. Do
    this after H1.'
  files_touched:
  - /Users/molchairuangutai/GitHub/harness/.claude/worktrees/harness/FEAT-2452-gh-one-transport/.harness/harness/features/FEAT-2452-gh-one-transport/runs/r-20261123-5-validate-validator/state.yaml
  - /Users/molchairuangutai/GitHub/harness/.claude/worktrees/harness/FEAT-2452-gh-one-transport/.harness/harness/features/FEAT-2452-gh-one-transport/runs/r-20261123-5-validate-validator/qa/manifest-unit.json
  - /Users/molchairuangutai/GitHub/harness/.claude/worktrees/harness/FEAT-2452-gh-one-transport/.harness/harness/features/FEAT-2452-gh-one-transport/runs/r-20261123-5-validate-validator/qa/manifest-integration.json
  - /Users/molchairuangutai/GitHub/harness/.claude/worktrees/harness/FEAT-2452-gh-one-transport/.harness/harness/features/FEAT-2452-gh-one-transport/observations/harness-qa.md
  open_questions:
  - id: OQ-QA-2
    question: 'Harness defect: check-domain refuses a QA perturbation edit inside
      QA''s own pinned checkout, although DEC-153 sanctions in-pin perturbation proofs.
      Which is wrong, the grant or the rule?'
    blocking: false
  - id: OQ-QA-3
    question: 'Harness defect: a fresh pinned checkout lacks node_modules, so integration
      test-typescript-typecheck.py is red until `bun install --frozen-lockfile`. Should
      pinned-checkout.py or the runner install the toolchain?'
    blocking: false
  escalations: []
  expertise_update: []
  adequacy_notes:
  - QA's green rests on DEC-255 receipts with non-zero discovery (unit 67, integration
    95). QA's in-memory mutants M2 and M3 closed the code-reviewer's T-04 evidence
    finding, so that finding is dismissed as closed.
  - 'Lead verified H1 at source: ensure_labels skip() sits ahead of abandon''s non-exiting
    loop and inside reject''s label step. Lead verified H2: blockers() `or []`. On
    the main checkout the coercion predates this feature, so H2 is an SC-03 gap the
    diff left in place, not a regression it introduced; the high rating stands under
    SC-03''s ''only'' clause.'
  - 'SC-04 is met with the cut, not as written: divergence (e) was cut under the pre-sanctioned
    C5 lever. The ship record must carry the cut.'
  - 'Advisory A1 (T-01, med): factory_gh accepts https://?/o/r/issues/42 as issue
    42. The fix is cheap, so do it in the same fix cycle.'
  - 'Advisory A2 (T-01/T-04, med, security): opt-in HARNESS_GH_COST_LOG persists full
    inline --body resolve comments. Redact or backlog.'
  - 'Fixes are main-session-direct under DEC-174, so Main implements H1, H2, G1 and
    F1. Order: H1 then F1; H2 is independent.'
  - Security's clean verdict on injection and binary selection is reasoning-only;
    PATH and env trust are unchanged from base.
  sc_status:
  - id: SC-01
    verdict: met
    method: automated
    evidence: t01-red-green/01-red-*.txt semantic reds; tests/unit/test-gh-cost-log.py:529;
      qa unit receipt green at pin
  - id: SC-02
    verdict: met
    method: automated
    evidence: t02-red-green/01-red-confinement-open.txt red; tests/integration/test-gh-sync-open.py:863
      single-override case; no GH_SYNC_GH/D-11 residue at pin
  - id: SC-03
    verdict: not_met
    method: automated
    evidence: 'Enumerated failure classes covered (t04 reds plus QA mutants M2/M3),
      but H2: a successful null, {} or a bad number payload is still treated as absence
      or as a usable parent (wayfind.py blockers/parent_of)'
  - id: SC-04
    verdict: partial
    method: automated
    evidence: '(c) and (d) reds present; (e) cut under C5. H1: label-create check
      applies the mirror SKIP to abandon and reject, overriding their caller policy'
  - id: SC-05
    verdict: partial
    method: automated
    evidence: 'URL red in t02 04-red-behaviour-old-override.txt; #13 abandon assertions
      green on old code (05-red-abandon-old-override.txt), so no failing-first exists'
  - id: SC-06
    verdict: partial
    method: inspection
    evidence: Policy table, no-deadline note and factory_cli exit-2 contract present;
      enforcement executors identical base/pin. The wayfind row omits the partial
      resolve write (F1)
  - id: SC-07
    verdict: met
    method: inspection
    evidence: 'notes/enforcement-backlog.json at pin: #2468 OPEN, signed title, body
      byte-identical, names branch-create-gate and merge-gate'
  - id: DEC-138
    verdict: met
    method: inspection
    evidence: DECISIONS.md:3132 shared-code sentences rewritten only; guard sentence
      and DEC-146 byte-identical (pm, code-reviewer)
  needs_approval: false
  severity_max: high
  matrix_ok: true
  coverage_gaps:
  - 'SC-05 #13 abandon: no failing-first; QA''s mutation proof was refused by check-domain'
  - No regression for label-create failure in abandon or reject (H1)
  - No regression for successful-but-unusable blocker/parent payloads (H2)
  findings:
  - kind: substance
    scope: none
    severity: high
    reader: code-reviewer
    summary: 'T-02: label-create failure skip()s (exit 0) before abandon''s local
      recording and bypasses reject''s exit-1 halt'
    why: Breaks abandon/reject caller policy (SC-04/SC-05, DEC-203); a 403 on label
      create drops the close/reseat and local station writes
  - kind: substance
    scope: none
    severity: high
    reader: code-reviewer
    summary: 'T-04: wayfind treats successful null or {} payloads as absence and accepts
      {"number": false}'
    why: SC-03 allows only a confirmed 404 as absence; a blocked ticket can enter
      the frontier, or resolve can comment and close before a bad gist lookup
  - kind: substance
    scope: none
    severity: med
    reader: code-reviewer
    summary: 'T-01: factory_gh URL regex accepts empty-authority https://?/o/r/issues/42'
    why: Can persist a false mirror receipt; advisory, cheap fix
  - kind: substance
    scope: none
    severity: med
    reader: security-reviewer
    summary: 'T-01/T-04: opt-in cost telemetry persists full inline resolve comments'
    why: Information disclosure to readers of the local JSONL; advisory, redact body
      operands
  - kind: form
    scope: none
    severity: med
    reader: code-reviewer
    summary: 'T-05: github-mirror.md wayfind row omits the partial resolve write'
    why: SC-06 requires partial writes; an operator who treats exit 1 as no mutation
      can repeat the comment on rerun
  - kind: form
    scope: none
    severity: med
    reader: code-reviewer
    summary: 'T-04: baseline reds hit the exit-97 sentinel, not the named payloads'
    why: 'Assessed and dismissed: QA''s mutants M2/M3 at the pin establish discrimination'
  - kind: form
    scope: none
    severity: low
    reader: code-reviewer
    summary: 'T-02: the #13 receipt is a preservation check, not a red'
    why: Deduplicated into G1 with pm's SC-05 partial and QA's coverage gap
  - kind: form
    scope: none
    severity: low
    reader: pm
    summary: 'T-05: the milestone row carries cut-history prose'
    why: Against T-05's current-policy-rows intent; folded into F1
  readers:
  - reader: qa
    status: ran
    persona: harness-qa
    reason: none
  - reader: code
    status: ran
    persona: harness-code-reviewer
    reason: none
  - reader: security
    status: ran
    persona: harness-security-reviewer
    reason: none
  - reader: ui
    status: ran
    persona: harness-ui-reviewer
    reason: none
  - reader: goalcheck
    status: ran
    persona: harness-pm
    reason: none
```
