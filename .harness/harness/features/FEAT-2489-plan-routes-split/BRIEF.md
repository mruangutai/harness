# BRIEF — FEAT-2489-plan-routes-split Split check-plan-routes.py's AST audits into two gate-imported library modules

## Problem

`check-plan-routes.py` is a required CI gate. DEC-174 enumerates it, so every edit to it, and to its test file, is main-session-direct. Yet about 1,711 of its 2,691 lines (measured at 261fdf72) are not route checking. They are the canonical-reader audit and the consolidation/structure audits, and those are the parts that keep changing: FEAT-61, 62, 63, 65, 69 and 71 all iterated there. Each audit tweak therefore pays the main-session-direct tax for a gate whose routing logic it never touches. Tests also reach the audits' private helpers by loading the hyphenated script dynamically.

Separately, the canonical-reader self-test asserts a dead FEAT-71 contract: that the inventory names no feature plan. The opt-in self-test exits 1 today with two FAILs. Because no runner invokes it, nothing noticed.

## Done when — by perspective

**operator** — When I or CI run the route check, the canonical-reader audit or the consolidation audit from a complete install, I get the same verdicts, exit codes and output as before the split, for any tree and any arguments. The visible exceptions are only those the move itself implies: the canonical summary's file count is higher by exactly the number of new module files, and a finding that points at code in check-plan-routes.py points at where that code now sits. The CI workflow is untouched.

**code maintainer** — I can change an AST audit's logic without editing the enumerated gate file. I can import the audit code like any other module, and no import path leads from it back into the gate. Every test of an audit helper reaches it by an ordinary import, never by loading the gate script. The inventory and the remedy table change only where code actually moved.

**reader (qa / reviewer)** — I can grade "behaviour unchanged" against a recorded before/after comparison. The canonical self-test runs by default, asserts the inventory's real contract, and was shown red on the moved tree with the stale inventory before it went green.

## Success criteria

- SC-01 (code maintainer): Read as git diff <base> <review_sha> -- .claude/skills/harness/bin with move detection (git diff --color-moved=plain --color-moved-ws=no), the split is a verbatim move:
  - the base entry's lines from READER_CALL_CATEGORIES through the end of _run_canonical_reader_audit sit, in order, in canonical_reader_audit.py, and the rest through the end of _run_consolidation_audit sit, in order, in structure_audit.py; every moved line is byte-identical to its base line except the one T07_TERMINAL_REMEDIES key;
  - none of them remains in check-plan-routes.py, whose other lines are unchanged apart from the appended docstring paragraph, the moved LEGAL_MAIN_SESSION_TOKEN line, the dropped imports ast, collections and json, and the added import and comment lines;
  - the entry imports from the two modules exactly LEGAL_MAIN_SESSION_TOKEN, _run_canonical_reader_audit and _run_consolidation_audit, and re-exports nothing else; neither module imports or loads the entry; structure_audit.py takes _reader_source_paths from canonical_reader_audit.py, which imports nothing from structure_audit.py;
  - the .py files under bin differ from base by exactly the two module files, so there is no package and no __init__.py.

  The reviewer cites file and symbol at the pin. No automated AST checker grades this; the move-detected diff is the evidence.
  verify: inspection
- SC-02 (operator): The behaviour invariant, for every audited tree state and every argv, with the entry at the review pin run from a complete bin (both modules beside it): dispatch (including the --help quirk), the exit code of each mode (route 0/1/2, canonical 0/1/2, consolidation 0/1), output formats, finding text, finding multiset and order, and source-error behaviour, on stdout and on stderr, are those of the base entry on the equivalent base tree, once each run's root path is normalized. The sanctioned differences are this closed list and nothing else:
  - inventory rows whose call sites moved have file and id rewritten in place to the new module;
  - the one T07_TERMINAL_REMEDIES key for _task_files is re-keyed to canonical_reader_audit.py;
  - scanned_files gains exactly the two module paths;
  - the canonical summary's Python-file count rises by exactly the number of .py files added under bin, its format and unresolved count unchanged;
  - every diagnostic, on stdout or stderr and in any mode, that names a site in check-plan-routes.py at base shows each such site's location at the pin, and is otherwise identical in text and keeps its place in the finding multiset. A locator is every place a diagnostic names a source site, in any printed form: the file path with its ::symbol, and the line number wherever one is printed (path::symbol or path::symbol:line), and each Python traceback frame's File "path", line N, in NAME. A diagnostic may carry several locators, and a traceback carries one per frame; each is in the class. Membership is decided by what the diagnostic prints, never by where the printed value comes from: a locator formatted from an inventory row (as _exemption_finding and _row_label do), from a scanned AST candidate (as _unaccounted_candidate_findings does with candidate['file']), from a structure-audit AST node (relative::symbol:lineno) or by the interpreter for a frame of an uncaught exception is in the class alike; these are illustrations, not a list. Text that only looks like a locator but names no source site, such as a plan path or other input value a diagnostic echoes, is not a locator and is unchanged. SC-01's verbatim move fixes each site's location at the pin: a moved site's file becomes its module and its line number its line there; a site that stays in check-plan-routes.py keeps its file, and its line number moves only by the lines SC-01's diff removes or adds above it. Output order is the base order, and so is the order of locators within a diagnostic and of frames within a traceback, except that where a producer emits diagnostics in file-walk or line order, a relocated diagnostic takes the place that same order gives its new location. Every character outside the locators, and every diagnostic that names no such site, is byte-identical to base. This item is a consequence of the move, not a new behaviour: the producers move unchanged and only the location of the code they report on changes. For example, a blank reason on the relocated _classification_document row prints canonical_reader_audit.py::_classification_document where the base printed check-plan-routes.py::_classification_document; and an inventory whose rows is null makes the canonical audit raise a TypeError whose traceback keeps its frames in base order, the retained <module> and main frames naming check-plan-routes.py at their shifted lines and the _run_canonical_reader_audit, audit_canonical_readers, _classification_task_files and _named_plans frames naming canonical_reader_audit.py at their lines there, every other byte unchanged.

  .github/workflows/tests.yml is byte-identical to base. The reviewer grades the invariant from three kinds of evidence, none of which is the contract's scope on its own: SC-01's verbatim move and SC-05's confined inventory delta; the existing suites' fixture finding text held at unchanged expected values (SC-03, SC-04); and the sample receipt notes/equivalence-final.txt. That receipt runs the base and pinned entries on matched archive trees (the base commit, and the base commit with only the pinned bin and tests overlaid), lists every path the overlay excluded, and covers a clean state over six argv shapes (no argument, --canonical-reader-audit, --consolidation-audit, --help, both audit flags, a nonexistent plan path) and a perturbed state (a source-parse error, unclassified reader calls, broad catches, and a blanked exemption reason on the relocated _classification_document row, so at least one finding names a relocated row) over both audit modes. For each run it records the full normalized stdout, stderr and exit and the old-to-new diff, and it names the commit and the bin and tests tree ids it graded; the reviewer binds it to the pin by those tree ids. Its comparison applies the fifth item mechanically where it models it, never as a loosened or fuzzy diff, and FAILs wherever it does not. It derives and prints an old-to-new map of exactly the moved symbols (check-plan-routes.py::NAME to MODULE::NAME for each top-level name the split moved), taken from the move and never from the inventory. It rewrites, through that map, only the locator field of the stdout diagnostic formats it recognizes, which T-02 enumerates from the base source's format strings, and compares every other line exactly, echoed input values, stderr and traceback frames included, line for line and in order. It models neither line numbers nor traceback frames: a recognized line-numbered locator in check-plan-routes.py or either module fails the comparison, and so does any traceback frame the move relocates; an unchanged frame passes as identical text.
  verify: inspection
- SC-03 (reader): At the review pin, running tests/integration/test-check-plan-routes.py with no arguments runs the canonical-reader cases and exits 0 with no FAIL line. Those cases assert the true contract:
  - for every inventory row that names a plan, one check that the plan resolves through feature_corpus.corpus_path, is readable, and has a task with the row's id;
  - no document-level plan key;
  - the audit holds on a temporary root holding only bin plus exactly the named plans;
  - fixture cases in which the named-plan check refuses a missing plan and a missing task.

  No check asserts that the inventory names no plan. qa must show the failing states first: notes/red-t01-canonical-self-test.txt (the base self-test exits 1 with the two FEAT-71 FAILs); and notes/red-t03-stale-inventory.txt (on the moved tree with the base inventory, the default run exits 1 with FAIL lines only on canonical_reader_ checks, and the canonical audit exits 2 with findings naming only the scanned-file manifest, the moved rows or the new module path). notes/green-t01-default-run.txt records the default run green at T-01's checkpoint, before the move, bound to that checkpoint: its recorded commit is an ancestor of the pin that already holds T-01's test change and neither new module, and its recorded blob is the test file at that commit.
  verify: automated        evidence: integration
- SC-04 (code maintainer): At git show <review_sha>, no file under tests/ reaches a name defined in canonical_reader_audit.py or structure_audit.py through cpr(), _checker(), spec_from_file_location or any other loader of check-plan-routes.py. Each reaches them by an ordinary import, resolved from the directory of the entry under test: CHECK_PLAN_ROUTES_BIN's directory when it is set, so a mutant copy of bin is what gets tested. Each such file asserts that every audit module it imports, directly or through structure_audit's own import of canonical_reader_audit, came from that directory. Loading the entry remains only for route, main and CLI surface. The four satellite files (test-checker-structure-locks.py, test-structure-audit-single-pass.py, test-structure-audit-index.py, test-broad-catch-census.py) change only imports, loaders, provenance checks and docstrings, never an expected value; their one-traversal checks cover structure_audit's in-process entries and the --consolidation-audit CLI, and no_session_or_index_is_retained_at_module_scope reads structure_audit's namespace. Evidence: the test-file diffs at the pin, and notes/green-t04-suites.txt, which records at the graded commit the five audit test files green and the two unit files green against a copy of bin outside the checkout named through CHECK_PLAN_ROUTES_BIN. These are regression locks: no fail-first run is claimed for them.
  verify: inspection
- SC-05 (code maintainer): Read against base, tests/integration/canonical-reader-classification.json changes in exactly two ways:
  - each row whose file is check-plan-routes.py and whose symbol is now defined in one of the two modules has its file and id rewritten in place to that module, every other field unchanged;
  - scanned_files is the base list plus exactly the two module paths.

  No row is added, removed or reordered, and T07_RELOCATED_IMPLEMENTATIONS is unchanged. T07_TERMINAL_REMEDIES differs from base only by re-keying the single _task_files key to the canonical_reader_audit.py path. plan_merge/check.py's index-row comment names structure_audit._decisions_index. The reviewer reads git diff <base> <review_sha> of the JSON and of plan_merge/check.py, and compares the T07 tables in the pinned canonical_reader_audit.py with the base check-plan-routes.py.
  verify: inspection

## Verification gaps

- No SC rests on a null or excluded kind. unit and integration are active. functional and eval are excluded under DEC-187; component and ui are unresolved, but this feature has no browser or component surface.
- **"Any tree, any arguments" (operator, SC-02):**
  - Measured as samples: notes/equivalence-final.txt compares the base and pinned entries on matched archive trees, in a clean state over six argv shapes and in one perturbed state over both audit modes. It shows finding text, multiset, order and source-error output on a non-clean tree, including one finding that names a relocated row, but only for that one tree. It does not measure the fifth item's line-number part, its traceback-frame part or its location-order exception: the checker fails on a line-numbered locator in the three files and on a relocated traceback frame, and compares order exactly, and no sampled state prints such a locator, raises an uncaught exception or reorders. Those parts are carried by inspection of SC-01's diff.
  - Measured on fixtures: the pre-existing suites' finding-text assertions run at unchanged expected values (SC-03, SC-04).
  - Carried by inspection, not by an automated check: SC-01's move-detected diff shows the moved code byte-identical and the dispatch untouched. No AST-identity checker is built (plan panel cycle 1); the reviewer's reading carries the rest of the class, including module initialization (the two modules' own imports), which is judged, not measured.
  - Not covered, by design: the invariant is stated for a complete install. A bin missing either module now fails at import (traceback, exit 1) where the base entry ran. That is new failure surface, covered only by case 19b's copy list for its fake bin.
  - Disclosed departure from the ruling, for the signer to accept or refuse: grilling Q3 sanctions "exactly these, nothing else" (its items 1 to 4). SC-02's fifth item adds one more: wherever any output names a place in check-plan-routes.py's source (a finding's file::symbol, a file::symbol:line, or a Python traceback frame's File "...", line N, in NAME), it names where that code sits after the split. Moved code is named in its new module at its line there; code that stays is named in check-plan-routes.py at a line shifted only by the lines removed or added above it. The order of findings, of the places within one finding and of a traceback's frames stays the base order, except that a producer which orders its output by file or line places a relocated finding by its new location. Every other byte is unchanged, and an input value the output echoes is never rewritten, even when it looks like a source location. It is derived from the move SC-01 requires, not a new behaviour. Without it SC-02 is unsatisfiable by that move on any tree where an output locates moved code, a crash traceback included (plan panel cycles 2 to 4). Refusing it returns the plan to Plan with SC-02 unsatisfiable as ruled.
- **The CHECK_PLAN_ROUTES_BIN mutant path:** each file's provenance check (SC-04, inspection) plus one recorded run of the two unit files against a copied bin (notes/green-t04-suites.txt). The three integration files are not run against a copy.
- **SC-01, SC-02, SC-04, SC-05:** inspection. The equivalence receipt's tool is a one-time feature-notes script, not a permanent test (grilling Q3).
- **SC-04's satellite files** are regression locks, green at base and at the pin; a move changes no expected value, so no fail-first run is claimed.
- No SC requires user-run UAT.

## Constraints

- **DEC-174 BLOCKS team execution.** `check-plan-routes.py` and its test file are enumerated, so every task is main-session-direct: red first, tests run explicitly, a human reads the diff. No task routes to harness-eng-lead.
- **DEC-174 SUPPLIES the payoff and the proof standard.** Its library clause ("A module a gate imports is not itself a gate") makes the two new modules squad-writable libraries after this cutover, while the entry stays the enumerated gate. Its cutover proof (an identical violation set before and after) is SC-02's shape.
- **DEC-183 BLOCKS** any change to the route and canonical summary formats that `.github/workflows/tests.yml` parses, and to the workflow itself.
- **DEC-179 BLOCKS** any change to route resolution. The route section stays byte-for-byte in AST terms.
- **DEC-188 SUPPLIES** why the historical line citations are left alone. The route section they cite does not move, and line drift is not a contradiction.
- **DEC-209 SUPPLIES** the review-time code grade. Every moved function graded 4 or 5 at 261fdf72 (facts §8), so file-local preimages cannot block the move.
- **SPEC "Structure-audit guardrail" (.harness/harness/docs/SPEC.md) BLOCKS** any retained module-scope session or index and any second traversal. The new modules keep fresh per-invocation state.
- **DEC-232 SUPPLIES** the anchor forms used by the plan.
- **Shape ruled by the grilling (Q2):**
  - Two flat modules under bin, `canonical_reader_audit.py` and `structure_audit.py`; no package.
  - `_reader_source_paths` lives in the canonical module, and the structure module imports it.
  - Neither module imports the hyphenated entry.
  - `LEGAL_MAIN_SESSION_TOKEN` moves to the canonical module, and the entry imports it back.
  - The CLI dispatch and `tests.yml` are unchanged, and there are zero re-exports.
- **Honest size:** this is a move, not a deletion. Net LOC is about +30 to +80 [INFERENCE: module docstrings and import lines]. A 2,691-line required gate becomes a gate of about 980 lines plus two gate-imported libraries. No SC is a line count.
- **Product checkout:** the assigned Harness feature worktree. AGENTS.md is the project context. Specification and decisions live in `.harness/harness/docs/SPEC.md` and `.harness/harness/docs/DECISIONS.md`. `docs/spec.md`, `docs/decisions.md` and `docs/architecture.md` do not exist in this checkout; the module docstrings supply the architecture guidance.

## Out of scope

The non-goals below are carried from the grilling ruling (Q5, Q6 and the Destination summary).

- No audit-rule logic changes, and no route-logic changes. The split is a move.
- No `tests.yml` edits. Nothing in-tree can verify a workflow edit (DEC-183).
- No argparse or `--help` fix. The dispatcher quirk is part of the invariant.
- No split of `test-check-plan-routes.py` into several files. Splitting it would drag the selector dispatch along for no behaviour gain.
- No new `SELF_GRADED_FILES` entries. That set is a historical per-feature pin, not live coverage.
- No consolidation of `_scan_reader_tree` with `_AuditSession.census`. Canonical detection deliberately keeps its own visits.
- No handling for rows naming shipped or archived plans beyond task 1's existence assertion.
- No package and no `__init__.py`.
- No DECISIONS.md citation renumbering, and no updates to historical line citations (`harness_boundary.py`, `test-wayfind.py`, DEC-179, the test file). The split moves no line any of them cites.

## Approval

status: approved
approved-by: Mike Ruangutai (delegated to fable-advisor)
date: 2026-11-24
