# Code Review — FEAT-52-factory-control-plane — remediation re-review (post impl-c9)

`review_sha: ff4ca877587dba6aa348577ba580dbd4fd2020aa`, diffed against
`merge-base(origin/main, ff4ca877) = 06bd60c8e3185a166723dfc7bfec860e2bdc88f7`. The later commit
`9fe48588` only repins `review_sha` in `feature.json`; not treated as implementation. Every code
claim below is grounded via `git show <review_sha>:<path>` reads, a `git diff <base>..<review_sha>`
for each cited file, live execution of the four affected unit/integration suites at the checked-out
tree (byte-identical to the pin for every file cited), and one live Python repro of the F2 defect
using the actual `harness_boundary`/`inflight_registry` modules from the pin.

## BLUF

**FAIL, unchanged from impl-c9.** Four of impl-c9's five findings are now closed by genuine test
and code work (F1, F3, F4, and SC-01/02/03/12's headline gaps from F5). **F2 is not fixed** —
`inflight_registry.feature_root()` still swallows `AmbiguousWorktree` behind a blanket
`except Exception: return owner_root`, exactly as before, and I reproduced the silent collapse live
against the pinned code. This directly contradicts the plan's own stated design for this exact
exception (`plan.yaml:756-758`, T-09: "AmbiguousWorktree is a refusal the resolver owns, not one
this block should convert") and REQ-06's guarantee that "a persona left unable to resolve it is
refused loudly rather than left to guess a root." Additionally, `code_grade` mechanically comes back
`fail`: two brand-new production functions and one brand-new test-file `main()` ship at grade 1
(cognitive 31/52 and ABC 73.1), and a fourth (`inflight_registry.py:635 main`) is a worsened
regression from this feature's own `feature-root` verb addition — none of this was touched between
impl-c9 and this pin. One new, narrower gap: SC-12's RED case checks the drift *count* line but
never the `<file>:<line>` detail line the criterion also names.

## Remediation disposition (the five areas this dispatch asked about)

| Area | Disposition |
|---|---|
| Shell-less dispatch fixtures (SC-13, F3) | **Closed.** `test-dispatch-guard.py:461 case_17_shell_less_persona_requires_matching_feature_root` — live-run, 6/6 sub-assertions pass — covers REFUSED (missing root), ALLOWED (matching root), the bash-holding-persona discrimination, and MISMATCH-REFUSED, matching SC-13's four named cases. |
| Injected root/unresolved/drift branches (SC-01/02/12, F5) | **Mostly closed.** `case4b` (root ≠ product cwd), `case4c` (UNRESOLVED + `VERDICT: BLOCKED`), `case14` (exit-code grep + positive control) all pass live and match their SC text exactly. `case4d` covers the drift branches' `none`/count-line pair but **not** the file:line detail SC-12 also names — see Finding 2. |
| Product-clone debug read (SC-06, F4) | **Closed.** `test-check-instruction-paths.py`'s `"product clone can read anchored systematic-debugging skill"` check is a legitimate pair: `os.path.isfile` on the anchored absolute path (works regardless of cwd, as anchoring intends) plus `not os.path.exists(os.path.join(product_cwd, ".agents/skills/harness-systematic-debugging/SKILL.md"))`, which is exactly the pre-change bare-relative spelling resolved against a product-shaped cwd (`harness-backend-dev.md:59` confirms the live spelling matches). Live-run, passes. |
| Five canonical carriers (SC-03) | **Closed.** `--list-scope` is asserted to contain all five S1-S5 sites by name (qa-gate, expertise, handoff, `harness-backend-dev.md`, `harness/templates/PLAN.md`) — five separate assertions, matching SC-03's "the Nth file is named individually" requirement. |
| Workflow gate mutants (SC-08) | **Closed.** `workflow_gate_is_enforced()` plus two mutants (step renamed away, `exit "$rc"` replaced with `exit 0`) both flip the assertion to False, live-run pass. Matches SC-08's literal design (text-pattern check against the real `tests.yml`, shown able to go RED on two mutants) even though the precise precedent citation in the BRIEF ("test-check-plan-routes.py case 25") does not itself concern workflow files — a BRIEF citation slip, not an implementation gap. |

## Findings, ranked

### F1 (carried, HIGH, BLOCKING) — `inflight_registry.py:265-271` `feature_root()` still swallows
`AmbiguousWorktree`, unchanged since impl-c9, contradicting the plan's own stated design.

```python
def feature_root(owner_root, feature):
    try:
        resolved = harness_boundary.worktree_for_feature(owner_root, feature)
    except Exception:
        return owner_root
    return resolved if resolved is not None else owner_root
```

`git diff <base>..<review_sha> -- inflight_registry.py` touches only `main()`'s new `feature-root`
CLI verb; this function is byte-identical to before impl-c9's review. `plan.yaml:756-758` (T-09's
own intent for `dispatch-guard.sh`'s comparison step) says: *"Call reg.feature_root(owner_root,
declared) inside try/except; on ANY exception print one stderr line and pass through —
AmbiguousWorktree is a refusal the resolver owns, not one this block should convert."* That sentence
only makes sense if `feature_root()` lets `AmbiguousWorktree` propagate to its caller — which it
does not. I reproduced this live at the pin (two linked worktrees named `FEAT-90` and
`FEAT-90-alpha`, querying `FEAT-90-alpha-redo`):

```
worktree_for_feature raised AmbiguousWorktree: feature 'FEAT-90-alpha-redo' matches 2 linked worktrees: FEAT-90, FEAT-90-alpha
feature_root() result: <owner_root>
SILENTLY COLLAPSED TO OWNER ROOT: True
```

**Failure scenario, end to end:** a feature with two linked worktrees whose basenames both
prefix-match the feature id in play. The orchestrator resolves
`inflight_registry.py feature-root --feature <FEAT>` to populate `HARNESS-FEATURE-TREE-ROOT:` for a
shell-less lead's dispatch — it silently gets the control-plane root, no error. `dispatch-guard.sh`'s
own comparison (`reg.feature_root(owner_root, declared)`, line ~172) computes the identical
silently-wrong value, so the two sides agree and the guard **allows** the dispatch. The lead's
receipt and observations land in the control plane instead of the ambiguous feature's actual
worktree — invisible at that worktree's `review_sha`, precisely the failure class D-06/REQ-06 exist
to end, and with no stderr breadcrumb anywhere. `test-inflight-registry.py`'s `case_35_feature_root_cli`
still covers only single-match, short-form, and no-match; no ambiguous-worktree case exists.

### F2 (NEW, HIGH, BLOCKING) — `code_grade: fail`, both new debt from this feature and an untouched
worsened regression already flagged at impl-c9.

Ran `code-grade.py --base 06bd60c8e3185a166723dfc7bfec860e2bdc88f7 --head ff4ca877` (the canonical
range). Blocking (grade 1, not grade 2) records:

- `check-instruction-paths.py:26 scope` — **NEW file**, cyclomatic 12 / cognitive 31 / ABC 23.9,
  grade 1, bar 4, driver cognitive.
- `check-instruction-paths.py:62 violations` — **NEW file**, cyclomatic 15 / cognitive 52 / ABC 34.4,
  grade 1, bar 4, driver cognitive.
- `inflight_registry.py:635 main` — **worsened** by this feature's own `feature-root` verb addition,
  cyclomatic 14 / cognitive 24 / ABC 45.4, grade 1, bar 4, driver abc. Already named in impl-c9's F6;
  untouched since.
- `test-check-instruction-paths.py:34 main` — **NEW file**, cyclomatic 16 / cognitive 8 / ABC 73.1,
  grade 1, bar 3, driver abc. This one is new *since* impl-c9 (the whole file landed in the
  remediation commits) and was never reviewed for shape.
- `test-anchor-directions.py:41 main` — **NEW file**, cyclomatic 12 / cognitive 22 / ABC 45.9, grade
  1, bar 3, driver abc. Already named in impl-c9 (as informational); still unaddressed.
- `test-inflight-registry.py:1081 main` — worsened (added one more case call), cyclomatic 4 /
  cognitive 1 / ABC 45.1, grade 1, bar 3, driver abc. Already named in impl-c9; still unaddressed.

Per `harness-code-risk-grading`/`harness-code-review`: "a grade-1 gated function... is a high finding
and fails review," with no carve-out for test-runner `main()` shape. `check-instruction-paths.py:90
main` and `test-inflight-registry.py:1016 case_35_feature_root_cli` are grade 2 (non-blocking with
reason; impl-c9 already gave `main`'s reason, and `case_35`'s shape — five sequential CLI-subprocess
assertions — matches this suite's established one-function-per-case convention).

impl-c9 reported these same production-code grade-1 records but ranked its consolidated finding
"LOW, non-blocking" while separately writing `code_grade: fail` in its own digest line — an internal
inconsistency in that review. Per the current protocol, `validate-digest.py` independently
recomputes `code_grade` over this exact range and refuses a digest that disagrees with it, so this
review reports it as what the tool says: `fail`, `severity: high`.

### F3 (MED, non-blocking on its own, contributes to the SC-unmet acceptance rule) — SC-12's RED
case never asserts the file:line detail the criterion names.

`test-inject-expertise.py:218 case4d` asserts `"HARNESS_PATH_DRIFT: none"` in the clean run and
`"HARNESS_PATH_DRIFT: 1 unanchored path(s)"` in the drifted run, but never asserts the
`  <file>:<line>` line that `inject-expertise.sh`'s `control_plane_block()` derives via
`sed -n 's/^VIOLATION \([^:]*:[0-9]*\):.*/  \1/p'` (lines ~81-83). SC-12's text: *"the SAME file with
one relative `.harness/` span yields the count line naming that file AND that line number."* I
traced the sed regex by hand against the fixture's `VIOLATION .omp/agents/harness-qa.md:1: ...` line
and it does extract `.omp/agents/harness-qa.md:1` correctly today — this is not a live defect — but
nothing red catches a regression to that extraction (wrong capture group, dropped `sed -n '1,5p'`
window, etc.) because the test only checks the count line, not the lines that follow it.

## Not re-raised (already covered above or out of scope per dispatch)

`check-state.sh` VIOLATION lines, `team-config.yaml` DEVIATION sub-cases, `STATE.md`'s stale status,
the untracked feature directory — impl-c9's own ruled-out list, unaffected by these commits. SC-04,
SC-05, SC-07, SC-09, SC-10 (literal text), SC-11, SC-14, SC-15 were MET at impl-c9 and nothing in the
remediation diff touches their mechanisms; re-verified unchanged by `git diff` scope on each cited
file.

## Verdict

**FAIL.** `must_fix` = {F1, F2}; F1 is a live-reproduced fail-open defect the plan's own text
requires to surface as a refusal and does not; F2 is a mechanically recomputed `code_grade: fail`
with four high-severity records, two of them introduced by this feature and never addressed since
impl-c9 flagged three of them. F3 is real but would not block alone. Recommend routing back to the
implementer: F1 needs `feature_root()` to let `AmbiguousWorktree` propagate (its caller,
`dispatch-guard.sh`, already fails open with a stderr line the moment it does) or to print its own
diagnostic before falling back — not silently; F2's four blocking records need either a shape
change or, where the CLI-dispatch/test-runner shape is deliberate, a written REASON at grade 2 (not
grade 1, which does not accept one).
