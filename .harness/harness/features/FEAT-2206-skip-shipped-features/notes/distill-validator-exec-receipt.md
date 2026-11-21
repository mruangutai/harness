# distill-validator EXEC-01 — main-session execution receipt (2026-11-21)

The validator lead returned BLOCKED solely on EXEC-01: security-reviewer is write-less, and the
lead has no shell, so the accepted op could not be applied inside the run. Distillation step 3
assigns that apply to the main session, verbatim.

Command (exactly as the digest named it, line 32):

    python3 .agents/skills/harness/bin/expertise-merge.py ops \
      --file .harness/expertise/harness-security-reviewer.md \
      --ops .harness/harness/features/FEAT-2206-skip-shipped-features/runs/distill-validator/security-ops.json

Output: `REPLACED P-11`, `APPLIED .../harness-security-reviewer.md`, exit 0.

Directory-wide `check-expertise.py .harness/expertise/`: exit 0, 16 OK, 0 violations; one
pre-existing ADVISORY (security G-01 names DEC-100, issue 340) unchanged.

Entry counts after (P/G/O/Open): harness-security-reviewer 15/15/10/0 and harness-qa 15/15/10/1,
both equal to before (both ops are replacements). Distill totals: product 0 accepted / 3 rejected;
validator 2 accepted (qa P-03, security P-11) / 11 rejected.
