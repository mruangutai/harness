# Build QA — BLOCKED

The configured QA gate cannot discover or run either required suite: both active commands stop during runner root resolution before any named test executes. This is gate misconfiguration, not an assertion failure.

## Scope and diff

- `review_sha`: `none`; baseline `7ccfae8dd7644bc3aaea612dabf4317c0d804f99` (`git merge-base HEAD origin/main`), HEAD `df63193f7ec9798d9660904e0e4e7c78d52358f5`.
- HEAD contains planning only; the complete feature is the baseline-to-working-tree delta: 33 tracked changed paths plus 22 untracked paths. The known dirty state is the feature implementation and is enumerable, so it did not make scope ambiguous.
- Logical classifications: grading library/CLI/policy and their tests are `logic`; validator/reviewer cutover and generated-agent delivery are `cross_module`; owner-manifest route resolution is `bugfix`; runner/matrix registration is `config`; guidance/glossary are `docs`.
- Matrix floor: `unit` for `logic` and `bugfix`; `unit` plus `integration` for `cross_module`. Neither change predicates require other kinds. `functional` is signed excluded (DEC-187). `component`, `ui`, `typecheck`, and `eval` are not required for this diff.

## Coverage presence and Phase-1 reconciliation

Before reading implementation, the brief required tests for hand-derived all-grade metric fixtures; bidirectional grade movement; changed-function set exactness; CLI fields/statuses/determinism/ungraded input/reason demand; skill-example and five-agent delivery conformance; gate-policy loading/evaluation; reviewer digest policy cutover; and owner-manifest route regression.

The changed test files contain direct coverage for those behaviors: `test-code-grade.py:19-41,111-173,177-230,240-264`; `test-code-grade-cli.py:51-111`; `test-gate-policy.py`; `test-validate-digest.py:1636-1648,1708-1782`; and `test-check-plan-routes.py:1379-1453`. Registration is present in `run-unit-tests.sh:30-32`; `test-code-grade-cli.py` is also in the integration detect string (`harness.json:119`). No coverage assertion gap was found by behavioral inspection.

The brief's documented gaps reconcile as follows: SC-11 is `verify: uat`, not an `ai_behavior` diff, so the null `eval` runner is not gate-required; no component/UI/TypeScript surface changed; functional is explicitly excluded; coverage instrumentation is absent but is not a configured test kind. None relaxes unit or integration.

## Required commands

| Kind | Configured command | Outcome | Discovery/state |
|---|---|---|---|
| unit | `.agents/skills/harness/bin/run-unit-tests.sh --kind unit` | exit 2 | `run-unit-tests.sh: no harness root could be resolved from .../.agents/skills/harness/bin — refusing to run`; zero named tests discovered; **misconfigured** |
| integration | `.agents/skills/harness/bin/run-unit-tests.sh --kind integration` | exit 2 | same pre-discovery root-resolution failure; zero named tests discovered; **misconfigured** |

The configured path resolves physically to `.claude/skills/harness/bin/run-unit-tests.sh`, but the runner derives `_SELF_BIN` from the symlink-spelled invocation (`run-unit-tests.sh:10-14`) and rejects it. The fix target is the configured invocation/root-resolution contract, not feature assertions.

## History and findings

`git log 7ccfae8..HEAD -- <changed production and test paths>` returned no commits: implementation and tests are uncommitted working-tree changes. Test-first ordering is therefore not observable; this is recorded but is not gate-failing.

- **BLOCKED finding BQ-01:** active `unit` and `integration` commands in `.harness/harness.json` cannot run from the configured `.agents/...` spelling. Restore root resolution for that configured command, then rerun both kinds and require named discovery.
- Must-fix from substantive coverage/assertion inspection: none. Initial gate cycles/send-backs: 0.

Open questions: none.
