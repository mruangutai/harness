# Handoff — FEAT-03-subissue-mirror, validate → ship — written at e68ba00, seq-6 (supersedes seq-5)

## Next

**Nothing is dispatchable. Present `notes/ship-review-2026-07-31-16.md` to the user and wait.** The
ship phase ends at a user gate, and the briefing is written, committed and complete. Three things come
back from the user, not from any agent: the ship/fix/re-scope/stop decision; the SC-13 edit to
`.claude/skills/harness/SKILL.md:137,144`, which no agent domain covers; and a judgement on the
half-applied `abandon` (product recommends a follow-on BRIEF item, not a FEAT-03 fix). On `ship`, the
unstruck backlog items B-1..B-12 become issues. **Do not dispatch a lead for any of it.**

## Trust

- **All twelve in-scope SCs met** (`runs/2026-07-31-13-product/digest.md`, `sc_status` 12 entries);
  panel + blocking qa PASS with `must_fix: []`, `matrix_ok: true` (`runs/2026-07-31-12-validator/`) —
  verified-at e68ba00
- **SC-12's reported evidence gap was a FALSE PREMISE and is closed.** `ship` is pre-existing —
  `BRIEF:19-20` names it, and at the approval commit `cmd_ship` was defined while `cmd_abandon` was
  not. `abandon` is the only new verb; `test-gh-sync.py:529` covers it. I re-ran the counts myself
  rather than accepting either tier — verified-at e68ba00
- **`test-gh-sync.py:353`'s label lies** — it claims "for the new subcommand too (SC-12)" while `:351`
  invokes `open`. That false label, not a real gap, propagated through two review tiers. Backlog B-2 —
  verified-at e68ba00
- **All eight `.harness/expertise/*.md` pass `check-expertise.sh`.** Two were repaired, not just
  extended: `harness-security-reviewer.md` had **four pre-existing violations** its member fixed, and
  **my own file had eleven** (six over the 50-word cap, five carrying feature ids) which I distilled
  this run — the spawn hook had been injecting a file its own validator rejects — verified-at e68ba00
- **Five commits: `2897b09`, `ae728e8`, `e68ba00`, `4d4c3af`, plus the close-out.** `git log
  4d00dbc..HEAD` shows only mine; the two `harness-*/SKILL.md` files were last touched by pre-existing
  `9a1f638`/`e4a07fb`, so nothing unintended rode in (validator Q5 resolved) — verified-at e68ba00
- **Cost ~$341 of $120 (2.8x); `cycles_used` 6 of 10.** ~$162 predates the build. Three of the six
  cycles were prose-only send-backs, no implementation rejected once — verified-at e68ba00
- **13 lead Expertise ops ride up UNAPPLIED** in my digest (eng 4, product 6, validator 3). My dispatch
  told leads not to self-apply on an over-generalized reading of my own G-01: the hook blocks *me* from
  writing another agent's file, but `team-config.yaml:259` grants each lead its own with `upsert: true`.
  Now corrected in my Expertise — UNVERIFIED whether the main session applies or re-dispatches
- The live GitHub API path is proven by nothing here: `github.sync` false, `repo` null, all three mirror
  sync points SKIP, every assertion against the fake `gh` — UNVERIFIED by design

## Dead ends

- **Editing `.claude/skills/harness/SKILL.md`** — SC-13 is the user's; an agent doing it is the boundary
  violation Q13 names — source: PLAN Preconditions
- **Widening `post_body_path`'s `except OSError`** (B-1) or **fixing the lying label** (B-2) now — both
  are post-gate changes to a passing suite; they are backlog, not in-flight — source: orchestrator, this
  run; validator Q3
- **Re-adjudicating SC-12, the `absorbs:` inversion, or `ship`/`abandon`'s origin symmetry** — settled
  over three fix cycles and re-verified post-build — source: user at 4d00dbc
- **Declaring a `<!-- stale: -->` marker for the SKILL.md wording** — turns `check-docs.sh` red and
  gates every `/harness` entry until the user's edit lands. Land the edit FIRST, then a marker is legal
  — source: PLAN Preconditions; T-08
- **A ship-refresh, ui review, or visual-designer pass** — no map/`INDEX.md` exists, no visual surface,
  no DESIGN.md — source: orchestrator; `skipped_segments`

## Working set

- `notes/ship-review-2026-07-31-16.md` — the briefing; the only artifact addressed to a human
- `{STATE.md,feature.yaml}` — phase `ship`, status `awaiting_user`, 16 runs recorded with per-run cost
- `runs/2026-07-31-13-product/digest.md` (goal-check `sc_status`) and `runs/2026-07-31-12-validator/digest.md`
- `.claude/skills/harness/SKILL.md:137,144` — SC-13's subject, the user's pending edit
