# QA gate re-audit — PR #922, cycle 1 (`7ccfae8..fee9d5f`)

**matrix_ok: true.** Both required `cross_module` kinds (`unit`, `integration`) re-verified green,
zero FAIL. All eight new tests independently reproduced RED against pre-fix code (not merely
asserted) and GREEN post-fix. All three of the fixer's revisions to cycle 0's own findings hold up
under independent scrutiny — F2's diagnosis correction, F3's re-rating, and F5's downgrade are each
grounded in code I read myself, not accepted on the strength of the prose. Gate-only; nothing
authored beyond this note and a disposable git worktree (below) needed for the red-side runs.

## Suite table — command, observed, fixer's claim, match

| Suite | Command | Observed | Fixer claim | Match |
|---|---|---|---|---|
| inflight registry | `python3 .../test-inflight-registry.py` | **97/97 PASS**, exit 0 | 88→97 | ✅ exact |
| dispatch guard | `python3 .../test-dispatch-guard.py` | **42/42 PASS** | 42/42 | ✅ exact |
| validate-digest | `python3 .../test-validate-digest.py` | CLI cases pass, T-09: **24/24 + 2/2 template, ALL PASSED** | "all passed" | ✅ |
| omp hooks (bun) | `python3 .../test-omp-hooks.py` (bun test) | **24 pass / 0 fail** | 20→24 | ✅ exact |
| unit suite | `run-unit-tests.sh --kind unit` | exit 0, **0 `FAIL` lines** across the full log; 417 `PASS <script>` lines (one per script, not per case — G-04) | 977→986 PASS/0 FAIL | ⚠️ no-fail confirmed; the specific 977→986 case-total is **not independently reproducible** from this script's own output convention (mixed `N of N`/`N/N`/bare-`ok` per-script formats, no cross-script aggregator) — same limitation c0 hit and declined to total. Treat the failure-count half of the claim (0 FAIL) as verified; the case-total half as unverified, not contradicted |
| integration suite | `run-unit-tests.sh --kind integration` | exit 0, **569 `PASS` lines, 0 `FAIL` lines** | not named by fixer, but required by the `cross_module` floor | ✅ — matrix requirement satisfied independently of the fixer's claim list |
| `check-omp-port.py` | direct | `OMP port surface: ok`, exit 0 | "ok" | ✅ |
| `check-state.sh` | direct | exit 0, all `note`-level, unrelated to this diff (same pre-existing housekeeping items c0 saw) | exit 0 | ✅ |

## The audit that matters — red-then-green, independently executed

**Method:** pre-fix state reconstructed two ways, both from git history at the pinned SHAs — no
in-place edits to the reviewed worktree. (1) Python: `INFLIGHT_REGISTRY_DIR` env var (already
built into `test-inflight-registry.py`) pointed at a scratch copy of the `cc9e5cf`-era
`inflight_registry.py` (pre-F3). (2) TypeScript: a disposable `git worktree add` at `66e9a9d`
(pre-F1/F2, base of the PR) plus the post-fix `omp-hooks.test.ts` copied into `/tmp` with its one
import line rewritten to an absolute path into that worktree — `bun test` needs no repo write to
run this way. All eight cases below were **executed**, not reasoned about.

| # | Case | Pre-fix result | Reason capable of failing? |
|---|---|---|---|
| 1 | omp-hooks: "a guard pass-through with no claim receipt allows the dispatch" | **FAIL** — `{block:true, reason:"…returned no claim receipt…"}` instead of `undefined` | yes — exact F1 mechanism |
| 2 | omp-hooks: "a claimless dispatch in a batch does not roll back its siblings' claims" | **FAIL** — same block, batch never reaches the roll-back check | yes |
| 3 | omp-hooks: "a tool result echoing another feature's marker cannot re-key the session" | **FAIL** — uncaught `Error: conflicting Harness feature markers…` thrown from `setFeature`, exactly the async-handler-throw F2 described | yes |
| 4 | omp-hooks: "a later user message cannot re-key the captured feature" | **FAIL** — same uncaught throw | yes |
| 5 | registry: case22 "the claim pins the supervisor start time" + "…foreign start time is expired, not trusted" + "…reconcile also clears it" | **FAIL** — pre-fix `_omp_claim_live` is bare `os.kill(pid,0)`; a foreign `supervisor_started_at` is never read, so the claim reads live and `reconcile` leaves it in place | yes |
| 6 | registry: case23 "a verified supervisor keeps its claim at any age" | **CRASH** — `AttributeError: module has no attribute 'OMP_UNVERIFIED_TTL_SECONDS'` (the constant is new in the fix) | yes, trivially — the backstop concept didn't exist pre-fix |
| 7 | registry: case24 "an unverifiable claim is still live inside the backstop" / "…past the backstop it expires" | **split** — first half incidentally PASSES pre-fix (see below); second half **CRASHES** on the same missing constant | second half yes; first half no (see caveat) |
| 8 | registry: case25 "a stranded child no longer holds its parent" | **FAIL**, cleanly (not a crash) — `live_children` still returns the stranded child; the exact "consumer no test reached" the fix commit names | yes |

**Case14's F5 sub-assertion** ("a featureless remedy cannot be composed at all") is a fifth
red-verified check, distinct from the eight above: pre-fix, `release_cmd(root, agent)` with no
`feature` raises no `TypeError`, so the check fails as expected — `feature` genuinely was optional
before this fix.

**One caveat, in the interest of an honest record, not a finding:** case24's *first*
sub-assertion ("an unverifiable claim is still live inside the backstop") passes on the pre-fix
code for the wrong reason — pre-fix, *every* live-pid claim is live regardless of any backstop,
because there is no backstop yet. That half of case24 doesn't discriminate the fix by itself; the
second half (which does, and which crashed pre-fix as shown above) is what actually proves the
behavior, and the case as a whole is correctly red. Not a defect in the test — a green suite could
still form around this if the second assertion were ever dropped, so noting it for the record.

## Do the new tests exercise the real seams, or still mock them?

**Yes, where it matters; no in the part that was never the problem.** Cycle 0's adequacy finding
was that `omp-hooks.test.ts:206-213`'s fixture mocked `dispatch-guard.sh` with only the golden
(claim-granting) response, so the pass-through shape (F1) and the toolResult/second-marker shapes
(F2) never existed in the fixture at all — not that the mock existed. The fixture in `cc9e5cf`
still mocks the external `dispatch-guard.sh`/`inflight_registry.py` subprocess calls (unchanged,
standard for a unit-level TS test — the real subprocess behavior is independently covered by
`test-dispatch-guard.py`'s own suite, run above). What changed is that the mock now **implements**
the fail-open shape (comment at the fixture: "Absent from this fixture, no test could execute the
pass-through path") and the **real, unmocked** `registerHarnessHooks`/`setFeature`/
`captureFeatureFromMessage` logic — where both bugs actually lived — is what the new cases drive.
The registry cases (22-25) go further: real subprocess PIDs, real file-based claims, zero mocking,
exercising `inflight_registry.py`'s actual functions end to end.

## 4(a) — does case23 guard the backstop against becoming a general TTL?

**Yes, genuinely, not just "fires when unverifiable."** Read `inflight_registry.py:159-178`
(`_omp_claim_live`): when `supervisor_started_at` (recorded) and `_process_start_time(pid)`
(current) are both present, liveness is `int(recorded) == int(current)` — **no TTL comparison
at all** on that branch, any age. The backstop (`now - started <= OMP_UNVERIFIED_TTL_SECONDS`)
only runs on the *other* branch, when identity cannot be proven. Case23 sets `started_at` to
10× the TTL in the past while keeping a real live pid with a *matching* `supervisor_started_at`
(verified identity) — it exercises exactly the verified branch. Were the backstop mistakenly
applied unconditionally (the "becomes a general TTL" regression this case is named to prevent),
case23's ancient `started_at` would expire the claim and the case would fail. It does not,
confirming the branch separation is real, not merely that some case somewhere asserts the
backstop fires.

## 4(b) — is validate-digest.py's held-child gate covered end to end with a real recycled claim?

**No — only `live_children` in isolation (case25).** `test-validate-digest.py` was **not touched**
by `fee9d5f`(confirmed: `git log` on that file stops at `66e9a9d`). Its own T-09 suite (re-run
above, 24/24 pass) drives real subprocesses through the held-child gate (cases 6/9/10/11), but
every claim it seeds is made via `reg.claim(...)` with no `supervisor_pid`/`runtime="omp"` — none
of those claims exercise the pid-owned/recycled-pid liveness path at all. So the exact consumer the
fix commit names ("the consumer no test reached, which is why this got through a green suite") is
still, honestly, not reached end to end by any test in this diff — the fixer's own commit message
says this plainly rather than claiming otherwise. This is a real, if narrow, coverage gap: a future
change to how `validate-digest.py` calls `live_children`/`_omp_claim_live` together would not be
caught by any test, only by the registry-level unit tests which don't drive `validate-digest.py`
at all.

## The three revisions — verified, not accepted on prose

**F2 diagnosis correction — CORRECT.** The pre-fix golden-path fixture (`omp-hooks.test.ts:188`
at `66e9a9d`, i.e. present in the *original* PR, unmodified by either fix commit) already encodes
the assignment message as `role: "user"`. This is not the fixer's invention — it's how the test
that was already passing on the original green suite was written. Filtering to `role === "user"`
(the actual fix) is therefore the correct read of DEC-204's "captures that message… before the
first tool call," and a naive filter-to-`"assistant"` (the shape c0's security note's own
`lastAssistantText` contrast could suggest by analogy) would indeed have silently broken capture.
Both exposure paths (toolResult echo, later user message) are independently red-verified above
(cases 3-4).

**F3 re-rating med→high — CORRECT, on a real, previously-unexamined consumer.**
`validate-digest.py:1000-1008`(confirmed by direct read) refuses a lead's/orchestrator's yield
whenever `live_children(...)` is non-empty, for whatever `agent_type` called it — nothing in that
function or its caller scopes the refusal to `SINGLE_FLIGHT_AGENTS`. Cycle 0's med rating cited
"it self-heals" as a mitigant; `reconcile` (read at `inflight_registry.py`) asks the identical
`_omp_claim_live` question `live_claim`/`live_children` ask, so a recycled-pid claim that reads
live to one reads live to all three — reconcile genuinely cannot clear it, as the fixer states.
The re-rating is sound.

**F5 downgrade to unreachable — CORRECT.** Grepped both cited call sites directly:
`dispatch-guard.sh:156` (`reg.release_cmd(root, dispatched, feature=declared)`) and
`validate-digest.py:1001` (`_reg.release_cmd(_root, _persona, feature=_c.get("feature"))`) — both
pass `feature` unconditionally. No third production caller exists. Made `feature` a required
positional (case14's featureless sub-check, red-verified above) rather than merely documented —
the dangerous form is now unconstructible, not just unused.

## Test-matrix gate

Change type: `cross_module` (unchanged from c0's correct inference — five interacting layers touched
by the two fix commits too: `harness-hooks.ts`, `inflight_registry.py`, plus the tests threading
through `dispatch-guard.sh` and `validate-digest.py`'s existing coverage).

| Kind | Required? | State | Evidence |
|---|---|---|---|
| `unit` | always | **satisfied** | `run-unit-tests.sh --kind unit` exit 0, 0 FAIL lines (table above) |
| `integration` | always | **satisfied** | `run-unit-tests.sh --kind integration` exit 0, 569 PASS / 0 FAIL |

**`matrix_ok: true`.**

## Coverage gaps carried forward or newly found

- **c0's Q1 (hook-level crash-reconciliation isolation) — still open, unchanged.** Grepped the
  current `omp-hooks.test.ts` for a two-feature dead-PID reconcile-isolation case at the hook
  layer (the exact assertion c0 asked for) — none exists. Neither fix commit touched this. The
  mechanism remains proven only at the registry level (`test-inflight-registry.py` case_20/21/22).
- **New, from 4(b) above:** `validate-digest.py`'s held-child gate has no end-to-end test with a
  real OMP/recycled-pid claim — only `live_children` in isolation. Same class of gap as Q1, one
  layer over. Neither blocks the gate (the mechanism is proven at unit level, matrix floor met),
  both are findings for the eng-lead/dev team, not for this gate to fail on.

## Process note — one artifact left behind, not mine to remove

Reproducing the TS red-side runs required a disposable `git worktree add --detach` at `66e9a9d`,
created at `.claude/worktrees/harness/qa-c1-scratch-pr922` (the bash-write-guard requires
worktrees live under `.claude/worktrees/`; nothing was ever written inside the reviewed worktree
itself). Per this dispatch's own constraint, worktree removal is never mine to run — even from
outside it, it belongs to the main session. Flagging for Main/orchestrator to run
`git worktree remove .claude/worktrees/harness/qa-c1-scratch-pr922` (it is clean, detached HEAD,
no changes) once this review lands.

```yaml
VERDICT: PASS
DIGEST:
  headline: "matrix_ok true; all eight new tests independently red-then-green verified (20/4 omp-hooks split reproduced exactly), and all three of the fixer's revisions to cycle 0's findings (F2 diagnosis, F3 re-rating, F5 downgrade) check out against source, not prose."
  suite: pass
  failures: 0
  matrix_ok: true
  kinds:
    - { kind: unit, state: satisfied, cmd: "run-unit-tests.sh --kind unit", named_tests: n/a }
    - { kind: integration, state: satisfied, cmd: "run-unit-tests.sh --kind integration", named_tests: n/a }
  coverage_gaps:
    - "hook-level (harness-hooks.ts) crash-reconciliation cross-feature isolation — c0's Q1, still open, neither fix commit touched it"
    - "validate-digest.py's held-child gate has no end-to-end test with a real OMP/recycled-pid claim — only live_children is covered in isolation (4b)"
  sc_evidence: []
  open_questions:
    - { id: Q1, question: "Should this cycle add a hook-level test seeding two features' claims under one dead/recycled PID and asserting cross-feature isolation through before_agent_start/message_end, and an end-to-end validate-digest.py case with a real OMP claim? Both are real, narrow gaps that survived two fix passes.", blocking: false }
    - { id: Q2, question: "The disposable worktree at .claude/worktrees/harness/qa-c1-scratch-pr922 (clean, detached at 66e9a9d) needs removal from outside itself — not mine to run.", blocking: false }
  files_touched: []
  expertise_update: []
artifact: .harness/harness/features/PR-922-omp-supervision/notes/review-harness-qa-c1.md
```
