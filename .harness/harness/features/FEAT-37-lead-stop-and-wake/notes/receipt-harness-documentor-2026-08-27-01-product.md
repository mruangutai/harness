# Receipt — harness-documentor — FEAT-37 T-05

**T05_PASS.** `indexdiff=0 coverage=0`; all three coverage cases green
(`case_index_row`, `case_entry_heading`, `case_entry_scope`).

## What changed

- `.harness/harness/docs/DECISIONS.md` — DEC-201 widened **in place**, one voice, present tense.
  Bounds re-derived by text: level-two heading `## DEC-201 …` to the next level-two `## DEC-202 …`
  (6968 → 7063 before the edit). No amendment heading, marker, dated note or changelog sentence
  (D-09); `grep -ciE '^\+.*(amendment|previously|corrected|2026-)'` over my own diff returns 0.
  - Heading now reads *"Neither an orchestrator nor a lead ever waits…"*.
  - Scope sentence carrying both a lead word and a turn-ending phrase: *"A lead that has dispatched
    a member ends its turn, and the member's completion is what wakes it"*.
  - Added, per the intent's SURVIVES list: the two-moves mechanism clause (issue 831 as a bare
    pointer), the explicit override of the platform dispatch-result text, the inoculation clause,
    the single-file home of the lead-tier rule, and the no-message-tool ruling (issues 610, 552).
  - Nothing on the CUT list was written: no transcript id, cycle/minute counts, sidecar range,
    observation date, stop-hook ruling-out, `8fc87f8` gap grep, or "not re-measured" disclaimer.
  - Existing orchestrator evidence untouched and not restated.
- `.harness/harness/docs/DECISIONS-INDEX.md` — row 219. Hand-written half right of `::` rewritten by
  hand to name both tiers, 28 words (cap 30), then the file regenerated with
  `gen-decisions-index.py`. `--stdout | diff` against the committed index is clean.

DEC-198 and DEC-199 were not touched — the DECISIONS.md diff is three hunks, all inside 6968–6999.

## Claims I altered rather than transcribe

The intent's clause *"appears nowhere under `.claude/`, `.harness/` or `docs/`"* about the platform
nudge text is false at this sha: `grep -rniE "continue other work"` matches
`.claude/skills/harness-team/SKILL.md:119` (the rule quoting and denying it), the guard test, the
BRIEF and `plan.yaml`. I wrote the true form of the same point instead — *"platform-supplied, with
no file the harness can edit to change it"* — which carries the constraint without a falsifiable
grep claim.

## Notes for whoever runs next

- `test-lead-stop-and-wake.py --check-kinds` is **not a flag of that script**: argparse rejects it
  with rc=2 and a usage line (`--self-check | --group {playbook,bound,coverage}`). The dispatch
  expected exit 0 from it. `--self-check` does exit 0.
- `--group bound`'s three DECISIONS.md failures are T-06's and were left alone.
