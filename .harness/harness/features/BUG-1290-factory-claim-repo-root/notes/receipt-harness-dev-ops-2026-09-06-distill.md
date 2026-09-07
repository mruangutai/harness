# Receipt — harness-dev-ops — distillation — BUG-1290-factory-claim-repo-root

**BLUF:** 5 ops applied (1 replace, 4 add), all self-derived from my own 8 receipts — no
lead-relayed candidate was accepted as-is. Both files pass `check-expertise.sh`, both applied
through `expertise-merge.py ops` (never a whole-file write), both well under budget.

## Per-section counts (read from disk before/after)

| File | Section | Before | After |
|---|---|---|---|
| craft | Patterns | 15/15 (cap) | 15/15 (cap, P-17 replaced in place) |
| craft | Gotchas | 15/15 (cap) | 15/15 (untouched) |
| craft | Outcomes | 0/10 | 3/10 |
| craft | Open | 0/5 | 0/5 |
| craft | total lines | 35 | 38 (budget 150) |
| repo | Patterns | 2 | 2 (untouched) |
| repo | Gotchas | 12 | 13 |
| repo | total lines | 19 | 20 (budget 40) |

## Applied ops (`expertise_update`)

1. **replace P-17 (craft Patterns)** — merged the existing apply/restore/selectivity checks with
   a pre-fix-baseline control leg: run the mutant against the pre-fix tree first to confirm the
   target case wasn't already red there. Source: own artifacts — `receipt-...-01-eng-b3-remeasure.md`
   item 5 (pre-edit scratch-copy control, the load-bearing evidence of that whole cycle) and
   `receipt-...-08-eng-b16-recheck.md` M2/M3. Net length unchanged from the longer input (merge,
   not append), so Patterns stayed at cap without displacing an unrelated entry.
2. **add O-1 (craft Outcomes)** — WHEN a simplification pass finds a comment naming a past
   incident DO check whether it's the sole rationale for a load-bearing guard before flagging
   removal. Source: own artifacts — `receipt-...-b16-simplification.md` and
   `receipt-...-b27-simplification.md` Q2, same judgement made twice.
3. **add O-2 (craft Outcomes)** — WHEN judging compound-conjunct redundancy DO verify each
   conjunct pins a genuinely distinct observable before flagging it. Source: own artifacts — same
   two simplification receipts, each ruling out an adjacent-looking multi-conjunct assertion by
   checking pairwise for actual duplication.
4. **add O-3 (craft Outcomes)** — WHEN a plan's verify: targets a not-yet-existing regression DO
   run it against today's pre-fix tree, confirm still-green, trace the exact reddening check, and
   assert that specific marker rather than the aggregate exit code. Source: own artifact —
   `receipt-...-02-eng-efficiency.md`'s A1 probe (baseline confirmed green, exact regression
   traced to case `(F) claim exits 0`, narrowed `verify:` recommended accordingly). This also
   subsumes lead-relayed candidate 3 in substance, reached independently from my own material.
5. **add G-14 (repo Gotchas)** — WHEN a probe imports production code via
   `.claude/skills/harness/bin` DO `cmp` it against `.agents/skills/harness/bin` before trusting
   the result. Source: own artifact — `receipt-...-01-eng-b3-remeasure.md` item 7, which found
   both trees real (non-symlinked) directories, confirmed byte-identical only by `cmp`.

## Rejections, with reasons

- **Lead candidate 1** (shared report-helper decline — literal `KEY-COLLAPSE PROOF` string pinned
  by both an operator directive and the qa gate, plus class-vs-instance marker lifetime): rejected.
  Already covered by existing craft P-13 ("check each location for a structural exemption — … a
  test tying wording to code — before recommending a fix"); the instance-vs-class-level detail is
  a one-off implementation fact, not a generalizable rule. Fails the six-spawns test as a
  standalone entry.
- **Lead candidate 2** (negative-control the gate at authoring time, not three cycles later):
  rejected. This role's own material is about *verifying* an existing fix/gate (the pre-fix
  baseline control I did fold into P-17), not *authoring* a new gate — authoring-time discipline
  belongs to whichever role writes the gate (backend-dev here). Also substantially subsumed in
  effect by the merged P-17's new leg.
- **Lead candidate 3** (verify idiom test-driven against the untouched tree before being written
  into the plan): not rejected outright, but not applied as its own op — my own A1-probe artifact
  is the stronger, self-derived version of the same insight and became O-3 instead.

## Harness defects flagged by lead — not distilled, forwarded as open questions

Per the lead's own read, both are workarounds-for-a-bug, not craft, and are not in Expertise:

- A guard resolving its policy from another checkout's uncommitted working tree.
- A gitignored run directory being overwritten in place.

I did not independently encounter either in my 8 receipts, so I have no additional grounding to
add — forwarding them verbatim as open questions per the lead's framing.

## Entries counted by source

- Own-artifacts: 5/5 accepted ops (P-17 replace, O-1, O-2, O-3, G-14) — all traced to a specific
  receipt of mine above.
- Lead-relayed: 0/3 accepted as distinct ops (1 rejected as redundant, 1 rejected as
  wrong-role/subsumed, 1 absorbed into an own-artifact entry rather than applied separately).

## Tooling

Both `expertise-merge.py ops` calls and both `check-expertise.sh` calls ran directly in this
session (exit 0 each); no step was left unapplied.

```yaml
VERDICT: PASS
DIGEST:
  headline: 5 self-derived ops applied (1 replace, 4 add) across craft+repo dev-ops Expertise; 0 lead-relayed candidates accepted as-is
  task: none
  open_questions:
    - { id: Q1, question: "Guard resolves policy from another checkout's uncommitted working tree — lead reads this as a harness defect, not craft. Confirm and route to harness maintenance.", blocking: false }
    - { id: Q2, question: "Gitignored run directory overwritten in place — lead reads this as a harness defect, not craft. Confirm and route to harness maintenance.", blocking: false }
  files_touched:
    - .harness/expertise/harness-dev-ops.md
    - .harness/harness/expertise/harness-dev-ops.md
    - .harness/harness/features/BUG-1290-factory-claim-repo-root/notes/receipt-harness-dev-ops-2026-09-06-distill.md
  expertise_update:
    - { op: replace, target: P-17, section: Patterns, entry: "WHEN verifying a mutant discriminates DO run it against the pre-fix baseline first to confirm the target case wasn't already red there, diff-confirm the mutation applied, confirm byte-identical restore, and require only the target case redden while all others stay green — else the reddening is coincidental, not causal." }
    - { op: add, target: O-1, section: Outcomes, entry: "WHEN a simplification pass finds a comment or docstring naming a past incident DO check whether it is the sole documented rationale for a load-bearing guard before flagging its removal — if so, leave it; rewording to drop the incident id while keeping the rule is backlog, not blocking." }
    - { op: add, target: O-2, section: Outcomes, entry: "WHEN judging compound-conjunct redundancy in an assertion DO verify each conjunct pins a genuinely distinct observable before flagging it — conjuncts that look adjacent (e.g. two different string-presence checks) can each guard a different mutant class and are not redundant just because they resemble each other." }
    - { op: add, target: O-3, section: Outcomes, entry: "WHEN a plan's verify: targets a not-yet-existing regression DO run it against today's pre-fix tree, confirm it's still green, and trace the exact check that will redden — assert that specific marker in captured output, not the aggregate exit code, especially when the target file has no case-selection mechanism." }
    - { op: add, target: G-14, section: Gotchas, entry: "WHEN a probe or mutation test imports production code via `.claude/skills/harness/bin` DO `cmp` it against the `.agents/skills/harness/bin` equivalent (or confirm a symlink) before trusting the result — this repo carries both trees, and they only sometimes point to the same file." }
artifact: .harness/harness/features/BUG-1290-factory-claim-repo-root/notes/receipt-harness-dev-ops-2026-09-06-distill.md
```
