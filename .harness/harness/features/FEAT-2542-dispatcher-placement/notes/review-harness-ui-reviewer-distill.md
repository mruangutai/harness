# UI-review distillation — FEAT-2542

**PASS — two craft replacements applied: check the physical line an operator copies, and prove the printed command reached the intended target.** No diff reviewed; no suite or command probe run in this dispatch.

- **U1 accepted as G-11.** The c2 UI audit covered spaces and apostrophes (30 invocations across 22 refusals), not literal newlines. Security measured intact argv for the whole command but split physical lines, including a standalone marker in stderr. Test the line actually copied, not just the reconstructed argv. O-10 rates a reached outcome, G-14 checks source patterns, and O-08 reproduces a known defect; none prompts this fixture. The displaced generated-HTML heuristic remains in Harness repository Patterns. The c2 panel treated the newline issue as a low advisory outside the wording ruling, not an unclosed c1 gate.
- **Decoy method accepted as P-03.** The c2 fixture put a matching claim in the default registry and asserted which registry was read or changed; an exit-only probe could pass at the wrong target. This adds a target discriminator, not a duplicate of the product squad’s pre-signature literal execution or O-08’s live repro. The broader census and direct-contract checks cover the displaced markdown scoping rule.
- **No new signed-wording rule.** The c1 escalation and delegated ruling confirm G-08: change signed intent through approval, not by treating conforming implementation as drift. O-10 already covers severity based on where a compliant reader lands. No repository-only update.

Evidence: `review-harness-ui-reviewer-c1.md`, `review-harness-ui-reviewer-c2.md`, `review-harness-security-reviewer-c2.md`, `answers-2026-11-26-validate-c0.md` (rules 1–4), and validator digests for `r-20261126-2` and `r-20261126-3`.

Craft counts before → after: Patterns 15 → 15, Gotchas 15 → 15, Outcomes 10 → 10, Open 0 → 0. Batch `c7e91a51daae10dd62a994508eb3f536168e260727ef9a17e78b1384a14dd3e4`; receipt `notes/expertise-receipt-fbf6bd30cd2478bc1dfcafde957ea6481bfc103154b22752ba0f6560e6244480.json`.

Open questions: none.
