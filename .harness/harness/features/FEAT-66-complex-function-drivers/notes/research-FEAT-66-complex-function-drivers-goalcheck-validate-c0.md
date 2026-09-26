# FEAT-66 goal-check — validate cycle 0

## Overall verdict

**FAIL.** The code-maintainer outcome is supported, but the operator outcome is only partial: the clean-pin receipt records different raw stdout hashes for `test-validate-digest.py`, then declares equality only after replacing each checkout root, while the divergence ledger says no output diverged. SC-02 explicitly requires raw stdout-byte identity or an exact ruled ledger entry and says an unledgered difference fails. QA independently confirms that failure, reports that SC-02 has no mandatory fail-first discharge, and reports a stale grade-1 exemption failing the configured unit matrix; the integration matrix and signed T-01 command pass.

## Pin and evidence basis

- Graded immutable review SHA: `c4ea33bc0ff93b11a846f24d70923ce108aa1358`; implementation pin: `e2b580a68cbc5116839c80e30c220f5b67cf6e65`; signed baseline: `cb6f80505721292c0c799cf03b0af6b180ba2970` (the receipts use signed-plan commit `35c39f02bb383bba167e27d9a9b97c97798ef076`, whose production bytes they state are identical to that baseline).
- The complete signed T-01 set was inspected at the review SHA: the three production files; eight `test-check-domain*.py` owning suites; `test-config-shape-matrix.py`, `test-plan-merge.py`, `test-validate-digest.py`, and `test-driver-grades.py`; and the red-first, clean-pin, and divergence receipts. `BRIEF.md`, `plan.yaml`, the build digest, and the build amendment were also inspected.
- The pinned production diff contains only `check-domain.py`, `validate-digest.py`, and `plan-merge.py`. The implementation pin is an ancestor of the review SHA, and commit `25259fe0` adds all three evidence notes after that pin.
- QA's canonical `notes/review-harness-qa-c0.md` records: configured unit **FAIL** on stale `validate: 1` allowlisting, integration **PASS**, signed T-01 **PASS**, SC-01 direct proof present, and SC-02 **FAIL** for both the raw hash mismatch and absent fail-first evidence.

## Perspective grades

- **operator — partial** — carrying SC-02 (**not_met**) and SC-04 (**met**): the exact-pin evidence artifacts exist in the right commit order, but the raw `test-validate-digest.py` stdout hashes are `05d44942d82f` at baseline and `d9b52125dd3b` at the implementation pin; root normalization is not the signed byte-identity rule and no divergence entry rules those exact bytes.
- **code maintainer — pass** — carrying SC-01 (**met**) and SC-03 (**met**): the red-first lock records all three drivers at grade 1 before the refactor, the clean-pin grade receipt records all drivers and extracted functions at grade 4 or 5, and the pinned diff shows ordered drivers/helpers with only the three named production files changed and the original explanatory comment bytes retained.

## Success-criterion dispositions

| Criterion | Verdict | Evidence and reason |
|---|---|---|
| SC-01 | **met** | `tests/unit/test-driver-grades.py`; `notes/red-first-receipts.md` “The grade assertion, red at the baseline”; `notes/clean-pin-byte-receipts.md` “Grade lock” and “Extracted functions at bar 4”; `notes/review-harness-qa-c0.md:13-17`. QA reran the signed T-01 command successfully. Its configured-unit failure is a stale exemption expecting grade 1 while `validate` now grades 4, so it is an owned ship gate (F-QA-01) but does not falsify this criterion's grade outcome. |
| SC-02 | **not_met** | `notes/clean-pin-byte-receipts.md` “Owning suites at the pin vs baseline” records the raw `test-validate-digest.py` stdout hash mismatch and applies checkout-root normalization; `notes/build-divergences.md` “Output divergences” says **None**; `notes/review-harness-qa-c0.md:19,35-43,55-63` independently confirms the unledgered difference and the missing mandatory fail-first discharge. Either defect is sufficient for failure. |
| SC-03 | **met** | Pinned diff `cb6f8050..c4ea33bc` changes only the three named production files under `.claude/skills/harness/bin`; `check-domain.py:SHAPE_RULES/shape_problems`, `validate-digest.py:validate/_common_errors/_persona_errors`, and `plan-merge.py:apply_merge/_merge_keys/_fold_merge_rows` preserve ordered dispatch. `notes/red-first-receipts.md` records the comment-line multiset proof; ledger D-08 records original bytes retained with only marked additions. |
| SC-04 | **met** | `notes/red-first-receipts.md`, `notes/clean-pin-byte-receipts.md`, and `notes/build-divergences.md`; commit `25259fe0` follows implementation pin `e2b580a6`. The notes name pins, commands, clean detached checkout/status, exits, and stdout/stderr hashes and expressly disclaim existence inside the earlier pin. |

## D-06 compatibility

D-06 is **compatible with the signed Done-when perspectives and SC-01/SC-03 without narrowing them**. `apply_merge` remains a grade-4 small driver; `_merge_keys` walks `out_order`; `_fold_merge_rows` concatenates the six phase-local lists in that order; and the public result is unchanged. Neither perspective nor SC-01/SC-03 assigns list-extension ownership to the driver or requires one `MergeResult` construction per historical return path.

D-06 nevertheless differs literally from plan decision D-02 and T-01's implementation instruction that only `apply_merge` extend the lists. That task-level design divergence remains visible here and in the ledger; it is not silently promoted into a narrower success criterion. Under the PM goal-check contract, which grades the signed perspectives through their SCs, it does not make either perspective unmet.

## Gate finding

### PM-66-01 — raw stdout difference is normalized away, not ruled

- **Reader / kind / severity / task:** operator / substance / high / T-01
- **SC:** SC-02; operator perspective
- **Concrete failure scenario:** an implementation-pin suite can emit different raw stdout and still be reported “11/11 identical” whenever the receipt author normalizes the differing substring, even though the signed contract makes raw bytes the gate and requires every exception to carry exact old/new bytes, affected case, and operator ruling.
- **Must-fix:** reproduce baseline and implementation-pin runs under one stable absolute checkout path so the raw stdout bytes compare equal, or add a divergence entry with the exact old and new stdout bytes, the affected `test-validate-digest.py` cases, and an explicit operator ruling. Then update the clean-pin receipt so its aggregate claim is about raw or explicitly ruled bytes, not normalized bytes.

### PM-66-02 — SC-02 has no fail-first discharge

- **Reader / kind / severity / task:** product/plan owner / form / medium / T-01 (scope change)
- **SC:** SC-02; operator perspective
- **Concrete failure scenario:** a PASS would claim an automated criterion met the Harness fail-first gate even though its own receipt says byte identity “has no red form”; the evidence proves a baseline comparison, not a pre-fix failure.
- **Must-fix:** obtain approval to amend SC-02's verification contract so a baseline byte comparison is the explicit evidence appropriate to this invariant, or retain a credible pre-fix failing proof. Do not add an artificial mutation that proves a different contract.

## Dismissed candidates

- **D-06 as a perspective failure:** dismissed for the criterion-level reason above; it is a visible D-02 implementation divergence, but the signed Done-when outcome is still satisfied without narrowing any SC.
- **D-08 comment additions:** dismissed because the original load-bearing bytes remain present and the ledger identifies only appended FEAT-66 sentences; SC-03 forbids rewriting or dropping, neither of which occurred.
- **Driver-only permanent unit lock:** dismissed because the task's pinned direct grade command grades every extracted function, and the clean-pin receipt records that full set at grades 4 or 5; the permanent ratchet remains scoped to the three named legacy drivers as required.
- **D-04 missing shadows suite:** dismissed because the build amendment removes a file absent from both baseline and branch, and the dispatch's complete signed review set and verbatim verify command exclude it.
- **Configured unit-matrix failure as an SC-01 failure:** not converted into `not_met` because the failing assertion expects the obsolete grade 1 and reports the criterion's desired actual grade 4; QA F-QA-01 remains an owned T-01 ship blocker that must be fixed even though the SC-01 outcome itself is met.

## Open questions

- **Q1 (blocking):** Should SC-02 explicitly accept baseline byte comparison as its fail-first-equivalent evidence, instead of requiring a pre-fix failure that this invariant has no natural form for?

```yaml
VERDICT: FAIL
DIGEST:
  headline: "The maintainer perspective passes, but the operator perspective is partial: SC-02 has an unledgered raw stdout mismatch and no fail-first discharge."
  feasibility: clear
  surface: M
  flags: [verification, byte-evidence, fail-first, test-matrix, spec-compliance]
  recommend: halt
  tasks: 1
  decisions: 2
  needs_approval: true
  risk: high
  sc_status:
    - { id: SC-01, verdict: met, method: automated, evidence: "review-harness-qa-c0.md:13-17; test-driver-grades.py; red-first-receipts.md#The grade assertion; clean-pin-byte-receipts.md#Grade lock/#Extracted functions" }
    - { id: SC-02, verdict: not_met, method: automated, evidence: "review-harness-qa-c0.md:19,35-43,55-63; clean-pin-byte-receipts.md raw stdout 05d44942d82f != d9b52125dd3b; build-divergences.md says None" }
    - { id: SC-03, verdict: met, method: inspection, evidence: "pinned cb6f8050..c4ea33bc production diff; red-first-receipts.md#Per SC; build-divergences.md D-08" }
    - { id: SC-04, verdict: met, method: inspection, evidence: "red-first-receipts.md; clean-pin-byte-receipts.md; build-divergences.md; post-pin receipt commit 25259fe0" }
  open_questions:
    - { id: Q1, question: "Should SC-02 explicitly accept baseline byte comparison as its fail-first-equivalent evidence, instead of requiring a pre-fix failure that the invariant has no natural form for?", blocking: true }
  files_touched: [.harness/harness/features/FEAT-66-complex-function-drivers/notes/research-FEAT-66-complex-function-drivers-goalcheck-validate-c0.md]
  expertise_update: []
artifact: /Users/molchairuangutai/GitHub/harness/.claude/worktrees/harness/FEAT-66-complex-function-drivers/.harness/harness/features/FEAT-66-complex-function-drivers/notes/research-FEAT-66-complex-function-drivers-goalcheck-validate-c0.md
```
