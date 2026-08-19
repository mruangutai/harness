# Expertise — harness-qa

## Patterns (max 15)

## Gotchas (max 15)
- G-01: WHEN gating a change to `team-config.yaml`'s per-agent repository-tier grants DO know
  the only regression protection is a one-shot task `verify:` block — `run-unit-tests.sh` never
  re-runs `check-domain.sh --resolve` across all agents, so a dropped grant will not redden CI.
- G-02: WHEN citing `check-expertise.sh`'s live-corpus `verify:` (greps `.harness/expertise/`
  for `ADVISORY`) DO note it is coupled to the craft tier still holding token-carrying entries —
  nothing pins that corpus state, so a full migration to the repository tier would silently drop
  this check's only positive signal.
- G-03: WHEN running `test-check-expertise.py` DO know it registers under
  `run-unit-tests.sh`'s `--kind integration` only, not `unit` — even when the task touching it is
  flagged `cross_module` (which obligates both kinds), the unit half is not separately exercised
  by any standing script.

## Outcomes (max 10)

## Open (max 5)
