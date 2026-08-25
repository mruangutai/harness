# plan-fix — four plan-text defects corrected, FEAT-34

**All four confirmed by measurement at `9165162`, all four fixed in `plan.yaml`. 13 tasks and 9
decisions stand; one decision added (D-10). No `traces:` changed, no SC changed, no BRIEF edit.
The task set changed, so `approval:` should be reset to pending by the main session — I cannot
write it and did not.**

## Defect 1 — REQ-04/SC-04 had no owner. Fixed by D-10.

Re-derived, not relayed:

- `classify(root)` runs ONE `git worktree list --porcelain` with `cwd=root`
  (`worktree_terminal.py:56-58`).
- `feature-worktree.py` `dest_for` (`:56-59`) joins `WORKTREES_SEGMENT` only to a resolved
  `owner_root`; `resolve_repo` (`:62-85`) returns `factory_config.workspace_path(...)` for a fleet
  repo. A served repo's worktrees are therefore inside a different git repository — structurally
  invisible to a `git worktree list` in the harness checkout.
- `test-worktree-terminal.py:382` calls `w.classify(repo2)` — directly on the second repository's
  own root. Ran it: **19/19 PASS**. Those 19 prove the per-repo predicate and prove nothing about
  one caller covering both, which is what SC-04 and T-07 (e) grade from ONE `check-state.sh` run.

**Where it lives: `worktree_terminal.py`, as `classify_all(root)`.** Cost priced both ways, in
D-10's `because:`. Short form: `check-state.sh` costs no rework (T-06 pending) but permanently
strands the logic on the lane whose only grader is `test-check-state.py` — a fleet fixture plus a
second real git repo plus a full gate run per posture branch — and splits the predicate D-02 says
must be one. `worktree_terminal.py` costs real rework (T-01/T-02 are `status: building` and green
today, both reopen), bounded because `test-worktree-terminal.py:337-406` already builds the
fleet-plus-second-repo fixture. One-time rework beats permanent leverage loss.

**Failure posture — three-way, and it is NOT D-05's copy.** INV-26/INV-30 record nothing offline
because their fact lives on GitHub; requiring it turns a pre-commit gate into an availability
dependency. Every fact INV-29 needs is local and decidable, so that trade does not transfer.

| Case | Posture | Ground |
|---|---|---|
| `fleet.yaml` fails to load | **blocking violation** | INV-25's import posture (`check-state.sh:1109`) — the file is tracked, so unloadable is a tree defect. DEC-193 am.1 already ruled a malformed `fleet.yaml` **fails closed** on the Bash write route |
| declared repo, checkout **absent** | **no record** | Decidable, not unknown: a directory that does not exist holds no worktrees. One rule for every repo — not the per-repository exception REQ-04 forbids |
| declared repo, checkout **present but unenumerable** | **blocking violation**, one repository-level `unresolved` record | REQ-06's own signed rule one level up: absence exempts, lookup failure does not |

The absent-checkout row is load-bearing, not convenient. Measured: `fleet.yaml` declares
`mruangutai/kaya-ai` (checkout present, zero linked worktrees) and
`mruangutai/harness-factory-smoke` (**no checkout at all**). Any other posture makes
`check-state.sh` red on this machine today for a kept fixture nobody provisioned.

## Defect 2 — T-01's zero-prefix-match contradiction. Confirmed. **The wrong line was the trailing one.**

`plan.yaml`'s step-5 bullet said absence is proven by no landed name equalling-or-beginning-with the
id → `exempt_absent`; the trailing paragraph said `unresolved` is for "a prefix matching zero landed
directories". Same case, two answers. **REQ-06 makes the bullet right**: it exempts a worktree
exactly when the default branch "genuinely carries no feature directory for it", and zero
equal-or-prefix matches *is* that condition. The shipped code and test (d) follow the bullet.
Fixed: the trailing paragraph now reads `unresolved` = prefix matching MORE THAN ONE, and the
"ANY other outcome" bullet's over-broad "a prefix of a directory that DOES exist" was narrowed to
"MORE THAN ONE" — the same defect, one sentence earlier.

## Defect 3 — T-05's verify was vacuous. Confirmed and replaced with a demonstrably discriminating one.

`run-unit-tests.sh integration` — bare positional — hits the else branch at `:33-36`, prints usage
and **exits 2 before** the drift detector (`:48-61`) or the kind cross-check (`:82-120`) runs.
`grep -c` printed `0` on the real tree. New verify: `--check-kinds` plus two explicit presence
greps, expecting exit 0 and `REGISTERED-BOTH`.

Discrimination demonstrated on three deliberately wrong copies of this tree:

| Wrong tree | Result |
|---|---|
| name dropped from `INTEGRATION_SCRIPTS` only | `MISCONFIGURED`, exit 2 |
| name dropped from `test_kinds.integration.detect` only | `KIND-DRIFT`, exit 2 |
| pre-T-05 state: both files absent, unmentioned in either list | `--check-kinds` **PASSES**; caught only by the greps, exit 1 |

The third row is why the greps are in the verify and not decoration.

## Defect 4 — T-03's CLI forms. Confirmed by running the real CLIs.

- `gh-sync.py <feature-dir> ship` → **exit 1**, `gh-sync: ERROR — ship is not a directory`. Real
  form is verb-first: `gh-sync.py ship <feature-dir>`.
- `feature-worktree.py remove <id>` → **exit 2**, `the following arguments are required: --repo,
  --id`. Real form: `remove --repo REPO --id ID`.

`post-merge-sweep.sh:140` and `:165-166` already use the correct forms; the plan text did not.

## Edits made

| Task | What changed |
|---|---|
| T-01 | `verify:` now asserts `classify_all` exists (fails today — red). Step-5 contradiction fixed both ways. `classify_all(root)` contract appended (D-10 a–e) |
| T-02 | Four `classify_all` cases appended: (i) one call, two repos, with the classify-only red proof; (j) absent checkout; (k) present-but-unenumerable, with both failing states; (l) unloadable fleet |
| T-03 | `gh-sync.py`/`feature-worktree.py` invocation forms corrected, with the measured wrong-form exit codes recorded |
| T-05 | `verify:` replaced; trailing "must print 0" replaced by the exit-0/`REGISTERED-BOTH` expectation plus why the old one was vacuous |
| T-06 | `classify(root)` → `classify_all(root)`, with the SC-04 reason. New message clause for a repository-level record: blocking, names the repo/fleet file, **carries no removal command** |
| T-07 | Case (e)'s fixture shape corrected to the fleet-resolved shape (a second repo cannot sit under the harness checkout's own `WORKTREES_SEGMENT`), plus the classify-vs-classify_all red proof |

Checks after editing: `plan.yaml` `safe_load`s; 13 tasks, 10 decisions; `approval:` byte-preserved
by `plan-merge.py`; `check-plan-routes.py` → **0 violations**, the same four D-09 DEVIATIONs;
`check-state.sh` → exit 0, no violation attributable to these edits.

## Open questions

- **Q1 (blocking on the operator, not on the build): approval resets.** `plan.yaml:7` says any
  change to the task set resets `approval:` to pending. Six task intents changed, one decision was
  added, and two `verify:` commands changed. The signature of 2026-08-24 covers none of it. I
  cannot write `approval:` and did not — it still reads `approved`. **The main session must reset
  it and the operator must re-sign before the build continues.**
- **Q2 (non-blocking): D-10's repository-level failure posture is graded by no SC.** T-02's new
  cases (j)(k)(l) cover it and trace REQ-04, so the requirement is tested; but SC-04 grades only
  the positive second-repo case. Adding an SC inside a correction is not available to me. Flagged
  so the operator can decide whether the BRIEF wants one.
- **Q3 (non-blocking): T-01 and T-02 must be re-dispatched.** Both are `status: building` and
  measured green at 19/19 today; D-10 reopens both. That cost is reported now rather than
  discovered at the gate.
