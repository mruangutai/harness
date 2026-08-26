# Research — FEAT-41 — cycle 3 narrow repair (R-01, SC-02, Q1, Q2)

**Conclusion.** All four items are closed in plan text. R-01 took remedy (a) — the widening becomes
the lowercase literals — because (b) is foreclosed by `project()`'s own return contract, and because
the widening is not the kind of thing `project()` answers. Nothing was re-planned: 13 tasks,
12 `main-session-direct` + 1 `team`, unchanged. `check-plan-routes.py` exits 0.

## R-01 — confirmed at source, remedy (a)

`grep -n "_st26" .claude/skills/harness/bin/check-state.sh` at `ee66ae2` returns exactly four lines:
`1403` (definition), `1404`, `1405` (`_EXPECT`), `1501`. Line `1501` is
`_accept |= {_st26["review"], _st26["building"]}` and is the only use outside the definition; it sits
outside the `1495-1500` span T-06 described as unchanged. The reviewer's finding is correct.

**(b) is foreclosed, verified against the plan's own contract.** `project`'s docstring at
`plan.yaml:441-464` is `Return {issue number: lowercase station}` — one station per card. The five
gh-sync decision points (`plan.yaml:489-500`: `cmd_start_task`, `cmd_status`, the parent rule,
`_to_backlog`, `cmd_ship`'s done pass) consume that single value, and T-06's own count verify pins
`gh_board.set_station(` at four call sites tree-wide. An accept-set return breaks each of them or
forces a second function — outside #845's seven items.

**(a)'s objection does not survive the discriminator the reviewer itself supplied.** Two independent
reasons, both recorded in the plan text so the executor can re-derive them:

1. *It is not duplication.* After T-01 a station's key and its name are the same word, so a lookup
   can only return the literal it was indexed by — zero information. What `_st26` carried was a
   status-to-**column** mapping between two vocabularies, and that mapping is exactly what moved into
   `project` and `station_column`. SC-02 grades CAPITALISED literals; these are lowercase, which
   SC-01 makes the declared vocabulary itself.
2. *It is not `project()`'s question.* The widening is a phase-scoped tolerance — which observed
   stations are acceptable while the feature sits at Review — not a placement rule.

**Importing from `factory_config` was considered and declined.** `_fc26` is already in scope
(`check-state.sh:1336-1349`), but `station_names` returns the six as an ordered tuple; selecting
`review` and `building` out of it still spells both words, adding an indirection that checks nothing.

**Third address named.** T-06's deletion bullet now names `1403-1405` *and* `1501`, with the
NameError and the `v.T22a-d` reds spelled out, and instructs the executor to leave the
`_fj["status"] == "Review"` guard on the line above alone (T-07 repoints it).

## Verify-grep extension — accepted

`plan.yaml:434` greps only `_EXPECT`, so "delete `_EXPECT`, keep `_st26`" passed while `:1501` still
worked — the plan asserted a deletion no gate measured. Extended to
`grep -n "_EXPECT\|_st26" ... ; test $? -eq 1`, matching F-03's both-names precedent (eng digest :92).
One line changed; every other verify line byte-identical.

## SC-02 — re-measured, both numbers were wrong

Command run at `ee66ae2` in this worktree:

```
grep -rnE "[\"'](Backlog|Plan|Ready|Building|Review|Done)[\"']" \
  .claude/skills/harness/bin/*.py .claude/skills/harness/bin/*.sh | grep -v "/test-"
```

**27 lines across 5 files** — `check-state.sh` 11, `gh-sync.py` 9, `board_lifecycle.py` 3,
`check-plan-routes.py` 3, `worktree_terminal.py` 1. Sums to 27.

Both prior figures were hand-carried: the total (26) and the split (13/7) were each wrong, and F-06's
31 with `gh-sync.py` at 11 was wrong too. BRIEF now carries the output's numbers and says so.

## Q1 — a missing top-level status is LEGAL

T-09's shape rule now reads "every task status, and the top-level status WHEN PRESENT". Stated, not
inferred, with the reason: T-07 adds the key and is not a dependency of T-09 (`depends_on:
[T-03, T-04, T-05, T-08]`), so a required-key rule would flag every un-migrated plan the sweep meets.
Matches `check-plan-routes.py`'s "when present" at `plan.yaml:321-322`. An absent *task* status is
legal for the same reason (T-04 keeps `status` out of `REQUIRED_TASK_FIELDS`). One test case added:
a plan with no top-level status is not reported.

## Q2 — the deferral gets an instrument: PB-01

New `## Proposed backlog` section in BRIEF.md, above `## Approval`. **PB-01 — case selection for
`run-unit-tests.sh`**: recovers ~150 s of the ~298 s, deferred because it edits the test harness
whose KIND CROSS-CHECK T-08 and T-13 already touch. Proposed only — the main session opens it as an
issue at ship acceptance. T-10's intent now cites PB-01 instead of "belongs in the backlog", and says
the 298 s is accepted, not permanent. No GitHub issue was opened.

## Open questions

- **Q3 (not mine to fix).** `check-state.sh` reports run dir `2026-08-25-03-product` on disk but not
  recorded in `feature.json`. `feature.json` is outside my writable domain; the orchestrator must
  reconcile it.

## State at handoff

`check-state.sh` exit 1, with three FEAT-41-relevant violations, all pre-existing and none introduced
here: BRIEF not approved (correct — I never sign), `review_sha` not pinned (orchestrator's), and the
live INV-26 FEAT-40 violation that T-10 exists to close.

---

# Cycle 2 addendum — the fourth address (`:1432`), and the shape closed by name

**Conclusion.** Both halves done. `check-state.sh:1432` is now a **rewrite**, not a deletion, and
T-06's deletion is stated **by name** for both identifiers with line numbers demoted to non-binding
orientation. `test-check-state.py:1655/:1669` need nothing: both sit **inside** T-11's deletion
extent. Task counts unchanged (13 / 12 `main-session-direct` / 1 `team`); both approvals still
`pending`; `check-plan-routes.py` exits 0 with 0 violations.

## The occurrence count, measured at `ee66ae2` in this worktree

`grep -n "_EXPECT\|_st26" .claude/skills/harness/bin/check-state.sh` → **6 lines**:
`_st26` on 4 (1403, 1404, 1405, 1501), `_EXPECT` on 3 (1404, 1432, 1475), line 1404 carrying both.
The reviewer's enumeration is exact. `:1432` was addressed by nothing.

## `:1432` — what changes and what the lesson is

The comment paragraph opens at `:1430` with "A None derivation silences the PARENT claim ONLY".
Only the identifier clause changes:

- was: `since _EXPECT maps each task's status on its own`
- now: `since project places each task's card from that task's own status`

Everything else stays: the None-silences-the-parent-claim-only rule, the exact cost (one task
`done` and the rest `pending` derives `None`, so the mis-columned `done` card SC-05 names went
unreported), and the lesson that **every INV-26 fixture was single-task so the suite could not see
it**. That is the load-bearing record, preserved under PRINCIPLES rule 15 — the weakest edit that
removes the token. It now names `project`'s per-task placement, which is what replaced `_EXPECT`'s
per-task mapping.

## The by-name form — adopted, and why it ends the shape

T-06's first D-11 bullet is rewritten: after the task, **neither identifier may appear anywhere in
`check-state.sh` — definitions, uses and comments alike**, which is precisely what the last verify
line already asserts. The verify is therefore the address; the four line spans are demoted to
orientation and the executor is told to re-derive them. The measured count 6 is written into the
intent with the instruction: if your own grep returns a different number, dispose of every line it
reports, not only these four dispositions. A fifth surviving occurrence can no longer be missed by
reading the intent, because the intent no longer enumerates the address — it enumerates the
property. Same re-anchoring F-03 and T-11 already carry.

## `test-check-state.py:1655` / `:1669` — nothing to do, confirmed

- `:1655` is the **first line** of T-11's named opening anchor:
  `# --- ONE CASE PER KEY, AND THAT IS THE POINT.`
- `:1669` (`# backlog: a MIXED plan …`) sits between the `_no_finding` helper and the first
  `board_override=_renamed` block — inside the unit.

T-11's extent runs from that opening comment through the third `results.append` labelled
`… for status: done`, so **both comments are deleted with the unit** and neither can go stale. They
are the only two `_EXPECT` mentions in the file (`grep -c "_EXPECT"` = 2). No scope widened.

## Constraints held

Seven items of #845 unchanged — no task added, removed or re-scoped. T-06 stays
`execution_mode: main-session-direct` (DEC-174). Real YAML, no markdown in any value, `verify:` a
literal block; **no verify line changed in this cycle** — `:434`'s `_EXPECT\|_st26` extension from
cycle 1 is the only one ever touched. `approval: pending` in `plan.yaml:6` and `BRIEF.md:174`.

## Open questions carried forward

- **Q3** (unchanged, not mine): `feature.json` does not record the on-disk run dir
  `2026-08-25-03-product`. Outside my writable domain; the orchestrator reconciles it.
