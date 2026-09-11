# BUG-285 — parity alignment, the BRIEF half and the verification (final amend)

**BLUF.** BRIEF.md is now aligned with the landed plan: the wrong-typed-members row is recorded
CLOSED by aligning `load_factory` onto `_opt_int`'s tolerance, the three deliberate contract
differences are recorded on the same footing as each other, SC-14 matches the twelve-input set and
D-09's seven-of-twelve figure, SC-15 mandates a two-part enumerated docstring with no convergence
claim in any spelling, and SC-06 now grades the coercion's PLACEMENT below the refusals. One plan
defect surfaced in the sweep and was fixed through `plan-merge.py amend`: **D-08's `WHAT IS LIVE
NOW` clause still asserted "ten inputs" and "one surviving divergence"** — both false after D-16.
`approval:` is byte-identical (`sha256 6f59dc091792…`, the figure the previous spawn recorded) and
no `panel:` key was written.

## What changed in BRIEF.md

- **Risk** rewritten: "all nine closed", the ninth row's disposition naming the incident it defends
  (`_opt_int` docstring, `gh-sync.py:515-518` — a quoted `"7"` read as ABSENT made gh-sync create a
  duplicate parent/milestone). The old eight-closed/one-KNOWN-OPEN framing is quoted in a
  **SUPERSEDED** block with the date and the reason, not deleted (rule 15; D-08's house form).
- **Three deliberate differences** added with their reasons, matching D-06 verbatim in substance:
  (i) neither reader detects a duplicate key (no measured incident; compensating Constraint);
  (ii) both refuse YAML-only (the point of the feature); (iii) `issues` KEY ADMISSION still differs
  — **not closed here, an open question for the operator.**
- **SC-14**: twelve inputs, value-parity group stated (`parent == 7`, `issues == {"T-01": 12}`,
  bool `None`), exclusion clause withdrawn as false, figure now seven of twelve (six verdict + one
  value) per D-09.
- **SC-15**: two-part enumeration — identical classes, then deliberate differences with reasons;
  the "ONE class is not identical" mandate withdrawn as false; `verify:`/`evidence:` untouched.
- **SC-06**: new clause grading the coercion — `_opt_int` by value, nested in `load_factory`, bool
  excluded, sitting BELOW both refusals; hoisting a refusal or turning a coercion miss into one
  FAILS. This is the composed-function check (T-02 items 5 and 6e). **SC-16 unchanged** — it grades
  the absent path behaviourally and the coercion cannot reach it.
- **Constraints**: `_opt_int` explicitly not edited in either direction (D-16).
- **Verification gaps**: SC-14 bullet re-figured; the KNOWN-OPEN bullet replaced by the
  key-admission gap. **Non-UTF-8 stays closed once, in the Q7 fold** (SC-11/12/13, T-04) — no new
  criterion minted.

## The three deliberate differences, verified at source before writing

All held as stated in D-06; nothing corrected.

- (i) `load_recorded` parses with `json.loads` (`gh-sync.py:566`) → last-wins; `load_factory` after
  T-02 does the same. No incident behind the lost `DuplicateKeyError` refusal.
- (ii) both refuse a YAML-only document — `gh-sync.py:566-574` today, `load_factory` after T-02.
- (iii) **measured at HEAD `6cb113f4`:** `gh-sync.py:613` is
  `if n is not None and re.fullmatch(r"T-\d+", str(k).strip())`; `factory_decompose.py:139-141` is
  `factory["issues"][str(k)] = v` with no key filter. So `{"issues": {"X-1": 5}}` → `{}` on one
  side, `{"X-1": 5}` on the other. Exactly D-06's statement.
  **One thing I had to correct in my own first draft:** I had written that (iii) survives because it
  "sits outside the sites this feature touches". False — `:613` is INSIDE `load_recorded` and the
  `issues` loop is INSIDE `load_factory`, so the Constraints permit reaching both. It survives by
  CHOICE: no measured incident, not the fail-open this bug removes, and no ruling on which
  admission policy is right. D-06 never claimed a constraint barrier; BRIEF now matches it.

## The five fail-open closures and the absent path

`load_factory`'s refusals (T-02 items 5a/5b) all sit at or below line 120; the **absent path is
`factory_decompose.py:114-115`** — `if not os.path.exists(path): return factory` — read at HEAD and
above every line T-02 touches. **Method:** re-read the function at HEAD (`:111-141`) and matched
each T-02 intent item to its line; item 1 starts at the `try` (`:120`), 5a replaces `:124-125`, 5b
replaces `:126-128`, 6 replaces `:133-135` and `:137-141`. No item names `:112-115`, and 6e forbids
hoisting a refusal above the member reads. SC-16 + T-02's own `factory key absent` / `file absent`
verify rows are the behavioural pins.

## Sweep — seven items, each with its pointer

1. **`files:` exist or are self-created** — `test-gh-sync-open.py`, `factory_decompose.py`,
   `gh-sync.py` EXIST; `tests/unit/test-factory-decompose-loader.py` (T-03) and
   `tests/unit/test-feature-json-readers.py` (T-05) ABSENT and created by their own task. PASS.
2. **No pre-split monolith, no rotted anchor** — zero matches for `test-gh-sync.py` in plan.yaml and
   BRIEF.md; all **33 distinct `.py:line` anchors** resolve and are in range at `6cb113f4`, and the
   load-bearing ones were content-verified (`gh-sync.py` 512/515/518/527/551/556/559/561/566/567/
   572/578/583/586/588/613; `factory_decompose.py` 35/46/111-141/480/515; `test-gh-sync-open.py`
   13-25/350/361/396/399/401/426/442/474; `gh_sync_support.py` 144/830/844-850;
   `test-factory-decompose.py` 426-437 = case `(1c)`; `test-factory-cli.py` 11-15/28;
   `harness_yaml.py` 224/242/254/259/263; `factory_cli.py` 40-42/50-52/88-96). PASS.
   *Out of scope, noted:* `tests/unit/test-gh-cost-log.py:287` still cites the monolith in a
   docstring — a repo-side staleness, not this plan's.
3. **No FAIL-line grading of the unit runner** — every one of the four mentions in plan.yaml
   (`:904-907`, `:1064-1069`, `:1263-1267`, `:1481-1485`) forbids it and mandates exit status;
   BRIEF SC-10 forbids it explicitly. The direct-run FAIL counts are for the pole files and the new
   unit file, which print zero on green. PASS.
4. **SC well-formedness** — all 16 SCs carry exactly one `verify:`; the nine `automated` ones name
   `unit` or `integration`, both live in `.harness/harness.json` `test_kinds`. PASS.
5. **REQ/task traceability** — union of `traces:` = REQ-01…REQ-12, no gap; every task traces ≥1
   REQ. PASS.
6. **`depends_on` + file disjointness** — T-01 [], T-02 [], T-03 [T-02], T-04 [T-01],
   T-05 [T-02,T-04]: acyclic, topological. Each task's `files:` is unique to it, so no two tasks
   edit one file. PASS.
7. **BRIEF table vs `notes/research-BUG-285-parity-survey.md`** — 9 DIFFERENT rows in the survey
   (empty file, non-UTF-8, top-level list/string/int, non-mapping block key, wrong-typed members,
   duplicate keys, YAML-only) and 9 accounted for in Risk; 4 SAME rows (absent, invalid-JSON text,
   block key absent, valid control) are not dispositions. Row for row. PASS.

## Verification, as run

- `python3 .agents/skills/harness/bin/check-plan-routes.py <plan.yaml>` from
  `/Users/molchairuangutai/GitHub/harness` → **exit 0**, `0 violation(s) across 1 plan(s)`, `OK` for
  all five tasks. (Passing the plan path is required — bare invocation reports other features.)
- `harness_yaml.load_plan(plan.yaml)` after the amend → parses; `approval:` raw block
  `sha256 6f59dc091792…` (unchanged); `panel:` still `last_run 2026-09-11-02-planpanelc2-validator`,
  cycle 2, 3 readers, 6 findings with unchanged severities and dispositions; `lanes:` unchanged;
  5 tasks, 16 decisions.
- `plan-merge.py amend --key decisions --id D-08 --field choice` → `AMENDED decisions:D-08.choice` /
  `APPLIED …/plan.yaml`, exit 0. The only plan.yaml write this spawn made.

## Open questions

- **Q1 (operator, non-blocking):** the `issues` KEY ADMISSION difference — `T-\d+`-only and
  stripped on one side, verbatim on the other. Separate ticket or widen? Recorded in Risk (iii),
  D-06 and the Verification gaps; no criterion here.
- **Q2 (main session, blocking the ship decision, not the plan):** `approval.status` is still
  `approved` at `2026-09-09`, but the decision set has grown by D-14/D-15/D-16 and T-02/T-05 changed
  materially since. Re-planning resets approval; only the main session can write that block.
