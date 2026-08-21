# Receipt — harness-documentor — 2026-08-21-03-product (FEAT-30 docs segment)

**BLUF.** `SPEC.md` now documents the delivered worktree CLI, its refusals, the HEAD-move rule and the
union-merge Expertise apply, all anchored to source. **`BUILD.md` was NOT edited** — I hold authority
for it and judged there is no row to retire and nothing to add.

## Files written

- `.harness/harness/docs/SPEC.md` — four hunks:
  1. **Index** (§ table rows 5 and 15) — §5 row names the union-merge apply; §15 row names the
     `feature-worktree.py` lifecycle and the HEAD-move refusal. Cost figures re-estimated against the
     table's own unit, calibrated from HEAD (§2 1539 words → listed 1.3k; §15 934 → 0.9k), giving
     §5 2651 words → 2.2k and §15 1688 → 1.6k.
  2. **§2.3** — one new bullet: `HEAD` is shared mutable state, no governed agent may move it, detail
     in §15.2. Pointer only; the mechanism is documented once.
  3. **§5.3** — new block "The apply is a union merge, not a whole-file write": the `apply` command,
     lock, union semantics, atomic write, and the three refusal exits (6 lock, 7 divergent text,
     8 cap overflow) with the target left byte-identical because both checks precede any write.
  4. **§15.2** — rewritten below the DEC-95 framing: the four subcommands with runnable commands,
     `--repo`'s two forms, the two-segment layout, `list` semantics, the three lifecycle acts,
     `remove`'s two refusals with no force flag, the HEAD-move refusal WITH its allow-list, and a
     residue list updated to say the Expertise concurrency loss is closed while the git-level merge
     conflict is not.

## BUILD.md — resolver output quoted, and the judgement

    $ .claude/skills/harness/bin/check-domain.sh --resolve .harness/harness/docs/BUILD.md
    harness-documentor
    exit=0

(`SPEC.md` resolves the same way.) So the file was mine to edit and I chose not to. Search performed:
`grep -in worktree BUILD.md` returns 4 lines — line 148 (DEC-85 `isolation: worktree` as the
write-safety mechanism, still true), row 25 (DEC-143 shared-workspace dispatch, a different pending
thing), line 438 (`.gitignore` entry) and line 461 (`detect` glob exclusion). I also read the task
ledger (rows 1-25), Open items, the GAP series, Hard constraints and Verification. **No pending row
describes the worktree lifecycle CLI, the HEAD-move refusal, or Expertise write concurrency**, so
there is nothing to retire; and BUILD.md records what is LEFT, so delivered work with no
corresponding row earns no new row. Row 8 ("Expertise governance holes") scopes to provenance, decay,
curation and the global tier — none of which this feature touched.

## Verified before writing

- `path`, `list` run live: `path --repo harness --id FEAT-99` prints
  `.../.claude/worktrees/harness/FEAT-99`; `list --repo harness` prints the legacy one-segment
  `FEAT-31` tree and NOT the main checkout. `create|list|path|remove --help` all exit 0.
- `create --repo harness --id nope` refuses, naming the flow-id form (exit 2).
- `python3 .claude/skills/harness/bin/test-expertise-merge.py` → `PASS`.
- Every `file:line` anchor in the new prose re-derived at HEAD with `grep -n`; nine anchors from my
  first draft were wrong (by 2 to 12 lines) and were corrected before this receipt.
- `WORKTREES_SEGMENT = ".claude/worktrees"` at `harness_boundary.py:33`; the `<repo>` segment comes
  from `dest_for` (`feature-worktree.py:56-59`), so the prose describes the two-segment delivered
  layout and neither DEC-193 spelling.
- `.claude/skills/harness/SKILL.md:313-332` already carries the orchestrator's lifecycle rule (SC-06),
  so SPEC cites it rather than restating it.

## Not touched, deliberately

`DECISIONS.md`, `DECISIONS-INDEX.md` (issue #626 owns the DEC-193/143/95 repair), `BRIEF.md`,
`plan.yaml`, `STATE.md`, `feature.json`, anything under `.claude/skills/harness/bin/` (DEC-174),
`.claude/worktrees/FEAT-31`. `README.md` and `.harness/README.md` need no FEAT-30 change: worktrees
live outside `.harness/`, and the CLI's audience is the orchestrator, which reads
`.claude/skills/harness/SKILL.md`.

## Stale prose found, flagged not fixed (all pre-date FEAT-30)

1. `.harness/README.md` layout table names `features/<FEAT>/feature.yaml` and `PLAN.md`; disk carries
   `feature.json` and `plan.yaml` (checked in FEAT-29 and FEAT-30), and features now live under
   `.harness/harness/features/`. That is the FEAT-21/22 + DEC-182 migration's residue, not this
   feature's.
2. `BUILD.md:147-148` says "the hook cannot see writes made via `Bash`". True of `check-domain.sh`
   alone; `settings.json:34-37` (the `bash-write-guard.sh` entry) registers `bash-write-guard.sh` as a `PreToolUse` Bash hook, which is
   where FEAT-30's HEAD-move rule lives. The sentence is a Step-0b historical note, so I left it.
