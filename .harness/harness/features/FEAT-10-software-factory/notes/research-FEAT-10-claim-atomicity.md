# Research — an atomic claim primitive, and the board read that does not silently drop work

Measured by harness-pm, 2026-08-08, against the live `mruangutai` account, `gh version 2.92.0`.
Inputs to the FEAT-10 plan revision. Justification only — the instructions live in `plan.yaml`.

**BLUF: the claim moves to git ref creation, which is a server-side create-if-absent, and the board
read moves to a server-side `--query` filter. Both are measured below. Neither needs new scope.**

## 1. Issue assignment cannot carry the claim

`gh issue edit --add-assignee` is additive. Two agents racing both succeed, both observe a
two-element assignee set, and neither can conclude it won. The failure is open, not safe: the issue
ends up marked, stationed `ready`, owned by nobody. This is the root defect both reviews reached.

## 2. Git ref creation is a create-if-absent, and it is the primitive

```
gh api -X POST repos/mruangutai/harness/git/refs -f ref=refs/heads/main -f sha=<main sha>
```

Measured, against a ref that already exists:

| Channel | Value |
|---|---|
| process exit | `1` |
| stdout | `{"message":"Reference already exists", ..., "status":"422"}` |
| stderr | `gh: Reference already exists (HTTP 422)` |

The conflict is reported on both streams and is discriminable from any other failure. Git refs are
compare-and-swap by construction and the REST create endpoint is create-only, so exactly one
concurrent creator can receive `201`.

**Residual risk, stated rather than assumed:** that concurrent creates *serialise* is inferred from
git ref semantics and from the endpoint being create-only. It is not measured here — measuring it
needs two real agents racing on a live repo, which is SC-07's job. What IS measured is that the
endpoint refuses an existing ref, which is the property additive assignment provably lacks.

The claim ref is `refs/heads/factory/issue-<n>` — the branch the journey already needs. Releasing an
abandoned claim is one command:
`gh api -X DELETE repos/<owner/name>/git/refs/heads/factory/issue-<n>`.

## 3. The board read: server-side filtering, measured on board 3 (150 items)

| `--query` | `totalCount` |
|---|---|
| none | 150 |
| `is:open` | 70 |
| `-status:Done` | 70 |
| `status:Ready` | **1** |
| `status:NoSuchOption` | **0** |

Three consequences:

1. The ready column is bounded by the station field, not by board size. The tool never needs the
   item payload's absent `state` key — the station field is the lifecycle signal.
2. `totalCount` reports the **untruncated** total: at `--limit 30` the response carried
   `{"got": 30, "total": 150}`. So truncation is detectable as `totalCount > len(items)` — a real
   guard, not an equality-against-limit heuristic that only fires at the boundary.
3. **A station option name that does not exist on the board returns zero items and exit 0.** A typo
   in `fleet.yaml` is therefore indistinguishable from an empty queue, forever. This is a silent
   failure of exactly the class SC-10 exists to prevent, and it is new — no review named it. The
   remedy is to validate the three station option names against `gh project field-list` before the
   first poll and refuse with exit 2 naming the option and the field.

Station option names containing a space would need quoting inside the query string. C-1's naming
rule (one word) is what keeps that safe, which makes the rule load-bearing rather than cosmetic —
it is why T-01 now cites it.

## 4. What this does not solve

The board still grows monotonically: closed issues remain as items (probe `notes/probe-board-limits.md`
measured #181, #182, #183, #197 all closed and all still present). Filtering makes the read correct at
any board size; it does not reap. Archiving stays the operator's, through the board UI, and effort
#186 owns automating it. Recorded as a limitation in `decisions:`, not left implicit.
