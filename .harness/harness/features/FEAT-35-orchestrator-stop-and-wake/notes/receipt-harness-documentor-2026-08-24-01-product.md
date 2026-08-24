# Receipt — harness-documentor — FEAT-35 — 2026-08-24-01-product

**The dangling pointer now lands.** `.claude/skills/harness/SKILL.md` step 5 closes with "The
calibration behind those bands is in DEC-201"; DEC-201 now carries that calibration. Three
paragraphs appended to DEC-201 in `.harness/harness/docs/DECISIONS.md`, occupying **lines 6859-6879**
(single-hunk diff `@@ -6858,0 +6859,22 @@`), inserted before `**Lineage.**` so the
`**Branch `chore/744-...`**` closer stays last.

## What the passage carries

- **Warning line, not a budget.** Crossing is normal and expected. DEC-198 is CITED for "advises,
  never refuses" and explicitly not narrowed — no restatement, no weakening.
- **Operator calibration, 2026-08-24.** 270,000 against the 200,000 line ruled acceptable, with the
  verbatim quote *"that's okay, i expect some margin buffer"*; concern line at roughly TWICE the
  threshold.
- **The bands, as guidance.** Just over — carry on; around 2x — next seam; far past — an unfinished
  phase costs more than the handoff avoided. Written with an explicit non-enforcement clause: no
  hook reads them, no validator checks them, no gate fails on them.
- **Why they exist.** The step gave a number with no scale, so a normal overshoot was
  indistinguishable from a real problem — early handoff burns a spawn, late one loses the phase.
  All five measured figures appear unaltered: **195k, 217k, 270k, 330k** across four correct
  handoffs, and **418k** past the concern line, framed as a data point FOR the band.

## Verification

- `SKILL.md` **unmodified by this run** — read only. It appears in `git status` as `M` because the
  tree was already dirty at spawn; `git diff` shows no hunk of mine in it (my only edit is the one
  hunk above in `DECISIONS.md`).
- `DECISIONS-INDEX.md`: `python3 .claude/skills/harness/bin/gen-decisions-index.py` run (exit 0);
  **byte-identical output, no diff**. Correct: DEC-201 is the last entry (`grep '^## DEC-'` tail), so
  its `@6800` anchor and every earlier offset are unshifted. The row's summary still describes the
  DECISION, not this addition — no generator defect to report.
- DEC-158 honoured: no band, figure or quote pushed back into the rule skill.

## Open

None blocking. DEC-201's own open measurement (post-merge run to prove the rewritten playbook causes
the long-wait survival) is untouched and still recorded as open.
