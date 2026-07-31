# Orchestrator playbook — rare missions (map, deepen)

Read this file only when dispatched with mission **map** or **deepen** (DEC-158). These run
between features, never inside a build; the plan/ship loop does not need them.

## Mission: map — understand-codebase (DEC-137)

Builds `.harness/codebase/` for a project the org has never seen. Not a team — **you sequence
per-squad runs** (DEC-118), each specialist authoring the view it will later consume. The manifest
carves the map by author; a wrong-author write is hook-blocked.

1. **Eng squad run** (eng-lead): backend-dev → `api-surface.md` + `domains/`; data-engineer →
   `data-flows.md`; frontend-dev → `ui-surface.md`; ai-dev → `llm-patterns.md`; dev-ops →
   `stack.md`. Steps are parallel — disjoint outputs. **A specialist whose surface does not exist
   self-scopes out in one line** (a CLI has no ui-surface); an empty view is a valid result.
2. **In the same turn, dispatch validator-lead**: security-reviewer → `trust-boundaries.md`; and
   **product-lead**: pm → `product-surface.md` **and `glossary.md`** (the ubiquitous language —
   one canonical term per concept, `_Avoid:` variants named, no implementation detail; the
   authoring rules are pm's own `harness-spec-driven` glossary section). Lazy creation failed in
   the field — three features shipped vocabulary with no glossary (DEC-162) — so the map is the
   checkable moment it gets authored. Independent of the eng run — all three go together.
3. **Documentor consolidates last** (product-lead, second run): reads every view, writes
   `architecture.md` and `INDEX.md` from the template (`templates/codebase-INDEX.md`). **The 60-line
   index cap is documentor's to honor** — the index is injected into every future spawn.
4. **Render the human view:** run `bin/render-map.py` — generates `codebase/map.html` (collapsible
   TOC, domain sections, Mermaid architecture diagrams) FROM the markdown. Derived, never authored:
   no agent writes HTML, and it needs no freshness policy of its own — it is exactly as fresh as the
   markdown it projects. Architecture diagrams (physical + component) are authored as ```mermaid
   blocks in `architecture.md` by documentor.

Rules that bind every view: **every claim carries a `file:line` anchor** — unanchored prose is
opinion, not a map; every section header carries `author · date · anchors-verified: <sha>`; the map
records what IS, never what should be — improvement ideas go to `open_questions`, not the map.

Authoring rules the first real audit earned (DEC-141):
- **Every view opens with `## In brief` — plain English, no jargon, no anchors** — three to six
  sentences a non-engineer reads and understands. The map's first audience is the human opening
  map.html; the anchored technical detail FOLLOWS the prose, never replaces it. A view that reads
  as a parts inventory has failed its reader (observed, round 2 of the kaya audit).
- **Prefer top-down (`graph TD`) diagram orientation** — layered architectures read naturally
  top-down, and the rendered viewport is full-window-width with a fixed height.
- **Every diagram edge is labeled with what flows — in BOTH directions.** An edge labeled only
  with its write path hides the read path sharing the same arrow.
- **An arrow into a module means what the module's NAME implies.** `WORKER → api/` read as an HTTP
  dependency when the worker merely imported persistence modules living under `api/` — split the
  node or point at the submodule, never let directory layout impersonate architecture.
- **No raw HTML comments in view bodies** — the renderer strips them now, but they are authoring
  metadata and belong in headers, not prose. Write for the human who reads map.html.
- **Physical and component diagrams stay at their level** — processes/runtimes/externals in one,
  modules/boundaries in the other; a mixed diagram answers neither question.

## Mission: deepen — the architecture-review scan (DEC-149)

Runs **between features**, on the user's invocation or when a briefing/backlog signals friction —
never inside a build (mid-build is the wrong time to want a different architecture). Proposes work;
the map records what IS. Adapted from Matt Pocock's `improve-codebase-architecture` (MIT), re-homed
onto harness machinery:

1. **Scope by heat.** Hot spots first: the files the last shipped feature(s) touched (union their
   `files_touched`), then `git log --oneline` recurrence. Deepening pays off where change happens.
2. **Scan** (eng-lead conducts): specialists walk their own surfaces for friction, in the
   `harness-codebase-design` vocabulary — shallow modules (deletion test), understanding one
   concept requiring a bounce across many small modules, tests that reach past an interface, seams
   nothing varies across. Read `glossary.md` first — candidates are named in domain terms — and the
   feature dirs' `## Decisions`: a candidate contradicting a recorded D-NN surfaces only if the
   friction justifies REOPENING it, flagged as such.
3. **Verify adversarially** (validator-lead): each candidate gets the review-panel treatment — is
   the friction real, does the deletion test actually concentrate complexity, what breaks? Killed
   candidates die with a reason.
4. **Report:** survivors land in `.harness/features/` as a notes artifact — per candidate: files,
   problem, solution in plain English, benefits as locality/leverage, recommendation strength
   (Strong / Worth exploring / Speculative) — topped by ONE top recommendation. Human-readable
   rendering follows the render-map pattern (offline, derived, never authored HTML). No interfaces
   are designed at this stage.
5. **The user picks at the briefing.** An accepted candidate enters `/harness-plan` as a normal
   feature (design-it-twice available to eng-lead at its interface-defining tasks); a rejection
   with a load-bearing reason is recorded as a D-NN so the next scan does not re-suggest it.

