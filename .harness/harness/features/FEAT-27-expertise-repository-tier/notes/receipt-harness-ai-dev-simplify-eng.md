# ALTITUDE read — harness-ai-dev — FEAT-27, `b4659cd..252fa72`

BLUF: one finding at briefing-row, everything else at the right altitude — **leave**. No
fold-in candidates (nothing here is cheap-and-safe enough to apply without qa's/eng-lead's
sign-off given the "no weakening an assertion" constraint, and my one finding needs a future
unit, not a same-cycle edit).

## Findings

### 1. Repository-tier injection has no per-dispatch segment filter — prose is the only guard against cross-repo bleed

`.claude/skills/harness/bin/inject-expertise.sh:82-97` — the hook globs and injects **every**
`.harness/*/expertise/<agent>.md` present, labelled only by segment name, and relies on one
sentence in the precedence line ("a repository block whose segment is not the one you were
dispatched against is not authoritative for your work — read the segment name") for the agent to
discount blocks belonging to a different repository.

**Cost:** unlike DEC-16's "irrelevant agent self-scopes" pattern (where a mismatched item is
simply *not applicable* and low-stakes to skip), a repository-tier block is a set of factual
claims ("migrations fail before the seed script") stated under the same heading shape regardless
of which repo it's true of. A future multi-segment repo with two or more `.harness/<seg>/expertise/`
directories injects all of them into every agent's context; misreading the segment line imports a
false fact about codebase B into a spawn working on codebase A, not merely noise.

**Alternative, precisely:** pass the dispatch's own repository/segment identifier into the hook's
input (today it only has `agent_type`) and filter the glob to that segment plus a pre-agreed
"generic/none" bucket, removing the need for the prose caveat entirely for the common case.

**Why not fold-in now:** this is already a documented, adjudicated open item — `notes/research-FEAT-27-expertise-tier.md:115-117`
records it as D-01 and states the blocker precisely: the hook has no per-dispatch segment input
this cycle, and `fleet.yaml`/`harness.json` are no-touch this cycle. The fix needs a different
unit's surface. Re-litigating the caveat's wording is explicitly out of scope for this reader per
the dispatch.

**What would prove it safe today:** nothing does, at single-segment scale — `.harness/*/expertise/`
currently resolves to at most one directory in this repo, so the failure mode is latent, not live.
The proof needed is a second segment directory actually present plus a transcript showing an agent
correctly discounting the foreign block; that test doesn't exist and can't without a second
repository segment to inject.

**Verdict: briefing-row.**

## Checked and found correctly placed (no finding)

- **Tier-classification test has one authority.** Grepped the classification-test phrasing
  ("could this be true and useful in a repository you have never seen?") across all six files the
  dispatch named as duplication risk — it appears exactly once, in `harness-distill/SKILL.md:49`.
  The other five (curate, SPEC.md, README.md, the hook, the checker) carry only budget numbers
  (150/40, consistently) or mechanical path-classification regexes, never the test itself.
- **Agent-name validation (`inject-expertise.sh:22-28`).** No pre-existing shared home for this
  check exists anywhere under `.claude/skills/harness/bin/` (grepped for the pattern and for
  agent-name-validation helpers — none found). The comment correctly scopes it as interpolation
  hygiene only, not an authorization filter, and it guards exactly the value it protects. Right
  altitude for a single call site with no shared consumer.
- **Advisory token scan (`check-expertise.sh`, CHANGE 2).** Shape matches the already-settled
  two-enforcement-points-for-one-budget-pair pattern: authoring-time lint on top of, not instead
  of, the distillation judgement call — and it is explicitly non-blocking, which is the correct
  restraint given the feature's own measurement (`harness-distill/SKILL.md:52-53`: 11 of 16
  repo-token hits were adjudicated repository-layer, 5 stayed craft "because the token was an
  example rather than the thing the rule turned on") — i.e., the token is not a reliable proxy for
  the rule, so a blocking version of this scan would be wrong at the altitude it's pitched.

## Out of bounds, flagged only

`.harness/team-config.yaml`'s per-agent repository-tier grant rows, the twelve Expertise files, and
the doc prose in `.harness/README.md`/`SPEC.md` were read for context (needed to confirm the
single-authority claim above) but carry no findings requiring action beyond what's already noted.
