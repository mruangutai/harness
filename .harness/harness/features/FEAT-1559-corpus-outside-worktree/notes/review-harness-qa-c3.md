# QA gate — FEAT-1559 cycle 3 (run validate-c2-validator, pin 6c11ab626ed568236978b1640928162b8cf0139f)

**BLUF: PASS.** Both required kinds are green at the exact SHA in an ordinary full non-linked clone
(unit exit 0, 52 files; integration exit 0, 80 files; no failing file). The four new c2-fix tests
are red against the prior production (`feature_corpus.py` at 42856abb) and green at 6c11ab62, and I
reproduced that myself. No source, test or fixture was edited. Only my own evidence has examined the
fix tests beyond the author's receipt (no second-reviewer independence applied to their design).

## Phase 1 (BRIEF + plan only, before source)
Expected coverage for this delta: a feature id present in two `.harness/*/features` segments must be
two population entries in a sparse worktree AND a full clone; this checkout's copy replaces only the
same (segment, id); each id-keyed consumer (`merge-gate` multi-owner deny, `board_lifecycle` audit)
must see both; population order unchanged for distinct ids. All four are present as tests (below).
Gap against Phase 1: no unit-kind test pins the shared-id behaviour (see coverage_gaps).

## Subject and identity
- Pin via `pinned-checkout.py add --feature FEAT-1559-corpus-outside-worktree --run-id validate-c2-validator --persona harness-qa --sha 6c11ab62…` → HEAD 6c11ab626ed568236978b1640928162b8cf0139f, clean. It is an unconverted linked worktree (hooksPath `.claude/skills/harness/hooks`, pre-1559 owner hooks), so suites ran in a disposable exact-SHA full clone instead: `git clone --no-local --no-checkout` + `update-ref --no-deref HEAD` + `git restore --source=HEAD --staged --worktree .` at `/tmp/f1559-qa-c3/clone`: HEAD 6c11ab62…, shallow false, status 0, `worktree-state.py --verify --json` → class `plain-clone`, findings `[]`.
- Delta 42856abb..6c11ab62 outside the feature directory: exactly `.claude/skills/harness/bin/feature_corpus.py` and `tests/integration/test-feature-corpus.py` (plus the feature's own notes). merge-base(6c11ab62, origin/main) = e8d868f7 = declared baseline; whole-feature diff e8d868f7..6c11ab62 = 88 paths, **0** under any other feature directory (SC-11 re-derived, inspection).
- Matrix: T-01..T-05 `cross_module` (→ unit + integration `always`), T-06 `docs` abandoned. `harness.json` `unit`/`integration` active with the commands below; functional/eval excluded; component/ui/typecheck unresolved with no SC.

## Required kinds
| Kind | Command | Exit | Discovery (ls-tree = runner pool) | Failing files | State |
|---|---|---|---|---|---|
| unit | `env -u HARNESS_AGENT_TYPE python3 .agents/skills/harness/bin/run-unit-tests.py --kind unit` | 0 | 52 / 52 | 0 | satisfied |
| integration | `env -u HARNESS_AGENT_TYPE python3 .agents/skills/harness/bin/run-unit-tests.py --kind integration` | 0 | 80 / 80 | 0 | satisfied |

PASS lines 767 / 2341 (one line per script, repo G-04). The only `FAIL` tokens are four `FAIL BUG-1290 5a/5b/5c` lines of `test-factory-claim-mutation.py`'s own mutation proof (repo G-09). Runner counts reconcile with c2 (52/80); clone status porcelain 0 after both runs.

## The four new tests — red/green (own reproduction)
Isolation: second disposable clone at 6c11ab62; `git restore --source=42856abb --worktree .claude/skills/harness/bin/feature_corpus.py` (production only; tests untouched at 6c11ab62), run `tests/integration/test-feature-corpus.py`:
`Ran 28 tests, FAILED (failures=3, errors=1)`
- `SegmentIdentity.test_a_shared_id_is_two_entries_from_a_worktree_and_from_a_clone`: FAIL `('harness','FEAT-2-beta') not found in [... ('kaya','FEAT-2-beta')]`.
- `SegmentIdentity.test_this_checkouts_copy_replaces_only_its_own_directory`: ERROR `KeyError: ('harness','FEAT-2-beta')`.
- `MergeGate.test_one_id_claimed_from_two_segments_is_two_owners_and_denies`: FAIL, gate reaches a different recover-terminal reason instead of "claimed by more than one feature record (FEAT-2-beta, FEAT-2-beta)" — one owner counted, deny cannot fire.
- `BoardStatus.test_one_id_active_in_two_segments_is_audited_in_both`: FAIL, only card #601 (kaya) reported, card #501 (harness) dropped.
Restoring production to HEAD: same file, `Ran 28 tests … OK` (and in the full integration run). This matches `receipt-main-session-fix-c2.md` (3 FAIL + 1 ERROR). Tier: natural RED against the retained pre-fix production byte-for-byte, test bytes unchanged.
Not retaken: per-site parity mutants (revert only `_local_entries` keying, or only the `population` landed map) — only the whole-revert red is established here; the two keying sites' independent discrimination is the author's claim, unprobed by me.

## Population-identity consumer coverage
Callers of `feature_corpus.population`: `merge-gate.feature_for` (bound by new MergeGate test), `board_lifecycle._feature_dirs` (bound by new BoardStatus test, plus c1 landed/broken-layout tests), `validate-feature-json` (reads `path`; unchanged shape, existing suites green), `branch-create-gate` (id membership: duplicate id is harmless; its allow/deny payload tests green). `ctx.population()` (`check_state/ctx.py:366`) is a separate id-keyed function, deliberately unchanged: its landed side is a list (both segments retained), its local side is the single active id, and `check_state/corpus.preflight` runs `worktree-state --verify` first, which refuses when two segments claim the active id (`tests/integration/test-worktree-state.py:144` `test_two_segments_claiming_the_active_id`, asserted in verify and repair mode). The code path supports the stated rationale. I did not obtain a check-state-level run showing that refusal (the guard denied a probe worktree), so the end-to-end refusal rests on the verify-mode test plus the `_layout` code read, not on an executed check-state repro.
Order: sort key `(id, segment)`; `test-feature-corpus-gates.py` / `test-corpus-regression.py` distinct-id order assertions still green.

## Previous closures (c1 must-fixes, c2 re-reddened by mutation)
Production delta since 42856abb is the single `feature_corpus.py` hunk set above; the c1 closure sites (`check-plan-routes` `require_landed`, `check-decision-anchors` owner routing, grade extractions) are untouched, and their reddening tests are green in the full integration pool. I did not re-run the c2 mutants (production unchanged there); closure status is carried by unchanged-green suites plus the c2 note, not a new fail-first.

## Per-SC automated evidence (c3, unchanged from c2 except the new rows)
SC-01 `test-worktree-state.py`, `-hooks.py`; SC-02 `test-feature-corpus.py` (reads, guards, anchors), `omp-hooks.test.ts`; SC-03 `test-check-state-corpus.py`; SC-04 `test-check-state-corpus.py`, `test-feature-corpus.py` Discovery/Board/**SegmentIdentity**, `test-feature-corpus-census.py`; SC-05 `test-feature-corpus-discovery.py`, `test-check-state-corpus.py`, **`test-feature-corpus.py` MergeGate**; SC-06 `test-corpus-non-regression.py` + plain-clone runs (positive control); SC-07/08/09 hook/state suites; SC-12 `test-corpus-real-owner.py`; SC-13 six unit files. SC-10 deferred-by-ruling (#2101, SC-10 amended 2026-10-05); SC-11 inspection re-derived; SC-14 inspection. Fail-first tiers are those of `review-harness-qa-c1.md`/`-c2.md`; c3 adds only the natural RED above.

## Bounded limitations (carried, not reopened)
- **SC-13 historical pre-production evidence:** no natural pre-production capture exists for most unit predicates; bootstrap/import reds and constructed mutants (c1, own reproduction) remain the tier. Bounded; not re-measured in c3.
- **G-1 (advisory):** `_maximal_outside_features` kept-ancestor clause mutant survives (c2); not retaken, no new evidence.
- **G-4 (inconclusive):** `check-domain.py` `if False:` mutant not reproduced red (c2); not retaken.
- **New advisory (qa):** the shared-id-across-segments behaviour of `population` is bound only by integration tests; the unit kind passed at 42856abb with the id-only keying, so no unit test discriminates it. Does not breach the matrix floor (unit named tests exist for `population` order/replacement) and is outside SC-13's enumerated predicates.
- Unit/integration passes are a plain-clone result; non-skipped SC-12 real-owner run needs a converted caller (#2101).

## Principles applied
- Verification is the product (rule 7): the new tests were reddened against the retained prior production, not credited from the receipt.
- Never falsify the record (rule 15): the unretaken per-site parity mutants and the missing check-state-level probe are recorded as unretaken.
- No more specific than necessary (rule 6): limitations stated at the weakest claim the evidence supports.

## Cleanup receipt
Pin `FEAT-1559-corpus-outside-worktree--validate-c2-validator--harness-qa` removed via `pinned-checkout.py remove`; `/tmp/f1559-qa-c3` (both clones, logs) removed. Confirmed below at return.
