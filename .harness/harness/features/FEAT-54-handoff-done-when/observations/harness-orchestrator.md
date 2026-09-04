# Observations - harness-orchestrator

- 2026-09-02: FEAT-54's approved plan pinned 5 files under .claude/skills/harness/bin/ that suite_layout.violations() forbids, and justified D-04/D-06 by UNIT_SCRIPTS/INTEGRATION_SCRIPTS/KINDCHECK machinery absent from run-unit-tests.sh. FEAT-47-tests-layout merged AT the plan's own declared base commit b7956fc4, so the plan was drafted against the layout that merge replaced. Four goal-check cycles and three panel cycles read it and none noticed; the c3 panel's own adequacy_notes said it could not distinguish a plan that will BUILD from one that READS. The first build dispatch found it in one member spawn.
- 2026-09-02: cheap pre-dispatch check that would have caught the above in seconds: resolve every task's declared `files:` path against the gate that governs that directory, before the first build dispatch. I ran `os.path.exists` over all 12 tasks' files: after the lead came back BLOCKED and it exposed the whole class at once (5 ABSENT paths where the task says "extend"), not just T-09's.
- 2026-09-02: `git merge-base main HEAD` stopped agreeing with a plan's pinned base SHA after the branch was rebased (returned 0ec44965 where the plan pins b7956fc4). Both were valid; the pin was still an ancestor. Pre-measuring which one the task means, and saying so in the dispatch, stopped a member re-deriving the wrong one.
- 2026-09-02: running `gh-sync.py open` mid-build to close INV-26's "the mirror never ran" traded one violation for twelve: `open` creates cards at backlog, and the signature-time promotion to `ready` is the main session's row in DEC-138's one-owner table, so the orchestrator cannot close the loop it opened. Reported it up rather than writing another owner's column.
- 2026-09-04: FEAT-54 ship. The feature's own new CI step (`Repository-state gate`, added
  post-review as B-5) was red-by-construction on every GitHub runner — `check-state.sh` INV-31 asks
  whether THIS MACHINE has `core.hooksPath` installed, and `actions/checkout` never sets it. It had
  never been exercised in CI before the ship PR, because a workflow step only runs when a PR exists.
  Lesson: when a change ADDS a step to the required check, the only proof it can pass is a fresh
  `git clone` of the branch with CI's own conditions (hooksPath unset, gitignored runs tree absent)
  — the local repo passes because the local repo is configured. Two-arm probe: unset -> exit 1 with
  exactly that violation, configured -> exit 0 over 877 rows.
- 2026-09-04: FEAT-54 ship. Probed `check-domain.sh` in enforcement mode with a hand-built
  PreToolUse payload to ask whether the orchestrator may write `.github/workflows/tests.yml`. All
  four arms exited 0, INCLUDING the control (another agent's Expertise file, which must be denied) —
  the payload shape was wrong and the guard fail-opens on it silently, exactly as its own header
  comment warns. Discarded the probe rather than the control. `--resolve <path>` is the only
  route-answering surface I could trust; it named `harness-dev-ops`, and the routing decision then
  rested on DEC-174 and the feature's own recorded lane, not on the guard.
- 2026-09-04: FEAT-54 ship. The pre-merge record commit is the only place a PR number can be
  recorded: `pr:` is known at `gh pr create` time, the merge SHA is not, and nothing can commit to
  the branch after the merge. Precedent confirms it — FEAT-52's `pr: 1275` landed on its own branch
  before merge commit `39bfad6d`.
