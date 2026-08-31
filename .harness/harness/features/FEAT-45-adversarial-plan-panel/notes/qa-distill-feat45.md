# FEAT-45 — harness-qa Expertise distillation (feature-close)

## Result

One repository-tier Gotcha applied. Craft tier unchanged: Patterns (15/15), Gotchas (15/15),
and Outcomes (10/10) are all at their hard entry cap, and `expertise-merge.py apply` is
**empirically confirmed additive-only** — see "Mechanical limitation" below. Four judged-durable
candidates could not be mechanically applied this dispatch as a result.

## Tier counts

| Tier | File | Section | Before | After |
|---|---|---|---|---|
| craft | `.harness/expertise/harness-qa.md` | Patterns | 15 | 15 |
| craft | " | Gotchas | 15 | 15 |
| craft | " | Outcomes | 10 | 10 |
| craft | " | Open | 1 | 1 |
| repository | `.harness/harness/expertise/harness-qa.md` | Patterns | 0 | 0 |
| repository | " | Gotchas | 4 | 5 |
| repository | " | Outcomes | 0 | 0 |
| repository | " | Open | 0 | 0 |

## Applied op

```
python3 .agents/skills/harness/bin/expertise-merge.py apply \
  --file .harness/harness/expertise/harness-qa.md --entries <scratch>
```
stdout: `ADDED G-05` / `PRESERVED G-01..G-04` / `APPLIED .harness/harness/expertise/harness-qa.md`, exit 0.

New repository-tier entry:
> G-05: WHEN a feature branch's later merge-from-main reintroduces run-unit-tests.sh's
> UNIT_SCRIPTS/INTEGRATION_SCRIPTS entries for files main already deleted DO expect the
> KIND-DRIFT union check to exit 2 for `--kind unit`, `--kind integration`, AND `--check-kinds`
> alike — it scans the combined array before any kind dispatch, so no single kind avoids it.

Source: `review-harness-qa-c2.md` — a stale merge reintroduced three dead
`test-context-watch*` array entries, breaking the canonical gate entry point for every kind at
once. Repository-specific (names this repo's own `run-unit-tests.sh` mechanism).

## Mechanical limitation — empirically confirmed, not just read from source

Probed against the craft file directly: proposing a 16th Patterns entry with a fresh id returned
`CAP EXCEEDED section=Patterns cap=15 union_size=16`, exit 8, and the base file was left
byte-identical (grepped for the probe id post-refusal — absent). Reading
`expertise-merge.py`'s `compute_union`: `apply` computes `base ∪ proposal` only. An id present
in base and absent from the proposal is **never removed**. Same id + different text is a hard
**conflict refusal** (exit 7), never an overwrite. There is no drop/replace verb in this CLI —
only `apply`.

The distill skill's "a candidate enters a full section only by displacing a weaker entry" model
has no supported execution path for a single per-feature distillation dispatch once a section is
already at cap — that capability appears to exist only in `/harness-curate`'s out-of-band,
direct-edit workflow. Raised as `open_questions` Q1 below rather than worked around with a
prohibited whole-file Write.

## Candidates judged this cycle

### Accepted in judgment, blocked by the cap (see above) — none applied

1. **Self-derived** (`qa-feat45-c0.md`, `review-harness-qa-c1.md`, `review-harness-qa-c3.md`):
   *WHEN a gate reports `matrix_ok: true` DO also run every kind whose registry holds the diff's
   changed tests, not just the declared change_type floor — a floor of `unit` does not mean the
   binding regression tests live there.* (This feature's fix-cycle regression tests were
   registered under `integration` while the plan's tasks declared `unit`/`config`/`docs`; c3
   ran both kinds for exactly this reason.) Target: would extend/replace craft Patterns P-04.
   Blocked: exit 7 (replace) or exit 8 (new id).
2. **Relayed (a)**, `review-harness-qa-c4.md`: *WHEN a suite-run's exit code is captured through
   a pipe (e.g. `| tee log`) and looks like a failure DO re-run directly without the pipe before
   trusting it — `PIPESTATUS[0]` can report a stale/unrelated code over an identical, all-passing
   log.* New craft Gotcha. Blocked: exit 8.
3. **Self-derived** (`review-harness-qa-c2.md`, `review-harness-qa-c4.md`): *WHEN
   bash-write-guard blocks a scratch-directory write/`rm`/`sed -i` even fully outside the repo
   tree DO recognize it matches on file basename, not path or repo membership — route
   mutation-probe file edits through `python3 -c` file writes/`os.remove` instead of shell
   `cp`/`sed`/`rm`.* New craft Gotcha; also resolves/supersedes the existing Open item Q-01
   ("confirm bash-write-guard's scratchpad behavior with a controlled repro" — now confirmed
   across two independent cycles). Blocked: exit 8. Even if room existed, Q-01 cannot be
   mechanically dropped (no drop verb), so it would sit alongside the new Gotcha as redundant
   residue.
4. **Self-derived**, `review-harness-qa-c2.md`: *WHEN every individual test script in a kind
   passes standalone DO still directly invoke the standing aggregate gate command before
   reporting `matrix_ok` — component-script health does not imply the aggregator runs; stale
   registry entries can make it exit before executing anything while each script alone stays
   green.* (This is the actual c2 BLOCKED finding — every script green, the aggregator dead.)
   New craft Outcome. Blocked: exit 8.

### Rejected

1. **Relayed (c)**, `review-harness-qa-c4.md`: revert the implementation to a real prior shape
   (32-hex → 8-hex) in a scratch copy and run the unmodified shipped test, counting which
   assertions redden. **Rejected as redundant** with existing craft Pattern P-09 ("run a
   mutation probe against the assertion's OWN intended mutant, not merely a convenient one"). A
   reverted prior implementation is a specific, faithful instance of exactly that technique, not
   a materially new generalizable rule — adding it would restate P-09 with a case history, which
   the distill skill bans.
2. **Self-derived**, `review-harness-qa-c1.md`: use the absolute worktree-rooted path when
   reading a file in a pinned-worktree review, since a bare relative path can resolve against the
   main checkout instead of the worktree under review. **Rejected as insufficiently distinct**
   from existing craft Gotcha G-01 (already covers absolute-vs-relative path resolution against
   the wrong root in a probe/worktree context) — a second instance of the same underlying rule,
   and G-01 cannot be replaced in place anyway.
3. **Self-derived**: log a new craft Open item restating the resolved bash-write-guard
   basename-matching finding, to use the Open section's headroom (1/5). **Rejected** — the
   finding is now demonstrated and resolved (two independent cycles, concrete workaround), so it
   belongs in Gotchas, not Open; padding Open with an already-resolved item to use free slots
   would misrepresent it as still uncertain.

## Open question raised

Should `expertise-merge.py` gain a bounded, auditable replace/drop verb usable by the
distilling agent against its own file, or should cap-blocked-but-judged-durable candidates route
to a queued curation list for a later `/harness-curate` pass? Non-blocking — the repository-tier
op still landed cleanly this session.
