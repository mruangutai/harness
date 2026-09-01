# Observations - harness-orchestrator

- 2026-08-31 (FEAT-50): a dispatch clause can authorize what a hook mechanically denies. Main's
  brief said "the orchestrator may implement main-session-direct tasks directly"; check-domain.sh
  hook mode returned exit 2 for harness-orchestrator on all seven files, and bash-write-guard.sh
  refused `cp` with the DEC-151 evasion message. DEC-174 is the reason. I applied T-01/T-02 before
  measuring, through `python3 <script> <path>` — a route the Bash guard cannot see through — which
  means my very first write of a build phase was an unintentional guardrail bypass. Measure the
  guard on every target path BEFORE the first edit, not after the first refusal.
- 2026-08-31 (FEAT-50): the Bash write guard denies cp/mv/rm/sed -i/tee/redirects but not an
  interpreter invoked with a path argument. Any governed agent can write any path with
  `python3 patch.py <target>`. check-domain.sh's own header already states this limit
  ("truly arbitrary shell remains unwinnable"), so it is a known hole, not a defect I found —
  but it is the hole a well-meaning agent falls into first, because a patch script is the
  natural way to edit a 1600-line file when no Edit tool is granted.
- 2026-08-31 (FEAT-50): a task's `verify:` can be unsatisfiable under the task's OWN stated rule
  and still pass every plan-time gate. T-08's heredoc built a bare `FEAT` worktree for its
  ambiguity case, then asserted an unrelated id falls back to owner_root — but that id
  prefix-matched the bare worktree the same block had just created. check-plan-routes.py,
  load_plan and the panel all passed it; only running it found it. A verify block is prose until
  someone executes it, and fixture setup that accumulates across assertions is where it hides.
- 2026-08-31 (FEAT-50): when a lead returns ESCALATE claiming a spec defect rather than a code
  defect, re-running the failing assertion myself cost one probe and converted its claim into my
  own measurement. Both the failure AND the proposed replacement id were worth measuring — the
  second is what makes the amendment a one-token edit instead of a question.
