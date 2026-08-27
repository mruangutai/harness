# Orchestrator ruling on E1/Q1 — FEAT-42 — 2026-08-26

## The constraint you stopped at was MINE, not the operator's. I am relaxing it.

Your digest records the byte-unchanged constraint as "set two tiers up" and "an explicit operator
instruction". **It was neither.** I wrote it, one tier up, in my own dispatch: *"This is an AMENDMENT,
not a re-plan... Nothing else about the plan changes. Do not re-derive, re-lane, or re-verify what
already passed."*

The operator's message said only: *"Add the task, widen SC-01's reach, return the plan
signature-ready again."* No freeze. **So relaxing it is an execution-time adjustment, which is
squarely mine, and it does not need the operator.**

You were right to stop rather than break a constraint you believed came from above — that judgement
was correct on the information you had. The misattribution is mine to fix, and this note fixes it.

## RULED: option A. Edit T-07 in place.

Fixing T-07 is **entailed by** the operator's ruling, not a departure from it. The ruling was "SC-01
must reach it". T-07 is SC-01's sole implementing task. If T-07 keeps the narrow scan root, SC-01
grades `not_met`, the repo-wide half of the gate is never exercised, and `.omp/extensions/harness-hooks.ts:144`
ships unguarded — which is the precise weak-gate outcome the widening existed to prevent. My "change
nothing else" was written without knowing T-07 hard-codes the scan root. It was over-broad, and your
run is what surfaced that.

Rejected alternatives, for the record: a T-21 would make two overlapping invariants for one fact
(rule 12 — structure earned by a real bottleneck, and this is not one); narrowing SC-01 back
contradicts a standing operator ruling.

## Three edits to T-07, all surgical. Nothing else in the plan changes.

I verified all three against `plan.yaml` myself before ruling.

1. **`depends_on`** (`plan.yaml:497`) — add `T-20`. T-07 asserts zero occurrences repo-wide; T-20
   removes the last one. Without the edge the invariant can run before its own precondition.
2. **`intent`** (`plan.yaml:521-527`) — the scan root becomes every tracked source file in the
   repository per the amended SC-01 (`git ls-files`, dropping `test-*` basenames, excluding
   `harness_boundary.py` and `*.md`), and the recorded baseline becomes **21 occurrences across 17
   files** at sha `3952814`. Keep the no-file-list rule and the DEC-169 presence pairing exactly as
   they are.
3. **The mutation proof** (`plan.yaml:505-512`) — **this is the one that matters most.** It currently
   appends the mutant to `$B/gh-close-gate.sh` where `B=.claude/skills/harness/bin`, i.e. INSIDE the
   old scan root, so a narrow invariant and a widened one go red identically and the proof cannot
   discriminate the very widening it exists to prove. **Plant the mutant OUTSIDE
   `.claude/skills/harness/bin/`**, on a tracked non-test non-`.md` file, and keep the existing
   discipline: assert the mutation APPLIED, assert the failure names the mutated file, restore, and
   re-run green.

That third defect was the lead's own find, not pm's. It is the sharpest thing in the run, and under
rule 7 it is the difference between a gate and a decoration.

## Q2 — the D-05 / D-12 count split: ACCEPTED as pm handled it, surfaced at signature.

`plan-merge.py` is add-only and exits 7 on a differing value for an existing id, so a supersede was
the only legal route and pm took it correctly. Two decisions now carry counts (D-05: 20/16;
D-12: 21/17 superseding). I am NOT having D-05 rewritten — that is the operator's call at signature,
and it is cosmetic beside the T-07 defect. Leave both, and let the operator decide whether D-05 gets
corrected in place when signing.

## Unchanged

Everything else in the plan stands: 20 tasks, 14/6 lane split, SC-01 at 21/17, the carve-out retired,
the inheritance note stating the MECHANISM and not a casualty (I read it — it clears the bar, and
quotes the author's rejection verbatim). Issue #869 carries the am.4 amendment.

**`approval:` stays `pending` in BRIEF.md and plan.yaml. The operator signs.**
