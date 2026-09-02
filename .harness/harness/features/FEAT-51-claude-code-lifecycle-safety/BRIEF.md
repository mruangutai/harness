# BRIEF — FEAT-51 Claude Code lifecycle safety

## Problem

On the Claude Code compatibility host a parent with a live child has only two exits, and both are
wrong. `validate-digest.py`'s `hook_mode()` (`:1453` at `ad93d43e`; the refusal is at `:1574`)
either refuses the stop — exit 2, printing
`children_refusal_lines` — or lets a terminal verdict through, so a lead whose member is provably
mid-run must state a verdict about work it cannot see. Issue #551 records five independent reports
from four hosts on one feature, and its comment of 2026-08-21 four measured occurrences: a 14-task
`plan.yaml` (1002 lines, `T-01..T-14`) replaced by a 191-line one-task file **63 seconds** later
because three `harness-product-lead` runs closed with their `harness-pm` still in flight and the
orchestrator dispatched a replacement into a live write; a line-count precondition whose pair was
internally impossible (`plan.yaml` 1243 intermediate against `BRIEF.md` 250 final) — the signature of
reading a file mid-write; a round where the refusal was hit **four times**, costing one wasted
`harness-pm` spawn; and two of three run verdicts inferred from disk that were wrong, `plan2b`
returning `BLOCKED` where `PASS` had already been recorded. DEC-199 records the count as a floor, at
least eight, and occurrence 7 as a false verdict committed to the durable record. Issue #280 is the
other half: interrupting a parent on this host leaves its children running, measured three times
during FEAT-14, one orphaned review panel completing about **40 minutes** after its lead had reported
and returning findings against state that had moved. Leads burn context holding turns open as a
workaround, and the record acquires statements nothing detects as false.

## Goal

Claude Code can suspend a parent with live children without polling or fabricating a terminal
verdict. If the parent is interrupted, children may finish analysis but cannot race a replacement
writer **on the two governed write routes the harness gates** — a generic `Bash` write to a
canonical artifact inside the writer's own domain is not covered, and `## Verification gaps` names
that route; a resumed parent explicitly adopts or discards the result. OMP behaviour does not change.

## Requirements

- REQ-01: A Claude Code parent with a live child never polls, sleeps, emits a heartbeat, or
  fabricates work to stay alive. Zero polling, not a budget.
- REQ-02: A Claude Code parent may end a normal turn while its children are live by making a
  nonterminal suspension that carries no terminal verdict, and is never forced to assert a verdict
  about work it cannot see.
- REQ-03: When a child completes, the host resumes the same parent, and no replacement parent is
  dispatched into a live child's write.
- REQ-04: A live child of an interrupted parent may finish read-only analysis, and its writes to
  canonical feature artifacts are quarantined instead of landing **on the two governed write routes
  the harness gates** — the `Write`/`Edit` editor route through `check-domain.sh`, and the
  `plan-merge.py` mutating verbs plus `quarantine.py adopt` through `plan-sign-gate.sh`. A generic
  `Bash` write to a canonical artifact that lies inside the writer's own domain is NOT covered
  (D-19).
- REQ-05: A quarantined result becomes canonical only by a resumed parent's explicit adoption.
  Adoption and discard are both explicit acts; neither is a default and neither is a timeout.
- REQ-06: A terminal digest is required only after completion or after adoption, never while a child
  is in flight.
- REQ-07: OMP lifecycle behaviour is unchanged: `blocking: true` nested edges, process-owned
  supervision, and every OMP-path assertion in DEC-204 continue to hold.

## Constraints

**What SUPPLIES the mechanism**

- DEC-204 supplies the schema-2 claims registry, feature-scoped single-flight keyed
  `(feature, persona)`, `runtime` on every claim, process-owned OMP liveness and the Claude Code
  1200s TTL. The quarantine boundary reads that registry; it does not replace it.
- DEC-199 supplies the one locked union-merging core, `harness_merge.py`, and `plan-merge.py` on top
  of it. Adoption of a quarantined `plan.yaml` goes through that union, never a whole-file replace.
- DEC-201 supplies the never-wait conduct this feature must not weaken: a dispatch ends the turn and
  the platform wakes the caller. REQ-02 gives that turn-end a legal shape; it does not license a wait.
- `team-config.yaml`'s `shared:` list supplies the existing "owned by nobody, writable by any
  specialist" mechanism, which is how a quarantined write reaches disk without twelve new grants.

**What BLOCKS**

- DEC-174 blocks a squad route on the enforcement layer. `validate-digest.py`, `check-domain.sh`,
  `dispatch-guard.sh` and the test file of each are executed directly by the main session;
  `inflight_registry.py` is inside the same category because both hooks import it and its answer is
  the gate's answer.
- `check-domain.sh --resolve` returns **NOBODY**, re-measured at `ad93d43e` from the main
  checkout, for `.claude/skills/harness/SKILL.md`, `.claude/skills/harness-team/SKILL.md`,
  `.harness/team-config.yaml` and `.claude/settings.json`, so tasks touching them are
  `main-session-direct` (DEC-179).
- **`plan.yaml` may not be hand-written, for a second and independent reason.** FEAT-41 (DEC-182
  reversed) gave `check-domain.sh` a route denial that exits 2 on a `Write`, `Edit` or
  `NotebookEdit` of any `plan.yaml` — for *every* author, the main session included, because it
  sits in the shape region and not the domain region. `plan-merge.py`'s verbs are the only route.
  A reader who knows only DEC-179 will reach for a `Write` and be refused by a rule DEC-179 does
  not mention.
- **A plan created by `plan-merge.py apply` cannot currently be signed**, and that blocks this
  BRIEF's own downstream gate rather than the BRIEF. Re-measured 2026-09-01 against main at
  `0bc57c88`, and it still holds: `apply` exits **8** on a proposal carrying an `approval:`
  mapping onto an absent destination, and `sign-approval` exits **5** on a plan that carries no
  `approval:` mapping. Recorded as blocking question Q1 in
  `notes/research-reanchor-c1.md`; it is a harness defect, not a scope item for this feature.
- Issue #628 is out of scope. FEAT-32 shipped `plan-merge.py` for it; it closes separately.
- FEAT-35 and FEAT-37 already shipped the orchestrator and lead stop-and-wake playbooks. This
  feature adds the host-compatibility half they did not cover and must not restate their rules.

## Success Criteria

- SC-01: At the reviewed sha, `validate-digest.py --hook` on a `harness-product-lead` payload whose
  registry holds one live claimed child ACCEPTS (exit 0) a return whose `VERDICT:` is `SUSPENDED` and
  whose `awaiting:` names that child, and REFUSES (exit 2) the byte-identical payload carrying
  `VERDICT: PASS`. Both exit codes come from completed runs of the same binary.
  verify: automated        evidence: integration
- SC-02: The suspension cannot be used as an escape from the digest contract. `VERDICT: SUSPENDED`
  exits 2 when the registry holds no live child for that parent, when `awaiting:` omits a live child,
  and when the returning persona is neither a lead nor the orchestrator. Each of the three is its own
  assertion; a single whole-file search would be satisfied by the two easy ones.
  verify: automated        evidence: integration
- SC-03: A suspension is not a completion: after a `SUSPENDED` return the parent's own claim is still
  live in the registry, and after a terminal return it is released. Both states are read back from
  the registry file, not inferred from the exit code.
  verify: automated        evidence: integration
- SC-04: `check-domain.sh` refuses (exit 2) a governed persona's `Write` to
  `.harness/harness/features/<FEAT>/BRIEF.md` when the registry holds at least one live claim for
  that feature and none for that persona in that session, and its stderr names the exact quarantine
  path to write instead. The same write exits 0 when that persona's own claim is live. Both cases run
  the real hook with a real registry file. `BRIEF.md` and not `plan.yaml`: an editor write of
  `plan.yaml` already exits 2 for every author at `ad93d43e` under FEAT-41's route denial, so a
  `plan.yaml` case would pass unchanged against the pre-change hook and prove nothing. The pairing
  is graded as one criterion with a third assertion: an orphan `Write` of `plan.yaml` still exits 2
  carrying the FEAT-41 route-denial text, never the quarantine text. This criterion therefore says
  nothing about the route by which `plan.yaml` is actually written, which is `plan-merge.py` through
  `Bash`; SC-11 grades that route, and SC-04 passing while SC-11 fails is exactly the hole SC-11
  exists to catch.
  verify: automated        evidence: integration
- SC-05: Quarantine stops writing, not thinking. For the same orphaned persona, a `Write` to its
  granted `notes/` path and a `Write` to the quarantine path both exit 0 while the canonical
  `BRIEF.md` write exits 2, and no canonical artifact is modified by the refused call.
  verify: automated        evidence: integration
- SC-06: Adoption is explicit and lossless. `quarantine.py adopt` on a quarantined one-task
  `plan.yaml` against a canonical 14-task `plan.yaml` yields a canonical file carrying all 14 tasks
  plus the adopted one — never the 1-task file — and `quarantine.py discard` removes the quarantine
  directory. Neither happens without the command being run: `quarantine.py list` leaves both the
  canonical and the quarantined file byte-identical, proven by sha256 before and after, and no code
  path schedules either act on a timer.
  verify: automated        evidence: integration
- SC-07: The OMP path is unchanged, and the check can go red. For a claim with `runtime: omp` and a
  live supervisor pid, the quarantine verdict is allow at both the registry level and the hook level
  even when no session matches; `check-omp-port.py` exits 0; every `.omp/agents/harness-*.md` except
  `harness-orchestrator.md` still declares `blocking: true`; and `run-unit-tests.sh --kind
  integration` and `--kind unit` both pass. Discrimination is demonstrated: removing the runtime
  condition from the quarantine predicate turns the OMP case red.
  verify: automated        evidence: integration
- SC-08: A reviewer reads `git show <review_sha>:.claude/skills/harness/SKILL.md` and
  `git show <review_sha>:.claude/skills/harness-team/SKILL.md` and cites `file:line` for each of
  four clauses: the suspension is the legal turn-end while a child is live; the parent does not poll,
  sleep, heartbeat or invent work; the same parent is resumed and no replacement is dispatched while
  a child's claim is live; and a resumed parent checks for a quarantined result and adopts or discards
  it explicitly. The reviewer states in one line why a parent reading only these four would not poll.
  Any missing clause is not_met even when SC-01 through SC-07 pass.
  verify: inspection
- SC-09: The decision record carries the WHOLE contract, not just the code and not just half the
  boundary. A new entry in `.harness/harness/docs/DECISIONS.md` states the suspension return shape,
  the quarantine write boundary, explicit adoption, and the clause that OMP behaviour is unchanged;
  its `DECISIONS-INDEX.md` row names the compatibility host in the hand-written ruling half; and
  `gen-decisions-index.py --stdout | diff -` against the committed index is clean. The entry
  additionally names **both** enforcement points **by script name** — `check-domain.sh` for the
  `Write`/`Edit` half on `BRIEF.md`, `feature.json` and `STATE.md`, and `plan-sign-gate.sh` for the
  `PreToolUse` `Bash` half, including `quarantine.py adopt` — and states in one sentence that
  `plan.yaml`'s write route is `plan-merge.py` through `Bash`. Naming only `check-domain.sh`, or
  resting `plan.yaml`'s coverage on FEAT-41's editor route denial, is `not_met`: that is the belief
  SC-11 exists to overturn, and an entry asserting it would understate the contract that shipped.
  Asserted in the suite by `test-gen-decisions-index.py`, which is in `run-unit-tests.sh`
  `INTEGRATION_SCRIPTS`, not only by a one-off command; each clause is its own assertion, because a
  whole-region search for two script names is satisfied by the one that is present. The check can
  go red: an entry carrying `check-domain.sh` but no `plan-sign-gate.sh` fails the suite.
  verify: automated        evidence: integration
- SC-10: **WITHDRAWN, not unmet.** It required the operator to interrupt and resume a real Claude
  Code parent, then verify quarantine and explicit adoption by hand. On 2026-09-02 the operator
  explicitly chose to skip this Claude Code-specific UAT and withdraw the criterion. The feature
  therefore ships without live-host evidence that the compatibility parent resumes correctly.
- SC-11: The quarantine boundary covers the `Bash` route, not only the editor route — and it is
  graded on `plan-sign-gate.sh`, the `PreToolUse` `Bash` hook, by name. At the reviewed sha, with a
  registry holding one live non-`omp` claim for `<FEAT>` held by another persona in another session,
  running `plan-sign-gate.sh` with `agent_type: harness-pm` refuses (exit 2) each of
  `plan-merge.py apply --file .harness/harness/features/<FEAT>/plan.yaml --proposal p.yaml`,
  `plan-merge.py set-task-station --file <the same plan.yaml> ...`, and `quarantine.py adopt` on a
  quarantined `plan.yaml` for that feature, and each refusal's stderr names the exact quarantine
  path; the byte-identical calls exit 0 when that persona's own claim is live, and exit 0 when the
  claim's `runtime` is `omp`. Asserted against `plan-sign-gate.sh` and not against a fact both
  routes happen to satisfy, because at `ad93d43e` `.claude/settings.json` registers
  `check-domain.sh` on `PreToolUse` for `Write|Edit` only, so a criterion graded on
  `check-domain.sh` alone is met while `plan.yaml`'s only writer travels an ungated route. The check
  can go red: with the quarantine rule removed from `plan-sign-gate.py`, or with the suite pointed
  by `PLAN_SIGN_GATE_BIN` at a pre-change copy of the gate, the three refusals return exit 0.
  verify: automated        evidence: integration
- SC-13: The catch-all `inflight_registry` fail-open is observed on **both** quarantine routes, and
  by more than its exit code. At the reviewed sha — the two test files read at
  `git show <review_sha>:.claude/skills/harness/bin/test-check-domain.py` and
  `git show <review_sha>:.claude/skills/harness/bin/test-plan-sign-gate.py`, so an uncommitted case
  cannot satisfy this — each file carries two fail-open cases: one where the registry call itself
  RAISES (the registry path is a directory, which raises `IsADirectoryError` out of `orphan_write`)
  and one where `inflight_registry` is UNIMPORTABLE (removed from a `copytree` copy of the bin
  directory that the hook is then fired from). Each of the four asserts BOTH the **exact** exit code
  `0` AND that stderr names the unenforced quarantine boundary. Each surface additionally carries a
  negative control: with the registry healthy and a live orphan claim for the feature held by another
  persona in another session, the refusal still fires at exit 2. The check can go red, by these
  specific mutations: (a) delete the two cases from **either one** of the two files and this is
  `not_met` even though every case in the other file still passes; (b) drop the stderr half of each
  fail-open case, keeping only the exit code, and the criterion is `not_met` because exit `0` alone
  cannot distinguish a deliberate fall-through from a handler that silently swallowed everything;
  (c) replace the handler's `except` body with a bare allow that prints nothing and the four stderr
  assertions go red, or widen the handler to swallow every exception and both negative controls
  return exit 0.
  verify: automated        evidence: integration

## Verification gaps

- `test_kinds.component`, `ui`, `eval` and `typecheck` all have `cmd: null` and
  `status: unresolved`; `functional` is excluded under DEC-187. No SC above rests on any of them.
  The playbook task is `change_type: docs` under DEC-70's narrowing — a markdown playbook an agent
  preloads is graded by CONDUCT, not by a dataset eval — so no `eval` is owed.
- **No runner in this repository executes a markdown playbook.** SC-08 grades text a human reads.
  SC-10, formerly the only live-host evidence of a parent's actual conduct under interruption, was
  withdrawn by the operator on 2026-09-02. The Claude Code compatibility behavior is therefore
  unverified in a live host at ship time.
- The TTL is the compatibility host's honest limit, not a bug to be fixed here. Claude Code exposes
  no durable child-process owner, so beyond `CLAIM_TTL_SECONDS` (1200) the harness cannot distinguish
  a suspended parent from an interrupted one and fails safe: the write is quarantined and adoption is
  required. A member running longer than 20 minutes will therefore meet the quarantine path on a
  normal run too. That cost is accepted rather than papered over, and it does not exist on OMP.
- **`quarantine.py discard` is deliberately NOT covered by the quarantine boundary, and SC-12 was
  WITHDRAWN rather than graded.** Panel finding `PF-2b48984b50ff69c5dfdf8afa20c3956b` measured that
  `bash-write-guard.sh` already permits a plain `rm -rf` of a quarantine directory — it exempts
  `harness-dev-ops` outright, and on the `shared` verdict D-06's own
  `.harness/*/features/*/quarantine/**` glob produces it prints a notice and continues — so a rule
  covering only `quarantine.py discard` would have recorded a protection the tree does not have.
  Nothing in this feature therefore proves that an orphan cannot destroy a quarantined result, and
  no success criterion and no decision entry may claim that it does (D-18). Generic deletion
  enforcement for quarantine directories is out of scope here and is filed as backlog. The `SC-12`
  number is left as a gap on purpose: renumbering would silently re-point `T-10`'s grade.
- **A generic `Bash` write to a canonical artifact is NOT covered by the quarantine boundary, which
  is why REQ-04 and the `## Goal` now name their two governed routes.** Panel finding
  `PF-c7ab6506f6ffde4765e238519f337887` measured it: with `agent_type: harness-pm` and a session
  holding no claim, `cp /tmp/evil.md <worktree>/.harness/harness/features/FEAT-51-…/BRIEF.md` was
  fired at all three registered `PreToolUse` gates in the main checkout at `0bc57c88` and every one
  exited **0** — `bash-write-guard.sh`, `plan-sign-gate.sh` and `check-domain.sh`. The cause is at
  source: `bash-write-guard.sh:259-260` exempts `harness-dev-ops` outright and passes any in-domain
  write for every other governed agent, `harness-pm`'s `team-config.yaml` domain grants both
  `.harness/*/features/*/BRIEF.md` and `.harness/*/features/*/plan.yaml`, and `check-domain.sh` is
  registered for `Write` and `Edit` only. So issue #551's FIRST measured occurrence — a fourteen-task
  `plan.yaml` replaced whole-file — travels a route this feature does not close if the writer uses a
  generic shell write (`cp`, `cat`, `tee`, `mv`, `sed -i`, `python3 -c`) rather than an editor tool
  or `plan-merge.py`. Nothing in this feature proves otherwise and no criterion or decision entry may
  claim that it does (D-19). Generic write-route enforcement is out of scope here and is filed as
  backlog.

## Approval

status: approved
approved-by: Mike Ruangutai
date: 2026-09-01
