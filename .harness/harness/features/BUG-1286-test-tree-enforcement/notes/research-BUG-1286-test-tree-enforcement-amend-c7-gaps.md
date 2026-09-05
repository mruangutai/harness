# Amendment — cycle-7 goal-check gaps 1 and 2 applied

**BLUF — both surviving gaps are closed in the plan text and measured. Case 11's positive control is
now DERIVED from the live matcher instead of asserting `.harness/tools/test_dir/gen.py` by name, so
the legitimate narrowing that made it RED now re-selects a subject and stays GREEN; the three-kind
blast radius is disclosed in the BRIEF, in T-01's remedy list and in T-05's DEC-213 bullets. Case 11
survives repaired — both halves intact, nothing deleted, narrowed or skipped (F-07 KEEP honoured).
Approvals untouched, `panel:` byte-identical, only T-01 and T-05 changed.**

## GAP 1 — the control is no longer pinned to today's `detect`

- Tripwire paragraph replaced by a DERIVED positive control: `plan.yaml:554-588` (T-01 case 11).
  Fixed candidate corpus of LITERAL paths; only the SELECTION consults the live config. Predicate:
  outside `tests/`, `_is_test_path` True, `is_test_shaped` False, not a `DOCUMENTED_EXCEPTIONS`
  path — the un-refused clause is stated as load-bearing, with the reason (a counted-but-shaped
  plant makes the equality assert against an actual `[]`).
- Corpus spans the families: `test_*` directory component plus `*.test.*` / `*_test.*` directory
  components, plus two non-qualifying neighbours (`plan.yaml:565-574`). Spanning is asserted as
  MEASURED, and the task tells the builder to re-measure rather than argue it.
- Inapplicable branch stated: no qualifying candidate ⇒ record INAPPLICABLE with the reason through
  the file's existing reporting channel, never a `check()` failure (`plan.yaml:579-583`).
- "What a red means" sentence added (`plan.yaml:584-586`): narrowing `detect`, adding a kind or
  removing a pattern must not be able to redden it alone.
- Derivation-is-not-synthesis clause restates both existing prohibitions verbatim so they do not
  read as being in tension (`plan.yaml:575-578`).
- SC-19 restated to the derived form including the inapplicable branch: `BRIEF.md:180-191`, plus two
  new "also fails it" clauses at `BRIEF.md:215-216`. `verify:`/`evidence:` line and the REQ-09 trace
  untouched (`BRIEF.md:217`, traceability row 1 of 19).

## GAP 2 — blast radius disclosed in all three places, no behaviour changed

- `BRIEF.md:252-266` — new `## Verification gaps` bullet: the union rule, the three kinds by name
  with their measured uncertified patterns, the FEAT-44 interaction, and the consequence for the
  DEC-163 runner work. The pre-existing first bullet is unchanged and still true ("this change
  touches none of those surfaces") — the new bullet sits beside it, not against it.
- `plan.yaml:653-666` — T-01 case 11 remedy text names kind activation as a legitimate reddening
  event, with the measured numbers, so a future dev-ops engineer reads a remedy.
- `plan.yaml:894-899` — T-05's DEC-213 bullet gains one clause: the invariant is stated over the
  kinds that RUN, so activating a kind extends the obligation. No patterns re-enumerated;
  `suite_layout.py` stays the vocabulary authority (D-01).
- No task, REQ or SC added. Disclosure is the deliverable.

## Remedy list, now four-part

Widen `suite_layout.py`'s vocabulary · fix the offending `detect` pattern · record in DEC-213 why the
new **or newly removed** surface is out of scope · (the events include kind activation).
`NEVER delete, narrow, skip or weaken either half` retained verbatim (`plan.yaml:667`).

## Measurements (throwaway prototype of the AMENDED case 11, self-deleted)

Prototype implemented the planned `suite_layout` vocabulary locally (that module ships only
`violations` today) and called the REAL `code_grade._is_test_path` / `_patterns` against the real
`.harness/harness.json` and the real Git index.

| # | mutation | observed |
|---|---|---|
| a | none (live config) | **GREEN**, control subject `.harness/tools/test_dir/gen.py` |
| b | `tests/unit/**` → `tests/../evil/**` | **RED** — `uncertified unit.tests/../evil/**` |
| c | `unit.detect += **/test_*/**` | **RED** — `uncertified unit.**/test_*/**` |
| d | `unit.detect += **/*.spec.*` | **RED** — `uncertified unit.**/*.spec.*` |
| e | drop `**/test_*.py` (legitimate narrowing) | **GREEN** — subject re-selects to `.harness/tools/a.test.d/gen.py` |

Blast radius, `status` flipped to `active` one kind at a time: `component` 3 uncertified
(`**/*.spec.tsx`, `**/*.stories.tsx`, `**/*.stories.ts`); `ui` 2 (`e2e/**`, `**/*.e2e.spec.ts`);
`typecheck` 2 (`**/*.ts`, `**/*.tsx`) **and** 2 behavioural offenders —
`FEAT-44…/evidence/probe-session-accessors.ts` and `.omp/extensions/harness-hooks.ts`.

Gate re-runs from the worktree root: `plan.yaml` loads, `status: plan`, `approval: {status: pending}`
with no `rulings`; `panel:` sha256 `d7a0cadc…f77b6e` identical before and after; T-02/T-03/T-04 task
hashes identical, only T-01 and T-05 changed; `check-plan-routes.py` → `0 violation(s)`, all five
tasks carry all eleven keys; `check-state.sh` → no `INV-35` line and no violation for this feature
other than the expected unsigned BRIEF.

## Open question — an adjacent pin I did NOT touch

An EXTREME narrowing (`unit.detect := tests/unit/**` alone) leaves case 11 RED, but **not** through
the control: the control correctly records INAPPLICABLE and does not fail. The red comes from the
pre-existing `guard-covered bucket must be non-empty` clause (`plan.yaml:627-633`), which is itself
a weak property of today's config. It is out of both gaps' scope and striking it would weaken a
clause F-03/F-04 put there, so it is reported rather than applied. Non-blocking: no legitimate
narrowing short of removing every guard-covered pattern reaches it.
