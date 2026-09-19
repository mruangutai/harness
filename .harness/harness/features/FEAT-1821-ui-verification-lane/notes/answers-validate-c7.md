# Answers — FEAT-1821 validate c7 — 2026-09-19

## Ruling: one more main-session-direct T-01 round; rework 7→8 rounds / 315→360 minutes.
V7-01 is a defect in Main's own gate (T-01): `spec_titles()` greps for literal `test('…')` titles, but the lane's specs are manifest-driven (`test(check.spec_title, …)`), so any client-package change reports eleven titles absent. That would block FEAT-53's next client change — the opposite fail mode of the one this feature closed, and just as wrong. Fix: a spec title counts as present when it appears literally in an e2e spec file OR when the bundle carries an executed record under that exact title with screenshot evidence (the record can only exist because the runner ran a test by that name). The static grep stays for the no-bundle case.
V7-02: pin fail-first per SC by running today's test file against the pre-T-01 tree (module absent) and the pre-c7 tree (mutants red), recording failing test names per SC in the receipt.
No specialist work; no FEAT-53 production change. Then re-validate (qa + code-reviewer on the T-01 diff only), docs, briefing.
