# QA gate — FEAT-1559 cycle 4 (run validate-c3-validator, pin 35587d8dfbf9178e21410c201601f7137fbfbbd6)

**BLUF: PASS.** Both required kinds are green at the exact SHA in an ordinary full non-linked clone (unit exit 0, 52 files; integration exit 0, 80 files). All seven c3 regression tests exist and are red against `6c11ab62` production (I reproduced each), green at the pin. No source, test or fixture was edited. Only my own evidence has examined the seven delta fixes in this gate; the code-reviewer and security lanes are separate.

## Phase 1 (BRIEF + plan only)
Expected for the seven c3 fixes: sparse-worktree factory_claim reads landed plan+issue map; raw no-filter hash and file-type mismatch → C; symlink (mode 120000) unchanged → B, retargeted → C; non-ASCII cone converges; rebase/bisect detached branch fallback; missing active dir stays local-missing; ordinary dirty work draws no hook instruction. Gaps vs Phase 1 (no test): see coverage_gaps.

## Subject
Pin created (`pinned-checkout.py add --persona harness-qa-c4`) and removed. Suites ran in `/tmp/qa1559c4/clone`: `git clone --no-hardlinks --no-checkout` + `update-ref --no-deref HEAD` + `restore --source=HEAD --staged --worktree .` (the guard denies `checkout`/`switch`). cwd=clone, toplevel `/private/tmp/qa1559c4/clone`, HEAD 35587d8d…, detached, git-dir `.git` = common-dir (non-linked, class plain clone), shallow false, 5264 tracked files, status 0. Matrix: T-01..T-05 `cross_module` ⇒ unit+integration always; T-06 `docs` abandoned (SC-10 deferred by operator to #2101).

## Required kinds
| Kind | Command (env -u HARNESS_AGENT_TYPE) | Exit | Wall | Discovered | State |
|---|---|---|---|---|---|
| unit | `python3 .agents/skills/harness/bin/run-unit-tests.py --kind unit` | 0 | 14.78 s | 52 files ("pool: 8 workers, 52 files"); 767 PASS lines | satisfied |
| integration | `python3 .agents/skills/harness/bin/run-unit-tests.py --kind integration` | 0 | 91.04 s | 80 files; 2341 PASS lines | satisfied |

Counts equal c3 (52/80). All 12 feature files appear as run scripts (integration: feature-corpus, worktree-state, worktree-state-hooks, feature-corpus-census, corpus-real-owner, check-state-corpus, corpus-non-regression; unit: worktree-state-rules, worktree-state-hooks-rules, feature-corpus-discovery, feature-corpus-gates, corpus-regression, check-state-corpus-rules); `omp-hooks.test.ts` runs via `test-omp-hooks.py` (exit 0). Only `FAIL`-shaped token class is the known `test-factory-claim-mutation.py` BUG-1290 mutation proof (repo G-09); no `^FAIL`/ERROR outside it.
**Skips (honest):** `test-corpus-real-owner.py` ran 4 of 6, 2 `SKIP (host prerequisite missing): clone is the owner itself, so there is no active-worktree caller to compare` (the active-worktree-caller equality for SC-12 is therefore NOT executed here); one `SKIP no conversion manifest` (T-06/SC-10 deferred #2101). A non-skipped SC-12 caller run needs a converted worktree (post-merge, #2101). The plain-owner half (names==disk, >70 floor, mutant/wrong-root arms) ran green here.

## Seven c3 fixes — red against 6c11ab62 (own reproduction)
Disposable clone at `6c11ab62` production; test files restored from pin via `git restore --source=<pin>` (tests only). Results:
| # | Test (pin line) | Old-code outcome | Pin |
|---|---|---|---|
| 1 | `test-feature-corpus.py:360` `FactoryClaim.test_a_landed_plan_and_issue_map_are_read_from_a_sparse_worktree` | FAIL `('no_plan', …)` vs `['None','77']` | green |
| 2 | `test-worktree-state.py:279` `test_bytes_a_clean_filter_hides_are_class_c` | FAIL `3 != 8` (bytes deemed B/removed path) | green |
| 3 | `:292` `test_an_unchanged_tracked_symlink_is_class_b` | FAIL `8 != 0` (dirty C) | green; `:301` retarget-C is a positive control, passes on old, not claimed red |
| 4 | `:91` `test_a_non_ascii_top_level_directory_converges_and_verifies` | FAIL `3 != 0` cone missing ['space ü 文'] unexpected quoted | green |
| 5 | `:111` `test_a_branch_named_worktree_keeps_its_feature_mid_rebase` | FAIL `('probe', None) != ('planning-worktree','FEAT-1-alpha')` | green |
| 6 | `test-feature-corpus.py:120` `test_a_missing_active_directory_is_missing_not_a_landed_copy` | FAIL owner path returned instead of local | green |
| 7 | `test-worktree-state-hooks.py:184` `test_ordinary_work_in_a_converged_worktree_draws_no_instruction` | FAIL `(0, 'worktree-state: repair …')` != `(0,'')` | green |
Totals on old code: test-feature-corpus 2 failures (of 30), test-worktree-state 4 failures (of 28), test-worktree-state-hooks 1 failure (of 9), test-worktree-state-hooks-rules.py (modified argv assertion) 12 OK on old code (it is a relaxed assertion, not a red claim). Tier: natural RED against retained prior production, test bytes as at pin. Raw logs not retained beyond this note (clone removed per cleanup); commands above reproduce.

## Per-SC fail-first (carried tiers + this cycle)
Tiers for SC-01..SC-13 are those of `review-harness-qa-c1.md`, `-c2.md`, `-c3.md` (natural RED where they exist: census, hooks/shims, instruction-paths, check-plan-routes, shared-id population, and now the seven above; otherwise bootstrap reds and constructed present-state mutants). I did not retake c1 SC-13 predicate mutants (production for those predicates unchanged by the c3 delta except as listed). SC-06 is a positive control (no red possible). SC-11/SC-14 inspection; SC-10 deferred.

## Extra probes for peers (source/probe distinction)
Run in disposable repos, not committed tests:
- **Directory names:** `git sparse-checkout set --cone --stdin` then `list` + `unquote` round-trips `a\b`, `x"y`, `sp ü` correctly. A directory whose name BEGINS with `"` makes `set --stdin` exit 128 (`unable to unquote C-style string`); worktree-state `_sparse` raises on nonzero, so repair fails closed with a named git error — advisory edge, no test, not claimed met.
- **Detached-start rebase:** `current_branch` returns the literal string `detached HEAD` (git writes it to `rebase-merge/head-name` when the rebase starts from a detached HEAD) instead of None. `identity()` → `_branch_id('detached HEAD')` is None, so identity is unchanged: docstring inaccuracy, benign (advisory/info).
- **Source-only closure (no executed test):** `rebase-apply/head-name` and `BISECT_START` branches of `_IN_PROGRESS_BRANCH` (only rebase-merge exercised by the test); regular↔symlink type mismatch in `present_blobs` (`worktree-state.py:181` returns None → C; no fixture); non-UTF8 symlink target (`os.fsencode(os.readlink)`); post-merge hook quiet path (test drives post-checkout and post-rewrite only; post-merge uses an identical `--quiet-dirty` + `-n "$_out"` pattern, read at `hooks/post-merge:41-46`); dirty+structural hooks still print (`post-checkout:41-47`, not tested).
- Hooks: dirty-only returns rc 8 with empty output → silent; `--quiet-dirty` leaves the exit code (`worktree-state.py:390`), per SC-07.

## Residual limits (assessed, not closed)
- SC-13 historical pre-production capture: bootstrap/mutant tier for most unit predicates (c1 G-5), bounded.
- c1 G-1 `_maximal_outside_features` kept-ancestor clause mutant survives (advisory negative-case gap); G-4 `check-domain` `if False:` inconclusive — neither retaken.
- SC-12 active-worktree-caller comparison skipped here (owner is the clone); needs converted caller (#2101).

## Principles applied
- Verification is the product (rule 7): red states reproduced on old production, not credited from the c3 receipt.
- Never falsify the record (rule 15): 2 real-owner skips, the skipped manifest and the uncovered source-only branches are listed as such.
- No more specific than necessary (rule 6): the `detached HEAD`/leading-quote probes are recorded as advisory.

## Cleanup
Pin `FEAT-1559-corpus-outside-worktree--validate-c3-validator--harness-qa-c4` removed via `pinned-checkout.py remove`; `/tmp/qa1559c4` (suite clone, old-code clone, probe repos, logs) removed; `.pins` and `git worktree list` hold no `qa-c4` entry.

## Addendum — bounded falsification evidence (same run validate-c3-validator, pin 35587d8d; persona harness-qa-c4b)

**BLUF: PASS retained; the three reader-flagged unexecuted probes (bisect/rebase-apply identity, quiet-dirty hook ordering, SC-12 caller) now ran at the exact SHA; no source/test/fixture edited, no suite rerun.** Subject: managed pin `FEAT-1559-corpus-outside-worktree--validate-c3-validator--harness-qa-c4b` (HEAD 35587d8d…, `git diff` of `bin/` vs pin empty). Probe drivers were ephemeral `python3 -` stdin scripts that import the committed `tests/integration/f58_sparse_fixture.py` (`sparse_fixture`, `add_worktree`, `add_pin`, `install_hooks`, `commit_owner`) and call the pinned `worktree-state.py` CLI; the guard did not refuse them for QA. Fixture owners live in `tempfile.mkdtemp` and are removed by the fixture context.

### 1. Detached operation identity (every row: CLI `--verify --json`, real git state)
| Subject | Real git state observed | Identity result |
|---|---|---|
| dir `scratch`, branch `feat/FEAT-1-alpha`, `git bisect start HEAD HEAD~2` | HEAD detached (`symbolic-ref` rc 1), `BISECT_START=feat/FEAT-1-alpha` | planning-worktree, `FEAT-1-alpha`, findings [] — same as before bisect |
| dir `FEAT-1-alpha`, **conflicting** branch `feat/FEAT-2-beta`, bisect | detached, `BISECT_START=feat/FEAT-2-beta` | refused (active None; cone finding "directory names FEAT-1-alpha but branch feat/FEAT-2-beta names FEAT-2-beta; … ambiguous") — identical to the attached pre-bisect result: bisect neither creates nor hides the conflict |
| dir `FEAT-2-beta`, non-feature branch `work`, bisect | detached, `BISECT_START=work` | `FEAT-2-beta` (directory), findings [] — unchanged by bisect |
| fixture pin `FEAT-2-beta--run1--qa`, HEAD symbolically attached to `feat/FEAT-1-alpha` then bisect | detached, `BISECT_START=feat/FEAT-1-alpha` | class pin, `FEAT-2-beta`, [] — pin identity ignores BISECT_START (same as baseline) |
| **exact managed pin** (`git bisect start --no-checkout HEAD HEAD~3`, tree untouched) | HEAD 35587d8d detached, `BISECT_START=35587d8d…` (a SHA) | class pin, `FEAT-1559-corpus-outside-worktree`, [] — identical before/during/after; `bisect reset` restored HEAD, status clean |
| dir `scratch4`, branch `feat/FEAT-1-alpha`, **`git rebase --apply main` conflict** | `rebase-apply/` exists, `rebase-merge/` absent, `head-name=refs/heads/feat/FEAT-1-alpha`, detached | planning-worktree, `FEAT-1-alpha` (finding: dirty only) — the rebase-apply arm of `_IN_PROGRESS_BRANCH` is now executed |
| dir `FEAT-1-alpha`, branch `wip`, `rebase --exec false` (rebase-merge) and `rebase --apply` conflict | detached, head-name `refs/heads/wip` | `FEAT-1-alpha` by directory in both (dirty only for apply) |
| dir `FEAT-2-beta`, branch `feat/FEAT-1-alpha`, mid `rebase --exec false` | rebase-merge head-name `refs/heads/feat/FEAT-1-alpha` | refused ambiguous, same as attached; in-process `current_branch` returned `feat/FEAT-1-alpha` |

Self-inflicted false alarm, recorded not hidden: one run appeared to show the conflicting rebase NOT refused (identity `FEAT-2-beta`) while a plain `git bisect start` was active in the managed pin; that bisect had moved the pin's working tree to a pre-fix midpoint, so the CLI run executed OLD `feature_corpus.py` (`AttributeError: no attribute _in_progress_branch` confirmed). A probe-setup artefact; the `--no-checkout` bisect above keeps the pinned bytes. After `bisect reset` HEAD is 35587d8d and status is clean.

### 2. Quiet dirty vs structural, through `install_hooks` (post-checkout, post-rewrite, post-merge; worktree `FEAT-1-alpha`, hooks copied from the pin)
- Dirty only (README + an active-feature note edited; `--verify` exit 8, findings `['dirty']`): all three hooks rc 0 with **empty stderr** (post-merge stdout shows only the unrelated `post-merge-sweep: resolved repository root` line). A real `git merge --no-edit main` with the same dirty tree: rc 0; stderr carries only `post-merge-sweep:` lines, no `worktree-state:`/"layout repair" text — post-merge quiet path executed, not source-read.
- Dirty + structural (untracked file in hidden `FEAT-2-beta`; `--verify` exit 8, findings `['dirty','materialisation']`): post-checkout, post-rewrite and post-merge each rc 0 and print `worktree-state: repair … — planning-worktree, FEAT-1-alpha in harness / dirty (8): 2 path(s) carry work that repair must not touch / .harness/harness/features/FEAT-2-beta/stray.m…` on stderr; a real `git merge` in that state prints the same. `--quiet-dirty` therefore suppresses only all-dirty reports (`worktree-state.py:390`).

### 3. SC-12 current exact-SHA active-caller run (no standing worktree converted)
Unrepaired managed pin: `python3 tests/integration/test-corpus-real-owner.py -v` → 1 FAIL `test_check_state_passes_the_corpus_choke_point` with the designed `LAYOUT cone (3) … skip-bits (4) … no invariant ran` (unconverted caller; c1 N-1) — recorded, not a code defect. Repair of the DISPOSABLE pin by pinned code: `python3 .claude/skills/harness/bin/worktree-state.py --repair --checkout <pin>` rc 0, "sparse cone re-applied", converged; `--verify` converged; status 0. Rerun: **`Ran 6 tests … OK`, 0 skips** (caller = the pin; test's own probe pin `BUG-1016…--f1559-73652--probe` at owner HEAD 3067d30c created and removed by the test). The two active-caller checks that SKIPped in the ordinary clone are therefore met at the exact SHA; SC-12 does not wait for #2101 once a disposable converted caller of the pinned code exists. The conversion-manifest check (SC-10/T-06) is a different test and stays deferred.

### 4. Per-SC fail-first (tier, test, evidence; originals not rewritten)
Evidence base: `review-harness-qa-c1.md` (§Automated SC → test evidence and fail-first; mutant table), `-c2.md`, `-c3.md`, this note lines 20-31 (seven c3 reds), `receipt-T-03/04/05.md`.
| SC | Test (pin) | Evidence | Tier |
|---|---|---|---|
| SC-01 | `test-worktree-state.py:91`, `:111`; `test-worktree-state-hooks.py` Creation | this note:27-28; c1 mutants `test-worktree-state-rules.py:38,112,117,123,86` | natural RED (two c3 fixes); bootstrap + constructed mutants otherwise; `maximal` clause mutant survives (c1 G-1) |
| SC-02 | `test-feature-corpus.py:92-120,228,234`; `omp-hooks.test.ts:1313` | this note:29; c1 mutants `:105`, gates `:110`, regression `:95`; `receipt-T-03.md:92-96` | natural RED for `:120`; mutants; guard routes are positive controls (no red claimed) |
| SC-03 | `test-check-state-corpus.py:84,99,105,123,143` | c1 bootstrap red; mutant `:143` | bootstrap + mutant; `:123` unmutated |
| SC-04 | `test-check-state-corpus.py:149,158`; `test-feature-corpus-census.py:182-235`; `test-feature-corpus.py:244,360` | census natural RED (c1); this note:24; c2 closure 1 (plan-routes) natural RED; board/anchors mutants (c2) | natural RED (census, factory claim, plan-routes); mutants otherwise |
| SC-05 | `test-feature-corpus-discovery.py:29-60`; `test-check-state-corpus.py:111`; `test-feature-corpus.py:139-199` incl. SegmentIdentity | c1 mutants (`:35,:46,:54,:111,:166`); `review-harness-qa-c3.md:29-37` | natural RED vs 42856abb for shared-id (3 FAIL + 1 ERROR); mutants otherwise |
| SC-06 | `test-corpus-non-regression.py:98,105,118` + plain-clone runs (this note:14-15) | `receipt-T-05.md:95-96` | positive control; no red exists or is claimed |
| SC-07 | `test-worktree-state.py:168-267,279,292` (`:301` retarget = positive control) | this note:25-26 (`3 != 8`, `8 != 0`); c1 mutants `:228,222,241,246,255` | natural RED (filter, unchanged symlink); mutants otherwise |
| SC-08 | `test-worktree-state-hooks.py:82-195`; `test-worktree-state-hooks-rules.py:81-176` | c1 absent-shim RED; this note:30; c1 mutants `:99,120,129`; `receipt-T-04.md:73-83` | natural RED (absent shim; quiet ordinary work); mutants; hooks-rules argv change is a relaxed assertion, not claimed red |
| SC-09 | `test-check-state-corpus.py:165,175,183,193`; `test-feature-corpus.py:166,199,251` | c1 mutants; §2 here (mixed dirty+structural through hooks) | mutant; no historical natural RED |
| SC-12 | `test-corpus-real-owner.py:106,118,135,138,144,189` | §3 here; c1 non-skipped run (HEAD 33d10434) | positive control at exact SHA; in-test equality mutants not independently mutated; no historical red claimed |
| SC-13 | six unit files (worktree-state-rules, feature-corpus-discovery, feature-corpus-gates, check-state-corpus-rules, corpus-regression, worktree-state-hooks-rules) | c1 mutant table (file:line); c2/c3 notes | constructed mutants (own reproduction, c1 pin), NOT a natural pre-production RED; not retaken here |

### Open / limits
- No unreachable capability in this addendum; the Python-open refusal that blocked reviewers did not apply to QA's authorized fixture drivers.
- Real-filesystem regular→symlink mismatch and non-UTF8 link cases remain security c4's (`security-c4:18-19`), not mine. Leading-`"` cone name (Q-C4-01) unchanged advisory.
- Retained: SC-08 literal merge skip-bit repro (git 2.54 cannot produce it, `receipt-T-04.md`), SC-13 per-predicate historical red gap, G-1/G-4.

### Cleanup (addendum)
Fixture owners removed by `sparse_fixture()`; pin bisect state reset (HEAD 35587d8d, status 0). Pin `…--harness-qa-c4b` removed via `pinned-checkout.py remove`.
