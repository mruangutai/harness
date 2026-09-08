# STATE

## Current

- feature: BUG-1309-mirror-build-entry
- run: c15 validate — `runs/2026-09-08-c15-validator/` (panel + gate-only qa) and
  `runs/2026-09-08-c15gc-product/` (goal-check), dispatched concurrently, read-only, disjoint files.
- squad: validator + product
- station: **review** (`plan.yaml:24`, unchanged). All thirteen tasks read `done`.
- `review_sha`: **e374c9a29e4321968e4c2a6bbae045da9203440c** — re-pinned this round and verified
  equal to HEAD before either run was dispatched. `plan.yaml` untouched since the pin, so INV-33
  stays quiet.
- status: **NOT shippable, and the cycle budget is EXHAUSTED** — `cycles_used` 14 of 14. No further
  fix cycle may open without the operator raising the budget.
- Both approvals still cover the current text (`plan.yaml:3-6`, `BRIEF.md:181-185`).

### What e374c9a2 fixed, measured not assumed

`git_merge()` now splits the old single `takes_value` set into `global_values` (pre-subcommand) and
`merge_values` (post-subcommand) and keeps walking after the `merge` token instead of returning
`rest[index + 1]`. Orchestrator measurement at this pin:

- `tests/integration/test-merge-gate.py` exit 0, **27 cases ALL PASSED** (3 new: `--no-ff`,
  `--squash`, `-m message`). `tests/integration/test-gh-sync.py` exit 0 / 323 ok / 0 FAIL;
  `tests/unit/test-gh-sync-build-entry.py`, `test-feature-schema-build-entry.py`,
  `test-omp-hooks.py` all exit 0.
- End-to-end through the real hook (`/tmp/bug1309-final-probe.py`, 23 checks): 14 deny forms
  (incl. `--no-ff`, `--squash`, `-m 'wip merge notes'`, `-s ours`, `-X ours`,
  `--strategy-option=ours`, `--into-name main`, `git -c … merge --no-ff`, `bash -c` wrapped) all
  DENY; 9 preserved bounds (healthy `opened`, era-exempt, `git merge-base`, `git commit -m 'merge
  …'`, `git status`, no-record + malformed record, single owner + malformed record) emit NO
  decision. **VP-01's named forms are closed**, and the 3 added test cases are DISCRIMINATING
  against `da6da610` (parser-level old-vs-new diff).

### Why it still does not pass — the CLASS survived the instances

Both sets are closed enumerations of option NAMES; signed T-05 step 2 (`plan.yaml:1029-1033`)
required value-taking options be handled **as a class**. Three current defects, each re-derived by
the orchestrator against **real git 2.50.1** (does git actually merge?) and the real hook (what does
the gate decide?) — `/tmp/bug1309-c15-verify.py`:

| form | real git | gate | verdict |
|---|---|---|---|
| `git merge -F <file> feature/test` | **MERGED** | **none — silent allow** | VF-01 high, fails OPEN |
| `git merge --cleanup strip feature/test` | **MERGED** | **none — silent allow** | VF-01 high, fails OPEN |
| `git --attr-source HEAD merge --no-ff feature/test` | **MERGED** | **none — silent allow** | VF-02 high, fails OPEN |
| `git merge --abort` | n/a (rc 128) | **deny** | VF-03 med, NEW, fails CLOSED |
| `--file=<f>` / `--cleanup=strip` / `--exec-path=<p> merge` | MERGED | deny | correct |
| `git merge --no-ff feature/test` (control) | MERGED | deny | correct |

VF-03 is a regression this delta introduced: the parser returns `("git", None)` for
`merge --abort/--continue/--quit`, `head_branch` falls back to `local_branch(cwd)`, and the
operator's own merge-recovery commands are refused on a branch owing a receipt. The old parser
returned `--abort` as the ref, found no owner, allowed.

**VF-04 — the code grade is a FAIL, not a 4.** Re-measured at this pin:
`code-grade.py --base da6da610 --head e374c9a2` → `git_merge` CYCLOMATIC 8, COGNITIVE 15, ABC 16.1,
**GRADE 3 / BAR 4 / RESULT FAIL / SEVERITY high**. The grade-4 figure carried into this round's
dispatch is falsified by the tool at the current tip.

### One reported finding is FALSE and must not buy a cycle

pm's goal-check made `git --exec-path <path> merge <branch>` ("form 16") its single blocking
must_fix. **Real git does not merge there**: bare `--exec-path` with a detached argument prints the
exec path and exits 0, so there is no merge for a gate to catch. The panel reached the same
conclusion independently and recorded VP-02 MOOT. SC-04 clause (a) is unmet for VF-01/VF-02, not for
form 16.

### Panel dispositions, none gating alone

VP-02 moot (class survives as VF-02). VP-05 substantively falsified — the `open` deny does print the
realpath'd feature dir (`merge-gate.py:183-184`); the untested-substring half stands, pre-existing.
VP-03/VP-04/VP-06 unchanged and still open: `main()`/`feature_for()` carry zero changes in this
delta. qa returned `matrix_ok: true` and noted correctly that the matrix is near-vacuous here — no
matrix-required suite binds `git_merge`. Full text in the two run digests.

### Routing — still no lead owns the remedy

`merge-gate.py` and its integration bed are DEC-174 enforcement-layer files. Both leads reported
**0 send-backs**; no fix cycle was opened because no squad may execute one. The increment to 14 is
the unmet-SC re-validation itself (DEC-157), not squad rework.

### SC-10 UAT — script AMENDED, hand test still NOT requested

pm added **Step 3b** to `notes/uat-BUG-1309-mirror-build-entry.md` (+41/-5, verified on disk): three
deny forms after the receipt is owed, a `--no-ff` over-refusal check in the post-`open` allow step,
and a verdict line that now requires 3b. It deliberately does not cover `-F` / `--cleanup` /
`--attr-source`; adding them today would encode a known FAIL. **No UAT requested**: the operator
would be hand-testing a build with three measured silent allows.

### The canonical checker

`check-state.sh` findings about shared external worktrees and board/task divergence are NOT this
feature's state and were not treated as cleared. Its BUG-1309 rows remain the INV-22 run-count note
(46 runs against an informational 20) and pre-existing run-dir bookkeeping drift.

### Next, in order

operator decision on Q1 → operator edit of `git_merge` closing the value-taking option CLASS and the
`--abort` fallback → fixtures for the four shapes in the reserved bed → re-measure `code-grade` →
re-pin → re-run panel and goal-check → extend UAT Step 3b → SC-10 UAT → rewritten briefing → ship.

## Open Questions

- Q1 (blocking, operator — **budget-gating**) — SC-04 clause (a) is unmet for a CLASS, not a list:
  `git merge -F <file> <ref>`, `git merge --cleanup <mode> <ref>` and `git --attr-source <t> merge
  <ref>` all merge in real git and are silently ALLOWED. Fix (consume a detached value generically,
  or fail CLOSED when the ref cannot be identified), or overrule the clause with a recorded ruling.
  DEC-174-reserved, not delegable. **`cycles_used` 14 of 14** — either answer needs the budget
  raised before another validate round may run.
- Q2 (blocking-adjacent, operator) — VF-03: `git merge --abort/--continue/--quit` is now DENIED on a
  branch owing a receipt. New regression of `e374c9a2`, fails closed. Same one edit as Q1.
- Q3 (non-blocking, operator) — VF-04: `code-grade` reports `git_merge` GRADE 3 / BAR 4 / FAIL.
- Q4 (non-blocking, coverage) — the reserved bed has no fixture for the value-taking-option class,
  for `merge --abort`, or for SC-04 clause (c)'s unreadable-JSON / empty-file / non-string-branch
  noise shapes (probe-proven only).
- Q5 (non-blocking, harness defect) — a lead run returning a well-formed digest while the host
  reports `failed (exit 1)` / "yield with null data" was seen in earlier rounds; NOT seen in c15.
- The stale briefing at `notes/ship-review-2026-09-08-resume.md` and its B-1..B-13 backlog still
  await operator disposition; rewritten after Q1 lands, before the ship decision.
