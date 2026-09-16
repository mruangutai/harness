# Runtime handoff — how a dispatch ends and how you are woken

Read this before your first dispatch of a run, if you dispatch at all: orchestrator and the three
domain leads. Members never need it. Evidence and history: DEC-201, DEC-204, DEC-210, DEC-214.

## The host supervises every dispatch

Under OMP, the outer orchestrator is background-dispatched and wakes the main session through a
terminal async result; nested leads and members are `blocking: true`, so their parent model is
inactive inside the task tool until the child is terminal. Neither route permits shell supervision,
sleeps, `hub wait`, or repeated status calls.

## On the tool result or wake

Re-read the durable checkpoint and verify the cited artifact before accepting a verdict — the
member's transcript is not the record; the file at its `artifact:` path is.

## Terminal signals

`yield` is the terminal Harness handoff; `agent_end` is notification-only. Claude Code keeps its
measured end-turn/wake compatibility rule (DEC-201/204) — under that host, never wait for a member;
suspend the turn (harness-team carries the `SUSPENDED` shape).

## Personas without a shell

A persona that holds no shell cannot resolve the feature-tree root itself. You supply it on a
`HARNESS-FEATURE-TREE-ROOT: <absolute path>` line of the dispatch; dispatch-guard.py refuses its
absence at exit 2 (DEC-214).
