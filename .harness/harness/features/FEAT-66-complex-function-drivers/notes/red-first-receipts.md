# FEAT-66 — red-first receipts

Committed AFTER the implementation pin `e2b580a6` and not claimed to exist inside it. The baseline is
`35c39f02` (the signed plan; production bytes identical to `origin/main` at `cb6f8050`).

## Baseline receipts, captured before any production edit

`python3 /tmp/feat66-baseline.py <worktree> /tmp/feat66-baseline.json` at `35c39f02`, in the feature
worktree, before the first edit to any of the three files. Per suite: command (`python3 <suite>` from
the checkout root), exit status, stdout bytes, stderr bytes (sha1 in `clean-pin-byte-receipts.md`).

| suite | exit | stdout | stderr |
|---|---|---|---|
| tests/integration/test-check-domain.py | 0 | 1733 B | 0 B |
| tests/integration/test-check-domain-artifact.py | 0 | 5110 B | 0 B |
| tests/integration/test-check-domain-claims.py | 0 | 2221 B | 0 B |
| tests/integration/test-check-domain-grant.py | 0 | 5874 B | 0 B |
| tests/integration/test-check-domain-post.py | 0 | 4458 B | 0 B |
| tests/integration/test-check-domain-worktree-parity.py | 0 | 4062 B | 0 B |
| tests/integration/test-check-domain-worktree.py | 0 | 4496 B | 0 B |
| tests/integration/test-check-domain-approval.py | 0 | 6319 B | 0 B |
| tests/unit/test-config-shape-matrix.py | 0 | 1267 B | 0 B |
| tests/integration/test-plan-merge.py | 0 | 38346 B | 0 B |
| tests/integration/test-validate-digest.py | 0 | 23803 B | 0 B |

`tests/integration/test-validate-digest-shadows.py`, named by the plan, does not exist on
`origin/main` or this branch (ledger D-04); its baseline run was "No such file" at exit 2 and it is
dropped by amendment.

## The grade assertion, red at the baseline (SC-01)

`tests/unit/test-driver-grades.py` was written and committed first (`abe0d43a`), then run at
`35c39f02` production bytes. Verbatim:

```
PASS check-domain.py: shape_problems exists under its name
FAIL check-domain.py: shape_problems grades >= 4 or exactly 2 grade 1 (cyclomatic+cognitive+abc cyc=135 cog=356 abc=320.6)
PASS validate-digest.py: validate exists under its name
FAIL validate-digest.py: validate grades >= 4 or exactly 2 grade 1 (cyclomatic+cognitive+abc cyc=124 cog=244 abc=251.0)
PASS plan-merge.py: apply_merge exists under its name
FAIL plan-merge.py: apply_merge grades >= 4 or exactly 2 grade 1 (cyclomatic+cognitive+abc cyc=59 cog=136 abc=162.9)
3 failure(s)
exit=1
```

The same file, from the pin, run against a clean detached checkout of the baseline
(`FEAT66_BIN=<baseline>/.claude/skills/harness/bin`) is reproduced in `clean-pin-byte-receipts.md`
under "Red-first"; at the pin it is `ALL PASS` exit 0.

A file-wide form of the lock (every function in the three files at bar 4) was written first and
rejected: red at the baseline, it also named `approval_guard`, `domain_check`, `parse_digest`,
`hook_mode` and eleven grade-3 helpers that SC-03 forbids touching (ledger D-03).

## Per SC

| SC | red | green |
|---|---|---|
| SC-01 | the lock above, 3 FAIL at `35c39f02` | `ALL PASS` at the pin; plan.yaml verify's grade assertion over every extracted function exits 0 at the pin |
| SC-02 | — (a byte-identity criterion has no red form; the receipt is the comparison) | 11/11 suites identical at the clean pin checkout |
| SC-03 | — (inspection) | `git diff 35c39f02..e2b580a6 --stat`: three production files, one test suite (two mutant anchors, D-01/D-02), one new unit suite; comment-line multiset per region equal to the baseline's plus the FEAT-66-marked lines (ledger D-08 and the `SHAPE_RULES` table comment) |
| SC-04 | — (inspection) | this file, `clean-pin-byte-receipts.md`, `build-divergences.md`, all committed after `e2b580a6` |
