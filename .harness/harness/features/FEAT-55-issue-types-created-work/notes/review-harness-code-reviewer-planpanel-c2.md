# Plan review — FEAT-55-issue-types-created-work — cycle 2 (plan mode)

**VERDICT: FAIL** — one high-severity Stage-1 spec-compliance gap, otherwise the settled repair
holds and the two goal-check findings are confirmed as non-gating.

## Stage 1 — spec compliance

### Must-fix — SC-08 is not fully proven on the `gh-sync.py open` route (high)

BRIEF `SC-08` (`BRIEF.md:132-138`) requires, per command, in that command's own test file: zero
`issue create` calls, **zero type-assignment calls**, non-zero exit, and the missing-type message
— "a refusal proven on one command never discharges this criterion for another." I checked all
three routes' refusal cases against this text directly:

| Route | Case | "zero `issue create`" | "zero `updateIssue`" | exit≠0 | names Task+`github.issue_types` |
|---|---|---|---|---|---|
| open — T-03 | F, `plan.yaml:522-524` | yes | **absent** | yes | yes |
| backlog — T-05 | G, `plan.yaml:774-775` | yes | yes | yes | yes |
| factory — T-07 | I, `plan.yaml:960-961` | yes | yes | yes | yes |

T-03 case F's intent never instructs the test-writer to assert zero `updateIssue` calls during the
refusal — the exact assertion T-05/T-07 both carry, in the exact wording T-04 §4 itself promises
("exit 2 BEFORE any issue create call and BEFORE any type-apply"). T-03's required-string loop
(`:460`) doesn't compensate: `updateIssue` is in that list, but is satisfied by any of the file's
*other* cases (A, E, G, H…) that assert successful `updateIssue` calls — it never binds specifically
to case F's refusal.

**Concrete failure scenario.** T-04 §4's required-set collection folds in already-recorded backfill
targets ("add the type of every already-recorded key that section 6 will backfill"). An
implementation that runs the backfill loop's `apply_issue_type` calls before it finishes computing
`missing_types` over the *whole* required set — the identical ordering bug T-05 case G's and T-07
case I's own intent text calls out ("a refusal ordered after `apply_issue_type`... would otherwise
ship with every plan-defined gate green") — mutates a real, already-existing GitHub issue's native
type on a run that is supposed to refuse cleanly, on the `gh-sync.py open` route specifically. T-04's
verify (`python3 tests/integration/test-gh-issue-types.py`) runs case F in full, but case F as
specified cannot catch this: it never asserts the `updateIssue` log is empty. This is the same
defect class the operator's 2026-09-04 ruling on `PF-f1031f76…` just closed for backlog/factory
("single-route coverage is not accepted") — left open here on the one route whose case F predates
this cycle's repair and was never re-aligned with its own siblings.

Repair is one line in T-03 case F's intent (add "ZERO argv containing `updateIssue`") plus adding
`updateIssue` binding to case F specifically if the required-string loop is tightened per C3-01
below. Not an operator decision — a completeness fix pm can make directly.

### Everything else in Stage 1 checked clean

- **No orphan `REQ`s.** REQ-01..REQ-11 each appear in at least one task's `traces:`; no task cites a
  `REQ` id BRIEF doesn't define.
- **No orphan `SC`s.** SC-01..SC-12 each have a task producing the named evidence (SC-04/SC-11 are
  `verify: inspection`, correctly deferred to the review-sha stage that doesn't exist yet in plan
  mode).
- **`depends_on` is a valid DAG**, red-before-green in all three pairs: T-03→T-04, T-05→T-06 (T-06
  also depends on T-04, correct — same file, sequential edits), T-07→T-08; T-01→T-02→{T-03,T-05,T-07};
  T-09→T-10; T-11→T-12. No inversion found.
- **The SETTLED repair (`PF-f1031f76…`) is real on the mechanism that gates the build.** T-05 gained
  case G (`:770-783`) and T-07 gained case I (`:954-969`); both trace `REQ-07`; both green tasks'
  `verify:` *execute* the file carrying the new case (T-06 `:795`, T-08 `:982`) — not just grep for
  its marker — so the refusal logic is bound by run, not by prose. This part of the repair is sound;
  the SC-08 gap above is a distinct, narrower hole in a case that predates the repair.

## Goal-check's own findings — independently checked

- **C3-01 (low) — confirmed, unchanged severity.** T-03's required-string loop (`:460`) omits
  `partial` and `github.issue_types` while T-05 (`:709`) and T-07 (`:872`) both require them. Verified
  by direct grep of the three loops. Real gate-uniformity gap, but the actual case-F assertions
  still get executed in full by T-04's verify (unlike the SC-08 gap above, which is a hole in what
  case F asserts, not in whether it runs) — low is the right call.
- **C3-02 (info) — confirmed, not a plan defect.** `PF-f1031f76…`'s `disposition` still reads
  `awaiting_user` (`plan.yaml:172`) after the ruling landed. Bookkeeping only; doesn't affect what
  ships. No action needed from me; pm's transcription pass is the natural place to close it.

## Stage 2 — code quality

N/A. No code exists yet (plan mode); nothing to grade.

## Not re-litigated

Both SETTLED rulings accepted as directed. The five unruled cycle-1 findings
(`PF-1286544c…`, `PF-452948136…`, `PF-e27f1c30…`, `PF-0c12a033…`, `PF-9a71cb9a…`) are untouched by
this pass — confirmed still present in `plan.yaml`'s `panel:` block, still `batched_to_signature_review`,
not re-raised here since nothing about them changed this cycle.
