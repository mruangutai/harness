# Expertise — harness-dev-ops
## Patterns (max 15)
- P-01: WHEN editing `inject-expertise.sh`'s emit order DO keep tier precedence stated as an explicit line in the output, never implied by emission order alone — craft, project, then sorted repository blocks are emitted in a fixed sequence, but that sequence is presentation only.
## Gotchas (max 15)
- G-01: Nothing invokes check-state.sh automatically — it is manual-only, so a green session is not evidence it ran. (This gotcha used to also cover check-docs.sh's exec-bit fail-open; that script and INV-10 were struck under DEC-188.)
- G-02: `.claude/skills/harness/templates/harness.json` is merged additively into `.harness/harness.json` by `.claude/skills/harness/bin/upgrade-config.py`, and copied verbatim on init — editing one without the other creates silent drift on the next upgrade or init.
- G-04: WHEN `.harness/team-config.yaml` gains or loses a manifest grant line for any agent DO update that agent's entry in `COLLECT_FIXTURE` inside `test-harness-yaml.py` by hand — it is a hand-maintained snapshot, not derived from `manifest_domains()`, and reddens on every legitimate manifest change.
- G-05: WHEN `CLAUDE_PROJECT_DIR` points at a tempdir lacking `SPEC.md` DO expect `factory_config.harness_root()` to silently fall back to the real checkout instead of erroring — assert the resolved root before any write in ad-hoc benchmarking here, not just by setting the env var.
- G-06: WHEN writing a new rationale string into harness.json's `budgets` block DO grep for the literal backslash-u-2014 sequence sibling strings use, rather than a raw UTF-8 dash — an Edit call can write the raw form and JSON stays valid, but a grep/byte-diff for the escape then misses it.
## Outcomes (max 10)
## Open (max 5)
