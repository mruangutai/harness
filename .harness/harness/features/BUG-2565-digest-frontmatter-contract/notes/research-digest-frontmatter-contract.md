# Research — BUG-2565 digest contract in agent frontmatter, yield validator fails closed

Observed at worktree HEAD 104252db (BRIEF pending) unless stated. Control plane at cf7b422b.

## Bottom line

- The per-call route is four symbols plus one module: `SCHEMA_CONTROLS`, `isInjectedCopy`,
  `schemaControlRefusal`, `withDigestSchemas` in `.omp/extensions/harness-hooks.ts`, and the whole
  of `.omp/extensions/digest-schema.ts` (its only importer is harness-hooks.ts). Deleting the four
  leaves the TS projection dead, so the projection moves to Python (D-01) and the TS loader goes.
- No generator for `.omp/agents/*.md` exists today; they are hand-authored. `output:` needs a new
  generator; precedent `gen-craft-index.py`, `gen-decisions-index.py`.
- Fail-open on yield lives in `classifyAnswer` (BROAD_GATES branch) plus the yield branch reading
  only `result.blocked`. validate-digest.py itself reports own failure as an `unavailable` line at
  exit 0 (`hook_guard(..., script=)`, `_pass_through`, `_validate_hook_object`, `_settle_claim`).
  The extension is the one place that sees both declared and synthesized failure, so it decides (D-05).
- Adjacent break found: the yield branch passes `data == null && type == "result"` untouched,
  justified in its comment by strict terminal yields rejecting it natively. Frontmatter cannot set
  strict mode (grilling, issue #2565), so that justification disappears with the route (D-04).
- `.harness/README.md` `feature.yaml` (grilling :28) is already gone at 104252db (removed by
  cf7b422b); the docs task keeps a regression assertion only.
- One more stale site the grilling did not list: `.harness/harness/docs/SPEC.md` § 8.3 Dispatch
  and its DEC-100 outcome table; `.claude/skills/harness-team/SKILL.md` says "the OMP hook injects
  your persona's strict schema". Both go to T-06.

## Gates that read the changed surfaces (P-07), per intermediate state

| Gate | After T-02 (hook) | After T-03 (projection) | After T-04 (frontmatter) |
|---|---|---|---|
| check-omp-port.py | green: config still `structured: true`, extension wiring markers untouched | unchanged | new rules: structured off, per-agent `output:` equals projection |
| test-typescript-typecheck.py | SETTLED/POISONED must drop digest-schema.ts in T-02 | unchanged | unchanged |
| omp-hooks.test.ts | rewritten in T-02 | unchanged | unchanged |
| check-skill-weight.py / INV-42 | n/a | n/a | reads autoloadSkills only; unaffected |
| check-instruction-paths.py | n/a | n/a | scans agent .md for `.harness/` etc tokens in backticks; projection keeps no prose |
| INV-48 | n/a | n/a | scans agent references; `output:` carries no DEC/path tokens [INFERENCE] |
| gen-decisions-index | n/a | n/a | T-06 regenerates |

## Decision dispositions — plan row identities

| Row | DEC | Clause (verbatim) | Successor |
|---|---|---|---|
| 1 | DEC-100 | `check-domain.py` … `validate-digest.py` an own | D-05 |
| 2 | DEC-126 | Python, while the OMP adapter resolves … injected | D-01 |
| 3 | DEC-127 | call so an own exception returns 0 — fail OPEN, on our own | D-05 |
| 4 | DEC-206 | the task hook injects strict schemas only for `harness-*` personas | D-01 |
| 5 | DEC-208 | Failing closed on our own gap was rejected in one clause: it would wedge | D-05 |
| 6 | DEC-237 | **Dispatch owns schema delivery.** Before any claim side effect, … refuses | D-01 |

DEC-100 also says "Failing these gates closed stays refused — one gate's bug would wedge every
agent"; DEC-208 also says "a missing claim registry — exits 0 visibly unavailable (DEC-100)".
T-06's intent covers those sibling sentences; the row carries one clause per DEC. Index tails
(` :: ` text, hand-written) for DEC-100, DEC-127, DEC-208, DEC-237 become false and are rewritten.

## The two grilling unknowns — where each is carried

- Retry consumption: measured by T-01 (live probe, minimal yield-blocking extension) before any
  code changes; recorded in `notes/research-yield-refusal-probe.md`; T-06 documents it.
- Crash vs refuse message: decided as D-02 (distinct text; re-yield once, then stop). T-01's probe
  records what OMP does when a structured child stops after refusals, and D-03 makes a refused
  payload reaching the parent a stop-the-build result.

## Not measured here

- T-02 verify duration: `node_modules` is absent in the worktree, so `test-typescript-typecheck.py`
  was not timed. `bun test tests/unit/omp-hooks.test.ts` took 18.8 s at 104252db.

## Plan landing — blocked on the seeded station_only marker

The proposal is `notes/research-plan-proposal.md` (plain plan YAML; plan-merge reads it as-is).
Bootstrapped into a scratch `.harness/harness/features/BUG-2565-digest-frontmatter-contract/plan.yaml`
with this BRIEF beside it, `plan-merge.py check --root <this worktree>` printed 6 tasks, 34 anchors
resolved, 0 failures; `check-plan-routes.py` printed 0 violations (TASK deviations only, G-12).
The seeded plan.yaml cannot take it: `apply` exited 5 here (the loader refuses `station_only` beside
tasks); a changed `station_only` value is a plain-key exit 7 and `set-key station_only null` would
turn the legal base illegal, which `_write_top_mapping` refuses ([INFERENCE] from the code, not run).
Remedy for Main: delete the `station_only: true` line (or the seed file), then
`plan-merge.py apply --file <plan.yaml> --proposal <this feature>/notes/research-plan-proposal.md`
and `plan-merge.py check --file <plan.yaml> --root <this worktree>`.
