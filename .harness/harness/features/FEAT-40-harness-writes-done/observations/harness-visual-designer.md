# Observations - harness-visual-designer

- 2026-08-25: FEAT-40 — post-merge-sweep.sh:192 greps ship's combined output for the literal `gh-sync: SKIP`; any new gh-sync line carrying that substring silently changes worktree-removal behaviour. Check that gate before pinning any new output string in gh-sync.py.
- 2026-08-25: FEAT-40 — a refusal that names one sanctioned command can route the operator to the WRONG one. The plan named only `abandon` (closes not_planned + labels abandoned) for a hand-typed `gh issue close`, whose likeliest intent is "this is finished". Route refusals by intent, not by naming the single alternative.
