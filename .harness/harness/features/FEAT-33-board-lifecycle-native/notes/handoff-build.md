# FEAT-33 build seam — 22 tasks, five live board runs, and what the tests could not see

## Next
The validation panel is run and its must-fixes are in fix cycle c1. What remains after that:
pm's goal-check against SC-01..SC-20, then the PR carrying `Closes #675`, `Closes #673`,
`Closes #674`.

Three things this build leaves open, all filed:
- **#783** — `audit`'s STATUS class ignored `--repo`. Fixed here; the ticket holds the analysis.
- **#782** — `retitle` refuses a ticket with no milestone but trusts one naming a non-existent
  feature, writing a confidently wrong title nothing re-checks.
- **#779** — `provision` needs a field's node id and type; no public primitive returns either.
- **SC-11 is deliberately `not_met`.** It is the operator's own run against board 2.

## Trust
- `run-unit-tests.sh --kind all`: **46 scripts PASS, 801 individual PASS lines, 0 FAIL, exit 0** —
  measured independently three times (builder, main session, both qa seats).
- Task counts, parsed rather than grepped: `api 1, bugfix 3, config 6, docs 4, feature 5,
  logic 3` = 22. The main session's grep said 27 and was wrong.
- **Board 3: 13 findings -> 2**, both operator-accepted. **Board 2: 29 -> 0.** 218 titles
  backfilled, 0 refused.
- **The best evidence was not a test.** Closing #85 and #98 made GitHub's native `Item closed`
  workflow move both cards to `Done` unaided in under 20s, the harness writing nothing.

## Dead ends
- **A matcher whose SHAPE cannot reach the thing it seeks is the defect.** Eleven instances in
  three days. Only an **absence** assertion turns it into a false green. Three were the main
  session's own: a `grep -c` counting `change_type:` inside `intent:` prose, a refusal count
  matching the word "refuse" inside ticket titles, and a `$?` read through a pipe returning
  `head`'s status.
- **#783 is that shape's worst case.** Nine mutation-proved assertions missed it because **no
  fixture audited a repo whose features were not the ones on disk** — and board 3 cannot expose
  it, since there they ARE the audited repo. The guard cost more than the fix.
- **Scoping STATUS by a recorded repo was INVENTED, not available** — no `feature.json` carries
  a `github.repo` field, and a served repo's config is read remotely. The fix self-skips.
- **SIX of this plan's own `verify:` clauses were broken.** Two named flags that do not exist
  (`--check`, `--dry-run`), one a key path the file has never carried, one an unreachable target,
  and **two grepped a report the same session writes** — satisfied by typing a string. All six are
  corrected in `plan.yaml` with the reason inline. On this feature a passing `verify:` is weak
  evidence.
- **I broke D-23 twenty-two times in the same build that documented it.** T-14 wrote "close-task
  is no longer run per commit"; I then ran `close-task` after every task, leaving 22 sub-issues
  CLOSED at `Review`. Nothing detected it but the audit this feature built. Reopened on the
  operator's ruling.
- **A live mutation must never exit with a code meaning "nothing mutated."** `provision` could
  create a board, fail the link, exit 2 and duplicate on retry; `retitle`'s loop contradicted its
  own docstring. Both found by the panel because **no test injected a failure there** — the cause,
  not just the defect.

## Working set
- `.claude/skills/harness/bin/board_lifecycle.py` — `provision`, `audit`, `reconcile`, `retitle`,
  `_missing_options`, `_field_probe`, the `#783` self-skip.
- `factory_gh.py` — six primitives; `project_single_select_extend` REPLACES an option set.
- `gh-sync.py` — T-07's fail-open guard, T-08's `--reason completed` and `abandoned` label,
  T-13's `status` subcommand, T-16's title format.
- `check-state.sh` — INV-26 widened, bounded on `feature.json` status `Review` (T-22, carve-out).
- `factory_config.py` `_STATION_KEYS` at six; `SKILL.md`, `commands/harness-plan.md`,
  `harness-init/SKILL.md`, `templates/harness.json`.
- `DECISIONS.md` — DEC-196 am.3 and am.4.
- `notes/migration-harness.md`, `retitle-harness.md`, `migration-kaya-ai.md` — live captures.
