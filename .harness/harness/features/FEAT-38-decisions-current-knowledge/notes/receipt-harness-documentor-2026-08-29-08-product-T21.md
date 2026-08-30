# Receipt — T-21 claim markers — harness-documentor — 2026-08-29

**Eleven claim markers added to six feature-rewritten entries; verify exits 0 with
`examined 11 claim(s), 0 failed`.** `DECISIONS.md` 6279 → 6299 lines (11 markers + 9 blank
separators). `DECISIONS-INDEX.md` untouched — `git diff --stat` on it is empty. Nothing staged,
nothing committed, HEAD still `0a120c6`.

## The markers — DEC id, command, expected substring, why a command settles it

| DEC | command | expected | why it is settleable |
|---|---|---|---|
| 145 | `grep -F "CRAFT_LINE_BUDGET = 150" .claude/skills/harness/bin/check-expertise.sh` | `CRAFT_LINE_BUDGET = 150` | entry states a numeric budget enforced by a named script; the constant is the enforcement |
| 157 | `grep -F "\"max_total_cycles\": 10" .harness/harness.json` | `"max_total_cycles": 10` | entry states the default *lives in harness.json with value 10* — a literal in a config file |
| 181 | `grep -F "budget is 80 (DEC-181)" .claude/skills/harness/bin/check-domain.sh` | `budget is 80 (DEC-181)` | MANDATORY 1. Claims the **enforcement message**, not a line number, so it survives the gate moving inside the file or the file moving |
| 181 | `grep -c -m 81 -e "" CLAUDE.md` | `12` | MANDATORY 2. `CLAUDE.md` is within budget. See the caveat below |
| 181 | `grep -F "budget is 300" .claude/skills/harness/bin/check-domain.sh` | `budget is 300` | MANDATORY 3. Claimed against `check-domain.sh`'s own `feature.json` message, never against another decision |
| 183 | `grep -F "name: Plan-route gate" .github/workflows/tests.yml` | `name: Plan-route gate` | the promotion IS the step existing in the workflow |
| 183 | `grep -F "violation(s) across" .claude/skills/harness/bin/check-plan-routes.py` | `violation(s) across {processed} plan(s)` | the entry quotes the checker's final line as the thing the step parses for M; the f-string is that line |
| 183 | `grep -F "run-unit-tests.sh" .github/CODEOWNERS` | `run-unit-tests.sh  @mruangutai` (two spaces) | entry says CODEOWNERS covering `run-unit-tests.sh` is committed; file existence + ownership row |
| 193 | `grep -F "WORKTREES_SEGMENT = " .claude/skills/harness/bin/harness_boundary.py` | `WORKTREES_SEGMENT = ".claude/worktrees"` | one of the two legitimate locations, spelled in the one shared resolver both write routes use |
| 205 | `grep -F "ALLOWED_FIRST_TOKENS = " .claude/skills/harness/bin/check-decision-claims.py` | `ALLOWED_FIRST_TOKENS = {"git", "grep"}` | the safety boundary the entry states as part of the rule |
| 205 | `grep -F "test-check-decision-claims.py" .claude/skills/harness/bin/run-unit-tests.sh` | `test-check-decision-claims.py` | "a checker re-runs every marker in the suite" — registration is what makes that true |

**No command contains a line number.** Every anchor is a content string or a whole-file path;
`150`, `300`, `80`, `81`, `12`, `10` are budgets, a grep cap and a line COUNT, never `file:NNN`.

**Deliberately not marked.** DEC-11, 138, 142, 149, 152, 158, 171, 174, 182, 189, 194 — their
rewritten content is design judgement, lineage or measurement history. Nothing in them is settled
by a `git`/`grep` invocation without substituting an adjacent claim, which is the failure mode the
task named.

## Caveat on the `CLAUDE.md` within-budget marker — read before "fixing" it

Grep cannot express `<= 80` portably. Tested: a multiline form (`grep -zcE '^([^\n]*\n){0,80}$'`)
returns **1 for a 6279-line file under BSD grep** — a false GREEN, strictly worse than no marker.
`-P` is unavailable on BSD grep at all. So the marker pins the exact count instead, with `-m 81`
capping stdout to `0..81` so the substring `12` cannot false-green against a `12x` count that is
over budget. Consequence: the marker reds on ANY change to `CLAUDE.md`'s length, including a legal
one — that red is a prompt to re-read DEC-181, not a defect. Do not relax it to a bare
`grep -c '' CLAUDE.md :: 12`; that green-lights 120–129 lines.

`CLAUDE.md` is currently **12 lines** — an `@AGENTS.md` pointer since `d35aa81`. DEC-181's prose
discusses the file at 74–84 lines. The prose is history and reads correctly as history; flagged, not
edited (out of T-21's scope, and T-09 owns that entry's content).

## Verification

- `python3 .claude/skills/harness/bin/check-decision-claims.py` → `examined 11 claim(s), 0 failed`,
  exit 0. **Marker count 11, non-zero.**
- Checker shown rejecting: `test-check-decision-claims.py` run scoped, all cases ok, including
  `test_disallowed_first_token_is_refused_and_exits_one`.
- Full T-21 verify block, cross-checked verbatim against `plan.yaml:1434-1443`, exit **0**.
- Worktree porcelain lists `M .harness/harness/docs/DECISIONS.md`; main-checkout porcelain does not
  list it. Host defect did not fire.

## Open question for the harness owner

`run_claim`'s docstring in `check-decision-claims.py` says `ok` is False for a nonzero exit, but the
code never reads `result.returncode` — a command that exits nonzero while printing the expected
substring passes. None of the eleven markers relies on that (all exit 0), but the doc and the code
disagree, and a later fix-to-docstring would change marker semantics.
