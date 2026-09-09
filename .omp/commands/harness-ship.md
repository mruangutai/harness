# /harness-ship — build, validate, and bring a planned feature to the ship decision

Read `.claude/commands/harness.md` and follow it with **mission: ship**. The differences:

- **Precondition, hard:** BRIEF *and* PLAN both `status: approved`. Anything less routes to
  `/harness-plan` — the orchestrator will refuse anyway (playbook step 1), so catch it here.
- **Precondition, mechanical — the worktree must not be behind the default branch.** After step 0b
  names the worktree and **before any orchestrator is spawned**, run:

  ```
  python3 .claude/skills/harness/bin/feature-worktree.py behind --repo <repo> --id <flow-id>
  ```

  Exit 0 means current. **Exit 6 means REFUSED**: it prints the count, every missing commit's
  subject, and the `git -C <path> merge <branch>` command that fixes it. Run that, re-run the check,
  then spawn. Exit 3 means there is no worktree at that path — cut it at step 0b first.

  This is not belt-and-braces. Measured 2026-08-21: FEAT-31's worktree sat **six** commits behind
  `main` at the moment its build was about to be dispatched, and the gap held `expertise-merge.py`
  and DEC-197 — a tool and a decision that two of that plan's own tasks needed. The build would have
  re-derived a rule it should have cited, against a tree that did not contain it. Nothing reported
  it; the operator asked.

  **It compares against LOCAL `main`, deliberately.** `gh` was considered and rejected on a
  measurement: none of the three in-flight feature branches existed on the remote, because nothing is
  pushed until PR time, so `gh` would answer "no such branch" for exactly this case. The accepted
  cost is that a stale local `main` makes the count a floor rather than a ceiling — it never accuses
  a tree that is current.

  **What it does NOT catch:** a build that starts current and drifts behind while it runs. This fires
  at the door, once, not mid-flight.
- The orchestrator sequences the squads (build → qa gate → review panel → goal-check → docs) and
  owns the fix cycles and both budgets.
- **Terminus:** the CEO briefing, presented by you verbatim. The user decides ship / fix first /
  re-scope / stop. PR and merge follow their call — never automatically.
