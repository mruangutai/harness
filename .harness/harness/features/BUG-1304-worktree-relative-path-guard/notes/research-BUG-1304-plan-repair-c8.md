# BUG-1304 — cycle 8 plan repair: the fourth binding ruling, applied

**All nine `required_plan_repairs` are applied, T-08 is struck, and no open operator choice
survives anywhere in `plan.yaml` or `BRIEF.md`.** Ten tasks remain listed; nine are live and T-08
is at the terminal station. `plan.yaml` loads under `yaml.safe_load`, `approval.status` is
`pending`, `panel:` is untouched, `status:` is still `plan`, and `check-plan-routes.py` exits 0
with 0 violations (its ten DEVIATION lines are the expected DEC-174 carve-out output).

## The nine repairs and where each landed

| # | Repair | Landed |
|---|---|---|
| 1 | REQ-05 scoping sentence | `BRIEF.md` REQ-05, third half — "THAT REFUSAL IS SCOPED, NOT FACTORY-WIDE"; REQ-03 untouched |
| 2 | New SC-12 | `BRIEF.md` SC-12, `verify: automated  evidence: integration`, both routes, both halves, SC-06 pre-change proof on the refusal half |
| 3 | D-10 rewrite | `plan.yaml` D-10 `choice` (the three-clause ordering) and `because` (cost at (a) scope; (a) SELECTED; (b) one line, rejected; Q1 resolved). The F2 asymmetry paragraph is byte-identical |
| 4 | T-02 intent | "unresolved operator choice" paragraph replaced by the selected ordering plus the seam shape: third parameter, `S_p`/`U`, shared containment primitive |
| 5 | T-01 unit cases | case 7 rewritten to the destination-outside-`S_p` raise (owner root included); new case 8 is the allow half. Integration cases 9/10 unchanged. `verify` needs no change — it asserts two exit codes, not counts |
| 6 | T-03 SC-12 pair | new cases 16 (allow) and 17 (refusal, routed through the helper) |
| 7 | T-05 SC-12 pair | new cases 18 (allow) and 19 (refusal, routed through the helper) |
| 8 | T-04 / T-06 | one sentence each: pass the resolved absolute destination as `claim_worktrees`' third argument; the existing catch-and-exit-2 clauses stand |
| 9 | T-07 obligation 1c | scoping sentence appended; obligation 1b's strike sentence replaced by "the retention half lands, write no conditional sentence" |

## Floors — measured, not carried over

`-ge 9` → **`-ge 10`** (T-03) and `-ge 11` → **`-ge 12`** (T-05), each restated in the intent as an
EXACT count with the refusing cases enumerated by number, so the L-04 tooth has zero slack. F5's
`grep -vc '^ *def bug1304_assert_pre_change_allows'` def-exclusion is intact in both.

## The T-08 strike — how it was executed, and the one deviation

`plan-merge.py` is **add-only and has no delete verb** (module docstring, `VERBS` table), and every
other write route to `plan.yaml` is denied. T-08 could therefore not be *deleted*. It is struck the
way this system strikes a task: `set-task-station --task T-08 --station abandoned`
(`factory_config.TERMINAL_MARKER` — gh-sync opens no sub-issue for it, and `gh-sync ship` treats
`abandoned` as terminal), with its title, intent and verify rewritten to a strike record. **There is
therefore no gap in the id sequence**; the record shows what was cut and why. Its verify is now a
falsifiable assertion that the struck work did NOT land (exit 0, checked).

Both prose references are repaired: T-09's symmetry sentence is gone along with all of its
strikeable framing (T-09 opens "IN SCOPE, AND SETTLED"), and T-10 no longer claims T-08 re-runs the
guard suites or that two tasks are strikeable.

## New: D-11

The three deliberately-unclosed defects were recorded in three different places and owned by none —
T-08's follow-up (dispatch-guard `_root_for`), F2 (`linked_worktrees` fail-open), OC-3
(`validate-digest` `live_children` horizon, previously only in `STATE.md` and the advisor notes).
D-11 records all three in one signable place with the filing obligation stated as REQUIRED.

## Also swept, beyond the nine

- **D-09** carried two live open choices the ruling closes: the backstop was written as "the PLANNED
  value … naming a different binding horizon is the operator's call" (now ratified at the existing
  `OMP_UNVERIFIED_TTL_SECONDS = 86400`, no new constant), and an "IF T-09 IS STRUCK AT SIGNATURE"
  paragraph (now "T-09 IS IN SCOPE"). The accepted residue is verbatim as recorded.
- **BRIEF SC-11** was headed "BOUND TO T-09 — if the operator strikes T-09 this criterion is struck
  with it". Now: carried by T-09, which is in scope; not conditional.

## Open questions for the tier above

1. **`panel:` still records F1 as `disposition: open_choice_at_signature`** and F1's resolution text
   still says "T-02's intent states the ordering as an unresolved operator choice" (`plan.yaml:231`,
   `:239`). Both are now false. `panel:` is the orchestrator's through `set-panel` and was left
   untouched as instructed — but a reader grepping for an open choice hits it. Suggested: F1 →
   `resolved`, `resolved_by: T-02, T-03, T-05`.
2. **T-08 is `abandoned`, not deleted** (above). If a true deletion is wanted, only a tool change can
   produce it.
