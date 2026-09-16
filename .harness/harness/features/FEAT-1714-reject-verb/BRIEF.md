# BRIEF — FEAT-1714 Reject a superseded ticket before planning

## Problem

When an orchestrator discovers from a source ticket that the work has been superseded or should not be planned, the harness has no terminal first-run outcome for that judgement. It must currently continue into product planning or return an unrecognised prose explanation, spending work on the wrong ticket and leaving issue #1714's provenance, terminal state, and GitHub disposition ambiguous.

## Done when — by perspective

**orchestrator** — I can reject a superseded or invalid source ticket at the start of the first `plan` or `patch` run, before dispatching any lead, and return one recognised terminal result that names a superseding issue or explicitly says there is none.

**operator** — I can audit why the ticket was rejected, overrule that judgement from the return, and rely on the local record and GitHub parent to preserve provenance while showing that no planning or rework cycle occurred.

**code maintainer** — I can add or change terminal feature states through one shared vocabulary, and the writers, gates, board projection, handoff checks, and worktree cleanup agree on what `rejected` means without respelling it.

## Success criteria

- SC-01 (orchestrator): A valid orchestrator return with `status: rejected` is accepted only when it carries a `kind: reject` judgement with a non-empty one-line reason and `superseded_by` set to a positive issue number or the literal `none`; missing or malformed reject fields are refused.
  verify: automated        evidence: integration
- SC-02 (orchestrator): Rejecting at first-run intake leaves the feature at terminal station `rejected`, preserves its original `source_issues` and any drafted BRIEF, leaves both plan and BRIEF unsigned, records exactly one orchestrator-owned run plus the reject judgement at `cycles_used: 0`, records no panel or lead run, and is classified for terminal worktree cleanup.
  verify: automated        evidence: integration
- SC-03 (operator): For a numeric superseding issue, `gh-sync.py reject` reports the intended mutations and writes nothing without `--yes`; with confirmation it closes only the parent as `not_planned`, comments with the superseding-issue link and supplied reason, adds the `superseded` label, reseats the parent card to backlog in close-then-reseat order, closes an existing milestone, touches no sub-issues, and records station `rejected` last.
  verify: automated        evidence: integration
- SC-04 (operator): State validation refuses every `rejected` feature that records non-zero cycles, any lead-owned run, more or fewer than the one orchestrator run, an approved signature, or a panel, while accepting the corresponding zero-cycle first-run record.
  verify: automated        evidence: integration
- SC-05 (code maintainer): `abandoned` and `rejected` are declared once as the non-board terminal station set, and every station writer, route/domain/state gate, board/lifecycle projection, handoff authority check, and landed-worktree classifier consumes that shared set.
  verify: inspection

## Verification gaps

- none

## Constraints

- Source issue provenance is GitHub issue #1714 and must remain in `plan.yaml.source_issues`; rejection never rewrites provenance to the superseding issue.
- DEC-230 SUPPLIES the append-only judgement ledger and operator-overrule boundary; `reject` extends that closed vocabulary without changing who decides whether a ticket is wrong.
- DEC-174 BLOCKS team execution for `validate-digest.py`, `check-state.py`, `feature-record.py`, and `plan-merge.py`; these enforcement surfaces and their coupled gate tests are main-session-direct.
- DEC-203 SUPPLIES the close-then-reseat GitHub lifecycle order and the rule that a non-board terminal station never becomes a board column.
- DEC-229 SUPPLIES the only legal plan mutation route: `plan-merge.py set-feature-station --station rejected`.
- A reject is decided before any lead dispatch, consumes zero rework cycles, carries no approval signature or plan panel, and does not erase a BRIEF already drafted at intake.

## Out of scope

- Rejecting work after build or another signed execution phase has started; issue #1716's amendment path or a DEC-32 operator decision owns that case.
- Automatically planning or opening the superseding issue; the reject return names it and the operator decides what happens next.
- Retrospectively changing BUG-285-yaml-loader-pin to `rejected`; its committed historical record remains unchanged.
