# Observations — harness-ai-dev — FEAT-27

- 2026-08-19: ALTITUDE read of `b4659cd..252fa72`. The semantic craft-vs-repository test
  ("could this be true and useful in a repository you have never seen?") lives in exactly one
  place — `.claude/skills/harness-distill/SKILL.md:49` — verified by grep across all six files
  the dispatch named as candidates for drift (distill, curate, SPEC.md, README.md, the hook, the
  checker). The other five carry only budget numbers or mechanical path classification, not the
  test itself. Matches my own P-01 pattern (governing constraint must live where the reader
  actually opens it) in the positive direction for once — worth remembering as a clean example
  the next time I'm asked to judge "is there one authority."
- 2026-08-19: `inject-expertise.sh`'s repository-tier injection globs every `.harness/*/expertise/<agent>.md`
  present and relies on a single prose sentence (the precedence line's segment caveat) for the
  agent to discount a labelled block from a repository it wasn't dispatched against. Confirmed via
  `notes/research-FEAT-27-expertise-tier.md:115-117` that this is a known, already-flagged gap
  (D-01): the hook has no per-dispatch segment input this cycle (`agent_type` is all it gets;
  `fleet.yaml`/`harness.json` are no-touch this cycle), so filtering to the relevant segment is a
  real deeper fix blocked on a different unit, not a same-cycle omission.
