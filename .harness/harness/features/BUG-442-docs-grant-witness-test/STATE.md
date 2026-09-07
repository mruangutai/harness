# STATE

## Current

- feature: BUG-442-docs-grant-witness-test
- run: .harness/harness/features/BUG-442-docs-grant-witness-test/runs/2026-09-07-04-product/state.yaml
- squad: none
- status: awaiting-user

Plan phase COMPLETE and the plan is signature-ready. `plan.yaml` carries station `plan`,
one task (T-01), three decisions, and the cycle-0 `panel:` record. `approval.status` is
`pending` in both plan.yaml and BRIEF.md — only the main session signs.

Panel outcome: PASS, `severity_max: med`, `must_fix` empty. Both readers RAN — no skips.
Three advisory findings (2 med, 1 low) were folded into T-01 before the plan was closed;
the fourth (info, the hand-pinned census) is recorded `open` as a deliberate non-action.
`cycles_used: 0` — every run passed first-pass, no send-backs.

Log — station transitions:
- 2026-09-07: backlog -> plan. Feature dir instantiated; BRIEF.md and plan.yaml drafted;
  panel run at cycle 0; handoff written to notes/handoff-plan.md. Awaiting signature.

## Open Questions

- Harness defect, non-blocking, for the harness owner: a handoff note's `plan-task:` and
  `brief-sc:` authority pointers CANNOT resolve from inside a git worktree.
  `handoff_done_when.py:359-364` matches FEATURE_RE against a worktree-relative `rel_path`
  and then joins the result to the MAIN checkout root, so it looked for
  `<main>/.harness/harness/features/BUG-442-.../plan.yaml`, which does not exist — the
  feature dir lives only in the worktree. Observed: the Write was denied with
  "cannot resolve target: No such file or directory". Worked around by using the
  explicit-path `approval:` form, which joins its own path to root and therefore resolves.
  Every worktree-based flow hits this, so the two most natural authority types are
  effectively unusable wherever the harness actually runs its features.
