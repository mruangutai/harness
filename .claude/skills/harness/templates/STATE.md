<!-- TEMPLATE — ORCHESTRATOR-OWNED, single writer. Every agent reads this at spawn,
     so it must stay small: `## Current` and `## Open Questions`, nothing else.

     HISTORY DOES NOT LIVE HERE. The activity stream is .harness/logs/<date>.md,
     appended as each DIGEST arrives and never loaded at spawn. That separation is
     why this file needs no rotation rule — both sections are self-clearing. -->

# STATE

## Current

- feature: <FEAT-NN or none>
- run: <.harness/features/<feat>/runs/<run-id>/state.yaml — a POINTER, never a copy>
- squad: <product | eng | validator | none>
- status: <idle | in-flight | awaiting-user | blocked>

## Open Questions

<The channel from subagents to the user. A non-empty entry is an ACTIVE ROUTING
SIGNAL, not a note: the orchestrator asks the user, writes the answers to
.harness/notes/answers-<FEAT>-<runid>.md, and re-delegates with that path. Clear
each entry when it is answered.>

- <question, and who is blocked on it>
