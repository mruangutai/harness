# QA merge-delta review — FEAT-43 (merge commit `1d292c2`)

**BLUF:** All five orchestrator measurements (a–e) reproduced by my own runs, with the exact
numbers claimed. Item f confirmed by execution: all three FEAT-43 test files are matched by the
kind they're registered under, and `run-unit-tests.sh --check-kinds` (the shipped cross-check)
agrees the two arrays and `test_kinds.integration.detect` are consistent. One correction to the
orchestrator's item-b explanation (arithmetic, not a defect, `severity: info`). **Send-back
correction:** the `test-validate-feature-json.py` (`case_root_resolves`) failure under `--kind
unit` is **caused by the merge**, not pre-existing — confirmed by parent-vs-merge experiment
below, `severity: med`, now in `must_fix`. Tree is byte-identical to the merge; HEAD unmoved.

## a. Derived-range gate

Read `validate-digest.py:597-618` (`_default_branch_or_none`): resolves via bare
`git symbolic-ref -q refs/remotes/origin/HEAD` — confirmed in this worktree that ref resolves to
`refs/remotes/origin/main` (`git symbolic-ref -q refs/remotes/origin/HEAD` → exit 0,
`refs/remotes/origin/main`). So the correct derived base is `origin/main` = `6d6d1ce`, not the
stale local `main` (`7ebfc9e`, confirmed via `git rev-parse main`).

Ran: `python3 code-grade.py --base 6d6d1ce --head HEAD --json` (cwd
`.agents/skills/harness/bin`) → **exit 0**. Parsed the JSON: **201** records (gated), **0**
blocking (`grade < bar and grade != 2`), **12** at `grade == 2` (`REASON REQUIRED`), `ungraded: []`.
**CONFIRMED exactly** — matches the orchestrator's 201/0/12 claim.

Did not execute the `git merge-base main HEAD` variant (explicitly told not to use it as the
gate's base) — but did run it standalone to confirm the trap is real: it resolves to `7ebfc9e`,
the same stale local `main` tip, confirming the range widening the orchestrator described.

## b. Crash sweep

Ran: `python3 code-grade.py *.py --json` over all `bin/*.py` (94 files by `ls *.py | wc -l`) →
**exit 1** (non-crash: caused by 118 blocking records at bar, not an exception — stderr empty,
valid JSON produced), `ungraded: []`. **0 crash CONFIRMED** — a genuine crash (unhandled
exception during AST parsing; `code_grade.py` has no per-file `except`) would abort the whole
process with a traceback and no JSON output; none occurred.

**94-not-99 reason — orchestrator's explanation is incomplete, count is right.** Diffed
`bin/*.py` between the feature tip (`cbdadef`, 99 files) and `HEAD` (94 files): **6** files were
removed (`context-watch.py`, `context-watch-hook.py`, `test-context-watch.py`,
`test-context-watch-cli.py`, `test-context-watch-hook.py`, `verify-context-watch-live.py`) and
**1** file was added from main (`probe-omp-session-accessor.py`): 99 − 6 + 1 = 94. The
orchestrator's claim names only 2 of the 6 removed files and omits the +1 addition; the two it
named are real deletions, but "94 not 99 because main deleted context-watch.py and
context-watch-hook.py" alone would arithmetically give 97, not 94. Count (94) and crash count (0)
are both confirmed; the stated reason is a partial account. `severity: info` — no functional
impact, just an imprecise explanation.

## c. Engine self-grade

Ran: `python3 code-grade.py code_grade.py --json` → **exit 0**, **53** functions, **0** below
grade 4, `ungraded: []`. **CONFIRMED exactly**.

## d. Six focused suites

Located the set from prior QA notes (`notes/qa-delta-c28.md`, five suites) plus
`test-run-unit-tests-kinds.py` as the sixth (present in `INTEGRATION_SCRIPTS`, referenced
extensively across the feature history as a matrix-drift regression test). Ran each individually
in `.agents/skills/harness/bin`:

| suite | exit | tail evidence |
|---|---|---|
| `test-code-grade.py` | 0 | `PASS test-code-grade` |
| `test-code-grade-cli.py` | 0 | `PASS test-code-grade-cli` |
| `test-gate-policy.py` | 0 | all `ok` lines |
| `test-check-plan-routes.py` | 0 | `ALL PASS` |
| `test-validate-digest.py` | 0 | `18/18 reviewer severity_max enum checks passed. ALL PASSED.` |
| `test-run-unit-tests-kinds.py` | 0 | `23 of 23 cases passed` |

All six **exit 0, CONFIRMED**.

## e. Byte-untouched check

Ran two `git diff baa96b7e HEAD --` invocations (corrected two paths from the dispatch's
assumption: glossary lives at `.harness/glossary.md`, not `.claude/skills/glossary.md`; the two
SKILL.md files are `harness-code-risk-grading/SKILL.md` and `harness-qa-gate/SKILL.md`, confirmed
as the feature's own skill surfaces):

```
git diff baa96b7e HEAD -- .claude/skills/harness/bin/code_grade.py .claude/skills/harness/bin/code-grade.py \
  .claude/skills/harness/bin/gate_policy.py .claude/skills/harness/bin/test-code-grade.py \
  .claude/skills/harness/bin/test-code-grade-cli.py .claude/skills/harness/bin/test-gate-policy.py \
  .claude/skills/harness/bin/check-plan-routes.py .claude/skills/harness/bin/test-check-plan-routes.py
→ 0 bytes output (empty)

git diff baa96b7e HEAD -- .claude/skills/harness-code-risk-grading/SKILL.md \
  .claude/skills/harness-qa-gate/SKILL.md .harness/glossary.md
→ 0 bytes output (empty)
```

**CONFIRMED EMPTY** — FEAT-43's own source is byte-untouched by the merge.

## f. Matrix registration — confirmed by execution, not by reading config alone

Read `.harness/harness.json` `test_kinds`: only `test-code-grade-cli.py` appears as an explicit
literal in `integration.detect`; `test-code-grade.py` and `test-gate-policy.py` do not appear
there (they reach `unit` only via `unit.detect`'s catch-all `.claude/skills/harness/bin/test-*.py`
glob). Read `run-unit-tests.sh`: `test-code-grade.py` and `test-gate-policy.py` are in
`UNIT_SCRIPTS`; `test-code-grade-cli.py` is in `INTEGRATION_SCRIPTS`.

Ran the shipped cross-check itself: `bash run-unit-tests.sh --check-kinds` → **exit 0**,
`check-kinds: the script arrays and test_kinds.integration.detect agree.` (Note the check's own
documented scope, read at `run-unit-tests.sh:82-88`: it is a set-membership comparison — every
`INTEGRATION_SCRIPTS` name must appear literally in `integration.detect`, and no `UNIT_SCRIPTS`
name may appear there — it deliberately does NOT adjudicate "which kind wins" when a catch-all
glob and an explicit entry could both apply, because that question is undecided by design.)

Then ran the two kinds directly and grepped for each of the three FEAT-43 files to see which
array actually executes and passes them:

| file | registered in | ran + passed under | matches registration? |
|---|---|---|---|
| `test-code-grade.py` | `UNIT_SCRIPTS` | `--kind unit` → `PASS test-code-grade.py` | **yes** |
| `test-gate-policy.py` | `UNIT_SCRIPTS` | `--kind unit` → `PASS test-gate-policy.py` | **yes** |
| `test-code-grade-cli.py` | `INTEGRATION_SCRIPTS` + explicit `integration.detect` entry | `--kind integration` → `PASS test-code-grade-cli.py` | **yes** |

All three FEAT-43 tests are discovered and pass under exactly the kind they're registered in,
after main's changes to `run-unit-tests.sh`. `run-unit-tests.sh --kind unit` full run: **exit
1**, but the single failure is `FAIL test-validate-feature-json.py` (`case_root_resolves`), a
file **unrelated to FEAT-43** — `git diff baa96b7e HEAD --` and `git diff cbdadef HEAD --` both
produce zero output for `test-validate-feature-json.py`/`validate-feature-json.py`, i.e. neither
the merge nor FEAT-43's own commits touched it; it appears to be an environment-sensitive
pre-existing case (it sweeps the real repo's `.harness/*/features/*/feature.{json,yaml,yml}`
tree and counted 41 files at run time). **Correction (send-back): this attribution was wrong —
see the "Send-back" section below.** `--kind integration` full run: exit 0,
`INTEGRATION_EXIT=0`.

## Adequacy judgement

**This sweep is sufficient evidence that the merge preserved FEAT-43's guarantees.** Every
orchestrator-cited number reproduced exactly by an independent run (a, c, d, e byte-for-byte; b's
count and crash-freedom exactly, only its stated *reason* was incomplete); item f additionally
proves by execution — not by reading config — that the hand-resolved matrix conflict actually
routes each FEAT-43 test file to the kind it claims, and that `run-unit-tests.sh`'s own drift
cross-check (main's replacement code) still agrees with `harness.json`.

**What this sweep does NOT cover, stated plainly:**
- **Main's own content was not re-reviewed on its merits.** `validate-digest.py`'s automatic
  +34/−8 merge, the `dispatch-guard.sh`/`inflight_registry.py`/`check-omp-port.py` changes, the
  agent-template changes, and the `context-watch` removal are accepted as main's own reviewed
  work, not independently re-audited here — only their *interaction* with FEAT-43's surfaces
  (the gate, the matrix, the SEC-01 range binding) was exercised.
- The eight previously-closed FEAT-43 defects were not re-reviewed.
- No canonical/project-wide suite, formatter, or linter was run.
- No new tests were written for this pass's own scope (send-back below required one targeted
  experiment, not a new test — see below).

## Final state

`git -C <worktree> status --porcelain` → only this artifact and sibling reviewers' own artifacts
(`review-harness-code-reviewer-mergedelta.md`, `review-harness-security-reviewer-mergedelta.md`),
no source touched. `git rev-parse HEAD` → `1d292c2b2e22486fd7ad47fa9021ddec880dabcb`, unmoved.

---

## Send-back: attributing `case_root_resolves` — pre-existing or merge-caused

**My original conclusion was wrong, and the sweep above shows exactly why it was wrong: "the
file is byte-identical between refs" says nothing about a test whose subject is the tree around
it, not its own source.** Re-litigated by experiment, not by re-reading the diff.

### What the case asserts, and over what input

`case_root_resolves_through_harness_boundary_not_the_retired_variable`
(`test-validate-feature-json.py:331-362`, FEAT-42 T-05) has two halves. The failing half: with
`CLAUDE_PROJECT_DIR` set to an empty tmp fixture and `HARNESS_PROJECT_DIR` unset,
`validate-feature-json.py` (no args) must ignore the retired `CLAUDE_PROJECT_DIR` variable and
fall back to sweeping the **real repo root** — `.harness/*/features/*/feature.{json,yaml,yml}` —
rather than the tmp fixture. The assertion (line 349-351):
```python
check(..., "1 file(s)" not in r.stderr, r.stderr)
```
asserts the stderr's file-count line does **not contain the substring `"1 file(s)"`**. This is a
**substring match, not an equality/threshold check** — it was written when the real sweep found a
two-digit count not ending in `1` (confirmed: was 40 at both parents below). It silently trips
whenever the live sweep count is `1`, `11`, `21`, `31`, `41`, … — i.e. `"41 file(s)"` contains
`"1 file(s)"` as a substring starting at its second character. The input set is **every
`feature.{json,yaml,yml}` under `.harness/*/features/*/` in the checkout the test runs from** —
repository state, not the test's own source.

### Three-point comparison, each run in an isolated `/tmp` clone (worktree HEAD never moved)

```
$ git clone /Users/molchairuangutai/GitHub/harness /tmp/feat43-merge-check   → exit 0
$ cd /tmp/feat43-merge-check
$ git worktree add --detach /tmp/wt-main 6d6d1ce      → exit 0 (HEAD is now at 6d6d1ce)
$ git worktree add --detach /tmp/wt-feature cbdadef   → exit 0 (HEAD is now at cbdadef)
$ git worktree add --detach /tmp/wt-merge 1d292c2     → exit 0 (HEAD is now at 1d292c2)
```

File-count sweep (same glob the CLI uses) at each ref:

| ref | commit | count |
|---|---|---|
| origin/main | `6d6d1ce` | **40** |
| FEAT-43 feature tip | `cbdadef` | **40** |
| merge | `1d292c2` | **41** |

`python3 test-validate-feature-json.py` (full file, run from each worktree's
`.claude/skills/harness/bin`), grepped for the case:

```
=== wt-main (6d6d1ce) ===
PASS case_root_resolves: CLAUDE_PROJECT_DIR alone does not redirect the sweep (...)
PASS case_root_resolves: HARNESS_PROJECT_DIR + team-config.yaml IS honoured

=== wt-feature (cbdadef) ===
PASS case_root_resolves: CLAUDE_PROJECT_DIR alone does not redirect the sweep (...)
PASS case_root_resolves: HARNESS_PROJECT_DIR + team-config.yaml IS honoured

=== wt-merge (1d292c2) ===
FAIL case_root_resolves: CLAUDE_PROJECT_DIR alone does not redirect the sweep (...)
  scanning .../.harness/*/features/*/feature.{json,yaml,yml} — 41 file(s)
PASS case_root_resolves: HARNESS_PROJECT_DIR + team-config.yaml IS honoured
1 FAILURE(S): [...]
```

**Passes cleanly at both parents. Fails only at the merge.** This is not path-dependent or
nondeterministic — reran the merge worktree case twice, same 41/FAIL both times; the count is a
pure function of which feature directories exist in the checkout, not of the absolute tmp path
(the fixture itself lives in a fresh `tempfile.TemporaryDirectory()` each run, untouched by this).

### Attribution: **caused by the merge**, not pre-existing

Diffing the three file lists identifies the exact cause:

```
main (6d6d1ce) has, feature (cbdadef) lacks:  .harness/harness/features/FEAT-44-omp-context-advisory/feature.json
feature (cbdadef) has, main (6d6d1ce) lacks:  .harness/harness/features/FEAT-43-code-risk-grading/feature.json
merge (1d292c2) has BOTH.
```

Neither parent alone has both feature directories — `origin/main` (40 files) carries FEAT-44's
`feature.json` but not FEAT-43's (FEAT-43 wasn't merged yet); the FEAT-43 feature tip (40 files)
carries its own `feature.json` but not FEAT-44's (main's FEAT-44 landed after the feature branch
diverged). The merge is exactly the operation that unions both trees, so the count goes from
40 → 41 **only at the merge** — a textbook combination effect, not a defect either side
introduced alone, and not something `git diff <either-parent> HEAD -- test-validate-feature-json.py`
could ever show, because the test file itself never changed on either side.

**Correction to my prior artifact:** "the file is byte-identical, therefore not a FEAT-43
regression" was the wrong inference. Byte-identical source proves the *test's own code* wasn't
touched; it says nothing about the *tree the test sweeps*, which the merge changed by
construction (that's what a merge of two feature branches does). The right question — "does this
test pass at both parents and fail only at the merge" — is answered above: yes.

**Ruling: caused by the merge, `severity: med`.** It is a genuine gate regression — a merge of
any two branches that each independently add one live feature directory, where the union's count
lands on a multiple-of-ten-plus-one, will trip `run-unit-tests.sh --kind unit` to exit 1 on an
unrelated file. It is not `high`/`critical`: `validate-feature-json.py`'s actual behavior (root
resolution, sweep correctness) is unaffected — only a fragile substring assertion in the *test*
is exposed by the merge's arithmetic. But it is a real, reproducible break in the unit-kind gate
at the merge commit that neither parent has, which is precisely the class of defect this
merge-delta review exists to catch, so it belongs in `must_fix`, not left as a visibility note.

**Recommended fix (not applied — read-only on source per this review's constraints):** replace
the substring check at `test-validate-feature-json.py:349-351` with an exact/regex match on the
leading count (e.g. `re.search(r'^\d+ file\(s\)', ...)` compared against `!= "1 file(s)"`, or
simply assert `count != 1` parsed as an int) so it no longer keys off "does the digit `1` appear
anywhere in the number". This is a dev fix, out of scope for QA to apply.

```yaml
VERDICT: FAIL
DIGEST:
  headline: All five orchestrator measurements (a-e) reproduced exactly; item f confirmed by execution. Send-back correction — test-validate-feature-json.py's case_root_resolves failure under --kind unit is caused by the merge (passes at both parents 6d6d1ce/cbdadef, fails only at merge 1d292c2, confirmed by isolated-worktree experiment), not pre-existing as I originally inferred from byte-identical source diffs alone.
  suite: fail
  failures: 1
  matrix_ok: false
  coverage_gaps: []
  sc_evidence: []
  severity_max: med
  must_fix:
    - "test-validate-feature-json.py case_root_resolves fails at merge 1d292c2 (`run-unit-tests.sh --kind unit` exit 1) but passes cleanly at both parents 6d6d1ce and cbdadef; caused by the merge unioning FEAT-43's and FEAT-44's feature.json (40+40->41 files swept), tripping a substring-match bug (`\"1 file(s)\" in stderr`) in the test's own assertion at test-validate-feature-json.py:349-351. severity: med — a real unit-kind gate regression introduced only by the merge, though validate-feature-json.py's actual behavior is unaffected."
  open_questions: []
  files_touched: []
  expertise_update: []
artifact: .harness/harness/features/FEAT-43-code-risk-grading/notes/qa-mergedelta.md
```
