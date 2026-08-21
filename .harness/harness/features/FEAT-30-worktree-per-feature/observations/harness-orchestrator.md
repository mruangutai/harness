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

- 2026-08-20: a runner's own drift detector turns a half-landed task set into a broken tree.
  `run-unit-tests.sh` globs `bin/test-*.py` and exits 2 on any file absent from its explicit arrays,
  so the moment T-01 created a test file every `--kind` exited 2, and stayed that way until T-08
  registered it. Committing a partial lane there would have shipped a suite runner that cannot run.
  The window was invisible from the task list; only invoking the runner showed it.

- 2026-08-20: two guard suites give a FALSE RED from the wrong cwd. `test-check-domain.py` and
  `test-bash-write-guard.py` report 13/14 and 25/27 with exit 1 from inside `bin/`, and 14/14 and
  27/27 with exit 0 from the repository root, because their worktree-boundary cases resolve against
  the current directory. I nearly reported a red suite; the cwd was the entire difference.

- 2026-08-20: a bare `^PASS ` count conflates two granularities in this runner's output — script
  lines and per-check lines. The coarse numbers (179 unit / 90 integration) move whenever anyone adds
  an assertion anywhere; the script-level counts (18 and 12, `grep -c '^PASS test-'`) are the ones a
  registration task actually changes and the only ones worth asserting on.

- 2026-08-20: a decision's summary and its task's intent disagreed and the intent was right. D-01
  named three subcommands for the new CLI; T-01's intent specified a fourth (`path`), and the member
  built four. Because the team file makes `intent:` the dispatch text, the intent is the executable
  spec and the decision text is prose — so check the intent before calling a delivered surface scope
  creep. Verifying it cost one grep and saved a fix cycle.

- 2026-08-20: a criterion's quantifier is checkable cheaply. "All sixteen governed agents" resolved to
  exactly 16 distinct `harness-*` entries in team-config.yaml, with `main-session` correctly absent —
  which is what makes the HEAD refusal scope coherent rather than a round number someone repeated.

- 2026-08-20: I structurally CANNOT re-run this plan's red proofs. Every one begins
  `cp -R .claude/skills/harness/bin "$T/bin"`, and the write guard blocks the orchestrator's `cp` to
  a mktemp path as outside its domain — correctly, and it names guardrail evasion if you switch
  tools. So a mutation proof is a member capability, not mine. The consequence for dispatch: demand
  the ACTUAL command output of every red proof in the digest, because "the red proof passed" is a
  claim I have no way to re-measure. I can still run the plain suites, which need no copy.

- 2026-08-20: both of this run's send-backs were about EVIDENCE, not code. T-02 landed green but its
  neutered proof contained no SC-07 dirty case; T-06 landed green but declared artifacts in
  `files_touched` it never wrote. Neither was a logic defect and neither would have been caught by
  the task's own `verify:`. A lead that only routes and relays would have returned both as PASS.

- 2026-08-20: `feature.json` admits NO blocked status. The schema allows only Backlog, Plan, Ready,
  Building, Review, Done, Abandoned - mirroring the board stations - so a feature halted mid-build
  stays `Building` and the blockage exists only in STATE.md and the digest. Do not invent `Blocked`;
  the shape gate rejects it and the correct value is the phase you are halted inside.

- 2026-08-20: a signed intent and an existing invariant test can contradict each other with NO task
  owning the remedy, and the runner-red window hid it until the registration task first invoked the
  runner. Both candidate fixes crossed an authority line - one edits a file in no task's `files:`, the
  other departs from signed text - so the correct move was a ruling request with a recommendation and
  a measured cost on each side, not a fix dispatch. What made the recommendation decidable was
  checking whether the signed clause was ASSERTED anywhere: it was not, which priced the cheap option
  honestly instead of defending the plan's letter.

- 2026-08-20: when a lead reports a contradiction it "could not run the discriminating check" on, look
  for whether the answer is WHO rather than WHAT. Two spawns got opposite results from one command
  because `bash-write-guard.sh` early-returns for no `agent_type` and for `harness-dev-ops`; I had
  reproduced the denial myself, so four data points settled in one read what the lead could not settle
  at all.
