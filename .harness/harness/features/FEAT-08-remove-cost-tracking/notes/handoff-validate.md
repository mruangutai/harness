# Handoff — FEAT-08-remove-cost-tracking, validate → ship — written at 7d9edde+, seq-3

## Next

STOP. **Three user gates, none of them yours.** The briefing is written and returned:
`notes/ship-review-validate-close.md`. Present it; do not act ahead of it.

1. **MF-1** — two prose deletions in `.claude/commands/harness.md` (`:18`, `:83`). **Main-session
   direct. No agent may write that file** and I proved it with the arbiter, not the config.
2. **SC-05 and SC-06** are red on their own signed wording with correct delivery behind them. Only
   the user can amend a signed criterion, or wave them through.
3. **Merge, and the 21-item backlog.** Anything not on that list dies silently.

Then: `gh-sync.py ship` on acceptance, `/harness-deploy` **before** the queued preload batch.

## Trust

- All twelve tasks DONE, all task issues closed; T-10's five `verify:` clauses re-run by ME, not
  relayed — verified-at `942505e`
- **SC-01 returns exactly the four amended survivors; SC-04's surviving half returns `digest ok`
  exit 0** — both run directly by me — verified-at `00f3e03`
- Panel was FOUR-WIDE, no skips. All four members PASS; the LEAD found three REQ-08 violations they
  all missed. MF-2 and MF-3 FIXED; MF-1 open — verified-at `8958840`
- **13 of 15 SCs met. SC-15 was a REAL failure, was fixed, and pm re-graded it — I never marked it
  met myself** — verified-at the sc15-product digest
- Twelve Expertise files, ALL `check-expertise.sh` clean, re-run by me because no lead holds `Bash`
  — verified-at this session's tip
- Gates: unit 0 (12 scripts), docs 0, state 0 zero violations — all re-run by me — verified-at
  `8958840`
- 21 commits and 33 files in `ae2443d..942505e`; **the panel dispatch said 22 and was wrong** —
  measured
- `cycles_used: 4` of 10. T-10's re-dispatch added ZERO: forward work from a SIGNED amendment is not
  rework — DEC-157
- ALL FOURTEEN run digests pass `validate-digest.py lead` EXCEPT `s2-eng`, which is `status: blocked`
  and therefore exempt — do not "fix" it. Two failed and were sent back to their OWNERS, not patched
  here — verified-at `b496e68`

## Dead ends

- Do NOT re-root `check-state.sh` via `CLAUDE_PROJECT_DIR` to make SC-03 pass — the re-baselining
  the user forbade — source: user ruling
- Do NOT add a replacement fixture for the deleted unknown-key pin. Ruled "add nothing"; filed as
  issue #104 — source: user ruling
- Do NOT raise an amendment for the three panel findings. They violate ALREADY-APPROVED REQ-08, so
  they are fixes, not scope — `BRIEF.md` REQ-08; my ruling, on the record in `feature.yaml`
- Do NOT re-open cycle counting, `max_total_cycles`, or any historical DECISIONS entry — standing
  ruling — `feature.yaml` `pending`
- Do NOT treat `.claude/commands/harness.md:49` as a defect. It is a historical anecdote, not an
  instruction; pm ruled it outside the criterion structurally — `runs/sc15-product/digest.md`
- Do NOT trust an all-green `verify:`. It happened FIVE times this feature: every clause matched
  compound tokens while every defect used the plain word — `PLAN.md` A-3

## Working set

- `.harness/features/FEAT-08-remove-cost-tracking/notes/ship-review-validate-close.md` — the briefing
- `.harness/features/FEAT-08-remove-cost-tracking/feature.yaml` — `sc_status`, `panel_result`, `open_q`
- `.harness/features/FEAT-08-remove-cost-tracking/runs/panel-validator/digest.md` — the three findings
- `.harness/features/FEAT-08-remove-cost-tracking/runs/goalcheck-product/digest.md` — all 15 criteria
- `.harness/logs/2026-08-05.md` — **deliberately NOT committed**: shared main-session state, appended
  by the concurrent flow. Do not hunt for it in the branch
