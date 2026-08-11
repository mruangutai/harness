# Goal-check — FEAT-13 Single-issue board lookup

**Nine of ten success criteria met. SC-05 is `partial` — its declared unit evidence never
instantiates a closed issue, so the one behaviour it exists to protect is unproven.** The behaviour
is not wrong: `_ISSUE_ITEM_QUERY` (`factory_gh.py:295-305`) carries no state filter of any kind, read
at source. It is unproven, which routes to qa, not to a fix cycle.

Evidence collected at `d4951c2` from the worktree
`/Users/molchairuangutai/GitHub/harness/.claude/worktrees/FEAT-13-single-issue-board-lookup`.
Both configured runners re-run by me there: `run-unit-tests.sh --kind unit` exit 0, 10/10 scripts
PASS; `--kind integration` exit 0, `test-factory-integration.py` 97/97. No `gh` call was made.
The integration runner reaches no live `gh`: every `base_env(...)` call site
(`test-factory-integration.py:389,428,497,533,591,625,649`) passes `gh_bin=<stub>`, and `base_env`
sets `FACTORY_GH` to it (`:349-350`), which `factory_gh.run_gh` reads at call time.

## Per-SC verdicts

| id | verdict | assertion | would-fail-if |
|---|---|---|---|
| SC-01 | met | `test-factory-gh.py:647,650,652` | the helper falls back to a `project item-list` read, or emits a second call: `:647` counts exactly one, `:650` pins `argv[1:3] == ["api","graphql"]`, `:652` pins zero `argv[1:3] == ["project","item-list"]` |
| SC-02 | met | decompose `test-factory-decompose.py:956-957` · land `test-factory-land.py:213-214` · claim `test-factory-claim.py:475-476` | any one call site keeps or reintroduces its whole-board `project_items` read — each of the three recorders asserts that list is empty independently, so a partial revert reddens only its own site |
| SC-03 | met | no-item: `:670-671` (node on a different project number) and `:682-683` (empty nodes, totalCount 0) · unrecognised: `:709-710` (no `"issue"` key raises), also `:721,:732,:743,:782,:793` | the helper collapses the discrimination — `issue = repository.get("issue"); if issue is None: return None` returns None for the key-absent shape and reddens `:709-710` alone (qa's M1 mutant, one check). Conversely, raising on a recognised empty list reddens `:682-683` |
| SC-04 | met | `test-factory-gh.py:768-771` | the truncation guard is dropped or made a `>=`: `totalCount 3` with one node returns None instead of raising, and `:769-771` also pins both totals appearing in the message |
| SC-05 | **partial** | `test-factory-decompose.py:1024` (no second `project_item_add`) · `:1026-1030` (call shape is exactly `(repo, number, board)`, no state kwarg) | **the discharged half:** decompose adds a `query=`/state argument at its own call site, or re-adds the item. **The undischarged half:** nothing fails if the *helper's query text* gains a state filter — see below |
| SC-06 | met | `test-factory-claim.py:532-536` (R6a, closed + unowned) · `:546-550` (R6b, closed + `factory:claimed` + self-assigned) | the closed-issue refusal moves after the self-ownership branch: R6b flips to exit 0 and re-emits, R6a stays green (qa's M3 mutant reddened exactly the two R6b checks). Both cases also assert `mutating_calls() == []` and `create_ref_calls() == []` |
| SC-07 | met | `test-factory-land.py:337,341,344,347` | land's state check moves earlier in the sequence: `:341` (push happened) and `:344` (PR created) are **positive** assertions, so an early refusal reddens them; `:347` pins `field_set_calls == []` (qa's M4 mutant reddened two checks) |
| SC-08 | met | `test-factory-integration.py:775` (`(F) land: board item actually moved to Review`), answered by the query-text-keyed stub branch at `:179-211` | the real argv the tools emit stops matching what the stub parses — the stub reads `owner=`/`name=`/`number=` out of the actual argv and its synthetic node carries `project.number = 9`; a mismatch makes the lookup return None and land never reaches Review |
| SC-09 | met | `test-factory-claim.py:568` (exactly one `project_items`) · `:569-570` (query string is literally `Status:"Ready" is:open`) · `:571-572` (poll never calls the new helper) | the poll is "tidied" onto the new helper, or its query string drifts by one character |
| SC-10 | met | receipt `notes/receipt-harness-backend-dev-live-spot-check.md:1-2, 39-53, 67-72` | `points_used: 1` against the "at most 5" bar, agreeing across two rounds with a null control of 0; `item_id_match: yes` — `PVTI_lAHOAAases4BfZ9Zzg2AMPA` returned by the helper in both rounds equals the id derived independently from `project item-list` after the measured window |

**Tally: 9 met, 1 partial, 0 not_met.**

Compound-criterion counts, both numbers as required:

- **SC-02** — 3 clauses (three call sites), 3 separate assertions, one per site. Balanced.
- **SC-03** — 2 clauses (no-item does not raise; unrecognised shape raises). Fixtures: 2 for the
  no-item clause as worded (`ISSUE_ITEM_OTHER_PROJECT_JSON`, `ISSUE_ITEM_EMPTY_JSON` —
  `test-factory-gh.py:115-119`), plus the `issue: null` case at `:694-696` which is a third
  non-raising case; 6 for the raising clause. Every case is its own `check()`. Balanced and then
  some.

## SC-05 — why partial, and the single fix

SC-05 reads: *decompose's recovery path resolves the existing item id for an issue whose state is
closed, and issues no second board add for it.* Method is fixed at `automated`/`unit` at approval.

Clause (ii) — no second board add — is fully discharged at `:1024`.

Clause (i) — **an issue whose state is closed** — is never instantiated. The decompose Recorder's
`issue_board_item_id` returns `self.item_by_issue.get(number)` unconditionally
(`test-factory-decompose.py:123-125`); it has no notion of issue state. D4-3c differs from the
open-issue case D4-3 only in the item id string (`"ITEM-CLOSED"` vs `"ITEM-EXISTING"`). The test's
own comment says so (`:995-999`). Nothing in the integration suite fills the gap: `grep -n CLOSED
test-factory-integration.py` returns nothing.

**Binary answer to the `_ISSUE_ITEM_QUERY` question: NO. No existing assertion fails if `state: OPEN`
is added to the query text.** Verified, not inferred:

- `grep -rn "_ISSUE_ITEM_QUERY" .claude/skills/harness/bin/test-*.py` → no hits.
- The unit fakes return canned JSON irrespective of the query string; the only query-text assertions
  in `test-factory-gh.py` are `:346-350`, and they belong to `project_field_set`.
- The integration stub keys on `"projectItems" in query_text` and then answers from its own state
  dict, so it satisfies any query text containing that token.
- decompose's D4-3c asserts the call-site tuple only (`:1026-1030`).
- T-01's `verify:` block carries no query-text clause.

These are not two findings. Because both fakes are state-blind by construction, **an assertion on
`_ISSUE_ITEM_QUERY`'s literal text is the only non-vacuous way to discharge SC-05 clause (i)** —
making a fake state-aware would test the fake. So this is not a scope addition to be noted and
deferred; it is the missing evidence for an approved `automated` SC, which routes back to qa.

Concrete shape: one `check()` in `test-factory-gh.py` asserting `_ISSUE_ITEM_QUERY` contains no
`state`/`states`/`filterBy` token, mirroring the existing `project_field_set` query-text idiom at
`:346-350`. It exceeds the signed step-5 list, so the operator authorises it, not the factory.

## The falsified instruction at `plan.yaml:368` — recommendation: no amendment

The defect is one line. `plan.yaml:367` already writes `argv[1:3]` correctly for the `api graphql`
clause; only `:368` carries `argv[:2] == ["project", "item-list"]`, which can never be true because
`run_gh` (`factory_gh.py:88`) builds `[gh] + list(args)`. The shipped test uses `argv[1:3]`
(`test-factory-gh.py:652`), so the code is right and only the plan's prose is wrong.

| | amend `plan.yaml:368` | leave it, observation only |
|---|---|---|
| operator cost | one signature on a finished plan | none |
| record cost | editing a signed artifact is a re-signature, not a correction — the file stops being what was approved | the on-disk plan keeps one instruction a reader could copy |
| residual risk | none on this file | a future plan author copies the vacuous slice form — mitigated: the adjacent `:367` already models the right form, and the defect is recorded in `feature.yaml plan_text_defect_found` and qa's Q1 |

**Recommend: do not amend.** Two records already exist; a third buys nothing, and the real exposure
is the idiom recurring in *future* plans, which an observations entry distilling into pm Expertise
addresses and an amendment to a completed plan does not.

## Two records, non-blocking

- T-01's commit message says the live read "returned the board item for an issue in the CLOSED
  state." The receipt records board **status** `Done` and a merged PR #222 — not the issue's `state`
  field (`receipt:19-25, 67-68`). It cannot move SC-05 either way (method fixed at `automated`), but
  the commit message asserts more than the artifact records.
- The BRIEF, `plan.yaml` `approval.rulings` and `feature.yaml` all cite
  `.harness/notes/grilling-board-read-lookups-2026-08-10.md` as binding; it is not reachable from
  this branch (`feature.yaml grilling_note_unreachable`). Not a goal-check finding — recorded so it
  is not rediscovered.

## Not reopened, per the dispatch

`claim --issue` exit 2 (ratified at signature); the grilling `## Settled` section; `land`'s #238;
harness defects #218/#241/#242; the claim poll's retained `project_items` and `totalCount` guard.
