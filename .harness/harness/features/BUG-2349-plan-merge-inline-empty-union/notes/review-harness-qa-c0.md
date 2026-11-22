# QA gate review — BUG-2349 c0 — harness-qa

Pin: `2a476ca04c3516bdac3e69dfe66cec7eb372e243` (base `e239d88156c508c948d49cd31238ea13b3b39865`). `git diff --name-only e239d88 2a476ca` outside `.harness/` = exactly `union.py` + `tests/integration/test-plan-merge.py` (SC-03 file scope holds).

## BLUF
**FAIL — one finding: the bugfix matrix's `unit` floor is `missing`.** `touches_runtime_code` fires on `union.py`, so `bugfix.when[unit]` requires `unit`; the unit kind runs green but no unit test binds `_union_key_head`/plan-merge union behavior. Integration evidence is strong (SC-01/02 green at the pin; SC-01 natural red captured). Nothing else blocks.

## Phase 1 (from BRIEF/plan only)
Expected: (a) `decisions: []` + add item → exit 0, reload has item; (b) same for `tasks: []`; (c) non-empty flow `decisions: [a]` + add → exit 5 "one dash per item", base unchanged; (d) fresh scratch git repo round-trip pre- and post-merge; (e) a unit-level test of the head-selection rule if the matrix requires `unit`. (a)–(d-pre-merge) have tests/receipts; **(e) has none → coverage gap.**

## Matrix (`harness.json`, change_type `bugfix`)
`always: []`; `when`: `unit if touches_runtime_code` → TRUE (union.py is runtime code); `integration if fix_confined_to_tests_and_contract_docs` → FALSE (runtime changed; integration is still the SC-01/02/04 evidence kind, `status: active`); `__bug_class__` → G-08 placeholder, fires for nothing. Harness.json read directly; present.

| kind | state | cmd (run once, at pin, `env -u HARNESS_AGENT_TYPE`) | result |
|---|---|---|---|
| unit | **missing** | `.agents/skills/harness/bin/run-unit-tests.py --kind unit` | rc 0, 63 files, 1202 PASS lines, 0 FAIL — but unrelated to the change (below) |
| integration | satisfied | `.agents/skills/harness/bin/run-unit-tests.py --kind integration` | rc 0, 91 files, 2901 PASS lines, `PASS test-plan-merge.py`, six `PASS  2349:` checks |

Unit is `missing`, not `satisfied`, because: `grep` of `tests/unit` for plan-merge/union finds only incidental references (`test-decision-disposition-schema.py` drives set-key/apply for disposition rows; `test-feature-record.py` and `test-gh-sync-build-entry.py` mention it/import `approval`); none calls `_union_key_head` or applies over an inline-empty union key. Green adjacent unit tests do not satisfy the kind (verification-rules, P-04). Counts are runner PASS-lines (one per script, G-04 — not case totals). Raw: `/tmp/qa2349/{unit,integ}.txt` (transient; rc=0 each).

## SC evidence (pin, test lines in `tests/integration/test-plan-merge.py`)
- SC-01: `case_2349_inline_empty_decisions_gains_items`, `case_2349_inline_empty_tasks_gains_items` (separate cases, each its own key; assert rc 0 and reloaded fields, `_apply_to_inline_empty` fixture).
- SC-02: `case_2349_nonempty_flow_base_still_refused` (asserts rc 5, `"not one dash per item"`, base byte-identical).
- SC-04: literal T-01 verify, receipt `notes/receipts/sc01-sc02-sc04-green-prefix.txt` lines 1–2, 689–691: rc 0, scratch `APPLIED`, `BUG-2349 scratch round-trip PASS: {'decisions': [{'id': 'D-01', 'choice': 'x'}]}`. I read the verify block in `plan.yaml` directly; it uses `BUG2349_TOOL_ROOT`, a fresh `git init` repo, and asserts exit 0 + reload equality (genuine, not self-referential; it does not use `git diff HEAD`). **Pre-merge receipt graded; the post-merge rerun is the main-session ship obligation, not a pre-merge must-fix.**

## fail_first (inspected, not rerun)
- SC-01: **natural red, assertion-kind** — `notes/receipts/sc01-sc02-red.txt` (rc=1; command line 1; HEAD `71f9aa45`, union.py identical to base e239d881 asserted in `red-first-T-01.md`): lines 681, 693, 695, 707 are `FAIL  2349: …` for both keys (apply exit 5 "splice defect"; reload shows base unchanged `tasks: []`). 680 PASS / 4 FAIL = failures are exactly the SC-01 checks, not load errors. Tier: natural RED at a recorded pre-fix state (O-03). Caveat: new tests were uncommitted in the worktree at that run, so the red is bound to the receipt, not to a commit.
- SC-02: **preservation control, not bug red-first.** Lines 709–710 show it PASS on the base (refusal pre-exists); discrimination vs. a relaxed `_aligned_items` is not shown by a red. I did not mutate; per O-05, discrimination is *unshown*, not absent. Honest `fail_first` entry says so.
- SC-04: no pre-fix scratch-repo capture exists (the BRIEF only requires after-fix and after-merge). The same mechanism is red in SC-01's receipt; the scratch verify itself was recorded green only. Stated as a limit, not a defect.

## Findings
1. **kind=missing-test (unit floor) · severity=high** — Task T-01, `touches_runtime_code`, bugfix matrix: no unit test exercises `_union_key_head` (`union.py:511-520`) or any plan_merge union behavior. Route: owning dev (main-session-direct under DEC-174) adds a focused unit test (the function is pure: `(key, base, prop, base_item_ranges, prop_item_ranges)` — head chosen from proposal iff base items empty and proposal items non-empty; else base head; else proposal; else None), or the operator rules the integration suite is this repo's unit-level surface for plan-merge and records that. QA does not author it.
2. **kind=evidence-hygiene · severity=low** — the green receipt's checkout SHA is `71f9aa45` with the fix as an uncommitted working-tree change; the fix commit is `4cf45dd3`, the pin `2a476ca0`. SC-04 asks for the tool checkout SHA; the post-merge receipt (merged SHA) will cover it. At the pin I re-ran the integration kind green (above), so the code under review is independently shown green.
3. **kind=coverage-edge · severity=low (advisory)** — untested neighbours of the new predicate: base with `tasks:` null/blank-block head (no items) + proposal items; base empty + proposal key with zero items (must keep base head). Not required by any SC.

## Not done / limits
Did not rerun the scratch verify or the red (instructed). No mutation proof taken (read-only source, gate-only). Product `docs/spec.md`, `docs/decisions.md`, `docs/architecture.md` absent in the product checkout — no guidance consulted or invented; none contradicted.

## Principles applied
- Delete First (leaf read): "minimize the diff" / "design for observed usage" — the production change is one predicate in the existing `_union_key_head` (the module that already reads the ranges), no new layer or threaded signal; no objection raised on diff size.
