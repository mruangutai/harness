# Handoff — FEAT-17-guard-boundaries, validate → operator fixes — written at c6a28bd, seq-3

## Next

STOP AND HAND THE OPERATOR THE FIX LIST — nothing here is dispatchable. Every surface named is a
DEC-174 carve-out file or `harness_boundary.py`, so the operator edits directly. Panel's fix ORDER is
load-bearing and is its recommendation, not mine: decide F-C's shape first (it changes which paths
reach `worktree_owner`, so it changes what F-A's tests must assert), then F-A (it changes the return
contract; F-E and half of F-D fold into it), then F-B (one line), and wrap `domain_check()` LAST —
wrapping it earlier masks the exit codes you would be testing. Re-run both validator runs after.

## Trust

- qa PASS, `matrix_ok: true`, `must_fix: []`, severity med; panel FAIL, severity high, 3 must_fix — runs/2026-08-12-09-qa-validator/digest.md and runs/2026-08-12-09-panel-validator/digest.md — verified-at c6a28bd
- Both runs examined c6a28bd and confirmed the pin themselves — each digest reports the SHA it read — verified-at c6a28bd
- F-A is real: three `return None` paths in worktree_owner and every caller reads None as not-a-worktree — I read harness_boundary.py:374-400 at source — verified-at c6a28bd
- F-B is real and is exit 0, not exit 1: `except Exception: _wt_seg = None` then `if _wt_seg:` skips all of INV-25 with no bad and no warn — I read check-state.sh:960-980 at source — verified-at c6a28bd
- The two post-goal-check SC-07 cases landed and are honest; the Bash one records that TWO rules independently grant it and so discriminates neither alone — I read the diff 2e02cfc..c6a28bd — verified-at c6a28bd
- F-C's three changed cells rest on the panel's executed before/after with a malformed fleet.yaml — I did NOT re-run that probe — UNVERIFIED by me
- classify's `shared` outcome is unreachable, making bash-write-guard.sh:571-577 dead — qa's analysis, three separate guards cited — UNVERIFIED by me
- The suite's green status at c6a28bd rests on qa's run; the panel ran no tests and said so — UNVERIFIED by the panel

## Dead ends

- Do NOT route any of F-A/F-B/F-C to a lead — all are DEC-174 carve-out files plus harness_boundary.py; assessment was dispatchable, changes are not — CLAUDE.md carve-out, verified-at c6a28bd
- Do NOT file "add a Bash shared-path test" for Q3 — the branch is unreachable, so the test must fail against correct code — qa digest adequacy notes, UNVERIFIED by me
- Do NOT treat the security reviewer's corrupt-then-write exploit story as live — the lead falsified it: the write to `<sibling>/.git` is itself refused at bash-write-guard.sh:479 — panel digest, UNVERIFIED by me
- Do NOT read qa's PASS as coverage of this diff by `--kind unit` — that kind ran 12 unrelated scripts; only `integration` touched the changed code — qa digest, verified-at c6a28bd

## Working set

- .harness/features/FEAT-17-guard-boundaries/runs/2026-08-12-09-panel-validator/digest.md — the 3 must_fix with anchors
- .harness/features/FEAT-17-guard-boundaries/runs/2026-08-12-09-qa-validator/digest.md — matrix accounting and adequacy notes
- .harness/features/FEAT-17-guard-boundaries/notes/review-harness-security-reviewer-2026-08-12-panel.md — F-A's executed evidence
- .claude/skills/harness/bin/harness_boundary.py:374-400 — F-A's three return-None paths
- .claude/skills/harness/bin/check-state.sh:960-980 — F-B's silent absorb
