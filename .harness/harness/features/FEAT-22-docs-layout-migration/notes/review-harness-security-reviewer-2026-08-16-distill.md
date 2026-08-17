# Distillation — harness-security-reviewer — FEAT-22

Sources: cold digest-and-notes skim only (no observations log exists for this squad — confirmed,
none under `.harness/harness/features/FEAT-22-docs-layout-migration/observations/harness-security*`).
Cost of that: none I can point to concretely. Both of my panel runs (2026-08-15 plan-panel,
2026-08-16 run-13) wrote dense, self-contained notes with literal probe output, so the granular
detail an observations log would have preserved was already captured in those notes. The one thing
a hot log might have caught that a cold skim cannot is *why* I reasoned the way I did in the moment
(vs. what I concluded) — but neither lost entry below turned on that.

## Relayed candidates — disposition

**C-1 — accepted, as Gotchas (not Patterns).** The lead's correction is real: I classified the
over-grant remedy's routing by the file where the *defect* lives (`team-config.yaml`, data) rather
than by the file the *remedy I actually stated* — segment-aware enforcement — would change
(`check-domain.sh`/`harness_boundary.py`, a DEC-174 carve-out). Placed in Gotchas rather than
Patterns because it's shaped as a trap adjacent to G-10 (state remedy as constraint, not direction)
— same neighborhood, different axis (who owns the remedy vs. how to word it). Gotchas had headroom
(11/15), so no displacement needed. New entry: G-12.

**C-2 — rejected, overlap.** The panel's point (my resolve-matrix reproduction proves current
correctness but pins nothing against future change) is the same shape G-09 already states:
"correct only by coincidence for today's single value; tests scoped to that value cannot catch
future divergence" — applied there to a hardcoded literal, here to a grant's reach. O-01 also
already requires identity-level evidence to close, which the panel's framing doesn't contradict (my
resolve matrix *was* identity-level evidence for *current* state — the gap is forward-looking
pinning, which G-09 already covers). No new actionable rule survives past these two. Checked hard
per the dispatch's instruction; confirms the suspected overlap.

**C-3 — accepted, as Outcomes.** Distinct from P-12 (assessed-and-dismissed *findings*): this is
about recording *unreproducible observations* and *denied probes* — non-findings — because two
independently-run agents' recorded-not-smoothed anomalies is what let the lead correlate them into
one infrastructure defect report. Outcomes had headroom (3/10). New entry: O-04.

## My own skim — no additional candidates

Reviewed both digests and my own two panel notes end-to-end. Nothing surfaced that isn't already
covered by an existing entry: CHECK 4's guard/grant-combination reasoning in the plan-panel note is
an application of P-10, not a new lesson (I cited P-10 by ID in that note at the time). The
multi-variant-remedy table (narrow / enforcement / witness, three different owners) is the same
lesson as C-1/G-12, already captured there.

## Flag, not a write — repository-layer candidate

P-01 is repository-shaped (names `.claude/skills/harness/bin/*.{py,sh}`, `bin/factory_*.py`,
`fleet.yaml`, `gh` — true of this repo, not a repo I haven't seen). Per dispatch: flagging, not
moving. No grant exists for `.harness/harness/expertise/harness-security-reviewer.md`; the lead or
an agent holding that grant should relocate it.

## check-expertise.sh

First run: `FAIL` — G-12 (62 words) and O-04 (58 words) both over the 50-word cap. Trimmed both;
second run: `OK`.

## Counts

| Section | Before | After |
|---|---|---|
| Patterns | 15/15 | 15/15 (unchanged) |
| Gotchas | 11/15 | 12/15 |
| Outcomes | 3/10 | 4/10 |
| Open | 0/5 | 0/5 |
