# Research — FEAT-22 docs layout migration (map #336 unit 4)

**Base: `0f12f14` — the dispatch pin RECONCILES.** `git rev-parse HEAD` = `0f12f14c166d…`, log head
`0f12f14 FEAT-21 terminal: status Done after ship acceptance and merge (#416)`. The `cf3af8f` in the
upstream session snapshot is stale by two commits. Every figure below was measured at `0f12f14`.

## BLUF

Unit 4 is **larger than the dispatch's three-item cluster** and its shape is decided by two
measurements, not by judgement:

1. **The destination is UNGRANTED.** `check-domain.sh --resolve .harness/harness/docs/SPEC.md` →
   `NOBODY`. Nothing in the repo may write the harness docs after the move. The grant must land in
   the same commit, mirroring FEAT-21's signed wildcard shape (`.harness/*/features/**` →
   `.harness/*/docs/**`). FEAT-21's ship review B-16 is the recorded cost of shipping a path without
   its grant.
2. **A DEC-174 file IS touched, and so is a signed decision's ruling text.** `check-state.sh:676`
   and `check-domain.sh:953` each carry one diagnostic string naming `docs/harness/DECISIONS.md`,
   and **DEC-189's ruling enumerates `docs/harness/**` as one of the four named control-plane
   paths** — the move falsifies that sentence.

## Premise corrections to the dispatch (all measured)

| Dispatch claim | Measured at `0f12f14` |
|---|---|
| `tests.yml` Layout-gate expectation "flips to docs: CLEAN — evidence migrated" | **FALSE, and the dispatch already says so — confirmed.** `.github/workflows/tests.yml:183-233` asserts only the two line SHAPES (:202, :209), non-zero counts (:219-230) and the checker exit code (:233). Real constraints: `doc_roots >= 1`, checker exit 0 |
| harness_boundary: "two verbatim-quoting comments at :198 and near :89" | **Three sites match the row's legacy regex `docs/harness/\*\*`: :84 (comment), :90 (the code entry), :221 (a DOCSTRING, not a comment).** :198 does not contain `docs/harness` at all |
| 755 occurrences / 192 files | **753 occurrences / 191 files tracked at the pin** (`git grep -o`, `git grep -l`). 755/192 is the WORKING TREE including 8 untracked review notes. Both are right under their own definition |
| ~30 files in the per-file audit | **35**, because the slash grep misses the `os.path.join("docs", "harness")` spelling. `.claude` is **22 files, not 17** |

## The union partition — state this rule, audit it, never sweep

Pattern audit for the partition itself (P-12: the weakest fragment every stale site necessarily
contains). Two spellings exist and neither subsumes the other:

```
git grep -lE 'docs/harness|"docs", ?"harness"' 0f12f14 -- .     -> 196 files
git grep -lE 'docs/harness'                    0f12f14 -- .     -> 191 files
git grep -lE '"docs", ?"harness"'              0f12f14 -- .     ->  15 files (5 unique)
```

Broader control `docs["/ ,]{1,4}harness` on `harness_boundary.py` adds **zero** lines over
`docs/harness` — no third spelling exists in that file.

| Partition | Files | Disposition, by rule |
|---|---|---|
| `.harness/harness/**` feature dirs | 158 | **knowing survivors** — shipped records of what was true |
| `.harness/logs/**` | 3 | **knowing survivors** — dated log entries |
| `.claude/**` | **22** | per-file audit |
| `.harness/notes/**` | 7 | per-file audit (6 are dated grillings/handoffs = survivors; `audit-decisions.py` is live code) |
| `.harness/expertise/**` | 2 | per-file audit + a lane decision |
| `docs/harness/**` | 3 | self-references that move with the files |
| `CLAUDE.md` | 1 | instruction-side, takes the literal new path |
| **audit total** | **35** | survivors: **161** |

The five files the slash grep alone misses — `test-check-state.py`, `test-factory-config.py`,
`test-harness-yaml.py`, `test-layout-migration.py`, `test-team-catalog.py` — are exactly the ones
that break at runtime. That is the finding, not a bookkeeping nit.

## The 22 `.claude` files, classified by MECHANISM

Path-spelling is not the axis that matters. Four classes:

**(a) runtime-breaks — a real-file read that 404s after the move**
- `test-harness-yaml.py:686` (real `SPEC.md`), `test-team-catalog.py:45` (real `SPEC.md`),
  `test-validate-digest.py:24` (real `SPEC.md`), `test-gen-decisions-index.py:23,24` (real
  `DECISIONS.md` + index), `test-no-distribution.py:89,210,228,244` (real `DECISIONS.md`, index,
  `EXCLUDED_EXACT`), `test-factory-config.py:399` (probe assertion against the real root).

**(b) semantics-flip — the path string may or may not change, the EXPECTATION inverts**

After `HARNESS_CONTROL_PLANE`'s docs entry becomes `.harness/harness/docs/**`, `docs/harness/x`
stops being a control-plane target, so in the harness base the documentor's `docs/**` grant match is
**discarded** (`harness_boundary.classify`, the `target_side_test` filter). These assert the OLD
semantics:
- `test-check-domain.py:35` (`docs/harness/guide.md` expects exit 0), `:712-732` (the "all four
  named entries resolve" case and the "not widened to `docs/**`" case), `:789` (LIVE-tree
  `--resolve docs/harness/SPEC.md` expects `harness-documentor`), `:801-826` (the symlink-escape
  fixture builds a `docs/harness` tree), `:519`.
- `test-bash-write-guard.py:85,87,89,107,110` — the comment at :107 states the reason verbatim:
  "granted AND control-plane, so it exits 0 alone".
- `test-check-plan-routes.py:117,224-283` — asserts `docs/harness/SPEC.md` is granted.
- `test-factory-integration.py:28,329-333` — builds the `docs/harness/SPEC.md` probe fixture.
- `test-check-state.py:1619` — builds a `docs/harness` fixture dir.

**(c) knowing code survivors — the legacy string is the POINT**
- `layout_fixtures.py:46,50,54` — the `legacy` side of three two-sided fixtures.
- `layout_migration.py:6,34,94,97,100,174` — the reader table's own legacy patterns and the
  `_evidence` marker. **Unit 4 must NOT delete these**: they are how the detector recognises the
  pre-state. `:34` (the docstring's own account of the gen-decisions-index row) was flagged here as
  the one line unit 4 may need to touch once the HEADER template is fixed; **that is withdrawn** —
  see "Disposition: `layout_migration.py:34` stays" at the end of this note.
- `test-layout-migration.py:77` — the legacy fixture builder.

**(d) instruction-side literals — take the new path**
- `CLAUDE.md` (resolve: NOBODY), `.claude/skills/harness-principles/SKILL.md` (NOBODY),
  `.claude/skills/harness/templates/plan.yaml:44` (NOBODY), `check-plan-routes.py:44` (a comment),
  `check-domain.sh:953` + `check-state.sh:676` (diagnostic prose, both DEC-174).

## The coupled cluster, re-verified

| Site | Measured | Migrated form the READER_TABLE requires |
|---|---|---|
| `factory_config.py:32` `_PROBE` (read :41, :45; docstring :11, :13) | confirmed | must match `os\.path\.join\("\.harness", [^,)]+, "docs"` |
| `harness_boundary.py:90` `HARNESS_CONTROL_PLANE[0]`, comment :84, docstring :221 | **3 sites**, not 2 | must match `\.harness/[^/"]+/docs/\*\*` |
| `gen-decisions-index.py:20` `DOCS_DIR` → `:21 DECISIONS_PATH`, `:22 INDEX_PATH`; HEADER template `:76`; docstring `:2,5,10` | confirmed | must match `os\.path\.join\("\.harness", [^,)]+, "docs"` OR `\.harness/[^/ ]+/docs/` |

`gen-decisions-index.py:76` is inside the HEADER string literal and its output is live in
`docs/harness/DECISIONS-INDEX.md:8`. **Regenerate in the same commit** or the committed index carries
a stale header.

**Detector-invisible sites in `harness_boundary.py`** — carry `docs/harness/` but NOT
`docs/harness/**`, so the row's legacy regex never sees them: `:111` (symlink-escape example),
`:143` and `:151` (both name `docs/harness/SPEC.md` as factory_config's probe — both go stale the
moment `_PROBE` moves), `:315` (`docs/**` grants `<harness>/docs/harness/guide.md`). These are the
residual bound the module docstring names, live. Assign them to the task, not to the sweep.

## Writers into `docs/harness/` — every one dispositioned

Only **one program writes into that directory**: `gen-decisions-index.py`, via `INDEX_PATH`
(`:22`). Everything else that constructs a `docs/harness` path either reads, or builds a fixture
under `tmp`.

**`org.html` has no writer.** It is hand-maintained — measured, not assumed: FEAT-08's documentor
receipt records "`org.html` is hand-maintained (no generator or template)"
(`.harness/harness/features/FEAT-08-remove-cost-tracking/observations/harness-documentor.md:250`),
and the only diff ever taken against it is three hand hunks (`:171`). `grep -rn "org\.html"` returns
no writer outside feature records. **It is tracked** (`git ls-files docs/harness` lists it), so it
moves and it counts in the emptiness criterion.

`git ls-files docs/harness` = 5 files: `BUILD.md`, `DECISIONS-INDEX.md`, `DECISIONS.md`, `SPEC.md`,
`org.html`. `docs/harness/.DS_Store` and `docs/.DS_Store` exist **untracked** — which is exactly why
the criterion is tracked-files-empty and never directory-absent.

## Lanes — measured with `--resolve` at `0f12f14`

```
docs/harness/{SPEC,DECISIONS,DECISIONS-INDEX,BUILD}.md, org.html  -> harness-documentor
.harness/harness/docs/SPEC.md                                     -> NOBODY   <-- the gap
.claude/skills/harness/bin/{factory_config,harness_boundary,
   gen-decisions-index,layout_migration,layout_fixtures,
   check-domain.sh,test-*}                                        -> harness-backend-dev harness-dev-ops
.github/workflows/tests.yml                                       -> harness-dev-ops
.harness/team-config.yaml                                         -> NOBODY
CLAUDE.md                                                         -> NOBODY
.claude/skills/harness-principles/SKILL.md                        -> NOBODY
.claude/skills/harness/templates/plan.yaml                        -> NOBODY
.harness/expertise/harness-documentor.md                          -> harness-documentor
```

**DEC-174, plainly: YES, two files are touched** — `check-state.sh:676` and `check-domain.sh:953`,
one diagnostic prose line each. Neither is a path resolution; both are user-facing staleness.
Folding them costs nothing extra, because four other surfaces (`team-config.yaml`, `CLAUDE.md`,
`harness-principles/SKILL.md`, `templates/plan.yaml`) already resolve NOBODY and force a
main-session segment regardless.

`harness_boundary.py` is **carve-out by content under DEC-193** (opened at index row 211): it is the
single shared module both PreToolUse write routes import, and its `classify()` decides the same
verdict for the hook path and for `--resolve`. Its own green cannot vouch for it.

## What is NOT unit 4

- **`READER_TABLE` needs no row edit.** Confirmed by reading `layout_migration.py:93-101`: every
  DOCS row already carries its `migrated` regex. Leave.
- `docs/PRINCIPLES.md` stays global (map #336 ruling). It is not under `docs/harness/`.
- `gh-sync.py`, `branch-create-gate.sh`, `validate-feature-json.py`, `factory_claim.py`, the
  gitignore snippet and prose: **unit 9**.
- **No `fleet.yaml` edit.** Segment `harness` comes from `harness.json` `github.repo`
  (`layout_migration._declared_segments`), and the features surface already reads
  `CLEAN — evidence migrated` on it — the segment machinery is proven live.

## Open for the user

- **DEC-189's ruling text names `docs/harness/**` as one of the four control-plane paths.** After
  the move that sentence is false of the tree. DEC-188 strikes only a flatly contradicted decision;
  this rule survives with a changed spelling, so it is an **amendment** — and an amendment to a
  signed decision is authored under the user's signature, not by pm. Carried as D-05 and T-08.
- **The Expertise lane.** `.harness/expertise/harness-backend-dev.md` and `harness-documentor.md`
  carry present-tense `docs/harness` claims and are injected into every spawn of those roles, but
  Expertise writes are distillation-only (DEC-125/DEC-145). FEAT-21 did this identical correction
  **inside a cluster commit with no task naming it** — ship-review B-8, raised independently by two
  reviewers as a structural gap. Carried as D-04 and T-07 so the correction is named.

## Backlog

- **#399-range B-1 (two-segment fixture) — DECLINED, with reason.** B-1's one-fixture change lands
  in `test-check-state.py` and `test-check-plan-routes.py` against the **features** surface
  discovery, and pins D-08, a FEAT-21 decision. Folding it would put a features-surface test change
  inside a docs-surface atomic commit — the precise coupling map #336 exists to prevent, and it
  would make this commit's review the enormous-PR problem again. It stands as its own unit and
  loses nothing by waiting.
- **B-10's docs analogue is FOLDED** — SC-05's `--resolve` pair becomes a standing case in
  `test-check-domain.py` rather than a manual measurement, so the criterion carries automated
  evidence.

## Which runner produces which evidence kind — measured, because the glob disagrees

`harness.json` `test_kinds` and `run-unit-tests.sh` do **not** agree, and the runner is what
executes. `run-unit-tests.sh:17-18` holds two explicit arrays:

| Suite | `harness.json` detect | `run-unit-tests.sh` array | Kind an SC must declare |
|---|---|---|---|
| `test-layout-migration.py` | `unit` (the `test-*.py` glob) | `UNIT_SCRIPTS` | **unit** |
| `test-check-domain.py` | `unit` (the same glob) | `INTEGRATION_SCRIPTS` | **integration** |
| `test-gen-decisions-index.py` | `unit` (the same glob) | `INTEGRATION_SCRIPTS` | **integration** |

`integration`'s own detect list names only four files and does not include either of the two
integration-run suites above. Declaring `evidence: unit` for a criterion that will be proven by
`--kind integration` is FEAT-21 ship-review drift B-12 #2 in reverse: the kind names a runner that
never runs the test. Every SC in the BRIEF names the runner that will really produce its evidence.

## Baselines (all at `0f12f14`, working tree clean of tracked changes except `.harness/logs/`)

```
python3 .claude/skills/harness/bin/layout_migration.py   ->  exit 0
features: CLEAN — evidence migrated
docs: CLEAN — evidence legacy
examined 21 feature dir(s), 1 doc root(s), 7 reader file(s)
layout: 2 surface(s) clean, 0 mixed, 0 cannot-verify
```

`git ls-files docs/harness | wc -l` = **5**. `git ls-files .harness/harness/docs | wc -l` = **0**.

---

## Send-back 1 (2026-08-15): the T-05 / T-10 contradiction, and what settled it

**Conclusion first.** T-05 and T-10 contradicted because T-10's control was an EXCLUSION list, and
an exclusion cannot express "one literal survives here". Replacing it with an exact per-file line
COUNT resolves both directions: deleting the survivor reds T-10, and a stale site inside an
excluded file no longer hides. Two survivors exist, not one — the second was found by reading, not
inferred.

**Survivor 1 — `test-check-domain.py`, exactly 1 line.** The refused-direction case's path argument
`docs/harness/guide.md`. A test that the legacy path is now REFUSED cannot be written without
naming it. Same class as the detector's own fixtures: the string IS the assertion.

**Survivor 2 — `test-check-state.py:1619`, exactly 1 line, and T-05 previously said to MIGRATE it.**
The comment at `:1610-1614` states the rule in the file's own words: "LEGACY on purpose: case_x's
reader stubs are all legacy-form, so its evidence must be legacy too". `:1599` builds `STUBS` from
`lf.STUB[...]["legacy"]`. Migrating the evidence while the readers stay legacy pairs migrated
evidence with legacy readers and silently changes what x.1 and x.3 pin. The file's only other docs
site, `:1643`, is already migrated form — so the file has **no edit at all** in this feature and was
dropped from T-05's `files:` list.

**Zero survivors, verified per file, in the other three T-05 files.** `test-bash-write-guard.py`
(5 lines) — `:107-110` needs a path that is granted AND control-plane so the first operand exits 0
alone; after T-03 only the NEW path is both, so all five repoint. `test-check-plan-routes.py`
(6 lines) — all are fixture plan bodies asserting a GRANTED path, plus the wildcard case at `:117`
whose verdict is path-independent. `test-factory-integration.py` (4 lines) — the `_PROBE` fixture,
which must track `_PROBE` or CLAUDE_PROJECT_DIR redirection stops being exercised.

### Three further defects found while reconciling, all folded into the same tasks

1. **Two fixture manifests need the new grant, not just the new path.** `test-check-domain.py`'s
   case-C fleet (`:698-712`) and the symlink-escape fixture (`:811-817`) both declare an inline
   `team-config` granting the documentor `docs/**` only. Repointing the subject without adding
   `- { path: .harness/*/docs/**, upsert: true }` makes the granted half refused for want of a
   grant rather than by the rule — the pair would then prove nothing. `docs/**` must be KEPT: the
   not-widened half needs the same persona still holding it.
2. **`test-check-domain.py:785-788`'s comment is falsified by T-02, not by T-03.** It argues the
   live `--resolve` case is discriminating because "no `docs/harness/**` entry exists anywhere in
   team-config.yaml, so a glob-keyed classifier would have nothing to match it against". Once T-02
   adds `.harness/*/docs/**` a glob-keyed classifier WOULD match. The case keeps passing while its
   stated reason is dead. Rewritten to what survives. It also IS T-05's standing case 1 once
   repointed — the plan no longer asks for a duplicate beside it.
3. **T-04 named 2 of 8 sites in `test-gen-decisions-index.py` and 1 of 2 in
   `test-validate-digest.py`.** Its verify forbids all of them, so the doer would have met a red
   gate with unnamed work — the same shortcut pressure this send-back is about. `:94` and `:163`
   are runtime-coupled temp fixtures (the generator reads `DOCS_DIR` under the temp root); `:8`,
   `:88`, `:382` are prose and `:678` an argv string; `test-validate-digest.py:1308` is a sample
   digest body. All enumerated now.

### Why T-04's positive control was NOT tightened to `harness/docs`

The reviewer's suggested tightening reds correct work. Most T-04 sites are comma joins and their
migrated form carries no `harness/docs` substring at all — `test-harness-yaml.py:686`,
`test-team-catalog.py:45`, `test-gen-decisions-index.py:23`, `test-no-distribution.py:210`,
`test-factory-config.py:399`. T-04's own intent says to keep each file's existing join style. Fixed
instead with the two-spelling control T-03 already models:
`\.harness/harness/docs|"\.harness", ?"harness", ?"docs"`.

### Pattern audit for the sweep pattern (layout_migration.py docstring rule, `:20-25`)

Candidate `docs/harness|"docs", ?"harness"` versus broader `docs["/ ,]{1,4}harness`, run at
`0f12f14` over `.claude`, `CLAUDE.md`, `.harness/expertise`: **identical per-file counts across all
25 files**. No third spelling of the concept exists on the live surfaces.

### The `survivors:` anchor was stale by construction

The old verify pinned `^survivors: 16[0-9]$`. This feature's own record, the moved docs and the
DEC-189 amendment all add literal-carrying files, so a correct tree could cross 170 and red. The
count is now DERIVED — after the migration every remaining match IS a survivor — and the verify
asserts the note's figure equals a fresh `git grep -l` excluding this feature's own directory, so
the same command still reproduces it after T-11 commits the notes.

### Per-file line counts at `0f12f14` (what T-10 now asserts against)

`git grep -cE 'docs/harness|"docs", ?"harness"' -- .claude CLAUDE.md .harness/expertise` = 25 files:
22 under `.claude`, 2 Expertise, `CLAUDE.md` at 3 lines. Post-migration expected:
`layout_fixtures.py` 3, `layout_migration.py` 6, `test-check-domain.py` 1 (from 19),
`test-check-state.py` 1 (unchanged), `test-layout-migration.py` 1 (unchanged), every other file
absent.

### Verified mechanics

- `run-unit-tests.sh:57-60` runs each script with stdout inherited, and BOTH sides print a per-case
  label on PASS: `test-check-domain.py` emits `ok    <label>` (integration half) and
  `test-layout-migration.py` emits `ok   - case 1: real root exits 0` and siblings (unit half). So
  both of T-05's label greps for `harness/docs` in runner output are real checks, not dead ones.
  `test-layout-migration.py`'s "case 1: real root exits 0 / non-zero feature-dir count / non-zero
  reader-file count" is also the precedent T-05's standing case 2 extends, confirmed by running it.
- The T-10 table comparison (`git grep -c … | sort` against a here-literal, plus the `:!<dir>`
  pathspec exclusion) was executed against the current tree with a two-row expectation and matched.
- `check-plan-routes.py` on the revised plan: **exit 0, 0 violations across 1 plan(s)**.

### Not fixed, recorded for the reviewer

`test-gen-decisions-index.py:361-363` FAILs when the real index is absent while `:399-401` SKIPs on
the same condition, so if T-04's repoint of `:23`/`:24` goes wrong one of the two goes quiet rather
than red. Pre-existing; one line about it is now in T-04's intent. SC-06's `evidence: integration`
is sound — `:373-374` reads `REAL_INDEX` and diffs it against fresh generator output.

## Send-back 2 — three revisions

### T-01's STOP no longer hangs on the feature-dir count

`layout_migration.scan` takes `feature_dirs` from `_evidence` (`:224-226`), which globs
`.harness/*/features/*/feature.json` on disk (`:171-172`). Twenty-one exist at `0f12f14`; `FEAT-22`'s
own is created at instantiation, so T-01 runs against **22** with nothing drifted. The STOP now hangs
on the four figures a cycle cannot move — the two surface strings, `1 doc root(s)` (the single
SPEC.md marker) and `7 reader file(s)` (the length of `READER_TABLE`) — and the feature-dir count is
recorded, not compared, with `< 21` named as the only reading that means drift. `verify:` was
already count-free and is untouched.

Swept the rest of the plan for the same shape. `T-09`'s verify is regex-bounded (`[0-9]+ feature
dir`), `T-10` derives its survivor count fresh, `T-02`'s `= 5` is a fact the task itself creates, and
every line anchor in T-03/T-04/T-05 points into a file no earlier task in this feature touches. Only
`D-07`'s `161 of 196` needed anchoring; it now carries `at 0f12f14` and says the figures are the
pin's, not a target.

### Disposition: `layout_migration.py:34` stays

Taken: **declare it a knowing survivor**, not edit-and-retable.

The rule is the one already exempting `:94`, `:97`, `:100` and `:174` in the same file: this module's
subject *is* the legacy layout, so a legacy path written inside it describes the pre-migration shape
rather than claiming where anything lives now. `:34` is the recorded reason the
`gen-decisions-index.py` row runs at BOTH spellings, and that row must keep matching legacy trees
after this feature lands — rewriting the reason invites a later editor to simplify the row away.
`layout_migration.py` is **not** in `READER_TABLE` (verified: the table holds seven other files), so
its own text is matched by nothing and the line changes no verdict in either direction. It is now
named in T-05's DO-NOT-TOUCH block with that rule, and T-10's table keeps the file at 6.

### T-08's heading date floats

The heading is exact apart from the date, which the builder takes from `date +%F`. `DECISIONS.md`
already carries `### DEC-174 amendment 1 (2026-08-11)` and `### DEC-186 amendment 1 (2026-08-12)`, so
the shape was right and only the hardcoding was wrong. T-08's verify anchor was already date-free.

## Send-back 3, resumed — validation, and the one item that was genuinely half-landed

The run was cut off between the edits and the validation. **The edits were all on disk; the
validation was not.** Re-checked every item, then ran the validation. One real defect surfaced.

### The five "missing" items were all already present — greppable tokens, so the next check lands

The send-back grepped for five markers and found none. All five were on disk under different
wording. Tokens below are verbatim, at post-edit line numbers:

| # | Item | Token to grep | At |
|---|---|---|---|
| 1 | D-02's second consumer | `BOTH of the list's consumers` | T-08 `:821`; also D-02 `:117-120` |
| 2 | Why T-02 precedes T-03 | `WHY THIS TASK RUNS AFTER T-02` | T-03 `:346` |
| 3 | `ws_c/widget/docs/guide.md` untouched | `MUST STAY UNTOUCHED` | T-05 `:642` |
| 4 | CLAUDE.md 75-vs-80 headroom | `IT IS A PATH SUBSTITUTION, NOT A REFLOW` | T-06 `:726` |
| 5 | RED STATE 3 accuracy | `NOTE what this state is NOT` | T-01 `:246` |

Each item's factual claim was re-derived at source rather than trusted (P-15):

- `CLAUDE.md` is **75** lines; `check-state.sh:674` warns above **80**. Five lines of headroom, as stated.
- The deny-message advertise filter is a comprehension over `applicable_globs` calling
  `is_control_plane_glob(g)` and iterating `HARNESS_CONTROL_PLANE` on the same expression
  (`harness_boundary.py:339-343`). D-02 and T-08 describe it correctly.
- `gen-decisions-index.main` reads `INDEX_PATH` into `existing_rows` before regenerating
  (`:412-414`), so a reversed T-02/T-03 order really would drop every hand-written ruling.
- `test-check-domain.py:736` is `os.path.join(ws_c, "widget", "docs", "guide.md")` — a comma join
  carrying no legacy literal, exactly as T-05 says, so leaving it alone cannot disturb the
  exactly-one-legacy-line count.

### The defect: RED STATE 3's interval quantifier was false for the first half of the cluster

Item 5 was **half-landed.** The two-phase absence/stale-header explanation was correct; the
INTERVAL it was quantified over was not. It read "From the move until T-09 regenerates the index,
the INTEGRATION SUITE is red on exactly one script... unit green."

That is the state **after T-04 and T-05 land**, not from the move. Measured against the runner's own
script lists (`run-unit-tests.sh:17-18`), T-04's six files split three unit
(`test-team-catalog`, `test-no-distribution`, `test-factory-config`) and three integration
(`test-harness-yaml`, `test-validate-digest`, `test-gen-decisions-index`); T-05's five split four
integration and one unit. So between T-02 and T-05 the unit suite is red too and integration is red
on several scripts — while a reviewer is explicitly told to trust this section to tell an expected
red from a defect.

Fixed in T-01's intent (`:229-247`): RED STATE 3 now opens `ONCE T-04 AND T-05 HAVE LANDED`, and a
new `THE INTERVAL BEFORE THAT IS WIDER` paragraph names the eleven files and the task that clears
each. The rule a reviewer needs is now stated positively — a red outside those eleven plus
`test-gen-decisions-index.py` is collateral breakage. T-05's expected-FAIL pin and T-09's suite gate
are unchanged; all three now describe the same interval consistently.

### Second fix: T-10's derivation did not reproduce its own table

T-10 asserts an exact per-file survivor table and told the reader to derive it from per-task deltas.
The derivation said "T-03, T-04 and T-06 take fifteen files to zero" and then jumped to the table,
omitting that T-05 also zeroes three files. Measured at `0f12f14`:

```
git grep -cE 'docs/harness|"docs", ?"harness"' -- .claude CLAUDE.md .harness/expertise  ->  25 files
```

25 − 15 (T-03/04/06) − 3 (T-05: `test-bash-write-guard` 5, `test-check-plan-routes` 6,
`test-factory-integration` 4) − 2 (T-07) = **5**, which is the table. The five baselines the table
pins are confirmed: `layout_fixtures.py` 3, `layout_migration.py` 6, `test-check-state.py` 1,
`test-layout-migration.py` 1, and `test-check-domain.py` 19 → 1. The arithmetic is now written out
in T-10's intent so a reviewer following it reaches the asserted number.

### The MF-1 remedy was overturned deliberately, not drifted into

eng-lead proposed dropping T-05's suite check because the mid-cluster red made it unpassable. T-05's
verify instead **pins** the expected failure (`:511-513`): zero unit FAILs, exactly one integration
FAIL, and that one must be `test-gen-decisions-index.py`. Dropping the check would have surrendered
collateral-breakage detection across three tasks that rewrite eleven test files and the classifier
they exercise — the largest blast radius in the feature — to accommodate one known red. Pinning
costs two extra lines and keeps the detection. Recorded here because it was a judgement against a
sanctioned remedy, not an oversight.

### Validation results

- **`check-plan-routes.py`: exit 0, 0 violations across 1 plan.** Seven `DEVIATION` lines are
  informational, not violations — they are D-03's carve-out, a file granted to a lane but declared
  `main-session-direct`, and the checker's own summary counts them as none.
- **Worst-case machine lines: T-05 at 25 of 50.** T-09 grew to 20 (was under budget before and
  still is), T-10 21. Nothing near the cap; the two fixes touched `intent:`, not `verify:`.
- `yaml.safe_load` parses the file; every `verify:` loads as a literal-block `str`; both edited
  intents' tails survive the load (G-12 check run explicitly).
- `approval.status: pending`, untouched. 11 tasks, 7 decisions — no renumbering, nothing added.

### Discriminating-power checks on the verifies (P-01)

Run against the tree at `0f12f14` before any migration:

- Both suites are **green, zero FAILs** at baseline. So T-05's "exactly one integration FAIL" is a
  state only this migration can produce.
- `run-unit-tests.sh` inherits each script's stdout (`:58-65`), so case labels do reach the captured
  output — T-05's `grep -qi 'harness/docs'` assertions can fire at all.
- Those greps return **zero hits in both suites pre-migration**, so they cannot pass by accident.
  The existing labels carry `docs/harness/**`, which does not contain `harness/docs`.
- `--stdout` (`gen-decisions-index.py:391-397`), `check-expertise.sh` and `check-domain.sh --resolve`
  all exist; no verify names a flag that is not there.
- T-09's `grep -q ... && { exit 1; }` at `:868` was tested under `bash -e`: an unmatched grep in an
  AND-list does **not** exit the shell, empirically. Not the G-14 shape. No fix needed.

### T-03's three enumerations are exact against source

`grep -nE 'docs/harness|"docs", ?"harness"'` returns, and T-03 names, precisely:
`gen-decisions-index.py` 2/5/10/20/76 · `factory_config.py` 11/13/32 · `harness_boundary.py`
84/90/111/143/151/221/315. No site is missed and none named is absent.

### Line-range delta table

| Section | Before this resume | After |
|---|---|---|
| `approval` / `lanes` / `decisions` | 4 / 9 / 100–173 | unchanged |
| T-01 | 175–243 | **175–255** (+12, RED STATE 3 interval) |
| T-02 … T-09 | 244–917 | **256–929** (shifted +12, content unchanged) |
| T-10 | 918–1015 | **930–1031** (+4, survivor arithmetic) |
| T-11 | 1016–1065 | **1032–1081** (shifted +16) |
| File total | 1065 | **1081** (+16) |

## Resume — send-back 4 completion (2026-08-15)

**The previous run was cut off mid-A2. One line of the plan changed in this resume; everything
else here is measurement.** Figures in the earlier "Validation results" section above are
SUPERSEDED where they conflict — specifically the worst-case machine-line figure, which was
T-05 at 25 and is now T-03 and T-09 tied at 31 of 50.

### What was already on disk when this resume started

- **A1 had landed.** T-01's RED STATES 3 already puts `test-layout-migration.py`'s red on
  `[T-02, T-03)` and cites case 1's real-root exit-0 assertion at `test-layout-migration.py:131`
  (plan `:259-265`), and already states the four-integration / one-unit split of T-05's five
  (`:270`). No edit was needed.
- **A3 had landed** — T-01's `SUITES` capture (`:216-218`) with its two verify clauses (`:194-198`).
- **The must_fix's four T-03 clauses had landed** (`:367-383`) with their intent counterparts.
- **A2 had landed in part**: T-09's prefix whitelist loop (`:950-958`) and a count assertion
  (`:959-960`). The count was the defect below.

### The one edit: T-09's count was an equality contradicting its own intent

T-09's intent at `:1025-1029` says the figure "is a FLOOR, not an equality, so a task that
legitimately touches one more file inside those prefixes does not red it". The verify asserted
`test "$k" = 28`. Two halves of the same task said opposite things, and the verify's half is the
one that reds correct work. Changed to `-ge`, with the message reworded to match.

**Derivation of 28, from the plan's own enumeration** (T-09 intent `:1025-1029`):
`team-config.yaml` 1 + the three resolvers 3 + T-04's six 6 + T-05's five 5 + T-06's six 6 +
the two Expertise files 2 + the five docs at the destination 5 = **28**. It is stable as a
minimum because every one of the 28 has a named edit in a task; it is not provably exact,
because nothing forbids a doer touching one more file inside the whitelisted prefixes. Floor plus
the prefix whitelist is therefore the shape: the whitelist catches the stray-path class the
send-back named, the floor catches a task that silently skipped a file.

### Rename display, measured rather than assumed

`git show --name-only --format= HEAD` over a synthetic repo (git 2.50.1, default rename detection,
`git mv` plus an unrelated modification) prints **only the destination path** for a rename —
`zz/zz/cc/S.md`, never the pre-image. Two consequences for T-09's verify:

- `grep -v '^docs/harness/'` at `:959` is dead code in the normal path. Left in place: removing it
  is churn, and it is harmless.
- The case-loop at `:952-957` would red on a `docs/harness/` line. That is **not** a false red —
  such a line can only mean rename detection failed, which T-02 requires ("preserving rename
  detection") and T-09's intent re-confirms via `git show --stat`. No `docs/harness/*` arm was
  added to the whitelist; adding one would weaken the check into accepting a delete-plus-add.

### Pattern audit of the two new greps, per `layout_migration.py:20-25`

All measured against `harness_boundary.py` at `0f12f14` (`git rev-parse --short HEAD` confirmed).

**`holds no.*entry anywhere` — the negative grep.**
- REDS on the false sentence: exactly one hit, `:221`, the `is_control_plane_target` docstring
  clause that T-02 falsifies.
- Does NOT red a correct rewrite: the sole hit is the sentence being removed, and T-03's
  instruction (`:424-425`) is to state the target-keyed rule and *drop* the claim about what
  `team-config.yaml` does not contain — a replacement carrying neither "holds no" nor
  "entry anywhere". **Boundary of this audit, stated because it cannot be greped:** the rewrite
  does not exist yet, so the residual is a doer re-spelling the phrase. The intent forbids it in
  those words (`:426`), and the grep exists precisely to red that.

**The `:315` grantor check — `awk` on the `guide.md` anchor.**
- Cannot pass on a token-swapped-but-unrewritten paragraph: `grep -F '.harness/*/docs/**'` returns
  **zero hits file-wide** at `0f12f14`. A pure token swap yields
  `<harness>/.harness/harness/docs/guide.md` — the path, not the glob literal — so `index()` finds
  nothing and the check reds. The literal only appears if the grantor is actually named.
- The anchor is sound: `guide.md` occurs **once** (`:315`), and the awk asserts `c!=1` loudly
  rather than silently picking one (G-04 avoided).
- Window collision ruled out: the only other future occurrence of `.harness/*/docs/**` in this file
  is T-03's rewritten `HARNESS_CONTROL_PLANE` entry at `:90`, ~225 lines outside the
  `[g-8, g+3]` slice.

**The other two clauses, re-audited for discriminating power (P-01).**
- `redundant`: absent from the `-B20 HARNESS_CONTROL_PLANE = \[` window at `0f12f14` (grep exit 1),
  so it cannot green before the clause is written. `HARNESS_CONTROL_PLANE = [` occurs **once**, so
  the window cannot land on a second block.
- The symlink pair: `-> ../../.claude` is **present** at `:111` (the forbid-clause reds on the
  unrewritten form) and `-> ../../../.claude` is **absent** (the require-clause reds too). Both
  halves are live at baseline.

### The four new assertions do not contradict T-10's per-file table

`harness_boundary.py` is absent from T-10's survivor table, i.e. it must reach **zero** legacy
lines. None of the four required literals — `redundant`, `-> ../../../.claude`,
`.harness/*/docs/**`, and the forbidden `holds no…entry anywhere` — matches T-10's pattern
`docs/harness|"docs", ?"harness"` (tested by piping the four literals through the exact grep:
exit 1, no match). The negative grep is a prohibition, not a requirement, so it demands nothing
of the file's content either. Zero is reachable.

### Validation results, at final state

- **`check-plan-routes.py`: exit 0, `0 violation(s) across 1 plan(s)`.** Seven advisory
  `DEVIATION` lines (T-01, T-03, T-04, T-05, T-07, T-10, T-11), each a granted path declared
  `main-session-direct` under D-03; the checker counts none as a violation.
- **Worst-case machine lines: T-03 31 and T-09 31, of 50.** Then T-05 25, T-10 21, T-04 14,
  T-01 12, T-06 11, T-11 9, T-02 8, T-07 7, T-08 6. This supersedes the earlier T-05-at-25 figure.
- **`yaml.safe_load` parses the file.** All 11 `verify:` values load as `str`, all 11 written as
  `verify: |` and zero as `verify: >` (grep counts 11 / 0 over 11 total). T-09's verify tail
  survives the reload after the edit (G-12).
- `approval.status: pending`, untouched. 11 tasks, 7 decisions — no renumbering, nothing added,
  nothing removed.

### Line-range delta table — this resume

| Section | Before this resume | After |
|---|---|---|
| `approval` / `lanes` / `decisions` | 4 / 9 / 100–173 | unchanged |
| T-01 … T-08 | 175–919 | unchanged |
| T-09 | 920–1030 | 920–1030 — **one line modified at `:960`**, none added or removed |
| T-10 / T-11 | 1031–1132 / 1133–1182 | unchanged |
| File total | 1182 | 1182 (+0) |

### Open

Nothing blocking. The plan is ready for signature.
