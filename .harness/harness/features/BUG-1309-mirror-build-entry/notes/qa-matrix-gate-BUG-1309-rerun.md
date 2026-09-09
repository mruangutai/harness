# QA test-matrix gate — RE-RUN — BUG-1309-mirror-build-entry — HEAD eadba844

## Verdict: PASS

All three prior grounds are closed by evidence I measured myself this run. Full unit
(33 files) and full integration (50 files) kinds are green with 0 FAIL. Matrix floor
fully discharged, including T-07's unit cell, which is graded NOT-APPLICABLE against
D-12 (verified at source) rather than reported as a gap.

## §1 — Ground 1 (T-07 fixture regression): CLOSED, measured

`env -u HARNESS_AGENT_TYPE .agents/skills/harness/bin/run-unit-tests.sh --kind
integration` → **exit 0**, 50 files, 0 `^FAIL` lines (was exit 1, 1 FAIL, last run).
Independently re-ran `python3 tests/integration/test-hooks-install.py` directly:
exit 0, all three named T-10 cases present as `PASS:` — `(e-green) SC-14: the
terminal feature`, `(e-green) the sweep removed the worktree by the normal path,
never the build-entry retention branch`, `(e-red) RED PROOF: with the shim
repointed`. T-10's `verify:` (plan.yaml:1612-1618) cross-checked byte-for-byte
against the dispatch and measured true.

## §2 — Ground 2 (T-03 unit floor): CLOSED

T-11 (`eadba844`) adds `tests/unit/test-feature-schema-build-entry.py` and
`tests/unit/test-gh-sync-build-entry.py`, both in the merge-base..HEAD diff (123 +
217 lines, new files). Ran directly: exit 0, no `^FAIL `, all 18 named `BE-*` ids
present. Per backend-dev's receipt (`notes/receipt-harness-backend-dev-T-11-c0.md`),
FILE 2's BE-11/12/14/19/23/24/25/27/28/29/30 exercise `gh-sync.py`'s
`load_recorded`/`save_recorded`/`record_build_entry`/`skip`/
`_build_entry_preflight`/`_recover_terminal_conflict`/`_recover_terminal_report` —
these ARE the T-02/T-03/T-04 decision seams, and the receipt names, per id, the
specific integration-fixture property (no out-of-enum value, no absent-parent leg,
exact-list assertions, etc.) that makes each one non-duplicative of
`tests/integration/test-gh-sync.py`. This discharges T-03's unit cell alongside
T-02/T-04. `feature.always = [unit, integration]` for T-03 (and T-05, unaffected)
is now **satisfied** in full.

## §3 — Ground 3 (bugfix unit floor for T-02/T-04/T-06/T-07): CLOSED for T-02/T-04/T-06; T-07 graded under D-12

T-11's FILE 1 (`test-feature-schema-build-entry.py`, BE-02/03/04/06/08/09/10)
discharges T-06's `feature_schema.recovery_command_for` /
`BUILD_ENTRY_ERA_EXEMPT` seam; FILE 2 discharges T-02/T-04's `gh-sync.py`
recording/preflight seams (see §2). D-10 records this as the intended design and
T-11 delivers it. **T-07 is the one cell not closed by a unit test — it is
closed by D-12's NOT-APPLICABLE ruling instead. See §4.**

## §4 — D-12 grading (T-07's unit cell)

**Heredoc bounds, verified at source (not taken from D-12's prose):**
`.agents/skills/harness/bin/post-merge-sweep.sh` line 29:
`POST_MERGE_SWEEP_BIN_DIR=... python3 -I - <<'PYEOF'`; line 293: `PYEOF`. Confirmed
via `grep -n "PYEOF\|python3 -I -"` — exactly two matches, at 29 and 293. The
entire Python body (`import json`, `import os`, … through `sys.exit(_code)`) sits
inside this one heredoc fed on stdin: nothing in it is importable by any
`tests/unit/**` file without first extracting it into a module. D-12's bounds
citation (`:29-:293`) is accurate.

**`:228` citation, verified at source:** line 228 reads exactly
`elif entry not in {"opened", "not-applicable", "recovered-terminal"}:` — the
retention/removal branch point D-12 names. Line 222 is confirmed as only the
`entry = (feature_doc.get("github") or {}).get("build_entry")` read that feeds it
(D-12's self-correction from an earlier `:222` mis-cite is accurate).

**Grading the three named substitutes:**
1. T-07's eight integration cases (`test-post-merge-sweep.py`) — confirmed present
   and green (ran directly, see §5).
2. T-10's red-proof — confirmed green, see §1. This is a genuine, unplanned
   discrimination event (a live neighbouring fixture reddened when the retention
   branch engaged), stronger than a constructed unit test would have been for this
   one branch instance.
3. T-13's `not-applicable` case — **I did not accept the claim; I proved it
   myself.** In a disposable worktree (`/Users/molchairuangutai/GitHub/harness/.claude/worktrees/qa-t13-mutation-proof`,
   created off HEAD `eadba844`, removed after — DEC-153), I mutated line 228's
   allow-set from `{"opened", "not-applicable", "recovered-terminal"}` to
   `{"opened", "recovered-terminal"}` (dropping the `not-applicable` member) and
   re-ran `test-post-merge-sweep.py`: **exactly one row reddened —
   `FAIL: T-13 not-applicable removes the worktree`** — every other row (all 8
   T-07 cases, all `(h)`/`(i)` cases) stayed `PASS`. Restored the file
   (`git checkout --`), confirmed `git status --porcelain` clean and the file's
   md5 identical before/after mutation (`286000ffffac3d2eb61bed5fc839aad9`), then
   re-ran the bed fully green (0 FAIL). This proves T-13's row is load-bearing for
   the specific `"not-applicable"` allow-set member and closes panel c2's own
   named gap ("no member reaches the third state").

**Is the allow-set now fully exercised?** Yes — all three members
(`"opened"` via a T-07 case, `"recovered-terminal"` via a T-07 case,
`"not-applicable"` via T-13, now self-proven) each have a dedicated case, and the
non-membership arm (`recovery-required`, absent, unparseable) is covered by the
remaining T-07 cases.

**My grading: D-12's disposition is SOUND and its named substitutes now fully
close the branch, including the previously-open allow-set gap.** I graded T-07's
`bugfix.when(touches_runtime_code) -> unit` cell as **not applicable**, per D-12,
not missing. I found nothing in D-12's reasoning (the Over-clause / no-import-surface
argument) that a heredoc extraction would discharge without itself becoming a
DEC-174-governed runtime cutover — D-12's own text concedes DEC-174 does not bar
extraction but raises its price; that price is not paid by this cycle and is not
required to close this gate. **If a future cycle extracts the retention logic into
an importable module, T-07's cell reopens to `unit` under the general floor.**

## §5 — Full kind runs, named

- `env -u HARNESS_AGENT_TYPE .agents/skills/harness/bin/run-unit-tests.sh --kind unit`
  → **exit 0**, pool 8 workers, **33 files** (was 31 — +2 T-11 files), all `PASS`.
- `env -u HARNESS_AGENT_TYPE .agents/skills/harness/bin/run-unit-tests.sh --kind integration`
  → **exit 0**, pool 8 workers, **50 files**, wall ~70s, **0 `^FAIL` lines** (was
  exit 1, 1 FAIL). Captured to `/tmp/qa_integration_rerun.log`; `grep -c '^FAIL'` = 0.
- Task verify blocks, cross-checked verbatim against plan.yaml and re-run directly
  by me, each exit 0 / `VERIFY-PASS` logic confirmed:
  - T-10: `test-hooks-install.py`, all 3 named cases `PASS:`.
  - T-11: `test-feature-schema-build-entry.py` + `test-gh-sync-build-entry.py`, all
    18 named `BE-*` ids `PASS BE-nn `, 0 `^FAIL `.
  - T-12: `test-gh-sync.py`, exit 0, 0 `^FAIL`, `ok    T-12 era-exempt trailing
    slash continues` present. Fix verified at source: `gh-sync.py:1360` reads
    `os.path.basename(feat_dir.rstrip("/"))`, matching `feature_schema.py:326`'s
    expression exactly.
  - T-13: `test-post-merge-sweep.py`, exit 0, 0 `^FAIL:`, `PASS: T-13
    not-applicable removes the worktree` present; **non-vacuity self-proven, see §4**.
- No new test written by me. No production code touched inside this checkout (the
  mutation proof ran and was reverted in a disposable worktree; git status there
  confirmed clean before removal).

## §6 — Per-cell table

| change kind | task(s) | required kind | predicate | covering file:case | state |
|---|---|---|---|---|---|
| config | T-01 | integration (`touches_config_shape`) | fires | `test-validate-feature-json.py` (8 cases) | **satisfied** (unchanged from prior run) |
| bugfix | T-02 | unit (`touches_runtime_code`) | fires | `test-gh-sync-build-entry.py::BE-11/12/14/19/24/25/27/28/29/30` (subset touching T-02 seams) | **satisfied** |
| bugfix | T-04 | unit (`touches_runtime_code`) | fires | `test-gh-sync-build-entry.py::BE-23` (+T-11's own note: passes without RED because T-12 landed first) | **satisfied** |
| bugfix | T-06 | unit (`touches_runtime_code`) | fires | `test-feature-schema-build-entry.py::BE-02/03/04/06/08/09/10` | **satisfied** |
| bugfix | T-07 | unit (`touches_runtime_code`) | fires | none possible (heredoc, `:29-293`) | **not applicable**, per D-12 (§4) |
| bugfix | T-02/04/06/07 | integration (`fix_confined_to_tests_and_contract_docs`) | does not fire (real runtime code changed) | present anyway, all named cases `ok`/`PASS` | not required; present |
| bugfix | T-12 | unit (`touches_runtime_code`) | fires | discharged by T-11's BE-23 (task intent explicitly routes the unit leg there; T-11 depends_on T-12) | **satisfied** |
| bugfix | T-12 | integration (`fix_confined_to_tests_and_contract_docs`) | does not fire (real runtime code changed, `gh-sync.py:1360`) | `test-gh-sync.py::"T-12 era-exempt trailing slash continues"` present anyway | not required; present |
| feature | T-03 | unit + integration (`always`) | both fire | integration: `test-gh-sync.py` (7 T-03 cases, `ok`). unit: `test-gh-sync-build-entry.py::BE-11/12/14/19/24/25/27/28/29/30` | **satisfied** (was MISSING on unit; now closed) |
| feature | T-05 | unit + integration (`always`) | both fire | unchanged from prior run: `test-merge-gate.py` (14 cases) + `test-omp-hooks.py` (56/56) | **satisfied** (carried forward) |
| scaffolding | T-11 | none (`always: []`) | n/a | — | **satisfied** (no floor; delivers coverage for other cells) |
| scaffolding | T-13 | none (`always: []`) | n/a | — | **satisfied** (no floor; own case self-proven non-vacuous, §4) |
| docs | T-08, T-09 | none (`always: []`) | n/a | carried forward from prior run | **satisfied** (no floor) |

No cell is `MISSING` or `BLOCKED`. **Matrix result: PASS.**

## §7 — Test-first audit, T-10..T-13 (T-01..T-09 carried forward by reference — see prior note)

- **T-10** (`execution_mode: main-session-direct`): no receipt (expected — DEC-174
  carve-out writes none). The task's own intent (plan.yaml:1663-1664) explicitly
  instructs "run the file first and record the single failing line... observe it
  fail too, then land both edits... Report both states" — a test-first ordering
  instruction, not evidence of compliance. I found no observations-log entry from
  any peer establishing red-before-green was actually followed for T-10. **Could
  not establish**, same as the prior run's T-04-T-08 main-session-direct set; not
  upgraded to compliant, not downgraded to violation.
- **T-11** (`execution_mode: team`, `harness-backend-dev`): **COMPLIANT, with
  strong evidence.** Two receipts exist:
  `notes/receipt-harness-backend-dev-T-11-c0.md` (per-id discrimination table plus
  a full mutation-to-reddened-ids table, 18/18 ids each tied to a specific,
  reasoned mutation and none found vacuous — I opened and read the table, not
  just its presence) and `notes/receipt-harness-dev-ops-T-11-verify-c0.md`
  (independent re-verification). This is the strongest evidence of any task this
  run.
- **T-12** (`main-session-direct`): no receipt (expected). Intent
  (plan.yaml:1911-1916) instructs "RED FIRST, AND REPORT BOTH STATES... observe
  the case FAIL... then land the edit and observe it pass," naming the exact
  mutation (revert to `os.path.basename(feat_dir)`) that reddens it and nothing
  else. No observations-log entry confirms this was executed in that order.
  **Could not establish**, not upgraded, not downgraded.
- **T-13** (`main-session-direct`): no receipt (expected). Intent explicitly
  states **no red-first claim is available** (production code already correct)
  and prescribes a mutation proof in its place. I do not need to rely on an
  unrecorded main-session claim here — **I ran that exact mutation proof myself
  this gate** (§4) and it discriminates as specified. This is stronger than
  "could not establish": it is directly measured.

## §8 — My own prior adequacy gaps

1. **T-04/T-06 era-gate coverage "reasoned, not measured":** CLOSED by T-11.
   BE-02 (`.rstrip("/")` drop → reddens), BE-06 (status-trigger set narrowed →
   reddens), BE-10 (exact-membership set poisoned with near-miss strings →
   reddens) are named, mutated, and independently cross-checked against every
   case in their function (not just the target id) per the receipt's own
   isolation table. I read the table; it is not vacuous. This gap is now
   **measured**, not reasoned.
2. **Main-session-direct "could not establish" set:** still open for T-04, T-05,
   T-06, T-07, T-08 (prior run) plus T-10, T-12 (this run) — this is structural
   (DEC-174 carve-out writes no receipt) and is not a defect I can close by
   re-running; noting it again rather than silently dropping it. T-13 is the one
   member of this set I converted to directly-measured evidence this run, because
   its own intent named a mutation proof instead of a red-first claim and I was
   able to run it.

## §9 — Case non-vacuity, per required cell

- T-01: prior run, unchanged, not re-verified this gate (out of scope of the
  re-run's four new tasks); carried forward `satisfied`.
- T-02/T-04/T-06 unit (BE-* ids): non-vacuous per backend-dev's mutation table,
  read and checked by me (§2/§3), not merely trusted by presence.
- T-03 unit: same table, BE-11/12/14/19/24/25/27/28/29/30.
- T-07 unit: not applicable (D-12); its integration substitute (T-13) is
  self-proven non-vacuous by me (§4).
- T-05: carried forward, unchanged.
- T-10 (`(e-green)`/`(e-red)` cases in `test-hooks-install.py`): non-vacuous by
  construction — this is a real production fixture that was RED before the fix
  landed (documented in the prior gate's ground-1 finding) and is GREEN now; I
  re-ran it directly and it passes for the reason claimed (the new assertion
  checks `"records github.build_entry"` is absent from combined output, not
  merely that the worktree is gone).
- T-12 integration case: non-vacuous per the task's own stated mutation (revert
  line 1360), which I did not re-run myself this gate (T-11's BE-23 already
  covers the identical mutation on the unit side, and I directly verified the
  production line at source matches the fix exactly, §5) — relying on the
  task's own stated discrimination, not re-measuring it independently.
- T-13: self-measured by me this gate (§4), not relied on secondhand.

## SC evidence pointers (carried forward, unchanged by this cycle)

Unchanged from the prior gate note — no new SCs introduced by T-10..T-13 (T-10 is
a FEAT-34 fixture repair, T-11/T-12/T-13 are scaffolding/bugfix support for
already-covered REQs). See `notes/qa-matrix-gate-BUG-1309.md` §"SC evidence
pointers".

## files_touched

None in the assignment checkout. A disposable scratch worktree
(`.claude/worktrees/qa-t13-mutation-proof`) was created off HEAD, mutated,
restored (confirmed byte-identical, `git status --porcelain` clean), and removed
via `git worktree remove` (non-force, from outside the scratch tree) for the T-13
non-vacuity proof in §4 — no lasting artifact.
