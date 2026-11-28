# BUG-2565 — plan-exit goal-check against the grilling artifact

**Verdict: PASS.** The plan as applied (6 tasks, `plan-merge.py check` 0 failures, run 2026-11-27 from the worktree at base 104252db) delivers the stated intent in `/Users/molchairuangutai/GitHub/harness/.harness/notes/grilling-digest-frontmatter-contract-2026-11-27.md`. All three perspectives pass, and all six hard constraints hold. Two stale-text sites outside every task's `files:` are advisory and non-blocking (see Gaps).

## Perspectives

| Perspective | Grade | Carried by |
|---|---|---|
| operator | pass | SC-01, SC-02 (T-02: six validate-digest process ends each refuse the yield, check-domain's six still proceed, the data-less yield is refused, and a could-not-run refusal is a different literal from a contract refusal); SC-09, SC-10 (T-06: README, BUILD, SPEC, harness-team SKILL, seven DEC amends, index regenerated); SC-11 (T-01 measures the retry and parent-result question and T-06 states it) |
| orchestrator | pass | SC-03 (T-02: flat and `tasks[]` dispatches carrying the fields are neither refused nor revised); SC-05 (T-05: live probe shows the task item exposes neither key, an off-schema yield is rejected and a conforming one accepted); SC-04 (T-02: the injection code and `digest-schema.ts` are deleted) |
| code maintainer | pass | SC-06 (T-04: generated `output:` in 16 agents, `task.structured` off, check-omp-port.py exits 1 on four drift fixtures plus three truthy `task.structured` forms, compared with `typed_equal`); SC-07, SC-08 (T-03: Python projection, generator, refusal cases, 16-persona parity with the 104252db TypeScript loader) |

## Destination clauses

- "Every harness-* child gets its digest schema from its own agent definition": T-04 generates into all 16 files in `.omp/agents/`, which match `digest_schema.PERSONAS` (16). The four ALIASES have no agent file, so nothing more needs it. T-05 proves the binding live.
- "Dispatchers never see, send, or copy": T-04 turns `task.structured` off and T-05 asserts `task_item_keys`. T-02 deletes the refusal and injection, and SC-03 tests that the fields pass through. Before this run, `rg --hidden outputSchema|schemaMode` found no skill telling dispatchers to send them, except the harness-team sentence that T-06 rewrites.
- "A yield validate-digest.py cannot check is refused, never passed": T-02 and D-05. Refusals go through `policyRunner` directly, with a per-class test, and the literal reason is written out in the test file.
- "README, BUILD and DECISIONS describe that contract": T-06. Its verify greps for `gen-agent-output.py` and `refused, never passed` in each file, and checks each amend row's clause is gone and names BUG-2565.

## Hard constraints

| Constraint | Holds? | Evidence |
|---|---|---|
| Every task main-session-direct | yes | `grep -c 'execution_mode: main-session-direct'` = 6 = task count, and every `lanes` row is main-session-direct |
| No harness-* dispatch carries or is refused for schema fields | yes | T-02 deletes SCHEMA_CONTROLS, isInjectedCopy, schemaControlRefusal and withDigestSchemas, and its verify greps for zero hits. SC-03 tests Main and a governed lead, flat and batch. T-05 checks the task item keys live |
| validate-digest.py failing to run refuses the yield, landing with or before the frontmatter route | yes | T-04 (the only task that turns `task.structured` off and generates `output:`) has `depends_on: [T-02, T-03]`. D-03 stops the build after T-01 if a refused payload leaks |
| schemas/digest/*.json the only edited source, check-omp-port.py failing on drift | yes, with a note | T-04 never hand-edits agent keys, and `check-omp-port.py` runs on CI through check-state INV-45 (`check_state/table.py`, `host.py`). `gen-agent-output.py --check` survives only as a non-gating self-test because SC-07 names it (PF-74363a25, low, disposition open) |
| Historical observation notes not rewritten | yes | No `files:` entry is under `observations/`, and T-06 intent says "Historical feature observation notes are not edited" |
| #2566 out of scope | yes | No task touches stale-hook detection, and the BRIEF's `## Out of scope` carries it |

## Grilling's open items

- Retry consumption: T-01 measures it (`hook_refusal_consumes_schema_retry`), and T-06 states the measured behaviour in the docs.
- What a crash refusal tells the child: settled as decision D-02 (yield the same object once more, then stop and name the cause), and SC-02 tests it. This is a choice, not a measurement, and it is correctly placed in `decisions:`.

## Gaps (advisory, non-blocking)

1. `.harness/harness/docs/org.html` (the "OMP task hook refuses dispatcher-supplied outputSchema or schemaMode, then injects the persona schema in strict mode" paragraph) will still describe the retired contract after T-06. It is not one of the documents the operator named, so the perspective still holds. It is still a surviving present-tense claim that contradicts the delivered contract. Adding it to T-06 `files:` is a one-line plan change.
2. `tests/integration/test-dispatch-guard.py` `case_30_schema_controls_are_not_the_guards` has a docstring saying the hook refuses and injects. The test's assertion (the guard ignores the controls) stays true. Only the comment goes stale.
3. Panel cycle-1 findings still read `disposition: open`. The apply note maps each one to a change, but closing them belongs to the next panel or a ruling, not to this goal-check.
