# Goal-check — FEAT-29-graphql-budget, at `4f2e5d0`

**8 of 10 SC met. SC-08 and SC-09 are unmet, both `genuinely-wrong`, both cheap to close.** The
feature's core claim — the state gate costs 5 points instead of 506 and still detects what it
detected — holds on evidence I re-derived myself. The two misses are record-keeping deliverables
that were never fully carried out, not defects in the read.

## Provenance objection: closed, re-confirmed here

```
git diff --stat 8c2c24d..4f2e5d0 -- .claude/skills/harness/bin/   -> empty
git diff --stat 8c2c24d..4f2e5d0                                  -> measurement-after.md,
                                                                     measurement-board6.md,
                                                                     plan.yaml (4 lines)
```
No source byte separates the trees. The cost evidence pinned at `8c2c24d` describes `4f2e5d0`.
Not reopened.

## Verdicts

| SC | verdict | method | key evidence |
|---|---|---|---|
| SC-01 | met | inspection | `notes/measurement-after.md:14-18` — before 0, after 5, delta 5, board_items 473, sha 8c2c24d. Ceiling 100 |
| SC-02 | met | automated/unit | `bin/test-gh-board.py:211-236` — one fixture, three cases, each its own assertion (other-repo excluded, stationed present, unstationed `None` not dropped) |
| SC-03 | met | inspection | `notes/measurement-board6.md:12-18` — old 102, new 1, `board_items: 4` on BOTH sides, raw values recorded |
| SC-04 | met | inspection | my own diff of the two `VIOLATIONS` blocks: 4 added, 0 removed, 0 altered, order of the 53 common lines preserved. Explanation sound (below) |
| SC-05 | met | automated/unit | ON+failing `bin/test-gh-cost-log.py:393-409` (rc==1 recorded); OFF both halves `:242-258`, variable genuinely `pop`ped, success and rc=1 cases |
| SC-06 | met | inspection | `COVERAGE_NOTICE` constant `bin/gh_cost_log.py:40-45`; written as line 1 of a fresh file `:129-131`, never repeated `:125`; asserted `test-gh-cost-log.py:106-111` |
| SC-07 | met | automated/unit | positive `bin/test-factory-gh.py:1393-1404` (names GraphQL, 5000, reset ISO, REST's own usage); discriminator `:1435-1436` asserts the headline ABSENT for an unrelated exit-1. **Caveat, Q1** |
| SC-08 | **unmet — genuinely-wrong** | inspection | corrections 1+2 met in the grilling note. The ABSENCE clause fails — see below |
| SC-09 | **unmet — genuinely-wrong** | inspection | at the pin, `CLAUDE.md` carries **no rule at all**; the working-tree rule cites no cost figure |
| SC-10 | met | automated/integration | `run-unit-tests.sh --kind unit` exit 0, 18 scripts; `--kind integration` exit 0, 12 scripts; zero FAIL lines. Run by me at the pin's source tree |

## SC-08 — the absence claim fails, and I ran the search

```
git grep -n -i -e "item-list" -e "project_items" -- '*.md' | grep -v "features/FEAT-29"
git grep -n -i -e "31 point" -e "31 GraphQL" -- '*.md'
```
(neither broken idiom used: no `wc -l` equality test, no `-E` with `\b`.)

- `.harness/harness/features/FEAT-11-graphql-field-resolve/BRIEF.md:170-171` — present at `4f2e5d0`,
  **unstruck**: "`gh project item-list` (`project_items`) stays as it is — 31 points, once per
  invocation, never in a loop. Out of scope." That is verbatim the assertion SC-08 requires no
  surviving document to make.
- Same claim repeated as live fact at `FEAT-11-.../STATE.md:31` and
  `FEAT-11-.../notes/ship-review-close.md:126`.

Root cause is plan-level, not execution-level: T-05's `files:` names only
`.harness/notes/grilling-graphql-cost-2026-08-10.md`. **No task was ever written to satisfy the
repo-wide clause of SC-08.** The remedy is the same in-place strike DEC-188 prescribes and that T-05
already applied to the grilling note — three lines across three FEAT-11 files.

## SC-09 — the deliverable is uncommitted, and the required citation is absent either way

`git show 4f2e5d0:CLAUDE.md` ends at the two pre-existing conventions. T-08's wait-loop rule exists
**only in the operator's uncommitted working-tree edit** (` M CLAUDE.md` in `git status`). Two
independent failures:

1. At the pin, no operating rule is recorded. T-08's `verify:` passes because it reads the working
   tree, not the tree under review — the verify cannot distinguish committed from uncommitted.
2. SC-09's third clause — "with the measured 2-points-per-poll cost cited" — is absent from **both**
   versions and from every tracked `.md` outside a FEAT-29 note (`grep -rn "2 points\|points per
   poll" --include="*.md" .claude/ CLAUDE.md` → nothing). T-08's own `intent:` deliberately dropped
   interval guidance ("Interval guidance is NOT the fix", operator ruling) but SC-09's text was never
   amended to match. Ship-review B-14 saw this and it was not routed.

Clauses 1 and 2 of SC-09 are otherwise satisfied *by the working-tree text*, which bans wait loops
outright — strictly stronger than the ≥60s interval the SC permits.

## SC-04 — the explanation is sound, judged rather than accepted

Re-derived independently: 4 lines added, 0 removed, 0 altered, common-line order preserved. All four
are T-01–T-04 cards reading `Backlog`. The explanation holds because it is falsifiable and was
checked: at the baseline sha every task read `pending`, so INV-26 had nothing to say; seven tasks
completed against a deliberately frozen mirror; **four** violate rather than seven, and the
difference is accounted for card by card (T-05/T-06/T-08 cards read `Done`, so INV-26 is correctly
silent). A hand-waved "the tree changed" would predict seven. The prediction that distinguishes them
was made and it came out right.

## The judgement asked for: does the cheap read still DISCOVER what the expensive one did?

**Yes — and neither piece of evidence would carry it alone.**

The threat #588 creates is that silence is ambiguous. Four ways a cheap read could look right while
being wrong: it raises or returns empty; it truncates; it returns a degenerate constant station; or
it drops unstationed cards.

The positive control kills *empty* and *constant*. It is not merely "seven lines appeared" — the
seven lines are verbatim string matches carrying issue numbers **and** station values, and one of
them (`parent (issue #571) … the board reads Building`) carries a *different* station from the other
six. A read returning nothing emits zero lines; a read returning one constant emits the wrong text on
that line. The control therefore contains its own two-value discriminator, at 5 points, matching what
506 points produced.

The live run kills *truncation*. Nine consecutive cards, #579–#587, produce three distinct outcomes
in one invocation — four Backlog-violating, three Done-and-silent, two Backlog-and-agreeing. Any page
boundary falling inside that range drops cards and changes the line set.

The fourth mode, dropping unstationed cards, is **not** exercised live — every real card had a
station — and it is the one INV-26 exists to distinguish. It is closed by a different instrument:
`test-gh-board.py:222,235-236` asserts a `fieldValueByName: None` item survives as `None` rather than
being dropped, and it is asserted separately from the other two cases so a mutation reddens it alone.
That is adequate, because the property is deterministic in the mapping code and does not depend on
board content.

**Where the proof is thinnest, named rather than buried.** The control is a *seven-of-eight* verbatim
match, not eight-of-eight. T-08's line is absent, and the reason offered — T-08's card now reads
`Done` — is reported by the same cheap read that is under test. That is mildly circular. It does not
break the result (T-08's completion is independently recorded in `plan.yaml`, and the other six lines
are exact), but if this proof is ever challenged, that is the seam. A strictly cleaner control would
have been captured against a mirror frozen at the same instant as the 506-point run.

One adjacent risk worth carrying forward: ship-review B-13 records `factory_gh.py:359-363` spinning
forever on `hasNextPage: true` with a null `endCursor`. That is a hang, not a silent empty — loud
enough not to threaten this criterion, but it is the one failure mode of the new read that neither
measurement would surface.

## Open questions

- **Q1 (non-blocking).** SC-07's trailing clause — "a `gh` command typed straight into Bash still
  returns raw text, **and that limit is stated where the operator will read it**" — is unsupported. No
  tracked document states it; `COVERAGE_NOTICE` states the *cost log's* blind spot, a different
  mechanism (ship-review B-7 conflates the two). SC-07 declares `verify: automated`, and an automated
  method is structurally blind to a documentation clause. Graded `met` on its automated core, with
  the gap named rather than absorbed. One sentence anywhere operator-facing closes it.
- **Q2 (non-blocking).** `.harness/harness/features/FEAT-29-graphql-budget/STATE.md:14-15` in the
  working tree states "**5 GraphQL points against a 506 baseline**" with no board, item count or
  commit — a bare corrected number, the exact shape SC-08's second absence clause forbids, introduced
  after the pin. Not graded (post-pin), flagged so the correction pass does not ship it.
