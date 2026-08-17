# Handoff — FEAT-22, build (T-01..T-09) → build (T-10..T-11) + validation — written at e6e74c8, seq-9

## Next

**Dispatch nothing. Execute T-10 yourself** — every task is main-session-direct under D-03, so you
sequence and verify while the main session edits. Read `plan.yaml` T-10 for the card; it is fully
specified there and is deliberately not restated in this note. T-10 is the **depth sweep**
(literal-free resolver, FEAT-21's inherited method); T-11 commits the feature record. Before either,
re-read `notes/rotation-carry-2026-08-16.md` for the validation sequence and the accumulated
ship-review rows — that file holds everything not already in `plan.yaml`.

## Trust

- The coupled cluster is committed whole and atomically — `git show --name-status e6e74c8` shows 29
  files, five docs as renames (R098/R099/R100), zero delete-plus-add — verified-at e6e74c8
- T-09's verify passed in full: index regenerates byte-identical, both surfaces `CLEAN — evidence
  migrated`, both suites exit 0, commit audit `k=29` at the floor — verified-at e6e74c8
- T-01..T-08 each had its verify re-run by me rather than relayed — verbatim, except T-05 (explicit
  paths substituted for its two `mktemp` vars, which the write-guard misparses) and T-07 (second
  half run with the intended invocation, since the signed one cannot pass on any tree); both
  deviations are recorded in the carry note — verified-at e6e74c8
- T-06 additionally proved MF-A closed by execution, not by edit: `audit-decisions.py` exits 0,
  clearing the `FileNotFoundError` it had carried since T-02 — verified-at e6e74c8
- `check-state.sh` note body is **42 lines, matching T-01's PRE-MOVE capture exactly** — the gate is
  examining, not sleeping (FEAT-21 passed both gates mid-cluster while examining nothing) —
  verified-at e6e74c8
- Cycles **9 of 10**; one fix cycle remains and exhausting it is `BLOCKED`, not a quiet stop —
  `feature.json` — verified-at e6e74c8
- `review_sha` is re-pinned to e6e74c8, the commit containing the work, ready for the validator
  segment — `feature.json` — verified-at e6e74c8

## Dead ends

- Do not re-litigate the seven accepted residuals — each was operator- or eng-lead-ruled; the list
  with its rulings is in `notes/rotation-carry-2026-08-16.md` — source: operator rulings + r10 panel
- Do not edit `plan.yaml`'s signed text to fix `:927`'s unexecutable `check-expertise.sh` clause —
  ruled an execution-time acceptance with the deviation recorded, not a plan change; correcting it is
  the operator's call and does not gate shipping — source: this orchestrator's ruling, T-07
- Do not use `git add -A` or `git add .`, and do not assume the tree is clean before staging — a
  separate commit already swept this build's staged renames once — verified-at 1246b06
- Do not write `>"$var"` redirects or heredocs containing `->` from an agent seat; the write-guard
  misparses both. Use explicit absolute paths — verified-at e6e74c8

## Working set

- `.harness/harness/features/FEAT-22-docs-layout-migration/plan.yaml` — T-10, T-11, and the 7 decisions
- `.harness/harness/features/FEAT-22-docs-layout-migration/notes/rotation-carry-2026-08-16.md` — briefing rows, residuals, validation sequence, budget
- `.harness/harness/features/FEAT-22-docs-layout-migration/BRIEF.md` — the 12 SCs the goal-check must verify
- `.harness/harness/features/FEAT-22-docs-layout-migration/notes/layout-boundary-2026-08-15.md` — T-01's PRE-MOVE capture; T-11 pairs the POST-MOVE half against it
- `.harness/harness/features/FEAT-22-docs-layout-migration/feature.json` — budget, runs, review_sha, mirror ids
