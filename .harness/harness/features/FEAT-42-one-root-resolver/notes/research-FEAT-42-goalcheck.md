# Goal-check — FEAT-42, review_sha 9d12e3a — cycle 1 2026-08-27, SC-09 re-graded cycle 2 2026-08-27

**BLUF (cycle 2): PASS. All eleven criteria MET.** SC-09 is re-graded from UNMET to MET: my cycle-1
claim that its anchors "land on comments at every sha" was **false at 9d12e3a**, which is the sha the
grade is owed at. At 9d12e3a `:324-330` is the body of `case_19a_argvless_output_is_independent_of_cwd`
and `:935`/`:983` are executable setup lines inside two of `case_24`'s cases. All three enclosing
cases are byte-identical across `ea71a1c..9d12e3a` and all three PASS. The line-anchor fragility is
real and stays as a finding (F-1), but it is a finding, not a grade.

**BLUF (cycle 1, preserved as written — superseded on SC-09 only):** *FAIL on one criterion of
eleven. SC-09 cannot be discharged as written; its three line anchors resolve to comments, not cases,
at every sha in the file's history, and the case family that actually carries the issue-#133 fix had
two assertion literals edited during the cutover. Everything else is MET, including SC-05, which I
re-derived from scratch and which QA had not proven.*

All content claims below were read with `git show 9d12e3a:<path>` or `git grep 9d12e3a`.

## SC-05 — re-derived independently, MET (QA had reported the wrong proof)

QA cited the #556 cwd-parity numbers (203/203 at ONE sha, two working directories). That is a
different proof. SC-05's declared instrument is `check-domain.sh --resolve` over a fixed path list,
BEFORE and AFTER, two shas. I took it.

Method (scripts kept at `scratchpad/sc05/`): two full mirrors of `.claude/skills/harness/bin` — 103
files at `3952814`, 105 at `9d12e3a` — each with `.harness/team-config.yaml` and `.harness/harness.json`
beside it. Whole-directory mirrors, so no case dies on ImportError (trap 1). `team-config.yaml` is
unchanged across the range (`git diff --name-only 3952814 9d12e3a`), so both copies grade the same
domain table. `3952814` is a *stronger* before-state than the `factory_config` cutover alone: it
predates every task.

**Result: 43 verdict lines before, 43 after, 0-line diff.** 10 distinct verdict strings, spanning
owner-granted (`harness-orchestrator | harness-pm`, `harness-qa`, …) and refused (`NOBODY`, 17 of the
43) — so the set is not vacuous in either direction.

**Positive control, because a clean diff is worthless without one:** mutating both `print("NOBODY")`
sites in the OLD mirror to `NOONE-MUTANT` (mutation asserted present on disk: 2 sites, 0 left) moved
**17 of 43 lines** and the harness exited 1. The instrument reddens.

Second, independent half — the suite the allow/deny cases live in, `test-check-domain.py` driven
through `CHECK_DOMAIN_BIN` against each mirror, with `HARNESS_PROJECT_DIR` **not** exported (trap 2;
the suite's `_env` sets both names per case): **203 verdict lines each side, one differing line** —
`#556: a harness_boundary.py in the CWD does not become the gate's resolver`, FAIL before, `ok` after.
That is the intended fix that commit `9d12e3a` exists to make, not a moved verdict. A second FAIL
(`schema/a CRASHING schema module…`) appears identically on BOTH sides: a bin-only-mirror artifact,
not a parity break — the live suite is 203 verdicts, exit 0, zero FAILs.

## SC-09 — RE-GRADED AT CYCLE 2: **MET**

### Cycle-1 reading, preserved

*UNMET, on two grounds: (a) the anchors `:324-330`, `:935`, `:983` land on comment text and "never
named a case at any sha"; (b) the nearest resolvable reading is the `case_19` FAMILY, and it WAS
modified — `case_19b3`/`case_19b4`'s assertion literal went `"IGNORING it"` → `"discarding"` and
`case_19b` gained a fixture copy of `harness_boundary.py`.*

### What is wrong with it

**Ground (a) is false at the sha the grade is owed at.** I read the anchors at `3952814` and
generalised. At `9d12e3a` the file is 1402 lines against 1388 at `ea71a1c`/`3952814`; +14 lines above
the anchors moved the case bodies down onto them. Read with
`git show 9d12e3a:.claude/skills/harness/bin/test-check-plan-routes.py`:

| Anchor at 9d12e3a | Content | Enclosing case |
|---|---|---|
| `:324` | closing `"""` of `case_19`'s docstring | — |
| `:325-330` | `r_root = run(cwd=REPO_ROOT)`, `r_tmp = run(cwd="/tmp")`, the `check(...)` call and its two detail lines | `case_19a_argvless_output_is_independent_of_cwd` (`check` at `:327`) |
| `:935` | `with open(schema_path) as f:` — setup for the enum comparison | `case_24_FINISHED_STATUSES_is_a_subset_of_the_schema_status_enum` (`check` at `:940`) |
| `:983` | `fd = _yaml_project(td, files=...)` in the loop body | `case_24_feature_yaml_{label}_is_checked_not_crashed` (`check` at `:991`, 4 parametrised verdicts) |

**Ground (b) slips scope.** SC-09 says "the cases at `:324-330`, `:935` and `:983`". I graded the
enclosing `case_19` FUNCTION — a family of 15 verdicts at other line numbers. `case_19b3`/`19b4` are
siblings of the anchored case, not the anchored case.

### Modification check — the three enclosing cases only, `ea71a1c..9d12e3a`

Comparison used: `ast.parse` at each sha, walk to the enclosing `case_19`/`case_24` `FunctionDef`,
extract each `check(...)` `Call` node by source span, compare the extracted text.

- `case_19a_argvless_output_is_independent_of_cwd` — `ea71a1c:319` → `9d12e3a:327`, **identical**.
  Its two setup lines are above the first `case_19` diff hunk (offset 105 within the function), so
  they are untouched too.
- `case_24` as a WHOLE function — **byte-identical** across the range (`difflib` over the full
  function source: zero diff lines). That covers both `:935` and `:983` cases outright.
- For contrast, `case_19` as a whole function shows 27 diff lines — all of them in `case_19b`,
  `case_19b3`, `case_19b4`, none within the anchored case.

### Verdicts — `python3 .claude/skills/harness/bin/test-check-plan-routes.py` at 9d12e3a, `ALL PASS`

- `PASS case_19a_argvless_output_is_independent_of_cwd`
- `PASS case_24_FINISHED_STATUSES_is_a_subset_of_the_schema_status_enum`
- `PASS case_24_feature_yaml_{a_sequence,a_bare_scalar,status_is_a_list,a_mapping_with_no_status}_is_checked_not_crashed` (all four)

### Grade and the reading applied

**MET.** Reading: *"the cases at `:324-330`, `:935` and `:983`"* denotes the three test cases those
anchors sit inside at the review sha. All three are unmodified across the feature's range and all
three pass; the leading clause — the no-cwd fallback still holds — is carried by the same
`case_19a…` verdict plus the suite's `ALL PASS`. `case_19b3`/`case_19b4`'s edited literal is a
**finding, not a grade**: it is a sibling case the criterion does not name.

### Anchor rot — kept as a finding either way

The anchors did **not** resolve to the same cases at signature time. At `ea71a1c` (and `3952814`)
`:324-330` was the `(a3)` comment block and `:935`/`:983` were comment lines. What IS stable is the
enclosing case FUNCTION: `:324`/`:330` fall inside `case_19` and `:935`/`:983` inside `case_24` at
both shas. So the criterion resolves to the same two case families at signature time and at review,
and to the precise cases only at review — by a +14-line drift, not by design. A criterion pinned to
line numbers in a file the same feature edits is fragile even when it happens to resolve; it should
name cases.

## SC-10 — MET on the literal reading, with the weakness recorded

Reading applied: the criterion asks for "at least one test case **demonstrated to fail before its
implementation existed**". An `AttributeError` red is such a demonstration — the case ran, it failed,
and it failed because the function did not exist. The second sentence bites only on surviving-mutant
evidence, and none is offered. So: MET. Four named FAIL lines in `receipt-harness-backend-dev-t01.md`
cover `MARKER`, `root_from_script`, `resolve_root`, `root_above`; the receipt's own VERIFY block
proves the mutation applied (`ast`-compared `worktree_owner` body, byte-identical pre/post).

**The weakness, stated rather than graded away:** three of the four reds are
`AttributeError: module has no attribute X`, which an assertion-free test file would produce
byte-identically. Only `root_above` has a behavioural red (`receipt-…-t02.md` case 1: a marker-less
`.harness` decoy beating the real root). SC-02's red rests on the same shape. Filed as an enhancement
to the SC wording, not as a defect in this build.

## Operator's two measurements — re-derived, both confirmed

- **SC-01.** 1669 tracked files at `9d12e3a`; after the four exclusions, 76 in scan; **0 occurrences
  across 0 files.** Presence half: `MARKER`, `resolve_root`, `root_above`, `root_from_script` all
  defined in `harness_boundary.py`. Discriminating: the identical scan at `3952814` gives **21
  occurrences across 17 files**, so the assertion can fail and was red at the widened baseline.
  One number differs from the operator's: I count **19** non-test files under `bin/` with a real
  `^\s*(import|from) harness_boundary` (26 if any mention counts), against the reported 23. Mine is
  the strict-import count; either is above the floor of 16, so the criterion is unaffected.
- **SC-04.** Each symbol checked separately at `9d12e3a` over `bin/` minus `test-*`: `harness_root`,
  `def root(`, `wayfind.root`, `_repo_root_from_script`, `_root_from(`, `_resolve_repo_root` — **all
  0**. Survivors present: `worktree_owner` at `harness_boundary.py:515`,
  `_resolve_main_checkout_root` at `post-merge-sweep.sh:64` (called at `:245`). The two inline chains
  (`harness_yaml.py`, `check-state.sh:22`) are gone — covered by SC-01's repo-wide zero.

## The remaining criteria

Every suite below run by me at `9d12e3a`, exit 0.

- **SC-02** MET — `resolve_root_strict_neither_carries_marker_raises` PASS (11/11 in
  `test-harness-boundary.py`); red in t01 receipt (AttributeError shape — see SC-10).
- **SC-03** MET — `case_1_wayfind_directory_probe_resolves_real_root` PASS, plus
  `root_above_bare_dot_harness_does_not_satisfy`. Genuinely behavioural red in t02.
- **SC-06** MET — `test-dispatch-guard.py` case 11 (exit 2, stderr names the missing field) and
  case 12 (admitted; claim in the declared worktree; main checkout untouched). Red in
  `receipt-main-session-T-18.md` against the `8439002` copy.
- **SC-07** MET, all four — (a)/(c) `case13 release_refuses_ambiguous` ×3 + `case14 remedy_is_absolute`
  ×3; (b) `case12 foreign_session_expired` ×3; (d) `test-validate-digest.py` cases 10 and 11.
  Behavioural reds in `receipt-…-eng-t06.md` and `receipt-main-session-T-17.md`.
  `test-validate-digest.py` re-run twice under the concurrent panel: exit 0, 106 verdicts, 0 FAIL.
- **SC-08** MET — `inflight_registry.py:322` carries #628 on the plan.yaml-overwrite sentence,
  `:335` carries #551 on the verdict-about-a-running-member sentence; pinned by `case6`/`case6b`,
  including the negative (`the plan.yaml-overwrite sentence is NOT tagged #551`). Red in t06.
- **SC-11** MET — `case 12 claim_lands_in_declared_worktree`, both halves; red in T-18.

## Residual findings

| # | Nature | Finding |
|---|---|---|
| F-1 | chore (was: bug, cycle 1) | SC-09's anchors resolve to the intended cases at `9d12e3a` but named comment lines at `ea71a1c`; only a +14-line drift aligned them. Line-anchored criteria in a file the same feature edits should name cases. Not blocking — SC-09 is MET. |
| F-2 | chore | `case_19b3`/`case_19b4` assertion literals changed `"IGNORING it"` → `"discarding"` during T-13 (message moved into `harness_boundary`); property preserved. These are SIBLINGS of the cases SC-09 anchors, so this does not bear on the grade — recorded so the edit is on the record. |
| F-3 | enhancement | Three of SC-10's four reds are `AttributeError` (absence), not behaviour. Future SCs of this shape should require a behavioural red. Same for SC-02. |
| F-4 | chore | `test-check-domain.py`'s `schema/a CRASHING schema module DENIES the write` case fails against a bin-only mirror at BOTH shas — it depends on repo state outside `bin/`. Harmless here; makes mirror-based parity proofs noisier than they need to be. |
| F-5 | chore | T-21's `change_type: test` has no `test_matrix` entry in `.harness/harness.json` (QA's finding, reproduced by reading the file). |
| F-6 | bug | `bash-write-guard.sh` denies redirects/`cp` to the session scratchpad despite an explicit dispatch grant (QA; hit again by me — every file in this proof went through the `Write` tool). |
| F-7 | bug | `gh_cost_log.py`'s counter reads `FACTORY_GH`, not `GH_SYNC_GH`, so `test-gh-sync.py`'s offline guarantee breaks under `HARNESS_GH_COST_LOG=1` (QA). Not in this diff; relates to #676. |
| F-8 | bug | `test-validate-digest.py` is non-hermetic while a dispatch is in flight (this feature's own known list). |
| F-9 | bug | STATE.md's three surfaced-but-unfixed defects: `bash-write-guard`'s angle-bracket refusal, `gh-sync`'s missing per-task finish command, `validate-digest` releasing a claim before refusing the return. |
| F-10 | chore | SC-01's presence floor is stated as "files that import `harness_boundary`" but was measured by mention. Strict imports: 19. Both clear the floor of 16; the counting rule should be written down. |

DEC-174 respected throughout: nothing was edited. Every measurement is a read, a run, or a mutation
inside a scratchpad mirror.
