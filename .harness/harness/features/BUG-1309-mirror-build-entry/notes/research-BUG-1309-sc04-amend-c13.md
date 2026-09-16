# SC-04 amendment — cycle 13, operator ruling R-1 (D-13 / DEC-174)

**SC-04 now grades the deterministic duplicate-owner DENY and its attribution bound, in one
criterion, without weakening anything it graded before.** BRIEF.md lines **108–125** (bullet 108–124,
`verify:` line 125, unchanged text). No other line of BRIEF.md was touched — the working diff is a
single hunk confined to the SC-04 bullet, and `## Approval` still reads `status: approved` /
`approved-by: Mike Ruangutai` / `date: 2026-09-08` byte-identical (`BRIEF.md:181-185`).

## Before (BRIEF.md:108-116 at the pre-edit state)

Denied a non-era feature whose Build-entry outcome read `recovery-required` or was absent under
enabled sync, "with a reason naming the feature and the re-run command"; allowed `opened` /
`not-applicable` / `recovered-terminal`; allowed an era-exempt feature at exit 0 with no permission
decision; and the gh-unavailable clause — a merge no local record condemns is ALLOWED with one
stderr line. **Silent on multiplicity** (the gap the operator's R-1 names,
`notes/rulings-2026-09-08-panel-c7.md:76`).

## After — clause map

| Clause | Covers | Authority |
|---|---|---|
| sentence 1, through "no permission decision emitted" | (a), preserved. The reason-shape phrase is now scoped to the **single-owner** deny ("that single-owner deny carries a reason naming the feature and the re-run command"), because the ambiguity horn has a different shape | `plan.yaml:1113-1153` (T-05 step 6 DENY SHAPE, remedy selection); prior SC-04 text |
| sentence 2, "Where TWO OR MORE valid, attributable records … decided before the era gate" | **(b)** — deterministic DENY, every claiming feature directory id in stable sorted order, duplicated top-level `branch` must be corrected, NO re-run/receipt command offered, reached even for an era-exempt claimant | `plan.yaml:204-223` (D-13); `plan.yaml:1067-1078` (T-05 step 4, two-or-more-owners walk) |
| sentence 3, "ONE owner plus ANY amount of noise is NOT ambiguity … ALLOWED while such a record exists" | **(c)** — the attribution bound as a graded requirement, in two falsifiable halves: single-owner verdict is unchanged by noise, and a branch no valid record claims is still ALLOWED in the presence of such a record | `plan.yaml:1057-1063` (bound restated, two fence cases); `notes/rulings-2026-09-08-panel-c7.md:41-49` ("The bound on R-1") |
| final sentence, "Every deny is earned by the LOCAL receipt …" | (a), preserved verbatim in substance | prior SC-04 text |

## Why (c) reddens if cycle 11's `473d82cb` returns

The scan-wide sentinel denied merges on branches **no valid record claimed**. Clause (c)'s second
half asserts exactly the opposite observable — such a merge is ALLOWED while an unreadable or
malformed record sits elsewhere in the scan — so a re-introduced sentinel produces a DENY where the
criterion requires an ALLOW, and SC-04 is falsifiably **not_met**. Its evidence is already pinned:
T-05's `verify` requires the case names `T-05 single owner plus unrelated malformed record still
allows` and the two standing fence cases (`plan.yaml:998`, `plan.yaml:1061-1063`).

## Discipline held

- Observable behaviour only: the criterion says what the merge gate **does** (deny / allow, what the
  message names, in what order, before which gate). It says nothing about `feature_for`'s
  implementation, its scan mechanism, or `glob.glob`. Weakest wording that keeps both new horns
  falsifiable (principle 6).
- `verify: automated        evidence: integration` unchanged; 2-space continuation and ~100-column
  wrapping preserved (no new line exceeds 100 columns — the three over-length lines in the file, 63,
  74 and 131, are pre-existing and untouched).
- No source change, no `plan.yaml` write, no new SC id, no edit to SC-01..SC-03, SC-05..SC-10,
  `## Verification gaps` or `## Approval`.

## Open questions

None. The standing Q1 (widen SC-04 vs. new SC vs. disclose as a verification gap) is **closed by the
operator's ruling: widen.** The operator re-signs `## Approval`; pm does not move that date.
