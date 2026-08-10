# Probe — blocked_by edge idempotence, MEASURED

Run by harness-orchestrator, 2026-08-08, live against `mruangutai/harness`.

`edges-delta-eng` raised E-1 and said the deciding fact was unmeasured and unmeasurable by its
squad — *"Needs `Bash` and `gh` … leads have no shell."* It is measured now.

**BLUF: re-POSTing an existing `blocked_by` edge returns HTTP 422. E-1 is REAL, and under 7b's
current fatal rule it is a deterministic wedge. Separately, read-before-write IS available — the
premise that it is not is false at the API level.**

## Measured

| Question | Answer | Evidence |
|---|---|---|
| Does re-POSTing an existing edge 422 or succeed? | **422** — `"Validation failed: Target issue has already been taken"` | `gh api repos/mruangutai/harness/issues/186/dependencies/blocked_by -F issue_id=5098018286` |
| Did the probe mutate the graph? | **No** — #186 still has exactly 1 blocker, #183, before and after | same endpoint, GET |
| Is there a GET for `blocked_by`? | **YES, it works** — returns `[]` for an issue with no blockers, a list otherwise | `gh api repos/mruangutai/harness/issues/197/dependencies/blocked_by` → `[]`, exit 0 |
| Existing edges in the repo | #186 ← #183, #188 ← one blocker | scan of issues 150-200 |
| Incidental | issue #185 is DELETED — the endpoint returns HTTP 410, not an empty list | same scan |

## What this decides

1. **E-1 is real, not hypothetical.** A crash between a successful edge POST and its `feature.yaml`
   receipt write leaves the ledger under-recording. The re-run re-POSTs, gets 422, and 7b's rule
   *"an edge write that raises GhError is FATAL"* turns that into exit 2 — **reproducibly**, every
   re-run, with the operator's only recovery being to hand-edit `feature.yaml` and no diagnostic
   pointing there.
2. **The error shape is now known, so the narrowing clause can be written correctly.** eng-lead's
   *alternative discharge* — a `GhError` indicating the edge already exists records the receipt and
   continues — was blocked only on not knowing the shape. It is HTTP **422** with a message
   containing **"already been taken"**.
3. **"Read-before-write is unavailable for the dependency half" is FALSE as stated.** The gap is in
   `gh_issues.py`, which has no read builder — not in the API, which has a working GET. That is a
   library gap of one function, and D-14's justification for choosing a ledger should say so rather
   than claim the read does not exist. The ledger may still be the right choice; the reason given
   for it is not accurate.

## Not probed

Whether `gh issue edit --add-label` rejects an undefined label — still deliberately unprobed, still
mitigated by ensuring every factory label.

---

## Part 2 — the hierarchy half, measured (answers final2-product Q1)

`final2-product` closed E-1's `blocked_by` half but left the **hierarchy** half as a stated
residual, asking whether a repeat `sub_issues` attach 422 means *this edge exists* or *this child
already has a different parent*. Measured live, same method.

| Question | Answer |
|---|---|
| Re-attach an existing pair (#182 → #181) | **HTTP 422**, message: `Issue may not contain duplicate sub-issues and Sub issue may only have one parent` |
| Did it mutate anything | **No** — #182's parent is still #181 |

**The message CONFLATES BOTH CAUSES in one string.** There is no way to tell "the edge already
exists" from "the child already has a different parent" by the response alone.

**So the conservative scoping is CORRECT and now evidenced, not merely cautious.** Narrowing the
fatal rule must stay scoped to `blocked_by`, whose message (`Target issue has already been taken`)
is unambiguous. Extending it to `sub_issues` would file a false receipt whenever the real cause is a
different parent — silently mis-reporting the hierarchy, which is worse than exiting 2. The residual
stands as written and needs no further work.

Note the two endpoints return **different** strings, so a tool can distinguish endpoint-by-endpoint;
it just cannot disambiguate *within* `sub_issues`.
