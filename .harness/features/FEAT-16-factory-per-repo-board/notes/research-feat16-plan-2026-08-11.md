# research — FEAT-16 plan, 2026-08-11 (revised at SEND-BACK cycle 2, then CORRECTED and re-baselined)

## Correction pass — 2026-08-11 re-baseline. Read this first.

**This note was corrected in place rather than struck.** Its research stands; three classes of claim
in it did not, and every corrected figure below carries the command that produced it. The trigger was
that the main session mutated board 2 mid-plan without telling the running flow, which falsified
criteria this note reasons about, and a separate re-run of the gates found that this note's "verbatim"
gate evidence had never been FEAT-16's.

| What was wrong | Where it is corrected |
|---|---|
| ~70 `OK` lines pasted as FEAT-16's scoped gate output were another feature's | "Gate 2" below — the real run is 11 lines |
| tree-wide "exit 1, 2 violation(s)" and the FEAT-14 budget story | "Gate 2" below — it is exit 0, 0 violations, and `intent:` is not budgeted at all |
| `Q1`–`Q4` ids colliding with the operator's answers file | "Questions" below — renumbered to the answers file |
| the before/after capture pair and its justification | D-04 note below — one capture, new reason |
| T-07's four-option, `sort`ed name clause | "Verifies proved rather than asserted" below — six names, board order, no `sort` |

**What DID hold and is unchanged:** the architecture, the DAG, the three-phase migration walk, the
per-repository schema, MF-1..MF-6, and every `check-domain.sh --resolve` resolution.

## BLUF — cycle 2

**MF-6 is closed and it was one token in two files.** `plan.yaml`'s T-10 verify and `BRIEF.md`'s
SC-12 both grepped `Amendment am.2`, a bold-inline form DEC-174 does not use; the entry's own house
style is a `###` heading, and a documentor following T-10's intent would have landed correct work on
a red gate. Both sites now grep `DEC-174 amendment 2`, which matches **0 lines** at `a29ad06`
(`grep -c "DEC-174 amendment 2" docs/harness/DECISIONS.md` → `0`), so the clause still
discriminates. T-10's intent now prescribes the literal heading rather than "the same style am.1
uses", closing the gap between the two halves I author (P-08).

All four advisory folds landed. Nothing else was re-opened; the architecture, the DAG, the
three-phase walk and MF-1..MF-5 stand as verified. `lanes.resolved_at` is unchanged at `a29ad06`,
which is HEAD.

**Verified before writing fold 4, because the fold could have re-created MF-6:**
`AMEND_HEADING_RE = ^###\s+DEC-(\d+)\s+amendment(?:\s+(\d+))?\b` (`gen-decisions-index.py:25`)
matches both `### DEC-174 amendment 1 ...` and `### DEC-174 amendment 2 ...` — confirmed by loading
the module and calling the regex on each string. The live `DEC-174` row already carries `am.1`
computed from the heading form, so the span reaching `am.1-am.2` is proven, not assumed.

## The four folds, as made

1. **T-06 now states FOUR fleet strings and names them by identifier**, not by line: `good_repos`,
   the inline fixture behind case (c) (built into `nows_root`), `two_base_fleet`, and
   `two_base_fleet_for`. The intent says why the count is stated — T-06's verify runs under T-01's
   permissive loader and cannot see a missed fixture, so the miss would surface at T-08 and be
   attributed there. T-08's dual-suite clause is named as the backstop so nobody collapses it.

   **Caught in the same edit, and it was mine:** case (c)'s board is a flow mapping carrying only
   `owner` and `number`, so the universal clause ("the same owner, number, station_field and
   stations values it had") is under-determined for it — and my first draft of the anchor list
   resolved that by writing "carries exactly those two keys, do not invent station_field or
   stations". That **contradicts the A-6 repair already standing further down the same intent**,
   which requires a COMPLETE per-repo board there precisely so case (c) fails on the missing
   `workspace_root` rather than on the missing `board.station_field` — the wrong-reason pass cycle 1
   resolved as deliberate. Two instructions to one doer about one fixture, both authored by me
   (P-08). The bullet now names case (c) as the explicit exception to the carry-the-same-values rule
   and points at the repair paragraph rather than restating it.
2. **T-07's clause 3 is now checkout-pinned.** `factory_config.py --show` with no `--fleet` resolves
   the fleet path from its own module root, so run from another checkout it exits 0 against a file
   the task never touched. The intent names the concrete second checkout on disk,
   `.claude/worktrees/FEAT-13-single-issue-board-lookup/`, and requires confirming the file edited
   is the file read.
3. **`d97f5ea` is out of the shipped test output.** T-09's `case5` failure detail now names the date
   and the live board (Projects v2 board 2 on the `mruangutai` account, renamed 2026-08-11). The
   remaining `d97f5ea` in the plan is T-07's before-capture provenance note — a feature artifact,
   left alone by the review's own instruction.
4. **The am-span is generated, and T-10 now says so.** The intent no longer tells the documentor to
   hand-edit the token: it says regenerate with `gen-decisions-index.py`, then confirm the DEC-174
   row's span reads `am.1-am.2`. The row's ruling text after the double-colon stays authored and is
   rewritten in place.

## Two prose corrections to this artifact

- **The one-way-schema claim is narrowed, not deleted.** The earlier wording — "a worktree or
  branch cut before T-01 runs the OLD `factory_config.py` against the NEW `fleet.yaml`" — is false:
  `fleet.yaml` is tracked and every checkout carries its own copy of **both** halves, so git alone
  cannot pair an old loader with a new fleet. What can is a **mixed invocation**: a
  `factory_config.py` predating T-01 resolving a fleet path that lands on a post-T-07 `fleet.yaml`,
  by an explicit `--fleet` or by running the tool from one checkout against another's tree. Fixed in
  both places in one pass — `plan.yaml` D-03 `because:` and T-08's intent. The mitigation and the
  recovery (rebase past T-08, never edit the fleet back) are kept.
- **The SC-11 sweep row for `test-factory-integration.py` no longer carries a line number.** It is
  content-anchored below. One nuance for the record: the reviewer described this artifact as
  claiming "T-05's intent names `test-factory-integration.py:645`". It did not say that — the line
  number appeared in the SC-11 sweep-assignment table, not in a claim about T-05's intent. The
  citation was still a line anchor into a file T-05 edits, which is the defect worth fixing, so it
  is fixed; the sentence the reviewer described was not there to fix.

---

## BLUF — cycle 1 (retained)

The plan is signature-ready again after the architecture review's five MUST FIX items: **11 tasks**
(was 10), 7 decisions, 6 REQs, **12 SCs** (was 11), **0 route violations**. The architecture was NOT
re-opened — D-01..D-07 stand, the three-phase migration stands, T-06 stays on the team lane, SC-03
and SC-06 keep their wording. *(Counts superseded at the 2026-08-11 re-baseline: 11 tasks unchanged,
**11 decisions** — D-08..D-11 appended — 6 REQs, **13 SCs** — SC-13 appended, nothing renumbered.
D-04 and D-07 were re-based and SC-03, SC-06 and SC-07 were rewritten; the DAG and task boundaries
were not touched. Counted with `grep -c` on `BRIEF.md` and `harness_yaml.load_plan` on `plan.yaml`.)* What changed is completeness: a fixture nobody owned, a task that
could not obey its own instructions, a task whose gate could not see the failure it exists to
prevent, two shipped documents that would have contradicted the shipped criteria, and REQ-06 with no
criterion at all.

## What the send-back changed

| id | Defect | Closed by |
|---|---|---|
| MF-1 | `test-factory-workspace.py`'s `good_fleet_dict` is top-level-board shaped, is in `UNIT_SCRIPTS`, and T-08 reddens it with no grant to fix it | new **T-11** (`depends_on: [T-01]`), added to T-07's `depends_on`. T-08/T-09 de-parallelised: T-08 now `depends_on: [T-07, T-09]` |
| MF-2 | T-05 was told to change no assertion, but `--show`'s payload key `board` disappears under it | T-01's intent states the `--show` payload contract; T-05's intent names the **two** legitimate sites (the `(D-config)` payload check, and the ready-option read in the fake-git case) with the replacement written out |
| MF-3 | T-07's `verify:` never checked that the file it rewrites loads | third clause `python3 .../factory_config.py --show >/dev/null`, plus intent text saying it is a **regression guard, not a discriminator** |
| MF-4 | `SPEC.md` says `factory_config` exposes `station` and `fleet.yaml` carries the board; SC-11 says the opposite | `docs/harness/SPEC.md` added to T-10's `files:` (resolves `harness-documentor`, lane unchanged), both rows named in intent, two absence clauses in T-10's `verify:` |
| MF-5 | DEC-186 rules "one Projects v2 board" and its read-back cost model is one query per poll | T-10 appends a DEC-186 amendment (**amend, not strike** — host ruling) and rewrites its index row; cost model restated as one ready-station query **per repository served** |
| ALSO | REQ-06 had no SC | **SC-12**, four mechanical clauses, mirrored by T-10's `verify:` |

Found while proving the new clauses rather than asserting them: T-10's original verify command
`gen-decisions-index.py --check` **does not exist** (see the last section). That defect predates
this cycle and would have blocked T-10 at run time.

## Two arguments corrected, conclusions kept

- **D-04's `because:` was the weaker reason.** The refusal window `factory_claim` opens on a station
  mismatch is real at source but **no factory run is a task in this plan**, so nothing enters that
  window. The reason recorded at the time was the evidence chain — a before-capture unrecoverable
  once an option is renamed, an after-capture as SC-03's measurement point.
  **SUPERSEDED at the 2026-08-11 re-baseline:** T-07 no longer edits a board, so there is no edit
  for a before-capture to precede, and a before/after pair with nothing between them would be two
  identical files. D-04 now folds a PRECONDITION CHECK, ONE capture and the fleet declaration, and
  the capture's surviving reason is narrower — it is SC-03's measurement point and no CI runner ever
  re-reads a GitHub board, so if T-07 does not write the reading down nothing else will.
- **T-07's rollback is benign, and it is now written down.** *Restated at the re-baseline:* the task
  writes nothing outside this repository at all, so if the fleet rewrite fails the tree is unchanged,
  `load_fleet` still succeeds and no write is blocked. The reverse-rename procedure the earlier draft
  carried is gone with the board edit; there is nothing to reverse.

## Advisories: folded and declined

**Folded (all nine in substance):** A-1 step 6's `project_field_set` rebind → T-02. A-2 the
superseded invariant comment moves with the code → T-02. A-3 tie-break made explicit as
`(issue_number, fleet order)` → T-02. A-4 T-08 verifies **both** suites → T-08. A-5 `case5`, and it
must be **called from `main()`** → T-09. A-6 case (c)'s wrong-reason pass is a deliberate repair →
T-06. A-7 de-duplicate merged candidates on `(repo_name, issue_number)` → T-02. A-8 the idiom split
and why `_STATION_KEYS` makes it safe → T-04. A-9 the one-way schema consequence → D-03 and T-08
(**narrowed at cycle 2** to the mixed-invocation case — see the prose corrections above; the
reviewer corrected its own A-9 and the mitigation is kept either way).

**Declined, both packaging rather than substance:**
- **A-2's alternative shape** (validate every served board first, then poll). The substance — no
  comment left asserting the retired invariant — is folded. Re-ordering validation ahead of the
  per-repo loop is a redesign of T-02, and the architecture is not re-opened this cycle.
- **A-3 as a `D-NN`.** It fails the DEC-149 bar on two of three legs: the tie-break is trivially
  reversible and carries no real trade-off. It is stated in T-02's intent and in a code comment
  instead, which is where a chosen-not-accidental ordering belongs.

**A-4's trap, resolved by measurement, and the operator's framing was slightly off:** `--kind all`
**is** runnable (`run-unit-tests.sh:33` accepts `all` and it is the default), but it is the `cmd` of
**no** entry in `.harness/harness.json`'s `test_kinds` — so no criterion could cite its output.
T-08 therefore carries two clauses in one literal `|` block, `--kind unit` and `--kind integration`,
which map 1:1 onto SC-08 and SC-09.

## The tree-wide sweep behind SC-11 (every hit has an owning task)

SC-11's old grep (`fleet\["board"\]` over `factory_*.py`) was narrower than the property it named.
Widened to all of `.claude/skills/harness/bin/`, both quote styles, and the `.get("board")` form. At
`a29ad06` the pattern matches **18 lines across 7 files**, and each is assigned:

`factory_claim.py` → T-02 · `factory_decompose.py` (including the hoist **comment**) and
`test-factory-decompose.py`'s `"Redy"` fixture → T-03 · `factory_land.py` → T-04 ·
`test-factory-integration.py`'s `ready_option = fleet_data["board"]["stations"]["ready"]` read in the
fake-git case → T-05 (exactly one such line; identified by content, not line number, because T-05
edits this file) · `factory_config.py` `--show` → T-01, `station()` body →
T-08 · `test-factory-config.py`'s board round-trip case → T-08.

Verified the pattern does **not** match the post-migration idioms (`entry["board"]`,
`fleet["repos"][0]["board"]`, `board_for(...)`), so the criterion is satisfiable, not just strict.

## SC-10 restated as a mechanical check

Was an inspection criterion nobody could fail. Now: `git diff --name-only a29ad06..HEAD` intersected
with the four carve-out paths must be empty. Measured at `a29ad06`: `git status --porcelain` reports
all four **clean**, so a non-empty intersection is this feature's doing.

## SC-12 could not be written as the review worded it

The review asked for "grep DEC-186 for the **absence** of 'one Projects v2 board'". That string is
at `DECISIONS.md:5324` and `:5331`, and this record **appends**: DEC-174 am.1 and DEC-179 am.2 both
leave the original ruling standing under a supersession note. An append cannot produce that absence.
SC-12 therefore asserts what an append does prove — a DEC-186 amendment stating the control plane is
one board **per repository**, plus the **index row** (which T-10 does rewrite in place) carrying
`per-repository board`. Stated as a deviation rather than applied silently.

## Shas — three, still not collapsed, and one is not on this branch

- **`lanes.resolved_at: a29ad06`** = `git rev-parse --short HEAD`, re-measured this cycle. It was
  `d97f5ea`.
- **`d97f5ea` exists but is NOT an ancestor of HEAD** (`git merge-base --is-ancestor` → 1). It is
  *"A filesystem root as workspace_root is rejected at load, not obeyed by the guard"*, off this
  line. `git diff d97f5ea a29ad06` over `check-domain.sh` and `check-state.sh` is **empty**, so
  D-06's claim is unaffected — but D-06 is now re-anchored at `a29ad06`, where I re-read it:
  `check-domain.sh` reads `workspace_root` and `repos[].name` only and never `board`;
  `check-state.sh` INV-24 reads the fleet with `harness_yaml.load_file` (`:768`), not `load_fleet`.
- **SC-03's board measurement stays pinned at `d97f5ea` / 2026-08-11** by operator instruction. The
  option ids and item counts were measured live, not derived from the tree, so the sha is a
  timestamp for them rather than a code anchor — but it is a sha a reader cannot `git show` from
  this branch. Recorded, not silently changed.

## Questions — RENUMBERED to `notes/answers-2026-08-11-01.md`, and all now closed

**CORRECTION.** An earlier version of this section used its own `Q1`–`Q4` numbering, which collides
with the operator's answers file: what this note called `Q1` is the answers file's **Q4**, and what
it called `Q3` is the answers file's **Q5**. Correcting figures while leaving colliding ids sends the
next reader to the wrong answer, so the ids below are the answers file's.

- **Q2 — closed by the operator** (`answers-2026-08-11-01.md`, "Q2 — the live run stays the
  operator's"). SC-06's live run creates a throwaway issue and `refs/heads/factory/issue-N` in
  `mruangutai/kaya-ai` and moves a station on live board 2. Only the operator consents; SC-06 stays
  `not_met` until they run it, and the issue used must not be one of the 118 in `Done`.
- **Q4 — closed as plan decision `D-09`.** T-10 appends a second amendment to DEC-174 rather than
  opening a new DEC number: the loose end being closed was opened by DEC-174 am.1, and a closure
  belongs in the entry that opened it.
- **Q5 — closed as plan decision `D-10`.** DEC-186 is **amended, not struck**, and DEC-188's own
  text is the authority rather than anyone's preference — its paragraph beginning "The rule does not
  generalize by itself" reserves striking for a flat contradiction and routes anything "merely
  dated, narrowed, or partly overtaken" to an amendment, with striking needing the operator's word
  first. DEC-186 is partly overtaken exactly: one-board framing falsified, three-purpose read-back
  bound alive and in gates.
- **Q6 — closed as plan decision `D-11`.** No prototype gate fires. Every literal `files:` entry
  across all eleven tasks is a `.py`, `.yaml` or `.md` file, and the only human-in-the-loop surface
  is SC-06's UAT. Recorded as overridable in either direction.
- **The former "Q4" of this note is VOID, not answered.** It reported 2 tree-wide budget violations
  in FEAT-14. There are none — see the correction under Gate 2 below. FEAT-14's `plan.yaml` is
  indeed untracked (`git status --porcelain` reports `??`, still true), but with 0 violations there
  is nothing for a commit to turn red.

**Settled this cycle, no longer open:** T-06's lane. It stays `team` — `check-domain.sh` is
untouched and reads no board, so what remains is a review problem, not a lane problem.

## Gate 1 — check-domain.sh --resolve on every literal `files:` path (verbatim, cycle 2, re-run)

**CORRECTED at the 2026-08-11 re-baseline.** An earlier version of this lead-in read "Paths did not
change this cycle; identical to cycle 1." They did change afterwards: T-07's two capture entries
collapsed into one, `notes/board2-capture.md`, when the board edit became a precondition check. That
one path was re-resolved on 2026-08-11 (`harness-orchestrator`, exit 0) and is pasted below in place
of the two it replaced; every other resolution is unchanged and was re-run.

```
$ bash .claude/skills/harness/bin/check-domain.sh --resolve .claude/skills/harness/bin/factory_config.py
harness-backend-dev
harness-dev-ops
(exit 0)

$ bash .claude/skills/harness/bin/check-domain.sh --resolve .claude/skills/harness/bin/test-factory-config.py
harness-backend-dev
harness-dev-ops
(exit 0)

$ bash .claude/skills/harness/bin/check-domain.sh --resolve .claude/skills/harness/bin/factory_claim.py
harness-backend-dev
harness-dev-ops
(exit 0)

$ bash .claude/skills/harness/bin/check-domain.sh --resolve .claude/skills/harness/bin/test-factory-claim.py
harness-backend-dev
harness-dev-ops
(exit 0)

$ bash .claude/skills/harness/bin/check-domain.sh --resolve .claude/skills/harness/bin/factory_decompose.py
harness-backend-dev
harness-dev-ops
(exit 0)

$ bash .claude/skills/harness/bin/check-domain.sh --resolve .claude/skills/harness/bin/test-factory-decompose.py
harness-backend-dev
harness-dev-ops
(exit 0)

$ bash .claude/skills/harness/bin/check-domain.sh --resolve .claude/skills/harness/bin/factory_land.py
harness-backend-dev
harness-dev-ops
(exit 0)

$ bash .claude/skills/harness/bin/check-domain.sh --resolve .claude/skills/harness/bin/test-factory-land.py
harness-backend-dev
harness-dev-ops
(exit 0)

$ bash .claude/skills/harness/bin/check-domain.sh --resolve .claude/skills/harness/bin/test-factory-integration.py
harness-backend-dev
harness-dev-ops
(exit 0)

$ bash .claude/skills/harness/bin/check-domain.sh --resolve .claude/skills/harness/bin/test-check-domain.py
harness-backend-dev
harness-dev-ops
(exit 0)

$ bash .claude/skills/harness/bin/check-domain.sh --resolve .harness/factory/fleet.yaml
NOBODY
(exit 0)

$ bash .claude/skills/harness/bin/check-domain.sh --resolve .harness/features/FEAT-16-factory-per-repo-board/notes/board2-capture.md
harness-orchestrator
(exit 0)

$ bash .claude/skills/harness/bin/check-domain.sh --resolve .claude/skills/harness/bin/test-no-distribution.py
harness-backend-dev
harness-dev-ops
(exit 0)

$ bash .claude/skills/harness/bin/check-domain.sh --resolve docs/harness/DECISIONS.md
harness-documentor
(exit 0)

$ bash .claude/skills/harness/bin/check-domain.sh --resolve docs/harness/DECISIONS-INDEX.md
harness-documentor
(exit 0)

$ bash .claude/skills/harness/bin/check-domain.sh --resolve docs/harness/SPEC.md
harness-documentor
(exit 0)

$ bash .claude/skills/harness/bin/check-domain.sh --resolve .claude/skills/harness/bin/test-factory-workspace.py
harness-backend-dev
harness-dev-ops
(exit 0)
```

Exactly one path resolves to NOBODY, `.harness/factory/fleet.yaml`, and it is lane-locked
`main-session-direct` on T-07. Every other path is granted on the lane its task declares.

## Gate 2 — check-plan-routes.py (verbatim, re-run 2026-08-11 on the REVISED plan)

**CORRECTION.** An earlier version of this section pasted ~70 `OK` lines as verbatim FEAT-16 output.
They were not FEAT-16's — they name paths such as `.claude/skills/harness/teams/review.yaml` and
`.claude/agents/harness-dev-ops.md` that appear **zero** times in this feature's `plan.yaml`; the
paste was output produced against another feature's plan and carried here by mistake. The real
scoped run is **11 lines, T-01 through T-11**. Re-run and pasted below, in full, nothing elided.

```
$ python3 .claude/skills/harness/bin/check-plan-routes.py .harness/features/FEAT-16-factory-per-repo-board/plan.yaml
OK T-01 granted to harness-backend-dev, harness-dev-ops
OK T-02 granted to harness-backend-dev, harness-dev-ops
OK T-03 granted to harness-backend-dev, harness-dev-ops
OK T-04 granted to harness-backend-dev, harness-dev-ops
OK T-05 granted to harness-backend-dev, harness-dev-ops
OK T-06 granted to harness-backend-dev, harness-dev-ops
OK T-07: declared main-session-direct (.harness/factory/fleet.yaml ungranted)
OK T-08 granted to harness-backend-dev, harness-dev-ops
OK T-09 granted to harness-backend-dev, harness-dev-ops
OK T-10 granted to harness-documentor
OK T-11 granted to harness-backend-dev, harness-dev-ops
0 violation(s) across 1 plan(s)
(exit 0, taken from an unpiped run)
```

Tree-wide, the form the required CI job runs:

```
$ python3 .claude/skills/harness/bin/check-plan-routes.py > routes.txt 2>&1
(exit 0)
$ tail -1 routes.txt
0 violation(s) across 12 plan(s)
```

**CORRECTION, and it is the load-bearing one.** An earlier version of this section claimed the
tree-wide run exits 1 with `2 violation(s) across 12 plan(s)`, both of them DEC-182 machine-field
budget overruns in `.harness/features/FEAT-14-feature-json-schema/plan.yaml` at T-04 (54 lines) and
T-08 (61 lines). Re-measured 2026-08-11: the run exits **0** with **`0 violation(s) across 12
plan(s)`**, 104 output lines, none of them a `VIOLATION`.

Three separate things were wrong, and the third explains the other two:

- **The cited intent lengths are wrong.** FEAT-14's T-04 `intent:` is **203 lines** and its T-08
  `intent:` is **73 lines**, not 54 and 61. Measured by loading that plan with
  `harness_yaml.load_plan` and counting `splitlines()` on each task's `intent:`.
- **`intent:` is not budgeted at all.** The cap is real — `check-plan-routes.py` defines
  `MACHINE_LINES_PER_TASK = 50` and emits a `VIOLATION` naming DEC-182 when a task exceeds it — but
  `BUDGETED_FIELDS` deliberately **excludes** `intent:`, on the stated ground that `intent:` is READ
  rather than matched. So no amount of `intent:` prose can produce a budget violation, and the
  mechanism the earlier claim invoked cannot fire on the thing it measured.
- **FEAT-14's machine-field totals are all under the cap.** Computed with the checker's own field
  list and counting rule: T-01 17, T-02 22, T-03 26, T-04 39, T-05 32, T-06 32, T-07 41, T-08 46,
  T-09 35, T-10 10, T-11 45, T-12 36. Maximum 46, cap 50. Nothing there violates.

**What survives from the old claim:** FEAT-14's `plan.yaml` is genuinely untracked
(`git status --porcelain` reports `??`), which was true and is still true. Its consequence is void —
there are no violations for a commit to turn red. FEAT-16's contribution is 0 either way, and this
feature's revision kept every task inside the machine-field budget (FEAT-16's highest, recomputed
after the revision, is T-07 at 20).

**HOW THIS DEFECT GOT IN, since it is the reason the section is corrected rather than struck.**
Nothing in the tree gates whether prose is TRUE, only whether tokens are present, and the plan
itself passed the real gate — so no mechanical check could have caught a wrong figure in a note.
It was found by re-running the command instead of reading the record. That is the behaviour to
keep.

**Clauses are `&&`-chained, not newline-separated, on T-07, T-08 and T-10.** A multi-clause block
run as one shell invocation without `set -e` reports only the LAST clause's status.


## Verifies proved rather than asserted

- **T-07's option-name clauses were rewritten at the 2026-08-11 re-baseline and re-run.** The old
  clause sorted the names and asserted four (`Building,Done,Ready,Review,`). It is falsified: board 2
  offers six. The `sort` is gone too — order is part of the assertion now, and sorted output is
  `Backlog,Building,Done,Plan,Ready,Review`, a different string that would pass on a scrambled
  pipeline. The replacement asserts board order on BOTH boards, by NAME. Run 2026-08-11, output
  pasted rather than constructed:
  `gh project field-list 2 --owner mruangutai --format json --jq '...|.options[].name' | tr '\n' ','`
  → `Backlog,Plan,Ready,Building,Review,Done,` (trailing comma from `tr`). Board 3 yields the same
  string. The full four-clause `&&` chain runs to **exit 0** today, which is expected: the first
  three clauses are a PRECONDITION on state the operator already applied, not a post-condition on
  work this task does. It fails closed because a `gh` error yields an empty string.
- **Cross-board assertions compare names, never ids.** `Backlog f75ad846`, `Building 47fc9ee4` and
  `Done 98236657` are identical on board 2 and board 3 — GitHub's default template ids — so an
  id-based cross-board check is vacuous. Measured 2026-08-11 with
  `gh api graphql` on `projectV2(number:N){field(name:"Status"){options{name id}}}` for N in 2, 3.
  SC-03's three-id anchor is a *different* rule: within board 2, across time.
- T-07's `factory_config.py --show` clause run today: `python3 .claude/skills/harness/bin/factory_config.py --show
  >/dev/null` → **exit 0**, with no `--fleet` argument, so it resolves the live fleet path itself.
  It passes before the change **by design** — it is a regression guard on the one failure the three
  board clauses cannot see, not a discriminator, and T-07's intent says so.
- **T-10's first clause was broken in the plan I shipped for review, and running it found it.**
  `gen-decisions-index.py --check` **does not exist** — the tool answers
  `unrecognized argument(s): --check` and exits 2, and names the real form itself:
  `gen-decisions-index.py --stdout | diff - docs/harness/DECISIONS-INDEX.md`. T-10's clause 1 is now
  that pipe with `diff -q`. Run today it exits **0** (the index is in sync at `a29ad06`), so it is a
  drift guard rather than a pre-failed clause.
- T-10's whole block re-run at cycle 2 with the corrected clause: **exit 1**, failing at the
  `DEC-174 amendment 2` grep. At `a29ad06`:
  `DEC-174 amendment 2` → 0 matches, `per repository served` → 0, `per-repository board` in the DEC-174
  and DEC-186 index rows → 0 each, `repo_entry` / `station` in SPEC → 1, the fleet.yaml board phrase
  in SPEC → 1. Every clause discriminates, and each of DEC-174's row and DEC-186's row is grepped on
  its own rather than the phrase being counted file-wide — a file-wide count of 2 passes on one row
  written twice.
