# Code review — PR #922 (OMP long-running Harness supervision) — code-reviewer, cycle 0

reviewed: `7ccfae8dd7644bc3aaea612dabf4317c0d804f99..66e9a9d64ec79d30ef43ea3e96aa8f0737ae8681`
Source read from the pinned worktree; all line numbers below are from that checkout.

## STAGE 1 — spec compliance: FAIL (see must_fix)

Spec of record = PR body (Summary + Verification) + DEC-204 (`.harness/harness/docs/DECISIONS.md:7317-7415`)
+ its DECISIONS-INDEX row. Four of five Summary bullets and all non-timing, non-deferred
Verification claims check out against real, reproduced evidence. One bullet's supporting change
is undeclared scope that also breaks silently.

### Summary bullets

| # | Bullet | Disposition |
|---|---|---|
| 1 | OMP is the provider-neutral supervisor | supported — `config.yml` (`async.enabled: true`, `task.maxRuntimeMs: 0`), `check-omp-port.py` enforces the roster/blocking/config invariants and passes for real (`OMP port surface: ok`). See must_fix #1 for a gap in the *reconciliation* half of this. |
| 2 | feature-scoped, process-owned claims with targeted crash reconciliation | supported for its tested cases (schema v2, feature key, targeted `reconcile`) — **but see must_fix #1**: the crash-reconciliation mechanism itself has a real gap under PID reuse that the test suite cannot exercise and the design (no TTL fallback for OMP claims) makes unrecoverable automatically. |
| 3 | async main→orchestrator edge, blocking nested edges | supported, strongly — `harness-orchestrator.md` carries no `blocking:` key and is untouched by this diff; all 15 other `.omp/agents/harness-*.md` gained exactly `+blocking: true` (verified `git diff` on `harness-pm.md`/`harness-eng-lead.md`: one line each); `check-omp-port.py:83-87` asserts the orchestrator must NOT be blocking and every other agent MUST be — ran it, passes. |
| 4 | enforce feature identity, terminal claim release, digest safety, GitHub close ordering | supported — `dispatch-guard.sh:74-98` is the one fail-closed branch (missing/malformed `HARNESS-FEATURE:` line); `harness-hooks.ts:547-579` (tool_result "settled"/attach) + `:592-604` (`task:subagent:lifecycle`) do targeted release; `validate-digest.py` diff adds feature/agent_id-scoped release; `harness-hooks.ts:475-480` puts `gh-close-gate.sh` first in the Bash preflight chain, ahead of branch/write guards, matching the DEC text. |
| 5 | document launch, provider switching, recovery, durable GitHub mirroring | supported — `README.md` "Long-running workflow"/"Recovery after terminal loss"/"GitHub lifecycle" sections and `references/github-mirror.md`'s new "Wake and recovery" section match DEC-204 prose closely, including the read-before-act ordering. |

### Verification claims

| Claim | Disposition |
|---|---|
| OpenAI leaf 7200.07s / Anthropic leaf 900.06s | not re-checked (excluded by assignment; asserted live evidence) |
| crash/resume: dead supervisor reconciled, no cross-feature release | supported for the tested case (`test-inflight-registry.py` case16/case20, real death) — **caveated by must_fix #1**, which is a case the claim's own wording ("dead supervisor reconciled") does not cover: a *reused* PID is never recognized as dead at all |
| OMP hook tests: 20 passed | **reproduced** — `bun test ./.claude/skills/harness/bin/omp-hooks.test.ts` → 20 pass, 0 fail |
| inflight registry checks: 88 passed | **reproduced** — `python3 test-inflight-registry.py` → 88/88 |
| dispatch guard checks: 42 passed | **reproduced** — `python3 test-dispatch-guard.py` → 42/42 |
| full unit suite, adapter drift, OMP port check, canonical state checker passed | **reproduced** — `run-unit-tests.sh` exits 0 (all scripts including the three above PASS); `sync-agent-adapters.py --check` exits 0; `check-omp-port.py` prints `ok`; `check-state.sh` exits 0 (only advisory `note` lines, no `VIOLATION`) |
| Deferred ship evidence (GitHub Building→Review→Done→auto-close) | out of scope by the PR's own framing — not graded |

### must_fix

**1 [high] — PID reuse silently defeats "targeted crash reconciliation" for every OMP claim, with no fallback.**
`inflight_registry.py:96-107` (`_pid_alive`) is the *only* liveness test for an OMP-runtime claim
(`_expire`, `inflight_registry.py:121-124`: `if claim.get("runtime")=="omp": live iff
_pid_alive(supervisor_pid)`), and per DEC-204 OMP claims are explicitly given **no TTL fallback**
("An OMP claim remains live for any age while its recorded supervisor PID exists"). `_pid_alive`
is a bare `os.kill(pid, 0)` with no secondary identity check (no recorded process-start-time, no
process name/cgroup check) to detect PID recycling. Concretely: supervisor PID 5000 claims
`harness-pm` for FEAT-9, then crashes without releasing; before anyone runs `reconcile`, the OS
reassigns 5000 to any unrelated process (ordinary churn on a dev/CI box, not adversarial); every
subsequent `reconcile`/`live_claim` call for FEAT-9 calls `_pid_alive(5000)`, gets `True`, and
treats the dead claim as live. Single-flight (`is_single_flight`, `harness-pm`) then refuses every
future PM dispatch for FEAT-9 forever, and because there is no TTL escape hatch for `runtime=="omp"`
claims, the *only* recovery is an operator who happens to know to run the manual `release`
command — the "targeted crash reconciliation" this PR advertises never fires for this case, silently.
This is exactly the fail-open shape called out for this review (a liveness check that sails through
on a miss) and it lands on the PR's own headline mechanism. Untestable by unit test (would need a
real PID collision), and indeed `test-inflight-registry.py` case16/case20 only exercise a genuinely
dead PID, never a reused one — the gap is real and unexercised.

**2 [high] — `dispatch-guard.sh`'s intentional fail-open branches are converted into a hard batch block by the TS caller.**
`dispatch-guard.sh` is explicit and repeated ("Only exit 2 blocks (DEC-100)... EVERY branch below
fails OPEN... a guard that blocks every spawn the moment the payload shape changes is worse than no
guard") that several conditions exit 0 with **no** stdout receipt and are meant to let the dispatch
through ungoverned: "dispatched persona ... is not a harness agent" (line 72), "registry libraries
unavailable" (line 112), "no checkout root for this dispatch" (line 138), "OMP dispatch has no
valid supervisor pid" (line 145), "claim step failed ... passing through, the dispatch is NOT
blocked" (line 187). But `harness-hooks.ts:514-524` treats *any* missing receipt, regardless of
exit code, as a hard failure: `if (!receipt) { receipts.forEach(release); reason = "Harness
dispatch policy returned no claim receipt; the task was not started."; break; }` — this both rolls
back any earlier claims in the same batch and blocks the whole `task` call. Concretely: eng-lead
dispatches two items in one batch; the registry import glitches transiently on item 2 (any of the
five fail-open branches above fires); dispatch-guard.sh exits 0 as designed, but the hook now
refuses the *entire* batch, including item 1's legitimate, already-claimed dispatch — the opposite
of the guard's documented contract. `omp-hooks.test.ts`'s "blocks a whole batch" test (lines
~204-230) only exercises the `blocked: true` (exit 2, "deny") path; no test exercises "exit 0, no
receipt," so this divergence between the guard's contract and its caller is real and unexercised.

**3 [high] — scope creep: the orchestrator's context-budget advisory was silently rewritten to depend on a signal that does not exist anywhere in this diff.**
`.claude/skills/harness/SKILL.md:52-56` replaces the previous two-call nonce-probe procedure
(`context-watch.py` + `references/context-check.md`) with: "Use the host's current-session context
signal when it exposes one. OMP-hosted sessions use OMP's own context signal; a host with no
trustworthy signal skips this advisory check in one line." Nothing in this diff implements, exposes,
or documents an "OMP context signal" — `harness-hooks.ts` carries no such field, `config.yml` adds
none, and neither `context-watch.py` nor `context-check.md` were touched (`git diff --stat` on both
paths is empty). The only thing that changed is the prose and its own unit test
(`test-orchestrator-playbook.py`'s `case4_host_neutral_context_signal`, lines 62-67), which checks
**only** that the phrase "host's current-session context signal" is present and that the literal
`context-watch.py` is absent — a wording sweep, not a check that any such signal is reachable. Net
effect: under OMP (the host this very PR makes canonical), an orchestrator following this
instruction has no way to discover "OMP's own context signal" and will fall through to "skips this
advisory check in one line," on every single OMP-hosted run — silently disabling the one existing
safeguard against context exhaustion, in the same PR that removes the *wall-clock* safety bound and
argues at length (DEC-204: "the safety bound is not the liveness bound") that removing one kind of
limit must not silently remove another. This change serves no Summary bullet and no sentence in
DEC-204's added text (grepped; absent) — it is undeclared scope, and it regresses a working
mechanism rather than porting it.

### Notes (non-gating)

**4 [low] — stale security-rationale comments now describe a flag that isn't used.**
`bash-write-guard.sh:34` ("`-P` IS LOAD-BEARING, NOT TIDINESS (#556)...") and `check-domain.sh:96`
("`-I` IS LOAD-BEARING, NOT TIDINESS (#556)...") both introduce this heading but the actual
invocation on the next lines (`bash-write-guard.sh:42`, `check-domain.sh:103`) uses neither flag —
it's `python3 -c 'import sys; sys.path.pop(0); exec(...)'`, the same manual-bootstrap technique
`check-state.sh` uses (and correctly labels without a flag name). Confirmed against baseline: both
files used real `-P` before this diff (`git show <base>:<path>`); the flag was dropped in favor of
the bootstrap but the heading text wasn't updated in either file. This is exactly the defect class
(#556: a governed hook's import path silently drifting) that these comments exist to prevent a
future editor from reintroducing — worth a one-line fix, not a blocker.

## STAGE 2 — code quality

Not reached as a separate pass: all quality-relevant findings above are also the spec/fail-open
findings (must_fix #1, #2 are squarely "silent failure path" / fail-open findings; #4 is the one
pure quality note). No additional quality issues rose above `low` in the areas inspected
(`inflight_registry.py` locking/atomicity — unchanged `harness_merge.locked_update`, not reviewed
per assignment; `validate-digest.py`'s ambiguous-match refusal in `release()` is correctly
conservative; `attach_runtime_identity` is always called with a unique `claim_id` from the
in-memory receipt, so the apparent ambiguity in its `agent+feature` matching is not reachable from
any call site in `harness-hooks.ts` — checked and cleared, not a finding).

```yaml
VERDICT: FAIL
DIGEST:
  headline: Two high-severity fail-open gaps (PID-reuse defeats OMP crash reconciliation; dispatch-guard's fail-open turned fail-closed by its TS caller) plus one undeclared, unimplemented scope item (orchestrator context-budget advisory silently disabled under OMP) — everything else in the diff (roster/blocking split, feature-identity gate, claim release paths, GitHub close ordering, docs) is well-supported by real, reproduced test runs.
  severity_max: high
  findings: 4
  must_fix:
    - "inflight_registry.py:96-107,121-124 — OMP claim liveness is a bare os.kill(pid,0) with no anti-PID-reuse check and no TTL fallback; a reused supervisor PID makes a dead claim permanently un-reconciled, defeating the PR's headline 'targeted crash reconciliation' claim"
    - "harness-hooks.ts:514-524 — treats every dispatch-guard.sh exit-0-no-receipt outcome as a hard block, inverting the guard's documented fail-open contract (dispatch-guard.sh:66-72,109-112,131-138,142-145,183-187; DEC-100 'only exit 2 blocks')"
    - ".claude/skills/harness/SKILL.md:52-56 — orchestrator context-budget advisory rewritten to depend on an 'OMP context signal' that is not implemented anywhere in this diff; its own test (test-orchestrator-playbook.py case4_host_neutral_context_signal) only checks wording; not tied to any Summary bullet or DEC-204 sentence"
  spec_violations:
    - { kind: scope_creep, path: ".claude/skills/harness/SKILL.md", ref: "DEC-204 (absent)" }
    - { kind: omission, path: ".claude/skills/harness/bin/inflight_registry.py", ref: "DEC-204 crash-reconciliation clause" }
  reviewed: "7ccfae8dd7644bc3aaea612dabf4317c0d804f99..66e9a9d64ec79d30ef43ea3e96aa8f0737ae8681"
  human_commits_in_scope: []
  open_questions:
    - { id: Q1, question: "Was PID-reuse considered and accepted as an out-of-scope risk for DEC-204, or should OMP claims record a secondary identity (process start time) to disambiguate a recycled PID?", blocking: false }
    - { id: Q2, question: "Is there an OMP-side context/token-usage signal available to a running agent that this diff simply didn't wire up, or does the SKILL.md prose describe a capability that doesn't exist yet on any host?", blocking: true }
  files_touched: []
  expertise_update: []
artifact: .harness/harness/features/PR-922-omp-supervision/notes/review-harness-code-reviewer-c0.md
```
