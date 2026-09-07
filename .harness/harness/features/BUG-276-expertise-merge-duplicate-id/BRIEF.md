# BRIEF — BUG-276 expertise-merge duplicate id

## Problem

A distillation can hand `expertise-merge.py apply --entries` a proposal in which two different
entries carry the same id in the same section — ids are per-file sequences that every distillation
reassigns, so a collision is ordinary, not exotic. Measured at 6d969ed3 in this worktree, on
`compute_union` directly (base `Patterns: P-01`, proposal `Patterns: P-02 ALPHA`, `P-02 BRAVO`):
the merge returns `P-01, P-02 ALPHA` with an empty conflicts list, and the CLI prints
`ADDED P-02 / PRESERVED P-01 / APPLIED <path>` at exit 0. BRAVO is gone. It is FIRST-wins: the
later entry never arrives, and nothing anywhere says so — no exit code, no stderr, and stdout
names the id once, as if a single entry had been added. Issue #276's own field evidence —
`harness-backend-dev.md` losing P-09, `harness-pm.md` losing P-06/P-10/G-06 — does NOT bear on
this defect: those losses are dated 2026-08-12 (`a810c115`), while `expertise-merge.py` was first
added 2026-08-21 (`47a9935a`), so no `compute_union` existed when they happened. They came from
the whole-file-rewrite distillation that DEC-95/DEC-125 and this tool were built to end — a
different mechanism, since ended — and the guard planned here would not have prevented them. The
defect this BRIEF closes is the one measured independently at 6d969ed3 by the reproduction above.
The one check that could notice a duplicated id — `check-expertise.sh` (~202-206) — is
structurally blind here,
because the drop happens before the file is written, so no duplicate ever reaches the file it
inspects. The cost is that the memory layer silently loses recorded lessons, and the only signal an
operator gets is that the entry is not there next time anyone looks.

## Goal

A distillation that would lose an Expertise entry fails loudly instead. When a proposal names the
same section and entry id more than once, `apply --entries` refuses, writes nothing, and says which
section and which id are ambiguous — so the author fixes the numbering rather than discovering the
loss months later, if at all.

## Requirements

- REQ-01: `apply --entries` never discards an incoming entry silently: a proposal naming the same
  section and entry id more than once is refused, and the refusal output names the section and the
  id.
- REQ-02: A refusal leaves the destination exactly as it was — byte-identical if it existed, and
  still absent if it did not.
- REQ-03: The apply path's existing outcomes are unchanged: a clean union still applies, a
  base-versus-proposal text divergence still refuses, and a section cap overflow still refuses.
- REQ-04: The tool's documented exit-code interface matches the codes `apply` can actually return.

## Constraints

- Supplies the fix's shape: `_check_proposal_ambiguity` (~305-317) and `_resolve_add` (~281) in the
  same file already refuse this exact class on the sibling `ops` path with
  `MergeRefusal(11, ["AMBIGUOUS TARGET section=<s> id=<i> reason=..."])` (DEC-219). The fix joins
  that convention; it does not invent an exit code or a message shape.
- `check-expertise.sh` is NOT modified. Its duplicate-id check already exists (~202-206) and is
  correct; it cannot see this defect because `compute_union` drops the duplicate before anything is
  written, so the file it inspects never contains one.
- `.claude/skills/harness/bin/expertise-merge.py` and `.agents/skills/harness/bin/expertise-merge.py`
  are the same inode (DEC-202: `.agents` links to the one authored tree). Exactly ONE path is
  edited and there is no sync step.
- python3 stdlib only — the file's own stated rule (module docstring, ~20).
- The refusal must leave the target byte-identical, as the existing exit-7 and exit-8 refusals do;
  the integration suite asserts this by sha256 (`_assert_case24_ambiguous`, ~1190-1209).
- Section caps (DEC-145) and the union semantics (DEC-95) are untouched.
- Out of scope, as a decision and not an oversight: issue #276's suggested standing checks — entry
  count monotonic across a distillation, and every input entry present by CONTENT afterwards —
  would police every write route rather than this one input, and are a separate, larger surface.
  This ticket closes the route the operator narrowed to: the ambiguous proposal input. It does not
  claim to close every silent-reduction route — the parse/render drop recorded as D-07 is a
  separate, known defect and stays reachable after this fix.

## Success Criteria

- SC-01: A proposal carrying one section+id twice with DIFFERENT texts is refused by
  `apply --entries` at exit 11; the output carries `AMBIGUOUS TARGET`, the section name, the id and
  `reason=`; and the target file's sha256 is unchanged across the invocation.
  verify: automated        evidence: integration
- SC-02: The SAME refusal occurs when the two duplicate entries carry IDENTICAL text — keyed on
  (section, id) alone, never on a text comparison (D-02).
  verify: automated        evidence: integration
- SC-03: `compute_union`, called directly with a proposal duplicating a section+id, raises
  `MergeRefusal` with code 11 and an `AMBIGUOUS TARGET` line naming the section and the id, rather
  than returning a merged list that silently contains only the first of the two entries. The
  assertion is demonstrated failing against the pre-fix function before the guard lands.
  verify: automated        evidence: unit
- SC-04: No regression on the apply path: an add-only proposal still exits 0 with
  ADDED/PRESERVED/APPLIED, a same-id-different-text divergence against the base still exits 7, and
  an over-cap proposal still exits 8.
  verify: automated        evidence: integration
- SC-05: With the destination absent (the `base_bytes is None` path of `cmd_apply`'s transform), a
  proposal duplicating a section+id is refused at exit 11 and NO file is created at the
  destination.
  verify: automated        evidence: integration
- SC-06: The module docstring's exit-code table lists every code `apply` can return, including 11,
  with no code listed that `apply` cannot return.
  verify: inspection

## Verification gaps

- None. Both kinds these criteria rest on — `unit` and `integration` — are `active` in
  `.harness/harness.json` with real runners (`run-unit-tests.sh --kind unit` / `--kind integration`),
  and both suites already reach the changed code.

## Approval

status: pending
approved-by:
date:
