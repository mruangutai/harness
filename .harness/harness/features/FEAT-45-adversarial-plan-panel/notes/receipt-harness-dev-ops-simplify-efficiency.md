# EFFICIENCY angle — FEAT-45-adversarial-plan-panel

**Conclusion: no findings.** Measured every candidate hot-path and suite-cost claim in the
dispatch; every one comes back negligible or explicitly sanctioned as evidence, not waste.

## 1. INV-32 in `check-state.sh` — read the branch

`.claude/skills/harness/bin/check-state.sh:174-238`. Confirmed by reading the surrounding
script (`:48` shows the WHOLE file is one `python3 -c ... <<'PY'` block — a single interpreter
for all ~30 invariants, so INV-32 spawns **no extra python3 process**), and by grep for
`panel_findings|subprocess\.` inside the block (none): INV-32 does zero subprocess calls, zero
new `glob`, zero new file reads. It iterates `plan_docs`, a dict already built once at
`check-state.sh:98-108` for other invariants, and is gated behind
`approval.status == "approved"` before touching `panel` at all (`:178`). The expensive case
(iterating `findings`/`rulings`/`readers` lists) only runs for a plan that is both approved
and carries a panel record — a small, bounded set. Cheap predicate gates the only per-item
work; nothing here runs unconditionally on every session entry beyond a dict `.items()` walk
over data already in memory.

## 2. Measured: `check-state.sh` before vs. after — delta is noise

Compared HEAD against the merge-base (`1d3e5db`) by extracting the old script + its
`harness_boundary.py`/`harness_yaml.py` deps to `/tmp` (never wrote into or moved the
worktree) and running both against the **same** worktree state via
`HARNESS_PROJECT_DIR` override, interleaved, using `/usr/bin/time -p` (not the shell `time`
builtin — that measurement in isolation showed a spurious ~1.1s "CPU" gap that vanished under
clean `time -p`, confirming it was measurement artifact, not signal — see `test_verified` below):

| run | new (HEAD) real/user/sys | old (1d3e5db) real/user/sys |
|---|---|---|
| 1 | 10.06 / 0.88 / 0.53 | 10.22 / 0.87 / 0.51 |
| 2 | 10.38 / 0.87 / 0.52 | 10.38 / 0.89 / 0.54 |
| 3 | 12.08 / 0.90 / 0.55 | 10.60 / 0.87 / 0.51 |

User time is identical to within 0.03s across all six runs. Real time (~10-12s) is dominated
by unrelated network-bound subprocess calls already in the script (`gh auth status`, `git
worktree list`) — present in both versions, unaffected by this diff. **Delta attributable to
INV-32: unmeasurable, well under noise.** No finding.

## 3. New/changed test scripts — measured suite-cost contribution

Ran each in isolation, worktree root, `time -p`:

| script | time | checks |
|---|---|---|
| `test-panel-findings.py` (new, unit) | 0.12s | 9/9 pass |
| `test-plan-panel.py` (new, unit) | 0.29s | 24/24 pass |
| `case_inv32()` alone inside `test-check-state.py` (integration, pre-existing file) | 2.59s | pass |

`case_inv32()`'s 2.59s comes from ~12 real subprocess invocations of `check-state.sh` against
minimal fixtures (no network, no real repo) — this is the mutation-kill discriminator proof
(`inv32-red`: deletes the marked region, confirms the check goes silent), explicitly the kind
of boundary evidence the skill says is not waste ("deliberate full-suite runs... are the
evidence the boundary exists"). Total new suite-time contribution across all three:
**~3.0s**, added to a runner (`run-unit-tests.sh`) that already executes 53 scripts
sequentially. Not flagged — this is normal test cost for a new module, and the runner's
sequential (non-parallel) execution is pre-existing, unchanged by this diff.

`run-unit-tests.sh`'s own diff: two `UNIT_SCRIPTS` array entries appended
(`test-panel-findings.py`, `test-plan-panel.py`); zero structural change.

## 4. `panel_findings.py` CLI — invocation pattern

Confirmed by grepping the diff for every caller: `harness-pm` (via `harness-spec-driven`
SKILL.md, `PLAN.md`/plan.yaml prose) invokes the CLI **once per finding at transcription
time** — plan-authoring time, not session-entry, not a hot path, and by design (D-05: "the
ONE place a finding's identity is computed... computed ONCE"). A handful of findings per panel
run means a handful of ~30-50ms python3 startups at a build-time step. No loop-invoking-
subprocess-per-item pattern at any hot path. No finding.

## 5. `test-plan-panel.py`'s 24 checks — read pattern

Verified by reading the file: each source (`SKILL.md`, `plan-panel.yaml`,
`harness-plan.md`, `harness-validator-lead.md`) is read into a variable **once**
(`:124`, `:233`, `:253`, `:270`) and all checks against that source run as in-memory string ops
on the already-read variable — not the "24-check re-read the same file" shape the dispatch
flagged as the likely candidate. That shape does not occur here. No finding.

## Findings

`findings: []`. Every candidate in the dispatch was measured directly; none crosses from
"unmeasured suspicion" to "real cost." The INV-32 branch is exactly what a session-entry gate
addition should look like: reuses existing parsed state, gated behind a cheap predicate,
zero subprocess, zero extra I/O.
