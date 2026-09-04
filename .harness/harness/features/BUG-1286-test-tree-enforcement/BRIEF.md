# BRIEF — BUG-1286 repository-wide test-tree enforcement

## Problem

DEC-213 made the directory the kind: Harness's executable tests live under `tests/unit/**` and
`tests/integration/**`, probes and review instruments under `tests/manual/**`. The predicate that is
supposed to hold that shape, `suite_layout.violations()`, only looks in two places — inside `tests/`
and inside `.claude/skills/harness/bin/` (`suite_layout.py:20-33`). Everywhere else in the tracked
repository is unexamined, so a test-shaped file added under `.harness/`, `.github/`, a feature's
`evidence/` directory or any other tracked path is never refused. It also never runs: the runner
selects `tests/unit/test-*.py` and `tests/integration/test-*.py` by directory, while
`harness.json` `test_kinds.unit.detect` claims `**/*.test.*|**/*_test.*|**/test_*.py` repository-wide.
The cost is a test that qa's kind map believes exists and no runner ever executes — a green suite
that is silently smaller than the map says, discovered only when someone reads the file.

## Goal

Issue #1286 should end with the `tests/**` tree actually enforced: every tracked test-shaped file in
the repository is either inside the right test directory or an exception somebody wrote down and
justified, and the refusal arrives before any test runs. Product checkouts keep discovering their own
tests exactly as they do today, and the governing decision says what the code now does.

## Requirements

- REQ-01: A tracked test-shaped Harness file anywhere outside the test tree is refused, and the
  refusal reaches the operator before any test executes.
- REQ-02: A refusal names every offending path, in a stable order, rather than stopping at the first.
- REQ-03: Inability to establish the authoritative tracked-file set is itself a refusal — never a
  clean result and never a partial scan reported as complete.
- REQ-04: Legitimate files keep working: valid `tests/unit/**`, `tests/integration/**` and
  `tests/manual/**` files stay accepted, manual files stay outside active test-kind discovery, and
  ordinary support modules that tests import stay where they are.
- REQ-05: Every permitted test-shaped exception is an exact, documented classification, and a stale,
  broadened, duplicated or unnecessary exception is refused.
- REQ-06: The complete set of test-shaped matches outside the test tree at the reviewed revision is
  measured, each with a recorded disposition, by an instrument anyone can re-run.
- REQ-07: The governing record describes the invariant that shipped, with no narrower claim left
  standing as current behaviour.
- REQ-08: Product-checkout test discovery and the runtime mutation-snapshot scope are unchanged.

## Constraints

- Supplied by DEC-213: the directory-is-the-kind rule, `tests/manual/**` as the home for probes and
  review instruments, and the write grants on `tests/**` (`harness-qa`, `harness-backend-dev`,
  `harness-dev-ops`). This feature extends that decision's predicate; it does not reopen it.
- Supplied by DEC-197: a test file matching two `detect` globs resolves to the kind that names it
  explicitly. The fix must not need a `detect` change to be correct.
- DEC-213 must be amended in place, with `DECISIONS-INDEX.md` regenerated in the same change: the
  index records each entry's source line, so lengthening an entry moves every later anchor.
- Out of scope, from the ticket and the intent artifact: redesigning product-checkout test
  discovery; broadening runtime mutation snapshots; renaming non-test support modules merely because
  tests import them.
- Unchanged surfaces, committed: `.harness/harness.json` `test_kinds` and `test_matrix`; the runtime
  mutation snapshot's bin-only scope; `run-unit-tests.sh`'s kind selection and exit codes.

## Success Criteria

- SC-01: A tracked test-shaped file placed outside `tests/**` in a real Git fixture is reported by
  the predicate, naming that path.
  verify: automated        evidence: unit
- SC-02: The assertions covering SC-01 were written before the production edit and are demonstrated
  failing first. Graded by qa's test-first audit, which must record the red result of running the
  new `tests/unit/test-suite-layout.py` assertions against `suite_layout.py` as it stands at the
  base commit — before T-01's edit to the predicate — and name the assertions that failed. A
  passing unit run at review time is not evidence for this criterion and cannot discharge it.
  verify: inspection
- SC-03: With several offending paths present at once, all of them appear in the predicate's output
  in a stable sorted order across repeated runs — not just the first.
  verify: automated        evidence: unit
- SC-04: With an offending tracked file present, the runner exits 2 with its `MISCONFIGURED:` lines
  and no test sentinel output appears on stdout.
  verify: automated        evidence: integration
- SC-05: When the root claims to be a Git checkout but the tracked-file set cannot be enumerated, the
  predicate reports a violation naming the enumeration failure — it does not return clean and does
  not report a partially scanned set as complete.
  verify: automated        evidence: unit
- SC-06: In a fixture holding valid `tests/unit/**`, `tests/integration/**` and `tests/manual/**`
  files, the predicate's output carries no finding attributable to any of those files. Graded by
  T-01 case 1's exact-equality assertion: that fixture holds exactly one offending file,
  `.harness/tools/test_rogue.py`, and with `suite_layout.DOCUMENTED_EXCEPTIONS` temporarily rebound
  to `()` — so the unrelated FEAT-44 registry entry's `no longer tracked` finding cannot mask the
  result — `violations()` over it returns a list EQUAL to the single element
  `tracked test-shaped file outside tests/: .harness/tools/test_rogue.py`. What fails it: any
  second element at all, so a finding naming `tests/manual/probe-fixture.py`, either kind
  directory, or the copied `bin/` module reddens the assertion. A membership, containment or
  length-plus-membership test in its place does not grade this criterion and leaves it ungraded.
  The asserted manual shape is `probe-*.py` deliberately, and a later reader must not substitute
  another: the unchanged under-`tests/` clause rglobs `test-*.py`, `test_*.py` and `*_test.py` and
  refuses any match whose parent is not `tests/unit` or `tests/integration`
  (`suite_layout.py:20-28`), so `tests/manual/test-*.py` is refused today and is not a legal shape
  to plant.
  verify: automated        evidence: unit
- SC-07: No `active` entry in `.harness/harness.json` `test_kinds` matches `tests/manual`, so manual
  files stay outside active unit/integration discovery. Discharged by the pre-existing assertion
  `manual tests are not actively detected` at `tests/unit/test-suite-layout.py:104-105`; no task in
  this plan traces to it, and it must still pass at `review_sha`.
  verify: automated        evidence: unit
- SC-08: The real repository root produces no violations at the reviewed revision.
  verify: automated        evidence: unit
- SC-09: `.claude/skills/harness/bin/layout_fixtures.py` remains present and unmoved, so the
  legitimate `bin/` support module keeps working for the tests that import it. Discharged by the
  pre-existing `import layout_fixtures as lf` at `tests/integration/test-layout-migration.py:62`,
  which fails the integration suite if that module is moved or renamed; no task in this plan traces
  to it, and it must still pass at `review_sha`.
  verify: automated        evidence: integration
- SC-10: Every entry in the exception registry is an exact path with a written reason, and each of
  these is separately reported as a violation: an entry with a glob character, a duplicate entry, an
  entry no longer in the tracked set, and an entry the vocabulary would never have flagged. Removing
  the registry's single live entry makes the real root report that entry's own path.
  verify: automated        evidence: unit
- SC-11: Coverage distinguishes tracked from untracked: in a real Git fixture, a committed offending
  file is reported and an otherwise identical untracked file in the same location is not.
  verify: automated        evidence: unit
- SC-12: The audit at `review_sha` records the complete measured set of vocabulary matches outside
  `tests/**`, each with an explicit disposition, and reports no unexplained match. Graded by reading
  `git show <review_sha>:.harness/harness/features/BUG-1286-test-tree-enforcement/notes/qa-tree-audit.md`
  against a re-run of the audit at `review_sha`: the fenced row set must be identical, and the SHA
  the note records must be an ancestor of `review_sha` with no tracked vocabulary match added or
  removed between them.
  verify: inspection
- SC-13: `git show <review_sha>:.harness/harness/docs/DECISIONS.md` describes the repository-wide
  invariant in DEC-213 and marks the earlier bin-only enumeration as superseded rather than current,
  and `git show <review_sha>:.harness/harness/docs/DECISIONS-INDEX.md` is byte-identical to a fresh
  `gen-decisions-index.py --stdout` and its DEC-213 row states the repository-wide invariant.
  verify: inspection
- SC-14: `git diff` at `review_sha` changes no byte of `.harness/harness.json`.
  verify: inspection
- SC-15: The runtime mutation snapshot's scope is not widened: at `review_sha`,
  `.claude/skills/harness/bin/run-unit-tests.sh` still carries exactly one `run_pool.py` invocation
  (line 47 at HEAD `1977ebd6`) whose `--mutation-check` argument is `"$BIN_DIR"`, naming the bin
  directory alone and no broader tree.
  verify: inspection
- SC-16: A product checkout is reached by neither control: the predicate's repository-wide clause is
  inert on a root whose own index does not carry the predicate at that exact relative path, and
  `violations()` still has exactly one caller, Harness's own `run-unit-tests.sh` — the condition
  DEC-189 records, that a product repo under the fleet's `workspace_root` is worked on from a
  harness-rooted session where harness's hooks fire and never the product's, is what makes that
  single caller decisive.
  verify: automated        evidence: unit
- SC-17: A root with no Git index at all is neither a failure nor a silently scanned pass: the
  directory and bin clauses still report their violations, and the repository-wide clause contributes
  nothing.
  verify: automated        evidence: unit
- SC-18: The repository-wide vocabulary's two extension policies are each asserted, in opposite
  directions, by the same method. A tracked file outside `tests/**` whose basename matches
  `*_test.*` or `*.test.*` is refused at a non-source extension — T-01 case 10 tracks
  `.harness/tools/session_test.md` and `.harness/evidence/run.test.jsonl` and requires each to be
  named by its own `tracked test-shaped file outside tests/` finding. A tracked `probe-*` file
  outside `tests/**` at a non-source extension is not refused — T-01 case 8 requires
  `.harness/notes/probe-something.md` to produce no finding while `.harness/notes/probe-something.py`
  does. What fails it: either case absent, either direction asserted only as the other's negation,
  or a single case carrying both halves so that one passing masks the other.
  verify: automated        evidence: unit

### Traceability

Each criterion, the requirement it serves, and the issue #1286 acceptance criterion (AC-NN, in the
ticket's own order) it covers:

| SC | REQ | issue #1286 AC |
|---|---|---|
| SC-01 | REQ-01 | AC-01 tracked test-shaped file outside `tests/**` rejected |
| SC-02 | REQ-01 | AC-01 the covering assertion demonstrated failing first |
| SC-03 | REQ-02 | AC-02 all offending paths, deterministic order |
| SC-04 | REQ-01 | AC-03 runner exits misconfigured before any sentinel |
| SC-05 | REQ-03 | AC-04 enumeration failure is a closed failure |
| SC-06 | REQ-04 | AC-05 valid `tests/{unit,integration,manual}` files accepted |
| SC-07 | REQ-04 | AC-05 manual files outside active discovery |
| SC-08 | REQ-04 | AC-06 ordinary support modules remain accepted |
| SC-09 | REQ-04 | AC-06 the existing `bin/` support-module case |
| SC-10 | REQ-05 | AC-07 exact documented exceptions; stale, broadened, duplicated or unnecessary refused |
| SC-11 | REQ-01 | AC-08 coverage demonstrates the tracked-file distinction |
| SC-12 | REQ-06 | AC-09 audit re-run at `review_sha`, complete set, no unexplained match |
| SC-13 | REQ-07 | AC-10 DEC-213 and the index state the shipped invariant |
| SC-14 | REQ-08 | AC-11 `harness.json` unchanged |
| SC-15 | REQ-08 | AC-11 mutation-snapshot scope unchanged |
| SC-16 | REQ-08 | AC-11 product-checkout discovery unchanged |
| SC-17 | REQ-03, REQ-04 | AC-04 no-index root: not a failure, not a silent scan |
| SC-18 | REQ-01, REQ-04 | AC-01 rejected at any extension for the agnostic shapes; AC-06 legitimate non-test probe records remain accepted |

## Verification gaps

- `component`, `ui` and `typecheck` carry `cmd: null` in `.harness/harness.json`, and `functional`
  and `eval` are signed `excluded` (DEC-187). This change touches none of those surfaces: it is a
  Python predicate, a bash runner path, two Python test files and two Markdown records, all covered
  by the `unit` and `integration` runners. No SC here rests on a null kind.
- The one TypeScript file in play, FEAT-44's `probe-session-accessors.ts`, is classified data rather
  than changed code; with `typecheck` unrunnable it is not type-checked, and nothing in this feature
  executes it.
- `harness.json`'s `unit.detect` is extension-agnostic (`**/*.test.*`, `**/*_test.*`), and the
  repository-wide guard now mirrors it: `*_test.*` and `*.test.*` are refused whatever the
  extension (D-01). The class that was previously a disclosed residual — a tracked `*_test.md` or
  `*.test.jsonl` outside `tests/**`, discovered as a `unit` test by the kind map, permitted by the
  guard and executed by no runner — is therefore closed by the guard rather than disclosed, with
  `harness.json` still byte-unchanged (SC-14). No residual remains on this surface: `probe-*`,
  which keeps its source-extension restriction, is matched by no `detect` glob at all, and
  `test_*` is reached by `detect` only as `**/test_*.py`, which the source-extension form strictly
  contains.
- The widening was re-measured before it was written, not inferred: at `c040c319` with a clean
  worktree, `git ls-files` in the worktree root filtered by basename against the five shapes gives
  85 total matches, 9 outside `tests/**`, 0 violations — one FEAT-44 documented exception and eight
  `probe-*` Markdown/JSONL records. Zero tracked paths outside `tests/**` have a basename matching
  `*_test.*` or `*.test.*`, so the widening makes no tracked file a new violation and changes no
  existing row's disposition. The command and its output are recorded in
  `notes/research-BUG-1286-vocabulary-split.md`; the falsifiable criterion is SC-18, not this note.

## Approval

status: pending
approved-by:
date:
