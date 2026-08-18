# FEAT-23 final-pass code review — pin `afc8cfd` (final-pass member: harness-code-reviewer)

**Branch confirmed:** `git rev-parse feat/FEAT-23-ship-flow-fixes` == `afc8cfd97ac6ced14fc1d40372336b972f84733e`. All source read via `git show afc8cfd:<path>`.

## Probe A — PASS-transfer claim: UPHELD

`git diff --name-only 490c37c afc8cfd -- '*.py' '*.sh' '*.ts'` → **empty**. Zero executable files
changed. Corroborated independently by the operator's own measurement in `bc498e4` ("zero .py/.sh/.ts
files changed between 490c37c and 18a2e05"); `afc8cfd` adds only one further STATE.md fix on top.

**Full unfiltered `git diff --name-only 490c37c afc8cfd`, 35 files:**
```
.claude/skills/harness-simplify/SKILL.md
.harness/expertise/harness-ai-dev.md
.harness/expertise/harness-backend-dev.md
.harness/expertise/harness-code-reviewer.md
.harness/expertise/harness-data-engineer.md
.harness/expertise/harness-dev-ops.md
.harness/expertise/harness-documentor.md
.harness/expertise/harness-eng-lead.md
.harness/expertise/harness-orchestrator.md
.harness/expertise/harness-pm.md
.harness/expertise/harness-product-lead.md
.harness/expertise/harness-qa.md
.harness/expertise/harness-security-reviewer.md
.harness/expertise/harness-ui-reviewer.md
.harness/expertise/harness-validator-lead.md
.harness/harness/docs/DECISIONS-INDEX.md
.harness/harness/docs/DECISIONS.md
.harness/harness/features/FEAT-23-ship-flow-fixes/STATE.md
.harness/harness/features/FEAT-23-ship-flow-fixes/feature.json
.harness/harness/features/FEAT-23-ship-flow-fixes/notes/handoff-build.md
.harness/harness/features/FEAT-23-ship-flow-fixes/notes/qa-2026-08-17-9-qa-validator.md
.harness/harness/features/FEAT-23-ship-flow-fixes/notes/receipt-harness-ai-dev-2026-08-17-13-distill-eng.md
.harness/harness/features/FEAT-23-ship-flow-fixes/notes/receipt-harness-backend-dev-2026-08-17-13-distill-eng.md
.harness/harness/features/FEAT-23-ship-flow-fixes/notes/receipt-harness-data-engineer-2026-08-17-13-distill-eng.md
.harness/harness/features/FEAT-23-ship-flow-fixes/notes/receipt-harness-dev-ops-2026-08-17-13-distill-eng.md
.harness/harness/features/FEAT-23-ship-flow-fixes/notes/receipt-harness-dev-ops-2026-08-17-13-verify.md
.harness/harness/features/FEAT-23-ship-flow-fixes/notes/receipt-harness-documentor-2026-08-17-12-dec195-product.md
.harness/harness/features/FEAT-23-ship-flow-fixes/notes/research-FEAT-23-goalcheck-490c37c.md
.harness/harness/features/FEAT-23-ship-flow-fixes/notes/review-harness-code-reviewer-2026-08-17-11-panel-validator.md
.harness/harness/features/FEAT-23-ship-flow-fixes/notes/review-harness-security-reviewer-2026-08-17-11-panel-validator.md
.harness/harness/features/FEAT-23-ship-flow-fixes/notes/review-harness-ui-reviewer-2026-08-17-11-panel-validator.md
.harness/harness/features/FEAT-23-ship-flow-fixes/notes/ship-review-2026-08-17-13.html
.harness/harness/features/FEAT-23-ship-flow-fixes/notes/ship-review-2026-08-17-13.md
.harness/harness/features/FEAT-23-ship-flow-fixes/observations/harness-orchestrator.md
.harness/harness/features/FEAT-23-ship-flow-fixes/observations/harness-product-lead.md
```
34 of 35 are `.md`/`.json`/`.html` under Expertise, `DECISIONS.md`/`DECISIONS-INDEX.md`, or FEAT-23's
own `notes/`/`observations/`/`STATE.md`/`feature.json` bookkeeping — pure record/prose. The one
substantive file, **`.claude/skills/harness-simplify/SKILL.md` (+18 lines)**, is a doc/skill file, not
`.py`/`.sh`/`.ts`, so it doesn't affect the transfer criterion as stated — but it matters to Probe C
(below): it lands SC-05's fix (ALTITUDE angle gains its plan-surface/code-surface pair, :90-96) plus
the "ceiling of one fix" apply bound (:100-107), matching `DECISIONS.md`'s DEC-195 update in
lockstep. Both edits are authored directly by the operator (`2cba9fb`, `bba5551`, both
`Mike Ruangutai <molchair@gmail.com>`), consistent with `check-domain.sh --resolve` returning NOBODY
for that path and the goal-check's routed lane (`main-session-direct`) — not autonomous scope creep.
`git log --oneline 490c37c..afc8cfd` carries no `[harness:human]`-tagged commit; the two operator
commits are tagged `[harness:sc-05]` and their content is reviewed above and in Probe C, not skipped.

**Conclusion: qa's gate green and the earlier panel's PASS (at `490c37c`) transfer to `afc8cfd`
without qualification for anything `.py`/`.sh`/`.ts`.** No code-behavior claim needs re-verification
on that account. The delta since is exclusively a documentation/decision-record fix (closing SC-05,
a goal-check-caught gap) plus feature bookkeeping.

## Probe B — `board-station.py`: one confirmed HIGH-severity defect, untested

**Finding B-NEW-1 (HIGH, blocks operator acceptance).** `main()`'s argument gate at
`board-station.py:65` —

```
if not issue_arg.isdigit() or int(issue_arg) <= 0:
```

— treats `str.isdigit()` as equivalent to "is a positive integer" — it is not. Empirically confirmed
(git status on `board-station.py` is clean, so the executed working-tree copy is byte-identical to
the object at `afc8cfd`; the traceback's line numbers 65 and 127 match the pinned file read via
`git show`):

```
$ python3 .claude/skills/harness/bin/board-station.py '²' Plan
Traceback (most recent call last):
  ...
  File ".../board-station.py", line 65, in main
    if not issue_arg.isdigit() or int(issue_arg) <= 0:
ValueError: invalid literal for int() with base 10: '²'
$ echo $?
1
```

`'²'.isdigit()` is `True` (superscript-2 is a Unicode digit character), so Python evaluates
`int(issue_arg) <= 0`, which raises `ValueError` **inside the gate itself**, before any root-probe or
I/O code runs (confirmed safe to execute — the crash happens at the very first statement of `main`
that touches `issue_arg`, never reaching the real board). The exception is unhandled — it is outside
the `except Exception` at `:118`, which wraps only the `gh_board.set_station` call — so it propagates
to `sys.exit(main(...))`, producing a raw Python traceback on stderr and **exit code 1**.

This directly contradicts:
- The module docstring's absolute claim: *"EXIT CONTRACT: 2 is the ONLY non-zero exit."*
- `plan.yaml` T-05 intent item 1, verbatim: *"A missing or extra argument, or an issue number that
  is not a positive integer, prints one usage line to STDERR and exits 2. That is a caller mistake,
  not an environmental condition, and it is the ONLY non-zero exit."*
- The design intent this whole tool exists to satisfy (item 6 / docstring): *"a mirror write must
  never abort planning."* A raw traceback at the head of `/harness-plan` kickoff is exactly the
  abort this tool was built to prevent — just triggered by the argument gate rather than the board
  write it was designed around.

**Untested.** `test-board-station.py` case 4 ("usage") only exercises `"not-a-number"`, which fails
`isdigit()` cleanly (short-circuits before `int()` is ever called) and correctly returns exit 2. No
case exercises a string that is `isdigit()`-true but `int()`-invalid. `SC-10`'s verdict ("all seven
required labels PASS... incl. ... usage exit 2") is therefore true of the label but narrower than the
docstring's absolute claim the label is read as certifying.

**Secondary, lower-severity observation (LOW, advisory only).** `'٥'` (Arabic-Indic digit five)
passes both `isdigit()` and `int()` — `int('٥') == 5` — so it is silently accepted and would move
**issue #5** on the real board with no indication the input wasn't ASCII. This does not violate the
letter of item 1 (it *is* a positive integer per `int()`), but it means the validator is simultaneously
broader than intended (silently accepts non-ASCII digit scripts) and narrower/crash-prone than
intended (some Unicode digit characters `isdigit()` accepts are not `int()`-parseable at all).
`isdigit()` is the wrong predicate for either direction.

**Remedy (covers both):** replace `issue_arg.isdigit()` with an ASCII-only digit check, e.g.
`re.fullmatch(r'[0-9]+', issue_arg)` or `issue_arg.isascii() and issue_arg.isdigit()`, before calling
`int()`. Add one test case exercising a Unicode digit string to `test-board-station.py` and register
it in the T-05 verify's label list.

**Not re-filed (per instructions):** B-8 (two untested environmental branches) and B-11 (harness.json
read twice) — already briefed at `ship-review-2026-08-17-13.md`.

**Everything else in the file reads as spec'd.** The environmental-precondition ladder (:76-111)
prints one `out()` line to stdout and returns 0 in every case, matching item 3/4. The board-write
`except Exception` (:118) correctly covers `gh_board.BoardError`, the unguarded `json.loads` inside
`factory_gh.run_gh`, and `OSError`, per item 6 — and correctly does **not** reach the usage gate,
which fires earlier. All environmental lines carry the `board-station: ` prefix (item 3a). A caller
that reads combined stdout+stderr text (as a planning-session transcript naturally does) can
distinguish every outcome except success vs. environmental-skip vs. write-failure by exit code alone
— all three exit 0 by design (D-02's mirror-write rule) — which is documented intent, not a defect.

## Probe C — DEC-195 / DEC-196 against code: no findings, both accurate

Re-located at `afc8cfd`: DEC-195 `DECISIONS.md:5970`, DEC-196 `DECISIONS.md:6057` (DECISIONS-INDEX.md
already reflects `@6057`, not the stale `@6049` cited in the dispatch — the index was regenerated
correctly, see T-04 verify re-run below).

**DEC-196, verified by symbol:**
- `_apply_parent_rule` (`gh-sync.py:162-196`) carries **no** `parent_origin` check — confirmed, it
  moves the parent's station unconditionally whenever a station derives and a parent is recorded.
- The CLOSE is origin-gated in both `cmd_ship` (`:728`, `if rec["parent_origin"] == "created":`) and
  `cmd_abandon` (`:671`, same condition) — confirmed, both match DEC-196's claim exactly.
- `main()`'s positional-argument shape (`:775-776`, `cmd, feat_dir = argv[0], argv[1]`) followed by
  `if not os.path.isdir(feat_dir): die(...)` before any subcommand dispatch — confirmed, and DEC-196's
  own prose states this correctly ("takes the feature directory as a positional argument... before
  any subcommand dispatch") without repeating the `plan.yaml` D-05 rationale's `argv1` error already
  recorded at B-14 (not re-filed).
- Stations map: `gh_board.set_station` (`gh_board.py:174-191`) passes a plain string to
  `factory_gh.project_field_set` (`factory_gh.py:446-469`), which resolves the option **by name**
  against the live GitHub project schema, with no declared/validated stations list anywhere in the
  tree — confirmed, matches DEC-196's claim. Issue-350 claim not independently checked against
  GitHub, per instructions ("verify what the tree does, not GitHub").

**DEC-195, position — unchanged, transfers.** `harness/SKILL.md` and `.claude/commands/harness-plan.md`
(the two files carrying the position/ordering statements — build-flow SIMPLIFY-before-pin, plan-flow
simplify-before-reviews, SC-07's ordering) are **not** in the `490c37c..afc8cfd` diff at all. SC-07
(ordering) was verified inspection-`met` at `490c37c` in the goal-check
(`research-FEAT-23-goalcheck-490c37c.md`), and since the files it depends on are untouched since, that
verdict transfers unchanged to `afc8cfd`. `DECISIONS.md:5975-5981` (build-flow paragraph) and
`:5993-5995` ("The step's position is unchanged by either bound") are present and unmodified in this
delta's prose.

**DEC-195, apply bounds — BOTH now present, matching the skill exactly.** `DECISIONS.md:6000-6012`
carries the assertion bound ("may not delete or weaken an assertion") **and** the newly-landed
ceiling bound ("carries a ceiling of one fix"... "Both bounds are stated authoritatively in
`.claude/skills/harness-simplify/SKILL.md`"). `harness-simplify/SKILL.md:100-107` carries the same
two bounds verbatim in substance. This closes the gap the `490c37c` goal-check recorded (DEC-195 had
only the assertion bound; the skill had neither) — confirmed fixed at `afc8cfd`, not half-landed:
both files changed together in the same two-commit sequence (`2cba9fb`, `bba5551`).

**T-04 verify re-run at HEAD:**
```
$ python3 .claude/skills/harness/bin/gen-decisions-index.py --stdout | diff - .harness/harness/docs/DECISIONS-INDEX.md
$ echo $?
0
```
Clean — no drift. `git status --porcelain` on `gen-decisions-index.py`, `DECISIONS-INDEX.md`, and
`DECISIONS.md` is empty, confirming the working tree matches `afc8cfd` for this check.

Not re-filed: B-13 (index generator's dropped `dispatch` tag).

## Verdict basis

Probe A and Probe C carry no blocking findings — the PASS-transfer holds and both decision entries
check out against the code exactly as recorded. Probe B's finding B-NEW-1 is the sole blocking item:
a genuine, empirically-reproduced defect in shipped code, novel (not among `ship-review-2026-08-17-13.md`'s
26 rows), contradicting an absolute documented contract at the head of every `/harness-plan` kickoff,
uncovered by the 7-case suite that otherwise reads as thorough.
