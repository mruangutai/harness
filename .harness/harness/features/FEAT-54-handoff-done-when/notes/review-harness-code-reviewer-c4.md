# Code review — FEAT-54 handoff Done when — c4

**FAIL.** The external c3 blocker is repaired: the exact repository-root SC-04 command exits 0 with zero `Done when` findings and zero violations. Stage 1 nevertheless fails because SC-15/T-06's permanent state-gate proof does not bind the behavior it claims to protect. Both “absent targets do not rot” cases filter output for `Done when`; a regression from `resolve=False` to `resolve=True` emits an unresolved-authority line without that phrase, so those cases remain green while INV-17 begins re-resolving persisted pointers. This is a high, policy-gating verification defect in the feature's core stability contract. Stage 2 was therefore not entered.

Reviewed immutable range: `0ec44965a961d19177de871c3bb1f02b701e646b..f05e1e6cd74c7d91580dd6ef565a00432faac1ad`. The checkout was exactly at `f05e1e6cd74c7d91580dd6ef565a00432faac1ad`; the sole dirty path was feature-local `feature.json`, outside the 16-path review set. No `[harness:human]` commit occurs in the range. The exact 16 paths are byte-identical to c3 pin `39602414e1cfe792655b7e68bce367e92790c32a`, but every path was independently re-read at the current pin rather than inheriting c3's conclusions.

## Exact inspected scope — 16 paths

1. `.claude/skills/harness/bin/handoff_done_when.py`
2. `tests/unit/test-handoff-done-when.py`
3. `tests/unit/test-probe-handoff-comprehension.py`
4. `tests/integration/test-check-domain.py`
5. `.claude/skills/harness/bin/check-domain.sh`
6. `.harness/harness.json`
7. `tests/integration/test-check-state.py`
8. `.claude/skills/harness/bin/check-state.sh`
9. `.claude/skills/harness/templates/HANDOFF.md`
10. `.claude/skills/harness/SKILL.md`
11. `tests/manual/probe-handoff-comprehension.py`
12. `.harness/harness/docs/DECISIONS.md`
13. `.harness/harness/docs/DECISIONS-INDEX.md`
14. `.harness/harness/features/FEAT-54-handoff-done-when/notes/handoff-plan.md`
15. `.harness/harness/features/FEAT-54-handoff-done-when/notes/handoff-build.md`
16. `tests/integration/test-run-unit-tests-kinds.py`

Authorities read: approved `BRIEF.md`, approved `plan.yaml` including D-01–D-10 and T-01–T-12, c3 validator digest `runs/2026-09-03-review-c3-validator/digest.md`, and c3 code note `notes/review-harness-code-reviewer-c3.md`. The configured review policy is `advisory_unless_high` (`.harness/harness.json:346-349`).

## Stage 1 — specification compliance: FAIL

### F-10 — high, must-fix — SC-15's no-re-resolution assertion watches the wrong output

**Defect class:** assertion subject mismatch / fail-open verification.

`_feat54_check_case` defaults its `needles` filter to `Done when` and only counts a handoff line containing every needle (`tests/integration/test-check-state.py:2162-2171`). The two cases intended to prove absent targets never rot pass no different needle (`:2234-2238`). But the production unresolved-target message is `Authority pointer ... is unresolved ...; follow templates/HANDOFF.md` (`handoff_done_when.py:112-113,116-141`); it does not contain `Done when`.

**Concrete failure scenario.** A future edit changes the persisted caller at `check-state.sh:1250-1251` from `resolve=False` to `resolve=True`. A later BRIEF renumbers `SC-04`, or a finding/approval target disappears. INV-17 then reports the untouched handoff as an unresolved-authority shape failure and exits 1, violating REQ-06, D-10 and SC-15. Both named “absent targets do not rot” cases still compute `lines=[]` because the new violation lacks `Done when`, so `bool(lines) == False` remains true and the complete `test-check-state.py` run stays green. The adjacent unit case proves what the module does when explicitly passed `False`; it does not bind the state gate to passing `False`.

SC-15 requires the fixture to be “reported by NO line of the state check,” not merely by no line containing one phrase. Repair owner: **Main-session-direct enforcement-test lane under DEC-174**, path `tests/integration/test-check-state.py`. The negative cases must reject any reported line naming the fixture handoff, ideally with a discriminating caller-mode mutant or equivalent executable control.

This is high because a one-token caller regression defeats the central “stable afterwards” guarantee, turns previously valid persisted notes into repository-entry blockers, and passes the permanent suite that claims to prevent exactly that outcome. Under `advisory_unless_high`, it gates this review.

No other scope creep, omission, or REQ/D mismatch was found in the 16-path set. The implementation currently calls `resolve=False`; the failure is the signed automated proof, not a claim that the current pin already re-resolves targets.

### Inspection success criteria

- **SC-04 PASS.** From the repository root, the exact command `bash .claude/skills/harness/bin/check-state.sh` completed with **exit 0**. Its complete 812-line output contains **0 `Done when` findings** and **0 `VIOLATION` lines**. The former c3 FEAT-51 missing-handoff blocker is gone.
- **SC-07 PASS by inspection.** The write gate imports/calls the shared module with `resolve=True` (`check-domain.sh:1561-1566`); the persisted gate imports/calls the same module with `resolve=False` (`check-state.sh:53-56,1243-1251`). No second Done-when body parser or pointer resolver exists in either gate.
- **SC-08 PASS by inspection.** The template (`HANDOFF.md:1-17,37-40`), playbook (`SKILL.md:309-316`), write gate (`check-domain.sh:1547-1574`), state gate (`check-state.sh:1069-1070,1211-1259`), DEC-159 (`DECISIONS.md:3701-3729`) and DEC-214 (`:6696-6724`) state the five-section contract. The only `four headings` hits are the criterion-authorized FEAT-31 historical measurements at `check-state.sh:1198-1202,1215-1219`.
- **SC-11 PASS by inspection.** The base-to-pin handoff diff contains four `A` rows and no modified/deleted base-existing handoff: FEAT-51 `handoff-validate.md`, and FEAT-54 `handoff-build.md`, `handoff-plan.md`, and `handoff-validate.md`. Thus the historical intersection is empty and the non-empty diff arm equals the added-only arm. Only the two contract-listed FEAT-54 handoffs were content-inspected; the other two paths remained outside the exact 16-path content scope.
- **SC-01/02/03/05/06/09/12/13/14 otherwise PASS on current-pin focused evidence.** `test-handoff-done-when.py` passed 54 printed checks; `test-probe-handoff-comprehension.py` passed 6 methods; `test-check-domain.py` passed all 41 FEAT-54 handoff cases; `test-run-unit-tests-kinds.py` passed all 5 registration/isolation cases; the real probe `--dry-run` exited 0 and planned two calls without executing them.
- **SC-15 FAIL as verification.** `test-check-state.py` completed successfully, including its 17 printed FEAT-54 cases, but the no-rot pair is non-discriminating for the production regression above. Current behavior is correct by inspection; the required permanent automated proof is not.
- **SC-10 PENDING / not performed.** Operator UAT was expressly outside this assignment and was not simulated.

The configured baseline independently measured **141 entries, 141 unique, sorted, and zero FEAT-54 members**. The focused current-pin commands were used only for these contract seams; no formatter, linter, project-wide build, project-wide suite, PM goal-check, live-model UAT, or SC-10 UAT ran.

## Prior findings, independently re-assessed at `f05e1e6`

| Finding | Current disposition | Current-pin evidence |
|---|---|---|
| F-01 — resolver containment/fail-closed | **closed** | Absolute, traversal, control-bearing, symlink-escape and special-file finding/approval targets are refused by `handoff_done_when.py:63-101,241-252`; unit and real write-gate cases passed for both authority families. |
| F-02 — probe admission/local-file disclosure | **closed** | `probe-handoff-comprehension.py:54-109` contains path, basename, symlink, regular-file, size and UTF-8 admission before model calls; all six focused methods passed, with rejected inputs making zero calls and the valid control making two. |
| F-03 — invalid pre-mutation Edit | **closed** | `check-domain.sh:1818-1873` reconstructs protected Edit candidates and refuses non-UTF-8 existing bytes before mutation; integration cases passed and asserted byte identity. |
| F-04 — literal SC-04 | **closed** | Exact root command exit 0, zero `Done when` findings, zero violations. |
| F-05 — blank Scope | **closed** | `handoff_done_when.py:187-193`; unit/write/state blank-Scope cases passed. |
| F-06 — Scope ordering | **closed** | `handoff_done_when.py:209-215`; unit/write/state Authority-first cases passed. |
| F-07 — changed-function risk | **closed** | Exact base/head grader passed all 86 discovered identities at the configured bars; details below. |
| F-08 — nested/duplicate H2 truncation | **closed** | `handoff_done_when.py:24-35,272-281`; nested-H3 and duplicate-H2 cases passed through unit, write and persisted layers. |
| F-09 — strict ATX approvals | **closed** | `handoff_done_when.py:154-171`; no-space and seven-hash lookalikes were refused beside valid controls in unit/write tests. |
| SEC-F-08 — raw terminal controls | **survives, med advisory** | Repository/model-controlled strings still reach `print(answer or "(no answer)")` and error/detail output without neutralization (`probe-handoff-comprehension.py:133-146,181-197`). A note fact or model answer containing ESC/OSC bytes can alter the operator's terminal display. Owner: harness-dev-ops via harness-eng-lead. This remains substantive but would not gate by itself under `advisory_unless_high`. |

The c3 duplicate missing-section refusal remains redundant but non-defective: it fails closed and violates no approved contract.

## Mandatory Python risk grade

Command: `python3 .claude/skills/harness/bin/code-grade.py --base 0ec44965a961d19177de871c3bb1f02b701e646b --head f05e1e6cd74c7d91580dd6ef565a00432faac1ad`

Result: exit 0, `PASSING: 86`, `code_grade: pass`. The grader discovered **86 changed function identities**: **27 production** functions in `handoff_done_when.py`, all at production bar **4** or better, and **59 test/probe** functions across the five changed Python test/probe paths, all at test bar **3** or better. No grade-2 reason and no blocking mechanical record was emitted. The exact scope is unchanged from c3, but the grader was independently rerun against the new immutable head.

## Stage 2 — code quality

**Not entered.** Stage 1 failed the required SC-15 automated proof. The mechanical grade is mandatory evidence, not a substitute for discretionary Stage 2. SEC-F-08 is recorded above only because the assignment explicitly required its current-pin disposition.

## Adequacy limits

- No dynamic mutant was written into the checkout. F-10 is established by the literal assertion subject at `test-check-state.py:2162-2171`, the unqualified no-rot callers at `:2234-2238`, and the production unresolved-message text at `handoff_done_when.py:112-141`; those three facts determine that a `resolve=True` caller mutation is invisible to the cases.
- The live credentialed comprehension comparison was not run; only `--dry-run` was exercised, as required by the non-goal and `locally_run` policy.
- SC-10, PM goal-check, full matrix suites, unrelated suites, builds, formatters and linters were not run.

```yaml
VERDICT: FAIL
DIGEST:
  headline: "SC-04 is now clean, but SC-15's no-re-resolution test filters out the exact unresolved-authority regression it claims to forbid."
  severity_max: high
  findings: 2
  must_fix:
    - "F-10: Main-session-direct must repair tests/integration/test-check-state.py so the two absent-target cases reject every state-check line naming the fixture handoff, and prove the check-state caller cannot change from resolve=False to resolve=True while green."
  spec_violations:
    - { kind: mismatch, path: tests/integration/test-check-state.py, ref: D-10 }
  reviewed: "0ec44965a961d19177de871c3bb1f02b701e646b..f05e1e6cd74c7d91580dd6ef565a00432faac1ad"
  human_commits_in_scope: []
  code_grade: pass
  open_questions: []
  files_touched:
    - .harness/harness/features/FEAT-54-handoff-done-when/notes/review-harness-code-reviewer-c4.md
  expertise_update: []
artifact: .harness/harness/features/FEAT-54-handoff-done-when/notes/review-harness-code-reviewer-c4.md
```
