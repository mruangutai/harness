# FEAT-66 — red-first receipts

Committed AFTER the implementation pin `f882dc3e` (production bytes as at `e2b580a6`; validate c0's test-only fixes on top) and not claimed to exist inside it. The baseline is
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

The lock is the plan's own inline grade assertion — T-01's `verify:` block's `python3 -c` line —
which grades the three retained drivers plus every function absent from the baseline's pre-image and
exits 1 when any is below bar 4 (grade 2 excepted). No permanent test file carries it (validate c0
MF-03; a `tests/unit/test-driver-grades.py` was written at `abe0d43a` and deleted at `f882dc3e`).

Run at the baseline tree (`35c39f02`), the assertion is red: the three retained drivers grade 1
(`shape_problems` cyc 135 / cog 356 / abc 320.6; `validate` 124 / 244 / 251.0; `apply_merge`
59 / 136 / 162.9). Run at the pin it is green. Both runs, verbatim with exit statuses, are in
`clean-pin-byte-receipts.md` ("SC-01" sections), taken in clean detached checkouts.

## Per SC

| SC | red | green |
|---|---|---|
| SC-01 | the inline assertion exits 1 at `35c39f02` (three drivers grade 1) | the same assertion exits 0 at the pin |
| SC-02 | — (byte identity has no red form; the baseline-vs-pin comparison is its fail-first equivalent by operator ruling, BRIEF SC-02) | 11/11 suites identical at the clean pin checkout after normalising the running checkout's own path (D-09) |
| SC-03 | — (inspection) | `git diff 35c39f02..e2b580a6 --stat`: three production files, one test suite (two mutant anchors, D-01/D-02), comment-line multiset per region equal to the baseline's plus the FEAT-66-marked lines (ledger D-08 and the `SHAPE_RULES` table comment) |
| SC-04 | — (inspection) | this file, `clean-pin-byte-receipts.md`, `build-divergences.md`, all committed after `e2b580a6` |
