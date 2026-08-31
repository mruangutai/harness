# Review panel — PR #922 "Add long-running OMP Harness supervision"

- **review_sha:** `66e9a9d64ec79d30ef43ea3e96aa8f0737ae8681` (base `7ccfae8dd7644bc3aaea612dabf4317c0d804f99`)
- **Panel:** code-reviewer, qa, security-reviewer, ui-reviewer · cycle 0 · standalone (no run dir)
- **Spec of record:** PR body Summary/Verification + DEC-204 (the diff's single new decision, `DECISIONS.md:7318+`)

## BLUF

**FAIL — two high-severity defects, both in `.omp/extensions/harness-hooks.ts`, both invisible to the
green test suite.** The design in DEC-204 is sound and the registry core is genuinely well tested
(qa reproduced 20/88/42 exactly; matrix_ok true; crash reconciliation and cross-feature isolation are
proven with a real killed PID at `test-inflight-registry.py:614-659`). The defects are in the OMP
adapter layer, where every test mocks the seam the bugs live in.

Both high findings are in the same file and same function; one focused pass fixes them.

## Ranked findings

**F1 · high · must_fix · code-reviewer (verified at source by lead)**
The OMP caller inverts `dispatch-guard.sh`'s fail-open contract into fail-closed.
The guard's every pass-through exits 0 *without* printing a claim receipt — `dispatch-guard.sh:34`
(unreadable payload, "passing through"), `:38` (non-harness agent), `:72`, `:112`, `:138`, `:145`,
`:187` (internal exception, "not blocked"). `harness-hooks.ts:~522-527` treats *no receipt* as a hard
block: `reason = "…returned no claim receipt; the task was not started."`
**Failure scenario:** the guard throws internally mid-run (`:187` — the branch fail-open exists to
survive). Designed behaviour: let the dispatch through. Actual behaviour under OMP: the dispatch is
refused, halting the multi-hour unattended run this PR exists to enable. Also blocks every dispatch of
a non-`harness-` subagent (`:72`). Contradicts DEC-100 ("only exit 2 blocks").

**F2 · high · must_fix · security-reviewer (raised from med by lead; verified at source)**
`HARNESS-FEATURE` capture is unbounded in both time and role, contradicting DEC-204's stated mechanism
("The extension captures that message before the first tool call").
`harness-hooks.ts:468` and `:477` call `setFeature(detectHarnessFeature([messageText(candidate)]))` on
*every* `message_update`/`message_end`. `messageText` (`:379`) does not filter role; `FEATURE_MARKER`
(`:6`) is `/…/gm`, matching any line anywhere. `setFeature` throws on mismatch (`:419-420`) from inside
an `async pi.on` handler. The one-shot guard pattern already exists in the same function
(`expertiseInjected`, `:412`) and was not applied here.
**Failure scenario (no attacker required):** an agent working feature A reads feature B's stored
dispatch or notes — routine harness work. The tool-result message carries a valid
`HARNESS-FEATURE: FEAT-NN-slug` line → uncaught throw in an async handler, mid-long-run. Secondary
path: if a foreign marker is captured *first*, `setFeature` fires `reconcile --feature <wrong>`
(`:423-429`) against another feature's claims.

**F3 · med · code-reviewer + security-reviewer (contradiction resolved by lead)**
PID reuse defeats OMP crash reconciliation. `_pid_alive` (`inflight_registry.py:96-107`) is a bare
`os.kill(pid,0)`; OMP claims carry no TTL fallback by design. A recycled supervisor PID makes a dead
claim look live, stalling single-flight for that `(feature, persona)`.
**Severity decided, not averaged.** code-reviewer rated high/must_fix; security rated it mitigated.
I rate **med**: DEC-204 deliberately signs PID-only liveness ("live for any age while its recorded
supervisor PID exists"), security's `_matches` analysis is correct that there is no authorization
bypass (feature+agent strings still must match), it self-heals when the recycled PID exits, and the
documented targeted-release command is a real remedy. A recoverable availability stall with an operator
remedy is not a ship blocker. Fix by recording process start time beside `supervisor_pid`.

**F4 · med · scope + regression · code-reviewer**
`.claude/skills/harness/SKILL.md:52-56` rewrites the orchestrator context-budget advisory to depend on
an "OMP context signal" implemented nowhere in this diff; its test
(`test-orchestrator-playbook.py case4_host_neutral_context_signal`) only asserts wording. Effect:
DEC-198's signed advisory is silently inert under the canonical host. No Summary bullet or DEC-204
sentence asks for this — scope leakage *and* a regression of a signed decision. Resolve Q2 first.

**F5 · low · security-reviewer + lead (same seam, merged)**
Claim release via CLI selectors carries no binding to the caller's identity. `release --agent X
--feature <sibling>` defeats a concurrent feature's single-flight; `release_cmd`
(`inflight_registry.py:395-406`) omits `--feature` when it is `None`, so a printed agent-only remedy can
release another feature's single matching claim. Bounded: same-user/same-machine, already-trusted
process, and `release()` refuses when matches != 1.

## Assessed and dismissed — nothing dropped silently

- **D1 — "dispatch-guard fails open on every branch."** Not a defect: fail-open is the intended posture
  (DEC-100). Only the *inversion* (F1) is a defect.
- **D2 — `_all_live`/`list` globally expires and persists across all features** (`:439-448`), sitting
  awkwardly beside DEC-204's "expiry is query-scoped". Dismissed as non-blocking: the swept claims are
  already dead by the same predicate, `list` is an explicit operator command, and targeted reconcile
  demonstrably preserves siblings. Recorded because it is the closest counter-example to the
  query-scoped invariant, and an edit here could make it live.
- **D3 — "`blocking: true` added to all 15 agents."** The brief is wrong: measured **14 of 15**.
  `harness-orchestrator.md` carries no `blocking:` key — which is precisely what preserves the async
  main→orchestrator edge. Summary bullet 3 is **supported**. Not a defect; count corrected.
- **D4 — the 7,200.07s / 900.06s hierarchy runs.** Out of scope by dispatch; recorded as asserted live-run
  evidence, unreproduced by this panel.
- **D5 — qa's hook-layer coverage gap.** Real but not independently blocking: the mechanism *is* proven at
  unit level. Folded into adequacy below rather than `must_fix`.
- **ui-reviewer** scoped out on a measured 0/48 extension census, no DESIGN.md governs the diff. Correct.

## Adequacy — the panel's green gate does not mean these were tested

The blocking gate passed (qa: matrix_ok true, 27/27 integration, all seven named suites run, counts
20/88/42 exact) **and neither high finding is catchable by any test in this diff.** That is not a
contradiction; it is a coverage boundary. F1 is invisible because `omp-hooks.test.ts:206-213` mocks the
policy runner, so no test ever executes the real guard's exit-0 paths against the TS caller. F2 is
invisible because the hook fixture supplies one clean assignment message, so no test supplies a second,
conflicting, or late marker. Every test that could fail on these mocks the seam where they live.

## Fix ordering — remedies interact

1. **F2** first: the capture-once fix changes `setFeature`, which also gates the reconcile call in F3's
   neighbourhood, narrowing F3's trigger surface.
2. **F1** next — same file, same `task` branch; land in the same pass to avoid two edits to one hunk.
3. **F3** — adds a field to the claim schema; land after the hook-layer fixes settle.
4. **F4** — answer Q2 before touching it; the answer decides revert vs implement.
5. **F5** — an ownership token is a registry-schema change; bundle with F3.

**Routing constraint (DEC-174):** every remedy above edits an enforcement-layer file
(`harness-hooks.ts`, `inflight_registry.py`, `dispatch-guard.sh`). These must not be executed by a
harness agent fix loop — the fix is main-session/human-executed.

## Open questions

- **Q1** (code-reviewer, non-blocking): was PID reuse considered and accepted for DEC-204, or should an
  OMP claim record process start time to disambiguate a recycled PID?
- **Q2** (code-reviewer, blocking): does an OMP-side context/token signal exist that this diff simply
  did not wire up, or does `SKILL.md` now describe a capability no host provides?
- **Q3** (security, non-blocking; **no longer gates F2**): does an uncaught throw from an `async pi.on`
  handler abort one hook call or the supervised session? F2 is high either way — under the benign answer
  the spec divergence and the wrong-feature-reconcile window remain.
