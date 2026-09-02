# FEAT-48 distillation — the 17 accepted ops the merge tool cannot write

**Every op below was ACCEPTED by the agent that owns the file, on the merits, and then refused by
`expertise-merge.py` for a mechanical reason. None of them was rejected for weakness.** This note
exists so the remedy is mechanical rather than a re-run of the whole round.

## The defect, verified at source

`expertise-merge.py` exposes exactly one subcommand — `apply` (`:281-286`). `compute_union`
(`:113`) never deletes: a proposal rewriting an existing id raises `MergeRefusal(7)` (`:230`), and
a new id over a section cap raises `MergeRefusal(8)` (`:232-238`). `harness-distill/SKILL.md`
documents `op: replace`, `op: drop` and `op: merge` as legal, and mandates displacement at a full
section. **Both routes out of a full section are refused, so a craft file at its caps is frozen.**
Every mature craft file in this repo sits at Patterns 15 / Gotchas 15 / Outcomes 10.

Remedy: a `displace` (or `replace`) verb in `expertise-merge.py`. That file is
`main-session-direct` under the DEC-174 carve-out, so no lead in the org may write it.

## Where the ops are, verbatim

| owner | count | target section(s) | verbatim ops |
|---|---|---|---|
| harness-pm | 5 | craft P, P, G, G, O | inline below — pm wrote no receipt |
| harness-security-reviewer | 5 | craft P-09, G-03, G-06, G-10, O-03 | `notes/review-harness-security-reviewer-distill.md:128-162` |
| harness-code-reviewer | 4 | craft P-10, P-11, G-11, O-08 | `notes/review-harness-code-reviewer-distill.md` |
| harness-ui-reviewer | 1 | craft P-10 | `notes/review-harness-ui-reviewer-distill.md` |
| harness-validator-lead | 2 | craft P-04, P-07 | `agent://Feat48Distill.ValidatorDistill` `expertise_update` |

## harness-pm's five, verbatim

Target file: `.harness/expertise/harness-pm.md` (craft). Each is a 1-for-1 displacement; the entry
it displaces and pm's reason are given.

1. **Patterns, displacing P-17** — "WHEN a real defect or consequence has no criterion that covers
   it DO route by what it changes: an approved consequence no task owns needs a task; a defect
   outside every criterion is a separate bug for the operator, never a widened scope; only an
   unmeetable criterion needs an amendment."
   *Weaker:* P-17 states two of these three branches in the language of one incident; the
   replacement is the same length and covers the third branch, which is the one that fired.
2. **Patterns, displacing P-16** — "WHEN every criterion passes DO still grade the approved plan's
   affirmative prose claims against measured behaviour: an overclaim inside signed prose is
   quantified over by no criterion, so it survives a plan panel and every goal-check."
   *Weaker:* P-16 is a recipe about one generator's bootstrap refusal branch — the narrowest entry
   in the section, and repository-flavoured.
3. **Gotchas, displacing G-03** — "WHEN an inspection criterion rests on numbers inside a note DO
   match each fence to the statements that emit it: a driver summary no command prints does not
   discharge measured-versus-typed, however precise it looks."
   *Weaker:* G-03 is generic shell-capture hygiene and its second half restates the write-guard
   rule already carried at repository G-01/G-02.
4. **Gotchas, displacing G-11** — "WHEN authoring or grading a wall-time criterion DO set its bound
   with headroom for concurrent siblings: the same command measured 42s on a quiet tree and 80s
   under a live review panel, so a tight bound fails on load rather than on regression."
   *Weaker:* G-11 prescribes one narrow repair for a sequence-dependent verify and overlaps
   O-04/O-11; the candidate binds every timing criterion pm authors or grades.
5. **Outcomes, displacing O-08** — "WHEN proving a set of in-file self-test cases discriminates DO
   patch one collaborator at a time, record which cases redden under each, and assert no case is
   ever-green. A per-probe pass rate hides a case nothing can falsify."
   *Weaker:* O-08 tells pm to look for one specific harness's binary-override env seam — a repo
   fact wearing craft clothes.

## The one write that went around the tool, and why it stands

`.harness/expertise/harness-qa.md` was edited in place rather than merged — qa performed the three
displacements the tool refuses (craft `P-06`, `G-06`, `G-09`). I verified the result before
committing: **41 entries before, 41 after, zero ids removed, exactly those three texts changed.**
The DEC-125 concurrency guarantee did not hold for that write; the content did. It stands because
reverting it would delete the only craft displacements this round produced.
