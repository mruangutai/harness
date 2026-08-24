# SC-01 live: the create path against the real GitHub API

BLUF: the live run found a defect no runner could reach, exactly where BRIEF.md said one could
hide. **A brand-new Projects v2 project already carries a `Status` single-select field with
GitHub's own options — `Todo`, `In Progress`, `Done`.** Every fake in this tree answered
`createProjectV2Field` with success, because that is what the mutation does when the field is
genuinely absent. Against the real API it fails.

## Why this run existed

BRIEF.md's `## Verification gaps` stated it plainly AS SIGNED (quoted here as the warrant for this
run; that sentence was itself corrected on 2026-08-23 once these runs proved its first half, and the
`:198-200` anchor the original draft of this note carried has since moved): "What is therefore NOT proven by any runner: that the real
GitHub API accepts the provisioning mutations, and that the reconciliation moved the cards the
operator sees." SC-01's own evidence is `unit`. The operator authorised a live run to close the
first half.

## The fixture, and why it needed two commits to exist

`provision --repo <other>` resolves that repo's declaration through `fleet.yaml`
(`board_lifecycle.py:276-281`), and `mruangutai/harness` is deliberately absent from that file
under DEC-174 am.1. So a live create-path run needed a fleet member that was not the harness and
not a live product: `mruangutai/harness-factory-smoke`, added as a KEPT FIXTURE, with its own
`.harness/harness.json` on `main` declaring board number **99** — a number that does not exist
under `mruangutai`, which is the only signal `project_resolve` trusts to enter the create branch.

Confirmed free before spending anything: `projectV2(number:99)` returns `NOT_FOUND`, and
`project_resolve` re-parses that error's own stdout for a `data` key and returns `None` rather
than raising (`factory_gh.py:515-531`) — so the create branch really is reachable.

## Two refusals, both correct, both on first contact

**Attempt 1 — the declaration was wrong and the tool said exactly how.** The first fixture
`harness.json` carried `board` at the document root instead of under `github`. Exit 2:

```
factory: board_lifecycle: product config missing board: github.board — declare github.board in
mruangutai/harness-factory-smoke@main:.harness/harness.json
```

It named the key, the repo, the ref and the path. Nothing was written.

**Attempt 2 — the create and link landed, the field did not.** Exit 4:

```
factory: board_lifecycle: created project 7 on mruangutai and linked
mruangutai/harness-factory-smoke, but failed to create field 'Status' -- gh api graphql failed:
api graphql — gh: Name cannot have a reserved value, Name has already been taken; the project
EXISTS and is LINKED (record 7 in mruangutai/harness-factory-smoke's harness.json now to avoid a
duplicate on retry) -- re-run provision once the failure is resolved and it will create the field
on the recorded project
board_lifecycle: no project 99 on mruangutai -- created project 7
board_lifecycle: linked mruangutai/harness-factory-smoke to project 7
```

**Everything about that exit code is what fix cycle c1's MUST-FIX 2 argued for, working on its
first real failure.** Not exit 2 — a project really was created, so "nothing mutated" would be a
lie. Not exit 3 — the run did not cleanly finish. The created number reaches stdout BEFORE the
failing call, and stderr names it again with the instruction to record it, so a retry cannot enter
the create branch a second time and produce a duplicate board. That reasoning was written against
a fake; the real API validated it unchanged.

## The measurement itself

Project 7 read back on 2026-08-23:

| field | type | options |
| --- | --- | --- |
| Status | ProjectV2SingleSelectField | Todo, In Progress, Done |
| Title, Assignees, Labels, Linked pull requests, Milestone, Repository, Reviewers, Parent issue, Sub-issues progress, Created, Updated, Closed | ProjectV2Field | — |

So `field cannot already be taken by a wrong-type field` — fix cycle c2's own comment on why the
fresh-board path skipped `_field_probe` — is false. The field is taken, by the right type, with
the wrong options. The saved network call was the whole defect.

## The ruling

On a project the SAME RUN created, set the station field to EXACTLY the declared stations,
deleting `Todo` and `In Progress`. Safe there and nowhere else: a brand-new board holds no items,
so no card can lose its column. The resolved-project path keeps its `existing + missing` union
untouched — deleting an established board's column is the disaster
`project_single_select_extend`'s replace semantics make possible, and T-03 already ruled on it.

Carried out as fix cycle c3.

## Project 7 is kept, and the c3 verification creates a second board

Project 7 is the failed output of the defect above: created, linked, and carrying GitHub's
default `Status` options because the field creation was rejected. It holds zero items.

Deleting it and re-running would have re-used number 99 for a clean single proof. The operator
ruled against the delete, so the c3 verification leaves 7 standing and creates a second board
instead. The declaration still names 99, which does not exist, so `provision`'s create branch
fires again without any edit to the fixture.

That leaves two boards under `mruangutai` for one repository, which is worth stating rather than
tidying away: **7 is the pre-fix artifact and the second is the post-fix proof.** Keeping both is
the more useful record — 7 shows what a fresh board looks like before the tooling touches it,
which is the measurement the whole fix rests on, and no fake in this tree can reproduce it.

## SC-01 proven live, both halves (2026-08-23, after fix cycle c3)

SC-01 reads: "Running the provisioner against an owner with no board creates the project, creates
the Status field carrying all six declared station option names byte for byte, and links the
repository; running it against an existing board adds only the options that are missing."

### Half one — the create path, ONE run

```
$ python3 .claude/skills/harness/bin/board_lifecycle.py provision --repo mruangutai/harness-factory-smoke
EXIT:3
board_lifecycle: no project 99 on mruangutai -- created project 8; record number 8 in mruangutai/harness-factory-smoke's harness.json
board_lifecycle: linked mruangutai/harness-factory-smoke to project 8
board_lifecycle: field 'Status' already existed on the new project (GitHub's default) -- replaced its options with exactly the 6 declared: Backlog, Plan, Ready, Building, Review, Done; REMOVED 2: Todo, In Progress
```

Board 8 read back through `projectV2(number:8)`:

- `repositories`: `["mruangutai/harness-factory-smoke"]` — linked.
- `Status` is a `ProjectV2SingleSelectField`.
- options: `['Backlog', 'Plan', 'Ready', 'Building', 'Review', 'Done']` — compared to the declared
  list with `==` in declaration order: **True**. `Todo` absent, `In Progress` absent.

All three of SC-01's first-half conjuncts, in one run, against the real API.

### Half two — the existing board adds ONLY what is missing

Board 8's number was recorded in the fixture's `harness.json`, exactly as exit 3 instructs. The
re-run is idempotent:

```
EXIT:0
board_lifecycle: nothing to do
```

Then the union path was set up **by a direct GraphQL mutation, not by the code under test**, so the
setup could not launder the result. Board 8's `Status` was set to
`Icebox, Backlog, Plan, Ready, Building, Review` — one option the operator owns and never declared,
and one declared option (`Done`) missing. Re-run:

```
EXIT:0
board_lifecycle: added 1 option(s) to 'Status': Done
```

Board 8 read back: `Icebox Backlog Plan Ready Building Review Done`.

**Exactly one option added, and `Icebox` survived.** That is the second half of SC-01, and it is
also the live proof of the disaster the whole `_extend_to_union` design exists to prevent:
`project_single_select_extend`'s mutation REPLACES an option set, so a path that passed the bare
declared list here would have DELETED the operator's own column. `Icebox` is left on board 8
deliberately, as the standing evidence that it does not.

### What the live runs cost, and what they found

Four runs. Two refusals (both correct, both naming the exact key or the exact failure), one
genuine defect no fake could reach, and one clean pass of both halves. The defect —
a fresh board's default `Status` field — had survived every unit and integration test in the tree,
because a fake that answers `createProjectV2Field` with success is answering the question the real
API never asks.
