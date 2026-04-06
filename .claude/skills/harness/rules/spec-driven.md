# Spec-Driven Development

This file is injected via `agent_skills` into gsd-planner. Follow ALL rules below. These constraints apply at plan-writing time.

## Task Completeness Requirements

Every plan task MUST include:

1. **Exact file paths** — not "update the config file" but "edit `.planning/config.json`"
2. **Complete code intent** — not "implement X" but the actual logic, types, structure, and values
3. **A verification step** with the exact command and expected output
4. **A reference** to the CONTEXT.md decision (D-XX) or REQUIREMENTS.md requirement (REQ-XX) it satisfies

A task that omits any of these four items is incomplete. Do NOT write it. Identify the gap and return to the orchestrator before proceeding.

## Placeholder Rejection

Reject any task that contains:

- "TBD", "TODO", or any placeholder notation
- Vague verbs without targets ("add error handling", "improve performance")
- Instructions that defer specification ("similar to above", "follow existing pattern")
- "implement X" without specifying what X produces, which files it touches, and how to verify it

If a task cannot be fully specified, it is a signal that discuss-phase or research-phase is incomplete. Return the task to the orchestrator with the specific gap identified.

## Spec Traceability

CONTEXT.md is the spec. Do NOT create a separate spec artifact. Every plan task must trace back to a specific CONTEXT.md decision or REQUIREMENTS.md requirement. If a task cannot cite its source, it is either out of scope or the spec is incomplete.

CONTEXT.md must contain approaches-with-tradeoffs and an explicit user approval indication before plan-phase begins. If CONTEXT.md is absent or lacks this content, STOP and return: "CONTEXT.md is missing required approaches-with-tradeoffs. Run discuss-phase before plan-phase."

## Verification Requirements

Every task's `<verify>` block MUST contain an `<automated>` command that:

- Runs in under 60 seconds
- Returns a clear PASS/FAIL signal
- Does not require human interpretation

If no automated verification is possible, the task MUST include `<automated>MISSING — [explanation of what test must be created first]</automated>`.
