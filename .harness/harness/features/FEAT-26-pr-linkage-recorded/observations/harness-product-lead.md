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
