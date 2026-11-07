# Operator receipt — BRIEF Verification-gaps reword, 2026-10-07

- Author: operator (direct edit). Answers Q-09.
- Change: one `## Verification gaps` bullet. `- SC-01–SC-03 are NOT RUN YET.` became `- The first three Success criteria have NOT RUN YET.` The rest of the bullet, all SC declarations, `verify:` modes and `## Approval` are unchanged.
- Reason: under #2131 (`37cfcfd4`), `validate-digest.py` treats any bullet naming an SC ID outside the `- SC-NN (perspective):` shape as a malformed declaration. That cancels the non-automated QA waiver (fail-closed by design).
- Check against main's `validate-digest.py`: `_malformed_sc_declarations` False; `_known_nonautomated_criteria` True.
