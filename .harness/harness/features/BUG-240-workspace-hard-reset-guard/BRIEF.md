# BRIEF — BUG-240 workspace hard-reset guard

## Problem

`factory_workspace.py` refreshes an existing checkout by running `git fetch origin`,
`git checkout <default_branch>` and `git reset --hard origin/<default_branch>` against whatever
directory `factory_config.workspace_path()` computes
(`.claude/skills/harness/bin/factory_workspace.py:126-130`, HEAD 6d969ed). The code's own comment
calls that branch a POINT OF NO RETURN, and nothing inspects the directory first: no
`status --porcelain`, no comparison of the target against the checkout the harness itself is
running from. On 2026-08-10 `workspace_root` was set to a directory whose child WAS the live
harness checkout, with three flows running against it and a signed feature branch in progress. No
claim was made and nothing was lost, but the collision is inherent rather than accidental: harness
is self-hosted and legitimately a fleet repo, so the moment `workspace_root` is the parent of the
harness checkout, the factory's workspace for harness IS the harness checkout. The cost of the
next occurrence is every uncommitted change in that directory, unrecoverably.

## Goal

A factory claim can never destroy work. Before the first destructive git command,
`factory_workspace` refuses to touch a checkout that holds uncommitted work, and refuses to touch
the harness control-plane checkout at all — saying which path and which condition, and offering
nobody a way around it. A clean scratch checkout is prepared exactly as it is today.

## Requirements

- REQ-01: When the computed workspace checkout is this harness control-plane checkout itself, the
  tool stops before the first destructive git command and mutates nothing.
- REQ-02: When the target checkout holds uncommitted work — tracked modifications, staged content,
  or untracked files that are not ignored — the tool stops before the first destructive git
  command and mutates nothing.
- REQ-03: A stop names the checkout path and states which of the two conditions fired, in the
  factory's existing operator-facing refusal grammar and with its refused exit status.
- REQ-04: A checkout whose only untracked content is ignored by the repository is not stopped —
  ignored dirt is not work.
- REQ-05: A clean existing checkout, and a checkout that does not exist yet, are prepared exactly
  as they are today, with the same git commands in the same order.
- REQ-06: No command-line flag, argument or environment variable lets a caller proceed past a
  stop.

## Constraints

- The refusal must travel through the existing `factory_cli.refuse(tool, what, value, next_step)`
  grammar and its `EXIT_REFUSED` (exit 2) — the deliberate, one-line refusal. It must NOT be
  produced by letting a git command fail into `run_git`'s `RuntimeError` and `factory_cli.run`'s
  unexpected-failure trap, which prints a different, wordier line and reads as a crash.
  `factory_cli` SUPPLIES this mechanism; it does not obstruct the work.
- Self-detection must reuse `harness_boundary` (`MARKER = .harness/team-config.yaml`), which
  `factory_config` already imports. It must not add a fourth private walk-up copy of the idiom —
  the copies are what FEAT-42 removed — and must never probe for a bare `.harness` DIRECTORY: that
  probe resolved `$HOME` as a root, the fail-open recorded at
  `.claude/skills/harness/bin/harness_boundary.py:48-54`. `harness_boundary` SUPPLIES the
  resolution.
- Out of scope, at the operator's word: no `--force`, no `--yes`, no environment override; no
  change to `workspace_path`'s derivation, to `fleet.yaml` validation, to the clone branch, or to
  `_checkout_issue_branch`.

## Success Criteria

- SC-01: A checkout with an uncommitted tracked modification is refused, the refusal line names
  that checkout path and the uncommitted-work condition, and the modified file survives
  byte-identical.
  verify: automated        evidence: unit
- SC-02: A checkout whose only untracked content is ignored by `.gitignore` is NOT refused, and
  the refresh proceeds.
  verify: automated        evidence: unit
- SC-03: A computed path that resolves to this harness control-plane checkout is refused even when
  that checkout is clean, and the refusal line names the path and the self-checkout condition
  rather than the uncommitted-work one.
  verify: automated        evidence: unit
- SC-04: A genuinely clean scratch checkout still refreshes exactly as today — fetch, checkout of
  the default branch, hard reset, then the issue branch — and a missing checkout still clones,
  with no extra destructive command and no change of order.
  verify: automated        evidence: unit
- SC-05: `.agents/skills/harness/bin/run-unit-tests.sh --kind unit` exits 0.
  verify: automated        evidence: unit
- SC-06: No bypass exists: a reviewer reading the shipped diff finds no flag, argument or
  environment variable that skips either refusal, and cites `file:line` for the refusal sites and
  for the argument parser.
  verify: inspection

## Approval

status: approved
approved-by: operator
date: 2026-09-07
