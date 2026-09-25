# Code review — BUG-1898 c4

PASS. The two-stage review of canonical range `a4d72e7fc91d0cf7a568d9e2a5225465a422170e..f73c999482fd931021a3eb50d30aa8ab2a885283`, with focused comparison `6bfc21e3ccdf78eb86cdd0eb250067348d887096..f73c999482fd931021a3eb50d30aa8ab2a885283`, finds no spec violation or code-quality defect.

## Stage 1 — spec compliance

The c4 hook delta serves SC-02/T-02: one `openRun` path resets the gate to `unready`, performs exact-id `startRun`, and publishes only `ready` or a cause-bearing `held` state (`.omp/extensions/harness-hooks.ts:906-913`). `before_agent_start` reuses it (`:927-941`); `agent_end` resets the gate even when a turn ends without yield (`:1338-1348`); and `agent_start` reopens only when a governed session exists and its gate is not already ready (`:975-985`). Thus an ordinary first turn is untouched, a no-yield turn safely reuses its still-live exact claim, a settled turn recreates its released exact-id claim, and a previously held turn retries rather than writing through stale readiness. Main has no `currentAgent`, so the handler is inert. The unit cases drive the actual wake signal—`agent_start` without a second `before_agent_start`—and separately prove that a post-`agent_end` write is blocked before reclaim (`tests/unit/omp-hooks.test.ts:1889-1931`).

The T-04 corrections match SC-04/SC-07: S3 nests `harness-eng-lead` and supplies a lead-shaped digest (`tests/manual/probe-inflight-claim-lifecycle.py:77-99,393-411`); plain ids exclude every `harness-*` persona (`:424-428`); S2 starts sampling only after wake initiation (`:367-390`); the driver waits for `get_state.isStreaming == false` and sends prompts with `streamingBehavior: followUp` (`:285-302`); and nested lineage is observed through sampled claims in addition to Main-visible children (`:413-422`). SC-07 is confirmed solely from the final live receipt: PASS 29/29, real feature-worktree cwd, S2 exact-id sampled ownership and write, `Scope-2`, `Nest.Probe`, lead lifecycle, byte-identical suite sentinel, and empty before/after registry (`notes/live-omp-probe.md:524-565,583-715`). Earlier failed runs remain preserved.

SC-01–SC-06 and SC-08 were already clean at the prior pin and the focused c4 delta does not weaken them. The seq-3 handoff's late succession under INV-43 is a residual ledger defect only: it predates the c4 live gate, does not alter executable behavior or immutable receipt evidence, and is neither a code finding nor a blocker.

## Stage 2 — code quality

The shared opener prevents divergence between initial and wake claim semantics. The reset-before-claim ordering is fail-closed: while reclaim executes, tool authorization observes `unready`; refusal becomes `held`; and only successful exact-id reclaim becomes `ready`. The needed-only `agent_start` condition avoids duplicate first-turn claims while permitting no-yield, settled, and held resumptions. No silent-write path was found under the supplied OMP ordering premise. The focused unit suite passed 99/99. Canonical Python grading reports 128 passing functions, no grade-2 reasons, and no failures.

The probe's current dry-run correctly returned NOT READY because this validation panel holds live feature claims; it started no OMP session and ran no scenario. This is expected fail-closed prerequisite behavior, not evidence for or against SC-07 and not a finding.

## Dismissed candidates

- **Duplicate claim on first `agent_start`** — dismissed: the preceding `before_agent_start` leaves `runGate=ready`, so the needed-only guard returns.
- **No-yield turn loses ownership** — dismissed: `agent_end` only resets the local gate; exact-id `claim_run_start` reuses the still-live row on the next `agent_start`.
- **Held run writes during retry** — dismissed: `openRun` publishes `unready` before the synchronous claim attempt and `held` on refusal; the existing tool gate blocks both states.
- **Main accidentally claims** — dismissed: Main never establishes `currentAgent`; `agent_start` returns immediately.
- **S2 sampling proves an old claim** — dismissed: the sample index is captured immediately before the wake prompt and only later samples qualify.
- **S3 accepts a non-governed nested id** — dismissed: nested work is a governed eng lead, plain-id collection excludes all `harness-*`, and lineage is obtained from the lead-held claim.
- **INV-43 seq-3 succession** — dismissed as instructed residual ledger defect, with no shipped-code failure scenario.

## Evidence and cleanup

- `bun test tests/unit/omp-hooks.test.ts` — 99 pass, 0 fail, 273 expectations.
- `code-grade.py --base a4d72e7f... --head f73c9994...` — `PASSING: 128`; no failure or reason-required record.
- Live probe was not rerun. `--dry-run` only checked prerequisites and correctly refused active rows.
- No immutable scratch checkout or temporary directory was created; scratch cleanup status: **nothing created, nothing remains**.
- Working-tree dirt is confined to Harness feature metadata/notes; pinned source and tests were inspected via `git show`. No `[harness:human]` commit is in scope.

## Principles applied

None.

```yaml
VERDICT: PASS
DIGEST:
  headline: Exact-pin wake handling is spec-compliant, fail-closed, and supported by the final 29/29 live receipt.
  severity_max: none
  findings: []
  must_fix: []
  spec_violations: []
  code_grade: pass
  reviewed: "a4d72e7fc91d0cf7a568d9e2a5225465a422170e..f73c999482fd931021a3eb50d30aa8ab2a885283"
  human_commits_in_scope: []
  open_questions: []
  files_touched: []
  expertise_update: []
artifact: /Users/molchairuangutai/GitHub/harness/.claude/worktrees/harness/BUG-1898-inflight-claim-lifecycle/.harness/harness/features/BUG-1898-inflight-claim-lifecycle/notes/review-harness-code-reviewer-c4.md
```
