# Receipt — harness-documentor — distill — c1

**Five entries added across both tiers; both files pass `check-expertise.sh` with exit 0 and no
advisories.** Nothing staged, nothing committed. No other agent's file touched.

## Ops applied

| Op | Target | Tier / section | Source |
|---|---|---|---|
| add | P-16 | craft / Patterns | observations log (mine) |
| add | G-16 | craft / Gotchas | relay C2 |
| add | G-17 | craft / Gotchas | relay C3 |
| add | O-06 | craft / Outcomes | relay C1 |
| add | G-04 | repository / Gotchas | my two receipts (self-derived) |

All targets are new IDs; no `replace`, `merge` or `drop` was applied, so no existing entry was
displaced and no section was at cap.

## Counts (before → after)

| Section | craft | repository |
|---|---|---|
| Patterns (15) | 13 → 14 | 2 → 2 |
| Gotchas (15) | 12 → 14 | 3 → 4 |
| Outcomes (10) | 5 → 6 | 0 → 0 |
| Open (5) | 0 → 0 | 0 → 0 |
| **Lines** | 99 → 112 (budget 150) | 26 → 29 (budget 40) |

## What each entry carries

- **P-16 (mine, the feature's strongest finding).** Four paraphrases of one falsehood survived a
  green literal `verify:` in a single document, one of them ~1300 lines from the section owning the
  subject and one twelve lines beneath a table I had just corrected. The rule is the sweep
  discipline: read every section touching the subject, sweep the *concept's vocabulary*, not the
  struck phrasing.
- **G-16 (C2).** Base-pin divergence: check the pinned SHA against real HEAD, work at HEAD, report
  the divergence. Distinct from craft P-01, which covers anchors and counts and prescribes
  re-deriving them; here you cannot re-derive, only report.
- **G-17 (C3).** A document can be true sentence-by-sentence and wrong as a whole when two
  vocabularies name the same objects. No existing entry covers a defect made of true statements.
- **O-06 (C1).** Correcting a relationship between two values without stating the mechanism leaves
  the next reader to re-derive it and read the equality as a bug.
- **G-04 (repository).** In this repo, `SPEC.md` states intent and drifts; the scripts under
  `.claude/skills/harness/bin/` are the authority when they disagree. Grounded in four SPEC claims
  falsified by `check-expertise.sh` and `inject-expertise.sh` during this feature.

## Rejections

- **C1/C2/C3: none rejected.** All three passed the six-spawns test and none duplicated a live
  entry.
- **Observation "fixing a section's table does not fix the prose beneath it"** — rejected as a
  standalone entry; it is the same rule as P-16 and is carried in P-16's clause "survive beneath a
  table you just corrected". A separate entry would be the case, not the rule.
- **"DEC-27 is falsified and unstruck"** — rejected from Expertise entirely. It is a defect report,
  and a defect report in Expertise ages into a stale workaround. It belongs on the operator's
  backlog, where the specfix receipt already put it.

## Stale entries

None. Every existing craft and repository entry was re-read against this feature's evidence; none is
contradicted. The five migrated entries were checked at their **destination** IDs (repository
P-01/P-02, G-01/G-02/G-03) — no op in this run names a craft ID that the migration vacated.

## Verify

`.claude/skills/harness/bin/check-expertise.sh` over both files: `OK`, exit 0 each.
