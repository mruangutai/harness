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
  ambiguous target, atomic failure, and a single proposal carrying two operations on distinct
  entries of one section.

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
- SC-04: Each of the two ambiguity conditions — a file already carrying a duplicate id inside one
  section, and two ops in one proposal naming the same section and id — exits 11 with
  `AMBIGUOUS TARGET` naming the section, the id and the reason, and the file's sha256 is unchanged.
  There is no third condition: `section` is required on every op, so an id spanning sections is
  refused at exit 12 by shape before any resolution runs — and that shape refusal is exercised,
  not merely asserted: an op with `section` absent, and one with it empty, each refuse at exit 12
  with `MALFORMED OPS` naming the offending key `section` and the op's index — at the resolver in
  `tests/unit/test-expertise-ops.py` `u13`, and through the CLI in
  `tests/integration/test-expertise-merge.py` `case20`, where the file's sha256 is unchanged
  across the refusal and a following `apply --entries` still exits 0.
  verify: automated        evidence: unit, integration
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
- SC-09: A contract-drift case reads `.claude/skills/harness-distill/SKILL.md` as text, normalises
  it — every run of whitespace collapsed to one space, backticks, asterisks and underscores removed
  — and asserts exactly this: every op verb the distillation contract names is either accepted by
  the `expertise-merge.py ops` subcommand or is `merge`, the one verb the contract itself rewrites,
  detected by BOTH of the phrases `replace on the surviving id` and `drop of the absorbed id`
  occurring in the normalised text; and the tool accepts no verb the contract does not name. The
  rewrite is pinned character for character only where the feature owns the characters — the tool's
  own exit-12 refusal line — so a copy-edit of the skill's prose cannot redden the suite. The case
  is additionally demonstrated RED in the same run against THREE deliberately drifted COPIES of
  the SKILL.md text — one with the phrase `drop of the absorbed id` removed, one naming an extra
  verb the tool does not accept, and one with the verb `drop` REMOVED from the vocabulary line so
  that `ACCEPTED − CONTRACT` is `{drop}` — and the case asserts WHICH direction's failure each
  copy produces, so BOTH directions are shown able to fail rather than assumed to, in the manner
  SC-07 uses for the resolver. The second direction is reachable only because the `ops`
  subparser's own `--ops` help text names the accepted verbs `add`, `replace` and `drop`, which
  is what lets the probe set exceed `CONTRACT` when the contract text stops naming a verb.
  verify: automated        evidence: integration
- SC-10: `.harness/harness/docs/DECISIONS-INDEX.md` carries a `DEC-219` row whose hand-written ruling
  carries the literal string `replace and drop through the ops subcommand`, and
  `python3 tests/integration/test-gen-decisions-index.py`
  exits 0, so the index is what the generator produces.
  verify: automated        evidence: integration
- SC-11 (REQ-07, concurrency half): Lock contention is forced DETERMINISTICALLY and with no
  production test bypass — no environment variable, no injected sleep, no test-only flag, and no
  edit to `expertise-merge.py` or `harness_merge.py`. The test process itself takes the production
  lock through `harness_merge.acquire(<file>.lock)`, the same primitive `locked_update` uses on the
  same path, and inside that block spawns both writers with `subprocess.Popen` — an add-only
  `apply --entries` adding `P-09` and `P-10`, and an `ops` replace of `P-07`'s text. Still holding
  the lock it polls both children every 0.05s for a 2.0-second hold window and asserts NEITHER has
  exited: a child that completes while the lock is held is the RED, because it is not taking the
  shared lock (D-09). The window sits far below `harness_merge.LOCK_TIMEOUT_SECONDS` (10.0), so a
  correctly-locking child is still waiting rather than refused at exit 6. After release each child
  is waited with a 20-second timeout; both exit 0; the final file's id census holds every id present
  before plus `P-09` and `P-10`, none lost; and `P-07` carries the replacement text, not its old
  text. The other two RED shapes are a writer's entries missing from the census and `P-07` still
  carrying its old text. Worst case, including every FAIL path, is the 2.0-second hold plus two
  20-second waits — under 45 seconds.
  verify: automated        evidence: integration
- SC-12 (REQ-01, REQ-02, multi-op composition): One proposal carrying two ops on DISTINCT ORIGINAL
  INDICES of one section — a drop of the entry at the low index and a replace of an entry at a
  higher index — exits 0, and the section's surviving id sequence IN FILE ORDER is exactly the
  base sequence minus the dropped id, with the replaced entry carrying the new text at its
  preserved position relative to every survivor. The identical result is asserted with the two
  ops given in the OPPOSITE order at the resolver, so the outcome is shown independent of op
  order rather than assumed to be; the CLI half is not repeated in reverse, because the CLI is a
  verbatim pass-through to the same function. A second shape, two drops at distinct original
  indices in one section, asserts its own surviving id sequence. Evidence:
  `tests/integration/test-expertise-merge.py` case19 for the file-order claim, with
  `tests/unit/test-expertise-ops.py` u11 (including its reversal) and u12 as the unit half.
  verify: automated        evidence: unit, integration

- SC-13 (REQ-03, cap preservation under adversarial text): No `ops` operation can leave a section
  over its cap, whatever text an op carries. For every character `str.splitlines()` treats as a
  line boundary — the set derived at test time from `str.splitlines()` itself, never a hardcoded
  character list — an `ops` proposal whose `entry` or whose `target` embeds that character exits 12
  with `MALFORMED OPS`, the file's sha256 is unchanged, and the file re-parsed by
  `parse_expertise` holds no section with more entries than its `CAPS` value. The at-capacity
  variant is exercised explicitly: the same proposal against a section already holding its cap
  re-parses at exactly the cap, never cap+1.
  verify: automated        evidence: unit, integration
- SC-14 (REQ-01, REQ-02, REQ-05, target identity): No `ops` operation can write a line the tool's
  own parser cannot address as the id the op named. For every verb — `add`, `replace`, `drop` — a
  `target` that `ENTRY_RE` does not parse back out equal to the target verbatim exits 12 with
  `MALFORMED OPS` naming the offending target, and the file's sha256 is unchanged. Both failure
  shapes are exercised: a target `ENTRY_RE` does not match at all (`PPPP-1`), and a target embedding
  a shorter valid id that `ENTRY_RE` does match while capturing less than the whole target
  (`P-01: fake prefix`). The grammar is asserted by round-trip through `ENTRY_RE`, never by a
  re-typed character class, so the check cannot drift from the parser. The no-lockout consequence
  is asserted directly: after a refused colon-prefix `add`, a legitimate `replace` of the embedded
  id exits 0, not 11.
  verify: automated        evidence: unit, integration

## Verification gaps

- `component`, `ui` and `typecheck` carry `cmd: null` in `.harness/harness.json`. This feature touches
  none of their surfaces — it is a python CLI and its tests — so no criterion rests on them.

## Approval

status: approved
approved-by: mruangutai
date: 2026-09-05
