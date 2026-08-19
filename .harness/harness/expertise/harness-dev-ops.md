# Expertise — harness-dev-ops

## Patterns (max 15)
- P-01: WHEN editing `inject-expertise.sh`'s emit order DO keep tier precedence stated as an explicit line in the output, never implied by emission order alone — craft, project, then sorted repository blocks are emitted in a fixed sequence, but that sequence is presentation only.

## Gotchas (max 15)
- G-01: Nothing invokes check-state.sh automatically — it is manual-only, so a green session is not evidence it ran. (This gotcha used to also cover check-docs.sh's exec-bit fail-open; that script and INV-10 were struck under DEC-188.)
- G-02: `.claude/skills/harness/templates/harness.json` is merged additively into `.harness/harness.json` by `.claude/skills/harness/bin/upgrade-config.py`, and copied verbatim on init — editing one without the other creates silent drift on the next upgrade or init.
- G-03: WHEN adding a new `.claude/skills/harness/bin/test-*.py` script DO append its filename to `UNIT_SCRIPTS` or `INTEGRATION_SCRIPTS` in `run-unit-tests.sh` in the same change — the drift detector walks the union of both arrays, so an unregistered new script is invisible to it, not caught by it.
- G-04: WHEN `.harness/team-config.yaml` gains or loses a manifest grant line for any agent DO update that agent's entry in `COLLECT_FIXTURE` inside `test-harness-yaml.py` by hand — it is a hand-maintained snapshot, not derived from `manifest_domains()`, and reddens on every legitimate manifest change.

## Outcomes (max 10)

## Open (max 5)
