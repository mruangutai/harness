# Plan-panel scope review — BUG-240 — cycle 1 `plan.yaml`

**BLUF: PASS, no must_fix.** Spec compliance is clean (no orphan REQ/SC, no scope creep, no
omission, `verify:` blocks are literal `|`). The two findings below are both advisory
(med, low) — neither reproduces one of the five already-repaired items, and neither is caused by
the repair itself. `code_grade: n_a` — plan-phase review, no commit exists.

## Stage 1 — spec compliance

Traced both directions against `BRIEF.md`'s REQ-01..06 / SC-01..06 (`plan.yaml:35,147` `traces:`
and `success_criteria:`): no orphan REQ, no task citing a nonexistent REQ/SC, no requirement
without a discharging task. `depends_on: []` / `[T-01]` is the correct test-first order and T-02's
`verify:` needs nothing T-01 fails to leave behind — T-01 writes the test file only
(`files: [tests/unit/test-factory-workspace.py]`), T-02 edits only the production file
(`files: [.claude/skills/harness/bin/factory_workspace.py]`), matching each task's `intent:`
exactly. Both `verify:` blocks use the required literal `|` form. No scope creep found: the
docstring-update instruction in T-02 (`plan.yaml:206-210`) is minimal and exists only to keep
case 7's negative textual tripwire (REQ-06) honest — not an added feature.

## Stage 2 — quality of the specification

### Finding 1 — med — `_control_plane_root()`'s real resolution path has zero test coverage
`.claude/skills/harness/bin/factory_workspace.py` (T-02 intent, `plan.yaml:161-165`) delegates
self-identity to `harness_boundary.resolve_root(_BIN_DIR, strict=False)`
(`harness_boundary.py:66-93`). That resolver honours an `HARNESS_PROJECT_DIR` env override
*before* falling back to the arithmetic-derived root — if the override is set and carries
`MARKER`, it is returned **silently, with no warning**, regardless of `strict`
(`harness_boundary.py:78-81`). Both of T-01's cases that are supposed to exercise REQ-01 (case 5,
`plan.yaml:116-134`, and case 6, `plan.yaml:...`the other-harness-checkout negative) install
`fw._control_plane_root` as a hardcoded `lambda`, per the repaired sentinel `setattr`/`delattr`
discipline. Neither case, nor any other in the suite, ever calls the *real*
`_control_plane_root()` and checks what it resolves to. Consequence: if `HARNESS_PROJECT_DIR`
is ever set in the environment a live claim runs under, to any *other* onboarded harness
checkout, `_control_plane_root()` returns that other checkout instead of the one this code is
physically running from; the identity guard then compares `path` against the wrong root, and a
genuine self-checkout collision — the exact 2026-08-10 near-miss `BRIEF.md` describes — is not
refused. No case in the plan would redden on this regression. Rated **med, not high**: repo-wide
grep (`.claude/skills/harness/bin`, whole worktree) found `HARNESS_PROJECT_DIR` set only inside
test fixtures, never by any production dispatch/launch path for `factory_workspace.py` itself
(the PreToolUse hook chain uses the host-owned `CLAUDE_PROJECT_DIR` instead — a different
variable this resolver deliberately does *not* read), so the trigger is real and unguarded but
not shown to occur on any live-claim code path today. Not a must_fix; worth a case exercising the
un-mocked resolver (e.g. asserting `_control_plane_root() == harness_boundary.root_from_script(fw._BIN_DIR)`
with the env var absent, and a case showing the override IS honoured) if PM wants REQ-01's identity
premise actually pinned rather than merely assumed.

### Finding 2 — low/info — D-01's containment reasoning is asserted, never exercised
`plan.yaml`'s `decisions: D-01` argues the *containment* case (computed `path` is an ancestor of
the control-plane checkout) needs no dedicated refusal because "a nested checkout is
untracked-not-ignored content" under the dirty check. No case in T-01 builds that fixture (a real
nested `.git` inside the guarded checkout) to confirm `git status --porcelain` actually reports it
as dirty rather than, say, being swallowed by an ambient `.gitignore` rule. Not blocking — D-01 is
a documented design decision, not a REQ, and the reasoning is ordinarily reliable git behaviour —
but the premise ships unverified.

## Findings

| # | Severity | Summary |
|---|---|---|
| 1 | med | `_control_plane_root()`'s real `resolve_root`/`HARNESS_PROJECT_DIR` path is never exercised by any case; both REQ-01 cases replace it with a lambda, so a spoofed/overridden root would sail through unrefused with nothing to catch it. |
| 2 | low | D-01's containment claim (nested checkout reads dirty) has no fixture confirming it. |

No must_fix. No re-raise of the five cycle-1 repaired items (occurrence-count clause, case-5
wrong-reason-red, case-6 tautology, ordering assertion, case-5 fixture) — all five read correctly
in the plan on disk, and neither finding above touches the repaired text.
