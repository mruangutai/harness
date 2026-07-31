# /harness-map — build or refresh the codebase map

Read `.claude/commands/harness.md` and follow it with **mission: map** (DEC-137). The differences:

- **When:** normally the map is built AT INIT (DEC-140); this command is for re-maps, refreshes
  after drift, and projects onboarded before the rule. INV-14 warning ("code without a map") routes
  here. Per-feature freshness is automatic (ship-refresh) — a full re-map is for when structure
  changed beyond what ship-refresh tracked.
- **What happens:** the orchestrator reads `references/missions.md` and sequences the per-squad
  runs — each specialist authors the view it later consumes; documentor consolidates
  `architecture.md` + `INDEX.md` (60-line cap — the index is injected into every future spawn);
  `bin/render-map.py` derives the human view.
- **Terminus:** map artifacts under `.harness/codebase/`, briefing notes anything the mapping
  surfaced as `open_questions`. No approvals — the map records what IS, never what should be.
