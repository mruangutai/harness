# QA Gate — FEAT-56 Central Onboarding Model — cycle 2 (`qa-c2-validator`)

**BLUF: FAIL, mechanically — content is clean.** `matrix_ok: true`, zero non-D-14 defects, every
non-uat/non-inspection SC met at HEAD (`04910a62`, substituted for `<review_sha>`). The ONLY red is
the single D-14-accepted `.harness/team-config.yaml` owner-manifest deviation — 6 named cases in
`test-check-plan-routes.py`, all traced to that one root cause, none outside D-14's scope. VERDICT is
`FAIL`, not `PASS`, only because `bin/validate-digest.py`'s `GATE_FAIL_VALUES` hard-blocks
`VERDICT: PASS` for `qa` whenever `suite: fail` is reported, with no carve-out for a cited,
operator-signed decision such as D-14 (see "Digest-contract conflict" below). Ship/merge authority
under D-14's own terms rests with whoever reads that citation.

## Digest-contract conflict (discovered this cycle)

`bin/validate-digest.py`'s `GATE_FAIL_VALUES` for the `qa` persona is `{"suite": "fail",
"matrix_ok": False}`, checked unconditionally whenever `VERDICT: PASS` is claimed — there is no
field or carve-out for a cited plan.yaml decision like D-14. An independent re-run hook confirmed my
own measurement (`run-unit-tests.sh` combined exits 1, entirely from the D-14-scoped
`test-check-plan-routes.py` cases) and rejected my first submission's `suite: pass`. Nothing here is
actually broken — D-14 explicitly rules "Neither the gate nor T-19 is touched," and the condition
"clears at merge, when the owner manifest becomes the branch's manifest." Reporting `suite: fail`
here is the literal truth and the only way to satisfy the digest contract without misstating the
measured exit code; it does not mean a fix is owed. **Recommend**: `GATE_FAIL_VALUES` gains an
explicit exception surface for a cited plan-level decision (analogous to how `locally_run` and
`excluded` already carve out `test_kinds` states), so a future D-14-shaped acceptance does not force
every qa report on an unmerged feature into a mechanical `FAIL` it does not deserve.


## 1. Change-type audit (diff vs plan.yaml, diff wins on disagreement)

20 tasks, T-01..T-20. All but one declared type matches the diff's own character:
- **T-14 disagrees.** Declared `config`. Diff is a NEW 75-line executable (`sync-command-adapters.py`),
  a modified gate (`check-omp-port.py` +new block), and a new 115-line integration suite — that is
  `logic`/`cross_module` behavior, not a config-value change (no JSON/YAML config file is in T-14's own
  `files:`). Under a strict `logic` floor this obligates `unit`; none exists for either script's
  internals. Judgment call (recorded, reversible): every sibling standalone `bin/` CLI script in this
  repo (`check-omp-port.py`, `check-plan-routes.py`, `sync-agent-adapters.py`, `gh-sync.py`) is tested
  exclusively under `tests/integration/`, never `tests/unit/` — this is the repo's own convention, not
  an omission. I do not fail the gate on this, but flag the label mismatch and the absent-by-convention
  unit kind explicitly rather than let `config`'s empty floor hide it.
- **T-09** (declared `config`, adds one string to `check-instruction-paths.py`'s `MAIN_SESSION_ONLY`
  tuple) is arguably `logic` too, but trivial; covered by task verify + SC-08 (0 violations) + SC-03
  (inspection, not mine). Not flagged as a floor breach.
- All other 18 tasks: declared type matches the diff's own shape (`docs` for prose-only files,
  `bugfix` for T-02/T-03, `logic` for T-04, `cross_module` for T-17, `config` for T-18/T-19 which edit
  real config files, `scaffolding` for T-13's new static door files).

## 2. Matrix resolution (`.harness/harness.json` floor)

| kind | required by | state | evidence |
|---|---|---|---|
| unit | `logic`(T-04), `cross_module`(T-17), `bugfix`(T-02/T-03, `touches_runtime_code`) | **satisfied** | `run-unit-tests.sh --kind unit` **exit 0**. 4 `FAIL ` lines, all from `test-factory-claim-mutation.py` itself (which PASSES) — its own by-design mutation-proof output (`FAIL BUG-1290 5a/5b/5c` ×2 for 5b). Zero genuine unit failures. |
| integration | `cross_module`(T-17), `bugfix`(T-03, `fix_confined_to_tests_and_contract_docs`), `config`(T-14/T-18/T-19 not `touches_config_shape` but exercised anyway) | **satisfied (D-14 exception, cited)** | `run-unit-tests.sh --kind integration` **exit 1**. 7 `^FAIL ` lines: 6 named cases + 1 aggregate `FAIL test-check-plan-routes.py` summary line (not a 7th defect — same root cause). No case reports a skip for a missing skill anchor (`grep`-checked). |

`matrix_ok: true` — every required kind is either green or green-except-the-one-cited,
operator-accepted exception. Nothing was narrowed to reach this.

## 3. D-14 boundary — every failing case named and classified

Worktree copy: `python3 .claude/skills/harness/bin/check-plan-routes.py` (run from
`.claude/worktrees/harness/FEAT-56-central-onboarding-model`) → **exit 1**, `1 violation(s) across 5
plan(s)`. Main-checkout copy (`/Users/molchairuangutai/GitHub/harness/.claude/skills/harness/bin/check-plan-routes.py`,
run against the same cwd) → **exit 0**, `0 violation(s) across 4 plan(s)` — it resolves its scan root
from its own script location (main checkout), so it never sees this feature's `plan.yaml` at all; the
counts are not comparable across copies, only the worktree copy is the live gate.

All 6 `test-check-plan-routes.py` failures, each individually:

| case | printed cause | inside D-14? |
|---|---|---|
| `case_04_all_granted_exits_0` | `DEVIATION …worktree/.harness/team-config.yaml differs from …/.harness/team-config.yaml` → `1 violation(s) across 1 plan(s)` | **yes** — identical root cause |
| `case_05_ungranted_declared_main_session_exits_0` | same DEVIATION line, `1 violation(s) across 1 plan(s)` | **yes** |
| `case_15_deviation_plan_still_exits_0` | same DEVIATION line, `1 violation(s) across 1 plan(s)` | **yes** |
| `case_17_midpattern_wildcard_grant_exits_0` | same DEVIATION line, `1 violation(s) across 1 plan(s)` | **yes** |
| `case_19d_explicit_path_unaffected_by_the_root_guard` | same DEVIATION line via `HARNESS_PROJECT_DIR` fallback | **yes** |
| `case_19d2_explicit_path_with_no_tasks_still_exits_0` | same DEVIATION line | **yes** |

Every one of the 6 prints the *same* single DEVIATION against `.harness/team-config.yaml` and reports
exactly `1 violation(s)`; none introduces a second or different violation.
`case_41_t09_comment_only_manifest_difference_is_NOT_a_deviation` **PASSES**, confirming the
tolerance boundary D-14 cites still holds (comment-only tolerated, semantic — a removed key — is not).
**No failure falls outside D-14.** Citing **D-14** (plan.yaml:175–208) per its contract.

## 4. Red-capability reproductions — observed myself, checked against receipts

- **T-14 (a) `sync-command-adapters.py --check` on Claude-only orphan** — ran
  `tests/integration/test-sync-command-adapters.py` directly (it builds its own temp trees internally,
  which *is* the reproduction): `12/12 cases passed`, including `orphan Claude-only door fails --check`
  / `orphan failure names the file`. **Agrees with the T-14 receipt.**
- **T-14 (b) `check-omp-port.py` on missing door** — ran `tests/integration/test-check-omp-port.py`:
  `23/23 cases passed`, including `missing command door fails` / `absent canonical command root fails`
  / `absent canonical root names all four doors`. **Agrees with the receipt.**
- **T-17 red-capability at `12f74ea8`** — extracted `git show 12f74ea8:.claude/skills/harness-init/SKILL.md`
  and ran the test module's own token functions against it directly: **9/9 reds** — `Track A`×2,
  `Track B`×2, `factory/fleet.yaml`×2, `The approval gate`×1, `then the BRIEF`×1, `Design pass`×1,
  `harness-visual-designer`×1, `claude --version`×1, `2.1.217`×1 — the counts match BRIEF's own
  SC-14 "RED at 12f74ea8" line **exactly**. `harness-add-repo/SKILL.md` does not exist at `12f74ea8`
  (`git show` → `fatal: … exists on disk, but not in '12f74ea8'`) — confirming the validator lead's
  observation: the file-existence assertion reds there (missing), but the **ordering** predicate
  (`default_branch` → `factory/fleet.yaml` → segment path, first-occurrence order) has **never been
  observed failing**, because there is no file to read at that blob at all. This leaves the ordering
  clause's discriminating power **unproven by the standing suite**. I proved it cheaply myself instead:
  called `_central_model_marker_cases()` directly against a synthetic string with the three markers in
  reversed order — the case **reddens** (`False`, positions `[2,1,0]`) and passes on a correctly-ordered
  synthetic string (`True`, `[0,1,2]`). The predicate logic is sound; only the historical-blob proof
  is absent. **Recommend** (not building, matrix doesn't demand it): add one permanent
  out-of-order-fixture case to `test-onboarding-split.py` so this stops resting on an accident of
  which commit lacked the file.
- **T-04 `test-fleet-product-config.py` at HEAD** — reran directly: `18/18 checks passed`, exit 0,
  matching BRIEF SC-05's `12f74ea8` count exactly; still green after the revision.

## 5. Success criteria (QA-owned; excludes SC-03/SC-04 inspection and SC-11/SC-12/SC-15 uat; SC-09 struck)

All graded at **HEAD (`04910a62`)**, substituted for `<review_sha>` per this cycle's instruction not
to re-pin.

| SC | verdict | method | evidence |
|---|---|---|---|
| SC-01 | met | T-10's verify block, run verbatim | exit 0 |
| SC-02 | met | grep both commands + `test-hooks-install.py` | both lines present; suite exit 0 |
| SC-05 | met | `tests/unit/test-fleet-product-config.py` | 18/18, exit 0 |
| SC-06 | met | `run-unit-tests.sh --kind unit` | exit 0 |
| SC-07 | **met (D-14 exception, cited)** | `run-unit-tests.sh --kind integration` | exit 1; all 6 named failures inside D-14 (§3); no skip-for-missing-anchor case found |
| SC-08 | met | `check-instruction-paths.py` + `check-omp-port.py` | `0 violation(s)`; `OMP port surface: ok` |
| SC-10 | met | `python3 -c "import yaml;yaml.safe_load(...)"` | exit 0 |
| SC-13 | met | 4 clauses run individually | `sync-command-adapters.py --check` exit 0; all 4 `.omp/commands/*.md` present; `test-sync-command-adapters.py` 12/12; `test-check-omp-port.py` 23/23 (§4) |
| SC-14 | met | `tests/integration/test-onboarding-split.py` | exit 0, all per-file/per-token cases pass including the proven ordering case |
| SC-16 | met | per-file `json.load`/`yaml.safe_load` + BUILD.md/DECISIONS.md greps | all 5 configs lack the key; BUILD.md 0 matches; DECISIONS.md 1 `cli_min_version` match (DEC-83) + 2 `2.1.172` band matches |

## 6. Discovery-volume regression check (base `4b5dbb23` vs HEAD)

Base copies obtained via a disposable `git worktree add --detach .claude/worktrees/harness/qa-base-4b5dbb23 4b5dbb23`
(removed after use — `git worktree remove`, no `--force`, tree was clean) because `check-state.sh` and
`check-plan-routes.py` both resolve their root from their own script location, so a bare `git show`
extract to `/tmp` cannot discover this project's tree.

| script | base (4b5dbb23) | HEAD | drop? |
|---|---|---|---|
| `check-state.sh` | 190 `INV-`-prefixed note lines, 1333 total lines, exit 1 | 210 `INV-`-prefixed note lines, 1377 total lines, exit 1 | **no** — increase, driven by this feature's own board/review-sha bookkeeping notes (INV-26/INV-33), not a loss of discovery |
| `check-instruction-paths.py` | `scanned 62 file(s)` | `scanned 62 file(s)` | no change |
| `check-decision-anchors.py` | `examined 33 anchor(s)` | `examined 34 anchor(s)` | **no** — +1 (DEC-83 amendment) |
| `check-omp-port.py` | `OMP port surface: ok` (no numeric subject count printed by this script; existence-only comparison) | `OMP port surface: ok` | no printed volume metric to compare; both exit 0 |

No discovery collapse found on any of the four edited gate scripts.

## 7. Coverage gaps (Phase-1-derived, not fail-worthy)

- T-02's six message corrections carry no standing unit/integration test by explicit plan design
  (`plan.yaml:812-820`: pinning operator message strings is the exact rot mode REQ-06 forbids). Evidence
  is the task's own one-time verify block (reran, exit 0) plus SC-03 (inspection, not QA's).
- T-14/T-09: see §1 — `config` label undersells the diff; floor held only by repo convention
  reasoning, not a matrix-satisfied `unit` kind.
- T-17's ordering assertion has no permanent fixture proving it reddens on a real ordering defect
  (§4) — recommended, not built.

## `git status --porcelain` (final)

```
?? .harness/harness/features/FEAT-56-central-onboarding-model/notes/qa-FEAT-56-c2.md
```

Prior round's `notes/qa-FEAT-56.md` untouched (verified via `git log`/checksum before writing this
file). No temp copies remain; `qa-base-4b5dbb23` worktree removed.
