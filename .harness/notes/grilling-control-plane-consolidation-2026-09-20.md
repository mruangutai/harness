# Grilling — control-plane consolidation (smell wave 1) — 2026-09-20

## Destination
Every hand-copied definition in `.claude/skills/harness/bin/` that a gate depends on — the
station lifecycle buckets, the checkout-guard predicate, the strict-JSON loader, the run-schema
navigation, the script-as-module loader — exists once, with the divergences between the former
copies enumerated, ruled and tested; the dead `gate_policy` surface and its unread config knobs
are gone; and two checks refuse re-introduction. First of three cleanup waves preceding the
smell-rule extension of `harness-code-risk-grading` (wave 2: decompose `check-state.py`'s
module-level invariants; wave 3: typed exception discipline).

## Mission
mission: plan
reason: bounded diff (~12 named files) but adds a new enforcement surface (two lock-in checks) and
changes station-predicate semantics at ten sites — rule 3 of the patch test fails.
confirmed-by: operator

## Settled
- Debt first, grader extension after → yes; a detector calibrated against a dirty baseline is
  tuned to tolerate the dirt. Each wave lands with the one cheap check that locks it in.
- Station data structure → **one table, one row per station, properties as columns**
  (`name`, has board column, lifecycle bucket ∈ {not_started, active, finished}); `MANDATED_STATIONS`,
  `TERMINAL_STATIONS`, `ACTIVE_STATIONS`, `FINISHED_STATIONS` all derived from it, existing two
  exports keep name and order. Reason, in the operator's words: the data structure carries the
  weight, leaving less logic and fewer conditions. Not an Enum — values are strings at every
  boundary and mixed comparisons fail silently.
- `is_finished(name)` / `is_active(name)` on an unknown or empty station → **raise** (strict),
  consistent with `station_column()`'s posture. Behaviour change at every migrated site; the
  fixture corpus decides whether anything leans on today's permissive `False`.
- `gates.qa_gate`, `gates.uat`, `gates.merge` policy knobs → **remove** from `load_policy`, the
  schema and `templates/harness.json` together, with `evaluate_qa`, `QaResult`, `SUITE_OUTCOMES`.
  Unread policy is dead config; a knob returns with its reader if one is ever wanted.
- `feature_checkout_guard` twins → one core predicate in `harness_boundary`, two route adapters
  keeping their own refusal channel and rationale comments. "One guard" as a literal criterion
  is unachievable; the route-specific halves are load-bearing.
- Correctness bar → NOT byte-identity-as-zero-behaviour-change. Byte-identity holds over the
  offline fixture corpus for gates that have one; the divergences between twins (sys.modules
  registration, loader failure handling, strict predicates, `load_policy` on missing keys) are
  enumerated with a ruling and a red-first test each.
- Dead-symbol sweep over all of `bin/` → **out of wave 1**; scoped to the named symbols. A
  bin-wide detector needs exemption tuning (gate `main`s are invoked as processes) and belongs in
  the grader wave against a clean baseline.
- Lock-in checks in wave 1 → **two only**: a feature-station literal outside `factory_config`
  (conceptual rule, not a word grep — task-status sets share the words) and a second
  `spec_from_file_location` on a repo-local path in `bin/`.
- Copied hook bootstrap prologue (5 files) → **accept**: cross-reference comment in each naming
  the other four; a DEC recording that no import seam exists before `sys.path` is set. No task.
- DEC-174 execution route → **this session writes the diff directly** in a worktree under
  `.claude/worktrees/`; Harness runs plan, review panel and goal-check only.

## Not yet specified
- Whether a `rejected` task completes a review. `plan-merge.py:854 _review_complete` treats only
  `{done, abandoned}` as complete; `rejected` (FEAT-1714) arrived after that set was written.
  Rule or drift is unknown; the divergence enumeration resolves it — either the site becomes
  `all(is_finished(...))` or keeps its own named predicate with the reason recorded.
- Same question for `plan-merge.py:858 _work_started` (`{building, review, done}`): a third
  bucket boundary ("has work started" = past `ready`) or a one-off.
- Whether the strict predicates surface bad data in any live `plan.yaml` under
  `.harness/harness/features/`. Answered by running the corpus, not by the operator.

## Out of scope
- `check-state.py` decomposition into per-invariant functions — wave 2; depends on this wave's
  station constants and shared loader landing first.
- The ~35 `except Exception` sites — wave 3; typed raises need stable seams.
- Grader/skill extension (param count, module-level statement count, private cross-module reach,
  dead-symbol detector, Stage 2 judgment shapes) — its own feature, against the post-wave-3 baseline.
- Any message or output improvement noticed while in the files — byte-identity over the fixture
  corpus is the bar for gates that have one.
- The 21 simpler `sys.path.insert(0, dirname(abspath(__file__)))` prologues — same reason as the
  5-file bootstrap; not a seam.

## Facts I verified (so pm does not re-derive them) — at 23d6745b
- Base vocabulary spelled once: `factory_config.py:45` MANDATED_STATIONS (6), `:51`
  TERMINAL_STATIONS (2). Tasks and features share it: `check-plan-routes.py:543
  legal_task_statuses()` and `gh-sync.py:139 STATION_VALUES` both derive MANDATED + TERMINAL.
- `("done",) + TERMINAL_STATIONS` respelled at `check-state.py:107`, `check-plan-routes.py:525`,
  `gh-sync.py:345`, `gh-sync.py:955` (documented as *task* stations), `handoff_done_when.py:277`,
  `worktree_terminal.py:416`. Active tuple `("plan","ready","building","review")` at
  `gh-sync.py:1525`, `gh_board.py:146`, `plan-merge.py:894`, `board_lifecycle.py:459`.
- Task-status sets that diverge from the buckets: `plan-merge.py:854` `{done, abandoned}`,
  `:858` `{building, review, done}`.
- `spec_from_file_location` in bin/: `check-state.py:1314`, `:2426` (the only one registering
  `sys.modules`, comment says dataclasses need it), `:2728`, `plan-merge.py:2254`, `:3405`,
  `worktree_terminal.py:44`. ~30 more in `tests/`, untouched by this wave.
- Twins: `feature_checkout_guard` `check-domain.py:682-704` / `bash-write-guard.py:796-818`
  (same regex `RE_FEATURE_ARTIFACT` at `:679`/`:793`); `_reject_duplicate_keys` + non-finite
  hook `artifact_accessors.py:23-40` / `feature_json_write.py:89-110`; run-schema
  `propertyNames` navigation `check-state.py:1383-1387` / `check-domain.py:1570-1573`.
- Dead: `gate_policy.py:92 evaluate_qa`, `:12 SUITE_OUTCOMES`, `QaResult` — callers only in
  `tests/unit/test-gate-policy.py`; `validate-digest.py:35` imports `GatePolicyError,
  evaluate_review, load_policy` only, and `:1507` is the sole `load_policy` call, `["review"]`.
  `templates/harness.json:170-171` ships `uat`/`merge` knobs nothing reads.
- `harness_boundary` regex respelling in `check-domain.py:1126-1142` is documented and justified
  (issue #1106) — not a twin; leave it.
- Grader baseline over bin/: 1342 functions; grade 1 = 30, 2 = 57, 3 = 49. `check-state.py:425-2531`
  module-level body is ungraded (grader walks FunctionDef/ClassDef only).
- No glossary entry for station/lifecycle/terminal/finished/active in `.harness/glossary.md` —
  the bucket names are new terms and BRIEF should add them.
- DEC-174 text (DECISIONS-INDEX.md:177): Harness "plans its own work but never EXECUTES changes
  to its own hooks, validators or gate scripts; the category governs."
