# EFFICIENCY angle — FEAT-56, simplify-c2 — receipt

**VERDICT: zero findings.** Every touched gate was measured; nothing costs materially more per
invocation than at `4b5dbb23`. Details and numbers below.

## Hot vs one-shot classification (wiring evidence)

| Script | Class | Evidence |
|---|---|---|
| `check-instruction-paths.py` | **HOT** — every subagent spawn | `.claude/settings.json:6-16` wires `inject-expertise.sh` to `SubagentStart`, matcher `harness-.*`; `inject-expertise.sh:68` calls `check-instruction-paths.py` |
| `check-omp-port.py` | **session-entry**, not hot | Called only from `check-state.sh:972-977`; `check-state.sh` is invoked once per door by `.claude/commands/harness.md:12` ("Run `check-state.sh`"), which `harness-plan.md`/`harness-ship.md`/`harness-grilling.md` all route through |
| `sync-command-adapters.py` | session-entry (via `check-omp-port.py --check`) + manual `--apply` (dev-invoked, one-shot) | subprocess call added at `check-omp-port.py:172-180`; no other caller found |
| `factory_config.py`'s new `product_config_report()`/`product_config()` | **one-shot**, CLI-only | Only reachable via `factory_config.py --check-product-configs` (`factory_config.py:448-479`) and `factory_decompose.py:377` (manual decompose tool). The diff's own comment at `factory_config.py:486-489` states this was deliberately kept OUT of `check-state.sh`'s per-door path. `check-domain.sh` (the true hot gate, wired to every `Write`/`Edit`) imports `factory_config` for `MANDATED_STATIONS`/`TERMINAL_MARKER` only — unchanged by this diff. |

## 1. Tree walks — no double walk found

- `sync-command-adapters.py` globs `.omp/commands` once and `.claude/commands` once — two different trees, one pass each (`sync-command-adapters.py:18-21,35`). Not a duplicate.
- The **new** block in `check-omp-port.py` (diff: `check-omp-port.py:168-182`) does **not** glob `.omp/commands` at all — it checks 4 fixed filenames exist, then shells to `sync-command-adapters.py --check` as a separate process. The pre-existing agent block is the identical shape (fixed-name/frontmatter loop + `sync-agent-adapters.py --check` subprocess). Two separate processes each walking once — not a same-process double walk.
- `check-instruction-paths.py`'s diff only adds one entry to an existing exclusion table (`harness-add-repo`); no new walk.

## 2. Subprocess cost — measured

Location matters more than the diff: an identical-content script run from `/var/folders` (temp,
outside the repo) timed 0.30–1.1s vs 0.13s from its real repo path — a 2–8x location artifact that
swamps anything this diff could add. Cross-location base-vs-head A/B is therefore invalid, so I
measured the true marginal cost directly and in isolation instead, same location both sides:

```
python3 sync-command-adapters.py --root <repo> --check   → median 0.044s (6 runs: .0476/.044/.0442/.0438/.0439/.0438)
python3 sync-agent-adapters.py   --root <repo> --check   → median 0.077s (6 runs: .0818/.0766/.0768/.0767/.0773/.0777)  [pre-existing, unchanged]
```

`check-omp-port.py` at HEAD, controlled (7 runs, same location): median 0.133s
(`.1425/.141/.1376/.1399/.14/.1374/.1358` then `.1349/.1377/.1329/.1325/.1309/.1319/.1314`).

**Verdict: the delta doesn't matter.** The new subprocess adds ≈44ms, cheaper than the pre-existing
agent-sync subprocess it sits beside, at a gate that fires once per `/harness`/`/harness-plan`/
`/harness-ship` door entry — not per write, not per subagent spawn. 44ms is imperceptible against
session-entry latency.

## 3. The three new suites — measured, decided

```
tests/integration/test-onboarding-split.py        0.03-0.06s  (text-probe only, no fixture)
tests/integration/test-sync-command-adapters.py   0.40s  (12/12 cases, fresh synthetic tempdir/seed per case)
tests/integration/test-check-omp-port.py          2.95s  (23/23 cases, 11 fixture() calls copying .omp+.agents+.claude, 3.1MB, per case)
```
Total added ≈ 3.3s. Full `--kind integration` run: **81.20s wall, 51 files, 8-worker pool**; pool's
own summary names the ceiling: `test-check-state.py 73.04s, test-check-plan-routes.py 71.01s,
test-check-domain.py 56.90s` — none of which this diff touches materially. **Decision: not
material.** The added 3.3s is absorbed by 8-way parallelism against a 73s ceiling set by unrelated
pre-existing files; the wall clock does not move.

`test-check-omp-port.py`'s per-case `shutil.copytree` of the live `.claude` tree (11 calls × ~3.1MB,
`symlinks=True` so `.agents/skills` copies as a symlink, not its contents) is real cost but ~260ms/call
buying independent isolation across 11 distinct corruption scenarios (edited banner, missing door,
orphan adapter, etc. — `test-check-omp-port.py:47+`). A shared fixture would save at most ~2.5s of a
2.9s file that itself doesn't move the suite total. **Keep it** — per-case isolation worth the cost,
and it isn't material anyway.

## 4. `factory_config.py`'s `product_config_report()` — no finding

`product_config()` memoizes per `(repo_name, ref)` for process lifetime (`factory_config.py:291-301`);
`product_config_report()` makes one linear pass calling it once per fleet repo, no repeated I/O
(`factory_config.py:341-353`). It is a network read (`factory_gh.file_at_ref`), correctly never
wired into any hot or session-entry gate (see classification table). No closures capturing scope
beyond the process-lifetime memo dict, which is intentional and explicitly documented as the only
sanctioned persistence.

## 5. Does any gate cost materially more per invocation than at `4b5dbb23`? **No.**

- `check-omp-port.py`: +≈44ms per session-entry-frequency invocation (measured above).
- `check-instruction-paths.py`: diff is a one-entry addition to an in-memory exclusion set; no
  separate marginal measurement is distinguishable from run-to-run noise on a ~50ms baseline
  (5 runs: `.0496/.0489/.0505/.0551/.0548`).
- Test suites: +3.3s added to an 81.2s pool run whose ceiling is set by three unrelated pre-existing
  files; wall time unchanged.
- `factory_config.py` additions: zero reachable hot-path cost (CLI-only, never imported into a
  per-write or per-door caller path).

## Scope note

Ran `git diff 4b5dbb23..HEAD` read-only throughout. All timing used `env -u HARNESS_AGENT_TYPE`.
One temp copy of `check-omp-port.py` (base and HEAD content) was written under `$TMPDIR` via the
Write tool for the location-controlled comparison in §2; both were deleted before this receipt was
written (verified via listing). No repository file was edited.

```yaml
VERDICT: PASS
DIGEST:
  headline: "EFFICIENCY angle FEAT-56 simplify-c2 — zero findings; every touched gate measured cheap at its actual invocation frequency"
  findings: []
  open_questions: []
  files_touched: ["/Users/molchairuangutai/GitHub/harness/.claude/worktrees/harness/FEAT-56-central-onboarding-model/.harness/harness/features/FEAT-56-central-onboarding-model/notes/receipt-harness-data-engineer-simplify-c2-efficiency.md"]
  expertise_update: []
artifact: /Users/molchairuangutai/GitHub/harness/.claude/worktrees/harness/FEAT-56-central-onboarding-model/.harness/harness/features/FEAT-56-central-onboarding-model/notes/receipt-harness-data-engineer-simplify-c2-efficiency.md
```
