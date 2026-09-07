# Plan-panel c1 — scope reader — T-10 and T-11

**BLUF: one real finding.** T-11's file 1 (`tests/unit/test-feature-schema-build-entry.py`) plans
three cases — BE-01, BE-05, BE-07 — that duplicate, predicate-for-predicate and observable-for-
observable, assertions `tests/integration/test-check-state.py`'s `case_t06_build_entry_invariant`
already makes by calling `feature_schema.recovery_command_for` directly in-process. This is the
exact DEC-217 Over-clause shape the plan already spent two amendment cycles removing from BE-21/22/23
— just in the file nobody cross-checked. Everything else I read (T-10's fixture repair, T-11's
gh-sync.py-hosted cases BE-11..BE-30, the depends_on lists, the REQ traces, the 29-id count
arithmetic, BE-16..BE-20's five-branch guard) holds up. The three known-open items (T-07's unit
floor, the approval re-sign, BE-22/23's real gh-sync.py defect) are being handled correctly — each is
surfaced as an explicit open question in the c8 re-aim record, not swept under a green verify.

## The finding, precisely

`tests/integration/test-check-state.py:4682-4699` (`case_t06_build_entry_invariant`, already built —
T-06 is done) calls `feature_schema.recovery_command_for(feat_dir)` **directly**, not through a
subprocess, and asserts `== "recover-terminal"` for three inputs bundled under one `all(...)` check:

| existing trigger (test-check-state.py:4687-4696) | planned T-11 case | same branch? | same observable? |
|---|---|---|---|
| `("BUG-1030-stale-anchor-write-hazard", "building", None)` — an era member | **BE-01** "an era-set member returns recover-terminal with no plan.yaml present at all" | yes — `feature_schema.py`'s first `if …in BUILD_ENTRY_ERA_EXEMPT: return "recover-terminal"`, which short-circuits *before* plan.yaml is ever read, so BE-01's "no plan.yaml" framing never reaches the branch it names | yes — `"recover-terminal"` |
| `("FEAT-9001-fixture-non-era", "review", None)` | **BE-05** "plan status review returns recover-terminal" | yes — `plan.get("status") in {"review","done"}` | yes |
| `("FEAT-9001-fixture-non-era", "building", "done")` | **BE-07** "plan status building with one task status done returns recover-terminal" | yes — the `any(task.get("status")=="done"…)` leg | yes |

`recovery_command_for` itself: `feature_schema.py:324-338` (read at plan-cited lines). The existing
integration case: `feature_schema.py:200-355` `read` confirms the fixture builds a real `plan.yaml`/
`feature.json` pair and calls the pure function directly — it is a mutation-provable guard already
in the tree (flip either branch and this assertion reddens), which is exactly what DEC-217's Over
clause (`DECISIONS.md:6876-6878`) names: "copying an already mutation-proven integration contract
guard into `tests/unit/**` solely to satisfy a directory label."

**This contradicts D-10's own stated justification** (`plan.yaml:115-138`), which claims every T-06
case is "asserted as a decision table the subprocess suites do not enumerate," and T-11's own
CONVENTIONS preamble (`plan.yaml:~1516-1518`), which claims `test-check-state.py` "reach[es] at one
or two points at most, never exhaustively" — measured, it already reaches all three of BE-01/05/07's
input classes, bundled in one assertion. The c1 goalcheck and the c8 re-aim record both verified
BE-21/22/23 against `test-gh-sync.py` exhaustively but never diffed BE-01..BE-10 against
`test-check-state.py`'s own T-06 case — this is the "union of two lenses" gap the dispatch warned
about, just relocated to the other file pair.

**Not duplicated**, checked the same way: BE-02 (trailing-slash era member — the existing fixture
never appends a slash to `feat_dir`, so this pins the same `rstrip()` gap class as BE-22/23, at a
different call site), BE-03/BE-04 (the `except Exception: return "recover-terminal"` leg for
missing/unparseable `plan.yaml` — untouched by the existing case), BE-08/BE-09/BE-10 (explicit
`"ready"` status, empty tasks list, exact non-membership — none constructed by the existing fixture).
BE-16..BE-20 (the five-conjunct skip guard) — no overlap found; nothing in either integration file
manipulates `_BUILD_ENTRY`/`remote_written` directly, and each of the five negates a different
conjunct (verified against `gh-sync.py:186-192`).

**Lower-confidence secondary note, not filed as a separate finding:** BE-06 ("plan status done
returns recover-terminal") is *indirectly* exercised by `test-check-state.py`'s first INV-37 check
(`fixture(tmp, "FEAT-9001-fixture-non-era")` defaults `station="done"`, and the subprocess assertion
requires `"recover-terminal" in line`) — but that's a different observable layer (a printed message
through `check-state.sh`'s own branch at `check-state.sh:2011-2018`, not `recovery_command_for`'s raw
return), so I would not call it as clean-cut a duplicate as BE-01/05/07. Worth a second look, not
worth blocking on.

## Everything else checked and held

- **T-10** (`plan.yaml:1444-1507`): single call site for `_commit_feature` confirmed at
  `test-hooks-install.py:406` (grep, one hit besides the `def`). All three verify needles are true
  prefixes of real/planned assertion names (`test-hooks-install.py:419` region, and the new
  assertion's exact text as specified). The retention-skip message it must NOT match,
  `"records github.build_entry"`, is verbatim in `post-merge-sweep.sh`'s SKIP print. `depends_on:
  [T-07]` is correct — the fixture repair only makes sense once T-07's retention branch exists.
  `traces: [REQ-02]` (post R4) is accurate; the heredoc bounds `post-merge-sweep.sh:29-293` cited for
  known-open item (a) are exact (grepped `PYEOF`/`set -u`).
- **T-11 gh-sync.py-hosted cases (BE-11..BE-30)**: cross-checked against every `build_entry`
  occurrence in `test-gh-sync.py` (T-02's 8 named cases at :3409-3494, T-03's 7 at :3509-3586, T-04's
  5 at :3596-3624) — none constructs an out-of-enum value, a bare `record_build_entry` call, or a
  direct `_recover_terminal_conflict`/`_recover_terminal_report` call the way BE-11/12/13-15/25-30
  do. BE-22/BE-23 reproduced RED at HEAD by reading `_build_entry_preflight`
  (`gh-sync.py:1357-1376`) directly: `feature_id = os.path.basename(feat_dir)` with no `rstrip`,
  confirmed — the same code the c8 re-aim record already diagnosed. BE-21's strike is correct: with
  the slash removed, `rec={"build_entry":"reopened"}` falls through both `if`s exactly as BE-24 does,
  confirmed by re-reading the function's four terminal paths.
- **29-id arithmetic**: file 1 "Ten cases" = BE-01..BE-10 (10); file 2 "Nineteen cases" = BE-11..BE-20
  (10) + BE-22..BE-30 (9) = 19; 10+19=29, matching the verify's explicit `01..20,22..30` list
  (29 tokens, counted).
- **`depends_on`**: T-11's `[T-02, T-03, T-04, T-06]` maps onto real touched seams
  (`record_build_entry`/`load_recorded`/`save_recorded` → T-02; recover-terminal helpers → T-03;
  `_build_entry_preflight` → T-04; `recovery_command_for`/`BUILD_ENTRY_ERA_EXEMPT` → T-06). T-01
  (the schema declaring `build_entry`) is already built and the unit fixtures construct dicts
  directly rather than round-tripping the JSON-schema validator, so its absence from `depends_on`
  has no live consequence — noted, not filed.
- **Known-open (a)/(b)/(c)**: all three are surfaced as explicit, unresolved, correctly-routed
  questions in the c8 re-aim record (Q1 for (a)/(c)'s consequence on T-11's own verify, Q3 for (b));
  T-11's intent itself states in plain language that its `verify` cannot reach `VERIFY-PASS` while
  BE-22/23 stay red. Nothing new to raise here.

## Not filed

- The `feature_id = os.path.basename(feat_dir)` missing-`rstrip` defect itself — already known-open
  item (c), already escalated as Q1 in the c8 re-aim record.
- T-11's `verify:` being structurally unable to reach `VERIFY-PASS` while BE-22/23 stand — already
  documented in the task's own intent text and in the c8 re-aim record's Q1.
