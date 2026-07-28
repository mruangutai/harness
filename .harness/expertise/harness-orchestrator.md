# Expertise — harness-orchestrator

## Patterns
- P-01: `cost-report.py` is project-cumulative with no per-run filter; it also exits 1 when the
  transcript contains models it refuses to price (e.g. claude-opus-4-8, <synthetic>) even though
  the YAML block is emitted. Append with `cmd; echo $?` not `cmd && ...`, and treat run-level
  cost_usd as an approximate attribution, noted as such in feature.yaml.

## Gotchas
- G-01: check-domain.sh blocks the orchestrator from writing other agents' expertise files
  (`.harness/expertise/<agent>.md` other than its own), contradicting harness-expertise's "the
  orchestrator applies them for you" for leads. Lead expertise ops must ride up to the main
  session in `expertise_update` instead.
- G-02: Dispatch prompts must not name `.harness/notes/**` as an output path for eng-lead — its
  domain excludes it; reviewer artifacts go under `.harness/features/*/runs/*-eng/**`.

## Outcomes
- O-01: plan-feature segment 3 (ui-reviewer contract check) is skippable when the design pass
  rules "no end-user interaction" and no DESIGN.md exists — there is no contract to review and
  ui-reviewer would self-scope out at the cost of a spawn. Record the skip and rationale in
  STATE.md and feature.yaml.
- O-02: An interrupted lead dispatch whose subtree ran on leaves member artifacts on disk while
  the run's state.yaml still shows every step pending (checkpoints were the host's to write).
  Recovery that worked (FEAT-02): orchestrator verifies the artifacts' key claims directly, then
  re-dispatches the SAME lead with explicit assess-not-redo instructions — mark the recovered
  step complete-with-note, run only the remaining steps. Do not redo the work and do not mark
  steps complete yourself; the run dir is the lead's.

## Open

