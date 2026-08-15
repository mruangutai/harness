# DESIGN — FEAT-10 Personal software factory, increment 1

## The prototype decision

**`prototype_required: false`.** This increment introduces no surface whose *rendering* the harness
controls. Enumerated, its entire output is: three single-select option names, three label strings,
an issue title and body, **one parent container issue and two kinds of edge between issues (C-5)**,
and terminal text — GitHub styles the board, the issue, the parent's sub-issue progress bar and the
child's blocked-by marker; the terminal styles the tools. #186's saved views, six-station field set and priority/kind/size fields are
deferred in BRIEF.md `## Deferred`, so there is no view layout to agree either. A high-fidelity
artifact here would contain nothing but the values this contract never chose and the operator has
now settled (Q1/Q2 below) — that is a form to fill in, not an experience to judge. **The C-5 edges
do not flip it:** the progress bar and the blocked-by marker are GitHub's own rendering, unstyleable
from here, so they add no surface the harness draws.

**What flips it, concretely:** (a) the harness gains a surface it renders itself — a status page, a
TUI, an HTML board view; (b) #186's saved views and field set land as something the harness
configures and the operator must judge *before* issues exist; (c) the user asks for one at the gate.

**Palette, type scale, spacing, light/dark are `n/a`** and deliberately so: inventing them for a
surface GitHub styles would be a contract nobody can implement or check. The contract below is
information design — semantics, naming rules, precedence, and output legibility.

## C-1 · Station semantics — what each key means, and what actually decides it

The fleet schema fixes the three *keys* (`T-01`'s verify asserts exactly `ready`, `building`,
`review`); only the display names are the operator's.

| Key | What it means | What decides it |
|---|---|---|
| `ready` | the item is queued for claiming: its board station field holds the `ready` option **and** its issue is open | the station field, written by `T-04` step 7 at publish. It is a queue position, never a guarantee that the item is claimable |
| `building` | an agent holds the claim on the issue | the existence of the ref `refs/heads/factory/issue-<n>` (D-05). The `factory:claimed` label and the assignee are the winner's bookkeeping, written after the fact, and decide nothing |
| `review` | an open pull request carries the work | `T-07` — it creates the pull request and then *writes* this station (step 5). **No tool ever evaluates this predicate.** C-1 is a vocabulary for reading the board, not a queryable state machine |

**How `ready` is selected, in three parts — two non-deciding, one that decides.** `factory_claim`
reads the board with a **server-side** query naming the fleet's `ready` option ANDed with `is:open`
(T-05 step 3, D-10), then applies a **non-mutating claimability pre-filter** per candidate — issue
open, no `factory:claimed`, no assignees (step 5a) — and then a **blocker gate**: a candidate whose
`depends_on` resolves to any blocker issue still open is skipped (C-2's amendment states the read
and its authority). **Neither the query nor the pre-filter is the claim.** The claim is the
`create_ref` in step 5b, and its return value is the only thing that confers ownership. The
pre-filter exists to spend a race on fewer candidates, not to decide one, and a candidate it skips
costs one iteration rather than blocking the queue.

**The blocker gate must not inherit that framing.** It is not the claim either, but unlike the
pre-filter it **decides what the factory takes**, not merely how fast it reaches it: a blocked
candidate is one the factory would otherwise have claimed. That is why it is ruled in C-2 as a
deliberate amendment to a decision rather than added here as one more cheap check.

**Naming rule for the display words** (the operator's answer must satisfy it): one word each, all
three distinguishable at a glance in the board's column header, each mapping 1:1 to one row above,
and none of them a verb the operator could read as an instruction to themselves. Two clauses are
load-bearing rather than stylistic. **One word:** the option name is interpolated into a board query
string and no tool quotes it, so a name containing a space silently matches nothing. **1:1 to a
row:** the station field is this factory's item lifecycle signal (D-10), so an option that maps to
no row leaves work in a state no tool can select. `T-01` is the only place the rule can bind,
because the words are chosen once at approval and never again.

## C-2 · Three layers of authority — the ref owns, the label reports, the station projects

`factory_claim` takes ownership with `create_ref`, and only afterwards writes the `factory:claimed`
label, the assignee, and the `building` station (T-05 step 6). Ordered by authority:

1. **The ref `refs/heads/factory/issue-<n>` is ownership.** Create-if-absent, decided by the server.
2. **The label and the assignee are operator-visible bookkeeping.** They report a claim that already
   happened. Two agents' assignee writes are additive and can never settle a race, which is why
   nothing reads them to decide one.
3. **The station field is a lossy projection.** Convenient for the operator, authoritative for
   nothing.

**Contract:** on divergence the higher layer wins — layer 1 beats layer 2 beats layer 3. A tool that finds a `ready` item whose issue is
already marked **skips it, reports the skip on stderr, and mutates nothing** — SC-14 and T-05
step 5a forbid the corrective write; SC-13 requires the skip. A candidate that clears that pre-filter
and is then refused by `create_ref` — the claim ref already exists — is skipped in poll mode (T-05
step 5b) and **that skip reports on stderr on every poll**, with a reason distinct from every other
skip reason in the loop, naming the issue and the fact that `refs/heads/factory/issue-<n>` already
exists. Poll mode only: under `--issue` the same refusal is a lost race at exit 3, not a skip.
Divergence is therefore *routine and
cheap*, not a fault: a winner interrupted between step 5b and step 6 holds the ref with no label,
and a bookkeeping failure in step 6 leaves the station still `ready` over a held claim. Both cost
one skipped candidate per poll, and recovery differs by case. A step 6 bookkeeping failure under a
*live* agent is repaired by re-running with `--issue <n>`, which the owning agent completes
idempotently. A winner that *dies* between 5b and 6 is not: it leaves an item that is open, station
`ready`, unlabelled and unassigned, so the item passes the claimability pre-filter forever while its
`create_ref` fails forever — and `--issue <n>` is unavailable here precisely because the owning
agent that would complete it no longer exists. The operator deleting the ref by hand is the only
remedy, and no tool reaps these, so **they accumulate without bound**.

The wedge is therefore structurally **downgraded, not structurally impossible**: work *behind* a
stuck item stays reachable, because the candidate loop skips and continues — that is the property
REQ-03 requires, and it holds — but a stuck item itself is permanent until an operator clears it,
and each one costs every agent one iteration on every poll from then on.

Reconciling a stale station field automatically is not in this increment; REQ-01 therefore carries a
named visibility gap — the board can under-report `building` — rather than a silent one.

### C-2 amendment · Blocker completion is a third permitted read — DEC-138 is the baseline amended

**DEC-138 makes the GitHub mirror strictly write-only, and D-01 bounds the factory's read-back to
learning a claim or a station.** That bound widens by exactly one item: `factory_claim` may also read
**blocker completion**, and it MUST NOT claim an issue whose blockers are unfinished. This is a
ruling, recorded here so a later reader sees a deliberate amendment and not drift.

- **What is read, and from where.** The DAG authority stays `plan.yaml`'s `depends_on` — the signed
  artifact, unchanged. Resolution runs `plan.yaml` `depends_on` → `feature.yaml`'s issue map → that
  blocker issue's open/closed state. GitHub contributes the last hop only: *is the blocker closed*.
- **What is never read.** The rendered `blocked_by` edge. It is hand-editable on GitHub, so deriving
  control flow from it would put a remote object in charge of the DAG and reopen D-01 from the other
  side — layer 3 beating layer 1, the exact inversion the ladder above forbids.
- **Where it sits in the ladder: nowhere, and that is why it needed a ruling.** Blocker completion is
  not ownership (layer 1), not bookkeeping (layer 2) and not a station (layer 3). It is a **gate on
  candidacy**, applied before the ladder is engaged at all. A blocked candidate is **skipped, mutates
  nothing, and reports the skip on stderr** — the same shape as every other skip in C-2, and under
  C-3's failure grammar it carries a reason **distinct from every other skip reason**, because
  "blocked by an open blocker" and "somebody already holds this" are different facts about the board.
- **The cost, stated honestly.** Enforcement adds one blocker-state read **per blocker** per
  candidate, not one per candidate — the plan's cache holds the YAML *files*, not `issue_view`
  results, so T-12's six blockers cost six reads. It is bounded by the ready column — D-10's
  server-side filter already bounds that set (measured on board 3: the ready-station query returned
  1 item).
- **Two edges of the gate, both ruled here so an implementer does not settle them silently.**
  (i) A `depends_on` entry that the issue map cannot resolve — C-5's dangling entry, which reaches
  T-04 from a *signed* plan and is permanent — counts as **blocked, not clear**, reported on stderr
  on every poll. Handing work out on an unresolvable blocker is the failure this ruling exists to
  stop, and D-02's fail-loudly control plane points the same way. (ii) A candidate the factory cannot
  resolve to a plan task at all — C-4's tolerant `feature: null` read, an issue from the `gh-sync.py`
  mirror — has no `depends_on` to resolve and is **not gated**. It stays claimable exactly as before,
  and making it an error would silently reverse C-4.
- **(iii) The gate is a POLL-MODE CANDIDACY gate, and `--issue` self-ownership is never gated.**
  Re-entry under `--issue <n>` on an issue this agent already owns is the only documented repair for
  a step-6 bookkeeping failure (above, and C-3's point-of-no-return row); it repairs a claim that
  already exists, so gating it would delete that repair and leave the ref to accumulate under D-13.
  The blocker check therefore sits with the poll-mode skips and after the self-ownership branch,
  never before it. A *fresh* `--issue` claim naming a blocked issue **is** refused, and its signal
  must stay distinguishable from exit 3, which is reserved for a race the agent actually entered;
  which exit that refusal carries is C-3 vocabulary and is left to the plan (Q9).
- **The under-reported block is a named visibility gap, not a silent one.** C-5 skips an edge whose
  blocker has no recorded issue, so a task blocked by a dangling `depends_on` entry is permanently
  unclaimable **with no block marker rendered on its card** — the board under-reports the block, the
  same family as C-2's `building` under-report above. That is why edge (i)'s skip is reported on
  **every** poll rather than once. Refusing at exit 2 instead was rejected: one bad entry would wedge
  the whole queue, which is exactly what REQ-03 forbids.
- **What it buys.** The board's block marker and the factory's behaviour now agree. On day one the
  five tasks with `depends_on: []` — **T-01, T-03, T-09, T-10, T-11** — are claimable, and T-12,
  which declares six blockers, is skipped until all six close.

## C-3 · CLI legibility — stream split, exit vocabulary, item lifecycle, failure grammar

**stdout carries the machine-readable payload only; every diagnostic, warning and error goes to
stderr.** The whole of stdout on a successful run must parse in one `json.loads`.

**The exit table binds the five tools with a command line** — `factory_config`, `factory_decompose`,
`factory_claim`, `factory_workspace`, `factory_land`. `factory_cli` and `factory_gh` are libraries
with no command-line entry and no exit statuses of their own (D-07, D-08).

| Exit | Meaning |
|---|---|
| 0 | success; the payload is the sole content of stdout |
| 1 | nothing to do. Not an error. In `factory_claim` it has two causes with two distinct stderr lines: `no work available` (the ready column held no candidate in the fleet) and `no claimable work` (every candidate was skipped or its create refused) |
| 2 | refused: config invalid, repository not in the fleet, plan unsigned, a station option the board does not offer, a guard tripped, or any unexpected exception. Zero mutating calls before the tool's point of no return, below |
| 3 | lost race: the `create_ref` was refused because another agent holds the claim. **`factory_claim` only, and only under `--issue`.** In poll mode a refused create skips to the next candidate, so the run ends 0 or 1 and never 3 |

**A tool never exits 1 for a failure.** An unhandled `GhError` or `FleetError` would exit 1 by
Python's default and read as "nothing to do" — the worst confusion in this table — so every entry
point traps unexpected exceptions and exits 2 (D-08).

**Point of no return, per tool.** Exit 2 cannot promise one invariant across all of them; each
states its own, and SC-14 asserts zero mutating calls over the full recorded call list on every
refusal path reached before it.

| Tool | Point of no return | What exit 2 can leave | Recovery |
|---|---|---|---|
| `factory_cli` | none — mutates nothing, ever | nothing | n/a |
| `factory_config` | none — mutates nothing, ever | nothing | n/a |
| `factory_gh` | none of its own; each function is one call, so the point of no return is its caller's to state | n/a | n/a |
| `factory_decompose` | the `ensure_labels` call in step 5 — still the first remote write, because the C-5 parent carries `harness` and `feature:<FEAT>` and so cannot be created before the ensure | labels ensured in the target repository; after the parent is created, **a parent with no children**; and after the first successful `create_issue`, a partially published feature with some edges undrawn | re-run, with one residual. Labels are idempotent by `--force`; every receipt — parent number, issue number, item id, edge — is written immediately and **atomically** (T-04 step 8, temp file plus `os.replace`), so no issue or board item is duplicated and the ledger is never observed half-written. Dependency edges also survive: 7b catches `GhError` **on the `blocked_by` call only**, and **only** when it carries both a 422 and "already been taken", recording that edge as already-drawn. **Hierarchy is the residual:** `sub_issues` is unprobed, the attach stays fatal in every case, and `edges.parent` is a per-edge receipt — so a death between a successful attach and its receipt **wedges the re-run at exit 2**, recoverable only by hand-editing `feature.yaml` |
| `factory_claim` | the `create_ref` that returns `True` | the claim held with the station possibly still `ready` | re-run with `--issue <n>`, or release the ref |
| `factory_workspace` | the clone in step 3 — or, on an existing checkout, the fetch-and-reset that step 3 does instead. It mutates nothing on GitHub ever; every mutation is local and disposable under `workspace_root` | a checkout not on the issue branch | re-run |
| `factory_land` | the successful push in step 3 | a branch pushed with no pull request, or a pull request with the station unmoved | re-run; every step from 3 on is idempotent |

The whole of `factory_claim`'s candidate scan — **including every refused `create_ref`** — precedes
its point of no return, so a losing agent is indistinguishable from an idle one in its effect on the
world, and exit 3 keeps the no-mutation guarantee intact.

**Board item lifecycle.** Board items are **never archived or removed by any factory tool**, and a
closed issue stays on the board as an item (re-measured 2026-08-08: #182, #183 and #197 are closed and
all still present on board 3, which holds 150 items). The item payload carries **no `state` key**, so
closed work cannot be filtered client-side at all. The board therefore grows monotonically, and
reaping stays the operator's through the board UI (D-10; effort #186 owns automating it). What makes
the read correct at any board size is that it is bounded by the **ready column** rather than by the
board: a server-side query on the station option ANDed with `is:open` (measured on board 3: no query
150, `is:open` 70, `status:Ready` 1), with `project_items` raising when `totalCount` exceeds the
items returned rather than silently truncating. That bound holds against the board's monotonic
growth but does not exclude C-2's residual: a stale-ref item is open and is in the ready column, so
it sits *inside* the bounded set by construction, and effort #186's saved views reap board items,
not refs. One consequence must be guarded explicitly: a station option name the board does not offer
returns **zero items and exit 0**, indistinguishable
from an empty queue forever — so the three option names are validated against the board's field
before the first poll and a mismatch exits 2 naming the option, the field and the fleet file.

**That guard is armed on day one, and the operator has stated the pre-condition that disarms it.**
Board 3's `Status` options, as measured by the operator on 2026-08-08, are `Backlog`, `Ready`,
`In progress`, `In review`, `Done`. Of the three station words settled in Q1, only **`Ready` exists
today**; **`Building` and `Review` do not.** The operator will rename the column `In progress` →
`Building` and `In review` → `Review`; `Backlog` and `Done` are untouched and stay
operator-managed, outside the factory's three stations. Until that rename happens, **`factory_claim`
exits 2 on its very first run** — correctly and loudly, naming the missing option — and the
increment cannot function, because the rename is a manual board edit no tool in this increment
performs. Scope it precisely, because it does not bite both tools: `factory_decompose` writes only
the `ready` option (T-04 step 7), and `Ready` exists, so decompose is unaffected. This is a stated
operator pre-condition, not a defensive maybe: the guard is expected to fire, once, and its firing
is the instruction to go rename two columns.

**Failure grammar.** `stderr` is **human-facing only**. A machine caller reads the exit status and
the single JSON document on stdout, and never parses a stderr line — which is what makes several
shapes on that stream legitimate rather than a contradiction. The default shape is one line:
`factory: <tool>: <what failed>: <the concrete value> — <what the operator does next>`, built in one
place (`factory_cli.message`, D-08) so it cannot drift. SC-10's "loud message" is checkable against
it. Every message names a value the operator can act on — the path, the repo, the issue number, the
option name — never a bare exception class, with **one carved-out exception**: the trap's
`unexpected failure: <type name>` line, where by definition there is no operator-actionable value to
name. `FACTORY_DEBUG=1` adds the traceback there. The `nothing_to_do` line is a deliberate three-part
form: there is no failed value and no operator action.

## C-4 · Telling one unit of work from another at a glance

The board is cross-repo and cross-feature. GitHub's card shows the repository, so repo
disambiguation is free. **Nothing shows the feature**, and `T-NN` is per-feature — two features both
ship a `T-01`, and the board would then carry two indistinguishable cards.

**Ruled by D-09:** every factory-created issue carries a `feature:<FEAT>` label alongside `harness`,
and `factory_claim`'s payload carries the same value in its `feature` key. The operator reads (repo
on the card) + (`feature:` label) + (`T-NN` in the title) as the unit's full address, and an agent
gets it without a second call. A factory issue carrying no `feature:` label is still claimable with
`feature: null` — issues from the existing `gh-sync.py` mirror carry `harness` and nothing else, and
a tolerant read keeps them on the same board.

**Issue body, fixed order — for a TASK issue** (T-04 step 6, arranged for a human reading it on
GitHub). This is the claim that had to narrow: it enumerates `change_type` and `traces`, and the C-5
parent has neither, so "the issue body has exactly four parts" cannot hold for every factory issue
and is now scoped to task issues, with the parent's own two-part body stated in C-5. The task's
`intent` verbatim first, because it is what the reader came for; then a blank line; then one line
`change_type: <value>`; then one line `traces: REQ-01, REQ-07` — comma-separated on a single line,
never a YAML list dumped into prose. No other content, so the body diffs cleanly when a task is
republished.

**Label vocabulary, complete — and it is two sets, not one** (T-04 step 5). **This claim stands
unchanged**, re-checked against C-5: the parent issue introduces no sixth label, because it carries
`harness` and `feature:<FEAT>` and nothing else. What gained a per-issue-kind split is the *applied*
rule, not the vocabulary. The **ensured** set, created in the target repository before any issue is:
`harness`, `feature:<FEAT>`, `chore`, `bug`, `factory:claimed`. The **applied** set, per issue at
creation: for a **task** issue, `harness` always, `feature:<FEAT>` always, plus `chore` or `bug`
derived mechanically from `change_type`; for the **parent**, `harness` and `feature:<FEAT>` only —
there is no `change_type` to derive from. `factory:claimed` is ensured
but never applied by `factory_decompose` — `factory_claim` applies it, and it has no create-issue
call to piggyback on. No other label is written by a factory tool. All five share one colour by
design: colour therefore carries zero information and every label is read by its text, which is
a11y-safe as built; a later increment must not "improve" this into colour-coding.

## C-5 · The DAG on the board — one container, many blockers, and an edge nothing reads back

C-4 gives a unit of work an *address*. It says nothing about how units *relate*, and the operator has
ruled (Q7) that the decomposition must encode the task DAG: flat issues are rejected. Two edge types,
and the tree already keeps them apart — `gh_issues.py` builds `attach_sub_issue_args` (hierarchy) and
`blocked_by_args` (dependency) against different endpoints, and `wayfind.py` attaches a ticket to a
*map* container with `sub_issues` while its `block` subcommand does dependencies.

**`depends_on` maps to `blocked_by`. The parent is a feature-level container, never a dependency.**
The disqualifier is checkable, not aesthetic: GitHub allows an issue exactly ONE parent, and
`plan.yaml`'s T-12 declares `depends_on: [T-02, T-04, T-05, T-06, T-07, T-11]` — six blockers, which
a parent-per-dependency cannot represent at all. So each task issue is a **sub-issue of one parent**
and carries **one `blocked_by` edge per entry in its `depends_on`**, pointing at that task's issue in
the same publish. Every task in the plan is published, including the main-session-direct ones (T-04
step 4 sorts *every* task; verified — T-01 and T-08 are `main-session-direct` and are not excluded),
so a blocker always has an issue to point at once the publish completes. The rule is: an edge whose
blocker has no recorded issue number is **skipped and reported on stderr, never an error**. The case it
actually covers is not a mid-publish one — 7b runs only after the create loop completes, so every
in-plan task already has an issue by then. It is a **`depends_on` entry naming a task the plan does
not contain**, which is how the plan's own test case builds it (`plan.yaml:894-899`). Nothing in the
harness validates `depends_on` referential integrity, so a dangling entry reaches T-04 from a
*signed* plan — and for that entry the skip is **permanent**, since no run will ever create the
issue it names. That is why T-04's step-8 payload carries `edges_skipped` beside `edges_drawn`
rather than leaving the skip on stderr alone.

**The parent is adopt-or-create, and its origin is recorded.** This is `gh-sync.py cmd_open`'s shape
reused rather than a new one: `--parent <n>` adopts an existing issue, its absence creates one, and
`feature.yaml`'s `factory` block records `parent` and `parent_origin: adopted | created` immediately,
by the same record-after-every-create rule the issue map already follows. Reuse is not tidiness here,
it is the only reading that survives D-12: `mruangutai/harness` is both a candidate fleet member and
`harness.json`'s `github.repo`, so a parent for this feature may already exist there and a factory
that creates its own would put a second container beside it. **The factory never discovers a parent**
— adoption is the operator naming a number, which is D-01's rule that GitHub state is read to learn a
claim or a station and never to decide an approval-gated artifact. (Concretely today: this feature's
`feature.yaml` carries no `github` block, so gh-sync has published no parent; the natural adoption
candidate is the effort issue #181, which is OPEN and is a `wayfinder:map` container with ten closed
decision sub-issues. Adopting it would put task issues beside decision tickets under one map. That is
the operator's call at the command line, not the tool's.)

**An adopted parent is not factory-created, and the asymmetry is stated so it is not decided
mid-build:** the factory applies `feature:<FEAT>` to the parent either way — D-09 says every issue the
factory puts on this address carries it, the write is additive and idempotent, and it is the label
REQ-01's reader actually looks for — but it **never rewrites an adopted parent's title or body**. A
*created* parent's body is two parts, following `cmd_open`'s precedent: the feature's problem
statement, a blank line, then one line `**Goal:** <goal>`. No `T-NN`, no `change_type`, no `traces` —
those describe a task and the parent is not one, which is why C-4's fixed-order rule narrowed rather
than stretched.

**The parent is never added to the board.** T-04 step 7 adds a board item and sets the `ready`
station for "every issue that has no recorded item id", and a newly created parent would qualify — it
would then sit open in the Ready column carrying `feature:<FEAT>`, and `factory_claim` would claim the
container. Keeping the parent off the board forecloses that with no new check anywhere, because
`factory_claim`'s read is bounded by the board (D-10): an issue that is not an item is invisible to
it. The cost is honest and small — the parent's progress bar is read on the issue page rather than on
a card.

**Authority: this is C-2's ladder extended, and it is what stops Q7 reopening D-01.** `plan.yaml`'s
`depends_on` is the truth. The `blocked_by` and parent edges on GitHub are a **projection** of it,
one layer below even the station field, because they are derived from a signed artifact and nothing
derives from them. **No factory tool ever reads an edge back to decide anything**, so a divergent
edge is a reporting defect, never a state change and never a wedge.

**That sentence now does harder work, and it survives intact.** Since C-2's amendment, the factory
*does* gate claiming on blockers — but what it reads is the **blocker issue's open/closed state**,
resolved `plan.yaml` → `feature.yaml` → issue, and never the rendered edge. The two are easy to
conflate and must not be: the edge is read-back-**never**; blocker completion is a third permitted
read, ruled in C-2. The consequence below is the proof rather than a restatement — an edge
hand-*added* on GitHub blocks nothing and an edge hand-*deleted* unblocks nothing, because neither
one is on the resolution path. **The repair differs by
direction, and only one direction is a re-run.** An **under-recorded** ledger — an edge left undrawn
by an interrupted publish — is repaired by re-running the publish, which draws exactly the edges the
ledger does not record. (An edge *drawn* but not recorded is a different case, and it is C-3's
`factory_decompose` row that states it, not this one.) An **over-recorded** one — an edge deleted by
hand on GitHub — is not: the ledger says drawn, so the re-run does nothing at all, and the repair is
hand-editing `feature.yaml`.
An edge hand-*added* on GitHub is in no ledger and in no plan, so no tool draws it, removes it or
notices it.

**What the operator actually gets, and what they do not.** GitHub renders sub-issue progress on the
parent and a blocked-by marker on the child, and that is real REQ-01 value: one issue page shows the
whole feature and its completion count without opening the board, and a card's blocker is visible
without opening `plan.yaml`. **And the marker is honest: ordering is enforced.** T-04 still publishes
*every* task at `ready`, so on day one all twelve sit in the Ready column — but `factory_claim`'s
blocker gate (C-2's amendment) takes only the five with no blockers, **T-01, T-03, T-09, T-10,
T-11**, and skips T-12 until all six of its blockers close. An operator who reads the board and
believes ordering holds is reading it correctly.

Two things the rendering still does **not** buy, said plainly because it implies both and delivers
neither:

1. **Sub-issue progress is not station progress.** The bar counts open versus closed, so a task in
   `review` with an open pull request still reads incomplete. Two notions of done coexist on one
   board and neither is wrong; they answer different questions.
2. **Cross-repo dependency is unexercised.** This increment publishes one feature into one `--repo`,
   so every edge it draws is within one repository. The blocker is addressed by internal id, so a
   cross-repository edge is plausible in shape and is **untested here** — treat it as unknown rather
   than supported.

## Squad convention

The Product squad's `astryx-design-system` convention is **INAPPLICABLE**, agreeing with pm, on
substrate grounds rather than "no UI": the convention binds work that implements rendered
components, and this increment's only rendered surfaces are GitHub's own — unstyleable from here —
and terminal text, which has no component model. A later increment that adds a harness-rendered
view of board state makes it fire; that is the same trigger as prototype flip condition (a).

## Open questions

- **Q1 — RESOLVED by the operator.** The station display names are `ready: Ready`,
  `building: Building`, `review: Review`. **They satisfy C-1's naming rule, and this is the only
  place that judgement is made** — nothing machine-checks the rule itself (Q-G stays a human check
  at signature, and no gate is claimed for it here). Checked clause by clause: each is **one word**,
  so it interpolates into an unquoted board query and matches; each maps **1:1** to exactly one C-1
  row — `Ready` to the queue position, `Building` to a held claim, `Review` to an open pull request —
  leaving no option that maps to nothing; and all three are **distinguishable at a glance** in a
  column header. On the no-verb clause: `Ready` is an adjective and `Building` a participle, both
  plainly states. `Review` is the noun naming C-1's `review` row — the thing an open pull request
  *is* — but in a column header it can be read as an imperative addressed to the operator. That is
  the one residual, accepted: the words are ruled, the reading is a nuisance and not a mechanism.
- **Q2 — RESOLVED by the operator.** Board owner `mruangutai`, board number **3** ("Harness"),
  station single-select field `Status`. C-3's day-one pre-condition above records what that board's
  options are today and which two must be renamed; nothing in this contract waits on it.
- **Q3 — RESOLVED by D-09.** The `feature:<FEAT>` label is ruled in and T-04 implements it; C-4
  above states the settled position, and nothing here waits on it.
- **Q4 (non-blocking, pm):** C-5 requires a seam that `plan.yaml` does not yet describe. **T-03's
  `factory_gh.py` function list has no `internal_id`, no `attach_sub_issue` and no `blocked_by`** —
  and both edge endpoints take an issue's internal `id`, never its number, which is the trap
  `gh_issues.py` documents at its head. Whether the factory imports `gh_issues.py`'s argv builders or
  restates them behind `factory_gh` is an engineering call, not a design one; C-5 only requires that
  the two edge types stay distinct functions.
- **Q5 (non-blocking, pm):** four things C-5 needs from **T-04** that its intent does not yet say.
  (i) A `--parent <n>` adopt-or-create step on `cmd_open`'s shape, run after `ensure_labels` and
  before the first task create. (ii) **A second pass for edges, after every issue exists** — a
  `blocked_by` edge needs both endpoints, so it cannot ride the create loop, and relying on task
  ordering would be a silent dependency on the plan's task order. (iii) The `feature.yaml` `factory`
  block widens to carry `parent`, `parent_origin` and a **per-edge receipt** — `gh-sync.py` records
  `attached` per task precisely because re-attaching is not assumed idempotent, and the same reason
  applies to both edge types here. (iv) **T-04 step 7's current wording — board-add "every issue that
  has no recorded item id" — is the exact line that would put the parent on the board** and make it
  claimable; it needs the parent excluded in text. Test cases follow from each: the parent's two-part
  body and its two labels, an adopted parent's title and body left byte-identical, the parent absent
  from the board-add recorder, one `blocked_by` call per `depends_on` entry with T-12's six asserted,
  and a re-run drawing zero duplicate edges.
- **Q6 (non-blocking, harness owner):** a harness defect, not a design question. My dispatch
  instructed me to write a receipt under this feature's `notes/`, and `check-domain.sh` blocked it —
  `harness-visual-designer`'s permitted set is `DESIGN.md`, `notes/mockups/**`,
  `notes/prototypes/**`, the expertise file and the observations log, with no receipt path.
  `harness-handoff`'s default receipt rule and this role's domain in `team-config.yaml` disagree. I
  did not work around the hook; this file is the artifact.
- **Q9 (non-blocking, pm)** — numbered from 9 so it cannot be confused with the plan review's Q7/Q8,
  which this file cites. **C-2's amendment requires a seam T-05 does not describe.** T-05's intent
  enumerates the step 5a pre-filter as three checks and never reads `feature.yaml`'s issue map, so
  the resolution path `depends_on` → issue map → issue state has no home in the plan. What T-05
  needs, in the register of Q4/Q5: the plan and the issue map as inputs to `factory_claim`; the
  blocker check placed after 5a and before 5b's `create_ref`, so a blocked candidate costs no race;
  a distinct stderr reason; and test cases for the three outcomes — blocker open (skip), all blockers
  closed (claim), blocker unresolvable (skip, per C-2's edge (i)) — plus the `feature: null` case
  claiming ungated.
- **Q10 (non-blocking, operator)** — **enforcement dilutes D-13's protected signal, and D-13's
  acceptance was conditional on it.** D-13 accepts two growths on the condition that SC-13 clause (b)
  lands, because `no claimable work` is "the operator's only signal that the residual is biting."
  Once the five roots move to `building`, the ready column holds only blocked items, so a poll skips
  every candidate and exits 1 on that same line **in healthy operation**. C-2's distinct stderr
  reason for the refused-claim-marker skip — the one route D-13's residual takes through the loop —
  preserves the discrimination without touching SC-13's protected wording, and that
  is the recommendation here — but the operator accepted D-13 under the old meaning of the line and
  should see that it changed.
