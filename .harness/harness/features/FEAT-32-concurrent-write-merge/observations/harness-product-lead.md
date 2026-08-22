# Observations — harness-product-lead — FEAT-32

- 2026-08-22: I passed `model: opus` in my first pm dispatch and `dispatch-guard.sh` blocked it,
  citing DEC-152/155. My own preloaded rule forbids it. The pull was "this judgement is hard" —
  which is exactly the red-flag wording in `harness-zero-micro-management`. Cost: one blocked call,
  no spawn lost.
- 2026-08-22: The covered-vs-new principle is at
  `notes/research-FEAT-32-t15-verify.md:8-10`, with worked precedent both ways in the same file
  (T-15 covered at :12-16, the #551 count not covered at :17-19) and the discriminator restated at
  :21-23. It is a notes file, not a decision entry — cite by that path until T-13 lands.
- 2026-08-22: `feature-worktree.py:34-38` says the dirty-tree gate constants are DECLARED by T-01
  and READ by T-02's `remove`. So "worktree removal refuses on a dirty tree" may be prospective or
  mid-write rather than on disk — the live eng run holds that file. I did not conclude from it; I
  handed it to pm. Lesson: a harm claim resting on an enforcer inside the feature's own build is a
  claim about unfinished code.
- 2026-08-22: `grep 'dirty tree|halts the next'` over `bin/` hits only four files
  (`feature-worktree.py`, `bash-write-guard.sh`, `test-bash-write-guard.py`, `merge-gitignore.sh`)
  and NOT `check-state.sh`. The "dirty tree halts the next team run" phrase is repeated in
  `.gitignore` comments and T-11's intent as if it named one enforcer; it may name none centrally.
- 2026-08-22: `Glob **/*.lock` over the whole worktree returns nothing, so a blanket `*.lock`
  rule cannot untrack an existing file today — the hazard the `gh-cost-*.jsonl` comment
  (`.gitignore:31-34`) warns about does not apply to it at this commit. That is a check on the
  present, not a guarantee about future tracked `.lock` files.
- 2026-08-22: I have no `SendMessage`, so I could not hand pm the mid-flight
  `feature-worktree.py:34-38` lead once its spawn was in the air. Anything a lead learns after
  dispatch reaches the member only via a send-back. Front-load the leads into the prompt.
- 2026-08-22: THE SECOND SURFACE nobody named. `.gitignore` is only this checkout. The rules the
  factory installs into every other repository live in
  `.claude/skills/harness/templates/gitignore.snippet`, merged by `merge-gitignore.sh:35` (which
  strips comments and matches whole lines with `grep -qxF`, :42). The snippet has 8 rules and no
  lock rule, so a repo-local `.gitignore` line closes this checkout and leaves every installed
  project with the same gap. Lesson: when a fix is a `.gitignore` rule about harness-produced
  files, always ask whether the installer template carries it too.
- 2026-08-22: Pre-existing drift, unrelated to FEAT-32 and NOT ours to fix here:
  `templates/gitignore.snippet:7` still says `.harness/features/*/runs/**` while this repo's own
  `.gitignore:7` says `.harness/*/features/*/runs/**`. The snippet is missing the `<repo>` segment
  the multi-repo migration (FEAT-21/22) introduced, so a freshly installed project does not ignore
  its own run dirs. Report as info, route to backlog.
