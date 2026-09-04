# FEAT-54 validation-order-c1 — product ruling

## Ruling

**F-06 is resolved without operator input.** `BRIEF.md` REQ-02 controls the required behavior: the sole `Scope:` line precedes every `Authority:` line. T-02 is the subordinate implementation/task detail; its contrary sentence does not narrow the approved requirement. Main may route a direct fix under the existing T-02 trace to REQ-02, enforcing and covering Scope-before-Authority order. No BRIEF or plan amendment is required or permitted for this fix.

## Controlling text and authority

- Required behavior: `BRIEF.md:26-27` says the fixed shape is “exactly one `Scope:` line carrying a concise action label, **then** one to four `Authority:` lines, and no other prose.” “Then” is an express ordering term, not an implementation inference.
- Task detail: `plan.yaml:245-249` first says the `Scope:` line is “followed by” the `Authority:` lines, but then expressly says line order “is not enforced beyond Scope: appearing exactly once.” That last sentence conflicts with, rather than clarifies, REQ-02.
- Finding record: `runs/2026-09-02-review-c0-validator/digest.md:20,28,47-49` records F-06 and the pending order question; its cited code-review finding, `notes/review-harness-code-reviewer-c0.md:33-49`, demonstrates the accepted reversed body and identifies the same BRIEF/T-02 mismatch.
- Governing level rule: DEC-48 (`.harness/harness/docs/DECISIONS.md:516-526`) defines a BRIEF REQ as what the product must do and a T item as a concrete step. Therefore the REQ governs observable shape; T-02 governs implementation only where consistent with it.
- Weakest-valid-specification rule: `docs/PRINCIPLES.md:104-118`, “No more specific than necessary,” requires the weakest statement consistent with the requirement. Here that means enforce only the order expressly committed: the one `Scope:` line must occur before all one-to-four `Authority:` lines. Do not invent ordering among Authority lines or further body constraints.
- DEC-214 (`.harness/harness/docs/DECISIONS.md:6696-6715`) confirms the shared parser and the one-Scope/one-to-four-Authority contract but is silent on relative order; that silence does not repeal REQ-02’s express “then.”
- DEC-32 (`.harness/harness/docs/DECISIONS.md:354-366`) requires operator input for scope, goal, or decision changes. Correcting implementation to the already-approved REQ changes none of those, so operator input is unnecessary.

## Independent Scope-label obligation

Line order and label content are separate defects. Regardless of where the line appears, REQ-02 independently requires its sole `Scope:` line to **carry a concise action label** (`BRIEF.md:26-27`). A bare `Scope:` or a whitespace-only value violates that clause. The weakest mechanical repair is to reject an empty value after trimming; semantic concision remains the operator-facing judgment already assigned by SC-10 (`BRIEF.md:143-147`). Fixing order must not be treated as fixing the empty-label defect, or vice versa.

## Disposition

Mark F-06 **resolved by product ruling, repair required**: Main direct should make the shared parser reject any body in which an `Authority:` line precedes `Scope:`, and add the corresponding existing-lane test mutation. Preserve F-05’s independent non-empty/whitespace-only Scope repair and coverage. Do not edit the signed BRIEF or plan merely to make their prose agree; the authority hierarchy already supplies the executable reading.

Internal send-backs: **0**.
