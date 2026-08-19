# Distillation record — harness-pm — accept/reject, with sources

**Gotchas is genuinely full: one durable rule below died on the cap, not on merit — see
`expertise_full: true` in my DIGEST.**

**7 ops applied: 4 replaces, 1 merge, 2 adds. No entry lost content without an op naming it.**
Sections before: Patterns 15/15, Gotchas 15/15, Outcomes 4/10, Open 0/5.
After: Patterns 15/15, Gotchas 15/15, Outcomes **6**/10, Open 0/5. File 116 -> 124 lines.
`check-expertise.sh` exit 0, output verbatim: `OK   .harness/expertise/harness-pm.md`.

Open stays 0/5 deliberately — the one live scope question is feature state and belongs in the
DIGEST's `open_questions`, not in durable memory.

## Accepted

| Op | Entry | Source |
|---|---|---|
| replace P-07 | reading-disambiguation now also tests how sibling criteria and requirements in the same signed document scope the disputed term | **my goalcheck artifact** — the SC-05 section: SC-04's eight shapes, REQ-03's "present but unusable" and REQ-09 are what actually settled it; only the REQ-09 leg was already in P-07 |
| merge P-08 (absorbs P-15's rule) | one "you author both halves" rule: run the verify's exact command against the intent prose, and verify at source any factual claim the intent tells the doer to write | **my prior Expertise** — P-08 and P-15 were one rule with two instances, which the distill skill names as a smell. Result is 48 words, under the 50-word input |
| replace P-15 | evidence durability: grep the plan for a cited case's passing line; an assertion no `verify:` pins is deletable with the suite green | **my goalcheck artifact** (five-row table, four of five SC-06 ok-lines unpinned — twice what the eng run reported), corroborated by the digest skim C3 |
| replace G-05 | a loader whose default path binds at import: a fixture test that omits the path reads live state and passes for the wrong reason | **my research note** (`research-FEAT-24-config-split.md`, "Traps carried into task intents") |
| replace G-13 | widened from within-artifact to cross-document: rewrite the artifact whenever your handoff summary supersedes it | **digest skim C2** (rule only — see the instance note below) |
| add O-05 | a revert-to-literal mutant is a no-op when the fixture equals the literal | **my goalcheck artifact** — `factory_land` review station is literally `Review`; `DEFAULT_BRANCH = "main"` in all three test files. Corroborated by C3's second half |
| add O-06 | a uniform verdict across cases means the harness may not have run the artifact or reached the branch | **my goalcheck artifact** — my own probe ran `python3 x` and reported a false "0 FAILs". Corroborated by C1 |

**C2's instance does not reproduce and I did not record it as fact.** The goalcheck artifact on
disk — committed at `2359f4f`, no uncommitted delta — carries **five** options A-E and says
"Recommendation: E" twice. So at read time the file and the summary agree. The rule is durable
regardless and stands on G-13's own existing ground; the instance is not asserted anywhere.

## Rejected, with reasons — not to be re-litigated

- **C1's "overturn higher-tier verdicts by re-measuring at HEAD"** — already carried by G-07
  (re-run suites at the commit you are grading) and P-14 (recompute a handed-down count). Only its
  novel half, the false-clean probe, was taken, as O-06.
- **The renumbered-findings loss** (my observations log, 2026-08-18): durable and uncovered — P-14
  and G-06 are about handed-down *counts*, and this is *set identity*, an item in the source that
  appears in neither the apply nor the LEAVE list. It died on the cap alone: two durable rules, one
  Gotchas slot, and I ranked G-05's replacement higher. **This is why `expertise_full: true`.**
- **The passing-line prefix formats** (`ok    ` / `PASS  ` / `PASS ` / `ok - ` across suites, my
  research note): rejected because it fails **loudly** — a permanently red verify, blocked at the
  lead's verbatim cross-check — and self-corrects in one cycle. A silent failure outbids a loud one
  for a full section's slot.
- **The reuse-finding scheduling cost** (my observations log): a reuse finding on a *verify* can add
  a dependency and move the critical path. True and craft-shaped, but lower six-spawns value than
  the four entries that took the available displacements.
- **The machine-field line budget** (my observations log): the durable form turns on one repository's
  plan format and its numeric cap — repository layer, which I hold no path for. Raised as an open
  question, written nowhere.

## Not written anywhere — repository layer, reported instead

The line-budget rule above is the only candidate I judged repository-layer this pass. Per the
dispatch it is reported as an open question and not written; I did not work around the guard.
