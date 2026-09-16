# Plan repair c7 — SC-06's chore leg is now provable at T-03 case E

**DONE, by the four dispatched points and nothing else.** T-03 case E's override map is now the
three-key `{"Bug": "Defect", "Task": "Maintenance", "parent": "Epic"}`, and the case asserts three
DECLARED non-default type ids — `IT_defect` on the bugfix sub-issue, `IT_epic` on the parent,
`IT_maintenance` on the config task and the feature task — each **by type id, per issue**. That is
the chore leg BRIEF SC-06 names, on `evidence: integration`. BRIEF.md was not opened; `panel:` and
`approval:` were not written. `check-plan-routes.py <this plan>` → `0 violation(s) across 1 plan(s)`,
exit 0.

I re-derived every anchor against the current file rather than trusting the c5 note. All three
anchors and T-03's `verify:` matched the dispatch byte for byte before I amended
(`--show` sha256 `9268144…` on `verify`, `84089b3…` on `intent`). Nothing in the remedy was wrong,
unnecessary or insufficient — one spelling call is recorded under point 4.

## The four points — before / after

| # | before | after |
|---|---|---|
| 1 | case E map `{"Bug": "Defect", "parent": "Epic"}` | `{"Bug": "Defect", "Task": "Maintenance", "parent": "Epic"}` |
| 2 | "the config task's and the feature task's **still carry IT_task**, because renaming Bug leaves Task alone" | "the config task's and the feature task's **each carry IT_maintenance** — three DECLARED, non-default type ids, one per override key, each asserted BY TYPE ID on its own issue", with the rationale rewritten to the three keys resolving independently (Bug → the bugfix sub-issue only, parent → the parent only, canonical Task → every implementation task issue at once under D-18) |
| 3 | available fake declares `Bug, Feature, Task, Defect and Epic` (`IT_bug, IT_feature, IT_task, IT_defect, IT_epic`) | declares `Bug, Feature, Task, Defect, Epic and Maintenance`, ids `+ IT_maintenance` |
| 4 | `for s in IT_feature IT_bug IT_task IT_defect IT_epic updateIssue …` | `… IT_defect IT_epic IT_maintenance updateIssue …` — one literal inserted, loop structure, case loop and every other line of `verify:` byte-unchanged |

**Point 4 spelling — a deliberate, recorded call.** The dispatch said "the `Maintenance` literal"; I
pinned **`IT_maintenance`**, the type id. Parity is with the five literals actually in that loop,
which are all type **ids** — no type *name* (Bug, Feature, Task, Defect, Epic) is pinned there — and
the acceptance criterion demands the chore leg be asserted BY TYPE ID. Pinning the name would have
been satisfied by the fixture's config map alone, which asserts nothing. Reversible in one amend if
the orchestrator wants the name pinned as well.

## Point 4's disclosure — gate parity, NOT coverage

T-03's `verify:` required-string loop is a **file-global `grep -qF`**. `IT_maintenance` is satisfied
by that text appearing anywhere in `tests/integration/test-gh-issue-types.py` — inside case A, in a
comment, in the fake's node table — so the entry buys **uniformity with the other pinned literals
and nothing about whether case E asserts it**. Case E's content stays bound only by its `CASE E:`
marker and by human review of T-04's verify run. This limitation is already the recorded panel
finding **PF-e74a2da89380cfa94f6b1693191d759d** (`med`, `batched_to_signature_review`); I did not
touch the loop's file-global nature, so that finding keeps reproducing verbatim.

## Writes — every one through plan-merge.py `amend`

1. `amend --key tasks --id T-03 --field intent --expect-sha256 84089b3… --value-file` → points 1, 2, 3.
2. `amend --key tasks --id T-03 --field verify --expect-sha256 9268144… --value-file` → point 4.

No other key, id or field was written. `panel.findings` still holds exactly 12 entries; `approval:`
is still `status: pending`.

```
 .../FEAT-55-issue-types-created-work/BRIEF.md      |   8 +-
 .../observations/harness-pm.md                     |   9 +
 .../FEAT-55-issue-types-created-work/plan.yaml     | 292 +++++++++++++++------
 3 files changed, 221 insertions(+), 88 deletions(-)
```

(Taken at exit. The same stat read `7 +` / `219 insertions` immediately after the two amends and
before I appended two observation bullets; the observations log is not a plan artifact.)

`BRIEF.md`'s `8 +-` is **c6's edit, not mine**: its sha256 is
`36a7c6ab3f284f3df75abb73fcdbd63ac3b3e604bfdd748ae46178cbe40eff5d`, character for character the
`36a7c6ab3f28…` the c5 goal-check recorded before this cycle. `plan.yaml` moved 278 → 292 changed
lines (+14 insertions, deletions unchanged at 85) — the c7 delta, T-03 only.

## LEAVE roll-call — all eight reproduce, re-checked on content after the edits

| finding | content anchor re-read post-edit |
|---|---|
| PF-56a2ce7a | `low` / `batched_to_signature_review`; "inert adopted marker written into approval-gated BRIEF SC-12" — BRIEF untouched, so unchanged |
| PF-452948136 | `med`; "T-06's verify omits tests/integration/test-gh-issue-types.py though T-06's own intent says to run it" — T-06's `verify:` not written this cycle |
| PF-e27f1c30 | `low`; "T-05 case F asserts a compat-mode rerun emits three MORE issue create argv" — T-05 untouched (and carries no `Maintenance`) |
| PF-0c12a033 | `low`; "'adopted' … behaviourally inert under absent-means-never-typed, yet three test cases pin it" — T-03 H/H2/J unchanged |
| PF-9a71cb9a | `info`; "character-identical 511-char eighth-purpose row duplicated" — T-11/T-12 untouched |
| PF-62b2b8ae | `med`; T-10 §6's two SKIP wordings both still present — "SKIP capability query failed on {target}" and the gh-cannot-reach-TARGET bullet |
| PF-e74a2da8 | `med`; the file-global `grep -qF` loop is still file-global — only one literal was inserted (see disclosure above) |
| PF-1280cd8f residue (a) | still live: T-10 §6 "resolve the type a real create would use — `gh_issue_types.type_for_parent(overrides)` read from the same harness.json" applied against the foreign TARGET |

**T-07 case D left exactly as written** — "Do not override Task in this case" plus its isolation
rationale. Closing SC-06 did not require touching it: the chore leg is discharged on the gh-sync
route at T-03, and T-07 D's `{"Bug": "Story", "parent": "Story"}` map carries no Task key, so its
trailing "still carry IT_task" remains true.

## Open questions

None. Q1 (widen) was executed; Q2's premise was verified false at source and is not restated.
