# Handoff — FEAT-42 one-root-resolver — validate → Done

## Next

Nothing on this feature. It merged as PR #899 at 2026-08-27T20:35:44Z; #870 and #556 are closed.
Eight residual findings are filed as #891–#898 and are ordinary backlog, not follow-up work owed
here. The two that matter most if anyone picks them up: #898 (the lead digest contract cannot
represent an honest send-back, so recording a corrected mistake reds `check-state.sh`) and #897
(this feature's own id is hardcoded as the copy-paste exemplar in `dispatch-guard.sh:105` and
`harness-zero-micro-management/SKILL.md:30`, so a lead copying the remedy is admitted and routed
to the wrong checkout).

## Trust

- `run-unit-tests.sh --kind all` at 61f0a0e: exit 0, 57 files, 3139 case verdicts, zero failures.
  CI `integration` agreed on the PR, 2m49s.
- The #556 proof is real and is the strong one: the same command from the repository root and from
  `bin/` gives a byte-identical verdict set after normalising tmpdir paths — case-level diff of 0
  lines. Before the fix those two runs disagreed.
- Every test pair added on this feature is mutation-verified with a paired half. The specific
  mutants and what they killed are in `notes/cwd-import-bypass-2026-08-27.md` and in the commit
  messages for 9d12e3a and 61f0a0e.
- All 11 success criteria MET per the goal-check. Read `notes/ship-review-2026-08-27-validate.md`
  section "Where the record is weaker than it looks" before citing SC-01 or SC-09: SC-01's
  presence half is method-sensitive (23 by one count, 14 by a stricter one, floor of 16) and SC-09
  is satisfied by line drift rather than by design.

## Dead ends

- `feature-worktree.py behind` cannot be run from inside the worktree it is asking about: it
  resolves root from the cwd and looks for a nested worktree, exiting 3. Use
  `git rev-list --count HEAD..main` instead.
- `gh issue close` is refused by the close gate. The harness lands a card at Done and lets GitHub
  close the issue — `board-station.py <issue> Done` is the sanctioned path for an untracked ticket.
- The `if override:` → `if True:` mutant named in `test-check-plan-routes.py`'s own comment does
  not grade `case_19b5`: against the current resolver it raises TypeError and crashes ten unrelated
  cases first. The mutant that grades it is dedenting the warning so it fires unconditionally.
- Two panel rows did not reproduce and were deliberately not filed. B-3: `harness_root` is still
  live vocabulary in `SPEC.md` — this feature deleted the function, not the term. B-4: the stale
  exemption it describes is already gone; the scan at `test-check-plan-routes.py:1191-1213` has no
  allowlist at all.

## Working set

- `.claude/skills/harness/bin/harness_boundary.py` — the one resolver.
- `.omp/extensions/harness-hooks.ts` — `gateRoot()` / `gatePath()`, the B-1 fix.
- `.claude/skills/harness/bin/test-no-distribution.py` case 7 — the invariant that catches the next
  gate script added without `python3 -P`.
- `notes/cwd-import-bypass-2026-08-27.md` — the #556 measurement and why the `.py` hooks are exempt.
- `notes/ship-review-2026-08-27-validate.md` — the CEO briefing, with the full 25-row finding list.
