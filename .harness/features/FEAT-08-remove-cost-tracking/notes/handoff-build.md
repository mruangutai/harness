# Handoff — FEAT-08-remove-cost-tracking, build → validate — written at c14ed96, seq-2

## Next

STOP. **Two user gates before any validation work**, and neither is yours to write.

1. **Re-signature.** `BRIEF.md` and `PLAN.md` carry three unsigned amendments — A-1 (T-04's lane
   split), A-3 (two SPEC sites T-10's table never enumerated), A-4 (SC-01 and SC-04, superseding
   A-2). Approved text is left verbatim with a pointer; both `## Approval` blocks are untouched.
2. **A five-edit main-session batch** across two DEC-174 carve-out files, specified by A-4 and
   detailed in `feature.yaml` `blocking_the_phase.main_session_batch`. **Never dispatch these to a
   team** — the gates cannot vouch for themselves.

Then, in order: **T-10's remainder** (rows 10-11, one documentor dispatch, all five verify clauses
re-run — issue #95 is deliberately still open), then the **four-wide review panel**, then pm's
goal-check, then ship-refresh and distillation, then the briefing.

## Trust

- Eleven of twelve tasks are committed and I re-ran **every** `verify:` clause at my own tier rather
  than relaying it — `feature.yaml` `batch_result`, commits `ba9a243`..`5ce3b13` — verified-at c14ed96
- SC-04's discriminating pair: the omitting payload was rejected `missing 'cost_usd'` exit 1 by the
  pre-change validator and is accepted by the current one; the carrying payload was accepted by both
  — I ran both binaries against both payloads — verified-at 3503d1d
- SC-01 is **reachable, not passing**: the sweep returns 6 with `--exclude-dir=worktrees` and 78
  without; 4 are the amended expected set and 2 are exactly what the batch edits — verified-at c14ed96
- Every remaining SPEC and BUILD hit carries the `DEC-178` marker, so SC-14 holds and those two files
  survive for the reason SC-14 itself states — verified-at c14ed96
- Gates green: `run-unit-tests.sh` 0 (**twelve** scripts now), `check-docs.sh` 0, `check-state.sh` 0
  with zero violations — all three re-run by me — verified-at c14ed96
- **$370.53 is the last measurable figure**, taken at `3503d1d` immediately before T-03 deleted
  `cost-report.py`. Everything after is unmeasurable BY DESIGN — verified-at 3503d1d
- The four-wide panel is a **USER RULING**, not a preference — `feature.yaml` `validate_panel`.
  Your own Expertise O-01 says to skip the ui-reviewer; **the ruling outranks it** — verified-at c14ed96

## Dead ends

- Do NOT re-root `check-state.sh` via `CLAUDE_PROJECT_DIR` to make SC-03 pass — that is the
  re-baselining the user forbade — source: user ruling
- Do NOT delete the `(cost-report.py removed — DEC-178)` markers in SPEC/BUILD to "finish the job".
  T-10/T-11 mandate them and SC-14 blesses them; SC-01 was the criterion that was wrong — `BRIEF.md` A-4
- Do NOT widen `team-config.yaml` to grant `templates/**`. The user ruled T-04 splits by lane
  instead; no domain was widened — `PLAN.md` D-10
- Do NOT re-litigate the template's em-dash escape normalization. `templates/harness.json` was
  rewritten through a JSON round-trip, so ~20 unrelated lines re-escaped. Already adjudicated:
  measured semantically identical by parsing both revisions and comparing objects, and
  `_max_total_cycles_rationale` is string-identical, so SC-05 holds — `feature.yaml` `lane_defect`
- Do NOT re-open cycle counting, `max_total_cycles`, or any historical DECISIONS entry — out of
  scope by standing ruling — `feature.yaml` `pending`
- Do NOT trust an all-green `verify:` as proof of absence. T-10 passed all four clauses and still
  left two live cost sites, because every clause matches compound tokens and both sites use the
  plain word — `PLAN.md` A-3

## Working set

- `.harness/features/FEAT-08-remove-cost-tracking/feature.yaml` — `blocking_the_phase` is your to-do list
- `.harness/features/FEAT-08-remove-cost-tracking/BRIEF.md` — `## Amendments`, A-2 superseded by A-4
- `.harness/features/FEAT-08-remove-cost-tracking/PLAN.md` — `## Amendments` A-1, A-3, A-4
- `.harness/features/FEAT-08-remove-cost-tracking/runs/s4-product/digest.md` — the T-10 remainder
- `.claude/skills/harness/teams/review.yaml` — the four-wide panel, all four steps
