# Code review — BUG-1290 B-27 fix cycle — panel/code at 72a97b99

**BLUF: PASS.** All three operator directives are achieved by construction, verified by direct
execution (not by reading comments). Two residual precision gaps (D1, D3) and two pre-existing
grade-2 test functions are reported below; none reach `high` severity, none are `must_fix`.

Diff reviewed: `c488218e..fb9a4ac4` (the only commit touching code; `72a97b99` adds only
notes/receipts, confirmed via `git diff --stat fb9a4ac4 72a97b99`). Production
(`.agents/ .claude/skills/ bin/`) confirmed byte-identical to `c488218e`, not re-litigated.

## Stage 1 — spec compliance: three directive verdicts

**D1 (kill the bare-negation loophole) — SATISFIED**, with a residual precision gap.
`test-factory-claim.py:1340-1349`'s six-conjunct check replaces the old bare `not
_5b_property_holds(...)` (`c488218e:1321`). Verified by construction, not by reading the
docstring:
- Injected a merely-raising `issue_number` into the CURRENT 5g's inline mutant class → 5g goes
  `FAIL` (confirmed by direct run).
- Injected the same raising mutant into the OLD (`c488218e`) 5g's bare-negation assertion → 5g
  stays `ok`, suite stays 125/125 green (confirmed by direct run) — this is exactly B-27.
- **Residual (MED, non-gating):** the six conjuncts pin the *symptom* (952 unresolvable, specific
  text), not the *cause*. I constructed an unrelated `_AlwaysNoneCache` (`issue_number` always
  returns `None`, not the intended first-repo-wins collapse) and ran it through the exact same
  `_emit_5b(_capture)` path 5g uses: it satisfies all six conjuncts identically
  (`mutant_cond=False, code=1, out='', "952"/"unresolvable blocker" in err, "no plan could be
  read" not in err`). 5g would report `ok` against this differently-broken mutant too. This does
  not violate D1 as stated (D1 was specifically about raising mutants) and a cruder "always
  unresolvable" regression would be caught elsewhere (B1/B3/B4/B5/B7 all exercise
  `_BlockerCache.issue_number` for single-repo blocker resolution) — tag: `enhancement`.

**D2 (make the literal case-5b line itself fail) — SATISFIED**, and is NOT the rejected 5g-only
equivalent wearing a second coat. Confirmed:
- `test-factory-claim.py:1236`'s intact run (`_emit_5b(check)`) always prints `ok    BUG-1290
  5b: ...` — 5g's internal mutation (`:1320-1351`) never touches this; it reruns `_emit_5b`
  through a non-printing capture shim (`:1328-1333`), so the module's OWN standalone run never
  shows a red 5b line.
- `test-factory-claim-mutation.py:150-182`'s new `_mutate_and_run_key_collapse` patches
  `factory_claim._BlockerCache` **at the module level, before the whole suite file re-executes**
  via `runpy` — a mechanism structurally distinct from 5g's internally-scoped shim. Under this,
  the REAL `check(name_5b, ...)` call at `test-factory-claim.py:1236` itself evaluates False.
  Ran `python3 tests/unit/test-factory-claim-mutation.py` directly: it prints `MUTANT
  KEY-COLLAPSE ACTIVE` then the literal `FAIL  BUG-1290 5b: same feature id on two repositories
  resolves per-segment, no cache bleed`, then `KEY-COLLAPSE PROOF: FAIL BUG-1290 5b printed`,
  exit 0. This is a real printed/counted failure from the unmodified suite's own case, guarded by
  its own `_reached` marker (`:194-199`).

**D3 (restoration path, no leakage into 5c-5f) — the restoration mechanism is sound and
independently verified; the "no leakage into 5c-5f" claim as worded is unfalsifiable by those
specific siblings.**
- Restoration: `factory_claim.py:333` does `cache = _BlockerCache()` fresh on every `run_main()`
  call — no module-level singleton/memo dict could carry a mutation forward. Confirmed
  `claim._BlockerCache is <original class>` is `True` after `_mutate_and_run_key_collapse`
  completes, and independently after 5g's own internal swap.
- Leakage: 5c/5d/5e/5f (`test-factory-claim.py:1244-1304`) run **before** 5g in source order, so
  they cannot see 5g's later mutation regardless of whether the restore succeeds. Separately, none
  of them exercise a same-feature, two-repository issue-map-cache lookup at all — 5c is a
  no-plan/absent-segment-root refusal, 5d/5e are direct attribute/API checks, 5f is a source scan.
  Confirmed empirically: running the full suite under the externally-applied key-collapse mutant
  (module-level patch active for the ENTIRE suite run, not just 5g's scope) leaves 5c/5d/5e/5f
  (and even 5g) `ok` — only 5b itself reddens, because only 5b's fixture ever puts two repositories
  under the SAME feature id through the cache. The comment at `test-factory-claim.py:1308-1310`
  ("the mutation never leaks into 5c-5f, which run afterward against the real, restored cache")
  overstates what "run afterward" proves — tag: `enhancement` (a genuine post-5g rerun of a
  fresh 5b-style multi-repo scenario would give behavioral, not order-of-execution, proof of
  restoration).

## Independent controls — reproduced

All five reproduced with a corrected harness (my first attempt globally monkeypatched `sys.exit`,
which corrupts the CLI's own internal exit-code capture and produces false failures unrelated to
the reviewed diff — discarded, redone by catching `SystemExit` around `exec()` instead without
touching `sys.exit`):
- (a) merely-raising mutant reddens 5g today, left the OLD (`c488218e`) suite green at 125/125 —
  reproduced both halves directly (see D1 above).
- (b) deleting `depends_on=["T-99"]` from the harness-segment fixture (`:382`) → exactly 1 failure,
  `BUG-1290 5g` — reproduced.
- (c) emptying the harness segment's issue map (`:383`, `{"factory": {"issues": {}}}`) → exactly 1
  failure, `BUG-1290 5b` — reproduced.
- (d) neutering the collapse in `_KeyCollapsingBlockerCache.issue_number`
  (`test-factory-claim-mutation.py:170`, made `canonical = repo` instead of the setdefault) while
  keeping the reached-print → `MUTANT KEY-COLLAPSE ACTIVE` still prints (reached) but `KEY-COLLAPSE
  MISSING: 5b` / `KEY-COLLAPSE PROOF: INCOMPLETE`, exit 1 — reproduced; the arm genuinely
  discriminates the collapse behaviour, not just reachability.
- (e) captured verdict keyed by `name_5b`, `False` under the mutant, real cache restored after —
  reproduced (see D1/D3 experiments above; `captured[name_5b] = (False, (1, '', <err>))`,
  `claim._BlockerCache is saved_blocker_cache` True afterward).

## Fail-open hunt

No new fail-open path found in either file. Every 5x case is wrapped in its own `try/except
Exception: check(name, False, ...)` (pre-existing convention, `:1163` etc.) so an unexpected crash
reddens rather than silently skips. `_5b_property_holds` defaults `False` on non-zero exit or
unparseable JSON before touching any of its positive conditions — no implicit `True` fallthrough.
`main()` in the mutation file requires **both** arms via `and`, not `or` (`:204`).

## Code quality / code-grade

Grader run over `merge-base(origin/main, 72a97b99)..72a97b99` (the range `validate-digest.py`
independently recomputes), not just this cycle's `c488218e..fb9a4ac4` delta:

```
python3 .claude/skills/harness/bin/code-grade.py --base 6e95435a58... --head 72a97b99...
```

20 functions pass at grade ≥4. Two are **grade 2** (test-code bar is 3), both **pre-existing,
unchanged by this cycle's diff** (confirmed absent from `c488218e..fb9a4ac4`):
- `test-factory-claim.py:324 build_features_root` (ABC 33.5, cyclomatic 1, cognitive 0) — a
  straight-line fixture-tree builder with zero branching; the ABC cost is the sheer count of
  `write_yaml`/`write_json`/`os.path.join` calls building one shared multi-segment tree the file's
  own docstring requires be built once. Splitting it would fragment that single-tree invariant
  across several loosely-coupled helpers for no reduction in real complexity. Accepted at grade 2.
- `test-factory-claim.py:403 run_main` (ABC 26.7, cyclomatic 6, cognitive 9) — the single shared
  test-driver seam ~150 cases call through; its cost is optional setup/teardown branches
  (`fleet_dict`, `features_root_fn`, patch/unpatch of `factory_gh`), not tangled control flow.
  Splitting would scatter shared state across helpers callers would need to know to compose.
  Accepted at grade 2 as the correct shape for a deep, single-seam test driver.

No grade-1 or below-bar production functions. `code_grade: grade_2` (never `fail`; both findings
recorded as `med`, non-gating per the grading skill).

## Findings summary

| # | Severity | Tag | File | Concrete scenario |
|---|---|---|---|---|
| 1 | med | enhancement | test-factory-claim.py:1340-1349 | An `_AlwaysNoneCache` (`issue_number` unconditionally `None`) satisfies 5g's six conjuncts identically to the intended first-repo-wins collapse; 5g does not discriminate cause, only symptom. Other blocker-gate cases (B1/B3/B4/B5/B7) provide a partial safety net for this class of regression. |
| 2 | med | enhancement | test-factory-claim.py:1308-1310 | "5c-5f run afterward against the real, restored cache" is order-of-execution truth, not behavioral proof — none of 5c-5f exercise a same-feature two-repo cache lookup, so their continuing to pass is guaranteed by construction, not evidence against leakage. |
| 3 | med | chore | test-factory-claim.py:324 (build_features_root) | Pre-existing grade-2, reasoned above; not introduced by this cycle. |
| 4 | med | chore | test-factory-claim.py:403 (run_main) | Pre-existing grade-2, reasoned above; not introduced by this cycle. |

No `must_fix`. `severity_max: med`.

## Already-ruled (not re-raised)

T-01's approved `verify:` exit 1; REQ-05 wording; `match_bug_class` matrix leg; null-yield
reviewer returns (not observed to recur in this diff — this diff has no reviewer-return code).
