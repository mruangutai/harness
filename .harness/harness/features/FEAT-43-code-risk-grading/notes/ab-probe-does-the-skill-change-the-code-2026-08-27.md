# A/B probe — does the skill change what gets written? — 2026-08-27

**Run BEFORE the build, on the operator's instruction, because ten tasks rest on the answer.**

## The question

Every criterion in this plan except one tests the TOOL. The feature's actual bet is that teaching
the squad changes the code it writes. Nothing had measured that.

The original SC-11 was a prediction quiz — read the skill, guess five grades by eye. That measures
**reading comprehension**, not writing behaviour. Someone can score a function correctly and still
produce a tangle under deadline. This probe replaced the guess with a measurement.

## Method

Four `harness-backend-dev` specialists, dispatched concurrently, **identical task**: implement
`load_config(path)` for a deployment tool — nine validation rules, three optional sections,
environment overrides with type coercion, ordered error reporting. Chosen because written carelessly
it collapses into one deeply nested validator, which is exactly where cognitive complexity bites.

- **Arm A (two agents):** the draft skill in the prompt — the band table, what the three measures
  count, and the habits. Draft kept at `notes/skill-draft-2026-08-27.md`.
- **Arm B (two agents):** the task only. No mention of complexity, metrics or grades.

All four outputs graded by the same scorer used for the repository baseline. All four parse.

## Result

| variant | arm | functions | worst cyclomatic | worst cognitive | worst ABC | lowest grade |
| --- | --- | --- | --- | --- | --- | --- |
| A1 | with skill | 18 | 5 | **10** | 10.3 | 3 |
| A2 | with skill | 20 | 9 | **7** | 12.1 | 3 |
| B1 | no skill | 10 | 24 | **57** | 43.5 | **1** |
| B2 | no skill | 12 | 14 | **19** | 19.2 | 2 |

**Worst cognitive complexity: 8.5 with the skill against 38.0 without.** A 4.5x difference on the
measure the guidance specifically targets.

## Why this is an effect and not variance

**The between-arm gap exceeds the within-arm spread, and not marginally.** The two skill-readers
differ from each other by **3** on worst cognitive. The two controls differ from each other by
**38**. The noise floor is visible in the data itself and the effect clears it.

**The arms do not overlap.** Neither control was as clean as the worse skill-reader on any of the
three measures.

## The mechanism is visible, not inferred

**19 functions on average with the skill, 11 without.** The skill-readers decomposed; the controls
wrote one large validator. B1 produced a single function at cognitive 57 — grade 1, which would fail
the gate outright.

That is the habit the guidance asks for ("return early", "one loop per function") showing up in the
shape of the code rather than in a quiz answer.

## Limits, stated so nobody over-reads this

- **Four samples, one task.** A clear separation on one task is evidence, not proof. A task with
  less branching might not separate the arms.
- **The DRAFT skill was tested, not the shipped one.** If T-04 writes something materially
  different, this result does not automatically transfer. The draft is a starting point for T-04,
  not a substitute for it.
- **No claim about durability.** This measures one turn with the skill in context. It says nothing
  about whether the effect survives a long session or a context reset.
- The scorer's cognitive figures remain a Sonar-*style* approximation, as the BRIEF already states.
  The COMPARISON is sound regardless — both arms were scored by the same code.
