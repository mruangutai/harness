# Review — SC-05 spec compliance of the T-03 tests-only delta (review_sha c472a02)

## BLUF

SC-05's ON-side failing clause is discharged, and robustly — verified by reproducing the exact
mutant myself, not by trusting the commit message. SC-05's OFF-side failing clause — BRIEF.md's
own words call it "the half that can fail" — is **still not discharged** after this commit. The
disputed mutant **survives** the full current unit suite (35/35 pass, exit 0, reproduced
independently). The engineering lead's specific stated reason ("rc is never consulted") is wrong
in detail — `m.returncode` IS populated when the mutant's `finally` runs, on both ON and OFF paths
— but the practical conclusion (the OFF-side clause is uncovered, and this mutant does not prove
otherwise) stands. This is the same finding QA already recorded independently at this pin
(`notes/qa-matrix-gate-final-c472a02.md` §2, item "New finding this gate") — confirmed, not
rediscovered, by an independent repro.

## Pin and diff shape

- `git rev-parse HEAD` = `c472a02262a64f465dad077e14df61f770538b58`; dispatched `review_sha`
  `c472a02` is its unambiguous short form — not BLOCKED.
- `git diff 3fbfd0a..c472a02 -- factory_gh.py gh_cost_log.py` is empty — confirmed, tests-only
  holds for the full range.
- Correction to the dispatch's framing: the range is **three** commits, not one —
  `8c89f57` (qa gate + reconciliation), `02277a1` (handoff refresh), `c472a02` (the actual
  test addition). Doesn't change the tests-only conclusion (none of the three touch production
  code), but worth flagging since "ONE commit" was asserted as fact.
- No `[harness:human]` commits in range (`git log --grep`).

## Q1 — ON-side failing clause (BRIEF.md:83-86)

**Discharged, and the strong form is load-bearing — verified empirically, not just read.**

I reproduced cycle-4's target mutant myself (deleting `_cost.returncode = r.returncode` at
`factory_gh.py:162`) and ran the real `test-gh-cost-log.py` against it:

```
1 of 35 FAILING.
FAIL  factory_gh.run_gh wrap site, FAILING: the recorded rc equals the real exit code (1)
      — non_cov=[{... 'rc': -1}]
```

Confirms `gh_cost_log.py:165`'s sentinel fires (`rc = m.returncode if m.returncode is not None
else -1`) when the assignment is missing. I then checked what a weaker assertion would have done
against that same captured record: `rc is not None` → `True` (since `-1 is not None`) — it would
have passed on the mutant, proving nothing. The landed assertion at
`test-gh-cost-log.py:407-409` (`non_cov[0].get("rc") == 1`) is the only form that catches this.
Matches the commit's own claim byte-for-byte; independently reproduced rather than trusted.

## Q2 — OFF-side clause (BRIEF.md:87-89)

**Not discharged at the wrap-site level anywhere in the file — this commit didn't touch it.**

- `test-gh-cost-log.py:335-346` (`factory_gh.run_gh` wrap site, OFF) and `:367-379` (`gh-sync.py`
  wrap site, OFF) both call `_counting_fake()` with no `rc` argument →
  `_counting_fake(rc=0, ...)` default (`:289`) → both drive a **succeeding** call. Neither is a
  failing invocation.
- The only OFF+"FAILING"-labelled checks in the whole file are `:255-258`
  (`with HARNESS_GH_COST_LOG unset, a FAILING invocation creates no log file` /
  `writes no line`). They call `gh_cost_log.record(["issue", "create"], 200, 210, 1)` **directly**
  (`:254`) — bypassing `measured()` and both wrap sites entirely. That exercises `record()`'s own
  internal guard (`gh_cost_log.py:112`, `if not _enabled(): return`), not the guard inside
  `measured()` (`gh_cost_log.py:157-159`) that a real wrapped call actually goes through.
- Net: no test anywhere drives a failing invocation through `factory_gh.run_gh` or `gh-sync.py`'s
  `gh()` with `HARNESS_GH_COST_LOG` unset. SC-05's literal text names exactly that scope
  ("every harness `gh` invocation that flows through `factory_gh.run_gh` or `gh-sync.py`'s
  wrapper"). This is an omission against SC-05, not a hypothetical one.

## Q3 — the disputed mutant

```python
if not _enabled() or is_counter_call(argv):
    try:
        yield m
    finally:
        if m.returncode not in (None, 0):
            record(argv, 0, 0, m.returncode)
    return
```

**(a) Does the current suite go red? No — survives.** Ran it directly (monkeypatched
`gh_cost_log.measured` to this exact mutant, executed the real, unmodified
`test-gh-cost-log.py` via `runpy`): **35/35 checks passed, exit 0.** Every OFF-side check in the
file either doesn't reach `measured()` at all (the two `record()`-direct checks) or drives `rc=0`
through it (the two wrap-site OFF checks), so `m.returncode not in (None, 0)` never evaluates
`True` on any exercised path. Nothing kills it.

**(b) Is `m.returncode` populated when `finally` runs? Yes — on both OFF and ON.** Traced
`factory_gh.py:151-162`: `_cost.returncode = r.returncode` (line 162) executes unconditionally,
still inside the `with gh_cost_log.measured(args) as _cost:` block, before that block exits — so
the generator resumes past `yield m` (into the mutant's `finally`) only after `m.returncode` is
already set to the real code. This is true regardless of whether `_enabled()` is True or False;
`measured()`'s branch selection happens at entry (line 157), before the caller ever sets
`.returncode`. Only a `FileNotFoundError` (gh binary missing) skips line 162, a different failure
shape than "ran and returned non-zero."

**Adjudication.** The lead's literal justification is wrong: rc is not unconsultable on this path,
and this mutant proves it by consulting a real, populated value. But the requester's claim that
"this mutant kills the argument" is also not supported — it survives the actual suite, verified
directly rather than assumed. There's a further wrinkle neither position states: on the
`not _enabled()` disjunct specifically, `record()`'s own independent `_enabled()` guard
(`gh_cost_log.py:112`) makes the mutant's added `record()` call a no-op regardless of what
`measured()` does — so *no* output-only assertion (checking only the log file's contents) can ever
distinguish this mutant via that disjunct; it is effectively equivalent-mutant-shaped there,
belt-and-suspenders masking a real gap rather than proving one closed. The mutant is genuinely
live only on the `is_counter_call(argv)` disjunct, when `_enabled()` is True and the **counter's
own** call fails — a narrower, also-untested scenario, and not what SC-05's OFF-side clause is
actually about. Bottom line: neither "unpinnable in principle" nor "this mutant kills the
argument" is correct. What's correct, confirmed by running it: the OFF-side clause is uncovered,
and this exact mutant, as given, does not demonstrate otherwise.

This matches `notes/qa-matrix-gate-final-c472a02.md` §2(a)/(b)/(c) exactly (same line anchors,
same conclusion) — independently reproduced here, not copied.

## Q4 — fail-open scan of the new block (:381-410)

No vacuous pass found.
- `:403-404` ("GhError was raised") — fails cleanly if `raised` stays `False`.
- `:405-406` ("one line written") — `len(non_cov) == 1` fails on 0 *or* >1 lines; not a presence-
  only check.
- `:407-409` (the rc-equality check) — conjunctive: `len(non_cov) == 1 and non_cov[0].get("rc")
  == 1`. If zero lines were written, this correctly evaluates `False` rather than short-circuiting
  to a vacuous pass — the presence and value assertions are paired in the same expression
  (DEC-169 shape done right, not wrong, here).

## Prior recorded items

B-1, B-2, B-3, B-5, B-6, B-11, B-12, B-13, B-15 — not independently re-derived, per dispatch.
B-5 (T-03 `intent:` stale anchor) is outside this task's scope (plan.yaml prose, not SC-05 test
discharge) — not touched.

## What this means for SC-05 as a whole

`evidence: unit` for SC-05 claims automated proof of both halves. Only the ON half is proven. The
OFF+failing half — the half BRIEF.md itself flags as the one that can fail silently — remains
open. This is a real gap in what SC-05 requires, not new information (QA already surfaced it at
this same pin), but my independent read and mutation repro confirm rather than contradict that
finding.
