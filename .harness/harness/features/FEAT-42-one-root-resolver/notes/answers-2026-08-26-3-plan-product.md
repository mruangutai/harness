# Operator rulings — FEAT-42 — 2026-08-26

Relayed by the main session. These are RULINGS, not proposals. Treat them as REQs.

## Q1 — CLEARED

Both stranded claims released, targeted (`release --agent harness-pm`, then
`--agent harness-product-lead`), never `release-all`, and only after proving each holder dead.
**Verified independently by the orchestrator: `/Users/molchairuangutai/GitHub/harness/.harness/.inflight-claims.json` now reads `{}`.**

FEAT-37's registry holds one claim at 524 minutes — already past the 3600s TTL, sweeps on next read.
Different feature's tree. **Not ours to touch.**

**If a dispatch is refused again, STOP and report it.** Do not retry. A second refusal means the
release did not hold, and that is a new fact.

## Q2 — RULED: cover ALL TWENTY. Widen REQ-01 and SC-01.

Counted by the operator at `3952814`, and **re-verified independently by the orchestrator**:
**20 non-test occurrences of the env fallback chain across 16 files.** (The orchestrator's earlier
"15 files" was an undercount; 16 is correct.)

Per file — 2 each: `bash-write-guard.sh`, `check-domain.sh`, `dispatch-guard.sh`,
`validate-digest.py`. 1 each: `branch-create-gate.sh`, `check-plan-routes.py`, `check-state.sh`,
`factory_config.py`, `gen-decisions-index.py`, `gh-close-gate.sh`, `harness_yaml.py`,
`inflight_registry.py`, `inject-expertise.sh`, `run-unit-tests.sh`, `validate-feature-json.py`,
`wayfind.py`.

**The gate must prove ZERO remain, not that six were fixed.** Write SC-01 so it FAILS while any
non-test occurrence survives — a count that must reach 0, with test files explicitly excluded and
that exclusion stated in the criterion.

Deciding reason, a measurement not a preference: `inject-expertise.sh:31` falls back to `$(pwd)` and
is a `SubagentStart` hook. That is the failure shape that blocked this very run. Shipping the other
fourteen "later" means the same failure recurs after the feature is declared done.

## Q3 — YES, task it

`test-check-plan-routes.py:1167`'s `KNOWN_DIRECTORY_PROBE = {"wayfind.py"}` goes stale the moment
`wayfind` moves onto the marker file, and a stale allowlist hides regressions. Enforcement-layer test
file -> `main-session-direct`.

## Q4 — FOLD IN, do not file separately

`inflight_registry.py:224-232` popping the OLDEST same-persona claim rather than the returner's own
is the FOURTH registry defect, measured live: the stop hook released the abandoned lead's claim and
stranded the returning lead's. Same file as the other three. **Widen REQ-06/SC-07 to cover it.**

## Q5 — pm decides from the evidence

If SC-11 is settleable from disk, downgrade it from `verify: uat` and **say in the plan what on disk
settles it**. Do not carry an operator-only check that is not one.

## THE CASCADE BELONGS IN THE BRIEF

One stranding cascades UPWARD through three tiers — pm's spawn refused by `dispatch-guard.sh`, then
the lead's return refused by `validate-digest.py`'s children-in-flight check, then the orchestrator's
return refused the same way. Each stranding creates the next. **Neither #742 nor #866 records this.**

REQ-06 currently reads as "a nuisance with a bad TTL". It is a fault that can **lock an entire tier
chain out of reporting**, and the record survived only because the hook fires once.
**pm rewrites REQ-06 around that, citing this run as the measurement**
(`runs/2026-08-26-2-plan-product/digest.md` and this feature's STATE.md).

## Unchanged from the original dispatch

D-1..D-5 are rulings, not proposals. The DEC-174 lane split stands (library is squad work; each gate
cutover is `main-session-direct`, proven by an identical violation set before and after).
`HARNESS-FEATURE:` is tasked separately from the resolver. Every task carries a runnable `verify:`.
Mutation proofs must assert the mutation APPLIED before trusting a survivor.

Approval stays `pending` in BRIEF.md and plan.yaml. The operator signs, nobody else.
