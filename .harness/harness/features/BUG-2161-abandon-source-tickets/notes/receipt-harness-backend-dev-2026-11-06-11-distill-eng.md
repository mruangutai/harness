# Receipt — harness-backend-dev — BUG-2161 distill (2026-11-06-11-distill-eng)

BLUF: 2 craft entries applied (both displacing weaker ones), 0 repo entries; no code, tests or review run. Checker OK on both files.

Counts (before → after): craft Patterns 15→15, Gotchas 15→15, Outcomes 10→10, Open 0→0; repo Patterns 4→4, Gotchas 11→11, Outcomes 1→1, Open 0→0.
Accepted: self-derived 0, lead-relayed 2 (candidates 1 and 3). Rejected: candidate 2; the self-derived piped-exit-code note.

Applied ops (`expertise-merge.py ops`, craft file): replace P-12 (opt-in alias overlap matrix plus dry-run/apply effect parity); replace G-02 (gate a destructive follow-up on the prerequisite write's reported success, red-first).

Rejections:
- Candidate 2 (receipt/tip pin identity): the loopback was receipt form, caused by a SHA self-reference. The author already recorded both SHAs, and the fix is a harness receipt-form rule, not craft; it would rot as a recipe.
- Piped-verify exit code unobserved (apply receipt): already covered by G-16's count and green-proof check; no new rule.
- Simplify-reader findings (helper extraction, fixture duplication): covered by P-16 and O-07.

Verification: none run besides check-expertise.py on both files (OK).
