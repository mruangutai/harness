# Code review — BUG-1309-mirror-build-entry — cycle 1 — review_sha d80a7b12

## BLUF

**F1 (my cycle-0 high) is CLOSED.** **PASS** overall — no gating finding stands; F2/F3 (both
non-gating) remain open, carried forward unchanged; the remediation introduces nothing new that
fails open. Note: the batch context's claim that "four grade-2 functions carry function-named
written reasons" is **false for `_run_merge_and_check`** — see F2.

Source read at HEAD; `git diff d80a7b12..HEAD` for every file cited below is empty (only
`feature.json`'s pin field differs from the pinned SHA), confirmed before citing.

## F1 — era-exempt + `recovery-required` denial: CLOSED

Reconstructed scenario: an era-exempt feature (`BUG-1030-stale-anchor-write-hazard`, confirmed
member via `feature_schema.BUILD_ENTRY_ERA_EXEMPT` at the pinned source) whose `feature.json`
records `github.build_entry = "recovery-required"`, merge attempted with `github.sync: true`.

**Direct execution against the pinned script**, scratch fixture built outside the repo tree
(`/tmp/...`, feature dir `FEAT-05-pyyaml-file-parsers`, an era-exempt member, `build_entry:
"recovery-required"`, `git merge test-branch`): `merge-gate.py` exits **0**, stdout empty (no
deny JSON — "no permission decision emitted," matching SC-04's literal wording), stderr: `"…
predates the build-entry receipt … so this merge is allowed."` **Observed decision: ALLOW.**

Source trace confirms why: `merge-gate.py:138` now reads `if feat in
feature_schema.BUILD_ENTRY_ERA_EXEMPT:` with no `entry is None` conjunct (`git show 1ad433b4`
confirms this is the only change to that line) — membership alone returns before the
`entry in {"opened", ...}` check at :141 is ever reached, regardless of `entry`'s value.

Binding test: `tests/integration/test-merge-gate.py:93-96` `"T-05 era-exempt recovery-required
allows"` builds `fixture(feature="BUG-1030-stale-anchor-write-hazard", entry="recovery-required")`
and asserts `returncode == 0`, `d is None`, `"predates" in stderr` — this is the exact scenario
(era member confirmed by direct membership check above, value pinned to `recovery-required`), not
a neighboring one. Ran `tests/integration/test-merge-gate.py` directly: **16/16 ok**.

**Asymmetry checked at all four sites, intact and matches the signed text (D-08, DEC-220,
BRIEF SC-06) exactly, word for word:**
- `check-state.sh:2002` — `if _feat37 in _fs37.BUILD_ENTRY_ERA_EXEMPT or …: continue` — membership alone.
- `gh-sync.py:1361` refuse-gate — membership alone (`entry is None and feature_id not in …`); the
  `recovery-required` arm (`:1375`→`_build_entry_recovery_notice:1380`) never refuses regardless of
  era, and its own era check (`:1380`) is membership alone within that value-filtered call.
- `merge-gate.py:138` — membership alone (this cycle's fix).
- `post-merge-sweep.sh:223` — `if entry is None and feature_id in …: continue` (swept normally) vs.
  `elif entry not in {opened, …}` (retained) — **keyed on the recorded VALUE**, era only bypasses
  retention for the absent case. This is D-08's literal text ("POST-MERGE RETENTION … keys on the
  RECORDED VALUE, not on era membership") and SC-06's literal text, not re-raised as a defect.

## F2 — unruled grade-2 `_run_merge_and_check`: **STILL OPEN, and the batch claim is wrong**

`git diff d80a7b12..HEAD -- tests/integration/test-hooks-install.py` is empty, and `git show
1ad433b4 --stat` shows the remediation touched only `merge-gate.py` and `test-merge-gate.py`. So
`_run_merge_and_check` (`test-hooks-install.py:392`) is byte-identical to what c0 graded: still
CYCLOMATIC 5 / COGNITIVE 6 / ABC 27.0, GRADE 2, no `REASON REQUIRED` answer anywhere — grepped the
whole file for `REASON` (zero hits) and the feature tree for the function name (only c0's own
finding and the T-11 plan task that grew it; no reasoned answer). The batch context's "four
grade-2 functions carry function-named written reasons" does **not** hold for this one — I could
find written `GRADE-2 REASON:` comments only at `merge-gate.py:29` (`direct_merge`) and
`merge-gate.py:118` (`main`); I did not independently verify the third (`case_t06_…` /
`case_t07_…`) but F2's specific function has none. `severity: med` — grade 2 never blocks the
build, so this does not gate; carried forward unchanged from c0.

## F3 — `gh-sync.py:278,282` root-level skip: **STILL OPEN, unchanged**

Untouched by the remediation (confirmed via the same empty diff). Unchanged assessment from c0:
informational/low, not a `must_fix`.

## New-in-remediation hunt: nothing fails open

- **`gh_head`'s `except OSError`** (`merge-gate.py:75-85`): the call passes no `timeout=` kwarg and
  no `check=True`, so `subprocess.TimeoutExpired`/`CalledProcessError` cannot occur here, and the
  argument list is always well-typed strings, so `ValueError` is not a realistic risk for this call
  shape — `OSError` (covers `FileNotFoundError`/`PermissionError` from `execvp`) is the complete
  width for what this specific call can raise. **Dismissed, not a gap.** Traced the `("", str(exc))`
  return through `head_branch:94-95` (empty `branch` → falls to `local_branch(cwd)`, carrying
  `failure`) and `main`: confirmed by direct execution — `GH_BIN=/nonexistent/gh` against a fixture
  whose LOCAL branch matches a feature owing a receipt still **denies** (does not deny "because" the
  read failed — matches DEC-138/SC-04's last clause); against a fixture with no local match it
  **allows** with "could not verify" on stderr. Both cases are also bound by
  `test-merge-gate.py`'s two gh-outage cases, both currently green.
- **Lazy `import feature_schema` inside `main()`** (`:129`): `sys.path.insert(0, …)` (`:10`) runs
  unconditionally at module load, before `ROOT = sys.argv[1]` even, so it precedes the import on
  every route including every early return — no ordering bug. An `ImportError` there is uncaught
  (outside the earlier `try/except Exception` block) and would exit 1 (fail-open, since only exit 2
  denies) — but this is **narrower** than before the fix, when the same import sat at module scope
  and ran on literally every invocation of the script (the hook matcher is `Bash`, i.e. every Bash
  call in the repo per `merge-settings.py:121-123`), not just merge commands with sync enabled.
  **Dismissed as a regression** — it reduces this crash's blast radius rather than introducing it,
  and there is no plausible runtime cause for `feature_schema` (already imported successfully by
  `gh-sync.py` in this same feature) to fail to import at this point.
- Everything else reachable in `main()` outside the initial `try/except` (`merge_ref`, `feature_for`,
  `repo_pinned`, `recovery_command_for`) is either pre-existing and untouched by this diff, or — in
  `recovery_command_for`'s case — now reached by *fewer* inputs post-fix (every era member now
  returns before it, not just era members with an absent receipt). No new exit-0/exit-1-while-owing
  path found.

## Findings summary

| id | severity | disposition |
|---|---|---|
| F1 | high (c0) | **CLOSED** — direct execution + source trace + binding test, all agree: ALLOW at exit 0 |
| F2 | med | **OPEN**, unchanged — non-gating |
| F3 | low | **OPEN**, unchanged — non-gating, informational |

## Open questions

- { id: Q1, question: "The batch context states four grade-2 functions carry function-named written reasons; `_run_merge_and_check` (test-hooks-install.py:392) has none. Should this be corrected in the batch record, and should a reason be written before this ships?", blocking: false }
