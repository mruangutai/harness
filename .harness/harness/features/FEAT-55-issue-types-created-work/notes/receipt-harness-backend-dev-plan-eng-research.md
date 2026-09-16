# Backend eng research — FEAT-55 issue types — plan step 1

BLUF: the mechanism is real (GraphQL `createIssue`/`updateIssue` take `issueTypeId`, measured
against `mruangutai/harness`), no `gh` CLI flag exists for it, the CLI-vocabulary mapping has one
real gap (`infra`/`ci` are dead chore values, and six of ten `change_type`s have no settled nature),
crash-safety is receipt-only for four of five routes but `cmd_backlog` has no receipt mechanism at
all today, and DEC-138 should be amended in place, not superseded — but that amendment is an
in-place REWRITE of DEC-138's Mapping paragraph, never an appended `DEC-138 amendment 8` (DEC-205
ended that shape). Separately: capability detection is itself a read-back GitHub state requires
under every crash-recovery option, needing a new enumerated purpose in `github-mirror.md` and in
DEC-203's own identical list. Every claim below is anchored; `[INFERENCE]` marks reasoning without
a direct measurement.

## 1. Creation routes — five, confirmed, no sixth

- Feature parent: `.claude/skills/harness/bin/gh-sync.py:941-943` — `gh(["issue", "create", "--repo", repo, "--title", title, "--body", body, "--label", "harness"])`.
- Planned task sub-issue: `gh-sync.py:957-967` — `labels = ["harness"] + ([type_label(task["change_type"])] if type_label(...) else [])`, then `args = ["issue", "create", ...]` with one `--label` per label.
- Ship-review backlog issue: `gh-sync.py:1410-1429` (`cmd_backlog`) — `labels = ["harness"] + ([nature] if nature != "enhancement" else [])`.
- Factory parent: `.claude/skills/harness/bin/factory_decompose.py:421-424` — `factory_gh.create_issue(args.repo, title, body, ["harness", f"feature:{feat_id}"])`.
- Factory task: `factory_decompose.py:433-436` — `factory_gh.create_issue(args.repo, title, _issue_body(t), _task_labels(t, feat_id))`, where `_task_labels` (`factory_decompose.py:325-332`) appends `chore`/`bug` from its own `CHORE_TYPES`/`BUG_TYPES`.

Grep for `issue create|create_issue` across `.claude/skills/harness/bin/**` returns exactly these
five call sites (two in `gh-sync.py`'s `cmd_open`, one in `cmd_backlog`, plus `factory_gh.create_issue`
called twice from `factory_decompose.py`) and one definition site, `factory_gh.py:198-211`. No sixth
route exists — every other `gh` invocation under `bin/` is `label create`, `issue edit`, `issue view`,
or a GraphQL query, none of which create an issue.

**`ensure_labels` is two implementations** (`gh-sync.py:871-887` vs `factory_gh.py:186-195`, D-04) and
the type path does **not** need to duplicate that split. Evidence: `gh_issues.py` is already a shared
argv-builder module imported by BOTH `gh-sync.py:87` (`from gh_issues import internal_id_args, ...`)
and `factory_gh.py:28` (`import gh_issues`) — the "three stay three" callers already share one
argv-building library today. The type-name-to-native-type mapping, the capability-detection GraphQL
query text, and the response-parsing logic have no reason to differ between the two callers and can
live in one new shared module on the `gh_issues.py` pattern, imported by both `gh-sync.py` and
`factory_gh.py`. Only the invocation glue stays separate (three callers, `gh()`/`skip()` in
gh-sync.py vs `run_gh()`/`GhError` in factory_gh.py) — the same shape `ensure_labels` already has.

## 2. The API, measured

- `gh --version` → `gh version 2.92.0 (2026-04-28)`.
- `gh issue create --help`: flags are `-a/--assignee -b/--body -F/--body-file -e/--editor
  -l/--label -m/--milestone -p/--project --recover -T/--template -t/--title -w/--web`. **No `--type`
  flag exists.**
- `gh issue edit --help`: flags are `--add-assignee --add-label --add-project -b/--body -F/--body-file
  -m/--milestone --remove-assignee --remove-label --remove-milestone --remove-project -t/--title`.
  **No `--type` flag exists either.** The CLI cannot set a native type at this version; every path
  MUST go through `gh api graphql`.
- Capability detection, run against `mruangutai/harness`:
  `gh api graphql -f query='query($owner:String!,$name:String!){ repository(owner:$owner,
  name:$name){ issueTypes(first:10){ nodes { id name } } } }' -f owner=mruangutai -f name=harness`
  → literal response: `{"data":{"repository":{"issueTypes":null}}}`. Exit 0, no top-level `errors`
  key. This matches #1289's prior finding, reconfirmed at this pin.
- Query-failure shape, measured against a repository that does not resolve:
  `gh api graphql -f query='query{ repository(owner:"mruangutai",
  name:"this-repo-does-not-exist-xyz123"){ issueTypes(first:5){ nodes { id name } } } }'` →
  `{"data":{"repository":null},"errors":[{"type":"NOT_FOUND","path":["repository"],...,"message":
  "Could not resolve to a Repository with the name '...'."}]}` plus a duplicate line on stderr
  (`gh: Could not resolve to a Repository...`), **exit 1**.
  **The discriminator is the shape, not the null alone**: a genuine "repository does not support
  Issue Types" response is exit 0, top-level `errors` key **absent**, and `data.repository.issueTypes`
  is JSON `null`. A query failure (bad repo, auth, rate limit, network) is exit non-zero with a
  top-level `errors` array present and a message — the same "match on message text, never on exit
  code alone" discipline `factory_gh.py:36-40`'s `_RATE_LIMIT_MARKERS` already uses for a different
  failure class, so the detector should reuse that pattern rather than invent a second one.
- Assignment mechanism, measured via schema introspection (no live mutation run — read-only):
  `__type(name:"CreateIssueInput"){ inputFields { name } }` → includes `issueTypeId` (alongside
  `repositoryId, title, body, assigneeIds, milestoneId, labelIds, ..., parentIssueId, ...`).
  `__type(name:"UpdateIssueInput"){ inputFields { name } }` → includes both `issueTypeId` and
  `issueType`. So `createIssue` sets the type at creation time via `issueTypeId`; `updateIssue`
  can set it after the fact via either `issueTypeId` (node id) or `issueType` (name-keyed, exact
  shape not further probed — read-only budget spent on the field that matters, `issueTypeId`).
- **No feature-preview `Accept` header was needed** — every query above ran as a plain
  `gh api graphql` call with no extra header and succeeded (or failed with the expected GraphQL
  error), measured, not assumed.

## 3. Total mapping coverage

- `test_matrix` keys (`.harness/harness.json`, measured via `json.load`): `ai_behavior, api, bugfix,
  config, cross_module, docs, feature, frontend, logic, scaffolding` — 10 values.
- `templates/PLAN.md:49-51` enum: `logic | api | cross_module | frontend | feature | bugfix |
  ai_behavior | config | scaffolding | docs` — the same 10, same set.
- `gh-sync.py:102` `CHORE_TYPES = {"config", "scaffolding", "infra", "ci"}` and
  `factory_decompose.py:48` (identical set), `BUG_TYPES = {"bugfix"}` (`factory_decompose.py:49`).
  **Disagreement, named explicitly: `infra` and `ci` are NOT legal `change_type` values** in either
  of the two authoritative vocabularies above — they are dead/legacy spellings baked into both
  label-mapping modules that the settled contract's "every value maps, none falls through" rule
  must not silently perpetuate.
- Backlog natures (`cmd_backlog`, `gh-sync.py:1421`): exactly `bug | chore | enhancement`, a
  **third, independent vocabulary** (not `change_type`).
- Value → default-type table implied by the settled mapping:
  - `bugfix` → `Bug` (defect, unambiguous — the only value under `BUG_TYPES`).
  - `feature` → `Feature` (user-visible capability, unambiguous — the value literally names the
    bucket). Feature parents and factory parents also default to `Feature` per the settled rule.
  - `config`, `scaffolding` → `Task` (chores, unambiguous, currently mapped to the `chore` label).
  - `infra`, `ci` → **no mapping possible**; they are not members of the current `change_type`
    enum at all (see disagreement above) — flag for removal from `CHORE_TYPES`/`BUG_TYPES`,
    not for a type assignment.
  - `logic, api, cross_module, frontend, ai_behavior, docs` (6 of 10 legal values) → **genuinely
    ambiguous**, and this is an open question for the operator, not for a dev to settle: these six
    describe the SHAPE of a change (which layer/kind of code moved) rather than its NATURE
    (defect vs. capability vs. chore), which is the axis the settled three-way split actually
    classifies on. A `logic` or `api` change is exactly as often an internal refactor (chore-like,
    → `Task`) as it is the mechanism behind a user-visible capability (→ `Feature`). Backlog's
    `enhancement` nature maps unambiguously to `Feature` (settled: "capabilities and enhancements").
  - Backlog natures: `bug` → `Bug`, `chore` → `Task`, `enhancement` → `Feature` — all three map
    cleanly, unlike the six ambiguous `change_type` values above.

## 4. Crash safety and the DEC-138 tension

- `gh-sync.py:966` saves the created sub-issue number **immediately** (`save_recorded(feat_dir,
  rec)`, comment: "after EVERY create — a crash mid-loop must not orphan issues"); the parent gets
  the same treatment at `:943-944`. Attachment to the parent is a **separate** receipt
  (`rec["attached"]`, `:971-977`), saved after its own step.
- `factory_decompose.py` mirrors this exactly: `write_factory(feat_dir, factory, feat_id=feat_id)`
  runs immediately after `factory_gh.create_issue` for both the parent (`:424-425`) and every task
  (`:436-437`).
- `cmd_backlog` (`gh-sync.py:1410-1429`) has **no local receipt at all** — it is a one-shot,
  no-milestone, no-feature-tracked call with no idempotency guard today; a rerun with the same
  item list already creates duplicates before this feature touches anything. This is the one route
  where "receipt-only" crash safety does not exist to extend — it must be **added**.
- DEC-138 (`DECISIONS.md:2984-2991`, "`open` creates one sub-issue per `T-NN`... adopted-or-created
  but never discovered") explicitly **rejects a parent-discovery read** as a second, contradictory
  source of truth. `github-mirror.md:7-18` bounds every read-back to seven enumerated purposes, and
  parent/issue existence-by-search is not one of them.
- **Capability detection is itself a read-back, required under EVERY option below — not contingent
  on which crash-recovery option is chosen.** The `issueTypes` query measured in section 2 reads
  GitHub state and is not one of `github-mirror.md:7-18`'s seven purposes, nor of DEC-203 item 5's
  identical list (`DECISIONS.md:6064-6077`, "The read-back bound, carried forward and now SEVEN
  purposes"). The settled contract's loud pre-create refusal also needs to read WHICH types the
  repository declares — but the measured query already answers both in one call:
  `issueTypes(first:10){ nodes { id name } }` is JSON `null` when the repository has no native
  types, and a non-null `nodes` array names every declared type otherwise. **One new purpose row
  covers both**, not two. Row, in the table's own voice: `| whether a target repository supports
  native Issue Types, and if so, which types it declares | the type-apply path shared by
  \`gh-sync.py\` and \`factory_decompose.py\` (the shared capability module recommended in
  section 1) |`. Where the value lands: process-local state for that invocation, feeding the
  `issueTypeId` mutation argument and the refusal message text, then — under option (a) below — a
  `typed` receipt flag in `feature.yaml`/`factory.yaml`. It never reaches `BRIEF.md`, `plan.yaml`,
  or any approval block: DEC-138's asymmetric-truth boundary (`:2939-2944`, "issue state is never
  read back into an approval-gated artifact") holds unchanged, and `github-mirror.md:20`'s
  restatement ("No read-back ever reaches an approval-gated artifact... unconditional") covers it
  the same way it covers the existing seven.
- **Option set for the orchestrator, on the separate CRASH-RECOVERY question** (the purpose set is
  widening regardless of which option is chosen, per the bullet above — that widening no longer
  distinguishes them; see below for what does):
  - **(a) Receipt-only (recommended).** For the four routes that already save a receipt
    immediately after create, add a `typed` flag (e.g. `rec["typed"][task_id] = True` /
    `factory["typed"][tid] = True`) written immediately after the type-apply GraphQL call
    succeeds, following the exact "create → record number → save" ordering already in place, then
    "apply type → record typed → save" as the next two steps. A rerun reads the already-recorded
    issue number from the local receipt and, if `typed` is not yet set, retries ONLY the type-apply
    mutation (idempotent) — no ADDITIONAL GitHub read beyond the capability detection already
    required above, because the issue number is already known locally. `cmd_backlog` needs a
    **new** small receipt (it has none today) to reach the same guarantee — net-new, not a
    violation of DEC-138's no-discovery-read rule, since it never reads GitHub back to find a
    number.
  - **(b) A further, additional read-back purpose.** After a crash, list/search issues by title or
    label to discover whether the create already happened — what DEC-138 explicitly rejected for
    the parent case. This is a DIFFERENT purpose from detection above (repository-level metadata
    vs. issue-level disambiguation of one specific prior create), so it would need its own row too.
    Widening the bound has precedent (DEC-203 item 4, `DECISIONS.md:6079-6082`) and this read would
    also prove out never reaching an approval-gated artifact, same as (a) and as detection — so
    "does this need a new purpose" no longer separates (a) from (b); (a) needs none beyond
    detection, (b) needs one more regardless.
  - **What now actually distinguishes them: reliability, not purpose count.** (a) resolves a rerun
    from the issue number the four routes already save locally at create time — an exact-key
    lookup. (b) would resolve a rerun by matching title/label text — fuzzy, and defeated by a
    partial create (issue created, crash before type-apply), a title collision, or an edited retry
    title, none of which a locally-recorded id can fail on. Recommendation unchanged: (a) for all
    five routes.
  - `cmd_backlog`'s missing-receipt finding, and the open question about its scope, stand as in
    cycle 1.

## 5. The diagnostic — one per command invocation

- `gh-sync.py cmd_open` and `cmd_backlog` each run inside one `main()` invocation — one Python
  process per `gh-sync.py open <dir>` / `gh-sync.py backlog <dir> <items>` command
  (`gh-sync.py:1666-1791`). A module- or function-scoped flag set at the top of the command and
  printed once (either unconditionally at entry, or on first miss, gated so a second miss is a
  no-op) is process-local and cannot double-print within one invocation.
- Factory parent and factory task creation both happen inside the same single `_main()` call
  (`factory_decompose.py:335-528`, steps 5b and 6) — also one process per `factory_decompose.py`
  invocation, so the same process-local-flag approach applies unchanged.
- **The invocation that prints ZERO**: if the diagnostic is only emitted from inside the
  issue-create branch (i.e., gated on "we actually attempted a create"), a `gh-sync.py open <dir>`
  rerun where every task already has a recorded issue (`rec["issues"]` fully populated, the
  `:951-952` skip branch fires for every task, and the parent is already recorded too) makes **zero**
  create calls and would print zero diagnostics even though the repository's capability is
  unchanged and worth reporting. The detector must be called **once, unconditionally, at the top
  of `cmd_open`/`cmd_backlog`/`_main()`**, not lazily inside the create branch, to guarantee exactly
  one line per invocation regardless of how many (if any) creates actually happen.
- No invocation shape produces TWO diagnostics under a single-flag design, since each command is
  one process and nothing here forks or re-enters the command function.

## 6. Config surface

- Current `github:` block (`.harness/harness.json:357-...`): `{sync: true, repo:
  "mruangutai/harness", board: {owner, number, station_field, stations}}`.
- Template (`.claude/skills/harness/templates/harness.json:160-167`) carries a matching shape:
  `{sync: false, repo: null, board: {...}}` — no divergence found between the two `github` blocks
  beyond the expected unfilled values.
- `tests/unit/test-config-shape-matrix.py` (docstring, `:1-14`) is scoped entirely to `test_matrix`
  shape drift (DEC-212) — it references `PROJECT_CONFIG`/`TEMPLATE_CONFIG`/`DECISIONS_MD` but a
  grep for `github`/`additionalProperties`/`"repo"` inside it returns **no matches**. No schema or
  shape gate constrains the `github` block today; adding a key there is unconstrained by any test.
- Recommended key shape (cheap, reversible — decided here): `github.issue_types: {"<change_type-or-
  nature>": "<Native Type Name>"}`, a flat string→string map keyed by the same vocabulary
  `change_type`/backlog-nature already uses (e.g. `{"bugfix": "Defect", "feature": "Story"}`),
  absent keys falling through to the settled defaults (Bug/Feature/Task). This mirrors the
  `board` sub-object's own flat-map style already in the block.

## 7. Contract documents that must change

- **Correction to the batch's citation**: the phrase "LABELS DERIVE, MECHANICALLY (DEC-138)" lives
  in `gh-sync.py:67-69` (module docstring), **not** in `references/github-mirror.md` — grepping that
  reference file for the phrase returns no match. The reference file's own text (read in full,
  `:1-115`) states the mirror's read-back bounds and command ownership but not the label-derivation
  rule itself.
- Documents asserting the `bug`/`chore` derivation that become false:
  - `gh-sync.py:67-69` (module docstring) and the `type_label()` function itself, `:427-432`.
  - `factory_decompose.py:47-49` ("# DEC-138, applied mechanically per task.") and `_task_labels()`,
    `:325-332`.
  - `DECISIONS.md` DEC-138 entry, `Mapping` paragraph (`:2933-2935`, "issue labeled `harness`, body
    carrying the task spec, `change_type` and `traces:`") and `One source document per GitHub
    construct` paragraph (`:2952-2954`, "labels `harness` + squad").
  - No other SKILL.md/reference/template/`docs/SPEC.md` paragraph asserting this derivation was
    found; `SKILL.md:347-349`'s backlog-nature description states IDs/collation, not the
    label-vs-type mechanism, and stays accurate regardless of this feature.
- **Correction**: cycle 1 left `references/github-mirror.md` off the list above because its
  read-back table (`:7-18`) does not assert the label mechanism — that part still holds. But per
  section 4's finding, that table becomes **INCOMPLETE, not false**: it must gain the new
  detection-purpose row. `DECISIONS.md`'s DEC-203 entry (`:6064-6077`, "carried forward and now
  SEVEN purposes") enumerates the identical seven independently and must gain the same row, for the
  same reason — it is a second, separately-maintained copy of the same enumerated set.
- **How this repo amends a signed decision, sharpened.** `DEC-205` (`DECISIONS.md:6275-6293`)
  **ends the amendment-sub-section convention**: "An entry states current truth directly. A
  correction rewrites the entry it corrects; it does not append a dated sub-section beside it."
  The mechanism for DEC-138 is therefore an **in-place rewrite** of its `Mapping` paragraph
  (`:2933-2935`) to present-tense current truth — not a new `### DEC-138 amendment 8` heading.
  This is a real trap for a planner reading DEC-138 alone: DEC-138's OWN edit history is full of
  exactly that retired shape (FEAT-03 committed "docs(FEAT-03): record the reversed closure
  contract as DEC-138 am.7", and `am.N`/`amendment N` citations to it survive across multiple
  feature directories in the tree today) — DEC-205 prohibits reproducing that shape going forward
  even though DEC-138's history is the closest local precedent for it. Measured: the live
  `DECISIONS.md` file itself carries zero `DEC-138 amendment`/`DEC-138 am.` headings today (grep
  returns no matches) — DEC-138 was already squashed to current-truth prose at some point, so this
  amendment rewrites prose only, it does not need to also collapse a lingering am.N heading.
  Precedent for the rewrite pattern: DEC-191 (`:5296`, "Amended by FEAT-41-one-station-vocabulary —
  the count, not the principle... UNCHANGED — which is exactly why this is an amendment and not a
  strike") and DEC-200 (`:6174`, same pattern for one clause). Recommendation unchanged: rewrite
  DEC-138's `Mapping` paragraph in place; DEC-203's wholesale-supersession pattern
  (`:6031-6036`, three entries collapsed to one) fits an entire-lifecycle restatement, not this
  one-paragraph correction.
- One sentence on the guard: `DECISIONS.md` is policed by exactly one mechanical check —
  **anchor rot** (`DEC-205`, `:6307-6316`: every file-and-line anchor cited must name a file that
  exists and a line within range) — so every anchor this amendment writes, including the two new
  `github-mirror.md`/`DECISIONS.md` read-back rows above, is subject to it.

## 8. Test surfaces

- Label behavior: `tests/integration/test-gh-sync.py` fakes `gh` with a **bash script written to a
  temp path and pointed to by the `GH_SYNC_GH` env var** (`FAKE_GH` heredoc, `:31-56`; wiring at
  `:177-178`, `env["GH_SYNC_GH"] = os.path.join(tmp, "gh")`). The fake logs every invocation
  (`FAKE_LOG`) and returns canned JSON by case-matching the argv text. Label assertions:
  `:768-771` (feature/chore/bug/absorbs on `open`), `:825-834` (backlog nature → label mapping).
  Factory station writes in the same file route through **`FACTORY_GH`** instead (`:1505-1508`,
  `:1799-1801`, `:1863-1865`), a second env var read by `factory_gh.py`, not `gh-sync.py`.
- Factory creates: `tests/unit/test-factory-gh.py` **monkeypatches `fgh.subprocess.run` directly**
  with an in-process recorder (`recorder()`, `:54-66`) — no real `gh` spawned, classified UNIT for
  that reason (docstring `:1-8`). `create_issue` label-passing assertions at `:300-308`.
  `tests/integration/test-factory-decompose.py` section 5 (`:466-481`) asserts `chore`/no-`bug` on
  a config-vs-feature task pair, going through the same `FAKE_GH`/`GH_SYNC_GH`-style fixture as
  `test-gh-sync.py` (integration-classified for the same subprocess-spawn reason).
- **What a test could prove without an enabled repository**: extending either fake (the bash
  script's case-match, or the Python recorder's canned `Result` list) to return a non-null
  `issueTypes` node list for the capability query, and a success response for the
  `createIssue`/`updateIssue` mutation carrying `issueTypeId`, would prove the CODE's own behavior
  is correct given that response shape — that it calls the right query/mutation, correctly omits
  `bug`/`chore` labels when the canned response says types are active, and correctly resolves the
  configured type name through overrides.
- **What it structurally cannot prove**: that GitHub's REAL API, on a REAL Issue-Types-enabled
  repository, actually returns that exact shape, accepts `issueTypeId` on `createIssue` without
  rejecting it for a reason invisible to introspection (e.g. an organization-scoped type not valid
  for a given repo, a type name collision, or a future schema change), or that the live cost/rate
  characteristics match what a canned fixture assumes. Introspection here confirms `issueTypeId` is
  a real, present field on both mutations' input types — that is measured, not inferred — but its
  *acceptance in a real live create/update call against an enabled repository* was never run
  because no such repository exists in this environment (`mruangutai/harness` returns `issueTypes:
  null`, confirmed above). Any success criterion phrased as "verified against an Issue-Types-enabled
  repository" cannot be satisfied by any fixture built here; it needs either operator access to a
  real enabled repo, or its acceptance criterion narrowed to "the code issues the correct
  query/mutation shape against a canned response," which is what the fixtures above can actually
  prove.
