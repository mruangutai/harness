# Handoff — FEAT-45-adversarial-plan-panel, plan → build — written at 1d3e5db, seq-1

## Next

STOP — the plan phase ends at the operator's signature and it is NOT given. Do not dispatch
a build. The next act belongs to the main session: present BRIEF.md and plan.yaml for ONE
signature, carrying the open questions in the orchestrator's return. Only after
`approval.status: approved` is written by the main session does T-01 (harness-documentor,
DEC entries + DECISIONS-INDEX regeneration, `depends_on: []`) become dispatchable.

## Trust

- The `spawns:` frontmatter is a HARD preflight allowlist, not advisory — orchestrator ran a
  live `general-purpose` dispatch and it was refused "Cannot spawn 'general-purpose'. Allowed:
  harness-product-lead,harness-eng-lead,harness-validator-lead" — verified-at 1d3e5db
- Canonical agent policy is `.omp/agents/**`; `.claude/agents/**` is GENERATED and the SPAWNS
  map is bootstrap-only — `sync-agent-adapters.py:4,240,252` — verified-at 1d3e5db
- `harness-validator-lead` holds `[read, glob, grep, task, write]` and NO bash, so it can never
  run `panel_findings.py` — `.omp/agents/harness-validator-lead.md:4-9` — verified-at 1d3e5db
- No governed spawn can select a model: the guard keys `model:` on the CALLING `agent_type` —
  `.claude/skills/harness/bin/dispatch-guard.sh:39-47` — verified-at 1d3e5db
- `advisorModel` is ABSENT from `~/.claude/settings.json`, contradicting DEC-170's cited `:112`
  — `grep advisorModel ~/.claude/settings.json` returns nothing — verified-at 1d3e5db
- `general-purpose` resolves and has run live on this platform —
  `.harness/logs/2026-08-03.md:23` — verified-at 1d3e5db
- Seven tasks are `main-session-direct`; only T-07/T-08 are DEC-174 carve-outs proper, the rest
  because `check-domain.sh --resolve` returns NOBODY — `plan.yaml` `lanes:` — verified-at 1d3e5db
- `approval.status` is `pending` in both artifacts — grepped both files — verified-at 1d3e5db

## Dead ends

- Do NOT plan the reader as the turn-level `advisor` tool — unattached on this workstation —
  `~/.claude/settings.json` — verified-at 1d3e5db
- Do NOT site the panel RESULT under `plan.yaml`'s `approval:` — `approval_guard` spans the whole
  YAML key range and locks pm out of every sub-key — `check-domain.sh:571-575` — eng-squad measured
- Do NOT edit the SPAWNS map expecting it to ship anything — `bootstrap()` refuses to overwrite
  existing canonical agents — `sync-agent-adapters.py` — pm measured in the c1 fix cycle
- Do NOT use `plan-merge.py` for this feature's plan — it refuses CREATE with an `approval:` key
  (exit 8) and refuses MODIFY on any differing task (exit 7) — pm measured, both cycles used Write

## Working set

- `.harness/harness/features/FEAT-45-adversarial-plan-panel/plan.yaml`
- `.harness/harness/features/FEAT-45-adversarial-plan-panel/BRIEF.md`
- `.harness/notes/grilling-adversarial-plan-panel-2026-08-29.md`
- `.harness/harness/features/FEAT-45-adversarial-plan-panel/notes/receipt-harness-dev-ops-arch-eng.md`
- `.harness/harness/features/FEAT-45-adversarial-plan-panel/notes/research-FEAT-45-planfix-c1.md`
