# STATE

## Current

- feature: FEAT-48-parallel-safe-suite
- run: `2026-09-02-c8-validator` (panel, FAIL) and `2026-09-02-18-product` (goal-check, ESCALATE)
- squad: validator, then product
- status: awaiting_user — **not shippable**; two `must_fix` and one operator ruling stand in the way

Station `review`. `review_sha: e64e863e`; `git diff --stat e64e863e..HEAD` touches only this
feature's own `.harness/` files, so grading at the pin grades the shipped code.

**The headline: the fix is real, and the review it had never had found a gate it does not clear.**

**What I verified myself, at my own tier, rather than accepting on report.**
- **All six in-file cases run unconditionally in CI and all six DISCRIMINATE.** `main()` calls
  `run_self_tests()` and returns 1 on any failure. Three monkeypatch probes, no edit to the
  checkout: blinding `scan_file` reddens the three red cases; an over-eager `scan_file` also reddens
  clean-controls and live-tree; patching `resolve_scan_root` so it never refuses reddens live-tree
  and root-refusal. **Cases that can never turn red: none.** That is SC-03's first half proven as a
  gate, not merely as text — the thing the previous round could only assert.
- **The c7 symlink HIGH is closed with a red proof.** The same probe run against
  `git show b86ce66a:run_pool.py` gives exit 0 and no `MUTATED` for both a dangling symlink and a
  directory symlink; the shipped copy gives `exit 1 MUTATED dangling` and `exit 1 MUTATED
  linked-dir`; the clean control stays exit 0 under **both**, so no false positive was traded.
- **SC-01, SC-04, SC-09 met**, and one `--kind all` green at the tip: exit 0, 63 files, 8 workers,
  48.87s, zero `FAIL`, zero `MUTATED`, `git status --porcelain` empty before and after.

**What blocks the ship — two `must_fix` from the c8 panel, and one signature.**
- **`code_grade: fail`, and the excuse for it does not survive.** Nine blocking records over
  `d135364e..e64e863e`, three of severity `high`. The panel's code reviewer partitioned them
  7 pre-existing / 2 introduced; **its own lead retracted that, and I confirmed why from source**:
  `gated_set` gates a function only when it has no pre-image or its grade WORSENED
  (`code_grade.py:427-431`), so an inherited-debt record is unrepresentable. All nine are FEAT-48's
  own, seven of them in three files that do not exist on `main`. The worst is
  `test-suite-independence.py:170 run_self_tests` — the very function the last fix added — at
  CYCLOMATIC 14 / COGNITIVE 29 / ABC 49.7. A non-relocating decomposition preserves coverage.
- **A new defect in the fix itself.** `run_pool.py:37-38` calls `os.lstat` on a directory symlink
  with no `OSError` guard, where the file loop nine lines below has one. I reproduced the asymmetry
  deterministically by injecting the failure with `islink` pinned True: the dir branch raises
  `FileNotFoundError` **out of** `snapshot()` — which `main()` calls outside any try, so the whole
  pool run aborts — while the identical failure in the file loop is swallowed. MED (it fails closed
  and needs a race), and the remedy sits inside the function the first item must decompose anyway.
- **SC-03 still needs the operator's signature**, unchanged in substance from last round and now
  seconded by pm: 9 of 10 SCs MET, SC-03 `unmeetable-as-written`, remedy **(B)** recommended — make
  the ten `ea6f51f` sites a review-time automated check rather than an in-CI clause, under which
  SC-03 reads MET at `e64e863e` with **no code left to write**. Remedy (A) buys the literal wording
  for ~22.6 MiB and 1023 commits fetched on every CI run.

**Every remedy is main-session-direct.** `.claude/skills/harness/bin/**` is `main-session-direct` by
DEC-174 policy carve-out (`plan.yaml:15-23`) — the glob IS granted to backend-dev and dev-ops, so
this is policy, not a missing grant. There is no lead I may route these to; they go up.

**Also open, none of them gating:** DEC-211:6601-6602 overclaims that a content-derived write inside
bin is still caught by the runtime snapshot — reproduced false (M5); `test-run-pool.py` still has no
`__pycache__` leg (M4); the clean control still omits the `src.replace(...)` shape; `run_pool.py`'s
`.pyc` skip is wider than SC-10's text licenses; `notes/measurements-parallel-suite.md` still holds
the pre-rewrite runs; the suite is green only with `HARNESS_AGENT_TYPE` unset.

Budgets: `cycles_used` stays **8 of 10** — both leads reported **zero** send-backs and I routed no
FAIL back, so no rework loop ran this round. `runs` is now **19 of an informational 20**: the next
run crosses it. Nineteen runs on one feature is long, and I will say plainly that they have earned
their place — the last three each closed something real (a wrong-premise criterion, a symlink
blindness, and now a first review of code that had never had one) — but the count is a signal and
the operator should see it before authorising more.

## Open Questions

- **BLOCKING — operator ruling, unchanged.** SC-03's ten-site clause cannot be met as written.
  **(B)** amend it to a review-time automated check (recommended by pm and by me), or **(A)** add
  `fetch-depth: 0` and assert the ten sites in CI. Either way it is a BRIEF amendment needing the
  signature. Under (B) nothing else about SC-03 remains to build.
- **Needs a call.** `code_grade: fail` is a real gate and the "inherited debt" reading of it is now
  disproven. Decompose `run_self_tests` (and `snapshot`) inside FEAT-48, or accept the grade
  explicitly and record the acceptance? It fires no SC clause, so it will not fail a goal-check.
- **Needs a call.** The `run_pool.py:37-38` guard: fix now alongside the decomposition, or backlog?
  It is one line and it sits in the same function.
- **Needs a call.** M4, M5, the missing `src.replace` control leg, the over-wide `.pyc` skip, and
  the stale `measurements-parallel-suite.md` — fold into the ship or take as backlog rows.
- **Backlog, not a gate.** The suite is not independent of the ambient environment: with
  `HARNESS_AGENT_TYPE` set, `test-plan-merge.py` fails 11 checks and the suite exits 1. pm rules
  this a genuinely new criterion no REQ or SC covers; it is pre-existing and the file is untouched.
- **Harness defect, not a FEAT-48 finding.** `harness-qa` returned `severity_max: medium` where the
  contract enum is `med`, and `validate-digest.py` accepted it. Raised, not normalised.
- Whether issue #1053 closes on ship remains the operator's call; its `## Scope` still reads
  "Folded into FEAT-47" and only the operator's hand fixes an issue body.
