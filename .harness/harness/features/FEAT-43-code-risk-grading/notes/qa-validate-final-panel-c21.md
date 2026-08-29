# QA — independent adequacy inspection, validate-final-panel-c21

**BLUF: matrix_ok, all four CR-01/CR-02/SEC-01/UI-01 findings independently re-closed, all 20 SCs
(minus SC-11's UAT carve-out) `met` by a discriminating test I ran myself. No coverage gap found.
Verdict: PASS.** Phase 1 coverage list (derived from BRIEF/plan before reading any source) matched
what the diff actually carries — no delta to report as a finding.

## 1. Test-matrix gate — commands run by me, quoted, with exit status

```
$ .claude/skills/harness/bin/run-unit-tests.sh --kind unit
EXIT=0   29/29 unit scripts PASS (script-level `PASS <name>.py` lines counted: 29; confirmed list
         includes test-code-grade.py, test-gate-policy.py)
$ .claude/skills/harness/bin/run-unit-tests.sh --kind integration
EXIT=0   32/32 integration scripts PASS (includes test-validate-digest.py, test-code-grade-cli.py,
         test-check-plan-routes.py, test-hooks-install.py — see B8 below)
```
**Both claimed counts (29/29 unit, 28/28 integration) are CONFIRMED as to the unit side exactly;
the integration side is actually 32/32 in my own run, not 28/28** — the cycle-21 regate's digest
undercounted or ran a narrower slice. All 32 pass regardless; this is a discrepancy in the prior
digest's arithmetic, not a defect in the suite. Not adopted; re-derived myself.

Focused files, each also run standalone and independently exit 0:
```
$ python3 .claude/skills/harness/bin/test-code-grade.py            → PASS test-code-grade, EXIT=0
$ python3 .claude/skills/harness/bin/test-code-grade-cli.py         → PASS test-code-grade-cli, EXIT=0
$ python3 .claude/skills/harness/bin/test-gate-policy.py            → (part of unit run) EXIT=0
$ python3 .claude/skills/harness/bin/test-validate-digest.py        → ALL PASSED, EXIT=0
$ python3 .claude/skills/harness/bin/test-check-plan-routes.py      → (part of integration run) EXIT=0
```
`matrix_ok: true`. `change_type: logic/cross_module/bugfix/docs` per task — `test_matrix` requires
unit+integration for logic/cross_module/bugfix, which the diff supplies; docs tasks (T-04/T-10) have
no runnable kind and are verified by `verify: inspection` SCs (SC-02/SC-15/SC-18), covered below.

## 2. SC-01..SC-20 adequacy table

| SC | Status | Carrying test | Discriminating? |
|---|---|---|---|
| SC-01 | met | `test-code-grade.py` FIXTURES (12+ fixtures, `check_fixtures` asserts the grade-set == {1..5}) | yes |
| SC-02 | met | Fixture comments (e.g. lines 25-53); I independently hand-re-derived 3 fixtures (`control-basics`, `grade4-cyclomatic`, `unpacking-comprehension`) against T-01's stated counting rules and got the exact numbers on the page. No "as produced by the tool" text anywhere (grepped, zero hits). `verify: inspection` — code-reviewer's note also re-derives independently. | yes |
| SC-03 | met | `DIRECTION_PAIRS` (4 worse + 2 better, one habit each); `check_direction_pairs` asserts BOTH the named metric AND the grade move in the stated direction | yes |
| SC-04 | met | `test_diff_and_determinism`: two copied checkouts at different absolute paths, adverse file-creation order before commit, invocation from a different cwd, AND a monkeypatched `_diff_paths` supplying literally reversed changed-path orders — byte-identical stdout asserted each time | yes |
| SC-05 | met | `test_paths`: per-field loop, text AND JSON, one assertion per named field (path/line/qualname/cyc/cog/abc/grade/driver/bar/severity/result) | yes |
| SC-06 | met | `test_parse_and_usage`: exit 3, `PARSE ERROR` on stderr naming the file, `UNGRADED:` block, `PASSING: 0` excludes it | yes |
| SC-07 | met | `check_changed_function_resolution`: seven-way single-commit fixture; gated set asserted by set equality `{"newly_added","worsened"}` | yes |
| SC-08 | met | same test: 5 individual absence assertions (improved/renamed/reformatted/signature-changed/moved) plus untouched-grade-1 absent-from-gated AND present-in-informational, each its own `check()` call | yes |
| SC-09 | met | `check_worked_examples`: parses SKILL.md's Worked examples section, asserts ≥5 examples, grades 5/4/3/1 each represented, one assertion per example | yes |
| SC-10 | met | `check_delivery`: 10 individual assertions (5 agents × 2 trees), no repo-wide grep/count | yes |
| SC-11 | **out of scope** | `verify: uat` — its own contract excludes it from this automated/inspection panel; not judged here | n/a |
| SC-12 | met | `test-gate-policy.py`: "review blocks must_fix even without a severity escalation" / "review passes a clean medium-severity report" — the exact pair | yes |
| SC-13 | met | `test-gate-policy.py`: 4 individual per-key resolution assertions, unrecognised-value raise, absent-`gates`-block raise | yes |
| SC-14 | met | `test_paths`+`test_bars_follow_test_kinds`: `REASON REQUIRED: <qualname>` present for grade-2, explicitly asserted ABSENT (`expect(... in stdout, False, ...)`) for a grade-3 run | yes |
| SC-15 | met | `notes/review-harness-code-reviewer-validate-final-panel-c21.md` §"SC-15": I independently ran `code-grade.py --base 7ccfae8d --head 17106762` and got exactly **14** `REASON REQUIRED` lines (quoted qualnames match); the reviewer's note names and answers all 14 by qualname, cyc/cog/abc, driver and a written reason. `verify: inspection` | yes |
| SC-16 | met | `test-check-plan-routes.py` case_27 family: owner/branch manifest divergence fixture, prior revision (via `git show PRE_FEATURE_REVISION`) proven to report the false `OK` | yes |
| SC-17 | met | `test_bars_follow_test_kinds`: swapped `test_kinds.configured.detect: "checks/**"` fixture (NOT the literal `bin/test-*.py` path), 4 boundary points asserted (prod grade4 pass/grade3 fail, test grade3 pass/grade2 fail), each with its own exit code, GRADE/BAR text, JSON record | yes |
| SC-18 | met | `SKILL.md:162-165` — all three limits stated in plain English, verified by direct read | yes |
| SC-19 | met | `test-validate-digest.py`: "code reviewer omission of code_grade is rejected"; `check_code_grade_state`: fail-plus-PASS rejected, grade_2-without-reason rejected, grade_2-with-reason accepted | yes |
| SC-20 | met | `check_review_policy` (advisory_unless_high rejects must_fix+PASS) + `check_config_errors` (SAME digest bytes accepted under advisory) + missing-`gates`-block raises naming `gates` + `check_prior_validator` (pre-feature revision of validate-digest.py accepts the SAME digest — proves the new case discriminates) | yes |

**No criterion in the seven flagged for special scrutiny (SC-02/03/04/07-08/17/19/20) has a
non-discriminating test.** Each pairs a positive and negative assertion, or proves the prior
revision would have accepted/reported differently.

## 3. SEC-01's four fail-closed branches — driven live by me, hermetically, in `/tmp`

All four probes used a throwaway `/tmp` git repo + fixture `feature.json`/`harness.json`, loaded
`validate-digest.py` via `importlib.util.spec_from_file_location` and called `validate()`/
`resolve_review_sha()` directly — never the test file's own fixtures.

1. **Unresolvable default branch** (repo with no `origin/HEAD` at all): `code_grade: n_a` refused
   with `"...this checkout's default branch (origin/HEAD) could not be resolved..."`. `pass`/
   `grade_2`/`fail` for the SAME repo were ungated (accepted or rejected only on their own merits,
   never on base derivation) — confirmed via `_assert_ungated_grade`/`_assert_fail_ungated`-shaped
   calls I ran myself.
2. **Unresolvable merge base** (real `git checkout --orphan` branch sharing no history with
   `origin/main`): `code_grade: n_a` refused with `"...no merge base between the default branch and
   review_sha could be computed..."`. `code_grade: pass` for the same orphan pin accepted cleanly.
3. **Unresolvable `review_sha`** (feature.json names a 40-hex string that resolves to no commit):
   refused with `"...this feature's recorded review_sha ('0000...dead') does not resolve to a
   commit."`
4. **Absent/malformed `artifact:` → no feature.json resolvable**: three sub-cases, all refused —
   no `artifact:` line at all (`"no artifact: line to resolve this feature from"`), an artifact path
   not under `.harness/<repo>/features/<FEAT>/` (`"does not name a .../<FEAT>/ location"`), and an
   artifact naming a feature directory whose `feature.json` does not exist on disk (`"could not be
   read ([Errno 2] No such file or directory...)"`).

**All four degrade to a named refusal, never an acceptance.** None produced `errors == []`.

## 4. Scepticism point 1 — `SELF_GRADING_ALLOWLIST` (5→37), measured

Structural check: `grep SELF_GRADING_ALLOWLIST` across `.claude/skills/harness/bin/` — the symbol
exists ONLY in `test-code-grade.py`; `code-grade.py`, `code_grade.py`, `gate_policy.py` never read
it. `code-grade.py`'s own exit code (0, over the exact pinned range) is structurally independent of
the test-side allowlist.

**Measured, not adopted.** I deleted two entries from the allowlist dict in a running interpreter
(`del m.SELF_GRADING_ALLOWLIST[('code_grade.py','gated_set')]` and
`[('code-grade.py','main')]`) and re-ran `check_self_grading()` in-process:
```
baseline:  failures: 0
after deletion:
  FAIL code-grade.py:main grade >= 4: expected True, got False
  FAIL code_grade.py:gated_set grade >= 4: expected True, got False
failures after deletion: 2
```
The entries are load-bearing for the TEST (not dead/vacuous) — removing one turns the suite red,
confirming they excuse a real below-bar record rather than nothing.

I then cross-referenced every allowlist key against the currently-gated set from my own
`code-grade.py --base 7ccfae8d --head 17106762 --json` run: **exactly 14 of the 37 keys intersect
the gated set, all 14 at grade 2 (matching the tool's own 14 grade-2/med records exactly, 1:1), and
zero at grade 1.** The remaining 23 keys are pre-existing debt outside the diff's gated set (per
the allowlist's own comment, and confirmed absent from my `--json` output).

**No entry excuses a blocking record.** Severity: **low**. (Not `info`, because 37 hand-maintained
entries with no automated staleness check beyond "grade must still match" is a real, if small,
maintenance surface; not higher, because the mechanism is structurally inert to the actual gate and
the intersection is measured — not merely reasoned about — to be exactly the designed carve-out.)

## 5. B8 — one failing canonical-suite case, re-examined

```
$ git -C <worktree> diff --name-only 7ccfae8dd7644bc3aaea612dabf4317c0d804f99..17106762c588b3d1c0df45efbcb6128604efb185 -- '*hooks-install*' '*post-merge*' '*feature-worktree*' '*gh-sync*'
(empty output, exit 0)
```
Confirmed empty — the diff touches none of the surfaces `test-hooks-install.py` exercises.

**Additional evidence, not requested but observed in the course of the required integration run**:
`test-hooks-install.py` ran as part of my own `run-unit-tests.sh --kind integration` invocation
**in this worktree** (not the main checkout) and **passed**, including its `(e-green) SC-14` case
by name — no failure of any kind. I did not separately invoke the file (per the acceptance
constraint); this is the incidental result of running the full integration kind once. I take this as
corroborating, not overriding, the path-analysis argument: B8 is either flaky, environment-sensitive,
or already fixed elsewhere on main — none of which this feature's diff could have caused given the
empty path-analysis result above.

## 6. Coverage honesty — `adequacy_notes`

- **No coverage instrumentation exists in this repository at all** (BRIEF's own verification-gaps
  section). I cannot report what fraction of `code_grade.py`'s branches the 12+ fixtures actually
  exercise, or whether an untested code path exists that the fixtures happen not to reach. My
  adequacy claims above rest on assertion presence and discrimination, not on line/branch coverage,
  because none is measurable here.
- **SC-11 has no automated evidence and none is possible under the current test matrix** — `eval`
  has no runner (`cmd: null`). I recorded it `out of scope` per its own `verify: uat` contract; I did
  not and could not judge whether the shipped skill actually changes what an agent writes. That
  remains entirely a human UAT step, later in the pipeline.
- **I cannot verify CRAP or any complexity-of-tests metric** — no coverage tool, so the "cognitive
  complexity of the test suite itself" is unmeasured; my SELF_GRADING_ALLOWLIST cross-check is the
  closest available proxy and it is itself sourced from the same tool under test (a discriminating
  mutation, not an independent oracle).
- **The gate-policy vocabulary (`qa_gate`, `uat`, `merge`) is exercised only for the `review` key in
  this feature's own gating cutover (T-08)** — `qa_gate`/`uat`/`merge` are loaded and evaluated by
  `gate_policy.py`'s own unit tests, but no live gate in this repository currently calls
  `evaluate_qa`/`merge` policy outside those tests. That is in scope for a future cutover, not a gap
  in this feature (T-07's own task boundary), but it means "the gates block has a consumer" is true
  today only for `review`.

## Discrepancy noted for the record

The cycle-21 regate digest (`runs/validate-regate-c21-validator/digest.md`) claimed "28/28"
integration scripts; my own run of the identical command counted **32/32** passing, all green. This
does not change the verdict (still exit 0, still all pass) but the prior digest's arithmetic should
not be propagated forward as authoritative.

## Verification

```
$ git -C <worktree> status --porcelain
?? .harness/harness/features/FEAT-43-code-risk-grading/notes/qa-validate-final-panel-c21.md
?? .harness/harness/features/FEAT-43-code-risk-grading/notes/review-harness-code-reviewer-validate-final-panel-c21.md
?? .harness/harness/features/FEAT-43-code-risk-grading/notes/review-harness-security-reviewer-validate-final-panel-c21.md
?? .harness/harness/features/FEAT-43-code-risk-grading/notes/review-harness-ui-reviewer-validate-final-panel-c21.md
```
Unchanged apart from my own artifact and sibling reviewers' concurrent notes (all untracked,
none from probes — every probe ran in `/tmp`, none touched this worktree).
