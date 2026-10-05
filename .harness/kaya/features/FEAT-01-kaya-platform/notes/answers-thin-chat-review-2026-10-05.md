# Operator review — FEAT-01-kaya-platform

## Source and authorization

The operator completed the review pass: "that's it. revise so i can review again." This authorizes one consolidated planning revision, not implementation, signing, build entry, deployment, or merge. BRIEF and plan remain pending.

## Operator feedback

"for either success criteria and/or definition of done, where is the UI that needs to be tested? it looks like the operator where you define \"get a real answer locally\" and \"observe that the answer's operational state survives restarting\" but no where in the doc does it say anything about a thin chat interface to do so. it should."

Main proposed the following understanding and the operator replied "that's much better":
- Definition of done: send a message, see a real Anthropic answer, restart the application, and reopen the persisted conversation—all through the browser.
- Success criteria: input/send controls, visible user/assistant messages, pending/error states, and browser verification of conversation restoration after restart.
- Use accepted Astryx + AI SDK UI + Mastra integration and binding folder convention.
- Financial renderers, Gmail, login, and full product chat remain excluded.
- CLI probes supplement, not replace, UI acceptance.

## Revision boundary

Replace the static-only/API-only promise with a minimal functional chat surface. Revise perspectives, SCs and verification methods, frontend/backend task contracts, version/protocol compatibility work, test runners, design/prototype determination and UAT steps coherently. Remove every conflicting static-only exclusion, no-interactive-UI/prototype assertion and stale UI-runner rationale. Keep hosted schema isolation, provider selection, fresh-clone setup, secret protection and unchanged exclusions. Do not add financial tools/renderers, multiple-conversation management, uploads, authentication screens or production functionality without operator approval.

Do not ask the operator to re-confirm this already settled review feedback. PM derives criterion wording/numbering and task decomposition; visual designer owns the necessary design contract/prototype decision. The existing localhost stub-token boundary must not expose real keys through the browser; settle a secure browser-compatible local flow in the plan.

## References

Original confirmed intake: .harness/notes/grilling-kaya-platform-2026-10-05.md. This review supersedes only its static/API-only interpretation; it does not replace the accepted technology stack or open unrelated product scope.

Product source: /Users/molchairuangutai/GitHub/harness-factories/kaya/.claude/worktrees/kaya/FEAT-01-kaya-platform/docs/ARCHITECTURE.md and docs/DECISIONS.md. Architecture Source organization is landed at Kaya 6303f9f.

Existing reviewed-but-unsigned working artifacts: BRIEF.md, plan.yaml, feature.json, STATE.md and notes/handoff-plan.md in this feature directory. Kaya issue #14 must be updated by main after the revised plan is complete, without claiming approval or implementation.
