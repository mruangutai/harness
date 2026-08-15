# Goal-check — FEAT-21-features-layout-migration — 2026-08-14

**Thirteen of fourteen criteria are met. SC-10 is UNMET, proven by mutation, and it routes a fix
cycle — not an escalation.** The migration itself delivered: features live under
`.harness/harness/features/`, every coupled reader moved with them, and the tree is never half moved
at any landed commit. The one failure is in the parity test #387 added, not in the move.

**The pin is not work.** `5c39f8c` (five commits in `62fef85..5c39f8c`, not four) touches only
`STATE.md`, `feature.json`, `observations/harness-orchestrator.md` and a one-line `plan.yaml` status
flip, all inside this feature's own directory (`git show --name-only --format=''`). Nothing was
described to me that the pin contradicts. No ESCALATE on that ground.

## The one failure

**SC-10 — the parity test is one-directional.** The criterion binds two properties; the second is
false as delivered.

- Mutating the CI rendering alone (`layout_migration.render` drops the last blamed reader) reddens
  4 of case 20's assertions. Correct.
- Mutating the session-entry rendering alone (`check-state.sh`'s INV-27 `CANNOT_VERIFY` composition,
  the `_named` line, same drop) leaves case 20 **fully green — 0 FAIL**.

Cause, at source: case 20 does not execute `check-state.sh`. Its `_inv27_text` helper is a *copy* of
check-state.sh's composition inside `test-layout-migration.py`, self-described as "mirrored". A copy
cannot detect drift in the thing it copies.

Mitigation, so the fix is scoped correctly rather than over-scoped: that same mutation **did** redden
`test-check-state.py` case x.2, which asserts the `[neither]` form tag reaches the session-entry
line. So the session-entry blame path is not uncovered — what is uncovered is *parity* between the
two sides in that direction. The remedy is to have case 20 read the real session-entry text (run
`check-state.sh` against a fixture tree), or to move the INV-27 composition into `layout_migration`
so both call sites share one owner and parity becomes structural rather than asserted.

## Verdicts, and the sha each ran at

| SC | Verdict | Ran at | Evidence |
|---|---|---|---|
| SC-01 | met | d033b9d | detector exit 0; unit case 1 scans `REPO_ROOT`, asserts non-zero feature-dir and reader counts (`test-layout-migration.py:122-133`); unit suite PASS |
| SC-02 | met | d033b9d, 5afa7e3, ea937b1 | re-derived verbatim at both sides; see the wording note below |
| SC-03 | met | d033b9d | `check-state.sh` exit 0, `grep -c INV-27` = 0 |
| SC-04 | met | d033b9d | unit 97 PASS exit 0; integration 89 PASS exit 0; all six named suites PASS by name |
| SC-05 | met | 5c39f8c (live checkout, deliberately not a worktree) | `.harness/features` absent to `test -e` and to `find`; T-08's verify asserts `[ -e ]`'s exit status, not a line count |
| SC-06 | met | d033b9d | `--resolve` on the migrated receipt path names `harness-backend-dev`; the pre-move shape prints `NOBODY`; the grant is pinned *exactly* by `test-harness-yaml.py`'s `COLLECT_FIXTURE`, which would redden if widened |
| SC-07 | met | d033b9d | scoped literal sweep plus a concept sweep; survivors enumerated below |
| SC-08 | met | d033b9d | gate allows `feat/FEAT-21-...` (systemMessage, exit 0), denies `feat/FEAT-77-does-not-exist` naming `.harness/harness/features/` |
| SC-09 | met | 5c39f8c live | `git check-ignore -v` on two run dirs at the new location matches `.gitignore:7 .harness/*/features/*/runs/**`; `git status --porcelain` on `runs/` prints nothing |
| SC-10 | **unmet** | d033b9d | two mutations, above |
| SC-11 | met | 62fef85..5c39f8c | `git diff --name-only -- docs/` empty; none of `factory_config.py`, `harness_boundary.py`, `gen-decisions-index.py` in the range |
| SC-12 | met | whole range | two work commits; three bookkeeping commits touch only this feature's own directory |
| SC-13 | met | d033b9d | `test-gh-sync.py:1228` (root resolved, not skipped) and `test-validate-feature-json.py:318` ("ONE file, not zero"); both suites PASS |
| SC-14 | met | d033b9d | exactly three scan-path messages exist (`check-plan-routes.py:639,:658`, `validate-feature-json.py:51`), each names the migrated glob, each asserted at `test-check-plan-routes.py:484,:551` and `test-validate-feature-json.py:321`; the tests.yml error string is covered by T-10's verify form check |

## SC-12 — why the bookkeeping commits do not violate it

Verified rather than accepted: `4b16f47`, `ea937b1` and `5c39f8c` touch **only** paths under
`.harness/{,harness/}features/FEAT-21-features-layout-migration/`. The work commits are `5afa7e3`
(T-01 alone, one file) and `d033b9d` (subject `[harness:t-09]`, body carrying all nine tags on one
line, 617 files). The strict reading — "planning record" means BRIEF and plan only — would disqualify
`STATE.md` and `feature.json` and make the criterion unsatisfiable under the harness's own
bookkeeping mechanics; I reject it as self-defeating.

One nuance for the record: T-09's deliverable, `notes/layout-boundary-2026-08-14.md`, was *created*
in `ea937b1` (a bookkeeping commit) and gained its post-move half in `d033b9d` (50 insertions, 0
deletions). It sits inside the feature's own record, so the exclusion clause covers it.

## SC-02 — met, with a wording weakness worth recording

Both outputs re-derived, not accepted: at `d033b9d` `features: CLEAN — evidence migrated` /
`docs: CLEAN — evidence legacy` / `0 mixed, 0 cannot-verify`; at `5afa7e3` and at the true parent
`ea937b1`, `features: CLEAN — evidence legacy` and the same summary. Both readings of "parent
commit" agree.

"Both captures are committed with their commit sha" is self-referential on the post side: the capture
lands *in* `d033b9d` and cannot name it from inside. What is on record instead — the capture says
"Working tree over HEAD: ea937b1 — this capture rides in the cluster commit", and `STATE.md` at
`5c39f8c` records `THE CLUSTER IS LANDED AT d033b9d` beside the same verbatim output. The sha is in
the tracked record and unambiguous, so the criterion's purpose is served. A future criterion of this
shape should say "the capture names the commit it lands in, and a later record pins the sha".

## SC-07 — the survivor set, re-derived, each justified

Sweep run as `git grep -F '.harness/features/' d033b9d` scoped to `.claude/**`, `.github/**`,
`.harness/team-config.yaml`, `.harness/expertise/**`, `CLAUDE.md`. **Zero instructional occurrences
survive** — every agent file, skill, team definition and the harness command names
`.harness/harness/features/`. The concept sweep (English prose naming the old layout, and
`features/<FEAT>` without the `.harness` prefix) returned only the relative-path family that D-04
explicitly defers to issue #356 — `harness-pm.md:27`, `harness-visual-designer.md:20`.

Survivors and their justifications:

- `harness-init/SKILL.md` ×2, everything under `templates/` — D-05: they describe the tree being
  onboarded, whose own `.harness/` does not move in this unit.
- `.github/workflows/tests.yml:119,125` — inside the block explicitly dated "measured at 62fef85,
  pre-move". BRIEF Scope Out: true as taken. D-07 governs the neighbouring comment, which *was*
  moved.
- `layout_migration.py:6,76,79` and `layout_fixtures.py:30,34` — the detector's own legacy patterns
  and fixtures. It cannot detect a legacy layout without spelling it.
- `check-plan-routes.py:226,:431,:463`, `gh-sync.py:730` — narratives of past defects or explicit
  legacy/migrated contrasts; historical by content.
- `merge-gitignore.sh:6`, `test-factory-claim.py:5`, `test-factory-integration.py:668` — the factory
  lane and onboarded-product layout, deferred to unit 9 by the BRIEF's Out section.
- `test-validate-digest.py` (9 sites), `test-harness-yaml-corpus.py:232` — synthetic fixture strings
  fed to parsers; no file is opened at those paths.
- `test-validate-feature-json.py:281` — **no decision sanctions this one; here is its justification
  from content.** `display = ".harness/features/FEAT-99-x/feature.json"` is the *value under test*:
  the case asserts that whatever display string is passed in appears in every problem line. The path
  is never resolved, opened or globbed, and the file's own docstring (line 6) states nothing there
  reads any real file under `.harness/*/features/*/`. Any string would do. Justified.

Two I name as the weakest, both advisory, neither a goal failure: `check-plan-routes.py:15` uses a
legacy-shaped grant as its illustrative example of a wildcard-segment bug, and `check-state.sh:62`
is a DEC-129 rationale comment whose path spelling is now stale while the glob beneath it carries the
segment. Neither instructs an agent where to write. A one-line follow-up, not a fix cycle.

## Method notes and deviations

- Re-runs at `d033b9d` and `5afa7e3`/`ea937b1` used detached worktrees under `.claude/worktrees/`
  (the write guard denies any other location) with `CLAUDE_PROJECT_DIR` unset so each run resolved
  its own checkout. Both removed after use.
- SC-05 deliberately ran on the live checkout: untracked and ignored files do not exist in a
  worktree, and the criterion binds them. The only dirty paths at the time were under
  `.harness/harness/`, so they cannot fake a pass at `.harness/features/`.
- SC-07 used `git grep <sha>` rather than a tree sweep, so the temporary worktrees inside the search
  path could not contaminate it.
- SC-06's declared evidence kind is `unit`; the suite that actually pins it (`test-harness-yaml.py`)
  is registered as integration. A kind mismatch in the criterion's wording, not a coverage gap.
- SC-05's declared kind is `integration`; the establishing check is T-08's plan `verify:`, which is
  what the criterion's own second clause describes. No suite case duplicates it.

## Open questions

- **Q1 (blocking, to qa/eng):** SC-10 unmet — case 20 must exercise the real session-entry rendering,
  or the INV-27 composition must move into `layout_migration` so both call sites share one owner.
- **Q2 (non-blocking, to the operator):** SC-02's "committed with their commit sha" is
  self-referential for the post-move capture. Met on the record as it stands; the phrasing should not
  be reused.
- **Q3 (non-blocking):** no SC covers what STATE.md's Q-D raises — that both `check-state.sh` and
  `check-plan-routes.py` exited 0 mid-cluster while examining nothing. That is out of this run's
  scope by dispatch and stays with the operator.
