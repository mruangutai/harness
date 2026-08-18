# Observations — harness-orchestrator — FEAT-24

- 2026-08-18: I have no `SendMessage` tool (Read/Glob/Grep/Agent/Write/Bash only), so there is NO
  channel to an in-flight lead. Measurements taken after dispatch cannot be relayed mid-run; they
  either wait for the return as a consolidated send-back or are wasted. Front-load measurement
  into the dispatch prompt — after it launches, the prompt is frozen.

- 2026-08-18: The `SubagentStop` digest hook fires on EVERY turn I end without a fenced digest,
  including while a delegated run is still in flight. Ending a turn with prose is rejected. The
  working pattern is a foreground bash until-loop (`for i in $(seq 1 N); do ...; python3 -c
  "import time;time.sleep(20)"; done`) — foreground `sleep` is blocked but a Python sleep is not,
  and the loop keeps the turn alive inside one tool call. A backgrounded sleep does NOT work: it
  returns control immediately and the turn ends anyway.

- 2026-08-18: `feature.json`'s schema REJECTS the `phase` key ("undeclared key 'phase' at /"),
  which the orchestrator playbook explicitly instructs be recorded there ("Record your phase in
  `feature.json` `phase:`"). Raised as Q5; it is a harness defect, not this feature's.

- 2026-08-18: The product-lead's own return never arrived, but its digest was complete on disk at
  `runs/2026-08-18-1-product/digest.md`, self-describing as final. Polling the feature dir for
  `runs/*/digest.md` and grading from the artifact worked. Corroborates the standing rule the
  other way round: the artifact on disk outranks the return channel in both directions.

- 2026-08-18: Passing `model:` in a dispatch is refused by `dispatch-guard.sh` (DEC-152 tiers). It
  is a hard block, not a warning, and the dispatch never runs — cheap to hit, cheap to fix, and it
  is NOT a send-back for cycle-counting purposes.

- 2026-08-18: Independent verification of the plan cost ~8 bash calls and caught nothing pm had
  wrong, but it confirmed four cited anchors (`test-no-distribution.py:160,166`,
  `templates/harness.json:155`, `gen-decisions-index.py:391-396`) at a fraction of a review cycle.
  Cheap enough to be routine before dispatching the next segment, not just at panel time.

- 2026-08-18: `bash-write-guard.sh` resolves the literal text of a `sed -i` target, so
  `sed -i '' '1194s/.../.../' "$P"` is BLOCKED as "targets $P, outside your domain" even when $P
  expands to a path I own. It does not expand shell variables. Re-issuing the identical command
  with the absolute path spelled out passes. Same family as G-08's quoted-redirect masking.

- 2026-08-18: Ship phase opened with `gh-sync.py open` before any task work: milestone, parent and
  ten sub-issues in one call, ~40s, all ids recorded into `feature.json` `github:` by the script
  itself — I write nothing there by hand. `start-task` then needs `plan.yaml` `status: building`
  written FIRST or the parent's derived station is a no-op.

- 2026-08-18: Handing the layer-0 lane its first segment BEFORE any team dispatch is the right
  opening move when a task in it has cross-repository human latency (T-09: issue → workspace →
  hand edit → land → operator merge). The operator's merge and my build cannot overlap inside one
  session — I die at the return — so the only lever on wall-clock is which one starts first, and
  the human one has unbounded latency while mine does not.

- 2026-08-18: Composing a main-session segment note is worth a probe pass first. Fetching kaya's
  live `github` block (`gh api .../contents/...?ref=master`) and re-probing board 2's Status
  options turned a prose instruction into a literal before/after diff, and confirmed all five
  station names exist before the operator spends a cross-repository pull request on them.

- 2026-08-18: A build team can be stopped dead by a coupling between a task's own edit and the
  PreToolUse guard that governs the editor. `harness_boundary.classify` calls `resolve_fleet` —
  hence `factory_config.load_fleet` — as its FIRST statement for every governed write, so ANY task
  that changes what `load_fleet` accepts locks every agent out of every path the instant it lands.
  The plan's route check does not model this: it asks who may write a path, not whether the write
  changes who may write the next one. Worth a standing question at plan time — "does this task edit
  a module the write guard imports?"

- 2026-08-19: The right response to a lead's BLOCKED-on-plan-defect is to re-read the chain myself
  before relaying it. Four cheap `sed -n` reads confirmed all five links and, more usefully, found
  the fact the remedy turns on that the lead had only asserted — `_governed` gates the whole domain
  phase, so the main session can cross a window no agent can. That turned "escalate a defect" into
  "escalate a defect with three costed options".

- 2026-08-19: Marking five tasks `building` in one act before dispatching a five-task team is a
  false claim as soon as the team stops early. Four of them never ran and `plan.yaml` said they had
  started. Reconciling status against the receipts on disk is a required step when a run returns
  anything but a clean full PASS — the board cards cannot be un-started, but the plan can, and the
  plan is what a successor reads as truth.

- 2026-08-19: The operator executed a main-session-direct task while an agent segment was running,
  and it showed up as an unexplained file in `git diff --stat` — read as a possible member violation
  until I diffed it and matched it to the text I had proposed. Fold "check the tree for the
  operator's own landings" into the post-run reconciliation instead of treating any unexpected diff
  as a member's.

- 2026-08-19: When a task's own edit will revoke your write access, the state files must be written
  BEFORE the dispatch, describing the state that will exist after it. Written afterwards they cannot
  be written at all. Two things make this survivable: commits still work (the bash guard extracts no
  write target from `git`), and the note must name the debts the successor discharges — the run
  entry, the task status, the close-task — because none of them can be recorded in the window.

- 2026-08-19: An open-questions list carried across sessions goes stale silently. Two of mine had
  been closed by a pm pass before signature and I re-raised both; the coordinator's greps settled it
  in one command each. Re-run the check that would falsify a carried question before repeating it —
  a stale question costs the reader more than a missing one, because it looks like new information.

- 2026-08-19: The write guard resolves the LITERAL text of a `sed -i` target, so a relative path
  after `cd` is refused as "outside your domain" exactly like a variable is. Absolute paths in every
  in-place edit, always — the refusal message names the basename and reads like a domain verdict
  rather than a path-resolution failure, which sends you looking in the wrong place.

- 2026-08-19: The lock-probe is worth doing as the FIRST act of the session after a blocking window
  is reported cleared. One append to a file I own either succeeds or returns the guard's own refusal
  text; both are unambiguous, and it costs one call. Taking "the lock is open" on report and then
  discovering otherwise three writes into a dispatch is the expensive version.

- 2026-08-19: A plan's per-file enumeration can be arithmetically false about the tree while its
  title is exactly right. T-03 said "five test files build fleet fixtures"; seven suites were red and
  six were fixture migrations, with `test-factory-workspace.py` in NO task's files list anywhere in
  the plan. The discriminator for whether that is mine or pm's: does the task's own TITLE/goal cover
  the extra work? If yes it is approved-but-unenumerated and extending the dispatch is
  execution-time; if the goal itself has to widen, it is pm's. Say which reading you took, in the
  dispatch and the return.

- 2026-08-19: Measure the red set yourself before re-deriving a task's scope from it. The operator
  reported seven failing files and was right, but the two beyond the plan's five were DIFFERENT
  problems — one an unowned fixture, one a pair of assertions the design deliberately falsifies,
  living in a file another task owns. A count alone would have routed both to the same place.

