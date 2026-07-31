---
name: harness-wayfinding
description: Take a vague idea to plannable clarity when one sitting cannot hold it — a persistent map of decision tickets (GitHub sub-issues, or local markdown when sync is off), resolved one per session by grilling, research, prototype or task, until nothing is left to decide and the effort hands off to /harness-plan. Run by the main session only.
---

# Wayfinding — the map from fog to a plannable idea

`harness-grilling` takes an idea to clarity **in one sitting**. When the idea is bigger than that —
the destination itself is fuzzy, or there are more open decisions than one conversation can hold —
you need a **map that survives between sittings**. That is this skill. Adapted from Matt Pocock's
`wayfinder` (MIT), re-homed onto harness files (DEC-165).

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

**Every tracker operation goes through `bin/wayfind.py`**, never hand-typed `gh`:
`map <n>` · `frontier <n>` · `chart` · `ticket <map#> <type> "<title>"` · `block <n> --by <n>` ·
`claim <n>` · `resolve <n> <file>`. Mutations are **dry-run until `--apply`**. Three operations are
traps by hand and the script exists for them: the sub-issue API takes the child's internal `id` and
not its `number`; the frontier is a compound query no single `gh` call expresses; and a ticket
created without its `wayfinder:<type>` label is invisible to every later query.

## Grill or map? — the entry test

| Signal | Door |
|---|---|
| The destination is nameable and the open decisions fit one conversation | `harness-grilling`. Do not build a map |
| The destination itself needs deciding, or decisions depend on facts/prototypes you do not have | **map** |
| Grilling started and stalled on "we can't answer that until we know X" | **promote to a map**, carrying what is already settled |

Charting a map for a small idea is pure overhead — the map is for fog, and a map with three
tickets you could have talked through was a worse conversation.

## Plan, don't do

Wayfinding produces **decisions, not deliverables**. The map is done when nothing is left to decide
before someone builds — that hand-off is `/harness-plan`, with pm authoring BRIEF and PLAN from the
map. The pull to just start building is the signal you have reached the edge of the map, not
permission to carry on past it.

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
6. **One decision per session** (research tickets excepted). Then stop, even if you feel fine: the
   next session starts fresh and cheap, and a long session writes worse answers (DEC-159).

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
