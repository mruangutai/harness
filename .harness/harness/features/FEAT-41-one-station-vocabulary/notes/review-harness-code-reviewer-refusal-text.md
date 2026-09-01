# Scoped review — FEAT-41 operator-facing refusal text

Read: `plan.yaml` (full, both halves) and `BRIEF.md` at the state present on 2026-08-25 while
harness-pm was concurrently editing T-06/D-09/T-12/a plan-level condition clause. None of the three
scoped items sit in files those edits touch, so nothing below reflects an in-flight paragraph.

## Verdict summary

One must-fix (T-09), one informational note (T-08). Item 3 (exit codes 3/4) is clear as specified —
no finding.

## Finding A — T-09's Edit/Write denial has WHAT and WHAT-TO-DO but no WHY (high, must_fix)

**Task:** T-09 — "Deny every editor and shell write of plan.yaml, and sweep what lands on disk"

**Quoted phrase:** "deny with exit 2 and a message naming the four verbs and the tool path. The
message must name set-task-station explicitly, because recording a task status is the write an
agent will actually attempt." (also mirrored in SC-05: "a message naming the verb to use instead" —
same gap)

**Concrete cost:** Per BRIEF.md's own problem statement, plan.yaml "has no code writer at all" today
and "an LLM types the value by hand" — direct Edit of plan.yaml is the established, previously-legal
practice this feature revokes. A denial that lists the four legal verbs and the tool path, with no
stated reason the previously-normal route is now closed, is indistinguishable from a stuck or
over-broad gate to an agent that has not loaded T-05's updated playbook into its current context.
BRIEF.md's own disclosure names the one gap this feature cannot close: "a shell command that writes a
*legal* station value into plan.yaml is still not attributable to its author." A reader who takes the
WHY-less denial for a malfunction is routed toward exactly that shell-write channel — the one path
the feature admits it cannot fully police. This is the operator's fourth question ("would any refusal
read as a HARNESS MALFUNCTION... that invites the reader to route around it") landing on a real gap,
not a hypothetical one.

**Proposed replacement sentence** (for T-09's message-content spec): "deny with exit 2 and a message
stating that plan.yaml has exactly one writer — plan-write.py, because every station value must be
validated before it lands — naming the four verbs and the tool path, and naming set-task-station
explicitly as the route for recording a task status."

The same one-clause WHY addition should be folded into SC-05's acceptance text, since SC-05 currently
only requires "a message naming the verb to use instead" and would pass an implementation that omits
the reason entirely.

## Finding B — T-08's sign-approval refusal doesn't literally name the verb it refused (info, not gating)

**Task:** T-08 — "Gate sign-approval on identity, so only the main session can sign"

**Quoted phrase:** "prints ONE refusal text, used verbatim for every denial: that the approval
signature is the user's, relayed by the main session alone, that the agent should return
awaiting_user rather than sign, and that the main session runs the verb itself."

This message is otherwise the stronger of the two: WHAT (the approval signature) and WHY (it's the
user's, relayed by the main session alone) are fused into one clause, and WHAT-TO-DO-INSTEAD is
explicit (return awaiting_user; main session runs it). Accuracy checks out against the described
mechanism (`agent_type` absent = main session, matching check-domain.sh:512 per the plan's own
citation). No malfunction-reading risk — it explains itself as a deliberate identity gate.

**Concrete cost (why this is info, not a finding that gates):** the text never literally says
"sign-approval" or "plan-write.py" — it only says "the verb." Cost is small since the trigger is
always the literal `sign-approval` command the caller just typed, so the caller already knows what
was refused. Flagging only for consistency with T-09's explicit-naming requirement, and because a log
line seen without its triggering command benefits from naming the verb itself.

**Proposed replacement sentence:** "prints ONE refusal text, used verbatim for every denial, naming
sign-approval as the refused verb: that the approval signature is the user's, relayed by the main
session alone, that the agent should return awaiting_user rather than call sign-approval, and that
the main session runs sign-approval itself."

## Item 3 — plan-write exit codes 3 and 4 — no finding

T-03's intent states, verbatim: "Exit codes are the interface, so extend the docstring's table: 3
unknown task id, 4 illegal station, and the existing 5, 6, 7, 8, 9 unchanged." Both new codes carry a
stated meaning and an actionable message from the plan text alone:

- exit 3 (set-task-station, absent task id): message "naming the ids the plan does carry" — WHAT
  (bad id) and WHAT-TO-DO (here are the valid ones) both present.
- exit 4 (set-task-station / set-feature-station, illegal station): message "naming the offending
  value and listing the legal ones" — same shape.

Both messages are self-descriptive without requiring the reader to know what "3" or "4" means, so
they clear the operator's bar even before consulting the docstring table.

**Non-collision with 5–9:** 3 and 4 are numerically disjoint from 5,6,7,8,9 by construction — the
plan frames them as new additions to a table whose prior entries start at 5, so no reused digit is
possible. I did not open `plan-merge.py` to confirm 5/6's semantics — the SURFACE for this review was
scoped to `plan.yaml` and `BRIEF.md` only, and the plan's own claim ("extend the docstring's table")
is internally consistent across every place exit codes 5, 7, 8, 9 are mentioned elsewhere in the plan
(apply's 7/8, require_destination's 9). Confirming 5 and 6 against the source is outside this pass's
surface.

**One structural note, not a finding:** T-09 also denies Edit/Write with exit 2, and T-08 denies
sign-approval with exit 2 — both in a *different* process (check-domain.sh / plan-sign-gate.py) from
plan-write.py's own exit space, so there is no cross-tool collision to check; exit codes are
per-binary.
