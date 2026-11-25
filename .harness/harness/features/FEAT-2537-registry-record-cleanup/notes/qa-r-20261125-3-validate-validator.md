# QA gate — FEAT-2537 fix c1, targeted re-validate, run r-20261125-3-validate-validator

**BLUF: PASS.** At pin `635b5c158c00047bab2998dd3349e524bc12d0b7`, case 18 asserts what the c0 ruling asks for: file
contents, full returns, and both new inputs. The base swap reds exactly the 12 ruled case-18 lines. The default-to-v2
mutant now dies on 4 lines. The code diff is confined to the two ruled files, and the module diff is docstring-only.
The immutables are byte-identical. T-01 verify exits 0 verbatim. unit (68/68) and integration (95/95) receipts are clean.

**There is no stop-and-rule finding.** One low adequacy note (F-1): the file comparison reads in text mode, so it is not
literally raw bytes.

## Setup
- **Repo:** harness (an unbound feature). Policy blob: `git show 635b5c15…:.harness/harness.json`.
  - T-01 `change_type: cross_module` → `always: [unit, integration]`.
  - typecheck (active) is warranted by the feature-wide `.ts` edit, per P-13.
- **Checkout:** `pinned-checkout.py add … --sha 635b5c15…` created `.claude/worktrees/.pins/FEAT-2537…--r-20261125-3-validate-validator--harness-qa`.
  - HEAD = 635b5c15.
  - `worktree-state.py --verify` exited 0 ("converged").
  - `bun install --frozen-lockfile` was run.
  - `git status --porcelain` was empty after all runs.
- **Environment:** Python 3.15.2, darwin arm64, **not CI**. Every run used
  `env -u PYTHONUNBUFFERED -u NO_COLOR -u FORCE_COLOR -u HARNESS_AGENT_TYPE TERM=xterm-256color`.
- **main:** `main` = `git merge-base main HEAD` = `a24eacee718898c4512379de1fe87b9611a7df43`, so main has not moved.

## Per-step results
1. **Whole file green at the pin.** `python3 tests/integration/test-inflight-registry.py` → exit 0,
   `PASS - 200/200 checks passed`, 0 `^FAIL` lines.
2. **Base swap.** Scratch `/tmp/feat2537-r3-base` is a **full copy of the pinned bin/** with `inflight_registry.py` replaced
   by `git show a24eacee:…` (sha256 `caac8af5…747b`). Command:
   `INFLIGHT_REGISTRY_DIR=/tmp/feat2537-r3-base python3 <pin>/tests/integration/test-inflight-registry.py` → **exit 1, 12/200**.
   - **All 12 are case 18, in the ruled direction:**
     - v1 persona map: strict, writer `(None, 1)`, warns.
     - v1 empty map: strict, warns.
     - version-less claims envelope: strict (base returns `[{claim c1…}]`), writer (base returns `({c1…}, 0)`), bytes, warns.
     - schema-1 claims envelope: writer (base returns `({c1…}, 0)`), bytes, warns.
       - Its strict read is green on base, because base already refused sv1.
   - **Every writer-producible control is green on base,** across all 6 assertions each: missing, empty, corrupt `{`,
     non-object `[]`, live v2.
   - **Swap-harness artifact: none occurred.** CLI cases 7, 9, 35, 40, 41 and feat65 are **green** in my swap.
     - fix-c1-receipt.md's CLI reds came from a partial bin/ copy (missing sibling imports), not from the module.
     - So the receipt's classification of them as an artifact is confirmed: zero reds are an artifact, 12 are real.
   - **One-factor control:** the same scratch layout holding the unmodified candidate module (`/tmp/feat2537-r3-cand`)
     → exit 0, 200/200.
3. **Default-to-v2 mutant.** `/tmp/feat2537-r3-mut` replaces `raw.get("schema_version") == SCHEMA_VERSION` with
   `raw.get("schema_version", SCHEMA_VERSION) == SCHEMA_VERSION` at both sites, in `_parse` and `_known_shape` → **exit 1,
   4/200**:
   - version-less claims envelope: strict read, writer return, writer bytes, warns.
   - At the prior pin this mutant survived at 183/183. It is now killed.
4. **Case 18 content** (`tests/integration/test-inflight-registry.py:497-570`).
   - **(a) File contents.**
     - `_file_bytes` (`:501`) returns the file text or `<absent>`.
     - `_canonical` gives `json.dumps(obj, indent=2, sort_keys=True)+"\n"`, so folded states expect
       `_canonical({"schema_version":2,"claims":[]})`.
     - Untouched states expect the original text, and strict reads assert "leaves the file bytes as found".
     - A missing file expects `<absent>` both after the strict read and after the writer.
     - There is no `json.loads` in `:481-571`. `_file_after`, `_strict_outcome`, `_writer_outcome` and `_EMPTY_V2` are
       gone (grep returns no hits).
     - Probe: a mutant that drops the trailing `\n` from the writer serialization reds 8 "leaves exactly the expected
       bytes" lines. That covers all 4 folded non-v2 inputs, plus the empty, corrupt, non-object and live-v2 controls.
     - Caveat: see F-1.
   - **(b) Full returns.**
     - The strict read compares the whole outcome: `[live]` for the full dict, or `UnreadableRegistry`.
     - The writer compares the full `live_claim` tuple: `(live, 0)` or `(None, 0)`.
     - The base-swap reds show full dicts in their diagnostics.
   - **(c) New inputs.**
     - `:527` is `{"claims":[live]}` and `:528` is `{"schema_version":1,"claims":[live]}`. Both go through `refused()`,
       which expects strict `UnreadableRegistry`, the text unchanged after the strict read, writer `(None, 0)`, canonical
       empty v2 bytes, and `warns=True`.
     - The warning check is `warned is warns`, so it binds both presence and absence. The empty file and live v2 expect no
       warning; corrupt and non-object expect one.
   - **Mutation probes:**
     - **Row-keeping writer** (`/tmp/feat2537-r3-keeprows`: `_parse` accepts any envelope whose `claims` is a list) → exit
       1, 6/200. It reds writer return, bytes and warns for **both** schema-1 and version-less; strict stays green, as
       expected.
     - **Silent fold** (the non-v2 warning `print` removed) → exit 1, 4/200. It reds the warns line for all 4 non-v2 inputs.
5. **Immutables.** `git diff --quiet a24eacee 635b5c15 -- <4 files>` exits 0. The blob ids are identical at both SHAs:
   - fixture `727295e5`
   - test-validate-digest.py `237ab46b`
   - canonical-reader-classification.json `a229bb10`
   - validate-digest.py `5b1b5934`
6. **Scope.**
   - `git diff --stat 8ae96bea…635b5c15`: outside the feature directory, only `inflight_registry.py` (3 +-) and
     `test-inflight-registry.py` (132 +-) change.
   - The other 17 paths are all under `.harness/harness/features/FEAT-2537-registry-record-cleanup/`, from commits
     2a0904e8 and 7d986b71 (station and ruling records) plus fix-c1-receipt.md.
   - `git diff -U0 … -- inflight_registry.py` is a single hunk, `@@ -6 +6,2 @@`. It changes docstring lines 6-7 (inside the
     `"""` at `:2-8`) and **zero executable lines**.
   - The test diff hunks start at `:478` and `:492`; they cover helpers plus case 18 only, ending before `case_19`.
7. **T-01 verify.**
   - The block was extracted from the pinned plan.yaml and confirmed byte-equal to the dispatch text
     (`verbatim_match True`).
   - Run from the pin root with `bash` → **VERIFY_EXIT=0**, with the test printing 200/200.
   - The explicit diff against a24eacee is covered by step 5.
8. **Regression floor (DEC-255 runner).** Command:
   `python3 <pin>/.claude/skills/harness/bin/run-unit-tests.py --kind <k> --shard 1/1 --manifest <run>/qa/manifest-<k>.json`
   with `HARNESS_PROJECT_DIR=<pin>`.

   | Kind | Exit | Pool summary | Receipt sha256 | Receipt fields |
   |---|---|---|---|---|
   | unit | 0 | `8 workers, 68 files, 27.23s` | `540b60c5…1738` | tested_commit 635b5c15, runner_exit 0, 68/68 |
   | integration | 0 | `8 workers, 95 files, 181.85s` | `3db7b787…2bff` | tested_commit 635b5c15, runner_exit 0, 95/95 |
   | typecheck | 0 | `tsc --noEmit -p tsconfig.json` | — | — |

   - `discover_expected` + `evidence_defects`, using validate-digest.py:2807's call shape, report **0 defects** for both
     receipts.
   - The unit log has 4 bare `FAIL  BUG-1290 5a/5b/5c` lines, all from test-factory-claim-mutation.py's deliberate
     proof output (repo G-09). The runner exited 0.

## Findings
- **F-1 (adequacy, low, T-01 case 18): file contents are compared as decoded text, not literal bytes.**
  - `_file_bytes` (`:504`) opens with `"r", encoding="utf-8"`, which applies universal-newline translation.
  - **Probe:** a writer emitting `\r\n` line endings (`/tmp/feat2537-r3-crlf`) **passes 200/200**.
  - The intent is met: there is no decoded-JSON comparison, and serialization, key order, indent and trailing newline
    are all pinned.
  - The literal wording of the ruling and SC-02 ("raw bytes") is not met for line endings.
  - The fix is `open(path, "rb")` against `.encode()` expectations.
  - Raised as a non-blocking question per O-04. I am not ruling it satisfied on my own reading. It is not a behaviour
    change, and no writer emits CRLF (it writes in `wb` mode).
- **No stop-and-rule finding.** No diff outside the two files plus the feature directory, and no executable-line change
  in `inflight_registry.py`.

## Fail-first
- **SC-02:** step 2's 12 base-swap red lines above. This is a natural red: the a24eacee module under the new tests, with
  the same-layout candidate control green.
  - The 4 lines for the new version-less input and the 6 for the schema-1 writer are the semantic reds for the c1
    additions.
  - Step 3's mutant reds are supporting evidence.
- **SC-01:** carried from `notes/qa-r-20261125-2-validate-validator.md` § Fail-first, since case 25/29 and the grep are
  unchanged by c1. At this pin, the verify block's `git grep live_children` still exits 1.

## Principles applied
- **Build the Lever:** one scripted loop ran 7 scratch modules (base, candidate control and 5 mutants) through the pinned
  test file. It replaced reading-based claims for (a), (b) and (c), and it surfaced F-1's surviving CRLF mutant.

Ephemeral logs (the excerpts above are the durable record):
- `/tmp/feat2537-r3-{step1,unit,integration,typecheck}.log`
- `/tmp/feat2537-r3-swap-{base,cand,mut,keeprows,silent,noncanon,crlf}.log`
