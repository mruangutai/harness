# Expertise — harness-security-reviewer
## Patterns (max 15)
- P-01: This codebase's untrusted-input boundary is the hook payload (JSON on stdin, `.claude/skills/harness/bin/*.{py,sh}`) — but `bin/factory_*.py` is a second surface: it builds subprocess argv and GraphQL query documents from operator-config values (`fleet.yaml`) and shells to `gh`. Audit both.
- P-02: This repo's `.harness/*/expertise/harness-<agent>.md` write grants (`team-config.yaml`) are enforced by `check-domain.sh` via `harness_boundary.py:glob_to_re`, which maps bare `*` to single-segment `[^/]*` — grants span one repo segment only, never cross `/`; the agent-name field is always literal.
- P-03: `inject-expertise.sh` globs and injects every `.harness/<segment>/expertise/<agent>.md` into every spawn with no per-repo isolation (live per `test-inject-expertise.py` case2) — a signed accepted risk (`plan.yaml` D-01); only the self-referential 'harness' segment is real today, so re-check severity once a second live segment exists.
- P-04: WHEN auditing validate-digest.py binding checks (plan-review, code-review, member roll-up) DO confirm each mode calls _branch_corroboration_error or an equivalent host-only check — the corroboration boundary is host-set data (current branch, inflight_registry.feature_root), never digest text; a new mode skipping it is a classic gap in this file.
- P-05: WHEN auditing an agent-definition or doctrine change DO diff both .claude/agents/<name>.md and .omp/agents/<name>.md for byte-identical additions — this repo duplicates agent and doctrine files across both runtimes, and an asymmetry (e.g. a missing spawns: field in the .claude format) may be pre-existing, not new.
## Gotchas (max 15)
- G-01: WHEN auditing panel-finding severity handling DO diff every doctrine and agent copy of the severity vocabulary (team yaml, plan template, SKILL.md docs, the validator-lead agent file in both .claude and .omp) for byte-identical tokens — this repo declares it independently in about six places with no single source of truth.
- G-02: WHEN auditing a new consumer of validate-digest.py's _repo_root_for_feature/_feature_dir_from_artifact DO confirm it routes through _contained_feature_dir's realpath-descendant check before trusting the resolved directory — a bypass reintroduces the artifact:-path traversal this feature closed.
## Outcomes (max 10)
## Open (max 5)
