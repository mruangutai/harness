# Expertise — harness-validator-lead
## Patterns (max 15)
- P-01: WHEN closing a review panel in this repository DO read `gates.review` in `.harness/harness.json` before calling the result blocking — it is `advisory_unless_high`, so an empty `must_fix` at `severity_max: med` does not gate the ship, and a digest implying otherwise misroutes the tier above.
- P-02: P-02: WHEN this repository's plan carries a change_type absent from harness.json's test_matrix vocabulary DO treat the plan as malformed and correct the record; never add a synonymous mapping to legitimize it.
## Gotchas (max 15)
- G-01: WHEN a feature's SHA or status is re-pinned here DO check `STATE.md` against `feature.json` — `feature.json` is the machine record and `STATE.md` the live human pointer a resuming context reads, and a re-pin applied to one and not the other sends the next run at a stale SHA.
- G-02: WHEN a gate relies on this repository's run digests DO establish that required artifacts are tracked at the reviewed pin before crediting them as durable evidence — `runs/**` is gitignored by default, so local presence neither proves repository-state completeness nor survival after worktree removal.
- G-03: WHEN a panel finding's only remedy edits the harness skill bin/ tree DO route it as an operator decision, not a fix cycle — that tree is main-session-direct, no lead holds write authority over it, and a routed FAIL spends a cycle proving it.
- G-04: WHEN an acceptance clause counts `^FAIL ` lines over this repo's suite output DO read the runner's exit status and per-file verdicts instead — a unit test reprints captured FAIL lines as its own success proof, so a green suite reads as red.
## Outcomes (max 10)
## Open (max 5)
