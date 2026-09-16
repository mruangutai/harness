# Ship review — BUG-1563 INV-35 multiline quoted scalar

## Decision

**Recommend ship.** The immutable review target `9fd79689e24353ac81689bb5227b8aa752e536ea` passes all five independent validation readers. The original matrix blocker V-01 is resolved rather than waived, the final simplify pass has no actionable finding, and every signed success criterion is met.

## Definition of done

| Perspective | Signed outcome | Verdict | Criteria and evidence |
|---|---|---|---|
| Operator | Valid multiline quoted YAML scalars may contain issue references without an INV-35 false positive, while genuinely unquoted issue references remain findings. | Met | SC-01. `runs/validate-validator-final/digest.md`: focused integration and unit commands both pass the multiline single-quote, multiline double-quote, and unquoted `#217` control; fail-first reproduces both old false positives. |
| Code maintainer | Focused integration and unit-kind behavioral coverage distinguishes multiline quoted content from genuinely unquoted `#<digit>` values. | Met | SC-02 and SC-03. `runs/validate-validator-final/digest.md`: configured unit kind passes 39 scripts, configured integration kind passes 72 scripts, and both include the focused BUG-1563 tests. |

## What ships

- INV-35 now maintains quote state across physical lines for single- and double-quoted YAML scalars.
- Unquoted `notes: close out #217` still produces the expected finding.
- The integration regression covers both quoted cases and the unquoted control.
- A focused unit-kind test invokes the real checker and closes the hard matrix requirement.
- The final cleanup skips two unused continuation-line string scans without changing behavior.

## Validation

- Code review: PASS after spec compliance, with no substantive quality finding.
- Security review: PASS; no exploitable input-validation regression.
- QA: PASS; V-01 resolved, unit and integration matrix kinds green, canonical checker green, and fail-first evidence accepted.
- UI review: PASS by legitimate self-scope; no rendered surface changed.
- Goalcheck: PASS for both signed perspectives and SC-01 through SC-03.
- UAT: not required; the BRIEF contains only automated verification and the change has no user-facing UI flow.

## Run history

- `runs/plan-product/digest.md` — initial bounded patch plan PASS.
- `runs/simplify-eng/digest.md` — initial two-file simplify PASS.
- `runs/validate-validator/digest.md` — FAIL solely on missing unit-kind matrix coverage V-01.
- `runs/plan-upgrade-product/digest.md` — minimum T-02 plan amendment PASS and signed by the operator.
- `runs/simplify-eng-final/digest.md` — FAIL on EFF-01, an in-scope redundant-scan cleanup.
- `runs/simplify-eng-confirm/digest.md` — EFF-01 resolved; all four simplify angles PASS.
- `runs/validate-validator-final/digest.md` — final pinned validation PASS with no findings.

No report round was spawned. This briefing was assembled directly from every run digest listed above and the feature ledger.

## Escalations and spend

- Resolved escalation: V-01 required scope beyond the original two-file patch. The operator authorized the minimum plan upgrade, preserved DEC-174 main-session-direct routing, and declined any matrix waiver.
- Resolved simplify finding: EFF-01 was applied main-session-direct and independently confirmed.
- Open questions: none.
- Spend: 7 recorded runs, 92 wall-clock minutes, 70 rework minutes, 3 of 10 feature cycles used, and 10 recorded orchestrator judgements. The run count is proportionate to one scope upgrade, one cleanup regate, and a final independent validation.

## Proposed backlog

| ID | Nature | Residual |
|---|---|---|
| B-1 | chore | Reassess whether the hard bugfix matrix should require duplicated unit- and integration-kind behavior proof for executable shell checkers. The duplication is intentional and non-gating here; changing it requires a fleet policy decision, not a BUG-1563 code change. |

If B-1 is not struck before ship acceptance, it becomes a backlog issue. Everything else not listed here is intentionally closed with this feature.
