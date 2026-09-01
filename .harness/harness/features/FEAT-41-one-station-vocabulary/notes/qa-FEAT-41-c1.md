# QA gate — FEAT-41-one-station-vocabulary — cycle 1 — review_sha fc08375 (base 9f2a070)

Worktree confirmed: `pwd` and `git rev-parse --show-toplevel` both resolve to
`.claude/worktrees/harness/FEAT-41-one-station-vocabulary`; `HEAD` (014f345) is one commit ahead
of the pin (feature.json re-pin only, `git diff --stat` confirms). All measurements below ran
against this checkout at the pin's source state.

BLUF: **SC-11 is RESOLVED — PASS.** A clean serial run, solely owned, reproduces the baseline
exactly: unit exit 0/505 PASS/0 FAIL, integration exit 0/816 PASS/0 FAIL (including
`test-bash-write-guard.py` passing cleanly — cycle 0's confound does not reproduce standalone),
check-state.sh exit 0/0 VIOLATION/0 traceback, code-grade 0 HIGH/6 grade-2. F-01..F-05 hold at
source, each mechanically stronger than claimed in one respect and each with one real gap: F-02's
"two independent layers" claim has no standing test that isolates them, and F-04's fix widened to
all six shape patterns but only one (plan.yaml) has a standing case-insensitivity test. Neither
gap is a live defect — both are coverage debt on a real fix. SC-08 fails **literally** (BUG-1071's
feature.json still carries `status: "Review"`) though the fix's own scope is intent-satisfied;
this is the disclosed, deliberately-unfixed item, not a build regression, and I rule it correctly
disposed at `note` severity, matching the dispatch's framing.

## 1. Baseline reproduction — serial, solo, this session owned both suites throughout

| check | expected | observed |
|---|---|---|
| `run-unit-tests.sh --kind unit` | exit 0, 505 PASS, 0 FAIL | **matches**: exit 0, 505 lines matching `^PASS ` (33 scripts, all green), 0 `^FAIL ` |
| `run-unit-tests.sh --kind integration` | exit 0, 816 PASS, 0 FAIL | **matches**: exit 0, 816 `PASS`-prefixed lines (28 scripts, all green), 0 `not ok`/`^FAIL `, `test-bash-write-guard.py` line 766 `PASS` |
| `check-state.sh` | exit 0, 0 VIOLATION, 0 traceback | **matches**: exit 0, `grep -c VIOLATION` = 0, `grep -ic traceback` = 0 |
| `code-grade.py --base 9f2a070 --head fc08375` | 0 gated HIGH, 6 gated grade-2 | **matches**: 105 PASS, 6 `RESULT: FAIL` all at `GRADE: 2` (`_verify_spliced`, `_task_status_line`, `cmd_sign_approval.transform`, `denies`, `case_set_task_station_one_line`, `case_f02_sign_approval_cannot_write_an_unparseable_signature`) — none gated HIGH |

**SC-11 resolution.** Cycle 0's confound — qa measured `test-bash-write-guard.py` failing 2/2
inside a full-suite run that overlapped the code reviewer's own concurrent run in the same
checkout — does **not** reproduce here. This run was the only process executing in this worktree
for its full 3m23s duration (unit finished first, serially, before integration started; no other
job of mine touched this tree concurrently). `test-bash-write-guard.py` passed cleanly at line
766. **SC-11 is PASS**, not BLOCKED: the whole suite is green and `check-plan-routes.py`'s own
exit code (exercised inside T-06/T-14's own verifies, both cross_module `always`-required and
green above) is 0 over every live plan including this one.

## 2. Test-matrix gate

Change types present in `plan.yaml` (16 tasks): config×4, cross_module×4, logic×3, docs×2, api×1,
bugfix×2. Resolved against `.harness/harness.json`'s matrix:

| kind | required by | state | evidence |
|---|---|---|---|
| unit | logic/api/bugfix (`always`), cross_module (`always`) | **satisfied** | `run-unit-tests.sh --kind unit`, 505 PASS |
| integration | cross_module (`always`) | **satisfied** | `run-unit-tests.sh --kind integration`, 816 PASS |
| api's `integration` (`touches_db_or_external`) | not triggered | n/a | T-03 (plan-merge.py) touches no DB/external service |
| bugfix's `__bug_class__` (`match_bug_class`) | not triggered | n/a | no `bug_class` field on any task |
| component / ui / eval | not required | **not applicable** | 171-file diff (base..pin) has zero matches for `*.spec.tsx`/`*.stories.(tsx\|ts)`, `tests/e2e/**`/`*.e2e.spec.ts`, `evals/**` |
| typecheck | not in matrix | not applicable | zero `.ts`/`.tsx` in the diff |

`matrix_ok: true`. Every required kind ran with an active command and named tests; no null `cmd`.

## 3. Per-commit test-first audit (`base..review_sha`)

| commit | claim | measured |
|---|---|---|
| 787c7fa (F-01) | test added with fix | **holds** — `git show --stat` shows `gh-sync.py` (+23/-3) and `test-gh-sync.py` (+48) in the same commit; new block reads gate literals out of `post-merge-sweep.sh` via regex rather than retyping them |
| 8c2972e (F-02) | test added with fix | **holds** — `plan-merge.py` and `test-plan-merge.py` both touched in this commit; six hostile-value cases added |
| dee7225 (F-03) | test added with fix, "mutated the regex back to prove discriminates" | **holds** — `plan-sign-gate.py` and `test-plan-sign-gate.py` both touched; message documents a mutation-back proof for the fallback case (not independently re-run by me, accepted as commit-message evidence per cycle-0's own standard for this class of claim) |
| 6eda94d (F-04) | test added with fix | **holds** — `check-domain.sh` and `test-check-domain.py` both touched; case 8 added under `run_t09` |
| 9bdbe91 (F-05 pt 3) | pure refactor, "held BYTE-IDENTICALLY" | **holds as a refactor claim** — this is grade repair (extracting `_landed_blob_text`), not new-behavior TDD; no new test-first obligation applies. Not independently diffed byte-for-byte by me; accepted on the commit's own description, consistent with cycle-0's treatment of T-16's fixture-debt repair as a different shape of compliance |
| 57892bd (D-15 + F-05 pt2) | decision recorded, two grade regressions repaid | **holds** — plan.yaml diff is additive only (checked: D-15 decision block present at plan.yaml:161-187, `dec: DEC-174`); no test-first question applies to a decision record |
| c248019 (F-05 pt1) | "All 26 T-09 assertions preserved and still running — counted, not assumed" | **holds** — `run_t09` split into `_t09_edit_denial`/`_t09_binds_every_author`/`_t09_post_sweep`/`_t09_spelling`, all four called from `run_t09` (confirmed at test-check-domain.py:2675-2683) |
| 8fa2d04 (D-16) | INV-32→INV-33 renumber, T-18 struck | **holds** — `check-state.sh` carries both `# INV-32 BEGIN (FEAT-45 T-07)` and FEAT-41's own INV-33 block (test-check-state.py:3328 onward) side by side; not a test-first case (renumber + strike, not new behavior) |

## 4. New-test binding verification (dispatch item 5)

**F-01 — CONFIRMED, both directions, exactly as claimed.**
- `_record_station` (gh-sync.py:571-631): both failure prints (absent plan.yaml at :618, non-zero
  `set-feature-station` exit at :627-628) read `gh-sync: FAILED —`. Test drives both branches
  (`test-gh-sync.py`, the F-01 block) and asserts the gate literal is present, read dynamically
  via `_GATE_LITERALS = re.findall(r'if "([^"]+)" in combined:', open(...post-merge-sweep.sh...).read())`
  — genuinely reads the gate's own literals, not a retyped copy.
- `_commit_terminal_station` (gh-sync.py:649-700): both failure branches (`git status` failure,
  `git commit` failure) print `gh-sync: WARNING -`, neither gate word. Asserted by the pre-existing
  T-10 "no git repository" case immediately above the F-01 block (`"gh-sync: SKIP" not in bothN
  and "gh-sync: FAILED" not in bothN`) — this one is a hardcoded literal comparison, not read
  dynamically, but it is the correct direction and it passes.
- Asymmetry is real and both directions bind. **No gap.**

**F-02 — the round-trip is solidly tested; the "two independent layers" claim is NOT.**
`case_f02_sign_approval_cannot_write_an_unparseable_signature` (test-plan-merge.py:745-813) drives
all six hostile values (`Dr: Bob`, `#845 owner`, `yes`, `Bob:`, quote, embedded newline) through
`sign-approval` and asserts, per case, either a byte-identical refusal or a value-correct write —
covering all three failure classes the commit claims, including both classes that parse cleanly
(`#845 owner`→comment-swallow, `yes`→boolean coercion). This is solid.
**Gap: I grepped `test-plan-merge.py` for `_field_lines` and `_verify_signature` and found zero
hits outside the source file itself.** No standing test monkeypatches or otherwise disables
`_field_lines`'s escaping to prove `_verify_signature` catches the resulting corruption on its
own — the commit message's claim ("mutating `_field_lines` back to raw interpolation leaves all
three unparseable classes REFUSED... boolean coercion included") describes a **one-off manual
probe during development, never encoded as a test**. `_verify_signature` is wired (called at
plan-merge.py:864), so it is not dead code, but its refusal branch is exercised today only as a
side effect of the six hostile-value cases succeeding without ever needing it (per the commit's
own "PROVED THE NET IS NOT DEAD WEIGHT... with escaping in place no case requires it" — meaning
the net's refusal branch has **never actually fired** in the standing suite). **Coverage gap,
named per DEC-174: `test-plan-merge.py`, a case asserting `_verify_signature` refuses when
`_field_lines`'s escaping is bypassed (e.g., via a raw-interpolation stand-in for one hostile
value) — currently absent.**

**F-03 — CONFIRMED, both token scan and text fallback, with negative controls.**
`test-plan-sign-gate.py:169-222`: token-scan separator skip case (`-- sign-approval` denied),
negative control for over-widening (`apply --proposal q.yaml # not a sign-approval call` still
allowed), text-fallback separator skip case (`plan-merge.py -- sign-approval` via an unlexable
line, denied), and the fallback's own negative control (unlexable non-signing line, allowed). All
four green. **No gap.**

**F-04 — plan.yaml's case-insensitivity is solidly tested; the other five patterns are NOT.**
`test-check-domain.py:2638-2672` (`_t09_spelling`) drives `Plan.yaml`/`PLAN.YAML`/`plan.YAML`
through the write-denial route (all DENIED) with a negative control (`plan.yaml.bak`,
`myplan.yaml`, still ALLOWED — the pattern is anchored, not substring). **The source fix widened
`_I = re.IGNORECASE` onto all six patterns** (`RE_FEATURE_JSON`, `RE_STATE_YAML`, `RE_HANDOFF`,
`RE_STATE_MD`, `RE_CLAUDE_MD`, `RE_PLAN_YAML` — confirmed at source, check-domain.sh:1037-1046),
and the commit message claims "Verified all six fold" — but I grepped `test-check-domain.py` for
`Feature.json`, `Claude.md`, `State.md`, and `Handoff-` (any case-variant of the other five
patterns) and got **zero hits**. Only one of six patterns has a standing case-insensitivity test;
the other five widenings are unverified by anything in the suite, resting on commit-message prose
only. **Coverage gap, named per DEC-174: `test-check-domain.py`, cases asserting a case-folded
`Feature.json`/`State.YAML`/`Handoff-x.MD`/`STATE.MD`/`Claude.MD` write is BLOCKED (budget) or
DENIED as appropriate — currently absent for five of six patterns.**
The realpath non-reproduction is correctly recorded as prose in the test file's own comment
(test-check-domain.py:2647-2651), not silently dropped — matches the dispatch's ask.

**F-06 (cycle-0 med, `_verify_spliced`) — STILL STANDS, unchanged.** `grep -n "_verify_spliced"
test-plan-merge.py` returns zero hits. No case forces either refusal branch (unparseable reload;
dropped/mismatched task id). Not addressed by any of F-01..F-05 (correctly — it was never in the
must-fix list) and not claimed fixed by the handoff. Named again so it is not lost.

**F-07 (cycle-0 med, `worktree_terminal.py:213-221` MissingDependency dispatch) — STILL STANDS.**
9bdbe91 extracted `_landed_blob_text` from `_read_landed_plan_yaml` for grade reasons only ("held
BYTE-IDENTICALLY"); `grep -n "MissingDependency\|_landed_blob_text" test-worktree-terminal.py`
returns zero hits. The wiring at worktree_terminal.py:231-232 remains covered only incidentally,
by whatever PyYAML's install location happens to be on the machine running
`test-post-merge-sweep.py`'s subprocess. Unchanged from cycle 0.

**INV-32→INV-33 renumber — both suites' cases are present and green side by side** (confirmed:
check-state.sh carries both `# INV-32 BEGIN (FEAT-45 T-07)` at :264 and FEAT-41's own INV-33
block from :3328 in the test file, both exercised in the green `test-check-state.py` run above).
**Not measured: whether either invariant's assertions pass on the other's output.** I found no
cross-mutation case (e.g., feeding an INV-33-shaped fixture through INV-32's grader or vice versa)
in the time available. This is a gap in my own audit depth, not a confirmed defect — reported as
unverified rather than asserted either way.

## 5. SC-01..SC-14 — method and evidence, each criterion's own command run verbatim

| SC | verdict | method | evidence |
|---|---|---|---|
| SC-01 | PASS | automated | `grep -rn --exclude-dir=__pycache__ "_STATION_KEYS" .claude/skills/harness/bin/` → 0 hits (exit 1, i.e. grep found nothing) |
| SC-02 | PASS | automated | criterion's own quoted-literal grep, verbatim → 0 lines |
| SC-03 | PASS | automated | criterion's own anchored `python3 -c` assertion → exit 0 |
| SC-04 | PASS | automated | `grep -rn "gh_board.set_station(" --include=*.py .../bin/` excluding tests → 4 sites |
| SC-05 | PASS (struck) | inspection | struck with T-13, recorded not deleted; PB-07 carries the coverage loss, unchanged this cycle |
| SC-06 | PASS | automated | `test-check-domain.py` exit 0, F-04 case block green (post-sweep coverage unchanged from cycle 0's PASS) |
| SC-07 | PASS | automated | `test-plan-sign-gate.py` exit 0, all F-03 cases + negative controls green — **flips from cycle 0's FAIL**: F-03 closed the bypass the criterion's own assertion could not see before |
| SC-08 | **FAIL as literally worded; intent-satisfied** | automated | `python3 -c "..."` scanning every `feature.json` for a `status` key → **one hit**: `.harness/harness/features/BUG-1071-inv32-era-guard/feature.json` still carries `"status": "Review"`. See §6 — this is the disclosed, deliberately-unfixed item, not a regression from this feature's own work. The eleven former readers this feature repointed are confirmed off `plan.yaml` (T-07's migration); BUG-1071 has no `plan.yaml` to repoint to. |
| SC-09 | PASS | inspection | `git show fc08375:.../FEAT-40.../plan.yaml` carries top-level `status: done`; `check-state.sh` full run emits zero `INV-26` lines for any feature |
| SC-10 | PASS | automated | `test-gh-sync.py` exit 0, F-01 cases green; T-10's worktree-refusal and commit-clean-against-HEAD cases unchanged from cycle 0's PASS |
| SC-11 | **PASS — RESOLVED** | automated | §1 above: clean serial run, both suites and check-state.sh exit 0 at expected counts |
| SC-12 | PASS (struck) | inspection | struck with T-13 exactly as pre-authorized; no coverage lost per D-01 |
| SC-13 | PASS | automated, integration | `grep -n "_EXPECT" check-state.sh` → 0 hits; `test-check-state.py` exit 0, INV-26 fixture cases (v.T06-pending etc.) green, no `if _want is None: continue` skip survives |
| SC-14 | PASS | automated | T-15's own verify script, run verbatim → exit 0, "three amendment records present, three amended clauses still standing" |

## 6. BUG-1071 disposition ruling

**Agree with the recorded disposition: `note`-level, not blocking, and correctly so.**
`BUG-1071-inv32-era-guard/feature.json` carries `status: "Review"` (pre-migration vocabulary) and
no `plan.yaml` exists to hold a station instead. Creating one to satisfy T-07's migration would be
fabricating a planning document for a feature this session did not build — exactly what the
dispatch and PRINCIPLES rule 15 forbid. `check-state.sh` emits no violation for it (I confirmed:
the tool has no schema-validation pass over resting `feature.json` files at all — `grep -n
"feature_schema\|additionalProperties" check-state.sh` is empty; schema enforcement in this
feature binds only the *write* path via `check-domain.sh`, never a read-time scan of files already
on disk), so nothing is silently gated shut by it. **The one place this bites is SC-08's literal
wording**, which the criterion's own text does not carve an exception into. I am not softening
that: SC-08 as written is measurably false today, by exactly one file, for a reason outside this
feature's own scope. Recommend the operator either accept the disclosed exception explicitly (a
one-line addendum to SC-08 naming BUG-1071) or treat it as a standing, tracked backlog item —
either is fine; leaving it unstated is not, because the next reader who runs SC-08's grep gets a
false PASS/FAIL signal with no context.

## DIGEST

```yaml
VERDICT: PASS
DIGEST:
  headline: SC-11 is RESOLVED (PASS) — one clean, solely-owned serial run reproduces the baseline exactly on both suites; F-01..F-05 hold at source with two real coverage gaps (F-02's layer-independence claim, five of six F-04 shape patterns) neither of which is a live defect, and SC-08 fails literally only through the disclosed, correctly-unfixed BUG-1071 item.
  suite: pass
  failures: 0
  matrix_ok: true
  kinds:
    - { kind: unit, state: satisfied, cmd: ".claude/skills/harness/bin/run-unit-tests.sh --kind unit", named_tests: 505 }
    - { kind: integration, state: satisfied, cmd: ".claude/skills/harness/bin/run-unit-tests.sh --kind integration", named_tests: 816 }
    - { kind: component, state: not_applicable, cmd: null }
    - { kind: ui, state: not_applicable, cmd: null }
    - { kind: eval, state: not_applicable, cmd: null }
    - { kind: typecheck, state: not_applicable, cmd: null }
  coverage_gaps:
    - "test-plan-merge.py: no case disables _field_lines's escaping to prove _verify_signature's refusal branch fires independently (F-02's 'two independent layers' claim is commit-message-only, never encoded as a test)"
    - "test-check-domain.py: only RE_PLAN_YAML has a case-insensitivity case (F-04); RE_FEATURE_JSON/RE_STATE_YAML/RE_HANDOFF/RE_STATE_MD/RE_CLAUDE_MD's identical widening is untested, resting on commit-message prose only"
    - "test-plan-merge.py: zero hits for _verify_spliced — cycle-0 F-06 still stands, neither refusal branch (unparseable reload, dropped/mismatched task id) is forced by any case"
    - "test-worktree-terminal.py: zero hits for MissingDependency/_landed_blob_text — cycle-0 F-07 still stands, the exception-dispatch wiring in _read_landed_plan_yaml is covered only incidentally by this machine's PyYAML install location"
    - "no cross-mutation case proves INV-32 and INV-33's assertions cannot pass on each other's fixture output (renumber correctness reasoned from side-by-side green, not independently proven)"
  sc_status:
    - { id: SC-01, verdict: PASS, method: automated, evidence: "criterion's own grep verbatim, 0 hits" }
    - { id: SC-02, verdict: PASS, method: automated, evidence: "criterion's own quoted-literal grep verbatim, 0 lines" }
    - { id: SC-03, verdict: PASS, method: automated, evidence: "criterion's own anchored python3 -c assertion, exit 0" }
    - { id: SC-04, verdict: PASS, method: automated, evidence: "set_station( outside tests, whole tree: exactly 4 sites" }
    - { id: SC-05, verdict: PASS, method: inspection, evidence: "struck with T-13, recorded not deleted, unchanged this cycle" }
    - { id: SC-06, verdict: PASS, method: automated, evidence: "test-check-domain.py exit 0, F-04 post-sweep coverage unchanged" }
    - { id: SC-07, verdict: PASS, method: automated, evidence: "test-plan-sign-gate.py exit 0, F-03 cases + negative controls green — flips from cycle-0 FAIL" }
    - { id: SC-08, verdict: FAIL, method: automated, evidence: "one feature.json (BUG-1071-inv32-era-guard) still carries a status key — literally unmet; disclosed and correctly disposed per §6, not a build regression" }
    - { id: SC-09, verdict: PASS, method: inspection, evidence: "git show fc08375:.../FEAT-40.../plan.yaml has top-level status: done; check-state.sh 0 INV-26 lines" }
    - { id: SC-10, verdict: PASS, method: automated, evidence: "test-gh-sync.py exit 0, F-01 + T-10 cases green" }
    - { id: SC-11, verdict: PASS, method: automated, evidence: "clean serial run: unit 505/0, integration 816/0, check-state.sh 0/0, both exit 0 — RESOLVED, cycle-0 confound does not reproduce standalone" }
    - { id: SC-12, verdict: PASS, method: inspection, evidence: "struck with T-13 exactly as pre-authorized, no coverage lost per D-01" }
    - { id: SC-13, verdict: PASS, method: automated, evidence: "grep _EXPECT 0 hits; test-check-state.py exit 0, INV-26 fixture cases green" }
    - { id: SC-14, verdict: PASS, method: automated, evidence: "T-15's own verify script run verbatim, exit 0" }
  severity_max: none
  open_questions:
    - { id: Q1, question: "SC-08's literal wording has no carved exception for BUG-1071's plan.yaml-less feature.json. Should the criterion get a one-line addendum naming the exception, or should BUG-1071's status-key migration become a tracked backlog item? Either resolves the false signal a future SC-08 re-run would otherwise give.", blocking: false }
    - { id: Q2, question: "Should test-plan-merge.py gain a case that disables _field_lines's escaping to independently prove _verify_signature's refusal branch fires (F-02), and should test-check-domain.py gain case-insensitivity cases for the other five shape patterns (F-04)? Both are coverage debt on real, correct fixes, not defects — naming per DEC-174, not writing.", blocking: false }
  files_touched: []
  expertise_update: []
artifact: .harness/harness/features/FEAT-41-one-station-vocabulary/notes/qa-FEAT-41-c1.md
```
