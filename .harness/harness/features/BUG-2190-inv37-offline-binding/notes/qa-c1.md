# QA gate c1 — BUG-2190 T-01 @ cf13aab6 (harness-qa)

**BLUF: PASS.** The literal verify and the configured unit and integration kinds are green. Both c0 med findings are closed: mutants M4 and M6 are killed at the pin. One qualification: M6 is killed only by the "owner repo recorded" case, not by the missing-receipt or unproven-mirror cases (details below).

## Pin and range (measured)
- Pin `cf13aab63f308c1d59e33737205a3064fa35b194` is an ancestor of the feature HEAD `2c2ec69f`.
- `git diff --name-only cf13aab6 HEAD` lists only `feature.json`, so the tests I ran at HEAD are byte-identical to the pin.
- `git diff --quiet 33c0c181 cf13aab6 -- board.py` exits 0, so `board.py` is unchanged since 33c0c181.
- Tests changed in `33c0c181..cf13aab6`: exactly the two T-01 test files (`fcc91963`).
- Mutants ran in a disposable detached worktree at cf13aab6, which I removed afterwards. No source or test was edited.
- `HARNESS_AGENT_TYPE` was unset for the runs (repo G-07).
- Product `docs/spec.md`, `docs/decisions.md` and `docs/architecture.md` are absent (BRIEF Constraints agree). I used the BRIEF and the signed SCs only.

## Gates executed
| Command | Exit | Result |
|---|---|---|
| Literal verify (unit then integration) | 0 | Unit: 18 PASS (u.1–u.5). Integration: 12 ok (i.1–i.12). Whole chain 4.0 s. |
| `run-unit-tests.py --kind unit` | 0 | 59 files, 19.4 s. It ran `test-check-state-inv37-local-binding.py` (exit 0). |
| `run-unit-tests.py --kind integration` | 0 | 85 files, 99.8 s. It ran `test-check-state-inv37-offline.py` (exit 0). |

Matrix: the `bugfix` floor resolves to unit (runtime code touched). Integration was also run. Both kinds are satisfied, so `matrix_ok` is true.

## Recheck of the c0 must-fix items
The mutants are in-process patches applied after `check_state.board` is imported, via a sitecustomize on PYTHONPATH. A marker file confirmed each mutant installed in every run (1 hit for the unit run, 18 for the integration run's subprocesses).

| Mutant | Unit | Integration | Reading |
|---|---|---|---|
| M4: mapping guard removed in `_inv37_local_repo` | exit 1: `AttributeError: 'str' object has no attribute 'get'` from u.3 | `(i.12)` FAIL | Killed. The reds are semantic: a traceback and a missing invalid-binding finding. |
| M6: `_inv37_finding` passed the owner repo `org/repo` | `u.2 offline owner repo recorded: recovery guidance…` FAIL (`recover-terminal` instead of `recover-mirror`) | `(i.4)` FAIL | Killed. |

- **SC-03** (non-mapping factory): u.3 covers `"org/prod"` and `["org/prod"]`. It asserts the `expected a mapping` finding and `log == {resolve: 0, product_config: 0}`. i.12 does the same through the real entrypoint with no traceback and no contents reads. This closes the c0 finding.
- **SC-02** (recovery guidance): u.2 and i.3–i.5 now assert the recovery verb. i.3 also asserts the factory-derived path `/prod/features/<feat>`, and i.4 asserts `--previous-repo org/repo`. This closes the c0 finding.
- **M6 qualification, low severity.**
  - `recovery_command_for` selects `recover-mirror` only when `mirror_provenance_problem(doc, bound_repo)` is non-empty (`feature_schema.py:151-154`).
  - With `github={}` (missing receipt), no provenance problem arises for either repository, so the guidance is the same. With an unproven active mirror, the problem arises for either repository.
  - Only the owner-recorded case can tell factory.repo from the owner repo. So in the missing and unproven cases the guidance assertions pin the verb but cannot discriminate this mutant. Discrimination is unshown there. It is inherent to the selector, not a test defect (O-05).
  - I cannot say M6 would be caught for those two cases. I only observed that it is caught for the mismatch case.

## fail_first
- The natural pre-fix red for every SC is the c0 reproduction at 33c0c181: tests final with `board.py` swapped to `c6bd42d2`. Unit and integration both exit 1 with semantic reds. Evidence is `notes/review-harness-qa-c0.md`, § fail_first. The `board.py` diff is unchanged since then (measured above), so it still holds.
- For the c1 additions (u.2 verbs, u.3 non-mapping, i.12), the retained red tier is mutation (M4 and M6 above, run now at the pin). I did not run a natural red for them against the base `board.py`.
- Independence caveat (O-07): the c1 tests were added after the c0 review that raised the findings. Only my own evidence examined them. The code reviewer's and security reviewer's c1 notes were in flight, and I did not rely on them.

## SC status at cf13aab6
SC-01, SC-04, SC-05 and SC-06 are unchanged and met (their cases are green in the runs above). SC-02 and SC-03 are now met, with the M6 qualification above. No coverage gap remains against the Phase 1 list (`review-harness-qa-c0.md` § E1–E6).

## Open
None blocking.

## Principles applied
- Build the Lever: the sitecustomize mutant patcher (in /tmp, removed) reproduced M4 and M6 against both suites in one loop. It is not retained in the repo.
