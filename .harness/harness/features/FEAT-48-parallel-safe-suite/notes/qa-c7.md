# QA gate — FEAT-48-parallel-safe-suite — validate c7

```
matrix_ok: true
change_type: bugfix(T-01,T-02) + logic(T-03) + cross_module(T-04,T-06) + docs(T-05)
required_kinds: unit, integration        # union across the diff's tasks
kinds:
  - kind: unit
    state: satisfied
    file_level_pass: 34   fail: 0   mutated: 0
    exit: 0
    pool_line: "pool: 8 workers, 33 files, 13.72s wall"
    file_level_pass: 24   fail: 0   mutated: 0
  - kind: integration
    state: satisfied
    file_level_pass: 35   fail: 0   mutated: 0
    exit: 0
    pool_line: "pool: 8 workers, 30 files, 44.41s wall"
    file_level_pass: 45   fail: 0   mutated: 0
  - kind: component
    state: skipped
    reason: "BRIEF `## Verification gaps`: cmd: null, none of component/ui/eval/typecheck detects any surface this feature touches (bash and Python gate scripts under .claude/skills/harness/bin/, covered by unit and integration, both of which have runners)"
  - kind: ui
    state: skipped
    reason: "same BRIEF quote as component"
  - kind: eval
    state: skipped
    reason: "same BRIEF quote; also change_type never resolves to ai_behavior here"
  - kind: typecheck
    state: skipped
    reason: "same BRIEF quote; not in the matrix for any change_type present in this diff"
```

## Change-type derivation

Union across the six tasks that actually touch code (T-05 is docs, contributes nothing):
- T-01, T-02: `change_type: bugfix` → matrix row `"bugfix": {"always": ["unit"], "when": [{"kind": "__bug_class__", "if": "match_bug_class"}]}`. The `when` predicate is a placeholder bug-class match that does not resolve for this diff (no bug-class taxonomy entry applies) — floor is `unit`.
- T-03: `change_type: logic` → `"logic": {"always": ["unit"]}`.
- T-04, T-06: `change_type: cross_module` → `"cross_module": {"always": ["unit", "integration"]}`.
- T-05: `change_type: docs` → `"docs": {"always": []}`.
Union floor: **unit + integration**. Both are `status: active` in `.harness/harness.json` with real `cmd`s, both run above, both green. `component`/`ui`/`eval`/`typecheck` all carry `cmd: null` and are quoted in the BRIEF's own `## Verification gaps` as detecting nothing this feature touches — soft skip, not BLOCKED, since the BRIEF states the reason and it checks out against `test_kinds.detect` (no glob here matches `.claude/skills/harness/bin/**`).

## Kind-by-kind detail

**Unit** (`--kind unit`, both runs invoked with `env -u HARNESS_AGENT_TYPE` per the dispatch's flake note; `HARNESS_AGENT_TYPE` was unset for the child in both runs): exit 0. `pool: 8 workers, 33 files, 13.72s wall`. Zero `FAIL` lines, zero `MUTATED` lines. `test-suite-independence.py` block: `root /…/FEAT-48-parallel-safe-suite`, `discovered 63`, `ok no test mutates a path derived from the live checkout`, `PASS test-suite-independence.py`.

**Integration** (`--kind integration`): exit 0. `pool: 8 workers, 30 files, 44.41s wall`. Zero `FAIL`, zero `MUTATED`. `test-run-pool.py` block: all nine of its cases print `ok` (attribution, failure-propagation, runs-exactly-once, env workers ×2, invalid-worker ×2, order-not-load-bearing, cap, mutation-check, empty/missing refuse), exit 0, `PASS test-run-pool.py`. `test-check-domain.py`'s SC-01 cases: `ok schema/the copied unbroken hook DENIES the illegal document`, `ok schema/a CRASHING schema module DENIES the write rather than letting it through`, `ok schema/the live feature_schema.py was never written (bytes and mtime unchanged)`.

Combined file-level `PASS`/`FAIL` count across both runs, matched against the dispatch's pre-flagged quirk: **69 `PASS <file>.py` lines over 63 discovered files, 0 `FAIL`** — the six double-printers named in the dispatch (`test-quarantine.py`, `test-plan-merge.py`, `test-panel-findings.py`, `test-observations-merge.py`, `test-feature-worktree.py`, `test-expertise-merge.py`) account for exactly the +6, confirmed pre-existing (not re-raised).

63 unit+integration files = the `discovered 63` the independence scan reports over the live tree, corroborating the orchestrator's own second-opinion run.

## Assertion-strength audit — the two new test files

### `test-suite-independence.py` — HIGH finding: no self-red-proof ships in the file

The file is exactly 180 lines (confirmed against `git diff --stat d135364e..8e7f56dc`, a clean new-file addition of 180 insertions) and contains **zero `case()`/`case_*()` functions** — only `main()`, the AST scanner, and `discover()`/`scan_directory()`. T-03's own intent mandates, verbatim, "ITS OWN RED PROOF, in the file, so CI keeps proving the guard can fail": fixture sources for the pre-fix injection idiom, the mutant-beside-the-original shape, a PID-named variant, a clean control that must not be flagged, a live-tree case asserting `discovered >= 50` with an independently recomputed root, and a root-refusal case (`SystemExit(2)` for a tempdir with no `team-config.yaml`). **None of this exists in the shipped file.** `main()` never asserts `discovered >= 50` — it only prints the count — so a scan that walked nothing would print `discovered 0` and still exit 0.

All of this red-proof machinery instead lives **only** in T-03's own build-time `verify:` block in `plan.yaml`, which ran once during the build cycle and is not part of anything CI re-executes on a later push.

Falsification, run in a system tempdir (never inside the checkout): copied `test-suite-independence.py` + `harness_boundary.py` out, patched `scan_file` to unconditionally `return []` (simulating the scanner regressed to a no-op), and ran it two ways:
- against a fixture holding the pinned `ea6f51f` copies of the three historically-violating files: `discovered 3`, `ok no test mutates …`, **exit 0** — should have reported all ten violations and exited 1.
- against the live tree: `discovered 63`, `ok …`, **exit 0** — identical to the real scanner's output on the same tree.

A scanner that finds nothing, ever, is indistinguishable from a correct one to anything that runs after this branch merges. Separately, I *did* confirm the scanner's rule itself is currently correct — pointing the real, unmutated file at the same `ea6f51f` fixture via its own `--scan-dir` flag reports all ten sites individually (`test-check-domain.py:1482`,`:1489`; `test-check-state.py:2112`,`:2114`,`:2133`,`:2248`,`:2250`,`:2269`; `test-feature-worktree.py:584`,`:605` — 22 raw `VIOLATION` lines collapsing to exactly those 10 unique `file:line` pairs, several sinks firing more than once per line) — so SC-03 **as literally worded is satisfied today**. The finding is that nothing enforces it stays satisfied.

### `test-run-pool.py` / `run_pool.py` — mutation-check genuinely reddens; one MEDIUM gap

Independently exercised `run_pool.py --mutation-check DIR` (own fixtures, own tempdirs, never trusting `test-run-pool.py`'s self-report) against all of SC-10's vectors:
- direct write to an existing watched file → `MUTATED keep.txt`, exit 1.
- the same write performed via `subprocess.run(["sh","-c", …])` → `MUTATED keep2.txt`, exit 1 (the vector the static scan is blind to).
- a brand-new file created under the watched dir (`.mutant-x.sh`) → `MUTATED .mutant-x.sh`, exit 1 (the vector a git-based watched set cannot see).
- clean run → exit 0, no `MUTATED` line.
- empty watched dir → exit 2, `mutation-check measured no files under …`.
- absent watched dir → exit 2, `mutation-check directory is missing: …`.
- a file rewritten under a `__pycache__` subdirectory of the watched dir → **not** reported, exit 0 — correct per D-11's exclusion.

All seven match the implementation's contract exactly. **Gap**: T-04's own intent item (g) explicitly requires a `__pycache__` leg in `test-run-pool.py` ("Include one file under a `__pycache__` subdirectory … rewrite it during the run: it must NOT be reported … or the check reddens on the interpreter's own byte-code caching every real run"). The shipped `test-run-pool.py` (case at lines 74–90) covers clean / direct-edit / subprocess-edit / new-file / empty / missing, but **has no `__pycache__` leg at all**. The underlying behaviour is correct (verified above independently), but nothing in the suite pins it — a future edit to `run_pool.py`'s `snapshot()` that stops excluding `__pycache__` would ship green forever, reddening every subsequent real run instead (self-inflicted flake, exactly the failure mode D-11 names).

## SC evidence (verify: automated)

| SC | Test | Result |
|---|---|---|
| SC-01 | `test-check-domain.py` (integration) — case `the live feature_schema.py was never written (bytes and mtime unchanged)` + retained `a CRASHING schema module DENIES the write` | ok, ran in step 2 |
| SC-03 | `test-suite-independence.py` (unit) — live scan: `root <toplevel>`, `discovered 63`, zero findings | ok, ran in step 2; **see HIGH finding above — the criterion is met today but is not durably CI-protected** |
| SC-04 | unit run's `PASS test-suite-independence.py` line | present |
| SC-07 | `--check-kinds` exits 0 with agreement line; `--kind nope` exits 2; 69 file-level PASS lines / 0 FAIL across both kinds | confirmed directly, not only via T-06's own verify |
| SC-08 | `test-run-pool.py` case `completion order is not input order` | ok, ran in step 2 |
| SC-10 | `test-run-pool.py` case `mutation check covers clean, direct, subprocess, and creation` + independent probes above | ok, ran in step 2; **see MEDIUM finding — `__pycache__` leg not exercised by the shipped suite, though the implementation is correct** |

## SC evidence (verify: inspection)

- **SC-02**: `notes/measurements-parallel-suite.md` carries `control method: isolated bin copy`, `control broken reads 4968` (>0, taken inside an isolated bin copy per the plan's mandatory route, never against the live tree), `post-fix broken reads 0`, and the live module's bytes/mtime asserted unchanged across the control run. Shape matches the BRIEF and T-06 verify exactly.
- **SC-05**: ten `run <i> exit 0 <wall>s` lines (46.84–53.16s each) plus `tree condition: one FEAT-48 main session writing feature notes between runs; no process wrote bin during a run`. Shape matches; the note itself states plainly that ten clean runs do not prove the hazard is gone.
- **SC-06**: `pool: 8 workers, 63 files, 48.13s wall` against the 247s serial baseline, ≤120s. Shape matches, and independently reproduced twice more in this session (13.72s unit + 44.41s integration ≈ split of one `--kind all` run; the orchestrator's own second-opinion run recorded 48.09s).
- **SC-09**: `DEC-211 — The suite runs in parallel, and no test mutates state another test can see`, 590 words, every required phrase present, `gen-decisions-index.py --stdout` byte-identical to `DECISIONS-INDEX.md` (verified directly, exit 0, no drift).

## Test-first audit

The merge is one squashed commit (`b86ce66a "Build parallel-safe test suite"`); `git log` between the pinned SHAs shows no per-task commit boundary for any of the touched files, so test-first ordering **cannot be mechanically audited from history** here — this is a reasoned, not measured, gap. What I did verify directly: every task's own `verify:` block in `plan.yaml` narrates a test-first sequence (write assertion, run, observe the expected failure, then implement), and T-01/T-02/T-03/T-04's `verify:` blocks are themselves independent reconstructions of the properties their tests claim (T-04's block drives `run_pool.py` directly with its own fixtures rather than trusting `test-run-pool.py`'s exit code) — the discipline the plan calls for. I did not re-run those `plan.yaml` verify blocks myself (they are build-time, already-consumed evidence); I re-derived their conclusions independently instead (the mutation-check probes and the historical-sites probe above), which is stronger than re-running the same script twice.

## Findings

- **HIGH** — `test-suite-independence.py` ships with none of the self-red-proof fixtures T-03's intent mandates (injection-idiom, mutant-beside-original, PID-named-variant, clean-control, `discovered>=50` assertion, independently-recomputed-root check, root-refusal case). Falsified live: a scanner patched to always report zero findings produces byte-identical output and exit code against both the live tree and a fixture holding all ten historical violations. The invariant's own correctness has no CI-enforced regression protection going forward — only a one-time build-cycle proof that already ran. SC-03 is met as worded today; nothing keeps it met. Pointer: `.claude/skills/harness/bin/test-suite-independence.py` (whole file, 180 lines, no `case()`); `plan.yaml:756-795` (the intent that mandated the missing fixtures).
- **MEDIUM** — `test-run-pool.py`'s mutation-check case omits the `__pycache__`-exclusion leg T-04's own intent item (g) requires. The underlying `run_pool.py` behaviour is correct (independently verified: a `__pycache__` rewrite during a run is not reported), but nothing in the shipped suite pins it, so a future regression to `snapshot()`'s exclusion would ship silently and only manifest as spurious `MUTATED` reds on real runs later. Pointer: `.claude/skills/harness/bin/test-run-pool.py:74-90`; `plan.yaml:990-992` (intent item g).
- **LOW/INFO** — Test-first compliance for this feature cannot be checked against commit-order history because the whole feature landed as one squashed commit (`b86ce66a`). Not a defect; recorded so the next reader does not go looking for commit boundaries that do not exist.
- Pre-existing, not re-raised as new: the 69-vs-63 PASS-line duplication (dispatch already attributes this to six scripts printing their own summary, confirmed identical on `main` at `d135364e`); the plan-panel's own open finding `PF-e69c81…` that no criterion here re-tests issue #1053's own symptom (`test-gh-sync.py` under repeated 8-worker load) — already recorded in `plan.yaml`'s embedded panel block, not this gate's to re-litigate.

No test was authored, no fixture was written, and nothing under `.claude/skills/harness/bin/**`, `.harness/harness.json`, or `DECISIONS.md` was touched. All falsification probes ran from copies made in system tempdirs (`tempfile.mkdtemp()`), never as in-place edits to checkout files.
