# Grilling — factory claim resolves the feature repository root (#1290) — 2026-09-05

Source ticket: https://github.com/mruangutai/harness/issues/1290 (body rewritten this sitting; it is
the detailed scope record — this note is the decision record).

## Destination
`factory_claim.py` reads a claimed issue's plan from `.harness/<segment>/features/<FEAT>/` under the
Harness root, where `<segment>` comes from the candidate's fleet repository name — so a claim for a
kaya-ai issue evaluates its blocker gate instead of returning `no_plan`. Ships as a `BUG-1290-*` flow
through the normal gates (DEC-139).

## Settled
- Full cycle or simplified? → BUG flow: single engineering squad, no product/design/UAT segments,
  `verify: test` only. Not a hand-fix on a branch — the mutation-proof requirement needs the QA gate.
- The contract claim adopts → the existing per-repository feature tree
  `.harness/<segment>/features/<FEAT>`, segment = fleet `name` minus owner, literal `harness` for this
  repository. NOT "decomposition's contract" — decompose takes `<feature-dir>` positionally.
- Where the segment rule lives → ONE resolver function, called by both `factory_claim.py` and
  `feature-worktree.py:resolve_repo`. Module placement (`factory_config` vs `harness_boundary`) is
  eng's call.
- `FEATURES_ROOT` module global → deleted, no alias. Tests that monkeypatch it migrate; the two
  module-scope cases pinning its default (`tests/unit/test-factory-claim.py:58-68`) are deleted, not
  re-pinned.
- Cache key → `_BlockerCache` keys on `(repo, feature)`, never `feature` alone.
- Unknown repository → no new refusal path; `factory_config.repo_entry` and candidate step 4 already
  fail closed. Absent per-repo root → the existing `no_plan` reason text naming the resolved path.
- "Harness-repository claims continue to work" → fixture-only criterion (fleet omits
  `mruangutai/harness`, DEC-174); kept as a regression check, not a live behaviour.

## Not yet specified
- none

## Out of scope
- Migrating `post-merge-sweep.sh:163`, `quarantine.py:109`, `worktree_terminal.py:107-129`,
  `feature_schema.py:231` onto the new resolver — they already work; touch only if the change forces it.
- Landing `.harness/kaya-ai/features/FEAT-04-…` on `main` — it lives only in the FEAT-04 worktree, so a
  live claim run from `main` still sees `no_plan` after this fix. That is FEAT-04's landing, not this bug.
- Populating FEAT-04's `feature.json` `factory.issues` map (decompose has not recorded receipts yet).

## Facts I verified (so pm does not re-derive them) — at eb9d044e
- `factory_claim.py:48-50` hardcodes `FEATURES_ROOT`; sole consumer `_BlockerCache(FEATURES_ROOT)` at
  `:341`; `repo_name` is in hand at `:343`. Docstring `:26-29` describes the hardcode.
- `factory_decompose.py:337` — `feature_dir` is a positional CLI argument; no repo-keyed resolution.
- Segment derivations today: `feature-worktree.py:64-87` (`resolve_repo`, `split("/",1)[-1]`, literal
  `harness`), `worktree_terminal.py:107-129` (reverse direction), `post-merge-sweep.sh:163`,
  `quarantine.py:109,171`, `feature_schema.py:231`.
- `fleet.yaml` repos: `mruangutai/kaya-ai`, `mruangutai/harness-factory-smoke`; `mruangutai/harness`
  deliberately absent (DEC-174, asserted by `tests/unit/test-no-distribution.py:178-198`).
- Feature-id collision is real: `.harness/harness/features/FEAT-04-decisions-index` and
  `.claude/worktrees/harness/FEAT-04-pdf-parser-evaluation/.harness/kaya-ai/features/FEAT-04-pdf-parser-evaluation`.
- Tests touching `FEATURES_ROOT`: `tests/unit/test-factory-claim.py:7-16,58-68,336-377,393-420,850-867`;
  `tests/integration/test-factory-integration.py:28-30,879-882`.
- FEAT-04 (kaya) `feature.json` carries no `factory` key — decompose receipts not yet recorded.
