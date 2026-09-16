# Goal-check — BUG-1129-validate-handoff-sweep

**Verdict: FAIL.** The pinned implementation at `df871448f55bcb7cf5804e5ffc9cca187a364131` has the intended fail-closed guard and both required QA matrices pass, but none of the four signed SCs is fully discharged by its declared automated evidence.

The signed delivery record is T-01, which traces SC-01 through SC-04 (`plan.yaml:35-42`). Its ledgered `T-01.files` amendment is part of the signed scope: `feature.json:38-43` records why `tests/integration/test-hooks-install.py` was added, and the pinned plan includes it at `plan.yaml:58-59`.

## Perspective dispositions

- **operator — PARTIAL:** the pinned guard and sweep path currently refuse before terminal writes and preserve the worktree, but the regression evidence does not assert the exact `validation incomplete` diagnostic or the full no-GitHub-write boundary.
- **code maintainer — PARTIAL:** ship and INV-17 currently call one fail-closed predicate, and the matrices are green, but SC-03 lacks its required negative/fail-first coverage and SC-04 lacks its required fixture-migration fail-first proof.

## Success-criterion dispositions

- **SC-01 — PARTIAL:** `gh-sync.py:2208-2220` implements exit-1 refusal before the first write and emits `validation incomplete` plus the missing note; `test-gh-sync-ship.py:458-481` covers exit 1, the note path, no Done-card/milestone write, no SKIP, and unchanged station; QA records the integration matrix passing (`notes/review-harness-qa-c0.md:18-25`) and the receipt records the pre-fix red at `notes/receipt-main-session-T-01-fail-first.md:6-9`. The regression condition at `test-gh-sync-ship.py:469-472` never asserts the required `validation incomplete` text, so that signed observable can regress while the matrix stays green.
- **SC-02 — PARTIAL:** `test-post-merge-sweep.py:577-608` exercises the real sweep, retains the worktree, and observes the refusal; its pre-fix red is recorded at `notes/receipt-main-session-T-01-fail-first.md:11-13`, and QA records the post-fix integration pass (`notes/review-harness-qa-c0.md:18-25`). The sweep assertion checks only absence of a milestone call, while the ship assertion checks only Done-card and milestone writes; neither proves the criterion's complete “no GitHub write occurs” boundary. A body/comment write moved ahead of the guard would escape both focused cases.
- **SC-03 — PARTIAL:** both production callers use `handoff_policy.exempt_reason` (`gh-sync.py:2212`, `check-state.py:1197`), whose fail-closed parsing and three-part all-direct rule are at `handoff_policy.py:36-68`; the positive all-direct ship case is at `test-gh-sync-ship.py:483-500`, and existing INV-17 cases are at `test-check-state-handoff.py:78-136`. QA reports both unit and integration matrices passing, but also confirms no changed regression drives unreadable, unparsable, non-mapping, empty, malformed-task, or mixed-mode plans through ship (`notes/review-harness-qa-c0.md:26`). Receipt line 10 was already green before the fix, so the required shared-predicate fail-first proof is absent.
- **SC-04 — PARTIAL:** validated fixtures write the note through `gh_sync_support.py:61-69,116-119,789-814`, sweep and hooks fixtures commit it at `test-post-merge-sweep.py:181-188` and `test-hooks-install.py:197-204`, and the refusal alone opts out at `test-gh-sync-ship.py:463-466`; the ledgered hooks amendment is included. QA records both matrices passing, but the fail-first receipt has no pre-migration note-writing assertion failure (`notes/review-harness-qa-c0.md:27,34`), so the SC's required red-before proof is missing.

## Substantive findings

- **GC-01 — kind: integration coverage; owner: T-01.** A change from `validation incomplete: <path>` to an arbitrary missing-file message would leave `test-gh-sync-ship.py:469-472` green while violating SC-01's exact diagnostic.
- **GC-02 — kind: integration coverage; owner: T-01.** A GitHub comment/body write placed before the validation guard would not be detected by the focused ship or sweep assertions, so SC-02's no-write promise is not regression-protected.
- **GC-03 — kind: integration/unit coverage and fail-first evidence; owner: T-01.** A regression granting exemption after plan read/shape failure could ship an unvalidated malformed-plan feature while both current matrices remain green; QA found no negative ship case and no SC-03 red receipt.
- **GC-04 — kind: fail-first evidence; owner: T-01.** The fixture migration is present and green, but no recorded pre-migration fixture-note assertion failed, so SC-04's explicit fail-first clause cannot be graded pass.
