# board2-capture — the measurement point SC-03 is evaluated at

Taken by the main session under FEAT-16 T-07, BEFORE any live factory run and before the
`fleet.yaml` rewrite in the same task.

- **Date:** 2026-08-12
- **sha:** `a9558be6062f8b239f015c191c0a0a0349d44ff8`
- **Board:** `mruangutai` project **2** (kaya-ai), `PVT_kwHOAAases4Bc7h3`

## 1. Status field, verbatim

Command:

```
gh project field-list 2 --owner mruangutai --format json
```

Output:

```json
{"fields":[{"id":"PVTF_lAHOAAases4Bc7h3zhXgwt4","name":"Title","type":"ProjectV2Field"},{"id":"PVTF_lAHOAAases4Bc7h3zhXgwt8","name":"Assignees","type":"ProjectV2Field"},{"id":"PVTSSF_lAHOAAases4Bc7h3zhXgwuA","name":"Status","options":[{"id":"f75ad846","name":"Backlog"},{"id":"51284156","name":"Plan"},{"id":"8f8df98a","name":"Ready"},{"id":"47fc9ee4","name":"Building"},{"id":"8c67edb9","name":"Review"},{"id":"98236657","name":"Done"}],"type":"ProjectV2SingleSelectField"},{"id":"PVTF_lAHOAAases4Bc7h3zhXgwuE","name":"Labels","type":"ProjectV2Field"},{"id":"PVTF_lAHOAAases4Bc7h3zhXgwuI","name":"Linked pull requests","type":"ProjectV2Field"},{"id":"PVTF_lAHOAAases4Bc7h3zhXgwuM","name":"Milestone","type":"ProjectV2Field"},{"id":"PVTF_lAHOAAases4Bc7h3zhXgwuQ","name":"Repository","type":"ProjectV2Field"},{"id":"PVTF_lAHOAAases4Bc7h3zhXgwuU","name":"Reviewers","type":"ProjectV2Field"},{"id":"PVTF_lAHOAAases4Bc7h3zhXgwuY","name":"Parent issue","type":"ProjectV2Field"},{"id":"PVTF_lAHOAAases4Bc7h3zhXgwuc","name":"Sub-issues progress","type":"ProjectV2Field"},{"id":"PVTF_lAHOAAases4Bc7h3zhXgwug","name":"Created","type":"ProjectV2Field"},{"id":"PVTF_lAHOAAases4Bc7h3zhXgwuk","name":"Updated","type":"ProjectV2Field"},{"id":"PVTF_lAHOAAases4Bc7h3zhXgwuo","name":"Closed","type":"ProjectV2Field"},{"id":"PVTSSF_lAHOAAases4Bc7h3zhYavpQ","name":"Priority","options":[{"id":"f2ad13cf","name":"Urgent"},{"id":"72e4efb5","name":"High"},{"id":"fd9c343c","name":"Medium"},{"id":"b78ede2d","name":"Low"}],"type":"ProjectV2SingleSelectField"}],"totalCount":14}

```

**Six options, in this order: Backlog, Plan, Ready, Building, Review, Done.** Board 3 was read
with the same command and offers the same six names in the same order. Both halves of the
precondition are confirmed, not assumed.

## 2. Item distribution, per status

Command — `gh api graphql` over `projectV2` items, paginated at 100, tallied on
`fieldValueByName(name: "Status")`:

```
query($q:ID!,$c:String){node(id:$q){... on ProjectV2{items(first:100,after:$c){
  pageInfo{hasNextPage endCursor}
  nodes{fieldValueByName(name:"Status"){... on ProjectV2ItemFieldSingleSelectValue{name}}}}}}}
```

| Status | Items |
|---|---|
| Backlog | 82 |
| Plan | 0 |
| Ready | 0 |
| Building | 11 |
| Review | 0 |
| Done | 118 |
| **Total** | **211** |

**This matches the figures the plan was signed on, exactly.** T-07's intent requires 211 items,
118 Done, 82 Backlog, 11 Building and zero in each of Plan, Ready and Review. It says to STOP and
report on any disagreement, because SC-03 and SC-07 rest on these numbers and a mismatch needs
re-signing rather than repairing. There is no disagreement.

## 3. Status option ids, read from the same field query

| Option | id |
|---|---|
| Backlog | `f75ad846` |
| Plan | `51284156` |
| Ready | `8f8df98a` |
| Building | `47fc9ee4` |
| Review | `8c67edb9` |
| Done | `98236657` |

## 4. The prior reading — HISTORY, not current state

At sha `d97f5ea` on **2026-08-11** this same board offered **three** options, and the ids are what
make the comparison mean anything:

| Then (2026-08-11) | id | Now |
|---|---|---|
| Todo | `f75ad846` | Backlog |
| In Progress | `47fc9ee4` | Building |
| Done | `98236657` | Done |

with 118 Done, 82 Todo and 11 In Progress — the same three counts standing today under the new
names.

**All three ids survive.** That is what proves the change was a RENAME and not a delete-and-recreate,
and therefore that no item was moved between statuses. Renaming a Projects v2 option keeps its id;
deleting and recreating one does not.

Recorded here as the prior reading it is. It is not current state, and nothing in this file should be
read as asserting that board 2 offers three options today — it offers six.

## Why the name comparison and the id comparison are two rules, not one

The cross-board precondition compares **names**, never ids. Backlog, Building and Done carry
IDENTICAL option ids on board 2 and board 3 — they are GitHub's default template ids — so any
cross-board assertion written on ids is vacuous and passes whatever either board says.

The id check above is a different rule that happens to sit beside it: it is a **within-board-2,
across-time anchor**. There, ids are exactly right. The two rules must not be merged.
