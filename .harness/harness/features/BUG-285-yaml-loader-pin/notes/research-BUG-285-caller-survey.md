# Caller survey — `load_factory`

**BLUF. `load_factory` has exactly ONE caller in the whole worktree, and it does NOT depend on
malformed tolerance.** `factory_decompose.py:515`, inside `_main()` (`:462`). It cannot distinguish
an empty record from a populated one by any means other than the record's own field values, and the
one malformed class it already meets today — an unparseable `feature.json` — is already a refusal,
asserted as such by an existing test. **No stop condition fires.**

## What was searched

`load_factory` across the whole worktree at HEAD `6cb113f4`, then `factory_decompose` importers, in
`.claude/skills/` (which is the same inode set as `.agents/skills/`), `tests/`, and the tree root.
`bin/` does not exist in this worktree.

| hit | kind |
|---|---|
|`.claude/skills/harness/bin/factory_decompose.py:111`|the definition|
|`.claude/skills/harness/bin/factory_decompose.py:515`|**the only call**|
|`.claude/skills/harness/bin/factory_decompose.py:478`|a comment referring to the same #208 fix at `load_plan`, not a call|
|`.claude/skills/harness/bin/feature-schema.json:106`|schema prose naming the reader|
|`tests/integration/test-factory-decompose.py:30`|`import factory_decompose as fd` — **no `fd.load_factory(` call anywhere in `tests/`**; the two `load_factory` mentions in that file (`:424`, `:611`) are comments|
|`.harness/**/features/**`|BRIEF, plan and notes prose. Not callers|

Subprocess callers — `tests/integration/test-factory-integration.py:65`,
`tests/integration/test-factory-issue-types.py:65` — invoke the CLI, so they reach `load_factory`
only through `_main()` at `:515`. Same single call site.

## The one call site

`factory_decompose.py:515-518`, step 4 of `_main()`:

- **What it does with the record.** `factory["repo"]` is overwritten unconditionally from `--repo`
  (`:516`), then the record is handed to `sort_dispositions(tasks, factory)` (`:276`) which sorts
  every task into `full | partial | new | edges_unwritten`. `factory["parent"]` drives
  `need_parent_create` (`:526`) and the step-5b adopt-or-create branch (`:546-574`); `need_step5`
  (`:536`) fires on any `new` disposition or a `None` parent. Step 6 (`:577-587`) creates a GitHub
  issue for every `new` task. `write_factory` persists the record after each create.
- **Can it distinguish empty from populated?** **No — not as such.** It never asks "was a record
  read?"; it only reads field values. An empty record is therefore literally
  indistinguishable from a genuinely-unsynced feature, which is exactly the fail-open: every task
  sorts `new`, `factory["parent"] is None`, and the run **re-creates the parent and every task
  issue that already exists on GitHub**. That is the FEAT-14 failure mode, and this call site is
  where it lands.
- **Does it depend on malformed tolerance?** **No.** If a malformed `feature.json` became a refusal,
  `_main()` would exit at `:515` before `ensure_labels` — the declared point of no return at `:538`
  — having made zero remote writes. Nothing downstream of `:515` reads `feature.json` again before
  that point. The tolerance is not load-bearing for any behaviour; it is the bug.
- **Does it depend on the ABSENT-file empty record?** **Yes, and that is correct and unchanged.**
  `:114-115` returning empty for an absent file is what lets a never-synced feature be decomposed at
  all; `test-factory-issue-types.py:216-217` documents that `write_factory` legitimately creates
  `feature.json` fresh, so cases "starting from nothing install no feature.json at all".

## Tests: none depends on tolerance either

- `test-factory-decompose.py` case `(1c)` (`:426-437`) feeds `feature_json_extra="{ not: valid json
  [[["` and **asserts refusal**: exit 2, stderr names the `feature.json` path, no class-name leak,
  zero mutating calls. A test that already demands refusal for a malformed file cannot depend on
  tolerance for one.
- Every other fixture is a legal JSON mapping or absent: `make_feature`'s default
  `feature_json_extra="{}"` (`:303`, `:317`) is the *block-key-absent* class, which the parity
  survey measures as SAME and legitimate; `:618` writes `json.dumps(pre_existing)`;
  `test-factory-issue-types.py:229` writes `{"factory": factory}`;
  `test-factory-integration.py:1509-1510` writes a `github` block. None is malformed.

## Live data: nothing on disk is affected

All 80 `feature.json` files under `.harness/*/features/*/` were parsed with
`json.loads` at HEAD `6cb113f4`: **80 parse to a mapping, 0 have a non-mapping `factory` value, 0
would change behaviour** under any refusal widening.

## Verdict

No caller — in-process, subprocess, or test — depends on `load_factory` tolerating a malformed
`feature.json`. The operator's ruling stands unchallenged: absence keeps returning the empty record,
and the present-but-malformed case is free to become a refusal without breaking a single caller.

## Open questions

- **Q3 (non-blocking):** `factory["repo"]` is overwritten at `:516` before any comparison, so a
  recorded repo that disagrees with `--repo` is silently discarded. Pre-existing, unrelated to this
  bug, already noted in `FEAT-10-software-factory/notes/review-harness-code-reviewer-panel-validator.md:157-160`.
  Not absorbed here.
