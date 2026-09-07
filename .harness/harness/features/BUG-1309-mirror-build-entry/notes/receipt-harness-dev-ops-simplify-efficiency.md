# EFFICIENCY angle — BUG-1309-mirror-build-entry

BLUF: one real finding. `merge-gate.py` imports the full `feature_schema` module — which
unconditionally imports third-party `jsonschema` at its top — for two schema-free symbols
(`BUILD_ENTRY_ERA_EXEMPT`, `recovery_command_for`). That import alone costs ~50ms and is now
paid on **every Bash tool call in the repo**, not just merges, because `merge-gate.sh` is a
registered PreToolUse gate on every Bash invocation. Everything else I measured is negligible
or is an accepted one-shot cost. Zero other findings.

## Measurements taken

1. **`merge-gate.sh` end-to-end, non-matching command** (`ls -la /tmp`, warm cache, averaged
   over 10 runs via a tight loop): **~121ms/call**. Breaks down as:
   - `python3 -I -c '...harness_boundary.resolve_root...'` (the root-resolution subprocess
     `merge-gate.sh:5` spawns before exec'ing the gate): **~20ms**.
   - `merge-gate.py` itself (stdin read, `harness.json` read, `merge_ref` tokenize — no glob,
     no `gh` subprocess on the non-matching path since `github.sync` is enabled but the
     command isn't a merge): **~60-70ms**.
   - Of that, **`import feature_schema` alone is ~50-60ms** (`feature_schema.py:36`
     `import jsonschema`, confirmed by disabling the import: same script with `jsonschema`
     forced unavailable drops from ~60ms to ~10ms). Bare `python3 -c 'pass'` startup is ~10ms,
     so `jsonschema` is essentially the entire non-baseline cost.
   - `merge-gate.py:11 import feature_schema` is new in this diff (`merge-gate.py` and
     `merge-gate.sh` are both wholly new files); the `jsonschema` import inside
     `feature_schema.py` is pre-existing, unchanged by this diff. The diff is what newly
     routes that pre-existing cost onto the hot path of every Bash call.
   - Neither symbol `merge-gate.py` uses touches `jsonschema` — `BUILD_ENTRY_ERA_EXEMPT` is a
     frozen set literal and `recovery_command_for` (`feature_schema.py:324`) does path parsing
     plus a lazy `import harness_yaml`, never `load_schema`/`problems_for_*`.
   - **Concrete cost:** ~50-60ms extra on every single Bash call in every session in this
     repo, for a code path that never validates anything against a schema. Over a session
     running hundreds of Bash calls this is seconds of pure waste, and it is the one place in
     this diff that fits the skill's own hot-path bar ("a gate that runs at every write earns
     scrutiny a one-shot build step does not").
   - **Alternative:** either (a) make `feature_schema.py`'s `import jsonschema` lazy — move it
     inside `load_schema`/`problems_for_doc`, the only functions that use it, so a caller that
     only wants `BUILD_ENTRY_ERA_EXEMPT`/`recovery_command_for` never pays for it; or (b), if
     touching the shared module is judged riskier, give `merge-gate.py` its own tiny
     schema-free import (the era set and `recovery_command_for` do not depend on anything
     schema-shaped). (a) is smaller and matches existing practice: `check-domain.sh:1398,1445`
     already imports `feature_schema` lazily inside the specific branches that need it rather
     than at module scope, so a lazy `jsonschema` import inside `feature_schema.py` itself is
     the same discipline applied one level deeper, not a new pattern.
   - **This is my highest-value finding.** It is the only one that lands on a true every-call
     hot path (the merge-gate PreToolUse hook), the cost is directly measured and reproduced
     with an isolation test (not inferred), and the fix is small, mechanical, and behavior
     preserving (moves an import, changes no logic).

2. **`check-state.sh` INV-37** (session-entry invariant, `check-state.sh:1983-2022`): full
   script run twice, **~13.0s and ~12.9s** total, 66 feature directories on disk. Isolated the
   INV-37 body (`import feature_schema` + the per-feature glob/read/`json.load` loop) outside
   the script: `import feature_schema` is **~53ms**, the glob+read loop is **~0.2ms** (most
   features are filtered by `BUILD_ENTRY_ERA_EXEMPT`/`plan_docs` membership before any
   `feature.json` open). INV-37's total added cost is ≈53ms against a ~13,000ms baseline —
   **0.4%, not a finding.** The per-feature `feature.json` re-read INV-37 does (rather than
   reusing an already-parsed document) is also not new waste specific to this diff: at least
   seven other pre-existing invariants in the same script (INV-6..8, INV-18, INV-23, INV-24,
   INV-28/30 — `check-state.sh:604,1145,1306,1335,1551,1590,1701,2313`) follow the identical
   glob-then-reopen-`feature.json` pattern per invariant block; INV-37 matches established
   convention rather than introducing a new inefficiency, and fixing the pattern would touch
   all seven sites, well outside this diff's scope.

3. **`feature_schema.py`'s `BUILD_ENTRY_ERA_EXEMPT`** (module-level frozen set, ~76 string
   literals) and `RUNS_AGENT_EXEMPT` precedent it sits beside: both are literal Python data,
   no computation, no I/O at import time. Not a cost site regardless of the four import call
   sites (`merge-gate.py`, `gh-sync.py`, `post-merge-sweep.sh`, `check-state.sh`) — the set
   itself is free; only the `jsonschema` import riding along with it (finding 1) costs
   anything.

4. **`gh-sync.py`**: `_open_ensure_labels` / `cmd_start_task` read `feature.json`/`plan.yaml`
   once per command invocation (a one-shot CLI, not a hot loop) — no repeated read of the same
   file found in the diff's added code. Not a finding.

5. **New test beds** (two `tests/unit` files plus integration cases in
   `tests/integration/test-gh-sync.py`/`test-check-state.py`): none re-run a whole suite where
   a targeted case would bind — each new unit case targets one function via direct import, and
   the integration cases already documented as full-suite gates (T-11's discharge notes) are
   boundary-step runs, which the skill says are evidence of the boundary, not waste. Not a
   finding.

## Ranking

1. **(highest)** `merge-gate.py:11` unconditional `import feature_schema` — ~50-60ms of
   unused-jsonschema-import cost on every Bash call, fix = make the import lazy in
   `feature_schema.py`.
2. (none) — no second finding cleared the bar; INV-37, the era set, and gh-sync's I/O are all
   measured negligible or consistent with pre-existing convention.
