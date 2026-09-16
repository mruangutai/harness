# Handoff — FEAT-55, build → blocked (two operator rulings) — written at ef591a53, seq-9

## Next

Do NOT re-dispatch the build. Nine of twelve tasks are done; the remaining three are code-complete
and blocked on TWO plan-level operator rulings. Read `notes/ship-review-2026-09-05-01-eng.md`, carry
F-01 and F-02 up, then route: F-01 is a `files:` amendment (pm, or main-session-direct); F-02 is a
criterion that CANNOT be met as written, so it is pm's re-plan under operator approval, never a fix
cycle. Then qa, then SIMPLIFY, then pin `review_sha`. The cycle budget is EXHAUSTED at 11 of 10 and
a raise is an operator decision (DEC-157). Cited: plan.yaml T-04/T-06/T-08, STATE.md `## Open
Questions`.

## Trust

- Both approval fragments signed — plan.yaml :4-29, BRIEF.md :207-210 — verified-at ef591a53
- Pinned row present in BOTH files, identical, 394 chars, one physical line, guard green —
  `tests/unit/test-issue-types-pin.py` exit 0, DECISIONS.md:6103 — verified-at ef591a53
- The schema is the WHOLE blocker: a reverted probe adding `typed` to the github and factory objects
  turned all FIVE affected suites green, exit 0, zero FAIL each — briefing F-01 table — verified-at
  ef591a53
- Probe restored byte-identically — `cmp` equal, `git status --porcelain` empty on that path, file
  absent from the commit — verified-at ef591a53
- `gh api` has no `--repo` flag — gh 2.92.0 answers `unknown flag: --repo` — verified-at ef591a53
- The two red factory suites are pre-existing control tests, same root cause —
  `MergeRefusal(11): undeclared key 'typed' at /factory` — verified-at ef591a53
- The live probe reports CAPABILITY ABSENT for mruangutai/harness, so SC-10 has no enabled target —
  briefing F-03 — verified-at ef591a53
- The three blocked tasks are behaviourally COMPLETE: the lead's members proved that under
  in-process overrides and I did not re-derive it per task — UNVERIFIED

## Dead ends

- Do not run qa: the only blocking gate would fail on three unverifiable tasks and DEC-174 leaves its
  `loop_back` no legal owner — harness.json `gates.qa_gate` — verified-at ef591a53
- Do not pin `review_sha`: the Building → Review seam was never reached — INV-6 — verified-at ef591a53
- Do not mirror to GitHub: that belongs at the validate seam — references/github-mirror.md —
  verified-at ef591a53
- Do not use `set-task-station` here: the tasks carry no `status:` key, exit 3 on all twelve —
  STATE.md Q5 — verified-at ef591a53
- Do not read a captured suite artifact for ABSENCE of failure: a truncated capture showed zero FAIL
  while the suite exited 1 on four files — STATE.md Q6 — verified-at ef591a53
- Do not fix F-02 by adjusting the test double: the double is what hid it — briefing F-02 —
  verified-at ef591a53

## Working set

- .harness/harness/features/FEAT-55-issue-types-created-work/notes/ship-review-2026-09-05-01-eng.md
- .harness/harness/features/FEAT-55-issue-types-created-work/runs/2026-09-05-01-eng/digest.md
- .claude/skills/harness/bin/feature-schema.json
- .claude/skills/harness/bin/gh-sync.py
- tests/integration/test-gh-sync.py

## Done when

Scope: rule F-01 and F-02 so T-04, T-06 and T-08 verify
Authority: finding:.claude/worktrees/harness/FEAT-55-issue-types-created-work/.harness/harness/features/FEAT-55-issue-types-created-work/notes/ship-review-2026-09-05-01-eng.md#F-01
Authority: finding:.claude/worktrees/harness/FEAT-55-issue-types-created-work/.harness/harness/features/FEAT-55-issue-types-created-work/notes/ship-review-2026-09-05-01-eng.md#F-02
