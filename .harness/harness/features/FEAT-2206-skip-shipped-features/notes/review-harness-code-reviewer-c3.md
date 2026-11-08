# FAIL — 4a351faea95ad3776f130d0f42f303a4eee3e4b9

T-01 closes both c1 conversions, but SC-03 still loses usable shipped branch comparisons when an unrelated recorded issue field is malformed. One medium substantive must-fix; no new operator decision required.

## Stage 1 — compliance

- **c1 closures (source-inspected):** `check_state/board.py:137-159` keeps `isdigit()` semantics and catches `int()`'s ValueError: superscript `²` and 4,301-digit strings become unusable, while Arabic-Indic `٣` remains 3. Integration regressions at `tests/integration/test-check-state-shipped.py:226,238` assert a surviving issue-11 collision and active issue-3 collision respectively. `notes/red-first.md:73-84` records c1 reds and baseline Unicode green; I did not rerun them.
- `git diff b7af829c 4a351fae -- .claude/skills/harness/bin/feature_json_write.py` is empty: `opt_int`'s raising contract remains unchanged. `artifact_accessors.py:145-170` contains its ValueError inside the loader's documented FeatureJsonError refusal.
- SC-01/02 inspection: `check_state/ctx.py:55-76,223-233` classifies once before artifact loads and keeps ambiguous/unreadable status checked; `runner.py:313-323` retains preflight before the single-note shipped exit. DEC-252's text-line contract governs; Q-01 below is unchanged.
- SC-03 inspection: INV-24's lenient fallback and usable-claim ledger preserve issue comparisons (`ctx.py:90-99,423-452`; `board.py:191-209`), but INV-52 does not consume that fallback (finding below). Existing INV-29 remains independent (`worktrees.py:317-333`).
- SC-04 inspection: implementations/helpers/imports/rows for INV-28/30 are deleted, numbers retired (`table.py:240-245`); enforcing fixtures migrate to current stations. No obsolete function callers remain in `.claude` or `tests`. Supporting documentation/schema-description changes serve retirement. No unrelated implementation changes found.

### F-1 — med / substance / T-01 / SC-03: malformed shipped issue data silently removes a valid branch claim

**Reproducible scenario [INFERENCE; source trace, not an executed probe]:** commit two landed records with `branch: "feat/dup"`; one has a `status: done` plan and `factory: {"repo":"acme/widget","parent":"²"}` (a 4,301-digit string or `issues: 42` also triggers strict refusal). The other has a readable record. A full audit should report their INV-52 branch collision, but does not: `artifact_accessors.py:154-170` refuses the shipped record; `feature_corpus.py:225-239` stores `document=None`; `check_state/corpus.py:153-160` passes those strict census entries straight to `branch_collisions`; `feature_corpus.py:445-456` silently skips the missing mapping. The shipped record is no longer an audit subject, so its malformed field is also intentionally not graded. Usable branch ownership is therefore lost without a diagnostic. `_landed_entry`'s raw fallback repairs INV-24 only, not this path.

**Must fix:** preserve readable shipped branch identity for INV-52 independently of unrelated strict record validation, without weakening active-record refusal; add a discriminating landed-branch collision regression containing malformed shipped issue fields. This is the same comparison-loss class SC-03 explicitly excludes. The current INV-52 regression (`test-check-state-shipped.py:251`) uses otherwise strictly readable JSON and cannot catch it.

## Stage 2 / evidence limits

Qualitative quality verdict is deferred because whole-feature compliance fails. Required mechanical grading independently ran `code-grade.py --base b7af829c0207522b43f978b5275a2ebdc96b3210 --head 4a351faea95ad3776f130d0f42f303a4eee3e4b9`: **PASSING: 60**, no severity or reason-required records (exit 0). This count is the tool's gated records, not a claim that every modified function was emitted.

Reviewed whole implementation/test/docs diff and c1→c2 delta at exact pin; merge-base is b7af829c, no `[harness:human]` commits. Dirty paths are only this feature's live `feature.json` and `plan.yaml`; pinned metadata was separately read with `git show`. No checkout created, source edited, or test/build/lint/full suite run. QA owns executable regressions and literal T-01 verification. The supplied 146-file log ends `verify-exit=0 review_sha=b5b6fa70...`; measured diff from that commit to this pin contains only feature.json review_sha/regate metadata, not executable/test changes. It is equivalent-code evidence, **not literal exact-pin verification**. Prebriefed INV-33/live-board/station/regate disclosures are not new findings.

Product `docs/spec.md`, `docs/decisions.md`, and `docs/architecture.md` are absent in PRODUCT; no control-plane substitute used. No engineering-lead build receipt exists for this main-session-direct task; amendments recorded in feature.json serve the signed criteria/DEC-252 and do not excuse F-1.

## Open questions

- **Q-01 (nonblocking):** align T-01's YAML-mapping/invalid-YAML wording with DEC-252's text-line rule; retain DEC-252 behavior.

## Principles applied

- **Migrate Callers, Then Delete Legacy APIs:** retirement removes old implementations, imports, table rows and enforcing tests together; no compatibility shim retained.
