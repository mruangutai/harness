# VL-01 — the third station-argument shape the witness cannot see

**Conclusion: the gap is real and LATENT, not live. Both occurrences of the unguarded shape are
lowercase and accepted today, so nothing ships broken; closing it edits a regex that the operator
SIGNED character for character in T-05's `intent:`, which makes it a plan question, not an
orchestrator fix.** Recommendation: take it as a backlog row, or let pm fold it into a later plan
that widens the witness. It is not routed as a fix cycle, and the panel did not gate on it
(`must_fix: []`, severity med).

## What the panel found

`tests/integration/test-station-argument-spelling.py:52`'s `TOKEN_PATTERN` alternates over
`gh-sync.py status` and `board-station.py` only. It cannot see
`plan-merge.py set-feature-station --station <token>` — a THIRD command shape that T-02 and T-03
themselves added to the swept corpus. `plan-merge.py` validates that argument against
`MANDATED_STATIONS` and exits 4 on a capital, so a reintroduced capital there would be as dead as
the two this feature repaired, and would ship green.

## The measurement (orchestrator, at `ac5e24e5`, over the real swept scope)

Same glob the witness uses (`.claude/commands/*.md` + `.claude/skills/**/*.md`, 37 files),
whitespace collapsed:

| file | shape | argument |
|---|---|---|
| `.claude/skills/harness/SKILL.md` | `set-feature-station --station` | `building` |
| `.claude/skills/harness/references/github-mirror.md` | `set-feature-station --station` | `building` |

Plus one placeholder, `set-task-station --file <plan.yaml> --task T-NN --station <name>` in
`SKILL.md`, which the witness's own character class already excludes correctly (a leading `<` cannot
match). **Zero offenders.** Widening the pattern would therefore add exactly 2 occurrences and 0
failures, and `MIN_OCCURRENCES` would move 6 -> 8.

## Why it is not fixed here

T-05's signed `intent:` spells the pattern verbatim:
`re.compile(r"(gh-sync\.py status|board-station\.py) \S+ ([A-Za-z_][A-Za-z_-]*)")`. Editing it
inside this run would amend an approved plan without approval — the one act an orchestrator does not
take (harness SKILL.md, "Authority boundary"). REQ-05's declared verification is SC-02 and SC-03,
and both PASS as scoped; what the finding exposes is that the SCs are narrower than REQ-05's plain
reading, which is a specification question for pm and the operator.

## If it is taken

One alternation plus one entry in the tool->accepted-set mapping (`plan-merge.py` accepts
`MANDATED_STATIONS`, with NO terminal marker), and `MIN_OCCURRENCES` 6 -> 8. Measured cost: one file,
no production code, no schema.
