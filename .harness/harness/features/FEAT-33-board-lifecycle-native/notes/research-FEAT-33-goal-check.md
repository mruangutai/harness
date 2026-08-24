# Goal-check — FEAT-33 — 18 MET, 2 NOT MET, 0 UNVERIFIABLE

> **THIS HEADER WAS REWRITTEN 2026-08-23, and it is the tenth instance of the defect this file
> spent the day cataloguing — in this file, mine.** It read **"17 MET, 3 NOT MET, 0 UNVERIFIABLE"**
> through SIX appended corrections that changed three of those verdicts. Appending a correction does
> not repair a summary a reader stops at; that is exactly what went wrong in
> `notes/migration-harness.md` and exactly how a wrong number reached `BRIEF.md`. The tally is now
> maintained here, and **every verdict below is graded at `e8a6058` + fix cycle c1 and may be
> superseded by the numbered Corrections at the end of this file. The Corrections win.**
>
> | SC | first verdict | current | superseded by |
> |---|---|---|---|
> | SC-01 | NOT MET | **met** | Correction 1 — the operator ruled fix the code; proven live on board 8 |
> | SC-04 | NOT MET | **met** | Correction 5 — two cards added at `ace0b06`; board 3 reads `0 finding(s)` |
> | SC-19 | met | **not_met** | Correction 6 — two clauses fail as written; intent delivered, wording not |
> | SC-11 | NOT MET | not_met | unchanged — `uat`, awaiting the operator's own run |

Graded against the working tree at `e8a6058` + fix cycle c1 (uncommitted). Suite and gate re-run by
me, not read off a report: `run-unit-tests.sh` exit **0**, `grep -c '^FAIL'` = **0**,
`test-board-lifecycle.py` PASS (line 1248 of the captured log); `check-state.sh` exit **0**,
`grep -c '^  VIOLATION'` = **0** (condition: FEAT-34's BRIEF signature is uncommitted — the 0 depends
on it).

## The three that are not met

- **SC-01 — NOT MET when graded; NOW MET, see Correction 1, which also records that "the defect is
  the sentence" was the WRONG conclusion — the operator ruled the code be fixed instead.** The criterion says one run against an owner
  with no board creates the project, creates the Status field with all six options, and links the
  repo. The delivered code deliberately does not: `cmd_provision` creates, links, prints the new
  number and `sys.exit(3)` before any field branch (`board_lifecycle.py:517-531`), and the test
  asserts it — "no project: never calls createProjectV2Field or updateProjectV2Field"
  (`test-board-lifecycle.py:480-483`). The signed plan specifies exactly that (`plan.yaml` T-04 step
  2: "STOP with exit 3 … the operator must record the new number"), and `harness-init/SKILL.md`
  documents the two-step. All three behaviours ARE proven separately (field-absent creates all six
  in declared order, `test-board-lifecycle.py:436-443`; extend sends existing-then-additions,
  `:405-412`). Only the one-run conjunction fails. **Operator's call: amend the criterion, not the
  code.**
- **SC-04 — NOT MET when graded; NOW MET, see Correction 5.** The citation below is the exact
  mechanism that later misled a reader, so it is kept and explained rather than edited away:
  `migration-harness-audit-after.txt` DID read `2 finding(s)` when this was written at `e8a6058`, and
  that same path was OVERWRITTEN at `ace0b06` to read `0 finding(s)`, its old content preserved as
  `migration-harness-audit-after-2-accepted.txt`. **The citation was true when made and the file
  changed underneath it** — a capture path is not a stable anchor unless the capture is immutable.
  As graded: `migration-harness-audit-after.txt` reads `2 finding(s)`, not zero (#25, #47
  — features `Done` whose parents were closed before board 3 existed, so no card was ever there).
  `migration-harness.md` says so in its own words, records the operator's ruling to accept them, and
  says the original verify was unsatisfiable. Honest, and still not the criterion. REQ-07 ("both
  projects reach a zero-finding state") is delivered for board 2 (`0 finding(s)`) and not for board 3.
- **SC-11 — NOT MET by design.** `uat`, the operator's own run. Board 2's capture shows
  `0 finding(s)` and audit exit 0, which is the evidence a runner cannot reach; the operator's
  eye-check is what is outstanding. Leave it.

## The 17 met, each with the evidence I checked

| SC | evidence |
|---|---|
| SC-02 | `board_lifecycle.py:610-620` names key + project number; `test-board-lifecycle.py:577-586`; single validator `factory_config.py:134` exact-set |
| SC-03 | `test-gh-sync.py:610`, `:922-930` (`--reason completed`, per issue), `:729-761` (`not_planned` + `abandoned` per sub-issue, colour b60205). RED: `git show origin/main:gh-sync.py` has no `--reason completed` and no `abandoned` label |
| SC-05 | `test-gh-sync.py:1266-1352` — #642 replay, open-card-at-Done, closed-card-at-Building all refuse with zero `item-edit`; the open-at-Backlog pair still writes. RED: `refusing #` absent from `origin/main:gh-sync.py` |
| SC-06 | `test-factory-config.py:401-436` — six accepted, five rejected naming `github.board.stations`, seven rejected; `factory_config.py:79` is the only `validate_board` |
| SC-07 | sole `project_single_select_extend` call site passes `existing + missing` (`board_lifecycle.py:579`); `test-board-lifecycle.py:379-392` zero mutations + "nothing to do" + second run |
| SC-08 | `test-board-lifecycle.py:420-427` no argv carries `Abandoned` on a fixture that DOES mutate; `Abandoned` appears nowhere as an option source; DEC-192 unstruck (index row 210, no strike record) |
| SC-09 | `test-board-lifecycle.py:629-656` MISSING for a renamed workflow, disabled reported, header names detection-by-name once |
| SC-10 | suite + gate above; `git diff --name-only origin/main...HEAD` names none of the four DEC-174 files, only `check-state.sh` (SC-20's sanctioned edit) |
| SC-12 | `git show e8a6058:DECISIONS.md:6448-6478` — DEC-196 am.3, reverses am.1's clause, explains why it is not a strike; index row 214 at the same sha |
| SC-13 | `test-gh-sync.py:1571-1636` — exact ITEM sets per status: Ready = 3 subs only, Review = parent + subs, Plan/Done/Abandoned = no `item-edit`. RED: no `status` subcommand at all on `origin/main` |
| SC-14 | `test-gh-sync.py:1637-1654` zero-sub-issue Ready writes nothing, no parent fallback; the only `stations["ready"]` write in the diff loops over `rec["issues"]` (`gh-sync.py:930-940`) |
| SC-15 | `git show e8a6058:DECISIONS.md:6497-6507` six-row map, one writer each; index row 214; **SKILL.md only in the working tree** — see the re-pin warning below |
| SC-16 | `test-board-lifecycle.py:658-742` — FEAT-32/FEAT-08/FEAT-09 shapes each own assertion naming dir, status, expected and actual column, plus three exemptions each asserted. RED: `board_lifecycle.py` absent from `origin/main` |
| SC-17 | `test-gh-sync.py:546-551` exact argv `--title FEAT-05-export-fix — T-01 — …`, same U+2014 as the parent title (`gh-sync.py:746`). RED: `origin/main:gh-sync.py:738` writes `f"{task['id']} — …"` |
| SC-18 | `test-board-lifecycle.py:1033-1053` (title derived from the milestone, exact argv), `:1055-1067` (no milestone → REFUSED, named, no rename call), `:1101-1112` (already correct → skipped, no call); derivation is milestone-only (`board_lifecycle.py:901-905`) |
| SC-19 | `retitle-harness.md` — 218 renamed, 0 refused, second run `0 to rename`, 436 points. See the ruling below |
| SC-20 | `check-state.sh:1357-1359` accept-set widening guarded on `feature.json` status Review; `test-check-state.py:1619-1654` v.T22a–d, both sides of the bound |

## SC-19's number: drift, not a miss

188 → 218 is drift. The criterion pinned a **measured population** (task tickets on board 3 on
2026-08-22) rather than an outcome the work controls, and the population grew before execution. The
outcome clauses all hold and are stronger than asked: 218 renamed, **0 refused**, idempotent re-run,
cost recorded. The report discloses the delta itself and even corrects its own false refusal grep.
Two textual gaps, immaterial: "already correct" is 0 rather than 218 (the selection regex excludes
renamed titles — stated in the report), and the points are recorded (436) but not compared to the
5000/hour budget the criterion names.

## Three things the ship gate must not skip

1. **`review_sha` must be re-pinned after c1 commits.** SC-15 and SC-12 grade content via
   `git show <review_sha>:<path>`. At `e8a6058` the SKILL.md phase-transition row still reads "the
   actor performing the transition" — the code reviewer's own med finding — and the fix (naming the
   main session for a `main-session-direct` segment) is **uncommitted**. Run SC-15's own command
   against `e8a6058` and it fails. The tree is correct; the pin is stale.
2. **The SKILL.md edit is unreceipted.** `receipt-harness-dev-ops-fixcycle-c1.md` "Files touched"
   lists three files and not `.claude/skills/harness/SKILL.md`, which is also modified. A fourth
   uncommitted change with no receipt behind it.
3. **SC-20's before/after capture proves only its negative half.** `diff check-state-before-T-22.txt
   check-state-after-T-22.txt` is **empty and both files contain zero `INV-26` lines** — so "differs
   by nothing except the INV-26 station findings the change removes" is satisfied by a comparison in
   which nothing was removed either. The bound itself is real (v.T22c/d), but the mutation claim
   "the second fails against an unconditional widening" I could only **derive by reading**
   `check-state.sh:1357-1359` against the fixture, not run: the write guard denies me a scratch copy
   of the script to mutate, correctly.

## Smaller record defects, none of them gaps in proof

- **Evidence-kind mislabel on three SCs.** SC-13, SC-14 and SC-17 declare `evidence: unit`, and
  their assertions live in `test-gh-sync.py`, which `run-unit-tests.sh:18` registers as
  **integration**. Assertions exist and run; the label is wrong.
- **SC-20's "once the status is Done" clause is untestable and the test says so** — the terminal
  exemption `continue`s before the per-task comparison, so no status-Done fixture can produce an
  INV-26 station finding. The author substituted status Building (v.T22c) and documented the
  substitution rather than hiding it. The criterion's sentence contains a factual error about
  `check-state.sh`; the bound it exists to protect is asserted.
- **No finding class reports an EXTRA board column.** `audit` reports declared-values-missing, never
  board-values-undeclared, so a hand-added `Abandoned` column on a live board would be invisible.
  SC-08 is met (no code path can write one), but the live direction has no detector.

## REQ coverage

11 of 11 REQs are traced by at least one task (`plan.yaml` `traces:`, all 22 tasks `status: done`,
approval `approved 2026-08-23`). REQ-07 is the one delivered short of its wording: zero findings on
board 2, two operator-accepted findings on board 3.

---

## Correction, 2026-08-23 — two of this note's own claims are now false

Appended, not rewritten (PRINCIPLES rule 15). Both were true of the tree graded here and are false
of the shipped tree after fix cycles c2 and c3.

- **SC-01's verdict is overturned, and its stated reason was wrong.** This note said "the defect is
  the sentence" and recommended amending the criterion. The operator ruled the other way: fix the
  code. Two runs was a choice, never a constraint — `project_create` returns the new project's node
  id, and both the field name and the station names come from the declaration rather than from the
  board number, so every input the field write needs is in hand at the moment of creation.
  `cmd_provision` now creates, links, writes the station field and exits 3 in one branch
  (`board_lifecycle.py:648-662`). SC-01 is **met**, proven live on board 8
  (`notes/live-provision-sc01.md`). `plan.yaml` T-04's `struck:` block, entry 1, is the record.
- **SC-07's evidence line is falsified.** It read "sole `project_single_select_extend` call site
  passes `existing + missing`". There are now **two** call sites: `_extend_to_union`
  (`board_lifecycle.py:597`, `existing + missing`, the established-board path) and
  `_fresh_board_station_field` (`board_lifecycle.py:573`, the bare declared list, reachable only
  from a project the same run created). So a code path **does** delete existing Status options —
  GitHub's default `Todo` and `In Progress`, on a board the same run just made, which holds no
  items. SC-07 as written in BRIEF.md ("no code path renames, deletes or reorders an existing Status
  option") is therefore **not met as written** and needs the operator: amend the criterion to carve
  out the same-run fresh board, or record it partial. pm does not amend a criterion.

---

## Correction 2, 2026-08-23 — the operator has ruled on both questions this note raised

Appended, not rewritten (PRINCIPLES rule 15). Correction 1 above raised two open questions and left
both to the operator. Both are now settled, and one of correction 1's own pointers had already rotted.

- **SC-07 is AMENDED, on the operator's express ruling, and is now `met`.** The criterion in
  `BRIEF.md` no longer claims provisioning is non-destructive everywhere. It claims
  non-destructiveness on every **established** board plus idempotence, with ONE named exception: a
  board the same run created, where the option set is replaced with exactly the six declared
  stations, deleting GitHub's defaults `Todo` and `In Progress`. The signed wording is kept verbatim
  inside the criterion so a later reader sees what was signed, what replaced it, and why. What forced
  the exception is a measurement, not a preference — measured 2026-08-23 on project 7, owner
  `mruangutai`, a brand-new Projects v2 project already carries a `Status` single-select field whose
  options are `Todo`, `In Progress` and `Done`, so a fresh board cannot be provisioned without either
  replacing those options or leaving two columns nobody chose. The operator ruled to replace them.
- **Correction 1's line anchors for the two call sites are already stale, and are replaced by function
  names.** Correction 1 cited `board_lifecycle.py:597` and `:573`. Re-read 2026-08-23 while fix cycle
  c4 was in flight: the two production call sites are inside `_extend_to_union` (the union,
  `existing + missing`, every established board) and `_fresh_board_station_field` (the bare declared
  list, the exact replace, reachable only from `project_create`'s own return value in the same run).
  There are still exactly TWO, both in `.claude/skills/harness/bin/board_lifecycle.py`. Cite them by
  function: that file has a concurrent writer and every line anchor either correction first carried
  moved within hours.
- **SC-07's evidence, restated so it names both sites and the amended criterion.** `_extend_to_union`
  proves the non-destructive half for established boards; `test-board-lifecycle.py` case 1 proves the
  idempotence half (a complete board and a second consecutive run each perform zero mutations);
  `test-board-lifecycle.py` case 5d proves the carve-out is exactly as wide as the amendment says
  (`updateProjectV2Field` called once, payload exactly the six declared options byte for byte, `Todo`
  and `In Progress` in no argv the fake received, the removal named on stdout). Verdict on the amended
  text: **met**, `verify: automated`, `evidence: unit`.
- **D-07 is AMENDED, not struck in part.** Its `choice:` is byte-identical to what was signed. The
  record beside it was labelled `struck_in_part`; that label was wrong under DEC-188, which strikes
  only what the tree flatly contradicts with zero room for interpretation and names the softer
  cases — dated, **narrowed**, partly overtaken — as amendments. The clause is narrowed: it holds,
  unweakened, over every established board.
- **T-04's step-5 record is relabelled an amendment too, and step-2's stays a strike.** The two are
  not the same shape. Step 2's clause ordered the run to STOP before the field work; the shipped run
  never stops there on any board, so nothing of it survives — a strike. Step 5's opening clause
  survives over every established board, which is the whole population it was protecting — an
  amendment. It is also the SAME SENTENCE as D-07's, by the same ruling and the same measurement, so
  labelling one struck and the other amended made the record contradict itself.

### Still open, and NOT edited — needs the operator's word

The authorisation covered SC-07's text and nothing else, so two statements outside it are left
standing and are reported rather than fixed:

- **`BRIEF.md`, `## The five previously-unspecified items`, item 1, last sentence: "Provisioning is
  never destructive (SC-07)."** Flatly false as written, and it cites the very criterion just
  narrowed. It is prose in a scope section, not a criterion, but it is the kind of surviving
  falsified statement DEC-188 warns nothing in this tree detects.
- **`BRIEF.md` SC-01's mechanism word "creates the Status field".** On a fresh board the field is not
  created — it already exists, and `createProjectV2Field` answered "Name has already been taken". The
  outcome SC-01 grades (after the run the Status field carries all six declared names byte for byte,
  the project exists, the repo is linked) is met and was proven live on board 8; the verb describing
  how is inaccurate. Correction 1 recorded SC-01 `met` and that verdict stands on the outcome.

---

## Correction 3, 2026-08-23 — Q3 and Q4 are ruled and applied; a fifth falsified statement is found and left standing

Appended, not rewritten (PRINCIPLES rule 15). Correction 2 raised Q3 and Q4 and left both to the
operator. Both are now ruled and applied, and the operator upheld the label argument in correction 2.

- **Q3 ruled CORRECT IT.** `BRIEF.md` scope-call item 1 no longer ends "Provisioning is never
  destructive (SC-07)." It now states non-destructiveness on every ESTABLISHED board with the same-run
  exception named, cites SC-07 as amended, and quotes the signed sentence verbatim beside the
  correction. The operator's reason for fixing rather than ticketing: the sentence sits in a scope-call,
  where a false line reads as reassurance, and a reader who is reassured stops checking.
- **Item 1's enumeration is completed in the same edit.** It listed two routes to a correct Status
  field — create when absent, add missing options to an existing field. There are THREE. The third is
  the one the live run found: on a board the same run created, GitHub has already shipped a `Status`
  single-select of the right type carrying the wrong options, `createProjectV2Field` answers "Name has
  already been taken", and the option set is replaced with exactly the six declared stations. This is
  the same incompleteness already recorded at `plan.yaml` T-04 step 3 (`record:` block, entry 4).
- **Q4 ruled ADD A NOTE, DO NOT REWORD.** SC-01's assertion, `verify:` and `evidence:` are
  byte-identical to what was signed. A note beneath them records that on a fresh board the station
  field is not created but replaced. The operator's reason: SC-01 grades an END STATE, that end state is
  met and was proven live on board 8, and rewording a signed criterion whose outcome is proven spends a
  signature for no gain. The note exists so the next reader does not write create-only code to match the
  verb — precisely the bug the live run found.
- **Labels stand as set.** The operator accepted the discriminator in correction 2: T-04 step 5 and
  D-07 are AMENDED (narrowed, with every established board surviving), T-04 step 2 stays STRUCK (no
  surviving population).

### The fifth, found and NOT edited — needs the operator's word

**`BRIEF.md`, `## Verification gaps`, the bullet "No runner can reach a live GitHub board", last
sentence: "What is therefore NOT proven by any runner: that the real GitHub API accepts the
provisioning mutations…"** That is now falsified on its own subject. The provisioning mutations WERE
run against the real API on 2026-08-23 — project 7 read back, board 8 created, linked and carrying
exactly the six declared options in one run (`notes/live-provision-sc01.md`). The clause about
*runners* remains true and should stay; what is false is "NOT proven", since the live capture is
precisely the proof, and it is the run that exposed the divergence this very bullet warns about — every
fake in the tree answers the field mutation with success, because success is what the real API returns
only when the field is genuinely absent. Leaving it reads as an open gap that has in fact been closed
by a captured live run, which understates the evidence this feature actually holds. The Q3/Q4
authorisation covered item 1 and SC-01 only, so this is reported rather than fixed.

---

## Correction 4, 2026-08-23 — Q5 applied to ONE half only, and a sixth is found

Appended, not rewritten (PRINCIPLES rule 15).

- **Q5's provisioning half: corrected.** `BRIEF.md`'s `## Verification gaps` bullet "No runner can
  reach a live GitHub board" keeps the runner clause and the fake-binary trap exactly as signed, and now
  records that the provisioning mutations ARE proven — four live runs, 2026-08-23,
  `notes/live-provision-sc01.md`. The signed sentence is quoted beside the correction.
- **Q5's reconciliation half: NOT corrected, because the evidence UPHOLDS it — and for a reason
  stronger than "no run yet".** `reconcile` does not move cards at all. Every station finding is
  classified "cannot fix, needs a human" (`notes/migration-harness-reconcile-dry.txt`, four such lines
  against board 3), so the eight findings it applied were `abandoned`-label writes on issues, and the
  two station findings that cleared on board 3 (FEAT-08 `#85`, FEAT-09 `#98`) cleared by a human hand.
  There are also no STATION-class findings anywhere in board 3's before capture (`grep -c STATION` on
  `notes/migration-harness-audit-before.txt` returns 0), so nothing in that capture could have proven
  card movement even in principle.
- **Board 3 finished at 2 findings, not 0.** `notes/migration-harness-audit-after-2-accepted.txt`'s last
  line reads `2 finding(s)` — the two `STATUS` findings for FEAT-06 `#25` and FEAT-07 `#47`, both
  operator-accepted. Board 2 finished at `0 finding(s)`
  (`notes/migration-kaya-ai-audit-after.txt`). This note's SC-04 verdict of NOT MET is unchanged and
  correct; scope-call item 3's "zero findings and exit 0 is the definition of finished" is a standing
  definition board 3 fell short of, which is recorded rather than falsified.

### The sixth, found and left standing

**`BRIEF.md`, the paragraph "The hole: a station write is REMEMBERED, not caused":** *"nothing anywhere
instructs the main session to move their cards; the only mention of `main-session-direct` in that file
is `:131`, about run counting."* Both halves are now false, and the feature's own delivery is what
falsified them. `grep -c "main-session-direct" .claude/skills/harness/SKILL.md` returns **3**, and two
of those are the table rows T-14 added that instruct the main session explicitly — one for
`start-task` on a `main-session-direct` task, one for a phase transition it holds itself. The `:131`
anchor has also drifted to `:134`.

This is the healthiest kind of falsification — a problem statement made false by the fix — but it is
still a false sentence standing in a signed brief. **SC-15 states the same baseline correctly and is
NOT falsified**, because it pins the claim to a sha: "which at `46ee87c` it names for nobody —
`grep -c` on that file returns 1, at `:131`". That contrast is the lesson: the sha-anchored copy of a
baseline survived its own fix; the unanchored copy of the same baseline did not.

Not corrected: it is outside the Q3/Q4/Q5 authorisations, and it is not falsified by the fresh-board
delete or the one-run flow.

### How completely both files have now been read

`BRIEF.md` has been read END TO END across this session — 1-278, 275-330 and 320-642, all 642 lines,
by eye rather than by grep. That is how the sixth was found; no grep for `never`, `no code path`, `zero`
or `non-destructive` reaches it. `plan.yaml` has NOT been read end to end: its 22 task `intent:` blocks
were reached by grep and by targeted reads of T-04, T-05 and the `decisions:` list only. If a seventh
exists, that is where to look.

---

## Correction 5, 2026-08-23 — I was wrong twice in Correction 4, and plan.yaml has now been read end to end

Appended, not rewritten (PRINCIPLES rule 15). **Correction 4 corrected a false sentence by inserting
two false ones.** Both are retracted here and both are fixed in `BRIEF.md`.

- **RETRACTED: "board 3 finished at 2 accepted findings, not zero."** FALSE. I read the ARCHIVED
  capture. The live capture is `notes/migration-harness-audit-after.txt` and its last line reads
  `0 finding(s)`; `notes/migration-harness-audit-after-2-accepted.txt` is the earlier state, kept as
  history. The two `STATUS` findings were cleared at `ace0b06` by adding cards for `#25` and `#47`,
  after which GitHub's native `Item closed` workflow placed both at `Done` with no column write
  (`notes/migration-harness.md`, "SC-04's two residual findings, resolved by adding the cards").
  **SC-04 is therefore MET as written** — this note's earlier NOT MET verdict predates the fix and is
  superseded here. Board 2 also reads `0 finding(s)`.
- **RETRACTED: "reconcile does not move cards at all."** FALSE, and it was a generalisation from one
  board. `_ALWAYS_FIXABLE_KINDS` in `board_lifecycle.py` is `{"STATION", "REASON", "LABEL"}` and the
  module docstring's RECONCILE section states that `STATION` is fixed by `gh_board.set_station`,
  which moves the card. Reconcile moved **six** cards on board 2 —
  `notes/migration-kaya-ai-reconcile-dry.txt` previews six `STATION` fixes (`#297`, `#296`, `#152`,
  `#83`, `#49`, `#31`) and the after capture reads `0 finding(s)`. Board 3 simply had NO `STATION`
  findings (`grep -c STATION` on its before capture returns 0), so nothing of that class existed to
  move there. The four "cannot fix, needs a human" lines I cited are the `Done`-status `STATUS`
  exemption in `_fixable`, a different class entirely.
- **So BOTH halves of the original signed sentence were falsified, and both are now corrected in
  `BRIEF.md`.** My Correction 4 claim that only the first half was is withdrawn.
- **The cause, stated so it is not repeated: I chose between two captures whose names differ by one
  word, on the strength of the name, and never checked which was current.** Every capture cited in
  the corrected bullet is now named explicitly and the archived one is labelled as archived in the
  BRIEF text itself.

### Q6 applied — the problem statement is now sha-pinned

`BRIEF.md`'s "The hole: a station write is REMEMBERED, not caused" paragraph now states its claims as
the state **at `46ee87c`**, with a separate re-derived paragraph for `8dfee3b`, and one sentence
saying why: SC-15 states the same baseline and survived its own fix because it names a sha, while the
bare copy did not. Verified at HEAD: `grep -c "main-session-direct"` on
`.claude/skills/harness/SKILL.md` returns **3**; FEAT-32's `9 of 17` still holds (re-counted from its
`plan.yaml`); its `feature.json` status reads **`Done`**, not `Review`. `#700`'s card column is not
re-read — no live GitHub call was made.

### Q7 — plan.yaml has now been read end to end, all 1973 lines. A SEVENTH, and it reddens.

**`T-11`'s `verify:` is falsified on TWO independent clauses, and `T-11` is `status: done`.**

1. It asserts `test "$(... audit | grep -c '^board_lifecycle: STATUS:')" = 2` and then greps for
   `parent #25 reads None` and `parent #47 reads None`. Those two findings were removed at `ace0b06`.
   The live capture carries **0** `STATUS:` lines and neither `#25` nor `#47` string. All three
   clauses fail. The verify's own comment states "the operator ruled not to clear them by hand" —
   that ruling was reversed by the later one to add the cards, and the verify was never updated.
   `T-11`'s own intent (steps 5 and 6, "confirm zero findings", "a line reading 0 findings") now
   matches reality while its verify does not.
2. It asserts `test "$(check-state.sh | grep -c '^  VIOLATION')" = 1`. **Measured at `8dfee3b`: the
   count is 0.** The comment pins the 1 to FEAT-34's unsigned BRIEF; that BRIEF landed at `3df18d3`.
   So this clause reddens because the defect it was pinned to was FIXED — an equality assertion on a
   transient defect count fails in both directions, and the improving direction is the one nobody
   anticipates.

Not corrected: `T-11` is outside every authorisation given (Q3, Q4, Q5, Q6). Flagged for a ruling. It
is the same decay class as the verification-gap note, in a `verify:` rather than in prose.

**Nothing else in `plan.yaml` is falsified.** One apparent contradiction was checked and is NOT one:
`D-24` calls `_EXPECT` `{building, done, pending}` while `T-02` and the BRIEF say it is built from
`stations["building"]`, `stations["done"]` and `stations["backlog"]`. Both are correct — the keys are
plan statuses, the values are stations. Line anchors in `D-24`, `T-19` and `T-22` have drifted
(`_EXPECT` is at `:1275`, `_want` at `:1345`), but each is pinned to `46ee87c` or `57e18ca`, so they
are honest stale baselines rather than false claims — the discipline this feature just wrote into its
own BRIEF.

---

## Correction 6, 2026-08-23 — T-11's verify is fixed and PROVED red-able; the claim-making notes are read

Appended, not rewritten (PRINCIPLES rule 15).

### Q8 applied — T-11's verify asserts invariants, and I watched it fail three ways

`T-11`'s `verify:` no longer greps a live mutable board. Both capture reads go through
`git show HEAD:`, never the working tree, so a capture that was never committed reddens instead of
passing. The clauses now are: the ARCHIVED capture carries exactly 2 `STATUS:` findings naming `#25`
and `#47` (immutable committed evidence that `audit` detects a real finding on a real board); the
LIVE capture's last line reads `0 finding(s)` and it carries zero `STATUS:` lines (the delivered
outcome); the DEC-174 four-file diff is empty; and `check-state.sh` reports ZERO violations, with the
narrower "no violation names FEAT-33" kept beside it. **The `= 1` equality is deleted, not
renumbered.** Both capture filenames are named in the block and the archived one is labelled
ARCHIVED, because the one-word difference is what misled a reader once already.

**Run at `8dfee3b`, extracted verbatim from the plan rather than retyped: `OK`, exit 0.** And proved
discriminating rather than assumed — three mutants, each exit 1:

| mutant | result |
|---|---|
| ARCH repointed at the LIVE capture (my exact mistake) | exit 1 |
| LIVE repointed at the ARCHIVED capture | exit 1 |
| `grep '^  VIOLATION'` -> `grep '^  note'` (a prefix that IS present) | exit 1 |

The third is the one that matters most: it proves the `check-state.sh` pipeline actually runs and its
output is really captured, so the two `test -z` clauses are not passing vacuously.

`T-11`'s `status` is untouched. The task is done; the verify was wrong, not the work.

### Q9 — the claim-making notes are read in full. TWO findings, both left standing.

Read end to end: `STATE.md`, `migration-harness.md`, `migration-kaya-ai.md`, `retitle-harness.md`,
`live-provision-sc01.md`, `handoff-build.md`, `handoff-plan.md`, `rulings-2026-08-23.md`, and the six
`research-*.md`. Skipped per the ruling: 20 receipts, 10 raw `.txt` captures, 7 `review-*.md` and
`qa-gate-c0.md` — a receipt, a capture and a review are dated records of one act, and a record of the
past does not rot the way a claim about the present does.

**EIGHTH, and the worst instance on this feature: `notes/migration-harness.md`'s header contradicts
its own final section.** Its `## Outcome` still says **"13 findings → 2 findings"** with a table row
`accepted, remaining | 2`, plus **"This report does NOT claim zero findings"**, the ruling
**"record as accepted, do not add cards"**, **"An `audit` that exits 0 is therefore impossible on this
board"**, and **"The verify now asserts ... `audit` reports exactly the two accepted findings"**. All
six are false. The same file's last section, *"SC-04's two residual findings, resolved by adding the
cards"*, records the reversal and ends `0 finding(s)`, exit 0. **A reader reads the Outcome table and
stops** — which is exactly what happened to me, one file over. This is the highest-value correction
left on the feature and it is outside every authorisation given.

**NINTH, minor: `notes/migration-kaya-ai.md`.** "Unlike board 3, this board genuinely reaches zero"
is no longer a distinction, and its "discriminating pair" table cell for board 3 after the fix reads
`2`, now `0`. The table's POINT survives untouched — that STATUS still runs on the own-repo board and
a blanket silencing would look identical on board 2 — so only the number and the contrast are stale.

**NOT new, already recorded above: SC-19.** This note's own "SC-19's number: drift, not a miss"
section already names both gaps — 188 pinned versus 218 renamed, and the points recorded (436) but
never compared to the 5000/hour budget the criterion names. One thing to put to the operator rather
than settle here: SC-19 sits in the "17 met" table while this note's prose admits two of its four
clauses fail as written. On this note's own standard — part of an enumeration is not met — the honest
verdict is **partial**. Raised, not decided.

**Two of the three "things the ship gate must not skip" appear discharged.** Item 1, re-pin
`review_sha`, is HEAD `8dfee3b` ("re-pin review_sha onto the c2/c3 tree"). Item 2, the unreceipted
SKILL.md edit, now has `receipt-harness-dev-ops-fixcycle-c4.md`. Both stated as observations for the
ship gate to confirm, not as verdicts I am entitled to close.

**`rulings-2026-08-23.md:109` was checked and is NOT falsified.** Its "both still assert" describes
the pre-fix state inside a rulings record, and ruling 5's fix did land: `D-17`'s `because` and
`T-13`'s step 6 both now read that `T-22` edits `check-state.sh` under the D-24 carve-out.

---

## Correction 7, 2026-08-23 — SC-19 graded honestly, three notes repaired, and a TENTH found in this file

Appended, not rewritten (PRINCIPLES rule 15). **But this correction also EDITS this file's own header,
and that is the point of it** — see the tenth, below.

### SC-19 — graded `not_met`, and here is why not `partial`

**The verdict is `not_met`.** I checked this file's own vocabulary before choosing rather than
importing one: its tally admits exactly three buckets — `MET`, `NOT MET`, `UNVERIFIABLE` (the header
line). `partial` occurs twice in the file but **never as an assigned verdict** — once in Correction 1
as a recommendation to the operator ("or record it partial"), once in Correction 6 as my own raised
recommendation. Grading SC-19 `partial` would add a fourth bucket to a three-bucket tally, so
`not_met` it is, on this file's own standard that part of an enumeration is not met.

**The two statements the record must carry separately, because they are different claims:**

- **The criterion's INTENT is delivered.** Every task ticket on `mruangutai/harness` names its
  feature. 218 renamed, **0 refused**, every id derived from the ticket's own milestone, second run
  reports `0 to rename`. Better than asked on every outcome clause.
- **The criterion's WORDING is not satisfied.** Clause 1 pins **188** and the run renamed **218** —
  disclosed population drift, not a miss: SC-19 pinned a population measured 2026-08-22 rather than an
  outcome the work controls, and the board grew before execution. Clause 4 required the points be
  recorded "against the 5000/hour budget"; the report recorded 436 and never named the budget.

**Clause 4 was FIXABLE and is fixed** — `notes/retitle-harness.md` now reads "436 GraphQL points
spent, of the 5000/hour budget — **8.72%**", computed here from the report's own figures (436/5000;
2 points/rename x 218 = 436, arithmetic re-run rather than carried from any dispatch). **Clause 1 is
not fixable and should not be**, so it stands as drift and the report now discloses it in its own
section. `BRIEF.md`'s SC-19 text is NOT touched — it is signed, and this is a grading correction.

### THE TENTH, and it is in this file

**This file's own header read "17 MET, 3 NOT MET, 0 UNVERIFIABLE" through six appended corrections
that changed three of those verdicts.** Exactly the defect I had just written up twice in other
people's files. It is now rewritten to `18 MET, 2 NOT MET, 0 UNVERIFIABLE` with a supersession table,
and the header states plainly that the Corrections win over the entries above them.

**And the origin of the whole capture confusion is here, now labelled.** This file's SC-04 entry cited
`migration-harness-audit-after.txt` as reading `2 finding(s)`. **That was TRUE when written at
`e8a6058`, and the same path was overwritten at `ace0b06` to read `0 finding(s)`**, its old content
preserved under the near-identical name. The citation did not rot — the file changed underneath it.
A capture path is not a stable anchor unless the capture is immutable, which is precisely why `T-11`'s
corrected verify now reads both captures through `git show HEAD:` and names which is archived.

### Q10 and Q11 applied

- **`notes/migration-harness.md`** — `## Outcome` now reads **13 → 0, `audit` exits 0**, with the
  table's last row crediting the two added cards. The first summary is quoted verbatim as superseded,
  the first ruling ("do not add cards") is quoted verbatim as superseded, and the "an `audit` that
  exits 0 is therefore impossible on this board" section is marked superseded with the part that is
  STILL TRUE separated from the part that was false: `reconcile` really will not write a `Done` column
  (`_fixable`, D-22) — what was wrong was concluding that a HUMAN could not. **A tool's limit was
  mistaken for the board's limit.** A which-capture-is-which table is now in the summary.
- **`notes/migration-kaya-ai.md`** — the "unlike board 3, this board genuinely reaches zero" contrast
  is gone (board 3 also reads zero; the difference was route, not outcome), and the discriminating-pair
  table's board-3 cell now says when it was read. The table's point is untouched.

### The SHAPE, hunted for as instructed

The pattern is **a summary section written before a reversal, with the reversal appended below it.**
Found in three files and all three are fixed: `migration-harness.md` (`## Outcome`), this file (the
header line), and — the same shape one level down — `T-11`'s `verify:`, whose comment described the
first ruling while the second had already landed. Checked and CLEAN of this shape:
`migration-kaya-ai.md` (its Outcome was always `0 findings`), `retitle-harness.md` (no ruling
reversed mid-run), `live-provision-sc01.md` (its BLUF matches its body — though it separately quoted BRIEF.md's
NOT-proven sentence by a line anchor that has since moved, now labelled as the text AS SIGNED; that is
a stale quotation, not this shape), both handoffs,
`rulings-2026-08-23.md` (a rulings log is append-only by nature and its "still assert" is correctly
historical), and the six `research-*.md`.
