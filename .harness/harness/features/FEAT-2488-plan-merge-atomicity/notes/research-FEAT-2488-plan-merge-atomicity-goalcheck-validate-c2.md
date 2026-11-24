# Goal-check (validate c2) — FEAT-2488-plan-merge-atomicity

- Pin: `c35841fe5511109dffb958eebe6dad86dbf654d7`
- Base: `2491336e43310cb3e95ae3110d098726ed4dc454`
- Fix delta: `987e57b9..c35841fe`
- Run: r-20261124-3-validate-validator
- Reader: harness-pm (goalcheck)

**BLUF: PASS.** All seven SCs are **met**, and all three perspectives **pass**.

The c0 partial on SC-05 is closed by an implementation repair under the same contract: the named-failure assertion and raw-byte snapshots. The operator clauses the c0 lead re-graded partial are closed too:

- "refused loudly, never overwritten" holds for dangling, FIFO, missing-key, misbound and feature.json-primary journals.
- "every other locked write behaves as before" holds: `amend --show` is read-only again.

I measured both with executed probes at the pin.

The two ledgered amendments (T-01.intent, T-02.intent) change task HOW only. No signed SC or perspective text is left unmet as written.

One advisory form finding remains: the residue of c0 F-2.

The worktree's `.claude` and `tests` are byte-identical to the pin (`git diff --quiet c35841fe -- .claude tests`, rc 0), so every probe below ran the pin's code.

## Perspectives

| Perspective | Grade | Carried by | Evidence |
|---|---|---|---|
| operator | **pass** | SC-01, SC-04, SC-07 | **Torn states:** each converges and a re-run settles. Divergence refuses at exit 5 naming the journal. A post-publish failure is reported as journaled. A feedback failure is advisory.<br>**Malformed journals (probe P-A):** 15/15 routes refuse loudly at exit 5, name the journal and leave every file byte-identical.<br>**amend:** stdout is locked at base and pin (SC-04). `amend --show` is read-only and byte-equal to base (probes P-B, P-C).<br>**Other suites:** the six are unedited and rc 0 at the pin. |
| code maintainer | **pass** | SC-02, SC-03, SC-06 | **One primitive:** `harness_merge.locked_pair_update`, with one call from `amendments.write_plan_and_ledger`. No plan_merge module carries rename, restore or journal code.<br>**fsync:** only on the journal and its directory, before the first member replacement. The unlink comes after the last.<br>**Docs:** the lock order and protocol are documented, and the docstrings were updated truthfully for the narrowing. |
| reader (qa / reviewer) | **pass** | SC-05, SC-01 | Every torn state is constructed on disk. The three SC-05 successors each assert a nonzero exit naming the failure, raw-byte identity and no journal. 8 `check()` calls at base became 8 at the pin. |

## SC status

**SC-01 (operator, automated/integration) — met.**
- **Test cases (QA, at the pin):** `tests/integration/test-plan-merge.py` cases (a) through (j), `#case_2488_*`. QA's manifest `runs/r-20261124-3-validate-validator/qa/manifest-integration.json` records `tested_commit` = pin, `runner_exit` 0, and `test-plan-merge.py` returncode 0. That file exits 1 on any FAIL row (`main`), so per-file rc is discriminating (G-08).
- **Gaps the fix round added assertions for:**
  - G-a: (b) now runs through record-amendments (`#case_2488_ledger_landed_plan_not_converges`, loop over `_TORN_VERBS`).
  - G-b: (d) asserts exit 6 and the message (`#_settles`).
  - G-c: (f) runs through both verbs.
  - G-d: (f) asserts the exit-5 message names `realpath(plan)+'.harness-merge.journal'` (`#case_2488_a_diverged_member_refuses_and_changes_nothing`).
- **Base reds (C3):** unchanged from c0, `notes/red-t02-plan-merge-base.txt`.
- **Probe P-D (executed):** after (e)'s `write_feature_json` convergence (rc 0, journal gone, amendment once), a further record-amendments exits 6 "recorded before" with both files byte-identical.

**SC-02 (code maintainer, inspection) — met.**
- `git grep -n "mkstemp\|os\.replace\|os\.unlink\|os\.remove\|JOURNAL_SUFFIX\|harness-merge.journal" c35841fe -- .claude/skills/harness/bin/plan_merge/` returns no lines.
- `guards.py` has no `def _replace_bytes` or `def _restore_plan` (git grep rc 1).
- `amendments.py#write_plan_and_ledger` makes a single `harness_merge.locked_pair_update(resolved, splice, ledger_path, ledger)` call.

**SC-03 (code maintainer, inspection) — met.** In `git show c35841fe:.claude/skills/harness/bin/harness_merge.py`:
- `_publish_journal`: `os.fsync(fh.fileno())` at :521, then `os.replace(tmp_path, journal_path)` at :522.
- `_commit_published`: directory `os.fsync(fd)` at :536, before the member loop at :539. `os.unlink(journal_path)` at :541 comes after the last member.
- `replace_bytes` (:220-236) says "No fsync" and has none.

**SC-04 (operator, automated/integration) — met.**
- `#case_2488_amend_stdout_is_unchanged` passed at base (`red-t02-plan-merge-base.txt`) and passes at the pin (QA manifest, rc 0).
- The fix delta does not touch the stdout path. Its `amend.py` change is only `recover=not args.show`.

**SC-05 (reader, inspection) — met. The c0 partial is closed.**

At the pin:

| Successor | `check()` calls | Named failure asserted |
|---|---|---|
| `#case_1985_amend_writes_nothing_when_the_ledger_fails` | 1 | asserts `"PermissionError" in r.stderr` |
| `#case_b1716_record_amendments_is_all_or_nothing` | 4 | `LOCKED` |
| `#case_b1716_record_amendments_writes_nothing_on_a_ledger_io_error` | 3 | `PermissionError`, no Traceback |

- That is 8 calls, equal to the 8 at base (awk count over the base's three cases).
- All snapshots now go through `_bytes` (`open 'rb'`), not the newline-normalizing `read()`. The c0 objection was that the snapshots were newline-normalized; that is closed.
- This is a fix under the same contract (P-06), not an authority change.

**SC-06 (code maintainer, inspection) — met.**
- `feature_json_write.py:23` reads "locked_update performs no fsync; only harness_merge's intent journal …".
- The `harness_merge.py` module docstring covers the protocol (:37-53) and the lock order (:67-73, "No path acquires them reversed").
- `amend.py` has no `APPROVAL_RESET` or `reset` token (git grep rc 1).
- `plan-merge.py:106` puts the exit-5 journal clause in its contract.
- The new refusals (non-regular, misbound, missing key) are all "unreadable", so the contract still covers them.

**SC-07 (operator, automated/integration) — met.**
- `git diff --stat 2491336e c35841fe` over the six named suites is empty.
- In `test-plan-merge.py`, the fix diff (`987e57b9..c35841fe`) touches only:
  - the three SC-05 successors;
  - the 2488 cases;
  - the `_bytes` helper, which moved up and is otherwise unchanged.
- QA's manifests at the pin show all of these suites at returncode 0: `test-harness-merge`, `test-feature-json-merge`, `test-observations-merge`, `test-expertise-merge`, `test-inflight-registry`, `test-check-state-feat59` and `test-plan-merge`. Integration is 95/95 with runner_exit 0, and unit is 68/68 with runner_exit 0.
- MF-1's `test-checker-structure-locks.py` is also rc 0 at the pin.

## Operator clauses re-graded (c0 lead's partial) — executed probes, at the pin

**Setup.** The probes import the pin's own fixtures (`_torn`) with HARNESS_AGENT_TYPE, CLAUDE_PROJECT_DIR and HARNESS_PROJECT_DIR unset. Every fixture lives in a tempdir. The repo was never written, and the fixture-check failure list was empty.

**P-A.** Each of five journal mutations was run through three routes: record-amendments, amend, and an in-process `write_feature_json`. The mutations:
- `before_sha256` key removed from the feature.json member
- dangling symlink
- FIFO
- journal renamed to `feature.json.harness-merge.journal`
- sibling misbound to `other.json`

| Result | Count |
|---|---|
| Refused at exit 5 (or MergeRefusal code 5) with `JOURNAL UNREADABLE` | 15/15 |
| Message names the journal path | 15/15 |
| plan, feature.json and journal entry byte- or type-identical | 15/15 |
| Hang (40s timeout) | 0 |

At 987e57b9 these spun or overwrote (`fix-c1-build/02-red-unit-journal-at-987e57b9.txt`).

**P-B.** With a pending amend torn state, `amend --show` exits 0 and plan, feature.json and journal stay byte-identical. `check` also leaves them byte-identical.

**P-C.** On a signed fixture with no journal, `amend --show` for `intent` and for `verify` was run with the base's `plan-merge.py` (from `git archive 2491336e` into a tempdir) and with the pin's. Both runs had rc 0 and equal stdout and stderr, both left the files unchanged, and the directory listings were equal.

**No other read-only verb is affected.** Every `_resolve_plan` caller at the pin besides `check` and `amend --show` is a mutating verb: apply, delete-items, set-key/panel/lanes, record-panel, record-amendments, sign/revoke, and set-*-station.

## Ledgered amendments (c35841fe) against signed SC and perspective text

Both judgements are in `git show c35841fe:…/feature.json` `judgements`: `amendment T-01.intent` and `amendment T-02.intent`. `approval.status` is still `approved`. Every changed file stays inside T-01/T-02 `files:` (`git diff --name-only 2491336e c35841fe -- . ':!.harness'`), so there is no P-17 scope finding.

**No signed SC or perspective is left unmet as written:**
- **SC-01, "a ledger write that fails after the journal is published is reported as journaled".** The ledger write is `replace_bytes`, whose failure class is OSError, and `_commit_published` catches OSError. The clause holds. The non-OSError sliver is ruling (1) and is not re-raised.
- **SC-01, "a feedback failure … does not turn the write into a failure".**
  - `changed_state_feedback` already absorbs `(OSError, SubprocessError)` (`harness_boundary.py#changed_state_feedback`).
  - `text=True` decode faults are ValueError (UnicodeDecodeError), and `_relay_after_commit` catches `(OSError, ValueError)`. The clause holds.
- **Operator, "refused loudly, never overwritten".** Strengthened, per P-A. A third-bucket traceback is loud and keeps the journal.
- **Task HOW only.** "No recovery failure prints a Traceback" (T-02 item 3) and "each further member's sibling lock" (T-01 item 6) appear in no SC or perspective.
- **`except BaseException` in `replace_bytes` and `_publish_journal`.** These are temp-file cleanup and re-raise, carried from base `locked_update` (base :168), not the refused isinstance evasion.

## Decision dispositions (Mode 2)

All six `decisions_affected` rows at the pin are `keep`: DEC-229 ×2, DEC-199 ×2, DEC-174 and DEC-230. Keep rows are not graded, and no DECISIONS.md landing is planned. `git diff --stat 2491336e c35841fe -- .harness/harness/docs` is empty.

The kept clauses still resolve in `git show c35841fe:.harness/harness/docs/DECISIONS.md`:

| Line | Decision | Clause |
|---|---|---|
| 5996 | DEC-199 | "No consumer opens its own lock or rename primitive" |
| 6011 | DEC-199 | "spliced as text, never re-rendered" |
| 7699 | DEC-229 | "all-or-nothing across both files (BUG-1716)" |

P-16 holds: the third bucket keeps the journal, so the pair still ends all-or-nothing on disk.

## Prior findings at the pin

| Finding | Status at the pin |
|---|---|
| **c0 SC-05 partial / F-1** | **Closed (fixed)**, as above. |
| **c0 F-2** | **Partially closed.** "Exit 5 names the journal" is now asserted (G-d). "A further invocation changes neither file" after (e) is still not asserted by the suite; probe P-D carries it. |
| **c0 F-3** | **Closed.** The unit journal file has a receipt (`fix-c1-build/05-green-unit-journal.txt`, 142/142, test sha `f01c1dd8…` equals the pin's), and QA's unit manifest at the pin has it at rc 0. |

## Findings

- **F-2r** (form, low/advisory, T-02, `tests/integration/test-plan-merge.py#case_2488_a_feature_json_write_completes_the_pair_first`). The clause "a further invocation changes neither file" after the feature.json-write route (e) has no suite assertion.
  - **Failure scenario:** a regression that made the post-(e) re-run rewrite the plan, for example re-splicing on an already-`now` field, stays green. The operator re-running record-amendments then gets an unexpected byte change.
  - Met now by probe P-D, but undefended (O-02). Backlog chore; not a gate.

## Method

- Every artifact was read with `git show c35841fe:`.
- Probes P-A to P-D were executed by me against the pin's code with throwaway tempdir fixtures; nothing in the repo was written.
- I did not re-run any suite. The automated evidence is QA's pin-bound manifests in this run.
- The builder's `fix-c1-build/` receipts predate commit `ee5a9596` and bind only test shas. Production binding rests on QA's manifests plus my probes.

## Principles applied

- **P-06 (harness-pm expertise):** I separated a fix under the same contract (SC-05, MF-2 to MF-5) from an authority change (the narrowing, ruling 1), and re-measured each c0 premise directly.
- **P-16:** I graded the signed SC text against the amended HOW, clause by clause, rather than accepting the ledger as covering it.

## Open questions

- None blocking. F-2r goes to backlog unless the operator wants it in rework round 2.
