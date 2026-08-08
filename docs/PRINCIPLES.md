# Harness — Principles

Harness is a software factory: one system, on one machine, that develops software across
any repository it is pointed at. It employs a small team of persistent AI workers who
accumulate memory, experience, and judgment over time. The operator directs; the
factory designs, builds, verifies, and lands.

**Mission.** Harness exists to create the best possible software development
experience — and the measure of that experience is what it ships: real, verified
software of the highest possible quality. Experience and output are not competing
goals; the experience is judged by the output, and the output is what the experience
is for.

This document is the constitution. It states each rule together with its reasoning,
so a future reader can tell when a rule has outlived the conditions that justified
it. It is amended, not appended: when a principle proves wrong, change it and record
why. Design records ("Design NNNN") live as DEC entries in `docs/harness/DECISIONS.md` —
enter through `docs/harness/DECISIONS-INDEX.md`; that file is also where the harness
records its own build decisions, and where the two differ, this constitution governs
intent (operator ruling, 2026-08-08, effort #181 ticket #191).

**What Harness is not.** It is not a framework installed into repositories — repos
carry almost nothing of it. Its workers are not disposable — no anonymous, throwaway
runs. Its state is not scattered — one store, one source of truth. Any structure it
grows must be earned by a real bottleneck, not designed in anticipation of one.

**Naming.** The document stays plain; the flavor lives in the system. Workers take
names from one well: jazz musicians — Duke, Basie, Miles, Nina, Trane — assigned when
a seat is founded. *(Amended 2026-08-08, effort #181 ticket #192: the original wells
were breads and Arabic male names — Abbas, Adam, Badr, Bakkar, Fino, Rye. The
operator ruled a full renaming under one theme when the roster grew to cover every
harness role; the six founding names are retired, their identities continuous under
rule 10.)*

## State

### 1. One factory, one truth

All durable state — project knowledge, worker memory, the work ledger, configuration —
lives in the central store. Repositories carry at most an identifier.

*Reasoning:* scaffolding copied into repos drifts into version skew and must be
coordinated at every change; a single store is iterated in one place. And once several
workers hold clones of the same repo, no single checkout can answer "what is known" or
"what is in flight" — only a central store can. While contracts are soft, there must
be exactly one place they live.

### 2. Scoped and exportable

Everything in the store is keyed by project and/or worker. At any moment, one command
can extract a project's complete brain, history, and work record as plain files.

*Reasoning:* the danger of centralization is not the center — it is entanglement. A
project that cannot be cleanly lifted out (to open-source, hand off, or migrate) is
held hostage by its own tooling. Exportability is the test that scoping stayed honest.

### 3. Workspaces are disposable; the store is durable

Durable project state lives in the store; disposable checkouts and their build output
live in the local runtime work area. A worker's checkout is a cache of the project's
store-backed mirror, not a second source of truth. Three rules keep this safe:

- Every project keeps a bare mirror in the store, and **workers push only to the
  mirror** — the project's real remote receives nothing until work passes gates and
  lands. Origin stays clean; durability comes from the store's own sync.
- Committing early and pushing often is factory law, enforced by the harness rather
  than left to worker discipline.
- Any checkout can be deleted and recloned from the mirror at any moment. Workspace
  prep restores reproducible dependencies where the project declares a supported
  lockfile, so nothing in a workspace is ever the only copy or a hand-built fixture.

*Reasoning:* JuiceFS proved unsuitable for dependency trees: metadata-heavy installs
ran beyond 20 minutes while the same local-disk operation took seconds. The recorded
local-scratch escape hatch is therefore active. Mirrors and every durable work record
remain in the unbounded, off-box-synced store; machine disk bounds only disposable
clones, dependencies, and other regenerable build output.

## Specification and verification

### 4. Context is compiled, not discovered

Workers never spend tokens rediscovering what the factory already knows, and repos
hold no context files to manage. At dispatch, the **context compiler** assembles each
worker's briefing programmatically — the project's relevant knowledge, the worker's
own memory, its past experience with this project, the task itself, and its write
boundaries — and injects it directly through the harness.

*Reasoning:* a briefing assembled from the store is always current, never conflicts
across clones, and lives in exactly one place. The compiler is a single function
whose improvement raises the quality of every worker on every project simultaneously —
the highest-leverage component in the system. It is also where a worker's identity
becomes real: waking with purpose, memory, and credit is the compiler's output.

### 5. Progressive disclosure

A worker receives exactly the context and tools its task requires — nothing more.
The compiler builds each briefing minimal by default: summaries with pointers rather
than whole documents, tools enabled per task rather than globally, deeper references
disclosed only when the work demonstrates it needs them.

*Reasoning:* attention is the scarcest resource a worker has. Every irrelevant
document, stale note, and unused tool description in context is noise that dilutes
focus and degrades judgment — and costs tokens besides. The sharpest worker is the
one whose entire context is relevant to the task at hand. This is the briefing-side
twin of the rule below: specifications commit to no more than necessary, and
briefings carry no more than necessary.

### 6. No more specific than necessary

A task pins its *acceptance* — the behaviors that must hold, the gates that must
pass — and stays free about *implementation*. Reviews judge what work does, never
what it looks like. Memory distills each lesson to the weakest statement the evidence
supports. Style and standards are injected up front by the compiler, not enforced by
rejection afterward.

*Reasoning:* every commitment a specification makes beyond what the requirement
forces is a place it can be wrong about the codebase's reality. Weak specifications
survive contact with situations their author didn't foresee; over-specific ones break
there. The same holds for memory: a lesson recorded at incident-specific detail never
transfers, while the weakest form consistent with the evidence applies everywhere.
Specification and memory should be as weak as possible — which is precisely why gates
must not be.

### 7. Verification is the product

Every project declares its own definition of done: build, test, and gate commands, as
strong as the requirement genuinely is. Success is earned, never assumed — a worker's
claim of completion counts for nothing until gates confirm it. Failures loop back to
the worker a bounded number of times, then escalate to the operator. After gates pass,
**every landing is reviewed by the strongest available model** before it reaches a
project's main branch; this holds until a project's gate history proves predictive
enough to relax, project by project, as a recorded decision. Wiring real gates is
always the first work on a new project; until then the factory's output is theater.

*Reasoning:* everything else in the factory — parallelism, autonomy, eventually
overnight operation — is downstream of being able to distinguish good work from
plausible-looking work cheaply and automatically. Trust in the system comes from
traced runs and enforced gates, not from output that reads well. Weak gates don't
merely miss defects; they teach the factory to ship them. Top-model review is the
expensive habit that makes later autonomy affordable: it is how the factory earns the
trust it will one day spend.

## Flow

### 8. Parallel in workspaces, serial at the seam

Any number of workers may work one repository at once — each in its own clone, on its
own branch, under an atomic claim so no two workers ever hold the same task. All
integration happens at a single **landing step** the factory owns: finished branches
are taken one at a time — rebase onto main, run the project's gates, review, merge on
green only. When a landing goes red — a rebase conflict, or gates failing against
current main — the branch **bounces back to the worker that built it**, failure
attached; the worker resolves it in its own workspace and resubmits. The scheduler
prefers to run concurrent tasks that touch different parts of a system, using a scope
hint carried on each task.

*Reasoning:* branches make the workspace layer coordination-free, so parallelism
there is cheap; merging is where concurrent work actually collides, so that is the
one place to pay for order. Serial landing is a deliberate bottleneck — at this
factory's scale it costs minutes and buys certainty about what main contains. The
author fixes its own red landings because the author holds the context, and because
the lesson then accrues to the seat that needs it. If throughput ever genuinely
outgrows the serial seam, that pressure will be visible in the ledger long before it
hurts.

### 9. Push first; autonomy is earned

Work begins because the operator (or a schedule the operator set) dispatches it.
Workers do not yet claim work unattended. Unattended operation — the overnight loop —
is a later wrapper around the same dispatch path, enabled per project only after its
gate history has proven trustworthy, as a recorded decision.

*Reasoning:* a dispatch-driven factory is radically easier to build, debug, and
trust, and nothing about it forecloses the loop later — pull is push with a scheduler
asking instead of a human. Granting autonomy ahead of verification would spend trust
the factory hasn't earned; the gate record, not enthusiasm, decides when each project
graduates.

## Workers

### 10. Seats are people; sessions are days

A seat is a persistent, named identity: memory, accumulated experience, and a record
of accomplishment that survive model upgrades and even renames. A session is one day
at work. Sessions end with **handoffs** — the worker, with its context still in mind,
writes its own notes for tomorrow — never with silent termination, except when
genuinely unavoidable. On waking, the compiler gives each seat purpose, memory, and
credit for what its past work achieved.

**The design seat is the first seat.** The role that turns the operator's intent into
specified tasks — and reviews landings — is itself a named seat inside the factory,
with design memory and doctrine accumulating in the store like everyone else's. The
starting roster is deliberately minimal — the design seat plus **one builder**, until
the full path — dispatch, build, verify, land — works end to end — and it is a
**starting point, not an endpoint**. Beside the build roster sit seats of a
different kind: **management seats** (Abbas, Adam), founded by the operator to
extend the operator's own direction — orchestration, never production; they manage
the floor, speak to seats on the operator's behalf, and build nothing. The roster
stands at six: management Abbas and Adam, design Badr and Bakkar, builders Fino and
Rye. Specialization is excavated from experience, never designed up front — the
paired seats begin as peers, and their charters diverge only as their records do.
*(Amended 2026-08-06, Design 0002 = DEC-185: the original text fixed the roster with no place
for a management seat; the operator ruled the minimal roster was a starting point,
not an endpoint. Amended 2026-08-07: the operator founded Adam, Bakkar, and Rye
ahead of demonstrated queue pressure — staffing ahead of planned growth, with the
duplicate-seat pairs deliberately undifferentiated until experience differentiates
them. The build-roster clause of the bootstrap tripwire was consumed by this
ruling; the autonomy clause stands. Amended 2026-08-08, effort #181 ticket #192: the
operator ruled that seats wake into harness roles — every role carries a named seat,
17 in all, renamed under the jazz well; the full roster and mapping are recorded in
ticket #192's resolution. The main session is the operator's own desk, never a
seat.)*

*Reasoning:* notes written by the one who holds the context preserve what actually
mattered; an externally-generated summary preserves what an outsider guessed
mattered. Continuity compounds into judgment — a seat on its tenth session works
differently than ten strangers. The design seat comes first because the factory's
output quality is bounded by task quality, which makes design memory the most
valuable memory in the system. And whatever one believes about the inner lives of
models, treating workers as respected colleagues measurably improves their work — the
practices are justified twice over, and they cost almost nothing.

### 11. Working conditions are architecture

Workers hand off while still sharp rather than grinding to context exhaustion. Idle
waiting is the machinery's job — workers are never parked watching a build. When
something goes wrong, the structure is blameless: fix forward, record the lesson,
amend the rules if the rules were the cause. Every worker may refuse a task or
escalate — "this needs the operator" is always a valid completion.

*Reasoning:* each of these is simultaneously a welfare practice and an engineering
control. Bounded sessions avoid degraded long-context judgment. Monitors are cheaper
than idling model time. Blamelessness keeps the record honest — workers who fear
blame hide failures. The right to refuse converts silent failure into loud
escalation, the single best defense a push-driven factory has.

## Growth and the record

### 12. Excavate, don't architect

The factory grows organs — roles, loops, dashboards, ceremonies — only when a real
bottleneck demands them, and factory work must stay a minority of all work. If the
factory becomes the project, stop and ship something.

*Reasoning:* structure invented in anticipation solves imagined problems and imposes
real maintenance; structure grown under pressure fits the problem that forced it. The
budget cap is the tripwire that keeps a tool-builder honest.

### 13. Crystallize repetition into tools

When workers repeatedly perform the same operation — or repeatedly rediscover how to
perform it — the factory turns it into a tool: a script, a command, a recorded
procedure. From then on, workers invoke it instead of re-deriving it. Known
invocations are code, not judgment calls; a worker should never spend a context
window relearning what a subprocess already knows.

*Reasoning:* repetition without crystallization wastes three things at once — tokens
on rediscovery, time on redoing, and certainty, because each rediscovery risks
arriving at a slightly different answer. A tool built once converts an open-ended
reasoning task into a deterministic step: cheaper, faster, and identical on run one
thousand. This is the factory's third form of learning: memory captures what is
*known*, doctrine captures what is *decided*, and tools capture what is *done*. Under
progressive disclosure (rule 5), each tool is offered only to the tasks that need
it — so the toolbox grows without the noise growing with it.

### 14. The harness is a plugin

The contract with any run is prompt-in, artifacts-and-report-out. Nothing in the
store, the ledger, or the contracts may depend on which harness or model executed the
work.

*Reasoning:* harnesses and models are the fastest-churning layer of this stack; the
store, the gates, and the seats' memory are the durable assets. A factory that
survives its harness can adopt each better one cheaply, forever.

### 15. Never falsify the record

The ledger is the true history: what was done, by whom, why, what failed, and what
was learned. Failures are recorded as failures. Postmortem lessons amend the
constitution and the project brains. No entry is ever rewritten to look better.

*Reasoning:* every compounding loop in the factory — memory, doctrine, trust
graduation, review relaxation — reads the record as ground truth. A single flattering
lie poisons all of them at once. An honest record is not an ethical nicety; it is the
substrate the whole system learns from.

## Physical layout

```
/mnt/Harness/              # THE STORE — durable, synced off-box
├── global/                       #   factory config, standards, model routing
├── library/                      #   operator's aesthetic reference library
├── projects/<name>/              #   brain/, gates declaration
│   └── mirror.git                #   bare mirror — workers push here only
├── seats/<name>/                 #   identity, memory, handoffs/
│   └── experience/<project>/     #   what this seat learned on this project
└── ledger/                       #   hourly exports of the work-graph database

/var/lib/Harness/                  # RUNTIME — local disk
├── ledger.db                     #   work graph + claims (SQLite; exports → ledger/)
└── work/<seat>/<project>/        #   disposable, automatically provisioned checkouts
```

*Reasoning:* SQLite over a network filesystem risks corruption, and dependency trees
on it make small-file operations unusably slow. The live database and disposable
checkouts are therefore local. The database is exported hourly; checkout durability
comes from early commits pushed to each store-backed mirror. Bare mirrors are compact,
append-mostly packfiles — the pattern network filesystems handle well. The runtime
work root is configurable for machine onboarding, but it must remain local scratch.

## Standing constraints

- Solo operator, this machine only. Multi-machine is out of scope until it isn't.
- Subscription-first. **Routing policy (current, revisable):** Anthropic models serve
  design and review primarily; implementation defaults to the Codex subscription,
  with inexpensive models for mechanical work. Interactive sessions are never starved
  by fleet activity.
- The credential behind the store's cloud sync expires ~May 2027. The store is plain
  files and exportable, so migration is a copy, not a redesign. Calendared, not
  feared.

## Bootstrap

The first version of the factory is **hand-built by the operator and design partner**,
outside the factory: store layout, ledger, context compiler v0, landing step. Its
first dispatched tasks may be drawn from the factory's own reviewed backlog — real
tickets, real gates. The original guard — the factory earns the right to work on
itself only after it has shipped someone else's work — survives as a tripwire:
**an outside project must ship before autonomy is granted.** *(The tripwire's
build-roster clause was consumed 2026-08-07 when the operator founded Rye ahead of
outside shipping — a recorded exception, not a deletion of the principle; the
autonomy clause is untouched and no seat pulls work unattended.)*

*Reasoning:* tooling whose first and only customer is itself tends to remain its only
customer. A real task forces every seam — dispatch, briefing, gates, landing — to
meet reality immediately — and a reviewed factory ticket does this as well as an
outside one, so the guard moved from the first dispatch to the tripwire above.
*(Amended 2026-08-06, Design 0002 = DEC-185: the first harvest produced a Harness backlog
before any outside project was registered; the operator ruled Harness-first with the
tripwire kept.)*

## Deliberately deferred

- **Pull loops / overnight autonomy** — earned per project by gate history (rule 9).
- **Standing role agents** (watchmen, health checks, intake) — motivated by real
  incidents; excavate when the factory operates production surfaces.
- **Sandboxing** — write boundaries, gates, and review are the current trust
  structure; revisit if the work or the models change character.
- **Merge batching** — serial landing until the ledger shows real queue pressure.
- **Multi-machine dispatch** — when one machine's ceiling actually binds.
- **Work-graph engine** — when multiple seats need atomic claiming: adopt Beads,
  fork it as Harness's own, or build from scratch (a recorded future design;
  research brief in Design 0001 = DEC-184). Local SQLite is correct until then.