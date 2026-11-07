# Receipt — harness-backend-dev — 2026-10-06-2 simplify · reuse (BUG-20261006-fleet-planning-recovery)

BULF: PASS (angle completed, flag-only). 7 findings (3 med-ish fold-ins, 4 low); the plan's core reuse claims hold
(`product_config`/`board_for`, `digest_record.load_record`, `feature_json_write.write_feature_json`, `_open_ensure_milestone`/`_open_ensure_parent`
are real and correctly named). No verify clause hand-rolls a check an existing script performs, except T-02's index drift (R-07).
Read-only; no verification executed. Craft leaf read: delete-first.md (judging added mechanisms). Settled set untouched.

Plan paths below are `plan.yaml` lines in the feature worktree; code paths are control-plane baseline 63cac11a.

## Findings (file · line · summary · cost · alternative · disposition)

**R-01 — gh-sync would grow a third "repo -> (repo, board, issue_types)" resolver.** (med, fold-in)
- plan.yaml:134-135 (T-01 repository contract) names `product_config`/`board_for` but not the composed resolver that already exists:
  `board_lifecycle.py:274-306` (`_own_repo` + `_resolve_board`: own repo -> `harness.json`, else `load_fleet(FLEET_PATH)` -> `repo_entry` check -> `board_for`) and `gh-sync.py:276-310` (`load_config`, owner-checkout only, with skip-on-sync-off / unpinned-repo / gh-auth rules).
  Third spelling also needs issue-type overrides: `factory_decompose.py:373` already does `gh_issue_types.overrides_from_config(factory_config.product_config(fleet, repo))`; plan is silent, and `load_config` line 309 takes them from the *owner checkout* cfg.
- Cost: a bound Kaya feature whose overrides come from Harness's cfg is the same cross-repository leak class as the bug; two resolvers (gh-sync, board_lifecycle) with different refusal shapes drift; board_lifecycle then re-reads `github.repo` a second time (`_own_repo` comment, line 275-278).
- Real new behavior vs duplication: new = bind from `factory.repo` first and never fall back. Not new = the fleet branch. Note `board_for` (`factory_config.py:292-307`) REFUSES a null board for a fleet member, so plan.yaml:135's "null board where currently legal" can only be the unbound-Harness path; say so in the task.
- Alternative: one `resolve_binding(feature_doc, root) -> (repo, board, issue_types)` (fleet branch = `load_fleet` + `repo_entry` + `product_config`/`board_for` + `overrides_from_config`; unbound branch = existing `load_config`); `board_lifecycle._resolve_board` and gh-sync both call it. Name the existing seams in the intent.

**R-02 — fake-gh integration tests will hit real `gh` or miss the config reads (dual-binary trap).** (med, fold-in)
- plan.yaml:148 (T-01 tests: "complete fake remote call log", "extend shared fake-gh"). `product_config` reads through `factory_gh.file_at_ref` (`factory_gh.py:93-96`, binary = `FACTORY_GH`); gh-sync's own calls use `GH_SYNC_GH` (`gh-sync.py:121`). `gh_board.py:8-12` documents this as "THE FAKE-BINARY TRAP … set BOTH". `gh_sync_support.py:190-194` `run()` sets only `FAKE_LOG`+`GH_SYNC_GH`; only `ship_env` (line 817-818) sets `FACTORY_GH`. The shared FAKE_GH scripts have no `repos/<r>/contents/...` branch.
- Cost: fleet-case tests either call the real `gh` (network, real repos; `file_at_ref` for a Kaya config) or the "no Harness mutation" assertion is made over a log that never saw the config/board reads — the proof the plan wants (SC-01) is vacuous. Unit seam `test-fleet-product-config.py:53-62` (`patched_file_at_ref`) is not available to a subprocess run.
- Alternative: in `gh_sync_support.run`, set `FACTORY_GH` to the same fake as `GH_SYNC_GH`; add one contents handler to the shared fake (canned per-repo `harness.json`, loud on unknown repo) rather than per-test fakes. State this in T-01's test paragraph.

**R-03 — three spellings of "evidence path is a confined feature-local regular file + sha256".** (med-low, fold-in)
- plan.yaml:145 (evidence confinement) spans feature-record (cycle/refusal/authorization operands), gh-sync `recover-mirror --evidence`/history, and check_state INV-7/15/46 re-verification. Existing: `feature-record.py:383-398` `_require_decision_file` (realpath both sides + `commonpath` + `isfile`, the same rule); also `plan_anchors.py:215-216`; no sha256 helper in feature-record/gh-sync/check_state (hashes exist only in `approval.py:557-558`, `plan_merge/amend.py`, `code_grade.py:373` for other domains).
- Cost: the plan's confinement rules (symlink escape, traversal, hash-change refusal) are the security-relevant part; three copies mean a symlink/abs-path fix lands in one. The existing helper is already the named precedent for operator evidence under the feature dir.
- Alternative: one pure function (home: `feature_schema.py` or a tiny sibling) `feature_evidence(feature_dir, operand) -> (rel_path, sha256)` and `verify_evidence(feature_dir, rel, sha)`; `_require_decision_file` may stay (different operand grammar: cwd-relative, `#fragment`) unless folded; do not migrate set-rework/raise-cycles (out of scope).

**R-04 — recover-mirror's "mode" and every gate's command text should come from `recovery_command_for`, which exists.** (low-med, fold-in)
- plan.yaml:138 says mode is "derived from the same existing work-started/terminal rules" but names no function; that rule IS `feature_schema.py:330-345` `recovery_command_for` (open vs recover-terminal: era-exempt, plan done/review, any task done).
- Command text is composed/hard-coded at `gh-sync.py:1366-1399`, `merge-gate.py:254-255`, `post-merge-sweep.py:260` (literal "recover-terminal …"; never consults the function). Plan.yaml:140 wants gates to pick `recover-mirror` for invalid mappings.
- Cost: adding recover-mirror as a fourth literal at each site; post-merge-sweep stays on the old text. A runnable recover-mirror line also needs `--previous-repo`/`--evidence` (unlike `--yes` appended by merge-gate:255), so naive reuse of the composer is not enough.
- Alternative: mode = full iff `recovery_command_for(feat_dir) == "open"`; extend/sibling that one function to return a recover-mirror selection for invalid/unproven mappings (and a shared "run X" formatter); route gh-sync, merge-gate, post-merge-sweep through it. Name it in T-01.

**R-05 — "reuse pure provenance/receipt predicates in feature_schema" names predicates that do not exist.** (low, fold-in wording)
- plan.yaml:140. Allowed-receipt set is duplicated as `{"opened","not-applicable","recovered-terminal"}` at `merge-gate.py:247` and `post-merge-sweep.py:256`; `board.py:308-310` (inv_37) has a third variant; enum also in `gh-sync.py:620` and feature-schema.json. `feature_schema.py` has `BUILD_ENTRY_ERA_EXEMPT`/`recovery_command_for` only.
- This is creation, not reuse; the plan should say: create one predicate (e.g., `receipt_allows_merge(doc, bound_repo)`), delete the two literals and the inv_37 variant in the same change, so "opened for the wrong repo" is rejected in one place (delete-first: removal precedes the new check).
- Alternative as stated.

**R-06 — schema timestamp/hash patterns will be pasted ~12 more times.** (low, briefing-row)
- `feature-schema.json:56,57,81,119` repeat the ISO-8601 regex inline; `:97` the sha256 pattern; the schema has no `$defs`/`$ref` (grep: none). plan.yaml:136, 141, 143 add `history.at`, `recovery.started_at/completed_at`, evidence/authorization hashes, `cycle_evidence.at`, `refusal.at` and sha256 fields.
- Cost: tightening one (fractional seconds, offset) leaves the others; INV-7/15 then disagree with the schema.
- Alternative: define `$defs.timestamp`/`$defs.sha256` once and `$ref` them from new fields (leave old four alone). [INFERENCE] `_missing_keys`/`_undeclared_keys` (`feature_schema.py:125-141`) read `error.schema` properties; a `$ref` target is the resolved subschema so message shape should hold, but not confirmed — if it changes error text, keep inline patterns and accept the cost.

**R-07 — T-02 verify skips the existing index-drift check for its own stated deliverable.** (low, fold-in)
- plan.yaml:167-168: verify = `check-decision-anchors.py --file DECISIONS.md` only; plan.yaml:172 requires regenerating `DECISIONS-INDEX.md`. `gen-decisions-index.py:9-10` documents the drift check: `gen-decisions-index.py --stdout | diff - .harness/harness/docs/DECISIONS-INDEX.md` (no `--check` mode). `test-gen-decisions-index.py` exists.
- Cost: a stale index (DEC-157/203/221 row text, INV-48 reads the index) passes T-02's verify.
- Alternative: append that pipe to T-02 verify (expect empty diff). Not a hand-rolled check; it omits an existing one.

## Checked and not flagged (real new behavior or correctly reused)
- `run-end --digest` is new: `run-end` has no such arg (`feature-record.py:773-781`); `close-run` already takes the digest (`:792`) and runs `validate-digest.py` then `run-end` as stages (`:609-644`); forwarding is a one-line stage change. `digest_record.load_record` (`digest_record.py:69`) is the right shared reader (consumers: `check_state/ctx.py:544`, `plan_merge/panel.py:437`).
- Archive/replace transition: `save_recorded` (`gh-sync.py:863-935`) already goes through `feature_json_write.write_feature_json`; recover-mirror's single locked transition must use the same transform path (plan.yaml:137 says so). `save_recorded` rebuilds the `github` block from `rec` (drops unknown keys) — plan.yaml:136 already calls this out.
- Marker read-back (plan.yaml:139): no issue-by-milestone reader exists in `factory_gh.py`/`gh_issues.py`/`gh-sync.py`; new. The "existing bounded milestone-title recovery" (`gh-sync.py:1087-1096`) is a first-page, default-state, no-truncation-signal jq lookup that fails closed on a miss (`skip`). It is fine for the milestone, but is not a template for the marker scan (needs its own page/truncation detection). PF-2157 not re-raised.
- `close-run --refused-return` already exists with an inverted stage (`feature-record.py:620-625`, `_stage` accepts any nonzero); the plan's exit-1-only hardening is new behavior, not duplication.
- All five T-01 verify files exist (`tests/unit/test-feature-record.py`, `test-digest-record.py`, `test-gh-sync-build-entry.py`; `tests/integration/test-gh-sync-open.py`, `test-check-state-records.py`).
