# BRIEF — BUG-1308 Expertise replace and drop

## Problem

The Expertise distillation contract instructs every agent to emit ops `add | replace | merge | drop`,
each naming a `target` (`.claude/skills/harness-distill/SKILL.md:112-123`, DEC-66), but
`expertise-merge.py` exposes exactly one subcommand, `apply --file --entries`, whose `compute_union`
can only append new ids. Nothing in that file can remove or overwrite an existing entry. So a
distillation that must displace a stale entry has no mechanism: when the target section is already at
its DEC-145 cap the union exceeds the cap, the tool refuses at exit 8, and the stale entry stays.
Observed at BUG-1286 feature-close distillation on a repository-tier entry. The contract promises an
operation the mechanism does not have, so the agent is instructed to do something that fails closed.

## Goal

An agent applying a distillation can replace or remove an Expertise entry through the same merge tool
it already uses to add one — deterministically, under the same lock, with the file left byte-identical
whenever the operation is refused. The distillation contract and the merge mechanism state the same
vocabulary afterwards, so no agent is instructed to emit an op nothing can apply.

## Requirements

- REQ-01: An agent can replace an existing Expertise entry's text through the merge tool, keyed to
  that entry, in one operation that either lands whole or does not land.
- REQ-02: An agent can drop an obsolete Expertise entry through the merge tool.
- REQ-03: Section caps are preserved: a replace at capacity succeeds and leaves the section the same
  size; no operation can leave a section over its cap.
- REQ-04: An operation whose target does not exist is refused with a message naming the section, the
  id and the reason, and nothing is written.
- REQ-05: An operation whose target is ambiguous is refused with a message naming the section, the id
  and the reason, and nothing is written.
- REQ-06: A refused proposal leaves the Expertise file byte-identical to its prior state — no partial
  rewrite, whichever operation in the proposal caused the refusal.
- REQ-07: Existing concurrent union-merge behaviour is unchanged for add-only proposals: the same
  exit codes, the same stdout tokens, the same lock.
- REQ-08: The distillation contract text and the merge mechanism agree: every op the contract tells an
  agent to emit is either applied by the tool or rewritten by the contract into ops that are.
- REQ-09: Regression coverage exists for replacement at capacity, removal, a missing target, an
  ambiguous target, and atomic failure.

## Constraints

- SUPPLIES — `harness_merge.locked_update` (`.claude/skills/harness/bin/harness_merge.py:121`) is the
  lock plus atomic-replace primitive the new operation must reuse; `MergeRefusal` is how it fails
  closed. DEC-199 makes this the one merging core.
- SUPPLIES — DEC-66 already blesses ops with stable per-section ids and a named target, so the
  operation is a mechanism for a contract that exists, not a new contract.
- BLOCKS — DEC-145's caps (`Patterns` 15, `Gotchas` 15, `Outcomes` 10, `Open` 5) are spelled once in
  `expertise-merge.py:37` and cross-checked against `check-expertise.sh` as text; no third copy.
- BLOCKS — DEC-174: `.claude/skills/harness-distill/SKILL.md` resolves to NOBODY under
  `check-domain.sh --resolve`, so its text change is a main-session-direct step, not a squad task.
- BLOCKS — DEC-213: harness tests live under `tests/unit/**` and `tests/integration/**`; the directory
  selects the kind.
- BLOCKS — python3 stdlib only in `.claude/skills/harness/bin/`; no third-party imports.
- BLOCKS — `.agents/skills` is a symlink to `.claude/skills`; every path recorded uses the tracked
  `.claude/...` spelling.
- Existing entry ids are never reused after a drop (DEC-66's accepted tradeoff).

## Success Criteria

- SC-01: With `Patterns` holding 15 entries, a proposal replacing `P-07` exits 0, stdout carries
  `REPLACED P-07`, the file still holds 15 `Patterns` entries, and `P-07` carries the new text at its
  original ordinal position (7th) in the section.
  verify: automated        evidence: integration
- SC-02: A proposal dropping `G-03` exits 0, stdout carries `DROPPED G-03`, the string `- G-03:` is
  absent from the file afterwards, and every other id present before is still present.
  verify: automated        evidence: integration
- SC-03: A proposal naming an id absent from the file exits 10, its output carries `MISSING TARGET`
  with the section and the id, and the file's sha256 is unchanged.
  verify: automated        evidence: integration
- SC-04: Each of the three ambiguity conditions — a bare id matching entries in more than one section,
  a file already carrying a duplicate id inside one section, and two ops in one proposal naming the
  same target — exits 11 with `AMBIGUOUS TARGET` naming the section, the id and the reason, and the
  file's sha256 is unchanged.
  verify: automated        evidence: integration
- SC-05: A proposal whose first ops are valid and whose last op is refusable exits non-zero and leaves
  the file's sha256 byte-identical to before the invocation.
  verify: automated        evidence: integration
- SC-06: Add-only behaviour is unchanged: `python3 tests/integration/test-expertise-merge.py` exits 0
  with every pre-existing case still passing, including exit 7 CONFLICT and exit 8 CAP EXCEEDED.
  verify: automated        evidence: integration
- SC-07: The op-resolution layer is unit-covered and its failing-first state is demonstrated in the
  same file: `python3 tests/unit/test-expertise-ops.py` exits 0, and one of its cases feeds the same
  replacement input to the pre-change mechanism, `compute_union`, asserting it reports a conflict and
  performs no replacement — so the suite reddens if the new resolver is reverted to the old one.
  verify: automated        evidence: unit
- SC-08: A file produced by a replace and a file produced by a drop are both accepted by
  `bash .claude/skills/harness/bin/check-expertise.sh <file>` at exit 0, so the format the checker
  governs is unbroken.
  verify: automated        evidence: integration
- SC-09: A contract-drift case reads `.claude/skills/harness-distill/SKILL.md` as text and asserts
  exactly this: Every op verb the distillation contract names is either accepted by the
  expertise-merge.py ops subcommand or is merge, the one verb the contract itself rewrites with the
  literal sentence: a replace on the surviving id plus a drop of the absorbed id; and the tool
  accepts no verb the contract does not name. The case is additionally demonstrated RED in the same
  run against a deliberately drifted COPY of the SKILL.md text — one copy with that literal sentence
  deleted, one copy naming an extra verb the tool does not accept — so a one-sided change is shown
  to fail rather than assumed to, in the manner SC-07 uses for the resolver.
  verify: automated        evidence: integration
- SC-10: `.harness/harness/docs/DECISIONS-INDEX.md` carries a `DEC-216` row whose hand-written ruling
  carries the literal string `replace and drop through the ops subcommand`, and
  `python3 tests/integration/test-gen-decisions-index.py`
  exits 0, so the index is what the generator produces.
  verify: automated        evidence: integration
- SC-11 (REQ-07, concurrency half): Two invocations against the SAME Expertise file overlap in time
  — an add-only
  `apply --entries` adding `P-09` and `P-10`, and an `ops` replace of `P-07`'s text — with the
  overlap forced structurally: both children are spawned with `subprocess.Popen` before either is
  waited on. Both exit 0; the final file's id census holds every id present before plus `P-09` and
  `P-10`, none lost; and `P-07` carries the replacement text, not its old text. Each child is waited
  with a 30-second timeout, so the case is bounded well under 60 seconds. A shared-lock regression
  (D-09) reports RED as one writer's entries missing from the census — `P-09`/`P-10` absent, or an
  id that existed before gone — or as `P-07` still carrying its old text.
  verify: automated        evidence: integration

## Verification gaps

- `component`, `ui` and `typecheck` carry `cmd: null` in `.harness/harness.json`. This feature touches
  none of their surfaces — it is a python CLI and its tests — so no criterion rests on them.

## Approval

status: pending
approved-by:
date:
