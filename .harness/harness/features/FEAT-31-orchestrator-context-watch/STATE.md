# STATE

## Current

- feature: FEAT-31-orchestrator-context-watch
- phase: **ship** — build complete for both lanes pending T-05/T-09; validate not yet entered
- run: `runs/t05-eng` IN FLIGHT (T-05, eng squad). Last complete: `runs/fix1-eng` PASS.
- status: in_progress
- budget: **cycles 4/10**, runs 10/20. Runs are INFORMATIONAL (INV-22); cycles are the hard bound.
- `review_sha`: **not yet pinned** — pin at panel dispatch time, never at turn start (P-02).

**BOTH GATES PASS** — `BRIEF.md:310-314` and `plan.yaml` `approval:` read `approved` / `operator` /
`2026-08-21`. Q-SIGN CLOSED (`notes/signature-reaffirmed-18-tasks.md`).

### SIXTEEN OF EIGHTEEN TASKS DONE. The operator's six landed; T-05 and T-09 are all that remain.

**All six main-session-direct tasks (DEC-174) are complete and committed** — T-04, T-10, T-12, T-14,
T-15, T-17 — across `1929774`, `47ff239`, `8329575`. **Those three commit messages are the receipts**
and carry the measurements, the deliberate divergences and three self-reported errors. Do not
re-derive what they record. Their `plan.yaml` statuses were recorded by me this run (the operator
deliberately left status alone) and sub-issues #645/#651/#653/#655/#659/#661 are closed.

- T-04 `orchestrator_context_warn_tokens: 200000` in `templates/harness.json` — verified present by
  direct read, which is what unblocks T-05 and T-09.
- T-14 INV-17's shape check RESTRUCTURED to one glob pass over `notes/handoff-*.md`. One call site,
  so no file can be double-reported by construction. 74 notes in reach, zero fail.
- T-10 an empty required SECTION now fails the shape, not only an absent heading (SC-15's automatable
  half). T-15 SC-07's POSITIONAL `agent` rule; all 393 existing entries still validate.
- T-17 `context-watch-hook.py` on the existing `PostToolUse` `Write|Edit|Bash` matcher, 20 assertions.
  T-12 `run-unit-tests.sh` cross-checks its arrays against `test_kinds.integration.detect`, 23.

### THREE LIVE MECHANICS THIS FEATURE JUST CREATED FOR ITSELF

1. **FEAT-31's `runs` exempt count is frozen at 9, so every entry from index 9 on MUST carry an
   `agent` key or `check-domain.sh` DENIES the feature.json write.** T-15's rule, first live test.
2. **`run-unit-tests.sh --check-kinds` before any commit.** A new `bin/test-*.py` must be in one of
   the two arrays AND, if integration, in `test_kinds.integration.detect`. Milliseconds, runs no test.
3. **This file is `## Current` + `## Open Questions`, nothing else, 120 lines, no history.**

### WHAT REMAINS

T-05 (backend-dev, in flight) → **T-09 must follow it, NOT run beside it**: T-09's intent requires
T-05's established answer on whether `upgrade-config.py` propagates a generic key, recorded as what
was read. Then qa gate (`gates.qa_gate: blocking`) → SIMPLIFY → pin `review_sha` → **the review
panel, requested by the operator by name** (validator-lead with code-reviewer, security-reviewer, qa;
ui-reviewer self-scopes out on a no-UI diff) → pm goal-check on all 14 SCs → close-out → briefing.
**The operator has PRE-APPROVED the ship** and authorised PR, CI and merge, so the briefing will be
acted on rather than filed.

### Premises the next cycle must not re-derive

- **Q-HOOKCTX is CLOSED** (`notes/settled-Q-HOOKCTX.md`): hook stderr reaches a running agent in
  full, as a **tool-result error string** rather than free-standing context. Settled by direct
  observation. T-17's design stands. **Do not re-raise.**
- **T-17's live firing cannot be confirmed from this branch** — hooks load from the session's
  `CLAUDE_PROJECT_DIR`, which is the main checkout, so this registration first fires after merge. The
  delivery CHANNEL is settled; this hook's own firing is not.
- **Seven backlog rows are already filed** — #663 (T-13's vacuous verify), #664 (footer scope), #665
  (`_safe_listdir` swallows OSError on a directory), #666 (absolute case-count floors are vacuous),
  #667 (`sed -i` with a variable target), #668 (`0 day(s) old`), #669 (lead force-closed with a member
  in flight). The other eight rows died. **Propose only what is NEW.**
- **Zero UI surface** — all 21 planned files are Python, shell, JSON or markdown.
- 14 SCs, SC-01..SC-11 and SC-13..SC-15 — **there is no SC-12**.
- Do NOT re-verify T-01 by its own `verify:` block — line 2 greps `no orchestrator` against a
  nonexistent dir, which a tool finding nothing ANYWHERE satisfies identically. It passed while both
  discovery defects stood (`notes/finding-discovery-depth-orchestrator.md`).
- Do NOT trust a `verify:` floor expressed as an absolute case count; verify by case NAME.
- Do NOT run `feature-worktree.py behind` from inside this worktree — `dest_for()` re-inserts the
  path and exits 3 on a tree that is fine. Run it from the PRIMARY checkout.
- SC-01's live half is DISCHARGED: tool and independent recomputation agree at current 696,472 /
  peak 696,472 / entries 669, matching `BRIEF.md:43` to the token.
- Two board cards (T-01 #642, T-02 #643) read Building though closed and done. `close-task` re-run
  twice did not move them. Documented mirror shape: never re-attempted, never a gate.
- `runs/plan3-product/digest.md` is an **incomplete stub** (IN PROGRESS, no verdict).

## Open Questions

<The channel from subagents to the user. A non-empty entry is an ACTIVE ROUTING SIGNAL: the
orchestrator asks the user, writes answers to notes/answers-<runid>.md, and re-delegates with that
path. Clear each entry when it is answered.>

- **Q-IRONLAW, non-blocking, FOR QA AND THE PANEL.** The cycle-4 fix applied code BEFORE writing its
  new assertions — a RED-first deviation the lead volunteered rather than concealed. Judged sound
  because all four mutants deliver a COUNT differential against the exact pre-fix shape,
  independently rebuilt by a second member. Carried forward, NOT waived: TDD ordering is qa's and the
  panel's to weigh, and it is on the panel's docket this run.
- **Q-WARNVERB, non-blocking, FOR THE PANEL — the sharpest open risk in the feature.** T-16's warning
  text says "this advises only; the orchestrator decides" but never says the tool call SUCCEEDED and
  needs no retry, while the harness wraps a POST exit 2 as a **"blocking error"**. Measured
  consequence: the operator's own reaction to exactly that wrapper was to UNDO the write. An
  orchestrator could retry (duplicate) or revert (loss). `check-domain.sh:698-703` already encodes
  the remedy by setting `VERB` to `OVER BUDGET (already written)`. `context-watch.py` is T-16's file
  and team-owned, so the fix is the panel's call, not the operator's edit.
