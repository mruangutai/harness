---
name: harness-wayfinding
description: Take a vague idea to plannable clarity when one sitting cannot hold it — a persistent map of decision tickets (GitHub sub-issues, or local markdown when sync is off), resolved one per session by grilling, research, prototype or task, until nothing is left to decide and the effort hands off to /harness-plan. Run by the main session only.
---

# Wayfinding — the map from fog to a plannable idea

`harness-grilling` takes an idea to clarity **in one sitting**. When the idea is bigger than that —
the destination itself is fuzzy, or there are more open decisions than one conversation can hold —
you need a **map that survives between sittings**. That is this skill. Adapted from Matt Pocock's
`wayfinder` and `batch-grill-me` (the frontier round), MIT, re-homed onto harness machinery
(DEC-165/166/167).

**Main session only** — every HITL ticket resolves through live exchange with the user, and no
subagent has a channel to them (DEC-120).

**Two storage modes, chosen by config, not by preference (DEC-166):**

| `github.sync` in harness.json | Mode | Where the map lives |
|---|---|---|
| `true` and `gh` works | **tracker** (the default) | a `wayfinder:map` issue; tickets are **sub-issues**; blocking is the native `blocked_by` dependency; the claim is the assignee |
| `false`, or `gh` missing/unauthenticated | **markdown** | `.harness/efforts/<slug>/MAP.md` + `tickets/T-NN-<slug>.md` |

Tracker mode is preferred because a map that spans days is a **shared** artifact: you can read it,
add a ticket, or see the frontier render in GitHub's own UI without opening a session. This is not
the DEC-138 mirror — wayfinding runs entirely *before* any approval, where DEC-138 already sanctions
issues as an input, so reading issue state here breaks no one-way rule.

**In tracker mode GitHub is the canonical store — there is no markdown shadow (DEC-167).** What is
saved, and where:

| What | Where it lives | Notes |
|---|---|---|
| The **dialog** itself | nowhere, deliberately | it is the transcript: ephemeral, and a verbatim log is not a decision |
| The **decision** | the ticket's resolution comment, on close | `wayfind.py resolve <n> --body "…"` — inline by default, so a short answer needs no local file. Postable because it is the **user's own answer**, not agent prose (DEC-138 am.6) |
| The **one-line gist** | the map body's `## Decisions so far` | the index entry pointing back at the ticket |
| A substantial **asset** (research findings, a prototype, a long analysis) | a file in the repo, **linked** from the comment | never pasted into the issue, and never a second copy of the decision |

The order is always **decide → record on the ticket → gist on the map**. Writing a local markdown
copy of a decision that already lives on a ticket is the two-copies drift this org keeps finding
(the digest.md gap, the qa-gate matrix table) — do not do it.

**Every tracker operation goes through `bin/wayfind.py`**, never hand-typed `gh`:
`map <n>` · `frontier <n>` · `chart` · `ticket <map#> <type> "<title>"` · `block <n> --by <n>` ·
`claim <n>` · `resolve <n> <file>`. Mutations are **dry-run until `--apply`**. Three operations are
traps by hand and the script exists for them: the sub-issue API takes the child's internal `id` and
not its `number`; the frontier is a compound query no single `gh` call expresses; and a ticket
created without its `wayfinder:<type>` label is invisible to every later query.

## Grill or map? — the entry test

This is the single door for an unclear idea, so the first act is deciding whether the idea needs a
map at all. Nothing here sends the user somewhere else — both answers are yours to run.

| Signal | What you run |
|---|---|
| The destination is nameable and the open decisions fit one conversation | **Grill it here.** Load `harness-grilling`, run the interview, write its artifact, stop. Build no map |
| The destination itself needs deciding, or decisions depend on facts/prototypes you do not have | **Chart a map** |
| A grilling started and stalled on "we can't answer that until we know X" | **Promote it to a map**, carrying what is already settled |

Charting a map for a small idea is pure overhead — the map is for fog, and a map with three
tickets you could have talked through was a worse conversation.

## Plan, don't do

Wayfinding produces **decisions, not deliverables**. The map is done when nothing is left to decide
before someone builds — that hand-off is `/harness-plan`, with pm authoring BRIEF and PLAN from the
map. Offer it and hand over the map path. Do not start planning unasked. The pull to just start
building is the signal you have reached the edge of the map, not permission to carry on past it.

## The map

**Tracker mode** — the map issue's body is the low-res whole (same sections as
`templates/MAP.md`: Destination, Notes, Decisions so far, Not yet specified, Out of scope); each
ticket is a sub-issue whose body is `## Question`, its answer posted as the resolution comment on
close. No ticket table is maintained by hand: status, type and blocking all live natively, and
`wayfind.py map <n>` renders the view.

**Markdown mode** — the same shape in files:

```
.harness/efforts/<slug>/
  MAP.md              # the low-resolution whole, from templates/MAP.md
  tickets/T-NN-<slug>.md
```

**Naming, either mode: the name comes from the DESTINATION, not the idea you were handed** — the
idea's wording is the fuzzy part; the destination is the first thing charting settles, which is why
the map is created at step 3, never step 1. 2–4 words. Tracker mode titles the issue
`Effort — <name>` and its **number** is the identity thereafter. Markdown mode kebab-cases it into
`.harness/efforts/<slug>/`, and that slug is **immutable** — the path is what `/harness-plan` is
handed and what the BRIEF cites, so a rename breaks recorded references (DEC-133's reasoning).
**Never reuse a feature's name**: an effort may spawn several features, and a 1:1 name invites the
reader to assume it is one. Test: if a second effort could plausibly claim the same name, it was not
specific enough — `bulk-statement-correction`, not `statements`.

**The map is an index, not a store** in both modes: a decision lives in exactly one place — its
ticket — and the map only gists it and points. Load the map once per session; zoom a ticket on
demand.

**The frontier is every open ticket whose blockers are all closed and which nobody has claimed** —
the edge of the known, and the only takeable work. Tracker mode computes it from native state
(`wayfind.py frontier <n>`); markdown mode reads it off the ticket table, whose rows carry
`open` · `claimed` · `closed` plus type and blockers.

## Ticket types — because not every unknown is a conversation

| Type | Who drives | Use when |
|---|---|---|
| `research` | **agent alone** — dispatch a subagent (`Explore`, or a specialist through its lead) | a decision waits on a fact: docs, an API's real behaviour, what the codebase actually does |
| `prototype` | with the user | "how should it look / behave" — build something cheap and throwaway to react to, via `harness-visual-designer`. Link the artifact; never inline it |
| `grilling` | with the user | the default: a decision that needs the user's judgment. Run `harness-grilling` on that one ticket |
| `task` | either | something must *exist* before a decision is possible — access provisioned, data moved, an account made. The one type that does rather than decides; it earns its place by unblocking a decision |

**Never answer a HITL ticket yourself.** An agent that supplies the user's side of a grilling has
produced a fabricated decision, which is worse than an open ticket.

## Charting (first session)

1. **Name the destination** — run `harness-grilling` on that alone. It fixes the scope, so it is
   settled before anything else.
2. **Map the frontier breadth-first** — grill across the whole space rather than deep on one thread,
   surfacing the open decisions and what is takeable now. **Surfaced no fog?** The idea did not need
   a map: stop, say so, and hand the grilling artifact to `/harness-plan`.
3. **Create the map** — tracker: `wayfind.py chart "<destination>" --apply`, then fill its body's
   Destination and Notes (decisions empty, the dim view in `## Not yet specified`). Markdown:
   the same from `templates/MAP.md`.
4. **Create the tickets you can specify now** (`wayfind.py ticket <map#> <type> "<title>" --apply`),
   then wire blockers in a **second pass** — issues need ids before they can reference each other
   (`wayfind.py block <n> --by <n> --apply`).
5. **Fire the research tickets in parallel** — they need no user, so they run now while the map is
   fresh.
6. **Stop.** Charting resolves nothing; a session that charts and then starts resolving has spent
   its context on both and done neither well.

## Working the map (each later session)

1. Load the low-res view — `wayfind.py map <n>` (tracker) or `MAP.md` (markdown). Not every
   ticket body.
2. Take the first frontier ticket (or the one the user names) and **claim it first**, before any
   work, so a concurrent session skips it — `wayfind.py claim <n> --apply` (the assignee IS the
   claim; an open unassigned ticket is unclaimed).
3. Resolve it by its type. Zoom only what this ticket needs.
4. Record: the answer as the ticket's resolution and the ticket closed — `wayfind.py resolve <n>
   <file> --apply` (markdown: `## Resolution` in the ticket file) — plus **one gisted line** in the
   map's `## Decisions so far` pointing at it.
5. **Graduate the fog the answer sharpened** into new tickets, clearing those patches from
   `## Not yet specified`. If the answer puts something past the destination, close it into
   `## Out of scope` with the reason — never resolve it on the route.
6. **One THREAD per session, then stop** — even if you feel fine: the next session starts fresh and
   cheap, and a long session writes worse answers (DEC-159). A thread is either one ticket explored
   deeply, **or one frontier round** (below). Sessions are contexts, not calendar days: running six
   back to back in an afternoon is the intended use, and costs only a map reload each.

## Clarity fast AND context-cheap — the frontier round (DEC-167)

The serialising rule bounds how deep one decision is explored; it never required serialising
**independent** decisions, and frontier tickets are by construction unblocked by each other.

**Step 1 — split the frontier by who drives it.** Every `research` ticket fires **in parallel,
immediately**: no user is needed, and fog most often hangs on facts. `wayfind.py round <n>` lists
those first for exactly this reason.

**Step 2 — for what is left, batch or serialise on TWO axes, not one:**

| | **Shallow** (a recommendation plus a pick settles it) | **Deep** (needs back-and-forth to reach an answer) |
|---|---|---|
| **Independent** | **BATCH** — one numbered round, recommendation each, then wait | **serialise** — one ticket per thread |
| **Dependent** | serialise — the first answer changes the later questions | serialise |

Independence alone is not enough: two questions can be unblocked by each other and still each need a
real conversation. Depth alone is not enough either: three deep questions do not become one round by
being independent.

**`prototype` tickets are never line items in a round.** The artifact *is* the exchange — you build
something cheap, the user reacts, and that reaction is the answer. It gets its own thread even when
it sits on the frontier beside three batchable questions.

**The user's stated preference outranks this table.** "Just ask me one at a time" or "give me
everything you've got" is a decision about how they want to work; take it and drop the heuristic.

A round is not a licence to dump every open question: a ticket still on the frontier only because
nobody wired its blocker is not independent, it is mis-wired.

## Fog, and out of scope

- **`## Not yet specified`** — in-scope questions you cannot yet state sharply. The test is the
  *question's* sharpness, never whether you can answer it: a sharp question you cannot answer is a
  ticket (possibly blocked); a fuzzy one is fog. **Do not pre-slice fog** — one patch may graduate
  into several tickets or none.
- **`## Out of scope`** — ruled beyond the destination. Scope, not sharpness, lands it here, and it
  never graduates: the frontier stops at the destination. Re-drawing the destination is a fresh
  effort, not a resumption.

## Done — and the hand-off

Done when the frontier is empty and no fog remains: nothing left to decide before building. Then
hand `/harness-plan` the **map path**. `## Decisions so far` is what pm authors REQs from,
`## Out of scope` is what keeps the BRIEF's scope honest, and every ticket's `## Resolution` is
there to zoom when pm needs the detail. pm still owns REQs, SCs and tasks — you removed the fog,
not its job.

## Red flags

| Thought | Reality |
|---|---|
| "I'll chart the map and resolve the first two while I'm here" | Charting is a session. Both jobs done badly is the outcome |
| "I know what the user would say here" | Then you are writing a fabricated decision. HITL means they answer |
| "I'll ask the user what the API returns" | A fact — that is a `research` ticket, and it is yours |
| "This fog is basically three tickets" | Pre-slicing invents structure the next answer may delete |
| "It's out of scope but I'll note it in the fog" | Fog gathers only *toward* the destination. Out of scope is its own section |
| "The map is nearly clear, I'll start building" | The edge of the map is the hand-off to `/harness-plan`, not a green light |
| "I'll put the ticket detail in MAP.md so it's all in one place" | The map is an index. A decision lives in one place — its ticket |
| "I'll wire the sub-issue with the ticket number" | The API takes the internal `id`. Use `wayfind.py ticket`, which reads it for you |
| "I'll maintain a ticket table in the tracker map's body" | Status, type and blocking are native there. A hand-kept table is a second copy that drifts |
