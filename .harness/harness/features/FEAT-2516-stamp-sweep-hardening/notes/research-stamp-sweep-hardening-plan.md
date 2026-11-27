# Research — FEAT-2516 stamp-sweep hardening (plan draft, run 2026-11-26-01-plan-product)

**BLUF.** The plan has five tasks, all main-session-direct (DEC-174), with three decisions and ten
decision dispositions; one of them amends DEC-157. After the c1 reader wave `plan-merge.py check`
exits 0 (5 tasks, 16 anchors, 0 failures). B-4 (#2519) and the mechanical half of B-1 (#2516) are
already delivered on main, so the plan only guards them. B-9's receipt is sharpened below (D-02).

## C1 reader-wave dispositions

- scope high, receipt contract: applied in T-03 A/B/C (sole_effect, exact keys, FAIL-only,
  shared verify_fix_receipt; close-run acceptance test added).
- scope high, repository binding: applied (T-03 A.3 moves `_qa_code_repository` to
  `feature_schema.code_repository`; bound-feature acceptance and planning-only refusal tests).
- scope med, same-second regate: applied by association, not timestamp (T-03 E; SC-11/SC-12).
- scope med, T-01 segments: applied (reason names hit segments; row (l) asserts both; SC-02 baseline).
- scope med, T-02 escaped diagnostic: applied (exactly one positively identified line per mode; SC-06).
- scope form/med, keep rows: applied (DEC-159, DEC-221, DEC-227, DEC-230).
- scope form/low, prose: applied (ledger synopsis and equality sentence in T-03 G; recommended
  filename in D-02, T-05, SC-12; operator perspective says "no stamp outside").
- fable info, D-03 decline: kept as is; operator signature question.
- fable low, T-04 verify flag: declined. The grilling destination says the self-test is green; the
  flag is the direct evidence, D-03 now says it stays a supported local entry point.
- fable form/low, test rename: moot. The association design leaves that test unmodified and its
  name true (its regates answer no FAIL run).

## Measured at e83c4e20 (worktree), HARNESS_AGENT_TYPE unset

- `tests/integration/test-check-plan-routes.py --canonical-reader-self-test` exits 0 with ALL PASS
  and 0 FAIL lines. `CASES` contains `*CANONICAL_READER_CASES` (commit 70e869d9, FEAT-2489 T-01:
  "self-test ... runs by default"), so the integration runner already executes every self-test case,
  T-07 included. `tests.yml`'s canonical-reader comment still says "which no runner invokes" (stale).
  #2519 is CLOSED by PR #2530; #2516 is still OPEN. → T-04 adds a membership guard and fixes the
  comment; D-03 records why no runner step passes the flag.
- The tracked bin path is `.claude/skills/harness/bin/` (`.agents/skills` is a symlink);
  `plan-merge.py check` resolves every anchor on that spelling.
- `classify_feature` (`worktree_terminal.py`) returns three classes; absence is `unresolved` plus the
  word `absent` in its reason. In the fleet walk, `_landed_dir_names` returning None is skipped, so an
  unreadable tree and a missing one look the same (B-3).
- `_sweep_shape_stamps` lists `os.path.join(main_checkout_root, ".harness")` by pathname with no
  containment check, and interpolates raw names and reasons (B-5, B-6).
- **spend `rework_rounds: 2` is wrong; it should be 1.** FEAT-2458's ledger holds regates at
  `2026-11-24T13:21:14` (re-gating the plan FAIL, written by run-start of validate-c1, whose
  `started_at` is the same second) and at `13:41:45` (re-gating validate-c1). `_regate_rounds` counts
  a regate whose `at` is greater than or equal to the window opening, so the plan-FAIL regate counts.
  run-start writes the regate in the same write as the run it opens, in the same second, so a
  timestamp cannot separate the plan FAIL's regate from a same-second successor's. **Superseded at
  c1 (scope finding):** the draft's "strictly after" cutoff is replaced by INV-40's ledger-order
  association (`_owed_regate`: the k-th regate answers the k-th FAIL run); a regate counts when its
  FAIL run is in the window, and only an unmatched regate keeps the old inclusive timestamp rule.
  So `test_the_window_opens_exactly_at_the_first_validate_start` (all-PASS runs, unmatched regates)
  stays unmodified and true. Cheap and reversible: a digest note, not a D-NN.
- The B-9 refusal comes from `_run_end_digest` (`count != args.cycles_used`). Nothing records a
  main-session round: ledger.md § The cycle budget says "A main-session-direct segment is not a run
  and never appears in `runs:`".

## B-9 receipt — sharpened (D-02)

- **Location:** any regular file under the feature directory, recommended name
  `notes/fix-round-<run-id>.json`, not `feature.json`. An `evidence_ref` hashes an immutable regular
  feature-local file (`feature_schema.resolve_evidence_ref`), and `feature.json` is the mutable
  ledger, so it cannot be its own evidence.
- **Content:** the existing authorization-note protocol (`verify_evidence_ref`), tightened at c1:
  `{"feature_id", "effects": [{"effect": "main-session-fix", "run_id", "digest": {path, sha256},
  "cycles_used", "fix_commit"}]}`, exactly one `main-session-fix` effect in the note (new
  `sole_effect=True`; the base matcher only requires one MATCHING effect), exactly those keys, and a
  40-hex `fix_commit`. One shared `feature_schema.verify_fix_receipt` serves writer and INV-7; it also
  requires the run's verdict FAIL and C = digest count + 1.
- **Repository:** the writer resolves `fix_commit` with `code_grade.commit_oid` in the feature's code
  repository: `validate-digest.py#_qa_code_repository` moves to `feature_schema.code_repository`
  (bound feature → the `factory.repo` fleet checkout, DEC-221; else the four-up planning root). Its
  `load_fleet` row in `canonical-reader-classification.json` moves with it. INV-7 checks shape only,
  because a squash merge can drop the commit.
- **Record:** `cycle_evidence.source: main-session-fix`, with `by`, `at` and `authorization`. The
  schema enum and `run_evidence_problems` gain the branch (DEC-191 closed shape kept).

## Decision dispositions

| DEC | disp | why |
|---|---|---|
| DEC-157 | amend → D-02 | its exact-equality clause is what refused FEAT-2458's round |
| DEC-174 | keep | route |
| DEC-180 | keep | stamps still deleted on terminal only |
| DEC-238 | keep | sweep posture |
| DEC-191 | keep | new source binds the same authorization note |
| DEC-226 | keep | INV-39 bound unchanged |
| DEC-159 | keep | close-run composition; receipt rides run-end |
| DEC-221 | keep | fix commit resolved in the bound product repository |
| DEC-227 | keep | spend stays advisory |
| DEC-230 | keep | regate duty; spend matches regates to FAIL runs |

FEAT-2458 D-01 (three results) was plan-local (`dec: none`). No DECISIONS.md entry records it, so the
reversal lives in D-01 here and the shipped record stays untouched.

## Open

- #2519 is excluded from `source_issues` because it is already closed. Ship should still name it as
  delivered by #2530.
- The B-5 stamp-path containment check in T-02 step 3 is close to unreachable: listed basenames hold
  no separator, and leaf symlinks are skipped first. It is kept because the operator ruled "or a stamp
  path". The redirected-`.harness` row and the leaf-symlink row carry the evidence.
