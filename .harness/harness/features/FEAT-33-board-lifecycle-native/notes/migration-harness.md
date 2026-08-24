# Migration report — board 3, mruangutai/harness

Date: 2026-08-23. Board: **3** (`mruangutai/harness`). Run by the operator's hand, main-session
direct. First real execution of `board_lifecycle.py` against a live board.

## Outcome

**13 findings → 0 findings.** `audit` exits **0**. Board 3 is clean.

| | count |
|---|---|
| before | 13 |
| fixed by `reconcile --apply` | 8 |
| fixed by closing two parents (operator ruling) | 3 |
| fixed by ADDING two cards (later operator ruling, see the last section) | 2 |
| **remaining** | **0** |

**THIS SUMMARY WAS REWRITTEN 2026-08-23 AND THE REASON IS THE POINT.** As first written it said
*"13 findings → 2 findings. Both survivors are ACCEPTED by operator ruling, recorded below. This
report does NOT claim zero findings, and the plan's verify has been corrected to match"*, and the
table's last row read *"accepted, remaining | 2"*. Every part of that was true under the FIRST
ruling and false under the second. When the ruling reversed, a new section was appended at the end
of this file and **this summary was left standing** — so the document contradicted itself, with the
false half at the top.

**That cost real work.** A later reader took the archived capture
`migration-harness-audit-after-2-accepted.txt` for the current one, wrote "board 3 finished at 2
accepted findings" into `BRIEF.md`, and had to retract it. An appended correction does not repair a
document a reader stops at. The history below is kept in full and quoted as superseded; what changed
is that the summary no longer disagrees with it.

**Which capture is which, because the names differ by one word:**

| file | what it is |
|---|---|
| `migration-harness-audit-after.txt` | **CURRENT** — `0 finding(s)`, written at `ace0b06` |
| `migration-harness-audit-after-2-accepted.txt` | **ARCHIVED** — `2 finding(s)`, the state at `e8a6058` |

## What was fixed, and by what

**Eight LABEL findings, by `reconcile --apply`.** Issues #358, #357, #349, #176, #175, #173, #43
and #12 were `not_planned` and carried no `abandoned` label. They carry it now.

**Three findings by closing two issues.** #85 (FEAT-08-remove-cost-tracking) and #98
(FEAT-09-plan-time-route-check) were **OPEN** while their features recorded `status: Done` with
`pr` 131 and 136. Their `parent_origin` is `none`, so `ship` had no recorded origin to act on and
left them open. Closed with `--reason completed`, which is what `ship` would have done.

**That close is live proof the native mechanism works.** GitHub's `Item closed` workflow moved
both cards to `Done` on its own, unaided, within twenty seconds. The harness wrote no `Done`
column — which is the whole design this feature rests on.

**One finding was the harness's own and the cause was fixed, not the symptom.** The audit reported
FEAT-33 recording `Ready` while its parent #675 read `Building`. `feature.json` is the authority,
so `reconcile` would have moved the card BACKWARDS to Ready. The real defect: `start-task` writes
the card and nothing had recorded the phase. `gh-sync.py status <dir> Building` fixed it.

## The two accepted findings — SUPERSEDED, kept as the record of the first ruling

```
STATUS: FEAT-06-team-layer-inv6 records status 'Done' (column 'Done') but its parent #25 reads None
STATUS: FEAT-07-verify-teeth-batch-probe records status 'Done' (column 'Done') but its parent #47 reads None
```

#25 closed COMPLETED on 2026-08-04, #47 on 2026-08-05. **Neither was ever added to board 3**, so
no card existed for `Item closed` to move. Both features are correctly `Done` with `pr` 45 and 77.

**SUPERSEDED. The FIRST ruling, 2026-08-23, quoted verbatim so the reasoning survives:** *"record as
accepted, do not add cards. Adding a card for work that finished weeks before the board tracked it
writes board history that was never true. The audit will report these two on this board until someone
removes them by hand."* **On revisiting the same day the operator ruled the other way: add the cards.**
Both were added, GitHub's native `Item closed` workflow placed both at `Done` unaided, and the audit
now reports zero. The last section of this file records what was run and what it measured.

## No DECLARATION and no WORKFLOW finding

T-02's six-key declaration is correct on board 3, and all three required workflows are enabled:

```
Item closed:         enabled=true
Auto-close issue:    enabled=true
Pull request merged: enabled=true
```

## Observation for the operator, NOT a finding

Board 3 has **`Pull request linked to issue` DISABLED**; board 2 has it **enabled**. Measured today,
confirming the 2026-08-22 reading. The audit does not flag it because it is not one of the three
required workflows. Named here so the asymmetry is on the record rather than rediscovered.

## SC-10's negative clause

```
git diff --name-only $(git merge-base main HEAD)..HEAD -- the four DEC-174 files:
(empty above = no edit reached any of the four)
```

The list is **four files, not five**: `check-state.sh` left it under D-24, because D-23's ruling
makes INV-26 fire on every done task with a deliberately-open sub-issue, and T-22 is the operator's
own cutover that fixes it.

## The verify was unsatisfiable, and is corrected — SUPERSEDED TWICE, kept for the reasoning

T-11's verify required `board_lifecycle.py audit` to exit 0 and this file to contain the string
`0 findings`.

**SUPERSEDED — this whole section reasons from the first ruling.** It argued: *"Neither can hold.
`reconcile` will not write a `Done` column — that column is GitHub's, by the station-writer map — so
the two accepted findings cannot be cleared by the tool, and the operator ruled not to clear them by
hand. An `audit` that exits 0 is therefore impossible on this board."* **The first sentence about
`reconcile` is still TRUE and still binding — the tool genuinely will not write a `Done` column
(`_fixable` excludes a `Done`-status STATUS finding, D-22). What is FALSE is the conclusion: an audit
exiting 0 was not impossible, because a HUMAN adding the two cards was never ruled out, and that is
what the second ruling directed.** A tool's limit was mistaken for the board's limit.

And `grep -q "0 findings"` reads a report this same session writes: it is satisfied by typing the
string, so it was never evidence. Typing it here would have been a lie that passed a gate.

**SUPERSEDED, and it reddened exactly as its own logic invited.** It read: *"The verify now asserts
what is actually true and what would actually break: `audit` reports exactly the two accepted findings
and nothing else. A third finding, or the loss of one of these two, reddens it."* Adding the cards IS
"the loss of one of these two", twice over — so pinning the assertion to the current finding count
made it fail the moment the board improved. `T-11`'s verify has been corrected again, and now asserts
invariants rather than a snapshot: the ARCHIVED capture proves `audit` detects a real finding, the
CURRENT capture proves the delivered zero, and both are read with `git show HEAD:` so an uncommitted
capture reddens instead of passing.

## Captures

Before: `audit-before.txt` content is reproduced in the run log; the dry-run write list and the
apply output likewise. Retained in this feature's notes as the three files below.

## SC-04's two residual findings, resolved by adding the cards (2026-08-23)

The audit's first "after" capture reported `2 finding(s)`, not the zero SC-04 asks for. Both were
STATUS findings: `FEAT-06` and `FEAT-07` record status `Done`, but their parents #25 and #47 read
`None` — no card at all. The cause is historical: both issues were closed before board 3 existed,
so nothing ever created a card for them.

That capture is kept as `migration-harness-audit-after-2-accepted.txt`. The first ruling was to
accept the two and add no cards. On revisiting, the operator ruled the other way: add them.

**The tool refuses to do this itself, on purpose.** `_fixable` (`board_lifecycle.py:733`) excludes
a Done-status STATUS finding — "reconcile does not move a card to the done station on its say
alone, so it is left for a human" (D-22). A hand-add is what that rule intends, not a workaround
for it.

What was run:

```
gh project item-add 3 --owner mruangutai --url https://github.com/mruangutai/harness/issues/25
gh project item-add 3 --owner mruangutai --url https://github.com/mruangutai/harness/issues/47
```

**Measured, and worth recording because nothing here predicted it: the native `Item closed`
workflow fires when an ALREADY-CLOSED issue is added to the board, not only when an open issue is
closed.** Both cards landed at `Done` with no column write of any kind. Verified per issue through
`projectItems.fieldValueByName(name: "Status")`, because `gh project item-list` truncates at 500
items and board 3 now holds at least that many — the item-list read found #47 and silently missed
#25, which the direct query then showed sitting at `Done` all along.

The re-run audit is `migration-harness-audit-after.txt`: `0 finding(s)`, exit 0. SC-04 is met as
written, with no criterion amended.
