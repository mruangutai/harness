# Code review — panel c14 — BUG-1309-mirror-build-entry — ac2bc0bb @ c8b23e03

## BLUF
**FAIL.** The orchestrator's probe claim is **CONFIRMED, and the consequence is confirmed end-to-end
through the real hook** — this is a **regression this delta introduces**, not a pre-existing gap.
`ac2bc0bb`'s new `git_merge` (D-14/R-2) silently drops the Build-entry merge gate for the extremely
common `git merge --no-ff <branch>` form, and independently for `git --exec-path <path> merge <branch>`
(an example D-14 itself names). Both are confirmed with a real PreToolUse payload against a real
fixture: **empty stdout, exit 0, no stderr** — a feature recording `recovery-required` merges clean.
F-01 (D-13, ambiguity-before-era) and F-03 (D-15, derived recovery notice) are correctly built at
source, but F-01's era-exempt-plus-duplicate-claimant clause and F-03's "open" horn are **not pinned
by any test** — both are real, separately reportable gaps the acceptance brief called out by name.

## F-01 — SC-04 clause grading (D-13, merge-gate.py `feature_for`/`main`)
| clause | satisfied at source | pinned by test |
|---|---|---|
| (a) ambiguity before era gate, even for an era-exempt claimant | **yes** — `main.py:150-155` (`len(owners) > 1` deny+return) runs unconditionally, strictly before the era-exempt check at `:157-159`, which only ever sees `owners[0]` | **no** — new test "T-05 duplicate valid records..." (`test-merge-gate.py`, added lines) uses two non-era ids only; no fixture makes one of the ≥2 claimants a member of `BUILD_ENTRY_ERA_EXEMPT` |
| (b) message stable across runs (sorted ids) | yes — `merge-gate.py:151` `sorted(os.path.basename(...))` | yes — same test asserts `reason == repeated_reason` across two runs |
| (c) no receipt/re-run command on ambiguity deny | yes — `merge-gate.py:152` fixed reason string, no `command_line` built | yes — same test asserts `"gh-sync.py" not in reason` |
| (d) valid record, different branch, is noise | yes — `feature_for` (`merge-gate.py:113-122`) only appends when `document.get("branch") == branch` | yes, pre-existing (`de04d841:test-merge-gate.py:79`, "branch matching no feature allows") |
| (e) unreadable/malformed/non-object is noise | yes — `except (OSError, json.JSONDecodeError): continue` + `isinstance(document, dict)` (`:117-121`) | yes, pre-existing + new "single owner plus unrelated malformed record still allows" |
| (f) unclaimed branch stays ALLOWED despite noise elsewhere | yes — `if not owners: ...; return` (`:145-148`) is reached regardless of unmatched records | yes, pre-existing (`de04d841:test-merge-gate.py:147`, "no-record branch ignores unrelated malformed record") |

**Finding RC-01** (severity **med**, `tests/integration/test-merge-gate.py` — an absence, no line):
clause (a) is the one SC-04 states explicitly as a named regression risk ("the deny is reached even
when a claimant IS era-exempt — ambiguity is decided before the era gate") and D-13's own `because:`
cites a real prior regression of this shape. No fixture combines `len(owners) > 1` with an era-exempt
member. **Concrete scenario:** a future edit adds `if any(era-exempt) and len(owners)>1: allow the
era-exempt one` ahead of the ambiguity deny — every existing test still passes, and this exact case
sails through un-caught.

## F-02 — merge_ref / git_merge (D-14) — CONFIRMED REGRESSION, must_fix

Orchestrator's probe reproduced verbatim, myself, against the pin:
```
git merge --no-ff feat/x         -> ('git', '--no-ff')     [pre-change: ('git', 'feat/x')]
git merge --squash feat/x        -> ('git', '--squash')    [pre-change: ('git', 'feat/x')]
git merge -m 'msg' feat/x        -> ('git', '-m')           [pre-change: ('git', 'msg')]
git -C /repo merge --no-ff feat/x-> ('git', '--no-ff')     [pre-change: None — the exact D-14 bug]
```
**Verdict: confirmed, and it is a genuine regression introduced by ac2bc0bb**, not a restatement of the
old bug. Root cause: once `git_merge` (`merge-gate.py:47-60`) matches the `"merge"` token it returns
`rest[index+1]` **unconditionally** — it never resumes the same skip-loop for tokens after the
subcommand. The pre-change parser (`args = [w for w in rest if not w.startswith("-")]`) stripped *all*
dashed tokens regardless of position, so it got post-subcommand options right by accident while
missing global-flag values (the bug D-14 exists to fix) — this delta fixed the global-flag case and
broke the post-subcommand case it used to get right.

**End-to-end proof**, real hook, real fixture (`/tmp/bug1309-e2e`: `.harness/harness.json` sync=true
repo pinned, `.harness/harness/features/feat-x/feature.json` branch=`feat/x`,
`github.build_entry=recovery-required`):
```
$ echo '{"tool_input":{"command":"git merge --no-ff feat/x"}}' | python3 merge-gate.py /tmp/bug1309-e2e
<empty stdout>                                                                  exit=0
$ echo '{"tool_input":{"command":"git merge feat/x"}}'        | python3 merge-gate.py /tmp/bug1309-e2e
{"hookSpecificOutput":{...,"permissionDecision":"deny","permissionDecisionReason":"merge-gate: feat-x
records github.build_entry=recovery-required..."}}                              exit=0
```
Run through the **pre-change** script (`git show de04d841:...merge-gate.py`, same fixture): both
commands correctly deny. **`git merge --no-ff <branch>` is an everyday merge invocation** (forcing a
merge commit) — this is not an exotic shell-quoting corner, it is the common case, and it now bypasses
the gate silently (no stderr line either — the DEC-138 "could not verify" message never fires because
`feature_for("--no-ff")` finds nothing and there is no `failure` to report).

**Second, independent instance — same defect class, a decision-named example.** D-14's own text lists
`--exec-path` as an example value-taking global; `merge-gate.py:47-48`'s `takes_value` set omits it.
```
$ python3 -c 'import merge-gate as mg; print(mg.merge_ref("git --exec-path /x merge feat/x"))'
None
```
Confirmed end-to-end against the same fixture: `git --exec-path /custom/libexec merge feat/x` →
empty stdout, exit 0 — the merge is never even recognized as a merge, so the whole gate is skipped.
This is exactly the "closed list is a hole" failure mode D-14's own `because:` warns against.

**Test coverage:** the new tests added in this delta (`git -C {root} merge feature/test`, `git -c
core.pager=cat merge feature/test`, `git --work-tree {root} merge feature/test`) all put the branch
*immediately* after `merge` with nothing following it — none combine a global flag with a trailing
option, and none test a bare post-subcommand option (`--no-ff`, `-m`, `--squash`) at all. The
regression is **100% invisible to the shipped suite** — confirmed by reading every new/changed
assertion in `test-merge-gate.py` and by the literal probe outputs above.

**Findings:**
- **RC-02, critical, `merge-gate.py:47-60`** — `git merge --no-ff <branch>` (and any option after the
  subcommand) is silently allowed for a feature owing a Build-entry receipt. Command: `git merge
  --no-ff feat/x` while `feature.json` records `recovery-required`. Outcome: exit 0, no stdout, no
  stderr — indistinguishable from an unrelated command. **must_fix.**
- **RC-03, high, `merge-gate.py:47-49`** — `takes_value` omits `--exec-path`, named by D-14 itself.
  Command: `git --exec-path /x merge feat/x` against the same owing feature. Outcome: `merge_ref`
  returns `None`, the gate exits before evaluating anything, silent allow. **must_fix** (same class,
  narrower trigger).
- **RC-04, info, `merge-gate.py:47-60`** — `git merge --abort` / `git merge --continue` resolve to
  `('git', '--abort')` / `('git', '--continue')` post-change vs. `('git', None)` pre-change (which fell
  through to `local_branch(cwd)`). Neither D-14 nor SC-04 names this case; flagging as a silent
  behavior change, not a scored violation — `feature_for('--abort')` almost never matches a real
  branch so the practical exposure is low, but it is a symptom of the same missing "keep walking past
  the subcommand" fix.
- Correctly **not** detected (matches pre-change, no finding): `git commit -m 'merge feat/x'`, `git
  log --merges` — both return `None` on pre- and post-change parsers.

## F-03 — `_build_entry_recovery_notice` (D-15, gh-sync.py:1379-1396)
Both horns read correctly at source: the `"open"` horn (`:1387-1391`) is **byte-identical** to the
pre-change unconditional string (`git show de04d841:...gh-sync.py:1386-1388`); the non-open horn
(`:1392-1395`) derives from `feature_schema.recovery_command_for(feat_dir)` and never emits `"open"`.
The classifier match against merge-gate.py's own deny (`command_name = feature_schema
.recovery_command_for(feat_dir)`, `merge-gate.py:166`) is the same function, same call shape — no
duplicated literal.

**Finding RC-05, med, `tests/integration/test-gh-sync.py`** — `grep -rn "MERGE is refused" tests/`
returns **zero matches**. The new test at `test-gh-sync.py:3618-3629` drives only the recover-terminal
horn (`expected_command == "recover-terminal"`); no fixture ever makes `recovery_command_for` return
`"open"` for a non-era feature through `_build_entry_recovery_notice`, so the retained-verbatim `"open"`
horn — arguably the *more common* real case, since `recovery-required` is typically recorded early in a
feature's life, before any task is done — has no regression test at all. A typo or a broken `if
command == "open":` guard would ship silently.

## Stage 2 — quality
- `feature_for` ordering: `owners[0]` is only used once `len(owners) <= 1`, so the prior
  `glob.glob`-order non-determinism D-13 exists to close is fully eliminated on the single-owner path;
  no remaining order-dependence.
- `main()` exit ladder matches D-13's required order exactly (ambiguity → era → terminal states → repo
  pinning → deny), confirmed by reading `merge-gate.py:133-176` top to bottom.
- **code_grade: `grade_2`** — `merge-gate.py:133 main` graded CYCLOMATIC 19 / COGNITIVE 22 / ABC 45.0,
  bar 4, **grade 2**, `SEVERITY: med`, `REASON REQUIRED: main`. Reasoned answer: the function already
  carries an in-file `GRADE-2 REASON` comment ("this is the gate's orchestration boundary; helpers own
  parsing, resolution and rendering, while this function preserves the policy's ordered exits") that
  predates this delta; the added ambiguity branch is one more linear, unnested early-exit in the same
  ladder, not new nesting — consistent with the existing rationale, not a new complexity source. Grade
  2 does not block per the skill. Three other grade-2 records in the same canonical range
  (`test-check-state.py:4621`, `test-hooks-install.py:396`, `test-post-merge-sweep.py:885`) belong to
  T-06/T-07/T-10, outside this delta's four-file set — not analyzed here.

## Fail-open hunt
The two must_fix findings above (RC-02, RC-03) **are** the fail-open findings — both are lookup misses
(`merge_ref` returning the wrong value / `None`) that sail straight through to an allow with zero
signal. No other fail-open branch found in the diff; the outer `except Exception: return` in `main()`
(fail-open on unreadable `harness.json`/stdin) is unchanged from pre-change and out of this delta's
scope.

```yaml
VERDICT: FAIL
DIGEST:
  headline: "Confirmed, end-to-end: ac2bc0bb's git_merge silently allows `git merge --no-ff <branch>` and `git --exec-path <p> merge <branch>` for a feature owing a Build-entry receipt — a regression this delta introduces, invisible to its own new tests."
  severity_max: critical
  findings: 5
  must_fix:
    - "RC-02 (critical, merge-gate.py:47-60): git merge --no-ff <branch> (or any option after the subcommand) bypasses the merge gate silently — confirmed end-to-end with a real PreToolUse payload"
    - "RC-03 (high, merge-gate.py:47-49): takes_value omits --exec-path (named by D-14 itself), so git --exec-path <p> merge <branch> is not even recognized as a merge — confirmed end-to-end"
  spec_violations:
    - { kind: omission, path: tests/integration/test-merge-gate.py, ref: D-14 }
  code_grade: grade_2
  reviewed: "de04d841..c8b23e03ce5ed6ecc5f667f0c8a4bb4496ababa9"
  human_commits_in_scope: []
  open_questions:
    - { id: Q1, question: "The probe claim in the batch context is CONFIRMED as a real regression (not merely a pre-existing gap) — should T-05 be reopened rather than closed as done, given plan.yaml/c8b23e03 already marked it complete?", blocking: true }
  files_touched: []
  expertise_update: []
artifact: /Users/molchairuangutai/GitHub/harness/.claude/worktrees/harness/BUG-1309-mirror-build-entry/.harness/harness/features/BUG-1309-mirror-build-entry/notes/review-harness-code-reviewer-c14.md
```
