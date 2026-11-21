# BUG-2241 — pinned goal-check

PASS — all three declared perspectives are discharged; SC-01–03 are met through T-01. No findings or approval request.

Review: `64fdc2dd528b7518a88b3e3d4990de7f3b7b86f1`; base: `594af2a8123771da1a5290942400f4f8a064656f`. Source paths below refer to Git objects at these immutable pins; feature evidence paths are relative to this feature directory.

## Perspectives — one line each

- **operator — pass (SC-01):** The normative rule requires execution-fresh or parameter-supplied ids for durable named state and identifies literal single-use ids as defects because validation cannot rerun them; pinned `.claude/skills/harness-spec-driven/SKILL.md:89–91`, complete-rule inline assertion in `plan.yaml` T-01 `verify`, failing `notes/receipts/red-base.txt:1–5` and passing `notes/receipts/green.txt:1`.
- **pm (author) — pass (SC-02):** One self-contained MUST paragraph in the existing verify section names timestamp/run-counter derivation and parameter input, gives the validation-rerun reason, and covers runs, issues, branches and other named records rather than one incident; pinned `.claude/skills/harness-spec-driven/SKILL.md:82–93`.
- **code maintainer — pass (SC-03):** The pinned base-to-review source diff adds only that 44-word paragraph in the single owned skill, with no removals or changes to existing guidance, detector, runtime, UI or unrelated recipes; `git diff <base> <review> -- .claude/skills/harness-spec-driven/SKILL.md`, pinned skill `:89–91`, and `notes/receipts/green.txt:1–19` record 1181 skill words (+44 from 1137), PM preload 5045 and universal 1476, below advisory budgets 5500/1900.

## Coverage and evidence boundaries

`BRIEF.md` Done when and SC-01/02/03 map respectively to operator, pm and code maintainer; `plan.yaml` T-01 `traces` names all three. No perspective or criterion is orphaned. Other pinned changed files are feature planning, signature, state and evidence records, not additional product-source changes.

The existing red/green receipts are used as explicitly requested; no tests or weight checks were rerun. The red receipt identifies the missing-rule assertion, not an incidental execution failure. SC-01 proves guidance content, not future author compliance. No runtime enforcement or UAT outcome is claimed.

Consulted pinned product guidance through `AGENTS.md` Project map: SPEC §6 and §11.2; DEC-158 move 1, DEC-179, DEC-182 and DEC-225. The accepted main-session-direct route and explicit validation dispatch are not reopened; no planning, source or approval changes were made.

Open questions: none.
