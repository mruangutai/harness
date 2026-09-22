# Goal-check — FEAT-61 control-plane consolidation — validate c1

## BLUF

**FAIL.** Reviewed SHA `57ef1c5739f55dd67d9daffd5da69d7d7b980ea7` over immutable range `066638e8acf68b47e74637006a01c8823cff939c..57ef1c5739f55dd67d9daffd5da69d7d7b980ea7`. All five signed task verify clauses passed at that SHA, but QA found no durable pre-fix failing receipt for SC-01 through SC-06; SC-07's passing controlled mutation exercises only an exact current bucket and misses partial or already-drifted lifecycle copies. SC-08 passes inspection. I did not rerun tests; automated evidence below is collected from `notes/review-harness-qa-c1.md`.

## Perspective headlines

- **operator — fail — SC-01, SC-03, and SC-04 are not met:** current suites pass and the baseline-corpus statement exists, but the required fail-first proof is absent, and one malformed-schema route changes gate error bytes outside SC-01's signed exception list.
- **code maintainer — fail — SC-02, SC-05, SC-06, and SC-07 are not met:** the shared seams and current regressions exist, but SC-02/05/06 lack their required fail-first evidence and SC-07's station lock lets a partial copied lifecycle predicate return undetected.
- **reader — partial — SC-08 is met, while SC-01's missing fail-first receipts leave the perspective's preserved-versus-intentional behavior distinction unproven:** the bootstrap, vocabulary, and direct-execution records themselves are present and traceable.

## Success-criterion outcomes

| SC | Verdict | Evidence at the reviewed SHA |
|---|---|---|
| SC-01 | **not_met** | QA ran all integration verify chains successfully (`notes/review-harness-qa-c1.md:19-27`), and the build ledger claims 21 plan-merge, 29 gate, and 20 lifecycle byte receipts (`notes/build-divergences.md:8-11`). The criterion nevertheless requires fail-first comparison evidence, and QA found no captured red command/output or pre-fix SHA (`notes/review-harness-qa-c1.md:31-34,42-44`). Separately, the ledger admits that malformed `items: []` changed from baseline `AttributeError` bytes to `TypeError` bytes (`notes/build-divergences.md:32-38`), although SC-01's signed exceptions name only strict-station, rejected-review, and missing-policy behavior (`BRIEF.md:17-18`). |
| SC-02 | **not_met** | The current unit chain passed (`notes/review-harness-qa-c1.md:21-24`), and assertions cover the ordered string rows, all four derived tuples, and strict empty/unknown handling (`tests/unit/test-factory-config.py:541-601`; implementation at `.claude/skills/harness/bin/factory_config.py:59-99`). QA found no durable run showing those tests red before implementation (`notes/review-harness-qa-c1.md:34`). Because fail-first is an explicit conjunct, current green coverage alone does not meet the SC. |
| SC-03 | **not_met** | The current integration chain passed; `rejected`, `abandoned`/`rejected`, and empty/unknown behavior is asserted in `tests/integration/test-plan-merge.py:3342-3389`. The one-time baseline-corpus record says every baseline status was declared or omitted/defaulted to `ready` (`notes/research-FEAT-61-control-plane-consolidation.md:14-16`). QA found no durable pre-fix failing run for the behavior cases (`notes/review-harness-qa-c1.md:35`), so the fail-first requirement is not established. |
| SC-04 | **not_met** | The signed unit and public-validator command passed (`notes/review-harness-qa-c1.md:26`). Current tests prove removed keys are ignored and missing/invalid `review` is rejected (`tests/unit/test-gate-policy.py:63-82`; QA maps the validator evidence at `tests/integration/test-validate-digest.py:3749-3764`), while production resolves only `review` (`.claude/skills/harness/bin/gate_policy.py:5-12,52-70`). No durable pre-fix failing receipt exists (`notes/review-harness-qa-c1.md:36`). |
| SC-05 | **not_met** | The T-03 integration chain passed (`notes/review-harness-qa-c1.md:25`). Both adapters call `harness_boundary.feature_artifact_checkout_mismatch`, whose single decision point is `.claude/skills/harness/bin/harness_boundary.py:247-280`; exact route-specific fixtures cover mismatch, ambiguous worktrees, and absorbed failures (`tests/integration/test-check-domain-worktree.py:712-814`; `tests/integration/test-bash-write-guard.py:995-1108`). Those test comments claim earlier byte receipts, but no durable receipt/output is present (`notes/review-harness-qa-c1.md:37`). |
| SC-06 | **not_met** | Current unit/integration chains passed and the shared implementations exist (`.claude/skills/harness/bin/artifact_accessors.py:38-64`; `.claude/skills/harness/bin/harness_boundary.py:283-322`). QA found no durable fail-first receipt for strict JSON, schema navigation, or module loading (`notes/review-harness-qa-c1.md:38`). In addition, the ledger records that a non-mapping step-schema `items` value now reaches `TypeError` instead of the baseline `AttributeError` (`notes/build-divergences.md:32-38`); the retained tests cover mapping-shaped `KeyError`s but not baseline byte identity for that list shape (`tests/integration/test-check-domain.py:166-189`; `tests/integration/test-check-state-feat59.py:673-684`). |
| SC-07 | **not_met** | QA's signed T-05 command passed, including the clean-tree assertion and one exact active-bucket mutant plus one second-loader mutant (`tests/integration/test-check-plan-routes.py:2450-2475`; `notes/review-harness-qa-c1.md:39`). But `_respelled_bucket` reports only a collection equal to the complete current active/finished bucket, or a concatenation (`.claude/skills/harness/bin/check-plan-routes.py:1679-1685`). A feature predicate such as `station in ("plan", "ready", "building")` is a copied, already-drifted lifecycle literal outside `factory_config.py` and produces no finding, contrary to SC-07. |
| SC-08 | **met** | At the reviewed SHA, each bootstrap comment names the other four and DEC-234 (`.claude/skills/harness/bin/branch-create-gate.py:46-49`; `gh-close-gate.py:39-42`; `merge-gate.py:39-42`; `plan-sign-gate.py:65-68`; `run-unit-tests.py:41-44`). DEC-234 records why no shared import seam exists before the trusted bin path is established (`.harness/harness/docs/DECISIONS.md:7647-7668`), and the glossary defines `not_started`, `active`, and `finished`, including the historical `_work_started` distinction (`.harness/glossary.md:31-45`). The approved direct-execution boundary remains durable in `plan.yaml:145-147`. |

## Findings

### F-01 — High — fail-first evidence is absent for six automated criteria

- **Severity:** high
- **Reader:** harness-qa / goalcheck
- **Kind:** substance
- **Owning plan tasks:** T-01, T-02, T-03, T-04, T-05
- **Concrete unmet-goal scenario:** A newly written test can mirror the shipped implementation and pass forever without ever having discriminated the pre-change defect; a later reader therefore cannot distinguish preserved behavior from a post-hoc assertion even though SC-01 through SC-06 explicitly require fail-first proof.
- **Cite:** `notes/review-harness-qa-c1.md:31-44`; the divergence ledger labels tests red-first without command output or a pre-fix SHA at `notes/build-divergences.md:15-47`.
- **Disposition:** blocking. Current green test output does not substitute for the missing red evidence.

### F-02 — High — the station lock misses partial or drifted lifecycle literals

- **Severity:** high
- **Reader:** harness-code-reviewer / goalcheck
- **Kind:** substance
- **Owning plan task:** T-05
- **Concrete unmet-goal scenario:** A maintainer reintroduces `station in ("plan", "ready", "building")` in a feature-lifecycle predicate. Because the literal is not exactly equal to `ACTIVE_STATIONS`, the AST audit reports clean while `review` is silently misclassified, so the copied form has returned despite SC-07.
- **Cite:** `.claude/skills/harness/bin/check-plan-routes.py:1679-1685`; the only station mutant uses the exact complete active bucket at `tests/integration/test-check-plan-routes.py:2435-2465`; independent review records the same mismatch at `notes/review-harness-code-reviewer-c1.md`.
- **Disposition:** blocking. The controlled mutation proves only the sampled exact-copy case, not the criterion's feature-station-literal boundary.

### F-03 — High — malformed list-shaped run schemas change gate bytes outside SC-01's signed exceptions

- **Severity:** high
- **Reader:** harness-pm goalcheck
- **Kind:** substance
- **Owning plan tasks:** T-01 and T-03
- **Concrete unmet-goal scenario:** If `run-state-schema.json` has `items: []`, operators now receive `TypeError: list indices must be integers...` from the shared accessor instead of the baseline jsonschema `AttributeError: 'list' object has no attribute 'get'`. The gate still blocks, but its stderr bytes changed even though this shape is not among SC-01's three signed divergences.
- **Cite:** admitted at `notes/build-divergences.md:32-38`; the early navigation that changes the failure site is `.claude/skills/harness/bin/artifact_accessors.py:50-64`; existing integration checks cover only mapping-shaped `KeyError`s at `tests/integration/test-check-domain.py:166-189` and `tests/integration/test-check-state-feat59.py:673-684`.
- **Disposition:** blocking. The build-time main-session acceptance recorded in the ledger is not one of BRIEF SC-01's signed exceptions.

## Preserved nonblocking observations

- **Low — harness-code-reviewer — form — T-02:** `tests/integration/test-gh-sync-record.py:356-377` adds the strict unknown-station regression, but T-02 neither owns that file nor runs it in its signed verify clause (`plan.yaml:181-203`). Scenario: a task-scoped replay can omit this regression while still reporting T-02 green. This does not add a separate SC failure because SC-03's named empty/unknown behavior is exercised by `test-plan-merge.py`, but the ownership drift should be corrected with any regate.
- **None — harness-security-reviewer — substance:** the pinned security review found no exploitable regression across JSON decoding, checkout binding, dynamic loading, lifecycle refusal, or gate-policy parsing (`notes/review-harness-security-reviewer-c1.md`).
- **N/A — harness-ui-reviewer — form:** UI review scoped out because the 62-file range has no user-facing UI surface (`notes/review-harness-ui-reviewer-c1.md`).
- No unowned scope change was identified; every blocking remedy belongs to an existing signed task surface.
