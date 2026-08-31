# QA gate audit — PR #922 (`7ccfae8..66e9a9d`), cycle 0

**Verdict: matrix satisfied and every named suite reproduces the PR's claimed counts exactly.
One real coverage gap: no test exercises the hook-level (`harness-hooks.ts`) crash-reconciliation
path, only the `inflight_registry.py` unit level does — and the PR's Verification bullet doesn't
distinguish the two layers.** Gate-only audit; nothing authored, nothing fixed. All commands run
from the clean worktree at the pinned SHA.

## Suite table — command run, actual vs. claimed

| Suite (PR claim) | Command | Result | Observed | PR claim | Match |
|---|---|---|---|---|---|
| OMP hook tests (20) | `python3 .claude/skills/harness/bin/test-omp-hooks.py` (bun test, absolute path — relative path fails, see note) | pass | 20 pass / 0 fail | 20 passed | ✅ |
| inflight registry checks (88) | `python3 .agents/skills/harness/bin/test-inflight-registry.py` | pass | 88/88 | 88 passed | ✅ |
| dispatch guard checks (42) | `python3 .agents/skills/harness/bin/test-dispatch-guard.py` | pass | 42/42 | 42 passed | ✅ |
| Full unit suite | `.agents/skills/harness/bin/run-unit-tests.sh --kind unit` | pass | exit 0, every registered script `ALL PASS`/`N/N cases passed`, no failures | "passed" | ✅ |
| Full integration suite (superset incl. the two above, run via the standing harness) | `.agents/skills/harness/bin/run-unit-tests.sh --kind integration` | pass | exit 0, 27/27 registered scripts pass, incl. `88/88` and `42/42` inline | "passed" | ✅ — 3rd attempt; see note |
| Adapter drift check | `python3 .agents/skills/harness/bin/sync-agent-adapters.py --check` | pass | exit 0, silent (no drift) | "passed" | ✅ |
| OMP port check | `python3 .claude/skills/harness/bin/check-omp-port.py` + `test-check-omp-port.py` | pass | `OMP port surface: ok`; 17/17 and 18/18 cases | "passed" | ✅ |
| Canonical state checker | `.claude/skills/harness/bin/check-state.sh` | pass | exit 0, output is all `note`-level pre-existing housekeeping items (unrelated STATE.md/glossary findings, none touching this diff) | "passed" | ✅ |

**Note on the integration suite:** standalone invocation is genuinely slow in this sandbox
(`test-check-domain.py` alone ran 2–5 min); two earlier attempts were killed by an outer `timeout`
wrapper before completing (recorded as `did-not-run` at the time — not silently dropped). A third
attempt with the tool's native 900s bound completed clean, `EXIT:0`, all 27 integration scripts
passing, with the two PR-named counts reproduced inline (`88/88`, `42/42`). No perturbation was
needed to trust this — direct standalone runs of the two named scripts (rows above) already matched
exactly before the full-suite run confirmed the same numbers a second, independent way.

**Count audit verdict: 20 / 88 / 42 all match exactly.** No inflation, no undercount, in either
direction.

## Adequacy audit — the substantive half

### Crash reconciliation — YES, at the `inflight_registry.py` unit level
`test-inflight-registry.py:614-634` (`case_20_reconcile_only_target_feature`): spawns a **real**
subprocess, records it as `supervisor_pid` on two claims (features A and B), kills it
(`proc.terminate(); proc.wait()`), then calls `reconcile(root, feature="FEAT-43-alpha")` and asserts
`removed == 1`. This is genuine crash reconciliation against a real dead PID, not a mocked liveness
check.

### Cross-feature claim isolation — YES, and it is the *harder* version of the test
Same case (`test-inflight-registry.py:630-634`): **both** features' claims share the identical dead
`supervisor_pid`. `reconcile(..., feature="FEAT-43-alpha")` is asserted to leave FEAT-44-beta's claim
in the registry (`features == ["FEAT-44-beta"]`) even though B's claim is *also* expired — this
proves the `feature` parameter in `inflight_registry.reconcile()` (`inflight_registry.py:368-392`)
actually filters, rather than the test being satisfiable merely because B's claim was alive. A live-B
variant would pass trivially through the `expired` check alone and prove nothing about the filter;
this variant does not have that escape hatch. `case_21` (`:637-659`) repeats the same shape for the
read-path (`live_claim`) instead of the write-path (`reconcile`).

### Gap: the hook layer (`harness-hooks.ts`) never exercises either scenario
`omp-hooks.test.ts:206-213` asserts only that `before_agent_start` **calls**
`inflight_registry.py reconcile --feature FEAT-43-long-run` — the test's own mock runner for
`inflight_registry.py` (`omp-hooks.test.ts:135-172`) doesn't implement `reconcile` at all, so the
assertion is "the hook shells out with this argv," never "reconciliation actually reclaimed a dead
claim without touching a sibling feature." The PR's Verification bullet 3 ("crash/resume recovery:
dead supervisor reconciled and the checkpointed step completed without releasing another feature's
claim") is worded at the hook/supervision layer, but the only test that proves the *mechanism*
(dead-PID detection + feature-scoped removal) lives one layer down, in the registry's own unit
tests, never wired through the hook's dispatch path in a test. This is a real, if narrow, gap: it
means a future change to how `harness-hooks.ts` invokes `reconcile` (wrong flag, wrong feature
variable, wrong exit-code handling) would not be caught by any test named in this PR, only by the
registry-level test which doesn't touch the hook at all. **Needed assertion:** a hook-level test
that seeds the mock registry with two features' claims under one dead PID, drives
`before_agent_start`/`message_end` for feature A, and asserts B's claim is still present afterward.

### Hook error/rejection-path coverage — YES, and it is exercised, not just success paths
`omp-hooks.test.ts:206-232` (`"blocks a whole batch and rolls back earlier claims"`) drives a
`dispatch-guard.sh` **denial** (`task === "deny"` → `{blocked: true, reason: "denied"}`) inside a
batch where an earlier task already claimed successfully, and asserts (a) the whole batch is blocked
with the denial reason surfaced, and (b) the earlier successful claim is rolled back
(`inflight_registry.py release --claim-id claim-1` is asserted present in the call log). This is a
genuine rejection-path test with rollback verification, not merely "the deny path returns
non-2xx." `dispatch-guard.sh`'s own suite covers refusal paths independently: `case_11` (missing
`HARNESS-FEATURE` line refused, stderr names the field), `case_13` (malformed flow id refused), and
`case_14` (duplicate pm claim for one feature refused) — all pre-existing-shape cases extended by
this diff, all asserting a distinguishing string alongside the exit code (per the file's own T-08
convention at `test-dispatch-guard.py:9-11`, avoiding the crash-exits-nonzero-too trap).

## Test-matrix gate

Change type inferred: **`cross_module`** — the diff moves one behavior (feature-scoped, PID-aware
claims) through five interacting layers in the same commit: the registry primitive
(`inflight_registry.py`), the dispatch-time enforcer (`dispatch-guard.sh`), the OMP hook adapter
(`harness-hooks.ts`), the digest-safety gate (`validate-digest.py`), and seven further gate scripts
touched to carry the new claim shape through. No single-module change_type fits; `cross_module` is
the correct and only per-project entry matching this shape (`.harness/harness.json:22-27`).

| Kind | Required by `cross_module`? | State | Evidence |
|---|---|---|---|
| `unit` | always | **satisfied** | `run-unit-tests.sh --kind unit` exit 0, all scripts pass (table above) |
| `integration` | always | **satisfied** | `run-unit-tests.sh --kind integration` exit 0, 27/27 scripts pass, incl. the two PR-named counts reproduced inline (table above) |

Both required kinds are `status: active` in `.harness/harness.json:104-123` with real, executed
`cmd`s (not `null`) — neither is `misconfigured` or `not applicable`. No `when` clause applies to
`cross_module` (it has none defined). No kind was inferred beyond the floor: `ui`/`component`/`eval`
are `unresolved`/not applicable to a hooks-and-scripts change with no browser or model-behavior
surface, and I found no diff content warranting an addition to the floor.

**`matrix_ok: true`.**

## Non-findings (already ruled, not re-raised)
BRIEF/plan absence, dirty main checkout, the `@deep`/`@strong` role aliases, and the two live timing
claims (7,200.07s / 900.06s) — treated as asserted, unreproducible evidence per the dispatch.

## Open questions
- The hook-layer crash-reconciliation gap above (Q1) is a coverage finding for the eng-lead/dev
  team to close, not something this gate can fix — it does not, by itself, fail the gate, since the
  matrix floor (`unit`+`integration`) is met and the mechanism itself IS proven at the registry
  layer. Flagging per DEC-169's spirit: an "it was reconciled" claim without a hook-level assertion
  of the isolation property is the same class of gap as an absence-only assertion.
