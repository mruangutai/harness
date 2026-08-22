# REUSE pass — FEAT-31 (harness-backend-dev)

**BLUF: 1 finding, material but modest. Everything else checked (walk logic, config-resolution
pair, hook's identity source, test fixture repetition) is either already covered by a settled
seam or not a genuine restatement of an existing importable thing.**

## Finding 1 — `"harness-orchestrator"` classification is a bare literal, spelled three times, and the walk that uses it is duplicated wholesale

- **File/lines:** `.claude/skills/harness/bin/context-watch.py:301` (inside `_build_row`) and
  `.claude/skills/harness/bin/context-watch.py:599` (inside `_orchestrator_jsonl_paths`) both
  write `meta.get("agentType") != "harness-orchestrator"` as an inline string compare — no
  shared module-level constant. A third independent spelling is
  `.claude/skills/harness/bin/context-watch-hook.py:41` (`IN_SCOPE_AGENT_TYPE = "harness-orchestrator"`).
- Beyond the literal, `_orchestrator_jsonl_paths` (context-watch.py:569-602) re-walks
  `projects_root -> project_dir -> session_dir -> subagents_dir -> agent-*.meta.json` — the exact
  same four-level walk `discover_orchestrator_rows` (context-watch.py:329-361) already performs.
  The function's own docstring says so directly: "Mirrors discover_orchestrator_rows' walk...
  but returns paths only." The walk is hand-copied, not called through a shared generator.
- **Cost:** the file already treats "one seam so classification can't drift" as a first-class
  discipline — that is exactly what `_measured_sizes` (line ~277) exists to guarantee for the
  arithmetic. The `agentType == "harness-orchestrator"` classification gets no equivalent
  guarantee: it is duplicated as a raw string three times across two files, and the directory
  walk that surrounds it is duplicated once more inside the same file. If the orchestrator's
  `agentType` value is ever renamed, or the walk depth changes (the module's own comment on
  `discover_orchestrator_rows` already flags that Claude Code interposes an extra project-dir
  level nobody expects on first read), three string sites and two walk copies must be edited in
  lockstep. Whichever one is missed does not error — it silently stops matching, so the tool
  quietly stops seeing orchestrators (footer, warnings, hook) while reporting nothing wrong. That
  is the fail-open shape this repo is specifically watching for, applied to discovery rather than
  arithmetic.
- **Alternative:** factor the walk into one generator (e.g. `_iter_orchestrator_sidecars(projects_root)`
  yielding `(agent_id, meta_path, subagents_dir)` for every sidecar whose `agentType` matches),
  and bind the literal to one module constant `ORCHESTRATOR_AGENT_TYPE = "harness-orchestrator"`
  that `discover_orchestrator_rows`, `_build_row`, and `_orchestrator_jsonl_paths` all import.
  `context-watch-hook.py`'s own `IN_SCOPE_AGENT_TYPE` cannot be unified the same way without a
  cross-file import (and that file is DEC-174 main-session-direct), so leave it as a separately
  named constant there, but note the drift risk.
- **Tag:** `context-watch.py:301` and `context-watch.py:599` — **APPLICABLE** (context-watch.py is
  one of the 9 team-lane surfaces). `context-watch-hook.py:41` — **FLAG-ONLY** (DEC-174
  main-session-direct; no squad member may write this file).

## Checked, not flagged

- `_measured_sizes` (context-watch.py:201-220 per dispatch) — already reviewed and settled; not
  re-litigated.
- `resolve_threshold` vs `resolve_retention_days` (context-watch.py ~183-251) look like a
  duplicated read-file/parse-JSON pattern, but the docstrings state the divergent behavior is
  deliberate (one carries a `reason` string for surfacing the miss, the other is silent by
  design per T-08). Not a restatement of the same thing — different contracts. Not flagged.
- `context-watch-hook.py`'s use of `session_id`+`agent_id` instead of `transcript_path` — this is
  a documented, evidence-backed choice (`notes/probe-hook-payload-identity.md`), not a
  reimplementation of an existing identity helper. Not flagged.
- Heavy inline fixture repetition in `test-context-watch.py` (`{"agentType":
  "harness-orchestrator"}` written ~15 times with no shared builder) — this is within-file DRY,
  not a restatement of an *existing importable* fixture; no such helper exists anywhere else in
  the tree to point at. Belongs to SIMPLIFICATION, not REUSE, if raised at all.
- Backlog rows #663-#669 — not re-checked, per dispatch.
