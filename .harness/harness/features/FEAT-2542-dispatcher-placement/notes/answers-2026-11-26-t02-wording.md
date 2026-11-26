# T-02 index-ruling wording — 2026-11-26

**Authority.** The operator delegated approval to fable-advisor; ruled by AdvisorA3Wording.

**Gap.** The signed T-02 intent prescribes a 32-word DECISIONS-INDEX ruling, but T-02's own verify runs `test-gen-decisions-index.py`, which caps a ruling at 30 words (`len(ruling.split()) > 30`).

**Ruling.** The gate wins on substance. The 30-word text replaces the prescribed one ("named" and "product-lead" dropped), and the deviation is recorded through `plan-merge.py record-amendments` on T-02.intent, never `amend` and never an edit.

**Constraints.**
- Only the post-`::` prose of the DEC-258 row changes.
- The DECISIONS.md entry and T-01's pin stay byte-identical.
- Re-run T-02's full verify.
