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
- REQ-09: The guard's refusal vocabulary is at least as wide as Harness's ACTUAL test-path
  discovery, and stays that way: every tracked path outside the test tree that
  `code_grade._is_test_path` counts — `fnmatch` over the FULL relative path, across every
  `.harness/harness.json` `test_kinds` entry whose `status` is `active` or `locally_run`, minus
  that kind's `exclude` — is refused by the guard and is not a permitted documented exception,
  and a later edit that widens `detect` past the guard fails loudly rather than reopening the gap
  in silence. The obligation is a SUPERSET of that matcher, not a mirror of the `unit` kind: the
  guard additionally carries the manual-probe source-name rule (`test-*`, `probe-*`) that no
  `detect` pattern expresses. Measured at `cab6adb2` against the real `.harness/harness.json` and
  the real Git index, the counted-outside-`tests/` set is EMPTY, so this requirement holds today
  and its assertion is a tripwire rather than a demonstration.

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
  `tests/**`, each with an explicit disposition, and reports no unexplained match, in a note whose
  row block is unambiguous. Graded by reading
  `git show <review_sha>:.harness/harness/features/BUG-1286-test-tree-enforcement/notes/qa-tree-audit.md`
  against a re-run of the audit at `review_sha`: the note must carry EXACTLY ONE fenced block, that
  block's row set must be identical to the re-run's, and the SHA the note records must be an
  ancestor of `review_sha` with no tracked vocabulary match added or removed between them. What
  fails it: a note carrying zero fenced blocks, or two or more. Those are two SEPARATE,
  SEPARATELY MESSAGED, SEPARATELY OBSERVABLE failures and neither message covers the other's
  case: a note with no fenced block is refused by name with `note carries no fenced block:
  <path>` and exit 2, and a note with two or more is refused by name with `note carries {n}
  fenced blocks, expected exactly 1: <path>` and exit 2. Either is a failure of this criterion,
  not merely of a command. Exit 2 is this instrument's own refusal status for those two
  conditions and is not a globally reserved code — `argparse` exits 2 on its own usage errors.
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
- SC-19: The guard-covers-discovery invariant is asserted against Harness's ACTUAL matcher, never
  argued from a snapshot and never read segment-wise. At test time the assertion reads
  `test_kinds` from `.harness/harness.json` and calls `code_grade._is_test_path` itself, so it
  exercises `fnmatch` over the full relative path — where a bare `*` crosses `/` — across every
  kind whose `status` is `active` or `locally_run`. Two halves, both required. BEHAVIOURAL: over
  a fixed synthetic tracked set AND over the repository's own tracked set, every path outside
  `tests/` that the matcher counts is judged test-shaped by the imported
  `suite_layout.is_test_shaped` and is not a `DOCUMENTED_EXCEPTIONS` entry; and a POSITIVE CONTROL
  proves the detector is not inert. The control's subject is DERIVED at test time by the live
  matcher from a fixed candidate corpus of literal paths written in the test — a candidate
  qualifies only if it sits outside `tests/`, is counted by `_is_test_path`, is NOT
  `is_test_shaped`, and is no `DOCUMENTED_EXCEPTIONS` entry — and the same helper must then report
  exactly that derived path, and only it, when it is added to the synthetic set. The corpus spans
  the pattern families in play (a `test_*` directory component such as
  `.harness/tools/test_dir/gen.py`, and the `*.test.*` / `*_test.*` directory-component shapes), so
  a legitimate NARROWING of `detect` re-selects a subject rather than reddening the case. If no
  candidate qualifies, the control records itself INAPPLICABLE with the reason through the file's
  existing reporting channel and does not fail. So the empty real set cannot leave this half
  unfalsifiable, and no property of today's `detect` value is pinned inside the assertion.
  HYGIENE: every `detect` pattern of every running kind is certified either inside-tests — by a
  NORMALIZED literal prefix, with any `..` component rejected outright — or guard-covered, where
  guard-covered means ALL FOUR of: the core, the pattern with a single leading `**/` removed,
  carries no `/`; the core is non-degenerate; the core carries FIXED wildcard-free literal text the
  vocabulary keys on, being either the extension-agnostic infix `_test.` or `.test.`, or one of the
  restricted prefixes `test-`, `test_`, `probe-` TOGETHER WITH a fixed wildcard-free source
  extension; and no basename of a fixed adversarial corpus — which must carry extension-poison
  entries such as `test_x.pw` and `a_test.pw` — is left matched-and-unrefused by the imported
  `is_test_shaped`. The two categories must PARTITION the pattern set, and a pattern certifying as
  NEITHER fails the case naming the pattern: FAIL-CLOSED BY DESIGN, as a general rule and never a
  list of banned shapes, so a `detect` shape nobody anticipated blocks until someone certifies it.
  Nothing is asserted about how many patterns land in either bucket, nor that either is occupied.
  The certification is a SUFFICIENT condition and is stated as one: the universal property — every
  path a pattern can match outside `tests/` is refused by the vocabulary — IS satisfiable by a
  `**/`-prefixed pattern (`**/*_test.py` satisfies it, its slash-free literal suffix surviving into
  every basename it can match), but it is not decidable by inspection for an arbitrary glob,
  whereas fixed slash-free literal text is — and that literal text is what closes the escape. The
  rule is sufficient over the leak axes ENUMERATED TO DATE, the directory-component axis and the
  extension-position axis, both found by picking an axis by hand; a third is not excluded
  (`## Verification gaps`). It therefore does not close the directory-component residual:
  `**/test_*.py` certifies guard-covered while counting `.harness/tools/test_dir/gen.py`, whose
  basename the vocabulary cannot refuse, and the BEHAVIOURAL half is what carries that residual
  over paths that actually exist. What fails it, all four verified on a prototype of the assertion
  against the real `.harness/harness.json` and none of them caught by the pre-existing
  template-equality assertion at `tests/unit/test-suite-layout.py:100-103` because both config
  files move together: substituting `tests/../evil/**` for `tests/unit/**` in
  `.harness/harness.json` and in `.claude/skills/harness/templates/harness.json`, which the `..`
  rejection refuses; introducing a wildcard in a NON-FINAL segment such as `**/test_*/**`, whose
  core spans a `/`; adding the extension-position core `**/test_*.p?`, which carries no fixed
  extension and counts `.harness/test_evil.pw` at an extension the vocabulary refuses nowhere; and
  a pattern of ANY shape that certifies as neither category, `**/*.spec.*` being the worked
  instance. Also fails it: an assertion that re-implements the vocabulary or the matcher instead of
  importing both, that carries a copy of today's `detect` value instead of reading it, that
  synthesises a representative path from a glob's final segment, that names the control's subject
  instead of selecting it with the live matcher, or that fails when no candidate qualifies instead
  of recording the control INAPPLICABLE.
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
| SC-19 | REQ-09 | AC-01 the refusal vocabulary stays at least as wide as actual matcher discovery |

## Verification gaps

- `component`, `ui` and `typecheck` carry `cmd: null` in `.harness/harness.json`, and `functional`
  and `eval` are signed `excluded` (DEC-187). This change touches none of those surfaces: it is a
  Python predicate, a bash runner path, two Python test files and two Markdown records, all covered
  by the `unit` and `integration` runners. No SC here rests on a null kind.
- Forward-looking consequence of that same null-kind set, and it is MEASURED rather than
  anticipated. `code_grade._is_test_path` unions every kind whose `status` is `active` or
  `locally_run`, so ACTIVATING any of those three kinds extends this feature's guard obligation to
  that kind's `detect` patterns and reddens T-01 case 11 as specified. Measured at `cab6adb2` by
  flipping `status` to `active` one kind at a time: `component` leaves 3 patterns uncertified
  (`**/*.spec.tsx`, `**/*.stories.tsx`, `**/*.stories.ts`); `ui` leaves 2 (`e2e/**`,
  `**/*.e2e.spec.ts`); `typecheck` leaves 2 (`**/*.ts`, `**/*.tsx`) and additionally turns two
  tracked paths into counted-but-unrefused offenders — FEAT-44's documented exception
  `probe-session-accessors.ts`, which stops being permitted and becomes counted, and
  `.omp/extensions/harness-hooks.ts`. The consequence at signature: the DEC-163 dev-ops work that
  would give `ui` or `typecheck` a runner is blocked until either `suite_layout.py`'s vocabulary
  widens or DEC-213 records the scope. This feature deliberately does NOT widen the vocabulary for
  those kinds — issue #1286's scope is the kinds that RUN — so the disclosure is the deliverable
  and the cost lands on whoever activates a kind. T-01 case 11's remedy text names kind activation
  so the red reads as a remedy, and T-05 records the mechanism in DEC-213.
- The one TypeScript file in play, FEAT-44's `probe-session-accessors.ts`, is classified data rather
  than changed code; with `typecheck` unrunnable it is not type-checked, and nothing in this feature
  executes it.
- `harness.json`'s `unit.detect` is extension-agnostic (`**/*.test.*`, `**/*_test.*`), and the
  repository-wide guard covers those two shapes at any extension (D-01). The class that was
  previously a disclosed residual — a tracked `*_test.md` or `*.test.jsonl` outside `tests/**`,
  counted by the kind map, permitted by an extension-restricted guard and executed by no runner —
  is therefore closed by the guard rather than disclosed, with `harness.json` still byte-unchanged
  (SC-14). The closure argument is the MATCHER CONTRACT, not a snapshot of today's `detect` value:
  `code_grade._is_test_path` (`code_grade.py:458-473`) `fnmatch`es the FULL relative path across
  every kind whose `status` is `active` or `locally_run`, so the guard's obligation is a superset
  of that matcher's reach outside `tests/**`, plus the manual-probe source-name rule no `detect`
  pattern expresses. T-01 case 11 asserts exactly that by calling the matcher, never by reading a
  glob segment by segment.
- One residual is DISCLOSED rather than closed, and it is the reason the guard is stated as a
  superset obligation instead of a mirror. Because a bare `*` crosses `/` under `fnmatch`,
  `**/test_*.py` also counts a path such as `.harness/tools/test_dir/gen.py`, whose basename no
  basename vocabulary can refuse — the pattern matched a DIRECTORY component. Measured at
  `cab6adb2` no such tracked path exists, so REQ-09 holds today; T-01 case 11's behavioural half
  reddens the unit suite on the commit that adds one, and the remedy is then to move the file, to
  widen the vocabulary, or to record the exception. The falsifiable criterion is SC-19.
- The hygiene half of T-01 case 11 is a SUFFICIENT rule, not a proof, and the operator signs against
  that limit explicitly. It closes the leak axes ENUMERATED TO DATE — the non-final-segment form of
  the directory-component axis, by requiring the core to carry no `/`, which refuses a wildcard in
  any NON-FINAL segment while the directory-component residual above stays with the behavioural
  half; and the extension-position axis, by requiring FIXED wildcard-free literal text the
  vocabulary keys on, which is what refuses `**/test_*.p?` (core `test_*.p?`, no fixed extension,
  counting `.harness/test_evil.pw` at an extension the vocabulary
  refuses nowhere). BOTH axes were found by picking an axis by hand; nobody enumerated the axis
  space, so a THIRD axis is not excluded and no claim of exhaustive proof over future glob shapes
  is made here. Two things bound that residual and neither is a proof either: a pattern certifying
  as neither category FAILS the case by name, so an unrecognised glob shape is refused rather than
  waved through; and the behavioural half carries the residual over paths that actually exist,
  reddening the unit suite on the commit that adds one. The falsifiable criterion is SC-19.
- The vocabulary widening was re-measured before it was written, not inferred: at `c040c319` with
  a clean worktree, `git ls-files` in the worktree root filtered by basename against the five
  shapes gives 85 total matches, 9 outside `tests/**`, 0 violations — one FEAT-44 documented
  exception and eight `probe-*` Markdown/JSONL records. Zero tracked paths outside `tests/**` have
  a basename matching `*_test.*` or `*.test.*`, so the widening makes no tracked file a new
  violation and changes no existing row's disposition. The command and its output are recorded in
  `notes/research-BUG-1286-vocabulary-split.md`. This census is evidence for SC-12 and SC-18 and
  carries no part of REQ-09's closure argument, which rests on the matcher contract above.

## Approval

status: approved
approved-by: mruangutai
date: 2026-09-05
