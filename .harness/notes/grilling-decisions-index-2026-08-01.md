# Grilling — DECISIONS.md index — 2026-08-01

## Destination

**`DECISIONS.md` stops being read whole.** An agent that must be correct about decisions reads a
bounded index and greps the two or three entries that bear on its task. The full file stays the
authority; `check-docs.sh` keeps harvesting stale markers from it. Scope is that one file.

Measurable: the next self-hosted feature's cache-read-per-output ratio drops materially from the
137x measured on FEAT-03.

## Settled

- **Index and citation discipline compose — build both.** They solve different problems: a
  dispatch naming its DECs gives **precision** (the agent needs *these*); the index gives **recall**
  (nobody knew in advance which apply). Citation alone is unfalsifiable — nothing checks that the
  dispatcher named the right DECs, so a missed one is silent, and correctness would rest on a
  dispatcher's recall of 170 decisions. The index makes citation mechanical: the dispatcher greps the
  index instead of remembering.
- **Citations are a FLOOR, never a ceiling** — the same language qa-gate already uses for the test
  matrix. A cited list means *at minimum these*.
- **Four go-broad triggers**, the first mechanical rather than instinct: (1) a cited DEC references an
  uncited one — with 426 in-body refs this is the common case, so following the graph is a lookup;
  (2) you are about to judge something the citations do not cover; (3) your own Expertise implies a
  rule they omit; (4) "surely this was decided already" fires.
- **Index row = hand-written ruling + generated topic tags + generated reference/supersession graph.**
  Titles alone are insufficient — a title says a decision *exists* about serialization, not what it
  ruled, which is most of the cost being removed.
- **The ruling is an open-or-skip filter, never the rule itself.** Its only job is to answer "do I
  open this entry?" An agent never acts on a ruling alone — same relationship as `INDEX.md` to the
  map views, or a `file:line` anchor to code: the pointer's whole value is that it survives being
  opened. **This is what makes the paraphrase backfill safe** — a lossy summary costs one
  unnecessary file-open, where an *acted-on* summary would make a prior session's compression law.
- **Ownership: documentor owns the index file.** No domain change needed — `docs/**` with
  `upsert: true` is already granted. It regenerates the mechanical columns and does the one-time
  ~170-row backfill, flagged as paraphrase. **It never touches `DECISIONS.md`.** Chosen over
  main-session-only because SC-13 proved this week that a step with no owner in the org has no
  checkable moment and gets forgotten.
- **New DECs carry their ruling written by their own author, in the same commit.** Paraphrase stops
  at today; only the backfilled rows are second-hand.
- **Access: read-on-demand by path.** `CLAUDE.md:43` changes from "read `DECISIONS.md`" to "read
  `DECISIONS-INDEX.md`, then grep the entries it names; never read `DECISIONS.md` whole (DEC-150)."
  Zero cost per spawn. Same demotion DEC-158 applied to `harness-systematic-debugging`. **Rejected:**
  preloading as a skill or injecting via `SubagentStart` — either charges all 16 spawn types for
  ~180 lines whether they touch decisions or not, undoing more than the feature saves.
- **The discipline ships in `harness-handoff`; the path pointer stays in harness's `CLAUDE.md`.**
  Verified: `deploy.sh` ships skills/agents/commands/templates and **never** `CLAUDE.md`;
  `harness-init` never writes one either. So a rule naming `docs/harness/DECISIONS-INDEX.md` is
  repo-specific, while the discipline (floor-not-ceiling, the four triggers, never read an authority
  whole) is universal and must travel. `harness-handoff` is preloaded by all 16 agents and kaya's
  copy is byte-identical, so the reach is confirmed.
- **Superseded DECs are marked in the index, and their text stays put** for this feature. The index
  row carries `SUPERSEDED BY DEC-NN` so an agent knows not to act on it.
- **Supabase: rejected.** Files-only is load-bearing (`CLAUDE.md`), and four concrete breakages:
  `check-docs.sh`'s registry *is* the file it greps; a DB read puts the network in front of a gate
  that fails open; git diffs *are* the record of how the thinking evolved (DEC-165's correction is
  only legible as a diff); and a row update has no signature surface. **The legitimate version, if
  ever wanted:** keep the file as truth and *project* it into Supabase as a derived read-model — the
  `map.html` pattern. Buys querying from outside a session; buys an agent nothing, since grep already
  answers those queries.

## Not yet specified

- What a *fresh* project's decision record contains at init, and whether an existing project (kaya)
  gets backfilled and by whom. Belongs to the per-project feature below, not sharpenable until its
  destination is named.
- Whether the ruling column ever needs a length cap. Suspect yes; no evidence of the failure yet.

## Out of scope

- **The archive split** — moving superseded text to `DECISIONS-ARCHIVE.md`. Decided as desirable, but
  **its own feature after this one**: it restructures the authority file and its gate is that
  `check-docs.sh` still harvests all 49 stale markers and all 426 in-body refs still resolve. Getting
  that wrong breaks the propagation checker, which gates every `/harness` entry. The index delivers
  its whole value without moving a line.
- **Per-project decision records** — teaching `harness-init` to establish a project's own
  `DECISIONS.md` + index and point that project's `CLAUDE.md` at it. Its own feature, and it is also
  what finally gives kaya's pre-harness decisions somewhere to live.
- **`SPEC.md` (2,160 lines) and `BUILD.md` (971)** — the destination is scoped to one file.

## Facts I verified (so pm does not re-derive them)

- **170 top-level DECs + 9 amendments.** 49 stale markers (check-docs' registry, spread through the
  file). **426 in-body `DEC-NN` references** — ~2.5 per DEC, a dense graph, mechanically extractable.
  9 titles carry an explicit supersession verb (SUPERSEDES / CORRECTS / INVERTS).
- **Only three places tell anyone to read the file**; `CLAUDE.md:43` is the load-bearing one
  ("Before changing any harness doc, read `docs/harness/DECISIONS.md`").
- **Mandatory reading today: 7,544 lines ≈ 97k tokens** — DECISIONS 4,413 + SPEC 2,160 + BUILD 971 +
  CLAUDE 51.
- **FEAT-03's measurement: 137 cache-read tokens per output token**, and `eng-lead` was the single
  most expensive agent (\$16) despite spawning no members — it read the authority to review correctly.
- **It compounds:** eleven DECs were appended on 2026-07-31 alone.
- **`deploy.sh` ships `SKILL_DIRS`, `AGENTS`, `COMMANDS`, `templates` — not `CLAUDE.md`.**
  `harness-init` does not write `CLAUDE.md` either. kaya has **no** decision record of any kind.
- **kaya's `harness-handoff` is byte-identical to harness's**, confirming a skill edit reaches every
  deployed project on the next `deploy.sh --apply`.
- **documentor's domain already includes `docs/**` with `upsert: true`** — no `team-config.yaml`
  change is needed for it to own the index.
- The `harness.json` budget note says to lower `per_feature_usd` from 120 once this lands.
