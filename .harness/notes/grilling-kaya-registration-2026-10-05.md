# Grilling — Kaya registration — 2026-10-05

## Destination
Register `mruangutai/kaya` in the configured Harness fleet and publish the approved product decision and architecture artifacts.

## Mission
mission: patch
reason: Bounded administrative registration using the existing config schema and fleet convention; no enforcement implementation or new schema.
confirmed-by: operator (requested registration and artifacts; confirmed mirror and publication choices)

## Settled
- Product repository: `mruangutai/kaya`, default branch `main`.
- Mirror: operator selected “Enable mirror on Kaya #9”; use existing user-owned project 9, not a new project.
- Publication: operator selected “Config and product documents”; publish `.harness/harness.json`, the new architecture/decision artifacts, existing `docs/SPEC.md` unchanged, and README links to Kaya's `main`.
- Project type: web application with user-facing UI. Next.js, TypeScript, pnpm, Mastra, hosted Supabase, AI SDK UI through Mastra, Astryx, and generative UI are recorded in Kaya's decision register.
- Language: operator required no ambiguous language. Documents distinguish binding requirements, prohibitions, and unresolved implementation contracts. Accepted decisions cannot be reopened without explicit operator permission.
- Verification commands: no product application, manifest, or test runner exists. Every test command remains null with a concrete BLOCKED reason; no command is invented and no test kind is excluded.

## Not yet specified
None for the repository identity, mirror, publication, or technical classification. Application verification tooling is owned by Kaya issue #7, not inferred during registration.

## Out of scope
Implementing the Kaya application, selecting unresolved implementation contracts, planning a first feature, and repairing historical Harness state violations.

## Facts I verified
- `gh repo view` returned `mruangutai/kaya`, default `main`, and ADMIN permission; the branch API reported `protected: false` at `983fd90b4a4cdab3e26c321c19f2545a162d523e`.
- Project 9 is the existing user-owned Kaya project. Its Status options initially were Todo, In Progress, and Done; provisioning must preserve existing items and add missing Harness stations.
- Kaya had README and an untracked `docs/SPEC.md`, with no application source, package manifest, or tests.
- Harness was configured, its template directory was present, PyYAML and jsonschema imported, and `core.hooksPath` was `.claude/skills/harness/hooks`.
- The preflight state checker reported historical digest and abandoned-run violations. Those pre-existing records are not modified by this registration.
- Harness base: `62ff2fe8`; all Harness changes use `.claude/worktrees/harness/kaya-fleet-registration/`.
- Kaya commit `96b3912` landed the product config and documents on `main`; `factory_config.py --check-product-configs --repo mruangutai/kaya` exited 0 with one reachable config.
- Board provisioning exited 0 and added Backlog, Plan, Ready, Building, and Review to the existing Status field. Existing columns were retained.
- Board audit reported Item closed, Auto-close issue, and Pull request merged disabled. Registration is incomplete until the operator enables all three in the web UI and the audit passes.
- Local document consistency checks passed: nine local links resolve, nine accepted decision IDs are unique, and all architecture decision references resolve.
