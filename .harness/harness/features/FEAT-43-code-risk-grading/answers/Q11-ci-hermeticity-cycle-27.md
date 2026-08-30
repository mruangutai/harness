# Q11 — Cycle 27, authorized solely for the PR #978 integration blocker

**Authorization issued by the operator on 2026-08-29.** `max_total_cycles` and `cycles_used` both
become **27**. Scope is the CI failure and nothing else. The operator retains PR #978's lifecycle;
no merge, ship or close is authorized here.

## The blocker

CI run `33294260861` on PR #978 failed. `test-validate-digest.py::check_prior_validator` runs
`git show df63193f7ec9798d9660904e0e4e7c78d52358f5:<file>` for two files, and that object does not
exist in GitHub's shallow checkout. The test passes locally and fails in CI — the classic
works-on-my-machine shape, and a real defect in the test rather than in the product.

The operator supplied an uncommitted focused edit deleting `check_prior_validator` and its call,
noting that `check_review_policy` already mutation-binds the current enforcement, and explicitly
invited revision: *"assess the smallest correct hermetic fix (revise mine if needed)."*

## Assessment — the supplied edit is REVISED, not adopted

**Deleting the check would make SC-20 `not_met`.** SC-20 is not a general statement about policy
enforcement; it enumerates four clauses, and the fourth is verbatim (`BRIEF.md:210-218`):

> "The previous revision of the validator is run against the first return and shown to accept it,
> **so the assertion is proven able to fail**."

Coverage of the other three is intact and is not in question — clause 1 at
`check_review_policy:1946`, clauses 2 and 3 at `check_config_errors:2503-2505,2523`.
`check_prior_validator` is the **only** implementation of clause 4, and it is not a duplicate of
`check_review_policy`: the current-contract test proves the rejection happens, while the
prior-revision run proves the rejection is *new* — it is the discriminating control that stops a
hardcoded always-reject from passing as enforcement.

Deleting a test to make CI green, when that test is named in a signed success criterion, is the
exact failure mode this feature exists to prevent. It would also be the second time in this feature
that a green suite concealed a missing control (B21 was the first).

## The ruling — vendor the prior revision as fixture data

Remove the dependency on repository history; keep the discrimination.

The two files `check_prior_validator` fetches — `validate-digest.py` (1048 lines) and
`harness_yaml.py` (621 lines) at `df63193` — are committed as **inert fixture data with a non-`.py`
suffix**, written to a temp directory at test time and executed there exactly as today. No
`git show`, no network, no history requirement.

Why this and not the two alternatives:

- **`fetch-depth: 0` in the CI workflow** preserves the criterion in one line, but it treats the
  environment rather than the test's dependency. The test would still fail for any contributor with
  a shallow or partial clone, and it would break permanently if `df63193` were ever garbage
  collected or the branch rewritten. The operator asked for a hermetic fix; a test that needs
  repository history to discriminate is not hermetic.
- **Deletion** is smallest and is refused, above.

The non-`.py` suffix is load-bearing: `code_grade._changed_python_files` selects on
`path.endswith(".py")`, so a vendored `.py` would enter the gated set and drag a pre-feature file's
old grades into this feature's own gate. Fixture data must not be graded as if this feature wrote it.

A secondary benefit, not the justification: a frozen fixture cannot be silently invalidated by a
history rewrite, and any future change to the control shows up in a diff.

## Sequence

Focused QA and `code-grade.py`, delta review, state gate, commit by explicit pathspec, re-pin
`review_sha`, refresh the goal-check and the briefing, return ship-ready. **No merge, ship, deploy or
close** — the operator owns PR #978's lifecycle after CI.

If any finding survives this cycle, the outcome is terminal `BLOCKED`.
