# Grilling — inflight claim lifecycle (#1898) — 2026-09-24

Evidence and full fix scope: #1898, comments `5815142370` (root cause analysis and fix scope) and
`5815186598` (definition of done). Flow id `BUG-1898-inflight-claim-lifecycle`.

## Destination
The claim lifecycle maintains itself. Every governed agent holds exactly one claim, bound to its
agent id from the first turn of its run until it settles. Nothing else removes that claim, and
nothing outlives the agent. The proof is a real plan → build → validate cycle in a worktree with
zero hand-binding and no leftover rows.

## Mission
mission: plan
reason: five causes across the OMP extension, the digest validator, the registry and their tests; the fix adds a claim-at-run-start path and re-arms the held-child gate (new enforcement surfaces), and occurrence 1's trigger is still unpinned
confirmed-by: operator

## Settled
- Destination → accepted as written.
- Scope → defects A–E exactly as in the #1898 fix-scope and definition-of-done comments: A (the
  suite releases live claims), B (waking a settled agent skips the claim), C (batch release pairs
  by position), D (the lifecycle handler never fires), E (release on yield and the held-child gate
  read the wrong registry).
- B → **a governed agent claims at the start of its run** (option a). Any governed run that starts
  without a live claim bound to its agent id either takes one, under the same one-pm rule
  dispatch applies, or refuses to proceed. The claim is released on yield. This one rule covers
  the first run (binding the claim dispatch created), a wake, and a dispatch where the guard
  crashed.
- One-pm rule → unchanged. A second `harness-pm` while one holds a live claim is refused, both at
  dispatch and at run start.
- Guard crashes (DEC-100) → dispatch keeps passing through, so DEC-100 is unchanged. A child that
  cannot hold a claim at run start refuses at the child: `before_agent_start` cannot stop a run,
  so it injects the reason and blocks every tool except `yield`, and the child returns BLOCKED.
- Retries → the run-start refusal names its cause and says whether a retry can succeed: a one-pm
  conflict names the live holder and clears when that holder settles; an unreadable registry is
  not retryable and needs the operator. No mechanical retry limit; BLOCKED already goes up, never
  back (`harness-team` step f, `harness` routing table).
- C → claims are keyed by agent id, never by batch position. The task result handler releases or
  attaches by each result row's `id`. Dispatch receipts are kept only to roll back children that
  never started. The dispatch-time pre-bind to the bare `dispatch.name` is deleted.
- OMP `before_subagent_spawn` change → dropped. The run-start rule already binds the exact id and
  covers eval `agent()` spawns; the remaining dispatch-policy gap is #1919.
- Order → E lands after C and D, because re-arming the held-child gate while leaked rows remain
  would refuse orchestrator and lead yields.
- Cutover → a one-time operator step at merge: before live sessions pick up the new hooks, list
  each feature registry and release the known-dead rows one by one. It goes in the ship checklist;
  it is not automated (the registry cannot tell a leaked row from a live one).
- Proof → a scripted live probe gates the merge. It runs in an OMP session started inside this
  worktree, so it loads only the new code, drives a small hierarchy covering D's lifecycle
  delivery, the wake claim, the mixed-batch release and a suite run, and asserts an empty
  registry at the end. The definition of done's end-to-end cycle is confirmed on the first real
  feature after merge and recorded there; it is not a ship gate.
- Records → DEC-204's release paragraph is rewritten to describe the shipped lifecycle (DEC-205).
  DEC-100 stays as it is, with a note on the run-start refusal.
- Execution → DEC-174: every task that touches a hook, the validator, the registry or their tests
  is `main-session-direct`.
- Sharp questions still unanswered; pm resolves them in the plan:
  - Occurrence 1 (FEAT-64 c0): either explain what removed the pm's claim 367 ms after qa's yield,
    or show the fixed lifecycle holds when qa yields while a pm is live.
  - Which resolver becomes the single one for E: dispatch-guard's `_root_for` (a linked worktree
    whose basename equals the flow id) or `inflight_registry.feature_root`
    (`harness_boundary.worktree_for_feature`).
  - Which event bus a parent session receives its children's lifecycle frames on
    (`pi.events` versus the subagent bus); the live probe settles it.
  - Whether a subagent revived after an OMP restart recovers its `HARNESS-FEATURE` marker, which
    the run-start claim needs.

## Not yet specified
- None.

## Out of scope
- The OMP fork change to `before_subagent_spawn`, and the eval `agent()` dispatch-policy gap →
  #1919.
- #1882 (check-domain widening a write with no agent id to every live orchestrator claim) → linked
  as related. D removes the leaked orchestrator claims that triggered it; the widening itself
  stays in #1882.
- A mechanical retry limit.
- Clearing FEAT-65's current leaked rows. That registry is also serving a live validate run owned
  by another session.

## Facts I verified (so pm does not re-derive them)
All at 4e8c73c0 unless noted. OMP means the pinned runtime `harness-runtime-lineage-v2` @ d0d1f810.
- **The issue body's hypothesis is refuted.** The extension always sends `harness_runtime: omp`
  and `supervisor_pid` (`.omp/extensions/harness-hooks.ts:960-966`), and dispatch-guard refuses
  with exit 2 without them (`dispatch-guard.py:301-309`).
- **A.**
  - `validate-digest.py --hook` releases by persona alone when the payload lacks a feature or agent
    id (`validate-digest.py:2327`), in the registry of the checkout the validator lives in
    (`:1933-1947`).
  - `tests/integration/test-validate-digest.py` fires the real hook with no root override: T-04
    (`:3621-3638`) as `harness-eng-lead`, T-08 (`:3679-3712`) as `harness-pm`,
    `harness-backend-dev` and `harness-documentor`.
  - A qa PASS re-runs the suite (`:2416`) in the checkout the qa artifact names (`:2120-2123`).
  - Reproduced: a scratch worktree with one live claim per persona kept only `harness-qa` after
    one passing run of `test-validate-digest.py`.
  - Occurrence 4: qa started `run-unit-tests.py --kind integration` in the FEAT-65 worktree at
    13:10:03Z; the pm's writes passed until 13:11:31Z and were refused from 13:11:59Z.
  - Occurrence 2: the pm's writes passed until 13:25:13Z and were refused from 13:30:07Z; qa's
    yield hook started at 13:27:22Z.
- **B.**
  - `FEAT65Plan.CommercialLemming` was dispatched at 22:05:06Z and completed after 49m32s; its
    claim was released on the settled result. `hub send` woke it at 22:57:08Z.
  - OMP fires `before_agent_start` at the start of every run (`session/agent-session.ts:6787`).
    Its result can only inject a message or replace the system prompt
    (`extensions/types.ts:1152-1156`); it cannot stop the run.
- **C.**
  - `harness-hooks.ts:1066-1068` pairs `receipts[i]` with the result row whose `index === i`.
  - Both plan runs leaked the ui-reviewer from a `[code-reviewer, fable-advisor, ui-reviewer]`
    batch: FEAT-65 `…CommercialLemming.HugeBass` and FEAT-64 `…TremendousDragon.WickedRaven`.
  - OMP names a child `${parentId}.${name}` and appends `-2` on a repeated name
    (`task/output-manager.ts:84-91`). A claim pre-bound to `Scope` refuses the real child
    `Lead.Scope` (reproduced with the registry library).
- **D.**
  - `pi.on("task:subagent:lifecycle")` (`harness-hooks.ts:1216`) is never called: OMP calls `pi.on`
    handlers only for its typed events (`extensions/types.ts:1238-1298`), and the lifecycle
    channel lives on `pi.events` (`extensions/loader.ts:196`).
  - The unit test calls the handler from a fake map (`tests/unit/omp-hooks.test.ts:608`), and
    `check-omp-port.py:175` only checks that the string is present.
- **E.**
  - dispatch-guard writes claims to the feature worktree's registry (`dispatch-guard.py:225-236`).
    validate-digest releases and checks live children in the owner checkout's registry
    (`validate-digest.py:2296`).
  - On 2026-09-24 the main checkout's registry was empty and the FEAT-65 worktree's held 9 rows.
- **The second-pm refusal was sequential work, not concurrent spawns.** The c0 goal-check pm
  finished at 03:08Z. `FEAT64PmEvidence`, dispatched at 12:55:29Z to amend the plan, was refused by
  the one-pm rule because of the first pm's hand-bound row (created 02:58:05Z). Re-dispatched after
  a manual release, it ran in 3m28s.
- **Tools.** No governed persona holds `eval`; only orchestrators and leads hold `task`
  (`.omp/agents/harness-*.md`).
- **Runtime identity.** Every extension context carries `agentId`/`parentAgentId`
  (OMP `extensions/runner.ts:1190-1192`), and the extension refuses a governed write that lacks
  either (`harness-hooks.ts:892-894`).
