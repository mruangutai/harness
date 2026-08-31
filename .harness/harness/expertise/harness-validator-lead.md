# Expertise — harness-validator-lead

## Patterns (max 15)
- P-01: WHEN closing a review panel in this repository DO read `gates.review` in
  `.harness/harness.json` before calling the result blocking — it is `advisory_unless_high`, so an
  empty `must_fix` at `severity_max: med` does not gate the ship, and a digest implying otherwise
  misroutes the tier above.

## Gotchas (max 15)
- G-01: WHEN a feature's SHA or status is re-pinned here DO check `STATE.md` against
  `feature.json` — `feature.json` is the machine record and `STATE.md` the live human pointer a
  resuming context reads, and a re-pin applied to one and not the other sends the next run at a
  stale SHA.
- G-02: WHEN planning to skim a prior run's evidence in this repository DO expect `runs/**`
  digests to be absent — they are gitignored, so a removed feature worktree takes every run
  digest with it, and only the `notes/` artifacts and the observations logs survive.

## Outcomes (max 10)

## Open (max 5)
