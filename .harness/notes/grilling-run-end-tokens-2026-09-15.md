# Grilling — DEC-227 tokens stamped by the host, never transcribed by the orchestrator (#1724) — 2026-09-15

## Destination
A completed dispatch on an OMP host leaves an integer `tokens` on its run entry in `feature.json`
with no `--tokens` argument anywhere in the orchestrator's transcript, so `feature-record.py spend`
prints a number and the `SPEND:` advisory carries it. `null` survives only where the host reported
nothing.

## Mission
mission: patch
reason: cause is measured (19/19 task results carried the figure, 0/26 run-ends passed it), the diff is bounded to the hook, feature-record.py and their tests, and the change moves an existing value onto an existing verb — no new schema or gate.
confirmed-by: operator (blanket ruling in session 2026-09-15: "do #1724 then continue each ticket … do all of them from plan (or patch) to ship"; flow shape chosen: patch intake + direct build + validate panel + ship)

## Settled
- Who measures → the host. The OMP extension already receives every orchestrator `task` tool result
  (`tool_result` handler, `harness-hooks.ts:898`) and already calls `feature-record.py spend` on it.
  The same handler reads `event.details.results[i].tokens` and stamps it before `spend` runs.
- How it lands → a new `feature-record.py` verb, `stamp-tokens --file <feature.json> --tokens N`,
  writes `tokens` on the ONE open run (has `started_at`, no `ended_at`); it refuses (exit 2) when
  there is no open run or more than one, naming them. `run-end` keeps an existing `tokens` when
  called without `--tokens` (it already does: `feature-record.py:139`).
- Several results in one `task` call → sum their `tokens`; that is one dispatch from the run's
  point of view.
- The orchestrator's part → the playbook stops telling it to transcribe `N` off the tool result
  (`harness/SKILL.md:80-81`). `run-end --tokens` stays as the explicit override for a host that
  reported nothing; it is no longer the primary route.
- Refusal → NOT added to `run-end`. With the hook stamping first, a bare `run-end` finds the figure
  already present. A `run-end` that would write `null` cannot know a figure exists elsewhere, so
  the ticket's "refuse, naming where the figure is" clause is dropped as unimplementable without
  the hook re-reading transcripts. Recorded here so nobody reads its absence as an oversight.
- Claude Code compatibility host (DEC-210) → no `tool_result` tokens; `null` stays correct there.
- Build execution → `main-session-direct` (DEC-174: hook, `feature-record.py` is what `spend` and
  the advisories read; its test is inside the line). pm writes T-01 with
  `execution_mode: main-session-direct`.

## Not yet specified
- none

## Out of scope
- Back-filling `tokens` on the 28 BUG-285-canonical-reader runs or any historical feature; DEC-227
  says historical values stay as recorded.
- Reading tokens off the session JSONL for the orchestrator's own context (that is the context
  advisory, DEC-198, already built).
- Anything about what the orchestrator decides with the figure (#1723).

## Facts I verified (so pm does not re-derive them)
- `tokens: null` on all 28 runs of `.harness/harness/features/BUG-285-canonical-reader/feature.json` — `jq '.runs[].tokens'` — at 82c9d074.
- 19 of 19 `task` tool results in the orchestrator transcript `~/.omp/agent/sessions/-GitHub-harness/**/ResumeCanonicalReaders.jsonl` carried numeric `details.results[i].tokens` (e.g. 135888, 299301, 68447); `details.results[i]` keys include `tokens`, `requests`, `contextTokens`, `usage`.
- 0 of 26 `feature-record.py run-end` commands in that transcript passed `--tokens`.
- `feature-record.py run-end` (`.claude/skills/harness/bin/feature-record.py:139`) writes `args.tokens` only when given or when the key is absent, so a pre-stamped value survives a bare `run-end`.
- The hook's SPEND block (`harness-hooks.ts:983-1009`) fires for `currentAgent === "harness-orchestrator" && toolName === "task"` with `currentFeature` set and resolves `spendFeatureJson` via `inflight_registry.py feature-root`; `taskIdentities(event.details)` already parses `details.results`.
- Hook tests live at `tests/unit/omp-hooks.test.ts` (bun) and `tests/unit/test-omp-hooks.py`; `feature-record.py` tests at `tests/unit/test-feature-record.py` (40 cases, green at 82c9d074).
