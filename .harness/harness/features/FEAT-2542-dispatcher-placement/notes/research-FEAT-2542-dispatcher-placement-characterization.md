# Research — FEAT-2542 characterization probe (SC-03, measured before signature)

**BLUF.** At base `2e7a2c77d61e3ae93180dc6d71a355ff7b85d8f8` I ran the real `dispatch-guard.py` on 98
data-carrying rows. 59 rows change under the planned contract and 39 stay the same.

- **#2542.** All seven failed-placement fixtures fall back to the child's declared feature, and the
  dispatch proceeds and claims (exit 0). That includes the section-f exploit: a lead placed in a
  distill run of X, with a failed lookup, dispatches a markerless child into Y and it claims.
  Under the contract, every one of these is an exit-2 lineage denial before any claim.
- **#2532.** The FEAT-2489 payload is refused at base by the plan-route mission rule, and
  `find_run_claim` is never reached. Under the contract it proceeds into the full distill
  preflight and claims.
- **Unchanged rows.** Main, non-lead and id-less controls, and every plan-placed, no-run and
  no-id plan-reader row, keep their base outcome.
- **Unreachable without fault injection.** The escaped `UnreadableRegistry`/`OSError` state
  cannot be produced by any on-disk fixture at base. I reached it only by fault injection
  (below).

## Method

- **Subject.** `<worktree>/.claude/skills/harness/bin/dispatch-guard.py`, the unedited worktree
  copy. `git rev-parse HEAD` printed `2e7a2c77d61e3ae93180dc6d71a355ff7b85d8f8` (the commit
  "FEAT-2537: feature-close distill (#2545)", 2026-11-25). Run as a subprocess under Python
  3.15.2 with `HARNESS_PROJECT_DIR=<fixture>`, `PYTHONDONTWRITEBYTECODE=1` and
  `HARNESS_AGENT_TYPE` unset. I ran it on 2026-11-26.
- **Fixtures.** Each row got a fresh checkout under a `mktemp -d` directory outside the
  worktree (`/tmp/feat2542-probe.WsLLTL`). I built them with the suite's own helpers, imported
  from `tests/integration/test-dispatch-guard.py`: `_checkout` and `_register_lead_run`, with
  manifest lead grants for all three leads. On top of that:
  - Feature `FEAT-90-one-root-fixture` (X) carries the row's `runs[]`.
  - Feature `FEAT-91-other-fixture` (Y) has `runs: []`.
  - Route rows have a real `plan.yaml` with `approval.status` set to pending or approved.
- **Registries.** Real registry rows were written through `inflight_registry.claim_run_start`,
  for runtime id `Orch.Lead` with parent `Orch`:

  | State | How the registry was built |
  |---|---|
  | ok+match | claim as the dispatching lead in X |
  | ok+persona-mismatch | claim as a different lead persona in X |
  | not-found | no claim |
  | ambiguous | two live rows for the same id (X and Y) |
  | unreadable-owner | valid claim, then the owner registry overwritten with `{not json` |
  | unreadable-linked | real git repo plus `git worktree add` (`BUG-99-unrelated`); the owner holds the valid matching claim and the linked worktree registry is `{not json` |

  The unreadable-linked row proves that strictness refuses even when a readable match exists.
- **Branch witness.** Each row ran a second time against an isolated copy of the bin tree
  (`isolated_bin`). The copy's `inflight_registry.py` is the original plus a wrapper around
  `find_run_claim` that logs each call: agent_id, ok, cause and claim persona.
  - I checked the copy with `filecmp`: the only differing file was `inflight_registry.py`, and
    the copy equals the original text plus the wrapper (`inflight_copy_is_original_plus_wrapper:
    true`).
  - Both passes agreed on (exit, claim) for all 98 rows; there were 0 disagreements.
  - The "branch witness" column shows whether `find_run_claim` (inside `_dispatcher_feature`) was
    reached, and with what answer. Every P row shows a call for `Orch.Lead` from a dispatcher in
    `LEADS`. That confirms each placement row reached `_dispatcher_feature` with
    `harness_agent_id` set. No Main, orchestrator or id-less row shows a call.
- **Escaped state.** It exists only on the instrumented copy, with `PROBE_ESCAPE` set to
  `unreadable` or `oserror`; the wrapper then raises after logging.
  - It is unreachable from on-disk data at base. `_live_claims_for_run` catches
    `UnreadableRegistry` per root.
  - `harness_boundary.linked_worktrees(strict=False)` swallows `OSError`/`UnicodeError` per
    pointer.
  - `_read_strict` converts `OSError`/`UnicodeError` and JSON errors into `UnreadableRegistry`.
  - `_process_start_time` swallows `OSError`.
  - The `except (reg.UnreadableRegistry, OSError)` in `_dispatcher_feature` is therefore a
    defensive branch. The build reaches it through a copied, sabotaged bin tree, as
    `DISPATCH_GUARD_BIN` already allows.
- **Read-only.** After this note was written I removed the temp directory (`ls` then reported
  "No such file or directory"). `git status --porcelain` in the worktree then showed only
  `?? .harness/harness/features/FEAT-2542-dispatcher-placement/`. No tracked file, bin file or test
  file was edited. The ignored entries that `--ignored` lists are not this probe's:
  - `bin/__pycache__` is timestamped 07:58:23 local, when the worktree was created, before the
    probe ran;
  - `.harness/.inflight-claims.json` is the host's live claim registry.

## Contract table (planned) — what the SCs and tests hold every row to

**Governed lead dispatcher placement (#2542).** This applies when `agent_type` is in `LEADS` and
the payload carries a non-empty `harness_agent_id`. It resolves through `find_run_claim` before
any other preflight.

| find_run_claim outcome | Contract |
|---|---|
| ok, claim persona == dispatcher | binds the claim's feature; every later check is its base outcome |
| ok, persona mismatch | exit 2, lineage denial `persona-mismatch`, no claim |
| not-found | exit 2, lineage denial `not-found`, no claim |
| ambiguous | exit 2, lineage denial `ambiguous`, no claim |
| structured unreadable | exit 2, lineage denial `unreadable`, no claim, registry bytes left as found |
| escaped UnreadableRegistry/OSError | exit 2, lineage denial `registry-error`, no claim |

**Outside the contract, unchanged.** Main (`omp_main`), non-lead dispatchers with or without
`harness_agent_id`, and a lead payload without `harness_agent_id` keep the declared-feature path.
None of them calls `find_run_claim`.

**product-lead → code-reviewer route (#2532).**

| Trusted placement | distill | plan | missing | conflicting | other (validate) |
|---|---|---|---|---|---|
| open `distill-*` run | proceeds into full distill preflight (feature, tree root, mission) and claims | refused: `_plan_preflight` if not pending, else `_require_distill_mission` | refused: `_require_distill_mission` | refused: `_mission_refusal` | refused: `_require_distill_mission` |
| open non-distill run | refused: plan-route mission | scope-reader preflight (pending plan claims; otherwise refused) | refused | refused | refused |
| no open run | refused: plan-route mission | refused: no registered run | refused | refused | refused |
| any placement failure | lineage denial | lineage denial | lineage denial | lineage denial | lineage denial |
| no `harness_agent_id` | plan route, unchanged (the `sc02_scope_reader` shapes) | unchanged | unchanged | unchanged | unchanged |

A distill-placed product lead whose child declares another feature is still refused by
`_require_distill_feature`.

## Rows, condensed by class

**Placement (P rows).** Dispatcher `harness-eng-lead`, id `Orch.Lead`, X carries `distill-eng`.
Two child shapes per state:

- bound: backend-dev in X with the distill marker and tree root;
- exploit: backend-dev in Y with no marker.

| State | Base bound / exploit | Branch witness | Planned | Delta |
|---|---|---|---|---|
| ok+match | 0 claim / 2 "bound distill run is for X" | ok/harness-eng-lead | same | same |
| ok+persona-mismatch | 0 claim / 0 claim | ok/harness-validator-lead | lineage `persona-mismatch` | changed |
| not-found | 0 claim / 0 claim | not-found | lineage `not-found` | changed |
| ambiguous | 0 claim / 0 claim | ambiguous | lineage `ambiguous` | changed |
| unreadable (owner) | 0 claim / 0 claim; claim step logs "corrupt or unparseable, treating as empty" and rewrites the file | unreadable | lineage `unreadable`, file intact | changed |
| unreadable (linked; owner holds the match) | 0 claim / 0 claim | unreadable | lineage `unreadable` | changed |
| escaped UnreadableRegistry (injected) | 0 claim / 0 claim | UnreadableRegistry | lineage `registry-error` | changed |
| escaped OSError (injected) | 0 claim / 0 claim | OSError | lineage `registry-error` | changed |

**Controls.**

| Rows | Base | Branch witness | Planned |
|---|---|---|---|
| Main → backend-dev (Y), one row per state | 0 claim | not called | same |
| orchestrator with `harness_agent_id` → backend-dev (Y), one row per state | 0 claim | not called | same |
| orchestrator without the id | 0 claim | not called | same |
| eng-lead without the id (ok and not-found registries) | 0 claim | not called | same |

**Route (R rows).** Dispatcher `harness-product-lead`, id `Orch.Lead`, child
`harness-code-reviewer`, declared X.

| Class | distill | plan | missing | conflicting | other |
|---|---|---|---|---|---|
| distill-placed (open `distill-product`, approved plan) — **FEAT-2489 payload = distill column** | base 2 plan-route mission → **proceeds (changed)** | 2 plan-status → same | 2 mission-missing → distill-mission (cause changed) | 2 mission-conflicting → same | 2 plan-route mission → distill-mission (cause changed) |
| distill-placed, pending plan | — | 2 distill-mission (witness: ok/harness-product-lead) → same | — | — | — |
| plan-placed (open `plan-product`, pending) | 2 plan-route mission → same | 0 claim → same | 2 → same | 2 → same | 2 → same |
| no open run (pending) | 2 → same | 2 no-registered-run → same | 2 → same | 2 → same | 2 → same |
| each of the 7 failure fixtures (distill-product, approved) | 2 plan-route mission → lineage (cause changed) | 2 plan-status → lineage | 2 mission-missing → lineage | 2 mission-conflicting → lineage | 2 plan-route mission → lineage |
| each failure fixture on a plan-product run, pending, mission plan | — | **0 claim → lineage denial (changed)** | — | — | — |
| no harness_agent_id (sc02 shapes) | 2 plan-route mission → same | pending 0 claim / approved 2 plan-status → same | 2 → same | — | — |

The validator-lead → code-reviewer ordinary review (no id, no mission) exits 0 and claims at base;
planned the same.

**Base finding (route).** For every R row refused at base, `find_run_claim` was never called. The
plan-route mission rule in `_start_preflight` decides before `_distill_preflight` reads the
placement (no trace line). Only the `plan` rows that passed the scope-reader preflight reached
the placement lookup. That is the source-traced defect, now measured.

## Consequences for the build — found by this census, not by the grilling

1. `tests/integration/test-dispatch-guard.py` has two existing cases whose positive rows dispatch
   as `harness-eng-lead` with `harness_agent_id: LeadOne` and no claim:
   - `case_30_repository_header_binds_exact_factory_claim` (its `dispatch` helper);
   - `case_31_repository_binding_read_from_the_feature_worktree` (via `_c31_dispatch`).

   That is the not-found class: base exit 0, contract exit 2. Their fixtures must bind `LeadOne`
   through `claim_run_start` before dispatching. Their assertions stay as they are, and the file
   is already owned by T-01. No other test that runs `dispatch-guard.py` sends a lead dispatcher
   with a runtime id:
   - `test-lead-start-return.py` and `tests/unit/test-lead-start-preflight.py` send no id from a
     lead;
   - `test-omp-native-gate-runtime.py` dispatches as `harness-orchestrator`;
   - `omp-hooks.test.ts` mocks the script.

   I found this by grepping for `harness_agent_id` across `tests/`.
2. `tests/unit/test-broad-catch-census.py` requires zero broad catches in `dispatch-guard.py`.
   The new placement helper must catch `(reg.UnreadableRegistry, OSError)` only.
3. Unreadable owner registry, base: the claim step's lenient `_parse` rewrites the corrupt file.
   DEC-218 keeps this treat-as-empty recovery for claim paths. Under the contract, a governed lead
   dispatch refuses before the claim step, so its registry is left as found. Main and non-lead
   dispatches keep the base rewrite, which this feature does not change.

## Open questions this probe raises

- The escaped state is unreachable from on-disk data at base. The SC keeps it as a class member,
  graded through a fault-injected copied bin tree. Non-blocking.
- A lead payload without `harness_agent_id` keeps the declared-feature path (rows C/*/lead-no-id).
  The host refuses a persona's nested Task without `ctx.agent` ids (DEC-218, "An OMP process
  without the official ctx.agent identity gets no fallback path"), so this path is unreachable
  for governed leads. DEC-250's "missing identity" denial is therefore not extended here.
  Non-blocking; the signer may widen it.

## Appendix A — full measured rows (base 2e7a2c77)

Columns:

- **base cause** is the guard's first BLOCKED line, trimmed; X is `FEAT-90-one-root-fixture`
  and Y is `FEAT-91-other-fixture`.
- **planned** is the contract-table outcome.
- **delta** compares the base cause with the planned cause.

| row | dispatcher -> child (declared, mission lines) | base exit / claim | base cause (trimmed stderr) | branch witness | planned | delta |
|---|---|---|---|---|---|---|
| P/ok/bound-child | eng-lead -> backend-dev (X, distill) | 0 / yes | proceeds+claim | find_run_claim(Orch.Lead) -> ok/harness-eng-lead | proceeds+claim | same |
| P/ok/exploit-child-Y-no-marker | eng-lead -> backend-dev (Y, none) | 2 / no | distill-feature: harness-eng-lead's bound distill run is for X, but this dispatch of harness-backend-dev declares Y. | find_run_claim(Orch.Lead) -> ok/harness-eng-lead | distill-feature | same |
| C/ok/main | Main -> backend-dev (Y, none) | 0 / yes | proceeds+claim | find_run_claim not called | proceeds+claim | same |
| C/ok/orchestrator-with-id | orchestrator -> backend-dev (Y, none) | 0 / yes | proceeds+claim | find_run_claim not called | proceeds+claim | same |
| P/mismatch/bound-child | eng-lead -> backend-dev (X, distill) | 0 / yes | proceeds+claim | find_run_claim(Orch.Lead) -> ok/harness-validator-lead | lineage:persona-mismatch | changed |
| P/mismatch/exploit-child-Y-no-marker | eng-lead -> backend-dev (Y, none) | 0 / yes | proceeds+claim | find_run_claim(Orch.Lead) -> ok/harness-validator-lead | lineage:persona-mismatch | changed |
| C/mismatch/main | Main -> backend-dev (Y, none) | 0 / yes | proceeds+claim | find_run_claim not called | proceeds+claim | same |
| C/mismatch/orchestrator-with-id | orchestrator -> backend-dev (Y, none) | 0 / yes | proceeds+claim | find_run_claim not called | proceeds+claim | same |
| P/notfound/bound-child | eng-lead -> backend-dev (X, distill) | 0 / yes | proceeds+claim | find_run_claim(Orch.Lead) -> not-found | lineage:not-found | changed |
| P/notfound/exploit-child-Y-no-marker | eng-lead -> backend-dev (Y, none) | 0 / yes | proceeds+claim | find_run_claim(Orch.Lead) -> not-found | lineage:not-found | changed |
| C/notfound/main | Main -> backend-dev (Y, none) | 0 / yes | proceeds+claim | find_run_claim not called | proceeds+claim | same |
| C/notfound/orchestrator-with-id | orchestrator -> backend-dev (Y, none) | 0 / yes | proceeds+claim | find_run_claim not called | proceeds+claim | same |
| P/ambiguous/bound-child | eng-lead -> backend-dev (X, distill) | 0 / yes | proceeds+claim | find_run_claim(Orch.Lead) -> ambiguous | lineage:ambiguous | changed |
| P/ambiguous/exploit-child-Y-no-marker | eng-lead -> backend-dev (Y, none) | 0 / yes | proceeds+claim | find_run_claim(Orch.Lead) -> ambiguous | lineage:ambiguous | changed |
| C/ambiguous/main | Main -> backend-dev (Y, none) | 0 / yes | proceeds+claim | find_run_claim not called | proceeds+claim | same |
| C/ambiguous/orchestrator-with-id | orchestrator -> backend-dev (Y, none) | 0 / yes | proceeds+claim | find_run_claim not called | proceeds+claim | same |
| P/unreadable-owner/bound-child | eng-lead -> backend-dev (X, distill) | 0 / yes | proceeds+claim | find_run_claim(Orch.Lead) -> unreadable | lineage:unreadable | changed |
| P/unreadable-owner/exploit-child-Y-no-marker | eng-lead -> backend-dev (Y, none) | 0 / yes | proceeds+claim | find_run_claim(Orch.Lead) -> unreadable | lineage:unreadable | changed |
| C/unreadable-owner/main | Main -> backend-dev (Y, none) | 0 / yes | proceeds+claim | find_run_claim not called | proceeds+claim | same |
| C/unreadable-owner/orchestrator-with-id | orchestrator -> backend-dev (Y, none) | 0 / yes | proceeds+claim | find_run_claim not called | proceeds+claim | same |
| P/unreadable-linked/bound-child | eng-lead -> backend-dev (X, distill) | 0 / yes | proceeds+claim | find_run_claim(Orch.Lead) -> unreadable | lineage:unreadable | changed |
| P/unreadable-linked/exploit-child-Y-no-marker | eng-lead -> backend-dev (Y, none) | 0 / yes | proceeds+claim | find_run_claim(Orch.Lead) -> unreadable | lineage:unreadable | changed |
| C/unreadable-linked/main | Main -> backend-dev (Y, none) | 0 / yes | proceeds+claim | find_run_claim not called | proceeds+claim | same |
| C/unreadable-linked/orchestrator-with-id | orchestrator -> backend-dev (Y, none) | 0 / yes | proceeds+claim | find_run_claim not called | proceeds+claim | same |
| P/escape-unreadable/bound-child | eng-lead -> backend-dev (X, distill) | 0 / yes | proceeds+claim | find_run_claim(Orch.Lead) -> UnreadableRegistry | lineage:registry-error | changed |
| P/escape-unreadable/exploit-child-Y-no-marker | eng-lead -> backend-dev (Y, none) | 0 / yes | proceeds+claim | find_run_claim(Orch.Lead) -> UnreadableRegistry | lineage:registry-error | changed |
| C/escape-unreadable/main | Main -> backend-dev (Y, none) | 0 / yes | proceeds+claim | find_run_claim not called | proceeds+claim | same |
| C/escape-unreadable/orchestrator-with-id | orchestrator -> backend-dev (Y, none) | 0 / yes | proceeds+claim | find_run_claim not called | proceeds+claim | same |
| P/escape-oserror/bound-child | eng-lead -> backend-dev (X, distill) | 0 / yes | proceeds+claim | find_run_claim(Orch.Lead) -> OSError | lineage:registry-error | changed |
| P/escape-oserror/exploit-child-Y-no-marker | eng-lead -> backend-dev (Y, none) | 0 / yes | proceeds+claim | find_run_claim(Orch.Lead) -> OSError | lineage:registry-error | changed |
| C/escape-oserror/main | Main -> backend-dev (Y, none) | 0 / yes | proceeds+claim | find_run_claim not called | proceeds+claim | same |
| C/escape-oserror/orchestrator-with-id | orchestrator -> backend-dev (Y, none) | 0 / yes | proceeds+claim | find_run_claim not called | proceeds+claim | same |
| C/ok/orchestrator-no-id | orchestrator no-id -> backend-dev (Y, none) | 0 / yes | proceeds+claim | find_run_claim not called | proceeds+claim | same |
| C/ok/lead-no-id | eng-lead no-id -> backend-dev (Y, none) | 0 / yes | proceeds+claim | find_run_claim not called | proceeds+claim | same |
| C/notfound/lead-no-id | eng-lead no-id -> backend-dev (Y, none) | 0 / yes | proceeds+claim | find_run_claim not called | proceeds+claim | same |
| R/distill-placed/distill | product-lead -> code-reviewer (X, distill) | 2 / no | plan-route-mission: the harness-code-reviewer dispatch for X declares 'distill'; the plan team's scope reader declares plan. | find_run_claim not called | proceeds+claim | changed |
| R/distill-placed/plan | product-lead -> code-reviewer (X, plan) | 2 / no | plan-status: harness-code-reviewer plan-panel start for X refused before any work: plan review mode is only valid while app | find_run_claim not called | plan-status | same |
| R/distill-placed/missing | product-lead -> code-reviewer (X, none) | 2 / no | mission-missing: the harness-code-reviewer dispatch for X has no HARNESS-MISSION line. | find_run_claim not called | distill-mission | changed |
| R/distill-placed/conflicting | product-lead -> code-reviewer (X, distill,plan) | 2 / no | mission-conflicting: the harness-code-reviewer dispatch for X has conflicting or malformed HARNESS-MISSION lines ('HARNESS-MISSION: | find_run_claim not called | mission-conflicting | same |
| R/distill-placed/other | product-lead -> code-reviewer (X, validate) | 2 / no | plan-route-mission: the harness-code-reviewer dispatch for X declares 'validate'; the plan team's scope reader declares plan. | find_run_claim not called | distill-mission | changed |
| R/distill-placed-pending-plan/plan | product-lead -> code-reviewer (X, plan) | 2 / no | distill-mission: the harness-code-reviewer dispatch for X is a child of a bound distill run but declares 'plan'. | find_run_claim(Orch.Lead) -> ok/harness-product-lead | distill-mission | same |
| R/plan-placed/distill | product-lead -> code-reviewer (X, distill) | 2 / no | plan-route-mission: the harness-code-reviewer dispatch for X declares 'distill'; the plan team's scope reader declares plan. | find_run_claim not called | plan-route-mission | same |
| R/no-open-run/distill | product-lead -> code-reviewer (X, distill) | 2 / no | plan-route-mission: the harness-code-reviewer dispatch for X declares 'distill'; the plan team's scope reader declares plan. | find_run_claim not called | plan-route-mission | same |
| R/plan-placed/plan | product-lead -> code-reviewer (X, plan) | 0 / yes | proceeds+claim | find_run_claim(Orch.Lead) -> ok/harness-product-lead | proceeds+claim | same |
| R/no-open-run/plan | product-lead -> code-reviewer (X, plan) | 2 / no | no-registered-run: harness-product-lead cannot start for X: authorization requires exactly one matching open registered lead run. | find_run_claim not called | no-registered-run | same |
| R/plan-placed/missing | product-lead -> code-reviewer (X, none) | 2 / no | mission-missing: the harness-code-reviewer dispatch for X has no HARNESS-MISSION line. | find_run_claim not called | mission-missing | same |
| R/no-open-run/missing | product-lead -> code-reviewer (X, none) | 2 / no | mission-missing: the harness-code-reviewer dispatch for X has no HARNESS-MISSION line. | find_run_claim not called | mission-missing | same |
| R/plan-placed/conflicting | product-lead -> code-reviewer (X, distill,plan) | 2 / no | mission-conflicting: the harness-code-reviewer dispatch for X has conflicting or malformed HARNESS-MISSION lines ('HARNESS-MISSION: | find_run_claim not called | mission-conflicting | same |
| R/no-open-run/conflicting | product-lead -> code-reviewer (X, distill,plan) | 2 / no | mission-conflicting: the harness-code-reviewer dispatch for X has conflicting or malformed HARNESS-MISSION lines ('HARNESS-MISSION: | find_run_claim not called | mission-conflicting | same |
| R/plan-placed/other | product-lead -> code-reviewer (X, validate) | 2 / no | plan-route-mission: the harness-code-reviewer dispatch for X declares 'validate'; the plan team's scope reader declares plan. | find_run_claim not called | plan-route-mission | same |
| R/no-open-run/other | product-lead -> code-reviewer (X, validate) | 2 / no | plan-route-mission: the harness-code-reviewer dispatch for X declares 'validate'; the plan team's scope reader declares plan. | find_run_claim not called | plan-route-mission | same |
| R/fail-mismatch/distill | product-lead -> code-reviewer (X, distill) | 2 / no | plan-route-mission (as R/distill-placed/distill) | find_run_claim not called | lineage:persona-mismatch | changed |
| R/fail-mismatch/plan | product-lead -> code-reviewer (X, plan) | 2 / no | plan-status | find_run_claim not called | lineage:persona-mismatch | changed |
| R/fail-mismatch/missing | product-lead -> code-reviewer (X, none) | 2 / no | mission-missing | find_run_claim not called | lineage:persona-mismatch | changed |
| R/fail-mismatch/conflicting | product-lead -> code-reviewer (X, distill,plan) | 2 / no | mission-conflicting | find_run_claim not called | lineage:persona-mismatch | changed |
| R/fail-mismatch/other | product-lead -> code-reviewer (X, validate) | 2 / no | plan-route-mission | find_run_claim not called | lineage:persona-mismatch | changed |
| R/fail-mismatch/plan-on-plan-run | product-lead -> code-reviewer (X, plan) | 0 / yes | proceeds+claim | find_run_claim(Orch.Lead) -> ok/harness-validator-lead | lineage:persona-mismatch | changed |
| R/fail-notfound/distill | product-lead -> code-reviewer (X, distill) | 2 / no | plan-route-mission | find_run_claim not called | lineage:not-found | changed |
| R/fail-notfound/plan | product-lead -> code-reviewer (X, plan) | 2 / no | plan-status | find_run_claim not called | lineage:not-found | changed |
| R/fail-notfound/missing | product-lead -> code-reviewer (X, none) | 2 / no | mission-missing | find_run_claim not called | lineage:not-found | changed |
| R/fail-notfound/conflicting | product-lead -> code-reviewer (X, distill,plan) | 2 / no | mission-conflicting | find_run_claim not called | lineage:not-found | changed |
| R/fail-notfound/other | product-lead -> code-reviewer (X, validate) | 2 / no | plan-route-mission | find_run_claim not called | lineage:not-found | changed |
| R/fail-notfound/plan-on-plan-run | product-lead -> code-reviewer (X, plan) | 0 / yes | proceeds+claim | find_run_claim(Orch.Lead) -> not-found | lineage:not-found | changed |
| R/fail-ambiguous/distill | product-lead -> code-reviewer (X, distill) | 2 / no | plan-route-mission | find_run_claim not called | lineage:ambiguous | changed |
| R/fail-ambiguous/plan | product-lead -> code-reviewer (X, plan) | 2 / no | plan-status | find_run_claim not called | lineage:ambiguous | changed |
| R/fail-ambiguous/missing | product-lead -> code-reviewer (X, none) | 2 / no | mission-missing | find_run_claim not called | lineage:ambiguous | changed |
| R/fail-ambiguous/conflicting | product-lead -> code-reviewer (X, distill,plan) | 2 / no | mission-conflicting | find_run_claim not called | lineage:ambiguous | changed |
| R/fail-ambiguous/other | product-lead -> code-reviewer (X, validate) | 2 / no | plan-route-mission | find_run_claim not called | lineage:ambiguous | changed |
| R/fail-ambiguous/plan-on-plan-run | product-lead -> code-reviewer (X, plan) | 0 / yes | proceeds+claim | find_run_claim(Orch.Lead) -> ambiguous | lineage:ambiguous | changed |
| R/fail-unreadable-owner/distill | product-lead -> code-reviewer (X, distill) | 2 / no | plan-route-mission | find_run_claim not called | lineage:unreadable | changed |
| R/fail-unreadable-owner/plan | product-lead -> code-reviewer (X, plan) | 2 / no | plan-status | find_run_claim not called | lineage:unreadable | changed |
| R/fail-unreadable-owner/missing | product-lead -> code-reviewer (X, none) | 2 / no | mission-missing | find_run_claim not called | lineage:unreadable | changed |
| R/fail-unreadable-owner/conflicting | product-lead -> code-reviewer (X, distill,plan) | 2 / no | mission-conflicting | find_run_claim not called | lineage:unreadable | changed |
| R/fail-unreadable-owner/other | product-lead -> code-reviewer (X, validate) | 2 / no | plan-route-mission | find_run_claim not called | lineage:unreadable | changed |
| R/fail-unreadable-owner/plan-on-plan-run | product-lead -> code-reviewer (X, plan) | 0 / yes | proceeds+claim (claim step: "corrupt or unparseable, treating as empty") | find_run_claim(Orch.Lead) -> unreadable | lineage:unreadable | changed |
| R/fail-unreadable-linked/distill | product-lead -> code-reviewer (X, distill) | 2 / no | plan-route-mission | find_run_claim not called | lineage:unreadable | changed |
| R/fail-unreadable-linked/plan | product-lead -> code-reviewer (X, plan) | 2 / no | plan-status | find_run_claim not called | lineage:unreadable | changed |
| R/fail-unreadable-linked/missing | product-lead -> code-reviewer (X, none) | 2 / no | mission-missing | find_run_claim not called | lineage:unreadable | changed |
| R/fail-unreadable-linked/conflicting | product-lead -> code-reviewer (X, distill,plan) | 2 / no | mission-conflicting | find_run_claim not called | lineage:unreadable | changed |
| R/fail-unreadable-linked/other | product-lead -> code-reviewer (X, validate) | 2 / no | plan-route-mission | find_run_claim not called | lineage:unreadable | changed |
| R/fail-unreadable-linked/plan-on-plan-run | product-lead -> code-reviewer (X, plan) | 0 / yes | proceeds+claim | find_run_claim(Orch.Lead) -> unreadable | lineage:unreadable | changed |
| R/fail-escape-unreadable/distill | product-lead -> code-reviewer (X, distill) | 2 / no | plan-route-mission | find_run_claim not called | lineage:registry-error | changed |
| R/fail-escape-unreadable/plan | product-lead -> code-reviewer (X, plan) | 2 / no | plan-status | find_run_claim not called | lineage:registry-error | changed |
| R/fail-escape-unreadable/missing | product-lead -> code-reviewer (X, none) | 2 / no | mission-missing | find_run_claim not called | lineage:registry-error | changed |
| R/fail-escape-unreadable/conflicting | product-lead -> code-reviewer (X, distill,plan) | 2 / no | mission-conflicting | find_run_claim not called | lineage:registry-error | changed |
| R/fail-escape-unreadable/other | product-lead -> code-reviewer (X, validate) | 2 / no | plan-route-mission | find_run_claim not called | lineage:registry-error | changed |
| R/fail-escape-unreadable/plan-on-plan-run | product-lead -> code-reviewer (X, plan) | 0 / yes | proceeds+claim | find_run_claim(Orch.Lead) -> UnreadableRegistry | lineage:registry-error | changed |
| R/fail-escape-oserror/distill | product-lead -> code-reviewer (X, distill) | 2 / no | plan-route-mission | find_run_claim not called | lineage:registry-error | changed |
| R/fail-escape-oserror/plan | product-lead -> code-reviewer (X, plan) | 2 / no | plan-status | find_run_claim not called | lineage:registry-error | changed |
| R/fail-escape-oserror/missing | product-lead -> code-reviewer (X, none) | 2 / no | mission-missing | find_run_claim not called | lineage:registry-error | changed |
| R/fail-escape-oserror/conflicting | product-lead -> code-reviewer (X, distill,plan) | 2 / no | mission-conflicting | find_run_claim not called | lineage:registry-error | changed |
| R/fail-escape-oserror/other | product-lead -> code-reviewer (X, validate) | 2 / no | plan-route-mission | find_run_claim not called | lineage:registry-error | changed |
| R/fail-escape-oserror/plan-on-plan-run | product-lead -> code-reviewer (X, plan) | 0 / yes | proceeds+claim | find_run_claim(Orch.Lead) -> OSError | lineage:registry-error | changed |
| R/no-id/plan-pending | product-lead no-id -> code-reviewer (X, plan) | 0 / yes | proceeds+claim | find_run_claim not called | proceeds+claim | same |
| R/no-id/missing-pending | product-lead no-id -> code-reviewer (X, none) | 2 / no | mission-missing | find_run_claim not called | mission-missing | same |
| R/no-id/plan-approved | product-lead no-id -> code-reviewer (X, plan) | 2 / no | plan-status | find_run_claim not called | plan-status | same |
| R/no-id/distill-pending | product-lead no-id -> code-reviewer (X, distill) | 2 / no | plan-route-mission | find_run_claim not called | plan-route-mission | same |
| R/no-id/validator-review | validator-lead no-id -> code-reviewer (X, none) | 0 / yes | proceeds+claim | find_run_claim not called | proceeds+claim | same |

Totals: rows=98, same=39, changed=59; instrumented-pass disagreements=0. Witness:
`{"only_in_subject": [], "only_in_copy": [], "differing": ["inflight_registry.py"],
"inflight_copy_is_original_plus_wrapper": true}`.

## Build-time repeat (SC-03 second clause)

T-01 writes the new test cases before it edits `dispatch-guard.py`, so the first run of the
extended `tests/integration/test-dispatch-guard.py` is a run against base source. Apply cycle 1
(panel PF-309f, PF-5bd4) replaced the prose prediction with one named row inventory.

- **Inventory.** Every new assertion is one check named `<row id>:<field>` (exit, claim, receipt,
  cause, remedy, unavailable, bytes, run-reads). T-01's intent states, per row, which fields are
  red at base. That distinguishes a changed cause (exit 2 → exit 2, new text) from a changed
  exit or claim. The receipt lists `predicted_red:` lines before the run and `observed_red:`
  lines after it, and T-01's verify requires the two sets to be equal.
- **Base run.** Cases 1-37 and the rebound cases 30/31 pass. A rebound claim changes nothing at
  base.
- **Pin run.** The run happens at the T-01 commit (`tested_sha`) and must be all green. T-02's
  terminal verify, and SC-03 at the review pin, require `dispatch-guard.py` and
  `test-dispatch-guard.py` to be byte-identical between `tested_sha` and HEAD (or `review_sha`).
- **Proportionality (PF-658a).** For failure states on the route, each state takes one mission,
  rotated so that every mission meets a failure. This holds because placement refuses before
  any mission is read. Controls run in the unreadable-owner and escaped-oserror states. The
  second state raises if anything calls `find_run_claim`, so it shows the controls never read
  placement.
- **Id-less lead rows (PF-0017, open).** They stay asserted as SC-02 LEAVE rows. The signer's
  OQ-1 ruling governs them.

## Expertise applied

- **harness-pm P-11** (data-carrying instances, not the minimal example). It put a real readable
  match beside the unreadable registry (unreadable-linked) and rebuilt the FEAT-2489 payload.
- **O-06** (assert the harness reached the branch). It added the instrumented second pass and its
  `filecmp` witness.
