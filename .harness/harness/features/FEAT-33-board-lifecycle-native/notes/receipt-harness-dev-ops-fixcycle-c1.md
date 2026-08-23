# Fix cycle c1 — board_lifecycle.py, three must-fix findings

BLUF: all three must-fixes are landed in `board_lifecycle.py`, each proven by a failure-injection
test that reddens against the pre-fix (HEAD) code and passes against the fix, restored
byte-identical after the RED proof. `run-unit-tests.sh --kind all` exits 0, zero FAIL lines.

## MUST-FIX 1 — the linkage guard (confused deputy)

New `_project_linked_repos(owner, number)` (board_lifecycle.py:328-380) sends this read-only
query, paginated via `repositories(first: 100, after:)`, capped at 10 pages (1000 repos) with a
`GhError` refusal on truncation:

```graphql
query($owner: String!, $number: Int!, $after: String) {
  repositoryOwner(login: $owner) {
    __typename
    ... on ProjectV2Owner {
      projectV2(number: $number) {
        repositories(first: 100, after: $after) {
          nodes { nameWithOwner }
          pageInfo { hasNextPage endCursor }
        }
      }
    }
  }
}
```

`cmd_provision` calls it right after `project_resolve` confirms the project exists, and before
either field-schema mutation branch (`board_lifecycle.py:530-547`). When `repo_name` is absent
from the linked set it refuses via `factory_cli.refuse` (exit 2, zero mutations):

> `factory: board_lifecycle: project is not linked to this repository: project 9 (acme) is not
> linked to 'acme/widget' -- confused-deputy guard: a served repo's own harness.json can name a
> project under the same owner it has no link to, and the field-schema write below would then
> land on the wrong board — link 'acme/widget' to project 9 (acme) with
> project_link_repository, or correct acme/widget's declared board number, before provisioning`

Names the project (owner + number), the repo, and the reason. `test-board-lifecycle.py`'s "linkage
guard (MUST-FIX 1)" case fixture reuses case 2's missing-options shape (which otherwise reaches
the mutating extend branch) so "zero mutations" is not vacuous.

## MUST-FIX 2 — create-then-link: exit code and print order

`cmd_provision`'s no-project branch now prints `created project {number}` **immediately** after
`project_create` succeeds, before the `project_link_repository` call that can still fail. On a
link failure it exits **4**, never 2 or 3:
- exit 2 is this module's own "nothing mutated / caller-declaration" code — false here, a project
  really was created.
- exit 3 is the clean-success "new project, needs a human to record the number" code — also
  false, since the run did NOT cleanly finish.
- exit 4 is honest: a write was attempted and did not fully land, matching the meaning `audit`/
  `reconcile` already give exit 4 (a `GhError` this module could not swallow).

The stderr line names the created project's number, tells the operator to record it now (so a
retry won't create a duplicate — the exact disaster `project_resolve`'s own docstring warns
against), and gives the manual remedy.

## MUST-FIX 3 — retitle's apply loop: code fixed to match the docstring

Chose to fix the **code**, not the docstring: the docstring's claim ("caught explicitly here
exactly as audit and reconcile catch it") was already the correct target behaviour — `reconcile`'s
own apply loop is the template it should have followed and simply hadn't. Each rename is now
wrapped in `try/except factory_gh.GhError`, printed to stderr, counted as `failed`, and the loop
continues to the next ticket. `--apply` now exits **1** if `failed > 0` (a genuine partial-failure
signal — `reconcile` already overrides the generic exit-1 "nothing to do" meaning for its own
residual count, so this mirrors an established precedent in the same file) and 0 otherwise. The
summary line now also reports `failed: N`.

## Failure-injection tests, each with its RED proof

All three live in `test-board-lifecycle.py`. RED proof method: `git show HEAD:<path> >
board_lifecycle.py` (pre-fix baseline — confirmed byte-identical to HEAD via `diff -q`), ran the
new tests, confirmed all 10 assertions reddened, then restored the fixed file from a `cp`'d copy
and confirmed byte-identical to the fix via `diff -q`. Full suite re-run GREEN afterward.

- **MUST-FIX 1** — case "linkage guard (MUST-FIX 1)": `linked_repos=_LINKED_REPOS_UNLINKED`
  against the missing-options fixture. RED (pre-fix): `rc=0`, `updateProjectV2Field` mutation
  reached the fake — the exact disaster. GREEN (fixed): `rc=2`, zero mutations, refusal names
  project/repo/reason.
- **MUST-FIX 2** — case "MUST-FIX 2": `resolve=_RESOLVE_ABSENT`,
  `fail_match="linkProjectV2ToRepository"`. RED (pre-fix): `rc=2`, stdout empty (the created
  number never printed — proving the ordering defect). GREEN (fixed): `rc=4`, stdout contains
  `created project 42` before the failure, stderr names the number and the repo.
- **MUST-FIX 3** — case "retitle case 2b (MUST-FIX 3)": two renamable tickets (#401, #402),
  `fail_match="401"`. RED (pre-fix): ticket #402's rename call never issued (log shows only
  #401's failed attempt), `rc=2`. GREEN (fixed): #402 is renamed despite #401's failure, `rc=1`,
  summary reports `renamed: 1` and `failed: 1`.

RED output (all 10 assertions, verbatim tails):
```
FAIL  MUST-FIX 2: create-then-link failure exits 4, ... — rc=2 stdout='' stderr="factory: board_lifecycle: gh api graphql failed: ..."
FAIL  MUST-FIX 2: the created project's number reaches stdout BEFORE the link failure ... — ''
FAIL  MUST-FIX 2: the stderr failure names the created project's number and the repo ... — "factory: board_lifecycle: gh api graphql failed: ..."
FAIL  linkage guard (MUST-FIX 1): refuses exit 2 ... — rc=0 stdout="board_lifecycle: added 2 option(s) to 'Status': Review, Done\n" stderr=''
FAIL  linkage guard: performs ZERO mutations ... — [... updateProjectV2Field call present ...]
FAIL  linkage guard: the refusal names the project ... — ''
FAIL  MUST-FIX 3: ticket #401's rename was attempted and failed, but the run continues ... — [only #401 logged, #402 never attempted]
FAIL  MUST-FIX 3: ticket #401's failure is reported on stderr ... — "factory: board_lifecycle: gh issue edit failed: acme/widget — fake_gh: forced failure ..." (no "401" in the propagated GhError's own message)
FAIL  MUST-FIX 3: exits 1 ... — rc=2 stdout='' stderr="factory: board_lifecycle: gh issue edit failed: ..."
FAIL  MUST-FIX 3: the summary reports both the renamed and the failed count ... — ''
```
All 10 assertions reddened against the pre-fix baseline; none were vacuously true.
(`MUST-FIX 2: createProjectV2( was actually called` was the one assertion in that block that
passed on BOTH pre- and post-fix code — it verifies the project creation itself happened, not the
fix's own behaviour, and was kept as a sanity anchor rather than counted as a discriminator.)

## The four sound behaviours — unchanged

- `project_single_select_extend`'s union computation (`_missing_options`, existing-then-additions
  ordering) — untouched; case 2 and the SC-08 no-"Abandoned"-substring case still pass.
- `audit`/`reconcile`'s exit-4 `GhError` contract — untouched; both GhError cases still pass.
- T-07's scoped fail-open (STATUS's #783 self-skip for a non-own repo) — untouched; both #783
  regression guards (audit case 8b, reconcile case 6b) still pass.
- The SC-20 / INV-26 bound — not touched by this file at all; no assertion in this fix cycle
  exercises it, and nothing here writes near it.

## `run-unit-tests.sh --kind all`

Exit code `0` (captured directly via `echo "EXIT:$?"` appended to the log, not inferred from a
piped `tail`). `grep -c "^FAIL"` on the full log: `0`. 46 `PASS test-*.py` lines logged (some
scripts print their own pass line twice, pre-existing and unrelated to this cycle) across all 20
unit + 22 integration scripts, including `test-board-lifecycle.py` (all cases, old and new) and
`test-factory-integration.py` (131/131, including case J's new linkage-query answer).

## Files touched

- `.claude/skills/harness/bin/board_lifecycle.py` — the three fixes plus updated docstring
  sections.
- `.claude/skills/harness/bin/test-board-lifecycle.py` — three new failure-injection cases, a
  `LINKED_REPOS_JSON` fixture/env-var plumbed through `run()`, a new fake-gh case for
  `repositories(first:`.
- `.claude/skills/harness/bin/test-factory-integration.py` — one new fake-gh branch answering
  the linkage-guard query for case (J)'s complete-board fixture.
- `.claude/skills/harness-init/SKILL.md` — the exit-code contract gains **4** (created but not
  linked), a direct consequence of MUST-FIX 2. Without this line the operator reads a 4 as an
  unknown failure and retries, which creates a second board — the exact disaster the new exit
  code exists to prevent.
- `.claude/skills/harness/SKILL.md` — the phase-transition row's owner cell. It read "the actor
  performing the transition", which names nobody: the code reviewer's medium finding, since a
  `main-session-direct` segment has no actor the sentence can resolve to. Now keyed on
  `execution_mode`, the same way the `start-task` and `close-task` rows already are.

Added after the goal-check flagged both files as modified-but-unreceipted (Q3). The two edits are
c1's, not stray: one follows MUST-FIX 2's new exit code, the other closes the code reviewer's
only remaining medium finding.
