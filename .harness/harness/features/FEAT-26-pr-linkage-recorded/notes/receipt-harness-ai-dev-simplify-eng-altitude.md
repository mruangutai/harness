# ALTITUDE — FEAT-26 build diff (HEAD `9a30ea5`) — receipt

Scope: code only (gh-sync.py, check-state.sh, feature-schema.json, SKILL.md, plan.yaml template,
DEC-200). No source file touched by this pass. All line numbers re-derived at HEAD via
`git show 9a30ea5` and direct `sed -n` reads of the worktree files, quoted below.

## Finding 1 — INV-28 vs INV-21 in check-state.sh: same skeleton, not a new duplication

`check-state.sh:1044-1084` (INV-28, comment 1044-1061, code 1062-1083) vs `check-state.sh:908-941`
(INV-21, comment 908-912, code 913-941).

Isolated the two code bodies (`sed -n '913,941p'` = 29 lines vs `sed -n '1062,1083p'` = 22 lines)
and `diff`'d them. Byte-identical lines: the gate (`if cj and (cj.get("github") or {}).get("sync"):`),
the glob loop, `feat = os.path.basename(...)`, `try:`, `except Exception as e:`, and the `continue`
after the parse-failure `bad.append`. That is 6 of ~22-29 lines identical verbatim; three more
(`gdoc`/`pdoc = harness_yaml.load_file(fy) or {}`, the `bad.append` message, `INV-21` vs `INV-28`
label) differ only in variable name and invariant number. After the parse guard the two predicates
diverge completely — INV-21 reads a nested `github` sub-block and checks issues/parent; INV-28 checks
top-level `status`/`pr` with an explicit bool-exclusion.

Cost: two engineers maintaining the same glob+try/except+"cannot be checked" idiom independently,
each free to drift (INV-21 catches `harness_yaml.YamlParseError` implicitly via bare `Exception`,
INV-28 does the same — consistent today, but nothing enforces it staying that way).

But: `grep -c` of the same `glob.glob(os.path.join(H, "*", "features", "*", "feature.json"))` line
shows **six** occurrences in this file (lines 177, 573, 708, 914, 953, 1063) — five existed before
this commit; INV-28 is the sixth data point of an idiom this file already repeats five times over.
This diff did not introduce the duplication pattern; it added one more instance of an established
(if unfactored) house style. Extracting a shared `for feat, doc in each_feature_json(H, bad, tag):`
helper is a legitimate simplification, but it is pre-existing architectural debt across the whole
file, not something T-05 introduced or was obligated to fix while adding one invariant.

Alternative: a shared iterator/helper that yields `(feat, doc)` and appends the standard parse-failure
message to `bad`, parameterized only by the invariant tag, collapsing all six sites to their
predicates.

**briefing-row** — real, worth a lead-level ticket to defactor all six sites together; not a defect
in T-05's specific 22 lines, which correctly followed the file's existing convention.

## Finding 2 — pr-required-on-Done: gate, not schema — and that is the right home

`feature-schema.json`'s only change this commit (`git show 9a30ea5 -- .../feature-schema.json`) adds
the `source_issues` array (type/shape validation only — integers, not bools/strings; confirmed by
`test-validate-feature-json.py`'s five new cases, e.g. `case_rejected_source_issues_quoted_number`).
The schema carries no `if status==Done then required: [pr]` conditional, and none was added.

The "Done implies pr recorded" rule lives entirely in `check-state.sh`'s new INV-28 block
(`check-state.sh:1073`, `str(pdoc.get("status", "")).split()[:1] != ["Done"]`) as a WARN.

This is the right home, and by direct precedent: INV-21 — same file, same warn, same
"the mirror never gates" reasoning — already governs a structurally identical cross-field,
workflow-conditional rule (issues recorded implies parent recorded) and was never put in the schema
either. A JSON Schema validates a *document's* shape; whether a `Done` feature's `pr` is populated is
a *state-machine* invariant over the mirror, which is exactly what `check-state.sh`'s INV-NN series
exists to hold, and it is explicitly non-gating (DEC-200: "the new invariant is warn, not violation").
Putting it in the schema would make an absent `pr` a hard validation failure on every non-terminal
feature, which is wrong — `pr: null` is legal until `Done`.

**leave** — home is correct, confirmed by precedent (INV-21) and by the mirror's declared
never-gates status (DEC-138, DEC-200).

## Finding 3 — cmd_closes: single-caller, but consistent with the file's own convention

`gh-sync.py:868-884` (`def cmd_closes(feat_dir):` through the two-line body). Exactly one call site:
`gh-sync.py:988`, `cmd_closes(feat_dir)` inside `main()`'s `if cmd == "closes":` branch
(`gh-sync.py:982-988`). No test imports `cmd_closes` directly — `test-gh-sync.py`'s three
`closes`-labelled cases (`_closes_fixture`, lines ~1554-1591) all invoke it via `run(["closes", ...])`,
i.e. through the CLI, same as every other subcommand.

Deletion test: delete `cmd_closes`, inline its two-line body (`rec = load_recorded(feat_dir); for n
in rec["source_issues"]: print(...)`) at the `if cmd == "closes":` site — complexity does not reappear
anywhere else, because there is nowhere else. By the letter of the deletion test this is a pass-through.

But every other subcommand in this file (`cmd_open`, `cmd_start_task`, `cmd_close_task`, `cmd_abandon`,
`cmd_backlog`, `cmd_ship` — confirmed via `grep -n 'def cmd_'`) has exactly the same shape: one
function, dispatched from exactly one site in `main()`. `cmd_closes` is not a special case bolted on;
it is the file's uniform convention (one function per subcommand, argument parsing separated from
action) applied to an eighth case. Singling it out for inlining would make it the one subcommand that
breaks the pattern the other six establish.

**leave** — consistent with the file's established one-function-per-subcommand shape; not a special
case.

## Finding 4 — the exactly-one merged-PR rule: three restatements, but along the existing table's grain

Rule stated in: (1) `gh-sync.py:536-551`, `_record_pr`'s docstring ("EXACTLY ONE is the rule, not
first-match..."); (2) `SKILL.md`'s sync table, new row ("derives the number from the recorded branch
when that branch carries **exactly one** merged pull request..."); (3) `DECISIONS.md` DEC-200
("Chose: ... only when exactly one merged pull request is found. Zero, two-or-more...").

Checked whether this is new duplication unique to this row: read the six pre-existing rows in the
same SKILL.md table (`SKILL.md:190-196`, e.g. the `abandon` and `ship` rows). Each pre-existing row
already restates its own subcommand's core rule in the same style — e.g. the `ship`/`abandon` rows
restate the `parent_origin` conditional-close rule that also lives in code (`cmd_ship`/`cmd_abandon`
docstrings) and in DEC-138/D-01. So a rule stated in code-docstring + SKILL.md-row + a DECISIONS.md
entry is this table's established convention for every row, not something T-07/T-08 introduced anew.

The underlying drift risk (three copies, no single authority, nothing forces the other two to update
if `_record_pr`'s threshold logic changes) is real, but it is a property of the whole sync table's
long-standing convention, and singling out this one row for a different treatment (e.g., "see DEC-200"
instead of restating) would be the inconsistent choice, not the consistent one.

**leave** — matches the table's pre-existing convention across all rows; the drift risk is real but is
the table's design as a whole, not this row's departure from it.

## Not raised (in scope but produced no finding)

- `_record_pr` itself: single implementation, two call sites (`cmd_ship` at `gh-sync.py:925`, the
  `record-pr` subcommand at `gh-sync.py:1045`) — the EXACTLY-ONE *logic* itself is not duplicated,
  only its prose description is (Finding 4).
- `cmd_ship`'s ordering of `_record_pr` before `_record_status` — structural, commented, not a depth
  concern.

## Summary

Four findings, all resolved to **leave** or **briefing-row**; none to **fold-in**. The pattern across
all four: what looks at first read like a new special case (INV-28's near-duplicate of INV-21,
`cmd_closes`'s single caller, the exactly-one rule's three homes) turns out, once measured against the
rest of the file/table, to be this codebase's *existing* convention applied consistently to an eighth
case — not a new departure this diff should be faulted for. The one real, worth-flagging debt
(finding 1's six-times-repeated glob+parse idiom in check-state.sh) predates this commit by five
instances and is sized as a lead-level defactoring ticket, not a fix owed by T-05.
