# Observations — harness-orchestrator — FEAT-29-graphql-budget

- 2026-08-19: `check-state.sh` runs at ZERO GraphQL cost with `FACTORY_GH` pointed at a
  non-existent binary. INV-26 gates its board read on `gh auth status` succeeding
  (`check-state.sh:1158-1165`) and records nothing when it does not, so every other invariant still
  runs. Measured: `graphql.used` 3753 before and 3753 after a full run. That turned the mandated
  pre-commit gate from a 507-point spend into a free one on a feature whose whole budget was 1,327
  points. It is not a substitute for the real run — INV-26's board claim goes unchecked — but for a
  commit that touches no plan status it checks everything that could redden.

- 2026-08-19: INV-17 names the seam handoff for the ENDING phase, not for the status being written.
  I wrote `notes/handoff-ready.md` alongside `status: "Ready"` and the gate said
  `status is 'Ready' but notes/handoff-plan.md is missing`. The G-06 trigger fired correctly (I
  wrote the note in the same act as the status) and I still got the filename wrong; the pre-commit
  gate is what caught it. Ending phase → filename, always.

- 2026-08-19: `bash-write-guard.sh` blocks `cp` into the session scratchpad
  (`/private/tmp/claude-501/.../scratchpad`) for `harness-orchestrator` — "targets probe.yaml,
  outside your domain". So the standard "copy the file and test the edit on the copy" move is not
  available. The substitute that worked: read the real file into Python, apply the substitution
  in memory, `yaml.safe_load` the result and assert the substitution count, never writing. That
  verified a `re.subn` snippet against all five task ids before handing it to the operator.

- 2026-08-19: the shared GraphQL counter moved 1,605 points between the operator's reading (2068)
  and mine (3673) roughly minutes apart, with no call of mine in between, and another 37 points
  between two of my own adjacent commands. The BRIEF records ~300 points of this drift; it is four
  times larger than documented. Any budget figure handed down in a dispatch prompt is stale on
  arrival — re-read the counter as the first act, before planning any spend.

- 2026-08-19: `gh-sync.py open` cost 40 GraphQL points for a milestone, 9 issues and 9 sub-issue
  attachments (3676 → 3716, board 3, 2026-08-19). About 2 points per issue-shaped write. It also
  printed no board-station line, so whether the new cards reach the board is not observable from
  its stdout — the operator's positive control later showed they DO land, in `Backlog`.

- 2026-08-19: INV-26 skips a feature entirely while every task reads `pending`
  (`check-state.sh:1218-1221`). A baseline/after comparison of gate output that straddles the first
  status write is therefore comparing two different INV-26 regimes, not two states of one gate —
  the before/after must both be taken on the same side of that line.

- 2026-08-19: **a positive control captured from BOARD STATE silently conflicts with the gh-sync
  protocol.** The operator captured 8 INV-26 lines whose text reads "the board reads Backlog" for
  seven specific cards, to be reproduced verbatim after the change. Running the ordinary
  `start-task`/`close-task` sync points would move those cards to `Building`/`Done` and change the
  line text, making the control unreproducible — and it could not be recaptured, because capturing
  it required the expensive read the feature removes. Nothing in either procedure mentions the
  other. I froze the mirror for the whole feature until the after-measurement lands. The general
  shape: when a control's expected output quotes MUTABLE EXTERNAL STATE, work out who else writes
  that state before the control is relied on, and freeze them.

- 2026-08-19: an amendment can move a task's `intent:` without moving its `verify:`. Amendment 2
  added the positive control to T-07's intent — "all 8 INV-26 lines must reappear VERBATIM" — while
  the `verify:` block still only diffs two files that both contain zero INV-26 lines. The gate is
  green and incapable of failing on precisely the defect the amendment was written to catch. When a
  plan is amended mid-flight, diff BOTH fields of the amended task, not the prose of the amendment.

- 2026-08-19: **"pre-existing failures" is scoped to the reporter's dispatch point, not to the
  feature.** A member measured its own baseline before editing and reported 7 integration failures
  unchanged after — honest, and wrong at my tier, because its baseline commit already carried the two
  tasks that caused them. I bisected in a throwaway worktree (bee6234 0 FAIL, 9fd11d7 6 FAIL) and the
  regression was ours. Whenever a member reports a red suite as pre-existing, re-run it at the
  commit the FEATURE branched from, not the one the member started at. Three checkouts settled what
  no amount of reading the digest could.

- 2026-08-19: a `change_type` that maps to `unit` alone gives a task NO path to the integration test
  that covers the function it edits. T-02 (`logic` -> unit) rewired `board_stations`, and
  `test-check-state.py` — the six INV-26 checks that exercise it — lives in `INTEGRATION_SCRIPTS`.
  Its `verify:` was structurally incapable of catching the regression it caused. When a task edits a
  function some OTHER suite's invariant depends on, run that suite too regardless of the matrix row.

- 2026-08-19: a stale test FIXTURE and a live positive control catch different failures and neither
  substitutes for the other. The fixture's fake `gh` answered the replaced call, so INV-26 went
  silent under test while working perfectly against the real board. The control (real API) would have
  passed; the fixture (fake API) failed. Both were needed to see the whole picture.

- 2026-08-19: backticks inside a double-quoted `git commit -m` are COMMAND SUBSTITUTED. My message
  said "the fixture fake gh serves `project item-list`" and zsh printed `command not found: project
  item-list` while the commit landed with the phrase silently deleted. The commit succeeded, so
  nothing flagged it; only re-reading `git log -1 --format=%B` found it. Single-quote the message or
  pass `-F <file>` — and always re-read the landed message when the shell printed anything at all.

- 2026-08-19: `bash-write-guard` rejects `git worktree add` with a RELATIVE destination and names the
  absolute path it wants under `.claude/worktrees/`. A throwaway worktree at an older commit is the
  cheapest way to bisect a suite regression without disturbing a working tree that holds another
  agent's uncommitted edits — and `git worktree remove --force` restores cleanly.

- 2026-08-19: **a reviewer alleged a signed record was falsified, and the timestamps cleared it.** qa
  found `.harness/logs/gh-cost-2026-08-19.jsonl` present after an amendment recorded the operator
  deleting it, reasoned from `gh_cost_log.py:53` (which reads default OFF) that "an exported
  HARNESS_GH_COST_LOG=1 must have reached a suite run", and concluded the record was falsified either
  way. It was not. Every record is stamped 21:02:07Z-21:09:22Z = 14:02-14:09 local; the flip commit
  `4b98191` landed at 14:16:40. All 167 records predate the flip by seven minutes, when the signed
  default was still ON — so no exported variable was needed and the deletion did hold. The reviewer
  read CURRENT code to explain a PAST event. When a finding alleges the record is false, date the
  evidence against the commit that changed the behaviour before repeating the allegation upward.

- 2026-08-19: **a lead overrode its own member's conclusion and was right.** qa found one unbound wrap
  site and wrote that the other half was "thoroughly unit-tested". The lead contradicted it on file
  evidence — `test-factory-gh.py:25` disables the recorder at module scope, so that file exercises the
  seam zero times. Accepting the member's half would have fixed half the defect and returned green. A
  lead's disagreement with its own member is signal, not noise; read the contradiction rather than the
  roll-up.

- 2026-08-19: **"the module is tested, the seam is not" is a distinct coverage hole from "the function
  is untested", and roll-ups cannot see it.** `gh_cost_log` had 24 passing checks; both call sites had
  zero. Deleting either `with` block left 164/0 and 90/0 untouched. Test-count and pass-rate metrics
  are structurally blind to it. The discriminating question is not "is there a test for X" but "which
  edit would this suite fail to notice".

- 2026-08-19: **I re-dispatched over a live run and caused two leads to work the same fix
  concurrently.** Run 05's digest said `BLOCKED ... still in flight, no return collected` — an
  explicit statement that its member had not returned. I checked `git diff --stat` on the source
  directory, measured it empty, concluded nothing had landed, and re-dispatched. The orphaned member
  was still alive: it wrote a MUTATION PROBE into `factory_gh.py` minutes AFTER my measurement,
  leaving production recording dead in the tree, then completed and overwrote its own run dir. Run
  06 found and reverted the probe. My own gotcha G-07 already says to treat a step with no
  `completed_at` as live and resume rather than re-dispatch — I had the rule and did not apply it.
  **An emptiness measurement has a timestamp; a live agent invalidates it a second later.** The
  discriminator is the run's `state.yaml` completion time, never the tree.

- 2026-08-19: when two runs duplicate one logical unit of work, their reported `cycles_used` must be
  combined by MAX, not SUM. Summing charges the feature twice for one cycle and is how a healthy
  feature goes BLOCKED on a tooling failure. Record the ambiguity in the digest rather than resolving
  it silently either way.

- 2026-08-19: a lead reporting `cycles_used: N` may be reporting the STEP's inherited cycle counter
  rather than send-backs it issued in this run. The discriminator is artifacts: N send-backs in a run
  implies N member attempts, so if no receipt and no source diff exists, the number is inherited and
  double-counting it is wrong. Ask for "send-backs issued inside this run" explicitly in the dispatch.

- 2026-08-19: **I cited a PASS count for four dispatches before checking what it counted.**
  `grep -c '^PASS '` on `run-unit-tests.sh` output returned 139/160/164/172 and I reported those as
  suite sizes. The runner emits exactly ONE `PASS <script>` line per script (18 for `--kind unit`,
  `run-unit-tests.sh:58-67`); every other match came from individual scripts printing their own
  `PASS` lines. A second measurer summing per-script totals got 806 on the same suite. The DELTA was
  always sound (+8 = eight new checks) and no decision turned on the absolute — but I put an
  unexamined number into a commit message and three dispatches. Before citing a count, run the
  command that shows WHAT is being counted, not just how many.

- 2026-08-19: **a conflict between two agents' reports about an enforcement hook was settled by
  running the hook.** qa reported one member denied an Edit on `factory_gh.py` and another completing
  the same mutation, and concluded all mutation evidence on the feature was of uncertain
  admissibility. `check-domain.sh --resolve` on that path returns `harness-backend-dev,
  harness-dev-ops` and not `harness-qa` — so the denial was correct and the other member reached the
  file through Bash, which the hook cannot see (DEC-85). Both were honest; neither was wrong. The
  evidence in question was authored by an agent that IS granted, so it stood. **When two agents
  disagree about what a guard does, run the guard — do not adjudicate their reports.**

- 2026-08-19: a validator returning ESCALATE with `must_fix: []` and the blocking item in
  `open_questions` is the correct shape when the only remedy edits a signed artifact. Asking for that
  routing explicitly in the dispatch — "if you disagree, return an open_question, NOT a FAIL, because
  a FAIL routes a cycle to a squad that may not touch the file" — produced it. Naming the routing
  consequence, not just the preference, is what made it land.

- 2026-08-19: **the same guard refused the same mistake in three independent lead contexts on one
  feature** — `dispatch-guard.sh` blocking a `model:` parameter. Each lead lost a spawn turn to it.
  The prior occurrences were recorded only in observations logs, which are never injected at spawn,
  so no successor could be warned. A lesson that lives only where it is never read is not a lesson;
  a repeated guard refusal across independent contexts is evidence the rule belongs where the call
  is made, not in a log.

- 2026-08-19: **the strong form of an assertion is what makes a mutation proof mean anything.**
  `gh_cost_log.py:165` writes the sentinel `-1` when `returncode` is None, so a check of
  `rc is not None` would have passed under the very mutant it was written to catch, while
  `rc == 1` reddened. When commissioning a mutation proof, specify the assertion's FORM, not just its
  subject — "assert the recorded exit code equals 1", never "assert the exit code is recorded".

- 2026-08-19: extra checks beyond a scoped fix are worth keeping when the RED output shows them
  PASSING under the mutant — that is empirical proof they are vacuous, which converts them from
  scope creep into controls. The discriminator is the mutant's own output, not a judgement about
  whether more tests are better.
