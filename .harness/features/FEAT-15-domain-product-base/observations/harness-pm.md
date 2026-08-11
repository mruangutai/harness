# Observations — harness-pm — FEAT-15-domain-product-base

- 2026-08-10: the ruling's four explicit entries were mechanically inexpressible under the plan's
  original glob-keyed classifier, and the defect was half-invisible: `README.md` and `.github/**`
  are exact manifest globs so they work either way, while `docs/harness/**` and `docs/PRINCIPLES.md`
  have no manifest entry at all (`.harness/team-config.yaml` grants documentor only `docs/**`).
  Half a list working is what makes a classifier-keying error survive review. Checking whether the
  data an option keys off actually contains the option's own terms is a cheap discriminator.
- 2026-08-10: the routing measurement that justified the ruling (`0 violation(s)`) models in-harness
  resolution only. Every product-side consequence of the rule was invisible to it, so the whole
  product half of the ruling rested on one added SC (SC-13) and one task group (T-03 pair C). When a
  measurement's model is narrower than the rule it measures, the uncovered half is the highest-value
  place to spend a criterion.
- 2026-08-10: scope stayed at five tasks; the depth was in T-02's intent, which roughly doubled
  because the two-sided rule had to be stated as a procedure rather than as "dual-base". Prose
  shorthand for a two-sided rule is what admitted the wrong reading in the first place.
- 2026-08-10: research and the ruling were pinned at `06ae963`/`96d5d5c`, HEAD had moved to
  `f3452bf`. Re-running `git diff --stat` over just the four cited files before reusing the
  disposition table cost one command and was the difference between a live table and a stale one
  (G-01). Only `.harness/team-config.yaml` had moved, and only by one control-plane glob.
