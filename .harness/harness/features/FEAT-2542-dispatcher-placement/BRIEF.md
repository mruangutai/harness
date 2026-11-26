# BRIEF — FEAT-2542 dispatcher placement and route keying (#2542 + #2532)

## Problem

`dispatch-guard.py` decides two things about a governed lead's nested dispatch from the wrong
source, and both are measured at base `2e7a2c77`
(`notes/research-FEAT-2542-dispatcher-placement-characterization.md`).

**#2532.** Every `harness-product-lead` → `harness-code-reviewer` start is treated as the plan
team's scope reader, which must declare `plan`. A product distill close is ordered to distill its
borrowed plan readers. FEAT-2489's product lead tried exactly that with `HARNESS-MISSION:
distill`, was refused, honestly declined to relabel, and left the reviewer's lesson undelivered
(FEAT-2489 `runs/distill-product/digest.md`, OQ-D1/OQ-D2). Every future product distill hits the
same wall, and the only way past it is relabeling the mission.

**#2542.** When a governed lead's runtime placement cannot be established, `_dispatcher_feature`
silently uses the feature the child declares instead. That happens when its own claim is missing,
ambiguous, unreadable, held by another persona, or the lookup raises. In all seven failed-placement
fixtures the dispatch proceeded and claimed. That includes a lead placed in a distill run of X,
whose lookup failed, dispatching a markerless child into Y: the distill obligation simply vanished.

## Done when — by perspective

**operator** — When a governed lead's own runtime claim cannot be found, read, told apart from
another, or matched to its persona, its dispatch stops. The denial names which state it hit and
what to repair; the dispatch never quietly runs under whatever feature the child declared. My
dispatches from Main, and every non-lead dispatch, behave exactly as before. Both tickets are
closed by this feature.

**orchestrator** — A product lead that holds a registered distill run can dispatch the code
reviewer it borrowed for the plan panel with `HARNESS-MISSION: distill`. No lead ever has to
relabel a mission to get past the guard. The plan team's scope reader keeps every refusal it has
today.

**reader** — I grade the change against one contract table. Every placement state and route class
has a measured base outcome, a planned outcome and a test row, so the behaviour change is
enumerated rather than asserted.

**code maintainer** — One decision records what each placement state must do and why it refuses
rather than passing visibly unavailable. When I change this guard, I know which neighbouring
decisions it leans on and which it leaves alone.

## Success criteria

- SC-01 (orchestrator): **Route class.** The class is every member of {trusted placement of the
  dispatching `harness-product-lead`: open `distill-*` run, open non-distill run, no open run, each
  of the five placement-failure states} × {declared mission: distill, plan, missing, conflicting,
  other}, on a `harness-product-lead` → `harness-code-reviewer` dispatch. Every member matches the
  contract table in the research note (section "Contract table (planned)"):
  - distill-placed with `distill` proceeds into the full distill preflight, which enforces
    feature, tree root and mission, then claims;
  - distill-placed with any other mission is refused before any claim;
  - every failure state is SC-02's lineage denial.

  The exemption keys only on trusted placement: runtime id → `find_run_claim`, persona-matched →
  that feature's one open registered run → `DISTILL_RUN_RE`. No declared mission, task text or
  child-supplied field can switch the scope-reader rule off. The route and the distill preflight
  consume one dispatch-local placement answer, its registered run read once, so they never
  disagree (a test counts the reads).

  **LEAVE (must stay as-is):**
  - Every non-distill-placed, no-open-run and no-`harness_agent_id` row keeps its base outcome
    (plan-route mission refusal, pending-plan scope-reader preflight, registered-run refusal).
  - `tests/integration/test-lead-start-return.py` `sc02_scope_reader` and
    `sc02_plan_status_refusals` pass, and that file is byte-identical to `2e7a2c77`.
  - `test-dispatch-guard.py` cases 32-37 pass.
  - The validator-lead → code-reviewer ordinary review is unchanged.

  qa demonstrates that the distill-placed + `distill` row fails at base `2e7a2c77` before the fix.
  verify: automated        evidence: integration
- SC-02 (operator): **Placement class.** The class is every `find_run_claim` outcome for a
  dispatcher in `LEADS` (all three leads) carrying `harness_agent_id`: ok+match,
  ok+persona-mismatch, not-found, ambiguous, structured unreadable (owner registry, and a linked
  worktree registry beside a readable match), and escaped `UnreadableRegistry`/`OSError`.
  - **ok+match** binds the claim's feature, and every later check keeps its base outcome.
  - **Every other member** exits 2 before any claim and leaves an unreadable registry's bytes as
    found. Its lineage denial names the cause token (`unreadable`, `registry-error`, `not-found`,
    `ambiguous` or `persona-mismatch`), the runtime id, a next step specific to that cause (an
    ambiguous claim is released only in its own registry, chosen by `--root`; an exception that
    names no file is reproduced before anything is repaired; a persona mismatch leaves a live
    claim alone), and `inflight_registry.py find-run --agent-id <id>`.
  - None of these states emits the unavailable outcome.

  **LEAVE (must stay as-is):**
  - Main, non-lead dispatchers with and without `harness_agent_id`, and a lead payload without
    `harness_agent_id` keep their base outcome in every registry state. The tests show it in the
    unreadable-owner state and under a `find_run_claim` that raises if called, which proves none
    of them reads placement, so no registry state can change their outcome.
  - The terminal claim-step unavailable pass-through is unchanged.
  - `inflight_registry.py` is byte-identical to `2e7a2c77`.
  - `dispatch-guard.py` carries zero broad catches (`tests/unit/test-broad-catch-census.py`).
  - `tests/unit/test-lead-start-preflight.py` passes.

  qa demonstrates that each changed class fails at base first. The escaped classes are reached
  through a fault-injected copy of the bin tree, because no on-disk fixture reaches them.
  verify: automated        evidence: integration
- SC-03 (reader): **Characterization.**
  - Before signature, `git show <review_sha>:` of the research note shows a measured base outcome
    at `2e7a2c77` for every placement state and route class. The fixtures are data-carrying, and
    each row has a branch witness, a planned outcome and a delta.
  - At build, `notes/characterization-pin.md` records one row inventory: the predicted base
    failures, the extended `test-dispatch-guard.py` run against base source (failing exactly
    those assertions, which are the new assertions for the research note's `changed` rows) and
    the all-green run at the tested commit, with base and tested SHAs. At the pin,
    `git diff --quiet <tested_sha> <review_sha> -- dispatch-guard.py test-dispatch-guard.py`
    is clean, so the tested source is the reviewed source.

  verify: inspection
- SC-04 (code maintainer): **Record.** `git show <review_sha>:.harness/harness/docs/DECISIONS.md`
  carries one new DEC: DEC-258, or the next free number if main has used it. It records:
  - explicit-bind-or-refuse for a governed lead dispatcher carrying `harness_agent_id`;
  - the five denial states, and the rejection of the unavailable outcome for them;
  - the preserved Main, non-lead and no-id paths;
  - the placement-keyed scope-reader route and its rejected alternatives;
  - its lineage relation to DEC-100, DEC-218, DEC-250 and DEC-253, none of which it amends.

  `DECISIONS-INDEX.md` at the pin carries its row with a hand-written ruling and regenerates with
  no drift.
  verify: inspection
- SC-05 (operator): **Tickets.** `plan.yaml` `source_issues` at `review_sha` names exactly 2542
  and 2532, so ship's finalization closes both. Closure itself is observable only after ship.
  verify: inspection

## Verification gaps

- **No null-runner kind covers a surface this feature touches.** Unit and integration are active
  with runners. `component` and `ui` are unresolved, but their detect globs (`*.spec.tsx`, e2e)
  match nothing here.
- **SC-02, escaped exception.** On-disk data cannot produce it at base (research note,
  "Method"). It is proven only by fault injection into a copied bin tree, not by a reachable
  production state.
- **SC-01 and SC-02, live host.** Payload provenance (`harness_agent_id` from `ctx.agent`) is
  taken from `harness-hooks.ts` `basePayload` by source reading. No live OMP probe runs in this
  feature; the integration suite drives the script with recorded payload shapes.
- **SC-05, closure.** Issue closure happens at ship, after goal-check. The goal-check grades
  `source_issues` only.

## Constraints

- **DEC-174 BLOCKS** the execution route. `dispatch-guard.py` and `test-dispatch-guard.py` are
  enumerated enforcement layer: every task is main-session-direct, and no team run executes them.
- **DEC-228 BLOCKS** weakening the scope reader. Its pending-plan contract and missing/wrong
  plan-marker refusals survive for every dispatch not placed in a registered distill run.
- **DEC-100 SUPPLIES** "a refusal outranks it". Placement failure is classified as a refusal
  inside DEC-100, which is not amended. The terminal claim-step unavailable pass-through (FEAT-65)
  stays.
- **DEC-218 and DEC-250 SUPPLY** the lineage semantics: cannot-read is never no-claims, ambiguity
  refuses, and text supplies no authority. Neither is amended. `find_run_claim`'s any-unreadable
  strictness is not relaxed.
- **DEC-253** is a different boundary (raw Expertise `Write`), untouched.
- **DEC-254 SUPPLIES** the five-field `decisions_affected` disposition rows.
- **No preflight reorder.** The discriminator lives inside `_mission_scope`; `_start_preflight`
  and `_distill_preflight` keep their order.
- **The build adds no broad `except`** to `dispatch-guard.py` (FEAT-65 census).
- **Rework budget, proposed for the signer, not approved:** 2 rounds / 90 min (the grilling's
  E/E2 parameters).

## Out of scope

Copied from the grilling's non-goals, with its reasons:

- Raw `Write` to own Expertise files. DEC-253 deliberately retains it; it is a distinct boundary.
- Downstream validate-digest / `expertise_apply` authority. Both are independently fail-closed
  (verified).
- `task` missing from the hook's `mutates` list. That is a hooks-layer residual, for a separate
  ticket if ever.
- `find_run_claim` internals.
- The claim-step unavailable pass-through.

## Approval

status: approved
approved-by: Mike Ruangutai (delegated to fable-advisor)
date: 2026-11-26
