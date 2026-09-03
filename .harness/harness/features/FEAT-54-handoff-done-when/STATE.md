# STATE

## Current

- feature: FEAT-54-handoff-done-when
- run: .harness/harness/features/FEAT-54-handoff-done-when/runs/2026-09-03-goalcheck-validate-c6-product/digest.md
- squad: product — goal-check PASS, UAT written
- status: review (plan.yaml `status: review`), validate phase COMPLETE, awaiting operator SC-10 UAT

Validate is done. The c6 panel returned PASS with `must_fix: []` over pinned `dd55b357`, all four
readers ran, and code review Stage 2 was entered for the first time in this feature — every earlier
cycle stopped at a failing Stage 1, so no quality clearance existed at any commit until now. It
cleared 90/90 on the Python risk grade. The product goal-check then met 14 of 14 non-UAT success
criteria.

Both c5 blockers are closed. F-04/SC-04 was external: I re-ran the exact repository-root
`bash .claude/skills/harness/bin/check-state.sh` myself at wake — exit 0, 478 lines, zero
refusal/fail lines, zero INV-29, zero lines naming `Done when` — and QA re-measured it
independently, then pm re-derived it in the worktree where this feature's own notes actually exist
(812 lines, 145-note corpus, baseline 141 with zero FEAT-54). F-11 was closed by a hand-applied
semantic test over all three handoff notes, including `handoff-validate.md`, which c5 never scoped.

Pin reconciled per INV-6: c5 graded `4690f724`, the F-11 repair landed in `dd55b357`, and the code
diff between them outside this feature's directory is empty — so c5's verdicts carried forward but
the repaired bytes still needed a graded pin. `review_sha` is `dd55b357`, committed at `1e3cc982`.

SC-10 is the sole open criterion and is `verify: uat` — the operator's judgment alone. Its
four-judgment script is at `notes/uat-FEAT-54-SC-10.md`. The CEO briefing is written and rendered at
`notes/ship-review-2026-09-03-review-c6-validator.md`, carrying seven proposed backlog rows.

Two residuals are worth naming here because both are gates that can pass without looking. VL-F-01:
the shipped gate cannot detect the F-11 defect class, since the old defective pointer resolved clean
too. B-2, which I measured myself in four arms: `check-domain.sh` exits 0 on a blank-`Scope:` note
when the claimed path is relative and cwd is outside the project, caused by `os.path.abspath(path)`
resolving against cwd rather than the located root; `CLAUDE_PROJECT_DIR` does not change it. Latent
in production, where the hook's cwd is the project root. Both remedies edit the DEC-174
main-session-direct gate tree, so neither is this feature's to execute.

Cycles used: 21 of 30; both runs this session used zero send-backs, so nothing was added. Runs stand
at 48 against the informational budget of 20 — over by more than double, and the honest read is in
the briefing: the c4/c5/c6 sequence earned its place, the four pre-signature plan panels are a
weaker story.

## Open Questions

- Q1 (blocking the ship decision): SC-10 is unrun and only the operator can close it —
  `notes/uat-FEAT-54-SC-10.md`, about 25 minutes, four separate judgments.
- Q2 (non-blocking): whether SC-04's clause naming `notes/review-<reviewer>-*.md` as the audit
  location is discharged by the run being recorded in `notes/qa-c6.md` and the goal-check note
  instead. Substance recorded twice; only the filename differs. My read is discharged.
