# BRIEF — BUG-1304 Prevent worktree agents from writing through relative main-checkout paths

## Problem

An agent dispatched to work in a feature's linked worktree edited the **main checkout** instead,
twice during the BUG-1286 cycle — caught by hand and reverted, main checkout verified clean
(row B-10, `.harness/harness/features/BUG-1286-test-tree-enforcement/notes/ship-review-2026-09-05-ship-final.md`).
The cause is structural, not carelessness: such an agent's process cwd is the main checkout, so a
bare relative path resolves into the session root and every existing guard reads it as in-base and
granted. The checkout binding that already exists covers feature ARTIFACT paths only — it derives
the feature id from the target path, so source, tests and docs, which carry no feature id, are
unbound (observed at `c369fb1f`: `check-domain.sh feature_checkout_guard`, keyed on
`RE_FEATURE_ARTIFACT = ^\.harness/[^/]+/features/([^/]+)/`). The `wrong_checkout` refusal (issue #895,
`harness_boundary.classify`) is the mirror case and cannot fire here: the target is in the session
root. Cost when it lands unnoticed: work written to the wrong branch, silently, with the worktree's
own copy of the file left stale.

## Goal

A governed agent that has been given a feature worktree can only write inside that worktree. If it
spells a governed path so that the write lands in the main checkout — or in another feature's
checkout — the write is refused before it happens, on both governed write routes, with a message
that names where the write belongs. Nothing an unbound agent, the main session, or a correctly
placed worktree write does today changes.

## Requirements

- REQ-01: The rule binds exactly the agents that have somewhere else to write: a governed agent
  (`harness-*`) that holds a live claim for a feature which has a linked worktree. An agent holding
  no live claim, an agent whose claimed feature has no linked worktree, and the main session (which
  carries no agent identity and is the DEC-174 executor of gate-script work) are all unbound and
  unaffected.
- REQ-02: The refusal is decided by the write's **resolved destination**, never by the path's
  spelling. A destination outside the agent's assigned worktree is refused whether it was written
  relative or absolute; a relative path that resolves inside the assigned worktree is allowed.
  Spelling is the cause of the observed incidents, not the harm: at `c369fb1f` the same claimed path
  already exited 0 relative and 2 absolute on an unrelated rule (`check-domain.sh _claimed_abs`
  docstring, measured at `f1ae55f2`), so a spelling rule would both refuse legitimate relative work
  and miss the identical damage done absolutely.
- REQ-03: Legitimate traffic keeps working unchanged: any write whose destination is inside the
  assigned worktree; every write by an agent with no live claim, including to the main checkout;
  every main-session write; scratch paths outside every checkout; and reads, which never reach a
  write guard. FINDING, not assumption: no governed path a worktree-bound agent must write in the
  main checkout was found at `c369fb1f`. The shared control-plane state that does live at the owner
  root — `.harness/.inflight-claims.json` (`inflight_registry.REGISTRY_REL`) — is mutated in-process
  by hooks or by a `python3` CLI call, and the Bash guard's write findings are only redirects,
  `sed`/`perl -i`, `tee`, `mv`/`cp`, `rm`, `sponge` and `awk -i`, so no such mutation is a governed
  write on either route.
- REQ-04: Both governed write routes refuse identically — the Write/Edit route and the Bash route.
  Neither is a non-goal: DEC-208 ruling 4 and DEC-193 both record that a divergence between the two
  surfaces is a bypass by construction, and the Bash guard exists because an agent routed around the
  other one.
- REQ-05: When the assignment cannot be resolved the answer is split by cause, and all three halves
  are required. **Unbound is allowed:** an agent holding no live claim, and an agent whose every live
  claim names a feature with no linked worktree, are outside the rule — this is the rule's own
  scope, not a compromise. **Bound but unplaceable is refused:** an agent holding at least one live
  claim that resolves to a linked worktree is refused when the destination lies inside none of
  those worktrees, when the destination checkout's `.git` pointer does not parse, or when one of
  its own live claims resolves ambiguously (`harness_boundary.AmbiguousWorktree`, two
  prefix-matching worktrees); the refusal names the worktrees the agent holds and, where it can be
  resolved, the destination's proper home. **Bound-or-not is unanswerable is also refused:** a
  registry file that exists among the scanned roots but cannot be read as a claim list —
  unparseable JSON, a payload that is not a JSON object, or a schema that is neither version 2 nor
  migratable — leaves the claim set INCOMPLETE, so an agent that would otherwise be bound cannot be
  shown to be unbound; the governed write is refused, naming the file to repair, and the unreadable
  root is never silently read as "no claims here". That is the identical shape this requirement
  already refuses in an unparsed destination `.git` pointer — a record that exists, claims to carry
  the answer, and cannot be read — and it matches the fail-closed treatment an unparseable manifest
  already gets on both routes (`bash-write-guard.sh:684-694`). `inflight_registry._parse` treats
  such a file as empty (`:56-65`) deliberately, for the CLAIM/WRITE path, and that fallback is
  pinned by `case_8_corrupt_registry` (`tests/integration/test-inflight-registry.py:329`); the
  READ/REFUSAL path this bug adds must not inherit it. Chosen fail-closed because the guarded
  direction is precisely the one REQ-03 found has no legitimate case, so refusing costs nothing
  real, while a wrong guess writes to the wrong branch; it also matches the treatment an unparsed
  worktree pointer already gets on both routes. THAT REFUSAL IS SCOPED, NOT FACTORY-WIDE: it binds
  exactly the governed writes the READABLE roots cannot place. A destination that lies inside a
  worktree proven by a readable registry stays allowed while an unrelated scanned registry is
  unreadable, because a destination already inside a proven member stays inside the claim set
  however many members the unreadable root would have added. REQ-03 is therefore not amended: its
  promise that a write inside the assigned worktree keeps working is kept unconditionally. A defect
  inside the guard's own code keeps failing open, unchanged.
- REQ-06: A refusal is actionable: it names the worktrees the agent holds and the destination the
  agent should have written, and never advises removing a worktree. For a destination under the
  control-plane root's `.harness/expertise/`, the advice is the sanctioned CLI
  (`python3 expertise-merge.py apply`), never "write it in your worktree" — that destination is
  legitimately outside every worktree and is reached by route, not by relocation.
- REQ-07: The boundary this bug settles is recorded where the harness reads doctrine — as a `D-NN` in
  this feature's plan, and, because it extends the checkout binding's source of truth from the target
  path to the run's own record, as an entry in `DECISIONS.md` with its index row.

## Constraints

- SUPPLIES — DEC-208 (ruling 2 and ruling 4): the checkout binding, its both-route completeness, and
  `harness_boundary.worktree_for_feature`, which resolves the assigned checkout by prefix and raises
  rather than guessing on two candidates. This bug widens that rule's reach; it does not replace it.
- SUPPLIES — DEC-193: one shared implementation in `harness_boundary.py`, imported by both guards,
  identifying a checkout from its own `.git` pointer without forking git.
- SUPPLIES — `inflight_registry`, which already records a live claim carrying `feature` and `cwd`,
  and resolves a feature's checkout via `feature_root`.
- BLOCKS — DEC-174: both guards and their tests are gate scripts, so the harness plans this and never
  executes it; every task lands `execution_mode: main-session-direct` and DEC-179/DEC-183 route
  checking applies at plan time.
- BLOCKS — DEC-110 and DEC-100: agent identity reaches a write guard only through the hook
  payload's `agent_type`, and only exit 2 blocks a write. The write-route payload is
  `{agent_type, hook_event_name, cwd}` (`basePayload`, `.omp/extensions/harness-hooks.ts:215-217`);
  `session_id` is added only to the Task/dispatch payload (`:719-723`), never to a Write, Edit or
  Bash payload, and Claude Code carries no feature field on any write payload either. There is no
  runtime agent-id environment variable (`plan-sign-gate.py` records `HARNESS_AGENT_ID` as a marker
  inside agent definition files, not an env var), so the persona is the whole write-payload
  identity.
- Existing behaviour that must not regress: DEC-153's carve-out RATIONALE, which survives intact —
  a perturbation proof keeps a legal home in a disposable checkout; the
  fail-open-on-missing-manifest rule, unchanged; and the `not_a_domain_question` pass-through for
  `/tmp`, unchanged. What narrows is that carve-out's EXTENSION, from any linked worktree to THE
  ASSIGNED worktree, per plan D-07 and T-06 on Advisor ruling 1 Q1
  (`notes/review-fable-advisor-plan-BUG-1304-dec153.md`), which found the rationale needs only the
  proving agent's OWN worktree and never a sibling's.

## Success Criteria

- SC-01: A governed agent holding a live claim for a feature with a linked worktree, writing a
  governed main-checkout path spelled relative, is refused with exit 2 on the Write/Edit route, and
  the stderr names the assigned worktree.
  verify: automated        evidence: integration
- SC-02: The same agent and the same destination reached through the Bash route (a redirect and an
  in-place `sed`, each its own case) is refused with exit 2.
  verify: automated        evidence: integration
- SC-03: The same destination spelled as an absolute path is refused identically on both routes,
  proving the trigger is the destination and not the spelling.
  verify: automated        evidence: integration
- SC-04 (negative — legitimate traffic): five cases, each asserted separately, exit 0 under the same
  live claim or its absence: a write whose destination is inside the assigned worktree spelled
  relative; the same spelled absolute; a write to the same main-checkout path by a governed agent
  holding no live claim; a scratch write under a temporary directory outside every checkout; and a
  main-checkout write by a governed agent whose only live claim names a feature with no linked
  worktree. The last case is asserted discriminatingly: the claim sits in the main checkout's own
  registry and that registry IS scanned, and the write is allowed because
  `harness_boundary.worktree_for_feature` returns None for that feature so the claim contributes no
  worktree — not because the main-checkout registry was skipped.
  verify: automated        evidence: integration
- SC-05: An agent holding at least one live claim that resolves to a linked worktree is refused
  with exit 2 on both routes in each of two unresolvable cases, asserted separately: a destination
  checkout whose `.git` pointer does not parse; and one of its own live claims whose feature
  resolves to two prefix-matching worktrees (`harness_boundary.AmbiguousWorktree`). The stderr
  names the worktrees the agent holds, and in the ambiguous case the candidates it declined to
  choose between.
  verify: automated        evidence: integration
- SC-06: Every case in SC-01 through SC-03 and SC-05 is demonstrated to pass (exit 0, unrefused)
  against the pre-change copy of the two guard scripts, run in the same test, so each new assertion
  is shown to be discriminating rather than ever-green. **An exit 0 out of a fail-open branch is not
  an unrefused write, so every pre-change call must also prove the frozen guard RAN.**
  `check-domain.sh` exits 0 after printing on its quarantine-boundary exception (`:1864-1869`,
  `quarantine boundary was not enforced ... passing through`) and on a missing manifest (`:383-386`,
  `enforcement OFF`); `bash-write-guard.sh` fail-opens SILENTLY at exit 0 on an unparseable payload
  (`:78-80`) and on a missing manifest (`:267-269`). Each pre-change call therefore asserts both:
  (a) its stderr contains none of the substrings `enforcement OFF`, `was not enforced`,
  `passing through`; and (b) a POSITIVE CONTROL fired at the same frozen guard, in the same
  isolated bin tree and the same environment, is still refused with exit 2 — the run-artifact
  refusal on the Bash route, a governed out-of-domain write on the Write route. Half (b) is what
  covers the Bash route's silent fail-opens, which half (a) cannot see. The criterion fails if any
  pre-change assertion carries only the exit code.
  verify: automated        evidence: integration
- SC-07: The boundary is present in the governing record at the pinned review sha, read with
  `git show <review_sha>:<path>` and never from the working tree. Two halves, both required. In
  `plan.yaml`, each of the five boundary questions is answered by the decision that carries it, and
  each is graded against that decision by id: **who is bound** — D-01 (empty claim set means unbound
  and allowed; non-empty binds); **destination, not spelling** — D-01 (the refusal turns on the
  write's resolved destination); **preserved traffic** — D-05 (the control-plane Expertise carve-out,
  stated by route) together with D-06 (the DEC-189 second base left unbound); **both routes refuse
  identically** — D-08; **unresolvable assignment** — D-01 for the refusal rule and D-02 for how a
  claim resolving to no worktree and a claim resolving ambiguously are each treated. In
  `DECISIONS.md`, one entry with its `DECISIONS-INDEX.md` row states all five in one place. The
  criterion fails if any one of the five is absent from the decision named for it.
  verify: inspection
- SC-08: The rule holds under a short-form worktree name: with the linked worktree's basename
  `BUG-1304` while the feature directory and the claim's `feature` field are
  `BUG-1304-worktree-relative-path-guard`, a governed agent holding a live claim in that worktree
  is still refused with exit 2 on a governed main-checkout write, on both routes. No existing
  criterion binds this — every SC-01 through SC-06 fixture builds its claims inside a
  long-form-named worktree.
  verify: automated        evidence: integration
- SC-09: A governed agent holding a live claim for a feature with a linked worktree, where that
  claim is a compatibility-host claim (`runtime` `"claude"`) whose `started_at` is back-dated MORE
  than `inflight_registry.CLAIM_TTL_SECONDS` but LESS than
  `inflight_registry.OMP_UNVERIFIED_TTL_SECONDS` before now, is refused with exit 2 on a governed
  main-checkout write on BOTH routes, and each refusal is shown to exit 0 against the frozen
  pre-change copy of the same guard, in the same test, carrying SC-06's ran-proof in full: no
  `enforcement OFF`, `was not enforced` or `passing through` marker on that call's stderr, and the
  positive control still refused with exit 2 at the same frozen guard. `started_at` is stored data,
  so the fixture back-dates it directly and the case needs no clock mocking: it is deterministic,
  and it fails against any implementation whose claim enumerator filters with `_expire` or
  `CLAIM_TTL_SECONDS`.
  verify: automated        evidence: integration
- SC-10: A governed agent whose ONLY live claim sits in a registry file that exists among the
  scanned roots and cannot be read — unparseable JSON — is refused with exit 2 on a governed
  main-checkout write, on BOTH routes, and the stderr names the unreadable registry file rather
  than reporting the agent as unbound. Three parts in the same case, so it cannot be satisfied
  vacuously: the refusal itself; a PAIRED CONTROL in which the identical payload is fired against
  the identical fixture with that one registry file WELL-FORMED and holding no claim for that
  agent, which must exit 0 — proving the refusal is caused by unreadability and not by a blanket
  refusal of governed writes, and pinning the reason a claim-set-derived refusal cannot supply,
  since with a readable claim the write would be refused anyway; and SC-06's pre-change proof, the
  same payload exiting 0 against the frozen guard with no fail-open marker and the positive control
  still refused. It fails against any implementation whose enumerator returns an empty list for an
  unreadable root, which is what `inflight_registry._parse` does today.
  verify: automated        evidence: integration
- SC-11 (carried by T-09, which is IN SCOPE — the fourth binding ruling settled that and the
  criterion is not conditional on anything): with an injected `now` that makes a non-OMP claim
  dispatch-expired (older than `inflight_registry.CLAIM_TTL_SECONDS`) but younger than
  `inflight_registry.OMP_UNVERIFIED_TTL_SECONDS`, the claim is STILL PRESENT in the registry
  file's JSON on disk after `reconcile`, `live_children` and at least one of `orphan_write` and
  `release` has run over it, AND every one of those calls returns exactly the answer it returns
  today. The dispatch half is asserted separately and by behaviour: with such a claim retained in
  the file, a fresh `claim_with_receipt` for the SAME agent and SAME feature is still ADMITTED, so
  single-flight admission still reads the 1200s horizon and FEAT-37's unstranding is untouched. A
  claim past `OMP_UNVERIFIED_TTL_SECONDS` is still pruned from the file. Deterministic:
  `started_at` is stored data, so no clock is mocked. It fails against a read-side-only
  implementation, which leaves the file pruned, and against a shared-primitive change that
  stretches admission to the backstop.
  verify: automated        evidence: integration
- SC-12: The unreadable-registry refusal is SCOPED to the writes the readable roots cannot place,
  proven in one fixture on BOTH routes: the writer's own live claim sits in a READABLE registry
  that proves its assigned worktree, and one UNRELATED scanned registry among the same roots
  exists and holds unparseable JSON. Two assertions, each made separately on the Write/Edit route
  and on the Bash route: a write whose destination is inside the writer's OWN assigned worktree
  exits 0; and a governed MAIN-CHECKOUT write by the SAME agent in the SAME fixture exits 2 with
  stderr naming the unreadable file. The refusal half carries SC-06's full pre-change proof through
  `bug1304_assert_pre_change_allows` — exit 0 at the frozen guard, no `enforcement OFF`, `was not
  enforced` or `passing through` marker on its stderr, and the positive control still refused with
  exit 2. Deterministic: the corruption is stored bytes and no clock is mocked. It can fail in both
  directions, which is why the pair is one criterion: an implementation that requires every scanned
  registry to be readable before comparing the destination refuses the allow half, and an
  implementation that builds a partial claim set and then ignores the unreadable root allows the
  refusal half. SC-10 is a DISJOINT fixture — there the agent's only claim is the corrupt one, so
  the readable roots place nothing and the refusal stands under the same rule.
  verify: automated        evidence: integration

## Verification gaps

- No runner exercises the guards inside a real dispatch: `integration` fires them as subprocesses
  with synthetic payloads. The wiring from a live dispatch to a live claim to the payload identity is
  therefore proven by construction, not end to end — SC-01/SC-04 prove the guard's verdict given an
  identity, not that the identity a real dispatch produces is the one under test. Carried by the
  claim fixtures being built through `inflight_registry`'s own API rather than hand-written JSON.

## Approval

status: approved
approved-by: mruangutai
date: 2026-09-05
