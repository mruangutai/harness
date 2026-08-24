# T-22 record — INV-26 widened, and its own verify proves nothing

Executed by the operator's hand under DEC-174. `check-state.sh` and `test-check-state.py` are
named in the enforcement layer; no squad touched either.

## The change

`_accept` replaces the single `_want` comparison. A recorded sub-issue whose task status is
`done` now satisfies INV-26 at the **done, review OR building** station — and **only while the
feature's own `feature.json` status is `Review`**. Outside that status the expectation is
unchanged and stays exactly the done station.

Located by symbol, not by the plan's line numbers, which had moved: `_EXPECT` is at
`check-state.sh:1275`, not `:1234`. FEAT-26's INV-28 is already present and was not touched.

## THE VERIFY IS A GREEN ASSERTION THAT CANNOT GO RED. READ THIS BEFORE TRUSTING IT.

T-22's verify is `! check-state.sh | grep -E "INV-26 .*should read"`.

It passed **before** the change and after it. There were no INV-26 station findings to remove,
because FEAT-33's own `feature.json` status is `Ready`, so the widening does not apply to this
tree yet. **The verify would pass identically if the edit had done nothing at all.**

That is the ninth green-but-unfalsifiable assertion found in this repo in three days, and this
one is in the plan's own verify clause. The tests below are the only evidence that the widening
works.

## DEC-174 amendment 4 proof: the finding sets

| | lines | rc |
|---|---|---|
| before | 442 | 1 |
| after  | 442 | 1 |

`diff <(sort before) <(sort after)` → **empty**. Captures kept as `check-state-before-T-22.txt`
and `check-state-after-T-22.txt`.

The amendment asks that the two differ **only** by the INV-26 station findings the change
removes. They differ by nothing, which satisfies it — and confirms the point above: there were
none to remove.

## The tests, and the red proof

Four cases in `test-check-state.py`, because the accept set has three members and the bound has
two sides. Three fixtures cannot see a widening that leaked past its bound.

| case | fixture | expected |
|---|---|---|
| v.T22a | status Review, task done, card Review | ACCEPTED |
| v.T22b | status Review, task done, card Building | ACCEPTED |
| v.T22c | status **Building**, task done, card Review | VIOLATION |
| v.T22d | status Review, task done, card **Backlog** | VIOLATION |

**Red-proved against the pre-T-22 baseline** — `git show HEAD:<path> > <path>`, never the shared
stash (#780), restored by `cp` and confirmed byte-identical by `diff -q`:

```
FAIL - (v.T22a) ...card reading Review is ACCEPTED
FAIL - (v.T22b) ...card reading Building is ACCEPTED
ok   - (v.T22c) THE BOUND ...
ok   - (v.T22d) the widening does NOT reach Backlog ...
```

The split is exactly right. The two acceptance cases are the widening and they go red without it.
The two violation cases are the bound, which existed before, and they stay green — so they are
not measuring the change, they are guarding it.

## THE PLAN ASKED FOR A CASE THAT CANNOT EXIST

Its wording: *"the same feature at status Done with the same card is still a VIOLATION"*.

At status `Done` the **terminal exemption** `continue`s before the per-task comparison is ever
reached — `check-state.sh:1295`, and existing case v.3 asserts exactly that silence. So **no
fixture at status Done can produce an INV-26 station finding at all**, and a case written to the
plan's words would have been green while testing nothing.

The honest test of the bound is a non-terminal status. `v.T22c` uses `Building`.

## Bounded on purpose

The code comment records why the widening is conditional on `feature.json` status rather than
unconditional: an unconditional widening would silence the mis-columned done card the invariant
was extended to catch. Case v.T22c is that sentence as an assertion.

## Not touched

`check-domain.sh`, `bash-write-guard.sh`, `validate-digest.py`, `check-plan-routes.py` — SC-10's
four-file list. No other invariant. FEAT-26's INV-28.
