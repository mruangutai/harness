# QA gate — FEAT-1559 cycle 1 (run validate-validator, pin 0e8301a5)

**BLUF: FAIL.** Both registered kinds are green at the exact pin in an ordinary full non-linked clone
(unit exit 0, 52 files; integration exit 0, 80 files; 0 named failures). The gate fails on
discrimination and coverage, not on a red suite: three changed units have no test that binds
them (mutants survive the whole unit and integration kinds), one derivation clause of SC-13's
`derive_cone` predicate is unbound, and the fail-first evidence for most automated SCs is a
bootstrap-tier red or a narrative receipt, not a retained natural RED. Details below; nothing
was fixed.

## Phase 1 — expected coverage, derived from BRIEF/plan before reading any source

(Only BRIEF.md, plan.yaml, STATE.md and the receipts' file lists were read; no `.py`/hook source.)
Matrix: every task T-01..T-05 is `cross_module` → `unit` + `integration` both required
(`harness.json` test_matrix.cross_module.always); T-06 `docs` (abandoned) → none. component/ui/
typecheck are null/unresolved with no SC; functional/eval are excluded (DEC-187).

| SC | Expected test (kind) |
|---|---|
| 01 | cone for each of harness worktree / fleet planning / validator pin = exactly the active dirs; new top-level dir survives; segment = record segment not worktree segment; recordless id from identity across all segments; creators converge (integration) |
| 02 | absolute owner-root read of landed other feature from all three classes equals main bytes and dir absent locally; unavailable owner/missing path refuse by name; Write/Edit + Bash guards refuse main-corpus write; relative control roots to checkout (integration + OMP adapter) |
| 03 | full vs sparse normalised finding equality; open() instrumentation confined to own record; explicit missing `--feature` refuses (integration) |
| 04 | name-set (not count) compare, N of M + sorted names + remedy, before invariants; plain clone full; unexpected-only non-gating; census detects unmarked enumeration incl. injected scratch site (integration) |
| 05 | landed-only branch claims; one finding naming both; sentinels none; exact FEAT-02/FEAT-03 era exemption with reason, third claimant/empty reason re-collide; merge/branch-create graded by permissionDecision with allow controls (unit + integration) |
| 06 | fresh plain clone full corpus, verify no-op, suites green in plain clone, CI untouched (integration + gate) |
| 07 | exits 3/4/7/8; verify mutates nothing; A/B/C classification; mixed refuse byte-identical; repair idempotent (integration) |
| 08 | post-checkout/merge/rewrite repair by identity; bare `git worktree add`; A/B/C merge cases; shim delegate attribution, exit 0, stdin preserved; sweep intact (unit + integration) |
| 09 | preflight verify-not-repair; 3/4/7 refuse, 8 non-gating; downstream-not-run witness + structural positive control (integration) |
| 10 | deferred-by-ruling (#2101), excluded |
| 11 | inspection (one-time immutable endpoint receipt) |
| 12 | real-owner name-set equality, >70 floor, staged-missing + wrong-root mutants, disposable pin dirty-vs-structural, skips announced (integration) |
| 13 | unit negative cases for: cone derivation, active segment + pin-name classification, owner-root resolution, linked_worktrees parity, branch sentinels + exact-set exemption, census discrimination (unit) |
| 14 | inspection of AGENTS.md + skill docs at the pin |

Phase 2 gaps against this list are under **Coverage gaps**.

## Subject and receipt audit

- Pin: `pinned-checkout.py add --feature FEAT-1559-corpus-outside-worktree --run-id validate-validator --persona harness-qa --sha 0e8301a5…` (removed on return; see end).
- The pin is a linked worktree and was **not sparse** (117 feature dirs; the owner's hooks are pre-1559 until merge), so it is not an ordinary full non-linked subject. The gate subject is a disposable clone made with `git clone --no-local --no-checkout` + `git update-ref --no-deref HEAD <pin>` + `git restore --source=HEAD --staged --worktree .` (bash-write-guard refuses `git checkout` by design): `/tmp/f1559-qa-clone-QZwT/clone`, HEAD `0e8301a58a7de7dc23a067005c9aa8b3ee528de0`, shallow `false`, `.git` a directory, 117 feature dirs, `worktree-state.py --verify --json` → exit 0, class `plain-clone`, findings `[]`, noop "not a linked worktree; a plain clone keeps the full corpus". `HARNESS_AGENT_TYPE` unset for the runner (expertise G-07).
- Relation 69e3d819..pin: three commits (`f81d43e1`, `dbadb584`, `0e8301a5`); `git diff --name-status 69e3d819 0e8301a5` touches only STATE.md, feature.json, plan.yaml, notes/non-regression-receipt.md, notes/receipt-T-05.md — all inside this feature directory. **Settled relation confirmed**; tests/source/docs are byte-identical between C and the pin.
- SC-11 re-derived at the pin (not credited from the receipt): `merge-base(pin, origin/main)` = `origin/main` = `e8d868f78a6ec43880598af5c5873f5daa8ba985`; `git diff --name-only e8d868f7 0e8301a5` has 0 paths under any other feature directory; other-feature `git ls-tree -r` entries 4635 at both endpoints; `.github` diff empty.

## Gate runs (once, exact pin, ordinary full clone)

| Kind | Command | Exit | Discovery | Named failures | Notes |
|---|---|---|---|---|---|
| unit | `python3 .agents/skills/harness/bin/run-unit-tests.py --kind unit` | 0 | `pool: 8 workers, 52 files, 15.29s` | 0 | 766 `PASS` lines; every `-----` file line `exit 0`; includes `test-omp-hooks.py` → bun `138 pass / 0 fail` (FEAT-1559 absolute-read case at `tests/unit/omp-hooks.test.ts:1313`) |
| integration | `python3 .agents/skills/harness/bin/run-unit-tests.py --kind integration` | 0 | `pool: 8 workers, 80 files, 83.59s` | 0 | 2341 `PASS` lines; every file `exit 0`; `git status --porcelain` clean after |

Emitted FAIL strings that are **not** failures: 4 lines `FAIL BUG-1290 5a/5b/5c` inside `test-factory-claim-mutation.py`'s own mutation proof (unit, exit 0; expertise G-09). Grade is the runner's exit code.

Announced skips (integration, exit 0, not credited as evidence): `test-corpus-non-regression.py` live manifest validation ×2 (`--conversion-manifest` absent; T-06/#2101 deferred, so SC-10's check is un-run, by ruling); `test-corpus-real-owner.py` ×2 "host prerequisite missing: clone is the owner itself, so there is no active-worktree caller" — the real-owner caller comparison cannot run in a plain clone.

**Discovery discrepancy (finding L-1):** receipt-T-05/non-regression-receipt/STATE report unit **54/0** and integration **86/0** at 69e3d819; `git ls-tree` at 69e3d819 and at the pin both give 52 `tests/unit/test-*.py` and 80 `tests/integration/test-*.py`, and the runner discovered exactly that. Exits agree (0/0) but the 54/86 file counts are not reproducible from the tracked tree and the receipt does not reconcile them (expertise G-11). Not a failure; the receipt's counts must not be cited as the discovery set.

Real-owner non-skipped run (SC-12), run by me from a converted subject: `python3 tests/integration/test-corpus-real-owner.py -v` from the feature worktree (HEAD `33d10434`; 0 non-feature-directory paths differ from the pin; `--verify` exit 0, class planning-worktree) → `Ran 6 tests … OK`, 0 skips, probe pin `BUG-1016-…--f1559-63793--probe` at owner HEAD `e8d868f7`, removed (0 probe pins after). Run from my own (unconverted, 117-dir) validator pin the same test **fails** `test_check_state_passes_the_corpus_choke_point` with `LAYOUT cone (3) … skip-bits (4) … no invariant ran` — correct structural refusal of an unconverted caller, not a code defect; the test's non-skipped outcome depends on which checkout invokes it (note for ship: a post-merge validator pin is converted by the new hooks, a pre-merge one is not).

## Per-kind state

| Kind | State | cmd | Named tests |
|---|---|---|---|
| unit | satisfied | `run-unit-tests.py --kind unit` | 52 files; new/changed for this feature: 8 (`test-worktree-state-rules`, `test-feature-corpus-discovery`, `test-check-state-corpus-rules`, `test-feature-corpus-gates`, `test-worktree-state-hooks-rules`, `test-corpus-regression`, + updated `test-check-skill-refs`, `test-factory-cli`, `test-feature-json-budget`, `test-plan-depends-on`) |
| integration | satisfied | `run-unit-tests.py --kind integration` | 80 files; new/changed: 11 (`f58_sparse_fixture` helper, `test-worktree-state`, `test-worktree-state-hooks`, `test-check-state-corpus`, `test-feature-corpus`, `test-feature-corpus-census`, `test-corpus-non-regression`, `test-corpus-real-owner`, `test-check-instruction-paths`, `test-check-plan-routes`) |
| component, ui, typecheck | not_applicable-equivalent: `unresolved`/null, no SC, no browser/TS production change (BRIEF Verification gaps) — not in the matrix for these tasks | null | 0 |
| functional, eval | not_applicable (`excluded`, DEC-187) | null | 0 |
| locally_run probes | no change touches their `detect` surface | — | 0 |

## Automated SC → test evidence and fail-first

Fail-first method. (a) **Natural pre-change RED, my own reproduction**: clone at `pre_change_sha` e8d868f7 with the pin's `tests/` restored over it (`/tmp/f1559-qa-clone-QZwT/pre`); every new/changed test run directly. All 19 exit 1. Tier of each red is stated — `bootstrap` = `ModuleNotFoundError`/missing command (proves the module is new, not a predicate); `assertion` = a named assertion on pre-change behaviour. (b) **Mutants** applied in the disposable clone (`git restore -- .claude` and `git status --porcelain` = 0 after each batch), per-test attribution from the failing test name.

| File (pre-change exit 1) | Pre-change red tier |
|---|---|
| test-feature-corpus-census.py | **assertion**: `test_every_detected_site_is_marked` — unmarked `board_lifecycle.py:456` + others |
| test-check-instruction-paths.py | **assertion**: "a landed feature read at the control plane is clean" got `anchored to the control plane`; "…refused at the feature tree" got 0 violations |
| test-worktree-state-hooks-rules.py | **assertion/absent shim**: `post-checkout`/`post-rewrite` FileNotFoundError, 12 tests |
| test-worktree-state-hooks.py | partial: `JSONDecodeError` ×8 (missing `worktree-state.py`) — bootstrap |
| test-worktree-state.py, test-check-state-corpus.py | bootstrap (`can't open …/worktree-state.py`; 22/12 failing) |
| test-worktree-state-rules, test-feature-corpus-discovery, test-feature-corpus-gates, test-check-state-corpus-rules, test-corpus-regression, test-feature-corpus, test-corpus-non-regression, test-corpus-real-owner, test-check-skill-refs, test-factory-cli, test-feature-json-budget | bootstrap: `ModuleNotFoundError: feature_corpus` |
| test-check-plan-routes.py | bootstrap: `FileNotFoundError …/feature_corpus.py` |
| test-plan-depends-on.py | non-discriminating (`harness_yaml` not importable in my pre tree) |

Mutant evidence (one clone at the pin; attributed failing tests, all red unless stated):

| Predicate (SC) | Mutant | Red test (file:line) |
|---|---|---|
| cone: top-level except `.harness` (01/13) | `top` keeps `.harness` | `test-worktree-state-rules.py:38` |
| cone: **maximal subtrees only** (01/13) | `maximal = set(under)` | **SURVIVES** unit `test-worktree-state-rules.py` (15/15 OK) and integration `test-worktree-state.py` (23/23 OK) — no fixture has a kept `.harness` dir with a kept descendant |
| in_cone ancestor-file clause (07/13) | `startswith(parent+"/")` → False | `test-worktree-state-rules.py:70` |
| active segment exact, not worktree segment (01/13) | segment forced `harness` | `test-worktree-state-rules.py:112` |
| recordless → all segments (01/08/13) | `every[:1]` | `…rules.py:117` |
| two claiming segments refuse (01/13) | `>5` | `…rules.py:123` |
| pin-name shape (01/13) | `len(parts) < 3` | `…rules.py:86` |
| name/branch disagree refuses (13) | disabled | `…rules.py:105` |
| branch sentinel `none` (05/13) | only `""` sentinel | `test-feature-corpus-discovery.py:35` |
| exact-set exemption; third claimant (05/13) | subset match | `test-feature-corpus-discovery.py:46` |
| empty reason defeats exemption (05/13) | reason not checked | `test-feature-corpus-discovery.py:54` |
| owner unparseable pointer (13) | disabled | `test-feature-corpus-discovery.py:114` |
| owner manifest not readable (02/13) | disabled | `test-feature-corpus.py:105`, `test-feature-corpus-gates.py:121` |
| compare_names swap (04/13) | missing/unexpected swapped | `test-feature-corpus-discovery.py:128`, `test-check-state-corpus-rules.py:56,67` |
| linked_worktrees parity (13) | no owner normalisation | `test-feature-corpus-gates.py:56` |
| population: this copy replaces landed; main refuses missing (02/04) | override removed / check removed | `test-feature-corpus-gates.py:69,78,87` |
| corpus_path never answers own feature from owner (02/13) | lexists clause dropped | `test-feature-corpus-gates.py:110` |
| no sibling provider (02) | sibling worktrees searched | `test-corpus-regression.py:95` |
| verify report: dirty must not mask structural; unknown code errors (09/13) | masked / ignored | `test-check-state-corpus-rules.py:34,47` |
| class C staged / real edit (07) | staged-index test removed; `y in "MT"` removed | `test-worktree-state.py:228,222,241` |
| repair refuses on dirty (07/08) | repair proceeds on exit 8 | `test-worktree-state.py:246,255` |
| missing name-set refuses (04) | refusal disabled | `test-check-state-corpus.py:149`, unit `:56` |
| missing `--feature` refuses (03) | always passes | `test-check-state-corpus.py:143`, unit `:81,86` |
| dirty non-gating (09) | dirty refuses | `test-check-state-corpus.py:175,183` |
| INV-52 duplicate (05) | no collisions | `test-check-state-corpus.py:111` |
| merge-gate layout refusal (05/09) | `refusal = None` | `test-feature-corpus.py:166` |
| hook stdin untouched (08) | `</dev/null` removed | `test-worktree-state-hooks-rules.py:99` |
| hook exits 0 (08) | `exit "$_rc"` (post-rewrite) | `test-worktree-state-hooks-rules.py:120,129` |

| SC | Test(s) | Fail-first (strongest tier) |
|---|---|---|
| SC-01 | `test-worktree-state.py:57,72,79,85,91`; `test-worktree-state-hooks.py:82,88,99,121` | bootstrap red + mutants above; **maximal clause unbound** |
| SC-02 | `test-feature-corpus.py:92,96,101,105,113,120,228,234`; `omp-hooks.test.ts:1313` | natural pre-change RED for the absence clause is receipt-only (receipt-T-03.md:94-96: "all three True"); my pre run is bootstrap; mutants `:105`, gates `:110`, regression `:95` red. Guard routes (`:228,:234`) and OMP adapter are declared positive controls (receipt-T-03.md:92, receipt-T-05.md:94) — no fail-first claimed |
| SC-03 | `test-check-state-corpus.py:84,99,105,123,143` | bootstrap red; mutants `:143` red; `:123` open-confinement not mutated (see gaps) |
| SC-04 | `test-check-state-corpus.py:149,158`; `test-feature-corpus-census.py:182,185,199-235`; `test-feature-corpus.py:244` | census: **natural assertion RED** (pre run above); name-set: mutants red; repo-wide readers: `board_lifecycle` **not bound** (see gaps) |
| SC-05 | `test-feature-corpus-discovery.py:29-60`; `test-check-state-corpus.py:111`; `test-feature-corpus.py:139-199` | mutants red incl. sentinel, third claimant, empty reason, INV-52, merge-gate layout; permissionDecision payload asserted |
| SC-06 | `test-corpus-non-regression.py:98,105,118`; full plain-clone runs above | positive control by definition (receipt-T-05.md:95-96); no fail-first possible/claimed |
| SC-07 | `test-worktree-state.py:168-267` | bootstrap red + mutants (C staged/edit/untracked, repair-on-dirty) |
| SC-08 | `test-worktree-state-hooks.py:82-174`; `test-worktree-state-hooks-rules.py:81-176` | natural pre-change RED (receipt-T-04.md:73-83 and my pre run: absent shims, `JSONDecodeError`); unit mutants red (stdin, exit 0). **Integration** hook file stayed green under both post-rewrite mutants (unit binds them) |
| SC-09 | `test-check-state-corpus.py:165,175,183,193`; `test-feature-corpus.py:166,199,251` | mutants red (dirty/structural, layout refusal) |
| SC-12 | `test-corpus-real-owner.py:106,118,135,138,144,189` | real-owner run above (non-skipped, converted caller); equality mutants are in-test (`:138,:144`); not independently mutated by me |
| SC-13 | the six unit files above | per-predicate mutants above; 1 survivor (maximal) |

SC-10: excluded by ruling. SC-11/SC-14: inspection, out of this gate's automated scope (SC-11 endpoints re-derived above).

## Findings / coverage gaps (assessment only; nothing fixed)

- **G-1 (SC-13/SC-01) `derive_cone` maximal-subtree clause unbound.** `feature_corpus.py:475` `maximal = set(under)` leaves unit (`test-worktree-state-rules.py`, DIRS at `:23-31` has no kept `.harness` dir with a kept child) and integration `test-worktree-state.py` green. Owner lane: T-01 (main-session-direct, `tests/unit/test-worktree-state-rules.py`). Bounded to a missing negative case.
- **G-2 (SC-04) `board_lifecycle._feature_dirs` cutover unbound.** `board_lifecycle.py:456,459` — mutants "layout refusal dropped" and "back to local `glob` of the checkout" both leave the **entire unit kind** green and `test-board-lifecycle.py`/`test-check-state-entry.py`/`test-feature-corpus.py`/`test-corpus-real-owner.py` green; the only integration red was the census noticing the new unmarked `glob` (a marker check, not behaviour). The STATUS-finding-on-`CorpusError` branch (`board_lifecycle.py:521-526`) has no test. Lane: T-03.
- **G-3 (SC-02/04) `check-decision-anchors.check_anchor` corpus routing and exit 2 unbound.** `check-decision-anchors.py:141` reverted to local `count_lines(candidate)` leaves `test-check-decision-anchors.py` green; no test references `CorpusError`/"cannot check". Lane: T-03.
- **G-4 (T-03) `check-domain.py:2706` own-checkout sweep skip.** Mutant `if False:` passes `test-check-domain-post.py`/`-worktree.py` in isolation (exit 0); once red in the 8-worker pool (`a write made during the sweep remains visible to the next sweep`) but not reproducible isolated, so **inconclusive** (possible load flake of an existing test or a real double-sweep effect); the `linked_worktrees` parity itself is bound (`test-feature-corpus-gates.py:56`). Lane: T-03.
- **G-5 fail-first quality.** Fail-first evidence outside the receipts is bootstrap-tier for 15 of 19 new/changed files; the receipts are narrative (no retained log). Natural assertion REDs exist only for census, instruction-paths, hooks-rules/integration (absent shims). SC-13's per-predicate "fail-first" therefore rests on my present-state mutants (tier: constructed mutation proof, own reproduction), not on a captured pre-fix failure of that predicate. SC-02's absence-clause red and SC-03/07's mutants are the receipt's word plus my mutants.
- **L-1** receipt file counts 54/86 vs measured 52/80 (above).
- **N-1** `test-corpus-real-owner.py` passes only from a converted caller; a pre-merge validator pin fails the choke-point test with the correct refusal.
- Not independently re-proven: SC-12's in-test mutant arms; census detector logic (lives inside the test file itself, so a production mutant cannot reach it).

## Principles applied

- Verification is the product (rule 7): green suites were not credited as met SCs; each SC was bound to a test and a mutant.
- Never falsify the record (rule 15): bootstrap reds, survivors, an inconclusive arm and the 54/86 discrepancy are recorded as such.
- No more specific than necessary (rule 6): findings are stated as the weakest claim the evidence supports (G-4 inconclusive).

## Cleanup

Pin `FEAT-1559-corpus-outside-worktree--validate-validator--harness-qa` removed on return; `/tmp/f1559-qa-clone-QZwT` (clones + logs) is disposable and not tracked. No source, test or fixture file was edited in any tracked tree; all mutants lived only in the disposable clone and were restored (`git status --porcelain` 0).
