# /harness-deepen — architecture-review scan, between features

Read `.claude/commands/harness.md` and follow it with **mission: deepen** (DEC-149). The differences:

- **When:** between features only — never inside a build. If a feature is mid-build, say so and stop;
  mid-build is the wrong time to want a different architecture.
- **What happens:** the orchestrator reads `references/missions.md` and runs: scope by heat
  (`files_touched` unions of recently shipped features + git recurrence) → specialists scan their own
  surfaces in the `harness-codebase-design` vocabulary → validator-lead adversarially verifies each
  candidate → survivors land as a notes artifact, topped by ONE top recommendation.
- **Terminus:** the briefing presents the candidates; you pick. An accepted candidate enters
  `/harness-plan` as a normal feature. A rejection with a load-bearing reason is recorded as a
  `D-NN` so the next scan does not re-suggest it. Nothing proceeds unpicked.
