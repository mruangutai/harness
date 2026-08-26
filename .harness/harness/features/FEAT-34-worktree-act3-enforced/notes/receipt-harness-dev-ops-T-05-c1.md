# Receipt — harness-dev-ops — T-05 — c1

## Conclusion
Both enumerations updated. `test-worktree-terminal.py` and `test-post-merge-sweep.py` are now
registered in the integration kind and were actually executed by `--kind integration`, all their
own cases PASS. `--check-kinds` confirms the two lists agree. One pre-existing, unrelated failure
surfaced in `test-validate-digest.py` (not my file, not caused by this edit) — named below, not
fixed, per scope.

## CLAUDE_PROJECT_DIR
Unset in the shell before invocation (`echo "$CLAUDE_PROJECT_DIR"` printed empty). Since
`run-unit-tests.sh:3` falls back to `$(pwd)`, an unset var with cwd = worktree root would have
resolved correctly on its own, but per the dispatch instructions I made it unambiguous and prefixed
every invocation explicitly:
`CLAUDE_PROJECT_DIR=/Users/molchairuangutai/GitHub/harness/.claude/worktrees/harness/FEAT-34-worktree-act3-enforced`

## Before/after counts (re-derived, not trusted from the dispatch)
- `.harness/harness.json` `test_kinds.integration.detect`: 23 pipe-separated entries before
  (measured directly via `python3 -c` split-count) -> 25 after (22 literal script paths + 2 new +
  1 glob).
- `run-unit-tests.sh` `INTEGRATION_SCRIPTS`: 22 entries before -> 24 after (grep-counted quoted
  tokens in the array literal).
- Matches the plan's stated before-counts exactly; no disagreement with the dispatch's numbers.

## 1. Mandated verify (verbatim command, actual output)
```
bash .claude/skills/harness/bin/run-unit-tests.sh integration 2>&1 | grep -c "KIND-DRIFT\|MISCONFIGURED"
```
Output: `0`

As flagged in the dispatch, this is vacuous by itself (positional `integration` falls to the
usage/exit-2 branch before either checker runs) — reported per contract, not treated as proof.

## 2. `--check-kinds` (the real drift/cross-check evidence)
```
$ CLAUDE_PROJECT_DIR=.../FEAT-34-worktree-act3-enforced bash .claude/skills/harness/bin/run-unit-tests.sh --check-kinds
check-kinds: the script arrays and test_kinds.integration.detect agree.
exit: 0
```
Positive confirmation line present — the two enumerations agree.

## 3. `--kind integration` (actually executes the suite, including both new files)
Ran to completion (took >120s, backgrounded and awaited). Both new files ran and every one of
their own cases passed:
```
PASS: (a) landed Done, exact name -> terminal
... (18 cases)
PASS test-worktree-terminal.py
PASS: --dry-run exits 0
... (many cases, including RED-PROOF self-checks, all PASS)
EXIT=0
PASS test-post-merge-sweep.py
```
Overall wrapper `exit: 1` — because of the pre-existing failure below, unrelated to T-05's files.

### Pre-existing failure, named, not mine to fix
`test-validate-digest.py` — 6 of its hook-route cases FAIL:
- `F1.1 quoted headline text must not satisfy the verdict lookup`
- `F1.2 multi-line inline members list is followed to its close`
- `F1.4 empty members against a nonzero steps_run is rejected`
- `DEC-156: narrative digest.md with no contract block is exit 2`
- `DEC-156: digest.md carrying the same valid block is exit 0`
- `DEC-156: missing file fails OPEN with the INV-15 pointer, not a block`

All six fail with the same symptom: the hook under test returned
`check-digest: BLOCKED - returned with children in flight (harness-eng-lead)` instead of the
expected fixture-specific message — i.e. this live session's own real inflight-registry claim
(harness-dev-ops dispatched by harness-eng-lead, started 2026-08-24T22:22:56) appears to leak into
what should be an isolated hook-test fixture. This is environmental/pre-existing, has nothing to
do with `.harness/harness.json` or `run-unit-tests.sh`, and I did not touch
`test-validate-digest.py`. Not fixed — out of scope and not one of my two files.

## Files touched (exactly the two dispatched, plus this receipt)
- `.harness/harness.json`
- `.claude/skills/harness/bin/run-unit-tests.sh`
