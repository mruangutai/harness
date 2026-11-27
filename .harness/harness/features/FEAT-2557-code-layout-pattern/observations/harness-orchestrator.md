# Observations — harness-orchestrator — FEAT-2557-code-layout-pattern

- 2026-11-27: A task deleted from a signed plan (delete-items) leaves its sub-issue receipt in feature.json github; gh-sync.py status plan re-places source, parent and surviving task cards only, and no gh-sync verb closes or detaches the dropped cards, so INV-26 reports each as "no card placement follows".
- 2026-11-27: check-state.py run from the control-plane bin with cwd in the feature worktree graded the main corpus and showed nothing for this feature at exit 0; the worktree's own copy graded it.
- 2026-11-27: plan-merge.py amend on a signed task, run by pm inside a product run, ledgered its amendment judgements as by: main-session.
