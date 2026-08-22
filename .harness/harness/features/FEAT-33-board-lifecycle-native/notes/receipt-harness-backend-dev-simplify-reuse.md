# REUSE pass — FEAT-33 plan.yaml — harness-backend-dev

## Finding 1: T-04's board-resolution step doesn't name the existing root helper

- **File/line**: `plan.yaml` T-04 intent, "Board resolution" bullet (plan.yaml:258-261): *"no
  --repo, or --repo naming harness.json's github.repo: read the board from
  gh_board.load_board(root)"* — `root` is never sourced.
- **Existing thing**: `factory_config.harness_root()` at
  `.claude/skills/harness/bin/factory_config.py:44-52` is already the established
  root-resolution convention for exactly this case (a bin tool run inside the harness's own
  checkout, resolving to `.harness/harness.json`'s directory). It is already reused by three
  other bin tools: `factory_claim.py:37,45`, `feature-worktree.py:66-67,75`,
  `gh_cost_log.py:37,111`.
- **Distinct thing it is NOT**: `board-station.py:94-100` hand-rolls a *different* walk-up (from
  cwd, probing for `.harness/team-config.yaml`) — that one has a different purpose (resolving an
  arbitrary target project's root) and is out of scope here; T-04's own docstring
  (plan.yaml:263) says `board_lifecycle.py` runs from the harness worktree even when targeting a
  fleet member, so the "no --repo" branch is squarely the `factory_config.harness_root()` case,
  not the `board-station.py` case.
- **Concrete cost**: without naming the helper, the T-04 implementer has no signal to prefer the
  three-tool convention over hand-rolling a fourth walk-up (as `board-station.py` already did
  once). A fourth copy of CLAUDE_PROJECT_DIR-vs-derived-root logic means a future change to that
  probe (e.g. the `.harness/harness/docs/SPEC.md` path, per `factory_config.py`'s own docstring)
  has one more site to edit in lockstep, and the site nobody remembers is the one that goes
  stale silently.
- **Alternative**: add one line to T-04's intent: "resolve `root` via
  `factory_config.harness_root()` (already imported by `factory_claim.py`, `feature-worktree.py`,
  `gh_cost_log.py`) for the no-`--repo` branch." Cheap, reversible — a pm wording fix, not a
  scope change.

## Checked and NOT flagged (considered, rejected)

- T-02's `_STATION_KEYS` edit (factory_config.py:41) — single authoritative constant, plan
  correctly points at the one call site; no duplicate.
- T-03's five GraphQL primitives (`project_create`, `project_link_repository`,
  `project_single_select_create`, `project_single_select_extend`, `project_workflows`) — grepped
  `createProjectV2`, `linkProjectV2ToRepository`, `singleSelectOptions`, `ProjectV2Workflow`,
  `workflows(first` across `.claude/skills/harness/bin/*.py`: zero non-test hits. Genuinely new,
  not a re-implementation. The plan already correctly cites reusing `project_field_options`
  (factory_gh.py:465) rather than adding a second reader.
- T-05's "five network calls" audit design — grepped for an existing `issue list --state
  closed --json ...stateReason,labels` helper: none exists. Not a duplicate.
- T-07/T-08's reuse of `gh_board.board_stations` (gh_board.py:122) and the existing
  `ensure_labels` split (D-04, three implementations deliberately not unified) — already
  correctly cited/settled in the plan; not re-litigated.
- D-11's "set BOTH FACTORY_GH and GH_SYNC_GH" — already documented as the established pattern in
  `gh_board.py`'s own module docstring; plan correctly restates it as a requirement rather than
  re-deriving it, not a duplicate spelling.

## Verdict

One finding, cheap to apply (a plan-wording addition, not a scope change). Everything else
checked came back clean — the plan's other reuse claims (project_field_options,
board_stations, ensure_labels split) are accurate against the source, cited by file/line, and
not duplicated elsewhere in the tree.
