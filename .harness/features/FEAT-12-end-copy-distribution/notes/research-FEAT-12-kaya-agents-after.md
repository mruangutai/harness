# SC-04 agents clause — the missing after-capture, taken at goal-check time

**BLUF. Zero `harness-*.md` under kaya's `.claude/agents/`, and all three parent directories still
exist.** With `notes/kaya-agents-count-before.txt` = `16`, the pair SC-04 names is now complete and
non-vacuous. Captured 2026-08-10 by read-only inspection of
`/Users/molchairuangutai/GitHub/kaya-ai`, at kaya `master` = `7d2f946128896ec6c9c203c57e0cfe051d08de33`.

**Limitation, stated up front (rule 15).** This is a goal-check-time capture, not a capture taken at
T-02 time. It witnesses **the current working-tree state**, not the state immediately after the
deletion. SC-04 is worded against "`kaya-ai` at the state this feature leaves it in" (BRIEF:90), so
the end state is the graded object and this observation is of that object — but nothing here can
attest that the count was zero continuously since T-02.

**Nothing was written, moved or deleted in kaya.** Every command below is read-only. No git command
that writes was run, in either repository.

## Commands and verbatim output

`zsh` fails a non-matching glob before `ls` runs, so the counts were re-taken with `find`, which is
unambiguous and does not depend on shell glob settings. Both runs agree at 0.

```
$ cd /Users/molchairuangutai/GitHub/kaya-ai
$ ls -1 /Users/molchairuangutai/GitHub/kaya-ai/.claude/agents/harness-*.md 2>/dev/null | wc -l
(eval):1: no matches found: /Users/molchairuangutai/GitHub/kaya-ai/.claude/agents/harness-*.md
       0

$ find .claude/agents -maxdepth 1 -name 'harness-*.md' | wc -l
       0
$ find .claude/skills -maxdepth 1 -name 'harness*' | wc -l
       0
$ find .claude/commands -maxdepth 1 -name 'harness*.md' | wc -l
       0
```

`-maxdepth 1` is deliberate: `.claude/worktrees/` is a sibling of `.claude/skills/`, not a child, so
the six worktrees are outside every glob above by construction. SC-04 is worded against
`.claude/skills/`, which they are not under (BRIEF `## Constraints`).

Parent directories — the presence half:

```
$ for d in .claude/agents .claude/skills .claude/commands; do test -d "$d" && echo "EXISTS  $d" || echo "MISSING $d"; done
EXISTS  .claude/agents
EXISTS  .claude/skills
EXISTS  .claude/commands
```

Directory contents, which settle "empty" against "deleted":

```
$ ls -1 .claude/agents
                       (no output — empty directory)
$ ls -1 .claude/skills
                       (no output — empty directory)
$ ls -1 .claude/commands
review-team.md
$ ls -1 .claude
agents
commands
hooks
scheduled_tasks.lock
settings.json
settings.local.json
skills
worktrees
```

`review-team.md` — the non-harness file SC-04 requires to survive — is present.

Repository state at capture:

```
$ git rev-parse --abbrev-ref HEAD ; git rev-parse HEAD
master
7d2f946128896ec6c9c203c57e0cfe051d08de33
$ git status --porcelain | head -5
 M .harness/features/FEAT-03-live-review-loop/feature.yaml
 M pyproject.toml
 M uv.lock
$ find .claude/worktrees -maxdepth 1 -mindepth 1 -type d | wc -l
       6
```

## Why filesystem inspection was the only method available

```
$ git log --oneline -5 -- .claude/agents
                       (no output — no commit has ever touched this path)
$ git check-ignore -v .claude/agents .claude/skills .claude/commands ; echo "exit=$?"
exit=1                 (none of the three is gitignored)
$ git log --oneline -3 -- .claude/skills
7d2f946 Remove the copied harness: this repo is worked on remotely, not enrolled
1ad0f1d chore(.harness): FEAT-03 ship state — 18/18 SCs, owner-scoped learnings, map refreshed at 006e138
98a0102 chore(.claude): harness deploy update — bash-write-guard hook, refreshed skills and templates
```

The 16 agent files were **untracked and un-ignored local files**: no commit ever touched
`.claude/agents`, so their deletion produced no commit content and no remote-side evidence was ever
obtainable. This is not an oversight in T-02's capture design — it is the reason the BRIEF grades the
agents clause against the working tree while grading skills and commands against `origin/master`
(BRIEF:95-102). The commit that removed the tracked half is `7d2f946`, kaya `master` HEAD.

## Corroboration for the skills and commands clauses — not the grading evidence

The grading evidence for those two clauses stays T-05's captured `REMOTE_CLEAN`
(`feature.yaml kaya_push`), which asserts against `origin/master`. The working-tree counts above are
corroboration only. One further corroborating read at this capture:

```
$ git ls-files '.claude/agents/harness*' '.claude/skills/harness*' '.claude/commands/harness*' | wc -l
       0
$ git ls-tree -r --name-only origin/master -- .claude | grep -c 'harness'
0
```

## Open items this capture does not touch

- SC-05 stays `partial`. The pre-deletion state is gone; byte-identity can never now be evidenced.
- Kaya's working tree currently shows ` M .harness/features/FEAT-03-live-review-loop/feature.yaml` —
  a content-level modification inside the tree SC-05 is worded against. This is an observation for
  the operator weighing "accept SC-05 on path-set equality" against "restate SC-05", **not** a
  re-grade of SC-05, which stays `partial` on its recorded reasoning.
