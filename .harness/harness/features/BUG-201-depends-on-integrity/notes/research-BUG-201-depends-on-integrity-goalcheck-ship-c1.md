# Goal-check — BUG-201-depends-on-integrity — ship c1

**The GOAL is MET. Nine of nine criteria met, each by its own declared method, executed at
`review_sha 626bb599`.** No criterion is unmet, none is unprovable as written, no UAT applies (no
`verify: uat` in BRIEF.md). Nothing here rests on another agent's digest: the one recorded run
SC-05 grades by design was additionally re-run live at the pin.

Suites run from the worktree, every invocation prefixed `env -u HARNESS_AGENT_TYPE`. Content
evidence read with `git show 626bb599:<path>`. Working tree clean at `2fe5f902` (notes +
feature.json only), so live runs are valid for the pin.

## The nine rows

| id | verdict | method executed | observed evidence |
|---|---|---|---|
| SC-01 | met | automated/unit | `python3 tests/unit/test-plan-depends-on.py` → `12/12 checks passed.` The naming clause is case 1, `test-plan-depends-on.py:96-101`: fixture `T-02 depends_on [T-99]`, assertion `isinstance(exc1, PlanSchemaError) and "T-02" in str(exc1) and "T-99" in str(exc1)`, printed `ok  a depends_on entry naming an absent task id is rejected, naming both ids`. Corroborated by case 3 (`:111-118`, `T-98`+`T-99` in ONE exception, D-02) |
| SC-02 | met | automated/integration | `python3 tests/integration/test-plan-merge.py` → `PASS test-plan-merge.py`. **5-of-5 clauses asserted separately**, `test-plan-merge.py:2138-2157`: exit **EXACTLY 5** (`r_a.returncode == 5`, `PASS bug201a: apply refuses a dangling depends_on with exit 5` — not 9), `ILLEGAL PLAN` present (`:2140`), `T-99` present (`:2141`), base **byte identical** (`:2143`, stronger than sha256-unchanged); paired allow `depends_on: [T-01]` exit 0 (`:2154`) and `- id: T-03` present after reload (`:2157`). Non-vacuity: `PASS bug201: the fixture base is a LEGAL plan (harness_yaml.load_plan accepts it)` |
| SC-03 | met (count clause met too — no UNPROVEN-BY-COUNT needed) | automated/unit | `test-plan-depends-on.py` case 7 (`:177-187`) printed `ok  the live plan corpus loads cleanly (68 files found, floor 67)` — zero failures, **68 ≥ 67**. Provenance independently confirmed: `.harness/harness/features/*/plan.yaml` = 68 in the main checkout and 68 in the worktree, and `git ls-tree -r --name-only 626bb599` counts 68 committed. Paired detector case 8 (`:209-211`) `ok  the same walk reports exactly one failure naming the throwaway dangling plan`, so the walk is not vacuous |
| SC-04 | met | inspection | `git grep -n "_validate_plan_depends_on" 626bb599` → **exactly one `def`** (`harness_yaml.py:427`) and **exactly one call site** (`harness_yaml.py:343`, inside `validate_plan_doc`), both in `.claude/skills/harness/bin/harness_yaml.py`. All other matches are PROSE: BRIEF.md:90-91, plan.yaml:166,432, four `notes/receipt-*`/`notes/review-*` files, `observations/harness-backend-dev.md`, `notes/research-*-goalcheck-plan-c1.md`. Second clause discharged independently — see below. MF-1's `_depends_on_entries`/`_dangling_edges` (`:391`,`:411`) are inside that one call tree, which is what the criterion scopes |
| SC-05 | met | inspection of the recorded run + live re-run | Record `notes/receipt-harness-backend-dev-T-01-c1.md`. **4-of-4 clauses**: (a) reached its cases — `:60-62` "file imported cleanly (no `ModuleNotFoundError`), every one of the 10 checks was reached and printed a distinct ok/FAIL line (no ImportError/fixture crash)"; (b) paired allows PASSED in that same run — case 2 `:42`, case 4 "ok, ok, ok" `:47`, cases 6a/6b `:52-55`; (c) FAIL lines **exactly** {1, 3, 5, 6c} — the four literal FAIL lines at `:22-29`, final line `4 of 10 FAILING.`, set stated `:59`; (d) passes in full now — live `12/12 checks passed.` (10 then, 12 now: T-04 appended the two corpus cases) |
| SC-06 | met, 3-of-3 suites + 3-of-3 naming | automated/unit | Each run by name: `test-factory-claim.py` → `133/133 checks passed.`; `test-factory-claim-mutation.py` → exit 0, `MUTATION PROOF: 3/3 cases reddened` + `KEY-COLLAPSE PROOF`; `test-harness-yaml-corpus.py` → `16/16 checks passed.` Second clause read from plan.yaml `verify:` blocks: T-03 `:413,415,416` and T-06 `:580,581,586` each name all three |
| SC-07 | met, 6-of-6 suites by name + 6-of-6 naming + 7-of-7 anchors | automated/integration | Each run individually (not a pool): `test-gh-sync.py` exit 0 `ALL PASSED`; `test-check-plan-routes.py` exit 0 `ALL PASS`; `test-harness-yaml.py` exit 0; `test-plan-merge.py` exit 0 `PASS`; `test-factory-decompose.py` exit 0 `162/162 checks passed.`; `test-check-state.py` exit 0. Naming: T-03 `:412,414,417,418,419,420`, T-06 `:582,583,584,585,588,589`. Factual claim spot-checked at the sha the criterion itself names (`af859ee8`, since T-06 shifted two files): all seven anchors are `load_plan` calls — `check-plan-routes.py:366`, `check-state.sh:140`, `factory_claim.py:107`, `factory_decompose.py:471`, `gh-sync.py:357/:1154/:1264`. The six-file closure holds: `git grep -ln "load_plan("` at the pin returns those five plus `harness_yaml.py` itself, and `plan-merge.py` reaches the rule via `validate_plan_doc` |
| SC-08 | met, 5-of-5 clauses | automated/unit | `python3 tests/unit/test-factory-claim.py` → `133/133`. Named cases, each printed `ok`: `(Da) blocker-gate reason a caller receives names BOTH T-02 and T-99` (`:1019`); `(Da) …no longer carries the missing-or-unparseable wording` — asserts `"no plan could be read" not in reason` (`:1021-1023`); `(Dc) poll does not crash: exit 0, #790 claimed despite #780's dangling plan` (`:1053`) = returns rather than raising AND the second legal candidate still evaluated and claimed; `(Dc) no traceback anywhere on stderr` (`:1059`); paired legal `(Db) blocker-gate over the legal fixture is CLEAR, exactly (B3)'s verdict` (`:1038`, the existing clear-candidate assertion). Prerequisite `(D0)` pair also `ok` |
| SC-09 | met, both sites, 9-of-9 ok lines | automated/integration | `python3 tests/integration/test-gh-sync.py` → exit 0, `ALL PASSED`, 318 ok lines. `start-task`: `ok (d) …exit status EXACTLY 2`, `ok (d) exactly one stderr line names BOTH T-02 and T-99`, `ok (d) no Traceback anywhere in the output`; paired `ok (e) …exits 0, exactly as today` + `ok (e) …sets T-02's OWN issue station to Building`. `status Ready`: `ok (f) …exit status UNCHANGED from today (2)`, `ok (f) the existing refusal line is UNCHANGED from today (captured pair, additive)`, `ok (f) stderr ALSO carries a line naming BOTH T-02 and T-99, additive to the above`; paired `ok (g) …exits 0, exactly as today` + `ok (g) …both recorded sub-issues moved to Ready`. Prerequisite `(D0)` raises/returns pair also `ok` |

## SC-04's second clause, discharged on its own

Searched the reviewed tree, not just the helper name. `git grep -n "depends_on" 626bb599 --
.claude/skills/harness/bin/` plus `git grep -nE "absent from (this|the) plan|task ids
absent|dangling"` over the same path. Every hit classified:

- `plan-merge.py` — **zero** `depends_on` matches; reaches the rule only through
  `validate_plan_doc`. (`:46`'s "absent from the plan" is `set-task-station`'s `--task` miss, a
  different field.)
- `check-plan-routes.py:337,350` — `depends_on` appears only as a member of `BUDGETED_FIELDS`, a
  byte-budget field list. No comparison.
- `factory_claim.py:183-192` — resolves entries against `feature.json`'s issue map, never against
  the plan's own task ids.
- `factory_decompose.py:263` (`_owes_edges`) and `:636` — compare entries against recorded
  `blocked_by` edges and `factory["issues"]`, both `feature.json` state. Not the plan's task ids.
- `gh-sync.py:1169,1279` — comments only.

No second implementation of the rule exists under any name.

## Open questions

None. No criterion required re-interpretation; no amendment is needed.
