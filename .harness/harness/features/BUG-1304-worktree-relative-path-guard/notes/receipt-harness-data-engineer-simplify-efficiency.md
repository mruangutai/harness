# Receipt — harness-data-engineer — simplify/efficiency — BUG-1304

## BLUF

Measured on today's real checkout (18 linked worktrees, real `.inflight-claims.json`
contents): `claim_worktrees()` costs **~1.24ms per governed write** (`time.perf_counter`,
200 iterations, real fleet data, throwaway harness at `/tmp/bench_efficiency.py` and
`/tmp/bench_efficiency2.py`, not committed). Against the ~38ms interpreter-startup floor
the guard already pays per write (figure taken from `linked_worktrees`'s own docstring,
`harness_boundary.py:165-167`), this is **~3% overhead — negligible**. One real, cheap,
low-risk recomputation was found and is reported below; current impact is unmeasurable
but it is unbounded in principle, so it is worth the trivial fix. **Recommendation: fix, low priority.**

## Tally for one governed write (real numbers)

- **Registry file reads:** N = 1 (owner) + `len(linked_worktrees(owner_root))` = 18 today,
  so **19 file opens+reads**, one per root in `claim_worktrees`'s `roots` loop
  (`harness_boundary.py:260-266`).
- **JSON parses:** **2× per registry**, not 1× — `live_claims` (`inflight_registry.py:290-334`)
  calls `json.loads(text)` once itself (line 302, to validate `schema_version`/`claims`
  shape) and then calls `_parse(text, path)` (line 319), which calls `json.loads` on the
  *same already-read text* again (line 71). Confirmed by monkey-patching `json.loads` and
  counting: 2 calls per `live_claims` invocation, both on the owner registry (0 claims) and
  a worktree registry (5 claims, 1 live for this agent). Measured cost of the double parse
  is sub-microsecond on these files (a few hundred bytes to a few KB) — real, but not worth
  the ceiling slot; not recommended.
- **Worktree resolutions (`linked_worktrees` calls, each a `listdir` + one `gitdir` pointer
  read per linked worktree — no `git` subprocess, confirmed in the source):** **not 1, not
  N — 1 + C**, where C = the number of *live claims matching `agent_type`* found across
  every registry. `claim_worktrees` computes `linked_worktrees(owner_root)` once up front
  (line 260) to build `roots`, but then for **every matching claim** it calls
  `worktree_for_feature(owner_root, claim["feature"])` (line 268), which **recomputes
  `linked_worktrees(owner_root)` from scratch internally** (`harness_boundary.py:229`) —
  this is the "recomputed per claim where per-call would do" case the dispatch asked me
  to check for, and it is real.
- **Enumeration of the linked-worktree list:** confirmed 1+C times per governed write, not
  1, by instrumented counting (see below).

## Measurement (real fleet + synthetic worst case)

- Real fleet today: 18 registries, only 2 non-empty, 7 claims total, **at most 1 claim
  live for any single `agent_type`** (checked every registry's contents directly). With
  C=1, `claim_worktrees` measured at 1.24ms/call (200 iters); `linked_worktrees` alone
  measured at 0.47ms/call (matches the docstring's own prior figure of 0.371ms — same
  order, consistent with today's 18 vs. the docstring's 5-worktree fixture).
- Synthetic worst case (monkey-patched `live_claims` to return 8 matching claims spread
  across 8 real feature ids, `linked_worktrees` left real and instrumented): confirmed
  9 = 1+8 `linked_worktrees` invocations per `claim_worktrees` call, cost climbing to
  4.34ms/call — i.e. the wasted share is ~(C−1)×0.47ms, real and linear in claim count,
  but claim count is bounded by how many agents of one type are concurrently dispatched
  fleet-wide, which today never exceeds 1.

## The one recommendation

**Leave the double JSON parse in `live_claims`** (sub-microsecond, not worth touching per
the ceiling).

**Fix:** in `claim_worktrees` (`harness_boundary.py:252-277`), the linked-worktree list is
already computed once at line 260 (`roots = [owner_root] + linked_worktrees(owner_root)`).
Resolve each claim's feature against `roots[1:]` directly (or a call-local prefix-match
helper over that same list) instead of calling `worktree_for_feature`, which recomputes
`linked_worktrees(owner_root)` from scratch per claim. This is **not a process-lifetime
cache** — it lives for the duration of one `claim_worktrees()` call only, over an
argument (`owner_root`) that is invariant across that call, so there is no staleness
question to answer. **Read-only**, no registry write, no TTL/`_expire` involvement.
**Cost removed:** (C−1)×~0.47ms per governed write, where C = live claims matching one
`agent_type` fleet-wide — unmeasurable today (C≤1 observed), bounded only by how many
concurrent dispatches of one persona exist, so it is a correctness-neutral, zero-risk
cleanup rather than an urgent hot-path fix. Flagging as low-priority backlog, not blocking.

## Method disclosure

Throwaway harnesses at `/tmp/bench_efficiency.py` and `/tmp/bench_efficiency2.py` (not
under the repo, not committed). They import the real modules read-only, call
`claim_worktrees`/`live_claims`/`linked_worktrees` against the real checkout, and in the
synthetic-worst-case script monkey-patch `inflight_registry.live_claims` in-process (no
file writes) to simulate more concurrent claims than exist today. No registry file was
written; no HEAD movement; no suite re-run.
