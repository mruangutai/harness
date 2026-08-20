# Observations — harness-orchestrator — FEAT-30-worktree-per-feature

## The expensive one

- 2026-08-20: **a digest file on disk is a CHECKPOINT, not a return.** A lead wrote a terminal
  `BLOCKED` digest saying its member was in flight; I measured the disk, found the member's artifact
  absent, and re-dispatched the round. The lead was still alive: it got more turns, its member
  returned PASS, and it overwrote its own digest with the real verdict. My re-dispatch was therefore
  a duplicate spawn of a member that owns the single most contended file in the feature. The check I
  skipped was free: the agent had not notified me yet. **Absence of the artifact proves the member
  has not finished; it does not prove the run is dead.** Only the completion notification does.
  Mitigation once I saw it: snapshot the verified file, then verify any later write against the
  pre-written criteria rather than assuming the later write is the good one.

## Probing guards

- 2026-08-20: probing a guard is vacuous unless the probe carries a GOVERNED `agent_type`.
  `bash-write-guard.sh` exempts `harness-dev-ops` (DEC-151), so my first three probes all exited 0
  and I nearly read that as "creation is permitted everywhere". Re-run as `harness-backend-dev` and
  `harness-orchestrator`, the served-repo destination exited 2. Same command, same file, opposite
  verdict — the agent_type IS the experiment.

- 2026-08-20: which SESSION ROOT a probe uses decides the verdict, and this nearly inverted a plan.
  Write route, same target inside a REAL two-level worktree: session rooted IN the worktree exits 0;
  session rooted in the outer checkout writing INTO it exits 2. Only the second shape exercises the
  refusal, so a test rooted in the worktree is green today and incapable of going red.

- 2026-08-20: a guard's blast radius is bigger than the site you found. I found one duplicated
  worktree strip; pm found two more (a sweep glob and a shape normaliser) and then found that the
  resolve path shares the constant, taking the count from 2 to 21 affected assertions. Three tiers
  each under-counted, each in good faith, each having read the code. Grep for the CONSTANT and for
  every literal spelling of it before quoting a number.

## Being wrong in public

- 2026-08-20: I recorded a measured conclusion ("the served-repo half is blocked and needs a guard
  task") that was true of the command I probed and false of the design the plan actually used, and it
  had already travelled one tier down as a staged send-back item. Correcting it in place, marked as a
  correction, cost one paragraph; leaving it would have bought an unnecessary enforcement-layer task.
  Two other tiers did the same thing on their own findings in the same run. A correction that names
  what it supersedes is cheap; a quiet deletion is what makes the record unusable.

- 2026-08-20: I recommended a fixture module I had not opened. It was 75 lines of stub DATA with one
  function and no ability to build a repository, and the mistake reached a member's dispatch prompt
  before a lead caught it. Read the file before naming it as a tool.

## Guard mechanics worth remembering

- 2026-08-20: the Bash guard's write-target extractor parses HEREDOC CONTENT as shell. Prose
  containing an angle-bracket placeholder read as an input redirect and my own append was denied
  naming a target that appears nowhere in my intent. Documentation about git or shell cannot reliably
  be written through the Bash route; use the Write tool.

- 2026-08-20: the creation door reads the LITERAL Bash string, so a destination in a shell variable
  is refused as relative even when it resolves legally, and a helper SCRIPT that forks git presents
  no git token at all, so the door never fires. A door on the Bash route is not a door on the
  capability.

- 2026-08-20: measure the removal path rather than planning for it. Removing a worktree holding one
  untracked file exits 128 and names the reason, so refuse-on-dirty is git's own behaviour; the same
  removal with the force flag passes the guard at 0. That turned a planned detector into a one-line
  parser addition.

## Baselines

- 2026-08-20: a whole-repository violation count is a shared mutable global, not a baseline. The same
  command in the same checkout reported 2 violations at 07:41 and 3 at 08:07 because another flow's
  BRIEF appeared. Scope a baseline to the feature, or it is falsified by work that has nothing to do
  with it.
