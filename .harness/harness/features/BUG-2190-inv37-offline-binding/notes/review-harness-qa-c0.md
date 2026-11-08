# QA gate — BUG-2190 T-01 @ 33c0c181 (harness-qa, cycle c0)

**BLUF: PASS with two coverage gaps.** The configured unit and integration kinds and the literal verify are green at the pin. Every automated SC has a natural, semantic red at the pre-fix `board.py`, which QA reproduced. Two literal SC clauses have no assertion, and mutants survive them. SC-02 recovery guidance names no repository. SC-03 has no malformed non-mapping `factory` case. Intent is met by construction; the text is not proven.

## Pin / environment
- The feature worktree HEAD is `a0e849d2`, not the pin. The two commits after the pin, `bb129db1` and `a0e849d2`, touch only `feature.json` and `runs/…/.run-identity.json` (`git diff --stat 33c0c181 HEAD` shows 2 files). I did not run in that tree.
- I ran everything in a managed pinned checkout (`pinned-checkout.py add --sha 33c0c181…`). `rev-parse HEAD` is `33c0c181e62c5e75692c8320fc01aaaaf06fa40b`, and `worktree-state.py --verify` exits 0 (converged). `HARNESS_AGENT_TYPE` was unset for the runs (repo G-07).
- Diff base is `c6bd42d2`. Corpus-prune files from `907225c1` are out of scope. I read the diff only for the T-01 files: `board.py`, `table.py` (adds `gh:auth` to the INV-37 row), the two new tests, the classification JSON and the DECISIONS docs.

## Phase 1 expectations, derived from BRIEF/plan before reading source
- E1: offline, a bound feature with a valid receipt is clean and makes zero remote reads, including with sync off (SC-01).
- E2: offline, a missing receipt, an absent `github.repo` and a mismatched `github.repo` each give the receipt finding. Comparison and recovery guidance use `factory.repo`. Zero remote reads (SC-02).
- E3: offline, each of the following gives an invalid authoritative binding: a malformed factory shape, a malformed or non-string or empty repo, and an unlisted repo. No owner fallback and no remote read. A bypass mutant must be rejected (SC-03).
- E4: online, the same fixture keeps remote `resolve_binding`. A remote failure stays an invalid binding. Remote-call assertions prove it ran (SC-04).
- E5: owner/unbound, sync-off and legacy-provenance controls keep their results beside a valid bound feature, and a feature with no plan is ineligible (SC-05).
- E6: in-process unit tests of the real `inv_37` with `gh_ok` false (SC-06).

## Matrix
- `bugfix` has `always: []`. Its `when` clauses are: `unit` if `touches_runtime_code`, which is true because `board.py` and `table.py` changed; `integration` if `fix_confined_to_tests_and_contract_docs`, which is false; and `__bug_class__` / `match_bug_class`, an unresolvable placeholder (repo G-08).
- The required floor is therefore `unit`. The brief and dispatch also require `integration` for the bug class. `unit` is satisfied and `integration` is satisfied; both were performed.
- `matrix_ok` is true.

## Runs at the pin (sequential, no concurrency)
| Command | Exit | Result |
|---|---|---|
| Literal verify: `python3 tests/unit/test-check-state-inv37-local-binding.py && python3 tests/integration/test-check-state-inv37-offline.py` | 0 | 13 PASS lines (u.1–u.5) and 11 ok (i.1–i.11). Zero lines match `fail`. Wall time **3.06 s** (<60 s). |
| `run-unit-tests.py --kind unit` | 0 | `pool: 8 workers, 59 files, 19.15 s`. It ran `test-check-state-inv37-local-binding.py` (exit 0, 0.14 s). No `FAIL test-` line. Four `FAIL BUG-1290 …` lines come from `test-factory-claim-mutation.py`'s own mutation proof and are not failures (repo G-09). |
| `run-unit-tests.py --kind integration` | 0 | `pool: 8 workers, 85 files, 97.03 s`. It ran `test-check-state-inv37-offline.py` (exit 0, 3.67 s). No `FAIL test-` line. |

Discovery is genuine. The runner executed both new files as named scripts: u.1–u.5 (13 assertions) and i.1–i.11. The runner's `PASS test-*.py` line counts (60 unit, 90 integration) differ from the pool file counts (59 and 85). I did not reconcile this (repo G-11). I used the pool counts and exit codes.

Count drift: the build evidence says the unit run has "14 PASS". I measure 13 at the pin, so the note's count is off by one. This does not affect any verdict.

## fail_first (natural red = tests final, `board.py` swapped to `c6bd42d2` in the pin, then restored)
Reproduced by QA on `33c0c181` tests with base `board.py`. Unit exit 1, integration exit 1. The reds are semantic (remote reads and misclassification), not import or setup errors. The tier is a natural red from swapping the pre-fix production file, not the historical `4612447f` red commit. The build-evidence table (fail-first witnesses) agrees with it: receipt-only for the original run, plus this reproduction.

| SC | Red witness at base (test, observed) | Control / twin |
|---|---|---|
| SC-01 | i.1 FAIL, i.2 FAIL. u.1 "neither remote boundary reached" FAIL (`log={'resolve':1,'product_config':2}`). | |
| SC-02 | i.3, i.4, i.5 FAIL. u.2 ×3 FAIL (binding finding replaces the receipt finding). | |
| SC-03 | Valid-bound twin red: i.1 and u.1. | Invalid cases i.6 and u.3 ×4 are green at base (unchanged controls). The bypass mutant is shown below. |
| SC-04 | Offline member red: i.1 and u.1. | Online members i.7, i.8 and u.4 are green before and after by design. Mutant M8 (online skips the resolver) reddens them: i.7, i.8, u.4 ×2. |
| SC-05 | i.9 FAIL, i.10 FAIL, u.5 "owner beside bound" FAIL. | i.11 (no plan) and u.5 "missing owner receipt" stay green. |
| SC-06 | u.1, u.2 ×3 and u.5 FAIL at base, so the unit kind has its own natural red. | |

## Mutants (QA lever `/tmp/qa-mutate.py`, applied to board.py in the pin, restored by `git checkout 33c0c181`; `git status --porcelain` clean afterwards)
| Mutant | Unit | Integration | Reading |
|---|---|---|---|
| M1 bypass all local validation (SC-03) | red: u.3 ×4 | red: i.6 | **Killed.** The invalid cases reject the SC-03 bypass. The mutant is retained only in my lever and the build-evidence receipt, not in the repo. |
| M2 drop fleet membership only | red: u.3 `org/gone` | red: i.6 | Killed. |
| M5 owner fallback offline | red ×7 | red ×6 | Killed (no owner fallback). |
| M7 offline branch also taken for unbound features | red u.5 ×2 | red i.9, i.10 | Killed. |
| M8 online skips the resolver | red u.4 ×2 | red i.7, i.8 | Killed. |
| M3 drop `_REPOSITORY` syntax check only | green | green | **Survives**, but it is probably equivalent. `repo_entry` already rejects the malformed values in the fixtures (`"not a repository"`, `5`, `""`) via fleet membership. A fleet entry with a malformed name is untested. Low severity. |
| M4 drop non-mapping `factory` check | green | green | **Survives.** No test uses a non-mapping `factory`. |
| M6 recovery command uses the owner repo | green | green | **Survives.** No test asserts the repository in the recovery command. |

## coverage_gaps and criterion-literal findings
1. **SC-02 text unmet (partial), severity medium.** The criterion says "comparison and recovery guidance use factory.repo". Comparison is asserted by i.4 and u.2 (`conflicts with bound repository 'org/prod'`). No test asserts the `recovery_command_line` repository, and mutant M6 survives. In the code, the same `repo` variable feeds both, so the intent is satisfied by construction. Kind: missing-assertion. Task: T-01.
2. **SC-03 text unmet (partial), severity medium.** "Offline malformed factory shapes": u.3 and i.6 use only a `factory` mapping with a bad `repo` value. The non-mapping branch (`board.py` `_inv37_local_repo`, "expected a mapping") has no test, and mutant M4 survives. Kind: missing-case. Task: T-01. This matches the peer goal-check note from `Bug2190Validate.NarrowTrout`.
3. **Retention, severity low.** The SC-03 bypass mutant lives only in the receipt (the build-evidence "SC-03 bypass mutant" section) and in my uncommitted lever. The repo carries no mutation test. It is acceptable under "QA records".
4. **SC-04 pairing, severity low.** Pre-fix the online members are green. The paired failing evidence is carried by the offline twin, per the criterion's "offline/online paired regression".
5. Non-blocking, not exercised: `table.py` `gh:auth` declaration. The integration kind ran `canonical-reader-classification` and was green. I did not separately assert the table row.

Receipt-only vs exercised: I re-executed the base-`board.py` red run and the mutants myself, because the `c6bd42d2` `board.py` swap was cheap. I did not re-run the historical `4612447f` red commit.

## Principles applied
- Build the Lever: `/tmp/qa-mutate.py` applies a named mutant, runs both regressions and restores through git. It reproduces the mutant matrix in one command. It is not in the repo and is not a retained lever.

## Cleanup
The pinned checkout is removed on return with `pinned-checkout.py remove`, run id `2026-11-08-02-validator`, persona `harness-qa`.
