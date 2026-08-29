# SIMPLIFY pass — ALTITUDE angle — C21 — harness-dev-ops

BLUF: no gating findings. Two briefing-row candidates (validate-digest.py's SEC-01 home,
the legacy-23 allowlist retirement), both explicitly deferred as backlog, not this pass —
extraction/retirement would each blow the one-fix ceiling and reopen settled scope. Every
other altitude question in scope resolves to `leave`. Five suites PASS. Working tree clean
apart from feature `notes/`/`answers/` (mine and peers').

## Lead question 2 — validate-digest.py's SEC-01 block (+~330 lines: `_default_branch_or_none`,
`_merge_base_or_none`, `_derived_reviewed_python_change`, `_feature_dir_from_artifact`,
`_resolve_feature_dir`, `_read_review_sha`, `_read_feature_branch`, `_current_branch_or_none`,
`_branch_corroboration_error`, `resolve_review_sha`, `code_grade_bound_to_review`)

**Home.** validate-digest.py's own docstring (`:2-9`) states its job as one thing: catch
DRIFTED digest fields a charitable LLM reader would normalize away. SEC-01 is a different
capability — cryptographically-flavored anti-forgery binding a `code_grade` claim to
`feature.json`'s `review_sha` via git, resolvable-branch corroboration, and a derived
merge-base range. It is scoped correctly *inside* `if raw_persona == "harness-code-reviewer"`
(`:1132`), never touching the other ~15 personas' validation — that part is right. But the
**module** carrying it is the generic digest parser, not a policy module.

**The file's own convention says otherwise.** validate-digest.py already imports thin,
single-purpose functions from two sibling modules for exactly this class of problem:
`from code_grade import commit_oid` (`:32`, called once, `:544`) and `from gate_policy import
GatePolicyError, evaluate_review, load_policy` (`:33`, called 3×: `:960`, `:1167`, `:1463`).
SEC-01 breaks that pattern — instead of a thin import from (or a new sibling to) `code_grade.py`
or `gate_policy.py`, it inlines the whole subsystem. Concrete cost: a maintainer opening
validate-digest.py to fix a YAML-parsing bug (its stated job) now wades past ~330 lines of
git/feature.json/branch logic to reach `validate()`; file grew 707→1505 lines this diff. This
is also exactly the "several authoritative statements that can drift" shape the angle asks
about — the repo already has ONE convention (policy → sibling module, thin import) and this
lands a second, unlabeled one in the same file.

**Deletion test.** Lifting SEC-01 into its own module (e.g. `review_binding.py`, mirroring
`gate_policy.py`) would genuinely shrink validate-digest.py by ~330 lines; the remaining call
site collapses to the same shape as the existing `evaluate_review`/`load_policy` imports.
Complexity does not merely relocate under a different roof — the file's own stated scope
(digest-schema drift) gets its integrity back, and the new module's name states the
capability truthfully.

**Seam reality — checked, not assumed.** Confirmed by `grep`: `code_grade_bound_to_review`,
`resolve_review_sha`, and `_derived_reviewed_python_change` are each called from exactly ONE
site, all inside `validate()` (`:1132`, `:1146`, `:1150`). That is a real single-adapter
situation today, same as `commit_oid`/`evaluate_review` before them — not evidence the seam
is fake, since those two are proof the pattern already works at one-caller scale in this
exact file.

**Why not now.** Extraction here is not the qa gate's single quick fix: it changes
`validate()`'s and `code_grade_bound_to_review`'s signatures, touches every fixture-override
call site across 724 new lines of `test-validate-digest.py`, and reopens work SEC-01 waves
2–4 already closed and had reviewed. That is far past the one-fix ceiling and reopens settled
scope, exactly as the dispatch anticipated.

**Recommendation: briefing-row — for the backlog, not this pass.** Row: "extract SEC-01's
review-binding subsystem out of validate-digest.py into its own module (mirroring
gate_policy.py), importing 2–3 thin functions the same way commit_oid/evaluate_review already
are." No `must_fix`; qa already PASSed this tree without it, and it changes no observable
behavior.

## Lead question 1 — SELF_GRADING_ALLOWLIST (5→37: 14 SC-15 grade-2, 23 pre-existing legacy debt)

**Altitude of the exemption list itself.** It lives inline in test-code-grade.py
(`:207-255`), a tuple-keyed dict with per-entry provenance comments (SC-15 item numbers citing
`notes/review-harness-code-reviewer-validate-final-panel.md`, or a batch comment citing the
`--base 7ccfae8..a643e44` cross-check that confirms the 23 legacy entries predate this
feature). That's a reasonable altitude for a list that's read by exactly one thing — this
file's own `check_self_grading()` — never by the production gate: confirmed by `grep
SELF_GRADING_ALLOWLIST` across `code-grade.py`/`code_grade.py` → zero hits. Per
`Q8-sec01-remedy-ruling.md` §Q3, the allowlist/gated-set intersection is settled, and
`code-grade.py` never reads it, so this is dogfooding on the repo's own bin/ scripts, not a
hole in the shipped gate. That materially lowers the stakes — it is a hygiene backlog, not a
production exemption surface.

**Is the compensating control sufficient?** `_check_self_graded_file` (`:274-278`) asserts
`record.grade == SELF_GRADING_ALLOWLIST[key]` — EXACT match, not `>=` — so the list decays on
BOTH directions: a regression (grade drops further) fails loudly, and so does an unnoticed
improvement (grade rises but the entry is never retired) — either way the suite goes red and
someone has to look. `check_self_grading()` (`:300`) additionally asserts
`matched_allowlist == set(SELF_GRADING_ALLOWLIST)`, so a renamed or removed qualname is caught
too (no silent staleness by omission). This is a real, automatic, self-enforcing control —
stronger than "a human remembers to re-audit it" — but it only prevents the list from lying
about the PRESENT grade of what's already in it; it does nothing to stop new entries being
added cheaply (one dict line + comment) as an alternative to fixing a function, which is the
"growing exemption surface" the cycle-18 digest actually warned about.

**Why not "fold-in" now.** Retiring 23 legacy-debt entries means materially refactoring 23
functions across 5 production+test files that are NOT part of the reviewed diff (confirmed
pre-existing by the batch comment's own `--base 7ccfae8..a643e44` cross-check) — reopening
settled, unreviewed scope, and nowhere near a one-fix ceiling.

**Recommendation: briefing-row.** Two rows for the backlog: (1) pay down the 23 legacy-debt
entries function-by-function in a future scoped pass, since the exact-match staleness control
only catches drift, not stagnation; (2) not urgent given (a) the list gates nothing in
production and (b) the staleness/coverage assertions already prevent it from silently
misreporting current state.

## Ordinary altitude sweep — the rest of the diff

- `check-plan-routes.py` `resolution_manifest` → `_owner_root` + `_manifest_deviation`: two
  private, single-caller helpers, correctly scoped, no special case bolted on. **Leave.**
- `code-grade.py` `_blocks`/`_severity`, `_run_name_status_diff`/`_name_status_entries`/
  `_is_changed_python`: same — small, single-purpose, one caller each, home unchanged from
  where the logic already lived. **Leave.**
- `code_grade.py` `_child_qualname`, `_next_paths`: same shape. **Leave.**
- `gate_policy.py` `_load_config`/`_require_gates`/`_resolve_gate`, `_validate_suites`: same
  shape, and matches the file's existing style (small pure helpers, `load_policy`/
  `evaluate_qa` as thin drivers). **Leave.**
- `.claude/skills/harness-code-review/SKILL.md`: doc-only rewording of the severity rule to
  match code-grade.py's actual bar-relative behavior (a grade-3 production function below its
  bar is `high`, same as grade-1). One authoritative statement, correctly kept in the one file
  that states it. **Leave.**

## `test-check-plan-routes.py` case_20's tokenize-based joiner — is a source-line joiner at
the right home inside one test case?

Read the live code directly (not a cached snapshot — this needed a second, shell-verified
pass after a tool read returned a stale body on the first try). `_logical_lines_python` /
`_logical_lines_shell` / `logical_lines` are all nested INSIDE `case_20` (`:1174-1233`), used
by that case's own `_scan_file`/`_assert_logical_lines_fixture` helpers, and by nothing else:
`grep -rl "generate_tokens\|logical_lines"` across all of `bin/*.py` returns only this one
file. `test-check-state.py`'s `case_o` — the sibling case_20's own docstring calls "this
repo's pattern" — uses a different, non-tokenize detector for a different duplicated pattern
(INV numbers), so there is no existing duplication this joiner should instead be reusing.

This is a single-caller, thoroughly-documented (six drafts' failure modes recorded in the
docstring, plus a dedicated fixture asserting string/comment-awareness) test-only heuristic
for one smoke check, explicitly labeled "a cheap smoke check, not the guarantee." It is not a
special case bolted onto shared infrastructure (there is no shared infrastructure here to bolt
onto — the seam would be hypothetical, one caller), and it is not a workaround patching a
runtime mechanism's symptom — it's test tooling. **Leave.** (Note: B5, carried forward — the
*actual* duplicated-pattern seam in this diff's test files is the git-scratch-repo
initialization repeated across `test-code-grade.py`/`test-code-grade-cli.py`, not this.)

## Residual: `_check_self_graded_file` at grade 3, exactly its bar

Measured directly: `code_grade.grade_source` on `test-code-grade.py` reports
`_check_self_graded_file` at `cyclomatic=4, cognitive=5, abc=21.4, grade=3` — the test-file
bar is exactly 3 (`code_grade_cli._is_test`). The cycle-18 receipt
(`receipt-harness-backend-dev-validate-remediate-c18-eng.md:51`) already names this exact
number when it was split out of the original `check_self_grading`.

Right to accept, and the compensating control is real and already named (in mechanism, not
previously in this word): `_check_self_graded_file` is not in `SELF_GRADING_ALLOWLIST`, and
`test-code-grade.py` is itself one of `SELF_GRADED_FILES` (self-application) — so if this
function's own complexity worsens past grade 3, `check_self_grading()` catches it on its very
next run with no separate exemption to add or forget. That is stronger than a manual residual
note: the guard grades itself.

## Suites run (verbatim exit codes, worktree root)

```
python3 .claude/skills/harness/bin/test-code-grade.py            -> exit 0, "PASS test-code-grade"
python3 .claude/skills/harness/bin/test-code-grade-cli.py        -> exit 0, "PASS test-code-grade-cli"
python3 .claude/skills/harness/bin/test-gate-policy.py           -> exit 0 (all `ok` lines)
python3 .claude/skills/harness/bin/test-check-plan-routes.py     -> exit 0, "ALL PASS"
python3 .claude/skills/harness/bin/test-validate-digest.py       -> exit 0, "ALL PASSED."
```

## Carried findings (not re-reported)

None of B1–B8 re-derived independently by this angle beyond what's already cited above (B5
noted in passing under case_20, not re-argued).

## `git status --porcelain` at end of run

```
 M .harness/harness/features/FEAT-43-code-risk-grading/STATE.md
 M .harness/harness/features/FEAT-43-code-risk-grading/feature.json
?? .harness/harness/features/FEAT-43-code-risk-grading/answers/Q6-cycle-20-remediation-authorization.md
?? .harness/harness/features/FEAT-43-code-risk-grading/answers/Q7-cycle-25-preemptive-authorization.md
?? .harness/harness/features/FEAT-43-code-risk-grading/answers/Q8-sec01-remedy-ruling.md
?? .harness/harness/features/FEAT-43-code-risk-grading/notes/qa-regate-c18.md
?? .harness/harness/features/FEAT-43-code-risk-grading/notes/receipt-harness-backend-dev-reuse-c21.md
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
All of the above are pre-existing (this run's own STATE.md/feature.json edits and peer
notes/answers files, none authored by this run) except this file itself, which is new. No
source file (`.py`, `SKILL.md`, `.json` config) under review scope was touched.

## `must_fix`

None. Nothing here gates the pin — both substantive findings are explicitly recommended as
backlog rows, not applies, and neither changes observable behavior of the shipped diff.
