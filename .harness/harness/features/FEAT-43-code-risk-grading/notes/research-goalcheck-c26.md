# FEAT-43 goal-check — final delta refresh at pin `cd8dae47`

**BLUF: no criterion moved. Nineteen of twenty `met`, zero `not_met`, SC-11 still `unproven` and
still the operator's to decide. SC-15 is now stronger than at c25 — it rests on a fresh answer set at
a directly-carried-forward pin, not on superset reasoning. B21's ruling is discharged: I confirmed
BOTH mutations the ruling names now fail a named test, including the `_qualname` half nobody had
re-run.**

## 0. Delta bound — confirmed, and tighter than "one file"

`git diff --numstat e12d53b1..cd8dae47 -- .claude .omp` → **one row: `68 0
.claude/skills/harness/bin/test-code-grade.py`**. `git diff --name-only e12d53b1..cd8dae47 | grep -v
'^\.harness/'` → that same single path. **68 insertions, zero deletions**, so no pre-existing line of
any existing case was touched — the change is additive by construction, not by claim. Everything else
in the diff is `.harness/` bookkeeping and notes. `code_grade.py` is not in the delta (`git diff
--stat … -- code_grade.py` → empty).

The two new cases, named from the diff: **`check_docstring_only_rename_not_gated`** (`:480`) and
**`check_method_qualname_collision_pre_images`** (`:511`), plus their two registrations in `main()`'s
runner tuple. Both grade **4** in the gated report (bar 3), which is why the demand count did not move.

## 1. Criteria whose evidence lives in the changed file — all re-run by me

`python3 .claude/skills/harness/bin/test-code-grade.py` → **`PASS test-code-grade`, exit 0.** I then
invoked each carrying case individually via a module load, each returning **0 failures**:

| SC | carrying case (run by me, 0 failures) | verdict |
|---|---|---|
| SC-01 | `check_fixtures` | met |
| SC-03 | `check_direction_pairs` | met |
| SC-07 | `check_changed_function_resolution` | met |
| SC-08 | `check_changed_function_resolution` (absence assertions) | met |
| SC-09 | `check_worked_examples` | met |
| SC-10 | `check_delivery` | met |
| — | `check_self_grading` (T-01's no-exemption guard) | 0 failures |

**SC-02** (inspection) — met, and I proved the fixture tables did not move rather than assuming it:
AST-dumped `FIXTURES` + `DIRECTION_PAIRS` out of `git show <sha>:…/test-code-grade.py` at all three
pins gives the **same md5 `df9f4fd0…`, 2 blocks, at `17106762`, `e12d53b1` and `cd8dae47`**. So the
c21 hand re-derivations still describe these bytes. `git show cd8dae47:…/test-code-grade.py | grep -c
'produced by the tool'` → **0**.

**Additive-only, on evidence:** 0 deleted lines in the diff, the full file exits 0, and every
pre-existing carrying case above returns 0 failures individually. No existing case's behaviour was
altered.

## 2. B21 — the ruling is discharged, both halves

`answers/Q10-b21-hold-and-fix.md:22-24` sets the bar: reducing `_qualname` to `return name` and
`_strip_docstring` to a no-op must **each fail a named test**. I ran both mutations myself in a `/tmp`
sandbox (copies of `code_grade.py`, `code-grade.py`, `test-code-grade.py`; the worktree was never
edited). Sandbox baseline: both cases 0 failures.

- `_strip_docstring` → `return body`: **`check_docstring_only_rename_not_gated` FAILS** —
  `expected set(), got {'renamed'}` plus the informational-set counterpart. *Confirms the
  orchestrator's measurement.*
- `_qualname` → `return name`: **`check_method_qualname_collision_pre_images` FAILS** —
  `qualname collision gated set: expected set(), got {'dispatch'}` plus the informational-set
  counterpart. *This half was not previously re-run by anyone; it holds.*

Each mutation fails **only** its own case, so the two tests bind the two branches independently
rather than one broad assertion covering both. Nothing in scope was refactored and no production code
changed. **The ruling is met, not approximated.**

## 3. SC-15 — **met**, and exactly what it rests on

My run: `code-grade.py --base 7ccfae8d --head cd8dae47` → **exit 0, 198 `FUNCTION` records,
`PASSING: 186`, 12 FAIL, 0 blocking (zero grade-1), 12 `REASON REQUIRED`.** *Confirms every
orchestrator figure.*

I extracted `PATH`+`QUALNAME` from all 12 demand blocks and compared them against
`notes/review-harness-code-reviewer-validate-delta-c25.md:148-188`: **set equality, 12 for 12**, paths
included — `check-plan-routes.py:main`, `code-grade.py:main`, `_case_27_owner_manifest`, `test_paths`,
`test_rejected_revisions`, `test_control_paths`, `test_bars_follow_test_kinds`,
`test_diff_and_determinism`, `check_commit_resolution`, `check_changed_function_resolution`,
`check_policy_loading`, `reviewed_python_change`.

**Basis, stated exactly: a fresh answer set, written at `e12d53b1`, whose demand set I proved
identical — set equality on (path, qualname), not superset containment — to the demand set at
`cd8dae47`.** The c25 caveat is retired: this is no longer superset reasoning off the c21 note. It is
not literally an answer note authored *at* `cd8dae47`, and the reason it does not need to be is
measured: the only delta is two new functions that both grade 4 and therefore emit no demand.
Non-vacuous (12 > 0), so the anti-vacuity clause in SC-15 is satisfied.

Also re-derived: `code-grade.py .claude/skills/harness/bin/code_grade.py` → **exit 0, 53 functions,
grades {4: 11, 5: 42}, `PASSING: 53`, nothing below grade 4.** T-01's self-bar clause is true as
written. *Confirms the orchestrator.*

## 4. Inherited criteria — named, with the reason each lies outside the delta

**SC-04, SC-05, SC-06, SC-14, SC-17** — evidence in `test-code-grade-cli.py`; not in the delta, and
its dependency `code_grade.py` is byte-unchanged since `e12d53b1`, where I ran that file to exit 0.
SC-14's live positive direction is additionally the 12 demands from my own run above.
**SC-12, SC-13** — `test-gate-policy.py`, not in the delta (`check_policy_loading` appears only as a
graded record, not a changed file).
**SC-16** — `test-check-plan-routes.py`, not in the delta.
**SC-18** — `harness-code-risk-grading/SKILL.md`, not in the delta.
**SC-19, SC-20** — `test-validate-digest.py`, not in the delta.
**SC-11** — inherited `unproven` by the operator's ruling, not by my choice.

## 5. Overall

**19 `met`, 0 `not_met`, 1 open — SC-11 only.** No verdict moved down; no new residual.

## 6. SC-11 UAT script — ready, unexecuted, correct arithmetic, current pin

`notes/uat-sc11-c21.md`, all three checks pass:
- `status: ready` (`:2`); results block (`:142-145`) still blank `____` on all nine fields with an
  empty `result:`. **Unexecuted.** I did not run it and did not edit it.
- Arithmetic compared clause by clause against `answers/Q9-sc11-maxima-and-t01-no-exemption.md:17-22`:
  `worst_A = max(a1,a2)`, `worst_B = max(b1,b2)`, `spread_A = |a1-a2|`, `spread_B = |b1-b2|`,
  `gap = worst_B - worst_A`, met iff `worst_A < worst_B` **AND** `gap > max(spread_A, spread_B)` —
  **identical**, and the null/reversed consequence table matches Q9's rulings too.
- `review_sha: cd8dae476607704fd3d2b874150aae9f814292d2` (`:3`). Correct.

**One precision, not a defect:** that header line is updated in the **working tree only** — the bytes
committed at `cd8dae47` still read `17106762…` (`git diff cd8dae47 -- <file>` shows exactly that one
line). Q10's own sequence puts the re-pin after the commit, so this is expected; the operator reads
the working-tree file and it carries the current pin. Worth naming so nobody later reads the
committed copy and thinks the pin is stale.

## 7. Working tree

```
$ git -C <worktree> status --porcelain
 M .harness/harness/features/FEAT-43-code-risk-grading/feature.json
 M .harness/harness/features/FEAT-43-code-risk-grading/notes/uat-sc11-c21.md
 M .harness/harness/features/FEAT-43-code-risk-grading/observations/harness-pm.md            # mine (one appended bullet, via observations-merge.py)
?? .harness/harness/features/FEAT-43-code-risk-grading/answers/Q10-b21-hold-and-fix.md
?? .harness/harness/features/FEAT-43-code-risk-grading/notes/receipt-harness-backend-dev-2026-08-29-validate-b21-c26-eng.md
?? .harness/harness/features/FEAT-43-code-risk-grading/notes/research-goalcheck-c26.md       # mine
```
One transient observation, recorded because I saw it: an intermediate `status` call showed
` M .claude/skills/harness/bin/code_grade.py`. `git diff` on it was **empty** and
`md5sum` against `git show cd8dae47:<path>` matched (`c5db829f…`), and the entry cleared on the next
`status` — a stat/mtime-only index entry, not a content change. The file is byte-identical to the pin.

`feature.json` and `uat-sc11-c21.md` were already ` M` and the Q10/receipt entries already untracked
when I arrived — the pin re-roll and the operator's ruling, not my hand. **Every tracked source and
test file is unmodified.** HEAD is `cd8dae47` and was never moved; all mutation probes ran on copies
in `/tmp`. I wrote my artifact and appended one observations bullet — nothing else.

```
$ git -C /Users/molchairuangutai/GitHub/harness status --porcelain   # main checkout
```
**No tracked modification** — output is untracked `??` entries only, including the stray
`.harness/harness/features/FEAT-43-code-risk-grading/` directory I flagged at c25.

## Open questions

- **Q1 (non-blocking):** the stray untracked `FEAT-43-code-risk-grading/` directory in the MAIN
  checkout persists (an earlier agent's relative-path leak). Still not mine to delete; still worth
  cleaning before the next feature.
