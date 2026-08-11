# Code review — harness-code-reviewer — FEAT-11-graphql-field-resolve — c0

**VERDICT: PASS.** No must_fix. Two info-level notes, neither blocking.

## Diff scope (real, from git)

`git diff --stat 8dedeae..2ea9af3`:

```
 .claude/skills/harness/bin/factory_gh.py                                        | 134 ++++++++---
 .claude/skills/harness/bin/test-factory-gh.py                                   | 245 +++++++++++++++++----
 .claude/skills/harness/bin/test-factory-integration.py                          |  26 ++-
 .../FEAT-11-graphql-field-resolve/DESIGN.md                                     |   4 +-
 .../FEAT-11-graphql-field-resolve/STATE.md                                      |  53 ++---
 .../FEAT-11-graphql-field-resolve/feature.yaml                                  | 187 +++++++++++-----
 .../FEAT-11-graphql-field-resolve/notes/qa-c0.md                                | 212 ++++++++++++++++++
 .../notes/receipt-harness-backend-dev-MF-1-c1.md                                | 132 +++++++++++
 .../notes/receipt-harness-backend-dev-T-01-c0.md                                | 236 ++++++++++++++++++++
 .../observations/harness-visual-designer.md                                     |   6 +
 10 files changed, 1056 insertions(+), 179 deletions(-)
```

**`DESIGN.md` IS in the range.** Its two hunks both just remove `<!-- ok-stale -->` HTML comment
markers (the already-ruled `ok_stale_receipt_markers` residual, item #4 in the dispatch) — no
substantive content change. No other doc/bookkeeping file carries anything beyond the expected
build record.

Two commits in range, both machine-authored: `5c433f2` (T-01) and `2ea9af3` (MF-1 fix). `git log
--grep='harness:human' -i` over the range returns nothing — no hand edits, nothing inherits-no-review
here.

**One non-blocking cross-reference note for whoever reads `feature.yaml` next:** at the pinned SHA
it still reads `review_sha: PENDING_MF1_COMMIT` — anyone scoping from that file alone, rather than
from the dispatch, finds no SHA recorded. Not this diff's defect; flagging so it doesn't surprise the
next reader.

## Stage 1 — spec compliance

Walked REQ-01..05, SC-02..12, D-01..04 against the diff and the plan's `intent:` block.

- **D-01** (one resolver): `_project_field_resolve` is the single call site; both
  `project_field_options` and `project_field_set` call it, no duplicated query/branch logic.
  `factory_gh.py:222-284` (post-diff).
- **D-02** (four-state discrimination via `repositoryOwner`): confirmed — null owner, non-User
  typename, null projectV2, null-or-empty field, each its own `GhError`. No `user(login:)` anywhere
  (`grep` clean).
- **D-03** (one diagnosis walk, entered from both paths): confirmed — `except GhError` parses
  `e.stdout`, and on a dict carrying `data` falls through into the *same* walk the success path
  uses; otherwise re-raises with a real value, never the generic fallback. Matches the signed
  decision text verbatim.
- **D-04** (frozen strings byte-identical): both frozen `next_step` strings present unchanged —
  `factory_gh.py:279` (`field-list for {owner} project {number} does not offer it`) and `:330`
  (`field {field} on {owner} project {number} does not offer it`).
- **SC-02/SC-03**: `grep -n '"field-list"\|"project", "view"'` over `factory_gh.py` and
  `test-factory-integration.py` — zero hits. `_FIELD_QUERY` exists at module level, single named
  `field(name:...)` selection, no `fields(`, no `first:`/`last:`. Bare token `field-list` survives
  at exactly 2 sites (both inside the frozen D-04 strings) — matches the plan's own predicted count.
- **SC-04, SC-06, SC-11, SC-12**: each has its own fixture and its own `check(...)` naming
  assertion; SC-12 specifically uses the empty-dict fixture and asserts it produces the *same*
  message as field-absent (`not field_obj:` catches both `None` and `{}` — confirmed at
  `factory_gh.py:277`).
- **SC-05**: both org fixtures present (`GRAPHQL_ORG_UNREACHABLE_JSON` exit 1,
  `GRAPHQL_ORG_OK_JSON` exit 0 — the derived, disclosed-unmeasured one), looped over the same
  assertion block (`test-factory-gh.py:420-441`).
- **SC-07**: every failing-path test block asserts zero `item-edit` calls; confirmed present in all
  six new/rewritten failure cases.
- **SC-08**: `test-factory-decompose.py` / `test-factory-claim.py` / `test-factory-land.py` are
  **absent from the diff's file list** (verified via `git diff --stat` above) and the task verify's
  three sha256 pins are asserted in the receipt as matching — signature/return-shape freeze holds.
- **SC-09**: both `["project", "field-list"]` and `["project", "view"]` handlers deleted from
  `test-factory-integration.py`, replaced by one `["api", "graphql"]` handler placed *before* the
  generic `argv[0] == "api"` REST block (confirmed by reading the file at the pinned SHA,
  `:177-196`) — the ordering the intent required, not accidental REST-regex non-collision.
- **SC-10**: bare owner/board/field assertions present throughout; negative clause (`"api graphql"
  not in str(exc)`) asserted on every failure path including the transport-failure case. The MF-1
  commit (`2ea9af3`) is scoped exactly to the four sites the receipt claims — confirmed via `git
  diff 5c433f2..2ea9af3` — three `"owner"` → `"acmeuser"` value-slot fixes plus their dependent
  assertions, nothing else touched (`factory_gh.py` untouched between the two commits, confirmed by
  its absence from that diff).
- Ran `python3 .claude/skills/harness/bin/test-factory-gh.py` directly: **118/118 PASS**, exit 0.

No scope creep found — every changed line traces to REQ-01..05 or D-01..04. No omission found.

## Stage 2 — the two adversarial asks

### (A) `projectV2.id` absent

`factory_gh.py:281`: `"project_id": project["id"],` — **subscript**, not `.get`. `project` is
non-`None` at this point (the `if project is None:` branch above already returned/raised), but if it
were an empty dict or missing `"id"`, this line raises a bare `KeyError` inside the return-dict
construction — before `item-edit` is reachable. Same failure class as the measured `field_obj["id"]`
KeyError qa already found for the sibling key: **safe crash, no write, not a `GhError`** (so the
operator sees a traceback, not a clean message — a pre-existing pattern, not new).

**On qa's fragment-boundary argument (`notes/qa-c0.md:141-151`):** it does not transfer as written.
That argument is scoped to `id`/`name`/`options`, which sit *inside* `... on
ProjectV2SingleSelectField` — an inline fragment that "resolves as a unit." `projectV2.id` is a
**direct selection on the `ProjectV2` object type**, one level up, outside any type-conditional
fragment; there is no "fragment resolves as a unit" mechanism to invoke here.

A *different* argument would cover the same ground: if `ProjectV2.id` is `ID!` in GitHub's schema (a
node-id field, conventionally non-nullable), a resolver error there null-propagates to `projectV2`
itself, which the code already handles via the existing `project is None` branch — making "projectV2
non-null but missing `id`" unreachable from a conformant server. **That argument is recorded
nowhere** — not in `qa-c0.md`, not in `DESIGN.md` (including the `:80-84` reasoning SC-05 cites) —
and it rests on a schema-nullability fact this review cannot verify without a live call, which is
out of bounds here. Call it an **unverified schema assumption**, not an established unreachability
argument.

**Severity: info.** The code fails safe either way (crash before write); the gap is that the
reachability argument covering it is unwritten, not that behavior is wrong. Not blocking.

### (B) New assertions — discriminating or merely green?

- **D-04 freeze assertions** (`test-factory-gh.py:332` in `project_field_set`'s option-not-offered
  block, `:622` in `project_field_options`' absent-field block): both assert the **rendered**
  string (`"field Station on owner project 3 does not offer it"`,
  `"field-list for owner project 3 does not offer it"`) — confirmed no `{field}`/`{owner}`/`{number}`
  braces present. **Reachability: both are top-level `check(...)` calls, not inside any
  `if raised:`/`if set_exc is None:` conditional** — the condition is `raised and "..." in
  str(exc)`, so a non-raise makes the check **fail**, not skip. Confirmed the preceding `try/except`
  sets `raised = False` correctly in the success branch of each block (read whole at the pinned
  SHA) — no stale-`exc`-from-a-prior-block risk. Stronger guarantee than "reachable on green": it is
  unconditionally evaluated.
- **Over-scope guard** (`test-factory-gh.py:~310-315`): **is** inside `if set_exc is None:` (the
  success-path branch of the two-call `project_field_set` case). On a green run `set_exc is None`
  is true, so the branch is taken — corroborated independently by qa's mutant 3, which reddened
  exactly the three named regex checks when the query was over-scoped. Both the freeze assertions
  and the over-scope guard are reachable on a green run, by two different mechanisms (unconditional
  vs. conditional-but-taken) — worth stating separately since the dispatch's phrasing suggested one
  question with one answer.
- **Regex clauses**: `_re.search(r"field\s*\(\s*name\s*:", q)`, `_re.search(r"fields\s*\(", q)`,
  `_re.search(r"\b(first|last)\s*:", q)` — all three present, matching the required clauses exactly.
  `q` is extracted from `graphql_call["argv"]` (the emitted `-f query=...` argument), **not** from
  `factory_gh._FIELD_QUERY` directly — confirmed by reading the extraction loop
  (`test-factory-gh.py:~300-308`). This is the distinction the plan's intent called load-bearing
  (a constant that passes at the unit level but is rewritten before the call would still be caught
  here), and it is honored.

**Severity: none — confirmed correct, not a finding.**

## Additional checks run, not requested but adjacent

- The `option_id` resolution loop in `project_field_set` (`factory_gh.py:320-323`) has `break`
  correctly nested inside `if o["name"] == option:` — read at the pinned SHA rather than trusting
  diff-hunk indentation. Not a defect.
- Whether the options loop is exercised past the first list entry: `test-factory-integration.py`
  drives real station moves to `Building` (`:509-510`, claim) and `Review` (`:567-568`, land) through
  the actual `project_field_set`, both non-first entries in the fake's
  `[OPT_READY, OPT_BUILDING, OPT_REVIEW]` list. Covered — not a gap.

## What I would NOT block on

Both (A) and (B) findings above. (A) is an unrecorded reasoning gap behind an already-safe code
path; (B) closes clean with no open question. Neither is a wrong-behavior scenario I can point to —
only a documentation/provenance gap in one case, and confirmed-correct in the other.

```yaml
VERDICT: PASS
DIGEST:
  headline: "T-01 + MF-1 both implement the signed plan.yaml/BRIEF.md spec exactly; two adversarial probes (projectV2.id absent, freeze/over-scope-guard reachability) both resolve to info-level or non-findings — nothing gates."
  severity_max: info
  findings: 2
  must_fix: []
  spec_violations: []
  reviewed: "8dedeae..2ea9af3"
  human_commits_in_scope: []
  open_questions:
    - { id: Q1, question: "projectV2.id absent-while-non-null is handled by a safe KeyError crash, but the reachability argument that would rule it truly unreachable from a conformant gh response (ProjectV2.id as ID! null-propagating to projectV2) is unverified and unrecorded anywhere in DESIGN.md or qa-c0.md. Worth a one-line addition to DESIGN.md's Contract 2 if anyone revisits this path, not worth a fix cycle now.", blocking: false }
  files_touched: []
  expertise_update: []
artifact: .harness/features/FEAT-11-graphql-field-resolve/notes/review-harness-code-reviewer-c0.md
```
