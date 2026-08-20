# Regrade — SC-08 and SC-09, amended text — FEAT-29-graphql-budget

Independent grade of the AMENDED 2026-08-20 text only. Formed before reading
`notes/research-goalcheck-FEAT-29.md` (which grades the pre-amendment text and is superseded here).

## Verdict

| SC | Verdict | Driving limb | Wrong, or unproven |
|---|---|---|---|
| SC-08 | **unmet** | limb 3, the bare-corrected-number clause | genuinely wrong (one live document), and the clause is grammatically ambiguous |
| SC-09 | **unmet** | limb 2, the committed-tree clause, at the pinned `review_sha` | merely unproven — a stale pin, not a defect in the tree |

Neither is routable to a fix cycle: budget is 10 of 10 (`feature.json cycles_used`). Both go to the
operator. **SC-09 is closable by a re-pin with no code change.** SC-08 needs one line edited or a
ruling on wording.

## SC-08 — three limbs

**Limb 1, the in-place correction: MET.**
`.harness/notes/grilling-graphql-cost-2026-08-10.md:13-22` — the 31-point bullet is struck in place
and replaced with 506 points "on board 3 with 473 items, at commit `6bbd706`", the range quoted as
490-506, and 608 recorded explicitly as a contaminated upper bound with the containment argument
(`check-state.sh` CONTAINS the call). The date marker "STRUCK 2026-08-19 (#571)" is on `:17`. The
companion strikes are at `:47` and `:61-64`, the latter recording the 31 as *unreconciled* rather
than explained. Committed: `git show 4f2e5d0:.harness/notes/grilling-graphql-cost-2026-08-10.md`
returns the corrected text.

**Limb 2, no in-force document asserts item-list is cheap enough to ignore: MET.**
In-force set derived from `status` in every `.harness/harness/features/*/feature.json`: 25 features
read `Done`, FEAT-19 reads `Abandoned`, and only FEAT-26 (`Plan`), FEAT-28 (`Plan`) and FEAT-29
(`Building`) are live. Everything else that is in force is non-feature: `.harness/notes/`,
`.harness/harness/docs/`, `CLAUDE.md`, `.harness/README.md`, `.claude/`, `docs/`, both expertise
trees.

Searches actually run, over exactly that set:
- `grep -rn "item-list|item_list|project_items" --include=*.md` over the in-force paths.
- `grep -rn "31-point|31 point|31 points"` over `.harness/`, `docs/`, `.claude/`.

Result: the only surviving cheap-enough-to-ignore assertions are in `FEAT-11-graphql-field-resolve`
(`feature.json status: Done`) and `FEAT-13-single-issue-board-lookup` (`Done`) — frozen history, put
out of scope by the amendment's own text. Every in-force hit is either struck
(`grilling-graphql-cost-2026-08-10.md:14,47,61`), a quotation of the old claim under refutation
(`notes/research-plan-product.md:115-116`), or the opposite claim: `DECISIONS.md:3510-3524` (DEC-146)
*removes* a whole-board `item-list` lookup, and
`.harness/notes/grilling-board-read-lookups-2026-08-10.md:19` scopes the claim poll out on
list-by-nature grounds while stating it "keeps costing what it costs" — not a cheapness claim.

**Limb 3, no bare corrected number without its condition: UNMET.**

`.harness/harness/features/FEAT-29-graphql-budget/STATE.md:14` reads
"**The result: `check-state.sh` costs 5 GraphQL points against a 506 baseline**, both differenced
across real runs." 506 is the corrected figure limb 1 installed. STATE.md carries no board number,
no board item count and no commit sha for it anywhere in its 40 lines —
`grep -n "board 3\|473\|474\|6bbd706" STATE.md` matches only `:15`, and that is `board_items: 4` for
**board 6**, a different measurement. FEAT-29 is `Building`, so STATE.md is in force, not history.
This is exactly the failure the note's own recording rule
(`grilling-graphql-cost-2026-08-10.md:85-90`) was written to prevent: "every GraphQL cost figure
recorded anywhere in this repository must carry three conditions".

Secondary, weaker: `.harness/notes/grilling-board-read-lookups-2026-08-10.md:77` records
`item-list 3 --limit 500` at 203 points as superseding the 31 (`:88-89`), under a header at `:74-76`
giving board 3, 163 items and the date — but **no commit sha**. Partially conditioned, not bare.

Not counted against the criterion: `.claude/skills/harness/bin/gh_cost_log.py:4-6` states 506 bare
but cites `notes/measurement-before.md` in the same sentence, so the condition is one hop away
rather than absent. Judgement call, stated so it can be overturned.

**The ambiguity that decides SC-08, and it is the operator's to settle.**
"and no *such document* states a bare corrected number without its condition" has two readings:
- (a) *such* = still in force → quantifies over every live document → **unmet**, via STATE.md:14.
- (b) *such* = a document asserting item-list is cheap → limb 2 already established the set is empty
  → **vacuously met**, and the clause can never fail.

I grade (a). Reading (b) makes the clause true by construction, which is not a criterion, and the
feature's own recording rule quantifies over the whole repository, which is reading (a)'s scope.

## SC-09 — two limbs

**Limb 1, no 10-second `gh pr checks` polling: NOT-ASSESSED, and not assessable from files.**
Searches run at both HEAD and `4f2e5d0`: `grep -rn "pr checks"`, `grep -rni
"10-second|10 second|--interval|sleep 10|watch --interval"`, `grep -rni "poll"` over `.claude/`,
`.harness/harness/docs/` and `CLAUDE.md`. No instruction to poll at any interval exists in the tree
now — **and none existed before the change either**: `git log -S "10 seconds" --all` and
`git log -S "sleep 10" --all` surface only unrelated `--resolve` timeout probes from FEAT-09/FEAT-16.
The 10-second polling was live main-session behaviour typed into Bash, never a recorded rule, so an
absence-grep here was already empty and discriminates nothing. This limb is carried entirely by
limb 2 — the recorded prohibition is the only durable instrument that exists.

**Limb 2, the rule present in the COMMITTED tree: UNMET AT THE PINNED SHA, MET AT HEAD.**

The discriminating fact:

```
git show 4f2e5d0:CLAUDE.md | grep -n "wait loop\|Monitor\|run_in_background"   -> no match
git show HEAD:CLAUDE.md    | grep -n "wait loop"                              -> :55 matches
```

`feature.json review_sha` is `4f2e5d0`. The rule landed in `9c9785f` ("CLAUDE.md: the wait-loop rule
lands in the tree"), and `git merge-base --is-ancestor 9c9785f 4f2e5d0` reports **not an ancestor** —
the rule is three commits *after* the pin (`4f2e5d0 < 9c9785f < 444c611 < a67302f < 4881173 = HEAD`).
The rule text at `CLAUDE.md:55` names both replacements, Monitor and `run_in_background`, and states
the reason (a foreground timeout detaches rather than kills). `git status --porcelain CLAUDE.md` is
empty, so the working copy equals HEAD — the working-copy-only failure the clause guards against does
not obtain at HEAD.

**So the tree is right and the pin is stale.** `444c611` — the very commit that wrote this amended
criterion — is also after the pin, meaning the criterion was authored against a tree the pin does not
name. `8c2c24d` ("FEAT-29: re-pin review_sha at the tip") shows re-pinning is this feature's
established mechanism and it was not run after `9c9785f`.

I do not resolve this by adopting the convenient reading. Graded against the sha the feature pins for
review, the rule is absent. The remedy is a one-step operator action — re-pin `review_sha` to
`9c9785f` or later — after which limb 2 is met on the same instrument. `STATE.md:19-21` already
verifies against `444c611`, a sha `feature.json` does not name; that inconsistency between the two
artifacts is the actual finding.

## Can either be met as written?

- **SC-08 can** — under reading (a), one line in STATE.md needs its board, item count and commit.
  Under reading (b) it is already met and the clause is inert. Either way the sentence is defective:
  it should say which documents it quantifies over.
- **SC-09 can**, with no code change, once `review_sha` names a sha containing `9c9785f`. Limb 1
  remains permanently ungradable from artifacts and should have been `uat` rather than `inspection` —
  a plan-level finding, not a fix.

## Post-hoc comparison — read AFTER the above was written

`notes/research-goalcheck-FEAT-29.md` grades the pre-amendment text and reaches unmet on both. Same
outcome, different causes — and one live disagreement.

- **SC-08.** It fails on the FEAT-11 surviving-document clause (`:41-47`), which the amendment
  explicitly retired; I pass that limb and fail on limb 3, which it did not grade. It reads limb 3
  the same way I do — its `Q2` calls STATE.md:14 "a bare corrected number, the exact shape SC-08's
  second absence clause forbids" — so reading (a) has two independent readers. **The disagreement is
  scope:** it declined to grade STATE.md because the text was "introduced after the pin". I do grade
  it. SC-08 says *still in force*, not *at the pin*; scoping an in-force clause to a pinned sha means
  a document edited after the pin can never violate it, which is the same true-by-construction
  failure the amendment was written to remove.
- **SC-09.** Its `:66-68` treats limbs 1 and 2 as "satisfied *by the working-tree text*" and fails
  the criterion on the cost-citation clause the amendment has since DROPPED. The committed-tree
  requirement is precisely what that working-tree reading sidestepped, and it is now the only thing
  failing. Its factual base has also moved: it recorded `M CLAUDE.md` uncommitted; the rule has since
  been committed at `9c9785f`. The behaviour was fixed, the pin was not moved.

No verdict of mine was revised to match it.
