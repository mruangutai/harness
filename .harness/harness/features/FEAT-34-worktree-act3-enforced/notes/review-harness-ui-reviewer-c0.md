# UI Review — FEAT-34, review_sha 513c4a46e34cbe327d96922c01cebdd18e85d62e

**Out of scope.** File-extension census of all 41 changed files (`git diff --name-only
9165162..513c4a4`) returns zero hits for html/css/scss/tsx/jsx/vue/svelte/less, and zero
DESIGN.md in the diff. Surface is shell (`check-state.sh`, `post-merge-sweep.sh`,
`hooks/post-merge`), Python (`worktree_terminal.py`, three `test-*.py`), one SKILL.md, JSON
config, and feature-tracking markdown (BRIEF/STATE/plan.yaml/notes/observations) — none of
which is a rendered or user-facing markup/style/component surface this role audits.

Checked the one adjacent surface the dispatch named as worth eyes: the INV-29/INV-30 refusal
text added to `check-state.sh` and the `post-merge-sweep.sh` stdout messages. Both are
plain-prose, consistently prefixed (`INV-29:` / `INV-30:` / `post-merge-sweep:`), state the
finding then the remedy command in the same sentence structure the file already uses for
sibling invariants (INV-25, INV-26). No unambiguous accessibility or comprehensibility defect
found in this pass — but this is terminal output read by a human waiting on `git merge` or a
commit, not UI, and is not this role's mandate to grade for fidelity or tone.
