# Research — the eval amendment — 2026-08-27 (all facts measured at 899e4a6)

**Bottom line.** The amendment adds two tasks and two decisions. T-07 authors the eval DEC-70 owes
for T-02; T-08 gives `test_kinds.eval` a runner so the qa gate has something to execute. Both are
UNSIGNED — `approval:` in `plan.yaml` still reads the pre-amendment signature and only the main
session may touch it (DEC-120). One finding overturns the dispatch's own premise: **`harness-ai-dev`
cannot write an eval in this checkout**, so T-07 is `main-session-direct`.

## The finding that changed the plan

`check-domain.sh --resolve evals/lead-never-wait/run-eval.py` → `NOBODY`. The PreToolUse guard,
given a `harness-ai-dev` Write to `evals/lead-never-wait/cases.yaml`, exits 2:
`harness-ai-dev may not write evals/lead_never_wait/cases.yaml`, and prints its permitted set —
notes, expertise, observations, nothing else. `.harness/team-config.yaml:182` does grant
`evals/**` to ai-dev, but the resolver's two-sided base rule filters product-source globs out in
this self-hosted checkout (`src/**/prompts/**` resolves `NOBODY` the same way).
`check-plan-routes.py` independently reports T-07's three files ungranted and passes the plan at
0 violations.

So DEC-179 forces a declared main-session step, exactly as it did for T-02. **DEC-70's author/gate
split survives**: the hand that wrote the playbook text under test IS the main session (T-02 is
main-session-direct), qa still runs and gates the eval, validator-lead still assesses adequacy in
the panel. What is lost is DEC-70's *named* author. That is the operator's to accept — D-14 records
it rather than hiding it.

## The runner problem — recommended: fix it inside the feature (T-08)

- **Chosen.** `harness-dev-ops` writes `test_kinds.eval.cmd`, sets `status: active`, deletes the
  `_reason`. `check-domain.sh --resolve .harness/harness.json` → `harness-dev-ops`, and the guard
  admits that agent (exit 0). Cost: **one dev-ops dispatch**, sequential after T-07 because T-08's
  verify executes the cmd it just wrote.
- **Rejected: defer to work outside the feature.** Saves no run — the eval still has to be authored
  — and the terminal state is a feature that ships an authored eval nothing executes, with the qa
  gate BLOCKED on `ai_behavior` indefinitely (DEC-36). That is the hole the amendment exists to
  close.

**Budget.** Six runs remain after this pass. T-07 is a main-session step, not a team dispatch;
T-08, the qa re-run, the panel, the goal-check and the docs sweep are five. One run of slack.

## DEC-174 — reported, not decided

`.harness/harness.json` is **outside** the carve-out on the evidence, and the operator rules:

- Amendment 4 (`DECISIONS.md:4983`) declares the category — hooks, validators, gate **scripts** —
  governing, and the list recording: `check-domain.sh`, `bash-write-guard.sh`,
  `validate-digest.py`, `check-state.sh`, `check-plan-routes.py`, `dispatch-guard.sh` and each
  one's test. `harness.json` is data, not a script.
- No enforcement-layer script reads `test_kinds.eval.cmd`. `run-unit-tests.sh:108` reads
  `test_kinds.integration.detect` only; `check-state.sh`'s sole mention of `test_kinds` is the
  comment at line 479. The consumer of `eval.cmd` is the qa **persona's** matrix.
- The residual worry is am.4's cutover rule — "the cutover that makes a gate use it is
  main-session-direct". It does not bite here: no gate script changes at all, and no script's
  behaviour switches on the edit.

If the operator rules the other way, T-08 becomes a second `main-session-direct` step; nothing else
in the amendment moves.

## Open, and deliberately not decided here

- The `approval:` block still reads `approved / 2026-08-27`, covering five tasks. The task set has
  changed, which under `harness-spec-driven` resets approval — but only the main session writes
  that block. Flagged, untouched.
- Proposed and NOT adopted: **SC-10** — "the eval flags every labelled violating lead-turn case and
  none of the compliant ones; `verify: automated`, `evidence: eval`." It would make the eval's
  discrimination a graded outcome instead of only a task verify. It rests on `eval`, which is a
  null kind until T-08 lands, so it is only well-formed if T-08 is approved with it.
