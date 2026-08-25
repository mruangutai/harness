# FEAT-40 — final fold of the Item-closed comment sites

**Done. Three surgical in-place edits to `plan.yaml`, no new task, no new decision.** Counts measured
after the edits: **11 tasks, 13 decisions**. `approval:` untouched, still `status: pending`. No source
file was edited — only plan task bodies.

## What changed in `plan.yaml`

1. **T-04 `depends_on: [T-01]` → `[T-01, T-03]`.** Acyclicity confirmed at HEAD before writing:
   `T-03 depends_on: []` (was `plan.yaml:221`), `T-01 depends_on: []`. Same shape as T-09's existing
   edge, same reason — the corrected `:898` comment cites DEC-203, which T-03 writes.
2. **T-04 intent gains `Step 8d`** — corrects `gh-sync.py:898`, the Plan/Done/Abandoned line of
   `cmd_status`'s STATION WRITES docstring block. Both halves named: the falsified causality
   (restated as "ship is the only writer of the done station, D-01") and the struck citation
   (`DEC-192` → **`DEC-203` by name**, with D-03 explicitly called insufficient as a durable
   pointer). States behaviour unchanged; ~2-3 lines.
3. **T-08 intent gains the two `check-state.sh` corrections**, `(a)` `:1416` and `(b)` `:1479`, with
   the DEC-174 sole-home reason recorded. `(b)` is written as a rewrite (~5-8 lines) and carries the
   explicit hard constraint that **the accept set at `:1486-1489` is not to be narrowed, widened,
   reordered or touched** — the correction is to the justification comment only.

Neither `verify:` block was modified. Both were byte-compared against the dispatch text: **match**.

## The class sweep

Searched **live code only** — `.claude/skills/harness/bin/` and `.claude/skills/harness/hooks/` —
with three passes: `grep -rniE 'item.?closed'`, `grep -rniE "native|lands? it in Done|landed it in
Done|closing .*(moves|lands)"`, and `grep -rniE "clos(e|es|ing|ed).{0,80}(Done|done station|board)"`.
Historical feature artifacts were deliberately not searched.

Sites of this class found in live code — **exactly four, all already accounted for**:

| Site | Home |
| --- | --- |
| `gh-sync.py:219-220` `_apply_parent_rule` | already fully specified as T-04 **Step 8b** (`plan.yaml:527`) — pre-existing, unchanged by me |
| `gh-sync.py:851` `cmd_close_task` | **already fully specified as T-04 Step 8c** — see below |
| `gh-sync.py:898` `cmd_status` | **new: T-04 Step 8d** |
| `check-state.sh:1416`, `:1479` | **new: T-08** |

### `gh-sync.py:851` — the reference at `plan.yaml:537` is NOT stale

It is a settled ruling, and it is complete. Step 8c reads "THERE IS NOTHING TO CORRECT HERE ANY
MORE": an earlier draft corrected this comment, the operator ruled Q8 on 2026-08-25 that
**`close-task` is deleted**, and T-11 owns the removal. T-11 step 1 says "DELETE `cmd_close_task` ...
**including its comments**", and T-11 `depends_on: [T-04, T-06]` so the two never edit the file
concurrently. **Correcting `:851` in T-04 would be work T-11 then deletes.** Changed nothing.

### Considered and deliberately excluded

- `gh-sync.py:793-795` (`cmd_start_task`) — describes a **measured past incident** on #642/#643
  (the bot moved a card to Done a second after a close). That is a record of an observation, not a
  general causality claim, and the guard's behaviour does not rest on it. Correcting it would
  falsify the record (rule 15).
- `board_lifecycle.py:139`, `:789` and the `test-*.py` occurrences — `"Item closed"` there is a
  **GitHub workflow name string** in `_REQUIRED_WORKFLOWS` and its tests, not a causality claim.
- `test-factory-gh.py`, `test-board-lifecycle.py`, `test-factory-integration.py`,
  `test-factory-decompose.py` — fixture data carrying the workflow's name.

## BRIEF — checked, no edit needed

`BRIEF.md:253-256` already records the falsification correctly under `## Corrections to the record
this feature makes`: it names DEC-138 amendment 7's D-23 reasoning as **false** and cites the
thirteen closed-at-Review sub-issues. Consistency does not require a change, so none was made.

## Gates

| Gate | Exit | Result |
| --- | --- | --- |
| `check-plan-routes.py` | **0** | `0 violation(s) across 1 plan(s)`. The DEVIATION lines are advisory DEC-174 carve-out notes, pre-existing and unchanged |
| `check-state.sh` | **1** | exactly one VIOLATION: `FEAT-40 BRIEF.md is NOT approved`. Nothing else |
| `harness_yaml.load_plan` | parsed | 11 tasks, 13 decisions, 0 dangling `depends_on`, 12/12 REQ traced |

The pre-existing note `run dir 2026-08-25-07-product exists on disk but feature.json does not record
it` is the orchestrator's run dir, not mine, and predates this edit.

## Open questions

None. Nothing here was re-opened and nothing new was raised.

---

## Cycle 2 — the fifth site, and why a phrase-shaped sweep could not see it

**Cycle 1's "exactly four live sites, no fifth" was FALSIFIED.** The fifth is
`test-gh-sync.py:1615-1617`, the comment introducing `cmd_status`'s Plan/Done/Abandoned loop. It is
the same class on both halves — the falsified causality ("Done is GitHub's own workflow") and the
struck citation (`D-03/DEC-192`, struck by T-03) — but it is a **paraphrase** of `gh-sync.py:898`,
not a copy: it carries no `Item`, no `closed`, no `native`, so all three cycle-1 patterns correctly
returned nothing. **Lesson: sweep the CLAIM, not the phrase.** A comment can assert the falsified
causality in words that share no token with any other site.

**Fold: T-04 Step 8e** — inserted immediately before Step 9. Confirmed before writing, at
`4571bda`:

- **Unowned.** `grep` of `plan.yaml` for `1615`, `1617` and `status Plan, Done and Abandoned`
  returned nothing.
- **T-04 is the right home.** `test-gh-sync.py` is already in T-04's `files:`. No new task.
- **T-11 does not absorb it.** T-11's `test-gh-sync.py` scope is the six close-task blocks
  (`:601-612`, `:1411-1438`, `:1440-1457`, `:1459-1476`, `:1481-1495`, `:1497-1525`) plus the
  header comment at `:5`. Line 1615 falls outside every one of them.

Step 8e mirrors Step 8d: re-derive the anchor, correct both halves, and **require `DEC-203` by
name** (D-03 is plan-local and stops resolving at merge). It states explicitly that the edit is
comment-only, that the assertions at `:1630-1632` (exit 0, no `item-edit` for the three statuses,
`feature.json` status recorded) are unchanged and stay true, and that T-04's `verify:` is therefore
untouched. `depends_on` stays `[T-01, T-03]`; still **11 tasks, 13 decisions**; `approval:` still
`pending`.

## Second sweep — claim-shaped. NO SIXTH SITE.

Scope again `.claude/skills/harness/bin/` and `.claude/skills/harness/hooks/`, case-insensitive:
`GitHub'?s own`, `GitHub'?s native`, `native.{0,40}(workflow|Done)`,
`built-?in .{0,40}(workflow|Done)`, `(Done|done station).{0,60}(automatic|automation|workflow|GitHub)`,
`(GitHub|board).{0,60}(moves|lands|puts).{0,30}Done`, `Item closed`, `Item-closed`,
`clos(e|es|ed|ing).{0,120}(Done|done station)`, `(Done|done station).{0,120}clos(e|es|ed|ing)`,
`never writes.{0,60}(Done|column)`, `no station`.

Every hit resolves to one of the five known sites (`gh-sync.py:219`, `:851`, `:898`,
`test-gh-sync.py:1615`, `check-state.sh:1416`/`:1479`) or to noise judged and excluded:

| Hit | Judgement |
| --- | --- |
| `test-gh-sync.py:1440-1441` | close-task's terminal-exemption comment, cites D-03/D-04 not DEC-192, asserts no GitHub-side causality. Owned by **T-11 step 4(c)**, which retargets the whole block |
| `test-board-lifecycle.py:876` | names the audit case's own subject ("a closed board issue off the done station") — no causality claim |
| `test-factory-integration.py:1489` | D-22's no-Done-exemption note, correct as written |
| `board_lifecycle.py` / fixture `"Item closed"`, `ITEM-CLOSED` | workflow-name strings and item ids, unchanged from cycle 1 |
| `gh-sync.py:793-795` | measured incident record; excluded under rule 15, unchanged |

**The absence is bounded to those two directories and those twelve patterns.** Historical feature
artifacts, `references/`, `docs/` and `.claude/commands/` were not swept in either cycle — T-09
owns the reference doc separately.

## Gates, re-run at 4571bda after the Step 8e insert

| Gate | Exit | Result |
| --- | --- | --- |
| `check-plan-routes.py` | **0** | `0 violation(s) across 1 plan(s)`; DEVIATION lines are the pre-existing advisory DEC-174 notes |
| `check-state.sh` | **1** | exactly one VIOLATION: `FEAT-40 BRIEF.md is NOT approved` |
| `harness_yaml.load_plan` | parsed | 11 tasks, 13 decisions, 12/12 REQ traced, 0 dangling `depends_on`, `approval.status: pending` |

HEAD unmoved at `4571bda`; nothing committed.
