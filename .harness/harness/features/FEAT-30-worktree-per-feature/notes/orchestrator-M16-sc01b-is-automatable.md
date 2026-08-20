# M-16. SC-01b's core IS automatable and CAN go red. Measured, 12 trials, not inferred.

Run 2026-08-20 while the amend round was in flight, so that the operator's instruction
("automate that test for me and budget for failure") is priced on a measurement rather than on
the previous round's assumption. Probe script:
`scratchpad/probe_concurrent_commits.py` (throwaway; every repo is a temp dir, nothing touches
this checkout).

## What was driven

The real shape, twelve times: **two throwaway repositories, two worktrees each at
`<repo>/.claude/worktrees/<repo>/<id>`, four committers running concurrently on a thread pool.**
Each committer does what an orchestrator does — writes its own file, stages it **by pathspec**,
commits with a `[harness:<id>]` message.

Then the **discriminating negative**: the same four writers against ONE checkout per repository,
no worktrees — today's shape.

## Result

    TRIALS                     12
    isolated-shape failures     0
    negative fixture detected   4 collision signal(s)
      repoA: HEAD carries foreign file FEAT-A2.txt
      repoA: HEAD carries foreign file FEAT-A1.txt
      repoB: HEAD carries foreign file FEAT-B2.txt
      repoB: HEAD carries foreign file FEAT-B1.txt

**Assertions were made per tree, never in aggregate**: each branch tip carries its own file; each
branch's FULL history (`ls-tree -r`) carries no other feature's file; each worktree's `HEAD` names
its own branch; each branch points at its own committer's returned sha.

## The three things this closes

1. **No concurrency flakiness.** Worktrees of one repository share `.git/refs` and `packed-refs`
   but hold separate index files, and four branches are four distinct ref locks. Twelve trials,
   zero contention failures. A concurrency test that is flaky by construction would be worse than
   the `uat` it replaces; this one is not. Twelve is the reason the count is stated — one green run
   of a concurrency test proves nothing.
2. **It can go RED.** The negative fixture is detected four ways. This is the FEAT-29 failure mode
   answered directly: twelve green-and-incapable-of-red assertions shipped there, and a
   four-worktree test that passes when isolation is broken would be the same defect wearing this
   feature's name.
3. **The subprocess route is unaffected by the guards** — corroborating the architecture review's
   attributed claim (Q10). Every git call above was a `subprocess` fork inside a `python3` script,
   which presents no `git` token to a Bash tool call. So the guards govern an agent's own typed
   commands and cannot interfere with an integration test that drives git this way. This is what
   makes an automated SC-01b buildable at all, and it is now measured rather than inherited.

## What automation still cannot reach — state this, do not let it pass as covered

My writers are threads, not live orchestrators. The probe proves the **isolation property**; it
does not prove **agent behaviour** — whether an LLM orchestrator addresses its tree by absolute
path, stages by pathspec, and does not move `HEAD`. That residue is REQ-05/SC-06's and T-05's job,
not SC-01b's.

The rest of SC-01b's stated substance is **already out of scope by the operator's own ruling**:
`BRIEF.md:202-204` excludes the shared GitHub API budget, and the board is the same single-writer
root from another direction. So "four live orchestrators contending for the same account budget and
the same board" asserts, as a success criterion, two things this brief deliberately does not fix.
The Expertise-file third is REQ-06/SC-08, already `verify: automated`.

**Conclusion: the `uat` was not forced by the mechanism.** What is irreducibly human here is
narrower than SC-01b's text claims, and what is mechanizable is the part that actually carries the
isolation guarantee.
