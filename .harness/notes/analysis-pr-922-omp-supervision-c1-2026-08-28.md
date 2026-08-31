# Review panel — PR #922 "Add long-running OMP Harness supervision" — cycle 1

- **review_sha:** `fee9d5fded415ad4a3db13a30958a4730f9ff61d` (base `7ccfae8dd7644bc3aaea612dabf4317c0d804f99`)
- **Panel:** code-reviewer, qa, security-reviewer, ui-reviewer · cycle 1 · standalone (no run dir)
- **Spec of record:** PR Summary/Verification + DEC-204. Cycle 0's record: `analysis-pr-922-omp-supervision-2026-08-28.md`

## BLUF

**PASS with notes. The remediation holds, and — the thing this cycle existed to establish — the fixer
was right on all three of its revisions to cycle 0's findings.** F1, F2, F3 and F5 are all **closed**
at source. Cycle 0's central adequacy finding (a green suite coexisting with two high bugs) is
**materially closed**: qa independently reproduced red-then-green for the eight named new cases rather
than accepting the fixer's assertion. `must_fix` is empty; `severity_max: med`. Under
`gates.review: advisory_unless_high` (`.harness/harness.json`) this does not gate the ship.

**Cycle 0's own severity reconciliation on F3 was wrong, and I made that call.** Recorded below.

## Per-finding verdicts

| id | c0 | c1 verdict | evidence |
|---|---|---|---|
| F1 fail-open inversion | high | **closed** | `cc9e5cf`; every `dispatch-guard.sh` exit-0 pass-through now passes through under the TS caller, incl. the internal-exception and non-`harness-` branches; pinned by a test that fails on the unfixed code (code-reviewer) |
| F2 unbounded capture | high | **closed** | `harness-hooks.ts:443-447` — `featureCaptured` one-shot latch **and** `role !== "user"` filter; `messageText:379-390` extracts only `part.text`, so a `tool_result` part yields `""`. Two independent guards, either sufficient |
| F3 PID reuse | med → **high** | **closed** | `_omp_claim_live:159-178` keys identity on `(pid, start_time)`, never the pid alone; `supervisor_started_at` pinned at claim time (`:342`) |
| F5 release selectors | low | **closed as to its scenario** | `release_cmd:476-486` now unconditionally emits `--feature`; the agent-only selector can no longer be printed |

**F4 not re-litigated** — split to issue #923, out of scope by dispatch.

## The three contested revisions — adjudicated at source by the lead, not taken from the fixer

1. **F2's diagnosis correction is CORRECT.** The assignment arrives as `role: "user"`; filtering to
   `assistant` would have broken capture outright while looking like a fix. `lastAssistantText:392-405`
   is a *separate* function on a different path — cycle 0 read the `assistant` filter there and
   attributed it to the capture path. The real exposure was `toolResult`, and it is closed twice over.
   Residual: full certainty about the host's message schema needs live OMP telemetry (code Q1,
   security Q1) — non-blocking, because the one-shot latch holds independently of the role filter.
2. **F3's re-rating to high is CORRECT; cycle 0's `med` was the error.** Verified both halves myself.
   (a) `validate-digest.py:977-1008` calls the same `live_children`/`_expire` and `return 2`s a return
   with non-empty children — so the blast radius was never single-flight's one persona
   (`SINGLE_FLIGHT_AGENTS == ("harness-pm",)`); it is **every lead and the orchestrator**. *The fixer's
   wording "for every persona" overstates it — the gate is `norm(agent) in ("lead","orchestrator")` —
   but the substance of the re-rating stands.* (b) `reconcile` (`:465-485`) calls `_expire` per claim and
   therefore **keeps** a claim that predicate calls live: the fixer is right that reconcile cannot clear
   it. Cycle 0's "it self-heals" is literally true only on the *recycler's* exit, which may never come
   within a run. **Cycle 0 under-rated F3 by scoping impact to the one consumer it examined.**
3. **F5's downgrade is CORRECT as to the misleading-remedy scenario, but its stated premise is FALSE.**
   Both production callers do pass `feature` (`dispatch-guard.sh:156` `feature=declared`, guaranteed by
   the guard's own missing-marker refusal; `validate-digest.py:1001` `feature=_c.get("feature")`). But
   "a claim always carries one" is contradicted by the codebase itself — `LEGACY_FEATURE = "legacy"`
   and `refusal_lines`' `existing.get('feature', LEGACY_FEATURE)` both exist for featureless claims. On
   such a claim `release_cmd` now raises in `shlex.quote(None)`, caught by the enclosing
   `except Exception` at `validate-digest.py:1005-1007`. Effect: a refusal with **no** remedy instead of
   a **misleading** one. Strictly better, still a gap. Folded into N3.

## Findings — ranked. `must_fix` is empty; all four are advisory

Ranked by irreversibility before severity, then by whether one remedy subsumes another.

**N1 · med · code-reviewer.** `_read_process_start_time:147-155` — the macOS `ps -o lstart=` branch
parses with `time.strptime("%a %b %d %H:%M:%S %Y")`. `ps` honours the inherited `LC_TIME`; Python's
`strptime` uses the C locale unless `setlocale` was called. Under a non-English `LC_TIME` the parse
raises, `_process_start_time` returns `None`, and **every** OMP claim on that host silently falls to the
`OMP_UNVERIFIED_TTL_SECONDS` backstop — F3's fix becomes inert and DEC-204's "live for any age" becomes
"live for 24 hours". Not high: the observed ceiling is a 7,200 s leaf run, so no real run is cut short,
and the common `en_US.UTF-8` case parses correctly. Remedy: pin `LC_ALL=C` on the `ps` invocation
(code Q2). Ranked first because it silently disables the very fix this cycle is verifying, on this
project's own platform.

**N2 · med · security-reviewer (re-rated by lead out of `must_fix`; security concurred).**
`_omp_claim_live:174-175` — `_is_number` admits `NaN`/`Infinity`, then `int(recorded)` raises. Every
caller's broad `except Exception` fails **open**, and the state is self-perpetuating: `reconcile` asks
the same question, so the pruning write never completes and the entry can never self-clear.
`json.loads` accepts bare `NaN`/`Infinity`, so the existing corruption guard (`_load:54-59`, which
catches `JSONDecodeError`) does not cover it. **Decided, not averaged — security rated this `must_fix`,
I did not.** The registry is already a fully trusted, same-user file: anyone able to write `NaN` can
instead write a forged claim with a live pid and a matching `supervisor_started_at`, defeating the same
gates with no crash and no trace. Security checked this against its own PoC and concurred, adding that
the crash path is *strictly worse* for an attacker — it only ever fails open and prints a stderr
diagnostic, where editing a claim field achieves the identical outcome silently. Not a boundary
violation. What survives is the corruption angle: ordinary bad data reaching a durable, reconcile-proof
fail-open in a system built for unattended multi-hour runs — which is what keeps it at `med` rather than
`low`. Remedy (security's, adopted): `math.isfinite` inside `_is_number`, i.e. **everywhere** that
predicate gates a conversion, not only `supervisor_started_at`.

**N3 · low · lead (from security's F5 verification).** `release_cmd(root, agent, feature)` raises on a
featureless claim (see revision 3 above). Contained, remedy-degrading not remedy-misleading. Fix
alongside N2 — same file, same defensive pass.

**N4 · low · code-reviewer.** Narrow TOCTOU between `_pid_alive` and the start-time read in
`_omp_claim_live`. Bounded; recorded, not actioned.

## Assessed and dismissed — nothing dropped silently

- **`_START_TIME_CACHE` staleness.** Module-level dict, no eviction. Cleared by process exit, and every
  consumer (`dispatch-guard.sh`, `validate-digest.py`, the hook's shell-outs) is a fresh short-lived
  process. No long-lived importer found. Dismissed — but it is one `import inflight_registry` from a
  daemon away from reintroducing exactly the PID-reuse bug F3 fixed. Recorded for that reason.
- **`/proc` parsing.** Field index verified correct: after `rpartition(b")")[2]` the fields start at
  proc(5) field 3, so `tail[19]` is field 22 `starttime`; `rpartition` handles a comm containing `)`;
  a missing `btime` raises `StopIteration` into the `except` and falls through to the `ps` branch;
  `SC_CLK_TCK` is a valid `sysconf` name. Clean.
- **`ps` injection / DoS.** `pid` is validated `int > 0` before argv construction, no `shell=True`,
  `timeout=5`. Clean (security concurs).
- **DST via `time.mktime(..., tm_isdst=-1)`.** The absolute value can be off by an hour in the fold, but
  both the write and the read use the same deterministic function, so the equality comparison is
  unaffected. Not a defect.
- **The 24h backstop becoming a general TTL.** Traced every path: `_omp_claim_live` reaches it **only**
  when `recorded` or `current` is non-numeric. With identity proven it returns exact equality with no
  TTL. DEC-204's long-run guarantee is intact — except on a host that cannot report start time at all,
  which is N1's territory.
- **ui-reviewer** scoped out on a census confirming neither fix commit added a user-facing surface and
  no `DESIGN.md` governs the diff. Correct, and measured rather than predicted.

## Adequacy — what the panel could not tell you

Cycle 0's finding was that every test mocked the seam the bugs lived in. **qa independently reproduced
red-then-green for the eight new cases against the pre-fix source** rather than accepting the claim, and
found none that passes for a reason other than the fix. That is the discriminator cycle 0 lacked, and it
is why this cycle's PASS means something the last green suite did not.

Two gaps survived two fix passes, both real and both narrow:
1. No hook-level (`harness-hooks.ts`) test of cross-feature isolation under a dead/recycled PID — cycle
   0's Q1, untouched by either fix commit.
2. `validate-digest.py`'s held-child gate has no end-to-end test with a real OMP claim; only
   `live_children` is covered in isolation. This is the consumer that F3's re-rating turns on, and it is
   the one the panel proved matters most.

Unaudited: the registry suite grew **88 → 97 (+9)**, but only four registry cases were named to the
panel. The other five were not individually audited for red-then-green. Not alarming; recorded because
the arithmetic does not close.

## Fix ordering

N1 and N2/N3 touch the same file and the same defensive pass; land N2+N3 together (both are `_is_number`
/ `release_cmd` hardening), then N1 (`LC_ALL=C`). N4 needs no action.

**Routing constraint (DEC-174):** every remedy edits `inflight_registry.py`, an enforcement-layer file.
None may be executed by a harness agent fix loop — main-session or human only. None of them gates this PR.

## Open questions

- **Q1** (code, security; non-blocking): confirming the OMP host tags the assignment `role: "user"` and
  tool results otherwise needs live telemetry outside this repo. Non-blocking only because the one-shot
  latch covers F2 independently; re-check if the host's message schema changes.
- **Q2** (code; non-blocking): pin `LC_ALL=C` on the `ps` read to remove N1 outright?
- **Q3** (qa; non-blocking): close the two coverage gaps above in a follow-up?
- **Q4** (qa; **action needed by the main session**): qa left a disposable scratch worktree at
  `.claude/worktrees/harness/qa-c1-scratch-pr922` (clean, detached at `66e9a9d`). It must be removed
  **from outside itself** — not qa's to run, and not mine.
