# BUG-285 amend, cycle 0 — what changed, and the three dispatch premises that were wrong

BLUF: the signed scope pinned a reader that is already correct and never named the one that is
broken. BRIEF.md now covers both readers, plan.yaml gains T-02 (the fix) and T-03 (the pin), D-03 is
re-derived, and D-05 records a tooling gap. **Three premises in my dispatch did not survive checking
at source** — none changes the conclusion, all three change what a reader should believe.

## The three corrections

1. **The line anchors were each one lower than the tree.** Measured in this worktree and at
   `8902f566`: history comment `:116-119`, `try` `:120`, `doc = harness_yaml.load_file(path)`
   `:121`, `except harness_yaml.YamlParseError` `:122`, `factory_cli.refuse(...)` `:123`. The
   dispatch said 115-118 / 119 / 120 / 121 / 122. BRIEF.md and T-02's intent use the measured values.
2. **There was no "converged" sentence to delete.** Neither `BRIEF.md` nor `plan.yaml` contained the
   words "converged" or "factory_decompose" (grep, both files). The false claim lives only in
   `notes/intake-BUG-285.md:14`, quoting the operator's original dispatch, and there it reads
   "gh-sync.py's feature.json reader converged on json.load" — which is **true**. The standing
   BRIEF's problem statement correctly said `gh-sync.py:523` uses `json.loads`. The defect was
   **omission, not falsehood**: `factory_decompose.py` appeared nowhere. The Problem section was
   rewritten to cover both readers regardless, which is the outcome the dispatch wanted.
3. **`approval:` is `approved`, not `pending`, in BOTH artifacts** — signed `mruangutai` 2026-09-09,
   committed at `bb488145`. I set `BRIEF.md` back to `status: pending` with empty fields (mine to
   write). **plan.yaml's approval block cannot be reset by anyone**: `sign-approval` refuses a
   pm-typed caller *and* hardcodes `status: approved` (`plan-merge.py:1082`), `amend` rejects
   `--key approval` (exit 2, `plan-merge.py:1571-1573`), and `apply` carries the base's approval
   bytes forward verbatim. The plan template asserts "any change to the task set resets this to
   pending" — **no writer implements that reset.** See open question Q2.

## What the amendment rests on (re-measured, 2026-09-11)

- `load_factory` genuinely accepts a YAML-only `feature.json` **today**: the probe in T-02's
  `verify` was run against the unchanged tree and printed `ACCEPTED a YAML-only feature.json`,
  exit 1. It is therefore proven red before the fix exists.
- Both-direction disagreement confirmed: `json.loads('{"a":1,"a":2}')` returns `{'a': 2}`;
  `harness_yaml.load_str` on the same text raises `DuplicateKeyError`.
- **79 `feature.json` files at the owner root, 77 inside this worktree, ZERO cross-loader
  disagreements in either.** The swap changes no current behaviour. This is in BRIEF.md under
  `## Risk`, not only here.
- `json.JSONDecodeError` is a `ValueError` subclass (verified). T-02 catches the narrower name, by
  decision, and says why.
- Case `(1c)` at `tests/integration/test-factory-decompose.py:426-437` uses `{ not: valid json [[[`
  — rejected by **both** loaders, so it stays green across the swap and is the #208 regression anchor
  (SC-08).
- `check-domain.py --resolve`: `factory_decompose.py` → `harness-backend-dev`, `harness-dev-ops`
  (no qa); the test path → those two plus `harness-qa`. `execution_agent` set accordingly.

## Two constraints that shaped the plan

- **The unit test needs a new file name.** `suite_layout.py:_unit_integration_findings` refuses any
  `test-*.py` name present in both `tests/unit/` and `tests/integration/`, and
  `test-factory-decompose.py` is taken. Hence `tests/unit/test-factory-decompose-loader.py`.
- **`lanes:` has no write route** (D-05). `check-plan-routes.py` contains zero occurrences of
  `lanes`; it grades each task's `files` through `check-domain.py` plus the `execution_mode` token.
  So the stale lanes table misreports, but binds nothing.

## Verification observed

`check-plan-routes.py` on this plan: `OK T-01`, `OK T-02`, `OK T-03`; exit 1 from a single
**MANIFEST DEVIATION** — the worktree's `.harness/team-config.yaml` differs from the owner's by 4
diff lines. Pre-existing and inherited; I edited no team-config. T-01 verified **whole-task
identical** to `HEAD` after every write (`verify` sha `b9a6105b0103`, `intent` sha `816752120e6c`);
`panel` and `lanes` reload identical to `HEAD`; D-01, D-02, D-04 untouched.

## The amended artifacts, in full

**Requirements.** REQ-01..04 unchanged (gh-sync pin). REQ-05 `load_factory` reads JSON · REQ-06 the
#208 refusal is preserved exactly · REQ-07 the parser choice is pinned both directions · REQ-08 no
check in `test-factory-decompose.py` deleted, case `(1c)` stays green.

**Success criteria — 10, each with exactly one `verify:`; all 6 `automated` name an ACTIVE kind.**
SC-01 automated/integration · SC-02 automated/integration · SC-03 inspection · SC-04
automated/integration (318-`ok` baseline at `7e0c2ec` retained, still correct) · SC-05 inspection ·
**SC-06** inspection (JSON parse + `json.JSONDecodeError`/`OSError` + `refuse()` intact, at
`review_sha`) · **SC-07** automated/unit · **SC-08** automated/integration (case `(1c)` survives) ·
**SC-09** inspection (mutation transcript) · **SC-10** automated/unit (zero `FAIL` lines asserted
directly, not inferred from the exit code).

**Tasks.**

|id|change_type|execution_agent|depends_on|verify|
|---|---|---|---|---|
|T-01|bugfix|harness-qa|—|`test-gh-sync.py`. **Untouched**|
|T-02|bugfix|harness-backend-dev|[]|`test-factory-decompose.py`, then the tempdir refusal probe|
|T-03|bugfix|harness-qa|[T-02]|the new unit file, then `run-unit-tests.sh --kind unit`|

T-02's intent decides the open questions a builder would otherwise ask: catch
`(json.JSONDecodeError, OSError)` — the narrower name over `ValueError`, with the reason — open and
read the file explicitly because `load_file` did the read too, `json` already imported at `:35`,
`refuse()` byte-unchanged, comment `:116-119` updated not deleted, `isinstance` guard at `:124`
kept. T-03's intent fixes the file name, the fixture, the three named checks, and the
copy-in-a-tempdir mutation proof.

**D-03, as amended** (re-derived, not carried forward): *"change_type is bugfix on all three tasks,
and the required kind is now unit, with integration retained for the two test-side tasks."* Because
editing `factory_decompose.py` makes DEC-217's `touches_runtime_code` TRUE;
`fix_confined_to_tests_and_contract_docs` is now FALSE so the matrix no longer demands `integration`
by itself, but T-01 and case `(1c)` keep it under DEC-35; DEC-213 selects by directory, so T-03 goes
under `tests/unit/`.

**`plan-merge.py` stdout, every invocation.**

- `apply --proposal …` → `ADDED D-05` / `ADDED T-02` / `ADDED T-03` / `APPLIED <plan>`, exit 0. No
  `IGNORED-APPROVAL` line — the proposal carried no approval mapping.
- `amend D-03.choice --show` → the old text + `sha256: f4f33285a48a675b…`, exit 0.
- `amend D-03.choice --expect-sha256 … --value-file …` → `AMENDED decisions:D-03.choice` /
  `APPLIED <plan>`, exit 0.
- `amend D-03.because --show` → the old text + `sha256: 7e70bb14820b039…`, exit 0.
- `amend D-03.because --expect-sha256 … --value-file …` → `AMENDED decisions:D-03.because` /
  `APPLIED <plan>`, exit 0.
- `observations-merge.py apply` → 5 `ADDED`, 9 `PRESERVED`, `APPLIED`, exit 0.


## Open questions

- **Q1 (blocking):** `plan.yaml` still reads `approval.status: approved` over a changed task set.
  No verb can reset it. The main session must decide how BUG-285 is re-signed.
- **Q2 (non-blocking, harness defect):** `lanes:` is unwritable by any verb, and approved→pending is
  unimplemented. Both are tooling gaps for the harness owner.


## Cycle 1 — T-02 repaired, two defects closed

Both defects were real and both are now closed in `plan.yaml`; nothing else in the file was
touched. The three premise corrections from cycle 0 stand and the lead's independent
re-measurement matches them.

**Defect 1 — `verify:` did not run the kind `change_type` demands.** T-02 is the only task whose
`files:` is `.claude/skills/harness/bin/factory_decompose.py`, so D-03's `touches_runtime_code`
clause demands the `unit` kind of it, and its block ran only the integration suite plus the inline
probe. Added, as the FIRST line of the block:
`env -u HARNESS_AGENT_TYPE .agents/skills/harness/bin/run-unit-tests.sh --kind unit`.

Order is deliberate: the unit suite is the cheapest, module-scoped regression check, so it fails
fast before the slower integration suite, and it leaves the inline probe last as this task's own
red-then-green evidence. The two pre-existing commands are byte-unchanged and the block is still a
literal `|` scalar (`plan.yaml:168`).

The runner CAN run at T-02's moment — checked, not assumed: `.agents/skills/harness/bin/run-unit-tests.sh`
exists and parses `--kind unit` (`run-unit-tests.sh:18`, usage line `:23`), and `harness.json`
`test_kinds.unit.cmd` is that exact command with `status: active`. T-02 lands before T-03 creates
`tests/unit/test-factory-decompose-loader.py`, so at T-02's moment this runs the EXISTING unit
suite over the module being edited — a regression check, which is the point.

**Defect 2 — `intent:` cited a nonexistent third command.** The TEST-FIRST paragraph pointed at
"the third verify command" while the block held two. Rewritten to name the probe by what it IS:
"the inline behavioural probe in verify - the python3 -c command that writes a YAML-only
feature.json into a fresh tempdir and demands load_factory refuse it". An ordinal would have gone
stale again the moment the block grew, which is exactly what happened here.

**One further stale ordinal found and fixed in the same field.** `intent` said "load_plan at line
479 still uses it"; measured at source, line 479 is the bare `try:` and the `harness_yaml.load_plan`
call is at `:480`. Corrected to 480 — same off-by-one family as the anchors the lead re-measured.
Every other anchor in the field re-measured correct and was left alone: `load_factory` `:111`,
`path = …` `:112`, `import json` `:35`, `import harness_yaml` `:46`, comment `:116-119`, `try` `:120`,
`load_file` `:121`, `except` `:122`, `refuse` `:123`, `isinstance` guard `:124`.

**`plan-merge.py` stdout, every cycle-1 invocation** (all exit 0):

- `amend --key tasks --id T-02 --field verify --show` → the old two-command block +
  `sha256: 840f6015534269db26e35249dbb8e4da9f9874a685d0715b90dff0cf0a9bf88f`
- `amend --key tasks --id T-02 --field intent --show` → the old intent +
  `sha256: 70d6747a6a8b08b4e1c53bc33a2f3eb1abb61d869ca849d5bb48dc15e74530b2`
- `amend … --field verify --expect-sha256 840f60… --value-file …` →
  `AMENDED tasks:T-02.verify` / `APPLIED <plan>`
- `amend … --field intent --expect-sha256 70d674… --value-file …` →
  `AMENDED tasks:T-02.intent` / `APPLIED <plan>`

**Post-amend verification**, via `harness_yaml.load_plan` on the amended file: top-level keys
unchanged (`approval decisions feature lanes panel schema source_issues status tasks`);
`approval` still `{status: approved, approved_by: mruangutai, date: 2026-09-09}`; decisions still
`D-01..D-05`; T-01 `files: [tests/integration/test-gh-sync.py]` and T-03
`files: [tests/unit/test-factory-decompose-loader.py]`, `depends_on: [T-02]` intact; T-02's
`files`, `change_type: bugfix`, `execution_agent: harness-backend-dev`, `depends_on: []`,
`traces: [REQ-05, REQ-06]` all unchanged. `intent` now contains no "third verify" reference and no
"line 479". `check-plan-routes.py <plan>` → `0 violation(s) across 1 plan(s)`, three `OK T-NN` lines.

Q1 (approval over a changed task set) is unchanged and remains the main session's; it did not block
this repair.
