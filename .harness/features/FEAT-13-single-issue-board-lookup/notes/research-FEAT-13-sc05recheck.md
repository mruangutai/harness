# SC-05 re-check after fix01 — FEAT-13

**SC-05 is `met`.** Verdict changed from `partial`. Method `automated`, evidence `unit`, discharged
by a two-assertion chain, neither leg of which existed at the previous goal-check. Full tally is
now **10 met / 0 partial / 0 not_met**. Verified at `5e81612` in the worktree
`.claude/worktrees/FEAT-13-single-issue-board-lookup`. The nine other verdicts are carried forward
unchanged from `runs/goalcheck-product/digest.md:23-32` — nothing since touched what discharges
them — but **their line anchors are re-derived below, because fix01 inserted assertions above most
of them** and the `d4951c2` numbers no longer land. Re-anchoring a pointer is not re-deriving a
verdict.

## The criterion and its two clauses

`BRIEF.md:61-63` — *"Decompose's recovery path resolves the existing item id for an issue whose
state is closed, and issues no second board add for it."* `verify: automated  evidence: unit`.

| Clause | Discharged by | Status |
|---|---|---|
| no second board add | `test-factory-decompose.py:1028` (`project_item_add` not called) plus the `raise_on` trap at `:1018-1024` | was already met |
| resolves the id for a **closed** issue | `test-factory-gh.py:661-677` + `test-factory-decompose.py:1030-1038` | **newly met** |

## Why the query guard discharges the closed-issue clause

The clause is a behavioural statement whose mechanism is "the lookup is not state-scoped". Two
automated assertions now cover the whole mechanism, and both redden under the regression:

1. `test-factory-gh.py:661-677` parses the argument-name list inside `_ISSUE_ITEM_QUERY`'s
   `issue( ... )` selection (`factory_gh.py:295-305`) and requires exactly `["number"]`. A state
   argument of any spelling adds a name; swapping to a plural state-taking form leaves the regex
   `issue\s*\(([^)]*)\)` with no match and an empty list. Both `!= ["number"]`. `fix01-eng`
   mutation-measured both directions, including that a whitespace reformat correctly stays green
   (`feature.yaml` field `red_proof_required_and_given`).
2. `test-factory-decompose.py:1030-1038` pins that decompose's recovery path calls
   `issue_board_item_id(repo, issue_num, 3)` and then sets the field with the **resolved** id
   (`"ITEM-CLOSED"`), so a decompose-side regression that ignored or re-derived the id reddens too.

**The decisive test I applied was not "is the evidence direct?" but "can the method detect the
failure the criterion exists to detect?"** The failure is: a state filter enters the lookup, a
closed issue fails to resolve, decompose adds a second board item. Under fix01 that failure reddens
the suite in three independent places. At the previous goal-check it reddened nothing — the only
check named for the property (`:1026` then) asserted a call tuple, and `issue_board_item_id` takes
no query parameter, so it could not fail from that regression. That gap is what closed, and it
closed with production code byte-identical (`feature.yaml` field `fix01_verified_by_me`).

## The proof standard — how it resolves

`BRIEF.md:104-106` (the `## Constraints` bullet): *"Proof is unit call-shape assertions plus one
live read. No `factory_decompose` run against the live board, no fixture snapshot, no restore."*

That standard is what settles this. It does **not** require the unit layer to instantiate a closed
issue — it explicitly forbids the only technique that could, a live decompose run. The Recorder is
state-blind by construction (`test-factory-decompose.py:123-125`: `issue_board_item_id` is a dict
lookup on issue number, with no notion of state), and making the fake state-aware would assert the
fake's own behaviour, which is circular. So under the signed standard, a call-shape assertion plus
a structural pin on the query text **is** the unit-layer proof; there is no stronger one available
inside the standard.

**SC-05 is therefore not undischargeable as written, and no operator re-signature is owed.** That
is consistent with the orchestrator's routing rationale at `feature.yaml` field `the_one_cycle_charged` — approved-but-unmet,
fixed in a cycle. I recommended the operator route last time and the orchestrator overruled it; on
the evidence now in the tree, its call was correct and mine was not.

## What is corroboration, not evidence

The live read at `feature.yaml` field `req02_evidence_closed_by_me` — `gh issue view 216 --json state` returns `state: "CLOSED"`,
`closedAt 2026-08-11T01:06:42Z`, so T-02's live lookup did run against a closed issue and returned
the correct board item id — supplies the one semantic leg the unit layer cannot reach: that
GitHub's `repository.issue(number:)` is genuinely state-independent. It closes my prior Q3 and the
panel's Q2.

I am **not** crediting it as SC-05's automated evidence. SC-05's method is fixed at `automated` by
the signature, and admitting a live observation as its evidence would silently convert it to
`inspection`. It is recorded here as corroboration that the mechanism the automated chain pins is
the right mechanism. SC-05 stands on the two unit assertions alone; the live read means the
residual risk in that chain is now measured at zero rather than merely argued.

The two `issue_view` field-list pins added by fix01 (`test-factory-claim.py:391`,
`test-factory-land.py:235`) serve SC-06/SC-07 and are **not** credited to SC-05.

## Full tally — 10 met, 0 partial, 0 not_met

Anchors below are at `5e81612`, re-located by grepping each `check()` label the prior digest cited.
Verdicts are carried forward, not re-derived. All paths relative to
`.claude/skills/harness/bin/` unless noted.

| SC | Verdict | Anchor at `5e81612` | was at `d4951c2` |
|---|---|---|---|
| SC-01 | met | `test-factory-gh.py:647,651` | `:647,650,652` |
| SC-02 | met | `test-factory-decompose.py:956-957` \| `test-factory-land.py:219-220` \| `test-factory-claim.py:486-487` | land `:213-214`, claim `:475-476` |
| SC-03 | met | `test-factory-gh.py:688,700,712` (no raise) \| `:727-728` (unrecognised shape raises) | `:670-671,682-683,694-696` \| `:709-710` |
| SC-04 | met | `test-factory-gh.py:786-788` | `:768-771` |
| SC-05 | **met** | `test-factory-gh.py:661-677` + `test-factory-decompose.py:1028,1030-1038` | `partial` |
| SC-06 | met | `test-factory-claim.py:543-545` (unowned) \| `:557-560` (self-owned) | `:532-536` \| `:546-550` |
| SC-07 | met | `test-factory-land.py:348,352,355,358` | `:337,341,344,347` |
| SC-08 | met | `test-factory-integration.py:775` via stub branch `:179-211` | unchanged |
| SC-09 | met | `test-factory-claim.py:579,580-581,582` | `:568,569-570,571-572` |
| SC-10 | met (inspection) | `notes/receipt-harness-backend-dev-live-spot-check.md:1-2,39-53,67-72` | unchanged |

Only SC-08 and SC-10 kept their `d4951c2` anchors; every other automated row moved. SC-01's
`:650,652` and SC-09's decomposed sub-ranges were folded to the `check()` head lines they belong to.

**These assertions currently pass.** `feature.yaml` field `fix01_verified_by_me` records the
orchestrator's own re-run at tip: unit 10/10 scripts exit 0, integration 97/97 exit 0, with
production files byte-identical to the previous commit. That is the pass evidence behind every
`automated` row above, SC-05 included.

## Open

- Q1 (non-blocking): `test-factory-decompose.py`'s fixture name `"ITEM-CLOSED"` and the case label
  `"resume with a closed issue"` still read as though the fixture instantiates a closed issue. The
  block comment at `:992-1003` now states plainly that it does not, so the audit trap is closed for
  anyone who reads the comment; the identifiers alone still mislead. Cosmetic, no verdict rests on
  it, and renaming is not worth a cycle.
- The prior digest's Q2 (`plan.yaml:368`'s falsified `argv[:2]` instruction) is untouched by this
  re-check and remains as recorded — backlog, not an amendment.
