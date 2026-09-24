# FEAT-65 hook-site classification

## Scope and measured baseline

The baseline is `4e8c73c07e5f1f102c392fe3800616fc94a1c53d` on `main`. The eleven Python hooks invoked by `.claude/skills/harness/harness-hooks.ts` contain 77 broad catches:

| Hook | Sites | Owning suites |
|---|---:|---|
| `check-domain.py` | 24 | eight `test-check-domain*.py` integration suites |
| `validate-digest.py` | 18 | `test-validate-digest.py`, `test-code-grade.py` |
| `dispatch-guard.py` | 9 | `test-dispatch-guard.py` |
| `bash-write-guard.py` | 6 | `test-bash-write-guard.py` |
| `merge-gate.py` | 5 | `test-merge-gate.py` |
| `branch-create-gate.py` | 4 | `test-branch-create-gate.py` |
| `gh-close-gate.py` | 3 | `test-gh-close-gate.py` |
| `inflight_registry.py` | 3 | `test-inflight-registry.py` |
| `inject-expertise.py` | 2 | `test-inject-expertise.py` |
| `plan-sign-gate.py` | 2 | `test-plan-sign-gate.py` |
| `feature-record.py` | 1 | `test-feature-record.py` |

The target is zero broad catches in those eleven files. `check-plan-routes.py:BROAD_CATCH_CEILINGS` must retain only `harness_boundary.py: 2`; an absent hook entry, not an explicit zero, is the final state.

## One classification for every site

Each numbered group below accounts for the hook's full measured count. “Typed boundary” means catch only the producer's documented exception type(s) and the local built-ins the operation can genuinely raise, while retaining the existing branch result. “Guard” means allow an unanticipated `Exception` to reach `harness_boundary.hook_guard`; it does not mean changing a hook's fail-open or fail-closed verdict.

### `check-domain.py` — 24

1. `_root` boundary import — typed import failure; retain derived-root fallback.
2. hook payload load — typed artifact/JSON failure; retain empty-payload behavior.
3. `_run_domain` boundary import — closed `hook_guard` boundary-load path; retain exit 2.
4. `_run_domain` manifest load — typed YAML/schema failure; retain exit 2.
5. `_hook_paths_for` boundary import — closed `hook_guard` boundary-load path; retain exit 2.
6. shape-only YAML import probe — typed import failure; retain “no parser” result.
7. `_approval_entries` manifest load/view — typed YAML/schema/input-shape failures; retain diagnostic result.
8. approval-fragment disk read — typed `OSError`/decode failure; retain pass-through diagnostic.
9. approval-fragment proposed YAML parse — typed YAML/type/value failure; retain pass-through diagnostic.
10. `feature_checkout_guard` rule-level absorber — delete; unexpected defects reach the outer guard.
11. `claim_checkout_guard` operation — catch the registry's explicit unreadable-registry result only; unexpected defects reach the outer guard.
12. `claim_checkout_guard` exception-type probe — delete the nested broad classifier; import/use the exported type directly.
13. `_norm` checkout-relative lookup — typed import, path and OS failures; retain relative-path fallback.
14. `_checkout_root` lookup — typed import, path and OS failures; retain caller root fallback.
15. `RE_RUN_IDENTITY` shape import — typed missing-module/missing-symbol failure; retain never-match repair fallback.
16. plan content parse — typed YAML failure; retain ownership-neutral result.
17. feature-budget helper — typed import/read/shape failures; retain stricter “count everything” fallback.
18. feature-schema validation — catch the schema reader's exported input/schema failures; unexpected defects reach the outer guard and cannot become exit 1.
19. run-state schema validation — catch exported artifact/schema/input failures and preserve the existing denial.
20. run-identity post record — catch only documented marker/write/input failures; retain best-effort post behavior.
21. prior-state parse — typed YAML failure; retain the current transition diagnosis.
22. Done-when validator call — catch the repo-module/validator's explicit boundary failures; retain refusal.
23. linked-worktree sweep discovery — typed OS/path/decode failures; retain the reduced sweep.
24. dirty-check subprocess — typed OS/subprocess/decode/value failures; retain “unknown cleanliness”.

### `validate-digest.py` — 18

1. canonical code-grade invocation — typed OS/subprocess/decode/value failure; retain grading failure result.
2. `review_sha` feature record load — exported feature-record failure; retain untrusted claim.
3. feature branch load — exported feature-record failure; retain no branch.
4. pending plan load — exported plan YAML/schema failure; retain unreadable-plan finding.
5. pinned feature load — exported feature-record failure; retain unreadable-record finding.
6. `_root_or_none` resolution — typed import/path/value failure; retain `None`.
7. `_hook_feature_dir` resolution — typed boundary/registry/path failure; retain `None`.
8. `_feature_artifact_root` resolution — typed boundary/registry/path failure; retain `None`.
9. durable-file validation own-failure line — delete local broad catch; guard emits the canonical hook failure.
10. re-verification feature-root resolution — typed boundary/registry/path failure; retain no re-verification root.
11. re-verification subprocess — typed OS/subprocess/decode failure; retain unavailable re-verification.
12. hook payload load — typed artifact/JSON failure; retain pass-through verdict and re-pin the diagnostic.
13. inflight registry import — typed import failure; retain loud unenforced-claim result.
14. live-child read — exported unreadable-registry/path failure; retain loud unenforced-return result.
15. claim release — exported registry/write failure; retain non-blocking cleanup result.
16. release-command composition — typed registry/path/value failure; retain the blocking return-contract verdict.
17. returned-digest validation own-failure line — delete local broad catch; guard emits the canonical hook failure.
18. CLI stdout reconfiguration — typed attribute/OS/decode failure; retain CLI operation.

Only hook mode is wrapped. Direct CLI behavior is not silently converted into hook pass-through behavior. The existing hook name is `check-digest`.

### Nine smaller hooks — 35

- `bash-write-guard.py` (6): root import, payload load, boundary-module load, feature-checkout rule absorber, claim enforcement, and nested exception classifier. Delete both rule-level/nested absorbers where the outer guard owns defects; use typed import/artifact/registry boundaries for the rest. The existing blocked boundary-load verdict remains blocked.
- `branch-create-gate.py` (4): DEC-234 bootstrap root resolver, GitHub config load, config shape read, and command extraction. The prologue becomes the exact run-unit-tests tuple; the other three catch only artifact/input/subprocess boundary failures while retaining the shell-compatible outcomes.
- `dispatch-guard.py` (9): bootstrap glob probe, payload load, registry import, run-dir shape check, spawn allowlist read, declared-root resolution, tool-grant read, feature-root resolution, and claim. Catch typed import/artifact/registry/path failures only; unexpected hook defects reach the guard. Existing governed-dispatch refusals and fail-open infrastructure branches do not change.
- `feature-record.py` (1): proposed-rework plan load. Catch only exported YAML/plan-schema failures and retain the refusal.
- `gh-close-gate.py` (3): DEC-234 bootstrap resolver, GitHub config load, payload command read. The prologue becomes the exact reference tuple; config/payload catches use their artifact/input types and retain pass-through.
- `inflight_registry.py` (3): Linux `/proc/<pid>/stat` plus `/proc/stat` catches exactly `(OSError, ValueError, IndexError, StopIteration)`; `ps -o lstart=` catches exactly `(OSError, subprocess.SubprocessError, ValueError)` and retains `None`, so liveness still falls back to 24 hours; feature worktree lookup catches exactly `(harness_boundary.AmbiguousWorktree, OSError)` and retains owner root.
- `inject-expertise.py` (2): root resolver and payload reader. Catch typed import/path and artifact/input failures while retaining empty results.
- `merge-gate.py` (5): DEC-234 bootstrap resolver, candidate feature-record load, payload read, named-feature receipt evaluation, and inferred-feature receipt evaluation. The prologue becomes the exact reference tuple; typed feature/artifact/schema boundaries retain their present deny/pass results, while unexpected hook defects use the guard without changing verdict.
- `plan-sign-gate.py` (2): DEC-234 bootstrap resolver and payload reader. The prologue becomes the exact reference tuple; payload failures use the artifact/input types and retain pass-through.

The four DEC-234 copies in `branch-create-gate.py`, `gh-close-gate.py`, `merge-gate.py`, and `plan-sign-gate.py` must match the `run-unit-tests.py` prologue byte-for-byte, including the FEAT-64 reciprocal-copy comment. The lock covers all five copies and fails when any one is mutated.

## Operator contract and evidence

For an unexpected hook defect, `harness_boundary.hook_guard` is the only broad catch and emits:

`<name>: the hook failed internally (<Type>: <msg>) — passing through; this is not a pass, nothing was checked.`

The check-domain and other already-closed boundary-load branches use the guard's closed form and preserve exit 2. Every other exit code, stdout byte, and stderr byte stays unchanged except for the eleven legacy own-failure/pass-through lines intentionally replaced by the canonical guard wording. Each replacement or deletion must be recorded in `notes/build-divergences.md` as old bytes, new bytes, and ruling, and its owning suite must be re-pinned.

Final receipts come from a clean checkout of the eventual review pin, not the implementer's dirty worktree. `notes/clean-pin-byte-receipts.md` must name the pin and record the invoked suites plus exit/stdout/stderr evidence. The census receipt must prove zero broad catches across all eleven hooks and exactly `harness_boundary.py: 2` in the ceiling map.

## Planning decisions grounded in project rules

- DEC-174 controls execution: every production hook, enforcement test, and evidence task is `main-session-direct`.
- DEC-234 controls the five bootstrap prologues: copied code remains the chosen design until code can import shared code safely.
- “Outcome-oriented execution” keeps the plan ordered by independently verifiable hook cohorts rather than by production-versus-test layers.
- “Redesign from first principles” rejects a second local exception idiom: typed expected boundaries plus the existing deep `hook_guard` module are sufficient.
