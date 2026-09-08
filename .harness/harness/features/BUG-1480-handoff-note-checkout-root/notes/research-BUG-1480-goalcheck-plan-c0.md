# Goal-check — plan vs stated intent — BUG-1480 (cycle 0, panel s1)

**YES — the plan as drafted delivers the operator's stated intent.** The single most important gap is
on the EVIDENCE side, not the behaviour side: `SC-05`'s line anchors (`BRIEF.md:88`) are pre-fix
positions that T-02's insertion at `check-domain.sh:1149` shifts by ~14, so the reviewer reads
unrelated code at review time. No finding is `high`.

## Item verdicts

**1. Authorities resolve against the feature's checkout — MET** (`plan.yaml:146-149`).
Every root/feature-dir derivation in `handoff_done_when.py` descends from the SINGLE `root` argument
of `problems()` (`:376`, forwarded at `:391`): `_resolve_all` `Path(root)` (`:360`), `_feature_dir`
`root / prefix` (`:51-54`), `_read_target` containment `Path(root).resolve()` (`:79-87`),
`_resolve_finding` `root / m(1)` (`:144`), `_resolve_approval` `root / m(1)` (`:162`),
`_satisfied_approval` (`:236`), and `_resolve_plan` / `_resolve_brief` / `_plan_task` via
`feature_dir` (`:117`, `:132`, `:203`). No `__file__`, env, or cwd derivation exists in the module.
**No resolver would still read the wrong tree.** `rel` (worktree-relative, from `_norm`) and the new
root are then a consistent pair.

**2. `_ck[0]` carried into the call, helper shape preserves it — MET** (`D-03` `plan.yaml:28`,
helper quoted `plan.yaml:127-137`, call `plan.yaml:148-149`).
`harness_boundary` exposes both assumed names with the assumed signatures: `checkout_relative(abs)`
→ `(checkout_dir, rel)` or `None` (`harness_boundary.py:115-116`) and `real(path)`
(`harness_boundary.py:389`). The guard is byte-parallel to `_norm:1145`, which already ships. The
inequality never wrongly falls back: when `real(_ck[0]) == real(root)` the path stands in the main
checkout, so `root` IS the correct answer; when `checkout_relative` returns `None` the fallback
reproduces today's behaviour rather than a wrong tree. `_claimed_abs` and the `root` global are both
in scope at the insertion point (`_norm:1141-1144` uses both).

**3. Red-then-green regression — PARTIAL** (`T-01` `plan.yaml:45-97`).
All named anchors verified at the named lines with the named signatures: `make_linked_worktree`
(`test-check-domain.py:138`), `_record_handoff_result` (`:4132`), `_handoff_text` (`:4140`),
`_invoke_handoff` (`:4148`), `_handoff_done_when_fixture` (`:4155`), `_handoff_line_cap_cases` ends
`:4399`, `run_handoff_done_when` `:4410`, and the already-satisfied comment at `:2584-2587`, which
says exactly what T-01 cites it for. The fixture materialises the feature dir in the worktree only,
and the extra assertion row (`plan.yaml:79-82`) proves the main root has no copy. Row 1 goes RED
pre-fix (main root lacks the dir → `_read_target` raises → `_unresolved`, exit 2 ≠ want 0) and GREEN
post-fix. **The two negative controls are green BOTH before and after T-02** — T-01 says so for row
2, correctly, but row 3's stated claim is unsupported.

**4. Standalone off `origin/main` — MET** (`D-01` `plan.yaml:20`, `D-02` `plan.yaml:24`).
`6d969ed3` IS `origin/main`'s tip; `75cef65b` IS the main-checkout HEAD (one record-only commit
ahead, touching `BUG-148-gate-record-correction/feature.json` only, so the lane rows read at HEAD
hold at the base). Nothing in `lanes:`, `decisions:` or either task references BUG-201, BUG-1290, or
any other base.

**5. TDD enforced — MET** (`T-02 depends_on: [T-01]` `plan.yaml:105`; `T-01 verify` `plan.yaml:44`).
The verify asserts REDNESS, not mere execution: `grep -qE '^FAIL +handoff worktree-only feature dir
resolves'` matches `_report_handoff_results`' exact print shape (`test-check-domain.py:4405`, `"FAIL
"` + `sep=' '` → two spaces). Accidentally green → no FAIL line → grep exit 1 → verify FAILS.
Suite crashes before the group → no FAIL line → verify FAILS. It fails closed in both directions.

**6. Minimal — MET.** The change set is one sibling helper, one changed argument
(`plan.yaml:146-149`), and one case group. The only thing beyond the literal ask is negative-control
row 3 (`plan.yaml:93-95`), which traces to `REQ-04`; that is defensible, not creep. `D-02` is
bookkeeping. Nothing touches `_norm`'s contract, `bash-write-guard.sh`, or BUG-1290.

**7. SC discrimination — PARTIAL.** `SC-01` discriminates (revert the fix → row 1 red → `main()`
returns non-zero → `sys.exit(1)`, `test-check-domain.py:5228,5235`). `SC-02` MET (each pre-existing
row prints its own name). `SC-04` MET, `SC-06` MET (git-log order plus a red run at the test commit).
`SC-03` cannot be graded independently — its own rows are green with the fix reverted, so the shared
whole-suite exit code carries only `SC-01`'s signal. `SC-05` PARTIAL on rotted anchors (F-02).

## Findings

- **F-01 (med) — T-01 row 3 claims a proof it does not deliver.** `plan.yaml:93-95` says the
  `brief-sc:SC-99` row proves "BRIEF.md is read from the worktree copy and not merely skipped". Its
  needles are `("SC-99",)` only. Pre-fix the same row exits 2 with `SC-99` in the message against the
  MAIN-root `BRIEF.md`. *If T-02 resolved the feature dir to the wrong checkout while still refusing
  SC-99, the suite reports `ok handoff worktree-only brief-sc pointer refused` and the row's stated
  proof ships false.* Remedy: `_unresolved` embeds the target path (`handoff_done_when.py:112-113`),
  so add a needle on the worktree path fragment (`worktrees`, `bug-1480-wt`) to rows 2 and 3.
- **F-02 (med) — SC-05's line anchors rot the moment T-02 lands.** `BRIEF.md:88` cites `:1906`,
  `:1912`, `:2042-2048`, `:2073`, `:2077`, `:2089-2090`; `:1906` is today a `_norm(cand)` call inside
  `_resolved_rel` and `:1912` is `_plan_route`'s `_norm(path)`, both confirmed. T-02 inserts a ~14-line
  helper after `:1149`. *At `review_sha` the reviewer opens `:1906` and finds `_plan_route` internals;
  they either report a false violation or green the criterion over code that is not the call site,
  and `_norm`'s eleven-call-site invariant goes unchecked.* Remedy: cite the call sites by function
  name (`_resolved_rel`, `_plan_route`, the PRE target construction, the POST classification), or
  mark the numbers explicitly as pre-fix positions.
- **F-03 (low) — T-01's verify does not require the other three new rows to be `ok`.** *If the
  worktree fixture path is mistyped, all four new rows go red, `T-01 verify` still passes on row 1's
  FAIL line, and T-02 then cannot turn it green for a reason nobody attributes to the fixture.*
  Remedy: add `grep -qE '^ok +handoff worktree-only main root has no feature dir'` as a conjunct.
- **F-04 (low) — SC-01/02/03 share one whole-suite command** (`BRIEF.md:70,75,80`). *With three
  criteria resting on one exit code, a qa DIGEST citing "suite exits 0" is accepted for all three, and
  SC-03's non-vacuity claim is graded by a signal that only reflects SC-01.* Remedy: each SC cites its
  own printed row name as `evidence:`.
- **F-05 (info) — the safe-path containment bound narrows for worktree notes.** `_read_target:85`
  bounds targets by the root it is handed, so after T-02 a worktree note's `finding:`/`approval:`
  pointer into the MAIN checkout is refused as escaping the root. T-02's intent declares this
  (`plan.yaml:152-155`) and it is the intended semantics, but no REQ or SC covers it. Main-checkout
  cases are unaffected (guard returns `root`), so `REQ-02` is safe.

## Open questions

- None blocking. F-01 and F-02 are one-line edits to artifacts the pm owns.

## Reconciliation — F-id mapping across the two c0 notes

`research-BUG-1480-remedies-applied-c0.md` applies F-01..F-06; this note numbers F-01..F-05. The
two documents do NOT use `F-05` for the same thing. Nothing is renumbered in either; this section
is the map.

- The remedies note's F-01..F-04 are this note's F-01..F-04, one-to-one.
- The remedies note's F-05 (the with-block placement of the `_handoff_worktree_cases` call) and its
  F-06 (the new REQ-06 / SC-07 containment pair) were contributed by the validator lead at its own
  tier. Neither is carried by this note.
- This note's own F-05 (info, the containment-bound narrowing) is therefore NOT the remedies note's
  F-05. It is the observation the lead's F-06 elevated into REQ-06/SC-07, and the plan panel records
  it again as finding `PF-7b29d51a6c8f4b6dbdcba528ca92d5ff` (`plan.yaml`'s `panel.findings`).
- A later reader citing "F-05" must name which of the two documents it comes from.
