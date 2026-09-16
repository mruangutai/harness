# T-09 verify amendment — already landed; I wrote nothing to plan.yaml

**BLUF.** The amendment this dispatch asked for was already applied and committed at
`f4b2883d` ("[harness] amend T-09 verification command"), before I was spawned. T-09's `verify:`
already holds the target command character-for-character, and that command **passes: `VERIFY-PASS`
at exit 0**. I performed no `plan-merge amend` — re-amending would have needed the target value to
be absent, and it is not.

**One thing needs the operator, and it is not the verify.** The same commit `f4b2883d` also moved
`approval.date` **backwards, from `2026-09-06` to `2026-09-04`**, while leaving
`status: approved`. `plan-merge.py amend` cannot produce that write
(`AMENDABLE_KEYS = ("tasks", "decisions")`, exit 2 on `--key approval`), and every verb other than
`sign-approval` carries approval bytes forward byte-identical. So it came from `sign-approval
--date 2026-09-04` or a hand-edit. `approval:` is the main session's mapping; I did not touch it in
either direction.

## Pre-check: the dispatch's premise is stale

The dispatch expected T-09's `verify:` to still read the `--check` form and told me to STOP if it
read anything else. It reads the target form. Provenance, not corruption:

```
f4b2883d [harness] amend T-09 verification command      <- HEAD, contains the amendment
ffceb68e [harness:t-09] record DEC-220, the Build-entry and Ship split
```

Worktree is clean for plan.yaml (`git status --porcelain` empty, `git diff` empty), so the amendment
is committed, not pending.

## The exact plan diff — verbatim, from `git show f4b2883d -U3`

The operator reads this before re-signing. Note it is **three** changed lines, not the one the
dispatch scoped.

```diff
diff --git a/.harness/harness/features/BUG-1309-mirror-build-entry/plan.yaml b/.harness/harness/features/BUG-1309-mirror-build-entry/plan.yaml
index 9cfa4192..13c94c69 100644
--- a/.harness/harness/features/BUG-1309-mirror-build-entry/plan.yaml
+++ b/.harness/harness/features/BUG-1309-mirror-build-entry/plan.yaml
@@ -1,7 +1,7 @@
 schema: plan/1
 feature: BUG-1309-mirror-build-entry
 approval:
-  date: '2026-09-06'
+  date: '2026-09-04'
   approved_by: Mike Ruangutai
   status: approved
   rulings:
@@ -1357,7 +1357,7 @@ tasks:
       - .harness/harness/docs/DECISIONS.md
       - .harness/harness/docs/DECISIONS-INDEX.md
     verify: |
-      python3 .claude/skills/harness/bin/gen-decisions-index.py --check && grep -q "DEC-220" .harness/harness/docs/DECISIONS-INDEX.md && python3 tests/integration/test-check-decision-anchors.py && echo VERIFY-PASS
+      python3 .claude/skills/harness/bin/gen-decisions-index.py --stdout | diff - .harness/harness/docs/DECISIONS-INDEX.md && grep -q "DEC-220" .harness/harness/docs/DECISIONS-INDEX.md && python3 tests/integration/test-check-decision-anchors.py && echo VERIFY-PASS
     intent: |
       ONE new entry, DEC-220 (219 is the highest today), appended in numeric order at the end of
       .harness/harness/docs/DECISIONS.md, pointer-style and no longer than the neighbouring
@@ -1397,4 +1397,4 @@ tasks:
       and hand-write the " :: <ruling>" tail on the new DEC-220 row - the generator does not
       produce it, so regeneration alone leaves the row without its one-line ruling. Lengthening
       an entry shifts every later anchor, so re-run the generator rather than editing the index
-      by hand, and confirm gen-decisions-index.py --check exits 0 afterwards.
+      by hand, then compare gen-decisions-index.py --stdout against the checked-in index.
```

Hunk 3 is the `intent:` prose the dispatch told me to **leave** and report. It was already rewritten
by `f4b2883d`, consistently with the new verify. Reporting, not touching. T-09's `intent:` no longer
mentions `--check` anywhere (checked by substring, not by eye).

## T-09 `verify:` read back with `yaml.safe_load`

`plan.yaml` loads; top-level keys `schema feature approval status source_issues lanes decisions
panel tasks`. The loaded string, `repr`:

```
'python3 .claude/skills/harness/bin/gen-decisions-index.py --stdout | diff - .harness/harness/docs/DECISIONS-INDEX.md && grep -q "DEC-220" .harness/harness/docs/DECISIONS-INDEX.md && python3 tests/integration/test-check-decision-anchors.py && echo VERIFY-PASS\n'
```

- char-for-char match to the dispatched replacement: **True**
- field sha256 (`amend --show`): `b83166367ac7883f9ae9b752d51f376b7b738a33abcc68e15d6771bfac5ec87d`
- literal block-scalar `|` style preserved (single trailing `\n`, no folding — a folded `>` would
  have collapsed the pipe onto one space-joined line and loaded as a different string)
- T-09 otherwise intact: `status: done`, `change_type: docs`, `traces: [REQ-01, REQ-02, REQ-08]`,
  `files: [DECISIONS.md, DECISIONS-INDEX.md]`, `execution_agent: harness-documentor`
- all 9 tasks `done`; task count 9; no station changed

## The new verify actually runs — final lines and exit code

Run verbatim from the worktree root:

```
ok - test_out_of_range_line_is_reported_and_exits_one
ok - test_malformed_anchor_extension_reports_line_and_exits_one
ok - test_zero_anchors_exits_zero_and_says_so
ok - test_unreadable_target_exits_two_not_zero
ok - test_default_file_is_dev_null_readable_zero_anchors
ok - test_live_authority_anchors_all_resolve
VERIFY-PASS
EXIT=0
```

`diff` printed nothing — zero index drift; `grep -q "DEC-220"` silent-true; anchors all resolve.
All three assertions of the original are intact in substance.

## `approval:` read back from the FILE — signature NOT reset

| field | value |
|---|---|
| `status` | `approved` — **not** reset to pending |
| `approved_by` | `Mike Ruangutai` |
| `date` | `2026-09-04` — **was `2026-09-06`** before `f4b2883d` |
| keys | `approved_by date rulings status` |

All **four** PF- ruling ids survive, each `who: Mike Ruangutai`, each `date: 2026-09-06`, and each
resolves to a live `panel.findings` id:

- `PF-1aa3b36ca9f98cdaf25b30f16e72069f` — standalone fifth gate accepted
- `PF-8bfef7ee69e3adc23a65c02cfd5debd4` — accepted forward-only
- `PF-23f51fd8ee94dc42e9df11fbed42593b` — era wording retained
- `PF-6030c547ed525627c274560e6edd9c05` — resolved by disclosure, D-09

**Plain statement:** the amend did **not** reset the signature — status is still `approved` and no
ruling was stranded. But the signature now carries a date **two days earlier than the rulings
recorded under it**, which is internally inconsistent and predates the rulings it is meant to
cover. Only the main session can rule on that.

Feature station: `building` (unchanged).

## `panel:` intact — three readers `ran`, seven findings

`f4b2883d` touched no line inside `panel:` (see the diff: the only hunks are approval line 4 and two
T-09 lines), so byte-identity holds by construction. Read back anyway:

Readers, all `ran`: `should-not-exist`, `scope`, `goalcheck` — the two existing readers plus
goalcheck, as required.

Seven findings, ids and dispositions unchanged:

| id | severity | disposition | resolved_by | reader |
|---|---|---|---|---|
| `PF-f1684ee3de7606a3e48a4bb9b545a8a9` | med | resolved | T-05 | should-not-exist |
| `PF-1aa3b36ca9f98cdaf25b30f16e72069f` | med | open | — | should-not-exist |
| `PF-a882c9b854373d226faa38bddba8fcc7` | med | resolved | T-02 | scope |
| `PF-6030c547ed525627c274560e6edd9c05` | low | open | — | should-not-exist |
| `PF-8bfef7ee69e3adc23a65c02cfd5debd4` | low | open | — | should-not-exist |
| `PF-23f51fd8ee94dc42e9df11fbed42593b` | low | open | — | should-not-exist |
| `PF-da04a39ff4551e9e99da72e940e64c99` | low | resolved | T-02 | scope |

No finding was reworded, so no content-hash id rehashed and no ruling is a stale risk acceptance.

## Open questions

- **Q1 (blocking the re-sign, not the build):** `approval.date` reads `2026-09-04` but was
  `2026-09-06` before `f4b2883d`, and the four rulings under it are dated `2026-09-06`. `amend`
  cannot write approval, so this was `sign-approval --date 2026-09-04` or a hand-edit. Is
  `2026-09-04` the intended signature date, or should the re-sign restore `2026-09-06`? Main
  session's call — I did not touch it.
- **Q2 (non-blocking):** the dispatch scoped one field but `f4b2883d` changed three lines. The
  third (T-09 `intent:`) is substantively correct and consistent; flagging only so the operator
  is not surprised by a three-line diff where they authorised one.

## What I did not touch

No other task, no other T-09 field, no decision, no `lanes:`, no `panel:`, no `approval:`, no
BRIEF, no station, no commit, no formatter/linter/project suite. HEAD unmoved at
`f4b2883d5bb685978d2bc6e753424e66c4b9287d`. Did not touch `merge-gate.py`,
`test-check-state.py` or `test-post-merge-sweep.py` (main session's concurrent edits).
