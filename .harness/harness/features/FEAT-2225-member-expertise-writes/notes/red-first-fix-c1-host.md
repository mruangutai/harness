# Red-first — validate c1 fix, HostTool slice (F1 host, F3)

Owned files: `.omp/extensions/harness-hooks.ts`, `tests/unit/omp-hooks.test.ts` and `tests/integration/test-member-expertise.py`.

## F1 — registered distill authority before member-ops

The test came first. Command: `bun test tests/unit/omp-hooks.test.ts`, run against the host that had no authority call. The real `validate-digest.py --distill-authority` from the DigestContract slice was already in the worktree.

Result: **155 pass, 2 fail**.

- `OMP task lifecycle adapter > FEAT-2225 F1: a distill marker under a non-distill registered run is refused and member-ops never runs`.
  - Mocked runner. The authority CLI refuses (exit 2, exit 1, `{"authorized": false}`, or empty stdout).
  - Observed: `apply` resolved, so the error was `undefined` instead of `expertise_apply refused`.
- `FEAT-2225 expertise_apply through the real policyRunner into the real core > F1: a distill marker under a non-distill registered run applies nothing`.
  - Real lineage. feature.json registers the eng-lead's run as `build-engineering`, and the dispatch carries `HARNESS-MISSION: distill`.
  - Observed: `harness-eng-lead`'s apply succeeded under the marker alone.

Fix: after `applyPlacement`, `expertise_apply` now calls `policyRunner(<feature root>, "validate-digest.py", ["--distill-authority"], {agent_type, harness_feature, harness_agent_id, harness_parent_agent_id, cwd})`. Only an unblocked answer with no reason and a `{"authorized": true}` line grants authority. Anything else throws `expertise_apply refused: <reason>`, and member-ops never runs.

Green: **157 pass, 0 fail**. In the real case, both the lead and its member are refused with `expertise_apply refused: distill-authority: REFUSED …`. Neither an Expertise file nor a receipt is written.

## F3 — real host→core coverage

This is new test code over existing host behaviour, so its fail-first evidence is a mutation check against one gate.

New describe: `FEAT-2225 expertise_apply through the real policyRunner into the real core`. It uses the module's own runPolicy, with no injected runner. Each session's real run start makes the real claims, and feature.json registers `distill-product`, `distill-engineering` and `distill-validator`.

The fixture is an isolated copy. Each temporary committed checkout carries:
- the root marker `.harness/team-config.yaml`;
- its own copy of `.claude/skills/harness/bin`;
- the `.agents/skills -> ../.claude/skills` symlink;
- copies of `.omp/extensions/harness-hooks.ts` and `digest-schema.ts`.

The test imports the copied module. Every gate, including `--distill-authority` (through `resolve_root` → `root_from_script`), then resolves the temporary checkout through the marker. No environment variable is involved.

It replaced a first version that named the root through the retired env chain, which `tests/unit/test-no-distribution.py` case6 refuses. A probe showed why the copy is needed: with cwd set to a marker-carrying temporary checkout and no override, the authority CLI answered exit 2, `no live claim binds runtime Orch.Eng to FEAT-9003-host-core`. `resolve_root` never reads cwd, so the owner was the shipping checkout, and that checkout's worktree family does not include the temporary one.

- Five representatives: product-lead, code-reviewer, dev-ops, orchestrator and backend-dev.
- Each applies `add P-01 + add G-01` and then `replace P-01 + drop G-01` on both the craft tier and the `harness` repository tier.
- Each asserts the returned receipt verbatim, the before/after counts, the destination and the file content.
- Each checks every receipt with the real `expertise-merge.py verify-receipt`.
- One more case: a claim under another persona's name is refused by verify-receipt.

Mutant 1: the host forwarded `--persona harness-qa` instead of the bound persona. Command: `bun test tests/unit/omp-hooks.test.ts -t "real policyRunner"`.

Result: **2 pass, 5 fail**. All five representative flows failed; the two that passed were the forged-persona case and F1. I ran it with the env-variable fixture and again with the isolated copy, and got the same result both times. The mutant was then reverted; the edit tool's snapshot tag is identical to the green state.

Mutant 2, on the isolated copy: `expertise_apply` ignored the authority refusal. Command: `bun test tests/unit/omp-hooks.test.ts -t "F1"`.

Result: **0 pass, 2 fail**. Both the mocked and the real F1 tests failed. The mutant was then reverted to the same snapshot tag.

`tests/integration/test-member-expertise.py` keeps the all-16 configuration checks and the guidance checks. Its direct-CLI flows are removed, because the real host flows above replace them.

## Acceptance (after the isolated-copy fixture)

`python3 tests/unit/test-no-distribution.py`: exit 0, case6 passes.

`python3 tests/unit/test-digest-schemas.py && bun test tests/unit/omp-hooks.test.ts && python3 tests/integration/test-member-expertise.py`

- Exit 0 in 16.9 s wall.
- Schemas: 34 OK.
- bun: 157 pass, 0 fail.
- member-expertise: 0 failures.

`code-grade.py tests/integration/test-member-expertise.py`: RESULT PASS, 10 passing functions at bar 3. code-grade cannot parse TypeScript, so `harness-hooks.ts` and `omp-hooks.test.ts` are ungraded.
