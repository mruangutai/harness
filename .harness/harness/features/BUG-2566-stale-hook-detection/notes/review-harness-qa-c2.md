# QA gate — BUG-2566-stale-hook-detection, validate cycle 2

Run `2026-11-27-05-validate-validator` · reader `harness-qa` · tested commit
`f4048ad3f9fbe9326d9799485fb97d87547d27be` (registered `review_sha` in `feature.json`; code-identical
to fix commit `71d686d6`, whose only delta is `feature.json`). Receipts are this host's
environment (macOS arm64, bun 1.3.14), not CI.

## BLUF

**PASS. `matrix_ok: true`.** Required floor is `{unit}` (T-01 `bugfix` + `touches_runtime_code`);
the DEC-255 runner exits 0 over 69/69 unit files at the pin, `test-omp-hooks.py` 274 pass / 0 fail.
`typecheck` (SC-08) exits 0. Both run-04 must_fix items are **closed, measured by me**:
M3 now reds 6 of 13 fingerprint cases (7 pass / 6 fail) while the pre-fix tests on the same
mutant stay 13/13 green; a failed `mkfifo` now reds the FIFO case with probe exit 3, while the
pre-fix test on the same perturbation stays green. Carried advisory F-2 (M6) **still survives**
(34/34 green) — low, not gate-failing. SC-05 median 0.063 ms. SC-10 (`uat`) pending on the operator.

## Matrix — read at the pin

- Repository: this harness repo (unbound feature). Commit `f4048ad3f9fbe9326d9799485fb97d87547d27be`.
  Blob `git show f4048ad3:.harness/harness.json` (sha256 `1f4b372d…bab`, identical to 87efcd8a's).
- Change types read from `plan.yaml` (full feature diff 87efcd8a..f4048ad3, P-13):
  - T-01 `bugfix` → `always: []`; `when`: `unit` if `touches_runtime_code` — **true**
    (`.omp/extensions/harness-hooks.ts` changed); `integration` if
    `fix_confined_to_tests_and_contract_docs` — **false** over the full diff (runtime code changed;
    only this cycle's delta is test-only); `__bug_class__` if `match_bug_class` — placeholder, no
    taxonomy entry fires.
  - T-02 `docs` → `always: []`.
- Required: `{unit}`. Also reported: `typecheck` (active; SC-08 rests on it). `integration`,
  `component`, `ui` not required, not run.

| kind | state | cmd | evidence |
|---|---|---|---|
| unit | satisfied | `env -u HARNESS_AGENT_TYPE python3 <pin>/.agents/skills/harness/bin/run-unit-tests.py --kind unit --shard 1/1 --manifest /Users/molchairuangutai/GitHub/harness/.claude/worktrees/harness/BUG-2566-stale-hook-detection/.harness/harness/features/BUG-2566-stale-hook-detection/runs/2026-11-27-05-validate-validator/qa/manifest-unit.json` | exit 0; receipt `runner_exit: 0`, `tested_commit: f4048ad3…`, selected 69 = completed 69, every `returncode` 0; `test-omp-hooks.py (exit 0, 24.11s) 274 pass 0 fail` |
| typecheck | satisfied | `bun run typecheck` (in pin) | `tsc --noEmit -p tsconfig.json`, exit 0 |

Receipt sha256 `32e6f1bb…f97e`, runner-written, untouched, run once. Full runner output appended below.
Managed checkout: `.claude/worktrees/.pins/BUG-2566-stale-hook-detection--2026-11-27-05-validate-validator--harness-qa`
(`pinned-checkout.py add`; HEAD = pin; `git status --porcelain` empty before and after; `bun install --frozen-lockfile` first).

**Candidate vs installed.** The hook enforcing this run is the installed control-plane copy
`/Users/molchairuangutai/GitHub/harness/.omp/extensions/harness-hooks.ts` (sha256 `62c8e121…f418`,
0 occurrences of `staleHookRefusal`; omp 19.2.1 at `~/.bun/bin/omp`). Candidate at the pin: sha256
`eb3f7fc7…857b`. Candidate behaviour is claimed only from tests run at the pin.

## Plan verify blocks, verbatim at the pin

| block | exit | output |
|---|---|---|
| T-01 verify | 0 | 274 pass / 0 fail; `tsc` clean; grep counts hold |
| T-02 verify | 0 | `SPEC 4.2 ok` |
| SC-07 `python3 tests/unit/test-omp-hooks.py` | 0 | 274 pass / 0 fail |
| SC-08 `bun run typecheck` | 0 | clean |
| SC-05 probe (`/tmp/bug2566-c2-sc05.ts`, 20 warm-up + 200 timed calls on the pin's real module) | — | median 0.063 ms, p95 0.076 ms, max 0.103 ms, 0 stale (bound 5 ms) |

## Phase 1 (BRIEF + plan only) vs what exists

Expected per SC-01..05/07/08 as in cycle 1; all present at `tests/unit/omp-hooks.test.ts:2479-2530`
and `:4476-4590`. No new gap; F-2 remains (below).

## SC evidence and fail-first

Pre-fix reproduction, retaken this cycle with the **pin's** test file: `git archive 87efcd8a`
(`87efcd8ae662…5852`) → `/tmp/bug2566-c2-old`, `tests/unit/omp-hooks.test.ts` from f4048ad3 overlaid,
`bun test tests/unit/omp-hooks.test.ts` → **exit 1, 248 pass / 26 fail**, the 26 names identical to
`notes/fail-first-T-01.md`'s RED list. Preserved `-t "BUG-2566 SC-0(2: a stale persona's BLOCKED|3)"`
→ exit 0, 8 pass. Old-tree typecheck → exit 1, `omp-hooks.test.ts(389,38): error TS2554: Expected 1-2
arguments, but got 3.`

| SC | test | fail-first | tier |
|---|---|---|---|
| SC-01 | `:4476`, `:4481`, `:4487`, `:4493`, `:4507` | 87efcd8a: 5/5 red, signature-absent. Semantic: **M3** reds 4/4 change cases; **M1** reds same-size fixed-mtime; FIFO-probe perturbations red (below) | natural (sig-absent) + mutation |
| SC-02 | `:2479` (10 rows), `:2486`, `:2497` (2 rows), carve-out `:2510` (4 rows) | 87efcd8a: all 13 refused rows red semantically; 4 carve-out rows preserved (pass pre- and post-fix) | natural semantic |
| SC-03 | `:2527` (4 rows) | preserved by design; discrimination from cycle-1 mutants M7b/M8 (hook unchanged since, byte-identical `eb3f7fc7…`) | mutation (c1) |
| SC-04 | `:4525-4575` | 87efcd8a: 7/7 red, signature-absent. **M1** reds touch, identical-rewrite, restore (+ SC-01 same-size) — retaken this cycle, 9 pass / 4 fail, exactly the build's list | natural (sig-absent) + mutation |
| SC-05 | `:4577` | 87efcd8a: red, signature-absent; threshold discrimination unshown | natural (sig-absent) |
| SC-07 | `tests/unit/test-omp-hooks.py` | the 26-red run above | natural |
| SC-08 | `bun run typecheck` | 87efcd8a + pin tests: exit 1, TS2554 | natural |
| SC-06, SC-09 | inspection — not QA's | — | — |
| SC-10 | uat — **pending, operator** | — | — |

## Closure of run 04's must_fix (measured; mutants in `/tmp/bug2566-c2-mut`, `git archive f4048ad3`)

Driver `/tmp/bug2566-c2-mut.py`; each mutant restored from saved bytes, final sha256 of hook and test
equal the pin's (`eb3f7fc7…857b`, `7b6fa18e…674e`). Baseline `-t 'BUG-2566 stale hook fingerprint'`: 13 pass / 0 fail.

- **F-1 / M3** (`staleHookRefusal` passes `process.cwd()` for `gateRoot()`): **exit 1, 7 pass / 6 fail** —
  SC-01 append, delete, same-size, FIFO; SC-04 restore, tree-B. Assertion: `Expected to contain: "no
  longer matches .omp/extensions/harness-hooks.ts on disk"`, received `…no longer matches
  ../../var/folders/…/bug2566-…/.omp/extensions/harness-hooks.ts on disk…`. **Control** (P-09): same
  M3 with the pre-fix test file from 8e18c053 → exit 0, 13 pass. Closed; matches the receipt's 7/6 claim.
- **FIFO probe, mkfifo fails** (probe spawns `mkfifo-bug2566-missing`): **exit 1, 0 pass / 1 fail**;
  `:4521` `expect([signal, error, status]).toEqual([null, undefined, 0])` received status **3**.
  **Control**: same perturbation on the 8e18c053 test → exit 0, 1 pass (it passed as the deletion case,
  the defect run 04 named). Boundary probe (P-11): `mkfifo` targets another path → red with status **1**
  (the `lstatSync(H)` throws ENOENT; still red, not exit 3). Closed.
- **M6** (carried F-2; `String(VERDICT ?? DIGEST?.VERDICT).trim().toUpperCase() === "BLOCKED"`):
  `-t BUG-2566` **exit 0, 34 pass / 0 fail — still survives.** Advisory, low, not in must_fix;
  SC-06 pins the exact predicate by inspection.

Logs: `/tmp/bug2566-c2-{base-fp,m3,m3-oldtests,m1,fifo-mkfifo-fails,fifo-mkfifo-fails-oldtests,fifo-other-path,m6,old,old-preserved,oldtsc,unit,t01,sc07}.log`.

## Findings

- **F-2 (carried)** · `tests/unit/omp-hooks.test.ts:2468-2478` · substance · low · T-01. M6 survives
  34/34. Repair: refused rows for `{VERDICT: "blocked"}` and `{DIGEST: {VERDICT: "BLOCKED"}}`.
- O-07 note: the fix-round tests were examined only by my own evidence this round.

## Principles applied

- harness-verification-rules (Absence, subject and mutant): each closure was graded by a flipped
  mutant against a pre-fix-test control on the same mutant, not by green alone.

## Open questions

none

---

## Appendix — full unit runner output (`/tmp/bug2566-c2-unit.log`, tested commit f4048ad3)

```text
shard 1/1: 69 selected files
selected tests/unit/test-answers-provenance.py
selected tests/unit/test-artifact-accessors.py
selected tests/unit/test-broad-catch-census.py
selected tests/unit/test-check-skill-refs.py
selected tests/unit/test-check-state-corpus-rules.py
selected tests/unit/test-check-state-inv26-routing.py
selected tests/unit/test-check-state-inv35.py
selected tests/unit/test-check-state-inv37-local-binding.py
selected tests/unit/test-check-state-shipped-ctx.py
selected tests/unit/test-code-grade.py
selected tests/unit/test-config-shape-matrix.py
selected tests/unit/test-corpus-regression.py
selected tests/unit/test-decision-disposition-schema.py
selected tests/unit/test-digest-dev-skill.py
selected tests/unit/test-digest-projection.py
selected tests/unit/test-digest-record.py
selected tests/unit/test-digest-schemas.py
selected tests/unit/test-expertise-ops.py
selected tests/unit/test-factory-claim-mutation.py
selected tests/unit/test-factory-claim.py
selected tests/unit/test-factory-cli.py
selected tests/unit/test-factory-config.py
selected tests/unit/test-factory-gh.py
selected tests/unit/test-factory-land.py
selected tests/unit/test-factory-workspace.py
selected tests/unit/test-feature-corpus-discovery.py
selected tests/unit/test-feature-corpus-gates.py
selected tests/unit/test-feature-json-budget.py
selected tests/unit/test-feature-json-reader.py
selected tests/unit/test-feature-record.py
selected tests/unit/test-feature-schema-build-entry.py
selected tests/unit/test-fleet-product-config.py
selected tests/unit/test-gate-policy.py
selected tests/unit/test-gen-craft-index.py
selected tests/unit/test-gh-board-item-add.py
selected tests/unit/test-gh-board.py
selected tests/unit/test-gh-cost-log.py
selected tests/unit/test-gh-sync-abandon-sources.py
selected tests/unit/test-gh-sync-build-entry.py
selected tests/unit/test-handoff-done-when.py
selected tests/unit/test-handoff-policy.py
selected tests/unit/test-harness-boundary.py
selected tests/unit/test-harness-config.py
selected tests/unit/test-harness-merge-journal.py
selected tests/unit/test-harness-yaml-corpus.py
selected tests/unit/test-instruction-workflow-gate.py
selected tests/unit/test-integration-shard-validation.py
selected tests/unit/test-issue-types.py
selected tests/unit/test-lead-start-preflight.py
selected tests/unit/test-lead-stop-and-wake.py
selected tests/unit/test-no-distribution.py
selected tests/unit/test-omp-hooks.py
selected tests/unit/test-orchestrator-playbook.py
selected tests/unit/test-plan-depends-on.py
selected tests/unit/test-plan-merge-first-station.py
selected tests/unit/test-plan-merge-union-head.py
selected tests/unit/test-probe-handoff-comprehension.py
selected tests/unit/test-prune-run-evidence.py
selected tests/unit/test-run-identity.py
selected tests/unit/test-runner-unsharded.py
selected tests/unit/test-session-accessor-probe.py
selected tests/unit/test-structure-audit-index.py
selected tests/unit/test-suite-independence.py
selected tests/unit/test-suite-layout.py
selected tests/unit/test-team-catalog.py
selected tests/unit/test-validate-digest-run-pool-lines.py
selected tests/unit/test-wayfind.py
selected tests/unit/test-worktree-state-hooks-rules.py
selected tests/unit/test-worktree-state-rules.py
----- test-answers-provenance.py (exit 0, 0.07s) -----
PASS case_harness_md_names_the_sole_authority
PASS case_orchestrator_canonical_trusts_only_handed_path
PASS case_orchestrator_canonical_forbids_self_authoring
PASS case_orchestrator_canonical_no_longer_claims_the_write_grant
PASS case_skill_playbook_states_the_receiver_rule
PASS case_spec_states_the_provenance_rule
PASS case_spec_no_longer_names_the_orchestrator_as_asker
PASS case_spec_names_the_main_session_as_asker
PASS case_spec_lateral_routing_no_longer_claims_a_second_write
PASS case_skill_lateral_routing_no_longer_claims_a_second_write
PASS case_state_template_reconciled_with_dec_120
PASS case_state_template_no_longer_says_orchestrator_asks

13/13 cases passed.
PASS test-answers-provenance.py
----- test-check-state-corpus-rules.py (exit 0, 0.37s) -----
.............
----------------------------------------------------------------------
Ran 13 tests in 0.002s

OK
PASS test-check-state-corpus-rules.py
----- test-broad-catch-census.py (exit 0, 0.69s) -----
PASS audit_modules_load_from_the_bin_under_test
PASS census counts except-Exception and bare except, and nothing typed
PASS census counts a handler NESTED in a function or class
PASS census of a clean file is zero
PASS a file that does not parse counts as None (its own finding, never a pass)
PASS at the ceiling is clean
PASS below the ceiling is clean (a reduction never fails the census)
PASS above the ceiling names the file and BOTH counts
PASS check-state.py's ceiling is zero
PASS a script absent from the allowlist has a zero ceiling
PASS an unparseable script is its own finding
PASS FEAT-64: factory_decompose.py has a zero ceiling
PASS FEAT-64: feature_schema.py has a zero ceiling
PASS FEAT-64: gh_cost_log.py has a zero ceiling
PASS FEAT-64: handoff_done_when.py has a zero ceiling
PASS FEAT-64: handoff_policy.py has a zero ceiling
PASS FEAT-64: harness_yaml.py has a zero ceiling
PASS FEAT-64: run_identity.py has a zero ceiling
PASS FEAT-64: worktree_terminal.py has a zero ceiling
PASS FEAT-64: board-station.py has a zero ceiling
PASS FEAT-64: check-omp-port.py has a zero ceiling
PASS FEAT-64: check-plan-routes.py has a zero ceiling
PASS FEAT-64: check-skill-weight.py has a zero ceiling
PASS FEAT-64: gh-sync.py has a zero ceiling
PASS FEAT-64: post-merge-sweep.py has a zero ceiling
PASS FEAT-64: run-unit-tests.py has a zero ceiling
PASS FEAT-64: upgrade-config.py has a zero ceiling
PASS FEAT-64: harness_boundary.py's ceiling is exactly two
PASS FEAT-64: a third harness_boundary.py broad catch is a finding against two
PASS FEAT-65: the ceiling table is exactly {harness_boundary.py: 2}
PASS FEAT-65: one broad catch in bash-write-guard.py is a finding against ceiling 0
PASS FEAT-65: bash-write-guard.py carries zero broad catches
PASS FEAT-65: one broad catch in branch-create-gate.py is a finding against ceiling 0
PASS FEAT-65: branch-create-gate.py carries zero broad catches
PASS FEAT-65: one broad catch in check-domain.py is a finding against ceiling 0
PASS FEAT-65: check-domain.py carries zero broad catches
PASS FEAT-65: one broad catch in dispatch-guard.py is a finding against ceiling 0
PASS FEAT-65: dispatch-guard.py carries zero broad catches
PASS FEAT-65: one broad catch in feature-record.py is a finding against ceiling 0
PASS FEAT-65: feature-record.py carries zero broad catches
PASS FEAT-65: one broad catch in gh-close-gate.py is a finding against ceiling 0
PASS FEAT-65: gh-close-gate.py carries zero broad catches
PASS FEAT-65: one broad catch in inflight_registry.py is a finding against ceiling 0
PASS FEAT-65: inflight_registry.py carries zero broad catches
PASS FEAT-65: one broad catch in inject-expertise.py is a finding against ceiling 0
PASS FEAT-65: inject-expertise.py carries zero broad catches
PASS FEAT-65: one broad catch in merge-gate.py is a finding against ceiling 0
PASS FEAT-65: merge-gate.py carries zero broad catches
PASS FEAT-65: one broad catch in plan-sign-gate.py is a finding against ceiling 0
PASS FEAT-65: plan-sign-gate.py carries zero broad catches
PASS FEAT-65: one broad catch in validate-digest.py is a finding against ceiling 0
PASS FEAT-65: validate-digest.py carries zero broad catches
PASS FEAT-65: harness_boundary.py carries exactly its two designed catches
PASS FEAT-65: a third harness_boundary.py catch is a finding naming 3 against 2
PASS an embedded `-c` program's broad catch counts against its carrier
PASS an embedded program with a typed catch adds nothing
PASS a docstring that merely mentions `except Exception` adds nothing
PASS the live branch-create-gate.py config reader carries no broad catch
PASS FEAT-65: the five DEC-234 prologues are byte-identical
PASS FEAT-65: the shared prologue catches exactly (ModuleNotFoundError, ValueError)
PASS FEAT-65: mutating branch-create-gate.py's prologue alone is reported
PASS FEAT-65: mutating gh-close-gate.py's prologue alone is reported
PASS FEAT-65: mutating merge-gate.py's prologue alone is reported
PASS FEAT-65: mutating plan-sign-gate.py's prologue alone is reported
PASS FEAT-65: mutating run-unit-tests.py's prologue alone is reported
PASS spawn resource of `subprocess.run(["git", "-C", root, "show", f"{sh` is git:show
PASS spawn resource of `ctx.spawn(["git", "-C", root, "status", "--porce` is git:status
PASS spawn resource of `ctx.spawn(["git", "worktree", "list", "--porcela` is git:worktree-list
PASS spawn resource of `ctx.spawn([gh_bin, "auth", "status"], capture_ou` is gh:auth
PASS spawn resource of `ctx.spawn([gh_bin, "api", "--paginate", "repos/%` is gh:milestones
PASS spawn resource of `gb.board_stations_for(board, repo, numbers)` is gh:board
PASS spawn resource of `subprocess.run([sys.executable, script, root], t` is None
PASS spawn resource of `read(path)` is None

ALL PASS
PASS test-broad-catch-census.py
----- test-config-shape-matrix.py (exit 0, 0.04s) -----
ok    project harness.json: test_matrix.config.when requires integration on touches_config_shape
ok    project harness.json: _matrix_provenance.config exists
ok    project harness.json: _matrix_provenance.config.added names integration
ok    project harness.json: _matrix_provenance.config is signed DEC-212
ok    project harness.json: bugfix has no unconditional test kind
ok    project harness.json: bugfix predicates are complete and unique
ok    project harness.json: _matrix_provenance.bugfix exists
ok    project harness.json: bugfix provenance records moved and added kinds
ok    project harness.json: bugfix provenance is signed DEC-217
ok    templates/harness.json: bugfix has no unconditional test kind
ok    templates/harness.json: bugfix predicates are complete and unique
ok    templates/harness.json: test_matrix.config.when requires integration on touches_config_shape
ok    DECISIONS.md declares ## DEC-212
ok    DEC-212's heading names touches_config_shape's purpose
ok    DECISIONS.md declares ## DEC-217
ok    DEC-217 defines both bugfix predicates
ok    harness-verification-rules/SKILL.md mentions touches_config_shape

17/17 cases passed.
PASS test-config-shape-matrix.py
----- test-check-state-inv26-routing.py (exit 0, 0.95s) -----
PASS  u.1 each binding is read once, for its own numbers only
PASS  u.1 the bound card is judged on its own board; the owner twin is clean
PASS  u.2 owner sync off: the unbound feature is skipped, the bound one still read
PASS  u.3 a GhError read is CANNOT VERIFY naming the feature and GitHub's answer
PASS  u.3 the healthy owner feature beside it is still compared
PASS  u.4 an unresolvable binding is CANNOT VERIFY naming the feature and the error
PASS  u.4 its numbers never reach the owner read
PASS  u.5 unauthenticated gh: no finding, no read, no binding resolution
PASS  u.6 no recorded issue anywhere: gh is not even probed
PASS test-check-state-inv26-routing.py
----- test-artifact-accessors.py (exit 0, 0.99s) -----
.........................
----------------------------------------------------------------------
Ran 25 tests in 0.650s

OK
PASS test-artifact-accessors.py
----- test-check-state-inv37-local-binding.py (exit 0, 1.28s) -----
PASS  u.1 offline: a fleet-listed bound receipt for factory.repo is clean
PASS  u.1 offline: neither remote boundary is reached
PASS  u.2 offline missing receipt: the receipt finding, never a binding finding
PASS  u.2 offline missing receipt: recovery guidance is selected against factory.repo
PASS  u.2 offline owner repo recorded: the receipt finding, never a binding finding
PASS  u.2 offline owner repo recorded: recovery guidance is selected against factory.repo
PASS  u.2 offline unproven active mirror: the receipt finding, never a binding finding
PASS  u.2 offline unproven active mirror: recovery guidance is selected against factory.repo
PASS  u.3 offline factory.repo='not a repository': still an invalid authoritative binding
PASS  u.3 offline factory.repo=5: still an invalid authoritative binding
PASS  u.3 offline factory.repo='': still an invalid authoritative binding
PASS  u.3 offline factory.repo='org/gone': still an invalid authoritative binding
PASS  u.3 offline factory='org/prod': a non-mapping factory is an invalid binding with no owner fallback and no remote read
PASS  u.3 offline factory=['org/prod']: a non-mapping factory is an invalid binding with no owner fallback and no remote read
PASS  u.4 online: the shared resolver and the remote config read both run
PASS  u.4 online: an unreadable remote config is still an invalid binding
PASS  u.5 offline: an owner receipt beside a bound one is clean, via the resolver
PASS  u.5 offline: a missing owner receipt is still reported
PASS test-check-state-inv37-local-binding.py
----- test-check-state-shipped-ctx.py (exit 0, 1.34s) -----
PASS  precondition: the shipped fixture plan fails the strict loader
PASS  subjects are exactly the unshipped features (missing, unreadable, nested, non-mapping, ambiguous and non-done status stay checked)
PASS  the context records which discovered features shipped
PASS  a strict-invalid shipped plan produces no loading finding
PASS  FEAT-1-shipped: context construction opens only its plan.yaml
PASS  FEAT-2-shipped-quoted: context construction opens only its plan.yaml
PASS  control: an unshipped feature's BRIEF and plan are still read up front
PASS  keep={shipped} leaves no audit subject
PASS  control: keep={unshipped} keeps it
PASS  no shipped feature.json is opened while the context is built
PASS  population entries carry (feature, document, shipped)
PASS  a readable shipped record is in the population, flagged shipped
PASS  an unshipped record is in the population, not flagged shipped
PASS  an unparseable shipped record contributes no claim
PASS  an unparseable shipped record is never reported

0 failure(s)
PASS test-check-state-shipped-ctx.py
----- test-digest-record.py (exit 0, 0.36s) -----
.........
----------------------------------------------------------------------
Ran 9 tests in 0.014s

OK
PASS test-digest-record.py
----- test-digest-dev-skill.py (exit 0, 1.16s) -----
ok   .omp/agents/harness-code-reviewer.md_example0_validates_harness-code-reviewer
ok   .omp/agents/harness-documentor.md_example0_validates_harness-documentor
ok   .omp/agents/harness-orchestrator.md_example0_validates_harness-orchestrator
ok   .omp/agents/harness-pm.md_example0_validates_harness-pm
ok   .omp/agents/harness-qa.md_example0_validates_harness-qa
ok   .omp/agents/harness-security-reviewer.md_example0_validates_harness-security-reviewer
ok   .omp/agents/harness-ui-reviewer.md_example0_validates_harness-ui-reviewer
ok   .omp/agents/harness-visual-designer.md_example0_validates_harness-visual-designer
ok   .claude/skills/harness/references/digest-dev-examples.md_example0_validates_harness-backend-dev
ok   .claude/skills/harness/references/digest-dev-examples.md_example1_validates_harness-dev-ops
ok   .claude/skills/harness/references/digest-dev-examples.md_example2_validates_harness-backend-dev
ok   .claude/skills/harness/references/team-digest-example.md_example0_validates_harness-eng-lead

all checks passed
PASS test-digest-dev-skill.py
----- test-expertise-ops.py (exit 0, 0.85s) -----
PASS  u1: merged Patterns still has 15 entries
PASS  u1: index 6 carries new text
PASS  u1: every other id untouched at its own index
PASS  u2: G-03 absent
PASS  u2: every other id present
PASS  u2: section length one smaller
PASS  u3: code is 10
PASS  u3: line starts MISSING TARGET
PASS  u5: code is 11
PASS  u6: code is 11
PASS  u7: code is 12
PASS  u7: line names the replace plus drop rewrite
PASS  u8: succeeds with final length 15
PASS  u9: code is 8
PASS  u9: line starts CAP EXCEEDED
PASS  u10: compute_union returns non-empty conflicts
PASS  u10: merged Patterns still carries OLD text at index 6
PASS  u11: forward order id sequence is [P-02,P-03,P-04,P-05]
PASS  u11: forward order P-05 carries marker text
PASS  u11: forward order no other entry carries the marker
PASS  u11: reversed order id sequence is [P-02,P-03,P-04,P-05]
PASS  u11: reversed order P-05 carries marker text
PASS  u11: reversed order no other entry carries the marker
PASS  u11: forward and reversed order produce identical merged Patterns
PASS  u12: merged Patterns id sequence is [P-02,P-03,P-05]
PASS  u12: length is 3
PASS  u13: add no section code is 12
PASS  u13: add no section line starts MALFORMED OPS
PASS  u13: add no section line names section
PASS  u13: add no section line names the op's index
PASS  u13: replace no section code is 12
PASS  u13: replace no section line starts MALFORMED OPS
PASS  u13: replace no section line names section
PASS  u13: replace no section line names the op's index
PASS  u13: drop no section code is 12
PASS  u13: drop no section line starts MALFORMED OPS
PASS  u13: drop no section line names section
PASS  u13: drop no section line names the op's index
PASS  u13: replace empty section code is 12
PASS  u13: replace empty section line starts MALFORMED OPS
PASS  u13: replace empty section line names section
PASS  u13: replace empty section line names the op's index
PASS  u13: base mapping unchanged after shape refusals
PASS  u14: digest mapping code is 12
PASS  u14: digest mapping line starts MALFORMED OPS
PASS  u14: digest mapping line names expertise_update
PASS  u14: bare string code is 12
PASS  u14: bare string line starts MALFORMED OPS
PASS  u14: bare string line names expertise_update
PASS  u15: merged mapping still carries the key Gotchas
PASS  u15: Gotchas has zero entries
PASS  u15: Gotchas still in order at its original position
PASS  u15: Patterns untouched
PASS  u16: (a) replace leaves Open at length 1
PASS  u16: (a) replace Open carries the marker
PASS  u16: (b) drop leaves Open at length 0
PASS  u16: (b) drop leaves Open still present
PASS  u17: U+000A entry: code is 12
PASS  u17: U+000A entry: line starts MALFORMED OPS
PASS  u17: U+000B entry: code is 12
PASS  u17: U+000B entry: line starts MALFORMED OPS
PASS  u17: U+000C entry: code is 12
PASS  u17: U+000C entry: line starts MALFORMED OPS
PASS  u17: U+000D entry: code is 12
PASS  u17: U+000D entry: line starts MALFORMED OPS
PASS  u17: U+001C entry: code is 12
PASS  u17: U+001C entry: line starts MALFORMED OPS
PASS  u17: U+001D entry: code is 12
PASS  u17: U+001D entry: line starts MALFORMED OPS
PASS  u17: U+001E entry: code is 12
PASS  u17: U+001E entry: line starts MALFORMED OPS
PASS  u17: U+0085 entry: code is 12
PASS  u17: U+0085 entry: line starts MALFORMED OPS
PASS  u17: U+2028 entry: code is 12
PASS  u17: U+2028 entry: line starts MALFORMED OPS
PASS  u17: U+2029 entry: code is 12
PASS  u17: U+2029 entry: line starts MALFORMED OPS
PASS  u18: U+000A target: code is 12
PASS  u18: U+000A target: line starts MALFORMED OPS
PASS  u18: U+000B target: code is 12
PASS  u18: U+000B target: line starts MALFORMED OPS
PASS  u18: U+000C target: code is 12
PASS  u18: U+000C target: line starts MALFORMED OPS
PASS  u18: U+000D target: code is 12
PASS  u18: U+000D target: line starts MALFORMED OPS
PASS  u18: U+001C target: code is 12
PASS  u18: U+001C target: line starts MALFORMED OPS
PASS  u18: U+001D target: code is 12
PASS  u18: U+001D target: line starts MALFORMED OPS
PASS  u18: U+001E target: code is 12
PASS  u18: U+001E target: line starts MALFORMED OPS
PASS  u18: U+0085 target: code is 12
PASS  u18: U+0085 target: line starts MALFORMED OPS
PASS  u18: U+2028 target: code is 12
PASS  u18: U+2028 target: line starts MALFORMED OPS
PASS  u18: U+2029 target: code is 12
PASS  u18: U+2029 target: line starts MALFORMED OPS
PASS  u19: code is 12
PASS  u19: line starts MALFORMED OPS
PASS  u20: (a) code is 11
PASS  u20: (b) code is 11
PASS  u21: add too-long id: code is 12
PASS  u21: add too-long id: line starts MALFORMED OPS
PASS  u21: add embeds valid id: code is 12
PASS  u21: add embeds valid id: line starts MALFORMED OPS
PASS  u21: replace too-long id: code is 12
PASS  u21: replace too-long id: line starts MALFORMED OPS
PASS  u21: drop too-long id: code is 12
PASS  u21: drop too-long id: line starts MALFORMED OPS
PASS  u22: well-formed add succeeds
PASS  u22: entry present in merged
PASS  u23a: different texts refuse with code 11
PASS  u23a: line starts AMBIGUOUS TARGET
PASS  u23a: line carries section, id and reason tokens
PASS  u23b: identical texts refuse with code 11
PASS  u23b: line starts AMBIGUOUS TARGET
PASS  u23b: line carries section, id and reason tokens
PASS  u23c: no base refuses with code 11
PASS  u23c: line starts AMBIGUOUS TARGET
PASS  u23c: line carries section, id and reason tokens
PASS  u30: first gap is chosen
PASS  u30: past the end
PASS  u30: empty section starts at 01
PASS  u30: other prefixes do not occupy ids
PASS  u30: numeric not textual comparison
PASS  u30: width grows past 99
PASS  u31: craft path
PASS  u31: repository path
PASS  u31: ('harness-backend-dev', 'craft', 'harness') refused with 9
PASS  u31: ('harness-backend-dev', 'repository', None) refused with 9
PASS  u31: ('harness-backend-dev', 'repository', '..') refused with 9
PASS  u31: ('harness-backend-dev', 'repository', 'a/b') refused with 9
PASS  u31: ('harness-backend-dev', 'repository', 'expertise') refused with 9
PASS  u31: ('reviewer', 'craft', None) refused with 9
PASS  u31: ('harness-../x', 'craft', None) refused with 9
PASS  u31: ('harness-backend-dev', 'global', None) refused with 9
PASS  u32: refusals empty
PASS  u32: foreign P-03 kept
PASS  u32: first free id P-02 received the add, then the remapped replace
PASS  u32: mapping exact
PASS  u32: reserved P-02 not reused, first free after it is P-04
PASS  u33: identical add keeps one entry
PASS  u33: no mapping for preserved add
PASS  u34: replace over changed entry refuses CHANGED
PASS  u34: replace of vanished entry refuses DISAPPEARED
PASS  u34: drop over changed entry refuses CHANGED
PASS  u34: drop of vanished entry refuses DISAPPEARED
PASS  u34: replace when original matches applies
PASS  u34: already-applied replace is idempotent
PASS  u34: drop when original matches applies
PASS  u34: refused batch leaves state unchanged
PASS  u34: refusal names persona
PASS  u34: refusal names runtimes
PASS  u34: refusal names destination
PASS  u34: refusal names section
PASS  u34: refusal names target
PASS  u34: refusal names batches
PASS  u35: identical independent replace is refused, not hidden by idempotence
PASS  u35: replace then drop by another caller refused
PASS  u35: the SAME caller may chain edits of one entry
PASS  u36: default cap refusal is 8
PASS  u36: enforce_caps=False defers the cap
PASS  u38: replacement retires the referenced batch
PASS  u38: chains retire step by step
PASS  u38: missing supersession refused with 15
PASS  u38: cross-persona supersession refused with 15
PASS  u38: cross-destination supersession refused with 15
PASS  u38: not-earlier supersession refused with 15
PASS  u38: self supersession refused with 15
PASS  u38: ambiguous supersession refused with 15
PASS  u38: cycle supersession refused with 15
PASS  u38: cycle is named CYCLIC
PASS  u38: double supersession is named AMBIGUOUS
PASS  u39: identity is a sha256 hex digest
PASS  u39: identity ignores the timestamp
PASS  u39: identity covers seq
PASS  u39: identity covers destination
PASS  u39: identity covers ops
PASS  u39: identity covers after_sha256
PASS  u39: identity covers supersedes
PASS  u39: identity covers before_sha256
PASS  u39: identity covers originals
PASS  u39: identity covers persona
PASS  u39: identity covers feature
PASS  u39: identity covers runtime_id
PASS  u39: identity covers parent_id
PASS  u40: receipt failure is refusal 15
PASS  u40: target was persisted before the receipt step
PASS  u40: no receipt exists, so verification must fail closed
PASS  u40: verify without receipt is 15
PASS  u41: final effect of ordered batches, superseded intermediate not required
PASS  u41: drop expects absence
PASS  u41: drop of absent id is satisfied
PASS  u42: disagreement is refusal 15 naming the mismatch
PASS  u43: the chain walks every recorded write back to the first before-state
PASS  u43: a file no recorded write produced has an empty chain
PASS  u43: a no-op write is consumed once, never looped
PASS  u44: no --base anchors on the merge-base with local main, not the feature HEAD
PASS  u44: --base anchors on its merge-base with HEAD
PASS  u44: refs/remotes/origin/HEAD wins over local main
PASS  u44: no default branch refuses 15 NO AUTHORIZED BASE
PASS test-expertise-ops.py
PASS test-expertise-ops.py
----- test-decision-disposition-schema.py (exit 0, 2.29s) -----
PASS absent decisions_affected stays legal (older plans load)
PASS explicit empty list is a legal claim
PASS a mapping block is refused
PASS a null block is refused
PASS a string row is refused
PASS a list row is refused
PASS a row missing dec is refused
PASS a row missing disposition is refused
PASS a row missing clause is refused
PASS a row missing successor is refused
PASS a row missing reason is refused
PASS a sixth key is refused
PASS keep with successor none
PASS amend naming a D id
PASS amend naming a DEC id
PASS amend with successor none is refused
PASS amend with a free-text successor is refused
PASS strike naming a D id
PASS strike naming a DEC id
PASS strike with successor none is refused
PASS strike with a free-text successor is refused
PASS keep naming a successor is refused
PASS an unknown disposition is refused
PASS a title-case disposition is refused
PASS a non-DEC dec is refused
PASS a lowercase dec is refused
PASS an empty clause is refused
PASS a whitespace clause is refused
PASS a non-string clause is refused
PASS a clause keeps its markdown verbatim
PASS an empty reason is refused
PASS a two-line reason is refused
PASS a non-string successor is refused
PASS set-key writes decisions_affected
PASS set-key round-trips every row losslessly
PASS set-key refuses a malformed row
PASS a refused row leaves the plan byte-identical
PASS apply creates a plan carrying rows
PASS apply creation round-trips every row losslessly
PASS re-applying the same rows is a no-op merge
40/40 passed
PASS test-decision-disposition-schema.py
----- test-check-state-inv35.py (exit 0, 3.40s) -----
PASS - multiline double-quoted #217 is silent
PASS - multiline single-quoted #217 is silent
PASS - unquoted notes value reports INV-35 naming #217
PASS test-check-state-inv35.py
----- test-factory-cli.py (exit 0, 0.07s) -----
ok    run(): fn returning normally leaves exit 0
ok    run(): success writes nothing to stdout
ok    run(): success writes nothing to stderr
ok    run(): unhandled KeyError exits 2, not 1
ok    run(): unhandled KeyError leaves stdout empty
ok    run(): unhandled KeyError stderr mentions FACTORY_DEBUG
ok    run(): fn calling sys.exit(1) still exits 1
ok    run(): fn calling sys.exit(3) still exits 3
ok    run(): expected exception produces the preformed line, no prefix duplication
ok    run(): expected exception has no 'unexpected failure' text
ok    run(): expected exception exits 2
ok    run(): FACTORY_DEBUG=1 prints a traceback after the hint line
ok    run(): without FACTORY_DEBUG set, no traceback is printed
ok    message(): renders the five parts in order with the em dash
ok    body(): builds 'what: value — next_step'
ok    the Unicode database names U+2014 EM DASH (source of truth for 'em dash')
ok    body(): the dash emitted is U+2014, not a hyphen or en dash
ok    payload(): writes exactly one stdout line
ok    payload(): that line parses as json.loads
ok    payload(): writes nothing to stderr
ok    payload(): a plain string raises TypeError
ok    nothing_to_do(): writes nothing to stdout
ok    nothing_to_do(): writes to stderr
ok    nothing_to_do(): exits 1 (EXIT_NOTHING), not an error
ok    EXIT_OK == 0
ok    EXIT_NOTHING == 1
ok    EXIT_REFUSED == 2
ok    EXIT_RACE == 3
ok    refuse(): exits EXIT_REFUSED
ok    refuse(): stdout stays empty
ok    refuse(): stderr carries message()
ok    lost_race(): exits EXIT_RACE
ok    lost_race(): stdout stays empty

33/33 checks passed.
PASS test-factory-cli.py
----- test-factory-claim.py (exit 0, 0.94s) -----
ok    (M1) empty ready column exits 1
ok    (M1) stdout is empty
ok    (M2) repo not in fleet exits 1 (no candidate)
ok    (M2) issue_view never called for it
ok    (M3/M6) happy path exits 0
ok    (M3/M6) stdout parses as one JSON payload
ok    (M6) branch is factory/issue-42
ok    (M6) station set to Building exactly once
ok    (M7) feature key equals label value with prefix stripped
ok    (M8) project_items called with a query naming the ready option
ok    (M7) harness-only issue claims normally, exit 0
ok    (M7) feature is null for an issue with no feature: label
ok    (M4) lowest issue number wins
ok    (M5) missing station option exits 2
ok    (M5) no board read happened
ok    (M5) stderr names the missing option, the field and the fleet file
ok    (C1) exit 1
ok    (C1) stdout is EMPTY
ok    (C1) stderr carries 'no work available'
ok    (C2) whole stdout parses as one JSON object
ok    (C2) exit 0
ok    (C2) issue_view's requested fields include "state"
ok    (C3) exit 2, not 1
ok    (C3) stdout empty
ok    (C3) exactly one stderr line
ok    (C3) stderr names a concrete value
ok    (R1) exit 0 with payload
ok    (R1) label/assign/field_set all happen AFTER create_ref
ok    (R2 route1) exit 1
ok    (R2 route1) stdout empty
ok    (R2 route1) zero mutating calls
ok    (R2 route1) 'no claimable work' present, 'no work available' absent
ok    (R2 route1) names all three issue numbers with ref-already-exists
ok    (R2 route2) exit 1
ok    (R2 route2) stdout empty
ok    (R2 route2) zero mutating calls
ok    (R2 route2) no create_ref attempted at all
ok    (R2 route2) 'no claimable work' present, 'no work available' absent
ok    (R2) route1 and route2 stderr are NOT equal
ok    (R3 closed) exits 0 and claims #92
ok    (R3 already-labelled) exits 0 and claims #92
ok    (R3 already-assigned) exits 0 and claims #92
ok    (R3 ref-refused) exits 0 and claims #92
ok    (R4) --issue lost race exits 3
ok    (R4) zero mutating calls
ok    (R4) --issue resolves via issue_board_item_id EXACTLY ONCE, zero project_items calls
ok    (R4) issue_board_item_id called with the fleet repo entry's own name, then args.issue, then the board number
ok    (R4) --issue self-owned re-entry exits 0
ok    (R4) self-owned re-entry payload
ok    (R4) self-owned re-entry never calls create_ref
ok    (R4) self-owned re-entry resolves via issue_board_item_id, zero project_items calls
ok    (R4) same issue in POLL mode is skipped (exit 1), not re-emitted
ok    (R5) exits 2, not 3
ok    (R5) loop stopped — #66 was never reached (issue_view called once)
ok    (R6a) --issue on a closed, unowned issue exits 2 (refused)
ok    (R6a) zero mutating calls
ok    (R6a) zero create_ref calls
ok    (R6a) stdout empty
ok    (R6a) stderr names the issue
ok    (R6b) --issue on a closed, self-owned issue exits 2 (refused), NOT re-emitted at exit 0
ok    (R6b) zero mutating calls
ok    (R6b) zero create_ref calls
ok    (R6b) stdout empty
ok    (R7) --issue found on no fleet repo exits 2 (refused)
ok    (R7) zero mutating calls
ok    (R7) stderr names the issue
ok    (R8) poll mode calls project_items EXACTLY ONCE
ok    (R8) poll query names the ready station and is:open, unchanged
ok    (R8) poll mode never calls issue_board_item_id
ok    factory_claim reads default_branch from the fleet entry before any clone exists
ok    (B1) exits 0
ok    (B1) create_ref called EXACTLY ONCE, with the CLEAR candidate (#720)
ok    (B1) blocked candidate's skip reason on stderr, distinct from labelled/assigned reasons
ok    (B2) exits 1
ok    (B2) zero mutating calls, including create_ref
ok    (B2) 'no claimable work' present, 'no work available' absent
ok    (B3) all blockers closed: candidate IS claimed
ok    (B4) mixed: skipped, create_ref called once with the clear candidate (#721)
ok    (B4) stderr names the LAST (open) blocker: T-04 / #603
ok    (B4) same fixture, last blocker closed too: candidate IS now claimed
ok    (B5) unresolvable blocker: skipped, not claimed
ok    (B5) distinct stderr reason naming T-99
ok    (B5-bis) edge (i): lost task identity is BLOCKED, not claimed
ok    (B5-bis) edge (i) reason distinct from open-blocker and unresolvable-blocker reasons
ok    (B5-ter) absent features root: the reason names the absolute path that was tried
ok    (B5-ter) absent features root: the reason does not use the edge (i) text
ok    (B5-ter) absent features root: nothing claimed, zero mutating calls, stdout empty
ok    (B5-ter) plan present, task id absent: still the edge (i) text
ok    (B6) feature: null claims normally
ok    (B6) no plan file was consulted for it
ok    (B7) fresh --issue on a blocked issue exits 2 (never 3, never 0)
ok    (B7) zero mutating calls and no create_ref
ok    (B7) stderr names the blocking T-02
ok    (B7) --issue on an issue this agent already owns exits 0, gate never blocks re-entry
ok    (D0) load_plan RAISES on the dangling fixture (T-02 depends_on T-99, absent)
ok    (D0) load_plan RETURNS on the paired legal fixture (T-02 depends_on T-01, present)
ok    (Da) blocker-gate reason a caller receives names BOTH T-02 and T-99
ok    (Da) blocker-gate reason no longer carries the missing-or-unparseable wording (factory_claim.py:193-196)
ok    (Db) blocker-gate over the legal fixture is CLEAR, exactly (B3)'s verdict
ok    (Dc) poll does not crash: exit 0, #790 claimed despite #780's dangling plan
ok    (Dc) #790's create_ref is the only mutating call across the whole poll
ok    (Dc) no traceback anywhere on stderr
ok    (X) sc13b fixture: exits 1, nothing claimable
ok    (X) sc13b fixture: stdout empty
ok    (X) sc13b fixture: zero mutating calls
ok    (X) sc13b fixture: exactly eight skip lines fired (fixture didn't silently short-circuit)
ok    (X) sc13b fixture: the seven skip lines are for exactly issues 901..907
ok    (X) SC-13(b): all seven skip reasons are pairwise distinct after normalising every embedded issue number, not just a leading one
ok    (X) SC-13(b) bonus: still pairwise distinct after ALSO normalising T-NN task ids
ok    (P1) poll mode queries both boards, not just one
ok    (P1) board A's query is built from board A's own field and ready option
ok    (P1) board B's query is built from board B's own FIELD, not board A's — the ready COLUMN is now the same on both, since FEAT-41 T-01 mandates the names
ok    (P2) claims #200 on repository A, exit 0
ok    (P2) exactly one project_field_set call, addressed to A's board and never B's
ok    (P3) exits 2 (refused)
ok    (P3) refusal names board B's board number
ok    (P3) refusal does NOT name board A's board number
ok    (P4) --repo REPO exits 1, no work on that repo's board
ok    (P4) --repo filters the served set: every board read names A's board, none names B's
ok    (P5) claims #300 exactly once, exit 0
ok    (P5) both fleet entries query the shared board (two project_items calls recorded)
ok    (P5) issue_view runs exactly once for #300 — the duplicate never entered the candidate loop
ok    (P5) exactly one project_field_set call despite the duplicate
ok    (P6) SC-13: --repo on the sole served repository's empty ready station: stdout is empty
ok    (P6) SC-13: stderr carries 'no work available'
ok    (P6) SC-13: exit code is EXIT_NOTHING (1), not a silent 0
ok    BUG-1290 5a: served non-harness repository reaches its own segment's blocker verdict, not no_plan
ok    BUG-1290 5b: same feature id on two repositories resolves per-segment, no cache bleed
ok    BUG-1290 5c: absent segment root still refuses via no_plan, naming that segment's own path
ok    BUG-1290 5d: owner-qualified name ending in harness resolves to .harness/harness/features
ok    BUG-1290 5e: factory_claim exposes no FEATURES_ROOT attribute
ok    BUG-1290 5f: the owner-strip derivation lives in exactly one place, factory_config.py
ok    BUG-1290 5g: issue-map-cache mutation fails case 5b itself on its own specific observable

133/133 checks passed.
PASS test-factory-claim.py
----- test-factory-gh.py (exit 0, 0.11s) -----
ok    run_gh: raises GhError when the binary is missing
ok    run_gh: missing-binary message carries a concrete value
ok    run_gh: raises GhError on non-zero exit
ok    run_gh: message carries the captured stderr
ok    run_gh: GhError message has an em dash, no class name, no traceback
ok    run_gh: FACTORY_GH set AFTER import changes the binary used
ok    run_gh: stdin is closed (DEVNULL)
ok    preflight: returns None on a zero exit
ok    preflight: runs `auth status`
ok    preflight: raises GhError telling the operator to run gh auth login
ok    create_issue: returns the number parsed from the URL
ok    create_issue: passes repo verbatim
ok    create_issue: passes every label
ok    create_issue: unparseable output raises GhError, never returns a default
ok    ensure_labels: raises GhError instead of swallowing a non-zero exit
ok    ensure_labels: stops at the failing label, does not run the remaining ones
ok    ensure_labels: each call uses --force
ok    ensure_labels: passes repo verbatim
ok    project_field_set: made no more and no fewer than TWO calls (graphql, then item-edit)
ok    project_field_set: first call is gh api graphql
ok    project_field_set: second call is gh project item-edit
ok    project_field_set: resolves the field id
ok    project_field_set: resolves the option id
ok    project_field_set: query selects exactly one field by name
ok    project_field_set: query has no plural field-connection selection
ok    project_field_set: query carries no connection argument (first:/last:)
ok    project_field_set: raises GhError naming the option when it is not offered
ok    project_field_set: option-not-offered case makes ZERO item-edit calls
ok    project_field_set: option-not-offered message is the D-04-frozen rendered string
ok    project_field_set: option-not-offered message carries no generic subcommand fallback
ok    project_field_set (--project-id case): did not raise
ok    project_field_set: exactly one item-edit call was made
ok    project_field_set: --project-id is present in the item-edit argv
ok    project_field_set: --project-id carries the GraphQL node id, NOT the bare board number
ok    project_field_set: a non-diagnosable transport failure raises GhError
ok    project_field_set: a transport failure makes ZERO item-edit calls (never falls back to the bare number)
ok    project_field_set: transport-failure message names owner + project number
ok    project_field_set: transport-failure message never carries the generic subcommand fallback
ok    unknown owner: raises GhError naming the owner
ok    unknown owner: makes ZERO item-edit calls
ok    unknown owner: message carries no generic subcommand fallback
ok    organization (exit-1 unreachable): raises GhError naming the owner
ok    organization (exit-1 unreachable): makes ZERO item-edit calls
ok    organization (exit-1 unreachable): message differs from the unknown-owner message
ok    organization (exit-1 unreachable): message carries no generic subcommand fallback
ok    organization (exit-0 reachable): raises GhError naming the owner
ok    organization (exit-0 reachable): makes ZERO item-edit calls
ok    organization (exit-0 reachable): message differs from the unknown-owner message
ok    organization (exit-0 reachable): message carries no generic subcommand fallback
ok    board absent: raises GhError naming owner + project number
ok    board absent: makes ZERO item-edit calls
ok    board absent: message differs from the organization message
ok    board absent: message differs from the unknown-owner message
ok    board absent: message carries no generic subcommand fallback
ok    field not single-select (empty dict): raises the SAME field-not-found error as the field-absent case
ok    field not single-select: makes ZERO item-edit calls
ok    field not single-select: message carries no generic subcommand fallback
ok    issue_view: passes repo verbatim and comma-joins fields
ok    add_label: passes repo verbatim
ok    assign: passes repo and login verbatim
ok    project_item_add: returns the item id
ok    project_item_add: passes owner verbatim
ok    create_ref: returns True on a zero exit
ok    create_ref: returns False WITHOUT raising on the measured conflict
ok    create_ref: raises GhError on a failure carrying neither token (auth failure)
ok    create_ref: a 422 WITHOUT 'already exists' raises rather than reporting a lost race
ok    project_items: returns the items list
ok    project_items: omits --query when none is given
ok    project_items: passes the query string verbatim when given
ok    project_items: raises GhError when totalCount exceeds the returned items
ok    project_items: a missing totalCount raises rather than defaulting to 0
ok    project_item_stations: made exactly ONE gh api graphql call
ok    project_item_stations: a stationed item maps to its station string
ok    project_item_stations: a stationed item's content carries the issue number and repo
ok    project_item_stations: a null fieldValueByName item maps to station None and is present in the output
ok    project_item_stations: two-page response makes exactly TWO calls
ok    project_item_stations: the second call carries the first page's endCursor
ok    project_item_stations: two-page response is fully accumulated (3 items)
ok    project_item_stations: the second page's items appear in the output
ok    project_item_stations: accumulated count below totalCount raises GhError
ok    project_item_stations: truncation message names both totals
ok    project_item_stations: a response missing totalCount raises GhError, never defaults it to 0
ok    project_item_stations: a null user (organization-owned board) raises GhError, never returns an empty list
ok    project_item_stations: argv passes owner/number/field/cursor as -F and query as -f
ok    project_item_stations: query has no widened plural fieldValues connection
ok    issue_board_item_id: made exactly ONE call
ok    issue_board_item_id: that one call is gh api graphql
ok    issue_board_item_id: ZERO calls hit project item-list
ok    issue_board_item_id: argv carries the issue number
ok    issue_board_item_id: argv carries both repository halves
ok    issue_board_item_id: returns the matching node's id when project.number == board_number
ok    issue_board_item_id: _ISSUE_ITEM_QUERY's issue(...) selection takes exactly the argument {number} — no state/filter argument of any spelling
ok    issue_board_item_id: an item on a DIFFERENT project number returns None, does not raise
ok    issue_board_item_id: empty nodes list with totalCount 0 returns None, does not raise
ok    issue_board_item_id: repository.issue explicitly null returns None, does not raise
ok    issue_board_item_id: repository dict with NO 'issue' key at all RAISES (distinct from the explicit-null case above)
ok    issue_board_item_id: issue with no 'projectItems' key RAISES
ok    issue_board_item_id: projectItems.nodes not a list RAISES
ok    issue_board_item_id: projectItems with no 'totalCount' key RAISES (never defaults to 0)
ok    issue_board_item_id: a string totalCount raises GhError, NOT a bare TypeError
ok    issue_board_item_id: totalCount 3 with one node RAISES
ok    issue_board_item_id: truncation message names the totals
ok    issue_board_item_id: a node missing 'id' RAISES
ok    issue_board_item_id: a node missing 'project' RAISES
ok    issue_board_item_id: a null repository RAISES, naming the repository, not the generic graphql-call-failed text
ok    issue_board_item_id: a non-diagnosable transport failure raises GhError
ok    issue_board_item_id: transport-failure message names the repo and issue number
ok    issue_board_item_id: a malformed repository string raises before any call
ok    issue_board_item_id: malformed-repository message names the repository
ok    project_field_options: returns the option names
ok    project_field_options: raises GhError naming the absent field
ok    project_field_options: absent-field message is the D-04-frozen rendered string
ok    project_field_options: absent-field message carries no generic subcommand fallback
ok    project_resolve: returns the project id and title when it exists
ok    project_resolve: sends owner and number as GraphQL variables
ok    project_resolve: an absent project (owner resolves, projectV2 null) returns None, raises nothing
ok    project_resolve: an unresolvable owner raises GhError naming the owner
ok    project_resolve: an organization-owned login raises GhError with the organization message
ok    project_resolve: the organization case sends no mutation
ok    project_resolve: organization and owner-absent messages differ
ok    project_create: returns the new project's id and number
ok    project_create: first call resolves the owner id
ok    project_create: second call sends the resolved owner id and the title as variables
ok    project_create: second call's query mutates createProjectV2
ok    project_create: an unresolvable owner raises GhError before any create call
ok    project_create: a null projectV2 in the create response raises GhError naming owner+title
ok    project_link_repository: returns None on success
ok    project_link_repository: resolves owner/name split from the repo string
ok    project_link_repository: second call sends the resolved project and repository ids
ok    project_link_repository: an unresolvable repository raises GhError before linking
ok    project_link_repository: an already-linked failure returns None, raises nothing
ok    project_link_repository: an UNRELATED link failure (not already-linked) still raises
ok    project_single_select_create: returns the new field's node id
ok    project_single_select_create: sends every option in the given order
ok    project_single_select_create: sends color: GRAY and description: "" for every option (GitHub rejects the mutation when either is omitted)
ok    project_single_select_create: sends the field name and project id as variables
ok    project_single_select_create: a null projectV2Field raises GhError naming the field
ok    project_single_select_extend: returns None
ok    project_single_select_extend: sends EVERY option — existing first, then additions — in the exact order given
ok    project_single_select_extend: sends color: GRAY and description: "" explicitly
ok    project_single_select_extend: sends the field id as a variable, not the project id
ok    project_single_select_extend: mutates updateProjectV2Field, never createProjectV2Field
ok    project_single_select_extend: a null projectV2Field raises GhError
ok    project_workflows: returns one dict per workflow with name/enabled/number
ok    project_workflows: sends owner and number as GraphQL variables
ok    project_workflows (user null): raises GhError rather than returning []
ok    project_workflows (projectV2 null): raises GhError rather than returning []
ok    project_workflows (workflows null): raises GhError rather than returning []
ok    default_branch_sha: returns the sha
ok    default_branch_sha: hits the ref/heads path
ok    file_at_ref: returns the decoded file body
ok    file_at_ref: hits the contents path with the ref
ok    file_at_ref: a missing file raises GhError naming repo, path and ref
ok    file_at_ref: undecodable content raises rather than returning empty
ok    file_at_ref: non-alphabet character in otherwise valid-length base64 raises
ok    file_at_ref: decodes GitHub's line-wrapped base64 content
ok    file_at_ref: an absent content field raises rather than defaulting
ok    delete_ref: hits the DELETE endpoint for the ref name
ok    internal_id: returns an int parsed from the output
ok    internal_id: the recorded argv's first element is never 'issue' (never issue view)
ok    internal_id: hits the REST path repos/<owner/name>/issues/<n> with --jq .id
ok    attach_sub_issue: argv path ends in /sub_issues
ok    blocked_by: argv path ends in /dependencies/blocked_by
ok    edge functions: all three route through run_gh and launch nothing of their own
ok    edge functions: every launch uses the call-time FACTORY_GH binary
ok    run_gh: writes nothing to stdout on success
ok    create_issue: writes nothing to stdout
ok    ensure_labels: writes nothing to stdout
ok    project_items: writes nothing to stdout
ok    project_field_options: writes nothing to stdout
ok    internal_id: writes nothing to stdout
ok    attach_sub_issue: writes nothing to stdout
ok    blocked_by: writes nothing to stdout
ok    create_ref: writes nothing to stdout on success
ok    create_ref: writes nothing to stdout on the measured conflict
ok    project_field_set: writes nothing to stdout
ok    issue_view: writes nothing to stdout
ok    add_label: writes nothing to stdout
ok    assign: writes nothing to stdout
ok    project_item_add: writes nothing to stdout
ok    default_branch_sha: writes nothing to stdout
ok    delete_ref: writes nothing to stdout
ok    run_gh: rate-limit failure raises GhError
ok    run_gh: budget message names GraphQL
ok    run_gh: budget message carries used and limit points
ok    run_gh: budget message carries the reset UTC ISO 8601 timestamp
ok    run_gh: budget remedy names REST's own usage
ok    run_gh: original gh stderr is preserved as detail
ok    run_gh: queried rate_limit exactly once, after the failing call
ok    run_gh: unrelated exit-1 raises a plain GhError, not a budget error
ok    run_gh: unrelated failure never contains the GraphQL budget headline
ok    run_gh: unrelated failure message preserves the original gh text
ok    run_gh: a rate-limit failure whose budget read also fails still raises GhError
ok    run_gh: budget-read failure names its own message, not the original rate-limit text
ok    run_gh: budget-read failure preserves the original rate-limit stderr as detail
ok    issue_stations: an empty number set makes ZERO gh calls
ok    issue_stations: an empty number set returns an empty map, not None
ok    issue_stations: four issues cost exactly ONE gh call
ok    issue_stations: an issue on the board carries its station verbatim
ok    issue_stations: an issue on the board with no field value is PRESENT with None
ok    issue_stations: a card on a DIFFERENT project is not answered for this one
ok    issue_stations: an issue GraphQL resolves null is absent, not an error
ok    issue_stations: 51 issues take exactly TWO calls at a batch of 50
ok    issue_stations: both batches' results are merged, none dropped
ok    issue_stations: a null repository RAISES rather than reporting an empty board
ok    issue_stations: an issue whose project items are truncated RAISES, never reports absent
ok    GhError invariant: at least one case was collected
ok    GhError invariant holds for 'gh not found: gh — install gh, or point FACTORY_GH at its pa'
ok    GhError invariant holds for 'gh issue list failed: issue list — permission denied'
ok    GhError invariant holds for 'gh auth status failed: gh — run `gh auth login` to authentic'
ok    GhError invariant holds for 'gh issue create returned no issue number: o/r — output did n'
ok    GhError invariant holds for 'gh label create failed: o/r — already frozen'
ok    GhError invariant holds for 'project field option not found: NotAnOption — field Station '
ok    GhError invariant holds for 'gh graphql call failed: owner project 3 — re-run after check'
ok    GhError invariant holds for 'project owner not found: acmeuser — check the owner login'
ok    GhError invariant holds for 'organization-owned board not supported: acmeuser — run again'
ok    GhError invariant holds for 'organization-owned board not supported: acmeuser — run again'
ok    GhError invariant holds for 'project not found: acmeuser project 3 — check the board numb'
ok    GhError invariant holds for 'project field not found: Station — field-list for owner proj'
ok    GhError invariant holds for 'gh api -X failed: o/r — gh: authentication required'
ok    GhError invariant holds for 'gh api -X failed: o/r — gh: Invalid request (HTTP 422)'
ok    GhError invariant holds for 'project item-list truncated: o project 3: totalCount=5 items'
ok    GhError invariant holds for 'project item-list response has no totalCount: o project 3 — '
ok    GhError invariant holds for 'project item stations truncated: owner project 3: totalCount'
ok    GhError invariant holds for 'project item stations response has no totalCount: owner proj'
ok    GhError invariant holds for 'project item stations unreadable: acmeorg project 3: user is'
ok    GhError invariant holds for 'gh graphql call failed: acme/widget issue 42 — re-run after '
ok    GhError invariant holds for 'gh graphql call failed: acme/widget issue 42 — re-run after '
ok    GhError invariant holds for 'gh graphql call failed: acme/widget issue 42 — re-run after '
ok    GhError invariant holds for 'issue projectItems missing totalCount: acme/widget issue 42 '
ok    GhError invariant holds for 'issue projectItems totalCount is not an integer: acme/widget'
ok    GhError invariant holds for 'issue projectItems truncated: acme/widget issue 42: totalCou'
ok    GhError invariant holds for 'issue projectItems node has unrecognised shape: acme/widget '
ok    GhError invariant holds for 'issue projectItems node has unrecognised shape: acme/widget '
ok    GhError invariant holds for 'repository not found: acme/widget — check the repository nam'
ok    GhError invariant holds for 'gh graphql call failed: acme/widget issue 42 — re-run after '
ok    GhError invariant holds for 'malformed repository: not-a-valid-repo — expected owner/name'
ok    GhError invariant holds for 'project field not found: NoSuchField — field-list for owner '
ok    GhError invariant holds for 'project owner not found: nosuchowner — check the owner login'
ok    GhError invariant holds for 'organization-owned board not supported: acmeorg — run agains'
ok    GhError invariant holds for 'project owner not found: nosuchowner — check the owner login'
ok    GhError invariant holds for 'project not created: owner: t — createProjectV2 returned no '
ok    GhError invariant holds for 'repository not found: owner/nope — check the repository name'
ok    GhError invariant holds for 'gh api graphql failed: api graphql — gh: authentication requ'
ok    GhError invariant holds for 'project field not created: Status — createProjectV2Field ret'
ok    GhError invariant holds for 'project field not updated: PVT_1 field PVTSSF_1 — updateProj'
ok    GhError invariant holds for 'project owner not found: owner — check the owner login'
ok    GhError invariant holds for 'project not found: owner project 3 — check the board number'
ok    GhError invariant holds for 'project workflows unreadable: owner project 3 — unexpected G'
ok    GhError invariant holds for 'gh api contents failed: o/r missing/file.txt@release-branch '
ok    GhError invariant holds for 'file content could not be decoded: o/r path/x@main — gh retu'
ok    GhError invariant holds for 'file content could not be decoded: o/r path/lax@main — gh re'
ok    GhError invariant holds for 'file content missing from response: o/r adir@main — gh retur'
ok    GhError invariant holds for 'GraphQL budget exhausted: 5000 of 5000 points used, resets a'
ok    GhError invariant holds for 'gh issue view failed: o/nope — could not resolve to a Reposi'
ok    GhError invariant holds for 'gh reported a rate limit and the budget could not be read: a'
ok    GhError invariant holds for 'issue stations unreadable: o/r: repository is null — check t'
ok    GhError invariant holds for 'issue project items truncated: o/r#5 — the issue is on more '

258/258 checks passed.
ok    FEAT-64 run_gh: a launch PermissionError is GhError
ok    FEAT-64 run_gh: the launch failure is chained as the cause
ok    FEAT-64 run_gh: a non-JSON body under json_out is GhError
ok    FEAT-64 run_gh: the decode failure names the argv and keeps the stdout
ok    FEAT-64 run_gh: an unrelated RuntimeError escapes
ok    T-01 GhResult: fields are exactly status, stdout, stderr, value, error
ok    T-01 GhResult: ok is derived as error is None
ok    T-01 GhResult: frozen
ok    T-01 try_gh success: ok, real status and raw streams retained
ok    T-01 try_gh success: value is stripped stdout, error None
ok    T-01 try_gh: writes nothing to stdout
ok    T-01 try_gh: one launch
ok    T-01 try_gh json: value is the parsed document
ok    T-01 try_gh json: JSON null is a successful None value, positional json_out
ok    T-01 try_gh nonzero: never raises; not ok with status and original streams
ok    T-01 try_gh nonzero: error is the GhError run_gh raises
ok    T-01 try_gh nonzero: no retry
ok    T-01 try_gh missing binary: status None, empty streams, no value
ok    T-01 try_gh missing binary: GhError with argv, status None and the launch error chained
ok    T-01 try_gh permission: status None, empty streams, no value
ok    T-01 try_gh permission: GhError with argv, status None and the launch error chained
ok    T-01 try_gh general OSError: status None, empty streams, no value
ok    T-01 try_gh general OSError: GhError with argv, status None and the launch error chained
ok    T-01 try_gh malformed JSON: status zero yet not ok, streams kept, value None
ok    T-01 try_gh malformed JSON: typed GhError chained from the strict parser
ok    T-01 run_gh malformed JSON: raises GhError
ok    T-01 try_gh duplicate key JSON: status zero yet not ok, streams kept, value None
ok    T-01 try_gh duplicate key JSON: typed GhError chained from the strict parser
ok    T-01 run_gh duplicate key JSON: raises GhError
ok    T-01 try_gh nonfinite JSON: status zero yet not ok, streams kept, value None
ok    T-01 try_gh nonfinite JSON: typed GhError chained from the strict parser
ok    T-01 run_gh nonfinite JSON: raises GhError
ok    T-01 launch_gh: an unrelated RuntimeError escapes, never a GhError
ok    T-01 try_gh: an unrelated RuntimeError escapes, never a GhError
ok    T-01 input: text input reaches the process from launch_gh, try_gh and run_gh
ok    T-01 input: text input is never combined with a stdin argument
ok    T-01 input: no input closes stdin through DEVNULL and passes no input
ok    T-01 input: every launch captures text output
ok    T-01 launch_gh: returns the completed process uninterpreted (nonzero, no JSON parse)
ok    T-01 launch_gh: FACTORY_GH resolved at call time
ok    T-01 launch_gh: a missing binary is GhError with status None and the cause chained
ok    T-01 try_gh: FACTORY_GH set after import is the binary launched
ok    T-01 try_gh rate limit: the process status stays authoritative beside the diagnosis
ok    T-01 try_gh rate limit: the GraphQL budget diagnosis is kept
ok    T-01 try_gh rate limit: one budget read and no retry of the failed operation
ok    T-01 try_gh rate limit: the budget query's own failure never recurses
ok    T-01 issue_number_from_url: a complete issue URL yields its positive number
ok    T-01 issue_number_from_url malformed: GhError with argv and the original output
ok    T-01 issue_number_from_url zero: GhError with argv and the original output
ok    T-01 issue_number_from_url zero padded: GhError with argv and the original output
ok    T-01 issue_number_from_url non-ASCII digits: GhError with argv and the original output
ok    T-01 issue_number_from_url oversized: GhError with argv and the original output
ok    T-01 issue_number_from_url trailing junk: GhError with argv and the original output
ok    T-01 issue_number_from_url negative: GhError with argv and the original output
ok    T-01 issue_number_from_url pull URL: GhError with argv and the original output
ok    T-01 issue_number_from_url no scheme: GhError with argv and the original output
ok    T-01 issue_number_from_url empty authority, query char: GhError with argv and the original output
ok    T-01 issue_number_from_url empty authority: GhError with argv and the original output
ok    T-01 issue_number_from_url authority is userinfo only: GhError with argv and the original output
ok    T-01 issue_number_from_url authority is a fragment: GhError with argv and the original output
ok    T-01 issue_number_from_url authority is a bare port: GhError with argv and the original output
ok    T-01 issue_number_from_url bare path: GhError with argv and the original output
ok    T-01 issue_number_from_url extra segment: GhError with argv and the original output
ok    T-01 issue_number_from_url two lines: GhError with argv and the original output
ok    T-01 issue_number_from_url owner carries a query: GhError with argv and the original output
ok    T-01 issue_number_from_url owner carries a fragment: GhError with argv and the original output
ok    T-01 issue_number_from_url repo carries a query: GhError with argv and the original output
ok    T-01 issue_number_from_url repo carries a fragment: GhError with argv and the original output
ok    T-01 issue_number_from_url owner carries a dot: GhError with argv and the original output
ok    T-01 issue_number_from_url owner carries a percent escape: GhError with argv and the original output
ok    T-01 issue_number_from_url owner carries userinfo: GhError with argv and the original output
ok    T-01 issue_number_from_url repo is a dot segment: GhError with argv and the original output
ok    T-01 issue_number_from_url repo is a dot-dot segment: GhError with argv and the original output
ok    T-01 issue_number_from_url consecutive host dots: GhError with argv and the original output
ok    T-01 issue_number_from_url label starts with a hyphen: GhError with argv and the original output
ok    T-01 issue_number_from_url label ends with a hyphen: GhError with argv and the original output
ok    T-01 issue_number_from_url leading host dot: GhError with argv and the original output
ok    T-01 issue_number_from_url trailing host dot: GhError with argv and the original output
ok    T-01 issue_number_from_url host starts with a hyphen: GhError with argv and the original output
ok    T-01 issue_number_from_url port 65536: GhError with argv and the original output
ok    T-01 issue_number_from_url port 99999: GhError with argv and the original output
ok    T-01 issue_number_from_url port 0: GhError with argv and the original output
ok    T-01 issue_number_from_url port with a leading zero: GhError with argv and the original output
ok    T-01 issue_number_from_url port of six digits: GhError with argv and the original output
ok    T-01 issue_number_from_url empty port: GhError with argv and the original output
ok    T-01 create_issue non-ASCII digits URL: GhError, never a number or a raw ValueError
ok    T-01 create_issue oversized URL: GhError, never a number or a raw ValueError

345/345 checks passed.
PASS test-factory-gh.py
----- test-factory-land.py (exit 0, 0.10s) -----
ok    (M1) exits 0
ok    (M1) pushes exactly one branch
ok    (M1) push args are --set-upstream origin <branch>
ok    (M1) push runs against workspace_path's cwd
ok    (M1) creates exactly one pull request
ok    (M1) pr create base is the fleet's default_branch
ok    (M1) pr create head is the branch
ok    (M1) pr create body contains closes #<n>
ok    (M1) issue_board_item_id was called EXACTLY ONCE — the targeted lookup replaces the whole-board scan (FEAT-13, D-01)
ok    (M1) project_items was called ZERO times
ok    (M1) issue_board_item_id's first argument is the repository string (args.repo), NOT the bare board-owner login
ok    (M1) issue_board_item_id's first argument is explicitly NOT the board-owner login (the mis-wire this assertion exists to catch)
ok    (M1) issue_board_item_id called with (repo, issue, board_number)
ok    (M1) sets the station to Review
ok    (M1) issue_view's requested fields include "state"
ok    (M1) payload url is the created pull request url
ok    (M1) payload carries repo, issue, branch
ok    (M1-json) stdout is a single json.loads-able stream
ok    (M2) still exits 0
ok    (M2) still sets the station
ok    (M2) payload carries the existing pr's url
ok    (M2) stderr mentions the url
ok    (M2b) a non-already-open GhError stays fatal: exits 2
ok    (M2b) the station is never set on an unopened pull request
ok    (M2b) stdout empty
ok    (M2c) a missing board item exits 2, not 0 or 1 (fail-closed on the miss)
ok    (M2c) the station is never set when no item was found
ok    (M2c) stdout empty
ok    (M2c) the pull request WAS already created before the miss was discovered
ok    (M3) exits 2
ok    (M3) zero git calls
ok    (M3) zero gh calls
ok    (M3) stdout empty
ok    (M3) stderr names the branch
ok    (M4) exits 2
ok    (M4) zero git calls
ok    (M4) zero gh calls
ok    (M4) stdout empty
ok    (M4) stderr names the repository
ok    (M5) at least one git call was recorded (anti-vacuum)
ok    (M5) no recorded git call pushes the default branch
ok    (M6) at least one gh call was recorded (anti-vacuum)
ok    (M6) no recorded gh call contains a merge subcommand
ok    (M7) a closed issue exits 2 (refused), not 0
ok    (M7) stdout empty
ok    (M7) stderr names the issue
ok    (M7) the push already happened before the closed-issue refusal
ok    (M7) the pull request WAS already created before the closed-issue refusal
ok    (M7) the station is never set on a closed issue (field_set_calls == [])
ok    (C1) code is 0
ok    (C1) whole stdout stream is one JSON object
ok    (C2) exit 2
ok    (C2) stdout empty
ok    (C2) exactly one stderr line
ok    (C2) that line names the branch
ok    (C3) exits 2, not 1
ok    (C3) stdout empty
ok    (T04-1) exits 0
ok    (T04-1) issue_board_item_id called with A's (repo, issue, board_number)
ok    (T04-1) project_field_set called exactly once
ok    (T04-1) project_field_set carries A's owner, board number, station_field and Review option name
ok    (T04-1) issue_board_item_id's call carries none of B's board markers
ok    (T04-1) project_field_set's call carries none of B's board markers
ok    (T04-1) no gh call of any kind was recorded against B's board number

64/64 checks passed.
PASS test-factory-land.py
----- test-factory-config.py (exit 0, 0.97s) -----
ok    (1) load_fleet round-trips repos[0].name
ok    (1) load_fleet round-trips workspace_root
ok    (3) a repos entry has no board — this is the correct shape now
ok    (2) schema is not factory-fleet/1
ok    (2b) workspace_root is a filesystem root
ok    (8b) a leftover top-level board key raises FleetError
ok    (9) repos is missing
ok    (10) a repo entry lacks a slash in its name
ok    (11) workspace_root is not absolute
ok    (8b) a leftover top-level board key raises FleetError
ok    (8b) the message names key 'board' exactly
ok    (8b) the next_step names the whole-fleet key, not repos[].board
ok    (8b) the next_step points at github.board
ok    (8b) the next_step no longer points at repos[].board
ok    (12) repos is empty
ok    (13) repos is not a list
ok    (14) a repo entry lacks default_branch
ok    (14d) workspace_root is missing
ok    (6)/(28b) validate_board coerces a digit string number to an int
ok    (15) at least 9 FleetError messages were collected
ok    (15) FleetError message obeys C-3: 'fleet schema invalid: schema — set schema: factory-fleet/1 in /var/fol'
ok    (15) FleetError message obeys C-3: "fleet key invalid: workspace_root — it is a filesystem root ('/') in /"
ok    (15) FleetError message obeys C-3: 'fleet key invalid: board — a whole-fleet board key is no longer read f'
ok    (15) FleetError message obeys C-3: 'fleet key invalid: repos — set a non-empty list of repo entries in /va'
ok    (15) FleetError message obeys C-3: 'fleet repo entry invalid: repos[].name — each repo needs a name contai'
ok    (15) FleetError message obeys C-3: 'fleet key invalid: workspace_root — set it to an absolute path in /var'
ok    (15) FleetError message obeys C-3: 'fleet key invalid: repos — set a non-empty list of repo entries in /va'
ok    (15) FleetError message obeys C-3: 'fleet key invalid: repos — set a non-empty list of repo entries in /va'
ok    (15) FleetError message obeys C-3: 'fleet repo entry invalid: repos[o/r].default_branch — set a non-empty '
ok    (15) FleetError message obeys C-3: 'fleet key invalid: workspace_root — set it to an absolute path in /var'
ok    (16) repo_entry finds the listed repo
ok    (17) repo_entry raises FleetError for an unlisted name
ok    (17) the message names the unlisted name
ok    load_fleet rejects a repos entry carrying a board key
ok    load_fleet still requires repos[].name, repos[].default_branch and workspace_root
ok    validate_board accepts the ordered lowercase station list, returns the board, and carries stations as a tuple of the six
ok    (X) schemas/feature.json declares NO status key — the second vocabulary is gone
ok    (X) MANDATED_STATIONS is exactly the six lowercase stations, in board order
ok    (T-03) TERMINAL_MARKER no longer exists — TERMINAL_STATIONS is the one terminal vocabulary
ok    (T-02) TERMINAL_STATIONS is the ordered abandoned/rejected non-board tuple
ok    (FEAT-61) STATION_ROWS is an ordered tuple of (name, has_board_column, bucket) rows
ok    (FEAT-61) STATION_ROWS names are plain strings in lifecycle order
ok    (FEAT-61) MANDATED_STATIONS is derived: exactly the rows with a board column, in order
ok    (FEAT-61) TERMINAL_STATIONS is derived: exactly the rows without a board column, in order
ok    (FEAT-61) ACTIVE_STATIONS is the four in-progress stations, in order
ok    (FEAT-61) FINISHED_STATIONS is done then the terminal names — the old concatenation order
ok    (FEAT-61) not_started | active | finished partition the eight names with no overlap
ok    (FEAT-61) is_active/is_finished('backlog') == (False, False)
ok    (FEAT-61) is_active/is_finished('plan') == (True, False)
ok    (FEAT-61) is_active/is_finished('ready') == (True, False)
ok    (FEAT-61) is_active/is_finished('building') == (True, False)
ok    (FEAT-61) is_active/is_finished('review') == (True, False)
ok    (FEAT-61) is_active/is_finished('done') == (False, True)
ok    (FEAT-61) is_active/is_finished('abandoned') == (False, True)
ok    (FEAT-61) is_active/is_finished('rejected') == (False, True)
ok    (FEAT-61) is_active('') raises FleetError naming the known stations
ok    (FEAT-61) is_finished('') raises FleetError naming the known stations
ok    (FEAT-61) is_active('Done') raises FleetError naming the known stations
ok    (FEAT-61) is_finished('Done') raises FleetError naming the known stations
ok    (FEAT-61) is_active('shipped') raises FleetError naming the known stations
ok    (FEAT-61) is_finished('shipped') raises FleetError naming the known stations
ok    (FEAT-61) is_active(None) raises FleetError naming the known stations
ok    (FEAT-61) is_finished(None) raises FleetError naming the known stations
ok    (FEAT-61) is_active(3) raises FleetError naming the known stations
ok    (FEAT-61) is_finished(3) raises FleetError naming the known stations
ok    (FEAT-61) is_active(('done',)) raises FleetError naming the known stations
ok    (FEAT-61) is_finished(('done',)) raises FleetError naming the known stations
ok    station_column('backlog') is exactly 'Backlog'
ok    station_column('plan') is exactly 'Plan'
ok    station_column('ready') is exactly 'Ready'
ok    station_column('building') is exactly 'Building'
ok    station_column('review') is exactly 'Review'
ok    station_column('done') is exactly 'Done'
ok    (X) every mandated station round-trips through station_column to a column that lowercases back to it
ok    station_column('abandoned') raises FleetError
ok    station_column('rejected') raises FleetError
ok    station_column('Done') raises FleetError
ok    station_column('Icebox') raises FleetError
ok    station_column('') raises FleetError
ok    station_column('DONE') raises FleetError
ok    station_names returns the six mandated stations as a tuple
ok    board_for refuses a valid member config whose board is null
ok    board_for resolves through product_config
ok    product_config reads the remote at default_branch with no checkout on disk
ok    product_config remote harness.json text is accepted by load_harness_json
ok    product_config raises naming repo, path and ref when the remote read fails
ok    product_config never falls back to a checkout
ok    product_config never falls back to a checkout on disk when the remote read fails
ok    product_config memoises a successful read: a second board_for makes no second remote read
ok    product_config memoisation: a failing read is not cached and the next call succeeds
ok    (29) board_station returns the derived column for a station the repo's board declares
ok    (30) board_station raises FleetError on an unknown key
ok    (31) board_for on an unlisted repository raises FleetError
ok    (31) the message names the unlisted repository
ok    (20) FLEET_PATH is an absolute path
ok    (21) a HARNESS_PROJECT_DIR with no MARKER is discarded
ok    (21) discarding it is announced on stderr
ok    (21) the returned root still carries harness_boundary.MARKER
ok    (21) it is the same root factory_config.FLEET_PATH was built from
ok    (22) workspace_path joins workspace_root with the name after the slash
ok    (22) workspace_path does not use the owner-prefixed name
ok    (23) --show over a good fleet exits 0 (or None)
ok    (23) --show's stdout parses as a single json.loads
ok    (23) --show's payload has 'repos' and no top-level 'board'
ok    (24) --show over an invalid fleet writes nothing to stdout
ok    (24) --show over an invalid fleet writes exactly one stderr line
ok    (24) --show over an invalid fleet exits 2
ok    (X) sanity: factory_*.py enumeration is non-empty and includes factory_config.py, and _find_fleet_reads self-test finds both the module-scope read and the function-scope assign-chain read in a throwaway fixture, and reports nothing else (the negative os.path.join shape is not a hit)
ok    (X) SC-18: exactly one scope in artifact_accessors.py and factory_*.py opens/parses the fleet file
ok    (X) SC-18: that one reader is artifact_accessors.py's load_fleet — no other tool bypasses it
ok    (X) issue #208: unparseable fleet.yaml raises FleetError
ok    (X) issue #208: the FleetError names the file path

112/112 checks passed.
PASS test-factory-config.py
----- test-factory-claim-mutation.py (exit 0, 1.55s) -----
BASELINE 3/3 ok
MUTANT ACTIVE
FAIL  BUG-1290 5a: served non-harness repository reaches its own segment's blocker verdict, not no_plan
FAIL  BUG-1290 5b: same feature id on two repositories resolves per-segment, no cache bleed
FAIL  BUG-1290 5c: absent segment root still refuses via no_plan, naming that segment's own path
MUTATION PROOF: 3/3 cases reddened
MUTANT KEY-COLLAPSE ACTIVE
FAIL  BUG-1290 5b: same feature id on two repositories resolves per-segment, no cache bleed
KEY-COLLAPSE PROOF: FAIL BUG-1290 5b printed
PASS test-factory-claim-mutation.py
----- test-corpus-regression.py (exit 0, 3.94s) -----
....
----------------------------------------------------------------------
Ran 4 tests in 3.666s

OK
PASS test-corpus-regression.py
----- test-feature-json-budget.py (exit 0, 0.28s) -----
........
----------------------------------------------------------------------
Ran 8 tests in 0.005s

OK
PASS test-feature-json-budget.py
----- test-factory-workspace.py (exit 0, 1.06s) -----
ok    (A) missing checkout: exits 0
ok    (A) missing checkout: first call is clone
ok    (A) missing checkout: some later call checks out the issue branch
ok    (A) missing checkout: no fetch
ok    (B) existing checkout: exits 0
ok    (B) existing checkout: fetch is called
ok    (B) existing checkout: clone is never called
ok    BUG-240 existing checkout: refresh order is fetch, checkout default, reset --hard
ok    (C) missing checkout: final command checks out the issue branch
ok    (C) existing checkout: final command checks out the issue branch
ok    (D) origin carries the ref: final checkout tracks origin
ok    (D) origin carries the ref: no command names both the issue branch and origin/<default_branch> together (the T-07 divergence bug)
ok    (E) origin has no ref: final checkout is created off origin/<default_branch>
ok    (F) existing local branch tracking origin: checked out as-is, not recreated with -b
ok    (F2) local branch diverges from origin (cut from default_branch): NOT a bare checkout (the fail-open shape)
ok    (F2) local branch diverges from origin (cut from default_branch): final command force-aligns onto origin/factory/issue-42
ok    (F2) local branch diverges from origin (cut from default_branch): still exits 0 (repaired, not refused)
ok    (F2) local branch diverges from origin (no upstream at all): NOT a bare checkout (the fail-open shape)
ok    (F2) local branch diverges from origin (no upstream at all): final command force-aligns onto origin/factory/issue-42
ok    (F2) local branch diverges from origin (no upstream at all): still exits 0 (repaired, not refused)
ok    (G) unlisted repo: exits 2
ok    (G) unlisted repo: zero git calls
ok    (H) a failing git command exits non-zero
ok    (I) happy path: stdout is exactly one JSON object
ok    (I) happy path: payload has path and branch
ok    (I) happy path: payload path is absolute
ok    (J) unlisted repo refusal: nothing on stdout
ok    (J) unlisted repo refusal: exactly one stderr line
ok    (J) unlisted repo refusal: that line names the repository
ok    (J) unlisted repo refusal: exits 2
ok    (K) a plain RuntimeError from run_git exits 2, not 1
ok    BUG-240 dirty tracked: exits 2 before any fetch
ok    BUG-240 dirty tracked: refusal line names the path and the uncommitted-work condition
ok    BUG-240 dirty tracked: the modified file survives byte-identical
ok    BUG-240 ignored-only dirt: not refused
ok    BUG-240 self checkout: refused when clean, naming the self-checkout condition
ok    BUG-240 other harness checkout: onboarded but not the control plane is not refused
ok    BUG-240 no bypass: the parser rejects --force
ok    BUG-240 case-mismatched self checkout: refused via identity, not spelling

39/39 checks passed.
PASS test-factory-workspace.py
----- test-feature-json-reader.py (exit 0, 0.55s) -----
..........................
----------------------------------------------------------------------
Ran 26 tests in 0.011s

OK
PASS test-feature-json-reader.py
----- test-feature-corpus-discovery.py (exit 0, 1.15s) -----
............
----------------------------------------------------------------------
Ran 12 tests in 1.031s

OK
PASS test-feature-corpus-discovery.py
----- test-feature-schema-build-entry.py (exit 0, 0.52s) -----
PASS FEAT-71 feature_schema holds no per-feature id table 
PASS BE-02 a building plan with no task done is open for every feature id 
PASS BE-10 no receipt allows no merge for any feature id 
PASS BE-03 a feature with no plan.yaml returns recover-terminal 
PASS BE-04 a feature whose plan.yaml does not parse returns recover-terminal 
PASS BE-06 plan status done returns recover-terminal 
PASS BE-08 building with three tasks none done is open, and only-last-done is recover-terminal 
PASS BE-09 plan status building with an empty tasks list returns open 
PASS a plan-flow engineering simplify run is not started work; a code-graded one is 
PASS FEAT-71 a runs entry without agent is refused at index 0 for every feature id 
PASS FEAT-64 BE-11 a plan.yaml that does not parse is recover-terminal 
PASS FEAT-64 BE-12 an unrelated RuntimeError in the plan loader escapes recovery_command_for 
PASS a bound feature's opened mapping without github.repo is not repository provenance 
PASS repository-aware merge receipt: matching opened generation 
PASS repository-aware merge receipt: wrong repository 
PASS repository-aware merge receipt: bound wrong repository 
PASS repository-aware merge receipt: legacy unbound opened, created by the owner binding that still resolves it 
PASS repository-aware merge receipt: legacy unbound recovered-terminal 
PASS repository-aware merge receipt: unresolved owner repository 
PASS repository-aware merge receipt: legacy unbound sync-off 
PASS the shared binding resolver exists 
PASS unbound sync-off retains legal null board 
PASS invalid authoritative binding refuses before owner fallback: '' 
PASS invalid authoritative binding refuses before owner fallback: 'owner' 
PASS invalid authoritative binding refuses before owner fallback: '../owner/product' 
PASS invalid authoritative binding refuses before owner fallback: 12 
PASS invalid authoritative binding refuses before owner fallback: False 
PASS test-feature-schema-build-entry.py
----- test-digest-schemas.py (exit 0, 4.34s) -----
..................................
----------------------------------------------------------------------
Ran 34 tests in 3.903s

OK
PASS test-digest-schemas.py
----- test-fleet-product-config.py (exit 0, 0.57s) -----
ok    (a) two declared repos, both succeed -> every entry ok, ok count 2, unreachable 0
ok    (a)/(d) len(report) equals len(fleet['repos'])
ok    (b) the FIRST entry, asserted individually, is not ok and names repo and ref
ok    (b) the SECOND entry, asserted individually, is ok with an empty detail
ok    (b)/(d) len(report) equals len(fleet['repos'])
ok    (f) an exception that is neither FleetError nor GhError propagates out of product_config_report instead of being reported as an ok:False entry
ok    every entry carries exactly repo/ref/path/ok/detail, path is _PRODUCT_CONFIG_PATH
ok    product_config_report preserves fleet['repos'] declaration order
ok    (e) --check-product-configs exits 2 (EXIT_REFUSED) under a failing stub
ok    (e) stdout under failure parses as ONE JSON payload with declared/ok/unreachable/members
ok    (e) exactly one stderr line is written for the one unreachable member
ok    (g) V-7: the stderr line starts with the canonical 'factory: config: ' prefix
ok    (g) V-7: the repo@ref:path token appears exactly once in the stderr line, not twice
ok    (e) --check-product-configs returns without SystemExit under an all-succeeding stub
ok    (e) stdout under success parses as ONE JSON payload with declared/ok/unreachable/members
ok    (e) no stderr line is written when nothing is unreachable

16/16 checks passed.
PASS test-fleet-product-config.py
----- test-gen-craft-index.py (exit 0, 0.15s) -----
ok   committed_index_matches_fresh_render
ok   every_leaf_parses
ok   at_least_ten_leaves
ok   attack-the-premise_indexed
ok   attack-the-premise_exists
ok   build-the-lever_indexed
ok   build-the-lever_exists
ok   delete-first_indexed
ok   delete-first_exists
ok   experience-first_indexed
ok   experience-first_exists
ok   foundational-thinking_indexed
ok   foundational-thinking_exists
ok   make-operations-idempotent_indexed
ok   make-operations-idempotent_exists
ok   migrate-callers-then-delete_indexed
ok   migrate-callers-then-delete_exists
ok   model-the-domain_indexed
ok   model-the-domain_exists
ok   outcome-oriented-execution_indexed
ok   outcome-oriented-execution_exists
ok   redesign-from-first-principles_indexed
ok   redesign-from-first-principles_exists
ok   separate-before-serializing-shared-state_indexed
ok   separate-before-serializing-shared-state_exists
ok   type-system-discipline_indexed
ok   type-system-discipline_exists
ok   description_must_start_with_apply
ok   seats_must_be_canonical_order

all checks passed
PASS test-gen-craft-index.py
----- test-gh-board-item-add.py (exit 0, 0.13s) -----
PASS  u.1 an absent item is looked up, added once with the canonical URL, then set
PASS  u.2 an existing item is set with its own id and never re-added
PASS  u.3 a GhError at lookup (existing=None) is a BoardError naming the issue and the lowercase station, with no later call
PASS  u.3 a GhError at add (existing=None) is a BoardError naming the issue and the lowercase station, with no later call
PASS  u.3 a GhError at set (existing=None) is a BoardError naming the issue and the lowercase station, with no later call
PASS  u.3 a GhError at set (existing='ITEM_EXISTING') is a BoardError naming the issue and the lowercase station, with no later call
PASS test-gh-board-item-add.py
----- test-feature-corpus-gates.py (exit 0, 1.85s) -----
...........
----------------------------------------------------------------------
Ran 11 tests in 1.749s

OK
PASS test-feature-corpus-gates.py
----- test-gate-policy.py (exit 0, 0.48s) -----
ok    loader resolves review by name from the validated config
ok    removed gate keys are refused, naming the key
ok    review blocks must_fix even without a severity escalation
ok    review passes a clean medium-severity report
ok    review blocks high severity
ok    blocking review blocks findings
ok    advisory review always passes
ok    unknown review severity raises loudly: names severity_max
ok    unknown review severity raises loudly: carries offending value
PASS test-gate-policy.py
----- test-code-grade.py (exit 0, 6.29s) -----
PASS test-code-grade
PASS test-code-grade.py
----- test-gh-sync-build-entry.py (exit 0, 0.31s) -----
PASS BE-11 load_recorded normalizes an out-of-enum build_entry to None 
PASS BE-12 save_recorded of a normalized record drops the build_entry key 
PASS BE-14 record_build_entry upgrades a recorded recovery-required to opened 
PASS legacy opened receipt, factory=None: rerun skip leaves opened 
PASS legacy opened receipt, factory={'repo': 'org/product'}: rerun skip leaves recovery-required 
PASS BE-19 skip armed with feature.json absent records nothing and creates no file 
PASS BE-31 an absent receipt refuses the Build start for every feature id 
PASS BE-32 recovery-required warns that the merge is refused, for every feature id 
PASS BE-25 a matching string --parent against the recorded parent is no conflict 
PASS BE-27 conflict is None with no --parent given, and None with no parent recorded 
PASS BE-28 milestone and parent recorded yields no creates and both adoption lines 
PASS BE-29 neither milestone nor parent recorded yields the exact two-line creates list 
PASS BE-30 milestone recorded plus --parent 9 given adopts by number, and no adoption state ever mentions a task or a sub-issue 
PASS test-gh-sync-build-entry.py
----- test-gh-cost-log.py (exit 0, 0.55s) -----
PASS  redirect took effect before any assertion about content
PASS  fresh log file's FIRST line is JSON carrying a coverage key
PASS  coverage value mentions run_gh
PASS  coverage value mentions gh typed directly into Bash
PASS  a successful invocation writes exactly one invocation line
PASS  recorded line has all six required keys
PASS  cost equals after minus before
PASS  before/after/rc are recorded verbatim
PASS  appending a second invocation does not rewrite the coverage line
PASS  appending a second invocation adds exactly one more line
PASS  a failing invocation (rc=1) is still recorded
PASS  the failing invocation's line carries rc 1
PASS  the failing invocation's line carries its real cost
PASS  a -f value longer than 80 chars is truncated with an ellipsis
PASS  a short -F value is left untouched
PASS  HARNESS_GH_COST_LOG=0 writes no line at all
PASS  a counter read that raises does not propagate out of measured()
PASS  a counter-read failure records null before/after/cost
PASS  a counter-read failure still records the real returncode
PASS  measured() never records a line for the counter's own argv
PASS  with HARNESS_GH_COST_LOG unset, a successful invocation creates no log file
PASS  with HARNESS_GH_COST_LOG unset, a successful invocation writes no line
PASS  with HARNESS_GH_COST_LOG unset, a FAILING invocation creates no log file
PASS  with HARNESS_GH_COST_LOG unset, a FAILING invocation writes no line
PASS  factory_gh.run_gh wrap site, ON: one line written for the wrapped invocation
PASS  factory_gh.run_gh wrap site, ON: three subprocess calls (counter, real, counter)
PASS  factory_gh.run_gh wrap site, OFF: no line written
PASS  factory_gh.run_gh wrap site, OFF: exactly one subprocess call (the real call only)
PASS  gh-sync.py gh() wrap site, ON: one line written for the wrapped invocation
PASS  gh-sync.py gh() wrap site, ON: three subprocess calls (counter, real, counter)
PASS  gh-sync.py gh() wrap site, OFF: no line written
PASS  gh-sync.py gh() wrap site, OFF: exactly one subprocess call (the real call only)
PASS  factory_gh.run_gh wrap site, FAILING: GhError was raised
PASS  factory_gh.run_gh wrap site, FAILING: one line written for the wrapped invocation
PASS  factory_gh.run_gh wrap site, FAILING: the recorded rc equals the real exit code (1)
PASS  OFF, FAILING: GhError was still raised (the wrapper does not swallow the real error)
PASS  OFF, FAILING: no log file is created
PASS  OFF, FAILING: no line is written
PASS  OFF, FAILING: exactly one subprocess call (the real call only, neither counter read)
PASS  FEAT-64: an absent counter binary reads None
PASS  FEAT-64: a counter that prints junk reads None
PASS  FEAT-64: an unrelated RuntimeError escapes _read_counter
PASS  FEAT-64: an unrelated RuntimeError escapes record
PASS  T-01 _read_counter: reads the counter through factory_gh.launch_gh only
PASS  T-01 _read_counter: a typed launch failure and a nonzero counter both read None
PASS  T-01 telemetry rc=0: before-counter, operation, after-counter, nothing else
PASS  T-01 telemetry rc=0: one recorded line with the real return code
PASS  T-01 telemetry rc=0: the result keeps the real process status
PASS  T-01 telemetry rc=1: before-counter, operation, after-counter, nothing else
PASS  T-01 telemetry rc=1: one recorded line with the real return code
PASS  T-01 telemetry rc=1: the result keeps the real process status
PASS  T-01 telemetry run_gh: the adapter adds no second measurement
PASS  T-01 launch_gh: telemetry ON still launches exactly once and records nothing
PASS  T-01 import gh_cost_log then factory_gh: no gh launch at import
PASS  T-01 import gh_cost_log then factory_gh: factory_gh wires the same gh_cost_log
PASS  T-01 import gh_cost_log then factory_gh: the counter resolves factory_gh at call time
PASS  T-01 import factory_gh then gh_cost_log: no gh launch at import
PASS  T-01 import factory_gh then gh_cost_log: factory_gh wires the same gh_cost_log
PASS  T-01 import factory_gh then gh_cost_log: the counter resolves factory_gh at call time

59/59 checks passed
PASS test-gh-cost-log.py
----- test-handoff-policy.py (exit 0, 0.09s) -----
PASS every task main-session-direct -> exempt, naming DEC-174 
PASS absent plan.yaml -> no exemption 
PASS absent plan.yaml -> no detail (nothing was unreadable, it simply is not exempt) 
PASS unparsable plan.yaml -> no exemption 
PASS unparsable plan.yaml -> the detail says why it could not be evaluated 
PASS plan.yaml that is not a mapping -> no exemption 
PASS plan.yaml that is not a mapping -> the detail says why it could not be evaluated 
PASS empty tasks list (vacuous truth is refused) -> no exemption 
PASS empty tasks list (vacuous truth is refused) -> the detail says why it could not be evaluated 
PASS tasks key that is not a list -> no exemption 
PASS tasks key that is not a list -> the detail says why it could not be evaluated 
PASS a task that is not a mapping -> no exemption 
PASS a task that is not a mapping -> the detail says why it could not be evaluated 
PASS a task with no execution_mode -> no exemption 
PASS a task with no execution_mode -> the detail says why it could not be evaluated 
PASS a team task -> no exemption 
PASS a team task -> no detail (nothing was unreadable, it simply is not exempt) 
PASS a mixed plan (one direct, one team) -> no exemption 
PASS a mixed plan (one direct, one team) -> no detail (nothing was unreadable, it simply is not exempt) 
PASS unreadable plan.yaml -> no exemption, detail names the read failure 
PASS FEAT-64: an unrelated RuntimeError in the plan loader escapes _plan_mapping 
21 passed, 0 failed
PASS test-handoff-policy.py
----- test-gh-sync-abandon-sources.py (exit 0, 0.59s) -----
PASS AS-01 planner: opted-in sources join the SAME plan list, a comment and a close line each; the default plan has no source entry 
PASS AS-02 planner: each source close line names not_planned, abandoned and the backlog 
PASS AS-03 planner: a source that is a task issue gets its own reason comment and is closed once; a source that is the parent is not planned twice 
gh-sync: reason posted on parent #40
gh-sync: detached #41 from parent #40
gh-sync: milestone #7 closed
gh-sync: reason posted on source #51
gh-sync: reason posted on source #52
PASS AS-04 executor: every comment, parent and both sources, passes the unchanged original reason-file argument 
PASS AS-05 executor: sources close with the target label 'source', in plan order 
PASS AS-06 dry run with --close-sources lists both sources and writes nothing 
PASS AS-09 --yes without --close-sources: ZERO source comment, close, label or board write, while the parent and task ARE disposed 
PASS AS-07 --yes with --close-sources: both sources closed, commented and labelled with the original reason-file argument 
PASS AS-08 close-sources: each source's backlog write follows its own close 
PASS GC-01 source/task alias, --yes, no --close-sources: ZERO writes name #41, and the skip is reported as a gap naming the flag 
PASS GC-01 source/task alias, --yes: the non-aliased entry #40 IS still disposed and the station is recorded 
PASS GC-01 source/task alias, dry run, no --close-sources: ZERO writes name #41, and the skip is reported as a gap naming the flag 
PASS GC-01 source/task alias, --close-sources --yes: #41 is commented once, closed once and reseated once, and no gap is reported 
PASS GC-01 source/parent alias, --yes, no --close-sources: ZERO writes name #40, and the skip is reported as a gap naming the flag 
PASS GC-01 source/parent alias, --yes: the non-aliased entry #41 IS still disposed and the station is recorded 
PASS GC-01 source/parent alias, dry run, no --close-sources: ZERO writes name #40, and the skip is reported as a gap naming the flag 
PASS GC-01 source/parent alias, --close-sources --yes: #40 is commented once, closed once and reseated once, and no gap is reported 
PASS F1 station write refused: runs/ pruned = False, and the gap is reported 
PASS F1 station write recorded: runs/ pruned = True 
PASS F1 station already abandoned: runs/ pruned = True 
PASS AS-10 a source cited by another active feature is still disposed, and only THIS plan's sources are targeted — never the other feature's #77 
PASS AS-11 neither feature's plan.yaml source list nor feature.json mirror is mutated 
PASS AS-12 plan.yaml's source list wins over a stale feature.json mirror 
PASS AS-13 unopened, no sources, --yes: no SKIP; records abandoned THEN prunes, with no remote write and no label creation 
PASS AS-14 unopened with plan-only sources: both disposed, then station, then prune 
PASS AS-15 re-entry at abandoned: the station is NOT rewritten, the source IS disposed, and runs/ is still pruned 
PASS AS-16 a failed source close is reported and never stops the next source or the station and prune 
PASS AS-17 a failed source comment and label are each named, and the card is still reseated and the later source disposed 
PASS AS-18 the reporters say 'reason posted on source #51' and never claim the reason went unposted when a source received it 
PASS AS-19 with no comment target at all, the gap line still says the reason was not posted 
PASS AS-20 an existing direct caller (no close_sources argument) still disposes parent and task and touches no source 

ALL PASSED
PASS test-gh-sync-abandon-sources.py
----- test-gh-board.py (exit 0, 0.84s) -----
PASS  load_board: an explicit null board is accepted and returns None
PASS  load_board: a padded digit string is normalised to an int and stations to a tuple
PASS  derive_station: one building among three -> building
PASS  derive_station: three of three done -> review
PASS  derive_station: two done one not-started -> None
PASS  derive_station: empty task list -> None
PASS  derive_station: task with NO status key counts as not-started -> None
PASS  derive_station returns the lowercase station 'building', not its board column
PASS  derive_station returns the lowercase station 'review', not its board column
PASS  derive_station rejects a second board argument
PASS  board_stations: item from another repository is EXCLUDED
PASS  board_stations: a board value is lowercased on read
PASS  board_stations lowercases a board value of "Review" to "review"
PASS  board_stations: no capitalised station survives the read
PASS  board_stations: item with NO status key is present with value None, not dropped
PASS  board_stations: item with content null does not crash and is not in output
PASS  board_stations_for: a board value is lowercased on read
PASS  board_stations_for: no capitalised station survives the read
PASS  board_stations_for: on the board with no value is PRESENT with None
PASS  board_stations_for: an issue that is not on the board is ABSENT, not None
PASS  board_stations_for: read_station tells its absent apart from its None
PASS  board_stations_for: an empty number set touches no network and returns {}
PASS  read_station: on the board with a station -> (station, None)
PASS  read_station: absent from the mapping -> (None, 'not on the board')
PASS  read_station: present with a None value -> (None, 'no station set')
PASS  set_station: a failing gh raises BoardError
PASS  set_station: the error NAMES the issue number and the lowercase station attempted
PASS  set_station passes "Done" to project_field_set when given "done"
PASS  set_station raises FleetError on a capitalised station and writes nothing
PASS  project: active plan projects every unique source, parent, and live task
PASS  project: active ready projects every unique source, parent, and live task
PASS  project: active building projects every unique source, parent, and live task
PASS  project: active review projects every unique source, parent, and live task
PASS  project: done preserves terminal placement and excludes abandoned tasks
PASS  project: absent phase leaves only the task-local non-terminal card
PASS  project: backlog is a column but never an active projection
PASS  project: abandoned places no parent or source card and no active projection
PASS  project: rejected places no parent or source card and no active projection
PASS  project: task station 'pending' raises FleetError naming the task and the value
PASS  project: task station 'Building' raises FleetError naming the task and the value
PASS  project: task station 'shipped' raises FleetError naming the task and the value
PASS  project: the value is a station, never a column

all pass
PASS test-gh-board.py
----- test-handoff-done-when.py (exit 0, 0.46s) -----
PASS missing section 
PASS well formed 
PASS plan authority rejects schema-invalid plan 
PASS nested heading cannot truncate validation 
PASS duplicate heading cannot truncate validation 
PASS zero scope 
PASS two scope 
PASS zero authority 
PASS five authority 
PASS stray line 
PASS blank scope 
PASS scope after authority 
PASS unsafe pointer rejected resolve=True 'finding:/tmp/review.md#F-02' 
PASS unsafe pointer rejected resolve=False 'finding:/tmp/review.md#F-02' 
PASS unsafe pointer rejected resolve=True 'finding:../review.md#F-02' 
PASS unsafe pointer rejected resolve=False 'finding:../review.md#F-02' 
PASS unsafe pointer rejected resolve=True 'finding:.harness/harness/features/FEAT-90-fixture/notes/\x00review.md#F-02' 
PASS unsafe pointer rejected resolve=False 'finding:.harness/harness/features/FEAT-90-fixture/notes/\x00review.md#F-02' 
PASS unsafe pointer rejected resolve=True 'approval:/tmp/review.md#Approval' 
PASS unsafe pointer rejected resolve=False 'approval:/tmp/review.md#Approval' 
PASS unsafe pointer rejected resolve=True 'approval:../review.md#Approval' 
PASS unsafe pointer rejected resolve=False 'approval:../review.md#Approval' 
PASS unsafe pointer rejected resolve=True 'approval:.harness/harness/features/FEAT-90-fixture/notes/\x01review.md#Approval' 
PASS unsafe pointer rejected resolve=False 'approval:.harness/harness/features/FEAT-90-fixture/notes/\x01review.md#Approval' 
PASS unsafe pointer rejected resolve=True 'brief-perspective:/tmp/BRIEF.md#operator' 
PASS unsafe pointer rejected resolve=False 'brief-perspective:/tmp/BRIEF.md#operator' 
PASS unsafe pointer rejected resolve=True 'brief-perspective:../BRIEF.md#operator' 
PASS unsafe pointer rejected resolve=False 'brief-perspective:../BRIEF.md#operator' 
PASS plan resolves 
PASS plan unresolved 
PASS plan unresolved ignored without resolution 
PASS brief resolves 
PASS brief unresolved 
PASS brief unresolved ignored without resolution 
PASS finding resolves 
PASS finding unresolved 
PASS finding unresolved ignored without resolution 
PASS approval resolves 
PASS approval unresolved 
PASS approval unresolved ignored without resolution 
PASS unknown authority docs:whatever resolve=True 
PASS unknown authority docs:whatever resolve=False 
PASS unknown authority check-domain.py:1523 resolve=True 
PASS unknown authority check-domain.py:1523 resolve=False 
PASS unknown authority brief-perspective:SC-04 resolve=True 
PASS unknown authority brief-perspective:SC-04 resolve=False 
PASS four authorities accepted 
PASS all authorities required 
PASS approval requires real ATX heading bad-nospace.md 
PASS approval requires real ATX heading bad-seven.md 
PASS missing section without resolution 
PASS zero scope without resolution 
PASS two scope without resolution 
PASS zero authority without resolution 
PASS five authority without resolution 
PASS stray line without resolution 
PASS resolve false opens no target 
PASS finding symlink escape 
PASS finding special file 
PASS approval symlink escape 
PASS approval special file 
PASS satisfaction: done task alone binds nothing 
PASS satisfaction: abandoned task alone binds nothing 
PASS satisfaction: approved approval alone binds nothing 
PASS satisfaction: every pointer satisfied binds nothing 
PASS satisfaction: open task still binds 
PASS satisfaction: pending approval still binds 
PASS satisfaction: satisfied plus open task still binds 
PASS satisfaction: criterion alone is indeterminate 
PASS satisfaction: satisfied task plus criterion still binds 
PASS satisfaction: stationless task is indeterminate 
PASS satisfaction: rejected task is terminal 
PASS satisfaction: a task status outside the vocabulary is indeterminate, not a refusal 
PASS satisfaction: silent when resolve is false 
PASS satisfaction: unresolved wins over vacuity 
PASS perspective: perspective resolves 
PASS perspective: perspective with gloss resolves by bare name 
PASS perspective: perspective name is case-insensitive 
PASS perspective: undeclared perspective is unresolved 
PASS perspective: perspective must sit under the by-perspective heading 
PASS perspective: no perspective under a by-perspective BRIEF is refused 
PASS perspective: perspective beside other authorities is accepted 
PASS perspective: perspective requirement is write-time only 
PASS perspective: perspective grammar is checked without resolution 
PASS perspective: old-shape BRIEF has no perspective block 
PASS perspective: old-shape BRIEF is unaffected 
PASS perspective: never already satisfied 
PASS perspective: unresolved wins over missing perspective 
PASS FEAT-64: plan.yaml is parsed once per note across resolution and satisfaction 
PASS FEAT-64: an unrelated RuntimeError in the plan loader escapes resolution 
PASS FEAT-64: an unrelated RuntimeError in satisfaction escapes 
PASS FEAT-64: a FleetError from the station vocabulary is indeterminate, not a refusal 
PASS test-handoff-done-when.py
----- test-instruction-workflow-gate.py (exit 0, 0.03s) -----
PASS - workflow runs instruction gate and propagates its nonzero status
PASS - workflow mutant without instruction gate is refused
PASS - workflow mutant that ignores gate status is refused
PASS - repository-state gate installs tracked hooks before checking INV-31
PASS - repository-state mutant without hook setup is refused
PASS - repository-state mutant with commented hook setup is refused
PASS - repository-state mutant that only echoes hook setup is refused
PASS test-instruction-workflow-gate.py
----- test-integration-shard-validation.py (exit 0, 0.07s) -----
PASS checks-result failure rejected: exit 1 
PASS checks-result failure rejected: diagnostic names 'checks-result is failure' 
PASS checks-result skipped rejected: exit 1 
PASS checks-result skipped rejected: diagnostic names 'checks-result is skipped' 
PASS checks-result cancelled rejected: exit 1 
PASS checks-result cancelled rejected: diagnostic names 'checks-result is cancelled' 
PASS checks-result missing rejected: exit 1 
PASS checks-result missing rejected: diagnostic names 'checks-result is missing' 
PASS checks-result unrecognized rejected: exit 2 
PASS checks-result unrecognized rejected: diagnostic names 'checks-result 'neutral' is not one of' 
PASS checks-result absent rejected: exit 2 
PASS checks-result absent rejected: diagnostic names 'checks-result was not supplied' 
PASS matrix-result failure rejected: exit 1 
PASS matrix-result failure rejected: diagnostic names 'matrix-result is failure' 
PASS matrix-result skipped rejected: exit 1 
PASS matrix-result skipped rejected: diagnostic names 'matrix-result is skipped' 
PASS matrix-result cancelled rejected: exit 1 
PASS matrix-result cancelled rejected: diagnostic names 'matrix-result is cancelled' 
PASS matrix-result missing rejected: exit 1 
PASS matrix-result missing rejected: diagnostic names 'matrix-result is missing' 
PASS matrix-result unrecognized rejected: exit 2 
PASS matrix-result unrecognized rejected: diagnostic names 'matrix-result 'neutral' is not one of' 
PASS matrix-result absent rejected: exit 2 
PASS matrix-result absent rejected: diagnostic names 'matrix-result was not supplied' 
PASS missing manifest for shard 3: exit 1 
PASS missing manifest for shard 3: diagnostic names 'no manifest for shard 3' 
PASS duplicate shard id: exit 1 
PASS duplicate shard id: diagnostic names 'shard 3 has 2 manifests' 
PASS extra manifest beyond shard count: exit 1 
PASS extra manifest beyond shard count: diagnostic names 'shard_index 5 outside 1..4' 
PASS foreign commit: exit 1 
PASS foreign commit: diagnostic names 'tested_commit bbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbb is not the supplied aaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaa' 
PASS foreign suite kind: exit 1 
PASS foreign suite kind: diagnostic names 'kind 'unit' is not integration' 
PASS foreign shard count: exit 1 
PASS foreign shard count: diagnostic names 'shard_count 3 is not 4' 
PASS malformed manifest (not an object): exit 2 
PASS malformed manifest (not an object): diagnostic names 'm2.json: manifest must be a JSON object' 
PASS wrong schema: exit 2 
PASS wrong schema: diagnostic names 'schema must be 1' 
PASS unreadable manifest: exit 2 
PASS unreadable manifest: diagnostic names 'm2.json: malformed JSON' 
PASS non-integer return code: exit 2 
PASS non-integer return code: diagnostic names 'returncode must be an integer' 
PASS boolean return code: exit 2 
PASS boolean return code: diagnostic names 'returncode must be an integer' 
PASS non-integer runner_exit: exit 2 
PASS non-integer runner_exit: diagnostic names 'runner_exit must be an integer' 
PASS non-normalized path: exit 2 
PASS non-normalized path: diagnostic names 'not a normalized repository-relative path' 
PASS absolute path: exit 2 
PASS absolute path: diagnostic names 'not a normalized repository-relative path' 
PASS runner_exit nonzero: exit 1 
PASS runner_exit nonzero: diagnostic names 'runner_exit 1' 
PASS completed file failed: exit 1 
PASS completed file failed: diagnostic names 'tests/integration/test-b.py returned 3' 
PASS omitted file: exit 1 
PASS omitted file: diagnostic names 'tests/integration/test-e.py: omitted' 
PASS within-shard duplicate: exit 1 
PASS within-shard duplicate: diagnostic names 'duplicated within shard 1' 
PASS cross-shard duplicate: exit 1 
PASS cross-shard duplicate: diagnostic names 'tests/integration/test-a.py: completed 2 times' 
PASS unexpected file: exit 1 
PASS unexpected file: diagnostic names 'tests/integration/test-zzz.py: unexpected' 
PASS selected without completion: exit 1 
PASS selected without completion: diagnostic names 'selected but has no completed record' 
PASS completed without selection: exit 1 
PASS completed without selection: diagnostic names 'completed but not selected' 
PASS empty expected suite: exit 1 
PASS empty expected suite: diagnostic names 'no tests/integration/test-*.py' 
PASS selection union is not coverage: exit 1 
PASS selection union is not coverage: diagnostic names 'tests/integration/test-d.py: omitted' 
PASS all-success exact coverage passes 
PASS empty individual shards pass when the suite is covered 
PASS filter keeps only top-level tests/integration/test-*.py 
PASS validation does not mutate evidence 
PASS unit receipt with exact coverage passes: exit 0 
PASS an integration manifest is refused as a unit receipt: exit 1 
PASS an integration manifest is refused as a unit receipt: diagnostic names 'kind 'integration' is not unit' 
PASS a unit manifest is still refused under the integration default: exit 1 
PASS a unit manifest is still refused under the integration default: diagnostic names 'kind 'unit' is not integration' 
PASS a unit receipt for shard 1/2 is refused: exit 1 
PASS a unit receipt for shard 1/2 is refused: diagnostic names 'shard_count 2 is not 1' 
PASS a second unit shard is an extra manifest: exit 1 
PASS a second unit shard is an extra manifest: diagnostic names 'shard_index 2 outside 1..1' 
PASS an omitted unit file is refused: exit 1 
PASS an omitted unit file is refused: diagnostic names 'tests/unit/test-b.py: omitted' 
PASS an integration file in a unit receipt is unexpected: exit 1 
PASS an integration file in a unit receipt is unexpected: diagnostic names 'tests/integration/test-a.py: unexpected (not in the tested commit's unit suite)' 
PASS an empty unit suite names the unit pattern: exit 1 
PASS an empty unit suite names the unit pattern: diagnostic names 'no tests/unit/test-*.py' 
PASS a red unit record is refused: exit 1 
PASS a red unit record is refused: diagnostic names 'tests/unit/test-b.py returned 1' 
PASS a malformed unit receipt is malformed evidence: exit 2 
PASS a malformed unit receipt is malformed evidence: diagnostic names 'manifest must be a JSON object' 
PASS unit filter keeps only top-level tests/unit/test-*.py 
PASS the integration filter is the default 
PASS an unsupported kind cannot masquerade as a supported one 
0 failed
PASS test-integration-shard-validation.py
----- test-harness-yaml-corpus.py (exit 0, 0.16s) -----
ok    every shipped YAML parses (11 files across 2 roots: .harness=7, .claude/skills/harness/teams=4)
ok    the corpus under .harness is not empty (a scan that matches nothing passes vacuously)
ok    the corpus under .claude/skills/harness/teams is not empty (a scan that matches nothing passes vacuously)
ok    .claude/skills/harness/teams holds exactly 4 team definitions (FEAT-06 SC-05)
ok    detects ` #` opening a comment inside a flow sequence (the team-config.yaml bug)
ok    detects `: ` inside a multi-line plain scalar (the FEAT-04/05 bug)
ok    detects a sequence item opening with a backtick (the FEAT-03 bug)
ok    detects an unclosed flow sequence
ok    detects a DUPLICATED top-level key (safe_load accepts these; the harness does not)
ok    detects a duplicated key NESTED in a block (column-0 scans cannot see these)
ok    a malformed YAML in a feature's notes/ is EXEMPT (issue #628's recovered draft)
ok    the IDENTICAL body one directory up, as plan.yaml, is still flagged -- so the exemption is scoped and the scan is not simply dead
ok    a notes/ NOT under features/<id>/ is still covered
ok    a correctly quoted/folded file is NOT flagged
ok    detects a broken team definition under .agents/skills/harness/teams (SC-06)
ok    a finding names file:line:column, not just 'invalid'

16/16 checks passed.
PASS test-harness-yaml-corpus.py
----- test-issue-types.py (exit 0, 0.06s) -----
ok    type_for_change_type: bugfix -> Bug
ok    type_for_change_type: feature -> Task (D-18: a task sub-issue, whatever its diff shape)
ok    type_for_change_type: logic -> Task
ok    type_for_change_type: api -> Task
ok    type_for_change_type: cross_module -> Task
ok    type_for_change_type: frontend -> Task
ok    type_for_change_type: ai_behavior -> Task
ok    type_for_change_type: docs -> Task
ok    type_for_change_type: config -> Task
ok    type_for_change_type: scaffolding -> Task
ok    type_for_change_type: infra -> Task
ok    type_for_change_type: ci -> Task
ok    type_for_nature: bug -> Bug
ok    type_for_nature: chore -> Task
ok    type_for_nature: enhancement -> Feature
ok    type_for_parent: {} -> Feature
ok    type_for_change_type('hovercraft', {}) raises UnknownWorkNature
ok    ...message contains the offending value 'hovercraft'
ok    ...message contains 'no issue type is mapped'
ok    type_for_nature('hovercraft', {}) raises UnknownWorkNature
ok    ...message contains the offending value 'hovercraft'
ok    ...message contains 'no issue type is mapped'
ok    override renames Bug
ok    override renaming Bug leaves Task alone (fall-through)
ok    override renaming Task renames every change_type resolving to Task, including feature
ok    override renames parent
ok    override renames Task via a nature
ok    a change_type string is NOT an override key and must be ignored
ok    overrides_from_config({}) == {}
ok    overrides_from_config({'github': {}}) == {}
ok    overrides_from_config({'github': {'issue_types': 'not-a-map'}}) == {}
ok    overrides_from_config({'github': {'issue_types': {'Bug': 'Defect'}}}) == {'Bug': 'Defect'}
ok    a key outside the four legal keys is dropped by the loader
ok    classify_capability: exit 0, null issueTypes -> state absent
ok    classify_capability: exit 0, null issueTypes -> declared {}
ok    classify_capability: exit 0, null issueTypes -> message ''
ok    classify_capability: exit 0, populated nodes -> state available
ok    classify_capability: exit 0, populated nodes -> declared maps NAME to id
ok    classify_capability: exit 1, top-level errors array -> state query_failed
ok    classify_capability: exit 1, top-level errors array -> declared {}
ok    classify_capability: exit 1, top-level errors array -> message contains 'Could not resolve'
ok    classify_capability: exit 0, unparseable stdout -> state query_failed, never absent
ok    capability_query_args: first two elements are api, graphql
ok    capability_query_args: contains -f owner=owner
ok    capability_query_args: contains -f name=name
ok    capability_query_args: query element contains issueTypes(first:10)
ok    capability_query_args: query element contains nodes
ok    capability_query_args: query element contains id
ok    capability_query_args: query element contains name
ok    node_id_args: exact argv
ok    apply_type_args: starts api, graphql
ok    apply_type_args: query element contains updateIssue
ok    apply_type_args: query element contains issueTypeId
ok    apply_type_args: passes the node id as an -f value
ok    apply_type_args: passes the type id as an -f value
ok    missing_types(['Bug', 'Task'], {'Bug': 'IT_1'}) == ['Task']
ok    missing_types(['Bug'], {'Bug': 'IT_1'}) == []
ok    refusal_text: contains the type name 'Maintenance'
ok    refusal_text: contains 'github.issue_types.Task'
ok    refusal_text: contains the repo 'owner/name'

ALL PASSED
PASS test-issue-types.py
----- test-lead-stop-and-wake.py (exit 0, 0.07s) -----
reading bound site from /Users/molchairuangutai/GitHub/harness/.claude/worktrees/.pins/BUG-2566-stale-hook-detection--2026-11-27-05-validate-validator--harness-qa/.harness/harness/docs/DECISIONS.md
0 once-only occurrence(s) in .harness/harness/docs/DECISIONS.md
PASS case_detector_control_ONCE_RE
PASS case_detector_control_QUALIFIER_RE
reading coverage index from /Users/molchairuangutai/GitHub/harness/.claude/worktrees/.pins/BUG-2566-stale-hook-detection--2026-11-27-05-validate-validator--harness-qa/.harness/harness/docs/DECISIONS-INDEX.md
reading coverage entry from /Users/molchairuangutai/GitHub/harness/.claude/worktrees/.pins/BUG-2566-stale-hook-detection--2026-11-27-05-validate-validator--harness-qa/.harness/harness/docs/DECISIONS.md
PASS case_index_row
PASS case_entry_heading
PASS case_entry_scope

ALL PASS
PASS test-lead-stop-and-wake.py
----- test-harness-boundary.py (exit 0, 0.60s) -----
PASS marker_constant_exact_value
PASS root_from_script_four_levels_up_no_marker
PASS root_from_script_unchanged_when_marker_exists
PASS resolve_root_strict_override_with_marker_honoured
PASS resolve_root_strict_bad_override_falls_through_to_derived
PASS resolve_root_strict_bad_override_reported_on_stderr
harness_boundary: discarding HARNESS_PROJECT_DIR='/var/folders/y3/nd_jssrd5dq8lbds73f0fy5m0000gn/T/ht-yf4rwo9z/tmphcgd77t8' — it does not carry .harness/team-config.yaml. Falling back to the derived root '/var/folders/y3/nd_jssrd5dq8lbds73f0fy5m0000gn/T/ht-yf4rwo9z/tmpd3i5joed'.
PASS resolve_root_strict_neither_carries_marker_raises
PASS resolve_root_override_relative_normalises_to_same_absolute_path
PASS root_above_finds_marker_walking_up
PASS root_above_bare_dot_harness_does_not_satisfy
PASS root_above_nothing_above_returns_none
PASS worktree_for_feature_exact_basename_match
PASS worktree_for_feature_short_form_prefix_match
PASS worktree_for_feature_unrelated_id_returns_none
PASS worktree_for_feature_hyphen_boundary_not_crossed
PASS worktree_for_feature_two_candidates_raises_ambiguous
PASS worktree_for_feature_no_worktrees_dir_returns_none
PASS changed_state_root: canonical repo-tier plan.yaml derives the checkout
PASS changed_state_root: canonical flat feature.json derives the checkout
PASS changed_state_root: scratch/plan.yaml derives NO checkout
PASS changed_state_root: .harness/harness/features/notes/plan.yaml derives NO checkout
PASS changed_state_root: .harness/harness/features/FEAT-7-x/BRIEF.md derives NO checkout
PASS feedback is silent when the derived checkout carries no checker, even with HARNESS_PROJECT_DIR pointing at one (PF-e27f2ac2)
PASS feedback forwards BOTH streams' rows from the derived checkout's checker
PASS the checker is spawned with --changed, in the derived checkout, WITHOUT the session's HARNESS_PROJECT_DIR, and marked nested
PASS a writer inside a feedback run never re-enters the loop
PASS a clean --changed run (no output) yields no rows
PASS checkout_mismatch_non_feature_path_is_none
PASS checkout_mismatch_no_worktree_for_feature_is_none
PASS checkout_mismatch_correct_checkout_is_none
PASS checkout_mismatch_wrong_checkout_names_feature_and_expected_worktree
PASS feature_artifact_id_extracts_the_feature_segment
PASS checkout_mismatch_lets_ambiguous_worktree_reach_the_adapter
PASS load_repo_module_executes_and_returns_the_module
PASS load_repo_module_default_does_not_register
PASS load_repo_module_register_true_is_visible_during_exec
PASS load_repo_module_register_true_stays_registered_after_exec
PASS load_repo_module_registered_exec_failure_is_RepoModuleError
PASS load_repo_module_registered_exec_failure_carries_name_path_and_cause
PASS load_repo_module_registered_exec_failure_renders_the_original_type_and_text
PASS load_repo_module_unregistered_exec_failure_is_RepoModuleError
PASS load_repo_module_unregistered_exec_failure_carries_name_path_and_cause
PASS load_repo_module_unregistered_exec_failure_renders_the_original_type_and_text
PASS load_repo_module_missing_file_is_RepoModuleError
PASS load_repo_module_missing_file_carries_name_path_and_cause
PASS load_repo_module_missing_file_renders_the_original_type_and_text
PASS load_repo_module_no_loader_is_RepoModuleError
PASS load_repo_module_no_loader_carries_name_path_and_cause
PASS load_repo_module_no_loader_renders_the_original_type_and_text
PASS load_repo_module_exec_failure_removes_only_its_own_registration
PASS load_repo_module_exec_failure_restores_a_prior_registration
PASS load_repo_module_keyboard_interrupt_propagates_unchanged
PASS load_repo_module_keyboard_interrupt_still_undoes_its_registration
PASS load_repo_module_system_exit_propagates_unchanged
PASS load_repo_module_system_exit_still_undoes_its_registration
PASS load_repo_module_success_is_unchanged
PASS load_repo_module_by_name_imports_through_sys_path
PASS load_repo_module_by_name_absent_is_RepoModuleError
PASS load_repo_module_by_name_absent_carries_name_path_and_cause
PASS load_repo_module_by_name_absent_renders_the_original_type_and_text
PASS load_repo_module_call_failure_is_RepoModuleError
PASS load_repo_module_call_failure_carries_name_path_and_cause
PASS load_repo_module_call_failure_renders_the_original_type_and_text
PASS call_repo_module_passes_process_control_through
PASS call_repo_module_returns_the_result
PASS bug1304: short-form worktree prefix contributes to S
PASS bug1304: owner-root registry claim resolves by its feature
PASS bug1304: unresolved feature contributes no worktree
PASS bug1304: no claims yields an empty set
PASS bug1304: claims in two features yield both worktrees
PASS runtime lineage selects only the exact child's worktree
PASS runtime lineage rejects a sibling parent's claim
PASS bug1304: ambiguous feature worktrees propagate
PASS bug1304: unreadable linked registry refuses an outside destination
PASS bug1304: unreadable owner registry also refuses
PASS bug1304: proven destination is allowed with unrelated unreadable registry
PASS bug1304: refusal names every claim worktree and destination home
PASS bug1304: refusal never advises removing a worktree
PASS bug1304: expertise refusal routes to expertise_apply, never the shell CLI
PASS feat2225: repository-tier expertise refusal names the repository tier and segment
PASS real() keeps ONE namespace: an unresolvable target still sits under the resolved root
PASS real() is still TOTAL on an unresolvable input — it must not raise, or the whole hook body fails open at exit 1
PASS real() NEGATIVE CONTROL: a resolvable path is unchanged by the fallback
PASS run identity pattern matches marker
PASS run identity pattern is case insensitive
PASS run identity pattern rejects .harness/harness/features/F/runs/r1/state.yaml
PASS run identity pattern rejects .harness/harness/features/F/runs/r1/digest.md
PASS run identity pattern rejects .harness/harness/features/F/runs/.run-identity.json
PASS run identity pattern rejects tmp/runs/r1/.run-identity.json
PASS tests/unit/test-x.py is a control-plane target
PASS tests/integration/test-y.py is a control-plane target
PASS tests/manual/probe-z.py is a control-plane target
PASS tests/** is not a control-plane glob
PASS tests/unit/** is not a control-plane glob
PASS src/main.py remains product-side
PASS web/src/app.test.ts remains product-side
PASS run_dir_grant_globs_uses_aggregated_manifest_accessor
PASS run_dir_grant_globs_combines_all_role_and_shared_run_grants
PASS run_dir_grant_globs_live_nonempty
PASS run_dir_grant_globs_live_all_contain_runs_segment
PASS run_dir_grant_globs_live_sorted_deduped
PASS run_dir_grant_globs_synthetic_exact
PASS run_dir_grant_globs_absent_manifest_empty
PASS run_dir_grant_globs_garbage_manifest_empty
PASS run_dir_refs_finds_tail_in_absolute_path_and_dedupes_repeat
PASS run_dir_refs_empty_for_no_run_dir
PASS run_dir_slug_ok_accepts_t01-eng
PASS run_dir_slug_ok_accepts_plan-product
PASS run_dir_slug_ok_accepts_2026-08-26-2-plan-product
PASS run_dir_slug_ok_rejects_eng-t01
PASS run_dir_slug_ok_rejects_plan_product
PASS run_dir_slug_ok_empty_globs_is_false
PASS run_dir_forms_synthetic_exact
PASS classifier_repository: harness target keeps harness identity
PASS classifier_repository: product target keeps declared identity
PASS hook_guard_returns_mains_result
PASS hook_guard_open_returns_0_on_exception
PASS hook_guard_open_names_hook_and_failure_and_passing_through
PASS hook_guard_closed_returns_2_on_exception
PASS hook_guard_closed_says_BLOCKED
PASS hook_guard_lets_KeyboardInterrupt_escape
PASS hook_guard_lets_SystemExit_escape
PASS hook_guard_is_called_by_exactly_the_five_guarded_hooks
PASS run_hook_body_returns_0_when_the_body_falls_off
{"decision": "unavailable", "gate": "hookish", "reason": "the hook failed internally (RuntimeError: body defect)"}
PASS run_hook_body_open_passes_through_a_body_defect
PASS run_hook_body_closed_blocks_a_body_defect
PASS run_hook_body_lets_the_bodys_SystemExit_escape
PASS feat2274_emit_unavailable_exists
PASS feat2274_emitter_writes_exactly_one_json_line_with_exact_keys
PASS feat2274_hook_guard_open_emits_unavailable_once_and_returns_0
PASS feat2274_hook_guard_open_keeps_its_stderr_diagnostic
PASS feat2274_hook_guard_closed_unchanged_exit_2_no_unavailable
PASS feat2274_hook_guard_normal_return_emits_nothing
PASS feat2274_hook_guard_without_script_emits_no_unavailable
PASS feat2274_hook_guard_lets_SystemExit_escape_without_unavailable
PASS feat2274_run_hook_body_passes_its_path_as_the_gate
PASS linked_worktrees_skips_a_non_utf8_pointer
PASS linked_worktrees_lets_an_unrelated_RuntimeError_escape
PASS run_dir_grant_globs_lets_an_unrelated_RuntimeError_escape
PASS resolve_fleet_blocks_exit_2_on_a_fleet_that_does_not_load
PASS resolve_fleet_lets_an_unrelated_RuntimeError_escape

ALL PASS
PASS test-harness-boundary.py
----- test-check-skill-refs.py (exit 0, 7.81s) -----
ok   committed_tree_is_clean
ok   catches_deleted_dec
ok   catches_unimplemented_inv
ok   catches_missing_path
ok   catches_missing_heading
ok   catches_unknown_name
ok   catches_claude_spelling
ok   every_finding_names_the_planted_file
ok   package_only_number_is_implemented
ok   unspelled_number_is_still_a_finding

all checks passed
PASS test-check-skill-refs.py
----- test-orchestrator-playbook.py (exit 0, 0.04s) -----
reading playbook from /Users/molchairuangutai/GitHub/harness/.claude/worktrees/.pins/BUG-2566-stale-hook-detection--2026-11-27-05-validate-validator--harness-qa/.agents/skills/harness/SKILL.md
PASS case1_absence_receive_the_team_digest
PASS case2_absence_loop_until_done
PASS case4_presence_reads_your
PASS case4_presence_appends_one
PASS case4_absence_claude_sidecar_probe
PASS case4_absence_hardcoded_threshold_numeral
PASS case5_presence_orchestrator_context_warn_tokens
PASS case6_presence_orchestrator_context_warn_tokens_exists_at_all
PASS case6_absence_context_warn_tokens_never_reads_as_a_refusal_trigger
PASS case7_absence_record_your_phase_in
PASS case8_presence_record_your_status_in
PASS case9a_playbook_names_set_task_station
PASS case9b_playbook_never_prescribes_an_Edit_of_plan_yaml
PASS case10_blocking_host_blocking_boundary
PASS case10_blocking_host_zero_polling
PASS case10_blocking_host_replacement_parent_registry
PASS case10_no_suspended_turn_end_anywhere

ALL PASS
PASS test-orchestrator-playbook.py
----- test-harness-merge-journal.py (exit 0, 1.01s) -----
PASS - api: JOURNAL_SUFFIX names the per-primary journal
PASS - api: JournalPending stores journal, cause, replay defaulting false
PASS - api: JournalPending message is '<cause type>: <cause>'
PASS - api: JournalPending carries replay=True
PASS - pair: transforms receive both bases (None for an absent secondary)
PASS - pair: success writes both images, no journal and no temp file
PASS - pair: primary refusal propagates unchanged
PASS - pair: primary refusal leaves both files byte-identical and no journal
PASS - pair: secondary refusal propagates unchanged
PASS - pair: secondary refusal leaves both files byte-identical and no journal
PASS - pair: secondary ValueError propagates unchanged
PASS - pair: secondary ValueError leaves both files byte-identical and no journal
PASS - pair: a held secondary lock refuses with code 6 naming LOCKED
PASS - pair: the LOCKED refusal writes nothing
PASS - pair: members in two directories raise ValueError
PASS - pair: the same file twice raises ValueError
PASS - pair: a ValueError writes nothing
PASS - pending: a secondary replace failure raises JournalPending
PASS - pending: journal attribute is the primary plus JOURNAL_SUFFIX, cause the OSError, replay false
PASS - pending: primary at after, secondary at before, journal present
PASS - pending: the journal is schema harness-merge-journal/1, members primary then secondary
PASS - pending: the journal records before/after hashes and the after images
PASS - pending: recover_journals(primary) rolls forward
PASS - pending: both files converge to after and the journal is gone
PASS - torn: recover_journals(primary) returns True
PASS - torn [primary at after] via recover_journals(primary): converges, journal removed
PASS - torn [primary at after] via recover_journals(primary): a second recover_journals is False, no byte changes
PASS - torn: locked_update(primary) transform sees the after image
PASS - torn [primary at after] via locked_update(primary): converges, journal removed
PASS - torn [primary at after] via locked_update(primary): a second recover_journals is False, no byte changes
PASS - torn: locked_update(secondary) transform sees the after image
PASS - torn [primary at after] via locked_update(secondary): converges, journal removed
PASS - torn [primary at after] via locked_update(secondary): a second recover_journals is False, no byte changes
PASS - torn: recover_journals(primary) returns True
PASS - torn [secondary at after] via recover_journals(primary): converges, journal removed
PASS - torn [secondary at after] via recover_journals(primary): a second recover_journals is False, no byte changes
PASS - torn: locked_update(primary) transform sees the after image
PASS - torn [secondary at after] via locked_update(primary): converges, journal removed
PASS - torn [secondary at after] via locked_update(primary): a second recover_journals is False, no byte changes
PASS - torn: locked_update(secondary) transform sees the after image
PASS - torn [secondary at after] via locked_update(secondary): converges, journal removed
PASS - torn [secondary at after] via locked_update(secondary): a second recover_journals is False, no byte changes
PASS - torn: recover_journals(primary) returns True
PASS - torn [both at after] via recover_journals(primary): converges, journal removed
PASS - torn [both at after] via recover_journals(primary): a second recover_journals is False, no byte changes
PASS - torn: locked_update(primary) transform sees the after image
PASS - torn [both at after] via locked_update(primary): converges, journal removed
PASS - torn [both at after] via locked_update(primary): a second recover_journals is False, no byte changes
PASS - torn: locked_update(secondary) transform sees the after image
PASS - torn [both at after] via locked_update(secondary): converges, journal removed
PASS - torn [both at after] via locked_update(secondary): a second recover_journals is False, no byte changes
PASS - diverged: recover_journals(primary) refuses with code 5 naming JOURNAL DIVERGED
PASS - diverged: recover_journals(primary) leaves both files and the journal byte-identical
PASS - diverged: recover_journals(secondary) refuses with code 5 naming JOURNAL DIVERGED
PASS - diverged: recover_journals(secondary) leaves both files and the journal byte-identical
PASS - diverged: locked_update(primary) refuses with code 5 naming JOURNAL DIVERGED
PASS - diverged: locked_update(primary) leaves both files and the journal byte-identical
PASS - diverged: locked_update(secondary) refuses with code 5 naming JOURNAL DIVERGED
PASS - diverged: locked_update(secondary) leaves both files and the journal byte-identical
PASS - diverged: no caller transform ran
PASS - diverged: locked_update on a third file in the directory succeeds
PASS - diverged: the third write leaves both members and the journal byte-identical
PASS - unreadable: a truncated journal refuses with code 5 naming JOURNAL UNREADABLE
PASS - unreadable: it fails closed for a third file in the directory too
PASS - unreadable: nothing is written
PASS - unreadable: a journal listing the primary twice refuses with code 5 naming JOURNAL UNREADABLE, never LOCKED
PASS - unreadable: a journal listing the primary twice writes nothing
PASS - unreadable: a journal whose first member is not its primary refuses with code 5 naming JOURNAL UNREADABLE, never LOCKED
PASS - unreadable: a journal whose first member is not its primary writes nothing
PASS - unreadable: a wrong schema refuses with code 5 naming JOURNAL UNREADABLE
PASS - unreadable: a wrong schema writes nothing
PASS - unreadable: an empty member list refuses with code 5 naming JOURNAL UNREADABLE
PASS - unreadable: an empty member list writes nothing
PASS - unreadable: a member name with a path separator refuses with code 5 naming JOURNAL UNREADABLE
PASS - unreadable: a member name with a path separator writes nothing
PASS - unreadable: a member name '..' refuses with code 5 naming JOURNAL UNREADABLE
PASS - unreadable: a member name '..' writes nothing
PASS - unreadable: an uppercase-hex before_sha256 refuses with code 5 naming JOURNAL UNREADABLE
PASS - unreadable: an uppercase-hex before_sha256 writes nothing
PASS - unreadable: an after_b64 that does not hash to after_sha256 refuses with code 5 naming JOURNAL UNREADABLE
PASS - unreadable: an after_b64 that does not hash to after_sha256 writes nothing
PASS - unreadable: an after_b64 that is not base64 refuses with code 5 naming JOURNAL UNREADABLE
PASS - unreadable: an after_b64 that is not base64 writes nothing
PASS - replay: recover_journals(primary) raises JournalPending with replay True, that journal and that OSError
PASS - replay: primary at after, secondary at before, journal present
PASS - replay: locked_pair_update raises JournalPending with replay True, that journal and that OSError
PASS - replay: locked_pair_update called neither transform
PASS - replay: the restored replace_bytes converges
PASS - replay: both at after, journal gone
PASS - replay: a second recover_journals returns False
PASS - interleave (i): the wrapper reached the primary's lock first
PASS - interleave (i): a replaced generation replays without refusal
PASS - interleave (i): both at J2's after images, no journal
PASS - interleave (ii): the wrapper reached the primary's lock first
PASS - interleave (ii): a fresh generation is replayed, never unlinked unreplayed
PASS - interleave (iii): the wrapper reached the primary's lock first
PASS - interleave (iii): a vanished journal returns False
PASS - interleave (iii): no byte changes after the wrapper's
PASS - interleave (iv): the wrapper reached the primary's lock first
PASS - interleave (iv): a generation that no longer names X returns False
PASS - interleave (iv): plan, ledger, X and J2 stay byte-identical to the wrapper's result
PASS - unreadable: a member with no before_sha256 key refuses with code 5 naming the journal and the key
PASS - unreadable: the missing key never recreates the absent ledger; nothing is written
PASS - unreadable: the missing key via locked_update(feature.json) refuses with code 5 naming the journal and the key
PASS - unreadable: via locked_update(feature.json) the absent ledger is not recreated; nothing is written
PASS - absent: an explicit null before_sha256 still records an absent member, which the replay creates
PASS - bound: a one-member journal via recover_journals(primary) refuses with code 5 naming JOURNAL UNREADABLE and the journal
PASS - bound: a one-member journal via recover_journals(primary) writes nothing
PASS - bound: a one-member journal via locked_update(primary) refuses with code 5 naming JOURNAL UNREADABLE and the journal
PASS - bound: a one-member journal via locked_update(primary) writes nothing
PASS - bound: a journal binding a sibling in feature.json's place via recover_journals(primary) refuses with code 5 naming JOURNAL UNREADABLE and the journal
PASS - bound: a journal binding a sibling in feature.json's place via recover_journals(primary) writes nothing
PASS - bound: a journal binding a sibling in feature.json's place via locked_update(primary) refuses with code 5 naming JOURNAL UNREADABLE and the journal
PASS - bound: a journal binding a sibling in feature.json's place via locked_update(primary) writes nothing
PASS - bound: a three-member journal via recover_journals(primary) refuses with code 5 naming JOURNAL UNREADABLE and the journal
PASS - bound: a three-member journal via recover_journals(primary) writes nothing
PASS - bound: a three-member journal via locked_update(primary) refuses with code 5 naming JOURNAL UNREADABLE and the journal
PASS - bound: a three-member journal via locked_update(primary) writes nothing
PASS - foreign: garbage evil.harness-merge.journal via locked_update(plan.yaml) succeeds, writes, foreign file untouched
PASS - foreign: garbage evil.harness-merge.journal via locked_update(plan.yaml) takes only ['plan.yaml.lock']
PASS - foreign: garbage evil.harness-merge.journal via locked_update(feature.json) succeeds, writes, foreign file untouched
PASS - foreign: garbage evil.harness-merge.journal via locked_update(feature.json) takes only ['feature.json.lock']
PASS - foreign: garbage evil.harness-merge.journal via locked_pair_update succeeds, writes, foreign file untouched
PASS - foreign: garbage evil.harness-merge.journal via locked_pair_update takes only ['plan.yaml.lock', 'feature.json.lock']
PASS - foreign: well-formed BRIEF.md.harness-merge.journal via locked_update(plan.yaml) succeeds, writes, foreign file untouched
PASS - foreign: well-formed BRIEF.md.harness-merge.journal via locked_update(plan.yaml) takes only ['plan.yaml.lock']
PASS - foreign: well-formed BRIEF.md.harness-merge.journal via locked_update(feature.json) succeeds, writes, foreign file untouched
PASS - foreign: well-formed BRIEF.md.harness-merge.journal via locked_update(feature.json) takes only ['feature.json.lock']
PASS - foreign: well-formed BRIEF.md.harness-merge.journal via locked_pair_update succeeds, writes, foreign file untouched
PASS - foreign: well-formed BRIEF.md.harness-merge.journal via locked_pair_update takes only ['plan.yaml.lock', 'feature.json.lock']
PASS - foreign: well-formed feature.json.harness-merge.journal via locked_update(plan.yaml) succeeds, writes, foreign file untouched
PASS - foreign: well-formed feature.json.harness-merge.journal via locked_update(plan.yaml) takes only ['plan.yaml.lock']
PASS - foreign: well-formed feature.json.harness-merge.journal via locked_update(feature.json) succeeds, writes, foreign file untouched
PASS - foreign: well-formed feature.json.harness-merge.journal via locked_update(feature.json) takes only ['feature.json.lock']
PASS - foreign: well-formed feature.json.harness-merge.journal via locked_pair_update succeeds, writes, foreign file untouched
PASS - foreign: well-formed feature.json.harness-merge.journal via locked_pair_update takes only ['plan.yaml.lock', 'feature.json.lock']
PASS - foreign: recover_journals(plan.yaml) with only foreign journals returns False
PASS - foreign: recover_journals(feature.json) with only foreign journals returns False
PASS - foreign: recover_journals(notes.txt) with only foreign journals returns False
PASS - foreign: recover_journals changes no byte
PASS - torn: recover_journals(primary) returns True
PASS - foreign: torn [primary at after] via recover_journals(primary) beside every foreign journal converges, the real journal removed, the foreign files untouched
PASS - torn: locked_update(primary) transform sees the after image
PASS - foreign: torn [primary at after] via locked_update(primary) beside every foreign journal converges, the real journal removed, the foreign files untouched
PASS - torn: locked_update(secondary) transform sees the after image
PASS - foreign: torn [primary at after] via locked_update(secondary) beside every foreign journal converges, the real journal removed, the foreign files untouched
PASS - torn: recover_journals(primary) returns True
PASS - foreign: torn [secondary at after] via recover_journals(primary) beside every foreign journal converges, the real journal removed, the foreign files untouched
PASS - torn: locked_update(primary) transform sees the after image
PASS - foreign: torn [secondary at after] via locked_update(primary) beside every foreign journal converges, the real journal removed, the foreign files untouched
PASS - torn: locked_update(secondary) transform sees the after image
PASS - foreign: torn [secondary at after] via locked_update(secondary) beside every foreign journal converges, the real journal removed, the foreign files untouched
PASS - torn: recover_journals(primary) returns True
PASS - foreign: torn [both at after] via recover_journals(primary) beside every foreign journal converges, the real journal removed, the foreign files untouched
PASS - torn: locked_update(primary) transform sees the after image
PASS - foreign: torn [both at after] via locked_update(primary) beside every foreign journal converges, the real journal removed, the foreign files untouched
PASS - torn: locked_update(secondary) transform sees the after image
PASS - foreign: torn [both at after] via locked_update(secondary) beside every foreign journal converges, the real journal removed, the foreign files untouched
PASS - foreign: an unreadable real journal via locked_update(plan.yaml) refuses with code 5 naming it
PASS - foreign: an unreadable real journal via locked_update(feature.json) refuses with code 5 naming it
PASS - foreign: an unreadable real journal via locked_pair_update refuses with code 5 naming it
PASS - foreign: an unreadable real journal via locked_update(notes.txt) refuses with code 5 naming it
PASS - foreign: the unreadable real journal's refusals write nothing
PASS - case: the pair is pending under the variant spelling (folds case: True)
PASS - case: recover_journals rolls the pending pair forward
PASS - pair: a sibling in feature.json's place raises ValueError
PASS - pair: a sibling in feature.json's place writes nothing and leaves no journal
PASS - pair: the pair reversed raises ValueError
PASS - pair: the pair reversed writes nothing and leaves no journal
PASS - bound: a feature.json write nested in a locked plan write succeeds
PASS - entry: a dangling symlink via locked_update(plan) refuses with code 5 naming JOURNAL UNREADABLE and the journal, never hangs
PASS - entry: a dangling symlink via locked_update(plan) writes nothing
PASS - entry: a dangling symlink via locked_update(feature.json) refuses with code 5 naming JOURNAL UNREADABLE and the journal, never hangs
PASS - entry: a dangling symlink via locked_update(feature.json) writes nothing
PASS - entry: a symlink to a well-formed journal via recover_journals(plan) refuses with code 5 naming JOURNAL UNREADABLE and the journal, never hangs
PASS - entry: a symlink to a well-formed journal via recover_journals(plan) writes nothing
PASS - entry: a FIFO via recover_journals(plan) refuses with code 5 naming JOURNAL UNREADABLE and the journal, never hangs
PASS - entry: a FIFO via recover_journals(plan) writes nothing
PASS - entry: a directory via locked_update(plan) refuses with code 5 naming JOURNAL UNREADABLE and the journal, never hangs
PASS - entry: a directory via locked_update(plan) writes nothing
PASS - entry: a directory via locked_update(feature.json) refuses with code 5 naming JOURNAL UNREADABLE and the journal, never hangs
PASS - entry: a directory via locked_update(feature.json) writes nothing
PASS - entry: a directory via recover_journals(plan) refuses with code 5 naming JOURNAL UNREADABLE and the journal, never hangs
PASS - entry: a directory via recover_journals(plan) writes nothing
PASS - entry: a directory via recover_journals(feature.json) refuses with code 5 naming JOURNAL UNREADABLE and the journal, never hangs
PASS - entry: a directory via recover_journals(feature.json) writes nothing
PASS - foreign: a FIFO under another journal name via locked_update(notes.txt) returns, never hangs
PASS - foreign: via locked_update(notes.txt) the write lands and the FIFO is left in place
PASS - foreign: a FIFO under another journal name via locked_update(plan) returns, never hangs
PASS - foreign: via locked_update(plan) the write lands and the FIFO is left in place
PASS - fifo swap via recover_journals(plan): the swap happened after the lstat, before the open
PASS - fifo swap via recover_journals(plan): refuses with code 5 naming JOURNAL UNREADABLE and the journal
PASS - fifo swap via recover_journals(plan): both members untouched
PASS - fifo swap via recover_journals(plan): the FIFO is left in place, its record unread
PASS - fifo swap via locked_update(feature.json): the swap happened after the lstat, before the open
PASS - fifo swap via locked_update(feature.json): refuses with code 5 naming JOURNAL UNREADABLE and the journal
PASS - fifo swap via locked_update(feature.json): both members untouched
PASS - fifo swap via locked_update(feature.json): the FIFO is left in place, its record unread
PASS - bounded: a 5000-character member name refuses with code 5 naming the journal
PASS - bounded: a 5000-character member name is echoed truncated and escaped
PASS - bounded: a 5000-character misbound member refuses with code 5 naming the journal
PASS - bounded: a 5000-character misbound member is echoed truncated and escaped
PASS - 202/202 checks passed
PASS test-harness-merge-journal.py
----- test-plan-merge-first-station.py (exit 0, 0.12s) -----
PASS a status-less task gains its first station at its field indent: exit 0 
PASS a status-less task gains its first station at its field indent: the whole file is exactly the expected bytes 
PASS a status-less task gains its first station at its field indent: reports its outcome 
PASS a status-less task gains its first station at its field indent: prints APPLIED only on success 
PASS an existing status is rewritten and every other byte is unchanged: exit 0 
PASS an existing status is rewritten and every other byte is unchanged: the whole file is exactly the expected bytes 
PASS an existing status is rewritten and every other byte is unchanged: reports its outcome 
PASS an existing status is rewritten and every other byte is unchanged: prints APPLIED only on success 
PASS a genuinely absent task refuses with exit 3 and writes nothing: exit 3 
PASS a genuinely absent task refuses with exit 3 and writes nothing: the whole file is exactly the expected bytes 
PASS a genuinely absent task refuses with exit 3 and writes nothing: reports its outcome 
PASS a genuinely absent task refuses with exit 3 and writes nothing: prints APPLIED only on success 
PASS the first station sits inside T-01's own mapping, before T-02 
PASS T-01's verify prose keeps its own `status: prose` line 
PASS the absent-task refusal never blames a status line 
PASS the first-station insert on a signed plan succeeds 
PASS the signed approval block is byte-identical after the insert 
PASS test-plan-merge-first-station.py
PASS test-plan-merge-first-station.py
----- test-no-distribution.py (exit 0, 0.84s) -----
PASS case1_absence_no_deploy_sh_tracked_anywhere
PASS case1_absence_no_harness_deploy_command
PASS case1_presence_canonical_four_doors_survive
PASS case1_presence_check_plan_routes_survives
PASS case1_presence_factory_workspace_survives
PASS case2_absence_no_unswept_distribution_tokens
PASS case2_presence_scan_reached_the_tree
PASS case3_presence_fleet_yaml_safe_loads
PASS case3_absence_harness_is_not_a_fleet_member
PASS case3_absence_no_board_in_fleet
PASS case3_absence_no_registry_json_under_harness
PASS case4_absence_no_dec12_heading
PASS case4_absence_no_stale_marker_reintroduced
PASS case4_presence_exactly_one_dec113_heading
PASS case4_presence_dec113_precedence_rule_survives
PASS case4_absence_no_dec12_references_under_docs
PASS case4_control_docs_walk_reached_decisions
PASS case4_presence_exactly_one_dec113_index_row
PASS case4_absence_no_dec12_index_row
PASS board_lives_per_repo_not_fleet_level
PASS case6_absence_the_env_chain_occurs_nowhere
PASS case6_presence_the_resolver_defines_all_four
PASS case6_presence_sixteen_files_reach_the_resolver
PASS case6_absence_harness_root_is_gone
PASS case6_absence_repo_root_from_script_is_gone
PASS case6_absence_root_from_is_gone
PASS case6_absence_resolve_repo_root_is_gone
PASS case6_absence_wayfind_defines_no_root_of_its_own
PASS case6_presence_worktree_owner_survives
PASS case6_presence_main_checkout_resolver_survives

ALL PASS
PASS test-no-distribution.py
----- test-plan-merge-union-head.py (exit 0, 0.10s) -----
PASS decisions: [] gaining an item merges without a refusal 
PASS decisions: [] gains the proposal's block head, not the inline [] 
PASS decisions: [] merged plan reloads with the added item 
PASS tasks: [] gaining an item merges without a refusal 
PASS tasks: [] gains the proposal's block head, not the inline [] 
PASS tasks: [] merged plan reloads with the added item 
PASS a decisions base with items merges D-02 
PASS a decisions base with items keeps its own head line 
PASS a decisions base with items carries D-01 then D-02 
PASS test-plan-merge-union-head.py
PASS test-plan-merge-union-head.py
----- test-harness-config.py (exit 0, 1.33s) -----
............
----------------------------------------------------------------------
Ran 12 tests in 1.196s

OK
PASS test-harness-config.py
----- test-run-identity.py (exit 0, 0.06s) -----
PASS fresh seed is recorded
PASS seed has exact seven keys
PASS seed values are retained
PASS second seed is refused
PASS second seed leaves bytes unchanged
PASS missing directory seed fails open
PASS absent marker is None
PASS truncated marker is unreadable
PASS array marker is unreadable
PASS invalid UTF-8 marker is unreadable
PASS minted uid shape
PASS minted uids are distinct
PASS uid injection succeeds
PASS uid injection preserves text and parses
PASS existing uid is not replaced
PASS existing uid bytes unchanged
PASS separator newline inserted
PASS missing checkpoint fails open
PASS identical seed fields agree
PASS run id conflict names both values
PASS squad conflict names field and values
PASS run uid is not a seed conflict
PASS born-null run_id stays writable
PASS born-null squad stays writable
PASS legacy prior without uid is allowed
PASS legacy null uid is allowed
PASS same uid is allowed
PASS different uid reason names both
PASS missing incoming uid explains recovery
PASS an unwritable run dir is False, not a raise
PASS an unrelated RuntimeError escapes record_seed
PASS the temp file is still cleaned up after the escape
PASS test-run-identity.py
----- test-probe-handoff-comprehension.py (exit 0, 0.28s) -----
..handoff comprehension probe: DRY RUN
model: test-model
arms: as-written, done-when-stripped
questions:
- What is the one immediate next action?
- What exact scope must be completed?
- Which authorities define when that action is complete?
- What evidence would show that every authority is satisfied?
notes:
- /private/var/folders/y3/nd_jssrd5dq8lbds73f0fy5m0000gn/T/ht-8e_fx0cr/tmp9r2kssj6/.harness/harness/features/FEAT-test/notes/handoff-valid.md
planned model calls: 2 (not executed)
..note: /var/folders/y3/nd_jssrd5dq8lbds73f0fy5m0000gn/T/ht-8e_fx0cr/tmppch60brn/handoff-repository-outside.md
error: refusing note: path is not a feature handoff note
handoff comprehension probe: REAL RUN
model: test-model
arm labels: as-written, done-when-stripped
total evidence:
arm: as-written; coverage: 0/0; complete answers: 0/0
arm: done-when-stripped; coverage: 0/0; complete answers: 0/0
all complete answers: 0/0
note: /var/folders/y3/nd_jssrd5dq8lbds73f0fy5m0000gn/T/ht-8e_fx0cr/tmp79h150gb/handoff-absolute-outside.md
error: refusing note: path is not a feature handoff note
handoff comprehension probe: REAL RUN
model: test-model
arm labels: as-written, done-when-stripped
total evidence:
arm: as-written; coverage: 0/0; complete answers: 0/0
arm: done-when-stripped; coverage: 0/0; complete answers: 0/0
all complete answers: 0/0
note: /var/folders/y3/nd_jssrd5dq8lbds73f0fy5m0000gn/T/ht-8e_fx0cr/tmppch60brn/.harness/harness/features/FEAT-test/notes/../../../../../outside/handoff-traversal.md
error: refusing note: path is not a feature handoff note
handoff comprehension probe: REAL RUN
model: test-model
arm labels: as-written, done-when-stripped
total evidence:
arm: as-written; coverage: 0/0; complete answers: 0/0
arm: done-when-stripped; coverage: 0/0; complete answers: 0/0
all complete answers: 0/0
..note: /var/folders/y3/nd_jssrd5dq8lbds73f0fy5m0000gn/T/ht-8e_fx0cr/tmpo5mmjgls/.harness/harness/features/FEAT-test/notes/handoff-directory.md
error: refusing note: target is not a regular file
handoff comprehension probe: REAL RUN
model: test-model
arm labels: as-written, done-when-stripped
total evidence:
arm: as-written; coverage: 0/0; complete answers: 0/0
arm: done-when-stripped; coverage: 0/0; complete answers: 0/0
all complete answers: 0/0
.note: /var/folders/y3/nd_jssrd5dq8lbds73f0fy5m0000gn/T/ht-8e_fx0cr/tmp86inbw9f/.harness/harness/features/FEAT-test/notes/handoff-link.md
error: refusing note: symlinks are not allowed
handoff comprehension probe: REAL RUN
model: test-model
arm labels: as-written, done-when-stripped
total evidence:
arm: as-written; coverage: 0/0; complete answers: 0/0
arm: done-when-stripped; coverage: 0/0; complete answers: 0/0
all complete answers: 0/0
note: /var/folders/y3/nd_jssrd5dq8lbds73f0fy5m0000gn/T/ht-8e_fx0cr/tmp86inbw9f/.harness/harness/features/FEAT-test/notes/handoff-link.md
error: refusing note: symlinks are not allowed
handoff comprehension probe: REAL RUN
model: test-model
arm labels: as-written, done-when-stripped
total evidence:
arm: as-written; coverage: 0/0; complete answers: 0/0
arm: done-when-stripped; coverage: 0/0; complete answers: 0/0
all complete answers: 0/0
.handoff comprehension probe: REAL RUN
model: test-model
arm labels: as-written, done-when-stripped
note: /private/var/folders/y3/nd_jssrd5dq8lbds73f0fy5m0000gn/T/ht-8e_fx0cr/tmpc2viso7b/.harness/harness/features/FEAT-test/notes/handoff-valid.md
note sha256: 445da21d1b0668eeb9b7a3958ee14ec14fe2434ba4ac8a539a8493924f4066a3
required facts (1):
- safe
arm: as-written
coverage: 1/1
covers every fact: yes
answer:
safe
arm: done-when-stripped
coverage: 1/1
covers every fact: yes
answer:
safe
note complete answers: 2/2
total evidence:
arm: as-written; coverage: 1/1; complete answers: 1/1
arm: done-when-stripped; coverage: 1/1; complete answers: 1/1
all complete answers: 2/2
.note: /var/folders/y3/nd_jssrd5dq8lbds73f0fy5m0000gn/T/ht-8e_fx0cr/tmp6vjxdco5/.harness/harness/features/FEAT-test/notes/not-a-handoff.md
error: refusing note: path is not a feature handoff note
handoff comprehension probe: REAL RUN
model: test-model
arm labels: as-written, done-when-stripped
total evidence:
arm: as-written; coverage: 0/0; complete answers: 0/0
arm: done-when-stripped; coverage: 0/0; complete answers: 0/0
all complete answers: 0/0
note: /var/folders/y3/nd_jssrd5dq8lbds73f0fy5m0000gn/T/ht-8e_fx0cr/tmp6vjxdco5/.harness/harness/features/FEAT-test/notes/handoff-oversized.md
error: refusing note: note exceeds 1048576 bytes
handoff comprehension probe: REAL RUN
model: test-model
arm labels: as-written, done-when-stripped
total evidence:
arm: as-written; coverage: 0/0; complete answers: 0/0
arm: done-when-stripped; coverage: 0/0; complete answers: 0/0
all complete answers: 0/0
.
----------------------------------------------------------------------
Ran 10 tests in 0.048s

OK
PASS test-probe-handoff-comprehension.py
----- test-session-accessor-probe.py (exit 0, 0.07s) -----
ok   identity: nested task child transcript
ok   identity: flat main transcript
ok   identity: empty string
ok   identity: None
ok   identity: non-string
ok   identity: tryCall 'undefined'
ok   identity: tryCall 'null'
ok   identity: tryCall threw
ok   identity: tryCall no-target
ok   identity: relative nested-looking path
ok   identity: relative flat path
ok   identity: nested dir, wrong extension
ok   identity: flat, wrong extension
ok   identity: bare .jsonl name
ok   identity: trailing slash
ok   session_file: string path
ok   session_file: no probed
ok   session_file: probed is null
ok   session_file: getSessionFile missing
ok   session_file: non-string not stringified
ok   measurement: tokens int
ok   measurement: tokens zero
ok   measurement: tokens float
ok   measurement: tokens bool True
ok   measurement: tokens bool False
ok   measurement: tokens null
ok   measurement: tokens absent
ok   measurement: tokens NaN
ok   measurement: tokens +inf
ok   measurement: tokens -inf
ok   measurement: tokens numeric string
ok   measurement: tokens list
ok   measurement: all finite
ok   measurement: usage null
ok   measurement: usage absent
ok   measurement: usage a string
ok   measurement: contextWindow string
ok   measurement: contextWindow absent
ok   measurement: percent NaN
ok   measurement: percent bool
ok   measurement: the actual numbers are returned unchanged
ok   independence: tokens int, usageDefined=True
ok   independence: tokens int, usageDefined=False
ok   independence: tokens zero, usageDefined=True
ok   independence: tokens zero, usageDefined=False
ok   independence: tokens float, usageDefined=True
ok   independence: tokens float, usageDefined=False
ok   independence: tokens bool True, usageDefined=True
ok   independence: tokens bool True, usageDefined=False
ok   independence: tokens bool False, usageDefined=True
ok   independence: tokens bool False, usageDefined=False
ok   independence: tokens null, usageDefined=True
ok   independence: tokens null, usageDefined=False
ok   independence: tokens absent, usageDefined=True
ok   independence: tokens absent, usageDefined=False
ok   independence: tokens NaN, usageDefined=True
ok   independence: tokens NaN, usageDefined=False
ok   independence: tokens +inf, usageDefined=True
ok   independence: tokens +inf, usageDefined=False
ok   independence: tokens -inf, usageDefined=True
ok   independence: tokens -inf, usageDefined=False
ok   independence: tokens numeric string, usageDefined=True
ok   independence: tokens numeric string, usageDefined=False
ok   independence: tokens list, usageDefined=True
ok   independence: tokens list, usageDefined=False
ok   scenario: #2194: nested numeric child + flat numeric main
ok   scenario: usageDefined lies on both rows; identity holds
ok   scenario: child usage undefined
ok   scenario: child tokens NaN
ok   scenario: child tokens bool
ok   scenario: main missing is a failure, not optional
ok   scenario: child missing
ok   scenario: child path malformed
ok   scenario: child reported a flat path
ok   scenario: child and main share one session id
ok   scenario: no observations
ok   scenario: the checks are case3..case6 in order
ok   structure: the probe compiles exactly one session-file pattern
ok   structure: the nested pattern is the module-level constant is_nested uses
ok   structure: observation_checks never reads usageDefined
ok   structure: is_nested never reads usageDefined
ok   structure: is_flat_main never reads usageDefined
PASS - 0 failing
PASS test-session-accessor-probe.py
----- test-structure-audit-index.py (exit 0, 0.06s) -----
PASS audit_modules_load_from_the_bin_under_test
PASS index_nodes_are_ast_walk_order
PASS index_parent_links_match
PASS index_functions_match_ast_walk
PASS index_calls_match_ast_walk
PASS index_handlers_match_ast_walk
PASS index_tries_match_ast_walk
PASS index_literal_candidates_match_ast_walk
PASS index_program_texts_are_the_try_except_strings
PASS within_Call_equals_ast_walk_of_the_subject
PASS within_Constant_equals_ast_walk_of_the_subject
PASS input_literals_skip_fstring_parts
PASS observed_resources_read_the_spawned_argv
PASS called_names_map_ctx_methods
PASS call_symbol_is_the_innermost_function
PASS broad_count_is_own_handlers_plus_embedded_program
PASS session_parses_an_embedded_program_once
PASS prose_with_both_keywords_is_not_a_program
PASS session_index_is_built_once_per_file
PASS session_reraises_the_same_parse_error_to_every_asker
PASS session_text_raises_for_an_absent_file
PASS clean_root_has_no_broad_catch_finding
PASS second_root_is_audited_from_its_own_sources
PASS first_root_is_still_clean_after_the_second
PASS an_edit_between_invocations_is_seen
PASS no_session_or_index_is_retained_at_module_scope

ALL PASS
PASS test-structure-audit-index.py
----- test-plan-depends-on.py (exit 0, 1.15s) -----
  ok  a depends_on entry naming an absent task id is rejected, naming both ids
  ok  a depends_on entry naming a task id present in the same plan is accepted
  ok  two dangling edges in one document raise ONE exception naming BOTH (D-02)
  ok  depends_on absent is accepted
  ok  depends_on: null is accepted
  ok  depends_on: [] is accepted
  ok  a bare-string depends_on is rejected, naming the task id and the field, with no single-character phantom id from iterating the string
  ok  6a: integer id 1 referenced as the string "1" is accepted
  ok  6b: string id "1" referenced as the integer 1 is accepted
  ok  6c: integer ids with a genuinely absent integer dependency (3) is rejected
  ok  the walk reaches every synthetic plan (3 of 3) and all load
  ok  the same walk reports exactly one failure naming the throwaway dangling plan
  ok  the live plan corpus loads cleanly (44 files found)

13/13 checks passed.
PASS test-plan-depends-on.py
----- test-runner-unsharded.py (exit 0, 1.34s) -----
PASS ['--kind', 'unit']: exit 0 and every discovered file attributed 
PASS ['--kind', 'unit']: pool reports exactly the discovered count 
PASS ['--kind', 'integration']: exit 0 and every discovered file attributed 
PASS ['--kind', 'integration']: pool reports exactly the discovered count 
PASS no-arg: exit 0 and every discovered file attributed 
PASS no-arg: pool reports exactly the discovered count 
PASS ['--kind', 'unit']: child failure propagates as exit 1 
PASS ['--kind', 'integration']: child failure propagates as exit 1 
PASS no-arg: child failure propagates as exit 1 

0 failed
PASS test-runner-unsharded.py
----- test-team-catalog.py (exit 0, 0.07s) -----
ok    (1) validate.yaml is {code, qa, security, ui, goalcheck} and qa is gate-only (persona: qa, mutates_repo: false) — SC-04, MF-1; FEAT-59 SC-13
ok    (2) build.yaml parses, name: build, lead: eng-lead — SC-07
ok    (3) build.yaml is hosted by a lead whose squad is Engineering, so the team is single-squad by construction — SC-07, DEC-118
ok    (4) the Engineering squad covers the personas FEAT-03's eng build runs actually used {dev-ops, backend-dev} — SC-08
ok    (5) harness/SKILL.md has a line naming both `build` and DEC-118 — SC-09
ok    (6) the placeholder literal occurs exactly once across bin/, and both consumers reference PLACEHOLDER_UNSET — SC-02
ok    (7) SPEC §13 has a `build` row whose conducted-by cell matches build.yaml's lead — SC-10
ok    (8) harness/SKILL.md names the blocking qa gate: `test_matrix` present and qa+validator+loop_back within 8 consecutive lines — SC-14, issue #24
ok    (9) the reader set agrees across SPEC's ship-feature row, SPEC's validate row and the shipped validate.yaml — SC-15
ok    (10) test-check-state-plans.py still carries T-01's INV-6 fixtures (`review_sha: none` >= 2, `review_sha: 1ce886a` >= 1) — SC-01

10/10 checks passed.
PASS test-team-catalog.py
----- test-validate-digest-run-pool-lines.py (exit 0, 0.21s) -----
.......
----------------------------------------------------------------------
Ran 7 tests in 0.001s

OK
PASS test-validate-digest-run-pool-lines.py
----- test-suite-layout.py (exit 0, 2.23s) -----
PASS real layout is valid 
PASS empty unit 
PASS empty integration 
PASS duplicate 
PASS planted bin test 
PASS nested test 
PASS undiscoverable test name 
PASS all layout violations reported 
PASS unit detect matches template 
PASS unit detect excludes .claude 
PASS integration detect matches template 
PASS integration detect excludes .claude 
PASS manual tests are not actively detected 
PASS case 1: rogue tracked file reported exactly once as the outside-tests finding 
PASS case 1: legal manual probe file is not named by any finding 
PASS case 1: exact one-element violation list with exceptions cleared 
PASS case 2: untracked rogue file is not reported 
PASS case 3: all three rogue files reported in sorted path order 
PASS case 3: repeat call returns an identical list 
PASS case 4: exactly one enumeration-failure finding 
PASS case 4: no tracked-dependent finding is present 
PASS case 5: non-git tree still returns exactly its four findings 
PASS case 6: listed tracked rogue path is accepted 
PASS case 6: glob entry refused as not an exact path 
PASS case 6: duplicate entry refused as listed twice 
PASS case 6: non-test-shaped entry refused as unnecessary 
PASS case 6: untracked entry refused as no longer tracked 
PASS case 7: fixture layout is clean with the synthetic entry listed 
PASS case 7: synthetic registry entry is load-bearing when cleared 
PASS case 7: live registry is empty 
PASS case 7: real layout is clean with the live registry 
PASS case 8: markdown probe record is not flagged 
PASS case 8: python probe file is flagged 
PASS case 9: repository not shipping suite_layout.py gets no outside-tests finding 
PASS case 10: session_test.md flagged with no extension restriction 
PASS case 10: run.test.jsonl flagged with no extension restriction 
PASS b5 corpus: _is_inside_tests verdicts unchanged 
PASS b5 structural: no unreachable dotdot comparison 
PASS b4 corpus: _literal_key_present verdicts unchanged 
PASS b4 structural: the tautological conjunct is absent 
PASS case 11 behavioural: synthetic tracked set has no offenders 
PASS case 11 behavioural: real tracked set has no offenders 
PASS case 11 behavioural: positive control offender is detected 
PASS b6 reachability: no candidate under a corpus-blind config 
PASS b6 message: the no-candidate failure names both remedies 
PASS case 11 hygiene: every running-kind detect pattern is certified 
PASS classifies_tests: hygiene skips a flagged kind's broad patterns 
PASS classifies_tests: hygiene still refuses the same patterns when the flag is absent 
PASS classifies_tests: offenders ignore production source a flagged kind detects 
PASS classifies_tests: offenders report it when the flag is absent 
PASS classifies_tests: the control candidate inherits the flag 
PASS test-suite-layout.py
----- test-suite-independence.py (exit 0, 4.97s) -----
ok self-test 0-injection idiom
ok self-test 1-mutant beside original
ok self-test 2-pid named mutant
ok self-test clean controls
ok self-test live tree, independent root and discovered floor
ERROR could not resolve scan root above /var/folders/y3/nd_jssrd5dq8lbds73f0fy5m0000gn/T/ht-wiuhc0sq/tmpr1lqnf29
ok self-test unresolved root refuses
root /Users/molchairuangutai/GitHub/harness/.claude/worktrees/.pins/BUG-2566-stale-hook-detection--2026-11-27-05-validate-validator--harness-qa
discovered 164
ok no test mutates a path derived from the live checkout
PASS test-suite-independence.py
----- test-prune-run-evidence.py (exit 0, 5.41s) -----
PASS - dry-run names exactly the ui/ lanes it would drop — no kept run, no run without ui/
PASS - dry-run changes no bytes
PASS - dry-run leaves every run record byte-identical
PASS - dry-run leaves every file in the feature byte-identical, feature.json included
PASS - keeps the ui/ of every PASS validator validate/fix run and any run bound to the pin; drops eng, failed, reconciliation, distill ui/
PASS - kept runs' UI evidence is byte-identical
PASS - exit 0 and names the ui/ it removed
PASS - every run directory, digest.md, state.yaml, .run-identity.json and non-UI sentinel survives prune
PASS - a second prune succeeds and removes nothing more
PASS - a repeated prune still leaves every run record byte-identical
PASS - refuses the placeholder review_sha 'none' — nothing shipped, nothing pruned
PASS - refuses an empty review_sha
PASS - refuses a --keep that names no run directory
PASS - refuses an unknown feature
PASS - refuses a feature.json with a duplicate key through the canonical reader, pruning nothing (#1993)
PASS - an explicit --keep of an otherwise pruned run keeps its ui/
PASS - an explicit --keep prune leaves every run record byte-identical
PASS - FEAT-2229 shape: check-state is clean before prune
PASS - FEAT-2229 shape: an empty keep set still exits 0
PASS - FEAT-2229 shape: every cycle_evidence digest survives prune at its recorded hash
PASS - FEAT-2229 shape: check-state is still clean after prune
PASS - dry-run names no deletion target through a symlink
PASS - dry-run leaves every link destination's ui/ byte-identical
PASS - prune removes no ui/ through a symlink and still prunes the real run
PASS - prune names each symlink it skipped
PASS - a kept run, an outside run and an outside ui/ reached through links keep their ui/ bytes
PASS - a linked subdirectory's external content is left byte-identical
PASS - dry-run starts no subprocess and exits 0
PASS - dry-run prints no staging output
PASS - dry-run prunes as before and leaves every run record and the index byte-identical
PASS - prune starts no subprocess and exits 0
PASS - prune prints no staging output
PASS - prune prunes as before and leaves every run record and the index byte-identical
PASS - dry-run leaves the real git index byte-identical
PASS - prune leaves the real git index byte-identical
PASS - pruner invokes no git subprocess
PASS - real temporary git repository index is byte-identical
PASS - prune refuses with exit 2 naming every missing cycle_evidence path
PASS - a refused prune changes no file and no index byte
PASS - dry-run refuses with exit 2 naming every missing cycle_evidence path
PASS - a refused dry-run changes no file and no index byte
PASS - complete cycle evidence permits the prune, keeps every digest and leaves the index alone
PASS - dry-run fails with exit 1 naming every unreadable directory under a recorded run
PASS - a dry-run over unreadable directories changes no index byte and removes no ui/
PASS - prune fails with exit 1 naming every unreadable directory under a recorded run
PASS - a prune over unreadable directories changes no index byte and removes no ui/
PASS - dry-run fails with exit 1 naming every unreadable directory under a recorded run's ui/
PASS - a dry-run over unreadable ui/ directories removes no readable lane and changes no index byte
PASS - prune fails with exit 1 naming every unreadable directory under a recorded run's ui/
PASS - a prune over unreadable ui/ directories removes no readable lane and changes no index byte
PASS - refused prunes over unreadable ui/ directories leave every feature file byte-identical
PASS - five-file current claims and historical restoration
all checks passed
PASS test-prune-run-evidence.py
----- test-worktree-state-rules.py (exit 0, 0.08s) -----
...............
----------------------------------------------------------------------
Ran 15 tests in 0.001s

OK
PASS test-worktree-state-rules.py
----- test-lead-start-preflight.py (exit 0, 6.49s) -----
PASS [startup] SC-01/eng/zero: harness-eng-lead with zero matching open runs is refused before any claim
PASS [startup] SC-01/eng/zero/cause: harness-eng-lead zero: stderr carries the actual binding failure
PASS [startup] SC-01/eng/irrelevant-only: harness-eng-lead with irrelevant-only matching open runs is refused before any claim
PASS [startup] SC-01/eng/irrelevant-only/cause: harness-eng-lead irrelevant-only: stderr carries the actual binding failure
PASS [startup] SC-01/eng/two: harness-eng-lead with two matching open runs is refused before any claim
PASS [startup] SC-01/eng/two/cause: harness-eng-lead two: stderr carries the actual binding failure
PASS [control] SC-01/eng/one: harness-eng-lead with exactly one matching open run among irrelevant runs starts and claims
PASS [startup] SC-03/eng/missing: harness-eng-lead missing-run refusal names feature, lead, cause and the run-start remedy
PASS [startup] SC-03/eng/ambiguous: harness-eng-lead ambiguous-run refusal directs legitimate reconciliation to one open run
PASS [startup] SC-01/product/zero: harness-product-lead with zero matching open runs is refused before any claim
PASS [startup] SC-01/product/zero/cause: harness-product-lead zero: stderr carries the actual binding failure
PASS [startup] SC-01/product/irrelevant-only: harness-product-lead with irrelevant-only matching open runs is refused before any claim
PASS [startup] SC-01/product/irrelevant-only/cause: harness-product-lead irrelevant-only: stderr carries the actual binding failure
PASS [startup] SC-01/product/two: harness-product-lead with two matching open runs is refused before any claim
PASS [startup] SC-01/product/two/cause: harness-product-lead two: stderr carries the actual binding failure
PASS [control] SC-01/product/one: harness-product-lead with exactly one matching open run among irrelevant runs starts and claims
PASS [startup] SC-03/product/missing: harness-product-lead missing-run refusal names feature, lead, cause and the run-start remedy
PASS [startup] SC-03/product/ambiguous: harness-product-lead ambiguous-run refusal directs legitimate reconciliation to one open run
PASS [startup] SC-01/validator/zero: harness-validator-lead with zero matching open runs is refused before any claim
PASS [startup] SC-01/validator/zero/cause: harness-validator-lead zero: stderr carries the actual binding failure
PASS [startup] SC-01/validator/irrelevant-only: harness-validator-lead with irrelevant-only matching open runs is refused before any claim
PASS [startup] SC-01/validator/irrelevant-only/cause: harness-validator-lead irrelevant-only: stderr carries the actual binding failure
PASS [startup] SC-01/validator/two: harness-validator-lead with two matching open runs is refused before any claim
PASS [startup] SC-01/validator/two/cause: harness-validator-lead two: stderr carries the actual binding failure
PASS [control] SC-01/validator/one: harness-validator-lead with exactly one matching open run among irrelevant runs starts and claims
PASS [startup] SC-03/validator/missing: harness-validator-lead missing-run refusal names feature, lead, cause and the run-start remedy
PASS [startup] SC-03/validator/ambiguous: harness-validator-lead ambiguous-run refusal directs legitimate reconciliation to one open run
PASS [startup] SC-01/eng/unreadable-record: an unreadable feature record refuses the lead rather than passing it through
PASS [startup] SC-01/validator/no-record: a feature with no registered record refuses the lead before any claim
PASS [control] SC-01/non-lead: a non-lead dispatch needs no registered lead run of its own
PASS [startup] SC-03/product/plan-approved: harness-product-lead plan refusal names target and status 'approved', panels precede signature, and directs to the pending-plan phase
PASS [startup] SC-03/product/plan-None: harness-product-lead plan refusal names target and status None, panels precede signature, and directs to the pending-plan phase
PASS [startup] SC-03/validator/plan-approved: harness-validator-lead plan refusal names target and status 'approved', panels precede signature, and directs to the pending-plan phase
PASS [startup] SC-03/validator/plan-None: harness-validator-lead plan refusal names target and status None, panels precede signature, and directs to the pending-plan phase
PASS [dec174] BUG-2141/main-eng/single-direct: Main -> harness-eng-lead on a single-direct plan is refused, registry unchanged
PASS [dec174] BUG-2141/main-eng/single-direct/diagnostic: single-direct: the refusal names DEC-174 and the build-directly remedy
PASS [dec174] BUG-2141/main-eng/multi-direct: Main -> harness-eng-lead on a multi-direct plan is refused, registry unchanged
PASS [dec174] BUG-2141/main-eng/multi-direct/diagnostic: multi-direct: the refusal names DEC-174 and the build-directly remedy
PASS [control] BUG-2141/main-eng/mixed: Main -> harness-eng-lead on a mixed plan keeps its prior start and claim
PASS [control] BUG-2141/main-eng/team: Main -> harness-eng-lead on a team plan keeps its prior start and claim
PASS [control] BUG-2141/main-eng/missing-mode: Main -> harness-eng-lead on a missing-mode plan keeps its prior start and claim
PASS [control] BUG-2141/main-eng/empty: Main -> harness-eng-lead on a empty plan keeps its prior start and claim
PASS [control] BUG-2141/main-eng/invalid: Main -> harness-eng-lead on a invalid plan keeps its prior start and claim
PASS [control] BUG-2141/main-eng/absent: Main -> harness-eng-lead on a absent plan keeps its prior start and claim
PASS [control] BUG-2141/main-product/plan: Main -> harness-product-lead (plan) on an all-direct plan still starts and claims
PASS [control] BUG-2141/main-product/patch: Main -> harness-product-lead (patch) on an all-direct plan still starts and claims
PASS [control] BUG-2141/main-validator/validate: Main -> harness-validator-lead (validate) on an all-direct plan still starts and claims
PASS [control] BUG-2141/main-validator/fix: Main -> harness-validator-lead (fix) on an all-direct plan still starts and claims
PASS [control] BUG-2141/orchestrator-eng: orchestrator -> harness-eng-lead on an all-direct plan keeps its prior outcome
PASS [control] BUG-2141/lead-eng: lead -> harness-eng-lead passes dispatch-guard: FEAT-2274 removed the spawns allowlist (omp's native spawn policy is the sole authority)
PASS [control] BUG-2169/precondition: PyYAML resolves with per-user site disabled, as the policy phase requires
PASS [startup] BUG-2169/single-install: a lead starts when both import phases resolve one system-wide PyYAML
PASS [control] BUG-2169/user-site-plant: a PyYAML planted in per-user site never reaches the policy phase
PASS [control] BUG-2169/pythonpath-plant: a PyYAML planted on PYTHONPATH never reaches the policy phase
PASS [control] BUG-2169/pythonpath-symlink-plant: a PyYAML planted through a symlinked PYTHONPATH entry never reaches the policy phase
PASS [control] BUG-2169/pythonpath-dotdot-plant: a PyYAML planted through a `..`-spelled PYTHONPATH entry never reaches the policy phase
PASS [startup] BUG-2169/advice/debian: Debian/Ubuntu's system python3 is told to apt install python3-yaml
PASS [startup] BUG-2169/advice/homebrew: Homebrew is told to pip install --break-system-packages pyyaml, without --user
PASS [startup] BUG-2169/advice/homebrew-warning: the Homebrew advice states Homebrew's PEP 668 warning plainly
PASS [startup] BUG-2169/advice/other: any other python3 is told to pip install pyyaml into itself, not per-user
PASS [startup] BUG-2169/advice/precedence: a Homebrew python3 on a Debian host gets the Homebrew advice
61 of 61 cases passed
PASS test-lead-start-preflight.py
----- test-digest-projection.py (exit 0, 13.62s) -----
PASS all 16 personas project
PASS alias main-session equals harness-backend-dev
PASS alias dev equals harness-backend-dev
PASS alias reviewer equals harness-code-reviewer
PASS alias lead equals harness-eng-lead
PASS no projected node carries $ref or a non-structural key
PASS malformed JSON names the file
PASS an unresolved reference names file and pointer
PASS a reference cycle names file and pointer
PASS a reference escaping the directory names file and pointer
PASS an unsupported keyword names file and pointer
PASS a property with no type, enum or anyOf names file and pointer
PASS an array without items names file and pointer
PASS array items holding no type, enum or anyOf names the items pointer
PASS an anyOf at the schema root names file and pointer
PASS an anyOf at the schema root reached through $ref names the referenced pointer
PASS a schema file changed on disk changes the next result
PASS the generator runs
PASS a second run leaves identical bytes
PASS --check exits 0 after generation
PASS harness-product-lead.md: body byte-identical
PASS harness-product-lead.md: other frontmatter lines byte-identical
PASS harness-product-lead.md: exactly one structured and one output key
PASS harness-validator-lead.md: body byte-identical
PASS harness-validator-lead.md: other frontmatter lines byte-identical
PASS harness-validator-lead.md: exactly one structured and one output key
PASS harness-security-reviewer.md: body byte-identical
PASS harness-security-reviewer.md: other frontmatter lines byte-identical
PASS harness-security-reviewer.md: exactly one structured and one output key
PASS harness-dev-ops.md: body byte-identical
PASS harness-dev-ops.md: other frontmatter lines byte-identical
PASS harness-dev-ops.md: exactly one structured and one output key
PASS harness-qa.md: body byte-identical
PASS harness-qa.md: other frontmatter lines byte-identical
PASS harness-qa.md: exactly one structured and one output key
PASS harness-frontend-dev.md: body byte-identical
PASS harness-frontend-dev.md: other frontmatter lines byte-identical
PASS harness-frontend-dev.md: exactly one structured and one output key
PASS harness-code-reviewer.md: body byte-identical
PASS harness-code-reviewer.md: other frontmatter lines byte-identical
PASS harness-code-reviewer.md: exactly one structured and one output key
PASS harness-eng-lead.md: body byte-identical
PASS harness-eng-lead.md: other frontmatter lines byte-identical
PASS harness-eng-lead.md: exactly one structured and one output key
PASS harness-visual-designer.md: body byte-identical
PASS harness-visual-designer.md: other frontmatter lines byte-identical
PASS harness-visual-designer.md: exactly one structured and one output key
PASS harness-ui-reviewer.md: body byte-identical
PASS harness-ui-reviewer.md: other frontmatter lines byte-identical
PASS harness-ui-reviewer.md: exactly one structured and one output key
PASS harness-data-engineer.md: body byte-identical
PASS harness-data-engineer.md: other frontmatter lines byte-identical
PASS harness-data-engineer.md: exactly one structured and one output key
PASS harness-pm.md: body byte-identical
PASS harness-pm.md: other frontmatter lines byte-identical
PASS harness-pm.md: exactly one structured and one output key
PASS harness-documentor.md: body byte-identical
PASS harness-documentor.md: other frontmatter lines byte-identical
PASS harness-documentor.md: exactly one structured and one output key
PASS harness-backend-dev.md: body byte-identical
PASS harness-backend-dev.md: other frontmatter lines byte-identical
PASS harness-backend-dev.md: exactly one structured and one output key
PASS harness-ai-dev.md: body byte-identical
PASS harness-ai-dev.md: other frontmatter lines byte-identical
PASS harness-ai-dev.md: exactly one structured and one output key
PASS harness-orchestrator.md: body byte-identical
PASS harness-orchestrator.md: other frontmatter lines byte-identical
PASS harness-orchestrator.md: exactly one structured and one output key
PASS a hand-edited output makes --check exit 1 naming the agent
PASS CRLF frontmatter and body keep their CRLF bytes when stale output is rewritten
PASS a quoted structured key is replaced, never duplicated
PASS an indentationless output sequence is replaced whole, never orphaned
PASS a dash-prefixed sibling key after a stale output survives byte-for-byte
PASS a commented indentationless output sequence leaves no orphan item, and a comment before the next key stays
PASS an escaped quoted structured key is replaced, never duplicated
PASS a bare output: line inside a multiline description is refused, never deleted
PASS an escaped quoted output key inside a multiline description is refused, never deleted
PASS test-digest-projection.py (0)
PASS test-digest-projection.py
----- test-worktree-state-hooks-rules.py (exit 0, 3.90s) -----
............
----------------------------------------------------------------------
Ran 12 tests in 3.809s

OK
PASS test-worktree-state-hooks-rules.py
----- test-wayfind.py (exit 0, 11.04s) -----
PASS case_1_wayfind_directory_probe_resolves_real_root
PASS case_2_wayfind_no_marker_dies_nonzero
PASS case_3_strict_json_read_value
PASS case_3_strict_json_read_one_fake_call
PASS case_4_do_dry_run_launches_nothing
PASS case_4_do_dry_run_prints_plan
PASS case_4_do_apply_runs_on_fake
PASS case_5_gist_dry_run_reads_only
PASS case_5_gist_edit_argv
PASS case_5_gist_stdin_byte_exact
PASS case_6_blockers_401_raises_gh_error
PASS case_6_blockers_403_raises_gh_error
PASS case_6_blockers_500_raises_gh_error
PASS case_6_blockers_network_raises_gh_error
PASS case_6_blockers_exit1_no_marker_raises_gh_error
PASS case_6_blockers_misleading_404_raises_gh_error
PASS case_6_blockers_status0_malformed_with_404_raises_gh_error
PASS case_6_blockers_launch_failure_raises_gh_error
PASS case_6_parent_401_raises_gh_error
PASS case_6_parent_403_raises_gh_error
PASS case_6_parent_500_raises_gh_error
PASS case_6_parent_network_raises_gh_error
PASS case_6_parent_exit1_no_marker_raises_gh_error
PASS case_6_parent_misleading_404_raises_gh_error
PASS case_6_parent_status0_malformed_with_404_raises_gh_error
PASS case_6_parent_launch_failure_raises_gh_error
PASS case_7_blockers_404_is_absence
PASS case_7_parent_404_is_absence
PASS case_8_blockers_value
PASS case_8_parent_value
PASS case_9_garbage_raises_gh_error
PASS case_9_duplicate_raises_gh_error
PASS case_9_nonfinite_raises_gh_error
PASS case_10_frontier_exit_1
PASS case_10_frontier_prints_no_ticket
PASS case_10_frontier_diagnostic
PASS case_10_frontier_stops_reading
PASS case_11_resolve_exit_1
PASS case_11_resolve_names_the_failure
PASS case_11_resolve_no_writes
PASS case_11_resolve_404_means_no_parent
PASS case_8b_blockers_null_raises_gh_error
PASS case_8b_blockers_object_raises_gh_error
PASS case_8b_blockers_string_raises_gh_error
PASS case_8b_blockers_number_raises_gh_error
PASS case_8b_blockers_bool_raises_gh_error
PASS case_8b_blockers_non_object_item_raises_gh_error
PASS case_8b_blockers_null_item_raises_gh_error
PASS case_8b_parent_null_raises_gh_error
PASS case_8b_parent_empty_object_raises_gh_error
PASS case_8b_parent_number_false_raises_gh_error
PASS case_8b_parent_number_true_raises_gh_error
PASS case_8b_parent_number_zero_raises_gh_error
PASS case_8b_parent_number_negative_raises_gh_error
PASS case_8b_parent_number_string_raises_gh_error
PASS case_8b_parent_number_float_raises_gh_error
PASS case_8b_parent_number_null_raises_gh_error
PASS case_8b_parent_list_raises_gh_error
PASS case_10b_frontier_null_exit_1
PASS case_10b_frontier_null_prints_no_ticket
PASS case_10b_frontier_null_stops_reading
PASS case_10b_frontier_object_exit_1
PASS case_10b_frontier_object_prints_no_ticket
PASS case_10b_frontier_object_stops_reading
PASS case_11b_resolve_empty_object_exit_1
PASS case_11b_resolve_empty_object_not_absence
PASS case_11b_resolve_empty_object_no_writes
PASS case_11b_resolve_number_false_exit_1
PASS case_11b_resolve_number_false_not_absence
PASS case_11b_resolve_number_false_no_writes
PASS case_11b_resolve_number_zero_exit_1
PASS case_11b_resolve_number_zero_not_absence
PASS case_11b_resolve_number_zero_no_writes
PASS case_11b_resolve_number_string_exit_1
PASS case_11b_resolve_number_string_not_absence
PASS case_11b_resolve_number_string_no_writes
PASS case_11b_resolve_null_exit_1
PASS case_11b_resolve_null_not_absence
PASS case_11b_resolve_null_no_writes
PASS case_8c_blockers_item_no_state_raises_gh_error
PASS case_8c_blockers_state_unknown_raises_gh_error
PASS case_8c_blockers_state_int_raises_gh_error
PASS case_8c_blockers_state_null_raises_gh_error
PASS case_8c_blockers_state_empty_raises_gh_error
PASS case_8c_blockers_state_list_raises_gh_error
PASS case_8c_blockers_second_item_stateless_raises_gh_error
PASS case_8c_blockers_open_closed_any_case_valid
PASS case_8c_blockers_empty_list_valid
PASS case_10c_frontier_blockers_item_no_state_exit_1
PASS case_10c_frontier_blockers_item_no_state_prints_no_ticket
PASS case_10c_frontier_blockers_item_no_state_typed_diagnostic
PASS case_10c_frontier_blockers_item_no_state_stops_reading
PASS case_10c_frontier_blockers_state_unknown_exit_1
PASS case_10c_frontier_blockers_state_unknown_prints_no_ticket
PASS case_10c_frontier_blockers_state_unknown_typed_diagnostic
PASS case_10c_frontier_blockers_state_unknown_stops_reading
PASS case_10c_frontier_blockers_state_int_exit_1
PASS case_10c_frontier_blockers_state_int_prints_no_ticket
PASS case_10c_frontier_blockers_state_int_typed_diagnostic
PASS case_10c_frontier_blockers_state_int_stops_reading
PASS case_10c_frontier_blockers_state_null_exit_1
PASS case_10c_frontier_blockers_state_null_prints_no_ticket
PASS case_10c_frontier_blockers_state_null_typed_diagnostic
PASS case_10c_frontier_blockers_state_null_stops_reading
PASS case_10c_frontier_blockers_state_empty_exit_1
PASS case_10c_frontier_blockers_state_empty_prints_no_ticket
PASS case_10c_frontier_blockers_state_empty_typed_diagnostic
PASS case_10c_frontier_blockers_state_empty_stops_reading
PASS case_10c_frontier_blockers_state_list_exit_1
PASS case_10c_frontier_blockers_state_list_prints_no_ticket
PASS case_10c_frontier_blockers_state_list_typed_diagnostic
PASS case_10c_frontier_blockers_state_list_stops_reading
PASS case_10c_frontier_blockers_second_item_stateless_exit_1
PASS case_10c_frontier_blockers_second_item_stateless_prints_no_ticket
PASS case_10c_frontier_blockers_second_item_stateless_typed_diagnostic
PASS case_10c_frontier_blockers_second_item_stateless_stops_reading
PASS case_10c_frontier_subs_null_exit_1
PASS case_10c_frontier_subs_null_prints_no_ticket
PASS case_10c_frontier_subs_null_typed_diagnostic
PASS case_10c_frontier_subs_null_stops_reading
PASS case_10c_frontier_subs_object_exit_1
PASS case_10c_frontier_subs_object_prints_no_ticket
PASS case_10c_frontier_subs_object_typed_diagnostic
PASS case_10c_frontier_subs_object_stops_reading
PASS case_10c_frontier_subs_non_object_item_exit_1
PASS case_10c_frontier_subs_non_object_item_prints_no_ticket
PASS case_10c_frontier_subs_non_object_item_typed_diagnostic
PASS case_10c_frontier_subs_non_object_item_stops_reading
PASS case_10c_frontier_subs_no_state_exit_1
PASS case_10c_frontier_subs_no_state_prints_no_ticket
PASS case_10c_frontier_subs_no_state_typed_diagnostic
PASS case_10c_frontier_subs_no_state_stops_reading
PASS case_10c_frontier_subs_state_unknown_exit_1
PASS case_10c_frontier_subs_state_unknown_prints_no_ticket
PASS case_10c_frontier_subs_state_unknown_typed_diagnostic
PASS case_10c_frontier_subs_state_unknown_stops_reading
PASS case_10c_frontier_subs_state_int_exit_1
PASS case_10c_frontier_subs_state_int_prints_no_ticket
PASS case_10c_frontier_subs_state_int_typed_diagnostic
PASS case_10c_frontier_subs_state_int_stops_reading
PASS case_10c_frontier_subs_no_number_exit_1
PASS case_10c_frontier_subs_no_number_prints_no_ticket
PASS case_10c_frontier_subs_no_number_typed_diagnostic
PASS case_10c_frontier_subs_no_number_stops_reading
PASS case_10c_frontier_subs_number_string_exit_1
PASS case_10c_frontier_subs_number_string_prints_no_ticket
PASS case_10c_frontier_subs_number_string_typed_diagnostic
PASS case_10c_frontier_subs_number_string_stops_reading
PASS case_10c_frontier_subs_number_bool_exit_1
PASS case_10c_frontier_subs_number_bool_prints_no_ticket
PASS case_10c_frontier_subs_number_bool_typed_diagnostic
PASS case_10c_frontier_subs_number_bool_stops_reading
PASS case_10c_frontier_subs_number_zero_exit_1
PASS case_10c_frontier_subs_number_zero_prints_no_ticket
PASS case_10c_frontier_subs_number_zero_typed_diagnostic
PASS case_10c_frontier_subs_number_zero_stops_reading
PASS case_10c_frontier_view_null_exit_1
PASS case_10c_frontier_view_null_prints_no_ticket
PASS case_10c_frontier_view_null_typed_diagnostic
PASS case_10c_frontier_view_list_exit_1
PASS case_10c_frontier_view_list_prints_no_ticket
PASS case_10c_frontier_view_list_typed_diagnostic
PASS case_10c_frontier_assignees_missing_exit_1
PASS case_10c_frontier_assignees_missing_prints_no_ticket
PASS case_10c_frontier_assignees_missing_typed_diagnostic
PASS case_10c_frontier_assignees_null_exit_1
PASS case_10c_frontier_assignees_null_prints_no_ticket
PASS case_10c_frontier_assignees_null_typed_diagnostic
PASS case_10c_frontier_assignees_string_exit_1
PASS case_10c_frontier_assignees_string_prints_no_ticket
PASS case_10c_frontier_assignees_string_typed_diagnostic
PASS case_10c_frontier_assignees_object_exit_1
PASS case_10c_frontier_assignees_object_prints_no_ticket
PASS case_10c_frontier_assignees_object_typed_diagnostic
PASS case_10c_frontier_labels_missing_exit_1
PASS case_10c_frontier_labels_missing_prints_no_ticket
PASS case_10c_frontier_labels_missing_typed_diagnostic
PASS case_10c_frontier_labels_string_exit_1
PASS case_10c_frontier_labels_string_prints_no_ticket
PASS case_10c_frontier_labels_string_typed_diagnostic
PASS case_10c_frontier_labels_non_object_item_exit_1
PASS case_10c_frontier_labels_non_object_item_prints_no_ticket
PASS case_10c_frontier_labels_non_object_item_typed_diagnostic
PASS case_10c_frontier_labels_nameless_item_exit_1
PASS case_10c_frontier_labels_nameless_item_prints_no_ticket
PASS case_10c_frontier_labels_nameless_item_typed_diagnostic
PASS case_10c_frontier_labels_name_int_exit_1
PASS case_10c_frontier_labels_name_int_prints_no_ticket
PASS case_10c_frontier_labels_name_int_typed_diagnostic
PASS case_10c_frontier_title_missing_exit_1
PASS case_10c_frontier_title_missing_prints_no_ticket
PASS case_10c_frontier_title_missing_typed_diagnostic
PASS case_10c_frontier_title_null_exit_1
PASS case_10c_frontier_title_null_prints_no_ticket
PASS case_10c_frontier_title_null_typed_diagnostic
PASS case_10c_frontier_number_missing_exit_1
PASS case_10c_frontier_number_missing_prints_no_ticket
PASS case_10c_frontier_number_missing_typed_diagnostic
PASS case_10c_frontier_number_other_exit_1
PASS case_10c_frontier_number_other_prints_no_ticket
PASS case_10c_frontier_number_other_typed_diagnostic
PASS case_10c_frontier_number_string_exit_1
PASS case_10c_frontier_number_string_prints_no_ticket
PASS case_10c_frontier_number_string_typed_diagnostic
PASS case_10c_frontier_number_bool_exit_1
PASS case_10c_frontier_number_bool_prints_no_ticket
PASS case_10c_frontier_number_bool_typed_diagnostic
PASS case_10d_frontier_closed_blockers_exit_0
PASS case_10d_frontier_empty_blockers_exit_0
PASS case_10d_frontier_blockers_404_exit_0
PASS case_10d_frontier_open_blocker_exit_0
PASS case_10d_frontier_claimed_exit_0
PASS case_10d_frontier_closed_ticket_exit_0
PASS case_10d_frontier_no_subs_exit_0
PASS case_11c_resolve_title_null_exit_1_typed
PASS case_11c_resolve_title_null_no_writes
PASS case_11c_resolve_title_list_exit_1_typed
PASS case_11c_resolve_title_list_no_writes
PASS case_11c_resolve_title_missing_exit_1_typed
PASS case_11c_resolve_title_missing_no_writes
PASS case_11c_resolve_title_title_null_exit_1_typed
PASS case_11c_resolve_title_title_null_no_writes
PASS case_11c_resolve_title_title_int_exit_1_typed
PASS case_11c_resolve_title_title_int_no_writes
PASS case_11c_gist_body_null_raises_gh_error
PASS case_11c_gist_body_null_no_edit
PASS case_11c_gist_body_missing_raises_gh_error
PASS case_11c_gist_body_missing_no_edit
PASS case_11c_gist_body_body_null_raises_gh_error
PASS case_11c_gist_body_body_null_no_edit
PASS case_11c_gist_body_body_int_raises_gh_error
PASS case_11c_gist_body_body_int_no_edit
PASS case_12_ticket_attached
PASS case_12_ticket_bad_url_exit_1
PASS case_12_ticket_bad_url_stops
PASS case_12_ticket_dry_run_no_mutation
PASS case_13_gh_issues_has_no_gh_bin
PASS case_13_wayfind_has_no_subprocess

ALL PASS
PASS test-wayfind.py
----- test-omp-hooks.py (exit 0, 24.11s) -----
bun test v1.3.14 (0d9b296a)

 274 pass
 0 fail
 1295 expect() calls
Ran 274 tests across 1 file. [23.97s]
PASS test-omp-hooks.py
----- test-feature-record.py (exit 0, 29.45s) -----
.................REFUSED at stage refused-return: later stages were not run.
Traceback (most recent call last):
  File "/var/folders/y3/nd_jssrd5dq8lbds73f0fy5m0000gn/T/ht-kwjdndpo/feature-record-test-sa4gre7l/broken-validator.py", line 1, in <module>
    raise RuntimeError('validator internal failure')
RuntimeError: validator internal failure
.REFUSED at stage refused-return: later stages were not run.
usage: validate-digest.py [-h] [--contract-refusal-code {1,65}] persona [file]
validate-digest.py: error: the following arguments are required: persona
................................................................................................................
----------------------------------------------------------------------
Ran 130 tests in 29.000s

OK
PASS test-feature-record.py
pool: 8 workers, 69 files, 34.92s wall
slowest: test-feature-record.py 29.45s, test-omp-hooks.py 24.11s, test-digest-projection.py 13.62s
```
