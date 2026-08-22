# Distillation — harness-pm — FEAT-31

**BLUF: three craft entries were judged worth holding and NONE could be applied — the mandated
merge tool cannot express a displacement.** `expertise-merge.py apply` is union-only: a sharpened
text under an existing id exits 7, a new id in a full section exits 8. Both measured below. Craft
Patterns and Gotchas are at cap, so the only appliable ops this cycle were repository-tier. Three
repository Gotchas applied, exit 0, checker clean.

## Measured tool limit (this is the blocker, not a judgement call)

- Sharpening craft `G-04` (adding the out-of-slice positive control): `CONFLICT section=Gotchas
  id=G-04` → **exit 7**, nothing written.
- Adding craft `P-16` (the false-closure rule) at Patterns 15/15: `CAP EXCEEDED section=Patterns
  cap=15 union_size=16` → **exit 8**, nothing written.
- `.harness/expertise/harness-pm.md` md5 `487ab254977eb652893b66e9759d2a18`, git-clean after both
  probes.

`harness-distill/SKILL.md:27` mandates displacement at a full section and its ops schema lists
`add | replace | merge | drop`; `expertise-merge.py:110` implements union only. The two disagree,
and the skill's instruction is the one that cannot be carried out. Raised as Q1.

## Counts

| File | Section | Before | After |
|---|---|---|---|
| `.harness/expertise/harness-pm.md` | Patterns / Gotchas / Outcomes / Open | 15 / 15 / 9 / 0 | 15 / 15 / 9 / 0 (unchanged) |
| `.harness/harness/expertise/harness-pm.md` | Patterns / Gotchas / Outcomes / Open | 0 / 3 / 0 / 0 | 0 / 6 / 0 / 0 |

Applied by source: **observation-log 3**, **lead-relay 0**. Displacements: **none possible.**

## Verdict per candidate

1. **False closure claim inside a decision** — ACCEPTED as craft (distinct from P-08, which covers a
   task's own factual claims, and from P-11, which covers scope versus task file lists). **Not
   applied: exit 8.** Intended text held in Q1.
2. **Repair preserves the superseded sentence** — REJECTED. Carried by the preloaded principle
   "never falsify the record", and the completeness half is craft G-13.
3. **Confounded evidence is evidence of nothing** — ACCEPTED as craft; no entry owns it (P-13
   counts methods, not sufficient causes). **Not applied: exit 8.**
4. **Second, out-of-slice positive control** — ACCEPTED as a sharpening of craft G-04; the new part
   is that a deletion or wholesale rewrite greens every in-slice check. **Not applied: exit 7.**
5. **Moving corpus / both sides in one breath** — REJECTED. Craft G-01 owns it ("equal counts across
   a concurrent edit are not confirmation"); the arithmetic slip is not a durable rule.
6. **Ungranted path denied though the dispatch named it** — REJECTED. Craft G-02 owns it verbatim
   ("a dispatch naming a path is not evidence the path is granted").
7. **Authority-document edit invalidates its generated index** — ACCEPTED, **repository tier**
   (`G-04`). The craft generalisation would need a displacement in a full section and nothing I
   hold is weaker than it; the value here is knowing which files a task must list in this tree.

From my own log, additionally accepted at repository tier: `check-plan-routes.py` with no argument
reports over every live plan (`G-05`), and `test_kinds` `detect` is a pipe-separated string, not a
list (`G-06`).

Also from my log and NOT applied, for the same cap reason: the recurring `: ` colon-space break in
one-line YAML prose keys (nine occurrences this feature) and the mid-write truncated read that
presents as a short complete file. Both are craft merges into existing G-12 and G-01 — exit 7.

## Open

- Q1 (blocking): the merge tool cannot displace. Until it can, every capped section is frozen and
  distillation degrades to append-only in whichever tier happens to have room. Three judged rules
  are lost per this cycle.
