# Goal-check (validate c2) — FEAT-2581 feature_record package

review_sha `a03103b0d85128217401dc84157bfa97827f8a96`, baseline `e12381fde910eb05728004476a10d741d6918010`,
previous pin `62da4501`, implementation pin `c91df7a5`. Run 2026-11-27-02-validate-validator.

**BLUF: PASS.**
- Both perspectives pass. SC-01..SC-10 are all met, and the three amend rows (DEC-259, DEC-220,
  DEC-150) plus D-01, D-02 and D-03 are landed.
- The fix commit regressed nothing. It touches exactly 7 files under `notes/` (5 receipt scripts,
  the generated receipt and the human receipt), and `git diff 62da4501 a03103b0` outside the feature
  directory is empty. So every product file, test, DECISIONS.md and the index are byte-identical to
  the c1 pin.
- Every claim the round makes about what landed held under execution, with one form-level
  inaccuracy in the operator answers file (F-1, low, non-gating).

## What I executed

All of this ran under `env -u HARNESS_AGENT_TYPE` in the feature worktree, at HEAD `b22e5989`. That
commit differs from the pin only in `feature.json` (the review_sha re-pin).

1. **The three `verify:` blocks**, taken verbatim from `git show a03103b0:<feat>/plan.yaml`:
   - T-01: exit 0 in 27 s. It printed `T-01 structure and smoke PASS`, `Ran 130 tests … OK`, `ALL PASS`
     and `0 unresolved reader site(s) across 110 Python file(s)`.
   - T-02: exit 0, `T-02 decisions PASS`, with an empty index diff.
   - T-03: exit 0 in 3 s, `verifying at a03103b0… (review_sha)` and then `T-03 receipts PASS at a03103b0…`.
2. **CR-1.** `code-grade.py --base e12381fd --head a03103b0` exited 0 with `PASSING: 279` and 0
   `RESULT: FAIL`. Every receipt-scripts function is at grade 4 or 5.
3. **CR-2, generator half (mutants).** I used a `git clone --shared` scratch copy and ran
   `feat2581-cleanpin.py c91df7a5 --reuse` from the pin. The only change was that `CHECKOUT` points
   at the existing clean checkouts.
   - **Control:** `overall: PASS`, 631 divergences, 0 unruled. The regenerated receipt differs from
     the committed one only in the `generated` stamp, and `build-divergences.md` is byte-identical.
   - **Mutants on the `audit:stdout` ruling:** I set `by` to null, `date` to a blank string,
     `reason` to the integer 7, deleted the `by` key, and dropped the ruling entirely. Each of the
     five gave `divergence: audit:stdout UNRULED`, `overall: FAIL` and `631 (1 unruled)`.
   - **The c1 script (`62da4501`) as a free mutant (O-07):** it gave `audit:stdout RULED` and
     `overall: PASS` under the null mutant. So the fix is what discriminates.
4. **SEC-1.** I loaded the pin's `private_dir` (from `feat2581-ledger-driver.py`) via AST and ran it
   on four cases:
   - path absent: created with mode 0o700 and empty.
   - path populated with mode-777 contents: recreated with mode 0o700 and empty.
   - symlink in its place: raised `OSError`, and the symlink target was left intact.
   - an unremovable subtree: raised `PermissionError`.

   `feat2581-replay.py#build_scratch` has the identical lexists/rmtree/mkdir(0o700) shape (inspected).
   It replaces the c1 `rmtree(..., ignore_errors=True)` at both sites.
5. **Receipt and disclosure claims.**
   - `git diff 62da4501 a03103b0` on the generated receipt shows exactly the 5 changed
     `script_sha256` lines (bun-preload is unchanged) plus the stamp.
   - `build-divergences.md`, `divergence-rulings.json` and `measurements/` are unchanged.
   - c65ceb81 is an ancestor of the pin. Its ledger-driver, replay and sitecustomize bytes hash to
     the c1 `script_sha256` values (fa8001a0…, ba875501…, 5e06b4a5…), so the disclosure in
     `clean-pin-byte-receipts.md` is accurate.
   - The rulings file has 631 entries holding 1,893 by/date/reason values, all non-blank strings.

## Perspectives

- **operator — pass.** It is carried by SC-03, SC-04, SC-05, SC-06, SC-08 and SC-10.
  - The T-03 verify recomputed every receipt line and every divergence body at a03103b0 from the
    unchanged measurements.
  - The CLI identity, replay identity, suite and case identity and D-02 lines are byte-identical to c1.
  - All 631 divergences are ruled with string metadata.
- **code maintainer — pass.** It is carried by SC-01, SC-02, SC-07 and SC-09.
  - The T-01 and T-02 verifies pass.
  - The audit reports 0 unresolved sites across 110 files.
  - The product tree is byte-identical to the c1 pin.

## SC grading (product subjects unchanged since 62da4501; verifies re-executed at a03103b0)

| SC | verdict | method | evidence |
|---|---|---|---|
| SC-01 | met | inspection | T-01 verify exit 0 at a03103b0, covering the 10-file `feature_record/`, the empty `__init__.py`, the gone set and the shim scan. Files are unchanged since c1 (LAYOUT.md:10, README.md:204). |
| SC-02 | met | inspection | T-03 verify ran `feat2581-grade-assert.py` from the pin bytes: exit 0 at the pin; exit 1 at the baseline, naming exactly the twelve. The receipt's provenance grade lines are unchanged from c1. |
| SC-03 | met | automated | T-03 `ng` assertion: every baseline-passing unit file exits 0 at the pin with identical FAIL lines. Pin-run evidence comes from qa c1 (`review-harness-qa-c1.md` SC-03: 68 files exit 0, runner exit 0) at 62da4501, and the tests and bin are byte-identical at a03103b0 (evidence transferred, not re-executed by me). qa's c2 DIGEST was not in hand. |
| SC-04 | met | automated | Same `ng` recomputation for integration files; only test-typescript-typecheck.py is baseline-failing. qa c1 `review-harness-qa-c1.md` SC-04 covers it, with the same transfer basis. The INV-40 observer line is in the T-01 verify output. |
| SC-05 | met | inspection | Receipt `cli_identity: PASS`, and the verify asserts at least one record for each of the three classes on each side. Measured by the c65ceb81 driver/recorder, which is committed and an ancestor. The pin's refactor of `recorder/sitecustomize.py` is pure extract-method (`_cli_record`, `_exit_as`, `_bytes_mode`, `_text_result`, `_write_gate`), and the counter and read order are preserved (inspected diff). |
| SC-06 | met | inspection | Receipt `replay_identity: PASS`; verify asserts 9 steps × every tracked feature.json except FEAT-2581's. The replay refactor (`build_scratch`, `replay_step`) is extract-method plus the SEC-1 scratch change, by inspection. |
| SC-07 | met | inspection | T-01 and T-03 audit `0 unresolved … across 110 Python file(s)`. The classification JSON is unchanged since c1. |
| SC-08 | met | inspection | The D-02 literals are unchanged since c1. Receipt `d02_item:` and `d02_item_record` are recomputed by the verify, `residual 576`, `gate_captures: 1538 1559`, all ruled. |
| SC-09 | met | inspection | `git show a03103b0:.harness/harness/docs/DECISIONS.md`: :8788-8791 (DEC-259, no exception), :7325 and :7333 (DEC-220 `feature_record.binding.*`), :3513 (DEC-150 `feature_record/schema.py`). T-02 verify exit 0. |
| SC-10 | met | inspection | Receipt `case_identity: PASS`; the 162 `case_set:` lines are byte-identical to c1 and recomputed by the verify's `cw`/`ch` assertions. |

## Decision dispositions (amend rows; keep rows not graded)

DECISIONS.md is byte-identical from 62da4501 to a03103b0, so the c1 grading stands, re-read at the pin.

| DEC | verdict | evidence |
|---|---|---|
| DEC-259 amend (clause `with one exception\n  this rule now names as a finding:`, successor D-03) | met | `git show a03103b0:.harness/harness/docs/DECISIONS.md` lines 8788-8791 read "…FEAT-2581 (#2581) moved the `feature.json` domain into `feature_record/` and removed the last re-export, `plan-merge.py`'s `signed_task_hash`, by loading `plan_merge.approval` by name…". The clause is absent. |
| DEC-220 amend (clause `treats non-null`, successor D-01) | met | Same path, line 7325 (`feature_record.binding.resolve_binding`) and line 7333 (`feature_record.binding.effective_recorded_repo`). The T-02 assertion that `feature_schema` is absent passed. |
| DEC-150 amend (clause `300 lines since FEAT-14,`, successor D-01) | met | Same path, line 3513 (`300 lines since FEAT-14, \`feature_record/schema.py\``). |

D-01, D-02 and D-03 have landed. Their code is unchanged since c1, with the same citations as the c1 note.

## Findings

- **F-1 (form, low, task T-03 `notes/**`; non-gating):**
  - **Claim.** The OQ-V1 rationale in `answers-2026-11-27-validate-escalate.md` says "no committed
    tool writes divergence-rulings.json".
  - **What the tree shows.** `feat2581-cleanpin.py#load_rulings` (and its c1 predecessor at
    :356-359) writes `[]\n` to that file when the file is absent.
  - **Failure scenario.** A reader auditing the accepted-risk basis finds a committed writer, and
    the disposition's evidence reads as false.
  - **Substance.** The seed is an empty list, so no tool can write null or blank by/date/reason.
    The risk argument holds. Only the sentence overclaims. Remedy, the operator's choice: reword to
    "no committed tool writes ruling metadata".

Non-gating notes, not findings:
- **CR-2's verifier half is still present.** T-03's `RD` uses `str(...).strip()`, which accepts
  null. It is dispositioned (OQ-V1).
- **SEC-1 boundary (P-19), executed.** `prepare_scratch` creates the ledger parent
  `/tmp/feat2581-ledger` with `makedirs(mode=0o700, exist_ok=True)`, which accepts a pre-existing
  directory or symlink at that parent unchanged. My probe showed `private_dir` then creating the
  side ledger inside the symlink's target. The record's claim names the four directories it
  covers, so this does not contradict it. It is security-reviewer territory, and SEC-2 is unrouted
  by ruling.

## Open

- None blocking. qa's c2 DIGEST should replace the c1 transfer citation for SC-03 and SC-04 when it
  lands.

## Principles applied

- harness-pm Mode 2 / P-06: I re-measured each prior finding's premise at the pin (code-grade exit,
  null mutant, scratch probe) rather than relying on the green T-03 verify.
- O-07: I used the c1 script as a free mutant to show the CR-2 fix is what discriminates.
- P-19: I ran a probe one boundary beyond SEC-1's stated class (the ledger parent).
