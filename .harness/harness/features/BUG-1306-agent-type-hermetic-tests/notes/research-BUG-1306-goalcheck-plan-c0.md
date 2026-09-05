# Goal-check — BUG-1306 plan vs. STATED INTENT (c0)

**YES — the plan delivers the operator's stated intent.** Checked against
`.harness/notes/grilling-six-residual-bugs-2026-09-05.md` (the intent), not the BRIEF. One
amendment is required before signature (SC-05, item 6); nothing else blocks. 4 of 5 SC are
deterministic.

## 1 — Intent coverage: YES

The intent's destination for #1306 is row B-13 of
`.harness/harness/features/BUG-1286-test-tree-enforcement/notes/ship-review-2026-09-05-ship-final.md:89`,
whose remedy is "strip it from the default env and opt back in per case." Both halves land:

- **Strip from default env** — `plan.yaml:77` (`os.environ.pop("HARNESS_AGENT_TYPE", None)` at
  module import, before every case body and before the raw `Popen`s at
  `tests/integration/test-plan-merge.py:305,309`).
- **Opt back in per case** — the mechanism survives and is exercised: `test-plan-merge.py:1107`
  builds `dict(os.environ, HARNESS_AGENT_TYPE="harness-pm")` and `:1111` still asserts exit 10;
  `plan.yaml:86-88` requires `run_verb`'s docstring to document the opt-in as the remaining route.
  `plan.yaml:95-98` forbids touching either `case_1103_` case.

**D-05 leaves no part of the intent undelivered.** B-13 asks for a remedy, not a regression case.
D-05's reasoning is sound at the file: the module-import pop runs before any case body, so no
in-process case can reconstruct the ambient-governed precondition. Residual, non-blocking: after
ship, a removal of the pop reddens only under a governed env, and CI carries no
`HARNESS_AGENT_TYPE`, so the standing 13 checks are a regression detector for agents only (Q1).

**15 vs 14 — a counting artifact, not a discrepancy.** `run_pool.py:105` prints its own
`FAIL {name}` line per failing file, on top of the file's own summary at
`test-plan-merge.py:2103`. Suite-wide via the runner: 13 check FAILs + 1 file summary + 1 pool
line = **15** (B-13's number). Direct `python3 tests/integration/test-plan-merge.py`: 13 + 1 =
**14** (the BRIEF/plan number at `c369fb1`). Two invocations, one defect. No action.

## 2 — Criterion strength: 4 deterministic, 1 not

| SC | Verdict |
|---|---|
| SC-01 | deterministic — literal command, exit 0 + zero `^FAIL`, with the pre-fix red pinned at `c369fb1` |
| SC-02 | deterministic — exact strings, confirmed byte-identical (item 3) |
| SC-03 | deterministic — literal command, clean-env control |
| SC-04 | deterministic — `verify: inspection`, but names `git show <review_sha>:tests/integration/test-plan-merge.py`, a single structural fact (one module-level pop preceding case bodies and `:305/:309`). Two reviewers reach the same verdict twice |
| SC-05 | **NOT deterministic** — graded on diff CONTENT with no base ref and no `review_sha` pin. Two reviewers can compute two diffs |

SC-05 is the only criterion grading file/diff content without a pinned ref; SC-04 already pins one.

## 3 — The pair: CONFIRMED, with one named residual

Byte comparison (printer `print(f"PASS  {name}")`, `test-plan-merge.py:2098` — **two** spaces):
check names at `:1111` and `:1136` concatenate to `PASS  a governed agent's sign-approval exits 10`
and `PASS  the signature actually lands`. Both strings appear **byte-identical** in BRIEF SC-02
(`BRIEF.md:69-70`) and in T-01's two `grep -qF` (`plan.yaml:65-66`) — spacing exact, apostrophe
ASCII `'`, no non-ASCII anywhere. SC-02 is satisfiable; the `grep -qF` will match.

Deleting `case_1103_...` removes the PASS lines → SC-02 fails. Neutering the env (dropping the
explicit `HARNESS_AGENT_TYPE`) makes rc 0 → the line prints `FAIL` → both SC-01 and SC-02 fail.
**Residual:** weakening only the predicate while keeping the check NAME (e.g. `r.returncode in (0,
10)`) still prints PASS and evades SC-01/02/04/05. Bounded by `plan.yaml:95-98` and by review, not
by a criterion (Q2, non-blocking).

## 4 — Traceability ruling: NOT a gap; T-01 is format-correct

`harness-spec-driven` defines `traces:` as "the `REQ-NN` this task serves, as a list" and
explicitly excludes other id classes from the field. Task→SC linkage is not part of the plan/1
format under DEC-182. T-01 traces REQ-01..03 = every REQ in the BRIEF. SC reachability holds
independently: SC-01/02/03 are discharged verbatim by T-01's `verify:` (`plan.yaml:59-67`);
SC-04/05 are `verify: inspection`, discharged by the reviewer, which no task carries by design.
Adding SC ids to `traces:` would be a format deviation, not an improvement.

## 5 — Out-of-scope leakage: none, in either direction

D-01/D-04's confinement is compliance with the intent's own ban on "unrelated cleanup, redesigns"
(grilling note line 27) and rests on an Advisor ruling the operator delegated (line 11) —
`runs/2026-09-05-02-validator/digest.md` Q-A. Not a scope reduction. D-05 declines a test that
cannot be written, not a gate: no risk acceptance, no waiver, no failed gate. D-03 (leave
`plan-merge.py`) is the Advisor's Q-C. Nothing added beyond the six-issue requirements; nothing the
operator asked for is quietly dropped.

## 6 — SC-05 amendment (orchestrator's position accepted, and strengthened)

Merge-base is right; add the `review_sha` pin so the criterion cannot drift under later commits.
Replacement wording for SC-05's first sentence:

> The change is confined. `git diff --name-only $(git merge-base main <review_sha>) <review_sha>`
> names `tests/integration/test-plan-merge.py` and Harness lifecycle artifacts under
> `.harness/harness/features/BUG-1306-agent-type-hermetic-tests/` only — …

Literal command string: `git diff --name-only $(git merge-base main <review_sha>) <review_sha>`

(Three-dot `git diff --name-only main...HEAD` computes the same set but leaves the endpoint
unpinned; the form above is preferred for that reason.) Not edited here — the orchestrator
sequences the amendment, and it resets approval.

## Open questions

- Q1 (non-blocking): post-ship, only a governed-env run reddens if the pop is removed; CI never
  sets `HARNESS_AGENT_TYPE`. Accepted consequence of D-05, or a follow-up backlog row?
- Q2 (non-blocking): no criterion catches a `case_1103_` predicate weakened under an unchanged
  check name. Worth one line in the reviewer's dispatch.
