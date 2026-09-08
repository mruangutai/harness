# UI Review — BUG-1480-handoff-note-checkout-root — c0 (Mode B, pinned `review_sha` 4de92e75)

## Verdict: PASS — no rendered UI surface in scope; one adjacent operator-facing text
finding graded and rated non-gating (LOW).

## 1. Census — complete changed-file set (`git diff --stat 64fcaa34..4de92e75`)

18 files changed, +1436/-1. Extension census across all 18: **zero** hits for
`html|css|scss|tsx|jsx|vue|svelte|less` (measured with `git diff --name-only | grep -Ei`,
count = 0). Breakdown:

- **2 code files** — the entire behavioral change: `.claude/skills/harness/bin/check-domain.sh`
  (+15/-1, the `_checkout_root` helper + one call-site argument swap) and
  `tests/integration/test-check-domain.py` (+42, the `_handoff_worktree_cases` test rows).
- **16 harness bookkeeping files** — `BRIEF.md`, `STATE.md`, `feature.json`, `plan.yaml`,
  `observations/harness-pm.md`, and 11 files under `notes/` (receipts, research notes, repro,
  qa report, plan-panel review). All markdown/YAML/JSON process artifacts describing the
  feature's own plan/review/QA trail — none is a rendered UI surface, none is a design
  contract for a built surface.

No `.tsx`/`.jsx`/`.vue`/`.svelte`/`.css`/`.scss`/`.less` anywhere in the diff. This is a pure
CLI-hook + test-suite change with zero rendered UI.

## 2. DESIGN.md / verify:uat check

- `<feature-dir>/DESIGN.md` — **absent** (`test -f` confirms: ABSENT). No design contract
  exists or was expected for this feature — correct, there is nothing rendered to contract.
- `BRIEF.md` `verify:` values — confirmed by direct grep, all 7 criteria are
  `verify: automated` (SC-01..SC-03) or `verify: inspection` (SC-04..SC-07). **Zero**
  `verify: uat` rows. Dispatch's expectation confirmed.

Mode A finding: n/a — no contract to grade, correctly so.

## 3. The one arguably-user-facing surface: the refusal-message text

Ruling: **in my lens** — `check-domain.sh` emits operator-read text on a blocked write, which
this role's repo-tier Expertise (P-01/P-03) already treats as an adjacent CLI/hook-emitted text
surface when a diff has no rendered UI. Graded below rather than declined.

**What the fix changed.** Pre-fix, `shape_problems`'s `RE_HANDOFF` branch always called
`handoff_done_when.problems(rel, content, root, resolve=True)` — `root` was unconditionally the
*main* checkout, even when the handoff note being validated stood inside a linked worktree. For
a worktree-standing note, every `plan-task:`/`brief-sc:`/`finding:`/`approval:` pointer resolver
inside `handoff_done_when.py` (`_resolve_plan`, `_resolve_brief`, `_resolve_finding`,
`_resolve_approval`, all read at `handoff_done_when.py:116-183`) then built its `target` Path by
joining onto the WRONG root — the note's own feature directory doesn't exist under the main
checkout, so every pointer spuriously failed to resolve. Post-fix, the call site
(`check-domain.sh`, `shape_problems`, `RE_HANDOFF` branch) passes
`_checkout_root(absolute_path)` instead, which correctly returns the worktree's own checkout
root when the note stands there.

**Measured, live**: ran `_handoff_worktree_cases`' own fixture shape directly (scratch
`tempfile.TemporaryDirectory` + `make_linked_worktree`, a `brief-sc:SC-99` pointer in a
worktree-standing handoff note). Actual stderr on the fixed code:

```
Authority pointer 'brief-sc:SC-99' is unresolved in
/private/var/folders/y3/nd_jssrd5dq8lbds73f0fy5m0000gn/T/tmpclcz0qqr/.claude/worktrees/harness/
BUG-1480-wt/.harness/harness/features/BUG-1480-wt-fixture/BRIEF.md: success criterion SC-99 was
not found
```

The path now correctly reaches inside the worktree (the bug this feature fixes) — but it is
spelled with the **realpath-resolved** root (`/private/var/...`), not the root as the caller
addressed it (`tempfile.TemporaryDirectory()` itself returned `/var/folders/...`, confirmed by
`os.path.realpath()` diffing the two strings in the same run). Traced why: `_checkout_root`
delegates to `harness_boundary.worktree_owner(path)`, whose first line is `cur = real(path)` —
`real()` is abspath *and* symlink-resolved (its own docstring names this exact case: `"/var" on
macOS is itself a link to "/private/var"`). By contrast the OLD, always-passed `root` value
comes from `resolve_root()`, which uses `os.path.abspath` only — never realpath — so it always
preserved the caller's typed spelling. The fix is therefore not spelling-neutral: it trades a
wrong root (pre-fix, worktree case) for a right-but-differently-spelled root (post-fix, worktree
case); the non-worktree case (the overwhelming majority: `_checkout_root` returns the shared,
unresolved `root` unchanged whenever `real(_ck[0]) == real(root)`) is untouched.

**Rating: LOW, non-gating.** The printed path is not wrong and not un-actionable — `/var` is a
transparent symlink to `/private/var` on macOS, so the exact string an operator sees still `cd`s,
`cat`s, and opens correctly; nothing is broken or misleading in a way that sends anyone to the
wrong file. It is a one-hop-of-recognition cosmetic inconsistency (a shell session that's been
addressing the same tree as `/var/...` sees an unfamiliar `/private/var/...` spelling in the
refusal), not a functional defect, and it only surfaces in the specific case this diff newly
makes reachable (worktree-standing handoff notes) — it does not regress the existing majority
path. Does not meet the `severity_max >= high` gate; does not belong in `must_fix`.

## must_fix: []

```yaml
VERDICT: PASS
DIGEST:
  headline: "No rendered UI surface in this diff (0/18 files, extension census confirms); one adjacent operator-facing refusal-message finding graded and rated LOW, non-gating."
  mode: B
  in_scope: true
  severity_max: low
  findings: 1
  must_fix: []
  states_unspecified: []
  contract_violations: []
  a11y: []
  open_questions: []
  files_touched: []
  expertise_update: []
artifact: /Users/molchairuangutai/GitHub/harness/.claude/worktrees/harness/BUG-1480-handoff-note-checkout-root/.harness/harness/features/BUG-1480-handoff-note-checkout-root/notes/review-harness-ui-reviewer-c0.md
```
