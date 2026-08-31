# Handoff — FEAT-45-adversarial-plan-panel, plan → build — written at b8777df, seq-2

Supersedes the 1d3e5db note, whose model-independence line and `general-purpose` pin are now WRONG.

## Next

STOP — the plan phase ends at the operator's signature and it is NOT given. Do not dispatch a
build. The next act belongs to the main session: present BRIEF.md and plan.yaml for ONE signature,
carrying the two non-blocking open questions. Only after `approval.status: approved` is written by
the main session does T-01 (harness-documentor, `depends_on: []`) become dispatchable.

## Trust

- The guard blocks a lead from PASSING `model:` and does NOT strip a dispatched agent's own
  frontmatter pin; it exits 0 for any non-`harness-` target. So a lead spawning a self-pinning
  reader without passing `model:` gets that reader's model — `dispatch-guard.sh:41-51` and its own
  comment "that pin is org design" — verified-at b8777df. THIS REVERSES the old note's line
- `fable-advisor` self-pins `model: anthropic/claude-fable-5` and is read-only —
  `~/.omp/agent/agents/fable-advisor.md` frontmatter — verified-at b8777df
- That definition lives ONLY in the operator's HOME; `.omp/agents/` holds exactly 16 `harness-*.md`
  and no advisor, so the roster does not grow (SC-06) and it is non-harness (SC-14) — verified-at b8777df
- The `spawns:` frontmatter is a HARD preflight allowlist — live `general-purpose` dispatch refused
  "Cannot spawn 'general-purpose'. Allowed: harness-product-lead,harness-eng-lead,
  harness-validator-lead" — verified-at 1d3e5db. Still true; evidence about the MECHANISM, not
  about which persona ships
- Canonical agent policy is `.omp/agents/**`; `.claude/agents/**` is GENERATED and the SPAWNS map is
  bootstrap-only — `sync-agent-adapters.py:4,240,252` — verified-at 1d3e5db
- `harness-validator-lead` holds `[read, glob, grep, task, write]` and NO bash, so it can never run
  `panel_findings.py` — `.omp/agents/harness-validator-lead.md:4-9` — verified-at 1d3e5db
- Plan parses, 11 tasks, ids unchanged, no duplicates; `check-plan-routes.py` exit 0, 0 violations,
  2 expected DEC-174 deviations (T-07, T-08) — both run by the orchestrator — verified-at b8777df
- `approval.status` is `pending` in BOTH artifacts and no `rulings` key exists — read at the commit
  with `git show` — verified-at b8777df
- `advisorModel` is ABSENT from `~/.claude/settings.json`, contradicting DEC-170's `:112` —
  verified-at 1d3e5db. Declined as a backlog row (Q5); it does not affect the reader, which is a
  spawned subagent and not the turn-level channel

## Dead ends

- Do NOT re-weaken REQ-02/REQ-05 to an independent CONTEXT — the operator refuted that premise on
  the guard measurement above — `notes/answers-2026-08-30-plan.md` Q1 — verified-at b8777df
- Do NOT pin the reader as `general-purpose` — a platform built-in with no definition file and
  therefore no model pin, so it cannot deliver REQ-02's model half — D-14 — verified-at b8777df
- Do NOT add `fable-advisor.md` to this repository — agent distribution is explicitly out of scope,
  and its absence is exactly what REQ-14 exists to handle — Q1 ruling — verified-at b8777df
- Do NOT file Q5..Q8 as backlog rows — the operator struck all four — verified-at b8777df
- Do NOT re-point `review_sha` past 1d3e5db — that is genuinely the sha the simplify and ui readers
  reviewed — Q1 ruling "Not changing" — verified-at b8777df
- Do NOT use `plan-merge.py` to CHANGE a value — exit 8 on an `approval:` key, exit 7 on any
  differing task; it is ADD-ONLY — pm measured across all three cycles
- Do NOT site the panel RESULT under `approval:` — `approval_guard` spans the whole YAML key range
  and locks pm out of every sub-key — `check-domain.sh:571-575` — eng-squad measured

## Working set

- `.harness/harness/features/FEAT-45-adversarial-plan-panel/plan.yaml`
- `.harness/harness/features/FEAT-45-adversarial-plan-panel/BRIEF.md`
- `.harness/harness/features/FEAT-45-adversarial-plan-panel/notes/answers-2026-08-30-plan.md`
- `.harness/harness/features/FEAT-45-adversarial-plan-panel/runs/2026-08-30-1-product/digest.md`
