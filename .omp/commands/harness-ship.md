# /harness-ship — build, validate, and bring a planned feature to the ship decision

Read `.omp/commands/harness.md` and follow it with **mission: ship**. The differences:

- **Precondition, hard:** BRIEF *and* PLAN both `status: approved`. Anything less routes to
  `/harness-plan` — the orchestrator will refuse anyway (playbook step 1), so catch it here.
- **Precondition, mechanical — the worktree must not be behind the default branch.** After step 0b
  names the worktree and **before any orchestrator is spawned**, run:

  ```
  python3 .claude/skills/harness/bin/feature-worktree.py behind --repo <repo> --id <flow-id>
  ```

  Exit 0 means current. **Exit 6 means REFUSED**: it prints the count, every missing commit's
  subject, and the command that fixes it. Run that, re-run the check, then spawn. Exit 3 means
  there is no worktree at that path — cut it at step 0b first.

  This is not belt-and-braces. Measured 2026-08-21: FEAT-31's worktree sat **six** commits behind
  `main` at the moment its build was about to be dispatched, and the gap held `expertise-merge.py`
  and DEC-197 — a tool and a decision that two of that plan's own tasks needed. The build would have
  re-derived a rule it should have cited, against a tree that did not contain it. Nothing reported
  it; the operator asked.

  **It compares against `origin/main` after one fetch (#1850).** Until 2026-09-22 it compared
  against LOCAL `main`, on the reasoning that feature branches are not on the remote before PR
  time — true, and beside the point, because the target is the default branch. Measured cost of
  the old target: FEAT-61's local `main` had missed one merge, the door printed `current with
  main`, and the PR was CONFLICTING with zero CI runs. When the fetch fails it falls back to LOCAL
  `main` and says `COULD NOT FETCH` on stderr — a named fallback, and then the count is a floor.

  **What it does NOT catch:** a build that starts current and drifts behind while it runs. This fires
  at the door, once, not mid-flight.
- The orchestrator sequences the phases (build → SIMPLIFY → one pinned `review_sha` → one `validate`
  run holding qa, code, security, ui and pm's goal-check → `fix` rounds inside the signed rework
  ruling → docs) and owns the cycle budget and the ledger.
- **Terminus:** the CEO briefing, presented by you verbatim. The user decides ship / fix first /
  re-scope / stop. PR and merge follow their call — never automatically.
