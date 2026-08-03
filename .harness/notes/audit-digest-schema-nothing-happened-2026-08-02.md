# Audit — DIGEST schemas cannot encode "nothing happened" — 2026-08-02

Run by the main session at `37a8a66` + working tree. Method: for each persona, construct the return
it would legitimately make in a did-nothing state (blocked, scoped-out, self-executed) and put the
**honest** encoding through the real `validate-digest.py`. A field is defective when the honest value
is rejected *and* a false one is accepted.

## Result: 6 of 7 personas cannot report "nothing happened" truthfully

| persona | scenario | field | honest value | accepted instead |
|---|---|---|---|---|
| `dev` | refuses an under-specified task per `tdd-enforcement` | `suite` | `none` → **rejected** | `pass` — asserts the suite passed when nothing ran |
| `qa` | cannot run the suite at all | `suite`, `matrix_ok` | `none` → **rejected** | `pass` + `matrix_ok: true` — asserts the project's only blocking gate passed |
| `reviewer` | `ui-reviewer` self-scopes OUT of a non-UI diff | `severity_max` | `none` → **rejected** | `info` — indistinguishable from "I reviewed it and found info-level issues" |
| `visual-designer` | decides the feature needs no DESIGN.md | `contract` | `none` → **rejected** | `written` — asserts a design contract exists |
| `pm` | blocked before it could size anything | `surface`, `risk` | `none` → **rejected** | `S` + `low` — asserts a small, low-risk feature |
| `lead` | self-executed a step, spawned no members | `members` vs `steps_run` | `members: []` with `steps_run: 1` → **rejected** | *(no accepted encoding at all)* |
| `dev-ops` | no suite applicable | `suite` | `n/a` → **ACCEPTED** | — (control) |

Reproduce: `python3 <this repo>/.harness/notes/audit-digest-schema.py` — script kept at
`$CLAUDE_JOB_DIR/tmp/audit.py` during the session; re-create from the table above if needed.

## Why this is one defect, not six

`dev-ops` is the control and it is the proof: its schema is
`"suite": {"pass","fail","n/a"}` (`validate-digest.py:49`) — the identical field, for a different
persona, already carries the third value. Every other occurrence of the same field
(`"dev"` :43, `"qa"` :44) is `{"pass","fail"}`. The vocabulary was extended once, where someone hit
the problem, and never propagated. `NULLABLE` (:35) exists for exactly this purpose but holds only
three scalars — `branch`, `blocked_on`, `briefing`.

**The failure mode is fail-open, and it is the harness's own signature defect.** In five of the six,
the accepted value does not merely lose information — it collapses "this did not happen" into
"this happened, with a benign result." `matrix_ok: true` is the sharpest: QA's inability to run the
suite is recorded as the test-matrix gate having passed. The orchestrator routes on these fields, so
a did-nothing step is indistinguishable from a clean one.

**It is already on the backlog once, unrecognised as a class.** `FEAT-03-subissue-mirror`
`feature.yaml:97` records B-13: *"`validate-digest.py:493-497` rejects `members: []` with a non-zero
`steps_run`, so a lead's self-executed step has no truthful encoding."* Raised independently by
product-lead and validator-lead. That is row 6 of this table.

## The trigger that surfaced it

`harness-tdd-enforcement/SKILL.md:65` instructs the four dev specialists + dev-ops to refuse an
under-specified task with an abbreviated return. That return is missing five required fields and
`artifact:`, so the `SubagentStop` hook rejects it with **exit 2** (verified in hook mode), blocking
the agent from stopping. The forced retry sets `stop_hook_active`, so the second message exits 0 —
**unvalidated, whatever it says**.

So the guard against under-specified tasks is told it committed a contract violation at the exact
moment it fires, and the correction it would need to make is a false one. Completing that example
without fixing `suite` would enshrine the lie in a normative template.

## Recommended shape of the fix (not decided — for pm)

1. Give every enum a "did not happen" member, or add its field to `NULLABLE`. `dev-ops`'s `n/a` is
   the in-tree precedent; one vocabulary across all personas is better than per-field invention.
2. `matrix_ok` is a `bool` and therefore cannot express it at all without a type change — this is the
   one that needs a real decision, not a vocabulary addition.
3. Resolve B-13's `members`/`steps_run` cross-field rule in the same pass; it is the same defect
   wearing a different shape.
4. Only then complete `tdd-enforcement`'s refusal example, so it is both valid and true.
5. Consider whether the `stop_hook_active` pass-through should stay a silent 0 — today a blocked
   agent's second attempt ships with no validation at all, which is how a wrong correction escapes.

## Blast radius

All 16 agents return a DIGEST. The five engineering specialists preload `tdd-enforcement`
(`frontend-dev`, `backend-dev`, `ai-dev`, `data-engineer`, `dev-ops`). The orchestrator routes on
`status`, `must_fix`, `matrix_ok` and `severity_max` — four of the affected fields.
