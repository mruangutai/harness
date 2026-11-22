# Sign-off by delegated authority — FEAT-2337 — 2026-11-22

## Delegation

Mike Ruangutai (operator), 2026-11-22, after the plan run was dispatched: **"take this to clean
merge, defer to fable-advisor for questions and approvals."** Every question and approval for this
feature, from signature through merge, goes to the `fable-advisor` agent instead of the operator.
Each ruling is recorded in this feature's `notes/answers-*.md`.

## Presented

To `fable-advisor` (`AdvisorB1Signoff`) at plan HEAD `00c12fa4`:
- BRIEF.md and plan.yaml (pending): 3 tasks, all main-session-direct (DEC-174); 10 SCs; panel c1
  applied, severity_max med.
- The operator's grilling intent:
  `/Users/molchairuangutai/GitHub/harness/.harness/notes/grilling-omp-native-gate-runtime-b-2026-11-22.md`.
- The proposed rework (`feature-record.py propose-rework`): 2 rounds / 90 min (3 tasks, 3 per
  round, floor 2; 45 min per round).
- pm's stated choice: this feature's own validate run is graded by the existing #919 re-run path,
  with candidate receipts produced and force-added as evidence.
- HQ-01: `plan-merge.py apply` returned APPLIED/0 while its own check reported an unloadable
  verify scalar.

## Ruling (fable-advisor, on the operator's behalf)

1. **Approve as drafted.** It honours every settled grilling item, the file lists match the task
   intents, the panel findings are applied, and the cited seams exist.
2. **Rework: 2 rounds / 90 minutes.** Re-capturing SC-04 benchmark evidence under the idle-host
   protocol, when the first capture failed only because the host was loaded, is not a rework round.
3. **Confirmed:** the installed control-plane hook grades this feature's own validate run. Using
   the candidate verifier would make unreviewed code its own judge.
4. **HQ-01:** file it as a separate backlog bug, outside FEAT-2337's scope.

Condition the advisor set: at close, "candidate manifests force-added with the committed validate
record" is a hard gate for main, not a reminder.

Signed by the main session as `Mike Ruangutai (delegated to fable-advisor)`.
