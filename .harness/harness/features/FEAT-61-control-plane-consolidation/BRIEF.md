# BRIEF — FEAT-61 control-plane consolidation

## Problem

Operators and maintainers currently encounter gate-critical rules copied across control-plane scripts. The copies have already diverged in lifecycle membership, JSON failure handling, module registration, and schema navigation, while unread gate-policy knobs still look effective; a change therefore requires auditing many sites and can silently leave a contradictory rule behind.

## Done when — by perspective

**operator** — I can rely on one authoritative definition for each gate-critical rule in this wave, with dead policy removed and gate behavior unchanged except where the signed rulings deliberately change it. A one-time planning receipt establishes that the baseline live plan corpus is clean, and strict predicates expose invalid station data thereafter.

**code maintainer** — I can change station lifecycle, checkout placement, strict JSON parsing, run-step schema navigation, or repo-local module loading in one place, and two cheap checks stop the copied forms from returning. The one accepted bootstrap duplication is explicit and justified where I will encounter it.

**reader** — I can distinguish preserved behavior from intentional divergence through fail-first evidence, and I can trace the accepted duplication, vocabulary, and direct-execution boundary to durable records.

## Success criteria

- SC-01 (operator): A fail-first integration comparison proves every migrated gate with an offline fixture corpus preserves its exit code and stdout/stderr bytes, except the separately specified strict-station, rejected-review, and missing-policy rulings.
  verify: automated        evidence: integration
- SC-02 (code maintainer): Fail-first unit cases prove one ordered station table derives `MANDATED_STATIONS`, `TERMINAL_STATIONS`, `ACTIVE_STATIONS`, and `FINISHED_STATIONS` in their required order, uses string values, and makes `is_active` and `is_finished` raise on empty or unknown names.
  verify: automated        evidence: unit
- SC-03 (operator): Fail-first integration cases prove `rejected` completes review, `abandoned` and `rejected` alone do not establish that work started, and explicit empty or unknown statuses fail loudly; the recorded one-time planning receipt proves every status in the baseline live `plan.yaml` corpus is accepted without making future live plans part of the permanent suite.
  verify: automated        evidence: integration
- SC-04 (operator): Fail-first unit and integration cases prove `review` is the sole effective gate policy: legacy `qa_gate`, `uat`, and `merge` inputs have no policy effect, while a missing or invalid `review` value still fails loudly.
  verify: automated        evidence: unit
- SC-05 (code maintainer): Fail-first integration cases prove both governed write routes consult one checkout-mismatch predicate while retaining their own exact refusal channel, rationale, ambiguous-worktree message, and absorbing unexpected-failure behavior.
  verify: automated        evidence: integration
- SC-06 (code maintainer): Fail-first unit and integration cases prove strict JSON loading, run-step schema navigation, and repo-local script loading each have one implementation; duplicate and non-finite JSON retain their public failures, malformed run-schema shapes preserve their natural errors at existing catch boundaries, and loader failures plus the one pre-exec `sys.modules` registration retain their ruled outcomes.
  verify: automated        evidence: integration
- SC-07 (code maintainer): Two AST-based checks each pass on the shipped tree and fail on a controlled mutation: one detects a feature-station literal outside `factory_config.py`, without matching task-status sets, and one detects a second repo-local `spec_from_file_location` call under `bin/`.
  verify: automated        evidence: integration
- SC-08 (reader): At the pinned `review_sha`, a reviewer can use `git show <review_sha>:` to cite all five bootstrap files, each comment naming the other four, plus the new `DECISIONS.md` entry explaining why no shared import seam exists before `sys.path` is established and the glossary entries defining `not_started`, `active`, and `finished`.
  verify: inspection

## Verification gaps

- none

## Constraints

- DEC-174 BLOCKS Harness teams from executing changes to hooks, validators, gates, and their tests, and SUPPLIES the main-session-direct route for every task in this plan; Harness performs planning, the review panel, and goal-check only.
- DEC-179 SUPPLIES plan-time route declaration; every task is explicitly `main-session-direct` rather than assigned to an engineering specialist.
- DEC-182, DEC-231, and DEC-232 SUPPLY the real-YAML plan shape, by-perspective success criteria, exact file anchors, dependency ordering, and scoped plan check.
- DEC-193 SUPPLIES the legitimate `.claude/worktrees/` checkout location used for direct execution.
- DEC-203 SUPPLIES the terminal-station rule: `abandoned` and `rejected` have no board column and represent no executable work; `done` remains the finished mandated station.
- Station boundary values remain strings, not an Enum. Existing `MANDATED_STATIONS` and `TERMINAL_STATIONS` names and order remain stable.
- The wave adds exactly two lock-in checks: the conceptual feature-station-literal check and the second repo-local `spec_from_file_location` check. It adds no bin-wide dead-symbol detector.
- The five accepted bootstrap prologues remain copied; only reciprocal cross-reference comments and the decision record are added.
- BRIEF and plan approval remain pending. Panel cycle 1 is recorded before the corrected plan returns for signature.

## Out of scope

- `check-state.py` decomposition into per-invariant functions — wave 2; depends on this wave's station constants and shared loader landing first.
- The approximately 35 `except Exception` sites — wave 3; typed raises need stable seams.
- Grader/skill extension for parameter count, module-level statement count, private cross-module reach, dead-symbol detection, and Stage 2 judgment shapes — its own feature, against the post-wave-3 baseline.
- Any message or output improvement noticed while in the files — byte identity over the fixture corpus is the bar for gates that have one.
- The 21 simpler `sys.path.insert(0, dirname(abspath(__file__)))` prologues — same reason as the five-file bootstrap; not a seam.

## Approval

status: pending
approved-by:
date:
