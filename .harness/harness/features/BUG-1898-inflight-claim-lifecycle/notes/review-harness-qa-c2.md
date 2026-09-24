# QA gate — BUG-1898 c2

**BLUF: FAIL.** The configured unit and integration matrix passes at `4942950a83c1895d85922f7cd9e9cfd41e28daf8`, and the wrapper is now per-run unique, drives the pinned real suite, preserves every seeded governed-persona sentinel, and reaches its persona-release mutant. However, its mutation oracle accepts *any* nonzero suite exit containing at least one `[bug1898]` line; it does not prove the required exact result—79/81 with exactly the two parent-settlement `[bug1898]` failures—or reject additional `[bug1898]` failures masked by known relocated-config schema failures. F-QA-01 remains active.

## Scope and matrix

- Reviewed pin: `4942950a83c1895d85922f7cd9e9cfd41e28daf8`.
- Canonical merge-base: `a4d72e7fc91d0cf7a568d9e2a5225465a422170e` (`git merge-base origin/main <pin>`).
- Focused c2 delta: `81dbd81d21b04b6fdcba2435d2e73a12ec72fd2e..4942950a83c1895d85922f7cd9e9cfd41e28daf8`: `validate-digest.py` and `test-suite-claim-preservation.py` plus feature records/review notes.
- Full pinned range includes cross-module runtime changes, bugfix runtime code, and config shape. The configured floor is `unit` plus `integration`; both were run and passed. `inflight_claim_lifecycle_live` is locally-run and remains SC-07's operator gate, not a panel failure.

| kind | command | result |
|---|---|---|
| unit | `env -u HARNESS_AGENT_TYPE .claude/skills/harness/bin/run-unit-tests.py --kind unit` | exit 0; 42/42 discovered files reported `PASS` (complete per-file runner verdicts: `artifact://659`; summary at lines 1847-1849). |
| integration | `env -u HARNESS_AGENT_TYPE .claude/skills/harness/bin/run-unit-tests.py --kind integration` | exit 0; 70/70 files reported `PASS`, including `test-suite-claim-preservation.py` (complete runner receipt: `artifact://707`; summary in completion receipt). |
| inflight_claim_lifecycle_live | not run | locally-run SC-07; `notes/live-omp-probe.md` remains without a live receipt. Pending operator gate by constraint. |

`matrix_ok: true`; configured typecheck has no executable runner as declared in BRIEF.md and is not a matrix requirement.

## Preservation and mutation evidence

`python3 tests/integration/test-suite-claim-preservation.py` exited 0 independently and printed all four PASS rows. The green arm enumerates every `harness-*.md` persona from the checkout registry, creates a live row per persona, binds a PID-qualified runtime id and feature, invokes the real pinned `tests/integration/test-validate-digest.py`, requires its exit 0, and compares the selected rows byte-for-byte after the suite (`test-suite-claim-preservation.py:57-97`).

The mutation arm copies the bin directory, redirects `VALIDATE_DIGEST_BIN` to that copied real validator, and overrides `inflight_registry.release` to omit `agent_id`—the pre-BUG-1898 persona selector (`:100-112`, `:33-42`). It reached a nonzero suite result with `[bug1898]` failure output, so this is a genuine discriminator for a persona-wide release, not the prior disconnected-registry check.

It is not a complete discriminator required for F-QA-01 closure: the oracle is only `code != 0 and reddened`, where `reddened` is any line beginning `FAIL  [bug1898]` (`:106-110`). It neither checks `79/81`, exactly two target parent-settlement failures, nor excludes additional `[bug1898]` failures; known unrelated relocated-config schema failures can coexist without attribution. It does reject a generic crash with no `[bug1898]` line, but a generic/unrelated red plus one accidental `[bug1898]` line passes. Thus the requested exact mutant count and crash-discrimination proof are absent.

## Findings

- **F-QA-01 — active**; kind: substance; severity: high; reader: harness-qa + harness-pm; owner: T-03/T-04. Scenario: a future validator change produces an unrelated relocated-config failure and one incidental `[bug1898]` failure while failing more or different BUG-1898 cases than the intended two parent-settlement checks. The wrapper's `code != 0 and reddened` condition passes, reporting its persona-release mutant healthy even though the expected behavioral signature is absent. Require the wrapper to assert the complete target BUG-1898 result/count and separately classify the known relocated-config schema failures.
- **F-01 — closed**; kind: substance; severity: high; reader: harness-code-reviewer; owner: T-03. Current source strict-reads both own and child claims before release and routes unreadable state to a no-write BLOCKED-only parent refusal (`validate-digest.py:2290-2340`). The current real suite's BUG-1898 cases require parent refusal, BLOCKED escape, leaf pass-through, and corrupt-byte preservation (`test-validate-digest.py:5850-5877`); it ran green inside the c2 wrapper and integration matrix. No regression observed.

## Automated SC evidence and fail-first

| SC | pin evidence | fail-first evidence |
|---|---|---|
| SC-01 | `tests/integration/test-validate-digest.py:5712-5760`; c2 preservation wrapper green/mutant arms | `notes/review-harness-qa-c0.md:23` (`artifact://365:243-391`); c2 mutant is additional but incomplete signature proof |
| SC-02 | `tests/unit/omp-hooks.test.ts:1875-2001` in passing unit matrix | `notes/review-harness-qa-c0.md:24` (`artifact://362`) |
| SC-03 | `tests/integration/test-inflight-registry.py:1238-1410` in passing integration matrix | `notes/review-harness-qa-c0.md:25` |
| SC-04 | `tests/unit/omp-hooks.test.ts:2003-2113` in passing unit matrix | `notes/review-harness-qa-c0.md:26` (`artifact://362`) |
| SC-05 | `tests/integration/test-check-omp-port.py:194-214` in passing integration matrix | `notes/review-harness-qa-c0.md:27` |
| SC-06 | `tests/integration/test-validate-digest.py:5769-5877` in passing integration matrix | `notes/review-harness-qa-c0.md:28` (`artifact://365:378-391`) |

SC-07 is `pending_operator_gate`; it was not run and no receipt was fabricated. SC-08 is inspection-only and outside this test gate.

## Coverage gaps

- The permanent mutation wrapper does not pin the exact 79/81 and two `[bug1898]` parent-settlement signature or distinguish it from relocated-config schema failures; this is F-QA-01.
- BRIEF.md records the non-gating typecheck-runner gap for the TypeScript hook.

## Scratch disposition

No scratch worktree was created; none requires removal.

## Principles applied

- **Build the Lever** — used the configured per-kind runners and the repository's deterministic wrapper rather than hand-inspecting claim rows.
