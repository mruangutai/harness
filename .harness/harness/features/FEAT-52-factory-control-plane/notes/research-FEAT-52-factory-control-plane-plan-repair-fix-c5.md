# Plan repair, cycle-5 findings — FEAT-52 — T-02 and T-15 intents amended

**BLUF.** All three cycle-5 defects in the cycle-4 repair are closed by exactly two
`plan-merge.py amend` calls, both exit 0. `check-plan-routes.py` reports `0 violation(s) across
1 plan(s)`, exit 0. Nothing but `tasks[T-02].intent` and `tasks[T-15].intent` changed — proven by a
before/after `safe_load` diff with those two fields place-held, which came back byte-identical.

## What changed

**T-02, scope/NF-3 (low).** The FEATURE-DIRECTORY SHAPE paragraph said the unsegmented
`.harness/features/` spelling "occurs 11 times - all eleven in the templates". Now: 9, with the
per-file breakdown so the next reader re-derives rather than trusts — `templates/README.md` 5,
`STATE.md` 3, `BRIEF.md` 1, and `PLAN.md`/`DESIGN.md`/`HANDOFF.md`/`MAP.md` none — and the
measurement basis named as `.claude/skills/harness/templates/*.md` within the declared scope
(`plan.yaml:184-190`). The argument is verbatim untouched; the 36 / 31 / 4 / 1 segmented figures are
untouched.

**T-15, sne/NF-1 (med) — tokens now defined by what the plan ORDERS.** A new paragraph
(`plan.yaml:1108-1113`) states that every token is the post-change spelling T-04/T-05/T-07/T-08
order, never planning-time file text, so a later edit to those tasks moves these rows with it. Each
row carries its ordering task inline.

| Row | Token (post-change) | Ordered by |
|---|---|---|
| 1 | `.harness/harness.json` | T-04 F1 — unchanged |
| 2 | `.harness/expertise/<your-agent-name>.md` | T-04 F2 — unchanged |
| 3 | `.harness/<repo>/features/<FEAT>/notes/receipt-<your-agent-name>-<runid>.md` | **T-08 (`plan.yaml:685-688`) — CORRECTED from `.harness/harness/…`** |
| 4 | `\.(agents\|claude)/skills/harness-systematic-debugging/SKILL\.md` | T-05 step 1 — unchanged; T-05 spells `.agents`, the alternation accepts both because the symlink resolves |
| 5 | `.harness/team-config.yaml` | T-07 READS list — unchanged |
| 6 | `.harness/<repo>/features/<FEAT>/observations/<your-agent-name>.md`, `min_occurrences 2` | **T-04 F3 (`plan.yaml:425-428`) — CORRECTED; old rows 6 and 7 collapse onto this one token** |

Seven rows became six. Every row was re-checked against T-04..T-11, not only the two the panel named.

**The rows-6/7 proof is preserved by a count, not by two regexes** (`plan.yaml:1146-1157`). T-04 F3
gives both spans in `harness-expertise/SKILL.md` — the prose table row (`:16`) and the fenced
`observations-merge.py --file` line (`:37`) — the same remainder, so they can no longer be told apart
by spelling. Row 6 therefore requires **at least two** occurrences, **every one** `FEATURE_TREE`-
anchored. It fails when only one span is right, both ways: the other span deleted or unanchored →
one anchored occurrence → count branch; the other span control-plane-anchored → two occurrences →
per-occurrence branch.

**T-15, scope/NF-1 (med) — the red proof now fires both branches.** `direction_failures` gains
`min_occurrences=1` and the RED PROOF is two fixtures per row, each naming the branch it proves
(`plan.yaml:1159-1182`): FIXTURE A the wrong-anchor branch, FIXTURE B the token present but
**unanchored** — the pre-feature spelling — proving the no-occurrence branch that the fail-open
implementation would skip. FIXTURE C, row 6 only, is half-anchored: it proves the count branch fires
at one, which B (zero) cannot.

## Evidence

- `amend T-02 --expect-sha256 ff9a3dbc5cf2a0f18bce11e37623af993f594e46e5ed161ad8eb6375376c5471`
  → `AMENDED tasks:T-02.intent` / `APPLIED …/plan.yaml`, exit 0.
- `amend T-15 --expect-sha256 56407889ffc749375e8cf4c60f0eaa3ab6c2a93ba0a9af4f3a9ed4d902286f71`
  → `AMENDED tasks:T-15.intent` / `APPLIED …/plan.yaml`, exit 0.
- Post-state: `tasks 15`, `approval_present False`, `status plan`, `panel_cycle 4` — identical to
  the pre-state readout.
- Structural diff (`/tmp/feat52_snap.py`, `safe_load` → sorted JSON, T-02/T-15 `intent` place-held):
  empty diff.
- `check-plan-routes.py <plan>` → `0 violation(s) across 1 plan(s)`, `EXIT=0`. The eight `DEVIATION`
  lines are the expected DEC-174 carve-out output and do not gate.
- Grep over the whole `plan.yaml`: zero remaining
  `harness/features/<FEAT>/(observations|notes/receipt)` spellings.

## Open questions

- Q1 (non-blocking): T-15's FIXTURE A note says "One occurrence is found, so the count branch is
  satisfied" — true for rows 1-5, imprecise for row 6, where a single wrong-anchored occurrence
  fires the count branch too. The assertion (`non-empty failure list`) is correct for every row and
  FIXTURE C independently pins the count branch, so nothing is unprovable. Not corrected: the
  dispatch fixes exactly two `amend` calls.
- Q2 (non-blocking, harness): the cycle-5 `panel:` result still has no write route — `apply` exits 7
  on a differing top-level `panel:` and `amend` refuses every key but `tasks`/`decisions`. Already
  measured and routed to the operator.

## Untouched, deliberately

`panel:`, `approval:`, `BRIEF.md`, `status:`, `decisions:`, and T-01, T-03..T-14. Findings
scope/NF-2, sne/NF-2, sne/NF-3, scope/NF-4 and the seven surviving cycle-4 findings go to the
operator's batched signature review under DEC-176; 2a's rewrite does not absorb sne/NF-3 — no legal
anchor was invented for any non-feature write.
