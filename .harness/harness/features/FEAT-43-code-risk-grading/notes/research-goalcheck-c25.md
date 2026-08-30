# FEAT-43 goal-check — delta refresh at the final pin `e12d53b1`

**BLUF: the T-01 residual I escalated at c21 is DISCHARGED, SC-15 stays `met` at the new pin, and no
other verdict moved. Nineteen of twenty criteria `met`, zero `not_met`, SC-11 still `unproven` and
still the operator's UAT to decide.** Baseline: `notes/research-goalcheck-c21.md` at pin
`d2e3b5eb`. Delta scope: `git diff --stat d2e3b5eb..e12d53b1` touches exactly two source files —
`code_grade.py` (+80/-…) and `test-code-grade.py` — everything else in the diff is `.harness/`
bookkeeping and notes. That bound is what makes this a delta rather than a re-derivation.

## 1. The T-01 residual — **discharged**

My own run, at the pin, from the worktree:
`python3 .claude/skills/harness/bin/code-grade.py .claude/skills/harness/bin/code_grade.py`
→ **exit 0, `PASSING: 53`, 53 of 53 functions graded, 0 records at grade 1/2/3** (grade histogram is
`{4, 5}` only; worst grade present is **4**, which is the bar).

The two named offenders, re-measured by me:

| qualname | at c21 (`d2e3b5eb`) | at `e12d53b1` | grade |
|---|---|---|---|
| `_body_hashes.collect` | cyc 9 / cog 18 / abc 17.3 → grade 2 | `:362` cyc **4** / cog **5** / abc **8.8** | **4** (driver cognitive+abc) |
| `gated_set` | cyc 8 / cog 25 / abc 24.9 → grade 2 | `:415` cyc **2** / cog **1** / abc **10.0** | **4** (driver abc) |

Fixed at the root, not exempted. The refactor extracted six named helpers — `_qualname`,
`_strip_docstring`, `_hash_body`, `_resolve_base_source`, `_resolve_pre_image`, `_gate_file_records`
— each of which grades 4 or 5 in the run above, so complexity was removed rather than relocated into
an ungraded corner. Two new characterization checks (`check_pre_image_resolution_priority`,
`check_base_source_rename_fallback`) pin the extracted priority order and the rename fallback.

**No allowlist carve-out survives.** `SELF_GRADING_ALLOWLIST` (`test-code-grade.py:207-253`) has 35
entries and **zero keyed on `code_grade.py`** — I loaded the module and enumerated the keys, and the
diff shows both entries (`SC-15 item 3`, `item 4`) deleted. `SELF_GRADED_FILES` still lists
`code_grade.py` (`:191`), so the file stays under self-grading coverage instead of dropping out of
it, and `check_self_grading()` returns 0 failures on my run. The allowlist's own staleness assertion
(`:298`) means a re-added exemption could not pass silently.

**One sentence, as asked: the residual I escalated at c21 — T-01's unconditional "grade 4 or better…
the tool must pass its own bar" clause (`plan.yaml:186-187`) being true-except-twice — is
discharged; the clause is now true as written, on my measurement, with no exemption carrying it.**

## 2. SC-15 at the new pin — **met**, and here is exactly what it rests on

My run: `code-grade.py --base 7ccfae8d --head e12d53b1` → **exit 0**, 195 `FUNCTION` records,
183 PASS / 12 FAIL, **0 at grade 1 (nothing blocking)**, **12 `REASON REQUIRED`** demands.

I established the superset relation myself rather than assuming it: same command at `--head
d2e3b5eb` gives **14** demands, and `comm` over the two sorted demand sets returns
`only-in-old = {_body_hashes.collect, gated_set}`, `only-in-new = {}`. The 12 are therefore a strict
subset of the 14, and the two that vanished are exactly the two functions just fixed.

Each of the 12 qualnames (`main` ×2, `_case_27_owner_manifest`, `test_paths`,
`test_rejected_revisions`, `test_control_paths`, `test_bars_follow_test_kinds`,
`test_diff_and_determinism`, `check_commit_resolution`, `check_changed_function_resolution`,
`check_policy_loading`, `reviewed_python_change`) is answered by qualname with cyc/cog/abc and a
written reason in `notes/review-harness-code-reviewer-validate-final-panel-c21.md:158-217`; I
grepped all eleven distinct names and each is present.

**What the verdict rests on: superset reasoning off the c21 reviewer note, with the subset relation
re-derived by me at the new pin — NOT on a fresh answer file.** No answer artifact at `e12d53b1`
existed under `notes/` when I looked (the only c25 file present is
`receipt-harness-backend-dev-validate-t01-c25-eng.md`); the concurrent validator run may add one and
would strengthen this, but the verdict does not depend on it. The ship briefing should state the
provenance this way and not claim a fresh answer set.

## 3. Criteria whose evidence lives in the two changed files — all re-run by me

`test-code-grade.py` → `PASS test-code-grade`, exit 0. I also invoked the carrying cases
individually, each returning 0 failures: `check_fixtures` (**SC-01**), `check_direction_pairs`
(**SC-03**), `check_changed_function_resolution` (**SC-07** and **SC-08**), plus
`check_worked_examples` (**SC-09**) and `check_delivery` (**SC-10**), which also live in this file.
**SC-02** (inspection): the diff touches neither `FIXTURES` nor `DIRECTION_PAIRS`, and
`git show e12d53b1:…/test-code-grade.py | grep -c 'produced by the tool'` → **0**, so the
hand-derivation property the c21 note verified is intact at the new pin.

`test-code-grade-cli.py` is unchanged by the diff but imports the refactored module, so it was the
real collateral risk: I ran it → `PASS test-code-grade-cli`, exit 0. That carries **SC-04, SC-05,
SC-06, SC-14, SC-17** forward on a live run. SC-14's live positive direction is additionally the 12
demands from my own gated run.

## 4. Overall

**19 `met`, 0 `not_met`, 1 open — SC-11 only.** No verdict moved down; the T-01 residual that the
c21 briefing carried is closed.

## 5. SC-11 — untouched, and correctly so

`notes/uat-sc11-c21.md`: `status: ready` (`:2`) — **unexecuted**, and the results block at `:143`
still holds blank `____` fields. Its pinned arithmetic (`:121-126`) is
`worst_A = max(a1,a2)`, `worst_B = max(b1,b2)`, `spread = |a1-a2|`, `gap = worst_B - worst_A`, met
when `worst_A < worst_B` **AND** `gap > max(spread_A, spread_B)` — **byte-for-byte the operator's
MAXIMA ruling** in `answers/Q9-sc11-maxima-and-t01-no-exemption.md` §1. The only working-tree change
to that file since the pin is the `## Open question — SETTLED before the run` annotation citing Q9;
the arithmetic and `status:` are untouched. I did not execute it and did not rewrite it.

## 6. What I did NOT re-derive — named, so the briefing cannot overclaim

**SC-12, SC-13, SC-16, SC-18, SC-19, SC-20 carry their c21 verdicts as inherited.** Safe because
their evidence lives entirely outside the delta: SC-12/SC-13 in `test-gate-policy.py`, SC-16 in
`test-check-plan-routes.py`, SC-19/SC-20 in `test-validate-digest.py`, SC-18 in
`harness-code-risk-grading/SKILL.md` — and `git diff --stat d2e3b5eb..e12d53b1` shows **not one of
those five files is in the diff**, nor is any file they read. The two changed files are
`code_grade.py` and `test-code-grade.py`; none of these six criteria cites either. SC-11 is
inherited as `unproven` by the operator's ruling, not by my choice.

## 7. Working tree

```
$ git -C <worktree> status --porcelain
 M .harness/harness/features/FEAT-43-code-risk-grading/feature.json
 M .harness/harness/features/FEAT-43-code-risk-grading/notes/uat-sc11-c21.md
 M .harness/harness/features/FEAT-43-code-risk-grading/observations/harness-backend-dev.md
?? .harness/harness/features/FEAT-43-code-risk-grading/answers/Q9-sc11-maxima-and-t01-no-exemption.md
?? .harness/harness/features/FEAT-43-code-risk-grading/notes/receipt-harness-backend-dev-validate-t01-c25-eng.md
?? .harness/harness/features/FEAT-43-code-risk-grading/notes/research-goalcheck-c25.md   # mine
```
**Not byte-identical to the pin, and not by my hand:** three `.harness/` bookkeeping files were
already modified and two already untracked when I arrived — the Q9 answer file, the SETTLED
annotation on the UAT script, a backend-dev observations append, and `feature.json`'s
`review_sha`/`cycles_used` roll. **Every tracked source and test file is unmodified**, which is what
my measurements needed; I verified the pin's own bytes via `git show` where content mattered. HEAD
was never moved and I wrote exactly one file.

```
$ git -C /Users/molchairuangutai/GitHub/harness status --porcelain   # main checkout
```
**No tracked modification.** Output is untracked entries only (`??`) — including a stray
`.harness/harness/features/FEAT-43-code-risk-grading/` directory in the main checkout, an earlier
agent's relative-path leak, untracked and therefore harmless to the pin. Nothing of mine landed
there.

## Open questions

- **Q1 (non-blocking):** the stray untracked `FEAT-43-code-risk-grading/` directory in the MAIN
  checkout is a leak from an earlier agent's relative write. Not mine to delete; worth cleaning
  before the next feature so it is not mistaken for the live folder.
