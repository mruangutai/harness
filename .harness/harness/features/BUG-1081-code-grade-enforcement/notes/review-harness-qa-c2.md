# QA — gate-only matrix re-run — BUG-1081-code-grade-enforcement — panel cycle 2 @ 2562e45a

**VERDICT input: matrix_ok=false.** The standing `integration` kind is currently RED (exit=1,
7 `^FAIL `), but every one of those 7 failures is isolated to `test-check-plan-routes.py` —
a file BUG-1081 never touches — and traces to a live-corpus drift wholly unrelated to the
reviewed diff (§1). The reviewed diff itself is sound: both halves of
`check_artifact_path_traversal` are measured-discriminating (§2), the new test is genuinely
wired into the standing gate (§3), and T-01's RED evidence — flagged in an earlier cycle as
"receipt-narrated only, could not be reproduced" — **I reproduced it myself this session** (§4),
so that finding no longer holds as stated. Reporting `suite: fail` honestly per rule 15; the
red state is not a defect in this diff.

## 1. Matrix re-run (measured, this session, `test_matrix` read directly from `harness.json`)

Unchanged from c1: `cross_module → {unit, integration} always` (T-01), `bugfix → {unit} always`
+ non-firing `__bug_class__` predicate (T-02), `docs → {}` (T-03/T-04). **Union required =
{unit, integration}.**

```
$ .agents/skills/harness/bin/run-unit-tests.sh --kind unit
exit=0   grep -c '^FAIL ' = 0
34 scripts run (distinct "PASS <name>.py" lines) — non-zero discovery, not an empty sweep.

$ .agents/skills/harness/bin/run-unit-tests.sh --kind integration
exit=1   grep -c '^FAIL ' = 7
```

All 7 `FAIL` lines are in **one script**, `test-check-plan-routes.py`:
`case_04_all_granted_exits_0`, `case_05_ungranted_declared_main_session_exits_0`,
`case_15_deviation_plan_still_exits_0`, `case_17_midpattern_wildcard_grant_exits_0`,
`case_19d_explicit_path_unaffected_by_the_root_guard`,
`case_19d2_explicit_path_with_no_tasks_still_exits_0`, plus the script's own aggregate
`FAIL test-check-plan-routes.py` line. Traced the cause directly: this fixture compares the
**worktree's** `.harness/team-config.yaml` against the **main repo's live copy**
(`/Users/molchairuangutai/GitHub/harness/.harness/team-config.yaml`) and expects them to match.
`diff` confirms the main repo carries commit `860639f6` ("[harness:FEAT-41] T-09: deny every
editor and shell write of plan.yaml") which this branch's `team-config.yaml` does not — a
separate PR merged into `main` after this feature branch's fork point, entirely independent of
BUG-1081. This is exactly the repo's own Gotcha G-15 class ("a live, mutable corpus... the
threshold can flip from unrelated state changes alone"). c1's own re-run (same session type,
different day) reported `exit=0, 0 FAIL` for integration — confirming this is new drift since
c1, not a standing condition BUG-1081 introduced.

Zero of the 7 failures touch `validate-digest.py`/`test-validate-digest.py`. Within the same
red run: `PASS test-validate-digest.py` (line 130) and `ok    code-grade and review-policy
gates` (line 73, the aggregate BUG-1081 line, §3) both pass clean.

**`matrix_ok: false`** — literal, honest state of the standing gate today. **Attribution: 0%
of the failure is in the reviewed diff; 100% is unrelated branch/corpus drift**, out of scope
for a gate-only, author-nothing dispatch to fix (would require rebasing onto `main` or
resyncing `team-config.yaml`, both tree mutations this dispatch forbids).

## 2. `check_artifact_path_traversal` — measured, not vacuous, both halves

Read the implementation: `_contained_feature_dir(root, relative)` (`validate-digest.py:793`)
does two checks — no `.`/`..`/empty segment, then a `startswith(realpath(root) + sep)`
containment check — called from `_feature_dir_from_artifact`. The test has a hostile-refuse
loop (`HOSTILE_ARTIFACT_PATHS`, 4 cases) plus `_assert_honest_artifact_resolves`
(`test-validate-digest.py:2562`).

**Note on harness**: `check_artifact_path_traversal` calls `_fresh_validator()` internally,
which does its own `importlib` load of `validate-digest.py` per invocation (isolates cases from
each other's monkeypatches) — an external patch of an already-imported module has **no effect**
on the module the check actually runs against. I wrapped `_fresh_validator` itself (not the
module) to land the mutation on the instance the check uses. Measured, in-memory only, zero
worktree writes:

- **Probe A — can the hostile-refuse half fail?** Patched `_contained_feature_dir` to bypass
  containment entirely (`return os.path.join(root, relative), None` unconditionally — simulates
  the pre-fix shape). Result: **3 of 4 hostile paths reported unrefused** (`'got
  .../.harness/../features/..'` etc.) plus the `validate()`-level assertion also failed. Both
  levels of the check are discriminating against exactly the pre-fix defect.
- **Probe B — can the honest-resolves half fail?** Patched `_contained_feature_dir` to always
  refuse (`return None, "always refuses"` — simulates an over-refusing regression). Result:
  `_assert_honest_artifact_resolves` failed (`"an honest artifact path must still resolve: None
  'always refuses for probe B'"`), plus the `validate()`-level assertion failed too (both
  hostile digest AND — implicitly — a real one would be refused). This is the accept-half proof:
  a validator wired to refuse everything would NOT pass this check.
- Baseline (unmutated) and restored runs: both clean, `failures: []`, confirming no leakage
  across probes (matches `_fresh_validator`'s own per-case isolation design) and that the probes
  themselves introduced no false positives.

**Both halves are measured-discriminating**, not reasoned. Full probe script:
`/tmp/probe_discrimination2.py` (deleted after use, not committed).

## 3. Binding into the standing gate — not a repeat of c1's §2b blind spot, but not fixed either

`check_artifact_path_traversal` is called from `_check_bug1081_enforcement`
(`test-validate-digest.py:2668-2678`), now the **10th** of what was 9 unconditional calls at
c1 (c1's total including `_check_review_repository`'s 3 was 12; now 13). `test-validate-digest.py`
remains registered under `INTEGRATION_SCRIPTS` only in `run-unit-tests.sh` (confirmed by reading
the array directly, not the `detect` glob) — so it **is** exercised by the standing
`--kind integration` gate and **does** feed the exit code / `^FAIL ` count. It collapses into
the same single `ok    code-grade and review-policy gates` line as the other 12 checks — c1's
§2b discovery-count blind spot (a dropped call line inside the helper would produce an
indistinguishable "ok") **still applies, unchanged in kind, now covering one more check.** Not a
new gap; not fixed either — reported for the record per c1's own framing.

## 4. T-01's RED evidence — re-tested, no longer "could not reproduce"

An earlier cycle (`qa-test-matrix-c1.md`) recorded T-01's RED evidence as receipt-narrated only,
blocked from independent reproduction by `bash-write-guard` denying scratch mutation without a
disposable worktree. This session I built one under the required path
(`bash-write-guard` blocks `git worktree add` outside `.claude/worktrees/`; a worktree placed
there succeeds) at `.claude/worktrees/qa_t01_probe_wt`, detached at current HEAD:

```
$ python3 .claude/skills/harness/bin/test-code-grade.py     # control, unmutated
PASS test-code-grade                                         exit=0

$ git checkout 17a23174~1 -- .claude/skills/harness/bin/code_grade.py   # pre-T-01 content
$ python3 .claude/skills/harness/bin/test-code-grade.py
AttributeError: module 'code_grade' has no attribute '_is_test_path'   exit=1

$ git checkout HEAD -- .claude/skills/harness/bin/code_grade.py         # restore
$ git status --porcelain .   # clean
```

Same failure **class** the receipt claims (`AttributeError: module 'code_grade' has no
attribute ...` against the unmodified-content-reverted tree) — the specific missing attribute
name differs (`_is_test_path` here vs. `classify`/`TestKindsError` in the receipt, because
`check_self_grading` hits a different call first) but the mechanism is the same defect class:
`code_grade.py` genuinely regresses to an import-shaped break when T-01's additions are removed.
**T-01's RED evidence claim is INDEPENDENTLY CONFIRMED at this pin, measured — not merely
receipt-narrated.** The disposable worktree was removed after restore was confirmed clean
(`git worktree remove`, no `--force` needed since the tree was clean).

## 5. Mechanical grader, self-run

```
$ python3 .claude/skills/harness/bin/code-grade.py \
    --base $(git merge-base origin/main 2562e45a) --head 2562e45a
exit=0   RESULT: FAIL count = 0   PASSING: 44
```

Matches the briefing (44 gated functions, `pass`, no blocking/grade-2 record).

## Residual findings

1. **Finding — nature: environmental/harness gap (not a BUG-1081 defect), severity: high for
   gating purposes.** `test-check-plan-routes.py` compares this worktree's `team-config.yaml`
   against the main repo's live copy; the two have diverged via an unrelated commit
   (`860639f6`) merged into `main` after this branch's fork point. This currently reddens the
   `integration` kind (`matrix_ok: false`) with zero relation to the reviewed diff. Belongs to
   whoever rebases this branch or updates the corpus, not to this gate-only dispatch. (Repo
   Gotcha G-15 class, worth citing verbatim if this repeats.)
2. **Finding — nature: chore, severity: low (unchanged from c1, restated per dispatch).**
   §3's discovery-count blind spot: 13 `check_*` fixtures collapse into one "ok" line in the
   standing integration output; a future dropped call line would be silently indistinguishable
   from today's clean run in the runner's own signal.
3. **Resolved, not a residual finding**: T-01's RED evidence, previously flagged as unreproducible,
   is now independently reproduced (§4). The earlier open question is closed.

## Open questions

- Q1 (non-blocking, harness/process gap, not a BUG-1081 code defect): the `integration` kind is
  currently red due to `team-config.yaml` drift against `main`, unrelated to this diff. Whoever
  routes this pin next needs to decide whether to treat `matrix_ok: false` here as blocking the
  panel (it shouldn't gate the traversal fix itself) or resync the branch first. `blocking: true`
  for the matrix literal, `blocking: false` for the security fix under review.

## Files touched

None inside the worktree beyond this note. sha256 of the two reviewed files confirmed unchanged
before and after every probe: `validate-digest.py` = `59c50568...`, `test-validate-digest.py` =
`f1642580...` (full hashes in-session; matches pre-probe values). All scratch mutation happened
either in `/tmp` (deleted) or in a disposable worktree at
`.claude/worktrees/qa_t01_probe_wt` (removed via `git worktree remove` after a confirmed-clean
`git status --porcelain`, per DEC-153).
