# FEAT-66 — build divergences ledger

Baseline: `35c39f02` (the signed plan; production bytes identical to `origin/main` at `cb6f8050`).
Owning suites compared byte-for-byte (exit status, stdout, stderr) after each of the three
decompositions and again at the implementation pin: the eight `tests/integration/test-check-domain*.py`
suites, `tests/unit/test-config-shape-matrix.py`, `tests/integration/test-plan-merge.py`,
`tests/integration/test-validate-digest.py`. Receipts: `notes/clean-pin-byte-receipts.md`.

## Output divergences

**None from the change.** Every compared suite has the same exit status and the same stdout and stderr
bytes as its baseline receipt once each checkout's own absolute root is normalised (D-09, operator-ruled:
the only raw difference is the running checkout's path in three `ok` lines). No operator-visible line changed.

## Non-output changes, ruled

| id | what | old | new | ruling |
|---|---|---|---|---|
| D-01 | `tests/integration/test-check-domain-artifact.py` `_feat50_digest_red_case` mutant anchors | slices the inline branch between the `# Issues #1058/#1619` comment and `if RE_FEATURE_JSON.match(rel):` | slices `_rule_run_digest`'s body between its `out = []` and `return out`, leaving the rule a no-op | The red proof's meaning is unchanged: with the digest rule muted, the clobber is not denied and no traceback appears. The old anchors name source that no longer exists; a mutant that cannot be cut is INCONCLUSIVE, not red. |
| D-02 | same file, `_bug1124_red_case` mutant anchors | slices between the `# Issue #1124` comment and the `# T-17 / D-08` comment | slices `_state_yaml_prior_refusal`'s body after its `absolute_path is None` guard up to the next `def`, so the prior-ladder returns None (falsy) | As D-01: the run_id collision is not denied under the mutant, no traceback. |
| D-03 | `tests/unit/test-driver-grades.py` (new) | — | locks `shape_problems`, `validate`, `apply_merge` at bar 4 or exactly 2 under `code_grade.grade_source` | SC-01's red-first assertion. Scoped to the three retained names: a file-wide lock was written first and rejected because it also caught `approval_guard`, `parse_digest`, `hook_mode` and eleven grade-3 helpers that SC-03 forbids touching; extracted (new) functions are gated at bar 4 by `code_grade` itself in review. |
| D-04 | plan.yaml T-01 `files` and `verify` name `tests/integration/test-validate-digest-shadows.py` | listed | dropped (amendment) | The file exists only as an untracked file in the operator's main checkout; it is on neither `origin/main` nor this branch. pm read it from the wrong tree. Recorded as an `amendments` entry on the build digest for `record-amendments`; nothing else in the verify block changes. |
| D-05 | `validate-digest.validate`: `load_policy(...)` for the code-reviewer persona | called right after `parse_digest`, before the headline check | called at the head of `_reviewer_errors`, after the common rules | The call either raises (nothing is returned either way) or yields a value read only by the reviewer's policy gate; no error text depends on its position. |
| D-06 | `plan-merge.apply_merge`: the six accumulator lists and the `MergeResult` return paths | six lists extended per key inside the driver's loop; `MergeResult` built on each of the two union-path returns | the key walk is `_merge_keys`, whose `_fold_merge_rows` extends the same six named lists in key order; `MergeResult` is built once on the union path after `_final_bytes` picks the verified splice or the safe_dump rendering | pm's intent asked that `apply_merge` alone extend the accumulators and construct `MergeResult` on each return path; both forms put the driver at abc 28-40 (grade 2-3), so the bar (SC-01) wins. Every list's order is unchanged: rows are folded in `out_order`. |
| D-07 | `check-domain`: the `_head`/`deny` closures | closures over `rel`/`display`/`out` inside `shape_problems` | module-level `_head(shown, text)` and `deny(out, shown, msgs)` | Same bytes produced; the closures' comments moved with them. `deny` keeps its name because four load-bearing comments name it. |
| D-08 | two rationales in validate-digest.py saying a branch was placed away from `validate` because `validate` was "already far past the grade bar (pre-existing)" (`_missing_field_default_hint`'s docstring; the comment above its call in `_missing_field_hint`) | carried verbatim | carried verbatim, each followed by one FEAT-66-marked sentence re-deriving the reason against the post-diff tree | Simplify altitude finding 4: the condition the rationale cites was removed by this diff, and a live instruction derived from a dead constraint sends the next reader to the wrong place. The original bytes are kept; only a marked sentence is appended (the repository's convention for a new fact). |
| D-09 | `tests/integration/test-validate-digest.py` raw stdout at the clean pin checkout vs the baseline receipt | three lines `ok    [severity_max enum] /Users/molchairuangutai/GitHub/harness/.claude/worktrees/harness/FEAT-66-complex-function-drivers/.omp/agents/harness-{code,security,ui}-reviewer.md` | the same three lines with `…/feat66-cleanpin-<pin>/…` | The suite prints the absolute path of the agent file it read, which names the checkout that ran it and nothing about the change. Operator ruling 2026-09-26 (validate c0, MF-01): not a divergence; the comparison replaces each checkout's own root with `<checkout>` on both sides; raw sha1 columns are kept in the receipt and the exact lines are printed there. |


## Simplify pass (four read-only readers, before the pin)

Applied (suites byte-identical after each; grades re-measured):
- reuse 1 — `_rule_run_digest` and the state.yaml prior ladder share `_prior_text` (was `_state_yaml_prior_text` plus an inline copy).
- reuse 3 — `_seed_new_plan` and `_merge_inputs` share `_parsed_proposal` (parse, coerce, anchor check).
- simplification 1 + altitude 3 — `_concat_columns(rows, width)` (zip transpose, literal `6`) replaced by `_fold_merge_rows`, six named lists extended in key order.
- simplification 2 — the reviewer's `(config_path, feature_dir, branch_override, review_pin)` tuple and its `(feature_dir, branch_override, review_pin)` repack replaced by keyword-only parameters at every crossing.
- simplification 3 — `_state_yaml_step_sort` returns `(bucket, names)`; the loop in `_state_yaml_step_findings` files it, instead of three caller-owned sets mutated through a five-parameter signature.
- simplification 4 — `_state_yaml_version` returns the value only; `_valid_state_version(_version)` is the predicate both consumers call.
- altitude 2 — `_merge_keys` no longer returns `changes` beside `replaced`; `apply_merge` derives it through `_replaced_fields` (MergeResult's documented `replaced` shape). Inline, the comprehension put `apply_merge` at abc 22.7 (grade 3).
- altitude 4 — D-08 above.

Skipped, with reasons:
- reuse 2 / altitude 1 — derive `SHAPE_PATTERNS` from `SHAPE_RULES`. `SHAPE_PATTERNS` predates this diff, sits 850 lines above the table with its own forty-line rationale (the `RE_RUN_DIGEST` exclusion, the case-sensitivity hole), and the duplication it names existed before (seven predicate patterns beside eight inline branches). Deriving it means moving a documented constant across the file — outside SC-03. Briefing row.
- reuse 4 — `check-state._inv15_digest_verdict` hand-rolls `_return_tail`. `_return_tail` predates this diff (it is called at the head of the pre-image `validate`); check-state.py is outside the diff. Briefing row.
- efficiency — empty return.

Briefing rows for the residual list: `SHAPE_PATTERNS` derivation; check-state's tail anchor citing validate-digest line numbers that moved.
