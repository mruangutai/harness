# Observations — harness-product-lead — FEAT-26-pr-linkage-recorded

- 2026-08-18: A grep character class silently under-counted a distributive set. Checking pm's
  backfill map I ran `"FEAT-[0-9]+[a-z-]*":` and got 22 entries against SC-08's stated 23, which
  read as a BRIEF/plan disagreement and nearly became a `must_fix` against correct work. The
  pattern could not match `FEAT-06-team-layer-inv6` — the slug ENDS IN A DIGIT, so `[a-z-]*`
  stopped at `inv`. Re-running `"FEAT-[^"]*":` returned 23. This is a variant of G-11 but the cause
  is different: G-11 is about line wraps splitting a phrase, this is about a character class that
  looks slug-shaped but excludes digits. Feature slugs in this repo carry trailing digits
  (`inv6`, and any future `-v2`), so an id-matching pattern must be `[^"]*` or equivalent, never a
  hand-built class. The failure direction is the dangerous one: it reports FEWER items than exist,
  which is exactly the shape of a real distributive defect.

- 2026-08-18: Leads hold `Read, Glob, Grep, Agent, Write` and therefore have NO `SendMessage`, so a
  mid-flight course correction to a running member is impossible. I discovered a false premise in my
  own dispatch (invariant numbering) while pm was in flight and reached for a correction; the only
  tool that takes an agent id is `Agent`, which SPAWNS rather than messages. The call created a
  second `harness-pm` with a placeholder body — ~30k tokens, wrote nothing, returned BLOCKED.
  The correct move when a dispatch premise turns out wrong mid-run is to do nothing to the running
  member and carry the correction into the ASSESSMENT instead: grade the returned artifact against
  the corrected fact, and send back only if the member propagated the error. Here pm had read the
  primary source and self-corrected, so no send-back was needed at all — which is the general case
  worth expecting when a dispatch tells a member to read the file the premise is about.

- 2026-08-18: A run dir cannot be checkpointed before the first dispatch on a `plan` mission,
  because the run dir lives under a feature dir that does not exist until pm coins the id. The
  checkpoint-before-dispatch rule is unsatisfiable for exactly this one step. Pre-coining the id at
  the lead tier to fix the ceremony would be worse — three orchestrators were planning concurrently
  and two of them both coined FEAT-25, so widening the window between coinage and write is the
  actual hazard.

- 2026-08-22: `Glob` with a `path:` argument plus a relative pattern reaching into a dot-prefixed
  tree returned "No files found" TWICE for directories I had provably just written into —
  `path=<worktree>` + `.harness/harness/features/FEAT-26-.../notes/*.md`, and `path=<worktree>` +
  `runs/**/*`. The same files came back immediately from a single ABSOLUTE pattern with no `path:`
  argument. I had already begun treating the first empty result as evidence that pm's notes dir was
  empty, which is exactly the false-absence assertion G-14 exists to prevent — and unlike G-14 no
  amount of careful reading would have caught it, because the tool answered confidently and wrongly.
  Every path in this repo's state tree is dot-prefixed (`.harness/`, `.claude/`), so this is not an
  edge case here, it is the default case. Absolute pattern, no `path:`, whenever a Glob result is
  going to be read as an absence.

- 2026-08-22: My dispatch told pm its artifact went to "your own per-feature notes path under
  notes/" without pinning the filename prefix. `team-config.yaml` L92-94 grants pm exactly
  `notes/research-*.md` and `notes/uat-*.md`, so any other filename would have been denied by the
  domain guard and cost the whole spawn on a naming technicality. pm chose
  `notes/research-FEAT-26-brief-amend.md` and was fine, but that was pm knowing its own grant, not
  my dispatch being correct. A dispatch that names an output DIRECTORY rather than the exact glob
  the grant carries is one guard-denial away from a wasted member spawn.
