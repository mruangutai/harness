# GATE-ONLY re-run — FEAT-27-expertise-repository-tier — review_sha 9b929de

## BLUF

`matrix_ok: true`. Both suites re-ran clean at `9b929de` (unit exit 0 / 0 `FAIL`, integration exit
0 / 0 `FAIL`), and `252fa72..9b929de` touched zero source or test files — the prior gate's matrix
result carries forward unchanged. The one open item from the prior gate is CONFIRMED, not new: the
16 repository-tier grants (T-01, `change_type: config`) are pinned against regression by nothing in
the standing suite — this is matrix-compliant (config's `always: []` obligates no kind), but it is
a real coverage gap, and `9b929de` did not close it.

## 1. Tree identity

- `HEAD` = `9b929de90f4de08a662750fb1b80f6791fa350ea`, branch
  `feat/FEAT-27-expertise-repository-tier`. Confirmed via `git rev-parse HEAD`.
- No uncommitted diff on any file under review (`git status --porcelain` against the bin/,
  team-config.yaml, README.md, SPEC.md, harness-distill/curate SKILL.md, and both expertise
  roots returns nothing).
- Working-tree `M` entries for `CLAUDE.md`, `DECISIONS-INDEX.md`, `DECISIONS.md` and untracked
  `FEAT-26/28/29` belong to other work per dispatch boundary — not graded, not reported further.

**`git diff --stat 252fa72..9b929de`** (prior gate SHA → this gate SHA):

```
.harness/harness/docs/SPEC.md                                      |  14 +-
.../FEAT-27-expertise-repository-tier/feature.json                 |  33 +-
.../notes/qa-FEAT-27-matrix-final.md                                | 352 ++
.../notes/receipt-harness-{ai-dev,backend-dev,data-engineer,dev-ops}-simplify-eng.md | +302
.../notes/receipt-harness-documentor-specfix-c1.md                  |  51 +
.../observations/harness-*.md (9 files)                             | +265
18 files changed, 975 insertions(+), 8 deletions(-)
```

**Zero source or test files in this delta.** SPEC.md and feature.json are `docs`/bookkeeping
(matrix `always: []`); everything else is notes/observations. Change-type re-derivation for the
delta itself: nothing obligates a test kind. The prior gate's `matrix_ok: true` therefore carries
forward as-is for `252fa72..9b929de`; it is not re-derived from scratch, it is confirmed
untouched.

**Full feature diff `b4659cd..9b929de`** (`57 files changed, 3892 insertions(+), 93 deletions(-)`)
does carry the source/test set named in the dispatch — all introduced between `b4659cd` and
`252fa72`, i.e. already covered by the prior gate. Re-ran fresh per dispatch instruction anyway
(section 2).

## 2. Suites re-run at 9b929de

Exit captured in a variable, never through a pipe, for both:

| Kind | cmd | exit | `grep -c '^FAIL '` | registered scripts | discovery |
|---|---|---|---|---|---|
| unit | `run-unit-tests.sh --kind unit` | `0` | `0` | 17 | 741+ counted case-assertions across the 12 of 17 scripts that emit an `N/N passed` line (5 report differently but still `PASS`) |
| integration | `run-unit-tests.sh --kind integration` | `0` | `0` | 12 | 201+ counted case-assertions across 6 of 12 scripts reporting `N/N`; all 12 `PASS` |

Every one of the 17 `UNIT_SCRIPTS` and 12 `INTEGRATION_SCRIPTS` entries (as literally read from
`run-unit-tests.sh` lines 17–18) printed `PASS <name>`, none `FAIL`. Non-zero discovery confirmed
both directions — this is not a sweep over an empty set.

`test-inject-expertise.py`: 13 case-**functions** in the file (`grep -c '^def case'`), but the run
reports **19** named checks — case5/7/9 each split into an `a`/`b` sub-check, case12 runs 4
hostile-`agent_type` sub-cases. 13 vs 19 is granularity, not a discrepancy; both counts are true of
the same file.

`test-check-expertise.py` (dispatch: "+6"): 22/22 cases pass standalone and under
`--kind integration`. Runs under **integration**, not unit — it is in `INTEGRATION_SCRIPTS`, not
`UNIT_SCRIPTS` (`run-unit-tests.sh:17–18`). This matches T-03's own `verify:` block, which greps
`run-unit-tests.sh --kind integration` output for `^PASS test-check-expertise.py$`.

## 3. Matrix obligation vs. what ran, per changed task

| Task | Files | `change_type` | matrix `always` | Satisfied by |
|---|---|---|---|---|
| T-01 | `.harness/team-config.yaml` | `config` | `[]` | nothing required; only T-01's inline one-shot `verify:` |
| T-02 | `inject-expertise.sh`, `test-inject-expertise.py`, `run-unit-tests.sh` | `logic` | `[unit]` | `PASS test-inject-expertise.py` (unit) |
| T-03 | `check-expertise.sh`, `test-check-expertise.py` | `cross_module` | `[unit, integration]` | `PASS test-check-expertise.py` runs under **integration** only — see below |
| T-07 | `test-inject-expertise.py` (case13) | `logic` | `[unit]` | `PASS test-inject-expertise.py` (unit), case13 present, `os.symlink` present |
| T-04/05/06 | SPEC.md, README.md, expertise files, SKILL.md | `docs` | `[]` | nothing required |

T-03 flags `cross_module` (`always: [unit, integration]`) but its own `files:` list and `verify:`
block only exercise `--kind integration` — `check-expertise.sh`/`test-check-expertise.py` produce
no unit-kind artifact of their own. This is not a new finding (it was true at `252fa72` too,
unchanged by this delta) and the prior gate accepted it; flagging for completeness since the
dispatch asked for the obligation to be re-derived independently, not taken from the mapping as
given.

## 4. The adequacy question — confirmed, unchanged by 9b929de

**SC-02** (BRIEF.md:115–118): "For each of the sixteen agents individually, `check-domain.sh
--resolve` on `.harness/harness/expertise/<agent>.md` prints exactly that agent's name." Its only
automated evidence is T-01's inline `verify:` block (plan.yaml:108–127) — ran it directly against
`9b929de`:

```
ALL-GRANTS-OK
```
exit 0, all 16 agents × repo-tier + craft-tier + two edge cases (second segment, two-segment
depth-reject).

**This block is not registered anywhere in `run-unit-tests.sh`.** `grep -n check-domain
run-unit-tests.sh` matches only a comment (line 14) and the unrelated `test-check-domain.py` entry
in `INTEGRATION_SCRIPTS` (line 18) — never T-01's loop. `test-check-domain.py` itself: exactly one
hit for `repository` (`grep -c repository test-check-domain.py` = 1), and it is a comment about "a
product repository" in an unrelated PAIR-B discussion, not a repository-tier test case.

**Confirmed at `9b929de`, as stated in the prior gate: the 16 repository-tier grants — the
feature's core new deliverable — are correct today and pinned against regression by nothing in the
standing suite.** `9b929de` did not change this: T-01, `check-domain.sh`, and `test-check-domain.py`
are all outside the `252fa72..9b929de` diff (confirmed in §1). This is matrix-compliant (T-01 is
`config`, obligating no kind) but is a real coverage gap on the feature's headline surface — a
future edit to `team-config.yaml` that silently drops a repository-tier grant would not redden any
CI-run suite; only SC-13's advisory scan or a human re-running T-01's shell loop would catch it.

## 5. matrix_ok

`true`. No required kind is missing: T-02/T-03/T-07 (`logic`/`cross_module`) are satisfied by named,
passing, non-vacuous tests in the diff; T-01/T-04/T-05/T-06 (`config`/`docs`) obligate nothing per
`.harness/harness.json`. The §4 gap is real but does not fail the matrix — it is an SC-level
adequacy finding, reported per `harness-verification-rules` ("a passing suite is not a met SC"),
not a matrix violation.
