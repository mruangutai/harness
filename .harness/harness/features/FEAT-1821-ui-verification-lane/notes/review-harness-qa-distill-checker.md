# Expertise checker evidence

PASS — the sole permitted checker invocation completed with exit status 0.

- Command: `python3 /Users/molchairuangutai/GitHub/harness/.agents/skills/harness/bin/check-expertise.py /Users/molchairuangutai/GitHub/harness/.harness/expertise/`
- Invocation count: 1
- Exit status: 0
- Feature validation: not run

## Checker result

All 17 checked craft Expertise files returned `OK`. The checker emitted two non-failing advisories:

- `harness-pm.md:3` P-01 names `.harness/` — repository-layer candidate (issue 340).
- `harness-security-reviewer.md:19` G-01 names `DEC-100` — repository-layer candidate (issue 340).

No checker violations were reported.
