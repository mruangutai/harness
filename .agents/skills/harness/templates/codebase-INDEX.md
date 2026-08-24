<!-- TEMPLATE — instantiated at .harness/codebase/INDEX.md by the understand-codebase playbook,
     owned by DOCUMENTOR only (DEC-137). HARD CAP: 60 lines — this file is injected into EVERY
     agent spawn; every line here costs ~44 spawns per feature. One line per entry, pointers only:
     anything that needs a second line belongs in the file it points to. The injection hook
     truncates at 80 lines as a backstop, silently — stay under the cap so nothing is ever cut. -->

# Codebase map — INDEX

> Map is a HINT; code is truth. Every claim in the detail files carries a file:line anchor —
> verify the anchor before relying on a load-bearing claim. Sections marked `stale: FEAT-NN`
> are awaiting their owner's refresh; trust them less.

## Views (owner · one line on what it answers)

- architecture.md        — documentor · how the pieces fit; module boundaries; where control flows
- domains/<module>.md    — backend-dev · what code belongs to each domain, entry points per module
- api-surface.md         — backend-dev · endpoints/services, inputs/outputs, contracts
- data-flows.md          — data-engineer · schemas, stores, how data moves and mutates
- ui-surface.md          — frontend-dev · screens/components, state, user-facing flows
- llm-patterns.md        — ai-dev · model calls, prompts, agents, eval hooks
- trust-boundaries.md    — security-reviewer · where untrusted input crosses, authn/z seams
- stack.md               — dev-ops · frameworks, build, test runners — what, where, and why
- product-surface.md     — pm · what the product does, for planning and success criteria

## Domains

<!-- one line per domain module: name — path glob — one-phrase purpose. THE map's spine. -->

## Provenance

<!-- mapped: <date> at <sha> · refreshed: <FEAT-NN list> -->
