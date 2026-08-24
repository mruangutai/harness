# Receipt — harness-dev-ops — FEAT-33 fix cycle c4

Both dispatched findings were real and are fixed. Two corrections to what I was told, and one
scope extension I judged mandatory, are recorded below. A third instance of the c4 coordinator's
falsified-comment item existed beyond the two it named; all three are fixed.

## Files touched (every one)

- `.claude/skills/harness/bin/board_lifecycle.py`
- `.claude/skills/harness/bin/test-board-lifecycle.py`
- this receipt

Nothing else. `git status` confirms the other modified paths in the worktree
(`harness-init/SKILL.md`, `test-no-distribution.py`, `BRIEF.md`, `plan.yaml`, pm's notes and
observations, the untracked c3 review) were already modified before this run and I did not open
them for writing.

## Suite

`bash .claude/skills/harness/bin/run-unit-tests.sh --kind all` — **EXIT 0**, 46 script-level
`^PASS test-` lines, **851** total `^PASS`, **0** `^FAIL`. Baseline before this cycle was EXIT 0 /
46 / 840 / 0, reproduced first on the untouched tree. +11 assertions, all in
`test-board-lifecycle.py` (138 -> 149 checks in that script).

No PLAN task id and no `verify:` command were carried by this dispatch, so there is no
`task_verify` to report.

## Finding 1 (HIGH) — confirmed, fixed, and it had a second instance

Verified as described. `factory_gh.run_gh`'s bare `json.loads(r.stdout)` (`factory_gh.py:170`) and
`_project_field_resolve`'s unguarded `field_obj["id"]` / `o["name"]` (`factory_gh.py:459-462`) are
both inside `_fresh_board_station_field`'s try and neither raises `GhError`. `factory_cli.run` is
called with `expected=(factory_gh.GhError, factory_config.FleetError)` (`board_lifecycle.py:1164`),
so anything else hit `except BaseException` (`factory_cli.py:88`) and exited `EXIT_REFUSED = 2`.

**Scope extension I made deliberately:** the create-branch LINK block had the identical
GhError-only catch, and `project_link_repository` sends two `run_gh(json_out=True)` calls plus an
unguarded `repository["id"]`. Leaving it would have kept the exit-code paragraph false at a
different line, so I broadened both. Reported rather than folded in silently.

Both blocks now `except SystemExit: raise` before `except BaseException` — `_bail` raises
SystemExit from inside its own try (the wrong-field-type branch), and that intended exit 4 must
pass through unwrapped. Nothing is swallowed; every path still exits non-zero.

**Docstring re-check.** `PROVISION'S EXIT CODES` — the sentence "4 is never conflated with 2" is
replaced by a paragraph that states the enforcement mechanism (exception class, both post-create
blocks) AND names the one window that genuinely remains: `factory_gh.project_create` itself is
unwrapped, because a failure inside it has no created number to report. Its GhErrors are true
zero-mutation failures (owner-id read failed, or the mutation returned null), so 2 is correct for
those; a `json.loads` ValueError on the createProjectV2 response — gh exited 0, so the board
EXISTS — still exits 2, and closing that needs a read-back by title this module does not do.
Named rather than papered over. `A FRESH BOARD IS NOT EMPTY` was re-read sentence by sentence and
needed no change: every claim in it is a measurement or a historical fact, none an exit-code
conflation claim.

The accepted residual (create-record confinement by dict SHAPE, not type) is recorded in
`_fresh_board_station_field`'s docstring with the operator's reason, including the `project_resolve`
`{"id","title"}` KeyError barrier and the c1 MUST-FIX 2 print-ordering constraint. Nothing was
restructured.

## Finding 2 (MEDIUM) — real gap, but two of its specifics were wrong

The gap is real: nothing asserted which project number the reads used. Two corrections:

1. **The fake already recorded the `number` argument.** `FAKE_GH_SRC`'s first line has always
   logged the full argv to `FAKE_LOG`. What was missing was any assertion that READ it. No change
   to the fake's logging was needed; I added a `number_arg(line)` helper that extracts the
   `-F number=<N>` token (unambiguous — the GraphQL bodies spell it `number: $number`).
2. **The literal mutant the review named does not compile.** `_fresh_board_station_field`'s
   parameters are `(created, repo_name, owner, field, declared)` — there is no `number` in scope,
   so swapping `created["number"]` for `number` is a `NameError`, not a silent wrong number. It
   does NOT keep the suite at 138 PASS / 0 FAIL. See mutant A below.

New assertions (3): the fresh-board probe and the options read must carry the CREATED number (42),
not the DECLARED 9, on the pre-existing-Status branch (case 5d), and the probe likewise on the
field-absent branch (case 5b).

## Mutation proofs

All three mutants were diff-confirmed applied before running and the restore verified
byte-identical by `diff -q` plus `md5` (`c9b89a5f8ef9ef1501e9d091078d2f29` before and after).

**Mutant A — the review's literal swap** (`created["number"]` -> `number` at both read sites).
Applied, ran, exit 1, **18 checks red**, including all three new ones. Real output:

```
FAIL  no project: exits 3 — rc=4 ... stderr="factory: board_lifecycle: created project 42 on
acme and linked acme/widget, but an UNEXPECTED NameError interrupted the field work for 'Status'
-- name 'number' is not defined -- ... the project EXISTS and is LINKED (record 42 in
acme/widget's harness.json now to avoid a duplicate on retry) ..."
```

Not a silent mutant — but it doubles as evidence that Finding 1's fix works: the NameError now
exits 4 naming project 42 instead of exiting 2.

**Mutant B — call site hands a hand-built record** (`{"id": created["id"], "number": number}`).
6 red: the 3 new checks plus 3 pre-existing stderr checks, because it also changes what `_bail`
prints. Also not silent.

**Mutant C — the genuinely silent one, and the real proof.** Thread the declared `number` in as a
sixth parameter, use it at both READ sites only, leave every message on `created["number"]`:

```
< def _fresh_board_station_field(created, repo_name, owner, field, declared):
> def _fresh_board_station_field(created, repo_name, owner, field, declared, number):
<         field_id, typename = _field_probe(owner, created["number"], field)
>         field_id, typename = _field_probe(owner, number, field)
<         existing = factory_gh.project_field_options(owner, created["number"], field)
>         existing = factory_gh.project_field_options(owner, number, field)
```

Result: exit 1, **exactly 3 red — the three new c4 assertions — and 138 PASS.** 138 is precisely
the pre-c4 pass count, which proves the entire pre-existing suite was green under this mutant
while the new assertions catch it. Sample:

```
FAIL  c4: the fresh-board probe is sent for the CREATED project number (42), never the DECLARED 9
      -- the declared number is the one that did not resolve — probe_calls=[...number=9...]
```

**Mutant D — Finding 1's own fix, re-narrowed.** Both broadened `except BaseException as exc:`
clauses reverted to `except factory_gh.GhError as exc:`. Exit 1, 6 red, 143 PASS. The defect
reproduced verbatim:

```
FAIL  c4: a NON-GhError (ValueError from run_gh's json.loads) in the field work after a
successful create+link exits 4, NEVER 2 -- 2 would claim nothing was written — rc=2
stdout="board_lifecycle: no project 9 on acme -- created project 42; record number 42 ..."
stderr='factory: board_lifecycle: unexpected failure: JSONDecodeError: Expecting value: line 1
column 1 (char 0) — re-run with FACTORY_DEBUG=1 for a traceback'
```

`rc=2` after stdout says a project was created, and the stderr names no project number at all —
exactly the duplicate-board disaster. To make this reachable honestly I added a `MALFORMED_MATCH`
lever to the fake gh: it makes a matched call SUCCEED with a non-JSON body, which is the only
shape that produces a non-GhError. `FAIL_MATCH` cannot express it — a nonzero exit is a GhError,
the class already handled. Two new cases (5h/5i, 8 assertions) cover the field work and the link.

**Order-of-work disclosure:** Finding 1's fix was written before its test (the dispatch specified
the fix), so mutant D is the RED evidence rather than a test-first cycle. Reported as what it is.

## Coordinator's mid-run item — `_extend_to_union` — confirmed, and there were THREE

Verified independently: the signature at `board_lifecycle.py:636` is
`_extend_to_union(project_id, field_id, owner, number, field, declared)`, so both cited statements
were false as literal code. **This correction came from an independent review (pm), not from my own
re-read** — I had read that docstring earlier in this session and did not catch it.

A third instance the coordinator did not name: `_fresh_board_station_field`'s own docstring said
the resolved-project path "never sees an option list it could pass through". Also false. All three
now state the property that is actually true and sufficient: `declared` is consumed only by
`_missing_options`, and the sole argument `project_single_select_extend` receives from that
function is the inline `existing + missing` built from its own read — so a bare `declared` cannot
reach the replacing mutation along that path. Verified `declared` appears exactly once in the
function body. Signature and design unchanged.

## Open questions

- The `project_create` exit-2 window above is real and unfixable without a read-back by title.
  Not blocking, and now documented in the exit-code paragraph rather than contradicted by it.
