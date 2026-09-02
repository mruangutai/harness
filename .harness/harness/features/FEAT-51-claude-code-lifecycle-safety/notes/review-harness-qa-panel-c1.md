# QA gate — FEAT-51 panel c1 — pin `fa5ce88e07d0a094570da25bf1110370ef84fcab`

## Verdict: matrix satisfied, both hard-gate kinds executed, five mutation probes all discriminated correctly. No new gating finding.

## 1. Change type and required kinds

Tasks (`plan.yaml`, all `done`): T-01 `api`, T-02 `logic`, T-03 `cross_module`, T-04 `feature`,
T-05/T-06 `docs`, T-07 `cross_module`, T-08 `scaffolding`, T-10 `cross_module`.

`harness.json` `test_matrix`: `cross_module` → always `[unit, integration]`; `feature` → always
`[unit, integration]`, `ui` when `has_interaction_flow` (not applicable — no UI, no interaction
flow: this is a CLI hook + markdown-playbook feature); `api` → always `[unit]`, `integration` when
`touches_db_or_external` (not applicable, no DB/external service; already required anyway by the
`cross_module`/`feature` tasks); `logic` → always `[unit]`; `docs`/`scaffolding` → `always: []`.

**Floor: `unit` and `integration`, both required.** No `ui`, `component`, `eval` obligation — none
of `test_kinds.ui/component/eval` has a `cmd` and none of the nine tasks' change_type requires them.
`functional` stays excluded under DEC-187 (per-project, unrelated to this diff).

## 2. Per-kind results (real exit codes)

| kind | cmd | exit | result | notes |
|---|---|---|---|---|
| unit | `run-unit-tests.sh --kind unit` | **0** | satisfied | 519 `PASS` lines, 0 `FAIL` |
| integration | `run-unit-tests.sh --kind integration` | **1** | satisfied (accepted) | 742 `PASS` lines, **7 FAIL** |

Integration FAIL lines, verbatim:
```
FAIL case_04_all_granted_exits_0 MANIFEST .../.harness/team-config.yaml
FAIL case_05_ungranted_declared_main_session_exits_0 MANIFEST .../.harness/team-config.yaml
FAIL case_15_deviation_plan_still_exits_0 MANIFEST .../.harness/team-config.yaml
FAIL case_17_midpattern_wildcard_grant_exits_0 MANIFEST .../.harness/team-config.yaml
FAIL case_19d_explicit_path_unaffected_by_the_root_guard ... DEVIATION .../.harness/team-config.yaml differs ...
FAIL case_19d2_explicit_path_with_no_tasks_still_exits_0 ... DEVIATION .../.harness/team-config.yaml differs ...
FAIL test-check-plan-routes.py
```
Reproduces the lead's measured shape exactly: 7 FAIL, all `test-check-plan-routes.py`'s
manifest-DEVIATION family, all attributable to T-03's approved `team-config.yaml` route line
existing on branch but not on main. **Ruled ACCEPTED by the operator as the gate of record — not
re-raised.** `matrix_ok: true` (both required kinds ran, both are the accepted shape).

`ui`/`component`/`eval` — not applicable; not soft-skipped in a way that weakens the floor, since
neither `test_matrix` nor the diff obligates them.

## 3. Mutation probes — the five criteria whose text claims discrimination

All run in a disposable `git worktree add` at the pin (`.claude/worktrees/harness/qa-mutation-scratch`,
removed clean afterward — no dirty tree), then copied (no `.git`, so bash-write-guard's worktree
rule doesn't apply to the *copy*) to `/tmp` because harness-qa's own domain forbids writing any
production path even inside a scratch worktree (`check-domain`/`bash-write-guard` both fired on
in-tree mutation attempts — confirmed, not routed around). Each probe below names the exact mutant.

| SC | Mutation applied | Result |
|---|---|---|
| **SC-09** | Stripped the literal string `plan-sign-gate.sh` from every sentence in the DEC-210 region of `DECISIONS.md` (both occurrences: the enforcement-points sentence and the plan.yaml-route sentence) | `test_dec_210_entry_names_both_enforcement_points` → **FAIL** (`'plan-sign-gate.sh' not found in the DEC-210 region`). Sibling checks (`states_the_bash_write_route`, `index_row_names_...`) stayed green — the failure is scoped to the one clause mutated, matching SC-09's "each clause is its own assertion" claim. **Confirmed reddens.** |
| **SC-11** | `plan-sign-gate.py`'s `quarantines()`: replaced `if not _reg.orphan_write(...): return None` with `if True: return None` — orphan-write detection unconditionally bypassed, simulating "quarantine rule removed" | `test-plan-sign-gate.py`: 5 new FAILs, including all three refusal cases SC-11 names (`an orphan agent plan-merge apply on plan.yaml is quarantined`, `...set-task-station...`, `an orphan quarantine.py adopt...`) plus the negative control and the raising-fail-open case, each now returning exit 0 where a refusal was expected. **Confirmed reddens exactly as SC-11 states.** |
| **SC-13** | (b)+(c) combined, the stronger mutant: in both `check-domain.sh`'s and `plan-sign-gate.py`'s quarantine-boundary `except` handler, replaced the `print(...stderr...); return`/`pass-through` body with a bare `except Exception: pass` / `return None` — same exit code, message dropped | `test-check-domain.py`: both `... fails OPEN at the check-domain.sh quarantine branch` cases → **FAIL** (rc stayed 0, `"boundary was not enforced"` absent from stderr). `test-plan-sign-gate.py`: both `...quarantine rule` fail-open cases → **FAIL** likewise, once the mutation was applied identically to **both** the `.claude/skills/harness/bin` and `.agents/skills/harness/bin` mirror copies (the test's own `BIN` resolves to the copy alongside itself, so a single-tree mutation under-tested the `_copybin`-based "unimportable" case — see gotcha below). **Confirmed reddens; exit-code-alone would have missed it, exactly as SC-13(b) states.** |
| **SC-07** | `inflight_registry.py`'s `orphan_write`: replaced `has_compatibility_claim = any(claim.get("runtime") != "omp" for claim in feature_claims)` with `has_compatibility_claim = bool(feature_claims)` — the runtime carve-out removed | `test-check-domain.py`: `an omp-runtime writer is never quarantined` → **FAIL**. `test-plan-sign-gate.py`: `an omp-runtime writer is never quarantined on the Bash route` → **FAIL**. Both OMP surfaces reddened together, matching "removing the runtime condition... turns the OMP case red." **Confirmed.** |
| **SC-02** | `validate-digest.py` `hook_mode()`: neutralised the `elif set(_awaiting) != _actual_children: _suspension_error = ...` branch to `elif False: _suspension_error = None`, applied to both mirror copies | `test-validate-digest.py`: **only** `a SUSPENDED return omitting a live child is refused` → **FAIL** (exit 0 instead of 2). The other four suspension cases (`live child accepted`, `claim stays live`, `no live child refused`, `member persona refused`) stayed green — those three are independently enforced (member-persona case rides the ordinary `VERDICT not in VERDICTS` path since `_kids` never populates for a non-lead/orchestrator agent; the no-live-child case short-circuits on `_kids` truthiness before reaching `_awaiting`). **Confirms SC-02's own claim that "a single whole-file search would be satisfied by the two easy ones" — the omitted-child clause is the one that needed its own targeted assertion, and it does have one.** |

**Gotcha worth recording (not a finding, a mechanics note):** `test-plan-sign-gate.py`'s
"unimportable inflight_registry" case builds its `_copybin` from the test script's *own* directory
(`.agents/skills/harness/bin`), not from `PLAN_SIGN_GATE_BIN`. A mutation applied only to
`.claude/skills/harness/bin/plan-sign-gate.py` (the canonical hook location) silently missed that
one case until the mirror copy was mutated identically. The two trees are kept byte-identical by
convention; a reviewer mutating only one tree would under-verify this specific sub-case. Filed in
observations, not Expertise (mid-run).

## 4. Test-first audit

All nine tasks land as one commit apiece with source and its paired test changed together
(`741804ad` t-01, `af5c7136` t-02, `94f7f2eb` t-03, `72ec341d` t-07, `e47afa3f` t-04, `a033793a`
t-10, `6db25ba2` t-08, `f260b5fb` t-05, `f5c33a49` t-06) — this repo's standing convention is one
commit per task, so git history cannot show file-level write-order within a commit. Two commit
messages give affirmative textual evidence of a real red-green cycle rather than tests written to
match the code: `e47afa3f` ("test-quarantine.py 25/25 after a recorded 11-assertion RED") and
`6db25ba2` ("I re-ran the discrimination myself... deleting plan-sign-gate.sh from the region reds
test 1 alone; splitting the joint plan.yaml/plan-merge.py sentence reds test 2 alone... removing the
index row reds test 3, a case the squad did not probe"). No commit in range touches a production
file without its paired test file changing in the same commit — no orphan production-only commit
found. **No test-first violation found; evidence for two of nine tasks is stronger than inference.**

## 5. Coverage bound

Every production file touched in the diff has its paired test file touched in the same diff:
`check-domain.sh`↔`test-check-domain.py`, `inflight_registry.py`↔`test-inflight-registry.py`,
`plan-merge.py`↔`test-plan-merge.py`, `plan-sign-gate.py`/`.sh`↔`test-plan-sign-gate.py`,
`quarantine.py`↔`test-quarantine.py`, `validate-digest.py`↔`test-validate-digest.py`. `harness.json`
and `team-config.yaml` are config, not code — matrix owes them nothing beyond the manifest-DEVIATION
check already exercised (and accepted) above. `DECISIONS.md`/`DECISIONS-INDEX.md` are exercised by
`test-gen-decisions-index.py`'s live-authority reads (SC-09, mutation-confirmed above). `SKILL.md`
playbook changes are `verify: inspection` (SC-08) — no runner in this repo executes a markdown
playbook, stated as a known gap in the BRIEF's own `## Verification gaps`, not something this gate
can close.

**What this bounds, and what it does not:** every changed unit has a directly-paired test, and five
of the criteria claiming "the check can go red" were independently proven to actually go red under
the specific mutation each names. This is evidence the gate is *not* vacuous for those five surfaces
— it is not evidence that every other assertion in the ~700 new test lines is equally discriminating;
that would need a mutation per assertion, out of scope for this pass.

## 6. Source-read confirmations (Lead framing from dispatch, reasoned not mutated)

- **Lead 1 (release ordering):** `741804ad`'s diff shows the accepted-suspension branch `return 0`s
  strictly *before* the `_reg.release(...)` call; every other return path (rejected suspension,
  terminal verdict, invalid payload) still reaches `release` first, byte-identical to the pre-change
  code, just relocated earlier in the function to compute `_kids` before the accept/reject decision.
  One structural nuance: the post-release "still has live children" refusal changed from
  unconditional (`if _kids:`) to `if _kids and _return_verdict in VERDICTS:` — a lead with live
  children returning neither an accepted `SUSPENDED` nor a `VERDICTS` member now skips the
  D-09-specific message, but `validate()` (called immediately after, line ~1163) still refuses it on
  `VERDICT is <x>; must be exactly one of {...}` (SUSPENDED is not in `VERDICTS`). Exit code is still
  2; only the diagnostic text differs. **Advisory, not gating** — no case exits 0 that should exit 2.
- **Lead 2 (`SUSPENDED` unreachable outside `hook_mode`):** confirmed at source — `VERDICTS =
  {"PASS", "FAIL", "BLOCKED", "ESCALATE"}` (line 35), `SUSPENDED` absent; `hook_mode()`'s own
  suspension branch is the only place that literal string is compared for acceptance. Not re-searched
  across every persona schema file individually (time-bounded); no contradicting hit in the diffed
  files.
- **Lead 3 (query-scoped expiry):** confirmed — `orphan_write`'s `mutator` calls `_expire_where(...,
  lambda claim: _matches(claim, feature=feature))`, `feature` threaded through from the call's own
  argument. Cross-feature sweep not possible from this call site.
- **Lead 4 (duplicated refusal middle sentence):** confirmed present — `check-domain.sh`'s
  `"{X} is canonical, but {agent} holds no live claim for {feature}. Its parent is gone and a
  replacement may already be writing."` and `plan-sign-gate.py`'s identical clause, character-for-
  character. Already reported by SIMPLIFY per dispatch; not elevated — genuinely a backlog-tier
  duplication, not a correctness gap (both refusals are individually correct and independently
  tested, confirmed by SC-11's mutation above).
- **Lead 5 (`--file` fail-open under a live-orphan fixture):** `test-plan-sign-gate.py`'s
  `"NEGATIVE CONTROL: an orphan apply whose --file value is a shell variable is allowed"` runs under
  `_other = [("harness-qa", "other-session", "claude")]` — a live orphan claim for the fixture
  feature held by a different persona/session — confirmed by reading the fixture list at the top of
  the file, not a no-claim fixture. The negative control is meaningful, not vacuous.
- **Lead 6 (plan.yaml ordering):** confirmed at source — `check-domain.sh` line 1529's own comment
  ("THE plan.yaml ROUTE DENIAL, AND IT SITS AHEAD OF EVERY MODE SPLIT BELOW") and the code layout:
  the FEAT-41 route denial executes before the mode split that contains the quarantine branch. D-11
  ordering intact.

## Gate state carried forward unmodified per dispatch
REQ-04 narrowing (D-19/DEC-210), `quarantine.py discard` non-coverage (D-18), SC-12 withdrawal — all
accepted at plan phase, not re-litigated here.
