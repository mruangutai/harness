# Goal-check (plan) — FEAT-2581 feature_record package — plan-product c1

**BLUF: the plan delivers the operator's stated intent with two narrowings the signer must see, and
the record has not caught up with the reader wave.** The code maintainer perspective passes. The
operator perspective is **partial** for two reasons:
(1) Settled Q3 asks that "the same pre-existing test cases pass on both sides", but T-03 grades per
*file* (exit 0, no FAIL line), not per case. FEAT-70's receipt compared case lists.
(2) The D-02 diagnostics are emitted by check-domain and check-state, never by `feature-record.py`,
so no ledger measures them. They are shown in an inventory but never enter the red-until-ruled gate.
`plan-merge.py check`: exit 0, 0 failures, no OVERLAP lines.

Judged against `.harness/notes/grilling-feature-record-package-2026-11-27.md` (stated intent). Plan
read from the working tree of the worktree (feature dir untracked at `e12381fd`; plan pending).

## Perspectives (BRIEF `## Done when — by perspective`)

- **code maintainer — PASS.** SC-01 (T-01), SC-02 (T-01 regrades, T-03 grade-assert at pin and
  baseline), SC-07 (T-01 re-key, T-03 audit), SC-09 (T-02). The package layout, the absence of
  the flat modules, the merge CLI and the re-export, and the AST sweep for shims are all in T-01's
  verify. The decision record is amended in place by T-02 (DEC-259, DEC-220, DEC-150).
- **operator — PARTIAL.** SC-03/SC-04 (T-01 edits, T-03 per-file suites), SC-05 (T-03 CLI
  ledger, three spawning classes, zero-count FAIL), SC-06 (T-03 replay), SC-08 (T-01 literals,
  T-03 inventory). Same path and verbs: T-01 keeps the entry path and the argparse tree, and the
  T-03 ledger and replay hold the bytes. Gaps:
  - *Case identity.* T-03 records "file, exit status and every FAIL line" per side. A test case
    dropped or skipped at the pin leaves its file green. FEAT-70's `feat70-cleanpin.py` asserted
    `b_cases == pre_existing` (git show a98451c5). Test files here have no uniform CASES shape
    (`grep -L` finds 10+ files with neither CASES nor `def case_`/`def test_`). The cheapest fix
    is for T-03 to record each file's stdout pass-line set per side and require that every
    baseline line is present at the pin.
  - *D-02 output never measured.* The ledger records only processes whose argv[0] is
    `feature-record.py`. The replay runs `feature-record.py` and `validate-feature-json.py`. At
    the baseline, neither of those emits a `feature_schema` or `plan-merge.py` diagnostic
    (grep of feature-record.py, validate-feature-json.py and feature_json_write.py: the only hit
    is an argv path in close-run). So the D-02 changes to the check-domain, INV-23/26/37/40 and
    INV-7, refusal-evidence and harness_config texts never produce a `divergence:` record.
    T-03 lists them by *template* in build-divergences.md, but nothing requires a ruling on
    them. SC-08's "none is exempted from the ledgers' red-until-ruled rule" holds only because
    no ledger reaches them. The same applies to the `check-state.py --list` reads-column change
    (research §11). In effect the operator rules on these at the D-02 signature, which the
    perspective ("none is exempted in advance") forbids. The fix: T-03 gives each inventory item
    a record id, and overall is PASS only when divergence-rulings.json carries a ruling for each.

## Settled rulings

- **Destination — delivered-with-operator-question.** Package, thin entry, same-change
  migration, deletions and #2569 are all in T-01/T-02. However, "behaviour is byte-identical,
  the only exception the 12 functions" is **extended**: D-02 changes 7 diagnostic literals by
  design, and 3 RepoModuleError renderings, traceback frames and the `--list` reads column
  change with them. The receipts can reach `overall: PASS` only through operator rulings.
- **Q1 scope — delivered.** T-01 moves the CLI verbs, both flat files and the loader (the full
  symbol list is in T-01's verify `moved` set). The import loop goes because `opt_int` becomes
  local to read.py.
- **Q2 module map — delivered.** It follows the map. Placements the map is silent on are recorded
  with reasons in research §4: `_read_doc`/`_runs`/`SCHEMA_REFUSAL_CODE` go to read, the
  `_apply`/refusal protocol to write, `now_iso` and the helpers to judgements. Added edges
  schema→binding and spend→read are justified there. read→artifact_accessors stays one-way.
- **feature-json-merge.py — delivered** (T-01: script, test, its one classification row, its
  durations row). The grilling's "3 rows" was a `grep -c` line count; there is 1 row by `file`
  (re-measured at e12381fd).
- **Q3 identity proof — delivered-with-operator-question.** T-03 has a separate pin task, clean
  detached checkouts, FEAT-70's structure (its clock freeze and tempfile counter are FEAT-70
  precedent; sitecustomize replaces FEAT-70's PLAN_MERGE_BIN shim because there is no env seam),
  the CLI ledger, the replay and red-until-ruled. **Narrowed:** case identity is now per-file
  (above). The replay excludes FEAT-2581's own feature.json (justified: that record changes) and
  runs a fixed verb sequence. **Kept against a reader:** the bun leg PF-d35d903d is open as a
  non-blocking operator question.
- **Q4 grade bar — delivered.** T-01 regrades the code. T-03's grade-assert is green at the pin
  and red at the baseline with exactly the twelve `below_bar` lines. New helpers are listed.
- **#2569 — delivered.** D-03 and T-01 (`ctx._load_hash_module` via
  `load_repo_module("plan_merge.approval")`, re-export removed), T-02 (DEC-259 exception struck),
  `source_issues: [2581, 2569]`. The PR closing it is a ship step that no task owns, which is
  normal.
- **Q5 mission — delivered.** All three tasks are main-session-direct (DEC-174), and the lanes
  table agrees.
- **Updated with the move — delivered-with-operator-question (extended twice).**
  - D-01 changes the `remedy` of 24 non-moving caller rows, plus canonical_reader_audit's
    category, remedy and T07 keys. The rule was "only file and id"; at source the audit matches
    on remedy, so this is necessary.
  - Tests change expected values beyond imports and targets: the D-02 literals,
    test-check-plan-routes' fixture import and remedy, test-worktree-terminal's FeatureJsonError
    owner, and (61.b)'s expected `plan_merge/approval.py did not import`.
  - **INV-40 (61.b):** T-01 re-targets the observer and its verify proves the new seam is live.
    The research (§8) measured that (61.b) never tested stale registration even at the baseline.
    Repairing that needs a new test seam, which falls outside this ruling. The plan carries no
    task and no open question for it, so the operator must decide whether it is a backlog item.

## Not yet specified

- **artifact_accessors rows — delivered** (research §2). All 4 rows (strict_json_loads,
  load_frontmatter, load_omp_config, load_harness_json) stay. The grilling's "9" was a line
  count. Re-measured: 4 rows by `file`, 24 remedies at e12381fd.
- **copy_executable_package delegate — delivered** (research §3, T-01: none added).
  test-feature-record.py copies the whole bin, and the selective copies in
  test-check-plan-routes.py add `feature_record/`.

## Out of scope — touches

- `feature_corpus.py`: import line only (T-01), as the BRIEF discloses.
- `check_state/feature_record.py` invariants: **touched beyond load targets**. The INV-23 literal
  changes (D-02) and the INV-7 rendering changes by consequence. Invariant logic is untouched.
- Other long bin files: check-domain gets the D-02 literal edits plus imports; validate-digest,
  gh-sync and the others get imports only. No splits.
- artifact_accessors' other loaders: docstrings only. Test-code layout: untouched.

## Record state the signer must see

The `panel.findings` in plan.yaml still show all 9 as `disposition: open`, 4 of them high. Research
§8 says the 4 highs and the form findings were applied. Before signature, either re-run the panel
or record rulings (`approval.rulings` by PF-id). The applied text alone does not close them.

## plan-merge.py check (verbatim, exit 0)

```text
OK T-01 11 anchor(s) resolved
OK T-02 2 anchor(s) resolved
OK T-03 1 anchor(s) resolved
CHECK /Users/molchairuangutai/GitHub/harness/.claude/worktrees/harness/FEAT-2581-feature-record-package/.harness/harness/features/FEAT-2581-feature-record-package/plan.yaml against /Users/molchairuangutai/GitHub/harness/.claude/worktrees/harness/FEAT-2581-feature-record-package: 3 task(s), 14 anchor(s) resolved, 0 failure(s)
```

## Principles applied

- harness-principles rule 15 (never falsify the record): the operator perspective is graded
  partial rather than softened, and every narrowing is named.

## Re-grade after apply send-back 1

**BLUF: the plan now delivers the operator's stated intent, and both perspectives PASS.** The two
blocking gaps are closed in the plan's text. GC-01: T-03 compares case identity per file. GC-02:
every D-02 inventory item becomes a red-until-ruled `d02#` record, either MEASURED or UNREACHED.
GC-03 is closed on the record: 7 findings are resolved, and the 2 left open are the operator's
call. GC-04 and GC-05 are carried as non-blocking operator questions. No criterion that passed
before is broken by the send-back edits. Two advisory notes for the lead follow below; neither is
a goal gap. `plan-merge.py check`: exit 0, 0 failures, no OVERLAP.

Judged against `.harness/notes/grilling-feature-record-package-2026-11-27.md`. The plan and BRIEF
were read from the worktree's working tree: the feature directory is untracked at `e12381fd` and
the plan is `approval.status: pending`. All three task verifies parse as Python (`ast.parse`):
T-01 is 25 lines, T-02 8 and T-03 30.

### Perspectives (BRIEF `## Done when — by perspective`)

- **code maintainer — PASS (unchanged).** SC-01, SC-07 (T-01; T-03 audit), SC-02 (T-01
  regrades; T-03 grade-assert, green at the pin and red at the baseline with exactly the twelve),
  SC-09 (T-02). The send-back touched none of T-01's layout or T-02's verify. Coverage holds.
- **operator — PASS.** It is carried by:
  - SC-03 and SC-04: T-01 edits, then T-03 suites per file, with the FAIL list identical to the
    baseline's.
  - SC-05: the T-03 CLI ledger, three spawning classes, zero-count FAIL.
  - SC-06: the T-03 replay.
  - SC-08: T-01 literals, then the T-03 `d02_item` and `d02#` records.
  - SC-10: T-03 `case_set` and `cases#` records (new).

  Every kind of difference (`cases#`, `d02#`, ledger, replay) is a `divergence:` line. T-03's
  verify requires each to be RULED, and requires a `divergence-rulings.json` entry with `by`,
  `date` and `reason`. "None exempted in advance" therefore now holds by construction rather than
  by absence.

  Disclosed narrowing, signed in the BRIEF's `## Verification gaps`: an UNREACHED D-02 item is
  shown to the operator as its old and new *source template*, not as emitted bytes. The
  perspective's "exact old and new bytes" is met only for MEASURED items. Static expectation: 2,
  10 and 11 are reached, and 1 and 3–9 are not. This matches the grilling, whose intent is
  red-until-ruled, which holds for UNREACHED records too. It is not a gap against stated intent.

### Settled / Not yet specified (re-graded)

- **Destination — delivered-with-operator-question (unchanged).** "Byte-identical, the only
  exception the 12" is still extended by D-02. D-02's choice now says outright that its
  signature "authorizes the source change, never its output bytes in advance", and PF-7999 stays
  open, so `sign-approval` must record an `approval.rulings` entry for it.
- **Q1, Q2, feature-json-merge, Q4, #2569, Q5 — delivered (unchanged).** The send-back did not
  touch T-01's move list, map or verify, or T-02.
- **Q3 identity proof — delivered.** The narrowing my first grade raised is gone. Case identity
  is per file, using FEAT-70's `b_cases == pre_existing` from T-03's `Case identity` paragraph.
  The bun leg is still an open operator question (GC-05).
- **Updated with the move — delivered-with-operator-question (unchanged).** D-01 remedies, and
  the test expectation changes enumerated in T-01's intent. T-03 now also writes "every test
  expectation T-01 changed, by file and case, with its old and new bytes" to
  build-divergences.md, so the operator sees each one.
- **Not yet specified, both — delivered (unchanged).** There are 4 artifact_accessors rows, and
  no `copy_executable_package` delegate is added.

### GC-01..GC-05 — closure

- **GC-01 (case identity) — CLOSED.**
  - T-03 intent: "a file's case identity is the ordered list of its stdout lines whose first
    whitespace-delimited token is ok, ok:, PASS or PASS:, … followed by one entry <outcome> <test
    id> per unittest result". Bun JUnit covers omp-hooks.test.ts.
  - "A DIFFERENT file gets one divergence record cases#<file> … a dropped, added, renamed,
    reordered or newly skipped case is a difference."
  - T-03 verify: `set(got)==want`, where `want` is the baseline `ls-tree` minus `baseline_failing`
    and the deleted test, plus omp-hooks.test.ts. Then `s=="SAME" or "cases#"+f in dv`, and
    `git diff --quiet` for any file with fewer than 2 entries.
  - BRIEF SC-10 (operator, inspection) carries it, and T-03 traces SC-10.
  - Re-measured: none of the six files with fewer than 2 entries names a moved symbol (`rg` for
    feature_schema, feature_json_write, feature-json-merge, load_feature_json, FeatureJsonError,
    signed_task_hash and feature-record gives 0 in each). The `git diff --quiet` conjunct is
    therefore satisfiable under T-01's intent.
- **GC-02 (D-02 never measured) — CLOSED.**
  - T-03 intent, "D-02 inventory, measured (SC-08)": items 1–11 have quoted markers, plus a
    residual class that catches relocated traceback frames by module name. An item with any
    capture is `MEASURED` and must show at least one `d02#` difference; one with none is
    `UNREACHED` with exactly one `d02#<n>:unreached` record.
  - Verify: `set(d2)=={1..11,"residual"}`, the per-item record rule, `gate_captures` non-zero on
    both sides, and every `dv` RULED.
  - D-02's choice and BRIEF SC-08 are reworded to match.
- **GC-03 (panel record stale) — CLOSED on the record.** `panel.findings` shows 7 `resolved`,
  each with a `resolved_by` naming T-01 or T-03 (PF-ccd4, PF-e7dd, PF-b3de by T-03; PF-d91c,
  PF-aaf4, PF-2782, PF-dc97 by T-01). PF-7999 (high) and PF-d35d stay `open` for the operator.
  Each resolution is visible in the text: the copied-bin class and the pin binding are in T-03's
  verify, the observer re-target is T-01's verify f59 block, `_runs`→read.py is in T-01's
  intent, the structural AST verify is in T-01, there are 11 decisions_affected rows, and there
  is one fixed fixture root. *Advisory A1, below.*
- **GC-04 ((61.b) stale-registration test gap) — CLOSED as a carried question.** It is raised as
  the apply digest's OQ-GC04 (non-blocking, backlog recommended) and recorded in research §9. No
  task fixes it, which is correct under Settled's rule that tests change only imports and
  targets.
- **GC-05 (bun leg) — CLOSED as a carried question.** PF-d35d903d is still `open`, and the apply
  digest carries OQ-BUN. T-03 now says the bun JUnit run "stays even if the operator drops the bun
  leg from the CLI ledger", so dropping the leg cannot weaken SC-10.

### Did the send-back break anything previously passed? No.

- **SC-03 "only imports and copy/patch targets changed" against T-01's expectation edits.** D-01
  and D-02 change expected values only in integration files: test-check-plan-routes,
  test-worktree-terminal and test-check-state-feat59. A grep of `tests/unit` for the D-02
  literals and for `FeatureJsonError` finds only `accessors.FeatureJsonError` owner references,
  which are import-target changes. SC-03 holds. SC-04 carries no such clause.
- **SC-03/04 FAIL wording.** "Same FAIL lines as the baseline" is stricter than "no FAIL line"
  for every file except test-factory-claim-mutation.py, which the old wording would have
  silently excluded. Not weakened.
- **SC-08 rewording.** It still names every D-02 diagnostic and its loaded module, and now adds
  measurement. Not weakened.
- **SC-10 new.** It is traced (T-03), and its unnamed-file bound is enforced in verify.
- **D-02 divergence records.** They widen the red-until-ruled set; they exempt nothing.

### Advisory, not goal gaps (for the lead)

- **A1. The panel has not re-read these resolutions.** Four of the 7 resolved findings are
  `substance`, 3 of them high, and the plan's author marked them resolved without a reader
  re-run. panel-recording.md says "A substance finding re-gates only the tasks it names"
  (T-01, T-03). Whether this cycle owes the scope reader a re-read of T-01 and T-03 is the lead's
  call. The text does carry each fix.
- **A2. `baseline_failing` is self-declared by the receipt** (P-03). T-03's verify subtracts
  every `baseline_failing:` line from `want` without bounding it. A mis-measured baseline could
  therefore exempt files from the SC-03, SC-04 and SC-10 comparisons, and the verify would stay
  green. The intent pins the measured set as test-typescript-typecheck.py alone. A one-clause
  verify conjunct asserting `bf <= {that file}`, or printing a ruled record for each additional
  file, would close it. The risk is low: the receipt is reviewed by inspection.

### plan-merge.py check (re-run, verbatim, exit 0)

```text
OK T-01 11 anchor(s) resolved
OK T-02 2 anchor(s) resolved
OK T-03 1 anchor(s) resolved
CHECK /Users/molchairuangutai/GitHub/harness/.claude/worktrees/harness/FEAT-2581-feature-record-package/.harness/harness/features/FEAT-2581-feature-record-package/plan.yaml against /Users/molchairuangutai/GitHub/harness/.claude/worktrees/harness/FEAT-2581-feature-record-package: 3 task(s), 14 anchor(s) resolved, 0 failure(s)
```

### Principles applied (re-grade)

- harness-principles rule 15: each GC is graded closed only where plan text closes it, and the
  UNREACHED narrowing and the panel-process gap are named rather than folded into the PASS.

## Addendum 2026-11-27 — repanel-product cycle-2 apply (goal-check NOT re-run, SC-09)

**BLUF: both grades stand; this is a statement of which re-graded text moved, not a re-grade.**
The cycle-2 apply rewrote text these grades rested on: T-03 intent and verify, T-01's pre-commit
gate paragraph, D-02's choice, and BRIEF SC-02, SC-05 to SC-08 and SC-10 plus the Constraints
disclosure. Nothing was graded again, and no reader has read the new text yet.

- **operator — PASS stands.** It rested on four things. Each still holds, and each is now
  stronger:
  - T-03 recomputes ledger, replay, gate and audit differences from the committed per-side
    measurement files. Before, it trusted PASS lines.
  - Every difference stays red until ruled.
  - Case identity per file is unchanged.
  - The D-02 inventory still yields one `d02_item` per item.

  The re-grade's GC-02 text is now stale in one place. A MEASURED item's red record is a
  `gate#<test file>#<ordinal>:<stream>` divergence that a `d02_item_record` line names. It is no
  longer a `d02#<item>:<test file>#<ordinal>:<stream>` record. `d02#<n>:unreached` is unchanged.
  The property the grade cited, red-until-ruled for every inventory item, still holds. Gate
  streams are now compared whole, as raw bytes, so the residual can no longer miss a byte.
  Advisory A2 is addressed in the text: an extra baseline failure needs a ruled `baseline#<file>`
  record. T-01's gate now matches SC-03's four preserved FAIL lines, which removes a
  contradiction the first grade did not catch.
- **code maintainer — PASS stands.** SC-02's grade-assert now runs the committed bytes on stdin
  at the review ref, and its green and red conditions are unchanged. SC-07 now also captures the
  audit at the baseline, which adds a disclosed red record. SC-01 and SC-09 are untouched.

One condition carries forward: these grades say the plan text closes the gaps. They do not say
the findings are closed. The four cycle-2 scope findings, including the restated PF-e7dd0045,
and the reopened cycle-1 PF-e7dd0045 stay open until a reader re-reads the text.

## Addendum 2026-11-27 — repanel2-product cycle-3 apply (goal-check NOT re-run, SC-09)

**BLUF: both grades stand. The operator grade's evidence moved and got stronger; no grade was
re-run.** This pass rewrote T-03's verify and intent, which carry the operator perspective's
SC-05, SC-06 and SC-08. It also added one sentence to the BRIEF disclosure.

- **operator — PASS stands.** Three things changed, and each one narrows what the verify accepts:
  - A record that lacks a stream its kind requires is now refused.
  - `audit_scanned_files` is derived from the raw audit stdout.
  - `build-divergences.md` payloads must equal the recomputed stream pairs. This makes "shown
    to me with its exact old and new bytes" checked, not just asserted.

  Unreached D-02 items are now source-only entries that are structurally distinct, so the
  disclosed narrowing (source template, not bytes) is labelled where the operator reads it.
- **code maintainer — PASS stands.** None of its SC text or task text changed.
- **Settled Q3 (a) — now delivered-with-operator-question (it was delivered).** The BRIEF
  discloses that T-03 exceeds "FEAT-70's receipt-script structure with no new proof framework"
  as the price of PF-14c27514. Only the operator can amend Q3 (a).

## Addendum 2026-11-27 — repanel3-product cycle-4 apply (goal-check NOT re-run, SC-09)

**BLUF: both grades stand; no grade was re-run. Grade-bearing text moved in T-03 (verify and
intent), D-01.because and BRIEF SC-08, the third Verification-gaps bullet and the Constraints
disclosure.** The apply follows the operator's answers (notes/answers-2026-11-27-plan-escalate.md).

- **operator — PASS stands, evidence widened.** T-03's verify is now keyed on four guarantees
  rather than per finding:
  - strict decode: canonical base64 only, validated decoding, so `!!!!` is refused (PF-96cdf9f1);
  - every disclosed field derived: each receipt line except the verdicts, and every
    `build-divergences.md` record body, is recomputed from the committed measurements and from
    `git show` at the baseline and the pin. The d02# source-only file, symbol and source now come
    from a fixed item table plus the refs (PF-3882d444);
  - every SC-08 record present: one `divergence:` record in `build-divergences.md` per divergence of
    every kind, plus `test_change` records carrying each changed test path's diff (PF-cf9cf710);
  - a readable account per ruled id: an injective line rendering inside each record (PF-a37e5b40).

  To make "every disclosed field" true, rather than true only for the four named fields, the
  store gains `suite` records, one per test file per side. `baseline_failing`, `case_set`,
  unit/integration FAIL lines, `d02_item`/`d02_item_record`, `gate_captures` and the pin audit's
  zero-unresolved count are no longer trusted from the receipt. This narrows what the verify
  accepts; it does not change what SC-03/04/05/06/08/10 promise. SC-08's text now names the
  readable rendering, the unreached record's file, symbol and source, and the test-expectation
  diff form. PL-05 (personal ruling at the ship review) is written into the T-03 intent and
  the BRIEF disclosure.
- **code maintainer — PASS stands.** D-01.because now states that the 24 remedy rows are 23
  caller rows plus the moved loader's own row, and records PL-03. SC-07 is unchanged; T-01's text
  is untouched (a non-goal of this pass).
- **Settled Q3 (a) — delivered-with-operator-ruling.** PL-10 accepted the exceedance as disclosed.
  The cycle-4 suite records grow the same store, and the BRIEF discloses that growth beyond PL-09.
- **Carried:** nothing was executed against a built tree, because none exists yet. The verify was
  compiled, its helpers were exercised on toy inputs, and its item table was resolved at
  e12381fd (all 11 symbols found). That is evidence that the verify is well-formed, not that it
  goes green.
