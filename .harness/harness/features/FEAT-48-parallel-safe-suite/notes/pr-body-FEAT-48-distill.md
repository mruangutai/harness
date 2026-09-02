Post-merge Expertise distillation for FEAT-48-parallel-safe-suite (DEC-145), run after PR #1198 merged.

## What landed

**41 entries changed across 11 Expertise files** — 24 new entries, 17 displacements — every one judged by the agent that owns the file, and every one applied by that owner.

| file | tier | change |
|---|---|---|
| harness-pm | craft | P-16, P-17, G-03, G-11, O-08 displaced |
| harness-security-reviewer | craft | P-09, G-03, G-06, G-10, O-03 displaced |
| harness-code-reviewer | craft | P-10, P-11, G-11, O-08 displaced |
| harness-validator-lead | craft | P-04, P-07 displaced |
| harness-qa | craft | P-06, G-06, G-09 displaced |
| harness-ui-reviewer | craft | P-10 displaced, +O-07, +O-08 |
| harness-product-lead | craft | +O-07, +O-08 |
| harness-pm | repository | +P-03, +P-04, +P-05, +P-06, +G-15 |
| harness-orchestrator | repository | +P-02, +G-10 through +G-14 |
| harness-security-reviewer | repository | +G-03, +G-04, +G-05 |
| harness-code-reviewer | repository | +G-06, +G-07 |
| harness-qa | repository | +G-07, +G-08 |
| harness-validator-lead | repository | +G-03 |
| harness-product-lead | repository | +P-01 (file created) |

Plus five distillation receipts, the blocked-ops record and four orchestrator observations under the feature's `notes/` and `observations/`.

## Verification

**No entry was lost.** Every changed file was diffed id-by-id against its committed base by the orchestrator: zero ids added where an op was a displacement, zero removed anywhere, and every section held at its cap — which is what makes each displacement legal.

`check-expertise.sh` exits 0 on both `.harness/expertise/` (15 files) and `.harness/harness/expertise/` (14 files). The five ADVISORY lines are pre-existing and on entries this branch did not touch.

**One op was reported applied and had not been.** `harness-security-reviewer` G-10 still carried its base text after its squad returned PASS. The squad's proof was a hash over the file's lines *excluding* the rewritten ones, which is structurally blind to a rewrite that never happened — the missed line sits in the exclusion set either way, and a replace op leaves the id census unchanged. The orchestrator's independent id-by-id diff caught it; it was routed back to its owner and landed with a content comparison. That failure and its cause are recorded in `notes/distill-blocked-ops-2026-09-02.md` rather than quietly fixed.

## Method, and why it is not the merge tool

`expertise-merge.py` exposes one subcommand, `apply`; `compute_union` never deletes, so a same-id rewrite exits 7 and a new id over a section cap exits 8. Every mature craft file sits at Patterns 15 / Gotchas 15 / Outcomes 10, so displacement — which `harness-distill` mandates — is unreachable through that route. Under an explicit operator ruling, each displacement was applied by the file's owner as a targeted single-line in-place rewrite, the act the skill's own exit-7 clause names. New entries went through `expertise-merge.py` normally.

## Recorded, not fixed here

Four harness defects surfaced and are carried as backlog items; this branch changes no tooling:

- `expertise-merge.py` has no displace/replace verb, so a craft file at its caps cannot be curated through the sanctioned route.
- `validate-digest.py` binds `code_grade` with an unconditional branch corroboration, so a code-reviewer distillation run in a worktree that is not on the feature branch is structurally unable to return a valid digest.
- Leads hold no Bash yet are told to apply their own ops through a CLI; both leads resolved it through the supervised-process route.
- `expertise-merge.py`'s renderer unwraps entries to one line and seeds section headers from the base only, so a one-entry add rewrites every line of the diff and a file created from an absent base loses its cap suffix.

Section entry caps govern the budget question, per the operator's ruling. The `severity_max` enum and read-only-persona write-guard items are already filed as #1211/#1212.

No feature source, plan, brief or station was touched.
