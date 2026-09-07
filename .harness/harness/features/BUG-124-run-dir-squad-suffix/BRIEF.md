# BRIEF — BUG-124 Run-dir squad suffix is unenforced

## Problem

A dispatcher can name a run-dir path in a dispatch prompt that the callee provably cannot write, and
nothing at dispatch time notices. Every lead's write grant keys on a **trailing** squad suffix — the
only three grants in `.harness/team-config.yaml` containing `/runs/` are
`.harness/*/features/*/runs/*-product/**` (line 306), `*-eng` (line 315) and `*-validator` (line 324)
— so an inverted slug resolves to a set that excludes the callee. Measured in this worktree at
6d969ed3: `check-domain.sh --resolve .../runs/t01-eng/digest.md` answers `harness-eng-lead` and
`harness-orchestrator`, while `.../runs/eng-t01/digest.md` answers `harness-orchestrator` alone.
Both exit 0, because `--resolve` answers on stdout and never through the exit code. The convention is
stated in prose only (`.claude/skills/harness/SKILL.md:272-274`); no mechanical enforcement exists.
The cost lands on the callee, mid-run, as a denied write of an artifact it was told to produce, with
the build spine already open.

## Goal

A dispatch that names an unwritable run-dir path is refused when it is dispatched, not discovered when
a member tries to write. The dispatcher gets one message naming the bad slug and the compliant form,
and fixes it in one step before any work starts.

## Requirements

- REQ-01: A governed dispatch whose prompt names a run-dir path that no squad lead can write is
  refused before the dispatch runs.
- REQ-02: The refusal names the offending slug and a compliant form, so the dispatcher can correct it
  without reading team-config.yaml.
- REQ-03: A governed dispatch that names only writable run-dir paths, or names none at all, is
  unaffected.
- REQ-04: The accepted slug vocabulary follows `.harness/team-config.yaml`: adding, renaming or
  removing a squad's run-dir grant there changes what is accepted, with no second edit anywhere.
- REQ-05: When the vocabulary cannot be determined, the dispatch passes through and the reason is
  stated on stderr. The check never blocks on its own failure.
- REQ-06: A dispatcher can quote a refusal — paste the guard's own output into the follow-up
  dispatch that debugs, shares or escalates it — without that dispatch being refused for carrying
  the quoted path.

**Disclosed as detected by nothing:** this fix checks slug SHAPE against the run-dir grant family,
not ownership by the callee, so a well-formed slug carrying a trailing squad suffix that is not the
callee's own — an orchestrator dispatching `harness-eng-lead` and naming `runs/t01-product/digest.md`
— passes every requirement above while still being unwritable by that callee (D-01).

## Constraints

- **DEC-100 SUPPLIES the mechanism**: only `exit 2` blocks a dispatch. Exactly one branch of
  `dispatch-guard.sh` fails closed today (a missing `HARNESS-FEATURE` first line); every other branch
  passes through on its own failure, and this check must join the second group.
- **DEC-171 BINDS the reader**: PyYAML is required and hand-rolled YAML regex readers of
  `.harness/team-config.yaml` are struck. The vocabulary must come from a real parse.
- **`dispatch-guard.sh` is the only site that can see a dispatch prompt** — `tool_input.prompt` exists
  only on the dispatch payload (`FEAT-31/notes/probe-hook-payload-identity.md`). `check-plan-routes.py`
  sees plan.yaml `files:` values and never a dispatch-named path, so it cannot host this rule.
- The guard's python body runs under `python3 -I` and is one single-quoted shell argument: stdlib
  only, and **no apostrophes** anywhere in added code or comments.
- `tests/integration/test-dispatch-guard.py` pins the pre-existing refusal set. Its 48 checks pass at
  6d969ed3 (`python3 tests/integration/test-dispatch-guard.py`, exit 0, "48 of 48 cases passed"). New
  cases are APPENDED; editing one is deleting the proof.
- `.harness/team-config.yaml` is READ by this fix and must not be edited by it.
- `.agents/skills` is a symlink to `.claude/skills`: there is one `dispatch-guard.sh`, not two.

## Success Criteria

- SC-01: The reported case is refused: a governed dispatch prompt naming
  `[.]harness/harness/features/<feat>/runs/eng-t01/digest.md` exits 2, and stderr contains the string
  `eng-t01`. The `[.]` is the D-05 escape, applied because this criterion quotes the path rather than
  directing a write; the producing case restores the real `.harness/` anchor from it — the
  `q.replace("[.]", ".")` idiom the plan's own `verify:` lines use — and it is that restored path the
  prompt carries.
  verify: automated        evidence: integration
- SC-02: The refusal is actionable: the same stderr also names a compliant form carrying a trailing
  squad suffix drawn from team-config.yaml.
  verify: automated        evidence: integration
- SC-03: Compliant slugs are unaffected: prompts naming `t01-eng`, `plan-product` and a dated
  `2026-08-26-2-plan-product` do not exit 2, and a prompt naming no run-dir path at all leaves the 48
  pre-existing checks in `tests/integration/test-dispatch-guard.py` passing with no case edited.
  verify: automated        evidence: integration
- SC-04: The vocabulary is derived, not literal: with a manifest whose only run-dir grant names an
  invented squad, `t01-<that squad>` is accepted and `<that squad>-t01` is refused.
  verify: automated        evidence: integration
- SC-05: The check fails open: with the vocabulary unloadable, a dispatch naming `eng-t01` does not
  exit 2 and stderr states why the check was skipped.
  verify: automated        evidence: integration
- SC-06: The gate is shown capable of red: the new integration cases, run against the pre-change
  `dispatch-guard.sh` from `git show 6d969ed3:.claude/skills/harness/bin/dispatch-guard.sh` via
  `DISPATCH_GUARD_BIN`, report the refusal cases as FAIL. Evidence is the recorded command and output
  in the builder's receipt, read at the review sha with `git show <review_sha>:<receipt path>`.
  verify: inspection
- SC-07: A refusal strands no state: the refused dispatch records no claim — the registry holds no
  claim for the dispatched persona after an `eng-t01` refusal.
  verify: automated        evidence: integration
- SC-08: The refusal is paste-safe: the exact stderr emitted by an `eng-t01` refusal, used verbatim
  as the body of a second governed dispatch prompt (behind a valid `HARNESS-FEATURE:` first line),
  does not exit 2 and its own stderr carries no run-dir slug refusal. Deleting the anchor rewrite
  from the refusal message turns this case red.
  verify: automated        evidence: integration
- SC-09: The skip reason is distinguished, so a broken check is not mistaken for the benign REQ-05
  skip: with a manifest that parses but declares no run-dir write grant, stderr states the
  vocabulary is empty because the manifest declares no run-dir grant; with the derivation itself
  broken (an unparseable manifest), stderr instead states that the vocabulary derivation subprocess
  failed. Neither exits 2, and the two messages are not interchangeable — each case asserts the text
  belonging to its own reason and asserts the absence of the other.
  verify: automated        evidence: integration

## Verification gaps

- None new. Both kinds this brief rests on have runners: `unit` and `integration` are
  `.agents/skills/harness/bin/run-unit-tests.sh --kind <kind>` in `.harness/harness.json`, and both
  select real files on this surface (`tests/unit/**`, `tests/integration/**`).

## Approval

status: pending
approved-by:
date:
