# Plan repair — BUG-1304 — consolidated pass before the panel — cycle 2

**BLUF:** one consolidated repair of `plan.yaml` and `BRIEF.md` closing the goal-check's four gating
gaps and applying Advisor ruling 3 items 1-7. The goal-check's proposed T-02 remedy — "name `_expire`
as the reuse" — was **NOT applied anywhere**; ruling 3 RULING D rejects it because it would bake the
1200s `CLAIM_TTL_SECONDS` dispatch horizon into the new binding enumerator.

Written through `plan-merge.py` verbs only, one field per call, compare-and-swap on sha256.

## Chunk progress
- C1 DONE — `amend tasks:T-02.intent`. Rejected `_expire`/`CLAIM_TTL_SECONDS` reuse deleted; binding
  liveness predicate written (OMP via `_omp_claim_live`, non-OMP until `OMP_UNVERIFIED_TTL_SECONDS`),
  with an explicit MUST NOT on `_expire` and `CLAIM_TTL_SECONDS`. Retention rule NOT here — it is OC-1.
- C2 DONE — `amend tasks:T-01.intent`. RULING D cases (1)(2)(3) added as registry cases 5/6/7, each
  with `now=` injection and a back-dated `started_at`; case (4) deliberately NOT here (it is OC-1).
  Existing case 2 re-worded to the binding horizon. Boundary case 2 now names itself as the
  discrimination T-03 c7 / T-05 c8 point at (goal-check gap 6).
- C3 DONE — `amend tasks:T-03.intent`, `.verify`, `.files`. In-test pre-change discrimination added
  (`bug1304_pre_change_hook` over a vendored `tests/fixtures/bug1304-check-domain-pre.sh.txt`,
  hermetic because CI checks out at depth 1 — `git show` is unreachable there). New case 13 =
  RULING D case (5). Case 7 now names T-01 boundary case 2 plus an exit-code-observable pair
  (goal-check gap 6). `verify` counts the pre-change helper's call sites.
- C4 DONE — `amend tasks:T-05.intent`, `.verify`, `.files`. Same stroke on the Bash route:
  `bug1304_pre_change_guard` over `tests/fixtures/bug1304-bash-write-guard-pre.sh.txt`; new case 15
  = RULING D case (5); case 8 given the exit-code-observable pair plus the T-01 citation.
- C5 DONE — `amend tasks:T-06.intent`. Added the IN-REPO DESTINATIONS ONLY clause: the `:840` branch
  fires on `allow` AND `not_a_domain_question`, so the claim-set check must not run for the latter
  (goal-check gap 5). Clarification only; no new scope.
- C6 DONE — `amend tasks:T-07.intent`, `.verify`. Obligation 1b added: the DECISIONS.md entry carries
  D-09's boundary and residue verbatim, plus the honest "T-09 struck" sentence. `verify` now greps
  `OMP_UNVERIFIED_TTL_SECONDS` and `inflight_registry.py:30-35` so the residue cannot be dropped.
- C7 DONE — `add-tasks` T-09 and T-10. T-09 = OC-1, STRIKEABLE AT SIGNATURE, carrying both halves
  (retention rule + RULING D assertion 4) so they strike together; nothing depends on it. T-10 =
  G-1a broad verification, `run-unit-tests.sh --kind all` plus `check-state.sh`, depends only on the
  always-landing T-02/T-04/T-06/T-07 so no edge dangles when T-08 or T-09 is struck.
- C8 DONE — `apply` D-09 (`dec: DEC-204`). Carries the two-liveness-questions boundary, the explicit
  "1200s is NOT accepted", the accepted past-backstop residue with its named reason
  (`inflight_registry.py:30-35`), OC-2's planned backstop value 86400s flagged ratified-at-signature,
  and the honest T-09-struck consequence. D-03 untouched.
- C9 DONE — `BRIEF.md`. SC-07 re-worded to name the decision carrying each of the five boundary
  questions (D-01, D-01, D-05+D-06, D-08, D-01+D-02), `git show <review_sha>:<path>` discipline kept;
  new SC-09 asserts RULING D case (5) on both routes with the in-test pre-change control. SC-01..08
  ids unchanged, so no task `traces:` broke.
- C10 DONE — `set-feature-station --station plan`. `approval.status` left `pending`; the `approval:`
  mapping was never written and `sign-approval` was never run.
- C11 DONE — integrity sweep. `yaml.safe_load` gives `10 {'status': 'pending'}`. All ten tasks carry
  `files`/`verify`/`intent`/`change_type`/`execution_mode`/`execution_reason`/`depends_on`/`status`/
  `traces`; ten `verify: |` literal blocks, zero folded `>`; no `TBD`/`TODO`; no dangling
  `depends_on`; DAG acyclic and every task reachable.
  `check-plan-routes.py <plan>` -> `0 violation(s) across 1 plan(s)` (the ten `DEVIATION` lines are
  the expected DEC-174 carve-out output, which does not gate).
  CORRECTION MADE DURING THE SWEEP: the pre-change fixtures were first specified at
  `tests/fixtures/<name>.sh.txt`, a directory and spelling that do not exist here. Re-pointed to the
  established convention `tests/integration/fixtures/prior-<name>.fixture`
  (siblings: `prior-validate-digest.py.fixture` and three others). `suite_layout` inspects only
  `test-*.py` shapes, so the two new fixtures add no layout finding.

## Where each closure item landed

| Item | Landed |
|---|---|
| Ruling 3 item 1 — T-02 binding predicate | `plan.yaml` T-02 `intent`, section "THE BINDING LIVENESS PREDICATE (D-09)". Explicit MUST NOT on `_expire` and `CLAIM_TTL_SECONDS`. |
| Ruling 3 item 2 — registry-FILE retention | NOT in T-02. Moved to the OC-1 task T-09 with RULING D assertion (4), per the dispatch. |
| Ruling 3 item 3 — T-01 RULING D cases | T-01 `intent`, registry cases 5/6/7 = RULING D (1)(2)(3); each injects `now=` and back-dates `started_at`. Existing case 2 re-worded to the binding horizon. Case (4) is in T-09. |
| Ruling 3 item 4 — case (5) on both routes | T-03 `intent` case 13 and T-05 `intent` case 15, each through the frozen pre-change copy. |
| Ruling 3 item 5 — new D-09 | `plan.yaml` `decisions:` D-09, `dec: DEC-204`. D-03 byte-unchanged. |
| Ruling 3 item 6 — T-07 carries D-09 verbatim | T-07 `intent` obligation 1b; T-07 `verify` greps `OMP_UNVERIFIED_TTL_SECONDS` and `inflight_registry.py:30-35`. |
| Ruling 3 item 7 — BRIEF criterion for case (5) | `BRIEF.md` SC-09. |
| G-1a — nothing verifies wider than the suite it edits | New task T-10: `run-unit-tests.sh --kind all` then `check-state.sh`, both exit 0. Not bolted onto any existing `verify:`. |
| G-3 — SC-06 had no producing task | T-03 `bug1304_pre_change_hook` and T-05 `bug1304_pre_change_guard`, each over a vendored pre-change fixture, called by every refusal case; both `verify:` blocks assert the helper exists and count its call sites. Discrimination now survives at `review_sha` instead of vanishing with the transient red suite. |
| G-4 — SC-07 unmeetable | `BRIEF.md` SC-07 re-worded to grade each of the five boundary questions against the decision that carries it. No decision was widened or collapsed. |
| OC-1 — registry-file retention scope | T-09, `STRIKEABLE AT SIGNATURE`, both halves together, nothing depends on it; D-09 states the consequence of striking it. |
| OC-2 — the binding backstop value | D-09: `OMP_UNVERIFIED_TTL_SECONDS` 86400s recorded as the PLANNED value, explicitly RATIFIED AT SIGNATURE. No alternative invented, nothing left open. |
| OC-3 — `live_children` at `validate-digest.py:1755` | DELIBERATELY ABSENT. No task, not absorbed into any intent; the orchestrator carries it to the operator as a backlog row. |

## The rejected remedy, in plain words

The cycle-1 goal-check asked for T-02 to "name `_expire` as the reuse". That was **not applied
anywhere.** `_expire` compares a non-OMP claim against `CLAIM_TTL_SECONDS` (1200s), which is the
dispatch presumption of death; using it as the binding predicate would empty the claim set for every
compatibility-host agent past twenty minutes and re-allow this bug's founding incident on that host.
T-02 now forbids both `_expire` and `CLAIM_TTL_SECONDS` by name, and T-01 case 6 plus T-03 case 13
and T-05 case 15 go red against any implementation that reintroduces either.

## Open questions for the panel

- The two pre-change fixtures are byte copies of a 2,115-line and an 859-line shell script. That is
  the hermetic route the repository already uses (`tests/integration/fixtures/`), chosen because CI
  checks out at depth 1 and a `git show` against a pinned sha is unreachable there. If the panel
  prefers a lighter proof, it must supply one that still discriminates at `review_sha`.
- T-10's `verify:` is expected to exceed the 60-second guidance. It is the broad gate G-1a demands;
  narrowing it would reopen the gap.
