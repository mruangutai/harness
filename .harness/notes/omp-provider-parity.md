# OMP provider parity evidence

Issues: #589, #596  
Baseline: `.harness/notes/omp-port-baseline.md` at `98976844a473c9e853c16ea2a82de8ec75088f1c`  
OMP: `18.0.4`  
Captured: 2026-08-24

## Result

OpenAI completed the required hierarchy with every final handoff accepted and no unresolved failure. Anthropic completed the same hierarchy with every final handoff accepted, but a valid digest carried only in the assistant turn was rejected when `yield` omitted its payload. The agent recovered by yielding explicit structured data.

The port is therefore provider-functional but not ready to claim strict digest-transport parity without a user decision: accept bounded correction retries as part of the contract, or authorize another implementation attempt after the agreed three-attempt stop.

## Canonical hierarchy

Both providers ran:

```text
harness-orchestrator
  → harness-eng-lead
      → harness-backend-dev
  → harness-validator-lead
      → harness-code-reviewer
```

Canonical identity came from each OMP role's `HARNESS_AGENT_ID:` marker, never its dynamic roster id. Spawn allowlists exposed exactly the required edges and leaves had no spawn targets.

## OpenAI run — PASS

Configuration: `.omp/providers/openai.yml`

| Agent | Model | Final handoff |
| --- | --- | --- |
| `harness-orchestrator` | `openai-codex/gpt-5.6-sol` | accepted |
| `harness-eng-lead` | `openai-codex/gpt-5.6-sol` | accepted |
| `harness-backend-dev` | `openai-codex/gpt-5.6-terra` | accepted |
| `harness-validator-lead` | `openai-codex/gpt-5.6-sol` | accepted |
| `harness-code-reviewer` | `openai-codex/gpt-5.6-sol` | accepted |

The orchestrator returned `feature: OMP-PARITY`, `status: shipped`, `cycles_used: 0`, `briefing: none`, and `artifact: none`. No files changed and no failure remained. The standard worker's `terra` model is an intentional capability-tier mapping, not drift.

## Anthropic run — final handoffs PASS, transport parity BLOCKED

Configuration: `.omp/providers/anthropic.yml`

| Agent tier | Configured model |
| --- | --- |
| `deep`, `strong` | `anthropic/claude-opus-5` |
| `standard`, `review` | `anthropic/claude-sonnet-5` |

All five final handoffs were accepted. Both leaves ran exactly `true`, touched no files, and returned PASS. Both leads returned one matching member. The orchestrator returned the required shipped OMP-PARITY digest.

Three first attempts were rejected:

1. Engineering lead used a bare-string member without `verdict`; this was a probe-prompt defect and corrected normally.
2. Validation lead put a fenced contract under a structured wrapper key not recognized by the adapter; it corrected to the supported structured contract.
3. Orchestrator emitted a valid digest in its assistant turn and called `yield` with omitted data. The adapter had no access to that current-turn text at `tool_call`, saw an empty payload, and rejected every field as missing. It accepted the identical values once explicitly included in yield data.

The third item is the unresolved interoperability defect. Unit coverage proves `yieldContractText({}, fallback)` uses a supplied fallback, but OMP's `message_end` notification occurs after `tool_call`; the extension has not observed the current assistant text when it validates an empty yield.

## Guardrail evidence

With Claude discovery disabled (`disabledProviders: [claude]`), native OMP behavior was observed:

- required skills autoloaded for `harness-backend-dev`;
- tiered Expertise was present in initial context;
- out-of-domain `write` was denied before execution;
- reviewer Bash write was denied before execution;
- invalid branch creation was denied;
- malformed `DONE` digest was rejected and corrected;
- valid structured digest was accepted;
- provider overlays selected the intended model families.

Claude Code compatibility was separately observed:

- Claude Code loaded shared `AGENTS.md` guidance and generated role adapters;
- `SubagentStart` still injected Expertise;
- the generated backend adapter's out-of-domain write was blocked through `.claude/settings.json` using canonical `.agents/skills` scripts.

## Deterministic verification

Passed:

```bash
bash .agents/skills/harness/bin/run-unit-tests.sh
python3 .agents/skills/harness/bin/check-omp-port.py
bash .agents/skills/harness/bin/check-state.sh
python3 -m compileall -q .agents/skills/harness/bin
bun test ./.agents/skills/harness/bin/omp-hooks.test.ts
bun build .omp/extensions/harness-hooks.ts --target bun --outfile /tmp/harness-hooks.js
git diff --check HEAD
```

`check-state.sh` exited 0 with the repository's pre-existing informational notes.

## Attempt record and stop

Digest transport work used three discriminating implementation/debug steps:

1. Directly validating `yield.result` exposed OMP structured wrappers.
2. Rendering structured `result.data` into the normative digest text fixed explicit structured yields.
3. Adding a prior-assistant fallback fixed the pure function but not runtime ordering: `message_end` has not fired when `tool_call(yield)` is intercepted.

The agreed stop condition fires here. The next hypothesis is to capture assistant text incrementally from `message_update` before `yield`, but implementing it would be a fourth attempt at the same blocker.

## Human decision required

Choose one:

1. Accept provider parity with bounded digest correction retries; all final handoffs and every other invariant pass.
2. Authorize a fourth attempt to capture current-turn assistant text before empty-yield validation.
