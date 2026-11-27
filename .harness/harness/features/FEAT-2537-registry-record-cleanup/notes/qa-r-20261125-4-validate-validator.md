# QA gate — FEAT-2537 c1 completion, QA-only re-check, run r-20261125-4-validate-validator

**BLUF: PASS. SC-02 is met (literal).** At pin `c67ba818977af535508b3a861b5eeead5bd39410`, every re-check that
`notes/answers-2026-11-25-validate-c1.md` § Constraints requires holds:

- The whole file is green (200/200).
- The base swap reds exactly the 12 ruled case-18 lines, with 0 other reds.
- The default-to-v2 mutant dies on 4 reds.
- The CRLF writer mutant is red on 8 reds. The same mutant is green (200/200) on the prior pin's test file.
- The code diff against 635b5c15 is confined to the one file and to case-18 helpers and state table.
- The four immutables are byte-identical to a24eacee.
- The unit (68/68) and integration (95/95) receipts have 0 defects.

There is no stop-and-rule finding. main's `fix-c1-receipt.md` § c1 completion table matches my independent
measurements row for row.

## Setup
- **Repository:** harness (an unbound feature). The policy blob is `git show c67ba818…:.harness/harness.json`.
  - T-01 `change_type: cross_module` → `always: [unit, integration]`.
  - typecheck (active) is run because the feature-wide diff a24eacee..c67ba818 touches `.omp/extensions/harness-hooks.ts`
    (P-13).
- **Checkout:** created with `pinned-checkout.py add --feature FEAT-2537-registry-record-cleanup --run-id
  r-20261125-4-validate-validator --persona harness-qa --sha c67ba818…`.
  - It resolved to `.claude/worktrees/.pins/FEAT-2537-registry-record-cleanup--r-20261125-4-validate-validator--harness-qa`.
  - HEAD = c67ba818.
  - `worktree-state.py --verify --checkout .` exited 0 ("converged").
  - `bun install --frozen-lockfile` was run.
  - `git status --porcelain` was empty after all runs.
- **Environment:** Python 3.15.2, darwin arm64, not CI. Every run used
  `env -u PYTHONUNBUFFERED -u NO_COLOR -u FORCE_COLOR -u HARNESS_AGENT_TYPE TERM=xterm-256color`.
- **Base:** `git merge-base main HEAD` = `git rev-parse main` = `a24eacee718898c4512379de1fe87b9611a7df43`.

## Per-step results
1. **Whole file green.** From the pin:
   `python3 tests/integration/test-inflight-registry.py` → exit 0, `PASS - 200/200 checks passed`, 0 `^FAIL` lines,
   and 45 `PASS - case18` lines.
2. **Base swap.**
   - **Driver:** `/tmp/feat2537-r4-swap.py`. For each variant it copies the **full pinned bin/** (82 entries) to a
     scratch directory, substitutes only `inflight_registry.py`, and runs `INFLIGHT_REGISTRY_DIR=<scratch> python3
     <pin>/tests/integration/test-inflight-registry.py`.
   - **Base:** `git show a24eacee:.claude/skills/harness/bin/inflight_registry.py`, sha256 `caac8af58a18…`. Result: exit 1,
     `FAIL - 12/200`. All 12 reds are case 18; **other reds: 0**.
     - v1 persona map: strict, writer `((None, 1))`, warns (3).
     - v1 empty map: strict, warns (2).
     - version-less claims envelope: strict (returns `[{claim c1…}]`), writer (returns `({c1…}, 0)`), bytes (writer kept the
       row), warns (4).
     - schema-1 claims envelope: writer, bytes, warns (3).
   - **Controls:** every writer-producible control is green on base: missing, empty, corrupt, non-object and live v2.
   - **One-factor control:** the candidate module in the same scratch layout (sha256 `e0b866a247f2…`) gives exit 0,
     200/200.
3. **Default-to-v2 mutant.** `raw.get("schema_version")` becomes `raw.get("schema_version", SCHEMA_VERSION)`, once each in
   `_parse` and `_known_shape` (each asserted to have exactly 1 site). Result: exit 1, `FAIL - 4/200`.
   - All 4 reds are the version-less envelope: strict, writer return, writer bytes and warns.
   - Other reds: 0. **The mutant dies.**
4. **CRLF writer mutant.** The writer's serialization line (`inflight_registry.py:92`) gets `.replace("\n", "\r\n")` before
   `.encode`. Result: exit 1, `FAIL - 8/200`.
   - The 8 reds are every "locked writer leaves exactly the expected bytes" row that writes: v1 map, v1 empty, version-less,
     schema-1, empty, corrupt, non-object and live v2. Diagnostics show literal `b'{\r\n …'`.
   - Missing-file rows write nothing, so they correctly stay green. Other reds: 0.
   - **P-09 control:** the same mutant against the prior pin's test file (`git show 635b5c15:tests/integration/test-inflight-registry.py`)
     gives **exit 0, 200/200**.
   - So this red is created by the c1-completion edit. It is the witness that case 18 now compares literal file bytes.
   - **Extra probe, silent rows:** a mutant that prints `inflight_registry: stray note` to stderr on entry to `_parse`
     reds `empty file: the writer is silent` and `live v2 claim: the writer is silent` (2/200).
     - The same mutant against the 635b5c15 test file gives 200/200.
     - The missing-file writer never reaches `_parse`, so that silent row is not exercised by this mutant.
5. **Inspection at source** (`tests/integration/test-inflight-registry.py` at c67ba818):
   - `:481-482` are `_ABSENT = object()` and `_UNREADABLE = object()`: module-level, distinct, compared by identity through
     `==`.
   - `:485-487`: `_canonical` returns `(json.dumps(...)+"\n").encode("utf-8")`, which is bytes.
   - `:496-497`: fixtures are written `"wb"` with `text.encode("utf-8")`. This is the write side of the same helper and stays
     within "case-18 helpers".
   - `:501-505`: `_file_bytes` opens `"rb"` and returns `bytes`; a missing file returns `_ABSENT`.
   - `:520-534` (state table):
     - `refused()` expects `text.encode("utf-8")` after the strict read and `folded` (bytes) after the writer.
     - The controls expect `b""`, `b"{"`, `b"[]"`, `json.dumps(live_v2).encode("utf-8")` and `_canonical(live_v2)`.
     - Missing rows expect `_ABSENT`.
     - No `json.loads` and no `.decode` comparison remains in `:481-574`.
   - `:557-562`:
     - Rows with `warns` assert `"treating as empty" in err`.
     - Silent rows assert `err == ""`.
6. **Scope.** `git diff --stat 635b5c158c00047bab2998dd3349e524bc12d0b7..c67ba818977af535508b3a861b5eeead5bd39410 -- .
   ':!.harness'` shows `tests/integration/test-inflight-registry.py | 33 +++---` and `1 file changed, 18 insertions(+), 15
   deletions(-)`.
   - The hunks are `@@ -481,2`, `-487`, `-496,2`, `-504`, `-521`, `-530,5` and `-557,3`. They cover sentinels, `_canonical`,
     `_registry_case_root`, `_file_bytes`, `_registry_states` and `_check_locked_write`.
   - `case_18_v1_registry_fails_closed` itself and every other case are untouched.
   - The whole-range stat adds only feature-directory records under `.harness/harness/features/FEAT-2537…/`.
   - `inflight_registry.py` has **zero diff**.
7. **Immutables.** `git diff --quiet a24eacee718898c4512379de1fe87b9611a7df43 c67ba818977af535508b3a861b5eeead5bd39410 --
   <4 paths>` → exit 0. Blob ids are equal at both SHAs:
   - `tests/integration/fixtures/prior-validate-digest.py.fixture` `727295e5`
   - `tests/integration/test-validate-digest.py` `237ab46b`
   - `tests/integration/canonical-reader-classification.json` `a229bb10`
   - `.claude/skills/harness/bin/validate-digest.py` `5b1b5934`
8. **Regression floor (DEC-255 runner).** From the pin, with
   `HARNESS_PROJECT_DIR=<pin>` and the stripped environment above:
   `python3 <pin>/.claude/skills/harness/bin/run-unit-tests.py --kind <k> --shard 1/1 --manifest <TREE>/.harness/harness/features/FEAT-2537-registry-record-cleanup/runs/r-20261125-4-validate-validator/qa/manifest-<k>.json`

   | Kind | Exit | Pool | Receipt sha256 | Receipt |
   |---|---|---|---|---|
   | unit | 0 | `8 workers, 68 files, 30.62s wall` | `3384d6d1…d845` | tested_commit c67ba818, runner_exit 0, 68/68 |
   | integration | 0 | `8 workers, 95 files, 196.68s wall` | `3eaa49e5…de83` | tested_commit c67ba818, runner_exit 0, 95/95; `PASS test-inflight-registry.py` |
   | typecheck | 0 | `bun run typecheck` | — | — |

   - `discover_expected` plus `evidence_defects`, in validate-digest.py:2807's call shape at basis c67ba818, report:
     unit expected 68 with 0 defects, and integration expected 95 with 0 defects.
   - The unit log has 4 bare `FAIL  BUG-1290 5a/5b/5c` lines. These are test-factory-claim-mutation.py's deliberate proof
     output (repo G-09), and the runner exited 0. The integration log has 0 `^FAIL` lines.

## SC status
- **SC-02: met (literal).**
  - Both directions hold: step 2 shows base reds in the ruled direction with controls green, and step 1 shows the
    candidate all green.
  - Full returns and raise or no raise are asserted against distinct `object()` sentinels.
  - "The file bytes after the call" is now literal: `rb` against encoded expectations, witnessed by step 4's CRLF
    mutant, which is red at c67ba818 and green at 635b5c15.
- **SC-01:** unchanged by this commit.
  - At c67ba818, `git grep live_children c67ba818 -- .claude/skills/harness/bin .omp/extensions` exits 1.
  - The positive control `git grep parent_agent_id=agent_id` over validate-digest.py matches (exit 0).
  - Cases 25 and 29 pass (8 PASS lines in the step-1 log).
  - Fail-first is carried from `notes/qa-r-20261125-2-validate-validator.md`.
- **SC-03 and SC-04:** `verify: inspection`, carried forward per the ruling.

## Fail-first
- **SC-02:** step 2's 12 base-swap reds. These are natural reds: the a24eacee module under the pinned tests, with the
  candidate control green in the same layout.
  - Steps 3 and 4 are mutation-tier supporting evidence: v2-default gives 4 reds, CRLF gives 8 reds, and the CRLF red is
    absent on 635b5c15.
- **SC-01:** carried from the r-2 note § Fail-first. Case 25, case 29 and the grep are unchanged since then.

## Principles applied
- **Build the Lever:** one driver (`/tmp/feat2537-r4-swap.py`) builds full-bin scratch trees for 5 module variants
  (candidate, base, v2-default, CRLF and stderr-noise) and replays CRLF and noise against the prior pin's test file.
  This replaced reading-based claims with measured reds and their one-factor controls.

Ephemeral logs (the excerpts above are the durable record):
- `/tmp/feat2537-r4-{step1,unit,integration,typecheck}.log`
- `/tmp/feat2537-r4-swap-{cand,base,v2,crlf,noise}.log`
- `/tmp/feat2537-r4-swap-{cand,crlf,noise}-prior.log`
