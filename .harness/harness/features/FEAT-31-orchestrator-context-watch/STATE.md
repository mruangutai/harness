# STATE

## Current

- feature: FEAT-31-orchestrator-context-watch
- phase: **validate** — build COMPLETE, all 18 tasks `done`, tree clean at `ed62d74`
- run: `runs/qa-validator` IN FLIGHT (the blocking qa gate). Last complete: `runs/t09-product` PASS.
- status: in_progress
- budget: **cycles 4/10**, runs 12/20. Runs INFORMATIONAL (INV-22); cycles are the hard bound.
  **No rework this session** — every run was first-pass, so cycles did not move.
- `review_sha`: **`ed62d7429d1f3e3f9321fd21885393d2ce8fd525`**, pinned for qa. **RE-PIN after SIMPLIFY
  moves the tip, before the panel** (INV-6; P-02: an inherited pin reviews a tree the work is absent
  from).

**BOTH GATES PASS** — `BRIEF.md:310-314` and `plan.yaml` `approval:` read `approved` / `operator` /
`2026-08-21`. **The operator PRE-APPROVED the ship** and authorised PR, CI and merge.

### ALL 18 TASKS DONE. Three commits this session; the parent card derived to Review.

- `0901c23` **T-05** — `upgrade-config.py` already propagates a new `budgets` key generically, so it
  was left BYTE-UNCHANGED: the task is a proof, not a change. `merge()` `:64` recursive additive; add
  branch `:79-83`, recursion `:86-87`; zero occurrences of `budgets`. 10/10 cases, the new case
  asserts the on-disk VALUE 200000 at `test-upgrade-config.py:224`.
- `5996951` **T-09** — **DEC-198** declares the leaf. `6f651f1`'s "196" was stale and my own `^### DEC-`
  grep's "194" read only the 25 AMENDMENT sub-headings, not the 195 `## DEC-N` entries. Highest entry
  is DEC-197 at `:6362`. Gaps exist (no DEC-12, no DEC-161) and must NOT be backfilled.
- `ed62d74` — the documentor's trailing receipt and observation log.

### MY OWN ERROR, ON THE RECORD: I READ A MID-FLIGHT DIGEST AS FINAL

`runs/t09-product/digest.md` said **BLOCKED** when I read it — the lead had written that while its
documentor was still in flight. **The lead then continued and rewrote the same file to PASS.** I had
already recorded BLOCKED in `feature.json` and asserted a BLOCKED run in `5996951`'s commit message.
`feature.json` is corrected to **PASS**; the commit message cannot be and stands wrong on that point.
**The rule this cost: a run digest is not evidence until its run has RETURNED.** A digest is rewritten
in place, so reading one early is reading a draft. The T-09 lead's own digest warned of exactly this
("a mid-write artifact can be rewritten in place, so reading it proves nothing") and I did it anyway.
Zero send-backs actually occurred, so cycles stay at 4.

### THE ENFORCEMENT LAYER GOVERNING THIS SESSION IS THE MAIN CHECKOUT'S, NOT THIS BRANCH'S

Hooks resolve through `CLAUDE_PROJECT_DIR` to the main checkout, so a branch that CHANGES the
enforcement layer is still governed by the OLD layer while being built. This explains two puzzles:

1. **T-15's rule is INVERTED in-session.** `runs[9]` and `runs[10]` carry `agent`. The BRANCH's
   validator confirms the rule both ways — with the key, 31 files clean at exit 0; without it, exit 1
   naming `runs[9]` and the 9-entry exemption. But the SESSION's `PostToolUse` hook REJECTS it as
   `undeclared key 'agent' at /runs/9`, because the main checkout's `feature-schema.json` predates
   T-15 with `additionalProperties: false`. **The key REQUIRED after merge is REFUSED before it.**
   KEPT — removing it breaks the branch's own validator at merge. The probe restored the file
   byte-identical.
2. **T-17's hook cannot be observed firing from here** — same mechanism. First fires after merge. The
   delivery CHANNEL is settled (`notes/settled-Q-HOOKCTX.md`); this hook's own firing is not.

The VERB is the good one: `OVER BUDGET (already written)` told me the write had landed, so I kept it.
That is exactly the remedy Q-WARNVERB asks for in `context-watch.py`.

### WHAT REMAINS

qa gate (in flight) → **SIMPLIFY** → **re-pin `review_sha`** → **the review panel, requested by the
operator by name** (validator-lead with code-reviewer, security-reviewer, qa; ui-reviewer self-scopes
out — 17 files, 4147 insertions, 13 deletions, all Python/shell/JSON/markdown, zero UI) → pm
goal-check on 14 SCs → close-out (ship-refresh + distillation, TWO dispatches in ONE message) →
briefing.

### Premises the next cycle must not re-derive

- **SIMPLIFY is mostly FLAG-ONLY.** Of `plan.yaml`'s 21 `lanes.rows`, **12 are main-session-direct** —
  including `check-domain.sh`, `check-state.sh`, `feature_schema.py`, `feature-schema.json`,
  `context-watch-hook.py`, `.claude/settings.json`, `templates/harness.json`. The last two resolve to
  **NOBODY**. The 9 team surfaces (`context-watch.py`, its three test files,
  `verify-context-watch-live.py`, `upgrade-config.py`, `.harness/harness.json`, the two docs files) are
  the only ones an apply may touch. `run-unit-tests.sh` is SPLIT by edit kind: array appends are team,
  T-12's rejection rule is main-session-direct.
- **`.gitignore:7` ignores `.harness/*/features/*/runs/**`** — ZERO run files tracked. Every digest
  path cited in the briefing is LOCAL to this worktree and never reaches the default branch. It is
  also why `git status` looked clean while `runs/t09-product/digest.md` existed.
- **Q-HOOKCTX is CLOSED** (`notes/settled-Q-HOOKCTX.md`). Do not re-raise.
- **Seven backlog rows are filed** — #663, #664, #665, #666, #667, #668, #669. The other eight died.
  **Propose only what is NEW.**
- 14 SCs, SC-01..SC-11 and SC-13..SC-15 — **there is no SC-12**. `BRIEF.md:103-207`.
- **SC-10 is `verify: uat`, SC-15 is SPLIT** (automated gate half + hand-graded behaviour half). With
  `gates.uat: blocking_when_uat_criteria_exist`, **the UAT gate IS blocking** and only the operator
  discharges it.
- Do NOT re-verify T-01 by its own `verify:` block — it passed while both discovery defects stood.
- Do NOT trust a `verify:` floor expressed as an absolute case count; verify by case NAME.
- Do NOT run `feature-worktree.py behind` from inside this worktree — run it from the PRIMARY checkout.
- Two board cards (T-01 #642, T-02 #643) read Building though closed and done; `close-task` re-run
  twice did not move them. Documented mirror shape: never re-attempted, never a gate.
- Baseline measured at `ed62d74`: `--kind unit` exit 0, 187 PASS lines, zero FAIL / MISCONFIGURED /
  KIND-DRIFT. `--check-kinds` exit 0. `check-state.sh` reports the same three violations as at session
  start — FEAT-26's unapproved BRIEF and the two INV-26 cards — none from this session.

## Open Questions

<The channel from subagents to the user. A non-empty entry is an ACTIVE ROUTING SIGNAL: the
orchestrator asks the user, writes answers to notes/answers-<runid>.md, and re-delegates with that
path. Clear each entry when it is answered.>

- **Q-WARNVERB, non-blocking, FOR THE PANEL — the sharpest open risk.** T-16's warning says "this
  advises only; the orchestrator decides" but never that the tool call SUCCEEDED and needs no retry,
  while the harness wraps a POST exit 2 as a **"blocking error"**. Measured twice: the operator undid
  a write on exactly that wrapper, and my own four `feature.json` writes each drew it. An orchestrator
  could retry (duplicate) or revert (loss). `check-domain.sh:698-703` already encodes the remedy.
  `context-watch.py` is T-16's file and team-owned, so the fix is the panel's call.
- **Q-IRONLAW, non-blocking, ON QA'S DOCKET THIS RUN.** The cycle-4 fix applied code BEFORE writing
  its assertions — volunteered, not extracted. Judged sound because four mutants deliver a COUNT
  differential against the exact pre-fix shape, independently rebuilt. Carried, NOT waived.
- **Q-STRAY, non-blocking, NEEDS THE OPERATOR'S HAND.** T-09's lead wrote a now-STALE copy of its
  digest, still claiming BLOCKED, into the MAIN CHECKOUT at
  `/Users/molchairuangutai/GitHub/harness/.harness/harness/features/FEAT-31-orchestrator-context-watch/runs/t09-product/digest.md`.
  It contradicts the real PASS. Outside my worktree, so not mine to remove.
- **Q-EXISTINGVAL, non-blocking, NEW.** No test pins that an operator's EXISTING
  `orchestrator_context_warn_tokens` survives `/harness-init --upgrade`. It rests on `merge()`'s
  contract alone, so a future merge change could overwrite a tuned threshold with the suite green.
  DEC-198 records this rather than leaving it to be discovered.
