# Goal-check (validate c3) — FEAT-2581 feature_record package

- review_sha: `c039c32dea25d26e3235ee90e1343d7280ddfd4e`
- baseline: `e12381fd`
- prior pin: `a03103b0`
- implementation pin: `c91df7a5`
- run: 2026-11-27-03-validate-validator

**BLUF: FAIL.** The failure is one gate, not the product.

- **SC verdicts.** SC-01..SC-10 are met on discriminating evidence, and both perspectives are discharged.
- **Decision rows.** The amend rows for DEC-259, DEC-220 and DEC-150 have landed.
- **No regression.** `git diff a03103b0 c039c32d` outside the feature directory is empty.
- **The failing gate: T-03's signed `verify:`, run exactly as written at the pin, is red.**
  - Its python block raises `AssertionError: build-divergences.md test_change records are not the
    baseline-to-pin diff of every changed test path` for all 29 test paths.
  - The shell still exits 0. The verify is two newline-separated commands, so its status is that of
    the trailing `check-plan-routes.py --canonical-reader-audit`.
  - So P5's claim "T-03 verify passes at c039c32d" is refuted in this environment (finding VF-1).

## What I executed

Everything below ran under `env -u HARNESS_AGENT_TYPE` from the worktree root. HEAD was `177af2d5`, which differs from the pin only in `feature.json` and an observations log.

1. **Verify blocks.** I extracted each one byte-for-byte from `git show c039c32d:<FD>/plan.yaml` (yaml load, task `verify`).
   - **T-01:** exit 0 in 27 s, printing `ALL PASS` and `0 unresolved reader site(s) across 110 Python file(s)`.
   - **T-02:** exit 0, printing `T-02 decisions PASS`.
   - **T-03:** exit 0. The python part raised the AssertionError above, at plan line `TC={...}`, and never printed `T-03 receipts PASS`.
2. **The cause of the T-03 failure is environmental drift, not the fix commit.**
   - `git count-objects -v` reports `in-pack: 65632`, which is past 2^16. Git's automatic abbreviation therefore grew from 8 to 9 hex digits: `git rev-parse --short HEAD` gives `177af2d5e`, where round 2 printed 8-digit shorts.
   - The verify (and `feat2581-cleanpin.py#test_changes`) runs `git diff` without `--full-index` or a fixed `core.abbrev`, so the `index aaaaaaaa..bbbbbbbb` lines no longer match the committed records.
   - I measured all 29 paths. Without a fixed abbreviation, all 29 mismatch, and 0 of them mismatch outside `index ` lines. With `core.abbrev=8`, 0 mismatch.
   - I re-ran the whole T-03 verify with `GIT_CONFIG_COUNT=1 GIT_CONFIG_KEY_0=core.abbrev GIT_CONFIG_VALUE_0=8`. It printed `T-03 receipts PASS at c039c32d…`, then `0 unresolved … across 110`. Every other T-03 assertion therefore holds at the pin.
3. **The code-grade claim in P5 holds.** `code-grade.py --base e12381fd --head c039c32d` exits 0 with `PASSING: 280` and 0 `RESULT: FAIL`.
4. **P1: confirmed within its contract.** I loaded the pinned `private_parent` by AST and ran it on these cases:

   | Case | Result |
   |---|---|
   | absent | rc 0, mode 0700 |
   | own 0700 | rc 0 |
   | own 0755 | rc 0 (no group/other write bit, as the claim states) |
   | own 0777, 0775, 0757, 1777 | rc 1 with `refusing …` |
   | symlink to an own-0700 dir | rc 1 (lstat) |
   | regular file | rc 1 |

   I did not execute the other-owner case.
5. **P2: confirmed at function level.**
   - The pinned `_exit_as(-9/-15/3)` gives returncodes -9, -15 and 3, with empty stderr.
   - a03103b0's `_exit_as(-9)` gives rc 1 with `OSError: [Errno 22]`, which is the CR-3 defect.
   - I did not re-run the wrapped child-runs-once scenario.
6. **P3 and P4: confirmed.** `git diff a03103b0 c039c32d` of the generated receipt shows only these changes:
   - three `script_sha256` lines (cleanpin, ledger-driver, sitecustomize);
   - the two footer lines relabelled `normalized` → `decompressed jsonl sha256`, with the values unchanged (`3a8fb085…`, `59e5b9ae…`);
   - the `generated` stamp.

   `build-divergences.md`, `divergence-rulings.json` and `measurements/` are byte-identical (empty diff stat).
7. **Provenance disclosure: names the recorder change.** `clean-pin-byte-receipts.md` adds a fix-round-2 bullet saying the recorder no longer resets SIGKILL/SIGSTOP. Its preceding bullet states the measurements ran with the c65ceb81 bytes, so the widened gap is named.
8. **P6: confirmed. F-1 is reworded with no change to any ruling's substance.**
   - The OQ-V1 sentence now reads "no committed tool writes ruling metadata (the generator only seeds an empty `[]` file when none exists)". This is true: `feat2581-cleanpin.py#load_rulings` at c039c32d writes `[]\n` only when the file is absent.
   - The disposition (accepted risk, T-03 verify unamended) is unchanged, as are the generator-half fix and the SEC-2 non-routing.
   - The only other change is a factual SEC-1 sentence describing fix round 2's parent check, which matches item 4.

## Perspectives

- **operator: pass on substance.** It is carried by SC-03, SC-04, SC-05, SC-06, SC-08 and SC-10.
  - The recomputation proving them passes at the pin once the abbreviation length the records were generated with is held fixed.
  - The signed gate that should show this is red as written (VF-1).
- **code maintainer: pass.** It is carried by SC-01, SC-02, SC-07 and SC-09: T-01 and T-02 exit 0, the audit reports 0 unresolved sites across 110 files, and the product is unchanged since c1.

## SC grading

Product subjects are byte-identical since a03103b0 (and 62da4501).

| SC | verdict | method | evidence |
|---|---|---|---|
| SC-01 | met | inspection | T-01 verify, exit 0 at c039c32d, with `ALL PASS`. The product diff from a03103b0 is empty. |
| SC-02 | met | inspection | T-03's grade-assert leg passes at the pin and is red at the baseline with exactly the twelve (in the abbrev-8 run). The receipt's grade lines are unchanged. |
| SC-03 | met | automated | T-03's `ng`/FAIL-line assertions pass (abbrev-8 run). The `test_change` bodies equal the live baseline-to-pin diff for all 29 paths except the `index` abbreviation. qa's c3 run is to be cited by the lead. |
| SC-04 | met | automated | The same recomputation for integration files, together with the INV-40 observer in the T-01 output. |
| SC-05 | met | inspection | `cli_identity: PASS`, and the per-class assertion passes (abbrev-8 run). The measurements are byte-identical to a03103b0. |
| SC-06 | met | inspection | `replay_identity: PASS`, recomputed (abbrev-8 run). |
| SC-07 | met | inspection | The audit reports `0 unresolved … across 110` (T-01 and T-03). The classification JSON is unchanged. |
| SC-08 | met | inspection | The `d02_item` and residual lines are recomputed and pass (abbrev-8 run). The D-02 literals are unchanged. |
| SC-09 | met | inspection | See the dispositions below. `gen-decisions-index.py --stdout` cmp the pinned index: equal. |
| SC-10 | met | inspection | The `case_set` lines are recomputed and pass (abbrev-8 run). |

## Decision dispositions (amend rows)

| DEC | verdict | evidence (`git show c039c32d:.harness/harness/docs/DECISIONS.md`) |
|---|---|---|
| DEC-259 amend (clause "with one exception\n  this rule now names as a finding:", successor D-03) | met | The clause is absent (grep finds 0 hits). Line 8790 reads "moved the `feature.json` domain into `feature_record/` and removed the last re-export". |
| DEC-220 amend ("treats non-null", D-01) | met | Line 7325 names `feature_record.binding.resolve_binding` and line 7333 names `feature_record.binding.effective_recorded_repo`. |
| DEC-150 amend ("300 lines since FEAT-14,", D-01) | met | Line 3513 reads "300 lines since FEAT-14, `feature_record/schema.py`". |

## Findings

- **VF-1 (substance, med, T-03; remedy needs the operator): T-03's signed verify is not reproducible, and its exit status hides that.**
  - **Claim:** "T-03 verify passes at c039c32d" (P5).
  - **Observed:**
    - The python assertion fails for all 29 `test_change` paths, because the `index` lines' abbreviation is now 9 digits where 8 were committed.
    - The verify exits 0 anyway, because the trailing audit command sets the status (G-08 class).
  - **Failure scenario:**
    - Any re-run in a repository past 65,536 objects (this one now, and the post-merge main) reads red.
    - A runner that trusts exit status reads green while the proof never completed.
    - The same masking would hide a real receipt defect.
  - **Not caused by c039c32d.** The records and the generator are unchanged in that respect, and the same red would appear at a03103b0 today. This makes it a pre-existing latent defect that surfaced now, not a regression.
  - **Remedy options (the operator's choice, since the verify is signed):**
    - (a) Amend T-03's verify to pin the abbreviation (`-c core.abbrev=8` or `--full-index`, the generator likewise) and to fail on the python status, for example by joining the two commands with `&&`.
    - (b) Unsigned: regenerate `build-divergences.md` under the current abbreviation. This is fragile, because it re-breaks in a smaller clone, and it does not fix the masking.

Advisory, not a finding: P1 accepts an own 0755 parent, which is consistent with "closed to group/other writes". The other-owner refusal is inferred from the `st_uid` check, not executed.

## Open

- OQ-C3-1 (blocking): VF-1 remedy (a) or (b)? Option (a) requires amending the signed T-03 verify.

## Principles applied

- P-06 / P-19: I re-measured every closed premise at the pin (the parent probe across 9 modes, plus the c2 `_exit_as` used as a free mutant, O-07) instead of trusting the green exit status.
- G-08: I read the verify's failure accounting (python stderr), not only its exit code. This is what exposed VF-1.
- P-05: I graded the SCs on discriminating evidence, and kept the gate failure as a separate block.
