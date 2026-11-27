# Plan goal-check — FEAT-2516-stamp-sweep-hardening (run 2026-11-26-01-plan-product, cycle 1)

**BLUF: Does this plan deliver the operator's stated intent? Mostly. It delivers every outcome in
the grilling's `## Destination`, but it replaces one settled instruction (B-1/B-4: "have the
integration runner invoke `--canonical-reader-self-test`") with plan D-03. No operator ruling for
that change is on record. Grades: operator PASS, code maintainer PARTIAL (it becomes PASS once the
operator ratifies D-03 at signature), orchestrator PASS.** "All nine issues close with this one
feature" no longer holds as written. All nine will be closed at ship, but #2519 was already closed
by PR #2530 (FEAT-2489) on 2026-11-24, so it does not close *with* this feature.

The grading source is `.harness/notes/grilling-stamp-sweep-hardening-2026-11-24.md`, the operator's
intent. The perspectives come from the BRIEF's `## Done when`, and the tasks from the applied
`plan.yaml`. Everything was read at worktree HEAD e83c4e20.

## Per-perspective grade

- **operator — PASS.** SC-04, SC-05 and SC-06 cover it, carried by T-02 (which depends on T-01 for
  the `absent` klass), with T-05 as the cumulative terminal gate. The sweep still deletes on
  `terminal` only (T-02 step 4) and labels kept stamps `absent` or `unresolved` from klass. It
  refuses when `.harness` resolves outside the main checkout (T-02 step 2;
  `case_shape_stamps_redirected_harness`). Names are escaped (`_shown`;
  `case_shape_stamps_link_and_controls`). Departures 3, 4 and 5 below are narrowings, not gaps.
- **code maintainer — PARTIAL.** SC-01, SC-02 and SC-03 are carried by T-01 and T-02 (four-class
  `classify_feature`, unreadable tree versus missing, no absence test on reason text). SC-07 and
  SC-08 are carried by T-04, which adds a CASES-membership guard and corrects the CI comment. SC-09
  is carried by T-01 to T-05, with T-05 terminal. Every item in the Destination ("self-test green
  and something runs it") is served:
  - I measured the self-test green at e83c4e20: `test-check-plan-routes.py --canonical-reader-self-test` exited 0, printed 0 `FAIL` lines and ended `ALL PASS`.
  - `CASES` already contains `*CANONICAL_READER_CASES` (`tests/integration/test-check-plan-routes.py#CASES`), so the integration runner runs those cases.

  The grade is partial only because D-03 overrides settled operator text (departure 1) without a
  recorded operator ruling. Departure 2 is a smaller literal deviation of the same kind.
- **orchestrator — PASS.** SC-10, SC-11 and SC-12 are carried by T-03; T-05 carries the DEC-157
  amendment that SC-10 depends on. The intent asked for three things, and all three are served:
  - `run-end`/`close-run` accept a count above the send-back count only with an operator-signed receipt that names the round. This is `--fix-receipt` plus `--by`, bound to the evidence like `--refused-return`.
  - The `rework_rounds: 2` cause is traced: run-start stamps the regate in the same second as the run it opens. T-03.E fixes it by matching each regate to its FAIL run in INV-40 order.
  - The grilling left one item "not yet specified": what the receipt contains and where it lives. D-02 settles it as `notes/fix-round-RUNID.json` with an exact effect shape.

  Departure 6 is a narrowing. The panel's open T-03 findings (PF-d0e16…, PF-3a8e…, PF-590e…) need
  dispositions before signature; that is a panel gate, not part of this grade (see the advisory
  below).

No perspective is left without a task.

## Departures from `## Settled` (operator text)

1. **B-1/B-4, the runner step is declined (D-03).** Settled text: "have the integration runner
   invoke `--canonical-reader-self-test`". D-03 adds no runner step. It relies instead on the
   default `CASES` run, which since FEAT-2489 is a superset of the self-test, and T-04 guards that
   with `case_canonical_reader_cases_run_by_default`. The flag survives only as a local entry point,
   exercised by T-04's verify. The panel's should-not-exist reader (PF-980581…, info) endorses the
   decline. The reasoning holds, and I checked its premise above. It is still a reversal of operator
   text and **needs the operator's explicit ratification at signature**.
   - The rest of the item holds. The "fix its 2 pre-existing failures" part was done outside this feature: #2519 was closed by PR #2530, merged 2026-11-24T17:13:38Z.
   - "Point SC-07-style evidence at `--canonical-reader-audit`" is met by SC-09, which requires exit 0 with more than 0 files scanned. T-03 and T-05 run the audit in their verify.
2. **B-2, "no code or test matches the reason text any more".** The plan narrows this to "no test
   reads the reason to decide absence" (SC-03). Some T-01 rows still assert reason substrings for
   other purposes:
   - row (k): `must=("unparseable",)`
   - row (l): `"2 segments", "second-repo", "third-repo"`
   - rows (n) and (o): `"third-repo"`

   These match the issue's intent (#2517 is about the absence marker), but a literal reading of the
   operator's sentence is broader. This is minor; the operator should be told.
3. **B-3, "it never decides from the remaining hits".** T-01 row (p) asserts that an id landed
   under the harness segment classifies `terminal` even while a fleet segment's tree is unreadable.
   The harness hit short-circuits before the fleet walk, which is existing behaviour that T-01 keeps
   ("keep steps a to c unchanged"). If that id were also landed in the unreadable segment, the
   duplicate would go unseen. This is defensible, but it is narrower than the literal text.
4. **B-5, "refuse to sweep when … a stamp path resolves outside".** A symlinked stamp is skipped
   **silently** by the existing `islink` filter: SC-05 says "no line names it". It is not reported
   as a refusal. The new per-stamp refusal branch (T-02 step 3) is therefore close to unreachable,
   because a non-symlink regular file under an in-checkout `harness_real` cannot realpath outside.
   The panel already flags this as overstated containment (PF-6cf433…, low). The safety outcome
   holds: nothing outside the checkout is deleted.
5. **B-6, "print stamp names with repr()-style escaping".** The plan applies `repr()` only when
   `str.isprintable()` is false (`_shown`, T-02 step 1). Printable names print unchanged, and SC-06
   requires that. This is a deliberate narrowing that preserves existing output lines.
6. **B-9, "accept `--cycles-used` above the digest's send-back count".** The plan accepts exactly
   the count plus one, on a `FAIL` run only (D-02, SC-10), with `--fix-receipt`/`--by` rather than
   a reused `--evidence` flag. This is narrower than "above", and D-02 justifies it: one FAIL run is
   answered by at most one round.

**`source_issues` excludes #2519.** `plan.yaml` lists `[2516, 2517, 2518, 2520, 2521, 2522, 2523,
2524]`. I checked each with `gh issue view` on 2026-11-26: #2519 is CLOSED (closedAt
2026-11-24T17:13:39Z, closed by PR #2530), and the other eight are OPEN. Each of the eight is served
by a task:

| Issue | Task(s) |
|---|---|
| 2516 | T-04 |
| 2517 | T-01, T-02 |
| 2518 | T-01 |
| 2520 | T-02 |
| 2521 | T-02 |
| 2522 | T-01, T-02 |
| 2523 | T-01 row (l), T-02 link case |
| 2524 | T-03, T-05 |

So the end state "all nine closed" holds. "Close with this one feature" is false for #2519, and the
operator should be told that at signature rather than discover it.

Out of scope is respected: deletion is still `terminal` only, there is no `cycles_used` retrofit, and
there is no further `check-plan-routes.py` split.

## Advisory (not graded here)

The panel records 2 high, 4 med, 3 low and 1 info finding, all with disposition `open`. Several of
them (PF-d0e16…, PF-3a8e…, PF-590e…, PF-4901…, PF-f289…) describe defects that the applied plan's
text now appears to address:
- `verify_fix_receipt` shared with INV-7, plus `sole_effect`
- `feature_schema.code_repository` for fleet commits
- regates counted by FAIL run "whatever its timestamp"
- the duplicate-hit reason naming every segment
- the exactly-one-line FEAT-914-ctl count

That is [INFERENCE] from reading the plan text; I did not re-run the panel. Their dispositions belong
to the product lead and must be recorded before signature.
