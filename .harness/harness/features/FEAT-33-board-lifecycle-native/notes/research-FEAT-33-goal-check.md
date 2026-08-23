# Goal-check — FEAT-33 — 17 MET, 3 NOT MET, 0 UNVERIFIABLE

Graded against the working tree at `e8a6058` + fix cycle c1 (uncommitted). Suite and gate re-run by
me, not read off a report: `run-unit-tests.sh` exit **0**, `grep -c '^FAIL'` = **0**,
`test-board-lifecycle.py` PASS (line 1248 of the captured log); `check-state.sh` exit **0**,
`grep -c '^  VIOLATION'` = **0** (condition: FEAT-34's BRIEF signature is uncommitted — the 0 depends
on it).

## The three that are not met

- **SC-01 — NOT MET, and the defect is the sentence.** The criterion says one run against an owner
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
- **SC-04 — NOT MET.** `migration-harness-audit-after.txt` reads `2 finding(s)`, not zero (#25, #47
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
