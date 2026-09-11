# BRIEF — BUG-285 yaml loader pin

## Problem

**The defect is TWO READERS DISAGREEING, not one reader being wrong.** Two tools read
`feature.json` — `gh-sync.py`'s `load_recorded` and `factory_decompose.py`'s `load_factory` — and
they do not accept and refuse the same documents. Measured in this worktree at `6cb113f4` over
**13 input classes fed as identical bytes to both readers: 4 give a caller the same answer and 9
differ**, and **6 of the 9 carry the FEAT-14 incident class** — a `feature.json` that is PRESENT
and MALFORMED read as "nothing is mirrored", indistinguishable from the legitimate absent-file
empty record. The table, per class and per reader, is
`notes/research-BUG-285-parity-survey.md`; its dispositions are under **Risk** below. Either
reader read alone looks defensible; the harm is that one tool records what the other refuses to
read. The original scope saw only half of it.

**`gh-sync.py` — a JSON parse, unpinned, and carrying two defects of its own.** `load_recorded`
(`.claude/skills/harness/bin/gh-sync.py:527`) parses with `json.loads(text)` at `:566`, and has done
since FEAT-14 landed at `1c5fd67`. Nothing in the suite pins that choice. Every fixture in the T-06
Part C / fix1 Part B block of `tests/integration/test-gh-sync-open.py` (`:350-474`) is written with
`json.dump` or a JSON literal, and JSON is a YAML subset, so all of them load identically under a
YAML loader. The zero-byte fixture at `:426-442` cannot catch a swap either: `yaml.safe_load("")`
returns `None`, so the document falls past the parse guard and is refused by the second guard,
`if not isinstance(doc, dict)` at `:578`. One of the two guards is pinned by a test and the other is
not. **Beyond the missing pin, two real defects, verified at source at `6cb113f4`:**

- The read at `:559-560` is guarded by `except OSError` at `:561` alone, and a decode failure is not
  an `OSError`. A `feature.json` whose bytes are not valid UTF-8 therefore escapes as a
  **traceback** where every other malformed input produces a refusal. Measured:
  `UnicodeDecodeError: 'utf-8' codec can't decode byte 0xff in position 0`, uncaught, no
  `SystemExit`.
- The parse guard at `:567` is `except (ValueError, UnicodeDecodeError)`, but `text` is already a
  `str` and `json.loads` on a `str` can never raise `UnicodeDecodeError` (it raises
  `JSONDecodeError`). That member is **dead** — it reads as coverage of exactly the input the read
  guard lets escape, and it is not.

**An earlier draft of this section called that reader "correct, unpinned" and called the work there
a regression pin that "fixes nothing". That is withdrawn as false** (amended 2026-09-11): the reader
is not already correct, and the work there fixes a live escape and deletes a guard that cannot fire.

**`factory_decompose.py` — still defective.** `load_factory`
(`.claude/skills/harness/bin/factory_decompose.py:111`) does `doc = harness_yaml.load_file(path)` at
`:121` on `feature.json`. That is a YAML loader on a JSON file, and it is the actual defect this bug
names. The surrounding shape is load-bearing and exists because of issue #208: the `try` is at
`:120`, the `except harness_yaml.YamlParseError as e:` at `:122`, and
`factory_cli.refuse(TOOL, "feature.json invalid", path, f"does not load: {e}")` at `:123`. The
history comment recording why sits at `:116-119`. Before #208 a malformed `feature.json` raised past
`factory_cli.run`'s `expected=` tuple and printed a class name instead of naming the file; `refuse()`
exits via `SystemExit`, which `factory_cli.run()` propagates unchanged rather than re-wrapping as
"unexpected failure".

**The two loaders genuinely disagree, in both directions** (measured in this worktree, 2026-09-11):

- YAML accepts / JSON rejects: `#` comments, single-quoted strings, unquoted scalars, block mappings.
- JSON accepts / YAML rejects: a **duplicate key**. `json.loads('{"a":1,"a":2}')` returns `{'a': 2}`
  (last wins); `harness_yaml.load_str` on the same text raises `DuplicateKeyError`.

So `load_factory` today both accepts documents no JSON reader would and refuses documents every JSON
writer may legally produce.

## Goal

Both readers of `feature.json` parse it as JSON, both choices are pinned by a test that reddens if
the parser is swapped back, and — the point of the feature — the two readers **refuse the same
inputs the same observable way**, pinned by a comparison on one shared input set rather than by two
independent per-reader assertions. `factory_decompose.py`'s reader is changed to JSON;
`gh-sync.py`'s reader is pinned AND its own two defects are fixed (the escaping decode failure and
the dead `except` member). Issue #208's refusal behaviour — the refusal names the file and exits via
`SystemExit` — survives the change exactly.

## Requirements

- REQ-01: Replacing `feature.json`'s parser with a YAML loader makes
  `tests/integration/test-gh-sync-open.py` fail.
- REQ-02: The fixture that carries REQ-01 cannot silently stop discriminating: the suite itself
  asserts, in both directions, that the fixture text is accepted by a YAML loader as a mapping and
  rejected by a JSON parser.
- REQ-03: The refusal is asserted on the reader's own message, so an unrelated `SystemExit` cannot
  satisfy the assertion.
- REQ-04: Everything the suite already proves keeps passing, and no pre-existing check is deleted or
  retargeted to carry the new one.
- REQ-05: `load_factory` reads `feature.json` with a JSON parser, not a YAML loader.
- REQ-06: Issue #208's refusal behaviour is preserved exactly: a `feature.json` that does not parse
  is refused by a message that **names the file**, exits via `SystemExit` so `factory_cli.run()`
  propagates it unwrapped, and never prints an exception class name or "unexpected failure".
- REQ-07: `load_factory`'s choice of parser is pinned: a document a YAML loader accepts as a mapping
  and a JSON parser rejects is refused, and the discriminating property is asserted in both
  directions so the fixture cannot rot.
- REQ-08: No pre-existing check in `tests/integration/test-factory-decompose.py` is deleted or
  retargeted — in particular case `(1c)` at `:426-437`, which is the standing #208 regression, stays
  green unchanged.
- REQ-09: A `feature.json` whose bytes are not valid UTF-8 is **refused** by `load_recorded` — by a
  message that names the file, raised as `SystemExit` — never raised as a traceback.
- REQ-10: `load_recorded` carries no exception handler that cannot fire.
- REQ-11: On one shared set of `feature.json` inputs, both readers agree on whether the document is
  accepted or refused, and every refusal names the file and leaks no exception class name.
- REQ-12: A `feature.json` that is PRESENT but does not parse to a usable record is **refused** by
  `load_factory`, while an absent `feature.json` — and a present mapping whose `factory` block is
  absent — still returns the empty record. Absence and corruption are distinguishable to the
  caller.

## Constraints

- **`gh-sync.py` IS edited, and only inside `load_recorded`** — amended 2026-09-11. The earlier
  constraint said it was not edited, on the premise that its reader was already correct; the Problem
  section above records why that premise is false, and T-04 now edits it, so an unamended constraint
  would forbid the plan's own task. Two edits only: the read guard at `:561` gains
  `UnicodeDecodeError`, and the dead `UnicodeDecodeError` member is deleted from the parse guard at
  `:567` with `ValueError` **retained** (`json.JSONDecodeError` subclasses it, and it is what
  refuses a zero-byte file). Its refusal wording, its `isinstance` guard at `:578`, and every other
  function in the module stay untouched — **including `_opt_int` at `:512-524`, which is edited in
  NEITHER direction** (added 2026-09-11, D-16). The coercion alignment travels the other way:
  `load_factory` reimplements `_opt_int`'s four lines as a helper nested inside itself.
- **`factory_decompose.py` is edited, and only inside `load_factory`.** The `factory_cli.refuse(...)`
  call and its wording are preserved; the history comment at `:116-119` is **updated** to record the
  JSON reader, never deleted — it is why the refusal is shaped the way it is.
- **`feature.json` must stay strict JSON.** The pin locks both readers to a JSON parser, so nothing
  may later introduce YAML-only syntax into a real `feature.json` or into `feature_json_write`'s
  output. Symmetrically, nothing may emit a duplicate key, which JSON accepts silently.
- `.agents/skills` is a symlink to `.claude/skills` in this checkout: each reader is a single inode
  reached by both spellings. Any mutation probe must operate on a COPY in a tempdir — an in-place
  edit of either file is a live-tree edit.
- A test file name may not appear in both `tests/unit/` and `tests/integration/`
  (`suite_layout.py:_unit_integration_findings`), so the new unit test cannot be called
  `test-factory-decompose.py`; that name is taken by the integration suite.
- **DEC-217 supplies, it does not block**, but it now resolves differently — see the amended D-03.
  DEC-213 supplies the directory-selects-kind rule. DEC-35 supplies the rule that the diff itself
  must carry the test exercising the change. DEC-73 supplies the rule that each criterion declares
  its method here rather than at ship time.

## Risk — the measured table, every DIFFERENT row accounted for

**The table itself is `notes/research-BUG-285-parity-survey.md`** — 13 input classes fed as
identical bytes to both readers in this worktree at `6cb113f4`, 4 SAME and 9 DIFFERENT, 6 of the 9
carrying the FEAT-14 incident class. It is not reproduced here. What is here is the disposition of
every DIFFERENT row: **all nine closed** (amended 2026-09-11 — the superseded framing is kept
below rather than deleted).

**Closed by this plan — all nine:**

- an empty file, a YAML-only block mapping, and a duplicate block key: closed by T-02's swap to a
  JSON parse, which makes all three SAME — `json.loads("")` raises, a block mapping raises, and a
  duplicate key is accepted last-wins on both sides. Pinned by SC-07 and SC-14.
- non-UTF-8 bytes, where `load_recorded` raised an **uncaught `UnicodeDecodeError`**: closed by
  T-04 under REQ-09, pinned by SC-12 and SC-13.
- a document parsing to a top-level list, to a scalar string, to a scalar int, and a document whose
  own `factory` key is present and is **not** a mapping: closed by T-02 under REQ-12 and D-14,
  which turn all four into refusals while the `factory` key being ABSENT keeps returning the empty
  record. Pinned by SC-06, SC-14 and SC-16.
- a block mapping carrying **wrong-typed members** — `parent` recorded as the string `"7"`: closed
  by T-02 under D-16, **by ALIGNING `load_factory` onto `_opt_int`'s TOLERANCE, never by making it
  refuse.** `load_factory` reimplements `_opt_int`'s four lines as a nested helper — it cannot
  import them, `gh-sync.py` is hyphen-named — so a quoted `"7"` reads as `7` on both sides and a
  bool reads as no value on both sides. **The incident this disposition defends:** `_opt_int`'s own
  docstring (`gh-sync.py:515-518`) records that the coercion "tolerates the quoted form the old
  `(\d+)` regex silently read as ABSENT — and 'absent' here meant `gh-sync` believed nothing was
  recorded and would create a duplicate parent or milestone." So reading a legacy-quoted
  `"parent": "7"` as ABSENT is that duplicate-parent/milestone incident reopened, and refusing such
  a member would have looked like tightening while doing exactly that. Unlike the five fail-open
  rows above, where the empty read came from a MISSING guard, here it would come from a STRICTER
  one. Pinned by SC-14's value-parity checks, which feed the SAME bytes to BOTH readers and assert
  the VALUES read are EQUAL — the behavioural drift detector that makes a deliberate duplicate
  acceptable where a comment alone would not.

**SUPERSEDED 2026-09-11, kept as the record rather than deleted** (rule 15). This section
previously said "eight closed, one known-open" and carried a **KNOWN-OPEN** block for the
wrong-typed-members row: it recorded `load_recorded` returning a populated record via `_opt_int`
(`gh-sync.py:512-524`) against `load_factory` returning the empty record because it admitted only
real ints (`factory_decompose.py:134-135`), called the row newly measured and present in no other
REQ, SC or decision, and declined to close it on the reasoning that the `load_factory` side meant
"choosing between refusing and silently dropping a wrongly-typed member … one nobody has ruled
on". **Why that no longer holds:** the operator ruled the row in on 2026-09-11 and ruled the
DIRECTION with it — adopt the tolerance. The old reasoning framed the choice as refuse-or-drop and
missed the third option, which is the correct one. Its `gh-sync`-side half still stands and is
exactly why the alignment travels the other way: `_opt_int` sits OUTSIDE `load_recorded`, so this
brief's Constraints forbid editing it.

**Three DELIBERATE contract differences remain — differences by choice, not residual defects**
(D-06, D-14, D-16). Each is stated with its reason rather than as an exception to a convergence
claim, and they are the only three:

- **(i) NEITHER reader detects a duplicate key any more.** `load_factory`'s `DuplicateKeyError`
  refusal is given up by the parser swap — `json.loads` takes the last key silently. There is **no
  measured incident** behind that refusal, and the compensating rule is this brief's own Constraint
  that nothing may emit a duplicate key. Pinned as an ACCEPT row on BOTH sides by SC-14, so a later
  reader cannot reintroduce the refusal on one side alone.
- **(ii) BOTH readers refuse a YAML-only document.** Deliberate, and the point of the feature rather
  than a residual: `feature.json` stays strict JSON (Constraints).
- **(iii) The `issues` mapping's KEY ADMISSION still differs, and this feature does NOT close it.**
  Measured 2026-09-11 at `6cb113f4`: `load_recorded` admits only keys matching `T-\d+` and strips
  them (`gh-sync.py:613`), while `load_factory` admits any key verbatim
  (`factory_decompose.py:139-141`), so `{"issues": {"X-1": 5}}` reads as `{}` on one side and
  `{"X-1": 5}` on the other. That is a key-admission POLICY, not a coercion; no incident is measured
  behind it; and — unlike the coercion — **nothing forbids closing it**: `:613` is inside
  `load_recorded` and the `issues` loop is inside `load_factory`, so both are reachable. It is left
  open because it is neither the empty-record fail-open this bug removes nor the parser choice it
  names, and which admission policy is right is a ruling nobody has made. **It is an open question
  for you, not a criterion here** — and SC-14's quoted-int row deliberately uses the key `T-01`,
  admitted identically by both readers, so the value-parity check is isolated from this difference.

**Nothing on disk is affected by any of it.** Measured 2026-09-11: **79 `feature.json` files** under
`.harness/*/features/*/` at the owner root parse identically under `json.loads` and
`harness_yaml.load_str`, **zero disagreements**. Re-measured today with the same glob: the owner
root still holds 79 and this worktree holds **80** — an earlier draft recorded 77 here, which the
worktree's feature set has since outgrown; the cross-loader result is unchanged. And all 80 in this
worktree have the `factory` key **absent**, with zero non-mapping documents and zero non-mapping
`factory` values, so the new refusals change the behaviour of no file that exists today — and, for
the same reason, no live file carries a wrong-typed member for the coercion alignment to read
differently either. Three consequences to weigh at signature:

- **Nothing observable regresses.** The swap closes a LATENT divergence: the value is that a future
  `feature.json` carrying a duplicate key stops being silently refused, one carrying a comment
  stops being silently accepted, and one truncated mid-write stops reading as "nothing recorded".
- **The absent-record path is what the new refusals put most at risk**, precisely because all 80
  live files sit on it. That is why T-02's guard is a SPLIT — `"factory" not in doc` returns the
  empty record, a present non-mapping value refuses — and why SC-16 exists.
- **A corpus-wide scan cannot serve as the able-to-fail proof**, because it is uniformly clean. The
  proof has to be a constructed fixture plus a mutation probe (SC-09).

## Success Criteria

- SC-01: A fixture in `tests/integration/test-gh-sync-open.py` carries feature.json text that a YAML
  loader parses to a mapping and `json.loads` rejects, and the suite asserts BOTH halves as named
  checks of their own — so a later edit that makes the text plain JSON, or makes it a non-mapping,
  reddens the suite instead of degrading the case into a meaningless "malformed input is rejected".
  verify: automated        evidence: integration
- SC-02: `load_recorded` refuses that fixture with a `SystemExit` whose message contains both the
  `feature.json` path and the `does not parse` wording, asserted on the message text — an unrelated
  `SystemExit` does not satisfy the check.
  verify: automated        evidence: integration
- SC-03: The new assertion is shown able to fail: red against a mutant COPY of `gh-sync.py` whose
  `json.loads(text)` parse call is replaced by `harness_yaml.load_str(text, path)`, green against
  the real reader, with both transcripts recorded under this feature's `notes/`. The grader reads
  that note at the pinned sha (`git show <review_sha>:<note path>`) and confirms it shows the mutant
  accepting the fixture and the real reader refusing it.
  verify: inspection
- SC-04: `env -u HARNESS_AGENT_TYPE python3 tests/integration/test-gh-sync-open.py` exits 0, prints
  zero lines beginning `FAIL` and at least 79 lines beginning `ok`; and
  `env -u HARNESS_AGENT_TYPE python3 tests/integration/test-gh-sync-record.py` exits 0, prints zero
  lines beginning `FAIL` and at least 56 lines beginning `ok`. Pre-change baselines measured in this
  worktree at sha `6cb113f4`, BRIEF pending: `-open` exit 0, 79 `ok`, 0 `FAIL`, 10.6s; `-record`
  exit 0, 56 `ok`, 0 `FAIL`, 8.8s. These two are the gh-sync pole files that exercise
  `load_recorded` and the only two with a measured baseline — commit `efcebe2d` split the gh-sync
  integration monolith into five poles plus `gh_sync_support.py` (issue #1527), so the old single
  command and its 318-`ok` baseline no longer exist. The `FAIL`-line count is
  asserted directly and not inferred from the exit code, which is sound here because each pole
  prints zero lines beginning `FAIL` on a green run — unlike the unit runner, see SC-10.
  verify: automated        evidence: integration
- SC-05: No pre-existing check is deleted or retargeted:
  `git diff <merge-base>..<review_sha> -- tests/integration/test-gh-sync-open.py` shows no removed
  line containing `check(` and no removed fixture, and every added line falls either in the region
  between the `T-06C: a feature.json with no github: block returns the default, does not raise`
  check and the `---------- fix1 Part B: three states must stay distinct` comment (`:399`–`:401`
  before the change), or is the single `import harness_yaml` line added to that file's own import
  block, which the new fixture's YAML-side assertion requires and which `test-gh-sync-open.py` did
  not previously carry.
  verify: inspection
- SC-06: At the pinned sha,
  `git show <review_sha>:.claude/skills/harness/bin/factory_decompose.py` shows `load_factory`
  reading `feature.json` through an explicit read plus a JSON parse, and shows its failure handling
  covering ALL THREE of a JSON parse failure, an undecodable-bytes failure and a read failure.
  **The criterion is the coverage, not the spelling:** the decided form is
  `except (json.JSONDecodeError, UnicodeDecodeError, OSError)`, and any form that demonstrably
  covers the same three (a common `ValueError` ancestor plus `OSError`, or separate arms) satisfies
  it, while a handler that omits the decode failure fails it — `UnicodeDecodeError` is a
  `ValueError` but is neither a `json.JSONDecodeError` nor an `OSError`, so the two-name pair does
  not reach it. **It also shows the two NEW refusals, and the absent path they must not touch:** a
  document that does not parse to a mapping reaches a `factory_cli.refuse` call rather than a
  `return`; the `factory` value is read only after an explicit `"factory" not in doc` membership
  test whose branch RETURNS the empty record; and a `factory` value that is present and not a
  mapping reaches a `factory_cli.refuse` call. An implementation that adds the JSON parse but
  leaves either guard returning the empty record FAILS this criterion, and so does one that
  collapses the membership test into the refusal. No `harness_yaml.load_file` CALL survives inside
  `load_factory`; all three refusals still go through
  `factory_cli.refuse(TOOL, "feature.json invalid", path, ...)` with the tool, the what and the
  path argument intact, and none of them puts an exception class name in the next-step clause; and
  the history comment still stands, now recording the JSON reader, which failures the handler
  covers, and why absent and present-but-unusable differ.
  It ALSO shows the coercion alignment, and WHERE it sits. The integer-valued members — `parent`,
  and the values of the `issues` mapping — are read through a coercion that accepts a real `int`,
  accepts a digit string after `strip()`, **excludes `bool`**, and yields no value otherwise,
  matching `gh-sync.py`'s `_opt_int` (`:512-524`) BY VALUE, defined inside `load_factory` rather
  than at module level, and carrying a comment that names it as a deliberate duplicate and names
  the test that detects drift. That coercion sits BELOW both refusals: a mapping document whose
  `factory` value is a mapping reaches the member reads, and a member the coercion cannot read
  yields NO VALUE rather than a refusal, leaving `_empty_factory()`'s default in place. An
  implementation that hoists any refusal above the member reads, or that turns a coercion miss into
  a refusal, FAILS this criterion — it would contradict SC-16 and D-16's tolerance at once. An
  implementation that omits the `bool` exclusion also fails it (`bool` is an `int` subclass, so
  `parent: true` would become `1` on one side only).
  verify: inspection
- SC-07: A unit test under `tests/unit/` asserts all three of: `harness_yaml` parses the fixture text
  to a mapping; `json.loads` raises `ValueError` on the same text; and `load_factory` on a directory
  holding that text raises `SystemExit` whose refusal output names the `feature.json` path. The first
  two are separate named checks, so a later edit that turns the fixture into plain JSON reddens the
  suite instead of degrading the case.
  verify: automated        evidence: unit
- SC-08: Case `(1c)` of `tests/integration/test-factory-decompose.py` (`:426-437`) still passes
  unchanged after the swap — exit 2, the `feature.json` path on stderr, and neither
  `"unexpected failure"` nor a class name in the output. Its fixture text
  (`{ not: valid json [[[`) is rejected by both loaders, so it is the direct #208 regression anchor.
  verify: automated        evidence: integration
- SC-09: The new unit assertion is shown able to fail: red against a mutant COPY of
  `factory_decompose.py` in a tempdir whose JSON parse is restored to
  `harness_yaml.load_file(path)`, green against the real reader, with both transcripts recorded
  under this feature's `notes/` and graded at the pinned sha
  (`git show <review_sha>:<note path>`). The COPY is mandatory: `.agents/skills` is a symlink to
  `.claude/skills`, so an in-place probe edit is a live-tree edit of production code.
  verify: inspection
- SC-10: `env -u HARNESS_AGENT_TYPE .agents/skills/harness/bin/run-unit-tests.sh --kind unit` exits
  0. The unit suite is graded on **EXIT STATUS ONLY**, and that status is captured into a shell
  variable on the command's own line rather than read from `$?` after a pipe — `$?` after a pipe
  reports the pipe's last stage, which has already produced one wrong measurement on this feature.
  **The `FAIL`-line count is deliberately NOT the measure here and must not be restored as one:**
  at baseline, measured in this worktree at `6cb113f4` on a GREEN run (exit 0, 36 files, 2.4s), the
  suite prints FOUR lines beginning `FAIL ` because one unit test reddens its own cases on purpose
  to prove its mutant is live (the block printing `MUTANT ACTIVE` and
  `MUTATION PROOF: 3/3 cases reddened`). A criterion asserting zero `FAIL` lines from this runner
  is therefore false at baseline and would fail a correct build.
  verify: automated        evidence: unit
- SC-11: A unit check under `tests/unit/` feeds `load_factory` a `feature.json` whose BYTES ARE NOT
  VALID UTF-8 (written in binary mode, beginning `\xff\xfe`) and asserts the OBSERVABLE refusal
  **across TWO named checks, matching T-03's intent check 4**: the first asserts, joined with
  `and`, that a `SystemExit` is raised, that its code equals `factory_cli.EXIT_REFUSED`, and that
  the captured stderr contains the `feature.json` path; the second asserts that the captured
  stderr contains neither `unexpected failure` nor the string `UnicodeDecodeError`. No exception
  class name is asserted. **The two-check split is the letter of this criterion:** an earlier draft
  said "in one check", which no builder could satisfy against T-03's two, so the criterion is bent
  to the task rather than the task to the criterion. This is the one input the pre-amendment catch
  set dropped, so its value is as a standing guard against that set being narrowed again: it is
  green under the old YAML reader and under the amended handler, and red against any handler that
  omits the decode failure. **It lands in `tests/unit/test-factory-decompose-loader.py`, the file
  T-03 creates, so T-03's existing `verify:` already runs it** — both of its commands (the unit
  file directly, and `run-unit-tests.sh --kind unit`) execute it with no command change.
  verify: automated        evidence: unit
- SC-12: In `tests/unit/test-feature-json-readers.py`, the `non-UTF-8 bytes` input
  (`bytes([0xff, 0xfe]) + b"trash"`, written in binary mode) run through `load_recorded` yields the
  verdict `refuse` — not `escape:<class>` and not `accept` — and its observable output contains the
  `feature.json` path and contains none of `unexpected failure`, `Traceback`, `UnicodeDecodeError`,
  `JSONDecodeError`, `YamlParseError` or `OSError`. Measured at `6cb113f4`, BRIEF pending: that same
  input raises `UnicodeDecodeError` uncaught out of `load_recorded`, so the check is red on the
  pre-change tree.
  verify: automated        evidence: unit
- SC-13: At the pinned sha, `git show <review_sha>:.claude/skills/harness/bin/gh-sync.py` shows
  `load_recorded`'s READ guard covering both a read failure and a decode failure, and shows its
  PARSE guard naming `ValueError` with **no `UnicodeDecodeError` member**. **The criterion is the
  coverage, not the spelling:** the decided form is `except (OSError, UnicodeDecodeError)` on the
  read and `except ValueError` on the parse, and any form demonstrably covering the same set
  satisfies it — while a read guard that omits the decode failure fails it, a parse guard that
  retains `UnicodeDecodeError` fails it (`json.loads` on a `str` cannot raise it, so the member
  cannot fire), and a parse guard narrowed off `ValueError` fails it (`json.JSONDecodeError`
  subclasses `ValueError`, and that arm is what refuses a zero-byte file). Both refusal messages at
  `:562-564` and `:572-574` and the `isinstance` guard at `:578` are unchanged.
  verify: inspection
- SC-14: `tests/unit/test-feature-json-readers.py` runs BOTH readers over ONE shared
  **TWELVE-input** set that SPANS the measured table in BOTH REFUSAL DIRECTIONS and in the VALUE
  direction — valid JSON mapping, absent file, own block key absent, empty file, malformed JSON
  text, YAML-only block mapping, non-UTF-8 bytes, a document that parses to a non-mapping, own
  block key present and not a mapping, a duplicate block key, a block carrying quoted-int members
  (`parent` as `"7"` and `issues` as `{"T-01": "12"}`), and a block carrying a bool-valued `parent`
  — and asserts, as named checks: each reader's verdict per input equals the expected
  `accept`/`refuse`; the two readers' verdicts are equal to each other per input; every refusal's
  observable output names the `feature.json` path and contains no `unexpected failure`, no
  `Traceback` and no exception class name; for the absent file and the absent block key, that each
  reader returns its own EMPTY default record rather than merely not refusing; and — **the VALUE
  PARITY, three checks** — that the two readers read EQUAL values out of the two accepting value
  rows AND that those values are the expected ones, namely `parent == 7` and
  `issues == {"T-01": 12}` on the quoted-int input and `parent is None` on the bool input, so two
  readers agreeing on a WRONG value cannot pass. **All three directions are required:** the two
  non-mapping inputs are cases where `load_recorded` refused and `load_factory` did not; the
  duplicate-key input is the one case where `load_factory` refused and `load_recorded` did not; and
  the quoted-int input is the case where BOTH ACCEPTED and read a DIFFERENT VALUE, which the verdict
  checks alone would report as a parity that does not exist. Per D-11, exit-code and message-text
  equality between the readers are **not** asserted. **NOTHING is excluded from the set** — amended
  2026-09-11 (D-16): the ten-input framing and the clause "Per D-14 exactly ONE measured input is
  excluded, because it still diverges after this feature" are withdrawn as false, the
  wrong-typed-members row being now closed by alignment. What the file carries in ONE comment
  instead of asserting is the three DELIBERATE contract differences under **Risk** — no
  duplicate-key detection on either side, both refusing YAML, and the `issues` key-admission
  difference — citing D-16, D-14 and the superseded D-08 as the record of what earlier drafts
  excluded. The valid mapping, the absent file and the absent block key are positive controls, so a
  reader that refused everything fails; the bool row is a control, green before and after, whose job
  is to redden if either copy of the coercion drops the `bool` exclusion. Measured pre-change
  baseline at `6cb113f4`, BRIEF pending: **SEVEN of these twelve inputs disagree — six on the
  verdict and one on the value read** (D-09), so this file is red on the pre-change tree without any
  mutant being constructed.
  verify: automated        evidence: unit
- SC-15: At the pinned sha, `git show <review_sha>:.claude/skills/harness/bin/gh-sync.py` shows
  `load_recorded`'s docstring asserting **no convergence claim in any spelling** — not "converged",
  not "converged except for", not "the one input that still diverges" — and carrying instead an
  ENUMERATION, in TWO parts, of what was measured in `notes/research-BUG-285-parity-survey.md`,
  citing that note and claiming no completeness beyond it.
  **Part one — the input classes both readers now treat IDENTICALLY:** that both do an explicit
  UTF-8 read then a `json` parse; that both load the record for a valid JSON mapping; that both
  return the empty or all-None default for an absent file and for a mapping whose own block key is
  absent, deliberately, because a feature that has never synced has no record; that both refuse — by
  `SystemExit` whose observable output names the file — an empty file, malformed JSON text, a
  YAML-only block mapping, non-UTF-8 bytes, a document that parses to a non-mapping, and a document
  whose own block key is present and is not a mapping; that both accept a duplicate key, last one
  wins; and that both read the same VALUE out of an integer-valued member, a quoted `"7"` reading as
  `7` and a bool reading as no value on both sides.
  **Part two — the classes they deliberately do NOT treat identically, each with its reason**, never
  as an exception to a convergence claim: that NEITHER reader detects a duplicate key any more, the
  refusal having been given up by the parser swap with no measured incident behind it and the
  compensating rule living in this brief's Constraints; that BOTH refuse a YAML-only document,
  which is the point of the feature because `feature.json` stays strict JSON; and that the `issues`
  mapping's KEY ADMISSION still differs — this reader admits only keys matching `T-\d+` and strips
  them while `load_factory` admits any key verbatim — a policy difference this feature does not
  close. It names `tests/unit/test-feature-json-readers.py` as what holds the enumerated classes.
  **A docstring that claims convergence fails this criterion even if its exception list is
  correct**, and so does one that omits a deliberate difference, or asserts the enumeration is
  exhaustive, or drops the citation. On the `factory_decompose.py` side the text names the function
  and the guard in words, never a line number, because T-02 edits that function in this same
  feature. Measured at `6cb113f4`, BRIEF pending: the docstring's standing sentence that the reader
  is "converged with factory_decompose.py's reader" (`gh-sync.py:528-529`) is false — nine of
  thirteen measured input classes disagree. **Amended 2026-09-11 (D-16):** an earlier draft of this
  criterion required the docstring to state "that ONE class is **not** identical — a block mapping
  carrying wrong-typed members". That is now false, no measured divergence surviving the feature, so
  it is withdrawn and replaced by the two-part enumeration above; the enumeration must not be
  reduced back to an exception clause.
  verify: inspection
- SC-16: The ABSENT path is provably unchanged. `tests/unit/test-factory-decompose-loader.py`
  carries two named checks — an empty directory, and a present mapping whose `factory` key is
  absent — each asserting that `load_factory` RETURNS a record EQUAL to `_empty_factory()`, with no
  `SystemExit` raised, and both are executed by that file's own run and by
  `run-unit-tests.sh --kind unit`. Both are green before and after the change by design; their job
  is to redden if a later edit moves a refusal above the `os.path.exists` early return, or collapses
  the `"factory" not in doc` membership test into the refusal beside it. A red here is a broken
  ruling, not a broken test. The source-level half — that the early return and the membership test
  are both still there at the pinned sha — is graded by SC-06, so this criterion stays on the one
  method that can falsify it behaviourally.
  verify: automated        evidence: unit

## Verification gaps

- The mutation probes behind SC-03 and SC-09 each rest on a one-off run, not on a permanent test,
  and no `test_kinds` runner executes either. What is therefore NOT proven by any re-runnable gate
  is that the two new assertions remain able to fail after a later edit; what carries it instead is
  the recorded transcript pair for each, plus the two-directional fixture assertions in SC-01 and
  SC-07, which redden if the discriminating property is edited away.
- No runner covers the `feature.json` corpus itself. The 79-file cross-loader scan under
  **Risk** above is a one-off measurement recorded in `notes/research-BUG-285-amend-c0.md`, not a
  standing gate, so a `feature.json` introduced later that the two loaders disagree about would not
  be caught by anything in the suite.
- SC-14's parity check is a STANDING gate — `run-unit-tests.sh --kind unit` runs it on every pass —
  but its **able-to-fail** evidence is not: it is the pre-change disagreement measured once at
  `6cb113f4`, seven of the twelve inputs (six on the verdict, one on the value read), recorded in
  `notes/research-BUG-285-parity-survey.md` (the 13-class table) and
  `notes/research-BUG-285-foldq7.md` (the earlier seven-input run). What is therefore NOT proven by
  a re-runnable gate is that the parity checks would still redden after a later edit that weakened
  them; what carries it instead is that the set includes six accept rows — three of them positive
  controls — and six refuse rows, spanning all three divergence directions, so a degenerate reader
  fails in one of them. No third mutation probe was commissioned for it, by decision (D-09).
- The `issues` **key-admission** difference — difference (iii) under **Risk** — is covered by no
  criterion here: it is neither the empty-record fail-open this bug removes nor the parser choice it
  names, and **it is left open by choice rather than by a constraint** — both sites are reachable
  inside the two functions this feature may edit. What is therefore NOT proven
  is that the two readers admit the same `issues` KEYS; what carries it instead is the measured
  statement under **Risk** and in D-06, the one comment T-05 writes into the parity file, and
  SC-14's deliberate choice of the key `T-01` — admitted identically by both readers — which keeps
  the value-parity check from being confounded by it. It needs an operator ruling and a separate
  ticket, not a criterion this feature cannot meet.

## Approval

status: pending
approved-by:
date:
