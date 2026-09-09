# UI Review — BUG-276 — Mode B — cycle 0

## Verdict: PASS (advisory audit of adjacent CLI text surface; no rendered UI in scope)

## Census (measured, not predicted)

Full diff `6d969ed3..ef8efd99` name-status (17 files) plus an extension census
(`html|css|scss|tsx|jsx|vue|svelte|less`) across every changed path: **zero hits**. The only
`.md` hits are feature-directory bookkeeping (`BRIEF.md`, `STATE.md`, `plan.yaml`,
`notes/*`, `observations/*`, `feature.json`) — explicitly out of scope per the dispatch and per
D-tier bookkeeping exclusion, not authored UI.

`DESIGN.md` search: none under
`.harness/harness/features/BUG-276-expertise-merge-duplicate-id/` and none at the worktree root.
The only `DESIGN.md` files anywhere in the tree belong to unrelated features
(FEAT-19, FEAT-40, FEAT-11, FEAT-10) and the skill template. **No design contract governs this
change** — expected for a CLI-internals bug fix, not itself a gap.

The three files under review are: `expertise-merge.py` (CLI, +24/-1), and two Python test
suites (`test-expertise-ops.py` +54, `test-expertise-merge.py` +53) with no rendered surface of
their own.

**Conclusion: no rendered UI surface in this diff.** Self-scoping fully out would be legitimate
on this basis alone (P-01/P-06 project tier), but the dispatch explicitly names the CLI's
operator-facing stdout/exit-code output as adjacent in-remit surface (step 4) — audited below,
per Expertise P-06.

## Adversarial audit — the new refusal message

The whole functional diff in `expertise-merge.py` is `_check_proposal_duplicate_ids`, called
from `compute_union` (the `apply --entries` path), emitting on the second occurrence of a
duplicated `(section, id)` inside one proposal:

```
AMBIGUOUS TARGET section=<name> id=<eid> reason=two entries in one proposal name this target
```
exit code 11 (`expertise-merge.py:120-131`).

**Legibility/actionability** — PASS. The line names the exact section and id (the distilling
agent's own generated ops/entries), and the `reason=` clause states the cause in plain language
("two entries in one proposal name this target"). The agent that receives this can locate and
deduplicate the offending entry without further lookup.

**Consistency with existing message shapes** — PASS, verified by direct comparison:
- `_check_base_ambiguity` (pre-existing, `:281-289`): `AMBIGUOUS TARGET section={s} id={t} reason=the id appears {n} times in section {s}`
- `_check_proposal_ambiguity` (pre-existing, ops-vs-ops, `:328-337`): `... reason=two ops in one proposal name this target`
- New (`_check_proposal_duplicate_ids`, entries-vs-entries): `... reason=two entries in one proposal name this target`

All three share the identical `AMBIGUOUS TARGET section=… id=… reason=…` prefix/field grammar;
the new one differs from its closest sibling only in "entries" vs "ops", which the function's
own docstring calls out as deliberate ("Mirrors `_check_proposal_ambiguity`, whose message
differs only in saying ops where this one says entries"). No divergent vocabulary, no new field
shape.

**Downstream contract fit** — checked against the consumer's own doc,
`.claude/skills/harness-distill/SKILL.md:138-144`, which already documents `11 AMBIGUOUS
TARGET` generically ("a target is ambiguous... or two ops in one proposal name the same
section and ID") and separately notes "Add-only proposals may still use `apply --entries`,
unchanged" — i.e. the distilling agent's existing mental model of code 11 already covers this
path; no doc update was needed and D-09 (no new row added there) is consistent with that, not a
gap.

**Exit-code docstring** (module header, `:16-21`): this diff also adds the previously-undocumented
code 9 and the new code 11 to the docstring's exit-code list. Codes 10 and 12 remain absent —
per the constraint's D-05, that is a signed, deliberate omission (adding them fails SC-06), not
re-litigated here.

**Accessibility / theme parity** — not applicable. This is a stdout/exit-code batch CLI surface
with no colour-only state encoding and no rendered theme (G-02, project P-03); stated explicitly
rather than omitted.

No findings raised. Nothing must_fix.

## Open questions
None.
