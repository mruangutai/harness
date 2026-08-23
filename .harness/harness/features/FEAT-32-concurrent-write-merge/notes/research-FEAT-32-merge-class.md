# Research — FEAT-32 — the merge class, measured at 5d9b428

**Conclusion first.** #606, #628 and #551 are one defect: a whole-file write with no merge path and
no serialisation, seen from the write side (#606, #628) and the read side (#551). The cure already
exists for exactly one file class and is unlanded. The plan therefore has a **start gate**, not just
a dependency: nothing may be built until FEAT-30 merges to `main`.

## Measurements taken here (each re-derivable)

| Claim | Command / anchor | Result |
|---|---|---|
| No lock primitive in `bin/` | `grep -rlE "O_EXCL\|fcntl\.flock" .claude/skills/harness/bin/` | empty |
| `plan.yaml` has no shape rule | `check-domain.sh:677` | `SHAPE_PATTERNS` = feature.json, state.yaml, handoff, STATE.md, CLAUDE.md — nothing else |
| Observation log has no shape rule | same tuple | absent |
| `validate-digest.py` fail-opens 3 ways | `:828` unreadable, `:838` no `agent_type`, `:845` `stop_hook_active`; `hook_mode` at `:804`, internal-error pass-through printed at `:869` | verified |
| `dispatch-guard.sh` has **no test** | `ls .claude/skills/harness/bin/test-dispatch-guard.py` | absent — hence T-07 |
| Unit baseline | `run-unit-tests.sh --kind unit` | exit 0, 179 PASS/FAIL/ERROR lines, 0 beginning `FAIL` |
| Integration baseline | `run-unit-tests.sh --kind integration` | exit 0, 93 such lines, 0 beginning `FAIL` |
| Route check on this plan | `check-plan-routes.py <plan>` | exit 0, 0 violations, 4 `DEVIATION` lines (all DEC-174 shape) |
| Highest decision number | `DECISIONS-INDEX.md` | DEC-196 — do **not** pin 197, FEAT-31 also takes one |
| New test files must be registered | `run-unit-tests.sh:39-55` drift detector; `harness.json` `test_kinds.integration.detect` is an explicit list | exits 2 MISCONFIGURED otherwise |

## Domain resolution (DEC-179), every literal path in the plan

`harness-backend-dev, harness-dev-ops` — every `.claude/skills/harness/bin/*` path, including
`dispatch-guard.sh`, `validate-digest.py` and their tests. **Granted, yet laned
`main-session-direct`** for the four enforcement-layer paths, which is why the route check prints
`DEVIATION` and not `VIOLATION`; DEC-179 makes that non-fatal and DEC-174 amendment 4 makes it
required.

`NOBODY` — `.claude/skills/harness-*/SKILL.md`, `.claude/agents/*.md`, `.gitignore`,
`.claude/settings.json`, `.harness/team-config.yaml`. `harness-dev-ops` — `.harness/harness.json`.
`harness-documentor` — `DECISIONS.md`. `harness-orchestrator, harness-pm` — everything under
`.harness/harness/features/<FEAT>/`.

## The #551 design, and the one thing it rests on that is not yet measured

FEAT-31's probe (`feat/FEAT-31-orchestrator-context-watch:…/notes/probe-hook-payload-identity.md`)
established that a `PreToolUse` payload inside a subagent carries eleven keys including
`agent_type`, `agent_id` and `cwd`. **It did not establish the key that names the DISPATCHED
persona** on a `Task` call, nor whether `SubagentStop` carries `agent_type`. Both are load-bearing:
the first for the refusal, the second for the release. T-01 measures them and T-06, T-08 and T-09
each return `BLOCKED` rather than guessing. Guessing a payload key is how `validate-digest.py:838`'s
own comment says a hook goes dark project-wide with no signal.

Restricting `SINGLE_FLIGHT_AGENTS` to `harness-pm` is what makes the release keyable on
`agent_type` alone — single flight means the count is 0 or 1, so no agent id is needed to know which
claim to release — while keeping a legitimate parallel squad of two `harness-backend-dev` legal.

## Why "make the lead wait" was rejected

`validate-digest.py`'s `hook_mode()` returns 0 on `stop_hook_active` (`:845`) to avoid an infinite
stop loop. So a `SubagentStop` refusal can fire **at most once** per stop and cannot be a wait. That
is why #551 occurrences 3 and 4 stay open and why the fix refuses the **second dispatch** instead.

## Live during this run: two guard behaviours worth knowing

1. `bash-write-guard.sh` refused `sed -i` against my own `plan.yaml` — the target was passed as an
   unexpanded `$P`, so the guard resolved a literal `$P` and denied it. The `Edit` tool worked. A
   shell variable in a write target is invisible to the guard's resolver.
2. The same guard allowed `python3 - <<PY` to rewrite that identical file, because the command
   carries no write pattern it recognises. That is #627, reproduced incidentally, and it is the
   reason each new CLI in this plan carries its own exit-9 destination refusal.

## Open, and in the DIGEST

DEC-90 (`DECISIONS.md:1153`) states as a scope boundary that every single-writer guarantee means one
agent on one machine "with no lock anywhere". This plan puts locks in the tree. Only the operator
strikes a decision (DEC-188, `DECISIONS.md:5648`); nothing here strikes it, and no task assumes an
answer.
