# QA gate — FEAT-2542 validate c1 (run r-20261126-2-validate-validator)

**PASS.** The matrix floor at `bc937a947fc8716c6cf1b171f05ad24d5e019747` is `unit` (T-01 bugfix,
`touches_runtime_code`). I added `integration` because the diff warrants it (the SC evidence
lives there). Both kinds ran once, green, with receipts. Both verifies exit 0. The SC-03 seam is
clean. Base-red reproduces exactly: 97 = 97, set-equal. Mutants a–f and h redden the suite.
**Mutant g (placement after `_start_preflight`) stays fully green.** I measured an observable delta
that no row pins (F-1, low). Four low advisories follow; none blocks.

## Pin and matrix (read at the pin)

- Repository: mruangutai/harness, the unbound Harness feature in this checkout. Commit:
  `bc937a947fc8716c6cf1b171f05ad24d5e019747` (feature.json `review_sha` agrees). Blob:
  `git show bc937a94:.harness/harness.json`.
- T-01 is `bugfix`, which has no `always` kinds. Its `when:` rules resolve as follows:
  - `unit` if `touches_runtime_code`: **true**, because the diff changes `dispatch-guard.py`.
  - `integration` if `fix_confined_to_tests_and_contract_docs`: **false**, because production
    code changed. QA adds it anyway as warranted.
  - `__bug_class__` if `match_bug_class`: an unresolvable placeholder, so no kind fires.
- T-02 is `docs`, with `always: []`.
- Required set: **unit**. Reported: unit and integration, both active with a `cmd`.
- Checkout: `pinned-checkout.py add … --persona harness-qa` → `.claude/worktrees/.pins/FEAT-2542-dispatcher-placement--r-20261126-2-validate-validator--harness-qa`.
  `worktree-state.py --verify` reported "converged" and exited 0. `git status` was clean.
  `bun install --frozen-lockfile` and `compileall` ran first, as in CI.
- Candidate versus installed: the hook enforcing this run is the main checkout's
  `dispatch-guard.py` at 2e7a2c77 (sha256 57fb0c65…). The candidate at the pin is f2510eae….
  Candidate behaviour is proven only by tests run from the pin.

## 1. Kinds, receipts and CI route (this host: macOS arm64, python 3.15.2 — NOT CI's ubuntu interpreter)

Environment: `env -u PYTHONUNBUFFERED -u NO_COLOR -u FORCE_COLOR -u HARNESS_AGENT_TYPE TERM=xterm-256color`, cwd = pin.

| kind | command | discovered / completed | exit | receipt |
|---|---|---|---|---|
| unit | `python3 <pin>/.claude/skills/harness/bin/run-unit-tests.py --kind unit --shard 1/1 --manifest <F>/runs/r-20261126-2-validate-validator/qa/manifest-unit.json` | 68 / 68, all under `tests/unit/` | 0 | sha256 11dec4dd… |
| integration | same, `--kind integration`, `manifest-integration.json` | 95 / 95, all under `tests/integration/` | 0 | sha256 4a0c1f6e… |

- Both receipts record `tested_commit` = the pin and `runner_exit` 0, with every
  `completed_files[].returncode` 0.
- No integration file is counted as unit: every completed path carries its kind's directory
  prefix.
- `test-dispatch-guard.py` and `test-lead-start-return.py` are in the integration receipt.
  `test-lead-start-preflight.py` and `test-broad-catch-census.py` are in the unit receipt.
- Pass/fail is graded from the runner exit, per-file `returncode` and the footer (`ALL
  PASSED.`). The unit log has 4 `^FAIL ` lines (lines 359–364). They are
  test-factory-claim-mutation.py's own BUG-1290 mutation-proof reprints, not failures.
- CI aggregation: `check-integration-shards.py --commit <pin> --shards 1 --checks-result success
  --matrix-result success` ran over a /tmp copy of the integration receipt, named
  `integration-manifest-1.json`. Result: "PASS integration: 95 expected files completed exactly
  once across 1 shards at bc937a94…", exit 0.
- The `checks` job gates ran from `tests.yml` at the pin, each with its own run body and summary
  parsing (`bash -eo pipefail`):
  - Typecheck 0. Validate feature execution state 0 (41 files). Plan-route gate 0 (41 dirs, 2
    live plans).
  - Canonical-reader audit 0 (103 files). Instruction-path gate 0 (68 files). Layout gate 0.
  - **Repository-state gate 1 at the pin**: five INV-26 board-projection violations only. The pin
    carries plan `status: building`, the live board reads review, and station commit aea5cbf1
    follows the pin. Rerun at the feature tip aea5cbf1: **exit 0**.
  - I omitted the gate's `git config core.hooksPath` line: from a linked pin it writes the
    shared repository config. CI's 4-shard matrix itself was not run: the kind runs exactly
    once, as 1/1.

## 2. Plan verifies, run as written (`bash -c <verify>` from the pin, HEAD = pin)

- **T-01 exit 0.** dispatch-guard 397/397, lead-start-return 60/60, lead-start-preflight 61/61,
  census "ALL PASS". The byte check `git diff --quiet 2e7a2c77 HEAD -- test-lead-start-return.py
  inflight_registry.py` passed inside verify; the same check run on its own exits 0.
  predicted = observed, the last `tested_sha` is an ancestor, guard ≠ base, the seam is clean and
  `pin_run_exit` is 0.
- **T-02 exit 0.** The heading and index row are present, the index regenerates with no diff,
  anchors pass (25 examined, 0 failed), `test-gen-decisions-index.py` passes, source_issues is
  [2532, 2542], `(DEC-258)` is in the guard, dispatch-guard 397/397, and the seam is clean.
- Main's claimed figures all reproduce.

## 3. SC-03 seam

- The last (only) Pin run block names `tested_sha` d23f372898d0129b4e89efe49a1bc87e6e300a73.
- `git diff --quiet d23f3728 bc937a94 -- dispatch-guard.py test-dispatch-guard.py` → **exit 0**.
  d23f3728 is an ancestor of the pin.
- Files changed between d23f3728 and the pin: DECISIONS-INDEX.md, DECISIONS.md, and the feature
  directory's own feature.json, plan.yaml, characterization-pin.md, amend-T-02-intent-digest.md
  and answers-2026-11-26-t02-wording.md. No code or test file changed.

## 4. Fail-first, reproduced (natural RED, base source)

- Tree: a /tmp `git archive` of the pin, with `dispatch-guard.py` replaced by `git show
  2e7a2c77:` (sha1 1b365112, identical to base). Its test file is identical to the pin (sha1
  6da0f9c8). `dispatch-guard.py` is the only bin file the diff changes, so every other bin file
  is already base.
- `python3 tests/integration/test-dispatch-guard.py` → exit 1, **300 of 397**, 97 FAIL lines.
  `sort`-ed FAIL names `diff` against the pin's `predicted_red` with **no output (97 = 97,
  set-equal)**.
- **SC-01:** `c38/distill/distill:exit`, `:claim` and `:receipt` FAIL at base. This is the
  semantic red: base refused the FEAT-2489 payload. `c38/distill/run-reads` also fails, and so
  do the cause rows of missing, other, foreign-feature, no-tree-root and foreign-tree-root.
- **SC-02:** every changed class reddens at base.
  - c39/eng, all seven failure states: 8 checks each, and 10 for unreadable-owner (exit, claim,
    cause, remedy, plus bytes). Exit and claim are semantic reds, because base exited 0 and
    claimed.
  - c39/validator/not-found: 4 checks. c40: 2 or 4 each.
  - c38/fail-*: cause and remedy, which are text-absent reds. Base already refused these rows,
    with exit 2 and no claim.
- **Cases 1–37: 178 checks, all PASS at base** with the new test file, including rebound cases
  30 and 31. **c41, all 16 checks: PASS at base**, as the LEAVE requires.

## 5. Mutants (pin tests, mutated pin guard, /tmp tree copies, deleted afterwards)

The control (unmutated pin copy) gave 397/397. Each line below gives the mutant, the suite
result, and the rows that went red.

- **a1** not-found → declared: 375/397. Rows: c38/fail-not-found/missing,
  c39/eng/not-found/{bound,exploit}, c39/validator/not-found/bound and
  c40/not-found/{distill-run,plan-run}.
- **a2** not-found → None: 377/397. Same six rows as a1.
- **b1** ambiguous → declared: 385/397. Rows: c38/fail-ambiguous/distill and
  c39/eng/ambiguous/{bound,exploit}.
- **b2** ambiguous → None: 387/397. Same three rows as b1.
- **c** persona check dropped: 381/397. Rows: c38/fail-persona-mismatch/plan,
  c39/eng/persona-mismatch/{bound,exploit} and c40/persona-mismatch/{distill-run,plan-run}.
- **d** `except reg.UnreadableRegistry` only: 385/397. Rows: c38/fail-escaped-oserror/plan and
  c39/eng/escaped-oserror/{bound,exploit}.
- **e** `plan_route` keyed on declared mission ≠ distill: 393/397. Rows: c38/plan/distill,
  c38/norun/distill, c38/distill/missing and c38/distill/other.
- **f** `_placed_distill_feature` not memoized: 396/397. Row: c38/distill/run-reads.
- **g** `_dispatcher_placement()` after `_start_preflight()`: **397/397, fully green.**
- **h1** `_refuse_placement` prints and returns: 349/397, 24 rows red.
- **h2** the refusal returns None (claim step reachable): 309/397, 26 rows red.

## 6. Adequacy

- **SC-01:** all 15 ok-placement cells (3 placements × 5 missions) have a row. Placement failure
  × mission is covered diagonally, not as a cross product:
  - c38 has 7 failure rows with one mission each, and c40 adds distill and plan for not-found and
    persona-mismatch, so every state and every mission meets a failure.
  - Cells such as ambiguous×plan or unreadable×missing have no row.
  - Extra rows: distill-pending/plan, foreign-feature, no-tree-root and foreign-tree-root.
- **SC-02:**
  - eng-lead has all 8 outcomes, bound and exploit.
  - product-lead has 7 failure states plus ok (c38/distill/distill).
  - **validator-lead has only ok and not-found.** Its persona-mismatch, ambiguous, both
    unreadable and both escaped cells have no row.
- **LEAVE:** c41 covers Main, orchestrator-id, orchestrator-no-id and lead-no-id. Each is run in
  unreadable-owner and in escaped-oserror, where `find_run_claim` raises if called, so each row
  proves placement is never read. The lead-no-id signpost comment is present, as ruled under
  PF-0017.

## Findings

- **F-1** — kind substance, severity low, bound to T-01. Step 3(iii)'s ordering ("before any
  other preflight") has no discriminating row. Mutant g stays green.
  - Probe: validator-lead or eng-lead (Orch.Lead, in the not-found, ambiguous or unreadable-owner
    state) → harness-code-reviewer for X with `HARNESS-MISSION: plan`, approved plan.
  - Pin: exit 2, "lineage: … cannot be placed (<cause>)".
  - Mutant g, and base: exit 2, "plan-panel start … refused before any work", with no cause token
    and no find-run remedy.
  - Failure scenario: a reorder ships green, and the operator repairs plan status instead of the
    lost or corrupt claim. Fix: one c39 row of this shape.
- **F-2** — kind proportionality, severity low, bound to T-01. These are the SC-02 and SC-01
  literal-class cells with no row (§6).
  - The code path is persona- and mission-agnostic, and mutants a–d all redden through the
    eng-lead and product rows.
  - Failure scenario: a validator-lead-specific special case for one state ships unseen.
  - The signed plan chose these rows (PF-658a resolved), so this is advisory.
- **F-3** — kind form, severity low, bound to T-01. The plan-specified Inspect line says "A
  governed lead's dispatch binds to the feature its own runtime claim names, never the declared
  one".
  - Measured: an eng-lead ok-placed in a non-distill run (build-eng) of X dispatches
    backend-dev declaring Y. It exits 0 and claims in Y, at the pin and at base.
  - This holds inside the contract ("every later check keeps its base outcome"). The sentence
    overstates the binding beyond the distill preflight. The ruler decides whether the wording
    stands; I am not classifying it in-class.
- **F-4** — kind form, severity low, bound to T-01. The lineage rows assert stderr fragments, not
  that the lineage denial is the refusal that exited.
  - Under h1, c39/eng/persona-mismatch/exploit and c38/fail-persona-mismatch/plan stay green,
    because a later refusal exits 2 after the printed lineage text.
  - The mutant is still caught by other rows.

## Measured vs reasoned

Measured: every number above. Reasoned: the F-1 failure scenario's operator impact, and that the
g delta is confined to dispatches whose `_start_preflight` refuses (dispatched lead or
plan-mission reader). No execution was refused me, except `git checkout` in a /tmp clone; I
used `git archive` instead. The raw runner logs (3152 and 8617 lines) are not retained under
`runs/`, because QA's grant there is the receipts only. The per-file verdicts are in the receipts
and listed below.

## Runner per-file verdicts (from the runs above)

- unit: ALL PASSED; pool 8 workers, 68 files, 23.60s. 68 per-file PASS lines.
- integration: ALL PASSED; pool 8 workers, 95 files, 166.19s. 102 PASS lines (95 per-file plus
  reprints), 0 per-file FAIL.

## Principles applied

- Build the Lever: /tmp/qa2542 `mut.py`, `ci.py` and `verify.py` drivers. They built every
  mutant, CI gate and verify run from the pin blobs, with no hand edits. Deleted afterwards.
