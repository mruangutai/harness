# Code review — BUG-1309 c15 — merge parser fix (`e374c9a2`)

**BLUF: FAIL.** The rewritten `git_merge` (`merge-gate.py:46-73`) fixes VP-01's exact defect for
`--no-ff/--squash/-m/...` but leaves the SAME defect class open for two other realistic option
forms (F2, F3 — SILENT ALLOW, SC-04(a) still unmet), introduces one NEW spurious deny not present
before (F4 — `git merge --abort`), and the rewritten function itself measures GRADE 3 against a
grade-4 production bar (F1) — the orchestrator's "grade 4" claim is wrong. VP-02 is falsified as
moot (real git behaviour). All measurements below are reproductions I ran, not restated claims.

## F1 — code_grade correction (HIGH, must_fix)
Orchestrator claimed `git_merge` grade 4. Measured directly, twice: full range
`merge-base(origin/main, e374c9a2)..e374c9a2` **and** isolated to this delta `da6da610..e374c9a2`
— identical result both times:
```
.claude/skills/harness/bin/merge-gate.py:46 git_merge  CYCLOMATIC 8  COGNITIVE 15  ABC 16.1
GRADE 3  DRIVER cognitive  BAR 4  RESULT FAIL  SEVERITY high
```
Command: `python3 .claude/skills/harness/bin/code-grade.py --base da6da610 --head e374c9a2` — this
is the ONLY gated record in the isolated delta (`PASSING: 0`), so the regression is introduced by
this fix's own rewrite (old `git_merge` was a single unnested walk; new adds a second nested
`while` for merge-phase options — textbook "give one loop to one function" per
harness-code-risk-grading). Report `code_grade: fail` — `validate-digest.py` will independently
recompute this and refuse `grade_4`/`pass`.

## F2 — PB confirmed: value-taking merge options still silently allow (HIGH, must_fix)
`merge_values` (`merge-gate.py:50-51`) omits `-F`/`--file` and `--cleanup`. Confirmed real git
accepts space-separated forms (`git merge -F msg.txt feature/test` and `git merge --cleanup strip
feature/test` both completed real fast-forward merges, rc=0, in a scratch repo). `git_merge` skips
`-F`/`--cleanup` as a bare flag (+1, not +2) and returns the FOLLOWING token (`msg.txt`/`strip`) as
the branch — `feature_for("msg.txt")` finds no owner. End-to-end against a `recovery-required`
fixture: both commands return `decision=None` (no permission decision) instead of `deny`. This is
the same fail-open shape VP-01 named, unresolved for this subset, and a direct violation of SC-04(a)
("every realistic operator merge form is denied — including forms carrying merge options between
merge and the ref").

## F3 — PC confirmed: value-taking global option still silently allows (HIGH, must_fix)
`global_values` (`merge-gate.py:47-48`) omits `--attr-source` (real, git ≥2.43, confirmed accepts
space form: `git --attr-source main status` rc=0). `git_merge` treats it as a bare flag (+1), then
sees `main` — not `-`-prefixed, not `"merge"` — and returns `None` outright. `merge_ref()` returns
`None`, so `main()`'s very first gate (`if not github.get("sync") or not merge_ref(command): return`)
fires with **no stderr note at all** (quieter than the gh-unavailable path). End-to-end: `git
--attr-source main merge --no-ff feature/test` against a `recovery-required` fixture ->
`decision=None`. Second, independent SC-04(a) violation at this SHA.

## F4 — PA confirmed: new spurious deny on `git merge --abort/--continue/--quit` (HIGH, must_fix)
Source archaeology + runtime, both ways: OLD `git_merge(['merge','--abort'])` -> `('git','--abort')`
(the literal string, never a real branch -> always silently ALLOWED, same fail-open family as VP-01
but harmless here by coincidence). NEW -> `('git', None)`, so `head_branch()` falls back to
`local_branch(cwd)` — the actual CURRENT branch. End-to-end: on a fixture whose current branch owes
`recovery-required`, `git merge --abort` now **denies**, citing the Build-entry receipt; on a
healthy fixture it allows. Reachable ordinarily: `git merge main` into your own feature branch is
NOT itself gated (branch resolves to `main`, no owner), so a developer can hit a conflict, then find
the unrelated cleanup command (`--abort`/`--continue`) blocked by a confusing receipt-themed deny —
introduced by this delta, not present at `da6da610`.

## VP-02 — MOOT, falsified (no finding)
Measured: `--exec-path` only accepts a value via `=`; `git --exec-path /x status` prints the
exec-path and exits 0 WITHOUT consuming `/x` and WITHOUT reaching any subcommand after it — so
`--exec-path /x merge ...` can never execute a merge in real git regardless of the parser. The
`=`-form (`--exec-path=/x`) is one token and is already correctly skipped by the generic
`token.startswith("-")` branch — confirmed `merge_ref('git --exec-path=/x merge --no-ff
feature/test')` -> `('git','feature/test')`, hook denies correctly. Drop VP-02 from future carry.

## VP-05 — partially falsified (LOW, advisory, out of this delta's scope)
Measured the actual `open`-recovery deny reason: it DOES include the realpath'd `<feature-dir>`
(`...gh-sync.py open /…/FEAT-9001-fixture-non-era records one.`). VP-05's substantive claim ("prints
a command with no `<feature-dir>`") is false at this SHA. The narrower half stands: no test asserts
that substring, only `"gh-sync.py open" in reason`. `main()` is untouched by `da6da610..e374c9a2`
(confirmed: isolated code-grade diff shows only `git_merge`), so this is pre-existing and non-gating.

## VP-03, VP-04, VP-06 — unchanged, still open, non-gating, out of this delta's scope
`main()`/`feature_for()` carry no changes in `da6da610..e374c9a2` (confirmed by the isolated
code-grade diff above showing zero other gated/changed records). Their status from c14 stands as
carried; none gates this review.

## Q1 — SC-04(a) re-derivation
Standing suite: `env -u HARNESS_AGENT_TYPE python3 tests/integration/test-merge-gate.py` -> 27/27
`ok`, `ALL PASSED` — confirms orchestrator's claim exactly. Independently re-drove 13/13 deny-forms
and 6/6 allow-bounds from the panel's list through the real `merge-gate.sh` hook via a fresh fixture
harness (not the suite's own code) — all matched. Also reconfirmed the duplicate-claim deny still
fires with an option-bearing form (`--no-ff`) and the gh-unavailable-with-owed-receipt path still
denies. **But** SC-04(a) as written ("every realistic operator merge form is denied") is not fully
met at this SHA — F2 and F3 are counter-evidence the suite's own case list doesn't cover.

## Stage 1 — spec compliance
Diff traces to REQ-07/SC-04 (T-05). Two added test cases are option-bearing deny-form regression
guards, correctly scoped. No scope creep. The gap is omission, not mismatch: SC-04(a)'s explicit
"including forms carrying merge options between merge and the ref" is not satisfied for `-F`,
`--file`, `--cleanup`, or any value-taking global option beyond the six enumerated.

```yaml
VERDICT: FAIL
DIGEST:
  headline: "git_merge measures grade 3 (not the claimed grade 4) and SC-04(a) is still unmet — two option forms (-F/--file, --cleanup, --attr-source) silently allow, plus a new spurious deny on merge --abort/--continue/--quit"
  severity_max: high
  findings: 7
  must_fix:
    - "F1: git_merge (merge-gate.py:46) grades 3, below the grade-4 production bar, driver cognitive=15 — code_grade: fail"
    - "F2: merge_values omits -F/--file/--cleanup — git merge -F msg.txt feature/test and git merge --cleanup strip feature/test silently allow (SC-04(a) violation)"
    - "F3: global_values omits --attr-source — git --attr-source main merge --no-ff feature/test silently allows with no stderr note (SC-04(a) violation)"
    - "F4: git merge --abort/--continue/--quit now falls back to the current branch and can be spuriously denied on a feature branch that owes a receipt, a regression introduced by this delta"
  spec_violations:
    - { kind: omission, path: ".claude/skills/harness/bin/merge-gate.py:50-51", ref: "SC-04" }
    - { kind: omission, path: ".claude/skills/harness/bin/merge-gate.py:47-48", ref: "SC-04" }
  code_grade: fail
  reviewed: "da6da610..e374c9a29e4321968e4c2a6bbae045da9203440c"
  human_commits_in_scope: []
  open_questions:
    - { id: Q1, question: "Should git merge --abort/--continue/--quit be excluded from git_merge's ref-detection entirely (return None, not (\"git\", None)), since they never introduce branch content and shouldn't be receipt-gated at all?", blocking: false }
  files_touched: []
  expertise_update: []
artifact: /Users/molchairuangutai/GitHub/harness/.claude/worktrees/harness/BUG-1309-mirror-build-entry/.harness/harness/features/BUG-1309-mirror-build-entry/notes/review-harness-code-reviewer-c15.md
```
