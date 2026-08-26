# EFFICIENCY angle — FEAT-34 four-angle quality pass

FLAG-ONLY. No edits applied, no git mutation performed. Two findings, both real network-I/O
waste in `check-state.sh`'s INV-30 (T-08, unreviewed `main-session-direct`), weighted first per
dispatch. `worktree_terminal.py` (T-01/T-02) and `post-merge-sweep.sh` (T-03) are measured clean.

## Method

- Baseline: extracted pre-diff `check-state.sh` at `9165162` via `git show`, ran it with
  `PYTHONPATH=<bin>` (dirname-based sys.path resolution breaks when copied elsewhere) —
  `time PYTHONPATH="$BIN" bash check-state-base.sh` → **11.414s** wall clock, exit 0.
- Post-diff, same repo state: `time bash .claude/skills/harness/bin/check-state.sh` → three
  runs: **14.935s, 11.315s, 12.177s**, all exit 0. Variance tracks network jitter from the two
  new `gh` calls (below), not the script itself.
- `time gh auth status` → **0.304s** (real network round trip, logged-in session).
- `time gh api --paginate "repos/mruangutai/harness/milestones?state=open&per_page=100" -q ".[].number"`
  → **0.475s**.
- Confirmed `gh auth status` does not fail fast when the network is *slow-but-reachable* (as
  opposed to *absent*, which the INV-30 comment explicitly designs for): routed through an
  unroutable proxy (`HTTPS_PROXY=http://10.255.255.1:1`) with a 3s test timeout, the call
  blocked for the full **3.003s** rather than erroring immediately — confirms it genuinely waits
  on the network rather than reading cached local state.
- `classify_all(root)` (INV-29, T-01/T-02) timed directly: **0.236s**, 5 worktree records, all
  `exempt_absent`, no fleet repos declared. Subprocess count: 1 `git worktree list` + ~2 per
  worktree (`git status --porcelain`, `git ls-tree`) ≈ 11 subprocesses total.
- `post-merge-sweep.sh 0 --dry-run` timed directly: **0.238s, 0.226s** across two runs, zero
  terminal records in this tree (no gh calls on this path — dry-run and no terminal worktrees).
- This repo's own `github.sync` is `true` and `github.repo` is set (`.harness/harness.json`),
  so INV-30's network path is the live path here, not a hypothetical.
- `gh_bin` / `gh auth status` cross-check: grepped `check-state.sh` for `_gh_bin`/`subprocess.run`
  — INV-26 (pre-existing, not part of this diff) already runs its own `gh auth status` at
  check-state.sh:1397, gated the same way (`github.sync` + `github.repo` + a declared board,
  which this repo has).

## Finding 1 — INV-30 re-runs `gh auth status`, duplicating INV-26's own call in the same script run

`.claude/skills/harness/bin/check-state.sh:1602-1605` (INV-30) duplicates the identical
`gh auth status` call INV-26 already makes at `check-state.sh:1397`, in the same script
invocation, under the same gating condition (`github.sync: true`, `github.repo` set — both
true in this repo). Neither block reads the other's result.

**Cost, measured:** `gh auth status` costs 0.304s per call (see Method). Both INV-26 and INV-30
run it unconditionally on every `check-state.sh` invocation in this repo (INV-26 gated on a
declared board, which this repo has at `harness.json`'s `github.board`; INV-30 gated on
`github.sync` + `github.repo`, both true). That is ~0.6s of network round trip spent proving
the same fact twice, on a gate the CLAUDE.md convention says to run before every commit.

**Alternative:** compute the auth check once (INV-26 already computes `_gh_ok` at line 1399)
and thread that result into INV-30's `_gh_ok30`, only re-running the probe if INV-26's block did
not execute (e.g., no board declared). Saves one full network round trip per invocation in the
common (both-configured) case, which is this repo's actual configuration today.

severity: low
call: backlog row after ship

## Finding 2 — INV-30's two timeouts (15s + 60s) stack a 75s worst-case stall onto a
pre-commit / session-entry gate, on top of INV-26's pre-existing 15s

`.claude/skills/harness/bin/check-state.sh:1602-1622` sets `timeout=15` on the `gh auth status`
call and `timeout=60` on the `gh api --paginate milestones` call. Both fire unconditionally
(subject to Finding 1's gating) on a script the project convention runs "before every commit"
and (per this pass's dispatch) at every session entry.

**Cost, measured/derived:** confirmed empirically (unroutable-proxy test, Method) that
`gh auth status` blocks for the network's full latency rather than failing fast on a
slow-but-reachable connection — the offline posture the code's comments describe (`gh` absent,
unauthenticated) is not the only way this stalls; a merely *slow* connection pays the timeout in
full. `gh api`'s real median cost is 0.475s (measured above); the code budgets 60s for it — over
120x the observed cost. Combined with INV-30's own 15s auth timeout and INV-26's pre-existing
15s auth timeout (unaffected by this diff, cited for scale), a degraded-but-not-down network can
now stall this gate for up to 15 (INV-26) + 15 (INV-30 auth) + 60 (INV-30 api) = 90s in the worst
case — up from a 15s pre-existing ceiling, an addition of 75s attributable to this diff.

**Alternative:** shrink INV-30's timeouts toward the measured reality — a 5s auth-status budget
and a 10-15s milestone-list budget cover any genuinely slow-but-working connection while capping
the worst-case stall this diff adds at ~15-20s instead of 75s. (Combining with Finding 1's fix
removes the redundant 15s auth timeout entirely, leaving only the milestone-list budget to
tighten.)

severity: med
call: fix cycle before ship

## Clean — no finding

- `worktree_terminal.py`: no closures capturing scope, no long-lived objects. `_import_feature_worktree()`
  re-execs `feature-worktree.py` via `importlib` on every `classify()` call rather than caching
  in `sys.modules` — measured cost: 20 calls in **0.00197s** (≈0.1ms each). Not worth flagging.
- `classify_all` (INV-29): 0.236s / ~11 subprocesses for this repo's 5 worktrees — proportionate
  to the real work (one `git worktree list` per repo, a bounded few `git` calls per worktree),
  and this repo declares no fleet repos so cross-repo fan-out is untested here but the mechanism
  is linear in worktree/fleet-repo count, not obviously wasteful.
- `post-merge-sweep.sh`: 0.226-0.238s in front of a human waiting on `git merge`, negligible.
  Its ship-then-remove path (real gh-sync + feature-worktree calls on a genuine terminal record)
  is necessary work, not waste — not measured further since this tree has no terminal worktree to
  exercise that path against.
- `run-unit-tests.sh`'s `INTEGRATION_SCRIPTS` diff: all three new test files
  (`test-worktree-terminal.py`, `test-post-merge-sweep.py`, `test-hooks-install.py`) are added to
  the array the runner actually executes — confirmed by reading the array literal, not
  `harness.json`'s detect globs. Not an efficiency finding (correctness/reuse territory), noted
  per dispatch instruction only.

## Addendum — the double-detect-match question, measured

The operator supplied the observation that `harness.json`'s `unit.detect` glob
(`.claude/skills/harness/bin/test-*.py`) and `integration.detect`'s explicit enumeration both match
all three new test files. Answered directly, per-question:

**Q1 — which array actually runs them.** Read `run-unit-tests.sh:17-18` (`UNIT_SCRIPTS` /
`INTEGRATION_SCRIPTS` literals, not the detect globs). All three names
(`test-worktree-terminal.py`, `test-post-merge-sweep.py`, `test-hooks-install.py`) appear only in
`INTEGRATION_SCRIPTS`. Cross-checked programmatically: `set(UNIT_SCRIPTS) & set(INTEGRATION_SCRIPTS)
== set()` — the two arrays are disjoint with zero overlap (21 unit + 25 integration, 46 total, no
shared name). `--kind unit` cannot select them; `--kind integration` is the only kind that runs them.

**Q2 — does the double glob-match cause a double run.** No. Measured directly by running
`.claude/skills/harness/bin/run-unit-tests.sh --kind integration` to completion (held the SOLE
Q8 permit for this dispatch; ran once, alone):
`real 287.16s / user 82.82s / sys 41.85s`, exit 0, all 25 `INTEGRATION_SCRIPTS` entries reporting
`PASS <script>`, including the three new files — `test-worktree-terminal.py` and
`test-hooks-install.py` each printed `EXIT=0` / `PASS <name>`, `test-post-merge-sweep.py` likewise
(full transcript in the 287s run; tail-truncated capture shows the last two plus
`test-post-merge-sweep.py`'s closing lines). Each script's own process tree was observed exactly
once per name across the run (tracked live via `ps -g <pgid>` at ~3-4s intervals throughout — no
repeat sightings of any of the three names). A file's selection is governed exclusively by
`SCRIPTS=("${UNIT_SCRIPTS[@]}")` / `SCRIPTS=("${INTEGRATION_SCRIPTS[@]}")` per `--kind`
(`run-unit-tests.sh:23-26`) — the detect globs in `harness.json` are never read by this script at
all except by the kind-cross-check (`run-unit-tests.sh:82-116`), which only asserts agreement
between `INTEGRATION_SCRIPTS` and `integration.detect`'s explicit paths and never touches
`unit.detect`. A `qa` pass running `--kind unit` then `--kind integration` back to back therefore
executes each of the 46 listed scripts exactly once, total.

**Q3 — why the double glob-match is harmless.** Array membership, not glob matching, decides what
`run-unit-tests.sh` executes. The `unit.detect` glob's `test-*.py` catch-all exists to feed
`qa`'s diff-scan classifier (which kind must run given which files changed in a diff) — a
different consumer entirely from `run-unit-tests.sh`'s own selection logic. Two files can match
the same detect glob without ever running twice, because the glob only ever decides "is this kind
required", never "run this specific file". The one place that WOULD matter — a name present in
both `UNIT_SCRIPTS` and `INTEGRATION_SCRIPTS` — is independently confirmed empty above. **Measured
wall-clock caveat:** 287.16s for `--kind integration` alone is markedly slower than the ~15.6s the
script's own top-of-file comment documents as the historical full-suite baseline (all 46 scripts,
unit+integration). Observed via live `ps` sampling: real subprocess forks (`gh api rate_limit`,
`git merge --squash`, `factory_decompose.py`, several `check-domain.sh --resolve` calls per test)
account for genuine work, and two unrelated local `mcp` python processes were running concurrently
on this machine throughout — the elevated wall-clock is not attributable to this diff or to the
double-detect-match; it is machine-load variance in this one measurement, not a claim about typical
CI cost. Flagged as measured, not diagnosed further (out of this angle's scope).

- Did not re-run the full unit/integration suite ahead of this addendum: this angle's original
  findings rest on direct wall-clock timing of the actual runtime code paths (`gh`, `classify_all`,
  the sweep script), which is more precise for a hot-path cost question than a pytest pass/fail
  count would be, and P-16 applies. The addendum above is the one exception — the operator's
  question is specifically about `run-unit-tests.sh`'s own execution behavior, which only running
  it settles.

```yaml
VERDICT: PASS
DIGEST:
  headline: INV-30 pays a redundant gh-auth round trip INV-26 already made, its 60s milestone-list timeout can stack a 75s worst-case stall onto a pre-commit gate, and the addendum's double-detect-match is harmless — array membership, not the glob, decides execution
  change_type: infra
  applied: []
  suite: pass
  task: none
  open_questions: []
  files_touched: []
  expertise_update: []
  test_kinds_written: []
  suite_note: "ran run-unit-tests.sh --kind integration once (SOLE Q8 permit, held alone, per addendum): real 287.16s / user 82.82s / sys 41.85s, exit 0, all 25 INTEGRATION_SCRIPTS PASS including the 3 new files. --kind unit not run — UNIT_SCRIPTS/INTEGRATION_SCRIPTS confirmed disjoint by direct set comparison, so a separate unit run cannot re-execute any of the 3 new files and was not needed to answer the addendum's question"
  measurements:
    - "check-state.sh baseline (pre-diff, 9165162): 11.414s wall clock"
    - "check-state.sh post-diff (513c4a4): 14.935s / 11.315s / 12.177s across 3 runs"
    - "gh auth status: 0.304s"
    - "gh api --paginate milestones: 0.475s"
    - "gh auth status under simulated slow network (unroutable proxy, 3s test timeout): blocked full 3.003s, confirmed no fast-fail"
    - "worktree_terminal.classify_all: 0.236s, ~11 subprocesses, 5 worktree records"
    - "post-merge-sweep.sh --dry-run: 0.226s / 0.238s across 2 runs"
    - "run-unit-tests.sh --kind integration (addendum, full 25-script run, all 46 UNIT+INTEGRATION scripts confirmed disjoint by set comparison): real 287.16s / user 82.82s / sys 41.85s, exit 0"
findings:
  - id: F1
    file: .claude/skills/harness/bin/check-state.sh
    lines: "1602-1605 (INV-30) vs 1397 (INV-26)"
    severity: low
    call: backlog row after ship
    summary: INV-30 re-runs gh auth status, identical to INV-26's own call in the same invocation
  - id: F2
    file: .claude/skills/harness/bin/check-state.sh
    lines: "1602-1622"
    severity: med
    call: fix cycle before ship
    summary: INV-30's 15s+60s timeouts stack a 75s worst-case stall onto a hot gate, on top of INV-26's pre-existing 15s
artifact: .harness/harness/features/FEAT-34-worktree-act3-enforced/notes/receipt-harness-dev-ops-simplify-efficiency.md
```
