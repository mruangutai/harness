# Receipt — harness-dev-ops — simplify-efficiency pass — FEAT-33

Angle: EFFICIENCY only, plan surface (`plan.yaml`, `BRIEF.md`, `notes/research-board-lifecycle.md`).
Flag-only — no edits made.

## Finding 1

- **File/line:** `plan.yaml` T-07 verify (line 427-428) and T-08 verify (line 474-475).
- **Summary:** Both tasks' `verify:` runs the whole `--kind integration` suite (14 scripts) although
  each task's `files:` list names exactly one pair, `gh-sync.py` / `test-gh-sync.py`.
- **Concrete cost, measured at this checkout (`a473c28`), read-only invocations only:**
  - `run-unit-tests.sh --kind integration` (all 14 integration scripts): **2:33 (153s)** wall,
    63.2s user / 22.3s system, exit 0.
  - `python3 .claude/skills/harness/bin/test-gh-sync.py` alone (the targeted case that binds T-07's
    and T-08's own acceptance — SC-05's #642 replay, SC-03's close-reason assertions): **1:13 (73s)**
    wall, exit 0, all cases ALL PASSED.
  - Difference: ~80s per verify invocation, so ~160s (2.7 min) across the two tasks for one pass
    each, and the same 80s again on every RED/GREEN iteration a task goes through before its verify
    goes green — the Iron Law cycle runs verify more than once per task in practice.
- **Alternative:** for T-07 and T-08 specifically, point `verify:` at
  `python3 .claude/skills/harness/bin/test-gh-sync.py` instead of the full `--kind integration`. This
  does not remove the broader suite from the pipeline — `--kind integration` (and `--kind unit`) still
  runs as the qa gate's own boundary check before ship, which is the deliberate full-suite run this
  angle is told NOT to flag. The targeted script is the file the task actually touches and already
  proves the specific SCs named.
- **Caveat, stated plainly:** every other task in this plan (T-02 through T-06) also verifies with a
  `--kind` command rather than a single script, and that may be this codebase's standing per-task
  verify convention rather than a choice made by this plan's author. If so, this finding is really
  about the convention, not about FEAT-33 specifically, and the fix belongs wherever that convention
  is set — not in this plan alone. Flagging it here regardless because T-07/T-08 are the two tasks in
  this plan with the narrowest, most exact file scope (one script each) against the most expensive
  kind (integration, not unit), making the mismatch measurable and the largest in the plan.

## Considered and rejected

- **T-02 through T-06's `--kind unit` verify** (five tasks, each re-running the same 18-script unit
  suite as it grows one script at a time). Measured: full `--kind unit` = 5.48s wall at this
  checkout. Five sequential runs cost ~27s total. This is de minimis against the plan's own dev-loop
  cost and each task's changes (`factory_config.py`, `factory_gh.py`, `board_lifecycle.py` growing
  across T-04/05/06) plausibly touch shared code paths other unit tests exercise, so a per-task
  full-unit-suite check is legitimate acceptance evidence, not waste. Not flagged.
- **T-05's five network calls per audit.** The intent text itself states the count and reuses each
  existing helper once (`gh issue list`, `board_stations`, `project_field_options`,
  `project_workflows`) rather than adding a redundant read. This is already the efficiency-conscious
  design the angle looks for; nothing to add.
- **T-07's guard reusing the single `board_stations` read for both its checks** — the plan already
  states this explicitly ("do not add a second board read"). Already efficient; not flagged.
- **T-11/T-12's repeated audit/dry-run/apply/audit-again sequence** (each ~4-5 audit-equivalent
  network-call batches). These are one-shot, human-run migration tasks producing before/after
  evidence for SC-04/SC-11, not a hot path and not a repeated build step — this is exactly the
  "deliberate full run at a boundary is not waste" case the angle names, and the plan's own T-06
  intent requires the residual re-check ("a reconcile that fixed nine of ten must not report
  success"). Not flagged.
- **T-10's `board_lifecycle.py provision`/`audit` calls added to `/harness-init`.** Runs once per
  onboarding, not at every session entry or every write — the plan itself states this in T-10's own
  intent (contrasted explicitly with `check-state.sh`, which would run "dozens of times per build").
  This is the hot-path scrutiny the angle asks for, already applied by the plan's own author. Not
  flagged.
- **`start-task`'s new one-board-read-plus-one-issue-read cost (T-07), added to a hot path
  (every `start-task` call).** Considered under EFFICIENCY's hot-path scrutiny. The two reads pull
  different objects (issue `state` vs. the project item's Status field value) that no single existing
  helper combines, so this is not a duplicate read of the same data — it is forced by the API shape,
  not a plan choice. The plan already reuses the one `board_stations` call rather than reading it
  twice. Not flagged.

## Verdict basis

One measured, concrete finding (T-07/T-08 verify scope) with an honest caveat about whether it is a
plan-specific choice or an inherited convention. Five candidates considered and explicitly rejected
with reasons. No edits made — this pass is flag-only and routes back to `harness-pm`.
