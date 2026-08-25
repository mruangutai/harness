# BRIEF — FEAT-36 merge-gitignore behavioral coverage

Source issue: #814, a sub-issue of #594.

## Problem

`merge-gitignore.sh` is the only shell utility in the canonical `bin/` directory without direct
executable behavioral coverage. Its documented contract protects a project's existing `.gitignore`
and keeps Harness run artifacts from dirtying the project, but regressions in merge, check, rerun, or
path-resolution behavior can currently reach users without a focused test naming the broken outcome.

## Goal

Give `merge-gitignore.sh` executable behavioral coverage for every documented user-visible outcome,
starting with tests and changing the production utility only if a new test first demonstrates that the
current implementation violates that documented contract.

## Requirements

- REQ-01: Merging Harness rules preserves all content already present in the project's `.gitignore`.
- REQ-02: `--check` succeeds when every Harness rule is present, fails when any Harness rule is
  missing, reports the missing rules, and does not modify the project in either case.
- REQ-03: A project with no `.gitignore` and a project whose `.gitignore` contains only some Harness
  rules each receive every missing rule without duplicating a rule already present.
- REQ-04: Re-running the merge after the Harness rules are complete leaves the resulting `.gitignore`
  byte-for-byte unchanged.
- REQ-05: The explicit project root determines which `.gitignore` is read and written even when the
  utility is invoked from an unrelated caller working directory.

## Success Criteria

- SC-01: A behavioral case starts with distinctive existing lines, runs the real utility, and proves
  those lines survive unchanged and in their original order while the Harness rules are added.
  verify: automated      evidence: integration
- SC-02: Separate behavioral cases prove that `--check` exits 0 for a complete target and exits 1 for
  an incomplete target, names each missing rule in the failure output, and leaves both targets
  byte-for-byte unchanged.
  verify: automated      evidence: integration
- SC-03: Separate behavioral cases prove that an absent target receives every Harness rule exactly
  once and a partially populated target retains its existing rule exactly once while receiving each
  missing rule exactly once.
  verify: automated      evidence: integration
- SC-04: A behavioral case runs the merge twice and proves the second run leaves the complete target
  byte-for-byte unchanged.
  verify: automated      evidence: integration
- SC-05: A behavioral case invokes the real utility from a directory outside both the utility and the
  project, passes the project root explicitly, and proves only that project's `.gitignore` changes.
  verify: automated      evidence: integration
- SC-06: At the reviewed commit, the new behavioral test is registered in the repository's integration
  suite and `merge-gitignore.sh` is unchanged unless commit history first shows a new test failing
  against the documented outcome that the production change corrects.
  verify: inspection

## Verification gaps

None. The `integration` test kind is active and runs real utilities as subprocesses. DEC-187 supplies
that classification rule, and DEC-197 requires this new explicit integration filename to take
precedence over the catch-all `test-*.py` unit detector.

## Constraints

- Tests are authored and run against the untouched utility first. Production changes are permitted
  only when a failing behavioral test proves a violation of REQ-01 through REQ-05; a passing first run
  leaves `merge-gitignore.sh` unchanged.
- The resulting tests and any conditional production fix remain provider-neutral. The OpenAI provider
  overlay used by agents in this cycle does not enter repository behavior, remove Anthropic support,
  or alter Claude Code compatibility.
- Coverage for unrelated `bin/` utilities, changes to undocumented behavior, and merging the resulting
  pull request are out of scope.
- DEC-187 supplies the repository's active integration runner and its real-process classification;
  DEC-197 supplies explicit-filename precedence and therefore requires the test filename to be added
  to both integration registries.

## Approval

status: approved
approved-by: operator
date: 2026-08-24
