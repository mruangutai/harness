# Ship review — FEAT-54, the ship run

**Recommendation: one line in `.github/workflows/tests.yml`, then merge. Do not merge as it
stands, and do not merge past the red check.**

The pull request is open — **#1285**, `feat/FEAT-54-handoff-done-when` → `main`, 45 commits, 0
behind. Ten of the eleven CI steps pass, including every suite and every gate this feature wrote.
The eleventh is the one this feature ADDED, and it cannot pass on a GitHub runner. It is the single
required context on `main` (`integration`, `enforce_admins: true`), so **nothing in this repository
can merge until it is fixed** — not this feature, not the next one.

The cause is one line and the fix is one line. Both are measured below, not inferred.

## F-01 — the blocker: FEAT-54's own CI gate step fails on every clone GitHub makes

The `Repository-state gate` step (added post-review as B-5, main-session-direct) runs
`check-state.sh` and exits on its status. On a CI checkout that checker reports exactly one
violation:

```
VIOLATION  INV-31: core.hooksPath is unset, not .claude/skills/harness/hooks
           — no harness hook runs on this clone.
```

INV-31 (FEAT-40) asks whether **this machine** runs the `post-merge` hook that runs `gh-sync.py
ship`. A GitHub runner never ships, and `actions/checkout@v4` never sets `core.hooksPath`, so the
answer is always no and the step is red by construction. It is not a defect in the handoff work,
and it is not a pre-existing condition: PR #1275 merged four steps ago without this step existing.

**Measured, two arms, in a fresh `git clone` of the branch at `91495a60` (`/tmp/feat54-ci-probe`,
CI's own conditions):**

| Arm | `core.hooksPath` | `check-state.sh` | Violations |
|---|---|---|---|
| 1 — as CI runs it | unset | **exit 1** | 1 — INV-31, and nothing else |
| 2 — remedy applied | `.claude/skills/harness/hooks` | **exit 0** | 0, over 877 rows |

Arm 2 also silences nothing: with the path configured, INV-31's second branch really does assert
that `hooks/post-merge` exists and is executable in the checkout, and it passes — so CI gains a
committed-state fact instead of losing one.

**The remedy** — inside the existing step, before it runs the checker:

```yaml
# CI IS NOT A SHIPPING CLONE. INV-31 asks whether THIS MACHINE runs the post-merge hook;
# actions/checkout never sets core.hooksPath, so the row is red by construction on every
# runner. Pointing it at the in-tree hooks directory makes the checkout a faithful working
# clone rather than suppressing the row — INV-31 then still asserts hooks/post-merge exists
# and is executable, which is a committed-state fact worth checking.
git config core.hooksPath .claude/skills/harness/hooks
```

**Why I did not apply it.** `.github/workflows/tests.yml` hosts the required check's own gate
steps. DEC-174 stops self-hosting at the enforcement layer, and this feature's own record already
settled the lane for this exact row: all seven post-review remedies, B-5 among them, landed
main-session-direct "because every remedy touches the enforcement tree DEC-174 reserves"
(`STATE.md`). The path resolver grants `.github/workflows/tests.yml` to `harness-dev-ops`, so a
squad dispatch would have been *available* — I refused it on the merits rather than on domain:
having a squad member edit the definition of the one required check is the act DEC-174 names.

## What this run did and did not do

Done: pushed the branch (new remote branch, no force needed — 0 behind `origin/main`, so no
`--force-with-lease` was required); opened PR #1285 with the verification record in its body;
recorded `pr: 1285` in `feature.json`; wrote `notes/handoff-ship.md`.

Not done, and each for a stated reason:

- **The merge.** Branch protection refuses it while `integration` is red, and `enforce_admins` is
  on, so there is no override to take and none should exist.
- **The station.** `plan.yaml` stays at `review`. Writing `done` over an unmerged, blocked feature
  would be a false record, and INV-28 does not fire until it is Done.
- **`gh-sync.py ship` / `record-pr`.** Both refuse at exit 1 while the feature directory resolves
  inside `.claude/worktrees/`, before any write. They run from the main checkout after the merge.
- **Worktree removal.** Never this agent's act (DEC-193): `git worktree remove` exits 0 from inside
  the tree it deletes. The `post-merge` hook takes it when `main` pulls.

## How this briefing was assembled

**No report round was spawned.** I read from disk: `STATE.md`, `plan.yaml` (station, approval,
lanes, task stations), `BRIEF.md` (requirements and all 15 criteria), and the previous briefing
`notes/ship-review-2026-09-03-review-c6-validator.md`, which is the record of the plan, build and
validate phases and names the digests it rests on. I did not re-read the 51 run directories, and
the phase summaries here are that briefing's, not re-derived. Everything about F-01 I measured
myself in this run, from the CI logs and the fresh-clone probe.

## Residual backlog

Strike any row by ID and it dies. **Anything not listed here is lost silently.**

| ID | Nature | What |
|---|---|---|
| R-1 | chore | Ledger entry `2026-09-02-goalcheck-c1-product` has no run directory. The run is real — its evidence is `notes/research-FEAT-54-goalcheck-plan-c1.md` — so the entry was kept: deleting it erases a recorded FAIL, and writing a digest invents one. Known ledger-floor gap |
| R-2 | chore | B-7's `eval` exclusion cites `signed: DEC-187`, the decision that signed `functional`'s exclusion on the same rationale. A DEC of its own for `eval` is a documentor dispatch if you want the record explicit |
| R-3 | chore | Local `main` is **4 commits ahead of `origin/main`** and unpushed — FEAT-52 and BUG-1157 record commits (`a12aa4e9`, `a85134aa`, `142baff2`, `0df47889`). Unrelated to this feature, but it means the post-merge `main` pull is a real merge, not a fast-forward |
| R-4 | chore | INV-28 still reports `BUG-1081-code-grade-enforcement` as Done with no pull request recorded. One command closes it: `gh-sync.py record-pr .harness/harness/features/BUG-1081-code-grade-enforcement` |
| R-5 | chore | Three legacy records carry INV-23 note rows (`FEAT-02`, `FEAT-05`, `FEAT-43` STATE.md sections and length; two feature.json over budget). Notes, not violations — but the new CI step prints them on every commit from now on, so they are noise with a fixed cost |

## Budgets

**Cycles: 22 of 30.** This run added none: F-01 was routed **up**, not back to a lead, and DEC-157
counts a FAIL routed back, an unmet-SC re-dispatch, or a lead-reported send-back. None applies.

**Runs: 51 against an informational budget of 20** — over by more than double, and unchanged by
this run, which spawned nobody. The previous briefing's read stands: the c4–c6 sequence earned its
runs, the four pre-signature plan panels are the weaker half of the story.

## What I need from you

1. **Apply the one line** above to `.github/workflows/tests.yml`, or tell me to route it to
   `harness-dev-ops` and overrule the DEC-174 reading.
2. **Then, in order:** commit and push it, let `integration` go green, merge #1285, pull `main`,
   run `gh-sync.py record-pr` and `gh-sync.py ship <feature-dir> --body-file <this note>` from the
   main checkout, and let the `post-merge` hook take the worktree. `notes/handoff-ship.md` carries
   that sequence with the traps attached.
3. **Strike any residual rows** you do not want carried.
