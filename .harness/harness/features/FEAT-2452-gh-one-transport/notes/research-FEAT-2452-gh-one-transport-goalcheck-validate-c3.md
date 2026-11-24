# Goal-check: FEAT-2452-gh-one-transport, validate cycle 3 (rework c2, the last signed round)

Run r-20261123-7-validate-validator. Pin `caeebc7cb24b7205bb5d5ad5191cd6541fc3519a`, base `b788e9dac342ee112106a3bc5aa7430d4467cbcb`, fix delta `3465716a..caeebc7c`.
I read all code and doc evidence with `git show caeebc7c:<path>` or `git diff <a> caeebc7c`. Outside `.harness/`, the worktree matches the pin byte for byte: `git diff --stat caeebc7c HEAD` is empty.

**BLUF: PASS. Both perspectives pass.** M1 is closed. I measured that myself and did not take it from the builder's receipts. The pin's `tests/unit/test-wayfind.py` gives:
- at the pin, ALL PASS (238 checks, exit 0);
- against the 3465716a copy of `wayfind.py`, 115 FAIL and 123 PASS, exit 1.

The 115 reds include every blocker-`state` and `assignees` case. Every control stays green in both runs.

M2 is closed. The reworded abandon row matches `gh-sync.py` at the pin. SC-05 stays met on its literal discharge, with the narrowed reading carried forward. Nothing in the delta claims that a per-item close-failure red was observed. Neither the base..pin diff nor the fix delta changes an enforcement file. DEC-138's landing is unchanged.

## Perspectives

| Perspective | Verdict | Carried by | Evidence |
|---|---|---|---|
| operator | **pass** | SC-03, SC-04 (with the C5 cut), SC-05 (literal), SC-07 | A malformed blocker or sub-issue state, or a malformed `assignees` list, now stops frontier with a typed `wayfind:` exit 1 before any eligibility decision. Before the fix it printed `#11 ? eligible?`, or raised an untyped AttributeError. Abandon and reject keep their caller policies. Ticket #2468 is unchanged. |
| code maintainer | **pass** | SC-01, SC-02, SC-06 | One transport and one override are unchanged; the delta touches only `_ISSUE_URL` in factory_gh. The policy table describes the abandon close-failure path and the wayfind decision-field checks exactly as the pinned code behaves. |

## SC verdicts

| SC | Verdict | Method | Evidence |
|---|---|---|---|
| SC-01 | met | automated (unit) | The only factory_gh change is `_ISSUE_URL`. I ran the pin's `tests/unit/test-factory-gh.py`: 345/345 at the pin, and 17 of 345 FAIL with the 3465716a `factory_gh.py`. The 17 are the new B1/B3 reject cases. |
| SC-02 | met | automated (integration) | No integration test and no `gh-sync.py` file changed in the fix delta (`diff --stat` is empty). The c1 evidence carries forward, and `notes/fix-c2-verify-T-02.txt` is in the pinned tree. |
| SC-03 | **met** | automated (unit) | See "SC-03 regrade" below. |
| SC-04 | **met with the C5 cut of (e)** | automated (integration) | The fix delta does not touch gh-sync or the integration tests, so the c1 grading stands. (e) stays cut under C5, and the ship record must say so. |
| SC-05 | **met (literal); narrowed reading recorded** | automated (integration) | See "SC-05" below. The URL half is still green: `issue_number_from_url` is unchanged and the new accept cases pass at the pin. |
| SC-06 | **met** | inspection | See "SC-06 regrade" below. |
| SC-07 | met | inspection | `notes/enforcement-backlog.json` has no diff in `3465716a..caeebc7c`. It still records #2468 with its signed title and a body naming both executors. |
| DEC-138 (amend, plan row 2, clause "each caller keeps its own runner, because", successor D-01) | met | inspection | At `caeebc7c:.harness/harness/docs/DECISIONS.md` line 3132, "**Shared code, and migration scope.**" names `factory_gh` as the one shared transport and keeps failure policy at the caller. `git show … \| grep -c 'each caller keeps its own'` returns 0. The fix delta does not touch `.harness/harness/docs/` (`diff --stat 3465716a caeebc7c` is empty), so the landing is byte-identical to c1. |

The `keep` rows (DEC-138 row 1, DEC-146, DEC-174, DEC-144, DEC-166, DEC-200, …) are not graded.

## SC-03 regrade: blocker `state` and `assignees`, measured

I exported the pin with `git archive` into a temp root, then made a second copy with the 3465716a `wayfind.py`. That copy is the free mutant (O-07). I ran `python3 tests/unit/test-wayfind.py` in both with `HARNESS_AGENT_TYPE` unset.

**State field: red at 3465716a, green at the pin.**
- `case_8c_blockers_{item_no_state, state_unknown, state_int, state_null, state_empty, state_list, second_item_stateless}_raises_gh_error`. At 3465716a they returned `('value', [{}])`, and the like.
- `case_10c_frontier_blockers_<same 7>_{exit_1, prints_no_ticket, typed_diagnostic, stops_reading}`. At 3465716a:
  - `[{}]`, `unknown`, `null`, `""` and the second stateless item gave `('value', 0, '#11\t?\teligible?')`, so the ticket was admitted;
  - `state_int` and `state_list` raised an untyped `AttributeError … 'lower'`.
- Sub-issue state: `case_10c_frontier_subs_{no_state, state_unknown, state_int}_*`.

**Assignees field: red at 3465716a, green at the pin.**
- `case_10c_frontier_assignees_{missing, null}_*`: at 3465716a the ticket was admitted as unclaimed (`#11 ? eligible?`).
- `case_10c_frontier_assignees_{string, object}_*`: at 3465716a these read as claimed, giving `(frontier empty)` with exit 0.

**Controls: green in both runs.**
- `case_7_blockers_404_is_absence`, `case_7_parent_404_is_absence`
- `case_8c_blockers_open_closed_any_case_valid`, `case_8c_blockers_empty_list_valid`
- `case_10d_frontier_{closed_blockers, empty_blockers, blockers_404, open_blocker, claimed, closed_ticket, no_subs}_exit_0`

My counts match the builder's receipts `fix-c2-FixD2_Frontier/01-red-wayfind.txt` (115 FAIL) and `03-green-wayfind.txt` (ALL PASS, 238).

At the source, `frontier` decides on `b["state"].lower()` and `full["assignees"]` only after `blockers()` has passed `_list_of(_fields(state=_state))` and `checked_issue()` has passed `assignees=_list`. Both checks raise `unusable()`, a GhError, before the decision. The other SC-03 clauses are unchanged in the delta, and the pin suite passes on all of them:
- 404-only absence;
- malformed JSON on a status-zero response raises;
- the URL text result;
- dry-run;
- gist stdin.

M1 is fixed under the same contract (P-06). The premise it failed on no longer occurs.

## SC-06 regrade

- **Abandon row (line 106 at the pin)** now says:
  - abandon attempts every other write independently, in plan order;
  - a ticket whose close succeeds is reseated and reported as closed but not labelled;
  - a ticket whose close fails is reported (`could not close`, and in the `FAILED n of m` line) and is neither reseated nor labelled;
  - later tickets, the milestone close and the local `abandoned` station still run.

  The pinned `gh-sync.py` matches each of these points:
  - `_close_and_reseat` returns before `_to_backlog` and `_label_abandoned` on a failed close and appends the ticket to `failed`;
  - `_apply_abandon_plan` is a flat loop;
  - `_report_abandon_gaps` prints `FAILED {len(failed)} of {len(plan)}`;
  - the station block follows unconditionally.
- **Wayfind row (line 118)** names the decision-field checks:
  - sub-issue and blocker state is `open` or `closed`;
  - sub-issue number is a positive integer;
  - the view's own number, string title, `assignees` list and named labels;
  - parent number, resolve title and map body;
  - the "unusable map body" partial-write case.

  Each of these matches a `require`/`checked_issue` call at the pin.
- `factory_cli.py` has no diff in the fix delta, and "Exit 2 does NOT mean nothing was mutated" is still present.

## SC-05: the literal discharge stands, the narrowed reading is carried, and no per-item red is claimed

The fix delta touches neither `gh-sync.py` nor any integration test. The literal discharge accepted under OQ-GC2-1 (the label-create red at 15a240bc) is therefore unchanged. I grepped the added lines of the delta for per-item, close-failure and #13 wording. The only hits are these:
- the ruling note, which states the gap ("never been observed red") and the constraint;
- the `fix-c2-verify-T-02.txt` lines `ok #13 failing close API: …`, which are green assertions and not a red claim.

No artifact in the delta claims the per-item red was observed.

## Enforcement and C4

- `git diff --name-only b788e9da caeebc7c` lists 30 paths outside this feature's directory: 8 bin scripts, `github-mirror.md`, `DECISIONS.md` and its index, and test files. No branch-create-gate, merge-gate, check-state, check-domain, hook or guard file is among them. Every path in the full diff that matches `gate` is one of this feature's own notes.
- Both `GH_BIN` sites (`branch-create-gate.py`, `merge-gate.py`) are unchanged.
- The fix delta's non-feature paths are exactly `factory_gh.py`, `wayfind.py`, `github-mirror.md`, `tests/unit/test-factory-gh.py` and `tests/unit/test-wayfind.py`.

## Findings (none gating)

- **F-c3-1 · form · low · T-01** (`tests/unit/test-factory-gh.py`, which T-01's `files:` own). The comment `# B1 (c2): owner is [A-Za-z0-9-]` is stale. The code's owner class is `[A-Za-z0-9_-]`, and the same file now accepts `jdoe_acme`. The builder note `notes/fix-c2-FixD2_Frontier.md` ("Disclosed limit … `jdoe_acme` would be refused") is also superseded, by `12-emu-owner-main.txt`. Failure scenario: a maintainer reads the comment, "restores" the narrower class, and EMU-owned create URLs SKIP as unreadable. The accept case at `t01_issue_number_from_url_accepts` would catch that, so the risk is only misreading. Backlog.
- **F-c3-2 · substance · info · T-04, out of SC scope.** `sub_issues()` validation also feeds `cmd_map`'s display tallies. A malformed sub-issue list now makes `map` exit 1 where it used to show zero tickets. This is fail-closed and consistent with the SC-03 class. No action.

## The ship record must carry

1. **SC-04 (e) cut under C5.** Divergence (e) has no failing-first regression; it was cut by the settled first-to-cut lever.
2. **OQ-GC2-1 narrowed reading.** SC-05 #13 is discharged literally by the abandon label-create red at 15a240bc. The three per-item close-failure assertions have never been observed red. The operator accepted this through the fable-advisor delegation (`notes/answers-2026-11-23-validate-c1.md`). The ship record must not claim that a per-item red was observed.
3. **Backlog:**
   - A2: the opt-in cost log persists inline `--body`. Its disclosure class is non-public issue body text, written to the local cost log when the operator opts in.
   - OQ-QA-2: check-domain against DEC-153 in-pin perturbation.
   - OQ-QA-3: the pinned checkout lacks `node_modules`.
   - B2: abandon stays silent on the label 403 when every close fails.
   - B4: the unit seam never asserts the labels event.
   - F-c3-1 above, optionally.
4. **Standing disclosures:**
   - the legacy grade-1 mains (`wayfind.main`);
   - the d64e9356 assembled name;
   - the T-02 commit-tree slip;
   - the rewording of the probe comment;
   - reds observed on the host only;
   - the B1 owner class widened by Main to `[A-Za-z0-9_-]` for EMU (`12-emu-owner-main.txt`);
   - the issue_types_live probe stdout at `notes/issue-types-live-probe.txt`, which Verification gaps requires before ship.

## Principles applied

- **P-06** (Expertise): I re-measured M1's failed premise, stateless or unknown blockers and assignees, at the pin against the pre-fix blob, and did not rely on the builder's receipts.
- **O-07** (Expertise): the 3465716a `wayfind.py` and `factory_gh.py` were used as free mutants under the pin's tests.
- **P-04** (Expertise): each field (state, assignees) is graded on its own named cases, not on a total FAIL count.
- **G-13** (Expertise): the stale "Disclosed limit" claim is flagged in the note that supersedes it (F-c3-1).
