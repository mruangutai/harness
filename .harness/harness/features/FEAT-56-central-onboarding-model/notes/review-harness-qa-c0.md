# QA gate-only review — FEAT-56-central-onboarding-model, review_sha 6f34e289

## BLUF: PASS with findings. `matrix_ok: true`. The must-fix from the pre-pin qa gate note
(`deploy.sh` literal tripping `test-no-distribution.py`) is confirmed fixed at the pin. The one
new production behaviour in the diff (`product_config_report` + `--check-product-configs`) has
two mutation-proved test-adequacy gaps in `test-fleet-product-config.py` that do not gate SC-05
(the mutants exercised only defensive/error-handling paths the current implementation cannot
otherwise reach) but are worth fixing forward. My SC-04 quarter (4/4 files) grades `met`. REQ-05's
verification gap is honestly disclosed in BRIEF.md but not restated in DECISIONS.md's DEC-220 —
reported as a low-severity documentation finding, not a functional gap.

## 1. Matrix re-run at the pin

Diff base `4b5dbb23`..pin `6f34e289` confirmed by `git diff --stat`: 56 files, the ONE production
behaviour change is `factory_config.py` (+`product_config_report`, `_check_product_configs`,
`--check-product-configs`/`--repo` flags) plus its new unit suite; everything else is prose/docs/
templates/commands/two agent files/plan-and-notes records. Matches the dispatch's contract exactly.

**Task change_type audit against `plan.yaml`:**
- T-04 `logic` → `test_matrix.logic.always = [unit]`. Required: **unit**.
- T-01, T-05, T-06, T-07, T-08 `docs` → `test_matrix.docs.always = []`. Required: **none**.
- T-02 `bugfix`, files all `.claude/skills/harness/bin/*.py|*.sh` (message/comment-only hunks,
  confirmed against the diff, matches the prior qa note's per-hunk audit) → `touches_runtime_code:
  true` (executed by gates) → obligates **unit**. `fix_confined_to_tests_and_contract_docs: false`
  (touches production `bin/`, not confined to tests) → does not itself obligate integration.
- T-03 `bugfix`, files all `tests/**` plus one comment-only `.sh` hunk → `touches_runtime_code:
  false`. `fix_confined_to_tests_and_contract_docs: true` → obligates **integration**.
- `match_bug_class` (the `__bug_class__` predicate): unresolvable placeholder repo-wide (repo
  Expertise G-08/T-02's own bugfix predicate note) — does not fire for either bugfix task.

**Combined floor: unit, integration.** Both required, both standing-active kinds
(`test_kinds.unit`/`test_kinds.integration`, `status: active`). No `config`-typed task exists in
this plan, so `touches_config_shape`/DEC-212 does not apply — assessed and dismissed, not a
pre-emptive skip: I checked every task's `change_type` and none is `config`.

## 2. Runner results — exit status and `^FAIL ` count reported separately

Ran in the FEAT-56 worktree at HEAD `1e65f995`, which is byte-identical in every source file to
the pin `6f34e289` (`git diff --stat 6f34e289 1e65f995` touches only `feature.json` and a new
`notes/handoff-*.md`, zero source files) — so running here is running at the pin.
`env -u HARNESS_AGENT_TYPE` used for both invocations per repository Expertise G-07.

- `--kind unit`: **exit=0**. `^FAIL ` count = **4** (raw grep), **all 4 attributed to
  `test-factory-claim-mutation.py`'s own deliberate mutation-proof output**, by name:
  `FAIL  BUG-1290 5a: served non-harness repository reaches its own segment's blocker verdict, not
  no_plan`, `FAIL  BUG-1290 5b: same feature id on two repositories resolves per-segment, no cache
  bleed` (×2, once under `MUTANT ACTIVE` and once under `MUTANT KEY-COLLAPSE ACTIVE`), `FAIL
  BUG-1290 5c: absent segment root still refuses via no_plan, naming that segment's own path` —
  all four sit between that file's own `MUTANT ACTIVE`/`MUTANT KEY-COLLAPSE ACTIVE` headers and its
  own `PASS test-factory-claim-mutation.py` line (confirmed by grepping the surrounding context).
  Zero `^FAIL ` lines outside that file. **Confirms the prior qa note's must-fix is fixed**: `grep
  -qF 'deploy.sh' .claude/skills/harness-init/SKILL.md` at the pin returns no match, and
  `test-no-distribution.py` contributes no `FAIL` line in this run.
- `--kind integration`: **exit=0**. `^FAIL ` count = **0**. Grepped for an anchor-skip line
  (`skip.*anchor` case-insensitive): **zero matches** — the no-anchor-skip clause holds.
- T-04's own verify (`test-fleet-product-config.py && test-factory-config.py`) already exercised
  inside the standing `--kind unit` run above (both files live under `tests/unit/`); independently
  confirmed exit 0, 15/15 then (existing count) 0 FAIL when run alone.

**`matrix_ok: true`.**

## 3. Test adequacy — `tests/unit/test-fleet-product-config.py` (15 cases, read at the pin)

Read via `git show 6f34e289:tests/unit/test-fleet-product-config.py` (243 lines) and
`.../factory_config.py` (512 lines).

**(a) Does any case assert implementation rather than observable behaviour? No — reasoned, not
mutation-proved.** Every case drives `product_config_report(fleet)` or `_main()` through its public
surface, stubs only the external boundary (`fc.factory_gh.file_at_ref`, the same convention
`test-factory-config.py` already uses), and asserts on the returned dict's public keys
(`repo`/`ref`/`path`/`ok`/`detail`), CLI stdout JSON shape, stderr line count, and `SystemExit.code`
— all consumer-observable. The only internal-looking call, `fc.clear_product_config_memo()` inside
`check()`, is test scaffolding to prevent cross-case memo pollution, not a per-case assertion.

**(b) Would the suite redden for the four named error-handling defects? Mutation-proved in a
disposable worktree (`.claude/worktrees/qa-mutant-proof-c0`, created from and removed back to the
pin; reviewed worktree untouched throughout):**

| Mutation | Result | Verdict |
|---|---|---|
| Widen `except FleetError` (line 348, pre-mutation numbering) to `except Exception` in `product_config_report` | 15/15 still pass, exit 0 | **NOT DETECTED — gap, mutation-proved** |
| Empty `detail` on the except branch (`ok, detail = False, ""`) | 2/15 fail: cases (b) and (c), both asserting `detail` content | **DETECTED** |
| Drop the `len(report) != len(fleet["repos"])` half of `_check_product_configs`'s exit guard, leaving only `if unreachable_count:` | 15/15 still pass, exit 0 | **NOT DETECTED — gap, mutation-proved** |
| Report over an empty `repos` list reading as vacuously all-ok | N/A — **unreachable, assessed and dismissed** | `load_fleet` itself refuses an empty `repos` list (`FleetError("fleet key invalid", "repos", ...)`, confirmed live), so this path cannot be driven through the CLI or any loader-mediated call; the docstring caveat is a defensive note for a caller that bypasses `load_fleet`, not a live gap in `--check-product-configs` |

**Findings from (b):**
- **[T-04] `tests/unit/test-fleet-product-config.py`** — no case distinguishes `except FleetError`
  from a wider `except Exception` in `product_config_report`. Concrete scenario: a future edit that
  widens the except clause (e.g. to catch a broader class "for robustness") would silently swallow
  an unrelated bug (a `KeyError`/`AttributeError` inside `product_config`) and report every member
  reachable-or-not with no distinguishing signal, exactly the failure mode the function's own
  docstring says it exists to avoid ("a report that swallows an unexpected bug would report every
  member unreachable for the wrong reason") — and the suite would not catch the regression. No
  stub currently raises a non-`FleetError` exception to prove propagation. Severity: **low** (the
  code today is correct; this is a coverage gap, not a live defect). Lane: **squad-writable**
  (`tests/**`, team lane, agents `harness-backend-dev | harness-dev-ops | harness-qa`).
- **[T-04] `tests/unit/test-fleet-product-config.py`** — no case distinguishes the
  `len(report) != len(fleet["repos"])` half of `_check_product_configs`'s exit-refusal guard from
  its absence. Concrete scenario: `product_config_report`'s loop currently always appends exactly
  once per declared repo, so the guard is defense-in-depth against a future regression that skips
  an append (e.g. an early-`continue` added under a future branch); if that regression landed
  alongside this coverage gap, `_check_product_configs` would exit 0 on a short-changed report —
  the docstring's own "declared count" caveat exists precisely because report length can drift from
  declared count, and the CLI-level guard is the one control that currently protects that, yet no
  test exercises the CLI with a short report. Severity: **low** (same reasoning as above — no live
  defect, a floor the current implementation can't yet trip, but the one guard is untested). Lane:
  **squad-writable** (`tests/**`, team lane).

Both are correctly scoped as coverage findings, not `FAIL`/`BLOCKED` gate results — they are gaps
in a satisfied-kind's own test file, not evidence the required kind is missing.

## 4. SC-04 — my quarter (4 of 15 files), each read individually at the pin

| # | File | Citation | Grade |
|---|---|---|---|
| 1 | `.harness/harness/docs/SPEC.md` | `SPEC.md:441-452` — "Onboarding a repository is three things, in order (DEC-220): land that repository's own `.harness/harness.json` on its `default_branch`; add a `- name: <owner>/<repo>` entry ... in `.harness/factory/fleet.yaml` ...; then create its central per-segment tree ... `that harness.json` on its default branch is the only file the harness puts into a product repository." | **met** |
| 2 | `.harness/harness/docs/BUILD.md` | `BUILD.md:389` — "`/harness-init` \| writes this control plane's own artifacts, and lands the one product-resident file — that repository's `.harness/harness.json` \| **one file only**, on that repository's default branch", with the fleet-entry half at `BUILD.md:391-397` | **met** |
| 3 | `.harness/harness/docs/DECISIONS.md` (new entry, DEC-220) | `DECISIONS.md:6987-6989` — "**Chose:** onboarding a repository is exactly three things: its own `.harness/harness.json` landed on its default branch, its entry in `.harness/factory/fleet.yaml`, and its central per-segment tree ... Nothing else is installed into a product repository" | **met** |
| 4 | `.harness/harness/docs/DECISIONS-INDEX.md` | `DECISIONS-INDEX.md:220` — "DEC-220 @6985 ... :: The central onboarding model: a repository's `harness.json` on its default branch, its fleet entry, and its central per-segment tree; nothing else enters a product repository." | **met** |

My quarter: **4/4 met**, one `file:line` citation each, each read at the pin via `git show`.

## 5. REQ-05 verification-gap honesty

BRIEF.md's `## Verification gaps` (last bullet) states the gap plainly: `check-state.sh`
deliberately makes no network call, so REQ-05 is discharged only by the operator-run
`--check-product-configs` (SC-05), and "a member whose config is deleted after onboarding stays
invisible until the next build." **Honestly disclosed — no understatement found.**

DECISIONS.md's new entry (DEC-220, `:6985-7008`) states the mechanism ("`factory_config.py
--check-product-configs` is what names it") but **does not restate the operator-run-only /
no-standing-invariant caveat** — it reads as though the check closes the gap, not that it is a
point-in-time, operator-invoked check with no continuous enforcement. This is not a contradiction
of BRIEF.md (nothing in DEC-220 claims a network invariant exists), but it is a documentation
completeness gap in the artifact of record most likely to be read in isolation from BRIEF.md.

**Finding — [T-07] `.harness/harness/docs/DECISIONS.md:6985-7008`** — DEC-220 omits the
operator-run-only nature of the REQ-05 check that BRIEF.md discloses. Concrete scenario: an
operator or a future agent reads DECISIONS.md alone (its own index entry is even terser) and
concludes the ordering constraint plus `--check-product-configs` fully closes the "unattributed
`FleetError`" failure mode, missing that nothing runs this check automatically and a config
deleted post-onboarding stays invisible until the next build reaches it. Severity: **low**
(documentation completeness, not a functional or contract defect — BRIEF.md, the authoritative
verification-gaps record, is not itself understated). Lane: **squad-writable**
(`.harness/harness/docs/**`, team lane, agent `harness-documentor`).

## Assessed and dismissed
- Vacuous-all-ok over an empty `repos` list: dismissed above (§3) — unreachable via `load_fleet`,
  which refuses an empty `repos` list before `product_config_report` is ever called through any
  real entry point.
- `touches_config_shape`/DEC-212: dismissed — no task in this plan carries `change_type: config`.
- SC-01/SC-02/SC-03/SC-06/SC-07/SC-08/SC-09/SC-10: out of my assigned scope for this dispatch
  (mechanically graded by the pre-pin qa gate note or reserved for other panel members); the two
  I independently re-verified because the matrix task required it (SC-06, SC-07) are consistent
  with that note's prior grading.

## Final tree state
`git status --porcelain` in the reviewed FEAT-56 worktree: one untracked file,
`notes/review-harness-security-reviewer-c0.md` — a concurrent sibling panel member's own artifact,
not mine; not present before this run and not written by me. No tracked file differs; I made zero
edits to this worktree. All mutation proofs ran in a disposable worktree
(`/Users/molchairuangutai/GitHub/harness/.claude/worktrees/qa-mutant-proof-c0`, created from and
restored to `6f34e289` via `git checkout --` between each mutation, confirmed clean before removal)
which has been removed (`git worktree remove`, no worktrees remain matching `qa-mutant-proof`).

## Open questions
- None blocking. The two test-adequacy gaps and the DECISIONS.md disclosure gap are routable
  findings, not gate failures — `matrix_ok: true` and both required kinds (`unit`, `integration`)
  are satisfied.
