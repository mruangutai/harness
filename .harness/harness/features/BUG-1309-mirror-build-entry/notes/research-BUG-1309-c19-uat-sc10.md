# Closing goal-check — SC-10 recorded, SC-01..SC-11 complete — BUG-1309 — 2026-09-09

**BLUF: the goal is FULLY MET. SC-10 = met, by the operator's own UAT, relayed inline by the main
session on 2026-09-09 and transcribed at `notes/uat-BUG-1309-mirror-build-entry.md:360-403`
(45 added lines, 0 deletions — the script itself is byte-unchanged). No BRIEF amendment and no
re-signature is owed: no criterion text moves, and I re-read SC-04 (`BRIEF.md:108-125`) and SC-10
(`:157-160`) against the record rather than assuming it. Seven residual items are recorded below;
none gates. `cycles_used` is 17 of 17 — no cycle is opened by this note and none is requested.**

**Evidence discipline.** Every row below is CITED from evidence already taken this feature, and
explicitly NOT re-measured by me: no suite, no integration run, no formatter, no linter, no git
content grading beyond reading the two criterion texts. Suite state at the pin
`4857818bb1408813c7a38311d9e4ffc20373427e` is `notes/qa-c19-copy.md` §Suite run (rc=0, 36 ok,
0 FAIL, `matrix_ok: true`); the c19 validator panel is PASS, `must_fix: []`, `severity_max: med`
(`runs/c19copy-validator/digest.md`).

## SC-01..SC-11 at the pin

| SC | Method (as BRIEF declares) | Verdict | Cited evidence (by path) |
|---|---|---|---|
| SC-01 | automated / integration | **met** | `notes/research-BUG-1309-goalcheck-amend-c13.md:77` — six `T-02` cases ok; carry-forward established `:71-73` and `notes/research-BUG-1309-c19-goalcheck-copy.md` §1 (c19 commit touched only `merge-gate.py` + `test-merge-gate.py`) |
| SC-02 | automated / integration | **met** | `…-goalcheck-amend-c13.md:78` (`T-02 partial remote write records nothing`, `T-02 contract error records nothing`) |
| SC-03 | automated / integration | **met** | `…-goalcheck-amend-c13.md:79` + §2 (red 20 FAIL against pre-change `gh-sync.py`, green 0 FAIL at the pin) |
| SC-04 | automated / integration | **met — BY OPERATOR RULING** accepting BOTH evidence gaps on inspected-correct source; **NOT met by new automated evidence** | `notes/research-BUG-1309-c18-sc04-ruling.md:79`; clause table `notes/research-BUG-1309-goalcheck-c18.md` §1 (clause (f) unmet as automated evidence, source correct at `merge-gate.py:174`); no regression at the pin, `notes/research-BUG-1309-c19-goalcheck-copy.md` §1 |
| SC-05 | automated / integration | **met** | `…-goalcheck-amend-c13.md:81` (milestone + parent only, `task issues = {}`) |
| SC-06 | automated / integration | **met** | `…-goalcheck-amend-c13.md:82` (both `T-07` era-exempt cases; sweep sources unchanged in range) |
| SC-07 | automated / integration | **met** | `…-goalcheck-amend-c13.md:83` + §2 (red 1 FAIL via `CHECK_STATE_BIN`) |
| SC-08 | automated / integration | **met** | `…-goalcheck-amend-c13.md:84` (`accepted_/rejected_github_build_entry_*`) |
| SC-09 | **inspection** | **met** | `…-goalcheck-amend-c13.md:85` — `github-mirror.md:41,51-52` and `SKILL.md:141-142` at the sha, zero `at ship` hits |
| SC-10 | **uat** | **met** | operator's own UAT; provenance = main-session inline relay, 2026-09-09, transcribed at `notes/uat-BUG-1309-mirror-build-entry.md:360-403`. PASS condition answered: Step 3 `:175-177`. Message judged: `notes/rulings-2026-09-08-c19-copy.md` §2 |
| SC-11 | automated / integration | **met** | `notes/research-BUG-1309-goalcheck-c18.md` §3 (three `T-05` merge-control cases; discrimination at `e374c9a2` cited `notes/qa-c17.md:50-63`); re-affirmed `…-c18-sc04-ruling.md:80` |

Eleven of eleven met. **The goal is fully met**; every REQ traces through the tasks these criteria
grade, and no criterion is waived, partial or deferred.

## Does the recording move any criterion? — no

- **SC-04 (`BRIEF.md:108-125`)** — its single-owner clause asks for "a reason naming the feature and
  the re-run command". Read at the text, not from memory: the c19 copy carries both, and the
  criterion never required the recorded `github.build_entry` value be printed
  (`notes/rulings-2026-09-08-c19-copy.md` §3, confirmed `…-c19-goalcheck-copy.md` §3).
- **SC-10 (`BRIEF.md:157-160`)** — "sees it refused with a message they can act on without reading
  the source; after re-running `gh-sync.py open` the same command is allowed." The operator's
  overall "pass" plus their explicit CLEAR-and-ACTIONABLE judgement of the refusal wording is the
  criterion's declared method delivered in full. What the relay does not carry is a per-step
  itemisation of the script's own five-step rule (Steps 3, 3b, 5, 6, 7) — the second half of the
  criterion is covered by the operator's overall verdict, not by a separately reported Step 5/6
  observation. Recorded as a limit, not resolved by inference, not a downgrade.
- **Approval** — `BRIEF.md ## Approval` approved, re-signed 2026-09-08 over SC-11; `plan.yaml
  approval` approved, re-signed 2026-09-08 (commit `de04d841`), with D-19 applied additively
  afterwards under ruling R-7 §4, which owes no re-signature. **No amendment, no re-signature.**

## Residual candidates — sourced from disk, none gating

1. Clause (f) — add `"branch" in reason` as a conjunct at `tests/integration/test-merge-gate.py:159-163`
   (`notes/research-BUG-1309-c18-sc04-ruling.md:90-91`). **Unscheduled.**
2. Gap B — reorder the fixture so the era-exempt claimant sorts into `owners[0]`
   (`…-c18-sc04-ruling.md:92`). **Unscheduled.**
3. `{feat}` is proven but undefended: `test-merge-gate.py:68-69` cannot redden on a `{feat}`
   deletion, because the feature id also appears inside the rendered path
   (`notes/research-BUG-1309-c19-goalcheck-copy.md` §1 and Q1). Pre-existing; needs a cycle allowed
   to edit the carved-out test file.
4. `T-06 INV-37 message discriminator names recover-terminal only` is vacuously green under the
   reverted script (`notes/research-BUG-1309-goalcheck-amend-c13.md:63-67`) — bind it to a non-empty
   line.
5. Fixture calibration: clause (k) asserts the stderr content but not that the note is exactly one
   line, and the `chmod 0` fixture in clause (i) is non-claiming
   (`notes/research-BUG-1309-goalcheck-c18.md` §5 Q3).
6. Test-first order for the c19 delta cannot be established from the git record and is reported as
   such (`notes/qa-c19-copy.md` §b); `code_grade` is exactly 4 against a `>= 4` floor, no margin
   (§T-05 verify).
7. Standing scope boundaries the operator already signed, restated for the ship decision:
   a live `gh pr merge` is never exercised, and 17 sync-enabled legacy feature directories are
   KNOWINGLY UNRECOVERED (`BRIEF.md:174-191`).

Plus one optional confirmation line the ship decision may carry to the operator: *were Steps 3b, 5,
6 and 7 also PASS?* — see the fidelity limit above. The validator panel's advisories are the
orchestrator's and are deliberately not re-derived here.

## Non-modification

Files written in this dispatch: this note, and `notes/uat-BUG-1309-mirror-build-entry.md` — one
appended `## Operator result` section, 45 insertions / 0 deletions, verified with
`git diff --numstat`. No step renumbered, no PASS/FAIL rule reworded, no quoted expectation touched.
`BRIEF.md`, `plan.yaml` (every approval byte), `feature.json`, `STATE.md`, `merge-gate.py`,
`merge-gate.sh`, `test-merge-gate.py`, every other source, test and agent note, and
`runs/c19uat-product/` are **untouched**. No suite, formatter or linter run; no cycle opened; no
answers file authored or sought; nothing shipped, merged, committed or pushed; `HEAD` unmoved.
