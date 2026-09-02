# pm craft displacements — applied, verified, gate green

**BLUF.** All five owner-accepted displacements landed in `.harness/expertise/harness-pm.md` as
targeted single-line in-place rewrites. 40 ids before, the same 40 after, in the same order.
Every non-rewritten line is byte-identical (sha256 proof below). Sections stayed 15 / 15 / 10.
`check-expertise.sh` is OK at exit 0. `expertise-merge.py` was not invoked (exit 7 on same-id
rewrite); nothing else in the tree was touched.

## The five ops (all `op: replace`, id and section preserved, position preserved)

| id | section | line | replacement text source |
|---|---|---|---|
| P-16 | Patterns | 16 | `notes/distill-blocked-ops-2026-09-02.md` item 2, verbatim |
| P-17 | Patterns | 17 | item 1, verbatim |
| G-03 | Gotchas | 21 | item 3, verbatim |
| G-11 | Gotchas | 29 | item 4, verbatim |
| O-08 | Outcomes | 41 | item 5, verbatim |

## Word counts — the checker's own rule

`len(text.split())` on the entry text after the `- <id>: ` prefix, measured on the written file:

```
P-16 36
P-17 50
G-03 34
G-11 43
O-08 38
```

All within the 50-word cap; none needed re-rendering. These reproduce the orchestrator's
pre-measured numbers exactly.

## Preservation proof

Command (run from the worktree root, before and after the edit):

```
sed '16d;17d;21d;29d;41d' .harness/expertise/harness-pm.md | sha256sum
```

Before: `da482c13902649a66d969b5d707da51428c6abbf056a2fdb9c2844053303a61f`
After:  `da482c13902649a66d969b5d707da51428c6abbf056a2fdb9c2844053303a61f`

Identical. No entry has continuation lines in this file — all 40 are single lines — so the five
deletions cover exactly the rewritten entries. File length 45 lines before and after.

## Ids and section counts

Before and after id lists are identical, in order:
`P-01..P-08 P-11..P-17 G-01..G-15 O-01 O-02 O-03 O-04 O-06 O-07 O-08 O-11 O-12 O-13` (40).

Section entry counts before and after: Patterns 15, Gotchas 15, Outcomes 10.

## The gate, verbatim

```
$ .agents/skills/harness/bin/check-expertise.sh .harness/expertise/harness-pm.md
OK   .harness/expertise/harness-pm.md
ADVISORY .harness/expertise/harness-pm.md:3: P-01 names '.harness/' — repository-layer candidate; rule on it (issue 340)
EXIT=0
```

The ADVISORY is on P-01, pre-existing and untouched by this pass; an advisory is not a violation.

## Open questions

None. The `expertise-merge.py` displacement defect is already recorded as backlog (#1211/#1212)
and is not re-raised here.
