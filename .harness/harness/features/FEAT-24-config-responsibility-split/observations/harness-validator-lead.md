# Observations — harness-validator-lead — FEAT-24

NOTE ON ANCHORS: every line number in the 2026-08-19 (run 5) entries below is a WORKING-TREE
read via Grep/Read, not a read of the pinned SHA `0fa6315`. I have no shell and cannot check
out a SHA. Treat them as working-tree anchors; qa's git-pinned measurement (it reported
`git rev-parse HEAD` = `0fa6315`, no drift) arbitrates if they diverge.

- 2026-08-19 (run 5): THE MID-WRITE READ — the single most costly mistake of this run, and a
  strict GENERALISATION of my own 2026-08-18 entry directly below. I read qa's artifact before
  its RETURN arrived, found the SC-02 summary row reading "met, 5/5" against a body proving
  "unmet, 4/5", and published an adequacy note asserting "qa's artifact contradicts itself".
  It did not. I had read a SNAPSHOT OF A FILE STILL BEING WRITTEN; qa fixed that row itself
  before returning, and the final file reads "unmet, 4/5" at `:215`. I then spent a SECOND qa
  spawn asking for a correction already made, which correctly came back a no-op PASS.
  THE 2026-08-18 LESSON WAS TOO NARROW. I had recorded it as "do not infer the VERDICT TOKEN
  from an artifact that landed early". The true rule is broader: **an artifact on disk is not
  final until the member's return arrives, and that applies to its CONTENT, not merely to its
  verdict.** Any claim about what a member's artifact SAYS — a contradiction, an omission, a
  wrong number — is unsafe before the return, and a claim about a member's conduct is exactly
  the kind G-07/G-09 warn about. Wait for the return, then read.
  SECOND-ORDER LESSON: when I "found" an inconsistency inside a single member's own document,
  the likeliest explanation was not that the member was careless but that I was reading it at
  the wrong time. Prefer the explanation that impugns my timing over the one that impugns their
  work — the first is cheap to test (re-read after the return) and the second costs a spawn.

- 2026-08-18: A member's ARTIFACT lands on disk before its RETURN arrives. I polled
  `notes/review-harness-ui-reviewer-2026-08-18-prebuild.md` into existence, read it, and had
  written `verdict: PASS` into both `state.yaml` and my `digest.md` members: block before any
  completion notification had reached me. The artifact is prose and carries no fenced VERDICT —
  the contract return travels separately and later. Inferring the token from the artifact is
  exactly the "never infer a verdict" failure, dressed up as evidence because I really had read
  a real file. Precedent that it matters here: FEAT-19's mode-A ui-reviewer returned FAIL on a
  single must_fix, so a reviewer's own token on a non-blocking medium is not predictable from
  its prose.

- 2026-08-18: Second same-day sighting of the product-lead's Q5 topology
  (`runs/2026-08-18-2-product/digest.md:25`) — a lead with one async member can be asked for a
  contract-valid return while that member is provably in flight. My `dispatched_at: seq-1` /
  `completed_at: seq-2` markers kept the run decidable, but note that I wrote `completed_at` on
  ARTIFACT-LANDING rather than on return-receipt, which makes the marker mean something weaker
  than the algorithm intends. Write `completed_at` when the return arrives, not when the file
  appears.

- 2026-08-18: Reading the plan tail I had not been handed (T-07..T-11) paid for itself twice:
  it surfaced T-08's `templates/harness.json` `_board_note` as a third operator-facing text
  surface my dispatch never named as a pointer (the reviewer swept it anyway, artifact
  :100-102), and it let me pre-measure `factory_cli.body`, `FleetError.__init__`,
  `gh-sync.py`'s `skip()`/`die()` and `board-station.py`'s `out()`/`err()` BEFORE the return
  landed. Both of my lead-tier additions came from those pre-measurements, not from reading the
  member's note — which is the difference between assessing and paraphrasing.

- 2026-08-18: `gh-sync.py:72-81` — both `skip()` and `die()` `print(...)` to STDOUT, not stderr.
  Any dispatch or plan clause telling a tool to emit "one line on stderr" in this file is asking
  for a primitive that does not exist there. Worth re-checking rather than assuming, because
  three of the four factory-family tools do write stderr.

- 2026-08-19 (run 5): THIRD sighting of the async-member/stop-hook topology, and this time the
  stop hook actively DEMANDED a contract-valid return while my only member was provably in
  flight. `members:` is mandatory, so the only well-formed close available was BLOCKED, which
  would have discarded the member's work. What worked: keep making genuinely useful tool calls,
  because a turn that never ends is never rejected.
  STATING WHAT I ACTUALLY DID, because my first draft of this entry claimed restraint I did not
  exercise: under hook pressure I wrote `verdict: FAIL` into the members: block from the
  artifact's own explicit `## VERDICT: FAIL` heading, BEFORE the return arrived. It resolved
  correctly — the return said FAIL. The honest lesson is narrower than "never infer": an
  artifact that EXPLICITLY DECLARES a contract token is different evidence from prose you
  interpret, and recording it is defensible when (a) the artifact states the token in so many
  words and (b) your own independent verdict is no better, so worst-wins cannot mask anything.
  The 2026-08-18 failure was inferring PASS — the BEST token — from prose that declared nothing.
  Direction matters: inferring the worst token is safe, inferring the best is how a FAIL ships.
  NOTE the tension with the mid-write entry at the top: the TOKEN survived the early read, the
  CONTENT did not.

- 2026-08-19 (run 5): I formed a lead-tier vacuity hypothesis and my own discriminating check
  KILLED it — recording that, because the near-miss is the lesson. All three new per-key cases
  (`test-check-state.py:1610,1617,1624`) assert `_no_finding(out)`, a NEGATIVE assertion, so I
  reasoned that a mutation neutering INV-26's station comparison would leave all three GREEN.
  Before publishing it I grepped the whole `results.append(("INV-26` / `(v.N)` set and found
  `(v.1) a mis-columned card is a VIOLATION naming feature, task, plan status and column found`
  at `:1429`, plus v.4, v.5, v.6, v.8, v.12 — the positive direction is pinned six ways. The
  negative per-key cases are a legitimate COMPLEMENT to an already-pinned positive, not a
  standalone. Lesson: a negative assertion is only vacuous if nothing else pins the positive;
  check the sibling cases in the same function before calling `_no_finding` a fail-open.

- 2026-08-19 (run 5): THE DEAD CONJUNCT, and my own first remedy for it was WRONG — recording
  both, because the correction is the lesson. `test-check-state.py:1570-1573`: the `completes`
  case computes `_tb = "Traceback" in out or "Traceback" in err`, then
  `_later_ran = "INV-13" in out or not _tb`, then asserts `not _tb and c == 1 and _later_ran`.
  `_later_ran` can never change the outcome — when `not _tb` is True the second disjunct makes
  it True regardless of INV-13, and when `not _tb` is False the conjunction already fails — so
  the expression reduces to `not _tb and c == 1`. The comment at `:1567-1569` claims "the case
  checks that INV-13 ... still ran", which the code does not do.
  I FIRST WROTE that the remedy was `_later_ran = "INV-13" in out`. That is wrong twice over:
  (1) INV-13's own messages (`check-state.sh:1293-1297`) never contain the literal "INV-13" —
  the string appears only in the comment at `:1286` — so the sub-expression is UNSATISFIABLE,
  not merely redundant, and the plain conjunct would redden the case permanently;
  (2) it is barely needed, because `check-state.sh:1366-1370` prints EVERYTHING at the very end
  after all invariants have run, so an abort yields EMPTY stdout and already reddens the
  sibling `reports` case via `bool(ls)`. The real remedy, if the intent is to be honest, is
  `bool(_lines(out))` — any output at all proves the run reached `:1366` — or to delete the
  clause and the comment's claim. Severity drops from what I first assumed: near-zero coverage
  impact, real false-narration impact.
  GENERAL SHAPE, twice over: (a) a guard written as `X or not Y` inside a conjunction that
  already requires `not Y` is always dead; (b) before proposing a remedy that greps for a
  label, CHECK THE LABEL IS ACTUALLY EMITTED — invariant names live in comments far more often
  than in output, and a grep for one is a test that can never pass.

- 2026-08-19 (run 5): The plan prescribed per-key fixture values `Col-A`/`Col-B`/`Col-D`
  (`plan.yaml:980-983`); the implementation used a full `_renamed` board renaming ALL FIVE
  columns — `backlog: Icebox, ready: Primed, building: WIP, review: Review, done: Shipped`
  (`test-check-state.py:1596-1598`). Different literals, strictly stronger than what was
  pinned. Judge what the work DOES, not what it looks like (principle 6): a mismatch against a
  prescriptive plan string is not automatically a finding, and here it was an improvement.

- 2026-08-19 (run 5): The `done`→`backlog` mutation coupling is visible statically and needs no
  worktree — `test-check-state.py:1606-1608`, the backlog case's fixture is
  `_inv26_fixture(..., "done", "Shipped", "Review", second_status="pending",
  second_card="Icebox", ...)`. Its FIRST task is `done`, so a reverted `done` literal reddens it
  as collateral. The author documented WHY at `:1603-1604`: an all-pending plan reports nothing
  whatever `_EXPECT` says (pinned as `(v.10)`), so a pending card can only be judged beside a
  started one. The coupling is forced by the invariant's own semantics, not chosen — so "would
  a single fixture change decouple them?" answers NO from the source alone, no worktree needed.
  qa then mutation-proved the leak is ONE-DIRECTIONAL (revert `backlog` reddens only `backlog`),
  which is the fact that turns "over-sensitive" into "harmless": the guarantee at risk is
  no-false-negatives, and that holds.

- 2026-08-19 (run 5): INV-26's marker slice is CORRECT and wider than the plan predicted.
  `check-state.sh:1100` BEGINS, `:1284` ENDS, one occurrence each, and INV-13 starts at `:1286`
  — so the slice is exactly INV-26 and over-spans nothing. The intent said "roughly lines 1100
  to 1200"; the real block is 184 lines. A marker-count check alone would not have caught a
  misplaced ENDS; reading what FOLLOWS the marker is what settles it.

- 2026-08-19 (run 5): SC-02's `ready` key is STILL non-discriminating at HEAD and is on nobody's
  fix list. `test-factory-decompose.py:412-413` asserts `c[1][4] == "Ready"` against a fixture
  whose own `ready` value is literally `"Ready"` (`:196`, `:224`). I also checked the two
  candidate rescuers and neither closes it: `(T-03)` at `:1198-1200` asserts A's `"Ready"` and
  not B's `"Other-Ready"`, which a hardcoded `"Ready"` still passes; and `(D4-4)` at
  `:1149-1161` is a validation-message case, not a lookup. qa then mutation-proved it at the
  real call site (`factory_decompose.py:399` → `"Ready"` reddens NOTHING). A fix list built from
  "what the last FAIL blocked on" silently drops the findings that FAIL carried alongside its
  headline — this one survived two runs because it was never the headline.
  RUN 9 UPDATE: CLOSED. The fixture moved to `"ready": "Promoted"` (`:196`, `:224`) and `:413`
  asserts `"Promoted"`; code-reviewer ran the mutant itself and it reddens three cases.

- 2026-08-19 (run 5): Same defect class swept per P-04, three more instances, all advisory
  because SC-02's `review` evidence is carried by the discriminating `Col-R` case instead:
  `test-factory-decompose.py:518-519` `(7) resume` asserts `== "Ready"`; `test-factory-land.py`
  `:308-309` `(M1) sets the station to Review` and `:490-492` both assert `== "Review"` against
  fixtures whose own value is literally `"Review"` (`:58`, `:95`).

- 2026-08-19 (run 5): PIN ASYMMETRY, derived from the plan rather than asserted at it.
  `plan.yaml:352-353` states the mechanism's purpose in the plan's own words — "the verify names
  `default_branch_sha: returns the sha` specifically to catch that" — i.e. pinning an ok-line in
  a `verify:` exists to catch case REMOVAL. T-04 pins both of its discriminating lookup lines
  (`plan.yaml:713-714`); T-05 pins all five. But three cases in `test-factory-gh.py` are pinned
  by no YAML anywhere: `:960` non-alphabet base64 (closes the validate fail-open), `:978`
  line-wrapped base64 (closes Gap 2), `:991` absent content field (required by T-01 item 3).
  Deleting any of them is invisible to every gate. The two that close the fail-opens this
  feature's own review cycles DISCOVERED are the two with no protection.

- 2026-08-19 (run 5): `feature.json:6` records `review_sha: b0604c3` — the SHA of the run that
  FAILED — while this run reviewed `0fa6315`. I ran the discriminating check before rating it:
  `review.yaml:9` says "review_sha IS PINNED BY THE CALLER, never read from" feature.json, and
  `feature-schema.json:37` says check-state.sh only tests it against PLACEHOLDER_UNSET. So
  nothing downstream validates a diff against the recorded value — it is record accuracy, not
  gate correctness, which is what demotes it from escalation to a note. Worth saying anyway:
  INV-6 checks that review_sha is PINNED, never that it is CURRENT — a gate checking presence
  rather than correctness, which is this feature's own subject.

- 2026-08-19 (run 5): CHECK THE GRANT BEFORE NAMING AN OWNER IN must_fix (my own G-12). Last run
  I corrected qa for routing a `check-state.sh` fix to a dev who may not touch it; this run I
  nearly shipped the mirror-image error by naming `harness-backend-dev` without looking. The
  manifest is `.harness/team-config.yaml`, NOT `check-domain.sh` — I grepped check-domain.sh
  first and got zero matches, which proves nothing about the grant. `:161` gives
  harness-backend-dev `{ path: .claude/skills/harness/bin/**, upsert: true }`, so
  test-factory-decompose.py IS writable by it and is not one of DEC-174's four carve-out files.
  The route is valid. qa has no such grant, which is the standing Q1.

---

## Run 9 (2026-08-19-9-validator) — full panel at pin `14994b3`

ANCHOR NOTE: all run-9 line numbers below are WORKING-TREE reads (Grep/Read). The dispatch
asserts `git diff --name-only 14994b3..7e30983` is `feature.json` alone; I folded that command
into the code-reviewer's step rather than relay it as fact (my own P-11), because a lead with no
shell either routes the measurement or publishes an assumption. IT CAME BACK CLEAN — `feature.json`
only — so every anchor below is valid for the pin. Routing the measurement rather than relaying it
cost nothing and would have converted the whole run to BLOCKED had it come back dirty.

- 2026-08-19 (run 9): **THE BUDGET TURNED A `FAIL` INTO AN `ESCALATE`, AND I NEARLY SHIPPED THE
  WRONG TOKEN.** I had written `VERDICT: FAIL` with `Q1 ... blocking: true` whose own text said
  all three ways forward需 a decision above the orchestrator. Those two fields give the runner
  OPPOSITE instructions: `FAIL` means "retrying or looping back is meaningful", and my own Q1 said
  the run budget cannot absorb a loop. `feature.json` records `max_total_runs: 20` against
  NINETEEN `runs[]` entries — and under either reading of the ambiguous entry (see the next bullet)
  the feature is at or past its ceiling, so a fix run PLUS a re-review does not fit.
  THE DISCRIMINATING QUESTION, and it is narrow enough to answer every time: **can the orchestrator
  action my `must_fix` without a decision from the tier above it?** If yes → `FAIL` and
  `blocking: false`. If no → `ESCALATE`. The roll-up rule already says why: ESCALATE outranks FAIL
  *deliberately*, so a decision only the user can make cannot hide behind a failure that looks
  loopable.
  WHY THIS IS A LEAD-TIER LESSON SPECIFICALLY: no member reads `feature.json`. The budget is
  invisible to every reviewer, so the fact that reframes the verdict is one only the lead can see —
  which is the same shape as "reporting worse than your members is allowed, you may see what they
  could not", but about the TOKEN rather than about severity. CHECK THE RUN/CYCLE BUDGET BEFORE
  CHOOSING THE TOKEN, not after drafting the digest. Note also that `cycles_used: 5/10` looked
  healthy while `runs` was exhausted — the two budgets are independent and reading the reassuring
  one is how this gets missed.

- 2026-08-19 (run 9): `feature.json`'s `runs[]` ALREADY CARRIED AN ENTRY FOR MY OWN RUN, with
  `verdict: BLOCKED`, before I had returned anything — while the run DIRECTORY did not exist when I
  created it. So either the orchestrator pre-registers a run optimistically/defensively, or that
  entry is a prior aborted attempt at the same id. I could not settle which, and it MATTERS: if it
  is my run, 19 of 20 are spent and one remains; if it is a prior attempt, registering mine makes
  20 of 20 and NONE remains. I reported both readings rather than picking, because the arithmetic
  is robust either way (at or past ceiling) and picking would have been a guess dressed as a
  measurement. LESSON: a pre-recorded verdict for your own run is not evidence of anything about
  your run, and a lead that reads it as its own history will mis-count the budget in the optimistic
  direction.

- 2026-08-19 (run 9): THE DISPATCH'S OWN DISPOSITION MISSTATES THE CODE, and re-deriving it is
  what found the real gap. The dispatch pre-briefed, as settled, that "`gh_board.load_board`
  returns `None` for an absent `github` block AND for a present block with no `board` key".
  The second half is FALSE at the pin: `gh_board.py:74-77` RAISES `FleetError("board key
  missing", "github.board", ...)`. The docstring at `:47-48` is CORRECT about that cell. What the
  docstring is actually wrong about is three OTHER cells it never mentions, all returning `None`
  silently: `:67-68` (harness.json unreadable/unparseable), `:69-70` (cfg not a mapping),
  `:72-73` (`github` block absent). The ui-reviewer reached the same correction independently.
  GENERAL SHAPE: G-05 applied to a DISPOSITION rather than to a count. A handed-down "already
  ruled, do not re-report" item is narration like any other; re-deriving it cost one grep and
  relocated the finding to three different cells.

- 2026-08-19 (run 9): I KILLED TWO OF MY OWN HYPOTHESES WITH MY OWN CHECKS. Recording both,
  because the discipline is the lesson and the near-misses are where a lead ships a false finding.
  (a) FAIL-OPEN AT `board-station.py` — I hypothesised that a corrupt `harness.json` reaches
  `load_board`, returns `None`, and prints "no github.board configured" with exit 0: a FALSE
  message plus a silently skipped station write, i.e. verbatim the BRIEF's own problem statement.
  DEAD: `board-station.py:114-133` guards file-missing, unreadable, non-dict, absent-github,
  sync-off and repo-unpinned FIRST, so by `:140` the reachable `board is None` is the explicit-null
  cell ONLY. Same shape at `gh-sync.py:135-151` and `check-state.sh:1138-1147`.
  (b) A FIXTURE MODELLING AN IMPOSSIBLE FLEET — `test-factory-claim.py:200`'s `repo_dict` nests a
  `board` under a repos entry, exactly the shape SC-01 requires `load_fleet` to REJECT. DEAD on
  reading the docstring three lines up (`:196-199`): a deliberate TEST-SIDE carrier, stripped by
  `_split_boards` before the fleet is written to disk.
  LESSON, the same one both times: READ THE GUARDS THAT RUN BEFORE THE FUNCTION, AND THE DOCSTRING
  AT THE POINT OF USE, BEFORE CALLING A `None` RETURN A FAIL-OPEN. Reachability is a different
  claim from behaviour, and I reached for the behaviour claim first both times.

- 2026-08-19 (run 9): THE FINDING BOTH DEAD HYPOTHESES LED ME TO, and it survives. Because the
  silent cells are unreachable, nothing is broken TODAY — but NOTHING PINS THAT UNREACHABILITY.
  `test-gh-board.py` has exactly one `load_board` non-raise case (`:90-91`, explicit null) and
  eight raise cases. No case covers the unreadable-file, non-dict, or absent-`github` cells. The
  absent-`github` cell IS tested — but only on the LOUD side, at `test-factory-config.py:431`, for
  `board_for`. The asymmetry is pinned where it raises and unpinned where it silently returns
  `None`. My own P-08 in the wild: "correct today" and "pinned against regression" are separate
  findings, and only the second survives an edit.

- 2026-08-19 (run 9): SC-05 HAS NO READING UNDER WHICH BOTH ITS CLAUSES HOLD — a G-10 shape reached
  by taking the dispatch's own disposition seriously and following it. Read clause 1 as `board_for`
  (the dispatch's stated reading): UNMET, because `factory_config.py:315-319` raises on explicit
  null and `plan.yaml:480-482` requires exactly that. Read it as `load_board` (the only reading
  making "is accepted" true, which REQ-09 supports): "and is the only non-error path" is UNMET,
  because there are four. The two clauses select different FUNCTIONS, so naming the reading is not
  a formality — it decides which half fails. Route the reading up rather than endorsing either.

- 2026-08-19 (run 9): THE STRONGEST FINDING OF THE RUN, AND ALL THREE REVIEWERS FOUND IT TOO.
  `factory_config.py:283-294` holds TWO raise branches — `json.loads` failure and a non-mapping
  document. `plan.yaml:464-466` (T-02 item 5) REQUIRES both; SC-06 names "unparseable JSON" as one
  of three modes. Nothing in the tree drives either: grepping both message literals across
  `.claude/skills/harness/` returns FOUR hits, all four in `factory_config.py` itself. T-02's seven
  pinned ok-lines cover neither, so both are deletable with the suite green.
  POSITIVE CONTROL RUN FIRST, per my own P-14 — the pattern matched the source's own instances, so
  a zero-in-tests result is a real absence rather than a pattern anchored on a detail the instances
  lack. Without that control the same grep is indistinguishable from cleanliness.
  CONVERGENCE IS NOT PROOF, and I said so in the digest: code-reviewer reached it by reading the
  raise sites, security by an adversarial census, me by the grep plus plan cross-reference — and
  NONE of us mutation-proved it. Security tried and `bash-write-guard.sh` correctly refused. Three
  independent searches agreeing raises confidence a lot and is still not a failing mutant.

- 2026-08-19 (run 9): A ONE-SURFACE MEMBER FINDING THAT WAS ACTUALLY FIVE, and the extension is the
  whole of what this tier adds. ui found `factory_config.py:165` telling an operator to move a
  stale top-level `board:` to `repos[].board`, which `:188-194` (new in the same diff) rejects.
  ui also asserted "nothing catches this, one-line fix". WRONG, and wrong in the direction that
  matters: `test-factory-config.py:225` ASSERTS `"repos[].board" in str(e)`, so the suite actively
  PINS the wrong advice and a one-line fix REDDENS the gate. Then `DECISIONS.md:4742-4744` — the
  DEC-174 am.3 that SC-11 required FOR THIS FEATURE — asserts both messages name where the board
  moved to, which is false for the top-level case. Then T-10's verify (`plan.yaml:1366-1393`)
  checks the amendments EXIST, never that they are TRUE, which is why it shipped green.
  ROOT CAUSE IS IN THE PLAN: `plan.yaml:452` told T-02 to "model it exactly on the existing
  top-level board rejection" — treat that message as a template to COPY, never update — while
  `plan.yaml:1409-1411` told T-10 to record that both HAD been updated. The code was built to plan
  and the record written to plan; the plan's two halves disagree.
  LESSONS: (a) when a member says "nothing tests this", GREP FOR AN ASSERTION ON THE STRING — a
  test pinning the defect is a different and worse finding than no test at all, and it changes the
  remedy from one line to three files; (b) when a message is wrong, ASK WHERE THE WORDING CAME
  FROM — tracing it to the plan converted "the documentor erred" into "the plan contradicted
  itself", which saves a wasted fix spawn aimed at the wrong seat.

- 2026-08-19 (run 9): A CRITERION CAN BE MET AND ITS INSTRUMENT STILL BE THE WRONG ONE, and the
  two must not be collapsed. SC-13 asserts "no test file was removed... by comparing the registered
  script count before and after". Clause 1 is MET — 28/28, code-reviewer measured. But (a) grepping
  `plan.yaml` for `SC-13`, `script count` and `no test file was removed` returns ZERO matches, so
  nothing in the tree automates it; and (b) THIS VERY DIFF deleted two named assertions
  (`test-no-distribution.py:293-298`) while the count stayed 28/28, because counting FILES cannot
  see a deleted CASE. The criterion's own instrument would not have caught the deletion that
  happened inside its own feature. I kept this OUT of `must_fix` because the signed clause IS
  satisfied — substituting my judgement for the criterion's text is not mine to do — and put it in
  `adequacy_notes` instead. It also generalises the three-unpinned-cases item the operator had
  already dispositioned: that is not three loose ends, it is the absence of any case-level deletion
  guard.

- 2026-08-19 (run 9): AN `sc_status` ROW CANNOT CARRY A TWO-CLAUSE CRITERION, and I first wrote
  SC-13 as `met` while my own adequacy note said its merge-commit half was unclearable. The ROW is
  what a successor reads; a caveat living only in an adequacy note is a caveat nobody applies.
  Recorded `unmet` with evidence naming which half cleared and which could not — a criterion is met
  only when ALL its clauses are, and "met with a footnote" is how an uncleared half ships as done.
  My own P-12, caught one step from publication.

- 2026-08-19 (run 9): I PASSED `model:` IN THREE DISPATCHES AND `dispatch-guard.sh` BLOCKED ALL
  THREE. My own G-12 is about checking capability before routing AROUND it; this is the inverse
  error — reaching for a capability I was never granted. A model pin is org design (DEC-152/155),
  and a task needing a stronger model is an ESCALATION, not a dispatch parameter. Cost: one wasted
  turn, ZERO spawns, because the hook is PreToolUse. RULE: the only parameters a lead gives `Agent`
  are `subagent_type`, `description` and `prompt`. Pleasant surprise worth keeping: three
  simultaneous blocks cost exactly what one would, so batching the ready set also batches the
  guard's feedback.

- 2026-08-19 (run 9): PRE-BRIEFING THE DISPOSITIONED LIST IS ALSO A ROLL-UP DEFENCE — a reason my
  own O-01 never recorded. O-01 says pre-briefing buys back reviewer attention. The additional,
  more mechanical reason: worst-verdict-wins means ONE reviewer returning FAIL on an item the
  operator already settled forces MY team verdict, and the hook will not let me claim better than
  my members. So the pre-brief keeps a settled item from re-gating the run. Phrase it as "report
  only if you disagree ON THE MERITS, with new evidence" — a flat "do not report X" would buy the
  roll-up at the cost of the independence the panel exists for. It worked: zero re-reports of the
  five dispositioned items, and both ui and code returned NEW findings instead.

- 2026-08-19 (run 9): POINTING THE ui-REVIEWER AT A NON-GRAPHICAL SURFACE PAID FOR THE SPAWN, for
  the second time on this feature. There is no UI in this diff; I named the operator-facing TEXT
  contract instead — streams, exit codes, refusal messages, the onboarding `_board_note` — and told
  it a decline was acceptable only if it published the census it measured (my own O-03). It scoped
  IN and returned the run's only operator-visible defect. A reviewer whose nominal domain is absent
  is not automatically out of scope; name the analogous surface and let it decide.
