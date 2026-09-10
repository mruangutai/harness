# EFFICIENCY angle — FEAT-104-strict-digest-schema

BLUF: no material waste. The three hot-path gates (`check-domain.sh`, `check-state.sh`,
`validate-digest.py`) are all correctly gated so the new schema-enforcement cost is paid only by
what it actually validates. One genuine but numerically negligible repeated-I/O pattern found in
`check-state.sh`; not worth an apply. `findings` below has one low-severity entry.

## 1. `check-domain.sh` hot path — answered

The new schema block is gated behind `if RE_STATE_YAML.match(rel):` at
`.claude/skills/harness/bin/check-domain.sh:1526`. A non-`state.yaml` Write/Edit never reaches it;
`shape_problems()` is still called for every target (pre-existing behaviour, unrelated to this
diff), but the new `import jsonschema` / schema read / step-validation code sits entirely inside
that `if`, so a non-state file pays exactly 0 extra work for it.

**Measured** (worktree root, real hook binary, 20 iterations each, `time`):
- non-`state.yaml` Write (`/tmp/scratch-nonstate.py`, `harness-backend-dev`): **1.688s / 20 = 84.4ms/call**
- valid v2 `state.yaml` Write, same content shape, granted agent: **1.666s / 20 = 83.3ms/call**

Delta ≈ 1.1ms/call, within noise of process-spawn variance — consistent with the file's own
comment at line ~86 measuring the whole governed path at 104.7ms and attributing "most" of it to
the interpreter launch. Confirmed live: feeding an actual v2 `state.yaml` payload with an
undeclared step key to a granted agent (`harness-orchestrator`) produces the new "undeclared step
key or evidence shape" refusal at exit 2, proving the code path is reached only there.

## 2. Repeated I/O — schema file / agents dir / team-config

- `run-state-schema.json` in `check-domain.sh`: opened and parsed exactly once per hook
  invocation (`check-domain.sh:1621-1622`), inside the single `if RE_STATE_YAML.match(rel):`
  branch — one Write, one open. No repetition to flag (a subprocess can't cache across
  invocations anyway).
- `run-state-schema.json` in `check-state.sh`: **opened and `json.load`-ed, and the
  `jsonschema.Draft202012Validator` rebuilt, inside the per-run-directory sweep loop**
  (`for sy in glob.glob(...)` at line 1433; the new block re-opens at lines 1492-1496, once per
  matching `state.yaml`). See finding F-1 below — real, but immaterial at current and near-term
  scale.
- `.omp/agents/*.md`: **not traversed by `validate-digest.py` at all.** The
  "bidirectional documented-vs-declared agreement" lives only in
  `tests/integration/test-validate-digest.py`'s `CONTRACT_SOURCES` table (lines 297-310+),
  exercised solely under the test suite, never on the `--hook` / `validate()` path that runs at
  SubagentStop. `DOCUMENTED_OPTIONAL`/`PASSTHROUGH` are plain dict literals consulted once per
  call (`validate-digest.py:1238-1254`) — no directory globbing anywhere in the runtime module.
- `team-config.yaml`: no new read site added by this diff in either script.

## 3. `validate-digest.py` per-SubagentStop cost

No agents-directory traversal exists in the runtime path (see #2). The new work per call is two
dict merges (`PASSTHROUGH.get(persona, {})`, `DOCUMENTED_OPTIONAL.get(raw_persona, {})`) and one
`set` difference for the undeclared-key check — O(number of digest fields), not O(agents on disk).
No measurement needed; there is no loop over `.omp/agents` to cost.

## 4. `check-state.sh` at rest

The sweep is `for sy in glob.glob(...)`, one iteration per run's `state.yaml`, and the new
per-step key/evidence check is a second `for _step in ...` nested inside — that part is linear in
steps, not superlinear (one `iter_errors()` call and one set-membership check per step, no
inner scan over other steps). The superlinear part is the schema **file** re-acquisition
described in F-1 below, which is linear-in-runs, not linear-in-steps.

**Measured**: full `check-state.sh` sweep over this worktree, wall clock 4.19s (`time bash
check-state.sh`, 1504 output lines — i.e. this feature's own large `notes/` census dominates).
Isolated cost of one open+parse+validator-build cycle for `run-state-schema.json`, 200 iterations
in-process: **0.0375ms/iteration** (7.51ms/200). The current census recorded in the code's own
comment is 356 run `state.yaml` files, all schema_version 1 — the new block's `if
_schema_version >= 2` guard means **today this reopen cost is paid zero times**; it activates only
as v2 runs accumulate, and even a worst-case sweep of a few hundred v2 runs would add roughly
0.0375ms × N ≈ single-digit milliseconds against a 4.19s sweep (<0.3%).

## 5. Test files

`test-check-domain.py` (11 cases, includes the new schema/floor cases): 0.865s wall.
`test-check-state.py` (3 new undeclared-key cases): 0.596s wall. Both dominated by real
subprocess hook launches (~80-100ms each, the same interpreter-startup floor as #1) — inherent to
exercising the real binary, not duplicated whole-suite runs. `test-validate-digest.py`'s existing
`_bug919_stub_script` pattern (already present, unmodified by this diff) stubs `run-unit-tests.sh`
rather than invoking the real multi-minute suite — the new cases added under this diff use the
same existing infrastructure and introduce no new full-suite re-run. Not run in full (4000+
lines, no evidence of waste to justify the wall-clock cost of running it here).

## Findings

- **F-1** · `.claude/skills/harness/bin/check-state.sh:1492-1496` · schema file
  reopened/reparsed and validator rebuilt once per matching run directory inside the sweep loop,
  instead of once per sweep · **cost**: measured 0.0375ms per redundant open+parse+build; at
  today's census (0 files ≥ v2) this is 0ms in practice, and even at a few hundred v2 runs it is
  low single-digit milliseconds against a 4.19s sweep · **alternative**: hoist the `open()` /
  `json.load()` / `Draft202012Validator(...)` construction (and the compiled `_evidence_name`
  regex) above the `for sy in glob.glob(...)` loop, guarded by the same `try/except` so a missing
  or broken schema file still reports `INV-16: ... run-state schema CANNOT be checked` for every
  run rather than none · **worth-doing: no** — real but immaterial at measured and realistically
  projected scale; not worth spending the pass's one-fix ceiling on a sub-millisecond saving.

findings_count: 1
