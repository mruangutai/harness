# SIMPLIFICATION angle — validate-final-simplify-c21

**Conclusion up front: empty apply set.** The three remediation commits
(`a643e44`, `34a49c4`, `1710676`) add substantial new surface but I found no
narrating comment describing a superseded mechanism, no dead reference to a
retired shape, and no redundant conjunct worth trimming. Five focused suites
all green. Working tree unchanged apart from this receipt.

## Scope actually read

Diff range used: `a643e44f97285c5388fcd1bc7287cdd6d79a103b~1..17106762c588b3d1c0df45efbcb6128604efb185`
(the three remediation commits on top of the prior simplify pass — NOT the
full-feature range against `7ccfae8d`, which the dispatch's stated review
base would have pulled in; I confirmed the commit log and restricted to the
named three commits).

- `.claude/skills/harness/bin/validate-digest.py` — full added region, lines
  566–924 of the new file (SEC-01 wave 2/4 comment block, `_default_branch_or_none`,
  `_merge_base_or_none`, `_derived_reviewed_python_change`, `_feature_dir_from_artifact`,
  `_resolve_feature_dir`, `_read_review_sha`, `_read_feature_branch`,
  `_current_branch_or_none`, `_branch_corroboration_error`, `resolve_review_sha`,
  `_parse_reviewed_range`, `code_grade_bound_to_review`, `_missing_field_default_hint`,
  and the `n_a` decision rewire at the old `:762` region).
- `.claude/skills/harness/bin/code-grade.py` — `_blocks`/`_severity` extraction,
  `_run_name_status_diff`/`_name_status_entries`/`_is_changed_python` decomposition of
  `_diff_paths`, `_status` reuse of `_blocks`.
- `.claude/skills/harness/bin/code_grade.py` — `_child_qualname` extraction in
  `_records`, `_next_paths` extraction in `_changed_python_files`.
- `.claude/skills/harness/bin/gate_policy.py` — `_load_config`/`_require_gates`/
  `_resolve_gate` decomposition of `load_policy`, `_validate_suites` extraction
  from `evaluate_qa`.
- `.claude/skills/harness/bin/check-plan-routes.py` — `_owner_root`/
  `_manifest_deviation` decomposition of `resolution_manifest`.
- `.claude/skills/harness/bin/test-code-grade.py` — `SELF_GRADED_FILES`,
  `SELF_GRADING_ALLOWLIST`, `_check_self_graded_file`, `check_self_grading`, and the
  `main`/`check_fixtures`/`check_nested_qualnames`/`check_direction_pairs` split.
- `.claude/skills/harness/bin/test-validate-digest.py` — full added region: the
  `code_grade` missing-hint case, `REVIEW_SHA`/`make_feature_dir`, `reviewer_digest`'s
  new `artifact` param and non-no-op default, `check_reviewed_range` and its
  `N_A_REFUSAL_SUBSTRINGS`/`_assert_n_a_rejects`/`_check_option_like_revisions` split,
  `make_derived_base_repo`/`check_derived_base_range`,
  `check_unresolvable_default_branch`, `make_orphan_review_repo`/`check_no_merge_base`,
  `check_review_sha_binding` and its three helpers, `check_resolve_review_sha_artifact_path`,
  `check_resolve_review_sha_feature_json`, `check_branch_corroboration`,
  `check_config_errors`'s `feature_dir` threading.
- `.claude/skills/harness-code-review/SKILL.md` — the grade-3/bar-relative
  paragraph replacing the old grade-1/grade-2-only wording.
- `test-check-plan-routes.py`, `test-code-grade-cli.py`, `test-gate-policy.py`
  diffs read for shape only (parameter threading to match signature changes
  above); no independent complexity added there.

## Targeted hunt (per dispatch)

**SEC-01 region of `validate-digest.py`.** No residue of attempt 1's
mechanism. The top-of-block comment (line ~10) explicitly narrates the
history ("wave 2" bound `reviewed`'s HEAD; "wave 4" rewires the `n_a`
decision) but every sentence is phrased as *why the current code is shaped
this way*, not as a description of a shape that still exists — I checked each
clause against the code beneath it and found none stale. The `_discarded`
binding (`validate-digest.py`, the `n_a` branch, `_discarded, shape_error =
reviewed_python_change(...)`) is explained in-place, three lines above where
a reader hits it: "its 'did Python change' answer is DISCARDED, never the
decision (Q8: cross-checked, not decisive)." No dangling reference to a
digest-driven decision anywhere else in the function.

**Severity handling in `code-grade.py`/`code_grade.py`.** Grepped the whole
`bin/` tree for the retired `{1: "high", 2: "med"}` literal and any prose
describing it: zero matches outside the diff's own removal. `_blocks`/
`_severity` fully replaced it, `_status` now calls `_blocks` too (no
duplicate `grade < bar and grade != 2` left inline).

**`check_self_grading` in `test-code-grade.py`.** No residue of the
cycle-14 thirteen-private-name-pin approach. `SELF_GRADED_FILES` is a file
tuple, `SELF_GRADING_ALLOWLIST` is keyed by `(filename, qualname)` pairs
discovered by AST enumeration (`code_grade.grade_source`), not by any
hard-coded helper-name list — the design cycle 18 replaced it with is the
only one present.

## Redundant conjuncts / dead branches

None found. Each decomposition (`_blocks`, `_severity`, `_child_qualname`,
`_next_paths`, `_owner_root`, `_manifest_deviation`, `_load_config`,
`_require_gates`, `_resolve_gate`, `_validate_suites`) is called exactly
once from its extraction site plus (for `_blocks`) once more from `_status`
— the reuse is the point of the extraction, not a duplicate check. No `if`
arm in the SEC-01 rewire is unreachable: `_derived_reviewed_python_change`'s
three failure branches (unresolvable default branch, unresolvable
review_sha/merge-base, degenerate range) are each independently exercised
by `check_unresolvable_default_branch`, `check_no_merge_base`, and
`check_derived_base_range` against real, purpose-built `/tmp` repos — not
speculative coverage.

**Not flagged as an apply candidate (per the pass's own rule):** the double
`git diff` in the `n_a` path (`reviewed_python_change` on the digest's own
range, then `_derived_reviewed_python_change` on the derived range) reads,
on first pass, like a redundant conjunct. It is carried forward as **B-carried
(no new ID)** — this is the exact double-diff the dispatch's settled-contract
section names as a deliberate, recorded cost preserving `reviewed_python_change`'s
byte-identical injection guard. Not re-reported as a finding.

## Lead question 2 — is validate-digest.py's growth restatement?

**Assessment: carrying its weight, not restatement.** The ~397 added lines
in this file (measured: `git diff --stat` over the three-commit range) split
into six independently-motivated units, each proven by its own dedicated
`/tmp`-repo test rather than sharing coverage:

1. default-branch/merge-base derivation (`_default_branch_or_none`,
   `_merge_base_or_none`, `_derived_reviewed_python_change`) — the actual
   SEC-01 wave-4 fix;
2. artifact-path → feature-dir resolution (`_feature_dir_from_artifact`,
   `_resolve_feature_dir`) — a distinct "WHICH feature" concern, factored out
   because both the SHA binding and the wave-3 branch check need it;
3. review_sha read (`_read_review_sha`) and the unconditional head-binding
   check (`code_grade_bound_to_review`, `resolve_review_sha`) — the core
   SEC-01 fix, applying to all four `code_grade` values, not just `n_a`;
4. wave-3 branch corroboration (`_read_feature_branch`,
   `_current_branch_or_none`, `_branch_corroboration_error`) — closes a
   residual hole SEC-01 itself didn't (cross-feature `artifact:` reuse);
5. `_parse_reviewed_range` — shape-check factoring shared by 1 and 3;
6. `_missing_field_default_hint` — unrelated (SC-19 hint wording), correctly
   isolated as its own small helper rather than growing `validate`.

None of these restates another; each guards a distinct forgery shape named
in `Q8-sec01-remedy-ruling.md` (no-op-at-pin, `~1`-ancestor, cross-feature
`artifact:` reuse, unresolvable default branch, unresolvable merge-base,
degenerate/already-merged range). The docstrings are long but load-bearing —
each states which of these six the function proves and why it needs a real
git repo rather than a stub, which is exactly the kind of anchor the pass is
told not to trim.

## Redundant-assertion note (not an apply)

`test-code-grade.py:check_self_grading`'s closing assertion
(`matched_allowlist == set(SELF_GRADING_ALLOWLIST)`, "no stale entries") is a
second check layered on top of the per-record `record.grade ==
SELF_GRADING_ALLOWLIST[key]` check inside the loop. It is not redundant —
the loop check catches a *drifted grade*, the closing check catches an
*orphaned entry* (renamed/removed qualname that never matched at all) — two
different failure modes, so no apply and no backlog row needed.

## Lead's assessment question 1 — SELF_GRADING_ALLOWLIST growth (5 → 37)

Not this angle's primary question, but bears on SIMPLIFICATION: **a sound,
self-invalidating record, not a growing exemption surface.** The staleness
assertion (`matched_allowlist == set(SELF_GRADING_ALLOWLIST)`) plus the
per-key exact-grade pin means any of three things breaks the suite loudly:
a rename, a removal, or *any* grade change including an improvement. That is
the opposite of silent rot — an entry cannot outlive the fact it records.
The list is long (37 entries, 23 pre-existing) but length is the honest
cost of the design: enumerating the whole file set (CR-01's own fix) makes
every pre-existing below-bar function visible where the old 13-name-pin
approach hid the rest. Growing further would show up as either (a) new
`REASON REQUIRED` entries at review time, which is the process working, or
(b) more pre-existing debt being surfaced by widening `SELF_GRADED_FILES`,
which is also the process working. No apply; no simplification available
that preserves the staleness guarantee.

## Suite runs (verbatim exit statuses)

```
python3 .claude/skills/harness/bin/test-code-grade.py          -> exit 0 (PASS test-code-grade)
python3 .claude/skills/harness/bin/test-code-grade-cli.py      -> exit 0 (PASS test-code-grade-cli)
python3 .claude/skills/harness/bin/test-gate-policy.py         -> exit 0 (28/28 ok)
python3 .claude/skills/harness/bin/test-check-plan-routes.py   -> exit 0 (ALL PASS)
python3 .claude/skills/harness/bin/test-validate-digest.py     -> exit 0 (66/66 CLI + 14/14 hook + 24/24 T-09 + 2/2 template, ALL PASSED)
```

## Carried-forward findings

None of B1–B8 re-derived independently by this angle (B6, the two git
subprocess wrappers, is adjacent to what I read in `code-grade.py`/
`code_grade.py` but the two wrappers I looked at, `_git_text`/`_git_output`,
were unchanged by these three commits — not re-verified here, cited as
already carried).

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
?? .harness/harness/features/FEAT-43-code-risk-grading/notes/receipt-harness-dev-ops-validate-remediate-c14-eng-s4.md
?? .harness/harness/features/FEAT-43-code-risk-grading/notes/receipt-harness-dev-ops-validate-remediate-c14-eng-s6.md
```

All of the above pre-date this run (prior agents' feature-tracking edits and
receipts); none were touched by me. No `.py` source or test file under
`.claude/skills/harness/bin/` or `.claude/skills/harness-code-review/` was
edited.

## Findings table

| ID | file:line | summary | concrete cost | alternative | verdict |
|---|---|---|---|---|---|
| — | — | no findings | — | — | empty return, as expected |

`must_fix: []`.
