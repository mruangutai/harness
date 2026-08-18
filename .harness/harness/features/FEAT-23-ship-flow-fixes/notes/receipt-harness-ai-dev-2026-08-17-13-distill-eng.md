# Receipt — harness-ai-dev — FEAT-23 — distill (2026-08-17-13-distill-eng)

## What happened

`.harness/expertise/harness-ai-dev.md` did not exist (confirmed: 14 files under
`.harness/expertise/`, mine absent). Created it. Section counts before: file absent
(0/0/0/0). After: **Patterns 2/15, Gotchas 1/15, Outcomes 0/10, Open 0/5.**

`bash .claude/skills/harness/bin/check-expertise.sh .harness/expertise/harness-ai-dev.md`:

```
OK   .harness/expertise/harness-ai-dev.md
```
Exit: 0. (First pass failed — P-01 was 52 words against the 50-word cap — trimmed and
re-ran clean.)

## Accepted entries, by source

**(a) From my observations log:** none — I have no observations log on this feature
(`observations/` on FEAT-23 holds only orchestrator, pm, product-lead; my step wrote no
artifact of my own, `files_touched: []` per the segment digest).

**(b) Surfaced by the orchestrator's skim relay:**
- C1 → P-01 (procedure step vs. its own governing constraints). The relayed FACT (the two
  apply bounds missing from `harness-simplify/SKILL.md`) is now dead — I verified at the
  current tree that `:120` and `:125` carry both. Accepted only the transferable MOVE, not
  the incident: rephrased as a rule about pointer-vs-source placement, no mention of the
  simplify skill, the apply bounds, or DEC-195. Derivation (the re-verification that the
  fact had been remedied) was mine, at the orchestrator's own instruction to check rather
  than assume.
- C2 → G-01 (detector-blind de-duplication). Re-derived at source before accepting: read
  `test-check-plan-routes.py:1098-1121`'s case_20 and its docstring line on silent drift,
  confirmed the probe scans source text for a string rather than exercising behavior.
  Accepted as the general trap — collapse-behind-a-function-call defeats a text-scanning
  detector — with no reference to `board-station.py`, root-probe walk-ups, or the specific
  refactor proposal that prompted it.
- C3 → P-02 (inventory sync on a second entry point). Re-derived at source: confirmed
  `harness/SKILL.md:188-195` is six rows all `gh-sync.py`, and `board-station.py`'s call
  site lives only as prose in `harness-plan.md:10-17`. Accepted as a general rule about
  inventories of callers, with no mention of `board-station.py`, `gh-sync.py`, or DEC-196.

**(c) Self-derived from the segment digest, not in the relay:** none. All three accepted
entries trace to the orchestrator's three candidates; nothing else in the digest (Q2's
gh-bounds disclosure, Q4's harness.json double-parse, the withdrawn D-02 citation) cleared
the six-spawns bar as a durable rule independent of what was already relayed.

## Rejections

None. All three candidates were accepted, each generalized to strip feature/task/decision
identifiers per the distill skill's rule format (no `FEAT-NN`, `T-NN`, `DEC-NNN`).

## What I deliberately left out

- The dispatch's own reminder that C1's underlying FACT is dead was heeded literally: P-01
  contains no claim about `harness-simplify/SKILL.md`'s current state, so it cannot go stale
  the way a fact-shaped entry would have.
- A2's `leave` ruling itself (REUSE vs. ALTITUDE contradiction) was not entered — the
  dispatch flagged correctly that it rests partly on signed decisions (D-02, T-05 intent)
  and would be a decision restatement, not craft. Only the detector-awareness rule (G-01)
  survived that filter.
- Q2 (a squad member's gh-bounds breach, self-disclosed) and Q6 (a non-recurring
  `validate-digest.py --hook` near-miss) are harness-defect/workaround shaped per the
  dispatch's hard bound — excluded on sight, not evaluated for craft value.

## Verification run

Full unit suite (`.claude/skills/harness/bin/run-unit-tests.sh`): 106/106 checks passed,
`PASS test-factory-integration.py` as the final line; all 16 scripts in the bucket exited 0
(re-run in full to report `suite: pass` truthfully — no source was touched, only the new
Expertise file and this receipt).
