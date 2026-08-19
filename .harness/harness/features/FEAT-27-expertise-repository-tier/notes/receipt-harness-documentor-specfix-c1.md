# Receipt — harness-documentor — T-05 continuation (specfix-c1)

**SPEC.md no longer states a budget relationship the shipped hook falsifies.** Two hunks, both in
`.harness/harness/docs/SPEC.md`. Verify `DOCS-OK`, exit 0. Nothing staged or committed.

## The named defect — §5.6, third bullet

`inject-expertise.sh` applies `cap_body "$glob" 150` and `cap_body "$proj" 150` — the global and
project caps are equal, and `check-expertise.sh` classifies both as the **craft** tier with one
150-line budget. The prose claimed the global cap was the tighter one, twelve lines below its own
table reading `150 | 150 | 40`.

- **Before:** "**Global entries stay short.** They are heuristics about *how to work*, never facts
  about a codebase, and they load on every spawn in every repo — so the global cap is tighter than
  the project one."
- **After:** "**Global and project share one budget, because both are craft.** They hold heuristics
  about *how to work*, never facts about a codebase, so `bin/check-expertise.sh` classifies both as
  the craft tier and gives each 150 lines. Only the repository tier is tighter, at 40 lines — it is
  the one that carries codebase facts, and the one that multiplies: every repository segment
  present adds another block to the same spawn."

The multiplication clause is not decoration — it is the reason the repository budget is smaller, and
it is what the hook's per-segment emit loop actually does.

## The sweep — by reading, not grepping

| Site | Claim | Disposition |
|---|---|---|
| §15.5 cost residue | "Expertise caps are *entry counts*, not token counts, and entries have no length limit" | **Fixed.** `check-expertise.sh` enforces a 150/40 **line** budget and a **50-word** per-entry cap. Rewritten to name all three proxies |
| §5 **Location:** line | "Two tiers live there — craft and repository-specific — plus an uncommitted global craft file" | **Left — correct.** Two *committed* tiers; global is named separately and named as craft |
| §5.2 "one of **two tiers**, told apart by its path" | craft 150 / repository 40 | **Left — correct.** This is the classifier's own two-way split; global and project are both craft, which is exactly why their caps match |
| §5.2 precedence paragraph | "repository over project over global, by specificity" + segment caveat | **Left — correct**, matches the hook's emitted string byte-for-byte |
| §5.6 table | `150 | 150 | 40` | **Left — correct** |
| §5.6 precedence bullet | "by specificity, not by tier age or position" | **Left — correct** |
| §6, §7, §14.3, §15.4 | Expertise mentioned, no tier ranking or budget claim | **Left — nothing to correct** |

No surviving statement in the file describes a two-tier *precedence* model, ranks tiers by position,
or asserts a budget the code does not implement.

## Out of scope, real, not mine

`DEC-27` is falsified by the same code and was never struck under DEC-188. `DECISIONS.md` and
`DECISIONS-INDEX.md` are uncommitted under another flow; untouched here. This belongs on the
operator's backlog.

## Caveat on the verify

The verify is literal-only. Every one of the four defects found across T-05 and this continuation
was a **paraphrase** that passed it green. The clause proves the path forms and the precedence
string survived; it proves nothing about whether the prose is true. Only the read did that, and a
fifth paraphrase elsewhere in the file cannot be ruled out by anything mechanical.
