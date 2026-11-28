# BRIEF — FEAT-2516-stamp-sweep-hardening Count a main-session fix round against the cycle bound, and each rework round once

## Problem

FEAT-2458 (#2509, squash 86ce6bac) had one fix round, built in the main session, and the ledger
could not record it (#2524, B-9 of the FEAT-2458 follow-ups). `run-end --cycles-used 1` was refused
with `cycles_used disagrees with authentic digest evidence` — the exact-count rule now in
`feature_record/runs.py` `_check_digest_record` — so the hard cycle bound never saw the round. At
the same time `spend` printed `rework_rounds: 2` for that single round: the plan FAIL's `regate`
and the validate FAIL's `regate` both landed in the rework window. The orchestrator therefore
under-counts the cycles a feature has spent and over-counts its rework.

## Done when — by perspective

**orchestrator** — When the main session builds a fix round itself, I can count that round against
the hard cycle bound, but only on an operator-signed receipt that names the round; and `spend`
counts each rework round once.

**code maintainer** — Moving the ledger, digest-validator and INV-7 changes in leaves every gate
that already covered those files green, and the code-repository reader the receipt needs stays
accounted for by the canonical-reader audit.

## Success criteria

- SC-09 (code maintainer): no regression at `review_sha`. The canonical-reader audit is clean:
  `check-plan-routes.py --canonical-reader-audit` exits 0 with a summary scanning more than 0
  Python files, and the `canonical_reader_live_audit_is_zero` check passes in
  `tests/integration/test-check-plan-routes.py`. Every pre-existing case in that file,
  `tests/integration/test-checker-structure-locks.py`, `tests/integration/test-validate-digest.py`
  and `tests/integration/test-check-state-table.py` passes. Each file exits 0 with no `FAIL` line
  (each exits 0 at e83c4e20, BRIEF pending; not re-observed at 3e979ae3).
  verify: automated        evidence: integration
- SC-10 (orchestrator): `feature-record.py run-end` and `close-run` accept `--cycles-used C` with
  `--fix-receipt <note>` and `--by <operator>` only when the run closes `FAIL` and C is the digest's
  `DIGEST.cycles_used` plus one. The note must be a feature-local strict-JSON file whose `effects`
  list holds exactly one `main-session-fix` effect, carrying exactly the keys `effect`, `run_id`,
  `digest`, `cycles_used` and `fix_commit`: it names the run, the digest's `{path, sha256}`, C, and a
  40-character lowercase hex `fix_commit` that resolves to a commit in the feature's code repository.
  For a feature bound by `factory.repo` that is the fleet member's checkout; otherwise it is the
  repository holding the feature. Each of the following is refused, writing nothing, and has its own
  unit assertion: no note; C not equal to the count plus one; `--verdict PASS` with a note; a note
  naming another run, another digest hash, another C or another feature; a note holding a second
  `main-session-fix` effect; an effect with an extra key; a `fix_commit` that is not 40 hex
  characters; a commit that does not resolve; for a bound feature, a commit present only in the
  planning repository; a note outside the feature directory; a missing `--by`; `--fix-receipt` with
  `--refused-return`. Acceptance is asserted through `run-end`, through `close-run`, and for a bound
  feature whose fix commit exists only in its product repository. On acceptance, the run's and the
  feature's `cycles_used` rise by one. `cycle_evidence` then records source `main-session-fix` with
  `by`, `at` and the note's `{path, sha256}`, and a replay writes nothing.
  `feature_record.evidence.run_evidence_problems`, the INV-7 reader, reports no problem for that
  record. It reports one once the note's bytes change, for a record whose run verdict is not `FAIL`,
  and for a record whose note holds a `fix_commit` that is not 40 hex characters.
  `schemas/feature.json` refuses a `main-session-fix` record that has no authorization. Asserted in
  `tests/unit/test-feature-record.py`; qa shows the acceptance assertion red before the change, when
  the writer refuses.
  verify: automated        evidence: unit
- SC-11 (orchestrator): `feature-record.py spend` counts a `regate` as a rework round when the FAIL
  run it re-gates is in the rework window, matching regates to FAIL runs in ledger order exactly as
  INV-40 does: the k-th `regate` answers the k-th FAIL run. A `regate` with no FAIL run left to
  answer keeps the existing rule, counting when stamped at or after the first validate run's start.
  `spend` prints `rework_rounds: 1` for a ledger shaped like FEAT-2458's: a plan run FAIL, a validate
  FAIL, a validate PASS, and two regates, the first re-gating the plan FAIL. It also prints 1 for
  the same ledger when both validate runs and both regates fall in one second. The existing
  contracts still hold, and every pre-existing `SpendTest` case passes unmodified: a direct fix
  round's regate counts, a window with no counted regate keeps its `fix-` run count, and no
  validate run means no round. Asserted in `tests/unit/test-feature-record.py`; qa shows both new
  rows red before the change, when they print 2.
  verify: automated        evidence: unit
- SC-12 (orchestrator): at `review_sha`,
  `git show <review_sha>:.claude/skills/harness/references/ledger.md` documents the main-session fix
  route. It names who writes the note and its recommended path `notes/fix-round-<run-id>.json`, says
  any feature-local regular file is accepted, and gives the exact effect shape. It shows both
  command forms that record it, `run-end` and `close-run` with `--fix-receipt` and `--by`. Its § Runs
  exact-count sentence names that route as the one exception. Its § Spend states that
  `rework_rounds` counts a `regate` by the FAIL run it re-gates, INV-40's ledger-order matching, and
  only when that run is in the rework window.
  `git show <review_sha>:.claude/skills/harness/SKILL.md` step 6's `close-run` synopsis carries
  `--fix-receipt`, and
  `git show <review_sha>:.claude/skills/harness/references/build-phase.md` step 6 points a
  main-session-direct fix round to that route. The reviewer cites each section.
  verify: inspection

## Verification gaps

- none: every automated criterion rests on an active kind with a runner (`integration` for SC-09;
  `unit` for SC-10 and SC-11). `component` and `ui` are unresolved with no runner, but this
  feature touches no `.tsx`, story or browser surface they would cover.

## Constraints

- BLOCKS — DEC-174: `feature-record.py` and its `feature_record/` package are the ledger writer,
  `feature_record/evidence.py` backs the gate-imported INV-7 reader, and `validate-digest.py` is the
  digest validator, so every task is `main-session-direct`.
- BLOCKS — DEC-191: `runs[].cycle_evidence` is a closed shape, so the new source is a schema enum
  value with the same hash-bound `evidence_ref` and authorization binding as `operator-history`.
- AMENDED by this feature — DEC-157: run-end's exact-equality rule between C and the digest count
  gains the one evidence-bound exception for a main-session fix round (plan D-02).
- SUPPLIES — the `evidence_ref` and authorization-note protocol in
  `.claude/skills/harness/references/ledger.md` § Runs (`--refused-return --evidence --by`), which
  the fix receipt reuses.
- SUPPLIES — DEC-221: a served feature's ledger and notes live in the control plane while its code
  lands in the product checkout, so the fix commit is resolved in the feature's bound repository.
- SUPPLIES — DEC-226: INV-39's hard bound on `cycles_used`, which a main-session fix round now
  reaches. DEC-159: `close-run` composes the existing authorities, so the fix receipt rides its
  `run-end` stage. DEC-230: every FAIL run still owes its `regate`, which `spend` now matches to
  that run. DEC-227: `spend` stays an advisory that never gates.

## Out of scope

- B-1 to B-8 of the FEAT-2458 follow-ups (#2516 to #2523): the operator closed #2516 to #2518 and
  #2520 to #2523 as not planned on 2026-11-27, and #2519 was closed by PR #2530 (FEAT-2489). The
  post-merge stamp sweep, `classify_feature` and the canonical-reader test wiring are unchanged.
- Retrofitting `cycles_used` for FEAT-2458 or any other already-shipped feature.

## Approval

status: pending
approved-by:
date:
