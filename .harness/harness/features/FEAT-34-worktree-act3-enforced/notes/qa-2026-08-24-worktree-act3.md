# QA — FEAT-34 worktree act3, working-tree grade (no review_sha pinned, per dispatch)

## BLUF

FAIL. The three team-owned suites (`test-worktree-terminal.py`, `test-post-merge-sweep.py`,
`test-hooks-install.py`) are green, well-designed, and — critically — they now DO vary the vantage
point that produced the three prior escaped defects. But the gate itself (`check-state.sh`'s new
INV-29/INV-30) has **zero direct automated test coverage** at this point in the plan: T-07, T-08,
T-09 (all `test-check-state.py`, main-session-direct/operator's per DEC-174 am.4) are `status:
pending`. SC-01, SC-02, SC-03, SC-04, SC-05, SC-12 all name `test-check-state.py`-shaped evidence
in the signed brief, and none of it exists yet. That is a missing floor row for T-06 (`status:
done`, `change_type: logic`), not an accepted gap — the brief's two accepted gaps are narrower
(operator's own clone, INV-30 offline posture) and do not cover this.

## My measured numbers (own run, no pipe before `$?`, matches the operator's)

| Suite | Exit | PASS | FAIL |
|---|---|---|---|
| `test-post-merge-sweep.py` | 0 | 47 | 0 |
| `test-hooks-install.py` | 0 | 29 | 0 |
| `test-worktree-terminal.py` | 0 | 34 | 0 |
| `check-state.sh` | 0 | — | 0 `VIOLATION` lines |
| `run-unit-tests.sh` (full, no `--kind`) | 0 | all listed scripts `PASS`, incl. the 3 new files | 0 `^FAIL` lines, no `KIND-DRIFT`, no `MISCONFIGURED` |

T-05's verify (extended to all three files, verbatim + `test-hooks-install.py` added myself since
T-05's own verify predates that file):
```
check-kinds: the script arrays and test_kinds.integration.detect agree.
REGISTERED-ALL-THREE
```
`test-hooks-install.py` confirmed in BOTH `INTEGRATION_SCRIPTS` (run-unit-tests.sh:18) and
`test_kinds.integration.detect` (harness.json:119).

## THE ACTUAL QUESTION — vantage point

Confirmed positively: two fixtures now exist that were structurally impossible before and target
the exact bug class named in the dispatch.

- `test-worktree-terminal.py:729` `case_classify_from_linked_worktree` (m/n) — calls
  `classify(dest)` with `dest` a **linked worktree**, not the repo root, and asserts (i) the main
  checkout is never silently re-included, (ii) the linked-worktree root itself is classified
  rather than skipped. This is bug #1 (`classify` comparing against `root`) reproduced and fixed.
- `test-post-merge-sweep.py:607` `case_cwd_outside_repo` (h) — invokes the sweep with `cwd` a
  directory **outside any git repository**, asserting the repo root still resolves and the sweep
  still finds/removes the terminal worktree. Docstring names the measured defect verbatim
  (`_resolve_repo_root()` used `cwd=os.getcwd()`). This is bug #2 reproduced and fixed.
- `test-post-merge-sweep.py:664` `case_linked_worktree_main_checkout` (i) — installs the
  fixture-local bin dir **inside a linked worktree** (`WT_CALLER`) carrying its OWN divergent copy
  of the same feature id, and asserts `feat_dir` resolves against the real main checkout `R`, not
  `WT_CALLER` — reads a `"resolved main checkout root: …"` line the sweep prints unconditionally.
  This is bug #3 (one root for two jobs) reproduced and fixed; matches `post-merge-sweep.sh:159-163`
  (`main_checkout_root` split from `_resolve_repo_root()`, verified by reading the source).

All three vantage-point cases measured PASS in my own run. `post-merge-sweep.sh` itself carries the
two named resolutions (`_resolve_repo_root` at :42, `main_checkout_root` handling at :159-163) —
confirmed by grep, not inference.

Where the vantage-point defense does NOT reach: `check-state.sh`'s own INV-29/INV-30 are called
only from the repository root in every real invocation I ran (`bash check-state.sh` from the main
checkout). Nothing in this diff exercises INV-29 with `root` set to a linked worktree — the
library underneath is now safe there, but the gate's own call site is untested for it. Flagged as
Q9 in `STATE.md`, already routed to pm — I am not duplicating that routing, only noting it changes
nothing about the T-07 gap below.

## SC evidence — named per SC, and the gap stated plainly

| SC | Automated evidence today | Note |
|---|---|---|
| SC-01 | **none at gate level.** `worktree_terminal.py` predicate covered by `test-worktree-terminal.py case_classify` (a/b), but the composed INV-29 message string (path+command substitution, red-proof malformed variants) has zero test — `test-check-state.py` carries 0 occurrences of `INV-29` (grepped). | T-07 pending |
| SC-02 | deadlock predicate covered at library level, `test-worktree-terminal.py:178` `case_deadlock` + `:233` `case_deadlock_red_proof`. Gate-level (INV-29 firing/not-firing) untested. | T-07 pending |
| SC-03 | dirty-clause predicate (`dirty: True`) covered at library level (`case_classify` (h)). Two-clause message assertion untested at gate level. | T-07 pending |
| SC-04 | second-repo predicate covered at library level, `case_second_repo` + `case_classify_all_two_repos`. One-`check-state.sh`-run assertion untested — no `test-check-state.py` case exists. | T-07 pending |
| SC-05 | four-worktree exemption discrimination covered at library level (`case_absent_red_proof`, short-name/unresolved cases). Gate-level fixture untested. | T-07 pending |
| SC-06 | **satisfied.** `test-post-merge-sweep.py` `case_fast_forward` / `case_squash`, both shapes asserted separately, both PASS. | — |
| SC-07 | **satisfied.** `case_self_exclusion` (c), red proof via genuine source mutation (`_mutated_copy`, asserts needle found before mutating), measured PASS/RED correctly. | — |
| SC-08 | **satisfied.** `test-hooks-install.py` case (a)/(b), both halves asserted separately. | — |
| SC-09 | **satisfied.** All 16 `.claude/agents/harness-*.md` preload `harness-handoff`, which now states the rule (`harness-handoff/SKILL.md:82`) — checked by grep across all 16 files, not asserted. | — |
| SC-10 | **not gradable as specified** — dispatch says grade the working tree, not `review_sha`; `check-state.sh` clean and `integration` kind green on the working tree stands in. | review_sha not yet pinned, by design |
| SC-11 | **satisfied.** `case_per_feature_record` (d) — two separate milestone-number assertions (801, 802), never a total count. | — |
| SC-12 | **none.** `INV-30` occurs 0 times in `check-state.sh` — T-08 unbuilt. | T-08/T-09 pending |
| SC-13 | **satisfied.** `test-hooks-install.py` case (c)/(d), red proof (unconditional-write variant) demonstrated failing clause 2 and clause 3. | — |
| SC-14 | **satisfied.** `case_sc14_end_to_end_and_red_proof` (e), red proof repoints the shim and demonstrates the mutant still passes (a)-(d) and fails (e) only. | — |
| SC-15 | **satisfied.** `test-worktree-terminal.py` `case_classify_all_absent_vs_unenumerable` (j/k) and `case_classify_all_fleet_unloadable` (l) — all three branches asserted per-clause (absence-of-record, klass+path separately, fleet-record-plus-harness-records-both-present), with red proofs for skip-both/report-both/swallow-exception. | — |

Accepted gaps (per BRIEF `## Added verification gaps`, NOT reported as defects):
operator's own clone repointing (INV-29/UAT), INV-30 silent-offline posture.

## Red proofs — verified genuine, not cosmetic

Checked the mechanics, not just the pass/fail line: `_mutated_copy` in
`test-post-merge-sweep.py:293` asserts the needle text is found verbatim in the real source before
mutating — a no-op mutation would raise, not silently pass. Same discipline in
`test-hooks-install.py`'s (d)/(e) red proofs (unconditional-write variant, repointed-shim variant),
confirmed by reading the case bodies. These are real perturbation proofs, not assertions of correct
behaviour dressed up as red proofs.

## Registration (T-05 + T-13's extension)

Both enumerations agree for all three new files — confirmed by direct grep and by
`run-unit-tests.sh --check-kinds`, not by re-stating the plan's own claim.

## matrix_ok

**false.** `change_type: logic` (T-06, `status: done`) requires `unit` at minimum per
`test_matrix`; this project's convention buckets subprocess-fork tests as `integration`
(`run-unit-tests.sh` comments cite issue #160), which is fine in general — but for T-06's own
artifact (`check-state.sh`'s INV-29 addition) NO test file in either bucket exercises it. That is a
genuinely uncovered row, not a bucketing technicality: `test-check-state.py` is the file the signed
brief names as SC-01..SC-05's evidence, it is unmodified in this diff, and it is main-session-direct
per DEC-174 am.4 — so the fix routes to the operator/main session, never to a squad.

## Route

FAIL. Missing row: `test-check-state.py` INV-29 cases (T-07) and INV-30 cases (T-09), both
main-session-direct, both `status: pending`. This is not new information to the operator — `STATE.md`
already names T-07/T-08/T-09 as in-flight and pending — but the qa gate cannot mark the matrix
satisfied while the brief's own named evidence for six SCs does not exist.
