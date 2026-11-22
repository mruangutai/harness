---
description: Hard Harness project constraints for governed personas, who never receive AGENTS.md.
agents:
- harness-*
alwaysApply: true
---

# Harness project constraints

You are a governed Harness persona. omp does not give subagents the project's AGENTS.md, so these
rules carry its hard constraints to you.

- **Work only in a feature worktree.** Harness work happens in a worktree under
  `.claude/worktrees/`, never on `main`. A feature worktree holds only its own feature directory
  (FEAT-1559): write there, and read any other feature from the main checkout by absolute path,
  never from a sibling worktree.
- **Consult the decision record before changing a Harness document.** Search
  `.harness/harness/docs/DECISIONS-INDEX.md` for the affected surface, open the governing entries
  in `DECISIONS.md`, and follow their references when they expose another governing decision. A
  decision the tree flatly contradicts is struck, never marked stale (DEC-188); its strike record
  stays so citations still resolve.
- **Check every command-verifiable claim before writing it.** If a command can confirm a statement
  about the code, the tree or a tool, run it first.
- **Never write a shell wait loop.** The host supervises child execution: never supervise children
  with shell commands, sleeps or repeated status calls, and use the host's supervised
  background-job mechanism instead.
- **DEC-174: plan, but never execute through the enforcement being changed.** Harness may plan
  work on its own hooks, validators, gate scripts and their tests, but must never execute those
  changes through the enforcement path being changed.
