# Fix c1 — tests (FixC1_Tests) — FEAT-2397 — 2026-11-22

Contract: `notes/answers-2026-11-22-c0-escalations.md` (Q1(a), Q1(b), c1 item 2). Grades come from
`.claude/skills/harness/bin/code-grade.py <paths>` (the same `code_grade` module that `tests/unit/test-code-grade.py` loads). The bar is 3.

## T-03 decomposition: same cases, same assertions, same order

- **`test-check-domain.py::_feat2274_cases`**
  - Before: grade 2 (CC8 / cog6 / ABC33.5).
  - Extracted `_run_unreadable(root)`, `_run_no_boundary()` and `_exits(result, code, gates)`.
  - After: `_feat2274_cases` 4 (2/1/15.4), `_run_unreadable` 5, `_run_no_boundary` 4, `_exits` 5.
  - The fixture and subprocess call order is unchanged: root, unreadable, no_boundary, passed, main_session, denied.
- **`test-layout-migration.py::_parity`**
  - Before: grade 2 (CC12 / cog10 / ABC30.8).
  - Extracted `_parity_env(tmp)`, `_parity_sides(build_kwargs, extra)` and `_parity_cause(label, res, gate, ci)`.
  - After: `_parity` 4 (5/0/9.1), `_parity_env` 5, `_parity_sides` 4, `_parity_cause` 4.
  - The two `check()` calls keep their text and order.

## Q1(a): `test-no-distribution.py` case6

- **Workflow exemption.** The absence scan now skips `.github/workflows/`. The comment says workflows are callers that set the resolver's seam, the same rationale as the `test-*` exemption, and cites the T-02 rename ruling. The heading changes from "FOUR" to "FIVE EXCLUSIONS".
- **Stale sentence fixed.** The claim "assigned repo-wide in exactly one place — test-gh-close-gate.py:41" now reads "assigned by the test files and their fixtures (and by the CI workflows below)".
- **Unchanged.** The presence half, the deleted-names checks, the survivors checks and every other scanned path stay as they were.
- **Grade.** `case6` was grade 1 (CC28 / cog28 / ABC62.4) and is a changed body. It is split into `_case6_scanned`, `_line_hits`, `_case6_absence`, `_case6_presence`, `_case6_deleted_names` and `_case6_survivors`. Their grades are 4, 5, 4, 4, 4 and 5, and `case6` itself is now 5.
  - The check names, messages and order are the same.
  - Substring matching on the chain name becomes `re.search(re.escape(name))`, which is equivalent.
- **Result.** case6 passes all 10 checks with 0 offenders on the current tree, which already has the other builder's bin-comment rewording.

## Q1(b): `test-lead-stop-and-wake.py`

- **Floor dropped.** The ≥1 floor (`case_floor_*` zero-occurrence failure) is removed. The count is printed instead.
  - Strict zero is not asserted.
  - An unreadable DECISIONS.md still fails.
  - The per-occurrence QUALIFIER/STRUCK bound check is unchanged.
- **Positive control added.** `detector_control_cases()` / `DETECTOR_SAMPLES` checks that `ONCE_RE` matches "A stop refusal fires at most once." and `QUALIFIER_RE` matches "…per consecutive stop sequence.". It runs inside `bound_cases` after the `--only` guard, so `--self-check` is unaffected.
- **Docstring.** It now explains that FEAT-2397 removed the bypass doctrine.
- **Grades.** `bound_site_cases` 3, `detector_control_cases` 5, `bound_cases` 4.
- **Live run.** 0 occurrences, both controls PASS.

## TDD evidence

All of these used temporary copies or module patches under /tmp. No repo files were edited for them.

- **Bound check.** I made a copy of DECISIONS.md and appended `## DEC-999 probe` with "A stop refusal fires at most once.". The bound check fails `case_occurrence_c1_DECISIONS.md_8692_1`.
- **Positive control.** I replaced `ONCE_RE` with a regex that never matches, and `case_detector_control_ONCE_RE` fails. Doing the same to `QUALIFIER_RE` makes `case_detector_control_QUALIFIER_RE` fail.
- **case6.** I built a probe tree containing `tools/probe.sh` (`export <var>=x`) and `.github/workflows/ci.yml` (`env: <var>: x`). Running `_case6_absence` against it fails with exactly 1 offender, `tools/probe.sh:1`; the workflow is exempt.

## Final runs

`HARNESS_AGENT_TYPE` and `CLAUDE_PROJECT_DIR` were unset for all of these.

- Each of the four files exits 0 with 0 FAIL lines.
- `test-lead-stop-and-wake.py --self-check` passes.
