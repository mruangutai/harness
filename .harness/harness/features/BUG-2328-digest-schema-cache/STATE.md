<!-- TEMPLATE — instantiated at .harness/features/<FEAT>/STATE.md, ONE PER FLOW, owned by that
     feature's orchestrator (DEC-120). Per-feature because N concurrent flows would otherwise give
     a single project-level file N writers.

     Single writer. Every agent reads this at spawn,
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
SIGNAL, not a note: the orchestrator surfaces it, the MAIN SESSION asks the user and writes
the answers to .harness/features/<FEAT>/notes/answers-<runid>.md, and re-delegates the
orchestrator with that exact path — the only answers file it will trust (issue #671). Clear
each entry when it is answered.>

- <question, and who is blocked on it>
