# STATE

## Current

- feature: FEAT-56-central-onboarding-model
- run: none
- squad: none
- status: awaiting-user

RE-SCOPED BY THE OPERATOR AT THE UAT GATE, 2026-09-08. Do not ship. The built work at
`review_sha` 9b72dd4b is complete and green — eight tasks done, qa gate green, review panel PASS,
nine of ten SCs met — but SC-09 FAILED a third time on a finding that is not a defect in the
delivery: it rejects the SCOPE. The operator confirms the central-model goal and rejects the
Claude-Code-only implementation and the combined command.

Their required outcome, as relayed by the main session: OMP must expose provider-neutral onboarding
usable with Claude Code, OpenAI or any model provider; `harness-init` becomes ONLY fresh Harness
configuration; adding a repository becomes a separate, clearer command, `harness-add-repo` unless
source conventions require another established name.

Consequences already recorded: feature station returned to `plan`; UAT and ship readiness
invalidated; `cycles_used` 11 of a raised `max_total_cycles` 11, so the budget is SPENT and a
revised plan needs a new figure recorded before any build resumes. The approval on both fragments
still reads approved for the OLD task set and must be reset to pending by the main session — no
agent, this one included, may write it.

Nothing is reverted. The delivered work stands as the substrate the revision builds on.

## Open Questions

- The approval on BRIEF.md and plan.yaml must be RESET to pending: the task set is materially
  changing and the old signature cannot carry it. Main session only.
- `max_total_cycles` must be raised again, or the revision must be scoped to fit no further rework.
  11 of 11 are spent. An operator decision, recorded in feature.json.
- Whether the revision proceeds inside FEAT-56 or as a successor feature: the delivered central
  model is sound and shipped-ready, and the new scope adds provider neutrality and a command split.
  pm's recommendation is required and the operator decides.
- Backlog rows B-1..B-13 remain undisposed. No PR, no issues, held as instructed.
