# PLAN FIX c1 — all six cycle-0 findings closed (three fixed as blocking, three advisory fixed, none declined)

All six are FIXED; nothing declined. G4 took resolution (b) — the contract keeps `merge` and states
its rewrite in the same file — so no decision was amended to buy nothing. plan.yaml was written only
through `plan-merge.py` (`amend` x7, `apply` x1); BRIEF.md edited directly; `## Approval` untouched at
`status: pending`; no `panel:` key; `safe_load` clean; `check-plan-routes.py` exits 0 with 0 violations.

## Disposition

| # | Disposition | What changed |
|---|---|---|
| G4 | FIXED, resolution (b) | one canonical sentence now carried verbatim by SC-09, D-10 `because`, T-03 `intent`, T-02 case17 `intent` |
| G3 | FIXED | new **SC-11** (concurrency) + new **T-02 case18**; T-02 already traces REQ-07 |
| G1 | FIXED | T-02 `traces:` now `[REQ-01 … REQ-09]` |
| G2 | FIXED (not declined) | SC-09 now *requires* a mutation demonstration against two drifted COPIES; case17 mechanises it as `contract_drift(skill_text)` so the same function runs on the copies |
| G5 | FIXED (not declined) | T-04 verify greps `^- DEC-216 .* :: .*replace and drop through the ops subcommand`; T-04 intent commits the ruling to that verbatim string; SC-10 reworded to the same literal |
| A1 | FIXED both ways | T-04's `depends_on` reduced to `[T-01]` (it never reads T-03's text), and the one remaining barrier recorded as **D-13** with its cost |

## G4 — the four now-identical statements

Each of the four carries this sentence verbatim (verified by whitespace-normalised substring match
against `safe_load`ed values; only line wrapping differs):

> Every op verb the distillation contract names is either accepted by the expertise-merge.py ops
> subcommand or is merge, the one verb the contract itself rewrites with the literal sentence: a
> replace on the surviving id plus a drop of the absorbed id; and the tool accepts no verb the
> contract does not name.

- **SC-09** (BRIEF.md) — "asserts exactly this: …" + the mutation demonstration.
- **D-10 `because`** — the old rationale "keeps the contract's four verbs all applicable" is gone; it
  now names this sentence as the agreement the refusal buys.
- **T-03 `intent`** — states it, then binds the text: the vocabulary line names exactly
  add/replace/merge/drop, and the file carries `a replace on the surviving id plus a drop of the
  absorbed id` as a contiguous unbackticked substring. T-03's pre-existing `verify:` already greps
  that literal, so contract, verify and case17 key on one string.
- **T-02 case17 `intent`** — the exact predicate, no judgement: `CONTRACT − ACCEPTED == REWRITTEN`
  and `ACCEPTED − CONTRACT == ∅`, where `REWRITTEN = {"merge"}` iff that literal occurs verbatim
  (substring test, never a reading).

Why (b): D-10 and T-03 already commit to `merge` surviving as an authoring concept with a named
rewrite. (a) would amend a signed-shape decision to delete a verb the contract wants.

## G3 — SC-11

Assertions: an add-only `apply --entries` (adds `P-09`, `P-10`) and an `ops` replace of `P-07`
overlap — **both spawned with `subprocess.Popen` before either is waited on** (no sleep) — then
(1) both exit 0, (2) the Patterns id census is exactly the eight pre-existing ids plus `P-09`/`P-10`,
(3) `P-07` carries the replacement marker text. Each child waited with `timeout=30`; `TimeoutExpired`
is a FAIL. Verify command: `python3 tests/integration/test-expertise-merge.py` (T-02's own verify),
case18. RED shape, stated in the criterion: one writer's entries missing from the census, or `P-07`
still carrying its old text — i.e. exactly a lost whole-file write if `ops` does not take `apply`'s
lock (D-09). Deterministic because either serialisation order yields the same final state.

## Coverage mapping

SC → T: SC-01→T-02 c11 · SC-02→T-02 c12 · SC-03→T-02 c13 · SC-04→T-02 c14 · SC-05→T-02 c15 ·
SC-06→T-02 c16 · SC-07→T-01 (u1–u10, u10 permanent red) · SC-08→T-02 c11/c12 (`check-expertise.sh`) ·
SC-09→T-02 c17 (+T-03 supplies the text) · SC-10→T-04 · **SC-11→T-02 c18**. No orphan SC.

T → REQ: T-01 → REQ-01…REQ-07 · T-02 → REQ-01…REQ-09 · T-03 → REQ-08 · T-04 → REQ-08. No orphan task.
REQ-07 is now criterion-covered on both halves: SC-06 (add-only compatibility) and SC-11 (concurrency).

## Porcelain

```
?? .harness/harness/features/BUG-1308-expertise-replace-drop/
```

Nothing outside the feature directory. No formatter, linter, build or suite run.

## Open

- D-13 records the single remaining mid-build yield (T-02 → T-03, main-session-direct). Unavoidable:
  a drift detector run before the text it grades would pass on work never done.
