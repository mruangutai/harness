# receipt — harness-data-engineer — 2026-08-19-8-eng — angle: ALTITUDE

HEAD confirmed `3396b5e` (matches dispatch). Diff `ada8e99..3396b5e`, 19 files, matches
`git diff --stat` dispatch summary exactly. `validate-digest.py dev` run against this DIGEST
block before returning: `digest ok`, rc=0.

## Findings (3, ranked)

### F1 — an absent `github` block silently resolves to "no board", the exact default D-07 exists
to remove, and no fixture drives this cell
- **File/line**: `.claude/skills/harness/bin/gh_board.py:69-71`.
- **Measured, not read off the diff**: built a temp `harness.json` with `{"sync": true, "repo":
  "o/r"}` — no `github` key at all — and called `gh_board.load_board(root)` directly. Returns
  `None`. Both live callers (`gh-sync.py:139`'s `g = cfg.get("github") or {}`, then
  `g.get("sync")`; `board-station.py:120`'s `isinstance(github, dict)` check) treat `None` the
  same as an explicit `github.board: null` — exit 0 / skip station writes, no error.
- **Contradicts**: `plan.yaml:759` ("github block absent, or board key ABSENT: raise"),
  `load_board`'s own docstring ("the `github` block absent" is among the shapes that "RAISE"),
  D-07 ("A board key that is absent … is an error"). The neighbouring cell — `board` key absent
  from a present `github` dict — DOES raise and IS tested (`test-gh-board.py`'s "no board key"
  case, `test-board-station.py:173`); only the `github`-block-absent cell falls through to
  `return None` two lines above it.
- **Cost**: a `harness.json` with a typo'd or missing `github` key (e.g. `githb`, or the block
  simply never added) is indistinguishable from a project that explicitly declared no board —
  the exact "absent is indistinguishable from a typo" silence D-07 was written to kill, now
  re-opened for one specific cell of the same check the rest of this feature closed everywhere
  else. No test in `test-gh-board.py` constructs a `github`-key-absent fixture, so nothing would
  catch a regression here.
- **Discriminator, not mine to resolve**: whether this is a one-line code fix (raise instead of
  `return None` at `gh_board.py:70`, matching the `board`-key-absent cell three lines below) or a
  docstring/plan correction depends on whether T-04's "github block absent → raise" is still
  intended now that both live callers pre-filter that case themselves before calling
  `load_board` — a scope call, not an implementation detail.
- **briefing-row**

### F2 — the fake `gh` still models argv text only, never the HTTP verb or a shaped response;
this diff's fix is a proxy assertion over that same blind spot, not a deeper seam
- **File/line**: `.claude/skills/harness/bin/test-factory-gh.py:35-47` (`Result`/`recorder`,
  seam shape unchanged) and the new `file_at_ref` cases at ~903-996.
- **Summary**: both live defects named in the dispatch are addressed — the base64 case by a
  genuine new fixture (`_wrap_body`, GitHub's real 60-char line-wrapped shape), the POST case by
  `"-f" not in calls[0]["argv"]`. Real assertions, but the fake enforces nothing about HTTP
  semantics — `recorder`'s `Result` is a canned `(returncode, stdout, stderr)` triple. It cannot
  fail a future call that forces a write via `--method POST`, `-F`, `--input`, or any argv shape
  other than the one string this diff learned to check for.
- **Cost**: the next divergence in this family — a write where a read was intended, a response
  shape `gh` returns for real that a hand-built `Result.stdout` never reproduces — is invisible
  again until production, exactly as these two were.
- **Concrete alternative**: move the constraint into the fake. `recorder`'s `fake_run` can refuse
  to serve a canned response when `argv` contains `-f`/`-F`/`--method`/`--input` for a
  `contents`-path GET call — one guard instead of a per-test assertion a future author must
  remember to write. A single shared `contents_response(bytes)` fixture builder that always
  emits GitHub's real 60-char-wrapped, trailing-newline form closes the same gap for shape
  (`_wrap_body` today is a one-off local to this file). Both are real work, so `briefing-row`
  still holds — but names something actionable.
- **briefing-row**

### F3 — `"github.board"` is spelled as a literal in two modules, not carried by one constant
- **File/line**: `.claude/skills/harness/bin/factory_config.py:309` (`board_for`, `where =
  "github.board"`) and `.claude/skills/harness/bin/gh_board.py:76,81`.
- **Summary**: `validate_board` is correctly the single validator (D-05) — no second copy of the
  field rules. The key path both entry points pass it is typed independently in each file.
- **Cost**: if the board key ever moves again, both spellings must be found and changed in
  lockstep; nothing asserts the two literals stay equal.
- **Verified safe**: `grep -rn "github\.board" .claude/skills/harness/bin/test-*.py` — every hit
  asserts on a runtime message/stdout string or passes the literal as an argument; no test greps
  `gh_board.py`/`factory_config.py` source. `gh_board.py` is separately clean of T-04's
  `Building|Review|Backlog|Ready|Done|Plan` whole-file grep (checked directly). A `BOARD_KEY =
  "github.board"` constant in `factory_config.py`, imported by `gh_board.py`, preserves the
  runtime string and trips no verify clause.
- **fold-in**

## Not flagged, considered and cleared
- `validate_board`'s interface vs implementation: simple interface, real work inside — correctly
  deep, not a finding.
- `board_for`'s "explicit null is an error" vs `gh_board.load_board`'s "explicit null is OK":
  D-07's own distinction (fleet-member board required; product's own local board optional) —
  settled.
- Test seams: `test-factory-config.py` patches `factory_gh.file_at_ref` (the real network
  boundary) for `board_for`/`product_config` — crosses the seam. `test-factory-decompose.py`
  stubs `factory_config.product_config` directly, appropriate since it isn't testing remote-read
  correctness.

## Suite
`bash .claude/skills/harness/bin/run-unit-tests.sh --kind all` — rc=0, zero `FAIL` lines, ended
`106/106 checks passed. PASS test-factory-integration.py`. Ran the three named directly too:
`test-factory-config.py` (79/79), `test-gh-board.py` (all pass), `test-factory-decompose.py`
(181/181). All green.

```yaml
VERDICT: PASS
DIGEST:
  headline: "altitude, FEAT-24 diff ada8e99..3396b5e: 3 findings, all briefing-row/fold-in, none blocking — F1 (measured): github-block-absent silently returns None from gh_board.load_board, contradicting plan/docstring/D-07's 'raise', untested; F2: gh fake models argv text only, not HTTP verb/shape, with a concrete alternative; F3: github.board literal duplicated in 2 files, safe to constant-fold per grep"
  tests_added: 0
  suite: pass
  task: none
  blocked_on: none
  open_questions: []
  files_touched: []
  expertise_update: []
artifact: .harness/harness/features/FEAT-24-config-responsibility-split/notes/receipt-harness-data-engineer-2026-08-19-8-eng-alt.md
```
