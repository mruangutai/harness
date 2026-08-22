# Observations — harness-orchestrator — FEAT-32-concurrent-write-merge

- 2026-08-21: My own dispatch asserted "the main session has already merged `origin/main` into your
  worktree at `c32f332`, so [the strike and DEC-197] are present in YOUR checkout". Half true. At
  `c32f332` the merged main tip is `7dbb0f1` (FEAT-30 terminal). `16b30c6` (the DEC-90 strike) and
  `1d2b036` (DEC-197) are fetched objects but NOT ancestors of HEAD —
  `git merge-base --is-ancestor` says so for both, and `origin/main` is `1d2b036`, two commits
  ahead. The dispatch's own instruction "verify that yourself rather than trusting this paragraph"
  is what caught it. LESSON: a dispatch that names a sha AND tells you to verify is telling you the
  sha is a hypothesis. `--is-ancestor` is the check; `ls` of a file is not, because a file can
  arrive from an earlier commit than the one you were told about.

- 2026-08-21: The cheap discriminator for "is this doc change in my tree" is not grepping for the
  new text (absence is ambiguous — wrong file, wrong phrasing, wrong section). It is
  `git merge-base --is-ancestor <sha> HEAD`, which is binary and cannot be misread. I grepped
  DECISIONS-INDEX.md first and got a suggestive answer; the ancestor check made it certain.

- 2026-08-21: The two missing commits are DOCS-ONLY (`git show --stat`: DECISIONS.md,
  DECISIONS-INDEX.md, SPEC.md and nothing else). That materially lowered the cost of being behind —
  no code or `harness.json` divergence — and it was one command to establish. Establishing the
  BLAST RADIUS of being behind is a different and cheaper question than getting up to date, and it
  is the one that decides whether the round can proceed.

- 2026-08-21: An orchestrator cannot course-correct a lead that is already in flight. I found the
  merge gap at my 5th tool call with pm dispatched at my 3rd, and had no way to relay it: I hold no
  SendMessage tool, and the harness states plainly that no message tool reaches a running agent.
  The correction had to wait for the return. LESSON: front-loading the dispatch is right, but the
  price is that everything discovered afterwards is un-relayable — so the dispatch must carry
  "verify this yourself" on every premise it asserts, because that instruction is the ONLY
  correction channel that works after the spawn.

- 2026-08-21: `# except approval: (DEC-129)` at `team-config.yaml:90-91` cites the wrong decision.
  DEC-129 (`DECISIONS.md:2946`) is about feature docs living in the feature's folder and
  `## Problem` preceding `## Goal`; it says nothing about approval authorship. The same wrong
  citation propagated into this feature's own plan — `plan.yaml` D-04 carries `dec: DEC-129`. I
  only found it by opening the entry the comment cited instead of trusting that a citation points
  somewhere real. LESSON: a citation in a config comment is unverified until opened, and the index
  summary row is not the entry.

- 2026-08-21: The "three artifacts disagree on who signs" framing I was handed was itself
  incomplete, and the resolution is a superseded-premise chain, not a typo. DEC-67 (`:802`, "the
  orchestrator is the single writer for ... `## Approval`") is already marked SUPERSEDED BY DEC-86
  in the index. DEC-112 (`:1923-1925`) says `## Approval` is "orchestrator-written by design"
  BECAUSE "pm has no user channel [and] init runs at the orchestrator tier and does" — a premise
  DEC-120 falsified when it made the orchestrator a spawned agent that "cannot call
  `AskUserQuestion`, so every approval, question and briefing bubbles to the main session"
  (`:2423`). LESSON: when N artifacts disagree, look for the one whose PREMISE a later decision
  removed, rather than counting votes. The outlier by count was the correct one.

- 2026-08-21: CORRECTED, and I had it wrong first. I grepped `team-config.yaml` for the literal
  string `plan.yaml`, got three lines (`:18` main session, `:90`/`:91` pm), and concluded "the
  orchestrator has NO plan.yaml write grant, so `templates/plan.yaml:25` instructs an act the guard
  would refuse". FALSE. `check-domain.sh --resolve` on a real plan.yaml prints
  `harness-orchestrator` AND `harness-pm`, exit 0: the orchestrator's grant is the parent-directory
  glob `.harness/*/features/**` in its own domain block, which a FILENAME grep cannot see. pm
  measured this correctly and I did not. LESSON: to answer "who may write this path", run the
  resolver, never grep the config. A grant expressed as a directory wildcard is invisible to every
  search for the file's name, and the negative result reads exactly like an absent grant. The
  repository already ships the tool that settles it (`--resolve`); reaching for grep instead was
  re-deriving what a subprocess knows.

  What survives of the finding: `templates/plan.yaml:25` is wrong on POLICY, not on capability —
  DEC-120 puts the signature with the main session — and `team-config.yaml:18` still names
  `BRIEF.md ## Approval` and `PLAN.md ## Approval` while naming `plan.yaml`'s `approval:` mapping
  nowhere, so the grant list never followed DEC-182's format change. Both remain real defects.

- 2026-08-21: The 8-file `INTEGRATION_SCRIPTS`-vs-`integration.detect` gap is STILL LIVE at
  `c32f332` and at `origin/main` — `harness.json`'s `test_kinds` is byte-identical between them.
  DEC-197 recorded the precedence rule; nothing fixed the divergence. LESSON: "a decision was
  merged about X" and "X was fixed" are different claims, and a docs-only `--stat` distinguishes
  them in one command.

- 2026-08-21: NEAR-MISS, and my own P-05 caught it. I ran `check-plan-routes.py` at `c32f332` and
  grepped its DEVIATION lines for `FEAT-32`: got 1, against the 4 STATE.md recorded at `5d9b428`.
  I was one keystroke from reporting "down from 4 to 1". Enumerating all 11 lines individually
  showed why: 6 of them name only `bin/` paths with no feature directory in them, and three of
  those — T-07 `test-dispatch-guard.py`, T-08 `dispatch-guard.sh`, T-09 `validate-digest.py` — are
  FEAT-32's by task title. The true count is 4 and the record was right. LESSON: when the id you
  are counting appears in the output only INCIDENTALLY (via a path), a grep for that id measures
  the paths, not the items. Enumerate and attribute. A "changed count" against a recorded
  measurement deserves more suspicion than agreement does.

- 2026-08-21: `timeout` is not on macOS by default — `timeout 110 python3 ...` returned exit 127
  and my summary greps happily reported "0 VIOLATION, 0 DEVIATION". A wrapper that fails to launch
  produces the same empty output as a clean run. LESSON: always print and assert the exit code of
  the measured command, and treat 126/127 as "did not run", never as "found nothing".

- 2026-08-21: `bash-write-guard.sh` blocks a bash `>` redirect into the session scratchpad under
  `/private/tmp/.../scratchpad` as outside my domain (DEC-151, guardrail evasion). Correct, and
  worth knowing before designing a measurement: an orchestrator's shell measurements must run
  through pipes and command substitution, never through temp files. The rewrite cost one tool call.

- 2026-08-21: `run-unit-tests.sh --kind integration` exceeds a 2-minute foreground Bash timeout in
  this checkout. Do not put it in a foreground call while a lead is in flight; the call is killed
  at 143 and the turn is spent for nothing.

- 2026-08-21: A correction ruled by the operator is not necessarily a correction that is SUFFICIENT.
  R5(b) ruled "pin `CLAUDE_PROJECT_DIR`" for the plan's verify blocks, and that is right for the
  one `run-unit-tests.sh` invocation (`plan.yaml:1009`) because `run-unit-tests.sh:3` is
  `cd "${CLAUDE_PROJECT_DIR:-$(pwd)}"`. But ~20 other verify blocks invoke
  `python3 .claude/skills/harness/bin/test-*.py` by RELATIVE path, and nothing in the runner reads
  that variable on their behalf — they depend on the process cwd, so the pin does not fix them.
  LESSON: when a fix is prescribed as "set variable X", check which commands actually READ X before
  reporting the surface as covered.

- 2026-08-21: I SPAWNED A SECOND LEAD BY MISTAKE, in the feature about concurrent writes. I meant
  to course-correct the live lead and reached for the `Agent` tool instead of `SendMessage`, which
  starts a fresh agent rather than continuing one. Then `SendMessage` turned out to be DISABLED for
  the session entirely ("disabled for this session, in subagents as well as here"), so the
  correction could never have been delivered by that route either. Contained only because the
  accidental dispatch carried an explicit no-op instruction — it returned 0 tool uses, 0 members,
  `files_touched: []`. LESSON, two parts: (1) `Agent` is never the continuation tool, and reaching
  for it under time pressure spawns a competitor; (2) do not assume `SendMessage` is available —
  if it is disabled, A DISPATCH IS UNRECALLABLE AT SEND TIME. That inverts the "dispatch early,
  measure during the wait" procedure for anything the dispatch's own correctness depends on:
  verify every ANCHOR you are about to hand down BEFORE sending, and spend the wait only on
  measurements whose answers you keep for yourself.

- 2026-08-21: Two anchors I put in a dispatch were wrong and I could not recall them — I cited
  "the DEC-119 region" for check-domain.sh's fail-open-loudly precedent (it is DEC-122 `@2542`, the
  table row at `:2578`), and I passed the operator's `templates/plan.yaml:25` pointer for a `phase`
  defect when `grep -n phase` on that template returns NOTHING. The saving grace was writing
  "re-derive the anchor from the index" beside the guess. LESSON: when handing down an anchor you
  have not opened, mark it as a guess AND name the re-derivation route in the same sentence. A bare
  wrong anchor is carried; a flagged wrong anchor is corrected by the receiver.

- 2026-08-21: THE OPERATOR'S STATED REASON FOR A RULING WAS FALSIFIABLE BY ONE GREP, and the ruling
  survived anyway. The ruling picked `plan-merge.py` as host for an approval-mapping guard because
  it was "the only place with both the old and new mappings in hand". `check-domain.sh:1034` shows a
  `Write` payload carries whole-file `content`, and the base file is readable off disk — so the hook
  has both too. The ruling's SHAPE (a check reads the record) was right; only its HOST argument was
  wrong, and the better host was already the plan's. LESSON: separate a ruling's decision from its
  justification before proposing an alternative. Falsifying the reason is not grounds to decline the
  ruling, and "your shape, corrected host, here is the measurement" is accepted where "not
  workable" would have cost a round.

- 2026-08-21: A guard that MATCHES a repo-relative path and a guard that READS a file off disk need
  different forms of the same path. `check-domain.sh` holds the raw payload path at `:307` and
  `_norm(target)` at `:660` strips the worktree segment (DEC-143) for glob matching. A guard that
  opens `_norm(target)` instead of the raw absolute path fails to find the file, and under this
  file's own fail-open precedent (DEC-122 `:2578`) that failure is a SILENT ALLOW — the guard
  reverts to being decorative, which is the exact defect it was built to fix. LESSON: for any new
  check that compares a proposal against on-disk state, say explicitly which path form does the
  matching and which does the reading. The failure mode is not a crash, it is a gate that passes
  everything.

- 2026-08-21: A guard sourced from a RECORD inherits the record's deletability. Making
  `main_session.writes` load-bearing is the right fix for a decorative list, but it means deleting
  one line from `team-config.yaml` silently disarms the denial, and under fail-open-loudly the only
  witnesses are a stderr line nobody reads and the guard's own test suite. LESSON: when you convert
  a record into a gate's input, the design is not complete until it states what happens when the
  record is EMPTY, and a test case pins that answer. "Load-bearing" and "tamper-evident" are
  different properties and only the first comes for free.

- 2026-08-21 (round 4, Q1 amend): A ruling handed down to me carried three numbers and I re-derived
  all three before dispatching. Two were wrong in ways that did not change the ruling but would have
  entered the plan as facts: the corpus is 23 tracked plan.yaml at 6bb7d82 (22 at c924c6d), not 21;
  and "zero anomalies" was false — FEAT-14/plan.yaml:1154 and FEAT-32/plan.yaml:647 carry `status:`
  at 10 and 11 spaces, both PROSE inside a task body. Neither is 2 nor 4 so the discriminator holds,
  but the discriminator holding and there being no anomalies are different claims. The core claim was
  true and stronger than stated: `^  status: ` appears exactly once in all 23 files and in 22 of them
  the preceding line is literally `approval:`. Lesson: re-derive every number in a ruling even when
  the ruling is right, because the numbers travel into the plan and the conclusion does not protect
  them.
- 2026-08-21: The ruling's non-conflict claim pointed at check-domain.sh:1039 ("no reconstruction of
  old_string/new_string, no replace_all semantics, no TOCTOU window"). Reading it settled the
  feasibility question the ruling never asked: that comment is in the SHAPE gate's POST branch, and
  `_domain_phase = _governed and not _post` (:294) makes the domain phase PRE-ONLY with no tool
  filter — its only early exits are no-target-path (:322) and no-manifest. So an Edit payload's
  old_string/new_string DOES reach the domain phase. The two rules are not in tension because they
  are in different phases with different information available, which is a cleaner non-conflict than
  "it does not reconstruct".
- 2026-08-21: I found a hole in a ruling's RATIONALE without the ruling being wrong, and reporting
  that distinction was the whole value. Layer 2 was justified as "what survives a reformatting that
  defeats layer 1" — but it lives in a tool the writer CHOOSES to invoke, which is the exact
  weakness pm had established one round earlier and the operator had accepted. So after a
  reformatting, a governed agent Editing plan.yaml directly is caught by NEITHER layer. I checked the
  obvious third route before raising it and it is expensive: the post-hoc route collides with the
  pre-only domain decision's own recorded measurement, and SHAPE_PATTERNS collides with DEC-182's
  recorded reasoning for plan.yaml's deliberate absence. Checking the fix before raising the gap
  turned "the ruling is incomplete" into "the gap is real and the closure is expensive, record it as
  a residual" — a far more useful thing to hand up.
- 2026-08-21: I EXECUTED a plan's specified parser against its real input instead of reading it, and
  it was wrong. T-14's intent specified "split the entry on the LAST space" for `main_session.writes`.
  Run against the actual list at 6bb7d82, `.harness/*/features/*/BRIEF.md ## Approval` rsplits to
  glob=`...BRIEF.md ##` / tail=`Approval`, which matches neither fragment test, so the entry becomes
  fragment-less and — by the spec's own third kind — CONTRIBUTES NO DENIAL. Both markdown entries
  silently disarm; only the plan.yaml mapping survives, which is precisely the plan.yaml special case
  the Q3 ruling had just refused to hardcode. Splitting on the FIRST space parses all four entries
  correctly. Lesson: when a plan specifies a parser AND the input is on disk, run the parser on the
  input. Reading "split on the last space" three times does not reveal `## Approval` has a space in
  it; one 20-line script does. This is the same class as verifying a count instead of restating it,
  applied to logic rather than to numbers.
- 2026-08-21: A ruling specified a discriminator for ONE of the three files its own generalisation
  covers, and I only caught it by measuring the other two. The two-space `status:` rule was derived
  from plan.yaml, where the signature is `  status: pending` under `approval:`. But BRIEF.md and
  PLAN.md carry the signature as `status: pending` at ZERO indent under a `## Approval` heading
  (FEAT-32/BRIEF.md:415). A two-space rule cannot see a zero-indent line, so Q1's hole stayed fully
  open for two of the three files. The symmetric rule turned out cleaner than the original: `^status:`
  at exactly zero indent occurs 31x across 31 BRIEF.md and 10x across 9 PLAN.md at 6bb7d82, and EVERY
  occurrence is a signature line — FEAT-06's extra one is under `## Re-signature`, so it is a second
  signature, not a false positive. Lesson: when a rule is accepted BECAUSE it generalises to N files,
  measure the discriminator on all N. The ruling and I both reasoned from the file that motivated it,
  and the generalisation was the part nobody re-checked.
- 2026-08-21: THE INDENT CONVENTION IS NOT ONE CONVENTION — it is INVERTED between two of the three
  files the mechanism covers, already, at HEAD. I was told to record "two-space indentation is a
  convention, not a YAML guarantee; a future reformatting would silently unhook this gate". I tried to
  falsify a simplification (one rule, "status: at 0 or 2 spaces", for all three kinds) and the
  falsification exposed something better: in the pre-DEC-182 `PLAN.md` files, `  status:` at TWO spaces
  is a TASK's field (27 occurrences across 5 files at 6bb7d82) and `status:` at ZERO indent is the
  SIGNATURE — the exact inverse of plan.yaml. So a two-space rule applied to PLAN.md denies 27
  legitimate lines and misses every signature. The caveat I was told to write as a FUTURE risk is a
  PRESENT, MEASURED fact, which is a stronger and more honest thing to put in the code comment. The
  indent rule must hang off the fragment KIND (mapping -> 2 spaces, heading -> 0 spaces), never be
  stated globally. Lesson: trying to SIMPLIFY a rule is an underrated way to discover the rule is
  wrong. I was not auditing the two-space claim; I was testing whether one rule could replace two, and
  the counterexample it produced was the defect.
- 2026-08-21: The approval block's own KEY NAMES are not consistent either, which matters for any rule
  keyed on them. At 6bb7d82: plan.yaml uses `approved_by` (30, zero hyphens); PLAN.md uses
  `approved-by` (9, zero underscores); BRIEF.md is SPLIT — 13 `approved_by` and 16 `approved-by`
  across the same corpus. So a denial rule that names a sibling key (my proposed closure for the
  mid-line-start Edit evasion) must accept BOTH spellings or it silently misses whole files. Third
  inconsistency found in one round on a surface everyone assumed was uniform: the indent inverts
  between kinds, the key separator varies, and the section boundary needs a bound only FEAT-06 exercises
  (`## Re-signature` is the sole heading following `## Approval` anywhere in the corpus). Lesson: before
  writing a rule over "the approval block", enumerate the corpus — it is three shapes wearing one name.
- 2026-08-21: "Dispatch early, spend the wait on measurement" and "verify the premise before you plan
  on it" PULL AGAINST EACH OTHER, and I resolved it wrongly. I dispatched pm with the ruling's
  two-space rule stated as the fix, then measured and found it is wrong for two of the three files the
  mechanism covers. Because a dispatch is unrecallable here (no message tool; SendMessage disabled this
  session) pm spent its whole run encoding a rule I had already falsified. The parallelism saved maybe
  ten minutes of wall clock and cost an amend round. THE RULE FOR NEXT TIME: front-loading the dispatch
  is right when the wait is spent on measurements that INFORM the next round, and wrong when it is spent
  on measurements that VALIDATE THE DISPATCH'S OWN PREMISE. Those must happen BEFORE the dispatch, however
  much they delay it — a premise check is not parallelisable with the work that depends on it. My own
  P-06 already says exactly this for review findings; I did not generalise it to my own outgoing
  dispatches.
- 2026-08-21: A grep for a quoted phrase in a HARD-WRAPPED document returns a FALSE NEGATIVE, and I
  nearly reported one as a defect. `grep 'the category decides, the list records' DECISIONS.md`
  returned zero; the phrase is real and sits at :4861-4862 with the line break falling inside it
  ("the category" / "decides, the list records"). Two lessons: grep a SHORT fragment that cannot
  straddle a wrap (`category decides` also failed here, so it has to be shorter still, or use
  `tr -s '\n' ' '` first); and never conclude "this text is absent" from a multi-word grep in
  DECISIONS.md, which is wrapped at ~100 columns throughout. Cost avoided: reporting a real
  citation as a phantom. (Also verified in passing: STATE.md's citation for that aphorism reads
  :4860-4862 where the text is :4861-4862 — off by one at the start, harmless, but it is a claim.)
- 2026-08-21: DO NOT baseline a checker by copying its input somewhere writable. I copied plan.yaml to
  /tmp to get a pre-amend `check-plan-routes.py` baseline without racing pm's in-flight write. It
  exited 0 with 0 VIOLATION and **0 DEVIATION** — while the same plan at its real path reports 6
  DEVIATION (recorded in STATE.md). The checker's deviation reporting depends on the plan being AT its
  feature path, so a /tmp copy silently under-reports and looks like a clean baseline. Had I compared
  the post-amend real-path run against that 0, I would have "discovered" 6 new deviations the amend did
  not introduce. Lesson: a measurement taken to avoid a race is still a measurement of a different
  thing. Wait for the write, or read the committed version IN PLACE via `git show`, never a copy.
- 2026-08-21: I ALMOST RECORDED A FALSE #551 OCCURRENCE FROM AN IN-FLIGHT DIGEST. While waiting on the
  product lead I read `runs/2026-08-21-01-product/digest.md` off disk. It opened "the amend is NOT done
  … re-dispatch is a full re-spend" — so I drafted STATE.md with occurrence 9 and a whole paragraph on
  pm running as an orphan. The lead then returned PASS and the SAME FILE had been rewritten (13:19
  draft -> 13:36 final). A digest is not append-only and not final until its author returns: it is
  working state during the run. What saved me was re-reading the file after the return and checking
  mtime against it. TWO RULES: (1) a digest read before its run's return is a DRAFT — cite it only with
  its mtime, never as the run's outcome; (2) the ONE thing that is trustworthy mid-flight is the
  artifact the member actually writes (plan.yaml's bytes, which I did verify) — files, not narration.
  My P-03 says restating another agent's claim launders it into fact; this is the same failure with a
  file instead of a sentence, and it would have put a fabricated incident into the permanent record.
- 2026-08-21 (round 5): A RULE ABOUT AN ATTACKER-AUTHORED PAYLOAD CANNOT BE JUSTIFIED BY A PROPERTY OF
  THE FILE, and this is the sharp form of the round-3 error the operator has now retracted in his own
  voice. The measurement was true — the approval `status:` sits uniquely at two spaces in every
  plan.yaml, 23 of 23 at 1e73248 — but the rule derived from it inspected the Edit's `old_string`,
  which the writer AUTHORS rather than reads from the file. So `old_string: "status: pending"` with
  `replace_all: true` satisfies the rule with no leading spaces at all and flips 18 lines: the rule
  closed the careful attack and opened the careless one. LESSON, generalisable past this feature:
  before turning a measurement into a gate, name which side of the trust boundary the measured thing
  lives on — on-disk state the writer cannot choose, or input the writer supplies. A discriminator
  measured on the first and applied to the second constrains nothing, and it LOOKS rigorous because a
  real measurement is attached to it. That is what made it survive a layer-1 review.
- 2026-08-21 (round 5): A REFUSAL NEEDS ITS COUNTER-EXAMPLE STORED BESIDE IT, or a later reader
  simplifies it away. "Do not hardcode two spaces; read the indent from disk" reads as defensive
  caution and invites deletion. With the measurement written next to it — at 1e73248, all 9 tracked
  PLAN.md carry the signature at ZERO indent while 27 task `status:` lines across 5 of them sit at TWO
  spaces, so a hardcoded rule there denies 27 legitimate lines and matches zero signatures — the same
  sentence becomes a fact about the corpus that a reader must falsify before touching. Same asymmetry
  as a test versus a comment: evidence resists edits, preference does not. Corollary on cost: at this
  tier I hold `Write` but no `Edit`, and `bash-write-guard.sh` correctly refuses a `>>` redirect even
  into my own domain, so appending four lines to a 23KB observations log is a full-file rewrite. Budget
  for that, or lose the observation — and verify append-only with `git diff --numstat` afterwards
  (0 deletions), because a hand-retyped rewrite is exactly how DEC-125's wipe happens.
- 2026-08-21 (round 5, THE IMPORTANT ONE — and this entry replaces a WRONG version of itself that I
  wrote 8 minutes earlier, because rule 15 applies to my own log): I WROTE TWO FALSE STATE.md's IN ONE
  ROUND FROM CORRECT MEASUREMENTS TAKEN AT THE WRONG TIME. Sequence, by mtime. 16:00 — the lead's
  `state.yaml` reads `status: blocked`, step `in_flight`, `completed_at: none`, note "host forced to
  close before the return landed", and its `digest.md` reads `VERDICT: BLOCKED`, `members: [{ verdict:
  none, files_touched: [] }]`. 16:03:10 — I measure `plan.yaml` byte-identical to HEAD and write "the
  amend did not land". 16:04:32 — plan.yaml is written; 16:06:05 — pm's own artifact appears. I rewrite
  STATE.md as "the host abandoned its member, #551 occurrence 9". 16:07:47 — the lead rewrites
  `state.yaml` to `status: complete`, `verdict: PASS`, `completed_at: seq-2`; 16:08:23 — its digest
  becomes `VERDICT: PASS`; then it returns normally. NO occurrence, nothing abandoned, four items
  delivered. THREE RULES, and the second is the one I did not have. (1) A member writes its artifact at
  the END of its run, so "absent at time T" is not "not produced" — and neither a host's departure nor
  its own checkpoint makes a member known-dead. (2) `state.yaml` IS WORKING STATE TOO, not just
  `digest.md`. I ruled out the draft trap because two files agreed — but both were written by the SAME
  author about a THIRD party, so their agreement measures the lead's belief and nothing else.
  INDEPENDENCE MEANS A DIFFERENT AUTHOR, NEVER A SECOND FILE BY THE SAME ONE. (3) The only sound
  completion signal is the harness's own notification; until it arrives, write no sentence whose truth
  depends on the run being over. My earlier entry says "the artifact the member writes is the one
  trustworthy thing mid-flight" — I had the right rule and applied it at a moment that made a true
  measurement produce a false conclusion. Timing is part of the measurement.
- 2026-08-22 (ship, T-15's rule biting its own author): `RUNS_AGENT_EXEMPT` denied EVERY `feature.json`
  write on this feature, because the map was generated by scanning ONE working tree and a branch-only
  `feature.json` is structurally invisible to that scan. Fixed in main as `12c66b3`. THE GAP THAT
  MATTERS AND SURVIVED THE FIX: the suite asserts the map's MECHANISM, never its COVERAGE.
  `test-validate-feature-json.py:361-399` proves a known feature's count is honoured and an unknown one
  gets 0; `test-check-domain.py:2232` uses `feat not in RUNS_AGENT_EXEMPT` as a fixture PRECONDITION —
  i.e. the tests are built to work regardless of which features are in the map, which is exactly why
  none of them noticed two features missing. Lesson: a positional exemption keyed on identity needs a
  test that the KEY SET matches the corpus, not a test that lookups work. Mechanism tests pass forever
  while the data rots.
- 2026-08-22 (ship): I ran the two `feature_schema` importers against the STALE worktree copy before
  accepting that "one commit behind" was a gate risk; both PASSED. So the staleness was a correctness
  problem for what ships, not a suite problem — and that distinction changed nothing about the merge
  being needed but everything about whether I had to re-sequence around it. One command. Lesson: when
  told "you are behind, this could break X", measure X before planning around it; "behind" and "broken"
  are different claims and the second is usually cheap to test.
- 2026-08-22 (ship): I cannot perform the merge I was told to perform — `merge` is in `HEAD_MOVERS` at
  `bash-write-guard.sh:144`, refused for every governed agent. I did NOT test it live, because two
  agents were mid-write and a HEAD move re-points every file under them; I read the guard's source
  instead, which is the same answer for zero risk. Lesson: when an instruction from above collides with
  a guard, establish the collision by READING the guard, never by running the command and seeing what
  happens — a permitted command you expected to be refused does damage you cannot undo.
- 2026-08-22 (ship): ENDING MY TURN WITH A PROSE PROGRESS NOTE TERMINATED ME. With two async children in
  flight and nothing to do, I wrote a status paragraph and stopped; `validate-digest.py --hook` refused
  the return for having no `VERDICT:`/`DIGEST:` and handed me another turn, which is the ONLY reason the
  run survived. There is no idle state for an orchestrator: a turn ends in a tool call or in the real
  contract, never in narration. Corollary: that refusal is a usable retry, but relying on it is relying
  on a gate to catch a mistake I chose to make.
- 2026-08-22 (ship): A `>>` redirect naming a BARE FILENAME after a `cd` is blocked as outside my domain
  — the guard resolves the redirect target literally and a bare name is not in any domain glob. The
  block is correct and the fix is the absolute path, not the Write tool. My earlier entry generalised
  this to "the guard refuses `>>` even into my own domain", which is WRONG and cost a 308-line full-file
  rewrite I was about to perform. Lesson: `cd` is the defect, not the redirect; and an over-general
  lesson in this log is more expensive than no lesson, because it forecloses the cheap path.
- 2026-08-22 (ship, closing a lead's question with a shell it did not have): product-lead escalated
  "#551 occurrence 8 claims the mechanism DEMANDS a false verdict; that may be too strong, and I cannot
  check it without a shell". I could. `validate-digest.py:703` ranks member verdicts against
  `RANK = {PASS, FAIL, ESCALATE, BLOCKED}` and anything else draws "member verdict 'none' is not one of
  ... the roll-up cannot rank it". Verified EMPIRICALLY, not by reading: piped four synthetic lead
  digests through `validate-digest.py lead` on stdin — `none` and `unknown` REJECTED with that exact
  line, `PASS` and `BLOCKED` rejected only for a missing `branch` field, which is the control that
  proves the discriminator is the verdict value and not my synthetic digest being invalid. So a lead
  force-closed with a member in flight genuinely CANNOT record "I do not know"; the contract forces an
  assertion about work it cannot see. The strong claim is right. LESSON: a subordinate's "I cannot check
  this without a tool I lack" is the highest-value item in any digest — it is a decision waiting on a
  capability I hold, and answering it cost 3 tool calls against a permanent overstatement in an
  authority file that has no propagation checker.
- 2026-08-22 (ship): building the control into the probe is what made the above sound. Had I only run
  the `none` case I would have seen "REJECTED" and concluded correctly by luck — the digest was ALSO
  invalid for a missing `branch`, so a bare pass/fail read would have been the mutant-dies-on-import
  trap in its exact classic form. The discriminator has to be the ERROR LINE, never the exit code.
- 2026-08-22 (ship): `bash-write-guard.sh` parses my command line for write verbs by TOKEN, so a shell
  variable or function named `mv` is read as the `mv` command ("`mv` targets BLOCKED, outside your
  domain"), and `>=` inside an embedded python heredoc is read as a redirect to `=`. Both blocks were
  correct refusals of a misparse, not of intent. LESSON: in any Bash call, avoid `mv`/`cp`/`rm` as
  identifiers and avoid `>`/`>=` in embedded code — use `range(i, -1, -1)` instead of a `while j >= 0`.
  Three tool calls lost to this in one run.
- 2026-08-22 (ship, T-02): the RIGHT way to audit a red proof, and it took three steps rather than one.
  T-02's verify exits 0 only if a mutated copy of the suite FAILS, which looks airtight until you ask
  why it failed. Step 1: assert the mutation applied — the plan's own `assert m != s, "... BY NAME"`
  does this. Step 2, THE ONE EVERYONE SKIPS: prove the mutant IMPORTS — `python3 -c "import
  harness_merge; print(harness_merge.USE_FLOCK)"` in the mutated tree, exit 0, prints `False`. Step 3:
  count and read the failures. Result: 18 checks ran, exactly 2 failed, both case4 (stale lock after
  SIGKILL), with the refusal text naming the 10s timeout. So 16 checks still pass under the mutant and
  only the two testing the mutated property go red — a targeted discriminator, not a crash. LESSON: a
  red proof that reports "the suite failed" is worth nothing without the import check plus the failure
  COUNT; a mutant that dies on import fails 18/18 or 0/18 and both are indistinguishable from a pass/
  fail at the exit code. The signature of a good mutant is a SMALL, NAMED subset failing.
- 2026-08-22 (ship): I ALMOST DECLARED A HEALTHY RUN HUNG, off a broken command. Waiting on an eng
  segment I ran `find <dirs> -newermt '-25 minutes' -type f -exec ls -1t {} +` to see recent writes; it
  printed nothing, and I read that as "no output for 25 minutes, possibly stuck". Then I ran `stat -f
  "%Sm %N"` on three specific files: the lead's `state.yaml` had been written **7 seconds** earlier.
  BSD `find` on macOS did not honour that `-newermt`/`-exec` combination and failed silently to empty
  output. This is my own `timeout`-is-not-on-macOS lesson in a new costume: a command that does not run
  produces the same empty result as a clean one, and "nothing found" is the most dangerous output shape
  there is. LESSON: to test liveness, `stat` a NAMED file and compare to `date` — never infer activity
  from a filter returning empty. And never let a negative result from an unverified command reach a
  conclusion about whether to abandon a run.
- 2026-08-22 (ship, the highest-value thing I did all phase): I RE-RAN EVERY TASK'S OWN `verify:` MYSELF
  and audited every red proof, rather than routing on the lead's digest. It cost ~8 tool calls across six
  tasks and it is what let me state SC-11 and SC-14 as MET with evidence instead of relaying a claim. Two
  things only that produced: (1) a mid-flight verify I took at 12:54 was SUPERSEDED when its test file
  changed at 12:55:16 — so I learned to compare the newest deliverable mtime against my run time before
  claiming a verify result is current; (2) the lead reported T-05's mutant reddening "1 of 38" where the
  true count is 2. Neither changed a verdict, and both would have travelled upward as facts.
- 2026-08-22 (ship): AN APPROVED PLAN CAN CONTAIN A FALSE MEASUREMENT, and ratifying the deviation is the
  orchestrator's call, not the lead's and not the operator's. T-10's intent ordered SEVEN paths appended
  on the stated ground that two were ABSENT; they were already PRESENT, because the decision's own fix
  landed after the plan's observation sha. The lead appended five and asked me to ratify. I verified all
  seven present with count 1 each — appending the two would have DUPLICATED them in a file the intent
  said to change in no other way. LESSON: when a plan states a measurement as the REASON for an
  instruction, the instruction's authority expires with the measurement. Re-measure before obeying, and
  ratify the deviation explicitly in the commit message so the plan's false sentence is on the record
  rather than silently overridden.
- 2026-08-22 (ship): DO NOT FREEZE A MOVING NUMBER INTO AN AUTHORITY FILE THAT NOTHING RE-CHECKS. The
  #551 occurrence count went 7 (signed) then 8 (measured by pm) then arguably 9 and 10, because the
  defect fired twice more DURING the build of its own fix. My recommendation to the operator was wording
  — "eight measured as of <sha>, and the mechanism fired again during this feature's own build" — rather
  than an integer. There is no propagation checker (DEC-188), so a bare number in DECISIONS.md is a
  statement that will be false soon and detected by nobody. Prefer a claim that stays true as the count
  moves.
- 2026-08-22 (ship): I NAMED AN OUTPUT PATH OUTSIDE THE PERSONA'S GRANT and the guard denied it. I told
  product-lead to have pm write `notes/operator-request-FEAT-32.md`; pm's grant is `notes/research-*.md`,
  so it filed `notes/research-FEAT-32-operator-request.md` instead — correctly refusing to route around
  the hook. `harness-handoff` states this outright: a dispatch naming a path for a persona does not
  override that persona's own path, and the guard will deny it (#216). LESSON: before naming an artifact
  path in a dispatch, check the receiving persona's grant — or better, name the CONTENT and let the
  persona choose the path it owns.
- 2026-08-22 (ship): I CITED A LINE NUMBER TWO OFF AND IT REACHED AN OPERATOR-FACING DOCUMENT. I wrote
  `validate-digest.py:705` for the `RANK` dict; it is at **:703** (identical on main, so not a
  divergence), and :705 lands on `worst, worst_src = None, None` — a reader following my citation finds
  nothing. It propagated into pm's operator request, which the coordinator was about to quote into a
  DECISIONS entry. Caught only because the coordinator cited :702 and the disagreement forced a grep.
  LESSON: a line number is a claim, and mine came from eyeballing a `sed -n 'A,Bp'` window rather than
  from `grep -n` on the token itself. Never derive a line number by counting inside a printed range —
  grep the symbol and read the number off the match. And when two agents cite different numbers for the
  same fact, the probability that EITHER is right is low; measure, do not pick.
