# BRIEF — FEAT-10 Personal software factory, increment 1

## Problem

Today a feature only exists as a factory job while a session is open. The plan lives in this repo,
the work lives in whoever's head is running the session, and nothing outside this checkout can
answer "what is in flight and where is it". The moment the operator wants a second repo worked on —
the personal fleet is several repos, and the harness lives in exactly one of them — there is no
place to look. Wayfinding effort #181 closed sixteen tickets settling what the factory should be;
none of it is usable yet, because no single journey runs from an approved plan to a pull request in
a repo the harness does not live in.

## Goal

Make one journey work start to finish: **an approved plan in the harness repo becomes GitHub issues
on one cross-repo Projects v2 board, an agent claims the next one without any other agent being able
to take it, gets a prepared checkout of the target repo on its own branch, and the finished work
arrives back as a pull request the operator merges — with the board, not a session, holding the
state the whole way.** Everything else the effort settled — seats, plugin distribution, new-product
bootstrap, unattended loops — waits for a later increment.

## Requirements

- REQ-01: One GitHub board, spanning several repositories, shows the operator every piece of work
  the factory has in flight and which station each one is at.
- REQ-02: An approved feature plan turns into work items in the target repository's issue tracker,
  with no hand transcription. Running the publish again is safe.
- REQ-03: An agent can take the next available piece of work from the board. No two agents can ever
  take the same one.
- REQ-04: An agent working on a repository the harness does not live in gets a ready checkout of
  that repository, on its own branch, without the operator preparing anything by hand.
- REQ-05: Finished work reaches a target repository only as a pull request the operator merges.
  Nothing an agent runs lands on a default branch.
- REQ-06: One place, edited by the operator, states which repositories the factory operates and
  which board is its control plane.
- REQ-07: Board and issue state never overwrite the approval-gated plan. The signed plan stays the
  source of truth for what the work is.
- REQ-08: Whoever runs a factory tool can tell what happened from its outcome alone. A failure is
  never mistakable for "there was nothing to do". A successful run's output is machine-readable
  without guesswork.

## Constraints

**User-mandated, non-negotiable**

- GitHub is the single source of truth and the control plane for the factory. Durable work state
  lives in Issues and one Projects v2 board, not in a session and not in a local database.
- This increment must be a usable end-to-end slice, not a horizontal layer. The journey named in
  `## Goal` runs start to finish; no station is built in isolation.

**Fleet bounding — verified 2026-08-08 at 914b6fd**

- The fleet is the personal `mruangutai` repositories. Implentio company repositories are out of
  scope (effort #181 `## Out of scope`).
- `mruangutai/pilot-implentio-app` is personally owned but is Implentio product work, and is
  excluded on that basis rather than left ambiguous.
- Candidate targets confirmed to exist with `gh repo view` (exit 0 each): `mruangutai/harness`
  (public), `mruangutai/kaya-ai` (private, default branch `master`, two Actions workflows),
  `mruangutai/rental-property-automation` (private, default branch `main`).
- Two user-owned Projects v2 boards already exist: number 3 "Harness" and number 2 "kaya-ai"
  (`gh project list --owner mruangutai`, exit 0).
- The active `gh` token carries the `project` scope (`gh auth status`).

**Hard external limits measured in effort ticket #183**

- Personal accounts emit no board-event webhooks. Agents must poll; any push-based board automation
  is not available and must not be assumed.
- The Projects v2 auto-add workflow cap is 1 on Free and 5 on Pro. `gh api user --jq .plan.name`
  returns null here and the cause is not established, so which cap binds is unverified — this increment therefore
  uses no auto-add workflow at all and adds every board item explicitly.

**Harness constraints**

- The harness is not installed into target repositories in this increment. Effort ticket #185's
  plugin distribution is deferred; the tools run from this checkout and address other repos over
  `gh` and `git`.
- Changes to the five enforcement-layer scripts are made directly by the main session, never
  dispatched to a specialist (DEC-174).
- The outbound GitHub mirror is write-only by DEC-138. This increment needs a bounded read-back and
  amends that decision explicitly rather than working around it.

## Deferred to later increments — named, not implied

- Effort #185 — harness distribution as a pinned plugin plus private marketplace; target repos get
  no harness install here.
- Effort #189 — new-product bootstrap (repo creation, onboarding, CI skeleton, board wiring).
- Effort #186 — the full six-station field set, the four saved views, and priority/kind/size fields
  beyond the minimum the journey needs.
- Effort #187 — scheduled or unattended dispatch. Work starts because the operator starts it.
- Effort #188 — relaxing the middle human gates to auto-pass on clean gate history.
- Effort #190 — native auto-merge, one-landing-slot enforcement, and branch-protection rulesets.
- Effort #192 — named persistent seats and the expertise restructure.
- Effort #193 — charter and architecture-document injection for design roles.
- Effort #194 — work-unit caps for queue-driven work.
- Effort #195 — the stuck protocol (park, report, release the claim).
- Effort #196 — the change to what a task may commit beyond acceptance.
- Effort #197 — dispatch memos and the validator lead joining plan time.
- Reaping stale claim refs. Nothing in this increment removes a claim ref left behind by a dead
  agent, and effort #186's saved views reap board items, not refs — so the manual ref delete named
  in the residual below is the only remedy until a later increment owns the reaping.
- Issues **#198, #199 and #200 are already filed** on board 3 at Priority P1, from the plan review's
  Q4, Q5 and Q6. They are outside FEAT-10 scope and are recorded here so nobody re-raises them as
  findings against this brief.
- A **checker for the `traces:` line on every success criterion** — asserting that each REQ has at
  least one criterion proving it positively, and that no criterion cites a requirement the brief
  does not carry. It is a named follow-up candidate, deliberately NOT added to this increment: this
  block is prose markdown, no gate reads it, and adding a reader for it is a harness-wide surface
  change rather than factory work.
- **Bringing the two issue writers to parity.** `gh-sync.py` already draws the parent and sub-issue
  edges — `cmd_open` adopts or creates a parent, records `parent_origin`, and attaches every task —
  but writes no `blocked_by` edge at all. `factory_decompose.py` draws both. Reconciling the two
  writers is D-12's problem and is deferred with it, not fixed here.
- Per-agent GitHub identity. All factory writes in this increment are made as `mruangutai` on one
  credential; the git-ref claim, not the assignee, carries the distinction between agents. Effort
  #192 owns named persistent seats.

## Accepted residuals — stated so the signature is a knowing one

- **The claim wedge is downgraded, not eliminated.** Work behind a stuck item *is* reachable: the
  claim loop skips a candidate whose ref create is refused and moves to the next, so one unclaimable
  item can no longer stop the queue. That is the property that matters and REQ-03 holds on it. What
  survives is narrower and, within this increment, permanent. An agent that dies between creating
  the claim ref and writing its bookkeeping — the label, the assignee, the station — leaves an item
  that is open, still at `ready`, unlabelled and unassigned. It passes the claimability pre-filter
  forever and its ref create fails forever, so such items accumulate without bound, each costing one
  skipped candidate per poll per agent. Recovery exists but is operator-manual: delete the ref by
  hand. The documented "re-run with `--issue <n>`" recovery belongs to the owning agent, which in
  this failure is dead. Accepted for increment 1; the stuck protocol that would release such a claim
  is effort #195, deferred above, and the operator's signal that this residual is biting is SC-13
  clause (b).

## Success Criteria

**Every criterion carries a `traces:` line naming the requirements it proves**, in the same
bracket-list form `plan.yaml` already uses for a task's `traces:` — one shape, so one future check
can read both surfaces. Be plain about its status: **nothing gates this today.** This block is prose
markdown and no harness script reads it, so the trace is mechanically *checkable*, not mechanically
*checked*. A checker that asserts every REQ has at least one positively-proving SC is a named
follow-up candidate under `## Deferred`, deliberately not added to this increment.

Criteria are grouped by what they prove: the first group proves the factory **works**, the second
proves it **refuses correctly**. Both are load-bearing — a factory that refused every request would
satisfy the second group alone, which is the imbalance this rework corrects.

### The factory works — positive criteria

- SC-16: Publishing a signed plan of N tasks creates exactly N **task** issues in the target
  repository. At most one feature parent is created beside them, only when none is recorded, and it
  is counted separately. Each task issue is added to the board and its station set to the fleet's
  `ready` option. Each task issue carries the labels `harness` and `feature:<FEAT>`. Each task issue
  body is the task's `intent` verbatim, then a blank line, then `change_type:` and `traces:` in that
  order, and nothing else.
  verify: automated        evidence: unit        traces: [REQ-01, REQ-02]
- SC-17: The published board carries the plan's dependency graph. Every task issue is a sub-issue of
  the one feature parent. Each task issue carries exactly one `blocked_by` edge per entry in its
  plan `depends_on`, asserted for the six-blocker task specifically. The parent is never added to
  the board. A second publish, run against the recorded edge ledger, draws zero duplicate edges.
  verify: automated        evidence: unit        traces: [REQ-01, REQ-02]
- SC-22: **The block marker is honest: the claim tool does not hand out work whose blockers are
  unfinished.** Given a ready column whose **lowest-numbered** candidate has an open `depends_on`
  blocker and a higher-numbered candidate has none, the tool claims **the clear candidate and not
  the blocked one**. That is asserted as the issue number the create-if-absent call was made for,
  exactly once, not as the exit status. The skip is reported on stderr with a reason distinct from
  every other skip reason. Given a ready column in which *every* candidate has an open blocker, the
  tool exits 1 with zero mutating calls and stderr reads `no claimable work`. With every blocker
  closed, the formerly blocked lowest-numbered candidate *is* claimed, so refusing everything does
  not satisfy this. A candidate carrying several blockers is skipped while any one of them is open,
  and becomes claimable only when the last one closes. A `depends_on` entry that resolves to no
  issue counts as blocked. An issue with no `feature:` label is not gated and stays claimable. A
  fresh `--issue` claim naming a blocked issue refuses with exit 2, which is distinguishable from
  exit 3.
  verify: automated        evidence: unit        traces: [REQ-03, REQ-07]
- SC-18: One fleet loader is the only reader of the fleet file, and a well-formed fleet is usable
  through it. The file loads and its board, station and repository values round-trip. `--show` emits
  them as one JSON object. The workspace checkout path is derived from the fleet's `workspace_root`
  by that one shared function, so two tools cannot look in two directories.
  verify: automated        evidence: unit        traces: [REQ-06]
- SC-19: The whole journey runs end to end without a human, observed as real processes. Against stub
  `gh` and `git` binaries, and a fleet file outside the harness checkout: publish creates the issues
  and boards them at `ready`; claim returns exactly one payload and moves that item to `building`;
  workspace produces a checkout on `factory/issue-<n>`; land pushes that branch, opens a pull
  request and moves the item to `review`. Each step exits 0 and its whole stdout parses in one
  `json.loads`.
  verify: automated        evidence: integration  traces: [REQ-01, REQ-02, REQ-03, REQ-04, REQ-05]
- SC-20: A publish leaves the feature's `plan.yaml` and `BRIEF.md` byte-identical. The feature's
  `feature.yaml` factory block is the only harness file content that changed. This is asserted by
  hashing the feature directory before and after the run, not by reading the source.
  verify: automated        evidence: unit        traces: [REQ-07]
- SC-01: Publishing an approved plan twice creates each task's issue exactly once, adds each to the
  board exactly once, and draws each edge exactly once. Given a `feature.yaml` ledger that
  accurately records the first run, the second run mutates nothing.
  verify: automated        evidence: unit        traces: [REQ-02]
- SC-04: Workspace preparation produces a checkout on a branch named for the claimed issue. It never
  leaves the checkout on the repository's default branch.
  verify: automated        evidence: unit        traces: [REQ-04]
- SC-05: The landing tool opens a pull request. It never issues a merge, and it never pushes to a
  default branch.
  verify: automated        evidence: unit        traces: [REQ-05]
- SC-12: The claim tool takes ownership with a create-if-absent marker, and it must handle both
  answers it can get. If the marker is created, it proceeds and emits a payload. If the marker
  already exists, it stops, exits with code 3, and writes nothing — no label, no assignee, no
  station move.
  verify: automated        evidence: unit        traces: [REQ-03]
- SC-11: For each of the five tools with a command line, the whole of stdout on a successful run
  parses as one JSON document. No diagnostic, warning or progress line is interleaved into it. On
  the "nothing to do" and refusal paths stdout is empty and the explanation goes to stderr.
  verify: automated        evidence: unit        traces: [REQ-08]

### The factory refuses correctly — negative and invariant criteria

- SC-03: No factory tool writes to a feature's plan, brief, or approval block. The only harness file
  they write is the feature's own `feature.yaml` factory block.
  verify: inspection        traces: [REQ-07]
- SC-06: The state check fails when a feature records a claimed issue in a repository the fleet file
  does not list.
  verify: automated        evidence: integration  traces: [REQ-06]
- SC-21: A station option name that the fleet declares but the board does not offer refuses with
  exit 2, before any board read, naming the missing option, the station field and the fleet file. It
  never reports zero items and exit 0, which is indistinguishable from an empty queue forever.
  verify: automated        evidence: unit        traces: [REQ-06, REQ-01]
- SC-08: Every factory tool takes its repository and board from the fleet file. It refuses to infer
  either from the working directory.
  verify: automated        evidence: unit        traces: [REQ-06]
- SC-09: The decision record states the read-back scope. Issues are the interface and the signed
  plan is the truth. Read-back is permitted for exactly three purposes and no others: whether an
  item is claimed, which station it is at, and whether a blocker issue is finished. The record names
  DEC-138 as the write-only baseline the third purpose amends. It states that the rendered
  `blocked_by` edge is never read back. It states the cost of the widening: one blocker-state read
  per blocker per candidate, bounded by the ready column. The propagation checker is clean
  afterwards.
  verify: inspection        traces: [REQ-07]
- SC-10: A factory tool that cannot reach `gh` — missing or unauthenticated — exits with status
  **2 and never 1**. It writes nothing at all to stdout. It emits one stderr line naming a value the
  operator can act on. An unexpected exception inside any entry point exits 2 as well, rather than
  Python's default 1. Exit 1 means only "nothing to do", so a failure that exits 1 is
  indistinguishable from an empty queue. "Non-zero" alone does not satisfy this.
  verify: automated        evidence: unit        traces: [REQ-08]
- SC-13: One stale item never blocks the queue, and an exhausted queue says which kind of empty it
  is. Two clauses, both binding:
  (a) A ready column whose lowest-numbered item is not claimable still yields a claim of the next
  claimable item: the tool exits 0 with a payload, not non-zero. An item is not claimable when it is
  already marked, already assigned, its issue is closed, its claim marker is already taken, or it is
  **blocked by a `depends_on` blocker that is not finished**.
  (b) A ready column in which *every* candidate is unclaimable exits 1 having mutated nothing, and
  reports which of the two exit-1 causes it was: stderr reads `no claimable work` and never `no work
  available`, so a queue full of stuck items is distinguishable from an empty one.
  Both clauses rest on this: every skip named in clause (a) reports its own reason on stderr, and no
  two of those reasons read alike. That includes the skip taken when the claim marker is already taken, which is the only path
  a claim ref left behind by a dead agent takes through the loop.
  verify: automated        evidence: unit        traces: [REQ-03]
- SC-14: For every tool, each refusal path reached before that tool's stated point of no return
  performs zero mutating calls. This is asserted over the full recorded call list, not over one
  call.
  verify: automated        evidence: unit        traces: [REQ-08]
- SC-15: Each of the five command-line tools' exit statuses is observed as a real process exit
  status, from a forked run against stub `gh` and `git` binaries. An entry point that never reaches
  the shared wrapper is caught, rather than passing every in-process assertion.
  verify: automated        evidence: integration  traces: [REQ-08]

SC-02 is retired and its id is not reused. It was written against an earlier claim mechanism in
which meeting an item somebody else owned ended the run; the claim is now a create-if-absent ref
whose refusal makes the poll path move to the next candidate. What it reached for is carried by
SC-12, the tool's half of atomicity on the refused create, and by SC-13, the queue not stopping at
one unclaimable item. REQ-03 is covered by SC-12, SC-13, SC-22 and, since the outcome-first
rework, SC-19's forked end-to-end run.

One further criterion was deleted on 2026-08-08 and its id is not reused. It was this feature's only
`verify: uat` criterion: it asked the operator to watch the live board and, by hand, to race two
claim runs against one issue. The operator deleted it on the ground that a one-issue-in-flight cap, one issue per wake,
a single credential and push-first dispatch mean two concurrent claims on one issue cannot arise in
normal use, so staging that race by hand is anticipation. The git-ref claim mechanism, D-05 and
REQ-03 are unchanged by the deletion, and SC-19 remains the end-to-end proof.

**Requirement coverage, positively.** Every requirement now has at least one criterion that proves
the thing works, not merely that it refuses to work wrongly: REQ-01 by SC-16, SC-17 and SC-19;
REQ-02 by SC-16, SC-17 and SC-19; REQ-03 by SC-12's success branch, SC-13 clause (a),
SC-19 and SC-22's claim-the-clear-candidate direction;
REQ-04 by SC-04 and SC-19; REQ-05 by SC-05 and SC-19; REQ-06 by SC-18; REQ-07 by SC-20 and SC-22, which proves the signed plan's DAG governs what the
tool takes; REQ-08 by
SC-11 and SC-15. The negative group is unchanged in force — SC-13 and SC-14 in particular are
load-bearing and were not touched by the rework beyond gaining their `traces:` line.

Two qualifications on that paragraph, both about what the named criterion actually proves.
**REQ-04 and REQ-05 are proven against test doubles only.** The automated proof of REQ-04 and REQ-05
is SC-04 and SC-05 against a unit seam, plus SC-19 against stub binaries. No criterion exercises
either on a real repository: the criterion that did was the deleted `verify: uat` one.
**REQ-07's proof splits differently.** SC-20 is its *automated* proof and is one tool wide: it
hashes the feature directory across a single `factory_decompose` publish, so it exercises no other
tool. The *general* statement — that no factory tool writes a feature's plan, brief or approval
block — is SC-03 (`verify: inspection`), which also traces REQ-07 and sits in the negative group
below. The general claim holds structurally, because the read-back tools never open `plan.yaml` or
`BRIEF.md` at all, but it is a human inspection that records it, not SC-20's test.

## Verification gaps

- **This feature has ZERO `verify: uat` criteria and therefore NO UAT script, and the ship gate must
  say so rather than skip the step in silence.** The feature's only `verify: uat` criterion was
  deleted on 2026-08-08, so nothing here is evidence the operator produces by hand. The consequence, accepted by
  the operator on 2026-08-08 when the deletion was ruled: **no success criterion exercises the live
  GitHub API before ship.** The first real dispatch is the live verification. `harness.json` sets
  `gates.uat` to `blocking_when_uat_criteria_exist`; no reader of that key was found in
  `.claude/skills/harness/bin/`, and the `harness-uat` skill's own instruction for this case is to
  say there is no UAT and move on. That is why the fact is stated here, at the signature, rather
  than left to be inferred from a missing UAT file.
- `integration` has a runner but its detect glob (`tests/integration/**`) matches zero files in this
  repository, so the kind is only ever selected explicitly. SC-06, SC-15 and SC-19 rest on it, so this
  increment widens that glob to name the two test files that carry them rather than downgrading
  either criterion. The fork-level test is what supplies that kind with a file to run, and it is the
  only test here that observes a real process exit status. It is not justified by a `change_type:
  feature` matrix floor: the qa gate classifies a diff by reading it rather than by reading a task's
  `change_type`, and this increment ships no user interface, so that classification is not reached.
- Atomicity of the claim is proven in one half only, and the other half is proven by nothing before
  ship. The tool's handling of a create-if-absent primitive is a unit test against a seam (SC-12).
  That the primitive genuinely serialises two concurrent creators is exercised by no criterion at
  all: it is inferred from the endpoint being create-only, and nothing in this checkout can race two
  real agents. This is the residual the operator accepted when the `verify: uat` criterion was
  deleted.
- `functional`, `component`, `ui`, `eval` and `typecheck` have `cmd: null`. This increment touches
  none of their surfaces — it adds Python command-line tools and one configuration file, with no
  user interface, no component substrate and no model-behaviour change — so nothing here rests on a
  kind with no runner.
- The live board, the real target repository and the merge itself cannot be exercised from this
  checkout without mutating production state. **No criterion carries them: they are unverified
  before ship**, which is the consequence the operator accepted in deleting the `verify: uat`
  criterion. What SC-19 gives
  instead is the same journey against stub
  `gh` and `git` binaries: it proves the four tools compose into one working sequence, and it proves
  nothing about GitHub's own behaviour.
- The blocker gate SC-22 asserts is proven against a recorder and fixture plan files, never against
  the API. What is exercised is the tool's resolution path — `plan.yaml` `depends_on` to
  `feature.yaml`'s issue map to a scripted issue state — and its skip, claim and refuse behaviour.
  That a blocker issue's closed state arrives correctly from the live board is **unverified before
  ship**: no criterion asserts it. An earlier version of this note claimed the deleted `verify: uat`
  criterion carried it as an operator step. That claim was false even before the deletion, because
  that criterion's text never contained a blocker clause.
- The GitHub edges SC-17 asserts are proven against a recorder, never against the API. Two
  consequences, stated rather than implied. Re-posting an edge is measured on one endpoint only: a
  live probe re-posted an existing `dependencies/blocked_by` edge and got HTTP 422 with a message
  containing "already been taken", while `sub_issues` on a repeat is still unmeasured. So edge
  idempotence is carried by a per-edge receipt in `feature.yaml`, and SC-01's "the second run
  mutates nothing" rests on that ledger and not on any API property. The measured 422 lets the
  publish treat an already-drawn `blocked_by` edge as drawn rather than as a failure; the same
  narrowing is deliberately NOT applied to `sub_issues`, so a crash between a successful parent
  attachment and its receipt still wedges the re-run at exit 2 until the ledger is repaired by
  hand. And every edge this increment
  draws is within one repository, because it publishes one feature into one `--repo`; a cross-repo
  edge is plausible in shape and untested, so treat it as unknown rather than supported.

## Approval

status: approved
approved-by: Mike Ruangutai
date: 2026-08-09
