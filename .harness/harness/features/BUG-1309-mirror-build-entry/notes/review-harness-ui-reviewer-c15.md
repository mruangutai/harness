# UI Review — BUG-1309-mirror-build-entry — c15 (Mode B, self-scoped)

## Verdict: PASS (out of primary scope; advisory glance only)

## Measured scope check

`git diff --stat da6da610..e374c9a2` at pinned `e374c9a2` touches exactly four files:
`.claude/skills/harness/bin/merge-gate.py`, `tests/integration/test-merge-gate.py`, and this
feature's own `STATE.md`/`feature.json`. Extension census
(`git diff --name-only da6da610..e374c9a2 | grep -Ei '\.(html|css|scss|tsx|jsx|vue|svelte|less)$'`)
returns **0 matches**. No `DESIGN.md` exists for this feature — confirmed by direct object check
(`git ls-tree -r e374c9a2 -- .harness/harness/features/BUG-1309-mirror-build-entry/`, full listing
enumerated, no `DESIGN.md` present, and no `design` hit under that path at any point in history for
this feature). There is a `ship-review-2026-09-08-resume.html` under this feature's `notes/`, but it
is not in the reviewed delta's file list and is this repo's known generated ship-review artifact
(repo-tier P-02), not product UI.

**No user-facing rendered surface and no design contract exist for this delta.** Self-scoping out of
Mode B per the dispatch's own criterion.

## Adjacent CLI-text glance (per dispatch instruction — treated in-remit)

Dispatch named the operator-facing denial/stderr region as worth a glance. Confirmed by
`git diff da6da610..e374c9a2 -- .claude/skills/harness/bin/merge-gate.py`: the change is entirely
inside `git_merge()`'s token walk (the branch-extraction parser). **None of the `deny()`/`print()`
message strings were touched by this delta** — every denial/notice string in the file (duplicate-owner
deny, era-exempt allow-notice, repo-unpinned deny, the terminal build-entry deny, the exception-path
deny) is pre-existing text, byte-identical before and after this delta.

Since the question is worth answering per dispatch: the denial path this fix newly makes reachable —
`build_entry` in `{"recovery-required"}` or absent, `github.sync` true, single owner, non-era-exempt
(`merge-gate.py:185`, reachable via the corrected parser) — **does** name an actionable next command:
`This merge is denied until {command_line} records one.`, where `command_line` is a concrete,
resolved `python3 .claude/skills/harness/bin/gh-sync.py <command> <absolute-feat-dir> [--yes]`
(`merge-gate.py:183-184`). The repo-unpinned deny (`merge-gate.py:181`) likewise names a concrete
`gh repo view --json nameWithOwner -q .nameWithOwner` command. The duplicate-owner deny
(`merge-gate.py:109` region) names the field to correct, not a command, but is explicit that "no
receipt command clears this" — also actionable, just not a single command line. Only the generic
exception-fallback deny (`merge-gate.py:187`, "Repair the feature record and re-run the merge.") is
vague, and it is pre-existing, untouched, and off the SC-04(a) path this feature targets.

**This is a confirmation, not a finding** — nothing here was authored or altered by this delta, so
there is no new CLI-message defect to file against it. No fix is owed by this cycle.

## Verdict detail

- `severity_max: none` — no in-scope UI surface, and the advisory CLI-text check found no
  delta-introduced defect.
- No open questions.
