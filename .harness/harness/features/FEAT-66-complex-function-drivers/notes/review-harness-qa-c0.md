# QA matrix gate — FEAT-66, review pin `c4ea33bc0ff93b11a846f24d70923ce108aa1358`

## Verdict

**FAIL.** The configured unit matrix has one real assertion failure. SC-02's raw stdout evidence also differs without a divergence-ledger entry, and it has no credible fail-first evidence. The configured integration matrix and the signed T-01 direct verification are green.

## Phase 1: matrix and coverage

`plan.yaml:38` labels T-01 `refactor`, while the configured test matrix has no `refactor` row. I therefore used the BRIEF's explicit active unit and integration evidence kinds as the floor: unit covers SC-01; integration covers SC-02. SC-03 and SC-04 require inspection, not invented automated checks.

| kind | command | result |
|---|---|---|
| unit | `env -u HARNESS_AGENT_TYPE .agents/skills/harness/bin/run-unit-tests.py --kind unit` | **FAIL** — 43 files discovered; `tests/unit/test-code-grade.py` failed because `validate-digest.py:validate` is allowlisted at stale grade `1`, but currently grades `4`. |
| integration | `env -u HARNESS_AGENT_TYPE .agents/skills/harness/bin/run-unit-tests.py --kind integration` | **PASS** — 70 files discovered; 108.13 s wall time. |
| signed T-01 | the exact 11-suite-and-grade command in `plan.yaml:72-84` | **PASS** — all named suites passed; final `FEAT-66 grades [...]` command exited 0. |

SC-01's direct behavioral proof is `tests/unit/test-driver-grades.py:41-51`. It checks all three named drivers. The committed receipt records the natural pre-refactor failure at `35c39f02`: three grade-1 drivers, exit 1 (`notes/red-first-receipts.md:30-48`). The current signed direct grade assertion passed at this review pin.

SC-02's 11 owning suites are covered by the signed command, but its receipt records different **raw** stdout SHA-1 values for `test-validate-digest.py` (`05d44942d82f` vs `d9b52125dd3b`) and calls them identical only after checkout-root normalization (`notes/clean-pin-byte-receipts.md:11-31`). The divergence ledger instead says every suite has the same stdout bytes and records no output divergence (`notes/build-divergences.md:9-12`). This violates SC-02's byte-equality-or-ledger condition. Separately, the receipt explicitly says the criterion has no red form (`notes/red-first-receipts.md:54-61`), so it does not meet this validation gate's mandatory fail-first standard.

I also inspected the three production driver locations, D-01/D-02, the clean-pin receipt, divergence ledger, and receipt amendment as required. SC-03 and SC-04 remain inspection claims; I did not add source-text or plumbing checks that would turn them into different automated contracts.

## Findings

### F-QA-01 — stale self-grade exemption blocks the unit gate

- **kind:** substance
- **severity:** medium
- **reader:** harness-qa
- **task:** T-01 (owned)
- **evidence:** `tests/unit/test-code-grade.py:216-261` retains `("validate-digest.py", "validate"): 1`; the configured unit run reports `expected 1, got 4`.
- **failure scenario:** Every configured unit-matrix execution fails after this refactor, even though the function now meets the production bar.
- **must-fix:** Update or remove the now-stale exemption in the owning test and rerun the complete unit and integration matrix at the immutable review pin.

### F-QA-02 — SC-02 cannot discharge the mandatory fail-first gate

- **kind:** form
- **severity:** medium
- **reader:** harness-qa
- **task:** T-01 (scope change; product/plan owner)
- **evidence:** SC-02 is `verify: automated` (`BRIEF.md:18-20`), but the retained red-first table says `— (a byte-identity criterion has no red form)` (`notes/red-first-receipts.md:56-60`).
- **failure scenario:** A PASS would claim an automated SC has demonstrated a pre-fix failure when the evidence itself says no such failure exists.
- **must-fix:** Either amend the signed acceptance/verification policy to permit baseline byte comparison as SC-02's appropriate evidence, or provide a credible pre-fix failing test. This is not a QA-owned test change.

### F-QA-03 — the plan’s change type cannot resolve mechanically in the test matrix

- **kind:** form
- **severity:** low
- **reader:** harness-qa
- **task:** T-01 (scope change; plan/config owner)
- **evidence:** `plan.yaml:38` says `change_type: refactor`; `.harness/harness.json` defines no matching matrix row.
- **failure scenario:** A future validator cannot derive the required kinds from T-01 alone and can select an inconsistent test floor.
- **must-fix:** Amend the signed plan to a configured type or add an approved `refactor` matrix row before relying on automatic matrix derivation.

### F-QA-04 — SC-02 receipt records an unledgered raw stdout divergence

- **kind:** substance
- **severity:** high
- **reader:** harness-qa
- **task:** T-01 (owned)
- **evidence:** `notes/clean-pin-byte-receipts.md:13-15,28` declares that raw bytes differ for `tests/integration/test-validate-digest.py` (`05d44942d82f / d9b52125dd3b`), while `notes/build-divergences.md:9-12` says no output divergence exists and all raw stdout bytes are equal.
- **failure scenario:** The operator's mandated raw byte-identity evidence is false for one owning suite, yet the ledger offers no exact old/new bytes, affected case, or ruling as SC-02 requires.
- **must-fix:** Either make the suite's observable stdout byte-identical across the two checkouts, or ledger this real divergence with its exact old/new bytes, affected case, and explicit operator ruling; then recapture the clean-checkout comparison.

## Dismissed candidates

- The removed `test-validate-digest-shadows.py` is not a missing test: its absence and T-01 amendment are explicitly recorded in `notes/red-first-receipts.md:26-28` and `notes/amendments-build-main-direct.md`.
- I did not demand an artificial SC-02 mutation solely to manufacture red evidence. That would prove a different contract from byte identity; the criterion/policy decision belongs to the plan owner.
- I did not convert SC-03 or SC-04 into source-text tests. Their BRIEF verification mode is inspection, and the required receipts already describe their scope and chronology.

## Reproducibility

The existing test-pool runners are the deterministic verification lever for both matrix kinds; no new harness or test was added during this read-only audit.
