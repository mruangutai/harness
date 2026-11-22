# REUSE reader receipt — FEAT-2225 · run r-20261121-5-simplify-eng · diff 594af2a8..fd8ffcdf (read via `git show fd8ffcdf:<path>`)

BLUF: 4 findings, none behavior-changing, all low/medium maintenance cost (lockstep spellings). Read-only; nothing applied. Nothing in the settled set re-flagged. Routing: F-1 is T-01 builder-owned (`expertise-merge.py`); F-2..F-4 are FLAG-ONLY (T-04 / tests).

## Findings (file · line · summary · cost · alternative)

### F-1 (builder-owned, T-01) — two spellings of the same Expertise-path grammar inside one file
- `.claude/skills/harness/bin/expertise-merge.py:470-471` (`EXPERTISE_TAIL`, pre-existing) vs `:716` (`EXPERTISE_PATH_RE`, new) vs `:710-711` (`PERSONA_RE`/`SEGMENT_RE`).
- Cost: `.harness/[<seg>/]expertise/harness-<x>.md` is now spelled twice in one module (one tail-anchored with persona capture, one `^`-anchored); the DEC-253 path shape changes in two places or one silently diverges. Cross-file the same shape also lives at `merge-gate.py:92` (deliberately broader `[^/]+\.md`), `check-instruction-paths.py:30`, `harness_boundary.py:707` — those are other-tool copies; do not touch for this finding.
- Alternative: one fragment `_EXPERTISE_REL = r"\.harness/(?:[^/]+/)?expertise/(harness-[a-z0-9-]+)\.md"`; `EXPERTISE_TAIL = re.compile(r"(?:^|/)" + _EXPERTISE_REL + "$")`, `EXPERTISE_PATH_RE = re.compile("^" + _EXPERTISE_REL + "$")` (the latter keeps an unused capture group, harmless). Behavior: identical matches for both; no test change expected beyond the existing path cases.

### F-2 (FLAG-ONLY, T-04) — `DISTILL_RUN_RE` restated; now three copies
- `dispatch-guard.py:756` and `validate-digest.py:1941` (both new) copy `feature-record.py:628` `DISTILL_RUN` (`(?:^|-)distill-`), tied only by a "feature-record.py's rule" comment.
- Cost: the run-id token rule edited in one place leaves the guard/validator disagreeing on what a distill run is — a fail-open for the member-vs-distill split (a run misread as non-distill is gated as member, a distill misread as member is not).
- Alternative: one constant in `harness_boundary.py` (already touched by this diff; `validate-digest` already loads repo modules via `harness_boundary.load_repo_module`, `:2151`), imported by both. If dispatch-guard's no-import bootstrap must stay, follow the repo's existing precedent `check-domain.py:962-964` (copied literal + a parity test) — add a test asserting all three literals equal. Behavior: none.

### F-3 (FLAG-ONLY, T-04) — merge-gate re-implements expertise-merge's git/hash plumbing
- `merge-gate.py:312-328` (`_run`/`_output`/`_git`, `SUBPROCESS_TIMEOUT_SECONDS=60`) and `:455-457` (`_blob_sha256`) vs `expertise-merge.py:949-956` (`_git`, timeout 30), `:974-977` (`base_blob`), `:727` (`_sha256`).
- Cost: two `git -C … -c core.quotepath=off` wrappers with divergent timeout and failure classes (`DistillRefusal` vs exit-9 refusal), plus a second blob-hash; the one that reads `head:rel` vs `base:./rel` (relative-root form) can drift on checkouts whose root is a subdirectory.
- Alternative: merge-gate loads `expertise_merge` through `harness_boundary.load_repo_module` (as validate-digest does) and uses `base_blob`-style/`_sha256` helpers, or keeps only its own `_blob_sha256` expressed via that module. Implication: error class translation (`MergeRefusal`→`DistillRefusal`) needed at the seam; moderate rework, hence low priority. Acceptable to leave if the divergent refusal exits are intended.

### F-4 (FLAG-ONLY, tests) — loud-git helpers re-declared; `tests/integration/git_support.py` exists
- `tests/integration/test-member-expertise.py:134` (`_git`), `test-merge-gate.py:412` (`git`), `test-expertise-merge.py` fixtures; `git_support.py:23` (`init_repo`), `:35` (`commit_files`) take a caller-chosen `git` callable explicitly for loud runners (docstring `:5-6`).
- Cost: a ~20th copy of init/identity/commit setup; fixture identity/branch config edits are per file.
- Alternative: import `git_support.init_repo/commit_all` passing the loud `git` callable. Behavior: none; only fixture setup.

## Checked, not findings
- `bash-write-guard.py:284` `PYTHON_EXECUTABLE`, `:285` `EXPERTISE_CLI`: no existing equivalent found by grep in bin/.
- `DURABLE_RUN_RE` (`validate-digest.py:1942`): no existing importable run-path matcher found (`handoff_done_when.py:14` `FEATURE_RE` matches the feature prefix only).
- `AGENT_RE` in `inject-expertise.py:45` equals `PERSONA_RE` but is another standalone script; not flagged beyond F-1.

## Principles applied
- Delete First: findings prefer deriving/importing a constant over adding a parity layer; only F-2's fallback adds a test where import is infeasible.

## Open questions
- none blocking.
