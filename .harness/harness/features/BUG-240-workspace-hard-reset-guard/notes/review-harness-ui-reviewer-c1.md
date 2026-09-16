# UI review — BUG-240 — cycle 1 — Mode B (re-panel over fixed pin `bae47f3c`)

## Scope measured (not predicted)

- `git ls-tree -r bae47f3c -- .harness/.../BUG-240-workspace-hard-reset-guard` (excluding
  `notes/`/`observations/`) lists only `BRIEF.md`, `STATE.md`, `feature.json`, `plan.yaml` — no
  `DESIGN.md` at the pinned SHA. No rendered-UI or design-contract file exists for this feature.
- `git diff 6d969ed3..bae47f3c --stat -- .claude/skills/harness/bin/factory_workspace.py
  tests/unit/test-factory-workspace.py`: 2 files, +290/-3, matching the batch context exactly.
- Full-diff extension census (`git diff 6d969ed3..bae47f3c --name-only | grep -E
  '\.(html|css|scss|tsx|jsx|vue|svelte|less|md)$'`) against the broader diff range: zero
  html/css/scss/tsx/jsx/vue/svelte hits; the only `.md` matches are Harness bookkeeping under
  `.harness/.../notes/` and `observations/` (BRIEF, STATE, receipts, review notes) — control-plane
  record-keeping, not product UI, consistent with repo Expertise P-01/P-02.
- Per dispatch, the two adjacent non-rendered operator surfaces are in remit: `factory_cli.refuse`
  copy and the `run_git` stderr line. Both read in full via `git show bae47f3c:<path>`.

**Verdict on scope:** no rendered UI, no `DESIGN.md`. Self-scoping out of Mode B proper; auditing
the two named adjacent CLI surfaces per dispatch, matching the cycle-0 disposition.

## Refusal copy — byte-unchanged from cycle 0 (confirmed, not assumed)

Diffed cycle-0's quoted composed strings (from `review-harness-ui-reviewer-c0.md`, itself audited
against the pre-fix `ed047fde` tree) against the pinned-SHA source
(`git show bae47f3c:.claude/skills/harness/bin/factory_workspace.py`, lines 153/166 — shifted from
c0's 143/156 only because the `samefile`/`OSError` fallback block inserted 12 lines above them,
not because wording changed):

- Identity: `what="refusing to reset the harness control-plane checkout"`, same `next_step`
  ("the control plane is never its own scratch workspace: point workspace_root in fleet.yaml at a
  directory that is not this checkout") — **byte-identical** to c0.
- Dirty: `what="refusing to reset a checkout with uncommitted changes"`, same `next_step`
  ("commit, stash or discard the work in that checkout, or point workspace_root at a scratch
  directory") — **byte-identical** to c0.

Both still populate all four `factory_cli.refuse(tool, what, value, next_step)` fields
(`value=os.path.abspath(path)` in both), so REQ-03 (path + which condition + exit status) remains
satisfied exactly as c0 found it. No new refusal call site was added by the fix — the fix only
changes *how* `is_control_plane` is computed (`os.path.samefile` with a `realpath`-equality
`OSError` fallback), never the message that follows.

**restates F-PANEL-04** (low, non-gating, already assessed as backlog): the two new `what` strings
still fold the refusal verb into the fact ("refusing to reset …") where the ~20 sibling
`factory_cli.refuse(` call sites across the repo use a noun-phrase fact only. Confirmed unchanged
at the pinned SHA — not a new instance, the same one c0 filed. Not presented as blocking.

## `run_git` stderr surface — untouched by this diff

`git diff 6d969ed3..bae47f3c -- factory_workspace.py` shows only three hunks: the docstring
paragraph, the `import harness_boundary` / `_control_plane_root()` addition, and the new
identity/dirty-check block inserted into `_main()` before the existing clone/refresh logic. No
hunk touches `def run_git(...)` (line 60) or its stderr handling — it is bit-for-bit what cycle 0
already reviewed. No new finding.

## Adjacent test-output surface (advisory, not required scope)

New BUG-240 case 8 (case-mismatched self-checkout) self-skips on a case-sensitive filesystem via
`print("skip  BUG-240 case-mismatched self checkout: filesystem is case-sensitive, premise does
not apply here")`. Format (`"skip  "` + description, two-space gap) matches the one other skip
site in the suite (`tests/integration/test-gh-sync.py:1114`, `print("skip  abandon with an
unreadable reason file exits 1 …")`) — consistent house convention, no legibility or attribution
defect. Not gating; recorded for completeness since it's new operator-visible text in this diff.

## Not applicable

Accessibility / theme parity / rendered layout: not applicable — this diff produces only batch
stderr/stdout text, no colour encoding, no visual surface to render. Confirmed not-applicable
rather than omitted, consistent with c0.

## Verdict

**PASS.** F-PANEL-01 is not this role's finding to close or reopen (security-reviewer's), but the
refusal copy it gates through is confirmed wording-unchanged and still spec-compliant. No must_fix.
One low-severity, already-assessed advisory restated (F-PANEL-04) — non-gating per batch context.
