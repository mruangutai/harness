# Operator decisions — FEAT-56 re-scope

The operator rejects the prior Claude-Code-only and combined-command implementation, while retaining the central onboarding goal.

1. **Revise issue #206 in place.** Do not ship a narrowed FEAT-56 or create a successor.
2. Implement a provider-neutral **skill named `harness-add-repo`** for adding a repository to an already configured fleet.
3. Include the missing **OMP command-door port in this same feature** so the provider-neutral surface is actually reachable through OMP.
4. Move the first-BRIEF, approval, and design work out of repository onboarding; when a configured fleet repository lacks its first BRIEF, route it to **`/harness-plan`**.

`harness-init` must be isolated to first-time configuration of a fresh Harness checkout. `harness-add-repo` must register a repository into the configured control plane. The OMP surface must work with Claude Code, OpenAI, and other providers through OMP, rather than implementing a Claude-Code-only path.

The operator raised `max_total_cycles` from 11 to 22 for this replan.
