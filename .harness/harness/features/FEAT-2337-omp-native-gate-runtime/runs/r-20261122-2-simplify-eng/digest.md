# FEAT-2337 — four-angle pending-plan pass

PASS: four read-only readers completed; nine deduplicated advisory findings, no blocking finding. FLAG-ONLY: PM owns any later apply. No settled choice is reopened. cycles_used: 0; files_touched: []. No builds, tests, lint or git ran. Neither plan.yaml nor BRIEF.md was written by this run.

## Numbered findings
Paths below are relative to this feature directory unless explicitly source paths. Anchors are the readers' task/section anchors; approximate line numbers are not executable anchors.

1. **fold-in · reuse + simplification** — File: plan.yaml and BRIEF.md; anchor: T-03 cumulative grading (~477–488), T-01/T-02 grading clauses, SC-08. Summary: name the existing grader rather than add another bar calculation, and cross-reference the common requirement. Concrete cost: a third bar-rule implementation plus four prose copies can drift. Alternative: T-03 names `code_grade.classify` and the existing configured-kind loader; T-01/T-02 point to SC-08/T-03, preserving every assertion and threshold.
2. **fold-in · reuse + efficiency + altitude** — File: plan.yaml; anchor: T-02 receipt identity (~359–375). Summary: give identity verification one local home and reuse existing revision resolution; avoid repeating lineage work across kinds. Concrete cost: duplicate git resolution can omit option-like-revision rejection; per-kind/per-commit subprocess work grows with history (cost unmeasured); inline identity logic raises reader load. Alternative: name `resolve_reviewed_commit`/`commit_oid`, resolve/cache identities per validation call, and keep lineage evaluation cohesive within the existing validator. Leave batching and helper shape to implementation; preserve merge-parent, rename and change-then-revert checks. No new cross-module adapter or requirement for CI to know review_sha. The altitude reader's claim that tests *must* reach through the caller is not established; do not mandate a public helper or call git-bearing code pure.
3. **fold-in · reuse** — File: plan.yaml; anchor: T-02 fixtures (~405–412). Summary: explicitly reuse committed-repository and argv-recording fixture patterns. Concrete cost: another git-fixture implementation and bespoke process witness add maintenance with no coverage gain. Alternative: build on `test-integration-shard-aggregation.py::repository`, real runner manifests, and the existing argv-append stub relocated into the trivial PATH shim. No shared fixture framework needed.
4. **fold-in · simplification** — File: plan.yaml and BRIEF.md; anchor: T-01 benchmark (~295–310), T-03 (~537–541), SC-04. Summary: reduce duplicate benchmark protocol prose. Concrete cost: three independently editable threshold/protocol descriptions. Alternative: T-03 references SC-04/T-01 and retains its own evidence-persistence obligation; preserve the idle-host acceptance run and all assertions.
5. **fold-in · simplification** — File: plan.yaml and BRIEF.md; anchor: T-01 (~312–316), T-02 (~416–420), T-03 (~527–534), Verification gaps. Summary: source-versus-installed identity guidance is repeated. Concrete cost: four differing phrasings can imply different evidence requirements. Alternative: cross-reference one identity rule while retaining task-local command budgets, full-suite obligations and the T-03 documentation landing. Do not remove caller-critical instructions merely for brevity.
6. **fold-in · altitude** — File: plan.yaml; anchor: T-02 refusal (~386–389), T-03 documentation (~504–513). Summary: avoid full repair-command duplication across role/team/spec/README surfaces. Concrete cost: approximately nine command/path copies drift on future CLI changes. Alternative: refusal supplies actionable exact command, DEC-255 states the rule, and other surfaces retain duties plus references. Preserve discoverability and QA's explicit force-add obligation.
7. **fold-in · altitude** — File: plan.yaml; anchor: T-03 DEC-255 (~494–499). Summary: distinguish schema authority from decision rationale. Concrete cost: copying schema fields creates a third version beside writer and verifier. Alternative: DEC-255 references `run-unit-tests.py::_write_manifest` and shared evidence verification, recording trust/identity/no-rerun policy rather than a second field list. The settled new decision and receipt contract remain intact.
8. **briefing-row · altitude** — File: plan.yaml and BRIEF.md; anchor: T-02 uncommitted receipts (~362–363), T-03 force-add (~510–511), Verification gaps. Summary: explicitly describe the residual if main forgets the settled force-add duty. Concrete cost: an accepted QA PASS may lack a committed inspectable receipt. Alternative: state that residual and its existing manual close-time inspection in the operator briefing; PM may clarify SC-09 evidence without adding a new gate. No automation, scope expansion, or change to accepted receipt trust is authorized here.
9. **leave · efficiency** — File: plan.yaml; anchor: T-01/T-02/T-03 prerequisite-reading paragraphs. Summary: repeated reference reads are not actionable waste. Concrete cost: negligible because all tasks are main-session-direct with reused context. Alternative: leave the task inputs explicit; no edit warranted.

## Per-member results / adjacency
All receipts are under `notes/` in this feature directory. All members returned PASS, files_touched: []. No angle returned empty; an empty angle would have been recorded as a valid result.

- **reuse / harness-backend-dev**: Python validator and async policy business logic adjacency. Three low flags; receipt `receipt-harness-backend-dev-r-20261122-2-simplify-eng-reuse.md`. Consolidated into findings 1–3.
- **simplification / harness-backend-dev**: TS lifecycle and Python validation-module adjacency, separate reader dispatch. Three low flags; receipt `receipt-harness-backend-dev-r-20261122-2-simplify-eng-simplification.md`. Consolidated into 1, 4, 5.
- **efficiency / harness-dev-ops**: CI/shard runners and timing adjacency. One low advisory and one leave observation; receipt `receipt-harness-dev-ops-r-20261122-2-simplify-eng-efficiency.md`. Consolidated into 2, 9. No measurements claimed.
- **altitude / harness-data-engineer**: manifest schema/serialization and validator data-contract adjacency. Four flags; receipt `receipt-harness-data-engineer-r-20261122-2-simplify-eng-altitude.md`. Consolidated into 2, 6–8. Helper/interface suggestion narrowed as explained in finding 2; force-add concern retained only as residual disclosure, not a new requirement.

## Open questions
None. Route advisory fold-ins and the residual briefing row to PM in a separate product run. This PASS certifies completion of the quality pass, not implementation correctness or approval of the pending plan.

```yaml
VERDICT: PASS
DIGEST:
  headline: 'Four-angle flag-only pass complete: nine deduplicated advisory findings;
    pending plan untouched.'
  open_questions: []
  files_touched: []
  expertise_update: []
  team: simplify
  steps_run: 4
  cycles_used: 0
  members:
  - step: reuse
    persona: harness-backend-dev
    verdict: PASS
    headline: Three low reuse flags.
    files_touched: []
  - step: simplification
    persona: harness-backend-dev
    verdict: PASS
    headline: Three low restatement-drift flags.
    files_touched: []
  - step: efficiency
    persona: harness-dev-ops
    verdict: PASS
    headline: One low lineage-work advisory; repeated reads left unchanged.
    files_touched: []
  - step: altitude
    persona: harness-data-engineer
    verdict: PASS
    headline: Four contract-placement flags, narrowed during consolidation.
    files_touched: []
  must_fix: []
  branch: none
  escalations: []
  adequacy_notes:
  - Four separate parallel reader receipts exist; adjacency and nine numbered five-part
    findings are recorded in digest.md.
  - Seven fold-in advisories, one briefing-row residual disclosure, one leave observation.
    PM applies separately.
  - No builds, tests, lint or git executed; neither plan.yaml nor BRIEF.md was written.
    No hash comparison claimed.
  - Identity-helper recommendation narrowed to preserve implementation freedom; no
    new public interface or gate mandated.
  - PASS certifies quality-pass completion, not implementation correctness or plan
    signature.
  sc_status: []
  needs_approval: none
  severity_max: low
  matrix_ok: none
  coverage_gaps: []
  findings:
  - kind: form
    scope: none
    severity: low
    reader: reuse,simplification
    summary: 'F1 fold-in: reuse grading classification and cross-reference SC-08.'
    why: Avoid duplicate bar logic and requirement drift.
  - kind: substance
    scope: none
    severity: low
    reader: reuse,efficiency,altitude
    summary: 'F2 fold-in: reuse revision resolver and share cohesive lineage work
      across kinds.'
    why: Avoid option-validation divergence, repeated git work and scattered identity
      logic.
  - kind: form
    scope: none
    severity: low
    reader: reuse
    summary: 'F3 fold-in: reuse repository fixtures and argv-stub patterns.'
    why: Avoid redundant fixture infrastructure.
  - kind: form
    scope: none
    severity: low
    reader: simplification
    summary: 'F4 fold-in: cross-reference benchmark protocol from T-03.'
    why: Avoid duplicate protocol copies without weakening acceptance.
  - kind: form
    scope: none
    severity: low
    reader: simplification
    summary: 'F5 fold-in: centralize identity guidance with task-local references.'
    why: Avoid conflicting evidence wording.
  - kind: form
    scope: none
    severity: low
    reader: altitude
    summary: 'F6 fold-in: centralize repair-command authority, retain duties.'
    why: Avoid command/path drift.
  - kind: form
    scope: none
    severity: low
    reader: altitude
    summary: 'F7 fold-in: decision cites schema authority instead of copying fields.'
    why: Avoid a third manifest schema statement.
  - kind: substance
    scope: none
    severity: low
    reader: altitude
    summary: 'F8 briefing-row: disclose forgotten force-add residual without adding
      a gate.'
    why: Receipt acceptance differs from committed availability.
  - kind: proportionality
    scope: task
    severity: low
    reader: efficiency
    summary: 'F9 leave: keep repeated prerequisite references.'
    why: Shared main-session context makes savings negligible.
  readers:
  - reader: reuse
    status: ran
    persona: harness-backend-dev
    reason: none
  - reader: simplification
    status: ran
    persona: harness-backend-dev
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
artifact: /Users/molchairuangutai/GitHub/harness/.claude/worktrees/harness/FEAT-2337-omp-native-gate-runtime/.harness/harness/features/FEAT-2337-omp-native-gate-runtime/runs/r-20261122-2-simplify-eng/digest.md
```
