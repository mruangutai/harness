# Consolidated verification — FEAT-43 code-risk-grading remediation (C14 eng-s4)

## VERDICT: FAIL

`test-check-plan-routes.py` fails when run against the fully combined tree (all four members'
edits present), exit 1, `1 FAILURE(S): ['case_20_validate_digest_py_probes_the_manifest']` — a
suite that s1's own receipt reports as `ALL PASS exit 0` in isolation. This is exactly the class of
regression this consolidated pass exists to catch (task section A). Everything else checked —
CR-01 grades, CR-02/UI-01 vocabulary, SEC-01 bypass closure, and tree cleanliness modulo the finding
below — is sound. The one failing gate is enough to withhold PASS.

## A. Five focused suites + adapter check

| suite | result | exit |
|---|---|---|
| test-code-grade.py | `PASS test-code-grade` | 0 |
| test-code-grade-cli.py | `PASS test-code-grade-cli` | 0 |
| test-gate-policy.py | all `ok` lines, no `not ok` | 0 |
| **test-check-plan-routes.py** | **`1 FAILURE(S): ['case_20_validate_digest_py_probes_the_manifest']`** | **1** |
| test-validate-digest.py | `ALL PASSED.` | 0 |
| sync-agent-adapters.py --check | (no output) | 0 |

### The case_20 failure — root cause, verified

`case_20` scans every `bin/*.py` source text with a **naive bracket-depth joiner**
(`depth += line.count("(") + line.count("[") - line.count(")") - line.count("]")`, no string-literal
awareness) to find multi-line filesystem-root probes, then requires any probe naming `.harness` to
also name `team-config.yaml` (the manifest). `validate-digest.py` line 283,
`_QUOTE_STARTS_AFTER = set(",:[{ \t") | {None}` — pre-existing code, **untouched by any of the four
members' diffs** (`git diff` on that region is empty) — contains an extra unmatched `[` inside a
string literal. The joiner never recovers: I reproduced it directly and it merges everything from
line 283 to EOF into one 48,393-character "logical line", which does contain a later `.harness`
mention but never `team-config.yaml` (confirmed: `grep -c team-config.yaml validate-digest.py` = 0
matches anywhere in the file, including its comments). Ground truth: `validate-digest.py` contains
**zero** occurrences of any of the six root-probe predicates (`os.access(`, `os.path.isdir(`,
`os.path.isfile(`, `os.path.exists(`, `os.stat(`, `Path(`) anywhere — there is no real root probe in
this file to be non-compliant. I confirmed the false positive is new: running the identical joiner
against the pin's `validate-digest.py` (`git show 94383e6:...`, 1122 lines) finds nothing — the same
unbalanced string exists there too, but the file was short enough that the runaway merge apparently
terminated (via other compensating brackets) before ever reaching a `.harness` mention. S3b's ~268
added lines changed what the merge sweeps up, which is what flips it. **This is a pre-existing
fragility in `test-check-plan-routes.py`'s own text-scanning heuristic, not a defect in
`validate-digest.py`** — but it is a real, reproducible suite failure in the combined tree today,
and none of the four members' isolated runs could have seen it since it only manifests once
`validate-digest.py` crosses a size threshold their individual diffs jointly create.

## B. CR-01 — six functions + every named helper, grade 4+

Ran `code-grade.py <file>` in paths mode per file (non-zero exit on `check-plan-routes.py` and
`validate-digest.py` is expected — pre-existing untouched functions below bar — acceptance is
per-qualname, not exit status).

| qualname | was | now |
|---|---|---|
| `resolution_manifest` | 3 | **5** |
| `_diff_paths` | 3 | **5** |
| `_records.collect` | 3 | **4** |
| `_changed_python_files` | 3 | **4** |
| `load_policy` | 3 | **5** |
| `evaluate_qa` | 3 | **4** |

All six now clear the bar. Every named helper also graded, all 4+:
`_child_qualname`(5) `_next_paths`(5) — `_load_config`(5) `_require_gates`(5) `_resolve_gate`(4)
`_validate_suites`(4) — `_owner_root`(4) `_manifest_deviation`(4) — `_blocks`(5) `_severity`(5)
`_run_name_status_diff`(5) `_name_status_entries`(4) `_is_changed_python`(5) —
`_resolve_feature_dir`(5) `_read_review_sha`(4) `_read_feature_branch`(4)
`_current_branch_or_none`(4) `_branch_corroboration_error`(5) `resolve_review_sha`(5)
`_parse_reviewed_range`(4) `code_grade_bound_to_review`(4) `_missing_field_default_hint`(5).
No helper below 4. No absentees (none claimed-but-missing) — cross-check against receipts confirms
no lost edits here.

## C. CR-02 / UI-01 — one canonical spelling, live on all three surfaces

1. **Tool.** The out-of-repo route was rejected: `code-grade.py` refuses paths outside the repo
   (`error: path outside repository`, exit 2) both in text and `--json` mode — took the documented
   fallback. `test-code-grade-cli.py::test_bars_follow_test_kinds` (part of the passing suite in §A)
   grades `src/grade-three.py` (grade 3, bar 4, below bar) and asserts `SEVERITY: high` present in
   stdout and `record["severity"] == "high"` in `--json`; a passing bar (`grade-four.py`,
   `checks/grade-three.py` at its configured bar 3) asserts `SEVERITY:` **absent**. Verified by
   reading the assertions directly at `test-code-grade-cli.py:207-234`.
2. **Guidance.** `harness-code-review/SKILL.md:64-71`: "a grade-3 production function below the
   grade-4 production bar blocks identically, and the tool marks it the same way — `SEVERITY: high`
   in its report (JSON: `"severity": "high"`) and `RESULT: FAIL` … report `code_grade: fail` for
   it… grade 2 never blocks the build … and is reported as `code_grade: grade_2`, never `fail`."
3. **Gate.** `validate-digest.py:822-825`: comment states the tool reports this "at severity `high`"
   and spells the digest field "`code_grade: fail`", then the schema line literally sets
   `"code_grade": {"pass", "fail", "grade_2", "n_a"}`.
4. **Judgement.** Yes — an author who reads only the tool's `SEVERITY: high` / `RESULT: FAIL` output
   and the SKILL.md passage above can write `code_grade: fail` correctly without opening
   `validate-digest.py` or `code-grade.py` source; the SKILL.md passage names both the tool's exact
   text/JSON tokens and the digest's exact enum value in one place. One canonical spelling, shared.

## D. SEC-01 — bypass reproduced and closed (temp digests outside repo, deleted after)

Built three digests in `/tmp/sec01check/` (outside the repo tree), ran each through
`validate-digest.py harness-code-reviewer <file>`, deleted the temp dir afterward.

1. **Original bypass, base-of-range self-consistent pair**
   (`reviewed: "7ccfae8dd7644bc3aaea612dabf4317c0d804f99..7ccfae8dd7644bc3aaea612dabf4317c0d804f99"`,
   artifact naming FEAT-43's own notes/): `VERDICT: BLOCKED (contract violation)` — `"reviewed head
   '7ccfae8dd7644bc3aaea612dabf4317c0d804f99' does not resolve to this feature's pinned review_sha
   (94383e671e51f95d142f3220f97c8e453721d516) — write the range that ends at review_sha
   (feature.json), not a convenient no-op."` exit 1. Was `digest ok`/exit 0 before the fix.
2. **Cross-feature forgery** (`reviewed: "9f87c48..9f87c48"`, FEAT-06's own honest `review_sha`,
   artifact naming FEAT-06's notes/): `VERDICT: BLOCKED (contract violation)` —
   `"code_grade cannot be bound to review_sha: this feature's recorded branch ('main') does not
   match the current checkout's branch ('feat/FEAT-43-code-risk-grading') — the digest's artifact:
   line must name the feature actually under review in this checkout, not another shipped feature's
   notes/ path."` exit 1 — names both branches as specified.
3. **Honest digest** (`reviewed: "94383e671e51f95d142f3220f97c8e453721d516..94383e671e51f95d142f3220f97c8e453721d516"`,
   artifact naming FEAT-43's own notes/): `digest ok`, exit 0. The gate discriminates rather than
   rejecting everything.
4. `harness-security-reviewer` and `harness-ui-reviewer` digests (no `code_grade`/`reviewed` field
   at all — legal for those personas) both return `digest ok`, exit 0: unaffected, as expected since
   the SEC-01 binding checks gate on `raw_persona == "harness-code-reviewer"` only
   (`validate-digest.py:819,852,1020`).

## E. Tree state

- `git rev-parse HEAD` = `0666c01a07a844ceb4a2bdfa7504ce4ef74536fb`, **not** the expected pin
  `94383e671e51f95d142f3220f97c8e453721d516`. **Finding, not a blocker on its own**: `0666c01` is
  one bookkeeping commit *ahead* of the pin (`git show --stat` confirms it touches only
  `.harness/harness/features/FEAT-43-code-risk-grading/**` — STATE.md, feature.json, notes/ — zero
  source files), and its own commit message states `review_sha stays
  94383e671e51f95d142f3220f97c8e453721d516`. `git merge-base --is-ancestor 94383e6 HEAD` = yes;
  reverse = no. Source-level pin integrity holds; only the literal `HEAD == pin` equality in the
  contract is stale relative to a prior orchestrator bookkeeping commit that predates this dispatch.
  Reporting it because the contract states it as a hard check.
- `git status --porcelain` — full output:
  ```
   M .claude/skills/harness-code-review/SKILL.md
   M .claude/skills/harness/bin/check-plan-routes.py
   M .claude/skills/harness/bin/code-grade.py
   M .claude/skills/harness/bin/code_grade.py
   M .claude/skills/harness/bin/gate_policy.py
   M .claude/skills/harness/bin/test-code-grade-cli.py
   M .claude/skills/harness/bin/test-code-grade.py
   M .claude/skills/harness/bin/test-validate-digest.py
   M .claude/skills/harness/bin/validate-digest.py
   M .harness/harness/features/FEAT-43-code-risk-grading/STATE.md
   M .harness/harness/features/FEAT-43-code-risk-grading/feature.json
  ?? .harness/harness/features/FEAT-43-code-risk-grading/answers/Q6-cycle-20-remediation-authorization.md
  ?? .harness/harness/features/FEAT-43-code-risk-grading/notes/receipt-harness-backend-dev-validate-remediate-c14-eng-s1.md
  ?? .harness/harness/features/FEAT-43-code-risk-grading/notes/receipt-harness-backend-dev-validate-remediate-c14-eng-s1b.md
  ?? .harness/harness/features/FEAT-43-code-risk-grading/notes/receipt-harness-backend-dev-validate-remediate-c14-eng-s2.md
  ?? .harness/harness/features/FEAT-43-code-risk-grading/notes/receipt-harness-backend-dev-validate-remediate-c14-eng-s3.md
  ?? .harness/harness/features/FEAT-43-code-risk-grading/notes/receipt-harness-backend-dev-validate-remediate-c14-eng-s3b.md
  ```
  Every entry is one of the seven intended source files or feature bookkeeping under
  `FEAT-43-code-risk-grading/**`. **No scratch file, no `.orig`/`.rej`, no `__pycache__`.** Note
  `test-gate-policy.py` and `test-check-plan-routes.py` are **not** modified — the members added no
  new cases to those two suites; not itself a problem since both still ran (§A).
- `git diff --stat`: 11 files changed, 793 insertions(+), 130 deletions(-) (source: 369 ins/55 del
  across the five bin/ files + SKILL.md; rest is bookkeeping/tests).
- **Reverted-file check**: `git diff -- code-grade.py` shows **both** the severity work
  (`_blocks`, `_severity`, and `_record`'s use of them via
  `_blocks(record["grade"], record["bar"])`) **and** the `_diff_paths` decomposition
  (`_run_name_status_diff`, `_name_status_entries`, `_is_changed_python`) present in the same diff.
  Nothing lost from the reported `git checkout --` incident. Per-file diff sizes (§B/§E) match the
  scale each receipt claims; no unexpectedly empty or truncated diff found.

## Recommendation

Loop back to remediation for `test-check-plan-routes.py`'s `case_20` only — either widen the
joiner's exemption list (it already special-cases `check-state.sh`; this is the same shape of
problem, a string literal defeating a source-text heuristic) or teach `logical_lines` to skip
bracket characters inside quoted strings. Nothing else in this dispatch needs rework: CR-01, CR-02/
UI-01, SEC-01 and tree hygiene all hold.

files_touched: [.harness/harness/features/FEAT-43-code-risk-grading/notes/receipt-harness-dev-ops-validate-remediate-c14-eng-s4.md]
