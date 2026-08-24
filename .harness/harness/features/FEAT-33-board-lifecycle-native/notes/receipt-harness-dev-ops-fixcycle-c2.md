# Fix cycle c2 — provision creates the Status field in the SAME run (SC-01)

BLUF: SC-01 was right and T-04's two-run flow was the defect. `cmd_provision`'s no-project branch
now creates the project, links the repo, AND creates the Status field with all six declared
stations before exiting 3. A field-create failure after a successful create+link exits 4 and names
the created number. `run-unit-tests.sh --kind all` exits 0, 0 FAIL lines; total `^PASS` lines
812 -> 822 (+11 new assertions, -1 inverted).

## The fix

`board_lifecycle.py:532-568` (post-fix line numbers). After `project_link_repository` succeeds:

- `factory_gh.project_single_select_create(created["id"], field, declared)` — every input was
  already in hand at that point. `created["id"]` is the new project's node id, which is exactly
  the first argument that primitive takes; `field` and `declared` come from the DECLARATION
  (`harness.json` `github.board`, via `_declared_stations`), never from the board number, so
  neither depends on the operator having recorded the new number. The two-run flow was a choice.
- On `GhError`: exit **4**, reusing c1's MUST-FIX 2 meaning ("a write was attempted and did not
  fully land"), never a new code. stderr names the created project's number and the field name,
  because a retry that cannot see the number re-enters the create branch and makes a SECOND board.
- `sys.exit(3)` is kept and its meaning is UNCHANGED: a new project exists and its number must be
  recorded before anything else runs. The field now already exists on it; the recording does not.
- No linkage guard and no `_field_probe` on this path, deliberately, and the comment says why: the
  project was created by this same call, so it is linked by construction (the confused-deputy shape
  the guard exists for cannot arise) and it is empty, so `field` cannot already be taken by a
  wrong-type field. Both reads would spend a call to confirm what the create establishes.

## RED proof

Method: the tests were written FIRST, against the unmodified working tree (which was HEAD, byte for
byte — `git status --porcelain` clean at start), so the RED run needed no pinning. The pinned-baseline
restore was still performed for the suite-count baseline below, and `diff -q` confirmed all three
fixed files restored byte-identical afterwards.

RED run: `python3 test-board-lifecycle.py` against HEAD -> 9 FAIL lines, all 9 new:

| assertion | reddened |
| --- | --- |
| SC-01: createProjectV2Field called exactly ONCE in the same run | yes |
| SC-01: field created on `projectId=PVT_NEW` and named Status | yes |
| SC-01: all six names over the wire BYTE FOR BYTE, declared order | yes |
| still exits 3 AFTER the field creation | yes |
| reports the field it created on stdout | yes |
| 5c: field-create failure exits 4, never 2 or 3 | yes |
| 5c: stderr names the CREATED project's number | yes |
| 5c: stderr names the field it failed to create | yes |
| 5c: the field-create was actually attempted | yes |
| 5: updateProjectV2Field is STILL never called | **NO — green on both trees** |
| 5c: create and link really did happen before the field failure | **NO — green on both trees** |

The two that did not redden are NOT discriminators for this change and are stated as such: the
first is the regression guard the dispatch asked to KEEP (extend must never run on a board whose
field was just created), the second is a precondition making 5c's exit-4 assertion non-vacuous.
Counting either as proof of this fix would be false.

The byte-for-byte assertion re-authors `factory_gh._options_literal`'s output in the test
(`_expected_options_literal`) rather than importing it, so it specifies the wire format instead of
tautologically agreeing with the renderer. It matches the logged argv, not a count.

The inverted assertion: case 5's old `"no project: never calls createProjectV2Field or
updateProjectV2Field"` asserted the defect. `createProjectV2Field` is now required;
`updateProjectV2Field` is still forbidden, in its own separate check.

## Integration case (J)

`test-factory-integration.py` case (J) forks `provision` against a COMPLETE board (project
resolves, field present, all six options), so it never enters the no-project branch and needed no
new fake-gh response — its fake already answers `createProjectV2Field` for the primitive-level
case (I). Verified by running it: exit 0, 0 FAIL, all four (J) assertions ok.

## Suite

`bash .claude/skills/harness/bin/run-unit-tests.sh --kind all`, exit code captured with
`echo "EXIT:$?"` appended to the log (never through a pipe — zsh does not carry PIPESTATUS):

| | baseline (HEAD, measured here) | after |
| --- | --- | --- |
| EXIT | 0 | 0 |
| `^FAIL` lines | 0 | 0 |
| `^PASS ` lines total | 812 | 822 |
| of which script-level (`^PASS test`) | 46 | 46 |
| `^ok ` lines | 1883 | 1883 |

Correction to the dispatch's baseline figures: 812 is the TOTAL `^PASS` count and INCLUDES the 46
script-level lines — it is not 812 assertion lines on top of 46. Measured both ways on HEAD after
reverting all three files. The +10 delta is exactly 11 added minus 1 removed.

## Files touched

- `.claude/skills/harness/bin/board_lifecycle.py` — the field creation, the exit-4 branch, a new
  `PROVISION'S EXIT CODES` paragraph in the module docstring (there was none; exit 4 now has two
  triggers), and a new `cmd_provision` docstring pointing at it.
- `.claude/skills/harness/bin/test-board-lifecycle.py` — case 5 rewritten (one assertion inverted,
  six added), new case 5c (five assertions), new `_expected_options_literal` helper.
- `.claude/skills/harness-init/SKILL.md` — the exit-code contract: `3` now says the Status field is
  created too ("one run, not two"), `4` widened from "linking FAILED" to "a follow-up write FAILED
  — either the link, or the Status field after a successful link".
- `.harness/harness/features/FEAT-33-board-lifecycle-native/notes/receipt-harness-dev-ops-fixcycle-c2.md`
  — this file.

Nothing else. `git status --porcelain` shows exactly these three modified files plus this receipt.
No commit made. `plan.yaml`, `BRIEF.md` and `feature.json` untouched — T-04's task text still
describes the two-run flow and is not mine to correct; that is an open question below.
