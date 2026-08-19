# Two directories became one — main session, 2026-08-18

## What happened

Three features were planned concurrently. `harness-pm` coins the feature id at BRIEF time and
nothing allocates ids, so two flows claimed `FEAT-25`: `FEAT-25-claim-feature-root` at 07:59:39
and this feature at 08:05:18. This feature's pm noticed and re-coined to `FEAT-27` at 08:07:39,
correctly skipping 26 — `FEAT-26-pr-linkage-recorded` had taken it 81 seconds earlier.

**The re-coin was right. What did not happen is the move of the work already written under 25.**
Both directories stayed live for the rest of the run: the product squad wrote to `FEAT-27`, the
eng squad to `FEAT-25`. Neither held a complete run.

This is #323, "The ID namespaces have no allocator". It fired here for the first time.

## What was in each

`FEAT-27` was the continuation and larger on every common file — BRIEF 210 lines against 188,
`plan.yaml` 722 against 560, the product digest 228 against 186 — and it alone carried
`feature.json`, `STATE.md` and the cycle-2 arch sendback note.

`FEAT-25` held two things that existed nowhere else:

- `runs/2026-08-18-1-eng/arch-review.md`, 160 lines — the cycle-1 architecture review.
- Five `harness-pm` observations, disjoint from the five in `FEAT-27`'s copy of that file.
  Neither file was a superset of the other.

## What I did

1. Copied `runs/2026-08-18-1-eng/arch-review.md` into this directory unchanged.
2. Appended `FEAT-25`'s five observations under a heading naming their origin. **`observations/`
   is the authoring agent's by the domain guard, not the main session's.** The crossing was made
   deliberately because the authoring agent was dead and the alternative was losing the entries;
   it is recorded here and in the file itself rather than left silent.
3. Deleted `FEAT-25-expertise-repository-tier`.

Nothing was overwritten. Every file `FEAT-27` already had is untouched.

## What this does not fix

Naming the feature id at dispatch — the interim mitigation recorded on #323 — prevents the NEXT
collision. It does nothing about one already on disk. There is no gate, invariant or check that
detects a feature split across two directories; this one was found because the main session
listed the directory for an unrelated reason.
