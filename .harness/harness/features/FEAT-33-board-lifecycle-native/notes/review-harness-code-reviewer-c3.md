# Review — c2+c3 — harness-code-reviewer

**FAIL.** The code is right and the record is not. Claim 3 (structural confinement of the exact
replace) holds and is stronger than claimed. The one blocking item is that `plan.yaml` T-04 still
states, as signed authority, the two behaviours c2 and c3 deliberately reversed — including "NEVER
… delete an existing option", which the shipped code now does on purpose.

Reviewed `b9a4642..337bbc2`, the five in-scope paths only. No `[harness:human]` commits in range.
Suites at the pin: `test-board-lifecycle.py` 138 PASS / 0 FAIL; `test-no-distribution.py` ALL PASS.
29 `check(` added, 1 removed — your count is exact.

## Your three claims

**Claim 1 (c2 exit codes) — upheld.** Field lands at `board_lifecycle.py:661`, before `:662`'s
`sys.exit(3)`. Every failure inside `_fresh_board_station_field` routes to `_bail` (`:540-553`) →
exit 4 naming `created['number']`. **No path exits 3 after a partial failure.**

**Claim 2 (probe + exact replace) — upheld, and c3 removed the falsified comment correctly.** The
two surviving occurrences of "empty by construction" (`:191`, `:655`) are both explicit quotations
labelled MEASURED FALSE. That is the record posture, not a second falsified statement.

**Claim 3 — upheld, and I found a barrier you did not claim.** Enumerated myself, not taken on
trust. `project_single_select_extend`: exactly two production call sites, `:573` (inside
`_fresh_board_station_field`) and `:597` (inside `_extend_to_union`); `factory_gh.py:675` is the
definition; every other hit is a test or a docstring. `_fresh_board_station_field`: one call site,
`:661`, first argument is `project_create`'s return from `:633`. `_extend_to_union`: one call site,
`:705`, no option parameter. The extra barrier: `project_resolve` returns `{"id","title"}`
(`factory_gh.py:544`) with **no `number` key**, and `_fresh_board_station_field`'s first statement
dereferences `created["number"]` (`:558`) — so the only other project-record shape in this module
raises `KeyError` before any mutation. `--repo` cannot reach it (it only selects which declaration
is read, `:285-300`); there is no retry or re-entry loop in `cmd_provision`. Residual, not reachable
today: the confinement is on a dict's *shape*, so a future caller could hand-build
`{"id": <established>, "number": N}`. Having `_fresh_board_station_field` call `project_create`
itself would close that.

## Findings, ranked

**F1 · high · must_fix · spec mismatch — the signed plan now states the opposite of the code.**
`plan.yaml` T-04 step 2: "report the NEW project number and **STOP with exit 3**" — contradicted by
`:661`. T-04 step 5: "**NEVER** rename, reorder or delete an existing option" — contradicted by
`:573`, which deletes Todo and In Progress. No amendment; `notes/rulings-2026-08-23.md` carries no
ruling on either; the only record of the authorising ruling is prose the same commit authored. The
c3 receipt (`:83-97`) says `plan.yaml` is dispatch-forbidden to dev-ops and nothing was committed —
the escalation was raised and never actioned. Failure scenario: the next agent dispatched into
`provision`'s create branch reads T-04 step 5 as authority and either blocks a correct change or
cites it downstream as evidence that `provision` never deletes an option, skipping a guard that
depends on it. CLAUDE.md is explicit that nothing in this tree detects a falsified statement left
standing (DEC-188), so the striking has to actually happen. Fix the record, not the code. *(T-04
step 6's exit list omitted exit 4 already at c1 and the panel signed that off — not re-raised.)*

**F2 · med · the "probe the CREATED number" invariant is asserted by a comment only.**
`:558` and `:572` use `created["number"]`; the comment at `:555-556` is the only thing holding it.
The fake gh dispatches the probe on `*"ProjectV2IterationField"*` (`test-board-lifecycle.py:202`)
and the options read on `*"options { id name }"*` (`:205`) — **query text alone, never `number=`** —
and no provision assertion greps `number=` (the four that exist, `:1068 :1072 :1107 :1161`, are
reconcile issue numbers). Failure scenario: swap `created["number"]` → `number`, the declared and
just-proved-nonexistent number, and the offline suite stays 138/0 green while every live fresh
provision gets `_field_probe` → "project not found" GhError → `_bail` → exit 4 on a board it just
created: the exact SC-01 regression c2 exists to fix, from the exact class of defect this commit's
own message names. Fix: in case 5d assert `"number=42"` present and `"number=9"` absent in the probe
and options argv. *Verified by reading the fake's dispatch and by grep — I could not execute the
mutant, the read-only guard blocks copying the tree.*

**F3 · med · `_fresh_board_station_field`'s `except` is narrower than its own contract, and the miss
lands on exit 2 = "nothing mutated".** `:574` catches only `factory_gh.GhError`. Everything else
falls to `factory_cli.run`'s `except BaseException` → `EXIT_REFUSED = 2` (`factory_cli.py:88-96`,
`:28`), documented at `factory_cli.py:10-12` as "refused … nothing mutated". Reachable non-GhError
raisers inside the new nine-statement window: `run_gh` does a bare `json.loads(r.stdout)` at
`factory_gh.py:170`, so a `gh` exiting 0 with empty or non-JSON stdout raises `JSONDecodeError`; and
`_project_field_resolve` indexes `field_obj["id"]` / `o["id"]` / `o["name"]` unguarded
(`factory_gh.py:459-462`). Failure scenario: provision creates project 8, links it, the probe's `gh`
returns exit 0 with empty stdout → exit 2 → a caller routing on the exit code reads "nothing
mutated", re-runs, `project_resolve` still returns None for the declared number, and a SECOND board
is created. This falsifies the new paragraph's "4 is never conflated with 2". Two mitigations
already present: stdout carries "created project 8; record number 8" from `:634` (c1 MUST-FIX 2),
and the rate-limit case is a GhError (`factory_gh.py:60-88`), so the likely failure is covered. The
pre-existing link handler at `:638` is equally narrow, so this is consistent with the tree rather
than a regression — but c2/c3 widened the window from zero statements to nine. Fix: `except
Exception` here, or wrap the whole post-link block and re-raise as exit 4.

**F4 · low · `harness-init/SKILL.md:225-230` is unconditional where the code is conditional.** "On a
NEW board, `provision` DELETES GitHub's default columns" is true only when `station_field` names the
field GitHub's default carries — `Status`. `templates/harness.json:156` documents `station_field` as
a declared key, not a fixed literal. Failure scenario: a repository joining the fleet declares
`"station_field": "Station"`. `_field_probe` returns `(None, None)`, provision creates `Station` with
the six stations, and GitHub's default `Status` survives with Todo / In Progress / Done — the board
has two station-shaped fields and its default view still groups by `Status`. The module docstring
gets this right (`:534-540` names the absent-field case as "a declaration whose `station_field` is
not `Status`"); the operator-facing surface does not. That surface addresses exactly the audience for
which the non-`Status` case is possible.

**F5 · low · the fleet tripwire's new form is not strictly stronger, and the comment says it is.**
`test-no-distribution.py:167` builds a SET, so cardinality is gone; `:155-158` and the commit message
both assert `len(repos)` was "strictly weaker". Failure scenario: `fleet.yaml` gains a duplicate
`- name: mruangutai/kaya-ai` with `default_branch: main`. `load_fleet` validates entries
independently with no duplicate check (`factory_config.py:175-191`), `found_repos` is unchanged, the
write-surface tripwire passes, and `repo_entry`'s first-match-wins hands `factory_workspace` the
wrong branch with nothing red. Fix: `and len(repos) == len(expected_repos)`. The `isinstance(r,
dict)` filter at `:167` is **not** a hole — `load_fleet` rejects a non-mapping entry outright, so
such an entry can never become a live write surface.

**F6 · low, and an open question · the fleet gained a permanent second DEFAULT write surface.**
`fleet.yaml:25-32` adds `mruangutai/harness-factory-smoke`. `factory_claim.py:250` defaults
`repos_to_serve` to every fleet entry when `--repo` is absent, and `:261-274` resolves each one's
board remotely and validates `ready`/`building`/`review` against it **before** any board read.
Failure scenario: if the smoke repo's remote `.harness/harness.json` on `main` does not declare a
board offering those three options — e.g. if the number the live run created was never written back,
since provision deliberately never edits a declaration — then `factory_claim --as <login>` with no
`--repo` refuses at exit 2 for the *whole* fleet, kaya-ai included. Settling this needs a live remote
read, which this dispatch forbids. Raised as Q1.

## Stage 1

Every code and test change traces to REQ-01 / SC-01. The `fleet.yaml` + `test-no-distribution.py`
pair traces to no REQ or SC: it is collateral of a live verification that BRIEF `:196-200` itself
discloses as the un-proven gap. Operator-authored, BRIEF-disclosed, and the right call — but a new
fleet member is a new factory write surface and belongs in a recorded decision, not only in a test
comment. Logged as `scope_creep`, low, record-don't-revert. No omissions found: SC-01's existing-board
half is now covered by case 5g's `Icebox` fixture, which case 2 provably could not catch.

## Absence assertions — all five live, none vacuous

`:531` (`updateProjectV2Field` absent) paired with `len(field_calls) == 1`. `:586`
(`createProjectV2Field` absent) paired with `len(extend_calls) == 1`, and it is precisely the call
c2's code made, so the matcher's shape provably reaches its target; `createProjectV2Field` is not a
substring of the `createProjectV2(` project mutation. `:597` (`Todo` / `In\x01Progress` absent) — the
`\x01` is correct, the fake logs `"$*" | tr '\n' ' ' | tr ' ' '\001'` (`:106`), and an
`existing + missing` implementation on the fresh path would put `Todo` in the extend argv and trip
it. `:640` paired with rc == 4 and `"ProjectV2Field" in stderr`, which does not false-match
`ProjectV2SingleSelectField`. `:669` (bare-declared literal absent) paired with a byte-for-byte
*presence* assertion of the expected union at `:663-668` — the strongest of the set.
`_expected_options_literal` re-authoring the renderer rather than importing it is the right call.
The one gap is not in your list: nothing asserts which project number the two reads used (F2).

## Open questions

- **Q1, blocking:** does `mruangutai/harness-factory-smoke`'s remote `.harness/harness.json` on
  `main` declare a board whose station field offers `ready`, `building` and `done`? If not,
  `factory_claim` with no `--repo` now refuses for the entire fleet (F6). Needs one live read.
- **Q2, non-blocking:** `project_single_select_extend` sends options as name-only literals
  (`factory_gh.py:633-642`); `updateProjectV2Field`'s input has no option `id`. Does GitHub preserve
  an option — and the items sitting in it — when a name is re-sent, or recreate it? The live run
  proved `Icebox` survives as a *column*; it did not prove a card in it keeps its station. Only the
  established-board path (`_extend_to_union`) depends on this, and it is pre-existing behaviour
  outside this diff.
