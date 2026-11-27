# BRIEF — FEAT-2516-stamp-sweep-hardening Harden the stamp sweep and count main-session fix rounds

## Problem

FEAT-2458 (#2509, squash 86ce6bac) shipped the post-merge stamp sweep with nine accepted residual
findings, now backlog issues #2516 to #2524 (receipt: `backlog-issues.json` in the main checkout's
FEAT-2458 directory). Three hurt whoever relies on the sweep: an id that landed nowhere is detected
by searching `classify_feature`'s reason text for the word `absent`, which an id or a station can
collide with (#2517); an unreadable fleet features tree is skipped exactly like a missing one, so the
id reads as absent or is decided from the other segments' hits (#2518); and a symlinked `.harness`
can point the sweep's unlink outside the main checkout, while a control character in a stamp name
can forge an output line (#2520, #2521). The tests leave gaps the validators named (#2522, #2523),
and the evidence for the canonical-reader contract pointed at a self-test no runner invoked
(#2516; #2519 was closed by PR #2530, FEAT-2489). Finally, FEAT-2458's one fix round was built in
the main session and could not be recorded: `run-end --cycles-used 1` was refused with
`cycles_used disagrees with authentic digest evidence`, so the hard cycle bound never saw the round,
while `spend` printed `rework_rounds: 2` for that single round (#2524).

## Done when — by perspective

**operator** — After a merge the sweep still deletes only the stamps of features finished on the
default branch. Every stamp it keeps is named once, labelled absent or unresolved with a reason, and
no stamp name, however strange, can print a line that reads as something else. No stamp outside my
main checkout is ever deleted, even when `.harness` is redirected.

**code maintainer** — Whether an id landed nowhere is a result I can branch on, never a word I must
search for, and a fleet tree that cannot be read is never mistaken for a missing one. The classifier
and sweep tests fail when the behaviour they name breaks, and the canonical-reader cases run in the
ordinary integration run with nothing able to drop them silently.

**orchestrator** — When the main session builds a fix round itself, I can count that round against
the hard cycle bound, but only on an operator-signed receipt that names the round; and `spend`
counts each rework round once.

## Success criteria

- SC-01 (code maintainer): `worktree_terminal.classify_feature(root, feature_id)` returns
  `(klass, reason)` with klass one of `terminal`, `not_terminal`, `unresolved`, `absent` and reason
  a non-empty `str`. It returns `absent` for an id with no landed directory under
  `.harness/harness/features/` or any readable fleet segment, including an id that strictly prefixes
  a different feature landed at `done`. It returns `unresolved`, never `absent`, for an unparseable
  landed `feature.json`, a landed `feature.json` that is not valid UTF-8, and a landed station
  outside the vocabulary. Each case is its own row in `tests/integration/test-worktree-terminal.py`;
  every row asserts the klass and that the reason is a non-empty `str`, and no row reads the reason
  to decide absence. qa shows the never-landed and strict-prefix rows red before the change, when they
  return `unresolved`.
  verify: automated        evidence: integration
- SC-02 (code maintainer): in a fixture fleet, an id not landed under the harness segment classifies
  `unresolved`, with a reason naming the segment, when one fleet segment's landed features tree
  exists but cannot be read. It stays `unresolved` even when another readable segment lands it at
  `done`. A declared segment with no landed features directory at all is skipped: an id landed
  nowhere is still `absent`. An id landed under two fleet segments is `unresolved` with a reason
  naming the count and both segments. Each case is its own row in
  `tests/integration/test-worktree-terminal.py`. qa shows the unreadable-tree and two-segment rows red
  before the change: the row whose other segment lands the id at `done` returns `terminal`, and the
  no-hit and two-segment rows return `unresolved` with a reason that names no segment.
  verify: automated        evidence: integration
- SC-03 (code maintainer): at `review_sha`, `git show <review_sha>:.claude/skills/harness/bin/post-merge-sweep.py`
  shows `_sweep_shape_stamps` choosing among delete, keep-as-absent, keep-as-unresolved and silence
  by comparing `klass` alone. `git show <review_sha>:.claude/skills/harness/bin/worktree_terminal.py`
  shows `classify_feature` returning the literal `absent` class. In neither file, nor in the
  classify_feature rows of `tests/integration/test-worktree-terminal.py` or the stamp rows of
  `tests/integration/test-post-merge-sweep.py`, does any expression test a `reason` string for
  absence. The reviewer cites each symbol.
  verify: inspection
- SC-04 (operator): on a fixture main checkout holding the plain stamp and stamps for a `done`
  feature, a `building` feature, a never-landed id that prefixes a landed `done` id, and a feature
  whose landed `feature.json` is not valid UTF-8, the real run deletes only the `done` stamp. The
  other four keep their bytes, and `--dry-run` deletes nothing. In each run, the never-landed stamp is
  named by exactly one line, `post-merge-sweep: stamps: kept .harness/<name> — absent: <reason>`.
  The undecodable stamp is named by exactly one line of the same shape labelled `unresolved`. Each
  reason is non-empty, and a line counts as naming a stamp only when it carries that stamp's exact
  token, so a longer id does not count. No line of either run that names the never-landed stamp
  says `removed` or `would remove`, and no line names the `building` stamp. Asserted in
  `tests/integration/test-post-merge-sweep.py`. qa shows the absent-label rows red before the
  change.
  verify: automated        evidence: integration
- SC-05 (operator): when the fixture main checkout's `.harness` is a symlink to a directory outside
  the checkout, the real run removes no stamp there: a `done` feature's stamp keeps its bytes. It
  exits 0 and prints exactly one `post-merge-sweep: stamps:` line, which says the sweep was refused
  because `.harness` resolves outside the main checkout. A stamp that is itself a symlink, for a
  `done` feature, is skipped: the link and its target both survive, and no line names it. Asserted in
  `tests/integration/test-post-merge-sweep.py`. qa shows the redirected-`.harness` row red before
  the change.
  verify: automated        evidence: integration
- SC-06 (operator): for a stamp whose file name carries a newline and an ESC character, in the
  `--dry-run` run and in the real run alike, exactly one stdout line mentions that stamp: the kept
  line `post-merge-sweep: stamps: kept .harness/<repr of the name> — absent: <reason>`, with a
  non-empty reason. The name and its reason are printed in Python `repr()` escaping, so a newline
  shows as a backslash followed by `n`, and the raw control characters appear nowhere in stdout. A
  printable name prints unchanged: the line `would remove .harness/.shape-sweep-stamp.<done id>`
  still appears verbatim. Asserted in `tests/integration/test-post-merge-sweep.py`; qa shows the
  control-character row red before the change.
  verify: automated        evidence: integration
- SC-07 (code maintainer): a case in `tests/integration/test-check-plan-routes.py` asserts that every
  member of `CANONICAL_READER_CASES`, `case_canonical_reader_t07_terminal_contract` included, is a
  member of `CASES`, the tuple the file's default run executes. Since FEAT-2489 the integration runner
  executes those cases. qa shows the case red on a mutant that drops `*CANONICAL_READER_CASES`
  from `CASES`, then restores the file byte for byte.
  verify: automated        evidence: integration
- SC-08 (code maintainer): at `review_sha`, `git show <review_sha>:.github/workflows/tests.yml`
  carries a canonical-reader audit comment that names `CANONICAL_READER_CASES` as running in the
  default run of `test-check-plan-routes.py`, and no longer says that no runner invokes the
  self-test. The reviewer cites the step.
  verify: inspection
- SC-09 (code maintainer): no regression at `review_sha`. The canonical-reader audit is clean:
  `check-plan-routes.py --canonical-reader-audit` exits 0 with a summary scanning more than 0
  Python files, and the `canonical_reader_live_audit_is_zero` check passes in
  `tests/integration/test-check-plan-routes.py`. Every pre-existing case in that file,
  `tests/integration/test-worktree-terminal.py`, `tests/integration/test-post-merge-sweep.py`,
  `tests/integration/test-checker-structure-locks.py`, `tests/integration/test-validate-digest.py`
  and `tests/integration/test-check-state-table.py` passes, except the rows this feature deliberately
  rewrites. Each file exits 0 with no `FAIL` line (each exits 0 at e83c4e20, BRIEF pending).
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
  `feature_schema.run_evidence_problems`, the INV-7 reader, reports no problem for that record. It
  reports one once the note's bytes change, for a record whose run verdict is not `FAIL`, and for a
  record whose note holds a `fix_commit` that is not 40 hex characters. `schemas/feature.json` refuses
  a `main-session-fix` record that has no authorization. Asserted in
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
  exact-count sentence names that route as the one exception, and its `close-run` synopsis carries
  `--fix-receipt`. It states that `rework_rounds` counts a `regate` by the FAIL run it re-gates,
  INV-40's ledger-order matching, and only when that run is in the rework window.
  `git show <review_sha>:.claude/skills/harness/references/build-phase.md` step 6 points a
  main-session-direct fix round to that route. The reviewer cites both sections.
  verify: inspection

## Verification gaps

- none: every automated criterion rests on an active kind with a runner (`integration` for SC-01,
  SC-02, SC-04 to SC-07 and SC-09; `unit` for SC-10 and SC-11). `component` and `ui` are unresolved
  with no runner, but this feature touches no `.tsx`, story or browser surface they would cover.
  The real main checkout's stamp population after merge is not a criterion; the fixtures carry the
  proof.

## Constraints

- BLOCKS — DEC-174: `worktree_terminal.py` and `check-plan-routes.py` are gate-imported,
  `post-merge-sweep.py` is a hook body, and `feature-record.py` is the ledger writer, so every task is
  `main-session-direct`.
- BLOCKS — FEAT-34 D-02 (one shared predicate, recorded in `worktree_terminal.py`'s docstring): the
  verdict stays `_landed_classification`'s; the sweep decides from `classify_feature`'s klass alone
  and deletes on `terminal` only.
- BLOCKS — DEC-191: `runs[].cycle_evidence` is a closed shape, so the new source is a schema enum
  value with the same hash-bound `evidence_ref` and authorization binding as `operator-history`.
- AMENDED by this feature — DEC-157: run-end's exact-equality rule between C and the digest count
  gains the one evidence-bound exception for a main-session fix round (plan D-02).
- SUPPLIES — DEC-180: a deleted stamp costs nothing, because check-domain.py falls back to its
  window. How stamps are written or read is unchanged.
- SUPPLIES — DEC-238: the sweep's pin and `node_modules` steps and the `--dry-run` posture the stamp
  step follows. Their retention rules are unchanged.
- SUPPLIES — the `evidence_ref` and authorization-note protocol in
  `.claude/skills/harness/references/ledger.md` § Runs (`--refused-return --evidence --by`), which
  the fix receipt reuses.
- SUPPLIES — DEC-221: a served feature's ledger and notes live in the control plane while its code
  lands in the product checkout, so the fix commit is resolved in the feature's bound repository.
- SUPPLIES — DEC-159: `close-run` composes the existing authorities, so the fix receipt rides its
  `run-end` stage. DEC-230: every FAIL run still owes its `regate`, which `spend` now matches to
  that run. DEC-227: `spend` stays an advisory that never gates.
- This reverses FEAT-2458 plan D-01 (three results, absent folded into `unresolved`) at the
  operator's explicit choice. That decision was plan-local (`dec: none`) and its shipped record is
  not edited.
- #2519 (B-4) was closed by PR #2530 (FEAT-2489): the self-test is green, and its cases run in the
  default `CASES`. This feature guards that property (SC-07) and does not list #2519 as a source
  issue.

## Out of scope

- Any change to which stamps get deleted: still `terminal` only.
- Retrofitting `cycles_used` for FEAT-2458 or any other already-shipped feature.
- Splitting `check-plan-routes.py` further; FEAT-2489 already landed that split.

## Approval

status: pending
approved-by:
date:
