# BRIEF — FEAT-32 Concurrent-write merge path

## Problem

Three defects filed against this repository are one defect wearing three hats, and the common
mechanism is a **whole-file write with no merge path and no serialisation**.

- **#628, measured.** Two `harness-pm` spawns wrote FEAT-31's `plan.yaml` 63 seconds apart:
  `13:05:17Z` 1002 lines with `T-01..T-14` and 14 decisions, then `13:06:20Z` 191 lines with `T-01`
  alone. Thirteen tasks and thirteen decisions were destroyed. Nothing detected it. The 191-line
  file parsed cleanly, so it was not malformed — only smaller.
- **#606, measured.** An observation log is one file per agent name, written with `Write`, and the
  preloaded `harness-expertise` rule instructs every agent to append by reading the file and
  writing it whole. Two concurrent contexts of one agent therefore erase each other. On FEAT-29,
  two of the eng lead's three members reached distillation with no usable log.
- **#551, six measured occurrences, operator comment 2026-08-21.** Occurrence 1 is #628's loss,
  caused by a lead yielding while its `harness-pm` member was still in flight, so the orchestrator
  dispatched a replacement into a live write. Occurrence 2 is a decision made on a file read
  mid-write: an orchestrator recorded a line-count precondition whose pair — `plan.yaml` at 1243
  lines, `BRIEF.md` at 250 — was internally impossible, and the impossibility was the signature of
  the mid-write read. FEAT-31's own pm log records the same read from the other side: `wc -l` said
  190 and `cat -n` stopped mid-`T-01`, and ninety seconds later the same file was 514 lines.
  Occurrences 3 and 4 are reporting consequences of the same early yield. Occurrences 5 and 6,
  both observed in run dir `2026-08-21-1-product`, are that same shape seen from the other two
  tiers: 5 is a lead forced to a terminal digest with its `harness-pm` still in flight, 6 is the
  orchestrator forced to a stop with its lead still in flight. Run dirs are gitignored, so the
  durable record of both is `STATE.md` and the decision entry this feature writes — not the run dir.

Read together: #628 and #606 are the **write** side of the class — a second writer's snapshot was
taken before the first writer's change, so the union is never computed. #551 is the **read** side —
a file consumed while another writer is partway through it. Both sides have the same cure, and it
already exists in this repository for exactly one file class.

## Goal

Every shared harness artifact that two contexts can write at once — a feature's `plan.yaml`, an
agent's observation log, an Expertise file — is written through **one** locked, union-merging,
atomically-replacing tool, so a second writer adds and never deletes, and a reader never sees a
half-written file. Alongside it, a persona that must never run twice at once on one checkout is
refused a second concurrent spawn, loudly, naming who holds the claim and how to clear it. Where a
guarantee cannot be given, this feature says so out loud rather than shipping a criterion that
cannot fail.

## Requirements

- REQ-01: Two writers of one feature's `plan.yaml` both keep their work, or the loser is told it
  applied nothing — a task or decision already in the file is never dropped by a later write.
- REQ-02: Two writers of one agent's observation log both keep their entries, and a bullet already
  in the file is never dropped by a later append.
- REQ-03: The user's approval block in `plan.yaml` survives every merge byte-for-byte, including
  nested sub-keys and any comment inside it.
- REQ-04: A reader of `plan.yaml` or an observation log never observes a partially written file.
- REQ-05: A second concurrent spawn of a persona that owns a singleton artifact is refused, and the
  refusal names the live claim and the one command that clears it.
- REQ-06: A stale claim or an abandoned lock never prevents an operator from writing their own
  feature's plan.
- REQ-07: The merge behaviour for all three file classes is one implementation, so a fix to one is a
  fix to all.
- REQ-08: A merge tool refuses a destination it does not own, decided on the resolved path.
- REQ-09: Every refusal and every concurrency guarantee this feature ships is demonstrably capable
  of failing, and the demonstration is part of the deliverable.
- REQ-10: The rules the writing agents actually read instruct the merge route, so the safe route is
  the documented route.
- REQ-11: An agent cannot change a feature plan's approval block, and the artifacts that say who can
  agree with each other and with what the tree enforces.
- REQ-12: An agent that reports a verdict while a subagent it dispatched is still running is told so,
  and told which children are still running, before that verdict is accepted.

## Constraints

**Supplies the mechanism** — already built, this feature stands on it:

- **`expertise-merge.py` (FEAT-30 T-06, D-05, DEC-95, DEC-125).** The pattern this feature reuses rather than reinvents: union by
  section+id; an exclusive lock held across the whole read-modify-write; exit 6 lock-not-acquired,
  exit 7 one id with two texts, exit 8 cap breach, exit 9 a destination the tool does not own
  matched on the **realpath**; atomic `os.replace` through a same-directory tempfile; and a
  module-level `UNION_APPLY = True` literal a test mutates **by name in a source copy** to prove
  its own assertions can go red. **It is now on `main`** — FEAT-30 merged as squash `47a9935` (PR
  #629, terminal record `7dbb0f1`), and `47a9935` is an ancestor of this feature's HEAD `c32f332`.
  All four FEAT-30 deliverables are present in this worktree.
- **DEC-193** — "one shared module decides both write routes, divergences
  recorded", implemented as `harness_boundary.py` imported lazily by both guards. That is the
  precedent for REQ-07, and its mutation-proof discipline is the precedent for REQ-09.
- **DEC-171 amendment 1** — PyYAML is REQUIRED and `safe_load` replaces
  hand-rolled YAML regex, so a merge tool may parse rather than pattern-match.
- **DEC-182** — the plan is real YAML, which is what makes a structural
  union by task `id` possible at all.
- **The measured hook payload, FEAT-31's probe** (`feat/FEAT-31-orchestrator-context-watch:.harness/harness/features/FEAT-31-orchestrator-context-watch/notes/probe-hook-payload-identity.md`).
  A `PreToolUse` payload inside a subagent carries eleven keys including `agent_type`, `agent_id`
  and `cwd`. That is what makes a claim registry possible without a probe for identity.
- **`os.replace` is already house practice** — `upgrade-config.py`, `factory_decompose.py`,
  `merge-settings.py`, `gh-sync.py`. `merge-settings.py` is a landed merge tool and is present in
  this worktree; it contributes the atomic-replace shape and a preservation discipline, and nothing
  else — it holds no lock and is an idempotent install-time JSON merge, not a concurrent-writer
  merge.

**Bounds the solution** — these forbid or limit:

- **DEC-174 and amendment 4.** The harness plans its own work but does
  not **execute** changes to its own enforcement layer. Amendment 4: the enforcement layer is the
  **category** "hooks, validators, gate scripts" — the list is examples — and **the test file of
  each joins it**, because "a gate's test is the only thing proving the gate discriminates". It also
  rules that "a module a gate imports is not itself a gate": a squad may write the library, and the
  cutover that makes a gate use it is `main-session-direct`, proven by showing the gate's violation
  set is identical before and after. This feature's design is deliberately shaped to that split —
  one library written by a squad, two hook cutovers by the operator's own hand.
- **DEC-179.** Routing is resolved at plan time by delegating every literal
  `files:` path to `check-domain.sh --resolve`. Every path in `plan.yaml` was resolved at HEAD
  `c32f332` before its lane was assigned.
- **DEC-90 no longer bounds anything: it is STRUCK, and not by this feature.** It stated the
  single-operator scope boundary and claimed there is no lock anywhere. **FEAT-30 falsified it** —
  `expertise-merge.py` landed on `main` holding one — and the operator struck it on 2026-08-21 under
  DEC-188, merged as `16b30c6`. Its index row carries the strike record and `SPEC.md` §15.1 is
  rewritten. Nothing in this feature re-opens it, and no task may re-litigate it. Listed here because
  three planning rounds treated it as a live constraint on this work; it never was.
- **`plan.yaml` is absent from `check-domain.sh`'s `SHAPE_PATTERNS`** (verified at
  `check-domain.sh`'s `SHAPE_PATTERNS`, `:727` at `c32f332`: the tuple holds `RE_FEATURE_JSON`, `RE_STATE_YAML`, `RE_HANDOFF`,
  `RE_STATE_MD`, `RE_CLAUDE_MD` and nothing else), and so is the observation log. Adding either
  changes nothing — #628's 191-line file parsed cleanly. A shape gate is not the fix and is not
  proposed.
- **A new test file must be registered or the runner refuses to run.** `run-unit-tests.sh` runs a
  drift detector over the union of its two arrays and exits 2 MISCONFIGURED on any unregistered
  `test-*.py` in `bin/`, and `harness.json` `test_kinds.integration.detect` is an explicit
  pipe-separated list, so a file absent from it is invisible to the kind even once the runner runs
  it.

### The identity limit — quoted, because it bounds what any of this can achieve

`expertise-merge.py`'s exit-9 docstring already states the ceiling, and it applies unchanged to
every CLI this feature adds:

> WHAT THIS CANNOT DO, stated so nobody mistakes it for the whole fix: this tool has NO identity
> source. No `agent_type` reaches a Bash-invoked CLI and no environment variable carries one, so it
> cannot check WHO called it — only WHERE it writes. A documentor overwriting the pm's Expertise
> file is still not caught here.

Two consequences, both accepted rather than designed around. First, a merge tool can guarantee
**no loss** and **no mis-targeted destination**; it cannot guarantee **authorship**. Second, the
CLI route is reachable at all only because `bash-write-guard.sh` is allow-by-omission (#627): it
finds no write pattern in a `python3 … .py --file …` command and exits 0 at its `if not findings`
guard, before the `agent in REVIEWERS` read-only denial and before the `for name, paths in findings`
domain walk. Named by symbol and not by line: the three anchors cited through earlier planning
rounds — `:617`, `:628`, `:676` — had all drifted by `c32f332`, where they are `:618`, `:625` and
`:634`. So for each tool this feature adds,
its own exit-9 destination check is the **only** thing standing between it and a write outside the
file class it owns.

## Scope

**In, with reason:**

- `plan.yaml`'s merge path and `plan.yaml`'s lock (#628). They are one piece of work, not two
  options: a `plan.yaml` write today goes through the Write tool, the domain hook fires **before**
  the write and that hook process exits immediately after, so there is no process boundary that
  could hold a lock and no moment that could release one. A lock exists only inside a CLI that
  itself performs the read-modify-write.
- The observation log's merge path (#606) — the same defect on a different file set, and explicitly
  not covered by FEAT-30's Expertise scope statement.
- **The read side, by construction rather than by timing.** Atomic `os.replace` makes a mid-write
  read of `plan.yaml` or an observation log unobservable: a reader sees the whole old file or the
  whole new one. That closes #551 occurrence 2's mechanism without any wait, any sleep and any
  "it did not happen again".
- The **cause** of #551 occurrence 1: a second spawn of a singleton persona dispatched into a live
  one. Refused at `dispatch-guard.sh`, the `PreToolUse Task|Agent` hook, against a claim registry.
- Rewiring `expertise-merge.py` onto the shared core, so there is one dialect and not two, and so
  the Expertise file class inherits the stale-lock fix.
- **The reporting half of #551, as far as it can go.** A lead or the orchestrator returning while a
  child it dispatched is still claimed is refused **once** on `SubagentStop`. That is a single
  correction round, not a wait — and a single correction round is exactly the strength every other
  digest contract in `validate-digest.py` already has, aimed at the right harm: occurrences 3, 4, 5
  and 6 are all a **verdict asserted about members the reporter could not see**.
- **The approval-block exclusion, made real.** `team-config.yaml` has carried an `except approval:`
  comment since DEC-182 and nothing enforced it; the merge tool this feature ships would be the first
  thing to depend on it. Four artifacts named three different signers and the tree enforced none of
  them, so the resolution ships with the enforcement.

**Out, with reason:**

- **A WAIT. Making a lead block until its members finish is IMPOSSIBLE at this layer, and that is
  recorded rather than approximated.** `validate-digest.py`'s `hook_mode()` passes through on
  `stop_hook_active` — `if d.get("stop_hook_active"): return 0`, re-read at `c32f332` — precisely to
  avoid an infinite stop loop, so a `SubagentStop` refusal fires **at most once** and can never be a
  wait. No task in this plan may attempt one; a task planning an unachievable wait is worse than a
  recorded impossibility. What ships instead is above: one correction round on the return, and the
  unbounded `PreToolUse` refusal that prevents the actual loss.
- **Two residuals of #551 therefore survive this feature, named rather than implied.** An agent that
  re-returns the same premature digest a second time ships it, because `stop_hook_active` passes the
  second return through unconditionally. And an orphaned child of an interrupted parent (DEC-131) has
  no parent left to refuse, so neither mechanism reaches it. **#551 narrows; it does not close.**
- **#627 — `bash-write-guard.sh`'s allow-by-omission default.** Out. Its fix is a change to a named
  enforcement-layer gate whose real cost is designing a **rule rather than a list** for extracting
  each tool's destination argument, and it is orthogonal to the merge class: nothing in #627 makes a
  second writer non-destructive, and nothing in this feature makes #627 worse in kind. It does make
  it worse in **degree** — this feature adds three more first-party write CLIs and instructs agents
  to use two of them, which is the same escalation FEAT-30 T-07 caused. That is why every new CLI
  here carries the exit-9 destination refusal, tested in both directions, and why the limit above is
  quoted rather than paraphrased. Raised as a non-blocking open question.
- **#560 (nothing serialises Expertise writes against an open distillation run) and #605 (nothing
  serialises two leads' members against one checkout).** Out. The claim registry built here is the
  mechanism both need, and the single-flight persona set is a named module literal, so joining a
  persona to it later is a one-line change with a test. Which personas join is a policy call with a
  real cost — refusing a legitimate parallel squad — and is not this feature's to make.
- **#610 (leads hold no `SendMessage`)** — a different mechanism entirely.
- **#626 (FEAT-30's two-segment worktree layout falsifies DEC-193, DEC-143 and DEC-95)** — FEAT-30's
  to answer.
- **A shape gate for `plan.yaml`** — checked and rejected above.

### FEAT-31 disjointness — verified, not trusted

FEAT-31 is claimed disjoint. Checked at `feat/FEAT-31-orchestrator-context-watch` tip `7299669`:
its ten tasks touch `context-watch.py`, `test-context-watch.py`, `test-context-watch-cli.py`,
`upgrade-config.py`, `test-upgrade-config.py`, `check-state.sh`, `test-check-state.py`,
`.claude/skills/harness/templates/harness.json`, plus `run-unit-tests.sh`, `.harness/harness.json`,
`DECISIONS.md` and `DECISIONS-INDEX.md`. **Logically disjoint: true** — no file whose behaviour
this feature changes appears there. **Textually disjoint: false** — the last four are shared
registration and record surfaces, so both features append to `run-unit-tests.sh`'s
`INTEGRATION_SCRIPTS`, to `harness.json`'s `integration.detect` list, and to the decisions record.
Whichever lands second rebases those four; each is an append, none is a rewrite.

## Verification gaps

- `component`, `ui`, `eval` and `typecheck` all carry `cmd: null` in `.harness/harness.json`. None
  covers a surface this feature touches: everything shipped here is Python and shell under
  `.claude/skills/harness/bin/`, plus markdown, and both `unit` and `integration` have real runners.
  **No criterion below rests on a null kind.**
- `integration` has a runner but no live database and no live Claude Code session. Consequently
  **no criterion below is evidence that a real orchestrator's real dispatch is refused in a real
  session.** Every hook criterion is a synthetic payload fed to the hook script on stdin, which is
  exactly how `test-bash-write-guard.py` and `test-check-domain.py` already work. The residual risk
  — that the live `PreToolUse Task` payload differs from the synthetic one — is carried by SC-15, a
  measurement taken against the real platform before the guard is written, and by nothing else. The
  `SubagentStop` half of that risk is already discharged: `validate-digest.py` selects a
  persona-specific schema from the returning agent's own name and a live orchestrator return was
  rejected against the `orchestrator` schema, which is only reachable when `agent_type` is present.
- **Every `verify:` in this plan pins its own checkout.** `run-unit-tests.sh` begins
  `cd "${CLAUDE_PROJECT_DIR:-$(pwd)}"`, so a verify run with that variable pointing at another
  checkout measures the wrong tree and reports zero matched lines. Each of the 15 `verify:` blocks
  therefore opens with `cd "$(git rev-parse --show-toplevel)"` and exports `CLAUDE_PROJECT_DIR="$PWD"`
  — self-locating, so it is correct in the worktree and on `main` without a hard-coded path.

## Success Criteria

- SC-01: A second writer proposing `T-01` alone against a `plan.yaml` holding `T-01..T-14` leaves
  all fourteen tasks and all fourteen decisions present, and the loss recorded in #628 is
  reproduced as a permanent case that never routes through the tool. It can go red: the naive case
  asserts `T-02..T-14` absent after two plain whole-file writes, so it fails the moment that
  sequence stops losing them, and the tool case fails on any dropped id, asserted one id at a time
  and never as a count.
  verify: automated      evidence: integration
- SC-02: Twenty concurrent pairs of `plan.yaml` merges admit exactly two outcomes — the union of
  both proposals survives, or one process exited 6 with the lock message having applied nothing —
  and any third outcome is reported by trial number with both exit codes and the file content.
  It can go red: with `UNION_MERGE` mutated from `True` to `False` by name in a copy of the source
  tree, the suite must FAIL; unmutated, it must PASS. Both halves are asserted, so an
  always-refusing tool fails the union half.
  verify: automated      evidence: integration
- SC-03: A base `plan.yaml` whose `approval:` block carries a nested `rulings:` list, a quoted
  scalar and a trailing comment is merged with a proposal that adds a task; the exact byte slice of
  the base's `approval:` block is present verbatim in the result, comment included, and the count
  and text of every other comment line in the file are unchanged. Key presence is explicitly NOT
  the assertion. It can go red: with `PRESERVE_BASE_BYTES` mutated from `True` to `False` by name in
  a copy of the source tree the tool re-renders through the YAML dumper, which cannot emit a
  comment, so the byte comparison fails and the suite must FAIL.
  verify: automated      evidence: integration
- SC-04: Two concurrent appends to one agent's observation log keep both bullets with the base
  file's bullets intact and their order preserved, a byte-identical bullet appears once, and two
  bullets differing in text are both kept. The #606 loss is reproduced as a permanent naive case.
  It can go red: with `UNION_MERGE` mutated to `False` by name in a copy of the tree the suite must
  FAIL; and each bullet is asserted individually, never by count.
  verify: automated      evidence: integration
- SC-05: Each merge CLI this feature ships refuses a `--file` outside the file class it owns with
  exit 9 decided on the realpath — including a `..` escape wearing a legal-looking tail — **and**
  exits 0 for a legitimate destination of that class. Both directions are asserted for each tool.
  It can go red: an allow-nothing tool fails the allow half, and a string-matching tool that never
  resolves the path fails the `..` case.
  verify: automated      evidence: integration
- SC-06: With a live claim for `harness-pm` on disk for this checkout, `dispatch-guard.sh` fed a
  `PreToolUse Task` payload naming `harness-pm` as the dispatched persona exits 2 and its stderr
  carries the refusal marker, the claim's recorded start time and the literal command that clears
  it; with no claim on disk the same payload exits 0. It can go red: the refusal is identified by
  its marker string and not by a non-zero exit, so a crash on the way in — which is also non-zero —
  fails the assertion; and with `SINGLE_FLIGHT_AGENTS` mutated to an empty tuple by name in a copy
  of the tree, the refuse half must FAIL while the allow half still passes.
  verify: automated      evidence: integration
- SC-07: `dispatch-guard.sh`'s pre-existing refusal set is unchanged by the cutover. Its
  `model:`-parameter behaviour is captured as a test **before** the claim check is added — the
  script has no test today — and that test passes byte-for-byte unchanged afterwards, covering the
  refusal, the main-session pass-through, the non-harness pass-through and the unreadable-payload
  pass-through. This is DEC-174 amendment 4's stated proof obligation for a gate cutover. It can go
  red: the before-capture is committed in its own task, so a behaviour change in the second task
  fails it.
  verify: automated      evidence: integration
- SC-08: `validate-digest.py`'s existing behaviour is unchanged by gaining the claim release and the
  return contract: the existing `test-validate-digest.py` suite passes with no case edited, and each
  new path is asserted by a new case of its own. It can go red: the existing suite is run unmodified,
  so any change to the three fail-open pass-throughs — identified by their stderr markers
  `unreadable hook payload`, `has no agent_type` and `stop_hook_active`, never by line number — fails
  it.
  verify: automated      evidence: integration
- SC-09: A stale claim cannot brick the factory. A claim whose start time is older than the
  time-to-live is treated as absent, the dispatch is allowed, and the staleness is reported on
  stderr; and one documented command clears every claim. It can go red: with `CLAIM_TTL_SECONDS`
  mutated to a value larger than the fixture's age by name in a copy of the tree, the stale case
  must FAIL.
  verify: automated      evidence: integration
- SC-10: A killed writer cannot brick plan writes. With the lock held by a child process that is
  then `SIGKILL`ed, the next merge run acquires the lock and applies, and the assertion is that the
  merge exited 0 and the union is on disk — not merely that something did not hang. It can go red:
  with the shared core's `USE_FLOCK` mutated from `True` to `False` by name in a copy of the tree
  the core falls back to an `O_CREAT|O_EXCL` sibling lock file, which the killed process leaves
  behind, so the next run exits 6 and the suite must FAIL.
  verify: automated      evidence: integration
- SC-11: There is one implementation. `plan-merge.py`, `observations-merge.py`,
  `expertise-merge.py` and the claim registry each obtain their lock and perform their atomic
  replace by calling the shared core, and none of them contains a lock or replace primitive of its
  own. It can go red: the assertion is positive as well as negative — each consumer must import the
  core by name and call it — and with a `fcntl.flock` call inserted into a copy of one consumer the
  suite must FAIL.
  verify: automated      evidence: integration
- SC-12: The documented route is the safe route. `harness-spec-driven/SKILL.md` instructs the
  `plan.yaml` write through the plan merge tool and `harness-expertise/SKILL.md` instructs the
  observation append through the observations merge tool, each naming the exact invocation, and
  neither still instructs a bare read-modify-write. Graded by reading `git show <review_sha>:<path>`
  so an uncommitted edit cannot satisfy it, with a cited `file:line` per instruction.
  verify: inspection
- SC-13: The record states what is NOT fixed. The feature's own record names, each as its own
  statement: that a wait is impossible with the `stop_hook_active` reason; that a second identical
  return ships anyway; that an orphaned child of an interrupted parent is unreachable by either
  mechanism; the identity limit as a bound on every CLI added; and #627, #560 and #605 as out of
  scope with #627 named as the reason the CLI route is reachable at all. A reviewer cites each
  statement by `file:line`, read at `git show <review_sha>:<path>`. It can go red: it is asserted one
  statement at a time, never as a count, so a record naming four of the six fails.
  verify: inspection
- SC-14: No test that passed before this feature fails after it. **Every observation of the runner,
  before and after, exports `CLAUDE_PROJECT_DIR` to the checkout being measured** — the runner `cd`s
  to that variable, so an unpinned run measures another tree. **Baseline observed at `5d9b428`,
  BRIEF pending, before any work, and NOT re-observed at `c32f332`** — FEAT-30 added two files to the
  runner's arrays after it, so the counts below have moved and only the exit code and the absence of
  `FAIL` lines are binding: `run-unit-tests.sh --kind unit` exited 0 with 179 lines matching
  `^PASS |^FAIL |ERROR` and **zero** beginning `FAIL`; `--kind integration` exited 0 with 93 such
  lines and **zero** beginning `FAIL`. (Three of the integration lines contain the word `ERROR`
  inside a test's own name — they are expected-output cases, not failures, which is why the
  assertion is on lines *beginning* `FAIL` and on the exit code.) Re-observed after, both still exit
  0 with no line beginning `FAIL`, and every new test
  file is registered — the runner's drift detector exits 0 and `harness.json`
  `test_kinds.integration.detect` names each new file by path, plus
  `test-validate-digest.py` and `test-check-domain.py`, the two pre-existing files this feature's own
  `evidence: integration` claims rest on and which were absent from that list (DEC-197).
  verify: automated      evidence: integration
- SC-15: The synthetic payloads the hook criteria rest on are the real ones — for the ONE key that is
  still unknown. Before the guard is written, the live `PreToolUse Task|Agent` payload is captured
  from a real spawn on this machine, its key set recorded, and the key naming the **dispatched**
  persona named explicitly. `SubagentStop`'s `agent_type` is deliberately NOT re-measured: it is
  already settled by `validate-digest.py` selecting a persona-specific schema from the returning
  agent's own name, a path unreachable when that key is absent. It can go red: it is a measurement with a written artifact, and a
  key the capture does not contain cannot be cited by the tasks that follow — a task that cites one
  anyway is a review finding against this criterion.
  verify: inspection
- SC-16: **WITHDRAWN, not unmet.** It asked the operator to be shown, at approval, that this plan
  contradicted a live DEC-90. DEC-90 was struck on 2026-08-21 under DEC-188 (`16b30c6`), falsified by
  FEAT-30 rather than by this feature, so the criterion has no subject left. No task depended on it.
- SC-17: An agent cannot change a plan's approval block and the main session can. `check-domain.sh`
  denies a `harness-pm` and a `harness-orchestrator` Write or Edit that changes `plan.yaml`'s
  `approval:` mapping, allows one that leaves it loaded-equal, and allows the same change from a
  payload carrying no `agent_type` — the main session. It can go red: both directions are asserted
  per persona, so a deny-everything gate fails the allow half; and with the guard's named literal
  mutated to `False` in a copy of the tree the deny cases must FAIL.
  verify: automated      evidence: integration
- SC-18: The artifacts that name a plan signer all name the main session. The plan template, the pm
  agent definition and `team-config.yaml`'s `main_session.writes` list each say so, and
  `main_session.writes` grants `plan.yaml`'s `approval:` mapping — which it grants to nobody today.
  Graded by reading `git show <review_sha>:<path>` with a cited `file:line` per artifact. It can go
  red: it is asserted per artifact, and the `team-config.yaml` half is asserted as a grant present in
  the parsed list, not as a comment.
  verify: inspection
- SC-19: A return made with children in flight is refused, once, and the once is asserted rather than
  hidden. With two live claims dispatched by `harness-eng-lead` on disk, `validate-digest.py --hook`
  fed a `SubagentStop` payload with `agent_type: harness-eng-lead` and an otherwise valid lead digest
  exits 2, its stderr names **both** children and `#551`, and the lead's own claim is gone — proving
  the release ran before the refusal, so a refused return cannot leak a claim. With no children the
  same payload exits 0 and carries no children marker. With `stop_hook_active` true it exits 0 with
  children still on disk, which is the recorded residual and must not be "fixed". It can go red: the
  refusal is identified by its marker string and not by a non-zero exit, and each child is asserted by
  name rather than by count.
  verify: automated      evidence: integration

## Approval

status: pending
approved-by:
date:
