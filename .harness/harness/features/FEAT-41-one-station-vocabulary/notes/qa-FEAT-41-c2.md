# QA gate — FEAT-41-one-station-vocabulary — cycle 2 — review_sha 39477a502cd6726f01ad403dbdb4222c26969d2e (base 7c4f0bd)

Worktree confirmed: `pwd` and `git rev-parse --show-toplevel` both resolve to
`.claude/worktrees/harness/FEAT-41-one-station-vocabulary`. `HEAD` (9a9f5ce) is one commit ahead of
the pin (`re-pin review_sha for re-review cycle 2` — a `feature.json` metadata-only commit,
confirmed by `git show --stat`). All measurements ran against this checkout at the pin's source
state; `git diff --stat 7c4f0bd..39477a5` confirms 177 files / 12795(+) / 1338(-).

**BLUF: FAIL.** H-01 and H-02 hold at source, mutation-confirmed load-bearing. The `_verify_signature`
forcing case is honest — it discriminates the guard, not the YAML loader (proved with both a
refuse-all and an accept-all stub). But the `_I` case-fold fix only closed 4 of 6 patterns
(`RE_STATE_YAML` and `RE_CLAUDE_MD` remain provably unpinned — zero test failures when either
loses `_I`, exactly cycle 1's original defect, just narrower). More importantly, **the carried HIGH
finding — `set-task-station`/`set-feature-station` accept no caller identity and are wide open to
an ordinary Bash call — still reproduces exactly as described**, unresolved by anything in this
cycle's diff. Baseline reproduces cleanly; SC-08 is disclosed-false by exactly one file as claimed.

## 1. Baseline reproduction — serial, solo, this session owned both suites and check-state.sh throughout

| check | expected | observed |
|---|---|---|
| `run-unit-tests.sh --kind unit` | exit 0, 505 PASS | **matches**: exit 0, 505 `^PASS ` lines, 0 `^FAIL `. 31 scripts declared in `UNIT_SCRIPTS`, all 31 seen as script-level `PASS <name>.py` markers (one extra `.py`-suffixed line, `case_floor_inflight_registry.py`, is a subcase name, not a 32nd script) — full discovery, no shrinkage. 20.6s wall. |
| `run-unit-tests.sh --kind integration` | exit 0, 819 PASS | **matches**: exit 0, 819 `^PASS ` lines, 0 `^FAIL `. 28 scripts declared in `INTEGRATION_SCRIPTS`, all 28 seen as script-level `PASS <name>.py` markers, set-equal both directions (`declared == seen`). 3m11s wall. |
| `check-state.sh` | exit 0, 0 violations, 0 tracebacks | **matches**: exit 0, `grep -ic violation` = 0, `grep -ic traceback` = 0. 14.9s wall. |
| gated HIGH code-grade records | 0, new `code-grade.py --base 7c4f0bd --head 39477a5` | **matches**: 107 `RESULT: PASS`, 8 `RESULT: FAIL`, all 8 at `GRADE: 2`/`SEVERITY: med` — zero at grade 3/HIGH. Qualnames: `_verify_spliced`, `_task_status_line`, `cmd_sign_approval.transform`, `denies`, `_t09_symlink`, `_t09_case_fold`, `case_set_task_station_one_line`, `case_f02_sign_approval_cannot_write_an_unparseable_signature` (two of these — `_t09_symlink`, `_t09_case_fold` — are this cycle's own new fixture functions, gated at grade 2 for their own size, not HIGH). |

Note on `--kind unit` coverage (per handoff's own Dead End): 31 unit + 28 integration = 59 scripts
declared and discovered this run, up from the "29 of 56" the handoff cites — the declared-script
count itself grew across the rebase/migration. Both kinds' declared sets were fully discovered
(no glob shrinkage), confirmed above by set-equality, not by exit code alone.

**Suite-owner note:** I was the sole process executing `run-unit-tests.sh`/`check-state.sh` in this
worktree for the full ~3.5 minutes; no other job of mine touched the tree during either run.

## 2. Mutation re-run 1 — `_I` case-fold patterns (check-domain.sh)

Baseline `run_t09()` (imported as a module, isolated from the rest of the suite): **0 fails.**

Ran the SAME mutation shape (drop `_I` from one `re.compile` call) across **five** of the six
patterns, restoring with `git checkout --` between each and confirming `git status --porcelain`
clean after every restore:

| pattern mutated | rows in `_FOLD_ROWS` | result |
|---|---|---|
| `RE_FEATURE_JSON` | yes | **1 fail** — `T-09 10: Feature.json over budget is DENIED` reds, nothing else |
| `RE_HANDOFF` | yes | **1 fail** — `T-09 10: Handoff-Build.md over budget is DENIED` reds, nothing else |
| `RE_STATE_MD` | yes | **1 fail** — `T-09 10: State.md over budget is DENIED` reds, nothing else |
| `RE_STATE_YAML` | **no** | **0 fails** — same defect class cycle 1 found, still present for this pattern |
| `RE_CLAUDE_MD` | **no** | **0 fails** — same defect class cycle 1 found, still present for this pattern |

**Finding (MED, coverage gap, not a live defect but only a partial closure of cycle 1's own
finding).** `test-check-domain.py`'s `_FOLD_ROWS` (lines 2774-2779) has exactly three rows:
`feature.json`, `handoff-build.md`, `STATE.md`. `RE_PLAN_YAML` is covered separately (case 8). That
leaves `RE_STATE_YAML` and `RE_CLAUDE_MD` — two of the six `_I`-widened patterns — exactly as
unpinned as cycle 1 found five of six to be. The commit message's own comment
(`test-check-domain.py:2773`, "except RE_PLAN_YAML, which case 8 above already covers") implies the
table means to cover the other five; it covers three. **Named per DEC-174:
`test-check-domain.py`, two rows to add to `_FOLD_ROWS` (or an equivalent case) — a folded
`STATE.YAML`/canonical `state.yaml` pair under `runs/<run>/`, and a folded `Claude.MD`/canonical
`CLAUDE.md` pair — currently absent.**

## 3. Mutation re-run 2 — `_verify_signature` (plan-merge.py)

Baseline `test-plan-merge.py`: exit 0, 0 `^FAIL` lines (187 case lines, all `PASS`).

**Accept-all stub** (early `return`, i.e. cycle 1's original disable): exit 1, **3** assertion
fails, all three inside `case_f02_verify_signature_is_not_dead_code` (exit-5 check, message-content
check, byte-identity check) — matches the handoff's claimed count exactly.

**Refuse-all stub** (`raise MergeRefusal(5, [...])` unconditionally, new this cycle): exit 1, **6**
assertion fails — every ordinary `sign-approval` case (`sign-approval exits 0`, writes `status`,
`approved_by`, `date`, leaves nothing behind, the F-02 negative control) plus the layer-two
message-content check (which now fails for the opposite reason: message text differs from the
stub's, not absence of a refusal). Critically, the **layer-two exit-5 check itself now passes** —
"a signature that would reload as a DIFFERENT name is REFUSED at exit 5" — since the stub always
refuses.

**Honesty judgement: the forcing case exercises the guard, not the YAML loader.** The two stubs
move disjoint sets of cases (3 vs 6, only the message-content sub-check overlaps, and it fails for
opposite reasons under each stub). The duplicate-`approved_by` scenario specifically requires the
real comparison logic to be present and correct: under accept-all it fails because nothing refuses
a mismatched reload; under refuse-all its exit-5 assertion passes (correctly, since exit 5 is
generic) but every ordinary, non-hostile signing also breaks, proving the guard is wired into the
live write path for every call, not merely reachable via a contrived fixture. A guard that only
watched the YAML loader would not move any of the six ordinary-case assertions under a
refuse-everything stub, since the loader itself never refuses. It does. **Genuinely discriminating,
not YAML-loader-only.**

Both files restored via `git checkout --` after each mutation; `git status --porcelain` on
`check-domain.sh` and `plan-merge.py` confirmed clean after every restore (final check at the end
of this note, together with `plan-sign-gate.py`).

## 4. Test-matrix gate

16 tasks in `plan.yaml`: config×4, cross_module×4, api×1, docs×2, bugfix×2, logic×3. Resolved
against `.harness/harness.json`'s `test_matrix` (unchanged from cycle 1/0's reading, re-checked at
this pin):

| kind | required by | state | evidence |
|---|---|---|---|
| unit | logic/api/bugfix (`always`), cross_module (`always`) | **satisfied** | §1, 505 PASS, exit 0 |
| integration | cross_module (`always`) | **satisfied** | §1, 819 PASS, exit 0 |
| api's `integration` (`touches_db_or_external`) | not triggered | n/a | T-03 (plan-merge.py) touches no DB/external service — confirmed at source, local file I/O only |
| bugfix's `__bug_class__` (`match_bug_class`) | not triggered | n/a | `grep bug_class plan.yaml` — 0 hits, no task carries the field |
| component / ui / eval | not required | **not applicable** | `git diff --name-only 7c4f0bd..39477a5 \| grep -E '\.spec\.tsx$\|\.stories\.(tsx\|ts)$\|tests/e2e/\|\.e2e\.spec\.ts$\|evals/'` — 0 hits |
| typecheck | not in matrix | not applicable | same diff, 0 `.ts`/`.tsx` files |

`matrix_ok: true`. Every required kind ran with an active command and named tests; no null `cmd`.

**Guard reachability, beyond presence.** For the diff's two highest-value guards I did not stop at
"a test exists" — §2 and §3 above, plus the H-01/H-02 mutation proofs in §5, establish RED on
removal for: `_route_candidates`'s symlink walk (H-01), `as_bash_reads_it`'s continuation-join
(H-02), `_verify_signature`'s comparison loop, and three of six `_I` case-fold widenings. Two of
six `_I` widenings (`RE_STATE_YAML`, `RE_CLAUDE_MD`) do **not** red on removal — named as the §2
finding, not asserted satisfied.

## 5. H-01 / H-02 closures re-verified at source, by mutation

**H-01 (`check-domain.sh` `_route_candidates`/`_plan_route`, lines 1490-1513).** Baseline
`run_t09()`: 0 fails. Mutated `_route_candidates` to `return [_norm(path)]` (no symlink walk):
**3 fails** — both the symlink-denial case and the refusal-names-the-target case, plus the POST
reporter case. Restored, `git status --porcelain` clean. Uses `readlink`-walking
(`os.readlink`/`os.path.islink` per hop, capped at `_MAX_HOPS`), not `realpath` — confirmed at
source, matches the Dead Ends entry exactly (never substitutes resolution for shape matching).

**H-02 (`plan-sign-gate.py` `as_bash_reads_it`/`CONTINUATION`, lines 112-127).** Baseline
`test-plan-sign-gate.py`: exit 0, 0 fails. Mutated `as_bash_reads_it` to a no-op (`return line`):
**2 fails** — both the token-scan and the text-fallback continuation cases. Restored, `git status
--porcelain` clean. Fixed once (`as_bash_reads_it` is called before either scanner runs, line 131),
exactly as the handoff claims — not two separate backslash-aware scanners.

## 6. Carried finding, re-measured at this pin: `set-task-station`/`set-feature-station` have no caller-identity binding

**STILL REPRODUCES. Not addressed by anything in `7c4f0bd..39477a5`.**

`plan-sign-gate.py`'s own docstring (lines 21-24) states the scope directly: "IT DENIES ONE VERB,
NOT THE TOOL. `apply`, `add-tasks`, `set-task-station` and `set-feature-station` are the
orchestrator's legal routes and stay open." `plan-merge.py`'s `cmd_set_task_station` (line 719) and
`cmd_set_feature_station` (line 797) validate only that `--station` is a legal vocabulary value
(`_legal_stations`) — no `agent_type`, no caller identity, no binding to the feature the CLI
invocation claims to be for.

**Reproduced under `$TMPDIR` (never inside the tracked worktree), via the `write` tool for fixture
creation and `bash` only to invoke the CLI directly — not a suite run:**

```
$ python3 .../plan-merge.py set-feature-station --file .harness/harness/features/FEAT-99-victim/plan.yaml --station done
STATION .../FEAT-99-victim/plan.yaml -> done
APPLIED .../FEAT-99-victim/plan.yaml
$ echo $?
0
```
No stderr. A fixture "victim" plan carrying `status: building` is silently, successfully flipped to
`status: done` by one ordinary Bash invocation, with the same caller-identity gap the cycle-1
security member reported. `T-08`'s identity check (`plan-sign-gate.py`) covers `sign-approval`
only, by design and by its own docstring — it was never meant to, and does not, cover these two
verbs. **This is unresolved, still HIGH, and belongs to the operator's disposition (accept as
disclosed scope, per the BRIEF's own "A disclosure, not a decision" note at BRIEF.md:109-112 — which
covers a shell write of a *legal station value*, i.e. exactly this — or open a follow-up).** The
BRIEF's disclosure at 109-112 does appear to already name this exact gap ("a shell command that
writes a legal station value into plan.yaml is still not attributable to its author... Closing that
would need write attribution the platform does not offer"), which weighs toward "disclosed, not a
regression" rather than "missed" — but the cycle-1 lead's digest that would have recorded this
disposition explicitly was never written to the run dir, so I cannot confirm it was ever actually
weighed against the BRIEF's disclosure rather than simply dropped. Flagging both the reproduction
and the unresolved disposition status.

## 7. Per-commit test-first audit, `42bc5fe..39477a5`

| commit | claim | measured |
|---|---|---|
| `42bc5fe` (H-01+H-02, = `707b547` pre-rebase, identical diffstat) | fix + test together | **holds** — `check-domain.sh`+`test-check-domain.py`, `plan-sign-gate.py`+`test-plan-sign-gate.py`, all four in one commit |
| `c4da870` (two coverage gaps, = `5dc5374` pre-rebase, identical diffstat) | test-only, no production change needed | **holds, and correctly test-only** — `test-check-domain.py`+`test-plan-merge.py` only. No source change is required because both guards (`_I` widening, `_verify_signature`'s wiring) already existed; this commit closes coverage debt, not new behavior. No test-first violation: nothing to precede |
| `542e888` (rebase + BUG-1055 migration) | data migration, not new behavior | **holds as migration, not TDD-applicable** — one file changed, a single `status` key deleted from `BUG-1055-code-grade-absent-path/feature.json`. No dedicated test added, but the change is validated by the standing `check-state.sh`/schema sweep (§1, 0 violations) rather than by a new assertion — consistent with T-07's own prior migration of ten other directories, which also added no per-directory test |
| `1a155ed` | re-pin `review_sha` | metadata-only, no test-first question applies |
| `a592c00` | handoff rewrite | notes-only, no test-first question applies |
| `39477a5` | handoff edit | notes-only, no test-first question applies |

No commit in this cycle's range lands a behavioral change without its test in the same commit.

## 8. SC-08 survey, RE-MEASURED (not accepted from the handoff)

```
total feature.json files:        47
dirs WITH plan.yaml:              35
dirs WITHOUT plan.yaml:           12
feature.json carrying `status`:    1  -> BUG-1071-inv32-era-guard, status="Review"
plan-having dirs w/ stray `status`: 0
```

**Every one of the 35 plan-having directories carries no `status` key** (independently confirmed,
not merely inferred from the plan-less count). Of the 12 plan-less directories, exactly **one** —
`BUG-1071-inv32-era-guard`, non-terminal (`status: Review`) — still carries the key; the other 11
(`FEAT-01`, `FEAT-02`, `FEAT-03..09` = 9, `BUG-1030`, and `BUG-1055` — the last migrated by this
cycle's `542e888`) carry none. The handoff's "10 plan-less terminal ones" undercounts by exactly
the one this cycle's own migration added (`BUG-1055`); 10 pre-existing + 1 newly migrated = 11,
which is what I measure. **The underlying claim — BUG-1071 is the sole exception — holds exactly.**
Schema enforcement independently confirmed: `validate-feature-json.py` on `BUG-1071`'s
`feature.json` exits 1, `undeclared key 'status' at /` (the schema at
`.claude/skills/harness/bin/feature-schema.json:4-6` sets `additionalProperties: false` and
declares no `status` property).

**SC-08's literal verdict: FAIL, by exactly one file, exactly as the handoff discloses.** The
"eleven former readers" clause holds — `grep` for any remaining `feature.json`-status reader
outside tests returns 0 hits.

## 9. SC-01..SC-14

| SC | verdict | method | evidence |
|---|---|---|---|
| SC-01 | PASS | automated | criterion's own grep, verbatim, `--exclude-dir=__pycache__` → 0 hits |
| SC-02 | PASS | automated | criterion's own quoted-literal grep, verbatim, excluding `test-*` → 0 lines |
| SC-03 | PASS | automated | T-04's own anchored `python3 -c` assertion, verbatim → exit 0 |
| SC-04 | PASS | automated | `gh_board.set_station(` outside tests, whole tree → exactly 4 call sites |
| SC-05 | PASS (struck) | inspection | struck with T-13, recorded not deleted, unchanged this cycle |
| SC-06 | PASS | automated, integration | `test-check-domain.py` exit 0 inside the full integration run (§1) |
| SC-07 | PASS | automated, integration | `test-plan-sign-gate.py` exit 0 inside the full integration run (§1) |
| SC-08 | **FAIL, literal; disclosed, not a regression** | automated | §8: one `feature.json` (BUG-1071) still carries `status`, re-measured and confirmed as the sole exception |
| SC-09 | PASS | inspection | `git show 39477a5:.../FEAT-40.../plan.yaml` → `status: done`; 0 `INV-26` lines in the check-state.sh run |
| SC-10 | PASS | automated | `test-gh-sync.py` run standalone: exit 0, 0 FAIL, 296 case lines |
| SC-11 | **PASS — decisive, serial** | automated | §1: this run is a solely-owned, serial, foreground run of both suites plus check-state.sh, all exit 0 at the expected counts. Cycle 0's concurrency confound (a simultaneous second run in the same checkout) structurally cannot have recurred here |
| SC-12 | PASS (struck) | inspection | struck with T-13 exactly as pre-authorized, unchanged this cycle |
| SC-13 | PASS | automated | `grep _EXPECT check-state.sh` → 0 hits; `test-check-state.py` green inside the integration run |
| SC-14 | PASS | automated | T-15's own verify script, run verbatim → exit 0, "three amendment records present, three amended clauses still standing" |

## 10. Unexamined

- No cross-mutation proof that INV-32 and INV-33's assertions cannot pass on each other's fixture
  output (carried from cycle 1's own audit gap; not re-attempted this cycle — time went to the
  dispatch's re-measurement priorities instead).
- F-06 (`_verify_spliced`, cycle-0 med) and F-07 (`worktree_terminal.py` `MissingDependency`
  wiring, cycle-0 med) were not re-checked this cycle; cycle 1 confirmed both still stand and
  nothing in `42bc5fe..39477a5` touches either area, so I did not re-derive them from source again.
- The two `_FOLD_ROWS` gaps (§2) were probed by mutation but I did not write the missing cases —
  DEC-174 forbids it here.

## Final clean-checkout confirmation

`git status --porcelain` on the whole worktree, after every mutation in §2/§3/§5 was restored via
`git checkout --`: **empty.** No fixtures, temp files, or edits left in the tracked tree; all
throwaway artifacts (the `$TMPDIR` fixture for §6) live outside it.

## DIGEST

```yaml
VERDICT: FAIL
DIGEST:
  headline: H-01, H-02 and the _verify_signature forcing case hold at source, mutation-proven, and the case is honest (discriminates the guard from the YAML loader). But the _I case-fold fix only closed 4 of 6 patterns (RE_STATE_YAML and RE_CLAUDE_MD remain provably unpinned), and the carried HIGH finding — set-task-station/set-feature-station accept no caller identity and are wide open to an ordinary Bash call — still reproduces exactly as reported, unaddressed by this cycle's diff.
  suite: pass
  failures: 0
  matrix_ok: true
  kinds:
    - { kind: unit, state: satisfied, cmd: ".claude/skills/harness/bin/run-unit-tests.sh --kind unit", named_tests: 505 }
    - { kind: integration, state: satisfied, cmd: ".claude/skills/harness/bin/run-unit-tests.sh --kind integration", named_tests: 819 }
    - { kind: component, state: not_applicable, cmd: null }
    - { kind: ui, state: not_applicable, cmd: null }
    - { kind: eval, state: not_applicable, cmd: null }
    - { kind: typecheck, state: not_applicable, cmd: null }
  coverage_gaps:
    - "test-check-domain.py: _FOLD_ROWS (2774-2779) has 3 rows (feature.json, handoff-build.md, STATE.md); RE_STATE_YAML and RE_CLAUDE_MD are still unpinned — mutation-confirmed 0 failures when _I is dropped from either, same defect class cycle 1 found for 5 of 6 patterns, now narrowed to 2 of 6"
    - "plan-merge.py: set-task-station/set-feature-station carry no caller-identity binding at all (T-08 covers sign-approval only, by its own docstring) — reproduced live this cycle, unaddressed by 7c4f0bd..39477a5"
    - "no cross-mutation case proves INV-32 and INV-33's assertions cannot pass on each other's fixture output — carried from cycle 1's own audit gap, not re-attempted"
    - "test-plan-merge.py: F-06 (_verify_spliced) still has zero forcing case (carried from cycle 0, unchanged, not re-derived from source this cycle)"
    - "test-worktree-terminal.py: F-07 (MissingDependency wiring) still has zero forcing case (carried from cycle 0, unchanged, not re-derived from source this cycle)"
  sc_status:
    - { id: SC-01, verdict: PASS, method: automated, evidence: "criterion's own grep verbatim, 0 hits" }
    - { id: SC-02, verdict: PASS, method: automated, evidence: "criterion's own quoted-literal grep verbatim, 0 lines" }
    - { id: SC-03, verdict: PASS, method: automated, evidence: "T-04's own anchored python3 -c assertion, exit 0" }
    - { id: SC-04, verdict: PASS, method: automated, evidence: "gh_board.set_station( outside tests, whole tree: exactly 4 sites" }
    - { id: SC-05, verdict: PASS, method: inspection, evidence: "struck with T-13, recorded not deleted, unchanged" }
    - { id: SC-06, verdict: PASS, method: automated, evidence: "test-check-domain.py exit 0 inside full integration run" }
    - { id: SC-07, verdict: PASS, method: automated, evidence: "test-plan-sign-gate.py exit 0 inside full integration run" }
    - { id: SC-08, verdict: FAIL, method: automated, evidence: "re-measured survey: 47 feature.json, 1 (BUG-1071) still carries status; disclosed, not a regression, per §8" }
    - { id: SC-09, verdict: PASS, method: inspection, evidence: "git show 39477a5:.../FEAT-40.../plan.yaml has top-level status: done; 0 INV-26 lines" }
    - { id: SC-10, verdict: PASS, method: automated, evidence: "test-gh-sync.py standalone: exit 0, 0 FAIL, 296 case lines" }
    - { id: SC-11, verdict: PASS, method: automated, evidence: "decisive serial, solely-owned run: unit 505/0, integration 819/0, check-state.sh 0/0, all exit 0" }
    - { id: SC-12, verdict: PASS, method: inspection, evidence: "struck with T-13 exactly as pre-authorized, unchanged" }
    - { id: SC-13, verdict: PASS, method: automated, evidence: "grep _EXPECT 0 hits; test-check-state.py green in integration run" }
    - { id: SC-14, verdict: PASS, method: automated, evidence: "T-15's own verify script run verbatim, exit 0" }
  severity_max: high
  open_questions:
    - { id: Q1, question: "set-task-station/set-feature-station have no caller-identity binding and I reproduced an unauthorized station flip live this cycle (§6). The BRIEF's own disclosure at 109-112 appears to name this exact gap as accepted scope ('write attribution the platform does not offer'), but the cycle-1 lead digest that would confirm this was weighed and accepted was never written to the run dir. Is this disclosed-and-accepted, or an unresolved carried HIGH that blocks ship?", blocking: true }
    - { id: Q2, question: "Should test-check-domain.py's _FOLD_ROWS gain the two missing rows (RE_STATE_YAML, RE_CLAUDE_MD) before ship, given the mutation proof in §2 shows they are exactly as unpinned as cycle 1's original 5-of-6 finding, just narrower? Naming per DEC-174, not writing.", blocking: false }
  files_touched: []
  expertise_update: []
artifact: .harness/harness/features/FEAT-41-one-station-vocabulary/notes/qa-FEAT-41-c2.md
```
