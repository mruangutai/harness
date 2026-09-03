# Code review — FEAT-54 handoff Done when — c5

**FAIL.** Stage 1 has two high blockers. First, the literal SC-04 command now exits 1 on an unrelated standing BUG-1157 worktree, although it reports zero lines naming `Done when`; the user's explicit acceptance rule requires exit 0. Second, both real FEAT-54 handoffs point their immediate-action completion boundary at a BRIEF approval that was already satisfied before either next action began, so the new section can declare re-signature or validation complete without those actions occurring. F-10 and SEC-F-10 are closed by the requested executable repairs. Stage 2 was not entered because Stage 1 failed.

Reviewed immutable range: `0ec44965a961d19177de871c3bb1f02b701e646b..4690f724cdbbdf03649f0cbea07efe7be3c03ce0`. The checkout was exactly at `4690f724cdbbdf03649f0cbea07efe7be3c03ce0`. No `[harness:human]` commit occurs in the range.

## Exact 16-path scope

Every path in the shared scope was inspected in the pinned diff and at the pinned checkout:

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

Authorities read: approved `BRIEF.md`; approved `plan.yaml`, including D-01–D-10 and T-01–T-12; c4 code/security review notes; and `runs/2026-09-03-sec-f10-c5-eng/digest.md`. The configured review policy is `advisory_unless_high` (`.harness/harness.json:346-349`).

## Stage 1 — spec compliance: FAIL

### F-04 — high, must-fix — literal SC-04 exits 1

From the repository root, the exact command `bash .claude/skills/harness/bin/check-state.sh` exited **1**. Its complete captured output contains **zero** lines naming `Done when`, but it contains one violation: INV-29 reports the standing worktree `.claude/worktrees/harness/BUG-1157-approval-overrule` because its landed `feature.json` is missing and terminal status cannot be determined.

**Failure scenario.** A reviewer runs the acceptance-prescribed repository state gate at this pin. The external worktree lookup fails, INV-29 reports rather than exempts it, and the command returns 1. The feature therefore cannot satisfy the explicit c5 rule that SC-04 exit 0, even though FEAT-54's handoff corpus itself produces no Done-when finding.

**Owner lane:** Main session / worktree lifecycle owner, outside FEAT-54 source. Do not weaken `check-state.sh` or remove a worktree from inside this feature worktree.

### F-11 — high, must-fix — both real Done-when authorities are already satisfied before their actions start

`handoff-plan.md:3-8` says the immediate next action is to re-sign the amended plan and brief. Its only completion authority at `handoff-plan.md:55` is `approval:.../BRIEF.md#Approval`, while the same note explicitly records that the approval bytes already say approved (`handoff-plan.md:29-30`). `handoff-build.md:3-8` says the immediate action is to run the validation panel and obtain its verdict, but its only authority at `handoff-build.md:37` is the same approval. The target itself already says `status: approved` (`BRIEF.md:199-203`).

**Failure scenario.** A successor validates either section before doing `## Next`. It follows the sole authority, sees the BRIEF approval is already satisfied, and may conclude the action is complete without re-signing or without running the validation panel. The section therefore describes a precondition, not the completion boundary of the immediate action, violating REQ-01, REQ-03, and T-11's requirement that the selected Scope/Authority describe that action.

This is high because the only two in-scope real handoffs demonstrate the exact early-stop mode the feature exists to prevent. Resolution-to-an-existing-heading proves pointer syntax and target existence; it does not prove that the target governs completion of the named action.

**Owner lane:** Main-session-direct handoff-note lane (T-11), paths `notes/handoff-plan.md` and `notes/handoff-build.md`.

### REQ/SC census

- **REQ-01 / REQ-03: FAIL** on F-11. Mechanical presence and AND evaluation exist, but the two real notes' only authority is already satisfied and does not delimit their immediate actions.
- **REQ-02, REQ-04, REQ-05: PASS.** The shared parser enforces one non-empty `Scope:`, one-to-four `Authority:` lines, no other prose, four exact typed grammars, ordering, and source-location refusal. The 54 direct checks and 41 real write-gate cases passed.
- **REQ-06: PASS.** `check-domain.sh:1561-1566` calls the shared implementation with `resolve=True` and fails closed; `check-state.sh:1243-1251` calls it with `resolve=False`. The repaired persisted fixtures reject every output line naming their handoff, and the caller-mode mutant discriminates exactly `real=0, mutant=1`.
- **REQ-07: PASS.** The frozen baseline is 141 entries, 141 unique, sorted, and set-equal to the `b7956fc4` handoff enumeration. It contains no FEAT-54 note.
- **REQ-08: PASS.** Whole-file 60/61 boundaries and long-Trust-at-60 cases passed through both gates; no per-section cap exists.
- **REQ-09: PASS.** Template, playbook, both gates, DEC-159, and DEC-214 state five sections. The only gate-script `four headings` occurrences are the two SC-08-authorized FEAT-31 historical observations at `check-state.sh:1198-1202,1215-1219`.
- **REQ-10: PASS.** Deterministic behavior is in the permanent unit/integration gates. The comprehension probe is `locally_run`, outside `test_matrix`, and excluded from `--kind all` by executable fixture evidence.
- **SC-01/02/03/05/06/09/12/13/14: PASS** on focused executable evidence.
- **SC-04: FAIL.** Exact root command exit 1; zero reported `Done when` lines; one unrelated INV-29 violation.
- **SC-07: PASS by inspection.** Both callers cross one `handoff_done_when.problems` interface; neither gate contains a second Done-when body parser or pointer resolver.
- **SC-08: PASS by inspection.** Current-contract prose says five; only authorized historical observations remain.
- **SC-10: not performed.** Operator UAT is expressly outside this review.
- **SC-11: PASS by inspection/execution.** With `BASE=$(git merge-base main 4690f724...)`, `comm -12` printed nothing. `comm -23` printed four added handoffs and exactly matched the added-only arm: FEAT-51 validate plus FEAT-54 plan/build/validate. The positive control was non-empty.
- **SC-15: PASS.** Both baselined and non-baselined absent-target fixtures matched no output line naming `handoff-plan.md`; malformed shape and unknown grammar remained loud. The real caller uses `resolve=False`, and the executable `False→True` mutation printed `real=0, mutant=1` and returned 1 for the mutant.

## Prior finding dispositions at `4690f724`

| Finding | c5 disposition | Evidence |
|---|---|---|
| F-01 — resolver containment/fail-closed | **closed** | Absolute/traversal/control paths, symlink escape, special files, and resolver exceptions refuse; direct and write-gate cases passed. |
| F-02 — probe path admission | **closed** | Outside/traversal/symlink/directory/wrong-name/oversized inputs made zero model calls; valid control made two. |
| F-03 — invalid pre-mutation Edit | **closed** | Invalid and invalid-UTF-8 Edit candidates exit 2 before mutation and preserve bytes. |
| F-04 — literal SC-04 | **reopened, high** | Exact command now exits 1 on INV-29; zero Done-when lines. |
| F-05 — blank Scope | **closed** | Direct, write, and persisted cases refuse it. |
| F-06 — Scope ordering | **closed** | Direct, write, and persisted Authority-first cases refuse it. |
| F-07 — Python risk | **closed** | Exact mandatory grader exits 0 with `PASSING: 90`. |
| F-08 — nested/duplicate H2 truncation | **closed** | Nested prose and duplicate H2 cases refuse at all three layers. |
| F-09 — strict ATX approval headings | **closed** | `#Approval` and seven-hash lookalikes refuse beside valid controls. |
| F-10 — SC-15 assertion subject | **closed** | Negative fixtures use an empty needle tuple and therefore reject every line naming the handoff; executable caller mutation prints `real=0, mutant=1`. |
| SEC-F-08 — raw terminal controls | **survives, med advisory** | Repository/model strings still reach `print` sinks without neutralization (`probe-handoff-comprehension.py:82-98,172-197`). A crafted ESC/OSC sequence can alter the operator's display during the manual run. Owner: harness-dev-ops via harness-eng-lead. |
| SEC-F-10 — tool-enabled auto-approved probe | **closed** | Actual argv contains exactly one `--no-tools` and no `--auto-approve` (`probe-handoff-comprehension.py:133-142`); focused test captures the real subprocess argv and pins both facts (`test-probe-handoff-comprehension.py:97-106`). |

## Focused execution and Python risk grade

- `python3 tests/unit/test-handoff-done-when.py` — exit 0, **54** printed checks passed.
- `python3 tests/unit/test-probe-handoff-comprehension.py` — exit 0, **7** tests passed; includes the exact argv assertion.
- `python3 tests/integration/test-check-domain.py` — exit 0; all **41** FEAT-54 handoff cases passed.
- `python3 tests/integration/test-check-state.py` — exit 0; all FEAT-54 cases passed, including `state caller-mode mutation (real=0, mutant=1)`.
- `python3 tests/integration/test-run-unit-tests-kinds.py` — exit 0, **5** registration/isolation checks passed.
- `python3 tests/manual/probe-handoff-comprehension.py --dry-run` — exit 0, planned two calls and executed none.
- Literal SC-04: `bash .claude/skills/harness/bin/check-state.sh` — **exit 1**, **0** lines name `Done when`, **1** INV-29 violation.

Mandatory command:

`python3 /Users/molchairuangutai/GitHub/harness/.claude/skills/harness/bin/code-grade.py --base 0ec44965a961d19177de871c3bb1f02b701e646b --head 4690f724cdbbdf03649f0cbea07efe7be3c03ce0`

Result: exit 0, `PASSING: 90`, `code_grade: pass`. All 27 production functions in `handoff_done_when.py` meet bar 4 or better; every changed test/probe function meets bar 3 or better. No grade-2 reason or blocking record was emitted.

No formatter, linter, project-wide build, unselected suite, credentialled model call, SC-10 UAT, or PM goal-check ran.

## Stage 2 — code quality: NOT ENTERED

Stage 1 failed, so the ordered review protocol forbids a discretionary Stage 2 pass. SEC-F-08 is recorded only because this dispatch explicitly required its c5 disposition; it remains medium advisory and would not gate by itself.

```yaml
VERDICT: FAIL
DIGEST:
  headline: "F-10 and SEC-F-10 are closed, but literal SC-04 exits 1 and both real handoffs use an already-satisfied approval as their action boundary."
  severity_max: high
  findings: 3
  must_fix:
    - "F-04: Main/worktree lifecycle owner must reconcile the unrelated BUG-1157 standing-worktree INV-29 so the exact repository-root SC-04 command exits 0; do not weaken the state gate or remove a worktree from inside this feature worktree."
    - "F-11: Main-session-direct must replace the already-satisfied BRIEF approval authorities in handoff-plan.md and handoff-build.md with authorities that actually delimit each note's immediate Next action."
  spec_violations:
    - { kind: mismatch, path: .harness/harness/features/FEAT-54-handoff-done-when/notes/handoff-plan.md, ref: REQ-03 }
    - { kind: mismatch, path: .harness/harness/features/FEAT-54-handoff-done-when/notes/handoff-build.md, ref: REQ-03 }
  reviewed: "0ec44965a961d19177de871c3bb1f02b701e646b..4690f724cdbbdf03649f0cbea07efe7be3c03ce0"
  human_commits_in_scope: []
  code_grade: pass
  open_questions: []
  files_touched:
    - .harness/harness/features/FEAT-54-handoff-done-when/notes/review-harness-code-reviewer-c5.md
  expertise_update: []
artifact: /Users/molchairuangutai/GitHub/harness/.claude/worktrees/harness/FEAT-54-handoff-done-when/.harness/harness/features/FEAT-54-handoff-done-when/notes/review-harness-code-reviewer-c5.md
```
