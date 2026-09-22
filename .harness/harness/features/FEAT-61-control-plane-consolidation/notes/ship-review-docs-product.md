# Ship review — FEAT-61 control-plane consolidation

**Recommendation: ship.** The final pinned regate at `f798e2e600ed08aeb49d61a3a229a626750a9ccb` passed with `matrix_ok: true`, no findings, and SC-01 through SC-08 met. The post-validation documentation audit corrected one stale lifecycle section in `.harness/harness/docs/SPEC.md` and found no remaining documentation gap. There are no open questions and no proposed backlog items.

## Definition of done — graded by perspective

| Perspective | Signed definition of done | Verdict | Discharged by | Evidence |
|---|---|---|---|---|
| operator | I can rely on one authoritative definition for each gate-critical rule in this wave, with dead policy removed and gate behavior unchanged except where the signed rulings deliberately change it. A one-time planning receipt establishes that the baseline live plan corpus is clean, and strict predicates expose invalid station data thereafter. | **met** | SC-01, SC-03, SC-04 | `notes/research-FEAT-61-control-plane-consolidation-goalcheck-validate-c3.md` §Perspective grades and §Success-criterion outcomes; `notes/review-harness-qa-c3.md` §Signed verify chains |
| code maintainer | I can change station lifecycle, checkout placement, strict JSON parsing, run-step schema navigation, or repo-local module loading in one place, and two cheap checks stop the copied forms from returning. The one accepted bootstrap duplication is explicit and justified where I will encounter it. | **met** | SC-02, SC-05, SC-06, SC-07 | `notes/research-FEAT-61-control-plane-consolidation-goalcheck-validate-c3.md` §Perspective grades and §Success-criterion outcomes; `notes/review-harness-code-reviewer-c3.md` |
| reader | I can distinguish preserved behavior from intentional divergence through fail-first evidence, and I can trace the accepted duplication, vocabulary, and direct-execution boundary to durable records. | **met** | SC-08 | `notes/research-FEAT-61-control-plane-consolidation-goalcheck-validate-c3.md` §Perspective grades and SC-08; `notes/receipt-harness-documentor-docs-product.md` |

## Run record

No report round was spawned. This briefing was assembled from every digest named by `feature.json`:

| Run | Result | Conclusion | Digest |
|---|---|---|---|
| `plan-product` | PASS | Five dependency-ordered direct-execution tasks and eight criteria were signed after all six panel findings were applied. | `runs/plan-product/digest.md` |
| `simplify-eng` | PASS | The four-angle pass found one low pass-through wrapper; it was removed before validation and does not survive in the shipped tree. | `runs/simplify-eng/digest.md` |
| `validate-validator` | FAIL | Initial validation exposed missing fail-first receipts, a partial-bucket detector gap, and an unruled malformed-schema byte change. | `runs/validate-validator/digest.md` |
| `amend-cr02-eng` | PASS | T-02's file and verify inventories were ledgered to include the D-03 `test-gh-sync-record.py` regression. | `runs/amend-cr02-eng/digest.md` |
| `validate-c2-validator` | FAIL | Behavior and all SCs passed, but three tasks carried unsupported `change_type: code`; the operator ruled this a signed-plan classification correction. | `runs/validate-c2-validator/digest.md` |
| `validate-c3-validator` | PASS | At the final pin, unit and integration matrices, all five signed chains, all readers, every SC, and all three perspectives passed with no finding. | `runs/validate-c3-validator/digest.md` |
| `docs-product` | PASS | The documentation audit corrected stale six-station/terminal wording in `SPEC.md`; DEC-234, the index, comments, glossary, guides, and READMEs are coherent. | `runs/docs-product/digest.md` |

## Resolved findings and escalations

- `VAL-01` — durable fail-first receipts now cover every automated SC (`runs/validate-validator/digest.md`; `notes/fail-first-receipts.md`).
- `VAL-02` — the station lock now detects incomplete and drifted lifecycle buckets, with controlled mutants (`runs/validate-validator/digest.md`; `notes/review-harness-qa-c3.md`).
- `VAL-03` — natural malformed run-schema errors were restored at existing catch boundaries (`runs/validate-validator/digest.md`; final c3 goal-check SC-06).
- `CR-02` — T-02's `files` and `verify` records now include `tests/integration/test-gh-sync-record.py` (`runs/amend-cr02-eng/digest.md`).
- `QA-C2-01` — the operator corrected T-01/T-02/T-03 to `cross_module`; no duplicate `code` mapping was introduced (`notes/answers-2026-09-20-validate-c2.md`; `runs/validate-c3-validator/digest.md`).
- The simplify wrapper finding is closed: `task_finished` no longer exists in `.claude/skills/harness/bin/gh-sync.py`.

## Spend and audit ledger

- Runs: **7 / 20 informational budget**; the budget was not exceeded, and each run records a distinct planning, review, correction, or documentation boundary.
- Cycles: **2 / 10 hard budget**, reconciled to the two recorded FAIL runs.
- Measured spend after documentation: **103 wall-clock minutes**, **57 rework minutes**, **723,003 tokens** (`feature-record.py spend`). The signed 90-minute rework window was not exceeded.
- Judgements: **11**.
- UAT: **not required**; the signed criteria are automated or inspection-only.

## Amendments to signed tasks

| At | Amendment | Reason | Overruled |
|---|---|---|---|
| `2026-09-20T23:31:15.564850+00:00` | `T-02.files` | The D-03 gh-sync regression belongs in T-02's file scope. | no |
| `2026-09-20T23:31:15.565005+00:00` | `T-02.verify` | T-02 verification must execute the D-03 unknown-station regression. | no |

Overrule rate: **0/2**.

## Open questions

None.

## Proposed backlog

| ID | Nature | Residual finding |
|---|---|---|

No residual finding survived collation; there is nothing to create on ship acceptance.
