# Receipt — simplify · altitude · FEAT-2337 plan surface (harness-data-engineer, r-20261122-2)

BLUF: 4 flag-only findings, none blocking; all on where the receipt contract is *stated*, not on settled scope. Angle: `harness-simplify/references/angle-altitude.md`. Scope: plan.yaml + BRIEF.md (pending). Nothing applied.

Checks performed: read plan.yaml (all tasks, D-01/D-02, decisions_affected), BRIEF, grilling Settled/Out-of-scope, panel-c1; grepped `check-integration-shards.py` (discover_expected/evidence_defects, :227/:243), `run-unit-tests.py` (_write_manifest :252, `--kind/--shard/--manifest`), bin for ancestry helpers and force-add mechanism.

## Findings

1. **Repair command / receipt path restated across ~8 surfaces** — plan.yaml T-03 intent (:504-513) folds the same `run-unit-tests.py --kind <kind> --shard 1/1 --manifest <run>/qa/manifest-<kind>.json` instruction into harness-qa.md, harness-validator-lead.md, verification-rules, validate.yaml, fix.yaml, plus SPEC, README and DEC-255, while T-02 (:386-389) emits it from validate-digest's refusal. Cost: a flag/path change must be made in ~9 places; docs and refusal text drift (the #919 rule drifted exactly this way — lived in code only, then in prose). Alternative: name two authorities — the refusal message (executable truth) and DEC-255 (rule); role/team/verification files carry QA's one-line duty and point at DEC-255, SPEC/README point only. **fold-in**.

2. **DEC-255 told to record the manifest schema** — T-03 (:494-499) has the decision record "path/schema/production command". The schema's authority is `run-unit-tests.py::_write_manifest` plus `evidence_defects`; T-02 already insists no schema change. Copying field lists into a decision creates a third statement that can drift from the runner. Alternative: DEC-255 cites the runner and shared verifier as schema authority and states only the trust rule (exact pin / feature-dir-only descendant, no rerun, CI backstop). **fold-in**.

3. **Pin-identity predicate has no named home** — T-02 (:369-375) plants the new "tested_commit == review_sha or descends with only the feature dir changed" logic (ancestry, NUL-safe per-commit paths, merge parents, renames) inline in `validate-digest.py#check_qa_matrix_claim`. BRIEF's maintainer outcome promises "one receipt-verification implementation shared with CI", but the shared module covers only coverage; the pin predicate is a separate, larger piece of git logic (only precedent: merge-gate.py:432 `--is-ancestor`, different purpose). Cost: tests must reach through the check_qa_matrix_claim caller, and it is untestable/reusable alone. Alternative: state it as one pure, importable function (inputs: review_sha, tested_commit, feature dir; output: ok/defects) that the exercised table drives directly. Do not move it into check-integration-shards (CI has no review_sha). **briefing-row**.

4. **Force-add residual has no compensating control** — receipts "may be uncommitted at QA return because main force-adds them" (T-02 :362-363; BRIEF Verification gaps). `.gitignore:7` ignores `runs/**`; I found no code or reference in bin/ or skills that force-adds run records, so the duty lives only in prose guidance (T-03 :510-511). A forgotten force-add leaves PASS accepted with no inspectable committed receipt and nothing (CI included) detects it. Accepted residual, control unnamed. Alternative: name the control in the plan — SC-09 inspection of `git ls-tree <pin> runs/<id>/qa/` in the validate record close step — or state explicitly that non-commit is an accepted, undetected residual. **briefing-row**.

## Open questions
None blocking.

## Principles applied
None cited (no craft leaf required for this read-only angle; migrate-callers-then-delete not consulted beyond plan's own cutover text).
