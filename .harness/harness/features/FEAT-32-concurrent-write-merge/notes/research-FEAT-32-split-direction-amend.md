# FEAT-32 — plan amend: entry split direction, limb B counter-example, Q5 limitation

All measurements taken in the worktree
`/Users/molchairuangutai/GitHub/harness/.claude/worktrees/harness/FEAT-32` at **1e73248**
(tree clean of my own edits at start). Only `plan.yaml` was written.

## BLUF

The defect reproduces exactly as the operator measured, and the fix landed. Splitting a
`main_session.writes` entry on the LAST space silences the two markdown-heading entries entirely
(tail `Approval` fails both fragment tests) **and** corrupts their glob to one ending `BRIEF.md ##`
that matches no path — 1 denying entry of 4 instead of 3. Both sites now say FIRST space, and the
intent carries the measurement as the reason.

## Item 1 — the split (fixed)

Command: `python3` over `yaml.safe_load(".harness/team-config.yaml")["main_session"]["writes"]`
(3 entries at 1e73248) plus the fourth entry T-15 adds, applying the plan's own fragment test.

| entry | rsplit LAST | split FIRST |
|---|---|---|
| `…/BRIEF.md ## Approval` | tail `Approval` → no fragment, glob corrupted to `…/BRIEF.md ##` | MD-HEADING `## Approval` |
| `…/PLAN.md ## Approval` | same | MD-HEADING `## Approval` |
| `.harness/logs/**` | no space → no fragment (by design) | same |
| `…/plan.yaml approval:` | MAPPING-KEY | MAPPING-KEY |
| **denying** | **1 of 4** | **3 of 4** |

Fixed at T-14 intent (now `plan.yaml:1734`, with the measurement at `:1738-1758`) and at T-15's
verify (now `:2035`, `split(" ", 1)`). The T-15 assertion's outcome is unchanged either way — those
entries hold a single space — so the fix there is consistency, not behaviour.

Other direction-restating sites: **only three exist in the file.** D-10 at `:289-290` states no
direction (`a glob plus an OPTIONAL trailing FRAGMENT, space-separated, and the fragment decides the
comparison`) — direction-neutral, not stale, not edited. Decision count unchanged.

## F-1 — the coverage paragraph was DRIFT-falsified, and is corrected

`grep -cE '^ {11}status:'` over this plan: **1 at 6bb7d82** (line 647, prose inside T-06's intent),
**0 at 1e73248** — the line reflowed. So the "EXACTLY TWO" claim was true when written and is false
now. Re-anchored to 1e73248 with **EXACTLY ONE** other-indent hit
(`FEAT-14-feature-json-schema/plan.yaml:1154`, ten spaces, prose). Every other number in that
paragraph reproduces at 1e73248: 23 tracked `*plan.yaml`, exactly one two-space `status:` each, 22
with `approval:` immediately above, the template hit at line 27, task keys at four spaces 1–17 per
file. The paragraph now says the earlier number was drift, so the anchor discipline is visible.

## Item 2 — limb B's counter-example (added, rule untouched)

`git ls-files '*/PLAN.md'` → 9 files; 9 lines match `^## Approval`; the signature's own `status:`
also sits at **zero** indent (10 such lines, the extra being FEAT-06's re-signature block), while
**27** lines across **5** files carry a task `status:` at **two** spaces (FEAT-06 10, FEAT-07 10,
FEAT-09 4, FEAT-02 2, template 1). A hardcoded two-space rule there denies 27 legitimate lines and
matches zero signatures — **inverted**, not imprecise. plan.yaml runs the other way: 23 files,
`status:` indents 2×23 / 4×176 / 10×1, the single ten-space hit being prose. Recorded at
`plan.yaml:1795-1812`, immediately below limb B. Limb A and limb B rule text is byte-identical to
HEAD (verified by diff).

## Item 3 — Q5 recorded as a stated limitation (T-10, `plan.yaml:1448-1465`)

Ran `run-unit-tests.sh --kind integration` with `CLAUDE_PROJECT_DIR` at the worktree root: exit 0,
**221** lines matching `^PASS |^FAIL |ERROR` (identical to the 62f861c baseline), **218** beginning
`PASS `, **0** beginning `FAIL`, **3** containing `ERROR` (all inside test names). Of those, **16**
are script-level `^PASS test-*.py` lines covering only **14** distinct scripts:
`test-feature-worktree.py:867` and `test-expertise-merge.py:338` each print a summary line spelled
exactly like the runner's `echo "PASS $s"` (`run-unit-tests.sh:62`). **202** lines are case-level,
emitted by 3 of the 14 scripts (`test-check-plan-routes.py:82` also prints per case). So the count
tracks three scripts' case granularity, not how many tests ran. No assertion, `verify:`, threshold
or recorded number was changed; BRIEF.md SC-14 untouched.

## Open question for the operator

SC-14's shrink detector still *states* 221 as its own comparison basis. The limitation is now
recorded in the plan at the site that owns the baseline, but the criterion itself still reads as if
the number were attributable. Whether SC-14's text should say so is the operator's call — it is a
BRIEF edit and an approval reset.
