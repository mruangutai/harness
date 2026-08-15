# Receipt — harness-documentor — 2026-08-12-2-product

**Q1 fixed. `SPEC.md` §3.3 no longer claims `name` + `default_branch` onboards a repository.** All
four board fields are named, the clone/nothing-installed clauses survive, and the change is one hunk.

## Before / after — exact text

Before (`docs/harness/SPEC.md:426-428` at spawn):

> **Onboarding a repository is one edit:** add a `- name: <owner>/<repo>` entry (with its
> `default_branch`) under `repos:` in `.harness/factory/fleet.yaml`. The first factory run against it
> clones it under `workspace_root`; nothing is installed into it.

After (`docs/harness/SPEC.md:426-432`):

> **Onboarding a repository is one edit, but not a small one:** add a `- name: <owner>/<repo>` entry
> under `repos:` in `.harness/factory/fleet.yaml` carrying its `default_branch` **and its own `board:`
> block — `owner`, `number`, `station_field` and `stations`, all four required**. An entry missing any
> of them makes `load_fleet` raise, and because `check-domain.sh` then fails CLOSED the symptom is not
> a failed onboarding but every agent write in this repository BLOCKED
> (`.claude/skills/harness/bin/harness_boundary.py:158`). The first factory run against it
> clones it under `workspace_root`; nothing is installed into it.

## Evidence

Four fields verified in the implementation, not taken from the dispatch:
`factory_config.py:82-86` (`owner`), `:87-92` (`number`), `:93-97` (`station_field`),
`:98-108` (`stations`); the missing-board raise at `:151-157`. Live entry carrying all four:
`.harness/factory/fleet.yaml:26-33`.

Fail-CLOSED consequence verified at `harness_boundary.py:139-165` — `resolve_fleet` catches any
`load_fleet` exception and prints `BLOCKED — the fleet declaration does not load`;
`check-domain.sh:196` calls it directly. Corrected after a full sweep: `git grep -n "resolve_fleet("
-- .claude` returns two call sites, `check-domain.sh:196` and `harness_boundary.py:261` (the shared
classifier, which the module comment at `:257-260` says runs for EVERY governed write). So the
BLOCKED symptom is not narrower than the SPEC sentence claims — it is if anything broader. I do not
claim to have traced every caller of that classifier.

One hunk, evidenced (`--stat` cannot show hunk count, so both are given):

```
$ git diff -U0 docs/harness/SPEC.md | grep -c '^@@'
1
$ git diff --stat docs/harness/SPEC.md
 docs/harness/SPEC.md | 8 ++++++--
 1 file changed, 6 insertions(+), 2 deletions(-)
```

## Full dirty set — complete `git status --porcelain` output

```
 M .harness/features/FEAT-16-factory-per-repo-board/observations/harness-orchestrator.md
 M docs/harness/SPEC.md
```

`observations/harness-orchestrator.md` was **already modified at spawn** — captured before my edit,
in the same shell that read `fleet.yaml`. It is not mine. `docs/harness/SPEC.md` is my only
modification. No untracked paths. (This receipt file is itself new and will appear as untracked once
written; it is the artifact this dispatch named.)

## Raised, not fixed

- **The code's own error text under-enumerates the same block.** `factory_config.py:151-156` tells
  the operator to give the repo a board `"with number, station_field and stations"` — omitting
  `owner`, which `_validate_board` then demands. Identical defect class to Q1, in the message an
  operator reads *at the moment they hit the failure*. Code is not my domain; raised as Q1 below.
- `SPEC.md:415` is reserved by the dispatch and deliberately left wrong. Not re-raised.
- The `"Onboarding a repository is one edit"` phrasing appears nowhere else live — only in two
  `.harness/features/` notes (FEAT-12 review, and my own prior receipt), which are historical record.
