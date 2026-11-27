# FEAT-2537 patch intake — product run r-20261125-1-plan-product

**BLUF: PASS.** The patch intake is ready for signature. `BRIEF.md` is 69 lines with Approval pending. `plan.yaml` has one task, T-01. T-01 is `main-session-direct` (DEC-174), `change_type: cross_module`, traces SC-01..SC-04, and its `decisions_affected:` names DEC-199, DEC-204 and DEC-218 (all `amend`). pm reported that `plan-merge.py check` exited 0. The orchestrator re-runs it.

## Member
- **intake** (harness-pm): PASS. Wrote `../../BRIEF.md` and `../../plan.yaml` and appended its observations log.

## Lead assessment
I wrote the send-back criteria before dispatch (`acceptance-criteria.md`). The artifacts meet all eight:
- T-01 `files:` excludes the fixture and `test-validate-digest.py`. Its verify block asserts that both are byte-identical to the merge-base, and that `canonical-reader-classification.json` and `validate-digest.py` are too.
- The ledger-first ordering, both directions of case 18, and the comment-only diff for `harness-hooks.ts` are each written into T-01, and each is asserted by a verify block or an SC.
- The rework budget (1 round / 45 min) is recorded under Constraints, unsigned.
- `INFLIGHT_REGISTRY_DIR` exists, so the base-module swap that SC-02 relies on is real (`tests/integration/test-inflight-registry.py:35`).

## The one signature question (Q-01)
pm widened the ruled class from "the extinct v1 shape" to "every non-v2 object", and that includes `{}`. Today `{}` meets `_known_shape`'s v1 predicate: the vacuous `all()` is true. A strict read of `{}` therefore returns `[]`, and after the patch it raises. I verified at source that no writer produces `{}`. Every direct registry seeder seeds v2: `test-validate-digest.py` `_b1898_seed`, `tests/unit/omp-hooks.test.ts` `seed`, and `test-lead-start-return.py`. Only the writer `_empty()` writes, and it writes v2.

pm did not flag one more delta. A dict that is neither v1 nor v2 (for example `{"schema_version": 2, "claims": 1}`) is already refused by strict readers today, and the locked writer silently folds it to empty. After the patch, the writer emits a stderr warning as it folds it. The change is stderr-only.

**Recommendation: accept both as in-class.** `{}` is a zero-persona v1 map, and the warning-only delta is the existing corrupt-as-empty convention. The grilling's stop clause says "further behavior delta … stops for a ruling", so the signer rules on this explicitly at signature and nobody re-cycles over it.

## Not run, by design
Patch lane (DEC-225): no readers, no panel, no goal-check.

## Noted for the orchestrator
check-state reports INV-37: github.sync is on and the feature has no Build-entry receipt yet. This is orchestrator work.

```yaml
VERDICT: PASS
DIGEST:
  headline: 'FEAT-2537 patch intake is ready for signature: a 69-line BRIEF with Approval
    pending, and a one-task plan (T-01, main-session-direct, cross_module, traces
    SC-01..04, amends DEC-199/204/218). One signature question: the v1 class widened
    to cover {} and other non-v2 objects. Recommendation: accept.'
  team: plan (patch lane)
  steps_run: 1
  cycles_used: 0
  members:
  - step: intake
    persona: harness-pm
    verdict: PASS
    headline: BRIEF.md (69 lines, Approval pending) and plan.yaml (one task T-01,
      approval pending, status plan); pm reports plan-merge check exit 0
    files_touched:
    - /Users/molchairuangutai/GitHub/harness/.claude/worktrees/harness/FEAT-2537-registry-record-cleanup/.harness/harness/features/FEAT-2537-registry-record-cleanup/BRIEF.md
    - /Users/molchairuangutai/GitHub/harness/.claude/worktrees/harness/FEAT-2537-registry-record-cleanup/.harness/harness/features/FEAT-2537-registry-record-cleanup/plan.yaml
    - /Users/molchairuangutai/GitHub/harness/.claude/worktrees/harness/FEAT-2537-registry-record-cleanup/.harness/harness/features/FEAT-2537-registry-record-cleanup/observations/harness-pm.md
  must_fix: []
  branch: none
  escalations: []
  adequacy_notes:
  - 'Patch lane (DEC-225): no readers, no panel and no goal-check were run, by design.
    The PASS rests on the lead''s check against eight send-back criteria written before
    dispatch (runs/r-20261125-1-plan-product/acceptance-criteria.md).'
  - plan-merge.py check exit 0 was reported by pm and was not re-run at this tier,
    because this tier has no shell. The orchestrator re-runs it.
  - 'T-01 files: exclude the fixture and test-validate-digest.py. The verify block
    asserts both are byte-identical to the merge-base, and also canonical-reader-classification.json
    and validate-digest.py.'
  - SC-02's base-module swap relies on INFLIGHT_REGISTRY_DIR, which exists (tests/integration/test-inflight-registry.py:35).
  - change_type cross_module was chosen by pm from the repository's configured matrix,
    and the plan-merge check accepted it.
  - The rework ruling of 1 round / 45 min is recorded under BRIEF Constraints, unsigned.
  sc_status:
  - id: SC-01
    verdict: not_met
    method: automated
    evidence: 'Planned (integration): live_children absent from bin/.omp/extensions;
      2b/2c deleted; 25 on exact-parent live_claims; 29 via live_claim.'
  - id: SC-02
    verdict: not_met
    method: automated
    evidence: 'Planned (integration): case 18 asserts both v1 directions; per-state
      controls for writer-producible states; base-module swap via INFLIGHT_REGISTRY_DIR.'
  - id: SC-03
    verdict: not_met
    method: inspection
    evidence: 'Planned: DEC-199/204/218 rewritten in place before code; DECISIONS-INDEX
      regenerated; immutable records byte-identical.'
  - id: SC-04
    verdict: not_met
    method: inspection
    evidence: 'Planned: both hook comments state verified behaviour; harness-hooks.ts
      diff comment-only.'
  needs_approval: true
  severity_max: none
  matrix_ok: none
  coverage_gaps:
  - SC-03 and SC-04 grade prose truth by inspection only. The EventBus claim rests
    on the Spike F read of omp 19.1.1 (answers-spike-f-2026-11-24.md), and no test
    re-runs that read.
  findings: []
  readers: []
  open_questions:
  - id: Q-01
    question: 'Signature ruling: D-01 and the BRIEF Constraints widen the ruled fail-closed
      class from ''the extinct v1 shape'' to ''every non-v2 object''. Two deltas follow.
      (1) For the empty object {}, a strict read returns [] today and raises UnreadableRegistry
      after the patch. Today {} passes _known_shape''s v1 predicate through a vacuous
      all(). (2) For a dict that is neither v1 nor v2 (e.g. schema_version 2 with
      non-list claims), strict readers already refuse it today; after the patch the
      locked writer also emits a stderr warning when it folds the dict to empty, where
      today it folds silently. Verified at source: no writer produces either shape.
      _empty() writes v2, and every direct test seeder (test-validate-digest.py _b1898_seed,
      omp-hooks.test.ts seed, test-lead-start-return.py) seeds v2. Recommendation:
      accept both as in-class. {} is a zero-persona v1 map, and the warning is the
      existing corrupt-as-empty convention. The grilling''s stop clause requires the
      signer to rule explicitly.'
    blocking: true
  - id: Q-02
    question: 'check-state reports INV-37: github.sync is on and the feature has no
      Build-entry receipt yet (gh-sync.py open). This is orchestrator or main-session
      work before build.'
    blocking: false
  files_touched:
  - /Users/molchairuangutai/GitHub/harness/.claude/worktrees/harness/FEAT-2537-registry-record-cleanup/.harness/harness/features/FEAT-2537-registry-record-cleanup/BRIEF.md
  - /Users/molchairuangutai/GitHub/harness/.claude/worktrees/harness/FEAT-2537-registry-record-cleanup/.harness/harness/features/FEAT-2537-registry-record-cleanup/plan.yaml
  - /Users/molchairuangutai/GitHub/harness/.claude/worktrees/harness/FEAT-2537-registry-record-cleanup/.harness/harness/features/FEAT-2537-registry-record-cleanup/observations/harness-pm.md
  - /Users/molchairuangutai/GitHub/harness/.claude/worktrees/harness/FEAT-2537-registry-record-cleanup/.harness/harness/features/FEAT-2537-registry-record-cleanup/runs/r-20261125-1-plan-product/state.yaml
  - /Users/molchairuangutai/GitHub/harness/.claude/worktrees/harness/FEAT-2537-registry-record-cleanup/.harness/harness/features/FEAT-2537-registry-record-cleanup/runs/r-20261125-1-plan-product/acceptance-criteria.md
  expertise_update: []
artifact: /Users/molchairuangutai/GitHub/harness/.claude/worktrees/harness/FEAT-2537-registry-record-cleanup/.harness/harness/features/FEAT-2537-registry-record-cleanup/runs/r-20261125-1-plan-product/digest.md
```
