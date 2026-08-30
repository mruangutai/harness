# SIMPLIFY — SIMPLIFICATION angle — harness-backend-dev

**BLUF:** Two real dead-code residuals from T-06/T-10's amendment/supersession removal,
both in `gen-decisions-index.py`, neither named by SC-06's seven-symbol list. The lead's
third candidate (`had_ok_stale`) is confirmed unused but rejected as a finding — it
predates this feature and its retention is explained by a protected incident comment.
No comment-narration or stale-docstring findings; the two docstrings that reference
FEAT-38/T-06/T-10 by name (test file, lines ~552, ~830) justify present test behavior
rather than merely narrating history, so they stay. `run-unit-tests.sh`,
`.harness/harness.json`, `board_lifecycle.py`, `check-domain.sh` diffs are single-line,
mechanical (one array entry removed, DEC-186→DEC-203 renumber) — no dead code found there.

## Lead's three pre-read candidates — verdicts

**1. `had_ok_stale` (strip_trailing_clauses' 2nd return, `gen-decisions-index.py:156-168`,
bound at `:200`/`:202`) — CONFIRMED unused, REJECTED as a finding.**
Evidence: every reader enumerated — `:181` already discards it (`prose, _ = ...`); `:200`
binds it but no line after `:200` in `build_index` reads the name `had_ok_stale`; grep
across `.claude/skills/harness/bin/` for `strip_trailing_clauses` found no importer besides
`gen-decisions-index.py` itself, and `test-gen-decisions-index.py` never calls it directly
(only `gdi.ROW_RE` and `gdi.DECISIONS_PATH` are pulled from the module). Verified this is
**pre-existing**, not left behind by this feature: `git show 7ebfc9eb:…/gen-decisions-index.py`
already had the identical dead binding before T-06/T-10 touched the file. Rejected because
(a) it isn't fallout of this feature's removals, and (b) the comment at `:204-209`
explaining the non-re-emission is named in this dispatch's own contract as a protected
incident record — the binding is the trace that comment's reasoning refers to. No net
benefit to renaming it `_`.

**2. `lines`, `parse_decisions`' 2nd return element (`gen-decisions-index.py:109-131`) —
CONFIRMED, real finding (see F1 below).** Before this feature, `lines` fed
`compute_amendments(lines, headings)`; T-10 deleted that call. `build_index:172` now
discards it (`decisions, _, headings = parse_decisions(text)`). Grep across `bin/` found
no other caller of `parse_decisions`.

**3. `"title"` dict key on each decision (`gen-decisions-index.py:128`) — CONFIRMED, real
finding (see F2 below).** Before this feature it was the sole input to
`compute_supersession_target(dec["title"])`, deleted by T-10. Grep for `["title"]` /
`.title` reads of the `decisions` dict across `gen-decisions-index.py` and
`test-gen-decisions-index.py` found zero — the only other `title` hits in the test file are
an unrelated local parameter name on `make_authority(tmp, decisions, bodies)`'s docstring.

## Findings

- **F1** — `gen-decisions-index.py:109-131` (`parse_decisions`) — `high`→no, `med`:
  the function still builds and returns `lines` (from `defenced_lines`) as its 2nd tuple
  element, but the only caller (`build_index:172`) discards it. **Cost:** the 3-tuple
  signature and docstring imply three meaningful outputs; a future maintainer wiring new
  logic into this parser may go hunting for an existing `lines`-consumer that no longer
  exists, or thread a new feature through the wrong return slot assuming it's already
  live. **Alternative:** narrow `parse_decisions` to return `(decisions, headings)`,
  update the one call site (`decisions, headings = parse_decisions(text)`), and update the
  docstring at `:110` (which states the return shape) to match.

- **F2** — `gen-decisions-index.py:125-130` (`parse_decisions`, dict construction) — `med`:
  each decision dict still carries `"title": lines[idx][1]`, unread anywhere since T-10
  deleted `compute_supersession_target`. **Cost:** the per-decision dict is wider than
  what's used, and the field name `title` signals load-bearing state (it was, until this
  feature) — a future reader may trust it as the source of truth for a decision's heading
  text rather than re-deriving it, when nothing currently keeps it in sync with anything.
  **Alternative:** drop the `"title": lines[idx][1],` line from the dict literal, and
  update the docstring at `:110` (`{"num": int, "line": int, "body": str}`, currently
  stale — it already omits `title` even though the code still sets it) to match the
  trimmed shape.

- No F3 — `had_ok_stale` confirmed unused but explicitly rejected, see verdict 1 above.

## What was checked and cleared

- `run-unit-tests.sh`, `.harness/harness.json`, `board_lifecycle.py`, `check-domain.sh`:
  diffed against `7ebfc9eb..8a7c75c`; every hunk is a single-line mechanical change (one
  `INTEGRATION_SCRIPTS`/`detect` array entry removed for T-24/T-25; three DEC-186→DEC-203
  renumbers in comments/docstrings following the amendment-removal renumbering). No dead
  code, no stale contract claims.
- Load-bearing incident comments explicitly protected by this dispatch — `MalformedRow`
  repair path (`:280-294`), `parse_argv` refusal (`:241-260`), ok-stale non-re-emission
  (`:204-209`) — read in full; all three still describe true present behavior. Not touched,
  not flagged, per contract.
- `check-decision-claims.py`/`test-check-decision-claims.py` sweep: grepped the whole
  worktree for `check-decision-claims`/`check_decision_claims` outside `notes/`/`runs/` —
  zero hits. Consistent with T-24's own receipt; nothing left behind for this angle to find.
- Test file docstrings naming `FEAT-38`/`T-06`/`T-10` by id (`test_refs_graph_omits_ids_with_no_live_heading`
  at `:551-560`, `test_no_amendment_construct_survives_in_the_authority` at `:829-833`) —
  read in full. Both justify present test behavior (a specific standing defect closed, a
  guard moved from generator to authority because the generator has nothing left to
  police) rather than narrating history for its own sake. Not flagged.

## Not evaluated (other angles)

REUSE, EFFICIENCY, ALTITUDE are out of scope for this dispatch.
