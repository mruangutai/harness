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
