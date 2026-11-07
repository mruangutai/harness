# Documentation distillation — 2026-11-06

BLUF: No new Expertise entry earned retention. The sourced recall reinforces existing evidence-scope rules; canonical acceptance pointers are sound practice but do not justify displacing a retained rule. No documentation or Expertise changed.

## Sources and attribution

Feature root: `/Users/molchairuangutai/GitHub/harness/.claude/worktrees/harness/BUG-2161-abandon-source-tickets`.
Control plane: `/Users/molchairuangutai/GitHub/harness`.
Paths below are relative to the stated root.

- Feature source: `.harness/harness/features/BUG-2161-abandon-source-tickets/notes/receipt-harness-documentor-T-02-c1.md`, especially “Gate scope: index consistency only” and “That runbook is not duplicated”.
- Corroboration: feature `.harness/harness/features/BUG-2161-abandon-source-tickets/BRIEF.md`, SC-06/SC-07 and Verification gaps; owned `.harness/harness/docs/DECISIONS.md`, DEC-203 section 8; `.harness/harness/docs/DECISIONS-INDEX.md`, DEC-203 row. These were read, not revalidated against implementation.
- Current layers read: control-plane `.harness/expertise/harness-documentor.md` and `.harness/harness/expertise/harness-documentor.md`.
- Accepted by source: dispatcher recall **0/2 aspects** of one compound candidate; self-derived documentation candidate **0/1**. Total accepted **0**, rejected **3**, applied ops **0**.

## Rejected candidates

1. **Separate generated-index consistency from substantive acceptance** — duplicate of craft O-03 (literal/count gates do not establish substance), reinforced by P-09 (generator checks do not validate example contracts). The receipt supplies another instance, not a stronger rule.
2. **Point to canonical live operator acceptance without copying its runbook or claiming it passed** — already required by handoff's pointers-over-payloads and honest evidence discipline. The source demonstrates compliance, not a new failure mode; it is not stronger than a retained entry in the full craft sections. SC-07 remains the canonical acceptance location; this distillation makes no current UAT-status claim.
3. **Retain source-disposal flags, ordering, operator risk and local-finalization behavior** (self-derived) — live repository behavior already documented in DEC-203, not a new documentation-workflow lesson. Copying its recipe into Expertise would introduce a second maintenance surface.

## Counts and verification

| Layer | Patterns before → after | Gotchas | Outcomes | Open | Lines / budget |
|---|---:|---:|---:|---:|---:|
| Craft | 15 → 15 | 15 → 15 | 10 → 10 | 0 → 0 | 45 / 150 |
| Repository | 7 → 7 | 7 → 7 | 0 → 0 | 0 → 0 | 19 / 40 |

Both own files returned **OK**, exit 0, from control-plane `.agents/skills/harness/bin/check-expertise.py`. No accepted ops required the merge tool; no write was attempted or refused. No diff review, build, test suite, documentation edit or live acceptance was performed.

Open questions: none.
