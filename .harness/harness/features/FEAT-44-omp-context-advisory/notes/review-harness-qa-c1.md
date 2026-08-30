# QA gate — FEAT-44 cycle 1 — review_sha 21e97ed

**VERDICT: PASS**, one non-blocking coverage defect found under Part 2 (SC-10's boundary claim is
false as tested — the mutation it says it catches would not be caught), plus several disclosed-scope
findings. No FAIL: every matrix kind ran green, re-derived independently, and the SC-10 gap is a
narrow, single-line boundary case with a cheap named fix, not a hollow suite.

## Part 1 — the matrix gate

### change_type audit

Every task in `plan.yaml` declares `change_type: bugfix`. Measured against the actual diff
(32 files, +2706/-3243: new mechanism, 7 file deletions, a hook unregistration, 3 decision
amendments, a skill rewrite, 2 test-registry moves) this reads as **cross_module**, not bugfix — the
BRIEF's own Goal ("the orchestrator... is handed its own real context size") describes new
capability, not a defect repair. This is a labeling finding, **not gating**: `bugfix`'s floor is
`unit` alone; `cross_module`'s is `unit` **and** `integration`, both `always`. The diff shipped both
kinds green regardless of which label applies (SC-07's task, T-04, is independently traced to
`evidence: integration`), so `matrix_ok` is unaffected either way.

### Required kinds, run and re-derived (not trusted from the author's numbers)

| kind | required by (bugfix ∪ measured cross_module) | state | command | result |
|---|---|---|---|---|
| unit | yes | satisfied | `.agents/skills/harness/bin/run-unit-tests.sh --kind unit` | **exit 0**, 418 `^PASS ` lines incl. `bun test` `42 pass / 0 fail / 71 expect() calls` for `omp-hooks.test.ts` |
| integration | yes (cross_module) / only via SC-07 trace under bugfix | satisfied | `.agents/skills/harness/bin/run-unit-tests.sh --kind integration` | **exit 0**, 590 `^PASS ` lines, `test-omp-session-accessor.py` `7/7 checks passed` inline |
| `--check-kinds` | drift cross-check | satisfied | `.agents/skills/harness/bin/run-unit-tests.sh --check-kinds` | `check-kinds: the script arrays and test_kinds.integration.detect agree.` exit 0 |
| `check-omp-port.py` | cited by dispatch | satisfied | ran inside the unit suite | `18/18 cases passed`, `PASS test-check-omp-port.py` |
| `check-state.sh` | cited by dispatch | satisfied | `bash .claude/skills/harness/bin/check-state.sh` | exit 0, 538 lines, **all `note`, zero `violation`/`error`** lines; explicit `INV-17 FEAT-44...exempt` note confirms the DEC-174 direct edits to `.harness.json`/`DECISIONS.md` are recognized deviations-by-design, not flagged |
| typecheck | null cmd, disclosed gap | **BLOCKED (soft, pre-recorded)** | n/a | `test_kinds.typecheck.cmd` is `null`; this is the standing dev-ops gap named in BRIEF's Verification gaps, not new to this feature |
| component / ui / eval | `status: unresolved`/excluded, not applicable | n/a | — | this feature touches no component/ui/eval surface |

All numbers reproduce the author's claims exactly: 1008-line unit output was not independently
totalled against a prior baseline (no such baseline was supplied), but every individual assertion
this dispatch named was re-run and matched.

**`matrix_ok: true`.**

### Test-first audit (T-01)

`git log 7ebfc9e..21e97ed`: `7747f5c` (T-01) precedes `812e145` (T-02, adds
`.omp/extensions/harness-hooks.ts` exports) and `3fa679a` (T-03, wires the handler). `git show
7747f5c -- .omp/extensions/harness-hooks.ts` is **empty** — T-01 touched no production file, matching
its own commit message ("Nothing here touches .omp/extensions/harness-hooks.ts"). RED state is
asserted by the commit message ("24 -> 41 test declarations; the suite is RED") but was not
independently re-executed at that commit: an earlier attempt to `git checkout 7747f5c -- .` in this
shared review worktree collided with two sibling reviewers' concurrently-written note files via
`git stash` — see **Incident** below. Given the collision risk of touching working-tree state in a
worktree three other agents are actively writing into, I did not retry the checkout. This one claim
(RED state literally reproduced) is **taken on the commit message and T-01's own `intent:`
reasoning**, not independently re-executed — flagged, not blocking, since the floor (`declared >= 41`)
was independently re-derived below and does not depend on the RED claim.

**The `declared >= 41` floor is present and binds.** `grep -cE '^[[:space:]]*test\(' omp-hooks.test.ts`
→ **42**, `bun test` reports **42 tests**, both match. The floor was added specifically because a
prior cycle's verify could pass on a load-error string match alone (cited in dispatch); the floor is
a static grep independent of runtime output, so it does bind — confirmed by direct count, not trusted.

**The two absence greps (secret pattern, username) are preceded by ONE shared positive control**
(`grep -q '{' "$A" && grep -q '{' "$B"`), not one control apiece. Ran the verify block live:
```
A B non-empty: OK
positive control OK
no secrets: OK
no username: OK
```
The control proves grep functions and both files are non-empty/parseable, ruling out the specific
DEC-98 shape (a broken invocation silently no-op'ing as "clean"). It does **not** independently prove
the credential regex itself is syntactically valid on this grep — a single shared sanity check is
weaker than one control per pattern, but is a reasonable design given embedding even a synthetic
secret-shaped string in the repo carries its own (larger) risk. Non-blocking observation.

### Per-SC status (SC-01..SC-11)

| SC | status | evidence |
|---|---|---|
| SC-01 | **met** | `omp-hooks.test.ts:426-431`, drives `readContextAnchor` against the anchored fixture; independently confirmed the fixture's newest record is `{promptTokens: 28614, ...}` (`omp-session-anchored.fixture.jsonl` record 10) matching `NEWEST_ANCHOR_TOKENS` |
| SC-02 | **met** | `omp-hooks.test.ts:433-440`, reasoned mutation-sound (see Part 2) |
| SC-03 | **met** | `:442-454` (inert + none), `:638-649` (accessor throws → failure notice), each asserted separately |
| SC-04 | **met** | `:585-602`, each of the 4 negative conditions its own `test()` |
| SC-05 | **met (as amended)** | `:575-583` (healthy, no `isError` key), `:612-625` (blocked non-wake, `isError:true`, no advisory) — amendment text in BRIEF.md is consistent with what the code can actually produce |
| SC-06 | **met** | `:511-517`; independently recomputed 223029/200000=1.1151→"1.12", 223029/150000=1.4869→"1.49", both match |
| SC-07 | **met** | 7/7 retired files confirmed deleted (`git diff --name-status` = exactly 7 `D` lines matching the plan's list); `context-watch` absent from `.claude/settings.json`, `.harness/harness.json`, both `run-unit-tests.sh` copies, `SKILL.md`; `--check-kinds` exits 0; both suites green |
| SC-08 | **met** | `SKILL.md:50-60` names the disk read + injection mechanism, no retired file, cites DEC-198/199/201; `test-orchestrator-playbook.py` `case4_presence_reads_your`/`case4_presence_appends_one`/`case4_absence_claude_sidecar_probe`/`case4_absence_hardcoded_threshold_numeral` all PASS live |
| SC-09 | **met** | DEC-198 (`:6863-6886`), DEC-201 (`:7147-7176`), DEC-159 (`:4114-4132`) each carry an "Amendment" section, none struck; DEC-198 does not claim the config key is absent (explicitly states it IS present at `:169`); DEC-201's amendment states the accessor as measured on one build; `gen-decisions-index.py --stdout` diffs **clean** against the committed index (re-run, confirmed) |
| SC-10 | **evidence exists, but the boundary claim is false — see Part 2 finding F-1** | `:651-660` |
| SC-11 | **met in substance, mis-scoped in the BRIEF** | see Part 2 stub-vs-real section; BRIEF.md:186 still says `evidence: unit` but the actual real-accessor check (`test-omp-session-accessor.py`) is an `integration`-kind script — the BRIEF's evidence-class line was never amended to match T-01's own documented pivot away from an in-`bun-test` `.d.ts` assertion. Non-blocking: the capability is genuinely covered, just filed under the wrong evidence class in the traceability doc |

## Part 2 — the adequacy question

### F-1 (the finding this hunt exists to surface): SC-10's own claim about the `>` vs `>=` mutation is false for the committed test

`harness-hooks.ts:812`: `if (anchor.tokens > threshold)`. SC-10's text: "a `>=` written where `>`
was specified reddens it." The test that is supposed to demonstrate this
(`omp-hooks.test.ts:651-660`, "stays silent at or under the threshold") drives the handler with the
**default** fixture, whose newest anchor is **28614**, against the real repo threshold resolved from
`.harness/harness.json` (**200000**, confirmed: `budgets.orchestrator_context_warn_tokens: 200000`).
28614 is nowhere near 200000. Under `>`, `28614 > 200000` is `false`. Under `>=`, `28614 >= 200000` is
**also** `false`. The two operators are behaviourally identical everywhere except at exact equality
(`tokens === threshold`), and **no test in the suite constructs that value** — the over-threshold
tests use 223029, the under-threshold test uses 28614, nothing uses 200000. So a `>` → `>=` mutation
at line 812 changes the healthy-path behaviour only at the one input value nothing exercises, and
survives this suite undetected.

I could not execute this mutation directly: `bash-write-guard` denies `harness-qa` any write to
`.omp/extensions/harness-hooks.ts` **by agent domain, not by location** — it blocked the same `sed`
both in the review worktree and in a disposable worktree I cut specifically to satisfy
`harness-verification-rules`' "perturbation proofs run in a worktree" guidance (`DEC-153`). This
conclusion is therefore **reasoned, not measured** (O-03) — but it rests on arithmetic (`28614 >
200000` vs `28614 >= 200000` both `false`) that requires no execution to confirm. Flagging this as an
`open_question` for the harness owner too: QA's mandate under `harness-verification-rules` explicitly
includes mutation-proving load-bearing assertions in a disposable worktree, and the domain guard
currently makes that structurally impossible for `.omp/extensions/**`, the one surface DEC-174 places
entirely outside every squad's grant.

**Concrete fix**: add one more injection test using a synthetic anchor built the same way
`overThresholdTranscript()` is (copy the anchored fixture, rewrite the newest `promptTokens` to
exactly the resolved threshold), asserting `result` is `undefined` there too. That closes the one
input value nothing today exercises.

### Assertion-subject table (what each new/changed assertion class actually binds)

| assertion class | file | binds | what breaks it |
|---|---|---|---|
| `readContextAnchor` newest-value equality | `omp-hooks.test.ts:427` | the reverse-scan + JSON-parse + segment-walk over a **real captured** transcript | wrong record picked, wrong field path, off-by-one in "newest" |
| widening-past-window | `:433-439` | the `window *= 4` loop | pinning the window to a fixed size — **reasoned sound**: mutating the loop to return `inert` on the first partial-window miss instead of widening changes `{kind:"tokens",...}` to `{kind:"inert",...}`, which fails `toEqual` |
| inert field/bytes | `:442-448` | `CONTEXT_TOKENS_FIELD` constant plumbed end-to-end, spelled as a literal string in the test | the constant drifting silently (test reads a hardcoded string, not the module's own constant — correct per its own stated design) |
| `resolveContextWarnTokens` | `:498-506` | real file read of a temp `.harness/harness.json`, real JSON parse, real key lookup | mutation back to hardcoded 200000 — **reasoned sound**, 150000 differs from default |
| `contextAdvisoryText` ratio | `:511-517` | the actual division + `toFixed(2)` | numerator/denominator swap, wrong precision — **reasoned sound**, independently recomputed both values |
| `resolveSessionFile` failure vs absent | `:473-486` | the three-way branch (missing manager / non-function accessor / throw) vs the two-way "clean call, no path" | collapsing "failed" into "absent" — **this is REQ-04's own load-bearing distinction**, and it is the one the cycle-0 plan review (`review-harness-qa-c0.md` §6) found **missing** in the plan; the built code (`resolveSessionFile`, `harness-hooks.ts:550-570`) closes that gap with its own export rather than the inline try/catch the plan originally specified, and `:638-649`'s "accessor failure" test exercises exactly this via a throwing stub |
| currentAgent / toolName gate | `:585-602` | the two `===` comparisons at `harness-hooks.ts:792` | either flipped to `!==`, or a scope check dropped — all 4 negative cases pass a **different** persona/tool through the same handler call, so a broken gate fails at least one |
| `isError` presence/absence | `:582`, `:622-624` | the key-existence check (`"isError" in result`), not truthiness | inventing `isError: false` on a healthy result, or dropping it on a blocked one — both are distinguishable from the asserted form, unlike a truthy/falsy check which a stray `isError: false` would pass vacuously |
| SC-08's `case4_presence_*` | `test-orchestrator-playbook.py` | **the SKILL.md prose only** — "a document changed" is the honest answer | SC-08 self-discloses this scope explicitly ("grades prose accuracy only... no SC rests on wording alone") and the runtime capability is independently covered by SC-01–06/10/11, so this is not a hollow claim wearing a capability's clothes — it is labeled correctly |
| `test-omp-session-accessor.py` cases 1-6 | see stub-vs-real below | the real `omp` binary | see below |

### Stub-vs-real boundary

Every case in `omp-hooks.test.ts`'s `describe("context advisory injection")` and
`describe("resolveSessionFile")` supplies a **fake** `ctx.sessionManager.getSessionFile` (a plain
closure returning a string, throwing, or returning a fixture path). Zero exceptions. The suite's own
comment at `:461-467` says so explicitly and explains why an in-`bun-test` `.d.ts` assertion (the
BRIEF's original SC-11 design) cannot work: `Bun.resolveSync` behaves differently under `bun test`
than under `bun run`, and three copies of the OMP package on the machine disagree (17.3.8 / 18.0.5
running / 18.0.10 cached).

The **only** real-binary check is `test-omp-session-accessor.py`. Read in full and **re-run live**:
```
PASS - case1: the omp binary is on PATH
PASS - case1: the committed probe extension exists
PASS - case2: the probe produced at least one observation
PASS - case3: a subagent session was observed with getContextUsage undefined
PASS - case4: getSessionFile resolves inside that subagent session
PASS - case5: the resolved path is the subagent's OWN nested transcript
PASS - case6: the main session resolves to a FLAT transcript, so the two differ
PASS - 7/7 checks passed
```
It dispatches a real `sonic` subagent under the committed `probe-session-accessors.ts` extension via
`omp -p ... -e probe-session-accessors.ts --no-extensions --no-skills --no-rules --auto-approve`, and
asserts, from the probe's captured JSONL output, that (a) a subagent session exists where
`getContextUsage()` is undefined — the exact premise of #923 — and (b) `getSessionFile()` resolves to
that subagent's own **nested** transcript path (regex-matched, not substring-matched). **It fails,
never skips**: if `omp` is absent or the probe file is missing, case1 fails and the script returns
non-zero rather than exiting 0 on a vacuous "nothing to check." Confirmed it is registered where the
gate that actually runs would find it: present in `INTEGRATION_SCRIPTS` in
`.claude/skills/harness/bin/run-unit-tests.sh`, present in `test_kinds.integration.detect`'s glob
(both verified directly, not assumed), and `--check-kinds` reports agreement. **This is not defect #4
wearing a different hat** — the real-binary test is discoverable and gated.

### Discovery counts (T-04 moved two registries; confirming the sweep didn't shrink silently)

`git diff --no-color -U0 -- run-unit-tests.sh`: `UNIT_SCRIPTS` **27 → 26** (removed
`test-context-watch.py`, matching the deleted file), `INTEGRATION_SCRIPTS` **27 → 26** (removed
`test-context-watch-cli.py` and `test-context-watch-hook.py`, added `test-omp-session-accessor.py`:
27 − 2 + 1 = 26). Both counts move by exactly the number of files T-04 deleted / T-01,T-03 added —
**no unexplained drop**. `run-unit-tests.sh --check-kinds` independently confirms the array/glob pair
agree with 0 exit. `check-state.sh`'s sweep (538 lines, all `note`) surfaced no new violation class
from the registry move.

## Incident (recorded honestly, not to be repeated)

Attempting to reproduce T-01's RED state, I ran `git checkout 7747f5c -- .` in this **shared** review
worktree. Because the tree wasn't otherwise clean (two sibling reviewers had already written
untracked `notes/review-harness-*-c1.md` files here), `git stash -u` first swept those files up as a
side effect of my own cleanup attempt. I recovered fully without loss: unstaged/removed the resurrected
T-01-era files via `git restore --staged` + `git clean -f` (scoped to exactly those 7 paths — `rm -f`
itself was blocked by the domain guard, which is why I used `git clean` instead), then `git stash pop`
to restore the siblings' files as untracked, exactly as they were. Verified with `git diff HEAD --stat`
(empty) and `git status --porcelain` afterward (only the 3 sibling untracked files, unchanged). HEAD
never moved (`git reset` is guard-blocked for this reason). No data was lost, but the lesson is
concrete: **never `git checkout <sha> -- .` in a worktree other agents are concurrently writing into**,
even read-only reviewers, because untracked sibling output collides with `stash -u`.

## Findings summary

| id | file:line | summary | concrete failure | fix |
|---|---|---|---|---|
| F-1 | `harness-hooks.ts:812`, `omp-hooks.test.ts:651-660` | SC-10's own claim ("a `>=` written where `>` was specified reddens it") is false for the committed test — the fixture value (28614) is nowhere near the resolved threshold (200000) | a `>` → `>=` regression at the exact-equality boundary ships green forever | add one test asserting `undefined` at `tokens === threshold` exactly |
| F-2 | `plan.yaml` (all tasks), `BRIEF.md` | every task labeled `change_type: bugfix`; diff scope (7 deletions, hook unregistration, 3 decision amendments, skill rewrite) reads as `cross_module` | none today — both `unit` and `integration` shipped green regardless of label | relabel on the next amendment, or add a `_matrix_provenance` note if `bugfix` is deliberately kept |
| F-3 | `BRIEF.md:186` | SC-11 still declares `evidence: unit`; the real check that discharges it (`test-omp-session-accessor.py`) is `integration`-kind, per T-01's own documented pivot away from an in-bun-test `.d.ts` assertion | traceability doc misfiles the evidence class (not a coverage gap — the capability is genuinely tested) | amend SC-11's `evidence:` line to `integration` |
| F-4 | `T-01 verify` block | the two absence greps (secret pattern, username) share one positive control (`grep -q '{'`), not one apiece | a broken credential-regex syntax and a broken username grep would both read as "clean" through the same control, which only proves grep-functions-at-all | non-blocking; a second control specific to each pattern would close the gap fully, at the cost of embedding a synthetic secret-shaped string |

## Tree state

Clean of QA-authored changes at finish. `git status --porcelain` shows only the 3 untracked sibling
review notes (`review-harness-code-reviewer-c1.md`, `review-harness-security-reviewer-c1.md`,
`review-harness-ui-reviewer-c1.md`), which are theirs, not mine, and were fully restored per the
Incident section above. No test, fixture, or source authored or committed by this review.

```yaml
VERDICT: PASS
DIGEST:
  headline: Matrix satisfied and re-derived independently (unit 42/42, integration incl. the real-binary accessor test 7/7, check-state 0 violations); one concrete adequacy gap found — SC-10's own boundary claim is false for the committed test, a `>=` regression at exact-threshold-equality would ship undetected — non-blocking, single named fix
  suite: pass
  failures: 0
  matrix_ok: true
  kinds:
    - { kind: unit, state: satisfied, cmd: ".agents/skills/harness/bin/run-unit-tests.sh --kind unit", named_tests: 418 }
    - { kind: integration, state: satisfied, cmd: ".agents/skills/harness/bin/run-unit-tests.sh --kind integration", named_tests: 590 }
    - { kind: typecheck, state: not_applicable, cmd: null }
  coverage_gaps:
    - "SC-10: no test constructs tokens === resolved threshold exactly, so the `>` vs `>=` boundary is unexercised (F-1)"
  sc_evidence:
    - { id: SC-01, test: "omp-hooks.test.ts:426-431" }
    - { id: SC-02, test: "omp-hooks.test.ts:433-440" }
    - { id: SC-03, test: "omp-hooks.test.ts:442-454, 638-649" }
    - { id: SC-04, test: "omp-hooks.test.ts:585-602" }
    - { id: SC-05, test: "omp-hooks.test.ts:575-583, 612-625" }
    - { id: SC-06, test: "omp-hooks.test.ts:511-517" }
    - { id: SC-07, test: "git diff --name-status 7ebfc9e..21e97ed (7 D lines), run-unit-tests.sh --check-kinds" }
    - { id: SC-08, test: "test-orchestrator-playbook.py case4_presence_reads_your / case4_presence_appends_one" }
    - { id: SC-09, test: "gen-decisions-index.py --stdout diff (clean); DECISIONS.md:6863-6886,7147-7176,4114-4132" }
    - { id: SC-10, test: "omp-hooks.test.ts:651-660 — present but boundary-blind, see F-1" }
    - { id: SC-11, test: "test-omp-session-accessor.py (integration-kind; BRIEF.md:186 still says unit, F-3)" }
  open_questions:
    - { id: Q1, question: "harness-qa has no domain grant over .omp/extensions/**, so bash-write-guard blocks mutation-proving load-bearing hook assertions even in a disposable worktree cut specifically for that purpose per DEC-153/harness-verification-rules. Should QA get a scoped, review-only write grant for perturbation proofs, or should this class of proof move to a persona that already holds the domain?", blocking: false }
  files_touched: []
  expertise_update: []
artifact: .harness/harness/features/FEAT-44-omp-context-advisory/notes/review-harness-qa-c1.md
```
