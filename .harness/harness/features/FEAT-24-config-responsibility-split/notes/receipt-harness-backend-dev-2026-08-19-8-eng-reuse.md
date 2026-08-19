# REUSE angle — FEAT-24, run 2026-08-19-8-eng

HEAD confirmed `3396b5e` (matches dispatch). Scope note: `git diff --stat ada8e99..3396b5e`
shows 64 files / +7473/-482 (feature-wide, includes plan.yaml, notes, observations, docs).
Restricted to the code surface named in the dispatch (`bin/factory_gh.py`, `factory_config.py`,
`gh_board.py`, `gh-sync.py`, `board-station.py`, `factory_decompose.py` + their test files,
`harness.json`, `fleet.yaml`) the diff is 13 files / +1070/-333 — neither figure matches the
dispatch's stated "19 files, +1394/-437". Reported as a scope-figure mismatch, not blocking:
I derived and used the named-surface file list per the dispatch's own instruction to derive it
myself.

## Finding 1 (highest priority — the fake-gh hypothesis, CONFIRMED)

**File/line:** `.claude/skills/harness/bin/test-factory-integration.py:275-284` vs.
`.claude/skills/harness/bin/test-factory-gh.py:38-52` (`recorder`).

**Summary:** Two independent fake-`gh` implementations exist in the tree and both model the new
`contents` (file_at_ref) endpoint, but neither asserts HTTP method, and the integration fake's
regex `^repos/([^/]+/[^/]+)/contents/(.+)$` absorbs the `?ref=...` query string into `group(2)`
and never checks it against the ref the test staged the fixture under — `state["product_configs"]`
is keyed only by repo name, not by `(repo, ref)`, so a caller bug that requests the wrong ref
would still be served the right document.

**Cost:** `test-factory-gh.py`'s `recorder` is order-based (a queue of canned `Result`s, blind to
argv content) and separately guards `-f not in argv` at the one call site that matters
(`test-factory-gh.py:918`) — that specific defect class (`gh api -f` forcing a POST) is covered
there. But `test-factory-integration.py`'s state-machine fake is the one exercising
`product_config`'s real call path end-to-end, and it has no equivalent method/ref guard. A future
change that adds a write to the same contents endpoint (GitHub's contents API supports `PUT`) and
reuses this URL shape, or a bug that requests the wrong branch, both pass this suite silently —
exactly the shape that let `-f`-forces-POST and the line-wrap defect ship past a green suite
before. This is a live gap, not a hypothetical: I read `test-factory-integration.py:270-284` and
confirmed the ref is discarded (`cm.group(2)` is never compared to anything) and no branch here
checks `-X` for the contents endpoint.

**Alternative:** Key `state["product_configs"]` by `(repo, ref)` and assert equality against the
requested ref before serving; add a `"-X" not in rest` (or explicit "no method flag") assertion
to the same conditional the `git/refs` POST case already uses as a precedent one function above
it, so the two write-vs-read cases in one fake are held to the same standard.

## Finding 2

**File/line:** `.claude/skills/harness/bin/gh_board.py:41-81` (`load_board`) vs.
`.claude/skills/harness/bin/factory_config.py:238-274` (`product_config`).

**Summary:** Not a duplication — flagging only because it looks like one at first read.
`load_board` opens `.harness/harness.json` locally via `open()`/`json.load` (the repo's own
checkout, used by `board-station.py`/`gh-sync.py` running *inside* that repo); `product_config`
reads the SAME relative path but always remotely via `factory_gh.file_at_ref`, for the factory
reading a fleet member it does not have checked out. Confirmed these are genuinely different
call sites with different constraints (settled by D-03, not re-litigated here) — no finding.

## Everything else checked, no finding

- `validate_board` (`factory_config.py:79`) is confirmed the sole board-shape validator —
  grepped `station_field|_validate_board|validate_board` tree-wide; `gh_board.load_board`
  delegates to it entirely (line 81); `factory_decompose.py`'s `_validate_stations` checks a
  *different* thing (the board's live GitHub field options, not local shape) and is not a second
  spelling of the same rule.
- `file_at_ref` (`factory_gh.py:428`) has exactly one caller (`factory_config.product_config`) —
  no duplicate remote-read primitive found elsewhere in `bin/`.
- The memo/clear pattern (`_product_config_memo` / `clear_product_config_memo`) has no prior art
  in the tree to have reused — it is the first per-process memo of this shape in `bin/`.

## Suite measurement

Ran: `test-factory-gh.py` (165/165 ok), `test-factory-config.py` (79/79 ok), `test-gh-board.py`
(all pass, no FAIL lines) — each run standalone via `python3 <file>`. Also ran the full
`bash .claude/skills/harness/bin/run-unit-tests.sh --kind all`: rc=0, zero `FAIL` lines
(includes `test-factory-integration.py`, 106/106 checks passed).

```yaml
VERDICT: PASS
DIGEST:
  headline: "REUSE pass on FEAT-24 code surface — one confirmed finding: two fake-gh doubles model the new contents/file_at_ref call and neither asserts HTTP method or ref fidelity"
  tests_added: 0
  suite: pass
  task: none
  blocked_on: none
  open_questions: []
  files_touched: []
  expertise_update: []
artifact: .harness/harness/features/FEAT-24-config-responsibility-split/notes/receipt-harness-backend-dev-2026-08-19-8-eng-reuse.md
```
