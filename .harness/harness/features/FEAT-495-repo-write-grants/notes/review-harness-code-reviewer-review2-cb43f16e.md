# FAIL — repository isolation is incomplete at cb43f16e

Reviewed `9f9a7301d85e40a2f6d8753506e6cef146c8eb85..cb43f16e`; clean initial worktree; no `[harness:human]` commits. Stage 1 compared SC-01..SC-08, plan decisions D-01..D-06 and DEC-250 before Stage 2. No build-lead amendments digest exists among the supplied notes; approved T-06 describes the run-start cutover.

## Findings (highest severity first)

- **R1 high, substance — SC-01/SC-02 omission:** `harness_boundary.py:915-921` labels every control-plane-base target `harness`; `check-domain.py:808-810` and `bash-write-guard.py:884-886` exempt that label. A product-a documentor writing `.harness/product-b/docs/change.md` in its otherwise permitted control-plane checkout reaches the wildcard `.harness/*/docs/**` grant (`.harness/team-config.yaml:141`) without a product-b claim. Checkout membership is not repository-segment membership (`harness_boundary.py:523-563`). **REASONED:** applies to Write, extractable Edit and Bash. Classify fleet-owned control-plane segments as their product, retaining only genuine Harness self-development exemptions.
- **R2 high, substance — SC-01/SC-02 omission:** `bash-write-guard.py:972-983` skips lexical cache paths before classification/binding. With `<control-root>/node_modules/foreign` symlinked to a declared product-b checkout, `echo x > node_modules/foreign/src/change.py` is a detectable product write but exits through the cache continue, even with no repository binding. The same applies to `.venv`, `__pycache__`, `.pytest_cache`; the prefix regex also accepts similarly prefixed ordinary directories. **REASONED:** resolve/classify target ownership before these skips; preserve noise exemptions only where they do not bypass product binding.
- **R3 high, substance — SC-02/SC-03 mismatch:** `inflight_registry.py:220-222,669-699,834-839` tombstones release, then authorization prunes the tombstone and permits unique-unbound fallback. State: child C's repository claim is released; a new same-role/same-feature receipt under C's parent is pending; C's next mutation callback still has a ready run gate. The adapter authorizes before invoking either guard (`.omp/extensions/harness-hooks.ts:1045-1068`), so authorization binds C to the new receipt and repository_binding returns allow instead of released. **REASONED:** released identities must not steal a sibling's pending receipt. Ordinary tombstone pruning with no replacement stays closed but loses the released category. `find_run_claim` excludes tombstones, `release_run` releases a unique live claim, and reconcile prunes tombstones as expired; those lifecycle paths otherwise preserve their stated live-claim semantics.
- **R4 high, substance — mechanical grade:** `harness_boundary.py:862`, `classify`: cyclomatic 7, cognitive 2, ABC 20.1; grade 3, production bar 4, driver ABC. Grader gates this changed function.
- **R5 high, substance — mechanical grade:** `tests/integration/test-inflight-registry.py:1185`, `case_38_repository_binding_through_run_start`: cyclomatic 8, cognitive 4, ABC 49.5; grade 1, test bar 3, driver ABC. Grader gates this changed function.
- **R6 med, substance — grade-2 reason:** `dispatch-guard.py:345`, `_repository_identity`: 14/22/37.4, grade 2. Reason: one cohesive preflight validates the artifact/header/fleet correspondence; splitting is not itself a security improvement, but keep the correspondence explicit.
- **R7 med, substance — grade-2 reason:** `inflight_registry.py:211`, `_expire`: 8/16/15.8, grade 2. Reason: one coherent lifetime predicate covers malformed, released and supervisor-owned rows; extracting meaningless branches would not improve its interface.

## Inspection and evidence

SC-07 inspected: target classification remains shared (`harness_boundary.py:887-912`), and both route adapters call the same exact-lineage/repository comparator (`check-domain.py:818`, `bash-write-guard.py:894`, `inflight_registry.py:756`), as DEC-250 specifies; R1/R2 limit its reach. Created run-start claims carry no repository and fail product binding (`inflight_registry.py:434-436,705-754`). Atomic registry replacement avoids partial-read snapshots (`harness_merge.py:145-167`); no independent partial-read fail-open was identified. SC-04's recorded live receipt was read, not rerun.

Measured: boundary suite ALL PASS; registry 170/170; dispatch 102/102; check-domain claims and Bash suites passed; OMP hook tests 100 passed, 0 failed. Output: `artifact://125`. These shipped tests do not exercise R1/R2/R3's scenarios. Pinned code-grade run failed with R4/R5 and grade-2 R6/R7 (`code_grade: fail`). No live probe, source edits or commits.

## Principles applied

- Model the Domain: distinguish a fleet-owned control-plane segment from the Harness base, and a revoked runtime identity from a merely absent claim (R1/R3).

Open questions: none. Must fix R1–R5; add discriminating regression cases for R1–R3 and rerun the affected deterministic suites plus pinned code grading.
