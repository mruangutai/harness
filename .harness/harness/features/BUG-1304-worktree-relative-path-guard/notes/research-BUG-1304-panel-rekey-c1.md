# Panel re-key — BUG-1304 plan.yaml `panel.readers` — cycle 1

**`panel.readers` now holds exactly three entries keyed by STEP name — `scope`, `should-not-exist`,
`goalcheck`. The goalcheck entry is recorded `status: skipped`, not `ran`: no evidence establishes
that a goalcheck reader ran in the recorded panel cycle.**

## What changed

One key, on two entries, plus one entry that did not exist:

| entry | was | now | rest of the entry |
|---|---|---|---|
| `reader: scope` | `reader: harness-code-reviewer` | step name | `persona`, `status: ran`, `verdict: PASS`, `deviation: none`, `findings` (`PF-976e37a61a8066731119885a2a18b1a7`), `artifact` — all verbatim |
| `reader: should-not-exist` | `reader: fable-advisor` | step name | `persona`, `status: ran`, `verdict: PASS`, `deviation`, `contract_compliance`, both `PF-` ids, `artifact: none`, `attribution_note` — all verbatim |
| `reader: goalcheck` | absent | new | `persona: harness-pm`, `status: skipped`, `verdict: none`, `findings: []`, non-empty `reason`, `artifact: notes/research-BUG-1304-goalcheck-plan-c1.md` |

## The goalcheck status, and the evidence for it — `skipped`

Re-derived, not taken on trust:

1. `notes/research-BUG-1304-goalcheck-plan-c1.md:1` — its own header reads
   `— cycle 1`, and `:16` describes this plan's `panel:` block as "present at `:8-12`, cycle 0".
   It is a plan-cycle-1 artifact, three panel cycles behind `panel.cycle: 3`.
2. `runs/2026-09-05-09-validator/state.yaml` — the run named by `panel.last_run` — records
   `steps:` with exactly two ids, `should-not-exist` (`:9`) and `scope` (`:17`). There is no
   goalcheck step.
3. `runs/2026-09-05-09-validator/digest.md:15-20` — the `## Readers` table lists those same two
   readers and no third.
4. Grep for `goalcheck|goal-check|goal_check` over the whole of `runs/`: **zero matches.** Grep for
   the note's own filename over the entire feature directory: **zero matches.** No run digest cites
   that reader or that artifact.

So the "if and only if" branch does not fire: nothing establishes a goalcheck reader ran in the
recorded cycle. `skipped` it is, with the `reason` naming exactly that gap, and the cycle-1 artifact
still cited so a later reader can find what does exist. Recording `ran` here would have been an
assumption dressed as a record.

## The write route — `apply` cannot do this; `set-panel` is the verb that can

The dispatch mandated `plan-merge.py apply --proposal -`. **It is structurally incapable of this
edit and I proved it rather than assuming it:** `panel` is not in `UNION_KEYS`
(`plan-merge.py:104`), so an existing `panel` whose proposed value differs hits the step-8 guard at
`plan-merge.py:764-774`. Run against this plan it printed
`CONFLICT: top-level key 'panel' carries two different values` and **exited 7**, writing nothing.

The edit went through `plan-merge.py set-panel --file <plan.yaml> --value-file <panel>`
(`plan-merge.py:1040`) — the same tool, the same `harness_merge.locked_update` lock, the verb the
tool provides for precisely this key, and it self-verifies by reloading and refusing unless the
panel reloads as the value supplied (`:1063`). No Edit, no Write, no redirect, no `sed` touched
plan.yaml.

## Post-write verification — read back from disk, not from the proposal

`safe_load` of the written file:

- `panel.readers` → `['scope', 'should-not-exist', 'goalcheck']`, count **3**. No fourth entry, no
  surviving persona-keyed duplicate.
- For each renamed entry, every pre-write key/value pair other than `reader` compares **equal**, and
  the key sets match exactly — no field dropped, none added.
- The three longest survivors, quoted from the **post-write** file by their opening words:
  - `deviation`: "RETURN SHAPE. This reader returned a JSON object carrying ex…"
  - `contract_compliance`: "At cycle 3 this reader returned the contract token PASS, so…"
  - `attribution_note`: "F-C3-2 and F-C3-3 are attributed to this reader by the produ…"
- Non-goals, compared **as text** block by block: `last_run`, `cycle`, `transcription_rule`,
  `cycle_2_verification`, `findings` (276 lines) and `history` (61 lines) are all **byte-identical**.
  The first differing byte in the whole file is at old line 33 — the first reader entry. The panel
  block grew 411 → 424 lines, entirely inside `readers`.
- `approval`, top-level `status`, all task `status` values, and the whole `tasks` and `decisions`
  lists compare equal pre/post. Untouched.

No finding was re-opened; no severity or disposition changed.

## Open

- The dispatch's stated single write route was wrong for this key. Any future dispatch that repairs
  a `panel` field must name `set-panel`, not `apply` — `apply` will exit 7 every time.
- I ran no checker. Whether INV-32 now passes three-for-three is the orchestrator's to measure.
