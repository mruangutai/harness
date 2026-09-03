# Code review — FEAT-54 handoff Done when — c3

**FAIL.** Stage 1 is blocked by the literal SC-04 command: from the exact repository root it exits 1 on one remaining violation, FEAT-51's missing `notes/handoff-validate.md`. The complete output contains no `Done when` line, so FEAT-54's own corpus contract is clean, but the operator explicitly made exit 0 with no remaining violations mandatory and forbade waiving or fixture-substituting this check. F-01–F-03 and F-05–F-09 are closed at the pin. Because Stage 1 does not pass, discretionary Stage 2 code-quality review was not entered; the mandatory mechanical Python grade nevertheless passes all 86 exact changed-function identities.

Reviewed immutable range: `0ec44965a961d19177de871c3bb1f02b701e646b..39602414e1cfe792655b7e68bce367e92790c32a`. All 16 required implementation/config/docs/test/handoff paths were checked against the pin before inspection (`git diff --quiet 3960241 -- <required set>` exit 0). The full range contains 87 changed paths; the behavioral paths trace to T-01–T-12 / REQ-01–REQ-10, and the remainder are feature-local planning, run, QA, review, receipt, observation, and grilling evidence. No `[harness:human]` commit occurs in the range.

## Stage 1 — specification compliance

### F-04 — surviving — high — SC-04 literal root check is red

**Failure scenario.** An operator enters Harness at this pinned checkout and runs the required state gate. It exits 1 because `FEAT-51-claude-code-lifecycle-safety` is `done` without `notes/handoff-validate.md`; consequently this review cannot truthfully claim the acceptance-required clean repository state or pass FEAT-54, even though no Done-when violation is present.

**Exact evidence.** From the repository root, `bash .claude/skills/harness/bin/check-state.sh` exited **1**. It reported exactly one `VIOLATION`:

- `FEAT-51-claude-code-lifecycle-safety: status is 'done' but notes/handoff-validate.md is missing — the validate seam was crossed without a handoff; the successor is on the disk-only path (DEC-159).`

All other output rows were `note` rows. Searching the complete 812-line capture returned **zero** output lines naming `Done when`. This fails the operator's mandatory literal SC-04 exit-0/no-remaining-violations clause; it cannot be waived, replaced with the green fixture corpus, or repaired by changing FEAT-51 inside this review.

**Owner lane:** Main session, FEAT-51 corpus/state reconciliation. Do not change FEAT-54's parser or either gate to conceal the violation; gate-script work would separately remain Main-direct under DEC-174.

No other REQ/D mismatch, omission, or scope creep was found in the pinned FEAT-54 change.

## Earlier F-01–F-09 dispositions

| Finding | Disposition at `3960241` | Exact evidence |
|---|---|---|
| F-01 — finding/approval containment and resolver fail-closed behavior | **closed** | Path grammar rejects absolute, traversal and control-bearing finding and approval paths (`handoff_done_when.py:57-75`); bounded regular UTF-8 reads must remain under root (`:78-101`); unexpected resolver exceptions become refusals (`:241-252`). Unit coverage independently exercises both finding and approval for absolute/traversal/control, symlink escape and FIFO targets (`test-handoff-done-when.py:76-103,169-192`); the real write gate repeats approval absolute/traversal and both kinds' symlink/FIFO cases (`test-check-domain.py:4108-4134`). All named cases passed. |
| F-02 — comprehension-probe admission / local-file disclosure | **closed** | Explicit/default candidates pass one containment, basename, symlink, regular-file, size and UTF-8 admission seam before `run` can call the model (`probe-handoff-comprehension.py:54-109`). Six focused test methods require zero calls for rejected outside/traversal/symlink/directory/wrong-name/oversized inputs and exactly two calls for a valid note (`test-probe-handoff-comprehension.py:41-101`); all six passed. |
| F-03 — pre-mutation Edit, including unreadable/non-UTF-8 existing bytes | **closed** | Handoff Edit is reconstructed and shape-checked in PreToolUse (`check-domain.sh:1820-1873`); invalid UTF-8 returns the sentinel and exits 2 before mutation (`:1840-1845,1864-1869`). Integration cases require exit 2 plus byte identity for an invalid candidate and separately for invalid UTF-8, restoring the fixture only afterward (`test-check-domain.py:4138-4190`); all passed. |
| F-04 — literal SC-04 | **survives** | Root command exit 1, one FEAT-51 violation, zero `Done when` lines; see above. |
| F-05 — non-empty Scope | **closed** | `_scope_problems` trims and refuses blank values (`handoff_done_when.py:187-193`); unit/write/state blank-Scope cases passed (`test-handoff-done-when.py:68-74`, `test-check-domain.py:4043-4064`, `test-check-state.py:2178-2258`). |
| F-06 — Scope precedes every Authority | **closed** | Product ruling makes REQ-02 controlling (`notes/research-FEAT-54-validation-order-c1.md:1-30`); `_order_problems` rejects Authority-first (`handoff_done_when.py:209-215`), with unit/write/state cases green at the same test ranges. |
| F-07 — changed-function risk | **closed** | Exact pinned grader exited 0 with `PASSING: 86`; 27 production identities meet bar 4 and 59 test identities meet bar 3; no grade-2 reason or blocking record exists. |
| F-08 — nested/duplicate heading truncation | **closed** | `_done_when_indices` requires exactly one standalone H2 and `_body` stops only at the next H2, not `###` (`handoff_done_when.py:24-35,272-281`). Unit, real write-gate and persisted-state nested/duplicate cases all passed (`test-handoff-done-when.py:52-70`, `test-check-domain.py:4033-4064`, `test-check-state.py:2178-2258`). A nested heading is now prohibited prose; a duplicate yields an exact-count refusal. |
| F-09 — non-Markdown approval headings | **closed** | `_atx_heading_text` accepts only 1–6 hashes followed by required whitespace, with optional closing hashes (`handoff_done_when.py:154-171`). `#Approval` and `####### Approval` are separately refused while ordinary `## Approval` remains the resolving control (`test-handoff-done-when.py:21-31,134-145`; `test-check-domain.py:4017-4029,4092-4105`). |

## Named repair seams and approval coverage

- **Approval authorities:** BRIEF and plan are both signed by Mike Ruangutai (`BRIEF.md:199-203`; `plan.yaml:3-6`). Both feature handoffs cite the real `BRIEF.md#Approval` target and resolve with `problems(..., resolve=True)` (`handoff-build.md:33-37`; `handoff-plan.md:53-55`). Approval resolution has its own positive/unresolvable pair, strict-ATX cases, and independent containment cases rather than borrowing finding coverage.
- **Logical AND / fail-closed:** four valid authorities pass and the same block with one dangling authority returns exactly one named problem (`test-handoff-done-when.py:110-132`). Write-time target failures and unexpected resolver exceptions refuse; persisted mode preserves grammar/shape while intentionally opening no target (`handoff_done_when.py:224-252,261-288`; `test-check-domain.py:4193-4213`; `test-check-state.py:2211-2258`).
- **One parser/resolver:** `check-domain.sh:1561-1566` calls `handoff_done_when.problems(..., resolve=True)` and `check-state.sh:53-56,1243-1251` calls the same interface with `resolve=False`. Searches found no second Done-when body parser or pointer resolver in either gate. This satisfies SC-07/DEC-179.
- **Five-section/current-contract wording:** the template (`HANDOFF.md:1-17,37-40`), playbook (`SKILL.md:310-316`), gate (`check-domain.sh:1544-1574`), state check (`check-state.sh:1069-1070,1212-1259`), amended DEC-159 (`DECISIONS.md:3701-3729`) and DEC-214 (`:6696-6724`) all state the current five-section contract. The only surviving gate-script four-heading text is the two SC-08-authorized FEAT-31 historical observations (`check-state.sh:1194-1202,1215-1219`).
- **Frozen corpus / no per-section cap:** the configured baseline is exactly **141**, unique, and byte-for-byte equal to the mechanically regenerated `b7956fc4` set. The two FEAT-54 handoffs are non-baselined, 37 and 55 lines, and each returns zero write-time problems. Whole-file 60/61 and long-Trust-at-60 cases pass through both gates (`test-check-domain.py:4235-4247`; `test-check-state.py:2263-2303`).
- **Probe registration/isolation:** `.harness/harness.json:284-295` registers `handoff_comprehension` as `locally_run` with exact detect/cmd/exclude and no matrix entry. The real-config presence check, empty-detect mutant, removed-kind mutant, `--kind all` sentinel, and layout control all passed (`test-run-unit-tests-kinds.py:15-98`). The credentialled nondeterministic run was not performed and remains outside normal suites, as required.
- **Five repaired lead digests:** each of the five named run digests was read and independently passed `validate-digest.py lead` (`digest ok`, exit 0): `2026-09-03-qa-validation-c2-validator`, `2026-09-03-validation-c1-eng`, `2026-09-03-validation-c2-eng`, `2026-09-03-qa-post-simplify-c2-validator`, and `2026-09-02-validation-c1-eng`.

## Success-criterion inspection

- **SC-01/02/03/05/06/09/12/13/14/15: PASS.** The five focused files completed in one chained run with exit 0 and **123** explicit focused objects: 54 shared-validator assertions, 6 probe-admission test methods, 41 write-gate handoff cases, 17 state-gate handoff cases, and 5 probe-registration/isolation cases.
- **SC-04: FAIL.** Literal root check exit 1 with the sole violation recorded above; zero lines name `Done when`.
- **SC-07: PASS inspection.** Single implementation/call sites cited above.
- **SC-08: PASS inspection.** Current surfaces say five; only both authorized historical observations say four.
- **SC-10: PENDING operator UAT.** Not run or substituted here.
- **SC-11: PASS inspection.** The exact repository-root command resolved `BASE=0ec44965a961d19177de871c3bb1f02b701e646b`; `comm -12` printed nothing. `comm -23` printed exactly the two FEAT-54 handoffs, and the added-only arm printed the identical two-path set. The positive control is non-empty and no base-existing handoff was touched.

## Mandatory identity-bound Python grade

Command: `python3 .claude/skills/harness/bin/code-grade.py --base 0ec44965a961d19177de871c3bb1f02b701e646b --head 39602414e1cfe792655b7e68bce367e92790c32a` — exit 0, `PASSING: 86`, `code_grade: pass`. The tool emitted cyclomatic/cognitive/ABC values for every identity. Compact identity/grade census:

- Production bar 4, `.claude/skills/harness/bin/handoff_done_when.py` (27): `_message` g5; `_done_when_indices` g5; `_body` g5; `_grammar` g5; `_unknown` g5; `_feature_dir` g5; `_pointer_path` g5; `_unsafe_rel_path` g4; `_read_target` g4; `_contains_token` g5; `_unresolved` g5; `_resolve_plan` g4; `_resolve_brief` g4; `_resolve_finding` g5; `_atx_heading_text` g5; `_resolve_approval` g4; `_resolve` g5; `_scope_problems` g5; `_authority_count_problems` g5; `_line_problems` g5; `_order_problems` g4; `_shape_problems` g5; `_parse_authorities` g4; `_resolution_problems` g4; `_classified_lines` g4; `_resolve_all` g5; `problems` g4.
- Test bar 3, `tests/integration/test-check-domain.py` (15): `_record_handoff_result` g4; `_handoff_text` g5; `_invoke_handoff` g5; `_handoff_done_when_fixture` g4; `_handoff_grammar_cases` g4; `_handoff_pointer_cases` g3; `_handoff_unsafe_cases` g4; `_handoff_valid_pre_edit_cases` g4; `_handoff_invalid_utf8_pre_edit_case` g4; `_handoff_pre_edit_cases` g5; `_handoff_validator_exception_case` g4; `_handoff_existing_edit_cases` g4; `_handoff_line_cap_cases` g4; `_report_handoff_results` g4; `run_handoff_done_when` g4.
- Test bar 3, `tests/integration/test-check-state.py` (7): `_feat54_fixture_case` g4; `_feat54_check_case` g4; `_feat54_case_notes` g4; `_feat54_baseline_cases` g4; `_feat54_clean_corpus_case` g3; `_feat54_line_cap_case` g4; `case_feat54_done_when` g5.
- Test bar 3, `tests/integration/test-run-unit-tests-kinds.py` (4): `check` g5; `registration_problems` g4; `tree` g4; `run` g5.
- Registered test bar 3, `tests/manual/probe-handoff-comprehension.py` (17): `arguments` g5; `is_handoff_note` g5; `read_regular_file` g4; `validate_note` g4; `note_paths` g4; `done_when_facts` g4; `without_done_when` g5; `prompt` g5; `ask` g4; `normalized` g5; `covered_facts` g5; `print_plan` g4; `print_note_header` g4; `measure_arm` g4; `measure_note` g4; `run` g3; `main` g5.
- Test bar 3, `tests/unit/test-handoff-done-when.py` (4): `check` g5; `fixture` g5; `note` g5; `problems` g5.
- Test bar 3, `tests/unit/test-probe-handoff-comprehension.py` (12): `load_probe` g5; `ProbePathSecurityTest.setUp` g5; `tearDown` g5; `record_call` g5; `exercise` g5; `assert_refused_without_model_call` g5; `test_explicit_repository_outside_absolute_and_traversal_are_refused` g4; `test_repository_contained_symlink_is_refused_for_explicit_and_default_selection` g5; `test_non_regular_input_is_refused` g5; `test_wrong_basename_and_oversized_note_are_refused` g5; `test_valid_handoff_reaches_both_measurement_arms` g5; `test_dry_run_makes_no_model_call` g5.

## Stage 2 — code quality

Not entered: Stage 1 failed on mandatory SC-04. The mechanical grade above is required evidence, not a substitute for Stage 2 and not a claim that a discretionary quality pass occurred.

```yaml
VERDICT: FAIL
DIGEST:
  headline: "Literal SC-04 still exits 1 on FEAT-51's missing validate handoff; every FEAT-54 repair seam and all 86 changed-function grades otherwise pass."
  severity_max: high
  findings: 1
  must_fix:
    - "F-04: Main must reconcile FEAT-51's missing notes/handoff-validate.md outside this FEAT-54 review so the exact repository-root check-state command exits 0; do not waive, fixture-substitute, or hide the violation in a gate change."
  spec_violations: []
  reviewed: "0ec44965a961d19177de871c3bb1f02b701e646b..39602414e1cfe792655b7e68bce367e92790c32a"
  human_commits_in_scope: []
  code_grade: pass
  open_questions: []
  files_touched:
    - .harness/harness/features/FEAT-54-handoff-done-when/notes/review-harness-code-reviewer-c3.md
  expertise_update: []
artifact: .harness/harness/features/FEAT-54-handoff-done-when/notes/review-harness-code-reviewer-c3.md
```
