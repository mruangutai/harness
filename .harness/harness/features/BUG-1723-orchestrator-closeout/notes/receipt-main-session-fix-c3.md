# Fix c3 — BUG-1723 (validate c2 BLOCKED: Q1/Q2) — by Main, main-session-direct

- Q2: DEC-159's BUG-1723 clause now reads "a violation at every station, `done` included", matching ledger.md:52-59 and check-state.py's INV-43 branch; index regenerated with gen-decisions-index.py. T-03's `files` amended to declare DECISIONS.md and DECISIONS-INDEX.md; approval re-signed (notes/answers-2026-09-15-sign.md, "Re-signature after validate c2").
- Q1: caller error at the verifier — `.agents/skills/harness/bin/run-unit-tests.py` executed as a shell script from the gitignored symlink. Matrix at HEAD: `python3 .claude/skills/harness/bin/run-unit-tests.py --kind unit` → 40 files OK; `--kind integration` → 72 files PASS. The exact-pin contract is unchanged.
- No code changed in this cycle beyond DECISIONS.md/-INDEX.md and the plan/feature records.
