# Goal-check — FEAT-2452-gh-one-transport — validate cycle 2 (rework c1)

Run r-20261123-6-validate-validator · pin `e282689dd01a1a45eb22f08be67b1e2a9b437fb1` · base `b788e9dac342ee112106a3bc5aa7430d4467cbcb` · fix delta `64102016..e282689d`.
All code and doc evidence was read with `git show e282689d:<path>` or `git diff <a> e282689d`. No suites were re-run. The receipts cited were committed at the pin.

**BLUF: PASS. Both perspectives pass.** H1, H2, F1 and A1 are closed at the pin. G1 is closed on SC-05's
**literal** text. Read against T-02's signed #13 reading, it is **narrowed**, and that is recorded below as a separate,
non-gating advisory. SC-04 is still **met with the C5 cut of (e)**. The DEC-138 amend row is still met, because DECISIONS.md is
untouched in the fix delta. I found no regression in the fix delta.

## Perspectives

| Perspective | Verdict | Carried by | Evidence |
|---|---|---|---|
| operator | **pass** | SC-03, SC-04, SC-05, SC-07 | Wayfind fails closed on unusable payloads (H2). Abandon and reject keep their caller policies when a label create fails (H1). #13 now has a real red (G1, literal). Ticket #2468 is unchanged. |
| code maintainer | **pass** | SC-01, SC-02, SC-06 | The single transport and the single override are unchanged. The policy table now carries the label caller split and the wayfind partial write, and the cut history is gone (F1). The `_ISSUE_URL` host is tightened (A1). |

## SC verdicts

| SC | Verdict | Method | Evidence |
|---|---|---|---|
| SC-01 | met | automated (unit) | The c0 evidence holds; factory_gh changed only in `_ISSUE_URL` (A1). A1 is red in `fix-c1-FixD1_Wayfind/02-red-factory-gh.txt` (4/324) and green in `04-green-factory-gh.txt` (324/324). `fix-c1-verify-T-01.txt` has 0 FAIL lines. |
| SC-02 | met | automated (integration) | Unchanged in the fix delta. `fix-c1-verify-T-02.txt` has 0 FAIL lines, and its 12 files include test-gh-sync-open.py `single_override_case`. |
| SC-03 | met | automated (unit) | **H2 closed:** wayfind.py `gh_json_or_absent` returns the `ABSENT` sentinel only for an int nonzero status with `(HTTP 404)`. `blockers()` and `parent_of()` raise `unusable()` → `GhError` for any other payload, and `parent_of` requires `type(n) is int and n >= 1`. Red: `fix-c1-FixD1_Wayfind/01-red-wayfind.txt` (28 FAIL, all new). Green: `fix-c1-verify-T-04.txt` (324 ok, 0 FAIL; case_8b/10b/11b PASS, case_7 404-absence still PASS). `GhError(argv, status, stdout, stderr, what, value, next_step)` matches `unusable()`'s 7-arg call. |
| SC-04 | **met with cut** | automated (integration) | **H1 closed:** the gh-sync.py `ensure_labels` matcher is unchanged, and it now returns the failure. `mirror_labels` is used for SKIP/0 by `_open_ensure_labels` (both branches) and recover-terminal `_finish_replacement`. Abandon calls `label_gap = ensure_labels(...)` → `_label_abandoned` (no attach after a failed create). Reject calls `_RejectWrites.label` → `_RejectHalt`. Every gh-sync caller of `ensure_labels` is enumerated at the pin (git grep). Colours and the absence of force are unchanged. Regressions in `fix-c1-verify-T-02.txt`: lines 688–691 (abandon), 730–732 (reject), 841 (open SKIP kept) and 843 (colours, never --force). (e) remains cut under C5; this is the standing disclosure, and the ship record must carry it. |
| SC-05 | **met (literal); narrowed reading advisory** | automated (integration) | See "G1" below. The URL half is unchanged from c0. |
| SC-06 | met | inspection | **F1 closed.** At the pin, github-mirror.md has three relevant rows. The checked-label row splits the failure policy by caller: open/recover-terminal SKIP/0, abandon per-ticket line/0 with closes, reseats, milestone and station landing, and reject halt/1 naming what landed. The milestone row no longer carries cut history (grep for "cut" or "planned narrowing" at the pin finds no match in the table). The wayfind row states that `resolve --apply` comments and closes before the gist, so exit 1 is not "no mutation"; wayfind.py `resolve` (`do([comment, close])` then `append_gist`) matches. The deadline non-goal note is unchanged. factory_cli.py is untouched in the fix delta ("Exit 2 does NOT mean nothing was mutated" kept). No enforcement file is in `git diff --name-only base..pin` (grep exit 1). The only added `GH_BIN` lines are prose in github-mirror.md, which matches C4. |
| SC-07 | met | inspection | `notes/enforcement-backlog.json` at the pin is unchanged: #2468, OPEN, signed title, and a body naming both executors. |
| DEC-138 | met | inspection | At `e282689d:.harness/harness/docs/DECISIONS.md` line 3132, "Shared code, and migration scope." names factory_gh as the shared transport, and there is no `gh_bin` or "keeps its own runner" anywhere. The fix delta does not touch `.harness/harness/docs` (diff --stat empty), so the c0 grading (one +6/−4 hunk, guard and policy clauses intact) carries forward. |

## G1 — two separate items

**Literal status: met.** SC-05 says "a failing abandon API call is reported while later per-item work and
local abandoned recording continue (#13) … QA demonstrates the new URL/abandon assertions failing first."
`abandon_label_create_failure_case` exercises a failing abandon API call, the 403 on `label create abandoned`, and
asserts four things: it is reported, every item is still closed and reseated, the milestone is closed, and the station is `abandoned`. At
`15a240bc` (gh-sync.py blob `86ddc86f`, the same blob as at 64102016), all four are FAIL
(`fix-c1-FixD1_Mirror/01-red-label-create-head.txt` lines 48–56, `05-red-final-tests-at-15a240bc.txt` lines 49–56,
exit 1). They pass at the pin (`06-verify-T-02.txt` lines 688–691). The red comes from a real prior state of the feature
that broke #13's continue policy, so it is a free mutant (O-07) and not a fabricated one. Caveat: the
demonstration is the builder's receipt. QA's c2 confirmation was still in flight when this note was written.

**Reading: narrowed.** T-02's signed intent fixes #13 as "abandon receives a failing REST close/API result:
assert diagnostic, later item writes and local abandoned recording". That is a **per-item** write failure inside
`_apply_abandon_plan`. The label create runs once, **before** the loop, so its red proves only "a pre-loop failure must not
exit". It does not prove "a failed item write must not stop later items". The three `#13 failing close API`
assertions (`06-verify-T-02.txt` lines 685–687) have still never been shown red: `t02-red-green/05-red-abandon-old-override.txt`
remains a preservation receipt. **Advisory A-G1 · substance · low · T-02:**
- Scenario: a later edit makes `_apply_abandon_plan` `break` after the first failed `gh_try` close.
- The #13 close assertions would probably catch it, but they have never been observed failing.
- Remedy, if wanted: a dev-side mutant run (main-session-direct, DEC-174), never a new gate.
- This does not gate, because the literal clause is discharged.

## Regression scan of the fix delta (64102016..e282689d)

- gh-sync.py: every former `skip()`-on-label caller moved to `mirror_labels`. The only `ensure_labels` callers that do not skip are abandon and reject, and both are intended. `_label_abandoned` keeps the per-ticket diagnostic text that the unit seam (`test-gh-sync-abandon-sources.py`, None = success) depends on. No other caller changed.
- wayfind.py: `ABSENT` is used only by `blockers` and `parent_of`, the only callers of `gh_json_or_absent`. `cli()` already catches `GhError`.
- factory_gh.py: only `_ISSUE_URL` changed. GHE hosts with a port still match (new accept cases).
- Gates: the T-01..T-05 verify receipts and `gate-after-fix-c1.txt` (PASSING: 122) carry zero `^FAIL` lines (G-08).

## Open (non-blocking)

- The ship record must carry the (e) cut (C5); this is standing.
- A-G1 above: the operator can accept the narrowed #13 reading, or ask for a per-item close mutant.

## Principles applied

- P-06 (Expertise): each c0 premise (H1 SKIP, H2 null→[], G1 no red, F1 rows) was re-measured at the pin, not taken from the fix note.
- P-05 and O-07 (Expertise): the G1 literal verdict and the narrowed reading are graded separately, and the 15a240bc blob is used as the free mutant.
