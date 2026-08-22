# T-19 receipt — SC-09: DEC-159 corrected in place

**PASS.** DEC-159 now states the mid-flight rule and no longer claims the watchdog is only a
post-hoc audit. One entry edited in place, no strike record, no `am.N` block, no parallel rule
anywhere. Index regenerated; all eight verify counts and both extra gates hold.

## What changed

`.harness/harness/docs/DECISIONS.md` — DEC-159 only, a single diff hunk (`git diff -U1` shows
exactly one `@@` on this file, so no collateral edit to neighbouring entries). The falsified
sentence-tail was replaced by two bolded paragraphs appended to the enforcement paragraph:

- **The in-flight warning, and the metric it is not.** Names the shipped instrument
  (`context-watch-hook.py`, PostToolUse, `Write|Edit|Bash` matcher, threshold
  `budgets.orchestrator_context_warn_tokens`, DEC-198), states that the deferred nudge measured
  turns while what shipped is a context-size threshold, and states explicitly that the
  turn-count nudge **remains deferred**. States the warning advises and never refuses.
- **The mid-flight case, which the seam rule does not cover.** The SC-09 deliverable: a warned
  orchestrator determines the nearest seam and writes the state a successor needs before it ends;
  where no seam is reachable it writes a mid-phase handoff rather than continuing, same four
  sections and same cap. Hooked to the entry's existing "a mid-phase relay is the bounded escape".

`.harness/harness/docs/DECISIONS-INDEX.md` — regenerated, never hand-edited. The change is
anchor-only: normalizing every `@<line>` to `@N` in `git diff -U0` makes every changed line pair
exactly, so no row's ` :: ` text moved. Regeneration is required by the index's own contract
header at `DECISIONS-INDEX.md:1-3`, not by DEC-141 (which governs `render-map.py`).

## Verify counts — after the edit (baseline at abcba0e in parentheses)

| # | Check | Expected | Actual |
|---|---|---|---|
| 1 | `^## DEC-159 ` | exactly 1 | **1** (1) |
| 2 | `templates/HANDOFF.md` | exactly 1 | **1** (1) |
| 3 | `the watchdog remains the post-hoc audit` | exactly 0 | **0** (1) |
| 4 | `mid-flight` | >= 1 | **2** (0) |
| 5 | `context-size` | >= 1 | **1** (0) |
| 6 | `context-watch-hook.py` | >= 1 | **1** (0) |
| 7 | `turn-count` | >= 1 | **2** (1) |
| 8 | `STRUCK\|am\.[0-9]` | exactly 0 | **0** (0) |
| 9 | `test-gen-decisions-index.py` | exit 0 | **exit 0**, incl. `test_committed_index_matches_a_fresh_regeneration` |

The baseline column is a live measurement taken on the pre-edit tree, not copied from the plan:
lines 3, 4, 5, 6 each discriminate (3 was 1 and is 0; 4-6 were 0 and are non-zero), so no count
here is vacuous. Counts 4 and 7 being 2 confirms both mandated tokens survived hard wrapping
unbroken on single physical lines.

## Extra gates

- `python3 .claude/skills/harness/bin/gen-decisions-index.py` — run **unconditionally** after the
  body edit. Exit 0.
- `bash .claude/skills/harness/bin/run-unit-tests.sh --check-kinds` — **exit 0**
  ("the script arrays and test_kinds.integration.detect agree").

## Facts verified at source, not assumed

- `.claude/settings.json` PostToolUse carries matcher `Write|Edit|Bash` with
  `context-watch-hook.py` as the second hook, alongside `check-domain.sh --post`.
- `orchestrator_context_warn_tokens` is at `.harness/harness.json:169` (200000), rationale marked
  INFORMATIONAL, NOT A GATE.
- The advisory wording quoted in the entry is verbatim from `context-watch.py:411,536`
  ("this advises only; the orchestrator decides").
- `context-watch-hook.py` returns 2 only to carry stderr; its docstring records that PostToolUse
  means the tool has already run, so nothing is blocked. The entry says so and claims no gating.
- DEC-159 is not struck; `BRIEF.md:242-245` is the signed ruling that only the one clause is false.

## Not touched

No other decision entry (DEC-198 untouched), no new entry, no skill, no `plan.yaml`, `STATE.md` or
`feature.json`. The pre-existing dirty edits to `plan.yaml`, `feature.json` and
`observations/harness-pm.md` were present at spawn and are left exactly as found.

## check-state.sh — exit 1, and none of it is mine

Run before reporting, per CLAUDE.md. Three VIOLATIONs, all outside this task's surface — nothing
about `DECISIONS.md` or `DECISIONS-INDEX.md`:

- `FEAT-26-pr-linkage-recorded/BRIEF.md is NOT approved` — a different feature.
- `INV-26 FEAT-31 T-19 (issue #672)`: plan says `building`, the board card reads Backlog.
- `INV-26 FEAT-31 parent (issue #598)`: the plan derives Building, the board reads Review.

Both INV-26 violations are board-status sync, which is the orchestrator's pen (DEC-153) — I may
not move a card or edit `plan.yaml`. Flagged, not touched.

## Open questions

Q1 (non-blocking): the FEAT-31 board cards for T-19 (#672) and the parent (#598) disagree with
`plan.yaml`. The orchestrator should reconcile them when it flips T-19 to `done`.

---

## Independent audit — second dispatch of T-19, same runid, no edit made

T-19 was dispatched a second time. **The edit was already in the working tree; I made none.**
This section is an independent re-verification, not a re-do. Everything above stands, with one
correction, one out-of-scope finding, and one judgement recorded.

**Baseline re-measured at source, not inherited.** `git show HEAD:.harness/harness/docs/DECISIONS.md`
(HEAD = `abcba0e`) run through the same `awk` slice gives: heading 1, `templates/HANDOFF.md` 1,
falsified clause **1**, `mid-flight` **0**, `context-size` **0**, `context-watch-hook.py` **0**,
`turn-count` 1, `STRUCK|am.N` 0. The verify block therefore genuinely fails at HEAD on four counts,
so the working-tree state is caused by this task's edit and by nothing else. Working tree now:
1 / 1 / **0** / 2 / 1 / 1 / 2 / 0; `test-gen-decisions-index.py` exit 0 (9 ok);
`run-unit-tests.sh --check-kinds` exit 0. `git diff -U1` shows **one** hunk on `DECISIONS.md`, so
no neighbouring entry was touched.

**Every factual claim in the new prose checked against source:**

| Claim in DEC-159 | Source | Holds |
|---|---|---|
| a PostToolUse hook on the existing `Write`/`Edit`/`Bash` matcher | `.claude/settings.json` PostToolUse: that matcher, hook is the second command | yes |
| warns in the orchestrator's OWN context while it runs | hook lines 41, 53 gate on `agent_type == harness-orchestrator`; line 81 writes stderr | yes |
| threshold is `budgets.orchestrator_context_warn_tokens` | `context-watch.py:81-115` `resolve_threshold`; `.harness/harness.json:169` = 200000 | yes |
| the quoted "this advises only; the orchestrator decides" is the warning's own text | `context-watch.py:536`, inside `warn_for_agent` — the exact string the hook re-emits, since the hook holds no message text (its docstring lines 4-8; call at lines 74-81) | yes |
| exit 2 carries text and stops nothing | hook lines 10-12, 79-82 | yes |
| the turn-count nudge remains deferred | nothing under `bin/` counts an orchestrator's turns; `warn_for_agent` compares context size only | yes |

**Correction to "What changed" above.** The index change is **not** anchor-only. DEC-159's own row
gained `DEC-198` to its generated `refs:` list, because the new body cites DEC-198; its `@3945`
anchor is unchanged. Rows DEC-160 onward shifted by +18 lines. No row's hand-written text right of
` :: ` changed, and none needed to — DEC-159's ruling text stays true after this edit.

**Out of scope, flagged not fixed — DEC-159 contradicts the enforced cap.** The Enforcement
paragraph still says a handoff note is denied at more than 40 lines, but `check-domain.sh:949-952`
denies at **60**, and DEC-159's own handoff paragraph already says "~60-line cap (raised from 40 at
DEC-160)". The entry contradicts itself and the code. Pre-existing at HEAD, unrelated to SC-09, and
correcting a second clause is not T-19's grant — routing it is the orchestrator's call.

**One judgement recorded, not changed.** "What this entry deferred was a turn-count nudge" is a
self-reference to the entry's own history, which brushes against SC-09's "reads as a single current
rule". It is kept because the task intent explicitly mandates stating the deferral's standing and
requires the literal token `turn-count`, and the surrounding sentences state that standing in the
present tense ("remains deferred") — so the entry reads as one current rule, not a rule plus a
correction note. No `am.N` block, no strike record, no parallel rule.
