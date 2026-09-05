# Handoff — BUG-1302-suite-layout-fail-closed, validate → ship — written at 1361c0a1, seq-2

## Next

Return to the main session with `notes/ship-review-2026-09-05-validate.md` for the operator's ship
decision. There is no squad step left: validation PASSED and every remaining act — merge,
`gh-sync.py ship --body-file`, filing the unstruck backlog rows, letting `post-merge` remove this
worktree — is main-session or operator work under DEC-174. Run `gh-sync.py ship` from the MAIN
checkout; it refuses at exit 1 when the feature dir resolves inside `.claude/worktrees/`.

## Trust

- The review panel PASSED at the pin with `must_fix: []`, `severity_max: low`; all four seats ran
  and none was skipped — runs/2026-09-05-6-validator/digest.md — verified-at ac8dd671
- All ten success criteria are met; SC-06 moved partial → met on qa's mutation transcripts —
  runs/2026-09-05-7-product/digest.md — verified-at ac8dd671
- Each of the five B-rows discriminates the defect it names, mutation-proven in a disposable probe
  worktree that was cleanly removed — notes/qa-2026-09-05-6.md §3–4 — verified-at ac8dd671
- Both DEC-174 files are byte-identical to the pin; no member edited either —
  `git diff ac8dd671 -- tests/` is empty — verified-at ac8dd671
- The suite discovers MORE than before, not less: `check(` sites 39 → 48, no named check lost —
  orchestrator-tier count over both blobs — verified-at ac8dd671
- SC-02/SC-04's structural pins genuinely separate base from fix: any() 2→1, `"*?["` 2→1, `".."`
  2→1 — orchestrator-tier AST census, base c369fb1 vs pin — verified-at ac8dd671
- plan.yaml `panel.readers` carries all three INV-32 readers with `approval:` and `status:`
  byte-unchanged; the re-pin covers it — `git diff ac8dd671 d5dbb9da -- tests/ .claude/` is empty
  — verified-at 1361c0a1
- `check-state.sh` exits 0 with ZERO violations tree-wide — run at the orchestrator tier from this
  worktree, which is the only checkout whose working tree holds this feature — verified-at 1361c0a1
- runs/2026-09-05-1-eng/digest.md now satisfies the DEC-156 contract; the lead's original 6339 bytes
  are preserved byte-identically — `validate-digest.py lead` exits 0, head -c 6339 md5
  fb265e2b3feb6eb2e5bb9267aaee279f — verified-at 1361c0a1

## Dead ends

- Editing either test file to produce more red evidence — DEC-174 reserves both to the main session,
  and qa already produced the evidence out-of-tree — BRIEF.md ## Constraints — verified-at ac8dd671
- REPLACING a recorded run digest — check-domain refuses it and permits only an EXTEND, so a
  malformed digest is repaired by appending, never by rewriting —
  check-domain.sh refusal observed this run — verified-at 1361c0a1
- `brief-sc:` and `plan-task:` authority pointers from inside a worktree — they resolve against the
  main checkout, where this feature dir does not exist; briefing row B-4 — verified-at 1361c0a1
- Re-running the plan panel — it ran at cycle 1 and all four PF- findings are recorded `resolved`;
  approval was never reset — plan.yaml `panel.findings` — verified-at ac8dd671
- Removing this worktree from inside it — `git worktree remove` exits 0 from within and destroys the
  working directory; the `post-merge` hook owns it — DEC-95/DEC-193 — verified-at ac8dd671

## Working set

- .harness/harness/features/BUG-1302-suite-layout-fail-closed/notes/ship-review-2026-09-05-validate.md
- .harness/harness/features/BUG-1302-suite-layout-fail-closed/feature.json
- .harness/harness/features/BUG-1302-suite-layout-fail-closed/runs/2026-09-05-6-validator/digest.md
- .harness/harness/features/BUG-1302-suite-layout-fail-closed/notes/qa-2026-09-05-6.md
- .harness/harness/features/BUG-1302-suite-layout-fail-closed/BRIEF.md

## Done when

Scope: the operator has taken the ship decision on the validated pin
Authority: approval:.claude/worktrees/harness/BUG-1302-suite-layout-fail-closed/.harness/harness/features/BUG-1302-suite-layout-fail-closed/notes/ship-review-2026-09-05-validate.md#Next steps, and who owns them
