# Receipt — harness-backend-dev — denialtier-eng

## BLUF

Widen T-17: the DENY tiers cost more than the REPORT tier per call (V1-V0 = **+1.9908 ms**
per governed write at 30 worktrees / 88 features, memoised V2-V0 = **+1.1659 ms**), but the
DENY-tier widening carries a real fail-open surface the REPORT-tier widening does not: when
`corpus_root` returns `None` (a documented, legitimate T-01 outcome), both DENY-tier guards
land in an unrelated broad `except Exception` and **ALLOW** the write — silently at
`feature_checkout_guard` (D4 route 3), with a printed warning at `claim_checkout_guard`
(D4 route 4). Neither guard special-cases `corpus_root() is None` the way `claim_worktrees`
already special-cases `UnreadableRegistry` (which correctly REFUSEs). If T-17 widens beyond
the sweep, that `None` case needs its own handling — not a bare pass-through catch — or the
widening trades a "reaches nothing" defect for a "silently allows more" one at exactly the two
tiers that gate real writes.

Cost is affordable either way (well under the ~18-24 ms interpreter-startup floor); safety is
the open question, not performance.

## D1 — four anchors, re-verified against the files opened in this session

- (a) `check-domain.sh:752` — `expected = harness_boundary.worktree_for_feature(root, feature_id)`; `:753-754` — `if expected is None:` / `    return`. MATCHES.
- (b) `harness_boundary.py:230` — inside `worktree_for_feature`, the comprehension calls `linked_worktrees(owner_root)` (line 230, first line of the candidates comprehension at 229-233); `return None` on no candidate is at line 235 (`if not candidates: return None`), not 236 as loosely stated in the dispatch — one line off, confirmed by direct read. MATCHES with that one-line correction.
- (c) `harness_boundary.py:265` `def claim_worktrees(owner_root, agent_type, destination):`; `check-domain.sh:780` — `claim_set = harness_boundary.claim_worktrees(root, agent, destination)`; its no-claim-set early return is at `check-domain.sh:809-810` — `if not claim_set:` / `    return`. MATCHES.
- (d) `harness_boundary.py:273` — `for registry_root in [owner_root] + linked_worktrees(owner_root):`. MATCHES.

## D2 — the multiplier (instrumented, `harness_boundary.linked_worktrees` counting-shim monkeypatched onto the live module in-process)

One `claim_worktrees(owner_root, agent, destination)` call makes **2** `linked_worktrees`
calls in both spellings measured on this host right now — but that count is a product of two
factors, and the factors differ sharply between spellings:

- Factor 1 (always exactly 1): `claim_worktrees`'s own list-build, `[owner_root] + linked_worktrees(owner_root)` (`harness_boundary.py:273`).
- Factor 2 (= total live claims found across every registry iterated): each live claim reaching `_registry_claim_worktrees` (`harness_boundary.py:253-262`) calls `worktree_for_feature(owner_root, claim["feature"])`, which itself calls `linked_worktrees(owner_root)` again (`harness_boundary.py:230`) — **re-scanning the same owner root's worktrees directory once per live claim found, regardless of which registry produced it.**

At the current spelling (`owner_root` = this worktree's own root): 1 registry to scan (`linked_worktrees` on a worktree root hits the `.git`-is-a-file `OSError` fast path, returns `[]`), 1 live claim found (my own claim on this feature) → 1 + 1 = 2.
At the widened spelling (`owner_root` = main checkout): 31 registries to scan (main + 30 linked worktrees), 1 live claim found *total* across all 31 → 1 + 1 = 2.

**The counts happen to match today only because exactly one live claim exists on this host at
measurement time.** The real cost driver at the widened spelling is not this multiplier — it
is that Factor-1's single `linked_worktrees(MAIN_ROOT)` call and the 31 `inflight_registry.live_claims` reads it drives are each individually far more expensive against 30 worktrees than the same calls are against a worktree's empty `.git/worktrees`. See D3.

## D3 — THE MEASUREMENT

Host: this workstation, Python 3 in-process (`time.perf_counter`), warm-up iteration discarded, N=200 per variant (no variant approached the 60s budget). Corpus size 88 features, 30 linked worktrees (see D5).

| Variant | mean ms/call | p95 ms | N |
|---|---:|---:|---:|
| V0 — `claim_worktrees(<this worktree root>, agent, dest)` (today) | 0.0528 | 0.0546 | 200 |
| V1 — `claim_worktrees(<main checkout root>, agent, dest)` (widened) | 2.0435 | 2.4200 | 200 |
| V2 — widened + per-invocation memo on the `/tmp` copy | 1.2187 | 1.3395 | 200 |
| V3 — `worktree_for_feature(<main checkout root>, "FEAT-58-corpus-outside-worktree")` | 0.7860 | 0.8139 | 200 |

Interpreter-startup floor: measured on this host via `subprocess.run([sys.executable, "-c", "pass"])`, mean of 5 = **~18.5–23.6 ms** across two runs of this receipt's script (both well above every variant above); the `harness_boundary.py:225-227` docstring cites ~38 ms for the same floor — same order of magnitude, not re-derived from that docstring, measured directly.

**Deltas at 30 worktrees / 88 features:**
- `V1 - V0 = +1.9908 ms per governed write`
- `V2 - V0 = +1.1659 ms per governed write` (memoised)
- `V2 - V1 = -0.8249 ms per governed write` (the memo's saving)

**V2 methodology note, because it is easy to get this wrong:** V2's `_LINKED_WORKTREES_MEMO`
dict is explicitly `.clear()`-ed at the start of every timed call, so each timed call re-pays
the *first* `linked_worktrees` call from cold and only reuses the cache for the *second*
call inside the same `claim_worktrees` invocation (Factor-1 vs Factor-2 above). **This is the
correct model of "the hook is one process per invocation": a per-process memo is exactly a
per-invocation memo, and it holds** — nothing in `claim_worktrees` or `worktree_for_feature`
crosses a process boundary, so there is no cross-invocation reuse to model or to lose. (An
earlier draft of this script measured V2 without clearing between iterations, which
amortized the memo across all 200 samples and produced a misleadingly low 0.29 ms mean — not
reported here; V2's real per-invocation figure is 1.2187 ms.)

At today's single-live-claim state, V2 saves less than half of V1's added cost, because
Factor-1's `linked_worktrees(MAIN_ROOT)` full-scan (30 worktrees × read one `gitdir` pointer
each) is paid once regardless; the memo only kills the Factor-2 re-scan. If live claims ever
number more than one (D2), the memo's saving grows — each additional live claim previously
paid a full re-scan; with the memo, only the first pays it.

## D4 — can the widened enumeration still fail open?

Every route below traced against `owner_root = corpus_root(root)` per the T-01 spec text at
`plan.yaml:340-344` (function not yet implemented — T-01 unexecuted, consistent with
DEC-174). `corpus_root` never falls back to `cwd`; it returns `None` only when both the
`worktree_owner`-derived owner root and the `resolve_root` fallback fail.

1. **`linked_worktrees`'s `except OSError: return []`** (`harness_boundary.py:171-174`). Triggers on both "no `.git/worktrees` dir" (plain checkout, or a wrong root) and "permission denied" — the code does not distinguish. LEGITIMATE when the owner root genuinely has no linked worktrees (a solo checkout). UNRESOLVABLE when the `OSError` is a permission fault on a real owner root — collapsed to the same silent `[]`, feeding into route 3/4 below with no diagnostic.

2. **The per-pointer `except Exception: continue`** (`harness_boundary.py:181-184`). Drops exactly one unreadable `gitdir` pointer. If that dropped worktree is the *only* one holding the agent's live claim, `claim_worktrees`'s result set ends up empty even though a real claim exists — then `claim_checkout_guard`'s `if not claim_set: return` (`check-domain.sh:809-810`) **ALLOWs** the write with no worktree binding enforced at all. UNRESOLVABLE: this is not "agent holds no claim," it is "agent's one claim's worktree pointer could not be read" — the two states are observably identical (empty `claim_set`) but only one is safe to treat as "nothing to bind against."

3. **`feature_checkout_guard`'s blanket `except Exception: return`** (`check-domain.sh:766-769`, confirmed matching D1(a)/D1(b) numbers). Under the widened spelling, `worktree_for_feature(corpus_root(root), feature_id)` raises `TypeError: expected str, bytes or os.PathLike object, not NoneType` when `corpus_root(root)` is `None` (confirmed by direct call in this session's instrumentation — `linked_worktrees(None)`, `worktree_for_feature(None, …)`, and `claim_worktrees(None, …)` all raise the identical `TypeError`). That `TypeError` lands in this catch-all and **ALLOWs**, with **no message printed at all** — silent. UNRESOLVABLE: `corpus_root` returning `None` is a degenerate host state (T-01: neither derivation resolved), not "this feature has no worktree yet," and this branch cannot tell the two apart because it was written to absorb *bugs in the narrowing check itself* (docstring, `check-domain.sh:744-745`), not to absorb a new upstream `None`.

4. **`claim_checkout_guard`'s generic `except Exception as exc:` pass-through** (`check-domain.sh:787-808`). Same `TypeError` under the widened spelling, same root cause. Unlike route 3, this branch DOES check `isinstance(exc, inflight_registry.UnreadableRegistry)` first (`check-domain.sh:790`) and REFUSEs (`sys.exit(2)`) for that specific, already-anticipated failure — but a `TypeError` from `corpus_root() is None` is not an `UnreadableRegistry`, so it falls through to the generic branch, prints `"claim-worktree boundary was not enforced; passing through …"` to stderr, and **ALLOWs**. UNRESOLVABLE, same as route 3, but *observable* — the operator gets a stderr line, unlike route 3's total silence.

5. **`corpus_root` returning `None` reaching the existing (unwidened) T-17 sweep** (`check-domain.sh:2148-2153`, `try/except Exception: pass` around the whole sweep-glob build). Same `TypeError`, caught by the same broad absorb, sweep silently adds nothing beyond the root-level patterns. This is a **REPORT** tier, not a DENY tier — no write is allowed or refused here, so this route is silent-empty-report rather than ALLOW. LEGITIMATE-vs-UNRESOLVABLE is lower-stakes here than routes 3/4 precisely because nothing is gated on it.

**Asymmetry worth naming:** the code already special-cases the one failure mode it anticipated
(`UnreadableRegistry`, route 4) and REFUSEs for it. Widening onto `corpus_root(root)` introduces
a *second*, unanticipated `None`-shaped failure that both DENY tiers fall through to their
generic bug-absorbing catches — the same catches whose entire purpose (per their own docstrings)
is to keep a bug in the narrowing check from turning an already-domain-allowed write into a
false block. Widening should either give `corpus_root() is None` the same explicit REFUSE
treatment `UnreadableRegistry` gets, or the widening inherits a new fail-open path at both
DENY tiers that the sweep-only T-17 scope does not have today (the sweep was already fail-open
by design, being a report).

## D5 — host facts

- Linked worktrees under `/Users/molchairuangutai/GitHub/harness/.git/worktrees`: **30**. Counted with `ls .git/worktrees | wc -l` from `/Users/molchairuangutai/GitHub/harness`; cross-checked as `len(harness_boundary.linked_worktrees(MAIN_ROOT))` = 30 in the instrumentation script (D2's `D2_registries_v1` = 31 = 1 + 30).
- Feature directories under the main checkout's `.harness/harness/features/`: **88**. Counted with `find .harness/harness/features -mindepth 1 -maxdepth 1 -type d | wc -l` from the main checkout. (Only `.harness/harness/features` holds entries; the other 8 `.harness/*/features` segments present in this repo are empty — checked with a loop over `.harness/*/features`.)
- Live claims `inflight_registry.live_claims` returns for `harness-backend-dev` across `[main] + linked_worktrees(main)` (31 registries) at measurement time: **1**, held by `/Users/molchairuangutai/GitHub/harness/.claude/worktrees/harness/FEAT-58-corpus-outside-worktree` for feature `FEAT-58-corpus-outside-worktree` — this session's own claim. Every other registry returned 0. Counted by iterating `inflight_registry.live_claims(reg, "harness-backend-dev")` over all 31 registry roots in a `/tmp` script importing the live module (no source edited).

## Reference-text check

The `T-17` `verify:` quoted in the dispatch —
`python3 tests/integration/test-check-domain-worktree-tier.py && python3 tests/integration/test-check-domain-worktree.py`
— matches `plan.yaml`'s `T-17` entry byte-for-byte as read in this session. Not run (per NON-GOALS; the first suite does not exist yet).

## Files touched

None outside `/tmp` and this receipt. `git status --porcelain` in the worktree (run after writing this receipt):

```
 M .harness/harness/features/FEAT-58-corpus-outside-worktree/BRIEF.md
 M .harness/harness/features/FEAT-58-corpus-outside-worktree/feature.json
 M .harness/harness/features/FEAT-58-corpus-outside-worktree/observations/harness-pm.md
 M .harness/harness/features/FEAT-58-corpus-outside-worktree/plan.yaml
?? .harness/harness/features/FEAT-58-corpus-outside-worktree/notes/answers-operator-c1.md
?? .harness/harness/features/FEAT-58-corpus-outside-worktree/notes/receipt-harness-backend-dev-denialtier-eng.md
?? .harness/harness/features/FEAT-58-corpus-outside-worktree/notes/research-FEAT-58-apply-operator-c1.md
?? .harness/harness/features/FEAT-58-corpus-outside-worktree/notes/research-FEAT-58-goalcheck-plan-c2.md
```

The four modified/untracked entries other than this receipt predate this dispatch (confirmed
against the pre-work `git status --porcelain` captured before any tool call in this session,
which showed the identical set) — this session added only the receipt.
