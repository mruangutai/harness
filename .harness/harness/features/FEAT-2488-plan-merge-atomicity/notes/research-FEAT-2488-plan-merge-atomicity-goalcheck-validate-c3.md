# Goal-check (validate c3) — FEAT-2488-plan-merge-atomicity

- Pin: `2eab047b9971bc428db21d1527ce614826ebc692` · Base: `2491336e` · Fix delta: `13500626..2eab047b`
- Run: r-20261124-4-validate-validator · Reader: harness-pm (goalcheck)

**BLUF: PASS.** All three perspectives **pass**, and all seven SCs are **met** at the pin. MF-7 and MF-8 are **closed by implementation repair under the same contract** (P-06). I measured each with a mutant or an old-code run, not from the build note. The two ledgered amendments truthfully describe the shipped code. The signature stands: `approval.status: approved`, and neither amend receipt printed `APPROVAL-RESET`. All six `decisions_affected` rows are `keep`, so none is graded. c2's F-2r is **closed**. One form advisory is new (F-3). No regression found.

Binding: the worktree's `.claude` and `tests` equal the pin (`git diff --quiet 2eab047b -- .claude tests`, rc 0). HEAD is `0ab2c053`, which touches only `feature.json` and the gate note. Every run below had HARNESS_AGENT_TYPE, CLAUDE_PROJECT_DIR and HARNESS_PROJECT_DIR unset.

## Perspectives

| Perspective | Grade | Carried by | Evidence |
|---|---|---|---|
| operator | **pass** | SC-01, SC-04, SC-07 | Torn states (a), (b) and (c) converge through both verbs and through a feature.json write, and a further run changes nothing. Divergence refuses at exit 5 naming the journal. A FIFO journal swapped in after the lstat now refuses at exit 5 and is never read (MF-8). A closed or broken output stream after the commit no longer turns a landed amendment into a traceback (MF-7). amend stdout is locked. The six other suites are unedited and rc 0. |
| code maintainer | **pass** | SC-02, SC-03, SC-06 | There is one primitive, `harness_merge.locked_pair_update`. No plan_merge module carries rename or journal code: `git grep mkstemp\|os.replace\|harness-merge.journal\|JOURNAL_SUFFIX 2eab047b -- …/plan_merge/` returns rc 1. The fsync order is unchanged. The docstrings were updated truthfully for the fstat (`harness_merge.py` module doc, `_require_regular`, `_journal_bytes`). |
| reader (qa / reviewer) | **pass** | SC-05, SC-01 | Every torn state is built on disk. The SC-05 successors are untouched in this delta. The new MF-7 cases (2488/k, 2488/l) and the MF-8 case (`case_fifo_swapped_after_lstat_refuses`) each go red against the defect (see the probes below). |

## SC status

- **SC-01 (automated, integration) — met.** I ran the pin's `tests/integration/test-plan-merge.py` myself (rc 0, 0 FAIL rows; the file exits 1 on any FAIL). That covers 2488/a–l, including 2488/e, e/b and e/c with their `/d` cases. The unit file `test-harness-merge-journal.py` gave rc 0, 165/165.
- **SC-02 (inspection) — met.** The grep above returns rc 1, and `guards.py` still has no `_replace_bytes` or `_restore_plan`. `amendments.write_plan_and_ledger` makes one `locked_pair_update` call and then calls `_relay_after_commit` (`guards.py`). That relay is advisory output, not journal I/O.
- **SC-03 (inspection) — met.** At the pin's `harness_merge.py`:
  - `_publish_journal` fsyncs the temp journal and then `os.replace`s it (:540-541).
  - `_commit_published` fsyncs the directory (:555) before the member loop, and runs `os.unlink(journal_path)` (:560) after it.
  - The delta does not touch `replace_bytes`.
- **SC-04 (automated, integration) — met.** These 2488/g rows pass at the pin:
  - "ledgered … AMENDED judgement=amendment, APPLIED plan, APPLIED feature.json"
  - "unledgered … AMENDED then APPLIED plan"
  - "neither carries APPROVAL-RESET"

  `_print_receipts` prints the same lines in the same order and then flushes, so a normal stdout gets the same bytes.
- **SC-05 (inspection) — met, carried from c2.** The delta's test diff does not touch the three successors.
- **SC-06 (inspection) — met.** This delta does not edit `feature_json_write.py`, `plan-merge.py` or the lock-order text. `amend.py` still has no `APPROVAL_RESET` token.
- **SC-07 (automated, integration) — met.**
  - `git diff --quiet 2491336e 2eab047b` is rc 0 for each of the six named suites.
  - I ran all six at the pin, and each gave rc 0 with 0 FAIL rows.
  - test-plan-merge.py's pre-existing cases pass, as above.

## MF-7 / MF-8 closure (measured)

- **MF-8 — closed.** I ran the pin's unit file against `13500626`'s `harness_merge.py` in a temp tree. It went red on exactly 6/165 checks: `fifo swap via recover_journals(plan)` and `via locked_update(feature.json)`, where the refusal never fires, the members are rewritten, and the FIFO record is consumed. At the pin it is 165/165. The swap-timing precondition check passes in both runs, so the red reaches the branch under test (O-06).
  - Code: `_regular_fd_bytes` fstats the descriptor before `fh.read()`.
  - `_journal_bytes` raises UNREADABLE naming the journal and never unlinks.
- **MF-7 — closed.** I ran two single-point mutants of the pin's `guards.py`, each in a temp tree:
  - **(A)** The relay fallback suppresses `OSError` only. This reddens `2488/k` "write_plan_and_ledger returns normally on a closed stderr" and "_locked_plan_update returns normally".
  - **(B)** `_print_receipts` catches nothing real. This reddens 2488/k's receipts row and 2488/l (both verbs): "exits 0 with no Traceback" and "stderr says the write landed".
  - Each mutant reddens a distinct set of rows, so neither fix is ever-green (O-08).

## Disclosed side effect: `_locked_plan_update` now shares the relay

**Graded: no regression.** Twelve callers pass through `_locked_plan_update`: amend, apply/union, delete, panel ×2, stations ×2 and approval ×2. Their success path is unchanged: the same relay output, then the verb's own prints.

The only path that changes is a feedback print that raises OSError or ValueError after the plan has already landed:
- **Before:** a traceback and exit 1, with the verb's receipts never printed. For sign-approval that meant `RESUME:`/`SIGNED` were never printed. For apply, an `APPROVAL-RESET:` receipt that the gh-sync rule keys on was never printed.
- **Now:** one stderr note, then the receipts print and the verb exits 0.

This reports a landed write truthfully. The operator clause "behave as before" is about a world with no journal and working streams, and that world is byte-unchanged (SC-07 suites, SC-04). The other verbs' own receipts still use plain `print`, so a broken stdout after a commit there still tracebacks. That is pre-existing, unchanged and outside DEC-229's pair scope. I note it only, with no finding.

## F-2r (c2) — confirmed closed

`_feature_json_write_converges` runs `_settles` after each of 2488/e, e/b and e/c. `_settles` asserts that one more record-amendments run exits 6 "recorded before" and that `(_bytes(plan), _bytes(fj))` equals the snapshot taken before it. All three `/d` pairs pass at the pin. A raw-byte equality check directly reddens c2's failure scenario (a re-run that rewrites the plan). This is fixed under the same contract; it is not a waiver.

## Ledgered amendments vs the shipped code (DEC-23)

- **feature.json at the pin** has `amendment T-01.intent` and `amendment T-02.intent` (2026-11-24T02:34). The receipts are `notes/fix-c2-build/amend-T-0{1,2}-receipt.txt`: AMENDED … judgement=amendment, two APPLIED lines, and no APPROVAL-RESET. The plan at the pin reads `approval.status: approved`, so **the signature stands.**
- **T-01 (4) — truthful.**
  - "lstat'd first … at the name … never opened": `_require_regular`.
  - "opened O_NOFOLLOW|O_NONBLOCK, the opened descriptor fstat'd before any byte is read … FIFO … refused unread and left in place; a directory or device the same way": `_journal_bytes` and `_regular_fd_bytes`, measured above.
  - "A symlink fails the open": O_NOFOLLOW raises OSError, which becomes UNREADABLE.
- **T-02 (7) — truthful.**
  - The fallback suppresses `(OSError, ValueError)`: `guards.py#_relay_after_commit`.
  - `write_plan_and_ledger` and `_locked_plan_update` share that relay.
  - amend and record-amendments receipts go through `_print_receipts`, which exits 0 and prints a "landed" stderr line (2488/l).
  - Normal stdout is byte-identical (2488/g).
  - "No write after a commit can turn a landed amendment into a traceback": true for both amendment verbs. Their only post-commit output is the relay and `_print_receipts`, and both are guarded.
- **Signed SC and perspective text:** no clause is narrowed. SC-01's "a feedback failure after both files … advisory" is now true for closed streams as well.
- **Scope (P-17):** the code files changed base→pin are all inside T-01's and T-02's `files:` (harness_merge.py, plan_merge/*, feature_json_write.py, plan-merge.py, and the two tests, plus `canonical-reader-classification.json` from c1). The delta adds none.

## Decision dispositions (Mode 2)

At the pin `decisions_affected` has six rows: DEC-229 ×2, DEC-199 ×2, DEC-174 and DEC-230. All are `keep`, so none is graded and none needs a DECISIONS.md landing. `git diff --stat 2491336e 2eab047b -- .harness/harness/docs` is empty. P-16 still holds: the fstat refusal and the post-commit guards add no path that leaves one file of the pair landed without a journal.

## Findings

- **F-3** (form, low/advisory; binds T-01 and T-02 plan text; not code). In the pin's `plan.yaml`, T-02.intent's deviation (7) comes after the paragraph's closing line "The signature stands (DEC-23); this is the ledgered judgement." T-01.intent (4) also lost the blank line that separated it from (5).
  - **Failure scenario:** a later reader or a P-16 audit takes the closing line as the end of the deviation list and skips (7), so the relay/receipt contract goes unread.
  - The text is truthful. Tidy it at the next amend, or leave it; it is not a gate.

## Method

- I read every artifact with `git show 2eab047b:`.
- I ran the suites and mutants myself in temp copies (`git archive`). Nothing in the repo was written apart from this note.
- QA's pin-bound manifests were not yet in `runs/r-20261124-4-validate-validator/` when I read it. The automated verdicts rest on my own runs at the pin, and on QA's manifests once they land.

## Principles applied

- **P-06:** I re-measured MF-7 and MF-8 against the defect (old code and mutants) rather than accepting the build note. Both are fixes under the same contract.
- **P-16:** I graded the amendment prose (4) and (7) clause by clause against the shipped code.
- **O-07 / O-08:** I ran the pin's tests against the old file, and used one mutant per branch.

## Open questions

- None blocking.
