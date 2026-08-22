# Receipt — harness-dev-ops — SIMPLIFICATION angle — FEAT-33

Flag-only pass over `plan.yaml`, `BRIEF.md`, `notes/research-board-lifecycle.md`. No edits made
(none permitted — `plan.yaml`/`BRIEF.md` are `harness-pm`-only).

## Finding 1 — T-05's own call count contradicts its own enumeration

- **File/line:** `plan.yaml` T-05 intent, lines 349–353.
- **Summary:** The paragraph enumerates exactly four network calls for `audit` — one `gh issue
  list` (classes 3+4), one `board_stations` (class 2), one `project_field_options` (class 1), one
  `project_workflows` (class 5) — then states "Five network calls per audit" in the very next
  clause, and instructs the docstring to record that count.
- **Cost:** The task instructs writing "state that count in the module docstring so a later reader
  can see the cost" — meaning the executing agent will most likely transcribe the literal "five"
  into `board_lifecycle.py`'s docstring even though the code it writes performs four calls,
  planting a wrong cost figure at the exact place a later reader is told to trust for that number.
  A reader auditing the audit's network cost (e.g. before adding it to a hot-path check) gets a
  number one call too high, with no signal that it disagrees with the enumeration three lines
  above it.
- **Alternative:** Either drop the standalone sentence and let the docstring instruction read "the
  four network calls enumerated above", or add the fifth call this sentence apparently assumes
  (none is named). Since I re-derived the enumerated list and it only supports four, the fix is
  almost certainly changing "Five" to "Four" — but that's `harness-pm`'s edit, not mine.

## Candidates considered and rejected

- Exit-code meanings for `provision` (0/2/3) are restated in both T-04 (the implementer) and T-10
  (the `harness-init` wiring, a separate main-session-direct task with no shared context). Two
  independent dispatches with no cross-task memory reasonably each need the full meaning restated;
  this is dispatch-isolation overhead, not plan complexity to trim.
- "compared byte for byte and case sensitively (DEC-192)" appears in T-02, T-04 and T-05, each
  applied to a different piece of code the task itself writes. Same reasoning as above — not
  flagged.
- BRIEF's Contradiction 1 / D-02 / T-02 intent / T-09 intent all restate "plan is declared for
  parity, no derivation added" — each serves a different consumer (rationale, decision record,
  executing agent, doc amendment). Not flagged; this is the load-bearing kind of redundancy the
  skill's counter-rule names.
- T-10's "placed after step 7 where github.sync and github.repo are pinned" is imprecise (that pin
  actually happens in the unnumbered "GitHub Issues mirror" section between step 7 and step 8 in
  `.claude/skills/harness-init/SKILL.md`), but this is an ordering/precision issue for another
  angle (altitude/correctness), not a duplicated-fact-that-can-drift case — skipped as out of lane.
- "eight prerequisites" language T-10 says not to touch: verified live in
  `.claude/skills/harness-init/SKILL.md` lines 3, 39, 46, 47 — current and correct, not a dead
  reference.
