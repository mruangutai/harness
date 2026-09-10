# Handoff — FEAT-58-corpus-outside-worktree, plan → signature — written at abff2a84, seq-1

## Next

Present the plan for the operator's ONE batched signature review (DEC-176). Two decisions must
come back before any task text moves: panel Q1 (keep or cut T-12/D-05's gate-enforced
provider+ref declaration — cutting amends SC-14 and deletes T-12) and the disposition of the
high panel finding PF-5945852660e0bd21e2b5aabb8cd48383 (T-10's sequencing plus the
sibling-branch window), which is resolved by a directed fix or overruled by
`sign-approval --overrule`, never accepted by an agent. Do not dispatch a pre-signature fix.

## Trust

- plan.yaml is final and internally consistent: 16 tasks, 12 decisions, all 11 REQ and 14 SC traced, `depends_on` acyclic and resolving — read via harness_yaml.load_plan — verified-at abff2a84
- `check-plan-routes.py` exits 0, 0 violations, 10 informational DEVIATION lines that are DEC-174's main-session-direct lanes — ran by the orchestrator — verified-at abff2a84
- `panel` mapping is on the record: cycle 1, both readers `ran`, severity_max high, 7 findings open — plan.yaml top-level `panel` key — verified-at abff2a84
- `.agents/skills` is a SYMLINK to `../.claude/skills`; one inode, git tracks only the `.claude/` spelling, hooks fire via `${CLAUDE_PROJECT_DIR}/.claude/` — `os.readlink` + `git ls-files -s` — verified-at abff2a84
- The high finding's premise about hook resolution (each worktree runs its own branch's gate copy) is the panel's reading of `.claude/settings.json`, corroborated by grep, NOT executed — runs/planpanel-validator/digest.md adequacy_notes — UNVERIFIED
- T-03's declared 21 enumeration sites in check-state.sh is an inherited hand count; ≥17 confirmed by one pattern — notes/receipt-harness-backend-dev-arch-eng.md — UNVERIFIED

## Dead ends

- Reflink/clonefile as the mechanism: measured 124× cheaper but leaves the files logically present, so it fails the bedrock rule — grilling-worktree-corpus-2026-09-09.md "Out of scope" — verified-at abff2a84
- Any `du`- or `df`-based byte criterion: both are satisfied by the excluded clonefile mechanism, which is why every footprint criterion counts entries and files — BRIEF.md SC section — verified-at abff2a84
- One-frame `provider="path"` for relocated sweeps: path enumeration has no independent expected set, so a mistargeted sparsify reporting "1 of 1" never refuses — runs/framefix-eng/digest.md F-1 — verified-at abff2a84
- `corpus_open` as a shared read seam: zero callers survive D-11's relocation — runs/planfix-eng/digest.md R-3 — verified-at abff2a84
- Executing any of this through a team run: enforcement-layer changes are made directly — DECISIONS.md DEC-174 — verified-at abff2a84

## Working set

- .harness/harness/features/FEAT-58-corpus-outside-worktree/plan.yaml
- .harness/harness/features/FEAT-58-corpus-outside-worktree/BRIEF.md
- .harness/harness/features/FEAT-58-corpus-outside-worktree/runs/planpanel-validator/digest.md
- .harness/harness/features/FEAT-58-corpus-outside-worktree/notes/research-FEAT-58-goalcheck-plan-c1.md
- .harness/notes/grilling-worktree-corpus-2026-09-09.md (main checkout, untracked, absent from this worktree)

## Done when

Scope: the operator's batched signature review returns a signature or a directed fix set
Authority: approval:.harness/harness/features/FEAT-58-corpus-outside-worktree/BRIEF.md#Approval
