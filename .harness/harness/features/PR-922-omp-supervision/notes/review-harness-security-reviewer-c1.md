# Security re-review — PR #922, cycle 1, `7ccfae8..fee9d5f`

**VERDICT: PASS** — one MED finding in the F3 remediation itself (`fee9d5f`), reproduced with a
runnable PoC, kept as advisory (not `must_fix`) after lead adjudication — see below. F2's diagnosis
correction and F5's downgrade are both CORRECT on inspection. No new findings in the F1/F2 fix commit
(`cc9e5cf`) beyond validating the reviewed fixes.

## Lead adjudication (post-review) — why the NaN finding is advisory, not blocking

Recorded verbatim from `ReReviewPR922`'s adjudication, concurred with after re-checking the reasoning:
the registry (`.harness/.inflight-claims.json`) is an **already-fully-trusted, same-user file** under
this diff's own accepted threat model (F5's actor: "a Bash-capable harness agent already running under
the operator's account, worst case steered by prompt injection," write-reachable per the allow-by-omission
gap at issue #627). Anyone who can write a `NaN` into `supervisor_started_at` can, with the *same* write
access, instead write a **forged claim** — a live pid with a matching `supervisor_started_at`, or simply
an edited/deleted entry — and defeat the identical single-flight/held-child gates with **no crash and no
trace**. Checked this against my own PoC: a crash-based bypass is in fact *strictly worse for an attacker*
than direct forgery, because the crash path only ever produces a fail-*open* result (the gate reports "no
conflict" / "no children"), it prints a diagnostic line to stderr, and direct field-editing achieves the
identical outcome silently and more reliably (e.g. setting `started_at` old enough to trip the ordinary
`CLAIM_TTL_SECONDS` branch, or removing the entry outright — no crash needed). So the NaN path grants this
actor no capability beyond what registry-write access already grants them; it does not cross a privilege
boundary the actor didn't already stand on **(P-02: an actor who already controls a value already holds
the privilege it grants)**.

What survives, and is why this stays a real `med` finding rather than being dismissed: **ordinary,
non-adversarial file corruption** — a race, a partial write, an unrelated bug writing a bad float —
reaches the *same* code path and produces a **durable, self-perpetuating fail-open that `reconcile` can
never clear** (`json.loads` accepts bare `NaN`/`Infinity`; the `JSONDecodeError`/`ValueError` guard in
`_parse:54-59` only catches a malformed *document*, not a well-formed one carrying a non-finite number),
in a system whose entire premise is unattended multi-hour supervision. That reclassifies it as a
**defense-in-depth / reliability gap**, not a boundary violation — `med`, advisory, not `must_fix`.
Remedy is unchanged and still worth doing next pass: `math.isfinite` inside `_is_number`, so it gates
every conversion/comparison this value feeds, not only the one field.

The lead separately verified and adopted my F5 call, folding in one correction as its own low finding:
the fixer's premise "a claim always carries a feature" is not universally true — `LEGACY_FEATURE` and the
defensive `existing.get('feature', LEGACY_FEATURE)` pattern used elsewhere show featureless claims are an
anticipated shape — so `release_cmd` can still raise inside `shlex.quote(None)` for such a claim, caught at
`validate-digest.py:1005-1007` (line anchor per the lead's re-measurement). That is remedy-**degrading**
(the printed remedy is lost, not silently wrong), not remedy-**misleading** (the original bug), so my
downgrade verdict on F5 itself stands — see that section below, unchanged.

## BLUF

The fixer's three revisions to cycle 0's findings all hold up:
- **F2 diagnosis correction: CORRECT.** Tool-result content carries `role: "toolResult"` in this
  host's message schema (`omp-hooks.test.ts:374`), distinct from `"user"` — the role filter does
  exclude it. More importantly, the new `featureCaptured` one-shot latch closes the vulnerability
  structurally even if that role-tagging assumption were ever wrong, since DEC-204 guarantees the
  legitimate assignment is the extension's first observed message.
- **F3 re-rate med→high: CORRECT**, verified at source. `validate-digest.py:969-1008` gates every
  persona's lead/orchestrator yield on `live_children`, not only `SINGLE_FLIGHT_AGENTS`. `reconcile`
  (`inflight_registry.py:449-475`) does ask the same `_expire`/liveness question per claim before
  its `feature` filter is applied, so "it self-heals" was false as stated.
- **F5 downgrade: CORRECT**, verified at both anchors. `dispatch-guard.sh:156` passes
  `feature=declared` (regex-validated non-empty earlier in the same script); `validate-digest.py:1000-1001`
  passes `feature=_c.get("feature")` sourced from a claim record that every legitimate write path
  (`claim_with_receipt`, the v1→v2 migration in `_parse`) sets to a non-empty string. No other
  production caller of `release_cmd` exists (grepped the full tree). The one adversarial edge case —
  a claim missing `feature` via direct registry tampering — makes `release_cmd` raise inside
  `shlex.quote(None)`, which `validate-digest.py:1005-1007` already catches and degrades to "could
  not compose the release command" rather than reproducing the original silent misleading-remedy.

**But the new liveness code itself has an unvalidated-input gap cycle 0 could not have seen, because
it did not exist yet.** `_omp_claim_live` (`inflight_registry.py:159-180`, all new in `fee9d5f`)
converts a registry-supplied `supervisor_started_at` with a bare `int(recorded)`. Python's `json.loads`
accepts the non-standard `NaN`/`Infinity` tokens by default, and `_is_number` (`:181-182`) accepts
them (`isinstance(x, float)` is true for NaN). `int(float('nan'))` raises `ValueError` uncaught inside
`_expire`. Reproduced against the real module (see PoC below): every `live_claim`/`live_children`/
`reconcile` call touching that claim throws. **Per the lead adjudication above, this is advisory —
a reliability/defense-in-depth gap, not a boundary violation, since the actor who could write it already
holds every capability it would grant.**

## PoC (run against the worktree's real `inflight_registry.py`)

Wrote a claim with `"runtime": "omp", "supervisor_pid": <live pid>, "supervisor_started_at": NaN` into
a scratch registry, then called `reg.live_children(...)`:

```
CRASHED: ValueError cannot convert float NaN to integer
```

Traced the blast radius precisely rather than assuming it:
- `live_claim`/`live_children` use `_expire_where(claims, now, predicate)`, which only calls `_expire`
  (and thus `_omp_claim_live`) on claims matching `(agent, feature)` / `(feature, dispatcher)` — so a
  poisoned claim in feature X does **not** crash `live_claim`/`live_children` calls for an unrelated
  feature Y (verified: a call for `"FEAT-01-other"` against a registry poisoned only under
  `"FEAT-99-victim"` returned cleanly). Single-flight and the held-child gate stay intact for every
  *other* feature.
- `reconcile` (`:449-475`) does **not** predicate-filter before calling `_expire` — it loops every
  claim in the registry and calls `_expire([claim_entry], now)` on each, regardless of the requested
  `feature`. A poisoned claim anywhere therefore throws out of `reconcile` for every feature that
  triggers it, not just its own.
- Every caller that reaches this code wraps it in a broad `except Exception` that fails OPEN, matching
  this codebase's DEC-100 posture (`dispatch-guard.sh`'s `except Exception as exc: ... passing
  through, the dispatch is NOT blocked`; `validate-digest.py:983-987`'s `except Exception as _e: _kids
  = []`). `setFeature`'s reconcile call in `harness-hooks.ts:426-430` never inspects the subprocess
  result at all. So the practical effect is not a hard crash of the pipeline — it is **silent,
  durable defeat of enforcement**: (a) for the poisoned claim's own feature, single-flight and the
  held-child gate both fail open, exactly like an absent claim; (b) system-wide, the automatic
  reconcile-on-dispatch sweep silently stops pruning *any* expired claim, for every feature, for as
  long as the poisoned entry exists — and it never expires on its own, because `_expire` never
  completes for it, so the write that would remove it from the registry never happens.

**Threat actor and scenario.** No legitimate write path can produce this value — `_process_start_time`
returns `int(...)` or `None`, never NaN/Infinity, and `time.time()` likewise. This requires direct
tampering with `.harness/.inflight-claims.json` — a real, already-acknowledged surface (F5's threat
model), but per the lead adjudication above, that same write access already grants direct forgery of any
claim field, so this specific mechanism adds no capability an already-Bash-capable actor lacked. What it
*does* add is a corruption-triggerable (not only adversary-triggerable) failure mode.

**Severity: med, advisory (not `must_fix`).** Not `high`: unlike F3 (triggerable passively by ordinary OS
PID reuse, no adversary required), this needs either deliberate tampering (which grants no new privilege,
per adjudication) or organic corruption of a specific field — an unusual precondition either way. Not
`low`: it reproduces the exact failure *class* the F3 fix was just elevated to `high` for (a claim the
liveness check should recognize as dead/questionable instead silently and durably defeats crash
recovery), it is trivially reproducible, and the fix is a one-line finiteness guard (`math.isfinite`) on
every numeric field read from the registry before it is compared or converted, in `_omp_claim_live` and
anywhere else `_is_number` gates an `int()`/arithmetic use. DEC-174 keeps this out of this cycle's fix
loop regardless of gating status; recording it as advisory queues it as a worthwhile hardening item for
the next pass rather than a blocking one.

## The `ps` subprocess (`_read_process_start_time`, item 1 of the dispatch) — clean

- `pid` is guaranteed a plain positive `int` before it reaches the `ps` argv: both `_pid_alive` and
  `_process_start_time` independently guard `isinstance(pid, int) and not isinstance(pid, bool) and
  pid > 0` ahead of any OS call, and `_omp_claim_live` calls `_pid_alive` first, so a non-int or `<=0`
  `supervisor_pid` (including `0`, ruling out the `os.kill(0, 0)` process-group hazard) never reaches
  `_process_start_time`, let alone the argv.
- List-form `subprocess.run(["ps", "-o", "lstart=", "-p", str(pid)], ...)`, no `shell=True` — no
  injection surface regardless of any field's content.
- `timeout=5` bounds the DoS posture of a hung `ps`; per-pid caching (`_START_TIME_CACHE`, dies with
  the CLI invocation per its own comment) means at most one fork per distinct live pid per gate
  invocation, not one per claim.
- `PATH` for this subprocess is inherited from the OMP host process's own environment
  (`harness-hooks.ts:194`, `env: { ...process.env }`, explicitly commented "nothing is added"), not
  from the Bash-tool environment a harness agent controls. A `ps`-shadowing attack would need to
  compromise the host process itself — a materially different, already-assumed-trusted boundary, not
  one this diff introduces or widens. Bare `"ps"` (no absolute path) is a minor defense-in-depth gap,
  info-only.

## `_omp_claim_live` beyond the NaN gap — sound

- Ownership via `os.kill`'s `PermissionError` branch (pre-existing, unchanged): even when a recycled
  pid belongs to a different user and `_pid_alive` fails open to `True`, `_omp_claim_live` still
  compares `supervisor_started_at` against the process's *current* start time — a genuinely different
  process almost never matches, so the identity check catches recycling in this branch too, not just
  same-user recycling.
- Negative/zero/huge pids: excluded before any OS call, as above; a huge pid causes `os.kill` to raise
  `OSError`, caught, treated as dead — no crash.
- `_is_number(started)` in the unverified-fallback branch does **not** share the NaN crash: `now - nan`
  is `nan`, and `nan <= OMP_UNVERIFIED_TTL_SECONDS` evaluates to `False` (NaN comparisons are always
  false) rather than raising — so a poisoned `started_at` (as opposed to `supervisor_started_at`) fails
  closed (claim treated as expired) instead of crashing. Only the `int(recorded) == int(current)`
  identity-match branch is the crash site.

## The 24h `OMP_UNVERIFIED_TTL_SECONDS` backstop — named in both directions, neither gates

- **Direction A (holds a dead claim too long):** an OMP claim whose identity cannot be proven (OS
  won't report a start time) and that is actually dead is held live for up to 24h before reconcile can
  clear it, denying a lead/orchestrator's yield through the held-child gate for that window.
  Precondition-absent as a *regression*: pre-`fee9d5f`, this exact case (unverifiable pid) was live
  **forever** (F3's own finding), so 24h strictly improves it; not a new gap.
- **Direction B (releases a claim still genuinely running):** on a host where process-start-time
  introspection is unavailable (no `/proc`, no `ps`, or both time out) for the entire life of a claim,
  a real supervisor older than 24h would have its claim expire out from under it — reintroducing the
  exact false-completion risk DEC-204 exists to prevent, for exactly the population this PR's Summary
  targets (multi-hour+ unattended runs). Bounded by the commit's own margin claim (24h vs. the longest
  measured leaf, 7,200s = 2h) — that margin is real but is evidence from one measured run, not a proof
  that no legitimate run ever exceeds a day, and not evidence that start-time introspection is
  reliable across every host OMP is deployed to. Not `must_fix` — no reproduction of introspection
  actually failing on a real supported host — but worth a named, non-blocking open question rather than
  silently clearing it, since it is exactly the class of assumption a future long-tail run could break
  silently.

## threat_model

```yaml
- { boundary: "registry-supplied supervisor_started_at trusted without finiteness check (_omp_claim_live, NEW in fee9d5f)", stride: "D", mitigated: false }
- { boundary: "ps subprocess argv construction (_read_process_start_time)", stride: "T", mitigated: true }
- { boundary: "F2 HARNESS-FEATURE capture: role filter + one-shot latch", stride: "T", mitigated: true }
- { boundary: "F3 pid+start-time identity vs. every-persona held-child gate", stride: "D", mitigated: true }
- { boundary: "F5 release_cmd feature now required; both prod callers verified", stride: "T", mitigated: true }
- { boundary: "OMP_UNVERIFIED_TTL_SECONDS 24h backstop, unprovable-identity hosts", stride: "D", mitigated: true, precondition_absent: true }
```

## Open questions

- Q1 (non-blocking): the exclusion of `toolResult`-role content in F2's fix rests on this host tagging
  tool-result messages `role: "toolResult"` (asserted by `omp-hooks.test.ts:374`, not independently
  verifiable from this repo — no vendored OMP SDK type defs). The one-shot `featureCaptured` latch is
  the mechanism that actually matches DEC-204's stated design ("captures... before the first tool
  call") and closes the gap even if that role tag assumption is ever wrong, so this does not change the
  verdict — flagging only so a future host-schema change gets checked against it.
- Q2 (non-blocking): has the 24h backstop's Direction B (start-time introspection failing for a whole
  claim's life on a real supported host) ever been reproduced, or only reasoned about? Would upgrade to
  `must_fix` if a live host in the supported matrix is shown to lack both `/proc` and a working `ps`.

```yaml
VERDICT: PASS
DIGEST:
  headline: "F2/F3/F5's fixer revisions are all correct on inspection. fee9d5f's new liveness code has a reproduced NaN/Infinity crash in _omp_claim_live that silently defeats enforcement, but per lead adjudication it grants no capability beyond what registry-write access already holds (P-02) — reclassified from must_fix to an advisory med reliability/defense-in-depth finding."
  in_scope: true
  scope_reason: "fee9d5f adds a subprocess fork inside an enforcement gate, a module-level cache, and a trust decision keyed on OS-reported process metadata read from an attacker-writable local file — exactly the kind of new trust surface this role audits, distinct from the already-reviewed base diff."
  severity_max: med
  findings: 1
  must_fix: []
  threat_model:
    - { boundary: "registry-supplied supervisor_started_at trusted without finiteness check (_omp_claim_live, NEW in fee9d5f)", stride: "D", mitigated: false }
    - { boundary: "ps subprocess argv construction (_read_process_start_time)", stride: "T", mitigated: true }
    - { boundary: "F2 HARNESS-FEATURE capture: role filter + one-shot latch", stride: "T", mitigated: true }
    - { boundary: "F3 pid+start-time identity vs. every-persona held-child gate", stride: "D", mitigated: true }
    - { boundary: "F5 release_cmd feature now required; both prod callers verified", stride: "T", mitigated: true }
    - { boundary: "OMP_UNVERIFIED_TTL_SECONDS 24h backstop, unprovable-identity hosts", stride: "D", mitigated: true }
  open_questions:
    - { id: Q1, question: "F2's role-based exclusion of toolResult content assumes this OMP host tags tool results role:\"toolResult\" (per omp-hooks.test.ts:374), unverifiable from this repo. The one-shot featureCaptured latch independently covers this, so it is non-blocking — flag for re-check if the host's message schema ever changes.", blocking: false }
    - { id: Q2, question: "Has the 24h OMP_UNVERIFIED_TTL_SECONDS backstop's premature-release direction (start-time introspection unavailable for a claim's whole life on a real supported host) been reproduced on any host in the supported matrix, or only reasoned about from one measured 2h leaf run?", blocking: false }
  files_touched: []
  expertise_update: []
artifact: .harness/harness/features/PR-922-omp-supervision/notes/review-harness-security-reviewer-c1.md
```
