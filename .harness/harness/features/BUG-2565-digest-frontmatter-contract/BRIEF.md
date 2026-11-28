# BRIEF — BUG-2565-digest-frontmatter-contract Digest contract in agent frontmatter; yield validator fails closed

## Problem

Every Harness dispatcher (main, orchestrator, leads) sees `outputSchema`/`schemaMode` on the task tool because global `task.structured` is on, and the task hook writes both fields into each `harness-*` dispatch, which OMP then persists as the dispatcher's own call. Dispatchers copy it back: 63 "Harness dispatches never carry" refusals across session transcripts (31 through 2026-11-21, 32 since), each a wasted round trip, and twelve feature observation notes now disagree about who adds the fields. Behind that, the one check that enforces the contract lets an unchecked return through: when `validate-digest.py` cannot run, the yield passes with a notice, the dispatcher receives an unvalidated object and no fenced record reaches `runs/<id>/digest.md`. README, BUILD, SPEC and DECISIONS describe the per-call route. Source: issue #2565 (supersedes #2482) and the operator-confirmed grilling `.harness/notes/grilling-digest-frontmatter-contract-2026-11-27.md`.

## Done when — by perspective

**operator** — Every harness child's return that reaches a dispatcher was checked by the digest validator; when the validator cannot run, the yield is refused and says so, never passed with a notice. The README, BUILD, SPEC and decision record I audit describe the contract that actually runs, including what a child does when it is refused for a Harness fault.

**orchestrator** — When I dispatch a harness persona there is no schema field for me to supply, copy, or be refused for; the child still returns its persona's digest shape.

**code maintainer** — I change a digest contract by editing its persona JSON schema and nothing else by hand; the agent definitions' copy is generated, and the port check fails if I forget to regenerate.

## Success criteria

- SC-01 (operator): When `validate-digest.py` cannot run on a yield — it prints its own `unavailable` line at exit 0, exits other than 0 or 2, is killed by a signal, cannot be spawned, or is killed at the 30-second budget — the OMP yield hook blocks the yield with a reason naming the validator failure. Each process-end class is its own assertion. The same classes from `check-domain.py` on a write still proceed with their could-not-run notice (the other broad gates are unchanged). A yield with no `data` and `type: "result"` is blocked too. qa shows the existing FEAT-2274 case "an unavailable digest validator lets the yield through" passing against the pre-change hook as the failing-first state.
  verify: automated        evidence: unit
- SC-02 (operator): A could-not-run refusal and a contract refusal are distinguishable to the child: a validator exit 2 or structured deny reaches the child with the validator's own reason and without the could-not-run text, and the could-not-run refusal states that the fault is Harness's, that the object was not checked, to yield the same object once more, and to stop yielding if refused again for the same cause (D-02).
  verify: automated        evidence: unit
- SC-03 (orchestrator): A Harness dispatch carrying `outputSchema`, `schemaMode` or both, flat or in a `tasks[]` item, is neither refused nor revised by the task hook: the hook returns no `input` revision and no block naming either key, so the host `task` call is not rewritten, and `dispatch-guard.py` still receives each target through the hook's normalized dispatch-guard input (agent, task and name per `normalizeTaskDispatches` entry), which stays its own interface and is not changed by this feature. qa shows the pre-change hook refusing or revising the same calls first.
  verify: automated        evidence: unit
- SC-04 (code maintainer): At `git show <review_sha>:.omp/extensions/harness-hooks.ts` none of `SCHEMA_CONTROLS`, `isInjectedCopy`, `schemaControlRefusal`, `withDigestSchemas`, `loadDigestSchemaBundle`, `outputSchema` or `schemaMode` appears, `.omp/extensions/digest-schema.ts` does not exist at the pin, and no other code path writes a schema into a task call.
  verify: inspection
- SC-05 (orchestrator): On OMP 19.2.1, with this repository's `.omp/config.yml` and an agent carrying the `structured: true` and `output:` keys copied verbatim from the generated `.omp/agents/harness-documentor.md`, the task tool item schema exposes neither `outputSchema` nor `schemaMode`, the child's yield of an off-schema object is rejected with field violations, and a conforming object is accepted. The live probe receipt `notes/research-frontmatter-binding-probe.md` at the pin records each of the three observations and the git blob id of the agent file it copied, equal to that file's blob at the pin.
  verify: inspection
- SC-06 (code maintainer): At the pin every `.omp/agents/harness-*.md` frontmatter carries `structured: true` and an `output:` equal to the Python projection of its persona schema, `.omp/config.yml` leaves `task.structured` unset or false, and `check-omp-port.py` exits 0. In a fixture copy, each of these alone makes it exit 1 naming the file: a persona schema JSON edited without regenerating; one agent's `output:` hand-edited; one agent's `structured: true` removed; `task.structured: true` set (boolean true, string "true" and integer 1 each). qa shows the schema-edit case passing the pre-change check as the failing-first state.
  verify: automated        evidence: integration
- SC-07 (code maintainer): The Python projection loads all 16 personas and every alias, and refuses — naming the file and JSON pointer — malformed JSON, an unresolved reference, a reference cycle, a reference escaping the schema directory, an unsupported keyword, a property or array element with no type, enum or anyOf, an array without `items`, and an `anyOf` at the schema root. `gen-agent-output.py` run twice leaves byte-identical files, its `--check` exits 0 on a generated tree and exits 1 naming a drifted agent, and it leaves each agent's body and other frontmatter keys byte-for-byte unchanged.
  verify: automated        evidence: unit
- SC-08 (code maintainer): For each of the 16 personas, the generated `output:` at the pin is structurally equal to what the pre-change hook injected: `loadDigestSchemaBundle` from `git show 104252db:.omp/extensions/digest-schema.ts`, run over the pin's schema files. The reviewer runs T-03's parity command at the pin and cites its per-persona output.
  verify: inspection
- SC-09 (operator): At the pin, `.harness/README.md`, `.harness/harness/docs/BUILD.md`, `.harness/harness/docs/SPEC.md`, `.claude/skills/harness-team/SKILL.md` and `.harness/harness/docs/org.html` no longer tell dispatchers about `outputSchema`/`schemaMode` or say the hook injects a schema; each of README, BUILD and SPEC states that the schema reaches each harness child from its generated agent frontmatter (`gen-agent-output.py`) and that a yield the validator cannot check is refused, never passed; README contains no `feature.yaml`.
  verify: inspection
- SC-10 (operator): At `git show <review_sha>:.harness/harness/docs/DECISIONS.md` each amend row of `decisions_affected` (DEC-100, DEC-126, DEC-127, DEC-202, DEC-206, DEC-208, DEC-237) has its quoted clause replaced by text stating the new contract and naming BUG-2565, and `DECISIONS-INDEX.md` at the pin is regenerated with the hand-written rulings of DEC-100, DEC-127, DEC-208 and DEC-237 no longer asserting hook injection or a passing yield on validator failure.
  verify: inspection
- SC-11 (operator): The two questions the grilling left open are answered from measurement, not assumption: `notes/research-yield-refusal-probe.md` at the pin records, for OMP 19.2.1, whether a hook-refused yield consumes one of OMP's schema-retry attempts, how many refused yields a child made before it ended, the parent's task-result status, and that no hook-refused payload reached the parent; and README or BUILD at the pin states that measured behaviour.
  verify: inspection

## Verification gaps

- No test kind runs a live OMP child. What a hook-refused yield does to OMP's retry budget and to the parent's result (SC-11), and that OMP binds the generated frontmatter schema (SC-05), rest on main-run live probes recorded under this feature's `notes/` and read by the reviewer at the pin. A standing live-child runner is not raised here; `omp_session_accessor` and `handoff_comprehension` are the existing locally_run precedent.
- SC-08's parity against the deleted TypeScript loader is a one-time comparison with a historical blob; it cannot become a CI test because the integration job's shallow checkout cannot reach 104252db.
- typecheck is active (`bun run typecheck`) and covers the touched `.ts` files. component and ui have null runners and their detect globs match no file this feature touches; functional and eval are excluded under DEC-187 and carry no SC.

## Constraints

- DEC-174 BLOCKS team execution: every task is `execution_mode: main-session-direct`, because the change touches the yield gate, the task hook and the port check that would enforce its own build. DEC-179 SUPPLIES declaring each ungranted surface before signature.
- Ordering (operator): the fail-closed yield lands with or before the frontmatter route, because OMP's own check is permissive under frontmatter (it drops the schema after 3 failed yields). Encoded in `depends_on`.
- `schemas/digest/*.json` stay the only edited source of the digest contract; the frontmatter copy is generated and drift-checked by `check-omp-port.py`, which already owns the `task.structured` rule this reverses (BUG-2171 SC-02).
- DEC-233 SUPPLIES that `.omp/agents/**` stays unowned by every agent; the main session runs the generator.
- DEC-126, DEC-237, DEC-100, DEC-127, DEC-206 and DEC-208 are amended, never struck (DEC-188); DEC-254 SUPPLIES the five-field dispositions and requires a task owning DECISIONS.md.
- Non-harness task dispatches lose per-call `outputSchema` once global `task.structured` is off: accepted by the operator.
- Historical observation notes are not rewritten; no task lists one in `files:`.
- Assigned PRODUCT checkout: /Users/molchairuangutai/GitHub/harness/.claude/worktrees/harness/BUG-2565-digest-frontmatter-contract. `docs/spec.md`, `docs/decisions.md` and `docs/architecture.md` are absent there; the Harness docs under `.harness/harness/docs/` are the governing record and are edited by T-06.

## Out of scope

- Detecting outdated hook code in long-running sessions — #2566, a separate feature that follows this one.
- Rewriting historical observation notes or the 63 recorded refusals — they are the record.
- Asking OMP to stop persisting hook-revised tool input — upstream behaviour.
- The `runs/`/`notes/` artifact bloat found in the same session's audit — a separate concern.

## Approval

status: approved
approved-by: operator
date: 2026-11-27
