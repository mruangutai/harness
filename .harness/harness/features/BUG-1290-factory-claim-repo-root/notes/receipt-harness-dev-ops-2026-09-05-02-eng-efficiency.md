# Receipt — harness-dev-ops — EFFICIENCY angle + A1 probe — BUG-1290-factory-claim-repo-root

**BLUF:** A1 probe done — both files are green (not yet red) at the pre-task baseline, as
expected since T-01/T-02 haven't executed. No unrelated-red risk found strong enough to worry
about, but the file has zero case-selection mechanism, so T-02's `verify:` cannot be narrowed to
"run only the (F) case" — only narrowed to "assert the (F) case's own FAIL marker in the captured
output of the full run." EFFICIENCY angle proper on the plan: **no findings**. Total measured
cost of every task's `verify:` in this plan is ~21s, none of it a hot path or session-entry gate;
the two full-suite runs (T-02, T-03) are the deliberate boundary evidence the skill says not to
flag.

## A1 probe

| | unit (`test-factory-claim.py`) | integration (`test-factory-integration.py`) |
|---|---|---|
| exit | 0 | 0 |
| wall time | 0.121s | 9.568s |
| failing cases | none (120/120 pass) | none (131/131 pass) |

Both green at HEAD (eb9d044e), unchanged. This is the correct pre-task baseline: T-01 hasn't
added the new unit cases yet and T-02 hasn't moved the integration fixture yet, so there is
nothing in either file today that could be red. **`already_red: false`.**

**Unrelated-red risk, one line:** low but non-zero — no network/`gh` dependency (gh is a local
stateful stub, git is hermetic-configured real git), but cases (G), (I)–(N) fork real `python3`/
`git` subprocesses and every case shares one module-level `FAILS`/`RAN` counter with no per-case
isolation, so a toolchain-version difference or a leftover temp-dir timing issue in an unrelated
case could turn the file's exit code non-zero for a reason that has nothing to do with BUG-1290,
and T-02's current `verify:` (bare `test $? -ne 0`) cannot tell the two apart.

**Case-selection mechanism, read directly (`tests/integration/test-factory-integration.py`):**
none. Confirmed by grep — no `argparse`, no `unittest`/`pytest`, no env-var case filter. It is one
flat top-to-bottom script (`check(name, cond, detail)` at :74-81, incrementing global `FAILS`/
`RAN`, final `sys.exit(1 if FAILS else 0)` at :1653) that runs every one of its 131 checks in
sequence, unconditionally. There is no way to run a subset without editing the file.

Traced the exact regression T-02 delivers: after moving `feat_dir` to the `widget` segment
(:882), the decompose step (:902) still succeeds because it takes `feat_dir` as an explicit CLI
arg. The claim step (:924) does not — it depends on `factory_claim`'s resolver, which (unpatched)
still hardcodes `.harness/harness/features` and will not find the moved plan, so claim reports
`no_plan`/no work and exits 1. The first check that reddens is **`(F) claim exits 0`** (:925);
everything after it in the `(F)` block cascades from that.

**Recommended `verify:`** — since the file supports no case selection, the narrowest honest
replacement still runs the whole file but asserts on the specific marker in its captured output,
rather than accepting any of the 131 checks' failure as proof:

```
cd /Users/molchairuangutai/GitHub/harness/.claude/worktrees/harness/BUG-1290-factory-claim-repo-root && out=$(python3 tests/integration/test-factory-integration.py 2>&1); printf '%s\n' "$out" | grep -q '^FAIL  (F) claim exits 0'
```

This keeps `test $? -ne 0`'s intent (T-02 delivers red) but ties it to the specific composed
claim case named in the task intent, not to whichever of the 131 checks happens to fail.

## EFFICIENCY angle — plan surface (BRIEF.md / plan.yaml)

**Findings: `[]`.** Measured, not assumed:

- T-01 `verify:` — unit file alone, 0.121s. Negligible.
- T-02 `verify:` — integration file alone, 9.568s, 131 checks. This is the only case where
  "re-run a whole suite where a targeted case binds equally" could apply, but the file has no
  targeting mechanism (see A1 probe above) — so running the whole file isn't wasted work, it's
  the only mechanism available. Not a plan defect; recorded as the A1 probe's `recommended_verify`
  instead, which narrows the *assertion*, not the *run*.
- T-03 `verify:` — re-runs both suites (0.121s + 9.568s) plus a trivial inline `python3 -c` file
  read (<10ms). This is the boundary step where production code lands; the skill explicitly
  names deliberate full-suite runs at boundary steps as evidence, not waste. Not flagged.
- T-04 `verify:` — `test-layout-migration.py` (measured: 1.347s) plus an inline
  `layout_migration.scan('.')` call (measured: 0.049s). The inline call duplicates a scan
  `test-layout-migration.py` likely already runs against fixtures, but it checks a different
  target (the real tree's `features` surface, not a fixture) — not the same work twice.
- Total measured cost of the plan's four `verify:` commands run in sequence: ~21s. No task's
  verify is a hot path, a session-entry gate, or a per-write gate (`check-state.sh`/INV-27 is
  manual-only per this agent's own project Expertise, G-01 — not invoked automatically at any
  boundary this plan touches).
- No same-file-re-read-across-tasks pattern: T-01 touches the unit test file only, T-02 the
  integration test file only, T-03 the four production files, T-04 the two layout files — no
  task's verify or intent re-reads a file another task's verify already consumed for the same
  purpose.

## Scope confirmation

- `BRIEF.md`, `plan.yaml`, every file under `.agents/skills/harness/bin/` and every file under
  `tests/` are byte-unchanged — both probe runs (`python3 tests/integration/test-factory-integration.py`,
  `python3 tests/unit/test-factory-claim.py`) and the two extra measurement runs
  (`test-layout-migration.py`, the standalone `layout_migration.scan('.')` inline check) executed
  a program; none edited a file.
- `git status --porcelain=v1` taken before the first run and again after the last run is
  identical: only the two pre-existing untracked feature-tree paths
  (`.harness/harness/features/BUG-1290-factory-claim-repo-root/`,
  `.harness/notes/grilling-factory-claim-repo-root-2026-09-05.md`), neither created by this
  agent. No artefact was left inside the worktree by either probe run.
