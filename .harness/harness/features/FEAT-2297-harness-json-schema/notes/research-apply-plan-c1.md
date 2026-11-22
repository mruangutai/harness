# Apply c1 — shared contract; c2 correction recorded separately

OQ-SMOKE is resolved by the operator ruling; S1–S4 are applied. The c1 readers found a retained contradictory T-03 paragraph, corrected in notes/research-apply-plan-c2.md. No implementation or exit goal-check is claimed; the host must collect the narrow T-03 re-review first.

## Shared task contract

### Execution and authority — all tasks

Product is Harness in /Users/molchairuangutai/GitHub/harness/.claude/worktrees/harness/FEAT-2297-harness-json-schema. All relative file edits stay inside that feature checkout. Read inputs: /Users/molchairuangutai/GitHub/harness/docs/spec.md, /Users/molchairuangutai/GitHub/harness/docs/decisions.md and /Users/molchairuangutai/GitHub/harness/docs/architecture.md are absent; do not invent their contents. AGENTS.md independently identifies /Users/molchairuangutai/GitHub/harness/.harness/harness/docs/SPEC.md and /Users/molchairuangutai/GitHub/harness/.harness/harness/docs/DECISIONS.md as actual Harness authority; consult their relevant config/test/state sections and indexed decisions. Execute main-session-direct under DEC-174, never through harness-eng-lead. The superseding smoke-removal ruling in notes/simplify-plan-c0.md applies; all other thirteen settled choices in /Users/molchairuangutai/GitHub/harness/.harness/notes/grilling-harness-json-schema-2026-11-22.md bind this work, as do the signed D choices. For behavioral changes, write focused tests first and observe the intended assertion failing against the pre-change implementation, not an import/usage failure; then production code and refactor only when green. No new matrix condition evaluator or plan-time evidence reconciliation: issue 2293 is excluded. 
Read BRIEF.md and D-01–D-08 in plan.yaml. Future dispatches carry this shared-contract reference together with their task-specific intent and literal verify block. Authority consultation is surface-relevant, not ten ritual full-document rereads.

Smoke disposition — remove only mruangutai/harness-factory-smoke from .harness/factory/fleet.yaml; leave its repository untouched, retain Kaya and every other fleet setting, and never weaken validation or suppress remaining refusals. This settled ruling supersedes all pre-ruling expected aggregate-failure/no-membership-removal/pending-disposition instructions, not the remote-authority contract. Permanent reader tests use synthetic remote-invalid/source-authority/aggregate-refusal cases. Exact shipped membership preservation belongs only to T-10's bounded feature receipt at the supplied base/review refs; remaining-fleet validation outcomes are reported factually, not required to become green before Kaya migration. SC-02/SC-10 retain their full regression obligations and SC-08 still requires the authorized Kaya remote-main landing.

### Fixture and inventory — every task touching config fixtures

Use only tests/harness_config_support.py build_config/write_config for every valid serialized harness.json fixture, local or remote, shared or inline. Convert inline constants, JSON dictionaries, empty configs, version overrides, remote base64 payloads and later rewrites, not just shared setup. For deliberate invalid inputs build a valid base and explicitly corrupt a field or its serialized bytes; missing-file cases explicitly omit/remove the built file. Preserve non-config schema_version data and already-validated in-memory domain stubs. Use supported kind/change-type names instead of custom_kind, service or widget in config fixtures, migrating their plan consumers together. Preserve excluded-kind and active-null-command semantic cases. For every inventory source row in /Users/molchairuangutai/GitHub/harness/.harness/notes/test-inventory-harness-json-schema-2026-11-22.md belonging to these files, implement its signed disposition from notes/research-config-contract.md. Delete every REMOVABLE row except the two explicitly retained policy cases; record a specific reason for retained coverage. Every UPDATE-BEHAVIOR asserts refusal for malformed/missing input, or the signed default for absent optional keys; never convert optional absence into an error. Keep unrelated transport, feature-record, board write, grading and runner-spawn failure behavior intact. Reduce duplication by delegation/parameterization, never assertion weakening, minification or moving counted test code outside the measured set. 

### Verification and ownership — all automated task gates

The literal verify command must exit 0 within 60 seconds with every reported assertion passing; any failure or reported FAIL is failure. These bounded phase gates do not replace final configured unit/integration evidence. Tasks must not edit predecessor-owned files; the full census and reader/schema checks repeat in T-10 after the final local changes. T-09 instead retains its literal operator-executed MANUAL verification and mandatory SC-08 authorization. T-10 runs the final census after its own local changes, not after imaginary later fixture tasks.

## Individual dispositions and classification

- OQ-SMOKE: applied; T-03 owns removal of only mruangutai/harness-factory-smoke from .harness/factory/fleet.yaml, preserving Kaya and every other fleet setting; smoke repository untouched. T-08 records the resolved disposition; T-10 owns exact shipped membership proof and reports actual remaining-fleet outcomes, without a pre-Kaya live-fleet green assertion. Original application delta: substance, task, T-03/T-08/T-10. The c2 substance correction is confined to T-03's retained contradictory instructions; membership-proof relocation is proportionality, T-03/T-10, without re-panel. Inherited should-not-exist finding remains med/substance/task as in panel-c0.md; no severity regrading.
- S1 (source priority 2): applied, T-10; proportionality/task. Remove duplicate checker controls for inline bypass and ordinary reader routing; retain T-02/T-03 suites and their negative controls, invoked cumulatively by T-10. Undisposed-row, stale-fail-open and nonnegative-delta controls remain.
- S2 (source priority 2): applied, T-01–T-10; form deduplication. Shared rules above are binding by explicit intent reference; individual logic, ownership except S3/smoke, traces, dependencies and every literal verify remain. No SC weakened.
- S3 (source priority 2): applied, T-01/T-03; proportionality/task ownership consolidation, not a new behavioral contract. Generic API and contract tests remain T-01; digest_schema.SchemaStore._load_one and run_identity.read_marker migrations and their classifications move together to T-03.
- S4 (source priority 2): applied, T-08; proportionality/task. Schema alone enumerates exact defaults and closed vocabulary; SPEC describes boundary semantics, README upgrade usage, DECISIONS rationale, all citing schema fields. SC-07 still inspects agreement at the pin, including defaults/conditional requirements/vocabulary by schema reference.

Actual c1 changed task IDs: T-01, T-02, T-03, T-04, T-05, T-06, T-07, T-08, T-09, T-10. The c1 scoped re-panel covered only substance delta T-03/T-08/T-10 (scope and independent should-not-exist), not S1–S4 proportionality/form trims. Actual c2 changed task IDs are T-03/T-10; only T-03 substance requires narrow re-review. Design self-scope-out remains valid: no interaction surface, prototype unnecessary and operator-overridable. All original decisions and SC text are preserved. Cycle-1 fan-in is now recorded with prior finding identities unioned and applied findings dispositioned; see notes/research-apply-plan-c2.md. The single exit goal-check remains host-final-step work after T-03 re-review.

## Historical c1 plan check

The c1 authorized plan-merge.py check exited 0. Exact command:

```text
python3 /Users/molchairuangutai/GitHub/harness/.agents/skills/harness/bin/plan-merge.py check --file /Users/molchairuangutai/GitHub/harness/.claude/worktrees/harness/FEAT-2297-harness-json-schema/.harness/harness/features/FEAT-2297-harness-json-schema/plan.yaml --root /Users/molchairuangutai/GitHub/harness/.claude/worktrees/harness/FEAT-2297-harness-json-schema
```

Exact stdout:

```text
OK T-01 11 anchor(s) resolved
OK T-02 4 anchor(s) resolved
OK T-03 29 anchor(s) resolved
OK T-04 14 anchor(s) resolved
OK T-05 11 anchor(s) resolved
OK T-06 11 anchor(s) resolved
OK T-07 13 anchor(s) resolved
OK T-08 5 anchor(s) resolved
OK T-09 2 anchor(s) resolved
OK T-10 2 anchor(s) resolved
CHECK /Users/molchairuangutai/GitHub/harness/.claude/worktrees/harness/FEAT-2297-harness-json-schema/.harness/harness/features/FEAT-2297-harness-json-schema/plan.yaml against /Users/molchairuangutai/GitHub/harness/.claude/worktrees/harness/FEAT-2297-harness-json-schema: 10 task(s), 102 anchor(s) resolved, 0 failure(s)
```

At c1, all 12 successful task-changing invocations printed their captured stdout; none emitted APPROVAL-RESET:, so no gh-sync or other remote call ran. Amend's automatic changed-state reporting still named unsigned BRIEF and missing INV-37 Build-entry receipt, with pending approval and historical-cycle attribution notes; these were not represented as a passing state gate. One list-field --show invocation initially exited 4 without --yaml-value; the corrected typed read and both ownership amendments succeeded. Approval was not edited. At c1 no record-panel, goal-check, implementation tests/builds/lint/formatters ran. Subsequent c2 panel recording, correction and check evidence is in notes/research-apply-plan-c2.md.
