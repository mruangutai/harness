# FEAT-2206 — ship review (validate-c3-validator)

**check-state no longer checks shipped features, and validation PASSES at review_sha `7b8e2e1f`.**
A feature whose `plan.yaml` reads `status: done` is dropped from the audit. Its records are still
read as comparison data by INV-24 (issue collisions), INV-52 (branch collisions) and INV-29
(standing finished worktrees). INV-28 and INV-30 are deleted and their numbers retired (DEC-252).
All four SCs are met and no must-fix is open. The branch is ready for a PR on your word.

No report round was spawned. Assembled from these digests on disk:
`runs/2026-11-08-01-product/digest.md`, `runs/validate-validator/digest.md` (c0 FAIL),
`runs/validate-c1-validator/digest.md` (c1 FAIL), `runs/validate-c2-validator/digest.md`
(c2 BLOCKED), `runs/validate-c3-validator/digest.md` (c3 PASS), plus the goal-check
`notes/research-FEAT-2206-skip-shipped-features-goalcheck-validate-c5.md`.

## Done when — graded

| Perspective (as signed) | Verdict | Discharged by | Evidence |
|---|---|---|---|
| **operator** — I can audit current work without shipped features being checked again. Historical claims still protect me from conflicting ownership and surviving finished-feature worktrees. | met | SC-01, SC-02, SC-03 | goal-check c5 lines 18–20; `notes/red-first.md` (baseline reds for every automated SC); real corpus: 10 landed, 8 shipped, 0 failures |
| **code maintainer** — I can change current validation without reviving historical checks, while unreadable status and non-shipped records retain their existing protection. | met | SC-04 (and SC-01's fail-closed cases) | goal-check c5 line 21; retirement tests red at b7af829c, green at pin |

## How it got here

| Run | Verdict | What it found | What changed |
|---|---|---|---|
| validate (c0) at `fe49c8df` | FAIL | **high**: `status: done` plus a second, malformed `status:` key read as shipped, so the plan was excused from every check. **med**: a shipped issue number `"²"` crashed INV-24. | Count every top-level status *key* before reading values. INV-24 and the strict loader turn unusable numbers into "unusable" rather than crashing. |
| validate c1 at `688c5ef5` | FAIL | **med**: a 4,301-digit shipped number still crashed INV-24. **low**: the ASCII-only guard regressed active `"٣"` claims. | You granted round 2. INV-24 goes back to `isdigit()` and treats an `int()` failure as unusable. |
| validate c2 at `4a351fae` | BLOCKED | **med (F-1/Q-02)**: a shipped record the strict loader refuses silently dropped its branch claim from INV-52. | You ruled "fix that" and granted round 3. INV-52 now re-reads such records leniently, as INV-24 does. |
| validate c3 at `7b8e2e1f` | **PASS** | No findings; SC-01..04 met. | — |

The lead summaries are in each run's digest.md. Security passed in every round (source-only review). UI scoped itself out (no visual surface).

## Open questions

- **Q-01 (non-blocking):** T-01's intent text talks about YAML-mapping and invalid-YAML handling. The adopted behaviour, per DEC-252, is a text-line classifier. The behaviour stays; only the signed wording drifts. Listed as B-1.

No escalations.

## Spend and judgements

`feature-record.py spend`: 5 runs, 68 wall-clock minutes, 60 rework minutes, tokens not recorded.
Rework budget: signed at 1 round / 45 min, raised by you to 2 / 75 and then to 3 / 105. All three rounds were used, ending at 60 of 105 minutes.
cycles_used 7 of 10. Judgements: 13 in total: 1 mission, 7 amendments, 3 regates, 2 continue.
`rework_rounds` reads 0 in `spend` despite three recorded regates (B-6).

## Amendments

| at | decision | reason | overruled |
|---|---|---|---|
| 2026-11-08T14:24:01Z | T-01.verify | Operator sign-off: also run the full suite and every gate in a standalone clone at the pin, with a final exit marker | no |
| 2026-11-08T14:41:22Z | T-01.verify | suite_layout refuses the same test file name in both unit and integration, so the unit test was renamed `test-check-state-shipped-ctx.py` | no |
| 2026-11-08T14:41:35Z | T-01.files | Same rename, plus ROW_FAMILIES, the `pr` schema text, and three fixtures that used `done` as an arbitrary station | no |
| 2026-11-08T14:46:51Z | T-01.files | Simplify REUSE: the audit-hook wrapper moved into the shared `f58_sparse_fixture.py` | no |
| 2026-11-08T15:13:34Z | T-01.files | Rework: `feature_json_write.py` added for a shared-coercion fix (later reverted, see the next row) | no |
| 2026-11-08T15:20:11Z | T-01.files | Rework: `opt_int` kept as is (#2151 relies on its raise); `artifact_accessors.py` absorbs it instead | no |
| 2026-11-09T15:01:37Z | T-01.files | Q-02 ruling: INV-52 (`check_state/corpus.py`) salvages strict-refused shipped branch claims | no |

overrule rate: 0/7

## Disclosed consequences (already stated in DEC-252)

- **No validate handoff note is demanded anywhere now.** INV-17 demanded `handoff-validate.md` only at station `done`, and `done` is no longer checked.
- **FEAT-63's "gh auth is probed once" test was deleted, not rebuilt.** INV-30 was its second prober; with INV-30 gone, the test has no pair of probers left to observe.
- **The exact-pin standalone verify can't run cleanly.** After `gh-sync status review` rewrites plan.yaml, INV-33/INV-26 report the pin stale (#2201, already filed). Each round's full verify therefore ran at the pin *commit*. That commit differs from the pin only in feature.json's `review_sha` and the regate. The readers independently confirmed the byte equivalence.
- The round-1 regate judgement names `09ac5a4e`, an intermediate tip that `688c5ef5` superseded after the `opt_int` revert.

## Proposed backlog

Strike any row by ID. Rows you don't strike become backlog issues when you accept the ship.

| ID | Nature | Item |
|---|---|---|
| B-1 | chore | Reconcile T-01's YAML-mapping intent wording with DEC-252's text-line classifier (Q-01). |
| B-2 | enhancement | Rebuild the "gh auth probed once" coverage lost with INV-30, over INV-26 + INV-37, if a second prober still exists. |
| B-3 | chore | Decide whether any seam should demand `handoff-validate.md` now that INV-17 no longer does at `done`. |
| B-4 | chore | `feature_json_write.opt_int`'s docstring promises None for junk, but it raises on `isdigit()` strings `int()` refuses (`"²"`, more than 4,300 digits). `board_lifecycle` (#2151) relies on that raise, and gh-sync reads only after the strict loader, which now refuses such values. Document the raise as the contract. |
| B-5 | chore | T-01.verify's real-corpus run does not capture the owner's HEAD before executing, so its evidence is not bound to an immutable SHA. |
| B-6 | bug | `feature-record.py spend` reports `rework_rounds: 0` after three recorded regate rounds. |
