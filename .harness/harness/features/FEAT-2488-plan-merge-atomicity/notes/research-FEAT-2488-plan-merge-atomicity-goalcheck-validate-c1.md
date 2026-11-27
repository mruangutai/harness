# Goal-check (validate c1) — FEAT-2488-plan-merge-atomicity

Pin `95606ddbaf9ab36f505328420159d97a10ad820d`, base `2491336e43310cb3e95ae3110d098726ed4dc454`, run r-20261124-2-validate-validator. Reader: harness-pm (goalcheck).

**BLUF: FAIL, at low severity.** Six of seven SCs are met. SC-05 is **partial**: the successor of `case_1985_amend_restores_the_plan_when_the_ledger_fails` forces the same failure, but it does not assert that the nonzero exit *names* that failure, which SC-05 requires word for word. No signed ruling covers a narrower reading. The code under test does name it (probe P4), so the fix is a one-clause assertion in T-02's test file. Operator: pass. Code maintainer: pass. Reader: partial, because SC-05 is its only carrier. All decision dispositions are `keep`, and the plan names no DECISIONS.md landing.

## Perspectives

| Perspective | Grade | Carried by | Evidence |
|---|---|---|---|
| operator | **pass** | SC-01, SC-04, SC-07 | Each torn state converges. Divergence refuses at exit 5. A post-publish failure is reported as journaled. A feedback failure is advisory. amend stdout is locked at base and at the pin. Six suites are unedited and green. |
| code maintainer | **pass** | SC-02, SC-03, SC-06 | One primitive, `harness_merge.locked_pair_update`. fsync covers only the journal and its directory. Lock order is documented. plan_merge carries no rename, restore or journal code. |
| reader | **partial** | SC-05 (plus SC-01's torn-state tests) | The torn-state tests exist (SC-01), and 8 base `check()` calls became 8. But SC-05's clause that each successor asserts "a nonzero exit naming it" fails for 1 of the 3 successors. |

## SC status

**SC-01 (operator, automated/integration) — met.**
- Cases in `tests/integration/test-plan-merge.py`:
  - torn state (a): `case_2488_plan_amended_ledger_not_converges`
  - torn state (b): `case_2488_ledger_landed_plan_not_converges`
  - torn state (c): `case_2488_both_landed_journal_left_converges`
  - (d) folded in through `_settles`
  - next feature.json write (e): `case_2488_a_feature_json_write_completes_the_pair_first`
  - exit 5 divergence (f): `case_2488_a_diverged_member_refuses_and_changes_nothing`
  - post-publish failure reported as journaled (i): `case_2488_a_ledger_failure_after_publish_is_journaled`
  - advisory feedback (h): `case_2488_feedback_failure_after_the_commit_is_advisory`
  - failed replay (j): `case_2488_a_failed_replay_stays_pending`
- Green: `notes/t02-build/01-green-test-plan-merge.txt` has 770 PASS lines and zero FAIL lines. `notes/t02-build/06-verify-T-02.txt` ends `# exit code: 0`.
- Base demonstration (C3): `notes/red-t02-plan-merge-base.txt` lines 702-971.
  - The torn states persist (a/b/c/e: FAIL on "no journal remains").
  - (f) is not refused at base (exit 6 instead of 5).
  - The reports differ: base (i) says "restored byte for byte … nothing landed".
  - (g) passes at base.
- The receipts bind to the pin. Production and the integration test last changed in `9b19ed55`. The later commits `e8d3031a` and `95606ddb` touch only the unit journal test and feature notes, and `git diff 95606ddb -- .claude tests` against the working tree is empty.
- Clauses and combinations no suite assertion discriminates. I executed each myself, with a throwaway probe (since removed) driving the pin's own fixtures with HARNESS_AGENT_TYPE unset:
  - **P2:** "refuses at exit 5 **naming the journal**". Both (f) and the unit test assert only the `JOURNAL DIVERGED` marker. The probe gives rc 5, and stderr names `…/plan.yaml.harness-merge.journal`, which `harness_merge._replay_targets` emits.
  - **P3:** "a further invocation changes neither file" after (e). The suite asserts (d) only after verb re-runs. The probe gives rc 6, both files byte-identical, and the amendment carried once.
  - **P1:** torn state (b) for **record-amendments**. The suite runs (b) for amend only. The probe gives rc 6 "recorded before", both files at their after images, the amendment once, no journal, and (d) byte-identical.
- So SC-01 is met on behaviour. Clauses P2 and P3 are undefended by the suite (finding F-2).

**SC-02 (code maintainer, inspection) — met.**
- `git grep -n "mkstemp\|os\.replace\|journal\|JOURNAL\|unlink\|os.remove" 95606ddb -- .claude/skills/harness/bin/plan_merge/` returns no mkstemp, os.replace, unlink or remove call. The only "journal" hits are message strings and docstrings: `amendments.py:184-229`, `guards.py:30-81`.
- `guards.py` defines neither `_replace_bytes` nor `_restore_plan`.
- `amendments.write_plan_and_ledger` makes one `harness_merge.locked_pair_update(resolved, splice, ledger_path, ledger)` call (`amendments.py#write_plan_and_ledger`). The core takes both locks, publishes and unlinks the journal, and recovers.
- Receipt: `notes/t02-build/03-sc02-grep-and-sc05-count.txt`.

**SC-03 (code maintainer, inspection) — met.** In `git show 95606ddb:.claude/skills/harness/bin/harness_merge.py`:
- `_publish_journal`: `os.fsync(fh.fileno())` at line 444, then `os.replace(tmp_path, journal_path)` at line 445.
- `_commit_published`: directory `os.fsync(fd)` at line 458, before the member `replace_bytes` loop, and `os.unlink(journal_path)` at line 463, after the last member.
- `replace_bytes` (lines 203-219), the body `locked_update` uses, has no fsync.
- Q2(c) accepts the dropped post-unlink directory fsync, and `_replay` documents it.

**SC-04 (operator, automated/integration) — met (literal).**
- `case_2488_amend_stdout_is_unchanged` asserts exact stdout for the ledgered and the unledgered amend, with no APPROVAL-RESET.
- It passes at base (`red-t02-plan-merge-base.txt` lines 892-895) and at the pin (green receipt).
- The BRIEF's text already names exactly these two shapes. The narrowing from the grill's "every existing green case" to two shapes is a reading, and signed ruling `notes/answers-2026-11-23-signoff.md` Q2(b) accepts it. The ruling's premise holds at the pin: `amend.py` has no `reset` or `APPROVAL` token.

**SC-05 (reader, inspection) — partial.**
- At `git show 95606ddb:tests/integration/test-plan-merge.py`, all three successors exist and each forces its base failure. Each asserts nonzero exit, both files byte-identical and `_no_journal(plan)`. Together they carry 8 `check()` calls, 1 + 4 + 3, equal to base.
- **Not met for one successor:** `case_1985_amend_writes_nothing_when_the_ledger_fails` (`#case_1985_amend_writes_nothing_when_the_ledger_fails`). Its single check asserts `returncode != 0`, "nothing was written", no journal and byte-identical files. **It does not assert that stderr names the failure.** The other two do: `b1716/atomic` asserts `"LOCKED"` and `b1716/io` asserts `"PermissionError"`.
- The base case did not assert the naming either. The coverage therefore did not shrink, but SC-05's literal "asserts a nonzero exit naming it" is unmet. No signed ruling accepts a narrower reading.
- Probe P4 shows that production does print `PermissionError: [Errno 13] … feature.json.lock`, so the remedy is assertion-only.

**SC-06 (code maintainer, inspection) — met.**
- `feature_json_write.py`'s module docstring now reads "locked_update performs no fsync; only harness_merge's intent journal … is fsync'd".
- The `harness_merge.py` module docstring documents the journal protocol (lines 25-54) and the lock order "plan.yaml.lock then feature.json.lock … No path acquires them reversed" (lines 56-61).
- `amend.py` has no `APPROVAL_RESET_LINE`, no `result["reset"]` and no `result.get("reset")`: `git show 95606ddb:…/amend.py | grep reset` is empty.
- In `plan-merge.py`, the exit-5 contract gains "or a leftover intent journal (harness_merge) is unreadable or names a file matching neither its recorded before nor after state".

**SC-07 (operator, automated/integration) — met.**
- `git diff --stat 2491336e..95606ddb` on these six suites is empty: test-harness-merge, test-feature-json-merge, test-observations-merge, test-expertise-merge, test-inflight-registry and test-check-state-feat59 (all under `tests/integration/`).
- In test-plan-merge.py, the diff edits only the three SC-05 cases and adds the new ones.
- All suites are green in `notes/t02-build/02-*.txt` and `06-verify-T-02.txt` (exit 0).
- No host-known reds appeared in these receipts.

## Decision dispositions (Mode 2)

All six `decisions_affected` rows are `keep`: DEC-229 ×2, DEC-199 ×2, DEC-174 and DEC-230. Keep rows are not graded. The plan names **no DECISIONS.md landing**, and the BRIEF's Constraints say "No DEC is amended". `git diff --stat 2491336e..95606ddb -- .harness/harness/docs/` is empty.

Each kept clause still resolves at the pin in `git show 95606ddb:.harness/harness/docs/DECISIONS.md`:

| Line | Decision | Clause |
|---|---|---|
| 4521 | DEC-174 | "Planning such a change through the harness remains fine" |
| 5996 | DEC-199 | "No consumer opens its own lock or rename primitive." |
| 6011 | DEC-199 | "spliced as text, never re-rendered" |
| 7698-7699 | DEC-229 | "every other byte and the approval mapping preserved" and "all-or-nothing across both files (BUG-1716)" |
| 7766 | DEC-230 | its clause |

P-16 check: DEC-199's affirmative claim that "No consumer opens its own lock or rename primitive" is true of the four consumers it names. `os.replace` and `mkstemp` survive in `artifact_accessors`, `gh-sync`, `run_identity` and `run-unit-tests`, none of which DEC-199 lists, so there is no overclaim. DEC-229's all-or-nothing claim is now carried by the journal.

## Findings

- **F-1** (substance, low, binds to T-02, `tests/integration/test-plan-merge.py`). SC-05 is partial. The `case_1985_amend_writes_nothing_when_the_ledger_fails` successor never asserts that stderr names the forced failure.
  - **Failure scenario:** a regression that dropped the cause from `_pair_failure`'s generic branch would still pass this case for the amend verb, leaving the operator with "nothing was written" and no reason. For example, a regression to print only "  nothing was written." The `b1716/io` case would catch it only for record-amendments.
  - **Remedy:** add `"PermissionError" in r.stderr` to that check, or get an operator ruling accepting the narrower reading.
- **F-2** (form, low, binds to T-02). Two SC-01 clauses are carried by probe and inspection, not by suite assertions:
  - "naming the journal" on exit 5: (f) asserts only the marker.
  - "a further invocation changes neither file" after the feature.json write (e).
  - **Failure scenario:** a refactor that drops `journal_path` from the DIVERGED message stays green, and the operator gets an exit-5 refusal without the file to reconcile.
  - Advisory under O-02: met now, undefended.
- **F-3** (proportionality, info, binds to T-01). `tests/unit/test-harness-merge-journal.py` changed in `e8d3031a`, after the `t02-build` receipts. Its re-run (PASS 101/101) is claimed in `notes/simplify-build.md` with no stdout receipt, against C6. No SC rests on the unit test, so this grades nothing, but the claim is unreceipted.

## Method

I read every artifact at the pin with `git show`. A throwaway probe script (removed after the run) imported the pin's `test-plan-merge.py` fixtures (the working tree's `.claude` and `tests` equal the pin) and ran with HARNESS_AGENT_TYPE unset. P1-P4 all behaved as stated, and the probe wrote nothing in the repository; its fixtures live in tempdirs. I did not re-run any suite.

## Open questions

- OQ-1 (non-blocking): fix F-1 in T-02's test file within the rework budget (2 rounds / 90 min, C1), or have the operator accept "naming it" as satisfied by the other two successors.
