# Handoff — FEAT-45-adversarial-plan-panel, validate → ship — written at c745d3a, seq-6

Supersedes the seq-5 note, whose `## Next` was the main-session-direct fix of M1/M2/M3. Those are
fixed and independently confirmed closed. Panel cycle 1 returns PASS at `severity_max: med`, which
under `gates.review: advisory_unless_high` does NOT gate. Validate is complete.

## Next

Ship-phase entry, which is the main session's own: present the CEO briefing and take the operator's
ship decision. No fix cycle is owed and no `must_fix` is outstanding. Before signature, the residual
advisory findings below need a keep-or-strike ruling — M4 in particular is a RATCHET and is cheapest
to fix now. `gh-sync.py ship` and the merge remain user-gated.

## Trust

- **The recorded `review_sha` was FABRICATED and I corrected it.** feature.json held
  `c745d3a61f1049e5325854618511544b10f68753`, which resolves to no object —
  `git rev-parse --verify` fails on it. The real commit is
  `c745d3a07c2accd8395c9df7a25d911d40dc2c09`, same 7-char prefix, invented tail. Three reviewers hit
  it independently. My own cycle-1 verification used the PREFIX, so it read the right tree and its
  conclusions stand — verified-at c745d3a
- The cycle-0 pin `d0ebbe6f361d8084176bee27202b1a3b9e005947` WAS genuine; it resolves. Only the
  cycle-1 value was wrong, so this is a one-off transcription, not a standing pattern — verified-at c745d3a
- **M1 CLOSED.** `check-state.sh:213` is now `if severity not in {"info","low","med"} ...` — an
  allow-list, so absent (`""`) and YAML null (`"none"`) both gate. **I proved the fixture RED-capable
  myself**: reverting that one line to the old deny-list makes `case_inv32_unrated_severity_fails_closed`
  print FAIL and the suite exit 1. Probe reverted; file byte-identical to the pin — verified-at c745d3a
- **M3 CLOSED.** `case_inv32_unrated_severity_fails_closed` covers all three directions in one
  fixture — `severity: "unrated"`, an absent key, and `severity: None` — verified-at c745d3a
- **M2 CLOSED.** I graded the file directly: `case_inv32` is grade 4 (cyclomatic 28->2, ABC
  95.1->11.0) and all eleven `_inv32_*` functions grade 3-5, zero below the bar — verified-at c745d3a
- **The allow-list widening gates nothing spuriously.** `ui` censused 10 sources and found the
  allow-list's complement is exactly the old deny-list `{high, critical, unrated}` — membership did
  not change. `security` fired 17 hostile severity values and all gated — verified-at c745d3a
- Full suite at the pin: runner exit 0, zero `^FAIL ` lines, counted not tail-read — verified-at c745d3a

## Dead ends

- Do NOT trust `code-grade.py`'s exit status on a `--base/--head` range. It raises an unhandled
  RuntimeError on any path NEW in the diff and exits 1 with zero `RESULT: FAIL` lines, so it reddens
  a clean range and would mask a real failure behind a crash. Grade files directly — verified-at c745d3a
- Do NOT treat the c1 panel's "the two stray main-checkout notes are byte-identical duplicates, delete
  them" as accurate. Only ONE stray existed and it DIFFERED from the worktree copy; it was MOVED to
  `review-harness-code-reviewer-c1-mainwrite.md`, not deleted — verified-at c745d3a
- Do NOT read `severity_max: med` as a gate. `gates.review` is `advisory_unless_high`; med is advisory
- Do NOT re-run the panel for the advisory items. They are ship-decision material, not fix-cycle
  material, and cycle 1 already assessed and recorded each

## Working set

- `.harness/harness/features/FEAT-45-adversarial-plan-panel/feature.json` — corrected `review_sha`
- `.harness/harness/features/FEAT-45-adversarial-plan-panel/notes/review-harness-code-reviewer-c1.md`
- `.harness/harness/features/FEAT-45-adversarial-plan-panel/notes/review-harness-security-reviewer-c1.md`
- `.harness/harness/features/FEAT-45-adversarial-plan-panel/BRIEF.md` — SC-01..SC-17 for the goal-check
- `.harness/harness/features/FEAT-45-adversarial-plan-panel/STATE.md`
