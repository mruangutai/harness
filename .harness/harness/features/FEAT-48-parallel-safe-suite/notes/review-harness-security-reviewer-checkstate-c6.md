# check-state.sh gate-reachability probe — FEAT-48 cycle 6

## Command run
```
cd /Users/molchairuangutai/GitHub/harness/.claude/worktrees/harness/FEAT-48-parallel-safe-suite && \
bash .claude/skills/harness/bin/check-state.sh; echo "EXIT=$?"
```
`check-state.sh` takes no CLI arguments — it self-resolves its harness root via
`harness_boundary.resolve_root()` from its own directory (never cwd/env) and then sweeps the
**entire repo tree**, not a single feature. It refused to run only if the root is unresolvable
(`exit 2`); here it resolved and ran to completion.

Full verbatim stdout/stderr captured at `artifact://3018` (784 lines; this note quotes the parts
that answer the three questions).

**Exit code: `EXIT=1`.**

## a. Is `runs/2026-09-01-08-validator/digest.md` still named as a lead-digest-contract violation?

**No.** Grepped the full captured output for `digest\.md is|INV-15|lead digest contract` and for
`2026-09-01-08-validator` — zero matches on every pattern. The INV-15 check (source at
`check-state.sh:1330-1444`, DEC-156) is the only lead-digest-contract invariant in this script; its
failure line reads `"{run}: run is complete but digest.md is missing…"` or `"…fails the lead digest
contract — a successor reads this file, not the transcript (DEC-156)."` Neither string, nor any
`FEAT-48` line referencing `digest.md`, appears anywhere in the run.

## b. Any OTHER `runs/**/digest.md` named for the same reason?

**None.** The same search across the entire 784-line output returns zero INV-15 hits of any kind,
for any feature. INV-15 is silent this run — every complete lead-hosted run in the tree currently
carries a passing digest.

## c. Overall exit code and remaining reasons

Exit code **1** (`bad` list non-empty; per `check-state.sh:2394`, `sys.exit(1 if bad else 0)` —
`note`/warn lines never affect the exit code). Four `VIOLATION` lines total, **none run-digest
related**:

1. `VIOLATION  .harness/harness/features/FEAT-48-parallel-safe-suite/BRIEF.md is NOT approved — halt that flow and surface to the user.`
   — **unrelated** (plan-approval gate, not a run digest).
2. `VIOLATION  FEAT-51-claude-code-lifecycle-safety: status is 'done' but notes/handoff-validate.md is missing — the validate seam was crossed without a handoff; the successor is on the disk-only path (DEC-159).`
   — **unrelated** (INV-17 handoff-note check on a different feature, not INV-15/digest.md).
3. `VIOLATION  INV-29: /Users/molchairuangutai/GitHub/harness/.claude/worktrees/harness/FEAT-51-claude-code-lifecycle-safety is a standing worktree whose feature FEAT-51-claude-code-lifecycle-safety reached a terminal state on the default branch. …`
   — **unrelated** (stale-worktree check, different feature).
4. `VIOLATION  INV-26 FEAT-48-parallel-safe-suite: tasks are in flight or finished (the plan has tasks under way) but feature.json records no mirrored issues, so the board cannot be telling the truth about this feature. The mirror never ran — run `gh-sync.py open` for it.`
   — **unrelated** (board-mirror check on FEAT-48, but a different invariant number/subject; not the digest contract).

All remaining `note`-level lines (INV-23 size budgets, INV-28 PR linkage, INV-32 panel-era grading,
pruned-run-dir notices, etc.) are warnings only and do not gate the exit code; none concerns
`runs/**/digest.md`.

## Conclusion
The repair is reachable by the gate: `check-state.sh` no longer flags
`runs/2026-09-01-08-validator/digest.md`, and no other run digest is flagged for the lead-digest
contract. The gate's exit-1 status is driven entirely by four pre-existing, unrelated violations.
