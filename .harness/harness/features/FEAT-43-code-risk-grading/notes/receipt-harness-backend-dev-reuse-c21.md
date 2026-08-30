# REUSE angle — FEAT-43 validate-final-simplify-c21

## Headline
No new reuse violations found in production code. One genuine finding: the SEC-01 remediation
added a fifth spelling of "init a scratch git repo" boilerplate in `test-validate-digest.py`,
extending the already-carried B5. `must_fix: []` — this is a backlog row, not a gate.

## Scope actually read
Diff `94383e6..17106762` (the three in-scope commits `a643e44`, `34a49c4b`, `17106762`, base
`94383e6` being the commit immediately prior to the first of the three) restricted to the ten
`bin/*.py` files and `harness-code-review/SKILL.md`:
- `code_grade.py` — full hunk (`_child_qualname`/`_records` refactor, `_next_paths` extraction).
- `check-plan-routes.py` — full hunk (`_owner_root`/`_manifest_deviation` extraction from
  `resolution_manifest`).
- `gate_policy.py` — full hunk (`_load_config`/`_require_gates`/`_resolve_gate`/`_validate_suites`
  extraction).
- `code-grade.py` — full hunk: `_blocks`/`_severity` extraction, `_run_name_status_diff`/
  `_name_status_entries`/`_is_changed_python` extraction.
- `validate-digest.py` — the CR-01/SEC-01 hunks: schema note (line ~932), the `n_a` branch
  (~1136-1154), and the SEC-01 wave-4 block (~596-713: `_default_branch_or_none`,
  `_merge_base_or_none`, `_derived_reviewed_python_change`).
- `test-code-grade.py` — the `SELF_GRADED_FILES`/`SELF_GRADING_ALLOWLIST`/`check_self_grading`/
  `_check_self_graded_file` addition (~184-311), and the `main()` decomposition into
  `check_fixtures`/`check_nested_qualnames`/`check_direction_pairs`.
- `test-code-grade-cli.py` — `test_review_skill_states_severity_vocabulary` (290-303) and
  `test_diff_paths_complexity` (306-315).
- `test-check-plan-routes.py` — the `case_20` rewrite: `_logical_lines_shell`,
  `_logical_lines_python` (tokenize-based), `logical_lines` dispatcher, `_assert_logical_lines_
  fixture`, `_scan_file`, `_report_scan_result`, `_scan_all_files` (full hunk, ~1143-1272).
- `test-validate-digest.py` — the SEC-01 wave-4 addition: `_git_quiet`, `_init_test_repo`,
  `_commit_file`, `make_derived_base_repo`, `_assert_derived_accepts`/`_rejects`,
  `check_derived_base_range`, `check_unresolvable_default_branch`, `make_orphan_review_repo`,
  `check_no_merge_base` (~1926-2100+), plus the `check_review_policy`/`check_code_grade_state`/
  `check_reviewed_range`/`check_review_sha_binding*` signature changes threading `feature_dir`
  through (94383e6-era → CR-01/SEC-01 era).
- `harness-code-review/SKILL.md` — the severity-vocabulary paragraph (lines 60-70 region).
- `test-gate-policy.py` — no diff in this range (confirmed via `git diff --stat`); not reviewed
  further.

## Findings

### C21-reuse-1 — fifth spelling of "init a scratch git repo" (extends carried B5)
- **File/line**: `test-validate-digest.py:1926-1943` (`_git_quiet`, `_init_test_repo`,
  `_commit_file`).
- **Summary**: SEC-01's `make_derived_base_repo` fixture reintroduces the same three-line
  "git init + configure identity + commit" boilerplate that `test-code-grade-cli.py:30-44`
  (`git()`/`make_repo()`) already carries as a named helper, and that B5 already flags as
  duplicated across `test-code-grade.py`/`test-code-grade-cli.py`. This diff adds a fifth,
  differently-spelled copy in a third file (`_git_quiet` vs `git`, `-b main` vs bare `init`,
  explicit `os.makedirs` vs implicit).
- **Concrete cost**: a shared bug in the git-fixture pattern (e.g. an old `git` needing `-b main`
  swapped for `git symbolic-ref HEAD refs/heads/main`, or a CI image lacking a default branch
  name) must now be fixed in five places across three files; the next reader who needs a scratch
  repo has five near-identical examples to choose from with no canonical one, and is as likely to
  write a sixth as reuse an existing one.
- **Alternative**: extract a shared `bin/test_support.py` (or similar) carrying one
  `init_test_repo(root, default_branch="main")` + `commit_file(...)`, imported by all three test
  files. This is exactly what B5 already recommends — this finding is evidence the debt grew
  during this remediation round, not a new root cause.
- **Disposition**: backlog row, cited alongside B5. Not a `must_fix` — extracting a shared test
  support module is new scope (a new file, touching three test files) that this pass's one-fix
  ceiling and read-only build-side apply model are not suited to attempt safely this late before
  the pin, and B5 already tracks the underlying debt.

### Everything else checked: no violation
- **CR-02 blocking predicate** (`grade < bar and grade != 2`): single authority. `code-grade.py`
  defines it once as `_blocks(grade, bar)` (line 56) and both `_severity` (line 60) and `_status`
  (line 166) call it. Grepped every `bin/*.py` file for `grade < bar`, `grade != 2`, `_blocks(` —
  the only other spelling is in `test-code-grade-cli.py:218`
  (`failures += expect(grade < bar, below_bar, ...)`), which is a test assertion re-deriving the
  expected boundary independently to test the production code, the normal shape for a test, not a
  second production authority. `code_grade.py` (the AST engine) has no bar/predicate logic at all
  — confirmed by grep, zero matches for `bar`.
- **Test/production bar classification**: single authority. `check_self_grading` in
  `test-code-grade.py:270` calls `code_grade_cli._is_test(repo_root, relative)` — a
  `spec_from_file_location` import of `code-grade.py` bound to the name `code_grade_cli`
  (`test-code-grade.py:16-18`) — rather than hardcoding a second file-pattern list. `_is_test`
  itself (`code-grade.py:47-52`) is defined exactly once, reading `test_kinds` from
  `harness.json`. Confirmed no second hardcoded test-path list exists anywhere in `bin/`.
- **SEC-01 derived-base range vs `reviewed_python_change`/`resolve_reviewed_commit`**: no
  restated git-range or path-filtering logic. `_derived_reviewed_python_change`
  (`validate-digest.py:638-713`) calls `resolve_reviewed_commit` to resolve `review_sha`
  (line 645) and, once it has computed `base_oid..review_oid`, calls the existing
  `reviewed_python_change(f"{base_oid}..{review_oid}")` (line 713) rather than re-implementing
  the "does this range touch a `.py` file" check. The genuinely new code is
  `_default_branch_or_none` and `_merge_base_or_none` — thin `git symbolic-ref`/`git merge-base`
  wrappers with no prior equivalent in this file (grepped `merge-base`, `symbolic-ref`: only
  these two new definitions and their doc-comment references). The `n_a` validate() branch
  (line 1137-1155) still calls `reviewed_python_change(seen.get("reviewed"))` first for its shape
  check, discarding the boolean and using only `shape_error` — this is the deliberate double
  `git diff` already ruled settled in the dispatch's contract, not new duplication.
- **SEVERITY / `code_grade` vocabulary across 4 surfaces**: not a reuse violation in the
  importable-code sense — `SKILL.md` is prose, not code, so it cannot import the enum. The
  vocabulary is defined once in code: `code-grade.py`'s `_severity`/`_text` produce the
  `SEVERITY:`/`RESULT:` text and `severity`/`grade` JSON fields; `validate-digest.py`'s schema
  (line 932) states the `code_grade` enum `{"pass","fail","grade_2","n_a"}` once, as a Python set
  literal. `SKILL.md` restates the surface words in prose for the human reviewer, and
  `test_review_skill_states_severity_vocabulary` (`test-code-grade-cli.py:290-303`) pins that
  `SKILL.md` contains those exact substrings — but the test only checks one direction (the doc
  names the words the tool emits); it does not cross-check that the tool's actual output equals
  what `SKILL.md` claims. So editing `code-grade.py`'s literal `"SEVERITY: "` wording would not be
  caught by this test, and `SKILL.md` would go stale silently. This is a real lockstep-edit risk,
  but it is not new to this remediation — the pre-existing grade-1/grade-2 wording in `SKILL.md`
  already had this shape before UI-01 extended it to bar-relative severity. I read this as an
  ALTITUDE question (single-authority-with-many-readers) more than a REUSE one (nothing here is
  importable code being re-typed), and it is outside my angle's mandate to file as a REUSE
  finding; noting it for the ALTITUDE reader's benefit.
- **Q1 — `SELF_GRADING_ALLOWLIST` (37 entries)**: sound, self-invalidating record, not a growing
  exemption surface that will rot silently. Each entry is a `(filename, qualname): grade` pin,
  and `check_self_grading`'s closing assertion (`test-code-grade.py:311-312`,
  `matched_allowlist == set(SELF_GRADING_ALLOWLIST)`) requires every entry to have matched a real
  below-bar record at exactly that grade on every run — a rename, a fix, or a further regression
  all break the test loudly rather than the exemption quietly outliving the code it excused. This
  is the opposite of a derivable-but-hand-copied list (which would rot silently): it is closer to
  a golden-file/snapshot assertion, which is a reasonable shape for pinning known debt. The
  genuine growth risk is size, not staleness: 37 entries in one dict is already hard to audit by
  eye, and nothing stops a 38th sneaking in without a comment discipline; the two-block
  structure (SC-15-cited items with a review-note pointer vs. pre-FEAT-43 legacy items justified
  by a `--base 7ccfae8..a643e44` methodology note) at least separates "we decided this" from
  "we inherited this," which is the right shape to keep growth auditable. No apply — this is a
  read, not a code change.

## Carried findings encountered, not re-reported
- B6 (two near-identical git subprocess wrappers, `code-grade.py:_git_text` — actually
  `_run_name_status_diff`/`_name_status_entries` — vs `code_grade.py:_git_output`): observed the
  same shape in this diff's `code-grade.py`/`code_grade.py` hunks; cited as B6, not re-filed.
- B4 (blank-line spacing near `commit_oid`/`_result`): out of REUSE's scope; not assessed here.

## Suite results (real, run from worktree root)
```
python3 .claude/skills/harness/bin/test-code-grade.py        -> PASS, exit 0
python3 .claude/skills/harness/bin/test-code-grade-cli.py    -> PASS, exit 0
python3 .claude/skills/harness/bin/test-gate-policy.py       -> PASS (all `ok`), exit 0
python3 .claude/skills/harness/bin/test-check-plan-routes.py -> ALL PASS, exit 0
python3 .claude/skills/harness/bin/test-validate-digest.py   -> ALL PASSED, exit 0
```

## Working tree
```
$ git -C <worktree> status --porcelain
 M .harness/harness/features/FEAT-43-code-risk-grading/STATE.md
 M .harness/harness/features/FEAT-43-code-risk-grading/feature.json
?? .harness/harness/features/FEAT-43-code-risk-grading/answers/Q6-cycle-20-remediation-authorization.md
?? .harness/harness/features/FEAT-43-code-risk-grading/answers/Q7-cycle-25-preemptive-authorization.md
?? .harness/harness/features/FEAT-43-code-risk-grading/answers/Q8-sec01-remedy-ruling.md
?? .harness/harness/features/FEAT-43-code-risk-grading/notes/qa-regate-c18.md
?? .harness/harness/features/FEAT-43-code-risk-grading/notes/receipt-harness-backend-dev-validate-remediate-c14-eng-s1.md
?? .harness/harness/features/FEAT-43-code-risk-grading/notes/receipt-harness-backend-dev-validate-remediate-c14-eng-s1b.md
?? .harness/harness/features/FEAT-43-code-risk-grading/notes/receipt-harness-backend-dev-validate-remediate-c14-eng-s2.md
?? .harness/harness/features/FEAT-43-code-risk-grading/notes/receipt-harness-backend-dev-validate-remediate-c14-eng-s3.md
?? .harness/harness/features/FEAT-43-code-risk-grading/notes/receipt-harness-backend-dev-validate-remediate-c14-eng-s3b.md
?? .harness/harness/features/FEAT-43-code-risk-grading/notes/receipt-harness-backend-dev-validate-remediate-c14-eng-s5.md
?? .harness/harness/features/FEAT-43-code-risk-grading/notes/receipt-harness-backend-dev-validate-remediate-c18-eng.md
?? .harness/harness/features/FEAT-43-code-risk-grading/notes/receipt-harness-backend-dev-validate-sec01-c19-eng.md
?? .harness/harness/features/FEAT-43-code-risk-grading/notes/receipt-harness-dev-ops-simplification-c21.md
?? .harness/harness/features/FEAT-43-code-risk-grading/notes/receipt-harness-dev-ops-validate-remediate-c14-eng-s4.md
?? .harness/harness/features/FEAT-43-code-risk-grading/notes/receipt-harness-dev-ops-validate-remediate-c14-eng-s6.md
```
All of these are pre-existing feature-notes/state artifacts from prior/concurrent runs, unrelated
to my read (I wrote only this receipt file, listed above as
`notes/receipt-harness-backend-dev-reuse-c21.md`, which had not yet been created when this status
was captured — it appears once I write it, per the write below). No file under
`.claude/skills/harness/bin/` or `.claude/skills/harness-code-review/` is modified.
