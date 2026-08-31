# FEAT-45 — QA gate review, cycle 3 (GATE-ONLY, no authoring)

Pin: `d78f393a7d5addc1cbd2f31628aed18c54983b9a`. Scope: `git diff main...d78f393` (merge-base `ba338d8`).

## VERDICT: PASS. No must-fix. All three named suspicions investigated and each is a non-issue.

## Change type / matrix

The plan's original tasks (T-01..T-12) are `logic`/`config`/`docs`, floor = `unit` only. But
this fix cycle's actual diff (validate-digest.py + its integration suite, run-unit-tests.sh,
check-state.sh, `.omp/extensions/harness-hooks.ts`) crosses Python/Bash/TS module boundaries
and its own regression tests (`check_hook_feature_dir`, `check_skipped_member_errors`,
`_check_plan_feature_binding`) live in `test-validate-digest.py`, which `run-unit-tests.sh`
registers under **integration**, not unit. I therefore ran BOTH kinds — unit alone would have
missed every regression test that actually pins F1/F2/F3/F5.

`matrix_ok: true`.

## Discovery counts (not just exit codes) — both kinds re-run live at this pin

| kind | rc | `^FAIL ` lines | script-result lines (broad `^(PASS\|FAIL) `) | distinct registered scripts | real KIND-DRIFT |
|---|---|---|---|---|---|
| unit | 0 | 0 | 433 | 30 (31 printed lines — `test-panel-findings.py` self-prints its own trailing "PASS test-panel-findings.py", benign dup) | 0 |
| integration | 0 | 0 | 588 | 27 (31 printed lines — 4 scripts self-print a dup PASS line) | 0 |

Union = 30 + 27 = **57 registered scripts**, matching the claim exactly. The only lines matching
`KIND-DRIFT` in either log are `test-run-unit-tests-kinds.py`'s own internal case names
(`ok case 1: … reports EXACTLY zero KIND-DRIFT lines`, etc.) — i.e. the detector testing itself,
not a live drift. Corroborated **exactly**: unit rc=0, 0 FAIL, 433 script-result lines, 57
registered, no drift.

## Main's per-suite evidence — corroborated by direct re-run, not restated

Ran inside `run-unit-tests.sh --kind integration`; grepped the `N/N … passed` summary lines
myself: `69/69 CLI cases passed`, `14/14 hook cases passed`, `24/24 T-09 cases passed`,
`2/2 template cases passed`, `18/18 reviewer severity_max enum checks passed`, `ALL PASSED.`
Matches exactly. `test-code-grade.py` PASS (unit kind). `test-gen-decisions-index.py` PASS
(integration kind).

## The three named suspicions — each demonstrated, none is a regression

**1. F3 (`skipped` narrowed to persona `fable-advisor`).** Read both team configs
(`teams/plan-panel.yaml`, `teams/review.yaml`): `fable-advisor`/`should-not-exist` is the
ONLY step either config documents as legitimately skippable ("If fable-advisor cannot resolve
or preflight refuses it, the lead skips the step…"). `review.yaml`'s four members (code, qa,
security, ui) are all mandatory — a reviewer with no user-facing/security surface **self-scopes
out and returns PASS**, a different mechanism from `status: skipped`. So there is currently no
legitimate non-fable-advisor skip case in either shipped team, and the restriction at
`validate-digest.py:944-946` matches design intent exactly — **not over-tight.** Regression test:
`check_skipped_member_errors` case `{"persona": "qa", ...}` → expects `"optional fable-advisor"`
in the error (`test-validate-digest.py:148-162`), plus CLI case `"mandatory member cannot be
laundered as skipped"` (line 34 of the diff). Both ran and passed. **DEMONSTRATED, not just
inferred.**

**2. F5 (`inflight_registry.feature_root` fallback).** `feature_root()` is not a persisted/stale
registry at all — it walks `harness_boundary.linked_worktrees(owner_root)` live via git's own
`.git/worktrees` pointers on every call (no caching), so "stale entry" doesn't really apply; a
no-match falls back to `owner_root`. I loaded `validate-digest.py` directly and called
`_hook_feature_dir()` with no matching worktree present: it returned a path under the fallback
`owner_root` that does not exist on disk. I then traced that into `_read_review_sha` /
`code_grade_bound_to_review`: both reject with `"…feature.json could not be read (…No such file
or directory…), so the claim is not trusted."` — **fails CLOSED, empirically confirmed by direct
execution, not reasoning alone.** (Confirmed independently: `.harness/harness/features/FEAT-45…`
exists at this pin's worktree but `git show main:` for the same path errors "exists on disk, but
not in main" — an unmerged feature's dir genuinely does not exist under the owner/main root, so
the fallback path is guaranteed absent for the exact case F5 was written for.) Coverage gap:
`check_hook_feature_dir` (test-validate-digest.py:120-145) only exercises the happy-path
(mocked `feature_root` returns the correct worktree) — no test pins the fallback-rejects-closed
behavior I just demonstrated live. **BACKLOG**, not must-fix — I demonstrated the code already
does the safe thing; only the pin is missing.

**3. F1 (branch corroboration on the plan-review path).** `_branch_corroboration_error` is
explicitly additive-only and documented as such: `current_branch is None` → no-op,
`feature_branch is None` → no-op, only a REAL and DIFFERENT branch on both sides rejects
(`validate-digest.py:798-822`). It cannot reject a reviewer whose branch is merely
undeterminable, only one whose recorded and actual branches genuinely disagree. Regression test:
`_check_plan_feature_binding` sets `branch: "feat/FEAT-PLAN"` in feature.json, then calls with
`branch_override="feat/OTHER"` and asserts a `"does not match"` error
(`test-validate-digest.py:2054-2068`) — ran and passed. **DEMONSTRATED.**

## Carried-forward, still open — unchanged, not re-derived

M4 (32-bit truncated finding id, med/security — asserted not demonstrated), M6 (goalcheck
transcription ambiguity, low), M7 (withhold message states fact not remedy, low), and the
`check-state.sh` attribution-check missing-`continue` (low) — did not re-derive; `check-state.sh`
did change at this pin (INV-32 disposition refactor, `70fd441`) but that hunk is unrelated to
the earlier low finding's line range and I did not re-verify it.

## Residual coverage gap (new observation, BACKLOG not must-fix)

`check_pending_plan_review`'s fixtures (`_check_plan_approval_states`,
`_check_plan_feature_binding`) still call `validator.validate(..., feature_dir, ...)` with an
**explicit** `feature_dir` (`test-validate-digest.py:2026-2029`) — the same gap the c2 code
review flagged, still true at this pin. What's new this cycle: `check_hook_feature_dir` now
independently unit-tests the resolver (`_hook_feature_dir`) that production's `hook_mode()`
actually uses. But no test drives a DEC-207 plan-review digest through `hook_mode()` end-to-end
with `feature_dir` resolved via the registry (unlike the code-review path, which has multiple
`[hook] …` cases). Since `_resolve_feature_dir` treats an explicitly-supplied `feature_dir`
identically regardless of provenance (`if feature_dir is not None: return feature_dir, None`),
and I directly proved the resolver's own fail-closed behavior above, I judge this an
**IMPROVEMENT** (test-completeness), not a live defect — reasoned from code plus the resolver's
demonstrated behavior, not from a full end-to-end hook run.

## SC evidence

This cycle is GATE-ONLY / no BRIEF success-criteria segment dispatched to me; scope was the
fix-cycle diff and the panel's F1/F2/F3/F4/F5 findings, all addressed above with named tests.
