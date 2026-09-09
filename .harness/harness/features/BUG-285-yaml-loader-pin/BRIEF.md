# BRIEF — BUG-285 yaml loader pin

## Problem

`load_recorded` in `.claude/skills/harness/bin/gh-sync.py:484` reads `feature.json` with
`json.loads(text)` at `:523`, and nothing in the suite pins that choice. Every fixture in the
T-06 Part C / fix1 Part B block of `tests/integration/test-gh-sync.py` (`:1415-1512`) is written
with `json.dump` or a JSON literal, and JSON is a YAML subset, so all of them load identically
under a YAML loader. The zero-byte fixture at `:1470-1480` cannot catch a swap either: `yaml.safe_load("")`
returns `None`, so the document falls past the parse guard and is refused by the second guard,
`if not isinstance(doc, dict)` at `:535`. One of the two guards is therefore pinned by a test and
the other is not, and the reader can silently regress to YAML — the parser whose silent-`None` on
an empty file was the original defect (`gh-sync.py:525-528`) — with the suite still green. This is
advisory rather than a live outage: the irreversible outcome stays closed by the `isinstance` guard.
What is open is the pin.

## Goal

The suite should notice if `feature.json`'s reader stops being a JSON parser. One fixture, in the
one file that already tests this reader, whose text a YAML loader accepts as a mapping and a JSON
parser rejects — and an assertion that the reader refuses it. Nothing in production changes; the
outcome is that a future loader swap turns the suite red instead of shipping quietly.

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

## Constraints

- **No production-code change is expected.** The reader already refuses such a document; the work is
  to pin that. If the new assertion is red against the real reader, that is a finding for the
  operator, not a licence to edit `gh-sync.py` under this bug.
- **One file, and it is the operator's explicit boundary:** `tests/integration/test-gh-sync.py`. No
  edit to `gh-sync.py`, no other test file, no other backlog item folded in.
- **`feature.json` must stay strict JSON.** The pin locks the reader to a JSON parser, so nothing may
  later introduce YAML-only syntax (comments, block mappings, unquoted scalars) into a real
  `feature.json` or into `feature_json_write`'s output.
- `.agents/skills` is a symlink to `.claude/skills` in this checkout: `gh-sync.py` is a single inode
  reached by both spellings. Any mutation probe must operate on a copy in a tempdir — an in-place
  edit of that file is a live-tree edit.
- **DEC-217 supplies, it does not block:** a bugfix confined to tests requires the `integration` kind,
  which is `active` with a real runner in `.harness/harness.json`. DEC-213 supplies the directory-selects-kind
  rule that makes `tests/integration/**` the `integration` kind. DEC-73 supplies the rule that each
  criterion below declares its method here rather than at ship time.

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

## Verification gaps

- SC-03 rests on a one-off mutation probe, not on a permanent test, and no `test_kinds` runner
  executes it. What is therefore NOT proven by any re-runnable gate is that the new assertion
  remains able to fail after a later edit; what carries it instead is the recorded transcript pair
  plus SC-01's two-directional fixture assertions, which redden if the discriminating property is
  edited away.

## Approval

status: approved
approved-by: mruangutai
date: 2026-09-09
