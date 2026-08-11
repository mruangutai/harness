# Observations — harness-pm — FEAT-12

- 2026-08-10: correcting a falsified BRIEF premise, I re-ran the four-phrase sweep tree-wide at
  835b297 instead of only over T-14's verify path roots. Two sites the plan never surveyed
  surfaced: `.claude/skills/harness/templates/team-config.yaml:46` (INSIDE the sweep root, edited by
  no task, so T-14's verify cannot pass as written) and `.harness/team-config.yaml:44` (outside every
  sweep, so REQ-07 is unmet and invisible). Both carry the same comment string
  "shipped by deploy — REPLACED WHOLESALE on every push". The wide re-run found them; checking my
  wording only against the check's own path list would have missed both.
- 2026-08-10: `D-03`'s `because` in plan.yaml is a plain scalar containing " #202's". YAML reads
  " #" as a comment start, so `safe_load` returns the string `'issue'` — the whole rationale vanishes
  silently, and `check-plan-routes.py` still exits 0. Any plan.yaml plain scalar carrying a GitHub
  issue reference has this shape.

- 2026-08-10 (send-back cycle 1): the two team-config files carried a falsified trailing comment
  pair that NO clause in the plan could see. One half ("replaced wholesale on every") tripped T-14's
  wide grep, so the plan failed at its own gate while T-11 passed green on a narrower pathspec; the
  other half ("deploy never touches it") matched no pattern anywhere and would have shipped. Lesson:
  when a task's verify pathspec is narrower than a downstream task's grep over the same tokens, the
  downstream task is the real survey and the narrow one is a blind pass. Run the downstream pattern
  over the whole tree at plan time and check every hit is assigned to a task.
- 2026-08-10: D-02's `because` truncates at "touches ground that" for the same `#206` reason as
  D-03. Measured with safe_load; left unfixed under an explicit freeze and reported instead.

- 2026-08-10 (send-back cycle 2): I wrote "56 harness skill trees under `.claude/worktrees/`,
  untracked and gitignored" into a signed BRIEF constraint from a `grep -r`/`git status` inference,
  never a `ls-files`. Measured: three of six worktrees, 153 files, all TRACKED on their own branch;
  `.gitignore:23` ignores only the container in the MAIN tree. The trackedness inverted the
  deferral's meaning — permanent residue became transient, cleared per branch on its next `master`
  sync. Sibling-worktree absence from `git status` is evidence about the parent tree's ignore
  rules, never about the child tree's index. Same defect shape as the R-9 sentence I had just been
  sent to delete, which is what makes it worth recording: eliminating one instance of a shape does
  not immunise the next paragraph.
- 2026-08-10: a narrowing landed in a REQ must be carried into `## Goal` in the same edit. I
  narrowed REQ-03 and rewrote Problem and SC-04, and the Goal — the paragraph the operator actually
  reads first — kept the unqualified claim, putting two contradictory statements inside one signed
  document. Grep the whole artifact for the claim's tokens after narrowing anything, not just the
  sections the send-back cited.
