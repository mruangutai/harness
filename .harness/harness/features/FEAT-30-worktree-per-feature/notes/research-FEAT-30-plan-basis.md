# Research — FEAT-30 plan basis (segment 1 of DEC-195's plan flow)

**Conclusion.** The brief is buildable as written: 9 tasks, 4 team / 5 main-session-direct, every one
of the 12 criteria mapped, `check-plan-routes.py` exit 0. Two things the dispatch did not name and the
plan now carries: `check-domain.sh`'s shape phase holds a **second and third** fixed-segment
assumption that the `<repo>/<id>` layout silently breaks, and the two new test files must be
registered before any verify may route through `run-unit-tests.sh`.

## The finding that changed the shape of REQ-08 (measured this run, at eeabc59)

`WORKTREE_REL_RE` is not the only place the segment count is load-bearing. Three consumers, not two:

- `harness_boundary.py:310` — `classify`, the domain match (named in the dispatch)
- `check-domain.sh:212` — the `--resolve` path (named in the dispatch)
- `check-domain.sh:644` — `_norm`, the shape phase's own regex, `^\.claude/worktrees/[^/]+/(.+)$`,
  spelled again locally
- `check-domain.sh:602` — `SWEEP_GLOBS`, `os.path.join(".claude", "worktrees", "*", pattern)`,
  consumed by non-recursive `glob.glob` at `:1025`

The last two are the two literals `harness_boundary.py:26-32` deliberately did NOT rewire, and its
comment says why: the shape phase's import of the module is absorbing, not fail-closed. Under
`.claude/worktrees/harness/<id>/` the `_norm` regex leaves the repository segment in the path and the
sweep globs match nothing at all. **The sweep failure is silent** — a glob that matches zero files
reports zero findings — and no success criterion in the brief would catch it. T-04 therefore moves all
four consumers and adds a sweep-at-depth case; the absorbing import stays absorbing.

Discovery of linked worktrees uses `owner_root/.git/worktrees/*/gitdir` rather than a fixed-depth glob
or `git worktree list`: depth-agnostic, and DEC-193 forbids a git subprocess on the governed-write
path. Inside the CLI (not a write path) `git worktree list --porcelain` is used instead of
reimplementing git bookkeeping.

## Why REQ-04 and REQ-08 have no team half

The operator's library-then-cutover split was available and was NOT used for these two. Reason: by
DEC-174 am.4's category, `harness_boundary.py` (the lead's ruling) and `bash-write-guard.sh`,
`check-domain.sh`, `test-check-domain.py`, `test-bash-write-guard.py` (am.4 by name) are ALL inside the
carve-out. There is no library left over for a squad to build — inventing a new module beside
`harness_boundary.py` purely to create a team-laned task would add a second home for one rule, which is
the drift DEC-193 closed. So T-03, T-04 and T-05 are main-session-direct end to end, and the squad's
work is the two genuinely new tools (T-01/T-02 worktree lifecycle, T-06 Expertise merge) plus the
registration.

`check-plan-routes.py` reports T-03, T-04 and T-05 as `DEVIATION ... granted but declared
main-session-direct` and still exits 0. That is the honest carve-out shape, and it is also the proof
that the checker cannot validate laning: `.claude/skills/harness/bin/**` resolves to
`harness-backend-dev harness-dev-ops`, so a wrongly team-laned `check-domain.sh` task would print `OK`.

## The registration trap, re-measured

- `run-unit-tests.sh:18` `INTEGRATION_SCRIPTS` — 12 explicit entries at eeabc59.
- `.harness/harness.json` `test_kinds.integration.detect` — `tests/integration/**` plus **four**
  explicit files (`test-check-state.py`, `test-factory-integration.py`, `test-gh-sync.py`,
  `test-check-plan-routes.py`). Not a wildcard over `bin/test-*.py`. Confirmed by reading the file.
- `run-unit-tests.sh:38-40` runs a drift detector over the UNION of both arrays, so a new
  `test-*.py` that exists but is unregistered makes the RUNNER fail. That is why D-06 exists: every
  verify before T-08 invokes its test file directly with `python3`, and only T-09 and T-08 call the
  runner.

## Red-state technique, and the precedent it copies

`test-bash-write-guard.py:489-509` mutates `WORKTREES_SEGMENT` by name in a copied module, drops
`__pycache__` (mtime+size collision is real — the mutant string is the same length), and requires both
routes to flip 0 -> 2. Every task here reuses one of three shapes derived from it:

- new tool: point the test's `*_BIN` env override at a nonexistent path and require failure, plus
  `git show eeabc59:<path>` must fail, proving the capability did not exist at the baseline.
- new refusal in a new tool: copy the tool, flip a named constant (`REFUSE_ON_DIRTY`,
  `REQUIRE_LANDED`, `UNION_APPLY`) to False, require the suite to FAIL.
- enforcement change: copy `bin/`, restore the changed guard from `git show eeabc59:`, run the NEW
  test file against it via `CHECK_DOMAIN_BIN` / `BASH_WRITE_GUARD_BIN`, require failure; then require
  the real suites to pass. That second half is DEC-174 am.4's identical-violation-set obligation.

T-03 is the one exception and deliberately so: it PINS existing behaviour, so it must pass against
eeabc59. Its discriminator is the `WORKTREES_SEGMENT` mutation — the 16 per-agent cases must go red
under it, which is only possible if the in-worktree half really exercises the worktree path. Both
halves of each pair also assert the agent is IN the set: two empty sets are equal.

Timings measured this run: `test-check-domain.py` 7.5 s, `test-bash-write-guard.py` 4.1 s. Every
verify that runs a suite twice stays well inside 60 s.

## Fixtures, not fleet.yaml

`fleet.yaml` declares one repo (`mruangutai/kaya-ai`, `default_branch: master`) and
`workspace_root: /Users/molchairuangutai/GitHub/harness-factories`; `mruangutai/harness` is absent by
DEC-174 am.1 and `test-no-distribution.py` fails if it returns. SC-01's four worktrees across two
repositories are therefore built on throwaway git repositories in `tempfile.mkdtemp()` with their own
fleet declaration — repoA standing in for the harness case on `main`, repoB under a fixture
`workspace_root` on `master`. The non-`main` default branch is load-bearing: SC-02 asserts the
merge-base, so a hard-coded `main` fails that case. `layout_fixtures.py` was read and is NOT reused —
it is layout-detector stub data, not a repository builder.

`workspace_root` vs `owner_root` is asserted mechanically, not trusted: T-01 case 2 requires that no
created path is under `workspace_root/.claude/worktrees` and that repoB's trees are under
`workspace_root/repoB/.claude/worktrees/repoB`.

## Open, for the reviewers of segments 2 and 3

- **The orchestrator cannot `cd`.** A subagent shares the session's cwd and `CLAUDE_PROJECT_DIR`
  stays the main checkout, so "the orchestrator works inside its worktree" is implemented as absolute
  paths plus `git -C <worktree>`. That is exactly the DEC-143 mechanism the guards already carry
  (raw match, then checkout-relative match), so it is consistent rather than a workaround — but it
  means REQ-01's isolation is enforced by the guards and by the branch, not by process cwd.
- **REQ-04 does not cover the main session**, which is what actually moved HEAD on 2026-08-19. That
  is the brief's scope ("a governed agent"), and the main-session case is answered by isolation: the
  orchestrator's HEAD lives in its own worktree. D-04 records it rather than widening the refusal.
- **SC-01b (uat) is not deliverable by any task.** Four live orchestrators contending for one account
  budget is the operator's judgement; the UAT script is a later mode and T-01..T-09 only make it
  possible.
