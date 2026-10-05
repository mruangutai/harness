# Receipt — efficiency angle, newest-main merge (FEAT-1928)

**BLUF: no efficiency findings.** Read-only; nothing executed. Timings are inference from source shape, not measured.

## Reads and cost judgement
- Interval union (`feature-record.py:462-484`): one sort + one linear sweep per call; `spend_for` (`:500-526`) calls it twice (whole feature, rework window) and runs precompiled regex `DISTILL_RUN`/`FIX_RUN` per run entry once. O(n log n) on a runs list of tens-hundreds, run on a CLI/hook spend read — microseconds to low ms (inference). The prior sum was cheaper but wrong (#2034). Not waste.
- CI canonical-reader audit (`tests.yml:200-226`, `check-plan-routes.py:1062-1087,1570-1584`): one `os.walk` of bin/, one `ast.parse` per .py file, classification read once, one-shot per PR in the same job as the route gate. Single-pass, no re-parse. Shell wrapper adds only a sed over a short output. Deliberate shared gate, not waste; parent runs it once.
- Cold revival (`harness-hooks.ts:1079-1108`): `adoptPersistedRun` runs only when `runtimeAgentId` is unset (`:1105`), so once per revived instance; `entries.find` stops at the first `session_init` (spawn record, first entry in practice — inference), then three marker scans over one string. Rescan could repeat per `agent_start` only if `runtimeLineage` yields no id; that is a degenerate path whose cost is an array scan, not I/O.
- digestBinding vs featureRootCache lifetimes (`:870,944-966,995-1009,1487-1488`): both reset at `openRun`; featureRootCache additionally at session shutdown. featureRootCache is keyed `[runtimeAgentId, currentFeature, cwd]` (`:946`) so the `inflight_registry.py feature-root` subprocess runs once per run/feature/checkout instead of per governed call (`rootCall` `:970-975`); refusals are never cached (`:959`), so a failing resolver retries per call by design (fail closed, correctness over speed). digestBinding spawns `digest_destination.py` once per lead run (`:1000-1008`), only for the three lead personas. Per-wake re-resolution after a hub wake is the stated lifetime, not redundancy; merging the two would conflate lifetimes (settled).
- Not read for cost: prune-run-evidence.py, DECISIONS*.md, distillation.md, classification JSON, unit tests — nothing in them is on a hot path or startup; no claim made.

## Findings
none

## Principles applied
None cited — no craft leaf was read this run.
