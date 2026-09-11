# BRIEF — BUG-285 yaml loader pin

## Problem

Two tools read `feature.json`. One reads it correctly and is unpinned; the other still reads a JSON
file with a YAML loader. The original scope saw only the first.

**`gh-sync.py` — correct, unpinned.** `load_recorded` (`.claude/skills/harness/bin/gh-sync.py:484`)
parses with `json.loads(text)` at `:523`, and has done since FEAT-14 landed at `1c5fd67`. Nothing in
the suite pins that choice. Every fixture in the T-06 Part C / fix1 Part B block of
`tests/integration/test-gh-sync.py` (`:1415-1512`) is written with `json.dump` or a JSON literal, and
JSON is a YAML subset, so all of them load identically under a YAML loader. The zero-byte fixture at
`:1470-1480` cannot catch a swap either: `yaml.safe_load("")` returns `None`, so the document falls
past the parse guard and is refused by the second guard, `if not isinstance(doc, dict)` at `:535`.
One of the two guards is pinned by a test and the other is not. The work here is a **regression pin
over already-correct code** — worth having, but it fixes nothing.

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

Both readers of `feature.json` parse it as JSON, and both choices are pinned by a test that reddens
if the parser is swapped back. `gh-sync.py`'s reader is pinned as-is; `factory_decompose.py`'s reader
is changed to JSON and then pinned. Issue #208's refusal behaviour — the refusal names the file and
exits via `SystemExit` — survives the change exactly.

## Requirements

- REQ-01: Replacing `feature.json`'s parser with a YAML loader makes `tests/integration/test-gh-sync.py`
  fail.
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

## Constraints

- **`gh-sync.py` is not edited.** Its reader is already correct; the work there is the pin. If the
  new assertion is red against the real reader, that is a finding for the operator, not a licence to
  edit `gh-sync.py`.
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

## Risk — the swap closes a latent divergence, not a live one

**This is the one fact that could make the change bigger than it looks, and it cuts in our favour.**
Measured 2026-09-11: **79 `feature.json` files** under `.harness/` at the owner root (77 inside this
worktree — the two trees carry different feature sets) were parsed under BOTH `json.loads` and
`harness_yaml.load_str`. **Zero disagreements**, in either tree.

So swapping `load_factory`'s loader changes the behaviour of **no file that exists today**. It closes
a LATENT divergence, not a live one. Two consequences an operator should weigh at signature:

- **Nothing observable regresses**, and nothing observable improves either. The value is that a
  future `feature.json` carrying a duplicate key stops being silently refused, and one carrying a
  comment stops being silently accepted.
- **A corpus-wide scan cannot serve as the able-to-fail proof**, because it is uniformly clean. The
  proof has to be a constructed fixture plus a mutation probe (SC-09).

## Success Criteria

- SC-01: A fixture in `tests/integration/test-gh-sync.py` carries feature.json text that a YAML
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
- SC-04: `env -u HARNESS_AGENT_TYPE python3 tests/integration/test-gh-sync.py` exits 0, prints zero
  lines beginning `FAIL`, and prints at least 318 lines beginning `ok` (pre-change baseline measured
  in this worktree at sha `7e0c2ec148c05786d2cbbc1bf1f352c3e0403738`, BRIEF pending: exit 0, 318
  `ok`, 0 `FAIL`, 36.9s). The `FAIL`-line count is asserted directly and not inferred from the exit
  code.
  verify: automated        evidence: integration
- SC-05: No pre-existing check is deleted or retargeted:
  `git diff <merge-base>..<review_sha> -- tests/integration/test-gh-sync.py` shows no removed line
  containing `check(` and no removed fixture, and every added line falls in the region between the
  T-06 Part C cases and the fix1 Part B block.
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
  not reach it. No `harness_yaml.load_file` CALL survives inside `load_factory`, the
  `factory_cli.refuse(TOOL, "feature.json invalid", path, ...)` call is still present with its
  wording intact, and the history comment still stands, now recording the JSON reader and which
  failures the handler covers.
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
- SC-10: `env -u HARNESS_AGENT_TYPE .agents/skills/harness/bin/run-unit-tests.sh --kind unit` exits 0
  and prints zero lines beginning `FAIL`. The `FAIL`-line count is asserted directly and not inferred
  from the exit code, because a runner that counts a failure only when a detail string is non-empty
  can exit 0 while printing `FAIL` lines.
  verify: automated        evidence: unit
- SC-11: A unit check under `tests/unit/` feeds `load_factory` a `feature.json` whose BYTES ARE NOT
  VALID UTF-8 (written in binary mode, beginning `\xff\xfe`) and asserts the OBSERVABLE refusal, in
  one check: a `SystemExit` is raised, its code equals `factory_cli.EXIT_REFUSED`, and the captured
  stderr contains the `feature.json` path and contains neither `unexpected failure` nor the string
  `UnicodeDecodeError`. No exception class name is asserted. This is the one input the
  pre-amendment catch set dropped, so its value is as a standing guard against that set being
  narrowed again: it is green under the old YAML reader and under the amended handler, and red
  against any handler that omits the decode failure. **It lands as a fourth named check in
  `tests/unit/test-factory-decompose-loader.py`, the file T-03 creates, so T-03's existing
  `verify:` already runs it** — both of its commands (the unit file directly, and
  `run-unit-tests.sh --kind unit`) execute it with no command change.
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

## Approval

status: pending
approved-by:
date:
