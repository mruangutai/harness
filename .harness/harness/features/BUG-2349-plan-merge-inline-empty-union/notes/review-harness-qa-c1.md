# QA gate review — BUG-2349 c1 — harness-qa

Pin `0174f364483df5c8d49f04e35d2308e5dca33257` = `feature.json` `review_sha` (verified); base `e239d88156c508c948d49cd31238ea13b3b39865`. Worktree HEAD = pin; only `feature.json` dirty (run record), `.claude`/`tests` clean. Non-`.harness` diff base..pin = `union.py`, `tests/integration/test-plan-merge.py`, `tests/unit/test-plan-merge-union-head.py`. `union.py` delta vs the c0 pin 2a476ca0: none (only the unit file added).

## BLUF
**PASS.** The c0 `unit: missing` finding is closed by advisor ruling A: the unit kind now has a named test that binds `_union_key_head` via `apply_merge`. Red is bound to e239d881 source, green is 9/9 at the exact pin, every gate ran green at the pin. Outstanding, not a pre-merge failure: the SC-04 post-merge scratch receipt, owned by the main session at ship.

## Phase 1 (BRIEF/plan only, unchanged from c0)
(a) `decisions: []` + item → exit 0 + reload; (b) same for `tasks: []`; (c) non-empty flow `decisions: [a]` → exit 5; (d) scratch-repo round trip pre/post merge; (e) a unit-level test of head selection. All have tests or receipts; no Phase 1 gap remains except the post-merge half of (d).

## Matrix (`.harness/harness.json`, read directly; change_type `bugfix`)
`always: []`. `when`: `unit if touches_runtime_code` → TRUE (`union.py`); `integration if fix_confined_to_tests_and_contract_docs` → FALSE, but integration is active and is the SC-01/02/04 evidence kind, so I ran it; `__bug_class__` → unresolvable placeholder (repo G-08), fires for nothing.

| kind | state | cmd (once, at pin, `env -u HARNESS_AGENT_TYPE`) | result |
|---|---|---|---|
| unit | satisfied | `.agents/skills/harness/bin/run-unit-tests.py --kind unit` | rc 0, 64 files (c0: 63), 0 FAIL outside the BUG-1290 mutation block; `test-plan-merge-union-head.py` ran in the pool (exit 0, 9 case lines) |
| integration | satisfied | `.agents/skills/harness/bin/run-unit-tests.py --kind integration` | rc 0, 91 files, `test-plan-merge.py` exit 0, six `2349:` PASS checks |
| T-01 verify | satisfied | plan.yaml literal block (extracted with yaml, not retyped), `BUG2349_TOOL_ROOT=<worktree>` | rc 0; `git rev-parse HEAD` = pin; `PASS test-plan-merge.py`; `PASS test-plan-merge-union-head.py` (9 PASS); `BUG-2349 scratch round-trip PASS: {'decisions': [{'id': 'D-01', 'choice': 'x'}]}` |

P-14 check: `run-unit-tests.py` discovers `tests/unit/test-*.py` by glob, so the new file is in the unit kind by discovery, not only by the glob match (seen executing in the pool output). Raw transient outputs: `/tmp/qa2349c1/{unit,integ}.txt`, `/tmp/qa2349c1/red.*`. The committed receipt `receipts/c1-verify-green-prefix.txt` was taken at 2a476ca0 with the unit file uncommitted; **this note's verify row is the exact-pin result** (the pin-bound receipt is this artifact plus the transcript above).

## Advisor's five conditions (inspected, not trusted)
1. One new file, no production change: confirmed — pin-vs-c0 delta is the unit file only; `union.py` byte-identical to c0.
2. Red bound to e239d881: reproduced. `git show e239d881:…/union.py` sha256 `2d595c81…35bb3d` matches the receipt header; `PLAN_MERGE_UNION=<that copy>` → 6 FAIL (both keys × merge-without-refusal / block head / reload; `MergeRefusal(5) UNPARSEABLE` or `None`) + control 3 PASS, exit 1. The harness loads the supplied file via `spec_from_file_location`, so the red exercises the base source. Natural RED, assertion-kind (not import error).
3. Only the fixed rule bound: file has two cases (inline-empty ×2 keys; base-with-items control). No neighbour variants.
4. No integration-as-unit waiver: none recorded or relied on here; the unit kind was satisfied by a real unit test.
5. SC-04 post-merge receipt: main-session ship obligation, **outstanding**, not graded.

## Discrimination (mutation, run via the env override on a /tmp copy — no repo edit)
Mutant `if key in base_ranges and not prop_item_ranges:` (drops the `base_item_ranges` guard, i.e. proposal head whenever the proposal has items): inline-empty cases stay green, control `keeps its own head line` goes RED (exit 1). So the control binds the "otherwise base-head precedence" half; the inline-empty half is bound by the base red. Nine assertions confirmed: 3 × 2 keys + 3.

## SC evidence and fail_first
- SC-01 (automated): `tests/integration/test-plan-merge.py` `case_2349_inline_empty_decisions_gains_items` / `case_2349_inline_empty_tasks_gains_items`; unit twin `tests/unit/test-plan-merge-union-head.py:52`. fail_first: `notes/receipts/sc01-sc02-red.txt` (natural RED, rc 1, `FAIL 2349:` both keys) and `notes/receipts/unit-red-base.txt` + my reproduction above.
- SC-02 (automated): `case_2349_nonempty_flow_base_still_refused`. Preservation control; PASS on the base, so no bug-red exists. Discrimination vs a relaxed `_aligned_items` is **unshown**, not absent (O-05). Honest fail_first: control, not red.
- SC-03 (inspection): the pin's `union.py` diff is the single `_union_key_head` predicate, exactly as specified. **Text-unmet / intent-met (O-04):** BRIEF text says the diff changes only `union.py` + the integration test; the signed amendment (feature.json judgements 20:28:38/40Z) added the unit file. Intent is met; the BRIEF wording is stale against the ledgered amendment. Routed to main/goal-check, not a QA failure.
- SC-04 (automated): pre-merge verify green at the pin (above). No pre-fix scratch capture exists (BRIEF requires only after-fix and after-merge). Post-merge receipt outstanding (main).

## Absence/subject/mutant (read)
Unit assertions are presence-paired (`f"\n{key}:\n" in out` with the reload equality), the base red proves they can fail on the exact defect (G-13: the red reproduces the real UNPARSEABLE splice, not an empty state).

## Findings
None blocking. Advisory: (1) BRIEF SC-03 file-scope wording vs the amendment (above); (2) c1 green receipt in-tree is old-HEAD/uncommitted-unit — superseded by this pin-bound run; (3) product `docs/spec.md`, `docs/decisions.md`, `docs/architecture.md` absent — no guidance consulted or invented.

## Principles applied
Build the Lever / verification rules only as the gate: extracted the verify block mechanically from `plan.yaml` rather than retyping it; no tests or source authored (DEC-174).
