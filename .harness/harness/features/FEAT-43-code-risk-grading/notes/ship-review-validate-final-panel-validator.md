# FEAT-43 code-risk grading — ship review

**Recommendation: do not ship. The feature is blocked, and the decision it needs is yours.**

The tool works. It grades Python functions, it is deterministic, it is well tested, and every gate
this cycle asked it to pass, it passed. It fails on one thing, and the thing it fails on is itself:
**run the grading tool over this feature's own code and the tool rejects it.** Six production
functions the feature ships are graded 3 against a bar of 4, and two of those six live inside
`code_grade.py`, the grading engine itself.

That is not a technicality. Task T-01 says, without qualification, "Keep every function you write in
`code_grade.py` at grade 4 or better… The tool must pass its own bar." The reviewer went looking for
an exemption — the BRIEF's out-of-scope section, all twelve decisions D-01 to D-12, the plan's
constraints — and found none.

I verified this myself rather than take it on report. Running the tool over the pinned range exits 1,
with **21 of 119 graded functions below their bar**.

The cycle budget is exhausted at 13 of 13, and no source fix is authorized after this panel. So the
work stops here until you decide.

## How this briefing was assembled

**No report round was spawned.** I read the run digests from disk, as the playbook requires. The
paths I assembled from:

- `runs/plan-product/digest.md`, `runs/t01-t07-eng/digest.md`, `runs/t02-eng/digest.md`,
  `runs/t03-eng/digest.md`, `runs/t06-eng/digest.md`, `runs/t10-product/digest.md`
- `runs/build-qa-validator/digest.md`, `runs/build-qa-validator-rerun/digest.md`,
  `runs/build-simplify-eng/digest.md`
- `runs/validate-review-validator/digest.md`, `runs/validate-fix-eng/digest.md`,
  `runs/validate-fix-qa-validator/digest.md`, `runs/validate-fix-simplify-eng/digest.md`,
  `runs/validate-review-final-validator/digest.md`, `runs/validate-fix-c11-eng/digest.md`,
  `runs/validate-fix-c13-qa-validator/digest.md`, `runs/validate-fix-c13-simplify-eng/digest.md`,
  `runs/validate-fix-c13-r01-eng/digest.md`, `runs/validate-regate-c13-r01-validator/digest.md`,
  `runs/validate-final-simplify-eng/digest.md`
- The three panel reviewer notes: `notes/review-harness-code-reviewer-validate-final-panel.md`,
  `notes/review-harness-security-reviewer-validate-final-panel.md`,
  `notes/review-harness-ui-reviewer-validate-final-panel.md`

**One gap, disclosed rather than papered over.** The panel's lead agent aborted before writing its
digest, so `runs/validate-final-panel-validator/` holds only `state.yaml`. The three reviewer notes
were written and are complete; I read them directly and independently re-ran the measurement their
central finding rests on. The panel verdict below is therefore grounded in member evidence plus my
own check, not in a lead's summary that does not exist.

## What blocks the ship

Four findings, from three reviewers working independently. Three of them are one root cause.

**1. The feature does not pass the gate it ships (high).** Six grade-3 production functions sit
below the bar of 4: `code_grade.py:232` and `code_grade.py:318` — the engine itself —
`code-grade.py:80`, `check-plan-routes.py:91`, `gate_policy.py:33`, `gate_policy.py:75`. T-01's
acceptance line is unmet and nothing in the signed scope exempts it.

**2. "Gated grade-3, below bar" has no name anywhere (med).** The tool assigns it no severity: the
map is `{1: "high", 2: "med"}`, so a grade-3 record prints no `SEVERITY` line and reports
`"severity": null` in JSON — yet it causes exit 1 exactly as a grade-1 does. The shipped reviewer
guidance names grade 1 and grade 2 and never mentions this case. The digest schema's four values —
`pass`, `fail`, `grade_2`, `n_a` — have no spelling for it. REQ-11 promised one canonical
vocabulary; this diff instantiates the missing case six times.

**3. A reviewer's grade claim is self-attested and can bypass the gate (high).** This one is
independent of the others and, in my read, the most serious. `validate-digest.py` decides whether
Python changed by diffing the range the reviewer *typed into its own digest*. It never checks that
range against `feature.json`'s `review_sha`. A reviewer that names a no-op range gets `code_grade:
n_a` accepted and the feature's own gate is skipped. The security reviewer notes the shared test
fixture defaults to exactly that shape, so the bypass is the suite's passing case, not an edge case.

**4. The report gives an author no way to act on a grade-3 failure (high).** Their build fails with
no severity and no named cause, and the guidance they are told to follow does not describe the
state they are in.

Findings 1, 2 and 4 close together: decide what a gated grade-3 means, then say it in the tool, the
guidance and the schema. Finding 3 is a separate fix.

## What is genuinely done and verified

Worth stating plainly, because the blockers above are about scope and self-consistency, not about a
broken tool.

- **Tests are green and non-vacuously bound.** Unit 29/29, integration 28/28, with named coverage
  across all seven changed files (`runs/validate-regate-c13-r01-validator/digest.md`).
- **The last change was verified by mutation, not by assertion.** R-01 consolidated three separate
  commit resolvers into one (`code_grade.commit_oid`). QA independently re-ran a mutation that
  deleted the option-rejection guard, confirmed a targeted failure, and proved a byte-identical
  restore. Behaviour is unchanged: the `^{commit}` peel, `--end-of-options`, and rejection of
  option-like revisions before Git runs are all preserved.
- **Simplification is closed.** The four-angle pass returned no blocking findings and confirmed R-01
  reduced duplication rather than relocating it (`runs/validate-final-simplify-eng/digest.md`).
- **Every earlier review finding is closed.** The code reviewer independently re-verified all six
  findings from the `45328d7` review as fixed at this pin.
- **State is clean.** `check-state.sh` exits 0. The work is committed at
  `94383e671e51f95d142f3220f97c8e453721d516`, `review_sha` is pinned to it, and GitHub parent #924
  and all ten sub-issues are at Review.

**One repository-wide test failure, and it is not ours.** The canonical suite records 955 passing
suites and exits 1 on `test-hooks-install.py` case `(e-green) SC-14`. It reproduces identically on
the main checkout at `3952814`, which does not contain `code_grade.py` at all. Its cause is test
isolation: the fixture's sweep calls `feature-worktree.py remove --repo harness`, which resolves to
the real harness checkout instead of the temporary fixture clone. Carried as B8.

## Not run

Goal-check, documentation, UAT and the ship decision did not run, because the panel is a gate and it
failed. **SC-11 is the feature's only `verify: uat` criterion** — it asks whether the guidance
actually changes what an engineer writes, and it is the one claim no automated gate can settle. It
remains unproven. Merge and deploy remain prohibited.

## Budget

`cycles_used` is **13 of 13** — exhausted. `runs` is **21 against an informational 20-run budget**.
Cycles count rework only, so the run count is not itself a defect, and my read is that these runs
earned their place: each of the three fix cycles closed real findings that the following review
independently confirmed closed. The feature ran long because the panel kept finding real problems,
which is the gate working.

## Proposed backlog

Unstruck rows become backlog issues on acceptance. **Anything not listed here dies silently.**

| ID | Nature | What |
|---|---|---|
| B1 | chore | `validate-digest.py:543` — `.encode()` preserves a `bytes` return that neither consumer requires. One-line drop, no caller or test change |
| B2 | enhancement | `validate-digest.py:32` — the eager `from code_grade import commit_oid` costs ~8.3ms on every hook invocation for a symbol reachable only under one branch; move it inside `resolve_reviewed_commit` |
| B3 | enhancement | `code_grade.py:281-292` — two `git rev-parse` spawns per validation (~22ms). Collapsing to one changes the seam signature and per-revision error attribution, so it needs a decision, not a tidy-up |
| B4 | chore | `code_grade.py:277-280` and `code-grade.py:115-118` — three blank lines where both files use PEP8's two everywhere else |
| B5 | chore | Four spellings of "init a scratch git repo" across `test-code-grade.py` and `test-code-grade-cli.py`; a future fixture change must land in four places. Needs a shared test-support module, which does not exist yet |
| B6 | chore | `code-grade.py:29-33` and `code_grade.py:295-302` — two near-identical git wrappers with different error contracts. Merge only if a third caller appears |
| B7 | bug | The digest schema gives a read-only engineering assessment no legal way to report its suite: `dev` + `suite: n/a` + PASS is rejected while `dev-ops` is allowed. This deadlocked a SIMPLIFY run for a full cycle |
| B8 | bug | `test-hooks-install.py` case `(e-green) SC-14` fails on any developer machine: its fixture's sweep resolves `--repo harness` to the real checkout rather than the temp clone. Pre-existing; makes the canonical suite red on main |

## The decision

One of three, and only you can make it:

1. **Authorize a remediation cycle beyond the exhausted 13.** Findings 1 and 4 are mechanical —
   split six functions and add a severity for grade 3. Finding 3 needs a real design call: bind the
   reviewed range to `review_sha`. Finding 2 needs you to name the grade-3 case.
2. **Record a decision accepting the six grade-3 functions**, which amends T-01's acceptance line.
   This is the cheapest path, and its cost is that the feature ships a bar it does not itself meet —
   the first exception to a rule the feature exists to enforce. Finding 3 would still need fixing.
3. **Stop and re-scope.** The branch, the commit, the pin and every artifact are preserved.

I do not recommend option 2 on finding 3 under any circumstance: a gate that any reviewer can skip
by naming a convenient range is worse than no gate, because it reports success.
