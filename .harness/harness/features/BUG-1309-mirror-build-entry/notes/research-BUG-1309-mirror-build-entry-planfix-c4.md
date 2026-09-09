# Plan fix c4 — rulings applied, pre-panel — BUG-1309

**All five edits and both verify hardenings are in `plan.yaml`, applied through
`plan-merge.py amend` (10 compare-and-swap field replaces; `apply` is add-only and exits 7 on a
changed value). `check-plan-routes.py` exits 0. `approval.status` is still `pending`. T-07's
retention BEHAVIOUR is unchanged — only the record around it moved.** This note supersedes item 3 /
R1-R2 of `…-goalcheck-plan-c2.md`: the premise of the predicted INV-29 refusal was re-measured and is
false, so the c2 remedy (sweep an era `recovery-required`) was NOT applied.

## What each ruling now says

| Ruling | Where | The text now |
|---|---|---|
| R8 | `D-08.choice` / `.because` | The frozen set governs the THREE REFUSALS (T-04 Build, T-05 merge, T-06 INV-37); post-merge retention (T-07) keys on the RECORDED VALUE — era + absent key is swept, any recorded `recovery-required` is retained, era or not. `because:` carries settled bullet 8 as the reason and states the old INV-29 clause is false as measured, replacing it. The one-definition clause and the `recovery_command_for` sentence survive verbatim in substance |
| R9 | `T-04.intent` | The `recovery-required` branch now spells TWO literal strings: non-era keeps the merge-refused sentence; era prints "Build proceeds. This feature predates the build-entry receipt … so its merge is not refused …", carrying no `open` token in any form |
| R10 | `T-07.intent` | The WHY paragraph is CORRECTED in place: INV-29 classifies terminal only on a LANDED `status: done` (`worktree_terminal.py:389-394`), and a feature owing a receipt never reaches that station (`gh-sync.py:1799-1800` skip returns before `_record_pr` `:1962` and `_record_station(..., "done")` `:1975`), so retention does not trip it; INV-37 (T-06) is the guard that speaks. Retention is stated DELIBERATE and not to be "fixed". The era-pair sentence that justified itself "under INV-29" is corrected too |
| SC-06 gap | `T-07` | New case `T-07 era-exempt recovery-required keeps the worktree`, declared a PAIR with `T-07 era-exempt absent build_entry is swept`, one without the other a REJECTED return |
| Hardening 1 | `T-06.verify` | Rejects `^FAIL`, then requires `ok - <name>` for 9 now-named cases. Bed shape confirmed at `tests/integration/test-check-state.py:1895-1898` (`ok - <name>` / `FAIL - <name>`, column 0) |
| Hardening 2 | `T-05.intent` + `.verify` | Intent carries the "THE CASE NAMES BELOW ARE A CONTRACT" block with 13 literal names and the `ok    <name>` / `FAIL  <name>` shape it must copy (`tests/integration/test-gh-close-gate.py:25-31`); verify rejects `^FAIL` and asserts all 13, then runs `python3 tests/unit/test-omp-hooks.py` unchanged |

## Pointers confirmed at source (worktree)

- `worktree_terminal.py:389-394` — `if station == "done": klass "terminal"`, station read from the
  LANDED plan.yaml (`:379-380`). Cited lines are exact.
- `gh-sync.py:1799-1800` `skip("no recorded milestone — nothing to close")`; `_record_pr` at `:1962`;
  `_record_station(feat_dir, "done")` at `:1975`. The grilling note's `:1960-1976` was a range; the
  precise lines are as written here.

## Measured after the edits

`yaml.safe_load` OK · tasks **9** · decisions **9** · REQ **10** · SC **10** · `approval.status:
pending` · `status: plan` · `check-plan-routes.py … plan.yaml` → `0 violation(s)`, **EXIT=0**
(3 expected DEC-174 deviations, T-04/T-06/T-07). Every case name in each amended `verify:` was
machine-checked to appear verbatim in that task's `intent:`.

## Reported, NOT changed

1. **T-05 `files:` names `tests/unit/omp-hooks.test.ts` while `verify:` runs
   `tests/unit/test-omp-hooks.py`. Both exist and this is CORRECT** — the `.py` is a 17-line registry
   wrapper that shells out to `bun test` on the `.ts` (`tests/unit/test-omp-hooks.py:14-17`). No
   defect; left alone as instructed.
2. **SC-06 (`BRIEF.md:118-120`) does not contradict any ruling — it under-specifies.** Its scenario is
   a recovery attempted while GitHub is unavailable, i.e. a RECORDED `recovery-required`, which the
   corrected T-07 retains and names. It does not say which corpus it grades; c2's R5 clause is now
   unnecessary, but SC-06 would read better naming the recorded value. BRIEF untouched.
3. **SC-04 (`:105-113`) is consistent** with R8: it grades merge ALLOW for the era corpus, which is a
   refusal, not retention.
4. **c2 R7 left in place**: T-04's era case still offers "add one such name to the fixture set the
   test controls", which the frozen literal makes impossible. Not in this dispatch's scope.
5. **c2 R6 left in place**: no fixture is staged under a `BUG-*` directory name, so REQ-01's
   FEAT-*/BUG-* symmetry clause is still asserted by no case.
6. **Placement tightened inside hardening 1**: T-06's two `recovery_command_for` cases are now pinned
   to `tests/integration/test-check-state.py` (they previously could live in the feature_schema bed).
   Forced by naming them in a `verify:` that only runs that runner.
7. T-04's existing non-era `recovery-required` case gained the words "NOT in the era set" so the new
   era case reads as its pair; no verdict changed.

## c4b — the unsatisfiable T-04 assertions, fixed (2026-09-06)

**Two assertions in T-04 could never hold against T-04's own literal message strings. Both are
fixed by changing the ASSERTION, never the message.** Both message strings are byte-identical to
c4 (region re-read from the loaded `intent:` after the amend). Only `tasks:T-04.intent` was
written, through `plan-merge.py amend --key tasks --id T-04 --field intent --expect-sha256
bf086e1f…` (compare-and-swap; `apply` would have exited 7 CONFLICT on a changed value).

1. **The era case** ("T-04 era recovery-required does not claim a refusal") required stderr NOT to
   contain "refused", while the era line says "so its merge is **not refused**". A correct
   implementation failed its own case, and the case name is in `verify:`, so T-04 could never
   verify. Now: stderr must NOT contain `"MERGE is refused"` (the non-era clause this case exists
   to rule out), MUST contain `"is not refused"`, and must NOT contain `"open"` as a substring in
   any form (that one already held — the era line carries no `open`). The case also spells out why
   asserting the absence of "refused" is wrong, so a later reader does not restore it. Exit 0, the
   attempted card write, "predates", "Build proceeds" and the PAIR sentence are unchanged, and the
   case NAME is byte-identical, so `verify:` is untouched.
2. **The non-era `recovery-required` case** (unnamed; not in the `verify:` loop) asserted stderr
   carries the word `"merge"`, while its literal line spells it `"the MERGE is refused"` — no
   lowercase `merge` anywhere in it. Case-sensitively unsatisfiable, the same defect class. Now it
   asserts the substring `"MERGE is refused"`, which also makes the two halves of the pair exact
   mirror images of each other.

**Every T-04 case composed against the literal string it will see.** `non-era absent refuses` —
`refuse()` prints `gh-sync: REFUSED — …` to **stdout** (`gh-sync.py:164-169`), and the open line
carries `gh-sync.py open`: holds. `station discriminator` — the recover-terminal refusal contains
no `open` substring: holds. `era-exempt continues` — the era absent line carries `predates` and no
`REFUSED`; `operator-approved` contains no `open`: holds. `opened` / negative control: no message.

**Reported, not changed** (D-08, T-05, T-06, T-07 verified unchanged by sha over
`intent:`+`verify:` — T-05 `59e1875af6f6`, T-06 `bf5db1706d6a`, T-07 `e83f4dbfdc4c`, D-08
`bc192f515690`, all identical before and after): **no unsatisfiable assertion found in any of
them.** T-05's era allow line carries `predates` and no `open`; its outage line carries
"could not verify" and "mirror"; its deny reason carries neither. T-06's recover-terminal INV-37
line contains no `open` substring. T-07's era line carries `predates` and no `SKIP removal`, and
its retention line carries `SKIP removal` and no `predates`.

**Measured after the edit:** `yaml.safe_load` OK · tasks **9** · decisions **9** · REQ **10** ·
SC **10** · `approval.status: pending` · `check-plan-routes.py … plan.yaml` → `0 violation(s)
across 1 plan(s)`, **EXIT=0** (three expected DEC-174 deviations, T-04/T-06/T-07).
