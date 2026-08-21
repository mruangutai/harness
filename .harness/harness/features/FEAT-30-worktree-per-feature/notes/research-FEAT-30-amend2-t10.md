# FEAT-30 amend round 2 — T-10 assessment. I WROTE NOTHING to plan.yaml.

**The idempotence clause fired.** Pre-write, with a real shell: `plan.yaml` **1383** lines (not
1243), `BRIEF.md` **250** (matches), `grep -c 'T-10' plan.yaml` = **5** (not 0). The dispatch's rule
is explicit for both conditions: write nothing, assess, report. This file is the assessment.

**The dispatch's premise about round 1 is falsified.** Round 1's pm was NOT force-closed before its
artifact. `notes/research-FEAT-30-amend.md` exists (7641 bytes, mtime 09:37 — it appeared *after* my
own first directory listing at 09:36) and reports pre-write counts 1171/219, post-write 1383/250.
That run landed the whole amendment, T-10 included; the operator's 1243/T-10=0 read was a snapshot
taken mid-write of that same run. There was no gap to close.

## T-10 as it stands, against this round's requirements — all four MET

- **Concurrency and the barrier.** One driver, four concurrent committers, five commits each, hard
  barrier timeout that fails rather than hangs, and a **pairwise write-window overlap assertion over
  all six pairs**. Assertions are stated per tree, never in aggregate, including the
  every-unrelated-branch-tip-unchanged-by-sha half.
- **The discriminating negative is IN the task, specified to build:** the same driver against ONE
  shared checkout of repoA, four children on one branch, requiring `assert_commit_isolation` to raise
  `IsolationViolation` via `try/except/else`-is-a-failure, and accepting a recorded committer failure
  (index lock, non-zero git exit) as the alternative collision signal. Anti-vacuity is enforced a
  third time by the task's own `verify`, which neuters the predicate BY NAME in a copy and requires
  the suite to go red. This is criterion 9 satisfied by a fixture, not a claim.
- **T-08 needed no change, and that is the right answer.** T-10 adds cases to
  `test-feature-worktree.py`, a file T-08 already registers in BOTH places. Verified at HEAD:
  `run-unit-tests.sh` builds `ALL_SCRIPTS` as the union (`:39`) and exits 2 MISCONFIGURED on an
  unlisted `bin/test-*.py` (`:52-53`); `--kind integration` selects `INTEGRATION_SCRIPTS` only
  (`:31`); `integration.detect` (`harness.json:119`) is an explicit four-file list. T-08's intent
  names the array by name and forbids `UNIT_SCRIPTS`, and edits `integration.detect` — so the
  operator's third correction is CONFIRMED and already discharged.
- **The failure-cost statement is an evidence-backed OVERTURN, not an adoption.** It lives at
  `approval.rulings` R-02 `fix_surfaces_if_sc01b_fails` and drops two thirds of the operator's read.
  I re-verified each reason at source: `bash-write-guard.sh` is registered PreToolUse **Bash** only
  and `check-domain.sh` PreToolUse `Write|Edit` + PostToolUse (`.claude/settings.json`), so T-05's
  refusal cannot see a `subprocess` fork from inside a python test — T-05 is correctly excluded;
  T-02 owns removal (`traces: [REQ-03]`) and T-10 never calls remove; T-06 owns REQ-06/SC-08.
  Remaining surfaces: T-10's own fixture, then T-01's create and destination derivation.
- **Lane, hand-checked against DEC-174.** The index reads DEC-174 as hooks, validators and gate
  scripts, am.4 extending it to `check-plan-routes.py` *and its test*. `feature-worktree.py` appears
  in NO hook block of `.claude/settings.json`, so it is not a gate and its test is not enforcement
  layer. T-10's single file is not `bash-write-guard.sh`, `check-domain.sh`, `harness_boundary.py`,
  nor either guard's test. **Legitimately `team` / `harness-dev-ops`.**

Loader check: `harness_yaml.load_plan` parses the file; T-10's `verify` is a literal block (20
newlines preserved), all required fields present, 10 tasks, 9 decisions, `approval.status: pending`.

## Four defects the other artifact does not name

1. **`traces: [REQ-01, REQ-03]` is wrong on REQ-03.** REQ-03 is removal plus artifacts reaching the
   default branch, and T-10's intent states it never calls remove. Nothing in T-10 exercises REQ-03.
   Case A's unrelated-tips-unchanged and HEAD-names-own-branch clauses point at **REQ-02**. This is
   the field goal-check traces REQ coverage through, so a claim the task cannot discharge here shows
   up later as false coverage. One-token fix: REQ-03 -> REQ-02.
2. **The red proof is exit-status-only.** `python3 "$T/t.py" && fail` treats ANY non-zero exit of the
   copied file as proof the predicate was load-bearing — an ImportError from running outside
   `BIN_DIR`, a missing git identity, anything. Tighten it to require the neutered run's output to
   contain case B's own `AssertionError` string.
3. **"Twelve absence assertions" undercounts.** Four trees x three others = 12 pairs, each carrying
   two clauses (`ls-tree -r` file absence AND `merge-base --is-ancestor`) = 24 assertions over 12
   pairs. Wording nit only; the shape is right.
4. **The failure budget is parked inside `approval:`.** A reader hunting a fix-surface list reads
   `decisions:` or `tasks:`, and anything that rewrites the approval block on signature takes the
   budget with it. Placement was the operator's own criterion 15, so this is a durability note.

## Non-defect, checked because it looked like one

`unit.detect` (`harness.json:105`) carries the glob `.claude/skills/harness/bin/test-*.py`, so
`test-feature-worktree.py` matches `unit` by pattern while T-08 puts it in `INTEGRATION_SCRIPTS`
only. No exclusivity rule exists anywhere: the qa gate uses `detect` per kind to confirm a test
covers the change (`harness-qa-gate/SKILL.md:57`), and the exit-2 gate is the runner's union. The
overlap already holds for all four currently-listed integration files, so it is pre-existing and
predates this feature. SC-01b's `evidence: integration` is sound.

Scope held: nothing written but this file. No commit. Q11-Q20 untouched. `approval.status` pending,
`BRIEF.md ## Approval` still `approved` and unedited by me.

---

# Cycle 1 send-back — the three T-10 edits are WRITTEN. plan.yaml 1383 -> 1395 lines.

`check-plan-routes.py` exits 0, **0 violations**, DEVIATION on T-03/T-04/T-05 only (expected).
`harness_yaml.load_plan` still parses; T-10 `verify` remains a literal block (31 newlines);
`bash -n` on the extracted verify is clean; `approval.status` still `pending`; 10 tasks, 9 decisions.
Uncommitted, as instructed. `BRIEF.md` untouched; `approval:` untouched; T-01..T-09 untouched.

## Edit 1 — `traces: [REQ-01]`. The operator is RIGHT and I do NOT overturn.

I dropped my own proposed REQ-03 -> REQ-02 swap. The discriminating check: grep T-10's whole entry
for `merge-base|default branch|main|cut from|ancestor`. It returns exactly two hits, and neither is
REQ-02:

- the single `merge-base --is-ancestor` is the **peer-absence** clause — no OTHER tree's sha is
  reachable. Absence between siblings, not ancestry from the default branch.
- the only `default branch` mention is *"catches a commit landing on a default branch"* — that is
  absence of advancement on an unrelated tip, not the origin of the cut.

REQ-02 is asserted **against the merge-base** (`BRIEF.md:147-149`, SC-02) and T-10's trees are
created *"through the CLI exactly as the SC-01 cases create them"* — it inherits the cut and never
asserts it. There is no clause to cite, so there is nothing to overturn with. Swapping would have
substituted a weaker unsupported claim for a stronger one; rule 15 and rule 6 both land on dropping.
REQ-01 stands alone and is genuinely discharged: its closing clause is four worktrees, four branches,
at once, which is exactly what the driver drives.

## Edit 2 — the red proof now reads the OUTPUT, not just the exit status.

`$T/neutered.out` captures stdout+stderr; the run is scored three ways instead of one:

- **exit 0** -> `RED PROOF FAILED: the suite PASSES with assert_commit_isolation neutered - the case
  B assertions are vacuous`, plus `cat` of the output, exit 1.
- **non-zero but the output lacks `MARKER`** (`assert_commit_isolation did not detect the
  shared-checkout collision`, case B's own string) -> `RED PROOF INCONCLUSIVE: the neutered suite
  exited $RC but THE SUITE BROKE rather than case B failing - its output does not contain the case B
  marker: $MARKER`, plus `cat`, exit 1.
- **non-zero WITH the marker** -> the predicate was load-bearing; the verify continues to the real
  suite and the two runner kinds.

The two failures are worded so an ImportError, a missing git identity, a bad `FEATURE_WORKTREE_BIN`
or an unusable `mktemp` path can no longer be scored as proof. The signature assert is untouched.
Nothing is discarded to `/dev/null` on either failure path.

## Edit 3 — the count.

Now reads: *"...read with merge-base --is-ancestor. Twelve ordered pairs carrying two clauses each -
twenty-four absence assertions, not one count - the same shape SC-01's absence cases already use."*

## Residual risk I did NOT fix, because it is intent, not interpretation (see Q1)

Case B accepts EITHER a raised `IsolationViolation` OR *"a recorded committer failure"*. On a neutered
run where the shared fixture happens to hit an index lock, case B is satisfied by the second path,
the marker never prints, and the suite may pass outright — so the red proof reports `RED PROOF FAILED`
for a reason that is not vacuity. Both outcomes are honest failures rather than false greens, and a
re-run resolves it, but it is a flake surface in a `verify`. Closing it means making case B
deterministic under neutering, which changes T-10's intent and was not in this cycle's three-edit
scope.
