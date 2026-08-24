# OMP provider parity evidence

Issues: #589, #596  
Baseline: `.harness/notes/omp-port-baseline.md` at `98976844a473c9e853c16ea2a82de8ec75088f1c`  
OMP: `18.0.4`  
Captured: 2026-08-24

## Result

**PASS.** OpenAI and Anthropic both completed the required four-layer Harness workflow with all five final handoffs accepted, no files changed, canonical identities preserved, and OMP lifecycle enforcement active while Claude discovery was disabled.

```text
harness-orchestrator
  → harness-eng-lead
      → harness-backend-dev
  → harness-validator-lead
      → harness-code-reviewer
```

## OpenAI

Configuration: `.omp/providers/openai.yml`

| Agent | Model | Final handoff |
| --- | --- | --- |
| `harness-orchestrator` | `openai-codex/gpt-5.6-sol` | accepted |
| `harness-eng-lead` | `openai-codex/gpt-5.6-sol` | accepted |
| `harness-backend-dev` | `openai-codex/gpt-5.6-terra` | accepted |
| `harness-validator-lead` | `openai-codex/gpt-5.6-sol` | accepted |
| `harness-code-reviewer` | `openai-codex/gpt-5.6-sol` | accepted |

The orchestrator returned `feature: OMP-PARITY`, `status: shipped`, `cycles_used: 0`, `briefing: none`, and `artifact: none`. No failure remained. The standard worker's `terra` selection is the configured capability tier, not drift.

## Anthropic

Configuration: `.omp/providers/anthropic.yml`

| Capability | Model |
| --- | --- |
| `deep`, `strong` | `anthropic/claude-opus-5` |
| `standard`, `review` | `anthropic/claude-sonnet-5` |

The final hierarchy run completed both canonical chains with every agent returning PASS and `artifact: none`. Both leaves ran exactly `true`; both leads reported one matching member; the orchestrator returned the required shipped OMP-PARITY digest. No agent substituted a dynamic roster id for its `HARNESS_AGENT_ID`.

One reviewer first emitted `findings: []` where the established schema requires the integer count `findings: 0`; enforcement rejected it and the agent corrected it. This was a deliberate probe-wording ambiguity, not a provider or runtime failure.

## Last-turn yield interoperability

Anthropic agents may emit the digest in assistant text and call OMP's accepted last-turn form with `result.type: result` and `data` omitted. The OMP extension now captures cumulative assistant text from `message_update`, validates that text, and rewrites the yield into explicit `result.data.content` before tool schema validation.

A focused Anthropic probe observed:

- one assistant turn containing the complete valid digest;
- exactly one accepted-form yield;
- no digest rejection or retry;
- delivered output byte-identical to the assistant-turn contract.

An actually empty result object remains invalid in OMP's own yield schema and is correctly rejected. It is not the accepted last-turn form.

## Native guardrails

With `disabledProviders: [claude]`, OMP directly demonstrated:

- all 16 canonical `.omp/agents` discovered;
- exact orchestrator → leads → owned leaves spawn allowlists;
- required `autoloadSkills` present;
- tiered Expertise injected before agent work;
- out-of-domain `write` denied before execution;
- reviewer Bash write denied before execution;
- invalid branch creation denied;
- malformed digest rejected and corrected;
- valid structured and accepted last-turn digests accepted;
- provider overlays selecting the expected model families.

## Claude Code compatibility

Claude Code directly demonstrated:

- shared `AGENTS.md` guidance loaded through `CLAUDE.md`;
- generated `harness-*` role adapters discovered;
- Expertise injected through `SubagentStart`;
- an out-of-domain backend write denied through `.claude/settings.json`;
- canonical scripts resolved through `.claude/skills` → `.agents/skills`.

## Deterministic verification

All commands passed:

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

## Comparison with the pre-port baseline

| Contract | Baseline | Port |
| --- | --- | --- |
| 16 named roles | present | preserved under native `.omp/agents` |
| Required hierarchy | passed | passed under both providers |
| Skill catalog | present through Claude source | preserved through `.agents/skills` |
| Expertise injection in OMP | missing | restored |
| Domain write denial in OMP | missing | restored |
| Reviewer Bash denial in OMP | missing | restored |
| Branch gate in OMP | missing | restored |
| Digest enforcement in OMP | missing | restored, including last-turn yields |
| Claude Code behavior | present | preserved through adapters |

No unresolved provider-parity failure remains.
