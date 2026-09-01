# Expertise — harness-qa
## Patterns (max 15)
## Gotchas (max 15)
- G-01: WHEN gating a change to `team-config.yaml`'s per-agent repository-tier grants DO know the only regression protection is a one-shot task `verify:` block — `run-unit-tests.sh` never re-runs `check-domain.sh --resolve` across all agents, so a dropped grant will not redden CI.
- G-02: WHEN citing `check-expertise.sh`'s live-corpus `verify:` (greps `.harness/expertise/` for `ADVISORY`) DO note it is coupled to the craft tier still holding token-carrying entries — nothing pins that corpus state, so a full migration to the repository tier would silently drop this check's only positive signal.
- G-03: WHEN running `test-check-expertise.py` DO know it registers under `run-unit-tests.sh`'s `--kind integration` only, not `unit` — even when the task touching it is flagged `cross_module` (which obligates both kinds), the unit half is not separately exercised by any standing script.
- G-04: WHEN citing run-unit-tests.sh's printed PASS-line count as a test-case total DO discount it — line ~139 emits exactly one PASS per script regardless of internal case count, so a script using its own ok/FAIL convention contributes one line for dozens of real cases, deflating any cross-run comparison.
- G-05: WHEN a feature branch's later merge-from-main reintroduces run-unit-tests.sh's UNIT_SCRIPTS/INTEGRATION_SCRIPTS entries for files main already deleted DO expect the KIND-DRIFT union check to exit 2 for --kind unit, --kind integration, AND --check-kinds alike — it scans the combined array before any kind dispatch, so no single kind avoids it.
## Outcomes (max 10)
## Open (max 5)
