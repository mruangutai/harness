# QA Gate — BUG-124-run-dir-squad-suffix — cycle 4 (final confirmation)

## VERDICT: PASS — `matrix_ok: true`

Grading commit `418a9eb6` on `feat/BUG-124-run-dir-squad-suffix`. `git -C <worktree> status
--porcelain` shows only `.harness/harness/features/.../feature.json` dirty (orchestrator-owned
run-artifact, whitelisted, not graded). `git diff --stat 80ce35d1..418a9eb6` confirms the eng diff
is exactly the four declared files (`dispatch-guard.sh`, `harness_boundary.py`,
`tests/integration/test-dispatch-guard.py`, `tests/unit/test-harness-boundary.py`); the full
feature diff `de97f4a2..418a9eb6` (merge-base to HEAD) additionally shows files from three
unrelated PRs merged onto this branch before the BUG-124 plan phase started (`check-expertise.sh`,
`factory_config.py`, `factory_decompose.py` and their tests) — these predate `8f9e8fe6` (BUG-124's
own first commit) and are out of scope; predicate evaluation below is against the correct,
unchanged 4-file eng diff, so cycles 1-3's predicate rulings are not disturbed.

**There is no known-remaining failure to carve out this cycle. None found — every FAIL would have
been new, and none appeared.**

## 1. Matrix resolution (unchanged from cycles 1-3, re-confirmed against the same 4-file diff)

`bugfix` (`.harness/harness.json:203-219`), each `when` leg evaluated against the diff:
- `{unit, if: touches_runtime_code}` — **TRUE**: `dispatch-guard.sh`, `harness_boundary.py` are
  executed on every governed dispatch. → obligates `unit`.
- `{integration, if: fix_confined_to_tests_and_contract_docs}` — **FALSE**: production files are
  touched, not just tests/docs. This leg does not independently obligate `integration` — but
  `integration` is *added above the floor* per cycles 1-3's standing reasoning (T-02 is a shell
  behavioral gate with no unit surface, every SC in BRIEF.md is `evidence: integration`). Floor is a
  minimum, not a ceiling; adding it forward is correct, not a re-litigation.
- `{__bug_class__, if: match_bug_class}` — **unresolvable**, repo Expertise G-08: no bug-class
  taxonomy entry exists in this project yet. Adds nothing.

**Required kinds: `unit`, `integration`. Both resolve to `satisfied`.**

`.agents/skills/harness/bin/...` (matrix's spelling) and `.claude/skills/harness/bin/...` (this
sweep's spelling) resolve to the **same inode** in this checkout (`.claude/skills` is a symlink to
`../.agents/skills`, confirmed via `readlink`/`stat -f %i`, both 212884364) — no divergence, both
paths run the identical file.

## 2. Per-kind runs (`env -u HARNESS_AGENT_TYPE`, from worktree root)

| kind | cmd | exit | outcome |
|---|---|---|---|
| task-scoped, T-01 `verify:` | `python3 tests/unit/test-harness-boundary.py` | 0 | 60/60 `PASS`, `ALL PASS` |
| task-scoped, T-02 `verify:` | `python3 tests/integration/test-dispatch-guard.py` | 0 | 69/69 `PASS` |
| `unit` kind (`test_kinds.unit.cmd`) | `.agents/skills/harness/bin/run-unit-tests.sh --kind unit` | 0 | 0 `^FAIL ` lines, 1491 log lines |
| `integration` kind (`test_kinds.integration.cmd`) | `.agents/skills/harness/bin/run-unit-tests.sh --kind integration` | 0 | 0 `^FAIL ` lines, 3914 log lines |

Both configured per-kind commands were exercised directly this cycle (not merely the two
task-scoped files), closing cycle 1's bounded-evidence caveat now that sibling worktrees are no
longer a stated constraint here.

## 3. Full sweep + discovery volume vs. baseline

`env -u HARNESS_AGENT_TYPE bash .claude/skills/harness/bin/run-unit-tests.sh`, run by me, captured
exit status (not tail-read), `^FAIL ` counted by grep, not inferred from the final line:

- **`RUNNER_EXIT=0`**
- **`grep -c '^FAIL ' = 0`**
- **5403 output lines** (matches lead's cross-check exactly)
- **`8 workers, 80 files, 66.54s wall`** — **80 files discovered**, identical to the lead's stated
  baseline (80/5403). No discovery-volume regression; the import change did not narrow what the
  sweep can reach.

## 4. The four named files — individually, by name

| file | exit | `^FAIL` count | tail |
|---|---|---|---|
| `tests/integration/test-run-unit-tests-kinds.py` | 0 | 0 | `PASS manual comprehension probe is layout-valid` |
| `tests/integration/test-run-unit-tests-layout.py` | 0 | 0 | `PASS git untracked rogue is not reported and both sentinels run` |
| `tests/integration/test-check-plan-routes.py` | 0 | 0 | `ALL PASS` |
| `tests/integration/test-check-domain.py` | 0 | 0 | `10/10 BUG-1305 identity cases passed.` |

All four green, individually confirmed, not inferred from the sweep aggregate.

## 5. Eng lead's supersession claim — VERIFIED at source, not adopted on say-so

Claim: `test-check-domain.py`'s `sweep/clean-tracked RED` case was a **fourth masked instance** of
T-01's own bare-import defect (qa-c3's fourth file), not the independent non-discriminating
self-test qa-c3 ruled it. Two independent checks:

- **Source**: `grep -n 'import harness_yaml' harness_boundary.py` → exactly one hit, line 847,
  between `try:` (846) and `walk(harness_yaml.load_file(manifest_path))` (848), inside the
  pre-existing `except Exception: return []` (849-850). Matches the digest's claim verbatim.
- **Behavior**: `test-check-domain.py`'s own printed red-proof line now reads `red proof: original
  reported 0 FEAT-OLD line(s), mutant 2` immediately followed by `ok sweep/clean-tracked RED:
  removing the skip makes case A red` — base=0, mutant=2, `mut(2) > base(0)` discriminates
  correctly. qa-c3 recorded this same case as `mut <= base` (0 <= 0, non-discriminating) at the
  pre-fix commit. The mechanism the digest describes (mutant's bare tmpdir lacks `harness_yaml.py`,
  so under the old top-level import the mutant's own `harness_boundary` import raised, its sweep
  silently reported 0, and `0 <= 0` false-failed) is now moot because the import site itself moved
  inside a guarded `try/except` that already returns `[]` on any import failure, at either commit
  side of the mutation — matching what the printed numbers show.

**Verified, not merely adopted.** This does **supersede** `qa-c3.md`'s §"Mechanism does NOT explain
(1 of 4 files)" on this one point: what qa-c3 ruled an independent pre-existing failure was in fact
a fourth instance of the same T-01 import defect qa-c3 itself found and ruled FAILING at cycles 3.
`qa-c3.md` is left unedited, per instruction — this note is the correction of record.

## Ruling

- `unit`: **satisfied**. `integration`: **satisfied**.
- Full sweep: exit 0, 0 FAIL, 80/80 files discovered (baseline-equal) — no silent-narrowing
  finding.
- All four cycle-3-red files individually green.
- Eng lead's four-files-one-cause attribution: **confirmed** at source and behavior, superseding
  `qa-c3.md`'s attribution of the fourth file on that one point only; nothing else in `qa-c3.md` is
  disturbed.
- **`matrix_ok: true`. `VERDICT: PASS`.**
- Cycle 1-3's unchanged rulings (predicate evaluations, assertion-strength review, Q1 test-first
  ruling, the 61/69 red-capability reproduction, the four behavioural-equivalence rulings, T-03's
  correct main-session-direct exclusion) are **not re-litigated** and stand.

## Not re-opened

- Operator rulings R-1..R-5, the eng lead's Q1 (already answered: no `qa-c3.md` edit, this note
  records it), T-03's exclusion — all settled per dispatch, none touched here.
