# Orchestrator measurements, part 2 — REQ-08 has FOUR consumers, and the fourth takes the
# shape caps dark. MEASURED, not inferred.

Read this before writing or reviewing the REQ-08 task. Part 1 is
`notes/orchestrator-measurements-plan.md`.

## M-10. The strip is spelled twice, and the second spelling is invisible to the proof that exists
## to catch exactly that

`grep -rn 'WORKTREE_REL_RE|worktrees/\[^/\]' .claude/skills/harness/bin/` returns four sites and no
more:

    harness_boundary.py:37    WORKTREE_REL_RE = compile(escape(WORKTREES_SEGMENT) + "/[^/]+/(.+)$")
    harness_boundary.py:310   the classify() verdict path        (Write and Bash routes)
    check-domain.sh:212       the --resolve path                 (plan-time routing, check-plan-routes)
    check-domain.sh:644       _norm(), an INLINE LITERAL COPY:
                              re.match(r"^\.claude/worktrees/[^/]+/(.+)$", rel)

Site 4 does not reference `WORKTREES_SEGMENT`. Its own docstring calls itself "The one path
normalisation" and it is the second one.

## M-10b. The consequence, measured three ways on the Write route

Payload: `agent_type: harness-orchestrator`, an over-budget `STATE.md` (204 lines against a 120
budget), same repo-relative path, three locations, `CLAUDE_PROJECT_DIR` at the main checkout:

    main checkout        exit 2   "STATE.md: state-file shape (DEC-150)"        SHAPE refusal
    .claude/worktrees/WT1/...     exit 2   "state-file shape (DEC-150)"          SHAPE refusal
    .claude/worktrees/harness/WT1/... exit 2  "may not write ..."                DOMAIN refusal

The third case never reached the shape gate. `_norm` returned
`WT1/.harness/harness/features/.../STATE.md`, which matches none of `RE_FEATURE_JSON`,
`RE_STATE_YAML`, `RE_HANDOFF`, `RE_STATE_MD`, `RE_CLAUDE_MD` (`check-domain.sh:984, 991, 1033` all
normalise through it). **The DEC-150 shape caps are already dark under the two-level layout, and
the domain refusal is what hides it.**

Fix sites 1 to 3 and forget site 4 and the mask lifts with the caps still off — writes succeed,
budgets unenforced, suite green. DEC-193's own evidence records this exact failure once already:
"taking DEC-150's shape caps dark with them on that route."

**Two obligations for the REQ-08 task, both forced by the measurement above:**

1. It names all four sites. Three is a silent regression, not a partial fix.
2. Its `verify:` asserts the SHAPE refusal from inside a two-level worktree by its WORDING, not by
   its exit code. Both refusals exit 2, so an exit-code assertion cannot tell them apart — and after
   the domain half is fixed, the exit-code-only assertion goes green while the caps stay off.

## M-10c. The mutation proof

`test-bash-write-guard.py:489-508` mutates the literal `WORKTREES_SEGMENT = ".claude/worktrees"`
inside a COPIED `harness_boundary.py` and requires both routes to flip 0 to 2. Site 4 hardcodes the
string, so mutating the constant leaves it untouched: the one-implementation proof passes today and
is blind to the second copy. If REQ-08 removes the constant's regex, that proof must keep flipping —
SC-09 — so the task either preserves the mutation surface or replaces the proof with one that flips.

## M-11. One site that looks depth-coupled and is not — leave it alone

`bash-write-guard.sh:545` is `re.match(r"^\.claude/worktrees/", rel)`, DEC-153's blanket allow for
governed agents on the Bash route. Prefix only, no segment count, so it is already depth-agnostic and
correct under the two-level layout. A REQ-08 task that "unifies" it into the new relativizer is
touching a signed carve-out for no behavioural gain.

## M-12. Every existing worktree assertion is a ONE-level fixture

`test-check-domain.py` builds `.claude/worktrees/wt1` and `.claude/worktrees/wt` (lines 1093, 1160,
1465-1482). SC-09 requires these to stay green, so the new relativization must accept BOTH depths —
the one-level shape is not legacy to be replaced, it is the shape every existing assertion uses.
