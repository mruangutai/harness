# FEAT-24 — the simplify findings applied to plan.yaml and BRIEF.md

**All ten dispatched items applied, none declined, plus one the dispatch dropped.** Approval stays
`pending`. `check-plan-routes.py` is at 0 violations. The plan `safe_load`s, every `verify:` passes
`bash -n`, every heredoc compiles as Python, and every non-loop `has()`/`hasin()` string in a verify
now appears verbatim in that task's own intent (the one exception is T-04's pre-existing
`derive_station: two done one pending -> None`, which is deliberately a deletion tripwire on an
existing case, the same pattern T-01 and T-02 already use).

Numbering below is the **dispatch's** F-1..F-8, not the eng digest's.

## The four must_fix

**F-1 · the memo contradiction — applied, all three sub-parts.**
- T-02 item 5 now says no cached value is consulted **when the read fails**, and names item 6 as
  the success-path memo; item 6 says **successful results only** are memoised, a raise is never
  memoised and never served. `D-03`'s clause carries the same split.
- New verify clause and matching ok-line:
  `product_config memoises a successful read: a second board_for makes no second remote read`.
  The case counts `file_at_ref` invocations across two `board_for` calls **and** asserts a failing
  read is not memoised — stub raises, `board_for` raises, stub repointed, next call succeeds.
- New `THE MEMO TRAP` paragraph in T-02's intent. The collision is real: `good_fleet_dict()` at
  `test-factory-config.py:44-52` reuses `mruangutai/harness` + `main` and its callers at `:238` and
  `:410-413` inherit it, so every new stubbing case must use a unique `(repo_name, ref)` or clear
  the memo dict as its first statement. Item 6 now also requires the dict to have a reachable
  module-level name.

**F-2 · SC-10 — remedy chosen: implement, not restate.** The dispatch offered either; the
per-file loop it suggested is the wrong instrument for half the files (P-01: a moved-key-absence
grep over `factory_claim.py`, `factory_decompose.py`, `factory_land.py` and `factory_config.py`
would be either green-at-HEAD or plain wrong — they are readers that change *source*, not files
that must stop matching). So each of the eight readers got the assertion its own shape admits, and
SC-10 was rewritten to say exactly that:

| file | its named assertion |
|---|---|
| `gh_board.py` | T-04 literal-absence grep + positive control |
| `check-state.sh` | T-05 INV-26 slice greps + positive control |
| `gh-sync.py` | T-04 `an unusable board config is a loud failure, not a skipped station write` |
| `board-station.py` | T-04 two named cases |
| `factory_config.py` | T-02's named `product_config`/`board_for` cases |
| `factory_land.py` | T-03 `(M1) pr create base is the fleet's default_branch` |
| `factory_claim.py` | T-03 `factory_claim reads default_branch from the fleet entry before any clone exists` (new, T-03 item 1b) |
| `factory_decompose.py` | T-03 `(2) both stations set to the fleet's ready option` (existing, now pinned) |

The non-reader half is implemented too — a four-file grep loop in T-04's verify, each file with its
own positive control — and **corrected from three files to four**: the survey classifies
`wayfind.py`, `layout_migration.py`, `check-plan-routes.py` and `branch-create-gate.sh`. All four
match zero moved keys at HEAD, so `## Verification gaps` now records that this clause is a
regression guard, not evidence of migration, and that the classification itself rests on a
planning-time grep at `ada8e99` that nothing re-runs.

**F-3 · SC-04 — applied.** T-02's verify gains the same eight-shape loop T-04 drives through
`load_board`, driven through `board_for`, with ok-lines
`board_for raises naming the file and the key: <shape>`. Intent lists all eight and requires two
assertions per case (path **and** key in `str(exc)`). The pre-existing
`board_for raises when the product config declares no board` case is kept beside them and its scope
disambiguated (absent `github` block, versus the loop's absent `board` key). SC-04's wording now
names both entry points explicitly.

**F-4 · SC-07 — applied, with SC-07 restated to match.** `factory_claim` gets a named case
(T-03 item 1b, the single addition that task now authorises — its "add nothing else" rule was
amended in the same edit so the executor is not forced to refuse). `factory_workspace` has no
dedicated suite, so its evidence is `(D-workspace) success: exits 0` in
`test-factory-integration.py`: `factory_workspace.py:115` reads `entry["default_branch"]` to cut the
branch, so that case cannot pass if the key leaves the fleet entry. SC-07 now spells out all three
pointers rather than claiming a uniform granularity it does not have.

## Also applied

- **The `--check` line** — `plan.yaml` T-10's intent now says `--stdout` piped into `diff`,
  matching that task's own verify, and states there is no `--check`. Re-derived: the docstring at
  `gen-decisions-index.py:9-10` says so and `:391-396` exits 2 on any argv but `--stdout`.
- **F-5 · the EOF-anchored slice** — both `src[i196:]` sites replaced by `src[i196:i197]`, with
  `i197 = src.find("## DEC-", i196 + 1)` defaulting to `len(src)`. DEC-196 is the last heading today
  (offset 415098, file length 417986), so the fix is a no-op now and correct the moment a decision
  is appended. **SC-11 needed no wording change: its per-entry claim is now true rather than
  accidental.**
- **F-6 · reuse** — T-06's and T-09's heredocs import `factory_config` (with
  `sys.path.insert(0, ".claude/skills/harness/bin")`, verified to import cleanly with no import-time
  I/O) and call `validate_board(...)` in try/except. The hand-rolled key-set comparison is gone
  from both; the live-option **value** assertions stay as a separate block, as instructed.
  **Collateral, and it is a real cost:** `_validate_board` is private at HEAD, so both tasks gained
  `depends_on: [T-02]`. T-06's "this task can run first" sentence was rewritten. T-09's intent now
  states the cost out loud — the plan's longest pole, the cross-repository kaya route, starts after
  one harness-side task, accepted because a verify that certifies a shape the real loader would
  reject is worse than a later start. No cycle: T-01 → T-02 → {T-06, T-09} → {T-04, T-07} → …
- **F-7** — T-10 `depends_on: [T-05, T-06, T-07]`.
- **F-8** — T-04's two suites now run once each into `sync_out`/`bs_out`, reused by a `hasin`
  helper. Every existing assertion survives; the removed "produced no passing lines" check is
  subsumed by the three named-case checks that follow it.
- **The accepted-cost line** — `D-03`'s `because` now records that `factory_decompose` resolves the
  board twice per run (`:329`, and `:399` via `board_station`) and `factory_claim.py:226` once more,
  that the success memo makes that one network read per process, and that a failed read is never
  memoised so an unreachable remote costs one loud failure per call site.

## The consistency check — SC-06 unchanged

Its clause "never falls back to a checkout, a cached value or a default" is coordinated with
"raises naming …", both predicates of "a failed remote read". It binds to the failure path and is
therefore true of a success-path memo. T-02 item 5, `D-03` and SC-06 now say the same thing.
The new memo ok-line does not collide with the failure-path case names at T-02's verify.

## One thing the dispatch did not carry

The eng digest's **own F-1** — T-06's `_note` clause being negative-only, so `"_note": ""` or a
deleted key passes unconditionally — is in neither the dispatch's apply list nor its LEAVE list. It
was lost when the dispatch renumbered digest F-2..F-9 as F-1..F-8. **I applied it**: T-06's verify
now asserts the replacement sentence is *present* (`loud` or `error`, and `null`), that
`PLACEMENT IS TEMPORARY` and the no-pinned-id sentence survive, and that the note's now-false
opening count `Three keys` is gone — the board declares four after this task. T-06's intent items 4,
4b and 4c were rewritten to require what the verify checks. Raised as `Q1` so the omission is seen,
not reconstructed.

## The four angle receipts, read

All four read in full after the edits, looking for anything contradicting what I applied. Nothing
did. Two reconciliations, both recorded rather than silently absorbed:

- The efficiency receipt measures `factory_land.py:85` as a third `board_for` call site. `D-03`'s
  accepted-cost line now names it alongside `factory_decompose.py:329,:399` and
  `factory_claim.py:226`, re-derived by grep at HEAD.
- The altitude receipt proposes excluding `branch-create-gate.sh` from the non-reader check (its
  pinned-id absence is covered by `test-branch-create-gate.py:55`). That is a different assertion —
  pinned ids, not moved board keys — and the lanes block already records a zero-match survey for it,
  so I kept it in, making the loop four files. SC-10 names all four.

## `check-plan-routes.py`, verbatim

```
scanning /Users/molchairuangutai/GitHub/harness/.harness/*/features/*/{plan.yaml,PLAN.md}
OK T-01 granted to harness-backend-dev, harness-dev-ops
OK T-02 granted to harness-backend-dev, harness-dev-ops
OK T-03 granted to harness-backend-dev, harness-dev-ops
OK T-04 granted to harness-backend-dev, harness-dev-ops
DEVIATION T-05 .claude/skills/harness/bin/check-state.sh, .claude/skills/harness/bin/test-check-state.py granted to harness-backend-dev, harness-dev-ops but declared main-session-direct
OK T-06 granted to harness-dev-ops
OK T-07: declared main-session-direct (.harness/factory/fleet.yaml ungranted)
OK T-08: declared main-session-direct (.claude/skills/harness/templates/harness.json ungranted)
OK T-09: declared main-session-direct (/Users/molchairuangutai/GitHub/harness-factories/kaya-ai/.harness/harness.json ungranted)
OK T-10 granted to harness-documentor
0 violation(s) across 1 plan(s)
examined 24 feature dir(s); 23 skipped as shipped
```

Exit 0. The `DEVIATION` line on T-05 is pre-existing and informational — the DEC-174 carve-out,
where a granted surface is deliberately declared `main-session-direct`. It is not a violation and
the count is 0.

## Budget note

T-06 sits at 49 of 50 machine-field lines (DEC-182). Any further verify clause there needs a line
returned first.
