# QA gate review — FEAT-32, pinned `5107efb`

## BLUF

Gate is green and the eight in-scope suites are largely well-built — five of six mutation-probed
task verify blocks (T-02..T-06, T-08, T-14) genuinely go red on their named literal. But **REQ-12 /
SC-19 (T-09, the D-09 return contract) ships with ZERO test coverage anywhere in the repo** despite
declaring `verify: automated evidence: integration` with nine named cases — I demonstrated this live
(below). That is a FAIL-worthy gap on its own. Two secondary findings: T-08's plan-mandated cases 9
and 10 (stale claim, missing library) never got written, and Q5 in STATE.md undercounts its own
finding by one suite.

## JOB 1 — the gate, re-run myself

- `CLAUDE_PROJECT_DIR=$PWD .claude/skills/harness/bin/run-unit-tests.sh --kind unit`: **exit 0**,
  187 lines matching `^PASS `, 0 `FAIL`.
- `--kind integration`: **exit 0**, 481 lines matching `^PASS `, 0 `FAIL`, 3 `ERROR` (all inside
  case names, matching BRIEF SC-14's stated baseline shape).
- `--check-kinds`: **exit 0** — "the script arrays and test_kinds.integration.detect agree."
- `test-check-domain.py` `ok` count: **201** now vs **173** at `12c66b3` (I ran the actual baseline
  script from the main checkout, not trusted from prose) — 28 new cases, none lost. Matches the
  dispatch's stated numbers exactly.
- Every task's `change_type` in plan.yaml is `logic`, `config` or `docs`; `harness.json`'s matrix
  maps `logic -> always:[unit]`. All eight new/rewired merge+hook suites are registered under
  `test_kinds.integration` (fork-based, per DEC-187's unit/integration split by process model, not
  by rigor) — consistent with FEAT-30's precedent (`expertise-merge.py` was already
  integration-only). **matrix_ok: true**, but flagging as an open question: nothing in this
  feature adds a fast in-process **unit**-kind case for any of T-02..T-09/T-14's logic, so the
  matrix's literal `unit` floor for `change_type: logic` is satisfied only by inheriting whatever
  pre-existing unit coverage exists elsewhere (none of it touches these new modules). Not a new
  problem — same shape as FEAT-30 — but worth naming since nobody has.
- Of the 21 changed/added files, the 8 suites named in the dispatch are where the real logic lives;
  I mutation-probed 6 of them live (T-02, T-03, T-04, T-05/T-06, T-08, T-14's check-domain) via their
  own plan-embedded verify blocks, plus one additional probe of my own (validate-digest.py, below).

## JOB 2 — can each new assertion go red? (mutation-probed, not just read)

Ran the plan's own verify block for each task, standalone, each doing its own named-literal mutation
in a copied tree and asserting red-then-green:

| Task | Mutated literal | Command | Result |
|---|---|---|---|
| T-02 | `USE_FLOCK` | `bash /tmp/qa32-t02-verify.sh` | exit 0 — 18/18 checks, red proof fired |
| T-03 | `UNION_MERGE`, `PRESERVE_BASE_BYTES`, `APPROVAL_REFUSAL` | verify script | exit 0 — red proofs fired for all three |
| T-04 | `UNION_MERGE` | verify script | exit 0 |
| T-05/T-06 (shared file) | `USE_FLOCK` (expertise), `CLAIM_TTL_SECONDS`, `SINGLE_FLIGHT_AGENTS` | verify scripts | exit 0, 55/55 checks (T-06); T-05's case10 stale-lock-recovery present and passing |
| T-08 | `SINGLE_FLIGHT_AGENTS = ()` | verify script | exit 0 — refusal cases (6) failed as required by the red proof, cases 1-5 (T-07's pinned set) unedited |
| T-14 (check-domain) | `APPROVAL_GUARD` | verify script | exit 0 — 201 `ok` lines, floor of 167/173 exceeded |

None of these are vacuous exit-code-only checks — every case I read in `test-harness-merge.py`,
`test-plan-merge.py`, `test-observations-merge.py`, `test-expertise-merge.py`,
`test-inflight-registry.py` asserts specific content (byte ranges, named ids, stderr markers), not
bare exit codes.

**`test-dispatch-guard.py` case 1** (pre-existing, T-07) and **case 6** (new, T-08) both assert exit
code AND stderr marker AND payload-derived content (model value, agent name; started_at, dispatcher,
release command) — not vacuous. Confirmed by reading `.claude/skills/harness/bin/test-dispatch-guard.py:54-171`.

### The finding: T-09 / REQ-12 / SC-19 has no test anywhere

`git diff 12c66b3 5107efb -- .claude/skills/harness/bin/test-validate-digest.py` is **empty** — the
file was never touched by this feature, despite T-09's own intent mandating "ADD cases... NEW CASES:
1... 9" covering claim release and the D-09 children-in-flight refusal.

```
grep -ni "children\|d-09\|single-flight\|551" .claude/skills/harness/bin/test-validate-digest.py
```
returns **zero matches**. `grep -rln "children_refusal_lines\|live_children" .claude/skills/harness/bin/test-*.py`
returns only `test-inflight-registry.py` — which tests the **library** functions in isolation, never
`validate-digest.py`'s actual wiring of them into `hook_mode()`.

**Live demonstration** (copied tree, outside the repo, per DEC-153):
```
python3 -c "... s.replace('_kids = _reg.live_children(_root, agent)', '_kids = []  # MUTATED')..."
VALIDATE_DIGEST_BIN=<mutant>/validate-digest.py python3 .claude/skills/harness/bin/test-validate-digest.py
```
Result: **exit 0, "ALL PASSED."** Neutering the entire D-09 refusal — the mechanism SC-19 exists to
grade — leaves the suite fully green. The mutation was confirmed applied (`assert s2 != s` before
the run) and the suite genuinely ran (1397-line file, template + hook + CLI sections all executed).

Root cause: T-09's own `verify:` block (plan.yaml:947-962) checks only (1) the existing suite still
passes unedited — trivially true since nothing was added, (2) three stderr markers exist as source
text, (3) code-ordering via string-index comparison. **It never asserts a new case exists.** The gate
that was supposed to prove this task honest cannot see the omission it left behind.

This is FAIL-worthy on its own: REQ-12 and SC-19 declare `verify: automated evidence: integration`
and neither is met. `validate-digest.py:860-918` (the D-09 code) is real and correctly ordered
(release-then-check, confirmed by the ordering assertion in T-09's verify, which I also ran and
which passed), but its behavior is unverified.

### Secondary: T-08's plan-mandated cases 9 and 10 are absent

T-08's intent (plan.yaml:1228) lists five new cases: 6 (refusal), 7 (allow), 8 (parallel squad legal),
9 (stale claim allowed + stderr says expired), 10 (library missing, fail-open). The shipped
`test-dispatch-guard.py` `main()` calls only `case_1` through `case_8` — confirmed by
`grep -n "case_9\|case_10\|STALE\|MISSING" test-dispatch-guard.py` returning nothing, and by reading
`main()` at line 250-257. T-08's own `verify:` block doesn't check for their presence either (it only
asserts cases 1-5's markers survived and the `SINGLE_FLIGHT_AGENTS=()` red proof). The stale-claim
guarantee (SC-09) IS tested, but only at the library level (`test-inflight-registry.py` case 3) —
never at the hook level, so `dispatch-guard.sh`'s own stale-claim stderr line and its "library
missing" fail-open path (a distinct fail-open branch T-08's intent explicitly names) are unverified.

## JOB 3 — the fixture trap, audited on both files

`test-check-domain.py`'s `FIXTURE_MANIFEST` (line 74) grants only `harness-documentor`. **T-14's own
new fixture, `APPROVAL_MANIFEST` (line 2344), correctly extends it** with explicit
`harness-pm`/`harness-orchestrator` grants over the plan/BRIEF/PLAN.md paths before firing any case
as those personas — and says so in a comment: "or every case below is an ordinary DOMAIN denial...
FEAT-31 T-15 hit this exact trap with this exact fixture." I read every one of the 14 new T-14 cases
(2429-2603): all fire against `_approval_root()` (built from `APPROVAL_MANIFEST`), none against the
bare `FIXTURE_MANIFEST` while claiming a pm/orchestrator identity. No repeat of the trap here.

`test-dispatch-guard.py`'s new cases (6-8) don't use `check-domain.sh`'s grant system at all —
`dispatch-guard.sh` is a different hook with no domain-manifest dependency — so the fixture-trap
shape doesn't apply to it. No finding.

## JOB 4 — test isolation, swept

- Grepped all five new merge/registry suites for a literal `".harness/` path: **none found** —
  every fixture is tempdir-rooted.
- The one KNOWN leak (T-08's `main()` comment, lines 222-245: `test-dispatch-guard.py` used to leak
  one live claim per run into the real `.harness/.inflight-claims.json` via case 2's cwd-less
  payload) is fixed by isolating `CLAUDE_PROJECT_DIR` for the whole process in `main()`. **I verified
  the fix live**, deliberately reversed from the registered order (`test-dispatch-guard.py` ran
  BEFORE `test-validate-digest.py`, opposite of `test_kinds.integration.detect`'s listing):
  `dg exit:0`, `.harness/.inflight-claims.json` absent after, `test-validate-digest.py` then ran
  clean (exit 0, 0 FAIL). No re-leak.
- `git status --porcelain` before/after every probe I ran showed only my own untouched pre-existing
  dirty file (`feature.json`) — no suite left new artifacts in the real tree.
- `test-check-domain.py`'s pre-existing `CLAUDE_PROJECT_DIR=ROOT` cases (lines 793, 865, 922, 940,
  979) run against the real worktree, but `git diff 12c66b3 5107efb` on this file shows **zero** of
  those lines were touched by this feature — pre-existing pattern, out of scope, and they only fire
  the hook in decision mode (no Write actually executes), so no live write occurs.

## JOB 5 — adequacy: the concurrency admit-set, confirmed and extended

Confirmed **and extended** — STATE.md's Q5 says the exit-6 LOCKED branch was taken 0/20 in T-03
case4, T-04 case7, T-06 case7. All three self-report this on their own `PASS ... informational —
...admitted 0/20 times` line, which I read directly in the live suite output. **T-02's own case5
(the shared `harness_merge.py` core's contention test) has the identical shape and I found it is
ALSO 0/20 — but it doesn't self-report the split, and Q5 doesn't name it.** I instrumented a copy
(outside the repo) to count the refused branch and reran: `REFUSED_COUNT= 0`. So it's four suites,
not three, and one of them is silent about its own imbalance where the others chose to disclose it.
This doesn't fail anything — Q5 already correctly frames it as "pinned by the SET, not those cases,"
non-blocking — but the STATE.md record should add T-02 to the named set for completeness, since it's
literally the base primitive the other three build on and shares the same discriminating property
gap.

## Suites mutation-probed vs. read-only

**Mutation-probed** (ran the actual plan-embedded verify script, or my own probe, and watched red/green):
`harness_merge.py`/test-harness-merge.py (T-02), `plan-merge.py`/test-plan-merge.py (T-03),
`observations-merge.py`/test-observations-merge.py (T-04), `expertise-merge.py`/test-expertise-merge.py
(T-05), `inflight_registry.py`/test-inflight-registry.py (T-06), `dispatch-guard.sh`/test-dispatch-guard.py
(T-07/T-08), `check-domain.sh`/test-check-domain.py (T-14), `validate-digest.py`/test-validate-digest.py
(T-09, my own probe — the demonstration above).

**Read only, not independently mutated beyond what's above:** the full body of `test-check-domain.py`'s
2653 lines (I read the T-14 section and the fixture in full, skimmed the rest for the isolation/ROOT
sweep); the full body of `test-validate-digest.py`'s 1397 lines (read the D-09-relevant grep results
and structure, not every one of its ~89 cases).

## SC evidence map (for pm's goal-check)

- SC-01/02: `test-plan-merge.py` case 1, case 4 (`git show 5107efb:.claude/skills/harness/bin/test-plan-merge.py`)
- SC-03: `test-plan-merge.py` case 3, case 10
- SC-04: `test-observations-merge.py` case 1, case 2, case 7
- SC-05: destination-refusal cases across all four merge suites (case 7/9 each)
- SC-06: `test-dispatch-guard.py` cases 6, 7
- SC-07: `test-dispatch-guard.py` cases 1-5, unedited (confirmed byte-identical assertions pass)
- SC-08: **the "existing suite unedited" half is trivially true because nothing was added** — see
  the JOB 2 finding. The "each new path is asserted by a new case of its own" half is **UNMET**.
- SC-09: `test-inflight-registry.py` case 3 (library level only — hook-level stale-claim stderr is
  untested, see JOB 2 secondary finding)
- SC-10: `test-harness-merge.py` case 4, `test-expertise-merge.py` case 10
- SC-11: `test-*-merge.py` case naming `harness_merge.locked_update`; `test-inflight-registry.py` case 10
- SC-14: confirmed live — see JOB 1
- SC-17/SC-20/SC-21: `test-check-domain.py` T14 cases 1-14, 5a-5e
- SC-19: **UNMET — no test exists.** This is the finding this whole review turns on.

## Coverage gaps (Phase-1-derived, before I read any code)

Reading BRIEF.md's REQ-12 ("An agent that reports a verdict while a subagent it dispatched is still
running is told so...") cold, I expected: a case firing `SubagentStop` as a lead/orchestrator with
live children on disk, asserting refusal content and claim release order. That test does not exist.
This is exactly the gap JOB 2 found from the other direction — Phase 1 and Phase 2 converge on the
same hole, which is why I'm confident reporting it as FAIL rather than an open question.

## Open questions

- Q1 (blocking): REQ-12/SC-19 has zero test coverage of `validate-digest.py`'s D-09 mechanism.
  Recommend routing back to a dev to add the nine cases T-09's own intent already specifies, then
  re-gate.
- Q2 (non-blocking): T-08's plan-mandated cases 9 (stale claim) and 10 (library missing) at the
  hook level were never written; the guarantee is proven only at the library level. Should the plan
  be amended to drop them, or should they be added?
- Q3 (non-blocking): Q5 in STATE.md should be extended to name T-02's case5, which shares the same
  0/20 LOCKED-branch shape but doesn't self-report it.

```yaml
VERDICT: FAIL
DIGEST:
  headline: "Gate is green (unit 187/0, integration 481/0, check-kinds 0) and six of eight target suites mutation-probe clean, but REQ-12/SC-19 (T-09's D-09 return contract) has zero test coverage anywhere — demonstrated live by neutering live_children() and getting a fully green test-validate-digest.py."
  suite: pass
  failures: 0
  matrix_ok: true
  kinds:
    - { kind: unit, state: satisfied, cmd: ".claude/skills/harness/bin/run-unit-tests.sh --kind unit", named_tests: 187 }
    - { kind: integration, state: satisfied, cmd: ".claude/skills/harness/bin/run-unit-tests.sh --kind integration", named_tests: 481 }
  coverage_gaps:
    - "REQ-12 / SC-19: validate-digest.py's D-09 claim-release-and-children-refusal mechanism (lines 860-918) has no test anywhere in the repo — test-validate-digest.py was never touched by this feature (git diff 12c66b3..5107efb is empty for that file), and test-inflight-registry.py only tests the library in isolation, never validate-digest.py's wiring of it."
    - "SC-09 (stale-claim recovery) is tested only at the library level (test-inflight-registry.py case 3); dispatch-guard.sh's own stale-claim stderr line and 'library missing' fail-open path (T-08 intent cases 9 and 10) are unwritten."
  sc_evidence:
    - { id: SC-01, test: ".claude/skills/harness/bin/test-plan-merge.py case 1/case 2" }
    - { id: SC-02, test: ".claude/skills/harness/bin/test-plan-merge.py case 4" }
    - { id: SC-03, test: ".claude/skills/harness/bin/test-plan-merge.py case 3, case 10" }
    - { id: SC-04, test: ".claude/skills/harness/bin/test-observations-merge.py case 1/2/7" }
    - { id: SC-05, test: "each *-merge.py suite's destination-refusal case (case 7 or case 9)" }
    - { id: SC-06, test: ".claude/skills/harness/bin/test-dispatch-guard.py case 6/case 7" }
    - { id: SC-07, test: ".claude/skills/harness/bin/test-dispatch-guard.py case 1-5 (byte-identical, confirmed by verify script)" }
    - { id: SC-08, test: "MISSING — no new case in test-validate-digest.py" }
    - { id: SC-09, test: ".claude/skills/harness/bin/test-inflight-registry.py case 3 (library level only)" }
    - { id: SC-10, test: ".claude/skills/harness/bin/test-harness-merge.py case 4, test-expertise-merge.py case 10" }
    - { id: SC-11, test: "each *-merge.py suite + test-inflight-registry.py case 10" }
    - { id: SC-14, test: "run-unit-tests.sh --kind unit / --kind integration, re-run live" }
    - { id: SC-17, test: ".claude/skills/harness/bin/test-check-domain.py T14 cases 1,3,4" }
    - { id: SC-19, test: "MISSING — no test exists for this criterion" }
    - { id: SC-20, test: ".claude/skills/harness/bin/test-check-domain.py T14 cases 9,10,11" }
    - { id: SC-21, test: ".claude/skills/harness/bin/test-check-domain.py T14 cases 5a-5e" }
  open_questions:
    - { id: Q1, question: "REQ-12/SC-19 has zero test coverage — route back to a dev to add T-09's own nine specified cases to test-validate-digest.py, then re-gate?", blocking: true }
    - { id: Q2, question: "T-08's plan-mandated cases 9 (stale claim) and 10 (library missing) at the hook level were never written. Amend the plan to drop them, or add them?", blocking: false }
    - { id: Q3, question: "Should STATE.md's Q5 be extended to name test-harness-merge.py's case5, which shares the same 0/20 LOCKED-branch shape but doesn't self-report it?", blocking: false }
  files_touched: []
  expertise_update: []
artifact: .harness/harness/features/FEAT-32-concurrent-write-merge/notes/review-harness-qa-c0.md
```
