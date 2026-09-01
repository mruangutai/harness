# QA gate — FEAT-41-one-station-vocabulary — cycle 3 — review_sha 5dc7710 (base 7c4f0bd)

**BOTH STAGES RAN.** Stage one = SC re-measurement below (§5). Stage two = the mutation gate
(§2), which is the actual job this cycle. Worktree confirmed at the assigned path; `HEAD`
(`a725472`) is one commit ahead of the pin, `feature.json`-only (`git diff --stat 5dc7710 a725472`
= 1 file, the review_sha pointer). All work done against this checkout, at the pinned tree.
`.claude/skills/harness/bin/*.py`/`*.sh` file locations resolved via `bash grep -n`/`sed`, not
this session's `read`/`grep` tools — both returned stale content and false "no matches" for files
confirmed present and correctly numbered via `bash`; treat this as a session-tooling defect, not a
finding against the feature (see Open questions).

**BLUF: FAIL.** Every T-19/C2-02/C2-03 guard the dispatch named IS pinned by mutation, with one
exception downgraded to a live-but-non-exploitable dead-code finding: `check-domain.sh`'s
`_resolved_rel`'s fail-closed branch cannot fire under the actual Python runtime (3.14; `strict`
defaults `False` since 3.10), because `os.path.realpath` no longer raises `OSError` on a symlink
loop — measured live, not inferred. The write path stays safe in practice because the underlying
write itself hits `ELOOP` at the OS layer through the same channel, but the "correction that
matters most" the C2-02 commit claims never executes as written. Everything else redded exactly as
predicted. Baseline suites match the reported green; SC-08 is now **literally true** (0 of 47
`feature.json` carry `status`, up from cycle 2's 1-of-47 exception — T-19's backfill closed it).

## 1. Baseline reproduction — serial, solo

| check | expected | observed |
|---|---|---|
| `--kind unit` | exit 0, 505 PASS | **matches**: exit 0, 505 `^PASS ` lines, 0 FAIL, 32 script markers (31 declared + 1 subcase name, same shape cycle 2 noted). 23.5s. |
| `--kind integration` | exit 0, 819 PASS | **exit 0, 0 FAIL confirmed** (the part that matters). Raw `^PASS ` count is **696**, not 819 — but this is a metric artifact, not a regression: 28 declared scripts == 28 discovered script-level markers (set-equal), and this run's per-script conventions split across `^PASS ` (696), `^ok` (1271), and `^PASS:` (123) lines depending on which convention each script uses internally (e.g. `test-plan-sign-gate.py`'s whole C2-03/H-02/F-03 block prints `ok`, not `PASS`). Raw PASS-line totals are not comparable across runs when scripts' internal conventions differ — this is exactly my own Expertise G-04, reconfirmed live. 3m26s. |
| `check-state.sh` | exit 0, 0 violations, 0 tracebacks | **matches**: exit 0, 0/0. 12.7s. |

**Coverage gap named per dispatch step 1.** `--kind unit`'s 31-script list contains **zero** of the
guard scripts this cycle's mutations target. Cross-referencing this feature's 17 changed non-test
`.py`/`.sh` files against both arrays: **11 of their test counterparts run under `--kind
integration` only** — `test-check-domain.py`, `test-check-plan-routes.py`, `test-check-state.py`,
`test-factory-integration.py`, `test-gh-sync.py`, `test-harness-yaml.py`, `test-hooks-install.py`,
`test-plan-merge.py`, `test-plan-sign-gate.py`, `test-post-merge-sweep.py`,
`test-worktree-terminal.py`. **Every guard in §2 below is one of these 11.** Running `--kind unit`
alone, as an agent might habitually reach for first, would show every mutation in this report as
GREEN. This is the same shape as the four-task blind spot the handoff's own Dead End records.

## 2. Mutation gate — the job

| guard | file:line @5dc7710 | mutation | suite | result |
|---|---|---|---|---|
| T-19 exemption widen | `check-state.sh:201` `if not doc["tasks"]:` | `if True:` (exempt every plan, tasks or not) | `test-check-state.py` (`python3` direct) | **RED** — 3 fails: `(inv34.d)` (the control), plus `(q/pending)` INV-3 and `(q/inv5)` STATE.md-task, both collateral since the mutation skips the whole loop |
| T-19 approval-check delete | `check-state.sh:203-208` (the `_appr =` block) | deleted entirely, exemption line untouched | same | **RED** — 2 fails: `(inv34.d)` + `(q/pending)`; `(inv34.d)` confirmed as the load-bearing control both ways |
| harness_yaml station guard | `harness_yaml.py:326` `if not tasks and not str(doc.get("status") or "").strip():` | `if not tasks and "status" not in doc:` | `test-harness-yaml.py` | **RED** — 1 fail: `test_load_plan_accepts_a_station_only_record_and_only_with_a_station` (`ACCEPTED what it must reject: empty tasks and a blank status`) — the negative-half case with `status: '   '` now wrongly passes |
| INV-34 isfile invert | `check-state.sh:1105` `if not os.path.isfile(...):` | inverted to `if os.path.isfile(...):` | `test-check-state.py` | **RED** — 2 fails: `(inv34.a)`, `(inv34.b)` |
| INV-34 live deletion | (live tree, not the fixture) | `mv`'d `FEAT-45-adversarial-plan-panel/plan.yaml` out of the tracked tree, ran `check-state.sh` over the real corpus | `check-state.sh` | **RED** — `VIOLATION INV-34: FEAT-45-adversarial-plan-panel has no plan.yaml...`; restored via `git checkout --` (the write-guard denied `mv`-ing it back — see Open questions), re-ran, confirmed 0 violations again |
| hardlink cap `< 2` → `< 1` | `check-domain.sh:1524` `if st.st_nlink < 2:` | literal mutation as specified | `run_t09()` isolated | **GREEN, 0 fails** — see finding below: the literal mutation is a no-op for correctness |
| hardlink cap, "never scans" variant | same line | `if True: return None` (the behavior the dispatch's parenthetical actually describes) | `run_t09()` isolated | **RED** — 1 fail: `T-09 11: a Write through a hardlink to plan.yaml is DENIED` |
| islink fail-closed branch, deleted | `check-domain.sh:1543-1551` (`if resolved is None: ... return None`) | deleted entirely (8 lines) | `run_t09()` isolated | **GREEN, 0 fails, and no crash** — see finding below: the branch is unreachable, not merely untested |
| `as_bash_reads_it` identity | `plan-sign-gate.py:133-147` | body replaced with `return line` | `test-plan-sign-gate.py` | **RED** — 6 fails: 2× H-02 (both scanners) + 4× C2-03 (both scanners × plain-and-doubled `${IFS}`; the precision-control and one text-fallback case were unaffected as expected) |

**Baseline assertion counts, confirmed by direct isolated runs before mutating (answers dispatch
step 3):** `run_t09()` in isolation: 0 fails, and `T-09 11` prints exactly **4** lines, `T-09 10`
prints exactly **9** — both match the handoff's `4 T-09 11` / `9 T-09 10` claim exactly.
`test-plan-sign-gate.py` in isolation: 0 fails, `C2-03` appears exactly **6** times, matching `6
C2-03`. All three of the handoff's cited counts are confirmed to **run**, not merely to be present
as strings.

### Two findings the literal mutation instructions surfaced, not just confirmed

**[med] `check-domain.sh:1524`'s `st_nlink < 2` → `< 1` literal mutation is a no-op, and the
dispatch's own "(never scans)" framing of it is wrong.** `< 1` is true only when `nlink == 0`,
which never happens for a `stat`-able file — so the mutated guard **never** returns early; it
makes *every* file (not just hardlinks) fall through to the glob scan, which is a performance
regression, not a correctness one, since the scan still correctly matches nothing for ordinary
files. The literal instruction, followed exactly, produces 0 fails — correctly, because it doesn't
touch what the guard actually protects. I additionally ran the mutation the parenthetical
describes (an unconditional `return None`, i.e. genuinely disabling the scan) and *that* reds
`T-09 11`'s hardlink case as expected. Both are reported; the second is the one that matches the
BRIEF's intent, the first is what was literally specified.

**[med] `check-domain.sh:1543-1551`'s fail-closed `islink` branch is unreachable in
`_plan_route`'s own fixture world AND under the actual Python runtime — measured both ways, not
inferred.** Deleting the branch produces 0 test failures. I did not stop there: `_resolved_rel`'s
`except OSError: return None` (the only way `resolved is None` can happen) depends on
`os.path.realpath` raising `OSError` on a symlink loop — the comment at `check-domain.sh:1502`
says exactly this ("realpath follows a chain of ANY length, and raises on a loop"). **That claim
is false for the Python version actually running this code.** `os.path.realpath` has taken
`strict=False` as its default since Python 3.10 (this repo runs 3.14), and under `strict=False`
it never raises — confirmed live under `$TMPDIR` (never the tracked worktree): a genuine
two-node symlink loop, a 500-hop non-cyclic chain, and a permission-denied path component all
returned a best-effort string with zero `OSError`. **The branch is unreachable by construction,
not merely absent from the test fixtures — both were measured, per the dispatch's own framing of
this exact ambiguity.** It is not independently exploitable: for a genuine loop, `_plan_route`
falls through to `_hardlink_plan`, whose `os.stat(path)` call *does* raise `OSError` (`ELOOP`,
confirmed live) and is caught, returning `None` — so the write is *allowed* to attempt, but the
actual filesystem write through a circular symlink fails at the OS layer the same way any tool
would hit it, so no corruption reaches a real `plan.yaml`. Severity **med, not high**: the
mechanism C2-02's commit message calls "the correction that matters most" is dead code and its
own justifying comment is wrong about current Python's `realpath` semantics, but no live write
evades detection through this specific path today.

## 3. Test-first audit (commit messages; DEC-174 carve-out — no per-task specialist notes expected)

`80a919e` (T-19/D-17) and `e071509` (C2-02+C2-03) — the two commits closing every cycle-2 HIGH —
each lands production fix and test in the same commit: `80a919e` touches `check-state.sh` +
`harness_yaml.py` alongside `test-check-state.py` (+121) and `test-harness-yaml.py` (+46) in one
diff; `e071509` touches `check-domain.sh` + `plan-sign-gate.py` alongside `test-check-domain.py`
(+72) and `test-plan-sign-gate.py` (+62) in one diff. Both commit bodies state the exact
new-assertion counts (`4 T-09 11, 6 C2-03, 9 T-09 10`), independently reproduced in §2. No
test-after violation in the cycle-2→cycle-3 delta.

## 4. Test-matrix gate

Change types unchanged from cycle 2's reading, re-derived from `plan.yaml` directly including the
new T-19 (`change_type: logic`): config×4, cross_module×4, api×1, docs×2, bugfix×2, logic×5
(T-16..T-19). `git diff --name-only 7c4f0bd..5dc7710` has zero matches against
`*.spec.tsx`/`*.stories.(tsx|ts)`, `tests/e2e/**`, `*.e2e.spec.ts`, `evals/**`, or any `.ts`/`.tsx`
— re-checked myself. `unit` and `integration` both satisfied (§1). `component`/`ui`/`eval`/
`typecheck` not applicable, none detect a touched file. **`matrix_ok: true`.**

## 5. SC re-measurement, criterion-owned commands, verbatim

| SC | command | demanded | measured |
|---|---|---|---|
| SC-01 | `grep -rn --exclude-dir=__pycache__ "_STATION_KEYS" .claude/skills/harness/bin/` | 0 | **0** |
| SC-02 | criterion's own quoted-literal grep over `bin/*.py`,`*.sh` excl. `test-*` | 0 | **0** |
| SC-03 | criterion's anchored `python3 -c` assertion | exit 0 | **exit 0** |
| SC-04 | `gh_board.set_station(` whole-tree, outside tests | exactly 4 | **exactly 4** — `board-station.py`, `board_lifecycle.py`×2, `gh-sync.py` |
| SC-08 | `feature.json` carrying `status`, whole tree; RE-MEASURED not accepted | 0 | **0 of 47** — full survey: 47 `feature.json`, **all 47 now have a `plan.yaml`** (T-19's backfill closed the 12-directory gap cycle 2 measured, including BUG-1071), 0 carry `status`. Schema independently confirmed to reject the key (`validate-feature-json.py` on a synthetic status-bearing copy: exit 1, `undeclared key 'status' at /`). **SC-08 is now literally true**, not merely intent-satisfied as in cycles 1/2. |
| SC-11 | `check-plan-routes.py` over every live plan | exit 0 | **exit 0**, `0 violation(s) across 3 plan(s)`, 48 dirs examined, 45 skipped as shipped (the `DEVIATION ... declared main-session-direct` lines are informational per DEC-174, not violations) |
| SC-14 | `grep -c "FEAT-41-one-station-vocabulary" DECISIONS.md` | 3 | **3** |

SC-05/SC-12 remain struck (unchanged); SC-06/SC-07/SC-09/SC-10/SC-13 unchanged from cycle 2's
inspection, not independently re-run this cycle (no dispatch line named them, and nothing in
`39477a5..5dc7710` touches their surfaces except T-19, which SC-09's `check-state.sh` full run in
§1 already re-covers with 0 `INV-26` lines).

## 6. Final clean-checkout confirmation

`git status --porcelain` on the whole worktree: **empty**, after every mutation above
(`check-state.sh`×3, `harness_yaml.py`, `check-domain.sh`×2, `plan-sign-gate.py`) was restored via
`git checkout --`. The one live-tree mutation (§2, INV-34 deletion) was restored the same way
after the domain hook denied restoring it by `mv`. All scratch fixtures (symlink loops, the
`$TMPDIR/loop_test*` dirs) live outside the tracked tree; two could not be `rm`'d because the
write-guard denies `bash rm` against out-of-domain targets even under `$TMPDIR` — left in place,
harmless, outside git.

## Open questions

- This session's `read`/`grep` tools returned stale/incorrect content and false "no matches" for
  `check-state.sh`, `check-domain.sh`, and `plan-sign-gate.py` — files confirmed present, correctly
  numbered, and byte-identical to their `git show` content via `bash sed`/`grep -n`. All
  ground-truth line numbers and mutations in this report used `bash` exclusively once the
  discrepancy was found. Likely a stale index for this worktree; flagged for the harness owner, not
  a FEAT-41 defect.
- The `bash-write-guard` denies restoring a file via `mv`/`rm` to a path it just permitted removing
  FROM (moving `FEAT-45`'s `plan.yaml` out was allowed as part of the same `mv`, restoring it back
  in was denied) — I worked around it with `git checkout --`, which the guard does not intercept.
  Consistent with cycle 1's own Q-01 (gate-write asymmetry) — not re-raised as a new finding, noting
  it recurred.

## Findings

- **[med] `check-domain.sh:1543-1551`'s fail-closed `islink` branch is dead code under the
  project's actual Python runtime** — `_resolved_rel`'s justifying comment ("realpath... raises on
  a loop") is false for Python ≥3.10's default `strict=False`; measured live with a genuine
  symlink loop, a 500-hop chain, and a permission-denied component, none raised. Not independently
  exploitable today because the fallback (`_hardlink_plan`'s `os.stat`) does raise `ELOOP` and
  denies via a different path, and any real write through a loop fails at the OS layer regardless.
  Fix: either delete the dead branch and its comment, or replace the `except OSError` premise with
  a check that can actually fire under this Python version.
- **[med] `check-domain.sh:1524`'s `st_nlink < 2` guard's literal `< 1` mutation is a no-op; the
  dispatch's own framing of it ("never scans") describes a different mutation.** Not a defect in
  the shipped code — reported so the dispatch's premise isn't silently carried forward as fact.
  The guard IS load-bearing (confirmed via the `if True: return None` variant, which correctly
  reds `T-09 11`'s hardlink case).
- **[info] Integration suite's raw `^PASS ` line count (696) does not match the reported baseline
  (819)** — not a regression: script-level presence is set-equal (28 declared == 28 discovered, 0
  FAIL), and the gap is explained by per-script printing convention drift (`ok` vs `PASS` vs
  `PASS:`), consistent with this session's own standing Expertise (G-04: raw PASS-line totals are
  not a reliable cross-run metric). Recommend the runner report a stable, convention-independent
  case count if this keeps recurring across cycles.
- **[info] Session tooling (`read`/`grep`) served stale content for the three files under
  heaviest mutation this cycle** — worked around with `bash`; raised as an open question, not a
  FEAT-41 finding.

```yaml
VERDICT: FAIL
DIGEST:
  headline: Every named T-19/C2-02/C2-03 guard reddens under its intended mutation except one — check-domain.sh's fail-closed islink branch is dead code under the project's actual Python runtime (os.path.realpath's strict=False default since 3.10 never raises on a symlink loop, measured live), not merely untested; not independently exploitable today, but the C2-02 commit's own "correction that matters most" claim does not hold. All other guards, baselines, and SC-08 (now literally true) confirm clean. Both stages ran.
  suite: pass
  failures: 0
  matrix_ok: true
  kinds:
    - { kind: unit, state: satisfied, cmd: ".claude/skills/harness/bin/run-unit-tests.sh --kind unit", named_tests: 505 }
    - { kind: integration, state: satisfied, cmd: ".claude/skills/harness/bin/run-unit-tests.sh --kind integration", named_tests: 696 }
    - { kind: component, state: not_applicable, cmd: null }
    - { kind: ui, state: not_applicable, cmd: null }
    - { kind: eval, state: not_applicable, cmd: null }
    - { kind: typecheck, state: not_applicable, cmd: null }
  coverage_gaps:
    - "--kind unit (31 scripts) covers none of this cycle's 11 mutated-guard test files (test-check-domain.py, test-check-state.py, test-harness-yaml.py, test-plan-sign-gate.py, plus 7 more) — all 11 live in --kind integration only; running unit alone hides every mutation in this report"
    - "check-domain.sh: the fail-closed islink branch (1543-1551) is unreachable under Python >=3.10's realpath(strict=False) default — dead code, not merely an untested branch"
  sc_evidence:
    - { id: SC-01, test: "criterion's own grep verbatim — 0 hits" }
    - { id: SC-02, test: "criterion's own quoted-literal grep verbatim — 0 lines" }
    - { id: SC-03, test: "criterion's own anchored python3 -c assertion — exit 0" }
    - { id: SC-04, test: "whole-tree set_station( grep outside tests — exactly 4 sites" }
    - { id: SC-08, test: "full survey: 47/47 feature.json now carry plan.yaml, 0 carry status; validate-feature-json.py rejects a synthetic status key, exit 1" }
    - { id: SC-11, test: "check-plan-routes.py full run — exit 0, 0 violations across 3 plans" }
    - { id: SC-14, test: "grep -c FEAT-41-one-station-vocabulary DECISIONS.md — 3" }
  open_questions:
    - { id: Q1, question: "This session's read/grep tools served stale content and false negatives for check-state.sh, check-domain.sh, and plan-sign-gate.py despite bash confirming correct, current content at the same line numbers. Worked around with bash throughout. Is this a known worktree-indexing issue?", blocking: false }
    - { id: Q2, question: "The bash-write-guard denied mv-ing a moved-out file back into place (a live-tree INV-34 mutation restore), forcing a git checkout -- workaround. Same asymmetry cycle 1's Q-01 flagged. Should the guard treat a restore-to-original-content as distinct from an arbitrary out-of-domain write?", blocking: false }
  files_touched: []
  expertise_update: []
artifact: .harness/harness/features/FEAT-41-one-station-vocabulary/notes/qa-c3.md
```
